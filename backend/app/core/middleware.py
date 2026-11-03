"""Pure ASGI Middlewares for Request-ID, process timing, security headers, and rate limiting."""

import time
import uuid
from collections import defaultdict
from starlette.datastructures import Headers, MutableHeaders
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from app.config import get_settings
from app.core.logging import logger

settings = get_settings()


class RequestContextMiddleware:
    """Pure ASGI middleware assigning unique Request-ID, calculating latency, and setting security headers."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = Headers(scope=scope)
        request_id = headers.get("X-Request-ID") or str(uuid.uuid4())
        if "state" not in scope:
            scope["state"] = {}
        scope["state"]["request_id"] = request_id

        start_time = time.perf_counter()

        async def send_wrapper(message: dict) -> None:
            if message["type"] == "http.response.start":
                duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
                mutable_headers = MutableHeaders(scope=message)
                mutable_headers.append("X-Request-ID", request_id)
                mutable_headers.append("X-Process-Time-Ms", str(duration_ms))
                mutable_headers.append("X-Content-Type-Options", "nosniff")
                mutable_headers.append("X-Frame-Options", "DENY")
                mutable_headers.append("X-XSS-Protection", "1; mode=block")
                mutable_headers.append("Referrer-Policy", "strict-origin-when-cross-origin")
                if settings.APP_ENV == "production":
                    mutable_headers.append("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
            await send(message)

        await self.app(scope, receive, send_wrapper)


class InMemoryRateLimiter:
    """Production-grade sliding-window rate limiter protecting against spam, DDoS, and quota draining."""

    def __init__(self, app: ASGIApp, max_requests: int = 60, window_seconds: int = 60) -> None:
        self.app = app
        self.default_max = max_requests
        self.window_seconds = window_seconds
        # Route-specific max requests per window (relaxed for local development)
        is_dev = settings.APP_ENV != "production"
        self.route_limits = {
            "/api/v1/chat": 60 if is_dev else 25,
            "/api/v1/chat/stream": 60 if is_dev else 25,
            "/api/v1/auth/login": 60 if is_dev else 10,
        }
        self.requests: dict[str, list[float]] = defaultdict(list)
        self._last_cleanup = time.time()

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        # Whitelisted health and documentation paths, plus CORS preflight OPTIONS requests
        if scope.get("method") == "OPTIONS" or path in ["/health", "/ready", "/docs", "/openapi.json"]:
            await self.app(scope, receive, send)
            return

        headers = Headers(scope=scope)
        forwarded = headers.get("x-forwarded-for")
        session_id = headers.get("x-session-id")
        client = scope.get("client")
        client_ip = forwarded.split(",")[0].strip() if forwarded else (client[0] if client else "unknown")

        # Whitelist localhost during development so testing isn't blocked
        if settings.APP_ENV != "production" and client_ip in ("127.0.0.1", "::1", "localhost"):
            await self.app(scope, receive, send)
            return

        # Composite identifier to prevent simple IP spoofing
        rate_key = f"{client_ip}:{session_id}" if session_id else client_ip

        # Determine limit for this path
        max_allowed = self.default_max
        for prefix, limit in self.route_limits.items():
            if path.startswith(prefix):
                max_allowed = limit
                break

        current_time = time.time()
        window_start = current_time - self.window_seconds

        # Clean up stale memory entries every 5 minutes
        if current_time - self._last_cleanup > 300:
            self._last_cleanup = current_time
            stale_keys = [k for k, timestamps in self.requests.items() if not timestamps or timestamps[-1] < window_start]
            for k in stale_keys:
                del self.requests[k]

        # Filter timestamps within current sliding window
        self.requests[rate_key] = [ts for ts in self.requests[rate_key] if ts > window_start]
        current_count = len(self.requests[rate_key])

        if current_count >= max_allowed:
            logger.warning(
                "Rate limit exceeded: %s on %s (count=%d, max=%d)",
                rate_key,
                path,
                current_count,
                max_allowed,
            )
            response = JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": f"Rate limit exceeded. You may make up to {max_allowed} requests per minute. Please slow down.",
                    },
                },
                headers={
                    "Retry-After": str(self.window_seconds),
                    "X-RateLimit-Limit": str(max_allowed),
                    "X-RateLimit-Remaining": "0",
                },
            )
            await response(scope, receive, send)
            return

        self.requests[rate_key].append(current_time)

        # Wrap send to append RateLimit headers to response
        async def send_wrapper(message: dict) -> None:
            if message["type"] == "http.response.start":
                mutable_headers = MutableHeaders(scope=message)
                mutable_headers.append("X-RateLimit-Limit", str(max_allowed))
                mutable_headers.append("X-RateLimit-Remaining", str(max(0, max_allowed - current_count - 1)))
            await send(message)

        await self.app(scope, receive, send_wrapper)
