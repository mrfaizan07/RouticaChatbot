"""Health and readiness check endpoints."""

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database.mongodb import MongoDBManager

router = APIRouter(tags=["Health"])
settings = get_settings()


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> dict[str, str]:
    """Liveness probe: verifies that the FastAPI process is running."""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "environment": settings.APP_ENV,
    }


@router.get("/ready")
async def readiness_check() -> JSONResponse:
    """Readiness probe: validates external dependencies (database, search index)."""
    db_connected = await MongoDBManager.ping()
    vector_status = await MongoDBManager.check_vector_index()

    configured_providers = []
    if settings.GEMINI_API_KEY:
        configured_providers.append("gemini")
    if settings.GROQ_API_KEY:
        configured_providers.append("groq")
    if settings.OPENROUTER_API_KEY:
        configured_providers.append("openrouter")

    # App is considered ready if database is connected or running in non-production mode
    is_ready = db_connected or (settings.APP_ENV != "production")

    response_payload = {
        "status": "ready" if is_ready else "not_ready",
        "database": {
            "connected": db_connected,
            "name": settings.MONGODB_DATABASE,
        },
        "vector_search": {
            "status": vector_status.get("status"),
            "index_name": settings.VECTOR_SEARCH_INDEX_NAME,
        },
        "ai_providers": {
            "primary": settings.CHAT_PRIMARY_PROVIDER,
            "configured_count": len(configured_providers),
        },
        "storage_backend": settings.STORAGE_BACKEND,
    }

    status_code = status.HTTP_200_OK if is_ready else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(status_code=status_code, content=response_payload)
