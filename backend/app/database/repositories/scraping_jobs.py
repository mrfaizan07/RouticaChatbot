"""Repository for scraping audit jobs."""

from datetime import datetime, timezone
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.scraping_job import ScrapingJob


class ScrapingJobRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["scraping_jobs"]

    async def create(self, job: ScrapingJob) -> ScrapingJob:
        job_dict = job.model_dump(by_alias=True, exclude={"id"})
        result = await self.collection.insert_one(job_dict)
        job.id = str(result.inserted_id)
        return job

    async def update(
        self,
        job_id: str,
        status: str,
        pages_discovered: int,
        pages_processed: int,
        pages_failed: int,
        error_summary: str | None = None,
    ) -> None:
        update_data = {
            "status": status,
            "pages_discovered": pages_discovered,
            "pages_processed": pages_processed,
            "pages_failed": pages_failed,
            "error_summary": error_summary,
        }
        if status in ("completed", "failed"):
            update_data["completed_at"] = datetime.now(timezone.utc)
        try:
            await self.collection.update_one({"_id": ObjectId(job_id)}, {"$set": update_data})
        except Exception:
            pass

    async def get_latest_job(self) -> ScrapingJob | None:
        doc = await self.collection.find_one(sort=[("started_at", -1)])
        if doc:
            doc["_id"] = str(doc["_id"])
            return ScrapingJob(**doc)
        return None

    async def list_jobs(self, limit: int = 20) -> list[ScrapingJob]:
        cursor = self.collection.find().sort("started_at", -1).limit(limit)
        jobs = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            jobs.append(ScrapingJob(**doc))
        return jobs
