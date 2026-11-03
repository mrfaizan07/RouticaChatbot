"""CLI script to trigger initial crawl and indexing of routica.com."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.database.mongodb import MongoDBManager
from app.database.repositories.knowledge import KnowledgeRepository
from app.database.repositories.scraping_jobs import ScrapingJobRepository
from app.database.repositories.website_pages import WebsitePageRepository
from app.api.v1.scraping import run_crawl_task
from app.models.scraping_job import ScrapingJob


async def main():
    print("=== Initial Routica Website Ingestion ===")
    await MongoDBManager.connect()
    db = MongoDBManager.get_database()

    job_repo = ScrapingJobRepository(db)
    page_repo = WebsitePageRepository(db)
    knowledge_repo = KnowledgeRepository(db)

    job = ScrapingJob(job_type="initial_crawl", status="running")
    saved_job = await job_repo.create(job)
    job_id = str(saved_job.id)

    print(f"Starting crawl task for routica.com (Job ID: {job_id})...")
    await run_crawl_task(job_id, job_repo, page_repo, knowledge_repo)

    final_job = await job_repo.get_latest_job()
    print("\nCrawling Completed!")
    print(f" - Status: {final_job.status}")
    print(f" - Pages Discovered: {final_job.pages_discovered}")
    print(f" - Pages Processed: {final_job.pages_processed}")
    print(f" - Pages Failed: {final_job.pages_failed}")

    await MongoDBManager.close()


if __name__ == "__main__":
    asyncio.run(main())

