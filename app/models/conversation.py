"""Conversation and Message data models."""

from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class Conversation(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str | None = Field(default=None, alias="_id")
    session_id: str
    title: str = "New Conversation"
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Message(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str | None = Field(default=None, alias="_id")
    conversation_id: str
    role: str  # "user" | "assistant"
    content: str
    sources: list[dict[str, Any]] = Field(default_factory=list)
    model_used: str = ""
    provider_used: str = ""
    response_time_ms: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
