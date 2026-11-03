"""Repository for scraped Routica website pages."""

from datetime import datetime, timezone
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.website_page import WebsitePage


class WebsitePageRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["website_pages"]

    async def get_by_id(self, page_id: str) -> WebsitePage | None:
        try:
            doc = await self.collection.find_one({"_id": ObjectId(page_id)})
            if doc:
                doc["_id"] = str(doc["_id"])
                return WebsitePage(**doc)
        except Exception:
            return None
        return None

    async def get_by_canonical_url(self, canonical_url: str) -> WebsitePage | None:
        doc = await self.collection.find_one({"canonical_url": canonical_url})
        if doc:
            doc["_id"] = str(doc["_id"])
            return WebsitePage(**doc)
        return None

    async def upsert(self, page: WebsitePage) -> WebsitePage:
        page_dict = page.model_dump(by_alias=True, exclude={"id"})
        page_dict["last_updated_at"] = datetime.now(timezone.utc)
        result = await self.collection.update_one(
            {"canonical_url": page.canonical_url},
            {"$set": page_dict},
            upsert=True,
        )
        if result.upserted_id:
            page.id = str(result.upserted_id)
        else:
            existing = await self.get_by_canonical_url(page.canonical_url)
            if existing:
                page.id = existing.id
        return page

    async def list_pages(self, limit: int = 100, skip: int = 0) -> list[WebsitePage]:
        cursor = self.collection.find().skip(skip).limit(limit)
        pages = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            pages.append(WebsitePage(**doc))
        return pages

    async def count(self) -> int:
        return await self.collection.count_documents({})
