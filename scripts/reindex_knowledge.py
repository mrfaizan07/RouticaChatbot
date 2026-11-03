"""CLI script to reindex all stored website pages and structured data into vector chunks."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.database.mongodb import MongoDBManager
from app.database.repositories.knowledge import KnowledgeRepository
from app.database.repositories.website_pages import WebsitePageRepository
from app.services.knowledge_service import KnowledgeService


async def main():
    print("=== Reindexing Knowledge Base ===")
    await MongoDBManager.connect()
    db = MongoDBManager.get_database()

    page_repo = WebsitePageRepository(db)
    knowledge_repo = KnowledgeRepository(db)
    knowledge_svc = KnowledgeService(knowledge_repo=knowledge_repo)

    pages = await page_repo.list_pages(limit=1000)
    print(f"Found {len(pages)} pages to re-index...")

    total_chunks = 0
    for idx, page in enumerate(pages, 1):
        if page.content:
            count = await knowledge_svc.ingest_content(
                source_id=str(page.id),
                source_type="website",
                source_title=page.title,
                source_url=page.canonical_url,
                raw_text=page.content,
                metadata={"page_type": page.page_type},
            )
            total_chunks += count
            print(f" [{idx}/{len(pages)}] {page.title[:40]}: {count} chunks")

    print(f"\nReindexing complete! Total chunks indexed: {total_chunks}")
    await MongoDBManager.close()


if __name__ == "__main__":
    asyncio.run(main())

