"""Repository for uploaded document metadata."""

from datetime import datetime, timezone
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.document import Document


class DocumentRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["documents"]

    async def create(self, doc: Document) -> Document:
        doc_dict = doc.model_dump(by_alias=True, exclude={"id"})
        result = await self.collection.insert_one(doc_dict)
        doc.id = str(result.inserted_id)
        return doc

    async def get_by_id(self, doc_id: str) -> Document | None:
        try:
            record = await self.collection.find_one({"_id": ObjectId(doc_id)})
            if record:
                record["_id"] = str(record["_id"])
                return Document(**record)
        except Exception:
            return None
        return None

    async def get_by_content_hash(self, content_hash: str) -> Document | None:
        record = await self.collection.find_one({"content_hash": content_hash})
        if record:
            record["_id"] = str(record["_id"])
            return Document(**record)
        return None

    async def update_status(
        self,
        doc_id: str,
        status: str,
        total_chunks: int = 0,
        error: str | None = None,
    ) -> None:
        update_data = {
            "processing_status": status,
            "total_chunks": total_chunks,
            "processing_error": error,
            "updated_at": datetime.now(timezone.utc),
        }
        try:
            await self.collection.update_one({"_id": ObjectId(doc_id)}, {"$set": update_data})
        except Exception:
            pass

    async def list_documents(self, limit: int = 50, skip: int = 0) -> list[Document]:
        cursor = self.collection.find().sort("created_at", -1).skip(skip).limit(limit)
        docs = []
        async for item in cursor:
            item["_id"] = str(item["_id"])
            docs.append(Document(**item))
        return docs

    async def delete(self, doc_id: str) -> bool:
        try:
            result = await self.collection.delete_one({"_id": ObjectId(doc_id)})
            return result.deleted_count > 0
        except Exception:
            return False

    async def count(self) -> int:
        return await self.collection.count_documents({})
