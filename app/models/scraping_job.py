"""Scraping job audit model."""

from datetime import datetime, timezone
from pydantic import BaseModel, ConfigDict, Field


class ScrapingJob(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str | None = Field(default=None, alias="_id")
    job_type: str = "full_crawl"  # full_crawl, single_page, sitemap_crawl
    status: str = "running"  # running, completed, failed
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    pages_discovered: int = 0
    pages_processed: int = 0
    pages_failed: int = 0
    error_summary: str | None = None
