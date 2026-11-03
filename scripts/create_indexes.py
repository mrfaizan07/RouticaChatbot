"""CLI script to initialize MongoDB standard B-tree indexes."""

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.core.logging import logger
from app.database.indexes import create_database_indexes
from app.database.mongodb import MongoDBManager


async def main():
    print("Connecting to MongoDB Atlas...")
    await MongoDBManager.connect()
    db = MongoDBManager.get_database()
    print("Creating indexes across all 8 collections...")
    created = await create_database_indexes(db)
    for col, idxs in created.items():
        print(f" - Collection '{col}': {idxs}")
    print("All indexes created successfully!")
    await MongoDBManager.close()


if __name__ == "__main__":
    asyncio.run(main())

