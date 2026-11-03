"""Script to ingest high-value technical blogs, setup guides, and Starlink integration articles."""

import asyncio
import os
import sys
import xml.etree.ElementTree as ET
import httpx

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(".env")
load_dotenv("backend/.env")

from app.database.mongodb import MongoDBManager
from app.database.repositories.knowledge import KnowledgeRepository
from app.database.repositories.website_pages import WebsitePageRepository
from app.ingestion.scraper import WebScraper
from app.models.website_page import WebsitePage
from app.services.knowledge_service import KnowledgeService
from app.utils.text_cleaner import compute_content_hash

HIGH_VALUE_KEYWORDS = [
    "install", "starlink", "carrier", "setup", "troubleshoot", "faq", "compare",
    "usb", "cost", "how-to", "guide", "best", "5g", "wi-fi", "sentry", "metal",
    "remote-work", "offline", "antennas", "sim", "failover", "security", "campground"
]

async def main():
    print("Connecting to MongoDB Atlas...")
    await MongoDBManager.connect()
    db = MongoDBManager.get_database()

    page_repo = WebsitePageRepository(db)
    know_repo = KnowledgeRepository(db)
    knowledge_svc = KnowledgeService(knowledge_repo=know_repo)
    scraper = WebScraper()

    # 1. Fetch post-sitemap.xml
    print("Fetching post-sitemap.xml...")
    async with httpx.AsyncClient(headers={"User-Agent": "Mozilla/5.0"}, timeout=15.0) as client:
        res = await client.get("https://routica.com/post-sitemap.xml")
        root = ET.fromstring(res.content)
        all_posts = []
        for loc in root.iter():
            if loc.tag.endswith("loc") and loc.text:
                u = loc.text.strip()
                if not any(u.endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif"]):
                    all_posts.append(u)

    print(f"Total articles found: {len(all_posts)}")

    # 2. Filter high-value articles
    selected_blogs = []
    for p in all_posts:
        p_lower = p.lower()
        if any(k in p_lower for k in HIGH_VALUE_KEYWORDS):
            selected_blogs.append(p)

    print(f"Selected {len(selected_blogs)} high-value technical and guide articles for indexing.")

    # 3. Check already indexed
    already_indexed = set()
    cursor = db["website_pages"].find({}, {"url": 1, "canonical_url": 1})
    async for doc in cursor:
        if "url" in doc:
            already_indexed.add(doc["url"].rstrip("/"))
        if "canonical_url" in doc:
            already_indexed.add(doc["canonical_url"].rstrip("/"))

    to_scrape = [u for u in selected_blogs if u.rstrip("/") not in already_indexed]
    print(f"Articles remaining to scrape and index: {len(to_scrape)}")

    success = 0
    total_chunks = 0
    for idx, url in enumerate(to_scrape, start=1):
        try:
            print(f"[{idx}/{len(to_scrape)}] Ingesting blog: {url} ...")
            page_data = await scraper.scrape_page(url, use_browser=False)
            content = page_data.get("content", "").strip()
            title = page_data.get("title", "Routica Guide")
            canonical = page_data.get("canonical_url", url)

            if len(content) < 200:
                print(f"  Skipped (content too short: {len(content)} chars)")
                continue

            page_model = WebsitePage(
                url=url,
                canonical_url=canonical,
                title=title,
                page_type="blog",
                content=content,
                content_hash=compute_content_hash(content),
                status="indexed",
            )
            saved_page = await page_repo.upsert(page_model)
            page_id = str(saved_page.id)

            chunks = await knowledge_svc.ingest_content(
                source_id=page_id,
                source_type="blog",
                source_title=title,
                source_url=canonical,
                raw_text=content,
                metadata={"page_type": "blog"},
            )
            total_chunks += chunks
            success += 1
            print(f"  Ingested {chunks} chunks from '{title}'")
            # Polite delay to respect Gemini free-tier RPM
            await asyncio.sleep(2.0)
        except Exception as exc:
            print(f"  Error on {url}: {exc}")
            await asyncio.sleep(3.0)

    print("\n================ BLOG INGESTION SUMMARY ================")
    print(f"Successfully indexed: {success} new guide articles")
    print(f"Total pages now in DB: {await page_repo.count()}")
    print(f"Total knowledge chunks now in DB: {await know_repo.count_chunks()}")
    print("========================================================\n")

if __name__ == "__main__":
    asyncio.run(main())

