"""Main FastAPI application entry point with lifespan, CORS, middleware, and routers."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.router import api_router
from app.api.v1.health import router as health_router
from app.config import get_settings
from app.core.exceptions import RouticaBaseException
from app.core.logging import logger, setup_logging
from app.core.middleware import InMemoryRateLimiter, RequestContextMiddleware
from app.database.mongodb import MongoDBManager

settings = get_settings()
setup_logging(settings.LOG_LEVEL)

# Ensure provider API keys are exported to os.environ for LiteLLM providers
import os
os.environ["LITELLM_LOCAL_MODEL_COST_MAP"] = "True"
if settings.GEMINI_API_KEY:
    os.environ["GEMINI_API_KEY"] = settings.GEMINI_API_KEY
if settings.GROQ_API_KEY:
    os.environ["GROQ_API_KEY"] = settings.GROQ_API_KEY
if settings.OPENROUTER_API_KEY:
    os.environ["OPENROUTER_API_KEY"] = settings.OPENROUTER_API_KEY


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manages application lifecycle: database connections and cleanup."""
    logger.info("Initializing %s in %s mode...", settings.APP_NAME, settings.APP_ENV)
    await MongoDBManager.connect()
    yield
    logger.info("Shutting down %s...", settings.APP_NAME)
    await MongoDBManager.close()


def create_application() -> FastAPI:
    """Application factory."""
    app = FastAPI(
        title=settings.APP_NAME,
        version="1.0.0",
        description="Enterprise AI Chatbot Backend for Routica (https://routica.com)",
        lifespan=lifespan,
        docs_url="/docs" if settings.DEBUG or settings.APP_ENV != "production" else None,
        redoc_url=None,
        openapi_url="/openapi.json" if settings.DEBUG or settings.APP_ENV != "production" else None,
    )

    # Request ID and Context Tracking
    app.add_middleware(RequestContextMiddleware)

    # Rate Limiting
    app.add_middleware(InMemoryRateLimiter, max_requests=settings.RATE_LIMIT_PER_MINUTE)

    # CORS configuration (Outermost wrapper - added last so it catches preflights and wraps error responses)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list or ["*"],
        allow_origin_regex=r"^https?://.*\.onrender\.com$|^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    # Global Exception Handlers
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        errors = []
        for err in exc.errors():
            loc = " -> ".join(str(l) for l in err.get("loc", []))
            errors.append({"field": loc, "message": err.get("msg")})
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid request parameters",
                    "details": errors,
                },
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": f"HTTP_{exc.status_code}",
                    "message": exc.detail,
                },
            },
        )

    @app.exception_handler(RouticaBaseException)
    async def custom_exception_handler(request: Request, exc: RouticaBaseException) -> JSONResponse:
        logger.warning("Custom domain exception: %s", exc.message)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "error": {
                    "code": exc.__class__.__name__,
                    "message": exc.message,
                    "details": exc.details,
                },
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error("Unhandled server exception: %s", str(exc), exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected internal error occurred.",
                },
            },
        )

    # Direct health check routes on root
    app.include_router(health_router)

    # API v1 routes
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    return app


app = create_application()
