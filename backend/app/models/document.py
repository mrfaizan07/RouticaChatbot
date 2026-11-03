"""Uploaded document metadata model."""

from datetime import datetime, timezone
from pydantic import BaseModel, ConfigDict, Field


class Document(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str | None = Field(default=None, alias="_id")
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    storage_key: str
    content_hash: str
    processing_status: str = "pending"  # pending, processed, failed
    processing_error: str | None = None
    total_chunks: int = 0
    uploaded_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
