"""Structured product data model."""

from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class Product(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str | None = Field(default=None, alias="_id")
    product_name: str
    product_slug: str
    category: str
    description: str
    specifications: dict[str, Any] = Field(default_factory=dict)
    features: list[str] = Field(default_factory=list)
    source_url: str
    source_type: str = "website"
    last_verified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
