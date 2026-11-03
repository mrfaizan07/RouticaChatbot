"""Knowledge and chunk schemas."""

from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class KnowledgeChunkResponse(BaseModel):
    id: str
    source_id: str
    source_type: str
    source_title: str
    source_url: str
    chunk_index: int
    content: str
    embedding_model: str
    embedding_dimensions: int
    metadata: dict[str, Any] = Field(default_factory=dict)
    is_active: bool
    created_at: datetime


class KnowledgeListResponse(BaseModel):
    total: int
    chunks: list[KnowledgeChunkResponse]


class ReindexRequest(BaseModel):
    force_all: bool = False
    source_type: str | None = None


class ReindexResponse(BaseModel):
    success: bool
    message: str
    chunks_indexed: int

