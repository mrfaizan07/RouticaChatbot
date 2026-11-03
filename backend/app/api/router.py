"""Aggregated API router for API v1 combining all endpoint groups."""

from fastapi import APIRouter
from app.api.v1 import (
    admin,
    auth,
    chat,
    conversations,
    health,
    knowledge,
    scraping,
    uploads,
)

api_router = APIRouter()

# Register endpoint groups
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(chat.router)
api_router.include_router(conversations.router)
api_router.include_router(admin.router)
api_router.include_router(uploads.router)
api_router.include_router(knowledge.router)
api_router.include_router(scraping.router)
