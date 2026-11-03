"""Repository for structured Routica product records."""

from datetime import datetime, timezone
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.product import Product


class ProductRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["products"]

    async def get_by_id(self, product_id: str) -> Product | None:
        try:
            doc = await self.collection.find_one({"_id": ObjectId(product_id)})
            if doc:
                doc["_id"] = str(doc["_id"])
                return Product(**doc)
        except Exception:
            return None
        return None

    async def get_by_slug(self, slug: str) -> Product | None:
        doc = await self.collection.find_one({"product_slug": slug.lower().strip()})
        if doc:
            doc["_id"] = str(doc["_id"])
            return Product(**doc)
        return None

    async def upsert(self, product: Product) -> Product:
        product_dict = product.model_dump(by_alias=True, exclude={"id"})
        product_dict["updated_at"] = datetime.now(timezone.utc)
        result = await self.collection.update_one(
            {"product_slug": product.product_slug.lower().strip()},
            {"$set": product_dict},
            upsert=True,
        )
        if result.upserted_id:
            product.id = str(result.upserted_id)
        else:
            existing = await self.get_by_slug(product.product_slug)
            if existing:
                product.id = existing.id
        return product

    async def list_products(self, limit: int = 50, skip: int = 0) -> list[Product]:
        cursor = self.collection.find().skip(skip).limit(limit)
        products = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            products.append(Product(**doc))
        return products

    async def search_by_query(self, query: str) -> list[Product]:
        """Intelligent regex search matching products by name, slug, or relevant keywords."""
        import re

        clean_q = query.lower()
        # Direct product checks
        targets = []
        if "explorer 1" in clean_q or "explorer i" in clean_q or "explorer-i" in clean_q:
            targets.append("explorer-i")
        if "explorer 2" in clean_q or "explorer ii" in clean_q or "explorer-ii" in clean_q:
            targets.append("explorer-ii")
        if "sentry" in clean_q:
            targets.append("routica-sentry")
        if "company" in clean_q or "located" in clean_q or "owner" in clean_q or "who owns" in clean_q or "india" in clean_q or "shipping" in clean_q or "warranty" in clean_q:
            targets.append("routica-company-info")

        if targets:
            cursor = self.collection.find({"product_slug": {"$in": targets}})
            products = []
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                products.append(Product(**doc))
            if products:
                return products

        # If general search, extract meaningful keywords (>= 3 chars, skipping stop words)
        stop_words = {"what", "when", "where", "which", "with", "from", "that", "this", "have", "tell", "does", "about", "your", "more", "the", "and", "for", "are", "can", "how"}
        words = [re.escape(w) for w in re.findall(r"\b\w+\b", clean_q) if len(w) >= 3 and w not in stop_words]

        if not words:
            # Fallback to returning all flagship products
            return await self.list_products(limit=5)

        regex_pattern = "|".join(words)
        regex = {"$regex": regex_pattern, "$options": "i"}
        cursor = self.collection.find(
            {
                "$or": [
                    {"product_name": regex},
                    {"description": regex},
                    {"features": regex},
                    {"category": regex},
                    {"product_slug": regex},
                ]
            }
        ).limit(10)
        products = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            products.append(Product(**doc))
        return products
