"""Website page data model."""

from datetime import datetime, timezone
from pydantic import BaseModel, ConfigDict, Field


class WebsitePage(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str | None = Field(default=None, alias="_id")
    url: str
    canonical_url: str
    title: str
    page_type: str = "general"  # product, solutions, faq, blog, policy, company
    content: str
    content_hash: str
    status: str = "scraped"  # scraped, indexed, failed
    last_scraped_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
