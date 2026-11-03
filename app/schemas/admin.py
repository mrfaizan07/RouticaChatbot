"""Admin dashboard and provider monitoring schemas."""

from datetime import datetime
from typing import Any
from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_users: int
    total_products: int
    total_pages_scraped: int
    total_knowledge_chunks: int
    total_documents_uploaded: int
    total_conversations: int
    total_messages: int
    vector_search_ready: bool
    storage_backend: str


class ProviderStatusResponse(BaseModel):
    primary_provider: str
    primary_model: str
    fallback_models: list[str]
    configured_keys: dict[str, bool]
    embedding_provider: str
    embedding_model: str
    embedding_dimensions: int


class ScrapingJobResponse(BaseModel):
    id: str
    job_type: str
    status: str
    started_at: datetime
    completed_at: datetime | None = None
    pages_discovered: int
    pages_processed: int
    pages_failed: int
    error_summary: str | None = None

