"""Repository for vector knowledge chunks in MongoDB Atlas."""

from datetime import datetime, timezone
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.config import get_settings
from app.core.logging import logger
from app.models.knowledge import KnowledgeChunk

settings = get_settings()


class KnowledgeRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["knowledge_chunks"]

    async def insert_chunk(self, chunk: KnowledgeChunk) -> KnowledgeChunk:
        chunk_dict = chunk.model_dump(by_alias=True, exclude={"id"})
        result = await self.collection.insert_one(chunk_dict)
        chunk.id = str(result.inserted_id)
        return chunk

    async def insert_chunks_batch(self, chunks: list[KnowledgeChunk]) -> list[str]:
        if not chunks:
            return []
        docs = [chunk.model_dump(by_alias=True, exclude={"id"}) for chunk in chunks]
        result = await self.collection.insert_many(docs)
        return [str(_id) for _id in result.inserted_ids]

    async def delete_by_source_id(self, source_id: str) -> int:
        result = await self.collection.delete_many({"source_id": source_id})
        return result.deleted_count

    async def search_vector(
        self,
        query_vector: list[float],
        top_k: int = 5,
        score_threshold: float = 0.6,
    ) -> list[dict]:
        """Performs vector search using MongoDB Atlas $vectorSearch pipeline stage."""
        pipeline = [
            {
                "$vectorSearch": {
                    "index": settings.VECTOR_SEARCH_INDEX_NAME,
                    "path": "embedding",
                    "queryVector": query_vector,
                    "numCandidates": max(top_k * 10, 50),
                    "limit": top_k,
                    "filter": {"is_active": {"$eq": True}},
                }
            },
            {
                "$project": {
                    "_id": 1,
                    "source_id": 1,
                    "source_type": 1,
                    "source_title": 1,
                    "source_url": 1,
                    "chunk_index": 1,
                    "content": 1,
                    "metadata": 1,
                    "score": {"$meta": "vectorSearchScore"},
                }
            },
        ]
        results = []
        try:
            cursor = self.collection.aggregate(pipeline)
            async for doc in cursor:
                score = doc.get("score", 0.0)
                if score >= score_threshold:
                    doc["_id"] = str(doc["_id"])
                    results.append(doc)
        except Exception as exc:
            logger.warning("Atlas vector search pipeline failed or unsupported: %s", str(exc))
            # Graceful fallback: return empty list so keyword / hybrid search can proceed
            return []
        return results

    async def search_keyword(self, query: str, limit: int = 5) -> list[dict]:
        """Fallback text/regex search across active chunks."""
        regex = {"$regex": query, "$options": "i"}
        cursor = self.collection.find(
            {
                "is_active": True,
                "$or": [
                    {"content": regex},
                    {"source_title": regex},
                ],
            }
        ).limit(limit)

        results = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            doc["score"] = 0.7  # nominal keyword match score
            results.append(doc)
        return results

    async def count_chunks(self) -> int:
        return await self.collection.count_documents({"is_active": True})

    async def delete_chunk(self, chunk_id: str) -> bool:
        try:
            result = await self.collection.delete_one({"_id": ObjectId(chunk_id)})
            return result.deleted_count > 0
        except Exception:
            return False

    async def list_chunks(self, limit: int = 50, skip: int = 0) -> list[KnowledgeChunk]:
        cursor = self.collection.find({"is_active": True}).skip(skip).limit(limit)
        chunks = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            chunks.append(KnowledgeChunk(**doc))
        return chunks
