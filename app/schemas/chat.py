"""Chat request and response schemas."""

from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class CitationSource(BaseModel):
    title: str
    url: str
    source_type: str = "website"  # website, document, product
    relevance_score: float | None = None
    snippet: str | None = None


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000, description="User prompt message")
    conversation_id: str | None = Field(default=None, description="Optional existing conversation ID")
    session_id: str | None = Field(default=None, description="Client session ID for conversation isolation")
    page_context: str | None = Field(default=None, max_length=2000, description="Optional current page URL or context")


class ChatResponse(BaseModel):
    success: bool = True
    conversation_id: str
    message_id: str
    answer: str
    sources: list[CitationSource] = Field(default_factory=list)
    provider: str
    model: str
    response_time_ms: int = 0
    created_at: datetime


class StreamChunk(BaseModel):
    event: str = "token"  # status, token, sources, complete, error
    data: dict[str, Any]

