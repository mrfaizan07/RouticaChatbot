"""Website scraping and crawl job management endpoints."""

import asyncio
from fastapi import APIRouter, BackgroundTasks, Depends, status

from app.core.exceptions import ValidationException
from app.database.repositories.knowledge import KnowledgeRepository
from app.database.repositories.scraping_jobs import ScrapingJobRepository
from app.database.repositories.website_pages import WebsitePageRepository
from app.dependencies import (
    get_current_admin,
    get_knowledge_repo,
    get_scraping_job_repo,
    get_website_page_repo,
)
from app.ingestion.crawler import RouticaCrawler
from app.ingestion.deduplicator import Deduplicator
from app.ingestion.scraper import WebScraper
from app.models.scraping_job import ScrapingJob
from app.models.user import User
from app.models.website_page import WebsitePage
from app.schemas.admin import ScrapingJobResponse
from app.services.knowledge_service import KnowledgeService

router = APIRouter(prefix="/scraping", tags=["Scraping"])


async def run_crawl_task(
    job_id: str,
    job_repo: ScrapingJobRepository,
    page_repo: WebsitePageRepository,
    knowledge_repo: KnowledgeRepository,
) -> None:
    """Asynchronous background crawler task."""
    crawler = RouticaCrawler()
    scraper = WebScraper()
    knowledge_svc = KnowledgeService(knowledge_repo=knowledge_repo)

    discovered_urls = await crawler.discover_urls(max_pages=30)
    pages_processed = 0
    pages_failed = 0

    for url in discovered_urls:
        try:
            page_data = await scraper.scrape_page(url)
            canonical = page_data["canonical_url"]

            # Change detection
            existing = await page_repo.get_by_canonical_url(canonical)
            old_hash = existing.content_hash if existing else None
            changed, new_hash = Deduplicator.is_content_changed(old_hash, page_data["content"])

            if changed:
                page_model = WebsitePage(
                    url=url,
                    canonical_url=canonical,
                    title=page_data["title"],
                    page_type=page_data["page_type"],
                    content=page_data["content"],
                    content_hash=new_hash,
                    status="indexed",
                )
                saved_page = await page_repo.upsert(page_model)
                page_id = str(saved_page.id)

                # Chunks and embeddings
                await knowledge_svc.ingest_content(
                    source_id=page_id,
                    source_type="website",
                    source_title=page_data["title"],
                    source_url=canonical,
                    raw_text=page_data["content"],
                    metadata={"page_type": page_data["page_type"]},
                )
            pages_processed += 1
            await asyncio.sleep(0.5)  # Rate limiting delay
        except Exception:
            pages_failed += 1

    await job_repo.update(
        job_id=job_id,
        status="completed" if pages_failed == 0 else "completed_with_errors",
        pages_discovered=len(discovered_urls),
        pages_processed=pages_processed,
        pages_failed=pages_failed,
    )


@router.post("/start", response_model=ScrapingJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def start_scraping_job(
    background_tasks: BackgroundTasks,
    current_admin: User = Depends(get_current_admin),
    job_repo: ScrapingJobRepository = Depends(get_scraping_job_repo),
    page_repo: WebsitePageRepository = Depends(get_website_page_repo),
    knowledge_repo: KnowledgeRepository = Depends(get_knowledge_repo),
) -> ScrapingJobResponse:
    """Triggers an asynchronous crawl of routica.com."""
    latest = await job_repo.get_latest_job()
    if latest and latest.status == "running":
        raise ValidationException("A scraping job is already actively running. Please wait for it to complete.")

    job = ScrapingJob(job_type="full_crawl", status="running")
    saved_job = await job_repo.create(job)
    job_id = str(saved_job.id)

    background_tasks.add_task(run_crawl_task, job_id, job_repo, page_repo, knowledge_repo)

    return ScrapingJobResponse(
        id=job_id,
        job_type=saved_job.job_type,
        status=saved_job.status,
        started_at=saved_job.started_at,
        completed_at=saved_job.completed_at,
        pages_discovered=0,
        pages_processed=0,
        pages_failed=0,
    )


@router.get("/status", response_model=ScrapingJobResponse | None)
async def get_scraping_status(
    current_admin: User = Depends(get_current_admin),
    job_repo: ScrapingJobRepository = Depends(get_scraping_job_repo),
) -> ScrapingJobResponse | None:
    """Returns the status and metrics of the latest scraping job."""
    job = await job_repo.get_latest_job()
    if not job:
        return None
    return ScrapingJobResponse(
        id=str(job.id),
        job_type=job.job_type,
        status=job.status,
        started_at=job.started_at,
        completed_at=job.completed_at,
        pages_discovered=job.pages_discovered,
        pages_processed=job.pages_processed,
        pages_failed=job.pages_failed,
        error_summary=job.error_summary,
    )


@router.post("/retry", response_model=ScrapingJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def retry_scraping_job(
    background_tasks: BackgroundTasks,
    current_admin: User = Depends(get_current_admin),
    job_repo: ScrapingJobRepository = Depends(get_scraping_job_repo),
    page_repo: WebsitePageRepository = Depends(get_website_page_repo),
    knowledge_repo: KnowledgeRepository = Depends(get_knowledge_repo),
) -> ScrapingJobResponse:
    """Retries scraping for previously discovered pages."""
    return await start_scraping_job(background_tasks, current_admin, job_repo, page_repo, knowledge_repo)

