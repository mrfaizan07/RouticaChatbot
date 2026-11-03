"""Structured application logger with contextual request tracking and secret sanitization."""

import json
import logging
import re
import sys
from datetime import datetime, timezone
from typing import Any

# Mask potential API keys, passwords, bearer tokens in log output
SENSITIVE_PATTERNS = [
    (re.compile(r'(api[-_]?key|secret|token|password|bearer)["\']?\s*[:=]\s*["\']?([^"\'\s]+)["\']?', re.IGNORECASE), r'\1="[REDACTED]"'),
    (re.compile(r'(AIzaSy[A-Za-z0-9_-]{33})'), r'[REDACTED_GEMINI_KEY]'),
    (re.compile(r'(gsk_[A-Za-z0-9_-]{32,})'), r'[REDACTED_GROQ_KEY]'),
    (re.compile(r'(sk-or-v1-[A-Za-z0-9_-]{32,})'), r'[REDACTED_OPENROUTER_KEY]'),
]


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter producing structured logs."""

    def format(self, record: logging.LogRecord) -> str:
        log_data: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Include request context if attached
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "endpoint"):
            log_data["endpoint"] = record.endpoint
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms
        if hasattr(record, "provider"):
            log_data["provider"] = record.provider
        if hasattr(record, "model"):
            log_data["model"] = record.model

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        formatted_msg = json.dumps(log_data)
        for pattern, replacement in SENSITIVE_PATTERNS:
            formatted_msg = pattern.sub(replacement, formatted_msg)
        return formatted_msg


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Configures root logger with JSON output."""
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level.upper())

    # Avoid duplicate handlers
    if not root_logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        root_logger.addHandler(handler)
    else:
        for handler in root_logger.handlers:
            handler.setFormatter(JSONFormatter())

    # Tone down noisy third-party loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("motor").setLevel(logging.WARNING)
    logging.getLogger("pymongo").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("liteLLM").setLevel(logging.WARNING)

    return logging.getLogger("routica")


logger = logging.getLogger("routica")
