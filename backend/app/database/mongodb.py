"""MongoDB connection management using Motor (Async PyMongo driver)."""

import asyncio
import os
from typing import Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from app.config import get_settings
from app.core.exceptions import DatabaseConnectionError
from app.core.logging import logger

settings = get_settings()


class MongoDBManager:
    client: AsyncIOMotorClient | None = None
    database: AsyncIOMotorDatabase | None = None

    @classmethod
    async def connect(cls) -> None:
        """Initializes the MongoDB Motor client and tests connection."""
        current_env = os.getenv("APP_ENV", settings.APP_ENV).strip().lower()
        if current_env == "testing":
            logger.info("Running in testing mode: skipping live MongoDB connection.")
            return

        try:
            logger.info("Connecting to MongoDB Atlas...")
            cls.client = AsyncIOMotorClient(
                settings.MONGODB_URI,
                maxPoolSize=settings.MONGODB_MAX_POOL_SIZE,
                minPoolSize=settings.MONGODB_MIN_POOL_SIZE,
                serverSelectionTimeoutMS=2000,
                connectTimeoutMS=2000,
                uuidRepresentation="standard",
            )
            # Test connectivity with 2 second timeout
            await asyncio.wait_for(cls.client.admin.command("ping"), timeout=2.0)
            cls.database = cls.client[settings.MONGODB_DATABASE]
            logger.info("Successfully connected to MongoDB database: %s", settings.MONGODB_DATABASE)
        except (ConnectionFailure, ServerSelectionTimeoutError, asyncio.TimeoutError, Exception) as exc:
            logger.error("Failed to connect to MongoDB: %s", str(exc))
            if current_env == "production":
                raise DatabaseConnectionError(f"Production database connection failed: {exc}")
            logger.warning("Continuing in development/test mode without active MongoDB connection.")

    @classmethod
    async def close(cls) -> None:
        """Closes the MongoDB client connections."""
        if cls.client is not None:
            logger.info("Closing MongoDB connections...")
            cls.client.close()
            cls.client = None
            cls.database = None

    @classmethod
    async def ping(cls) -> bool:
        """Pings the database to verify live connectivity."""
        if settings.APP_ENV == "testing":
            return True
        if cls.client is None:
            return False
        try:
            await cls.client.admin.command("ping")
            return True
        except Exception:
            return False

    @classmethod
    def get_database(cls) -> AsyncIOMotorDatabase:
        """Returns the current database instance."""
        if cls.database is None:
            # In development fallback if called before startup lifespan
            if cls.client is not None:
                cls.database = cls.client[settings.MONGODB_DATABASE]
                return cls.database
            raise DatabaseConnectionError("MongoDB is not initialized. Please ensure the app lifecycle is running.")
        return cls.database

    @classmethod
    async def check_vector_index(cls, collection_name: str = "knowledge_chunks") -> dict[str, Any]:
        """Checks if the configured Atlas Vector Search index exists and is ready."""
        if cls.database is None:
            return {"status": "unavailable", "message": "Database disconnected"}

        try:
            collection = cls.database[collection_name]
            cursor = collection.list_search_indexes()
            indexes = await cursor.to_list(length=20)
            target_index = next((idx for idx in indexes if idx.get("name") == settings.VECTOR_SEARCH_INDEX_NAME), None)

            if target_index:
                queryable = target_index.get("queryable", False)
                status = target_index.get("status", "READY")
                return {
                    "status": "ready" if queryable or status == "READY" else "building",
                    "index_name": settings.VECTOR_SEARCH_INDEX_NAME,
                    "details": target_index,
                }
            return {
                "status": "missing",
                "index_name": settings.VECTOR_SEARCH_INDEX_NAME,
                "message": f"Search index '{settings.VECTOR_SEARCH_INDEX_NAME}' not found in '{collection_name}'.",
            }
        except Exception as exc:
            logger.warning("Error inspecting vector search index: %s", str(exc))
            return {
                "status": "unsupported_or_error",
                "message": f"Could not query Atlas search indexes: {exc}",
            }


# Fast dependency helper
async def get_db() -> AsyncIOMotorDatabase:
    """FastAPI dependency for accessing the database."""
    return MongoDBManager.get_database()
