"""Knowledge chunk data model for vector and hybrid search."""

from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class KnowledgeChunk(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    id: str | None = Field(default=None, alias="_id")
    source_id: str = ""
    source_type: str = "website"  # website, document, product
    source_title: str = "Routica Knowledge"
    source_url: str = "https://routica.com"
    chunk_index: int = 0
    content: str = ""
    embedding: list[float] = Field(default_factory=list)
    embedding_model: str = "text-embedding-004"
    embedding_dimensions: int = 768
    content_hash: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
