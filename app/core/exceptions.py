"""Centralized application exception definitions."""

from typing import Any
from fastapi import HTTPException, status


class RouticaBaseException(Exception):
    """Base exception for all Routica application errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ConfigurationError(RouticaBaseException):
    """Raised when an environment or configuration setting is invalid or missing."""
    pass


class DatabaseConnectionError(RouticaBaseException):
    """Raised when the database connection cannot be established or verified."""
    pass


class VectorIndexError(RouticaBaseException):
    """Raised when the Atlas Vector Search index is missing or misconfigured."""
    pass


class EmbeddingError(RouticaBaseException):
    """Raised when embedding generation fails."""
    pass


class AIProviderError(RouticaBaseException):
    """Raised when all configured AI providers fail or quota is exhausted."""
    pass


class ScrapingSSRFError(RouticaBaseException):
    """Raised when a crawling target violates security or SSRF rules."""
    pass


class StorageError(RouticaBaseException):
    """Raised when file storage operations fail."""
    pass


class DocumentProcessingError(RouticaBaseException):
    """Raised when parsing or extracting an uploaded file fails."""
    pass


# HTTP Exception standard helpers
class UnauthorizedException(HTTPException):
    def __init__(self, detail: str = "Could not validate credentials") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class ForbiddenException(HTTPException):
    def __init__(self, detail: str = "Insufficient permissions") -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class NotFoundException(HTTPException):
    def __init__(self, detail: str = "Resource not found") -> None:
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class RateLimitExceededException(HTTPException):
    def __init__(self, detail: str = "Rate limit exceeded. Please try again later.") -> None:
        super().__init__(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=detail)


class ValidationException(HTTPException):
    def __init__(self, detail: str = "Invalid request parameters") -> None:
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)
