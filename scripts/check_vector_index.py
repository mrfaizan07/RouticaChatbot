"""CLI script to check MongoDB Atlas Vector Search index status."""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.config import get_settings
from app.database.mongodb import MongoDBManager

settings = get_settings()


async def main():
    print(f"Checking MongoDB Atlas Vector Search index for database '{settings.MONGODB_DATABASE}'...")
    await MongoDBManager.connect()

    res = await MongoDBManager.check_vector_index(collection_name="knowledge_chunks")
    print("\nVector Search Index Status:")
    print(json.dumps(res, indent=2))

    if res.get("status") not in ("ready", "READY"):
        print("\n--- HOW TO CONFIGURE ATLAS VECTOR SEARCH IN MONGODB ATLAS ---")
        print("1. Log in to your MongoDB Atlas dashboard (https://cloud.mongodb.com).")
        print("2. Navigate to your Database -> Atlas Search -> 'Create Search Index'.")
        print("3. Choose 'Atlas Vector Search' -> JSON Editor.")
        print(f"4. Target Database: {settings.MONGODB_DATABASE}, Collection: knowledge_chunks.")
        print(f"5. Name: {settings.VECTOR_SEARCH_INDEX_NAME}")
        print("6. Paste the following JSON definition:\n")
        index_def = {
            "fields": [
                {
                    "type": "vector",
                    "path": "embedding",
                    "numDimensions": settings.EMBEDDING_DIMENSIONS,
                    "similarity": "cosine",
                },
                {"type": "filter", "path": "is_active"},
                {"type": "filter", "path": "source_type"},
            ]
        }
        print(json.dumps(index_def, indent=2))
        print("\n7. Click 'Next' and 'Create Search Index'. It will take 1-2 minutes to build.")

    await MongoDBManager.close()


if __name__ == "__main__":
    asyncio.run(main())

