"""One-off crawler and ingestion script to scrape and index all routica.com content into MongoDB."""

import asyncio
import os
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(".env")
load_dotenv("backend/.env")

from app.database.mongodb import MongoDBManager
from app.database.repositories.knowledge import KnowledgeRepository
from app.database.repositories.products import ProductRepository
from app.database.repositories.website_pages import WebsitePageRepository
from app.ingestion.crawler import RouticaCrawler
from app.ingestion.scraper import WebScraper
from app.models.product import Product
from app.models.website_page import WebsitePage
from app.services.knowledge_service import KnowledgeService
from app.utils.text_cleaner import compute_content_hash


PRODUCTS_METADATA = [
    {
        "product_name": "Routica Explorer I",
        "product_slug": "explorer-i",
        "category": "RV Internet Gateway Router",
        "description": "Routica Explorer I is a rugged wireless gateway router designed specifically for RVs, motorhomes, and campers. Available in 4G LTE Cat 4 and Cat 6 variants with built-in cellular modems for reliable mobile connectivity anywhere. Starting price is $329.00 USD for Cat 4 and $399.00 USD for Cat 6.",
        "specifications": {
            "Price": "Starting from $329.00 USD (Cat 4: $329.00, Cat 6: $399.00)",
            "Financing": "PayPal Pay in 4 (4 interest-free payments over 6 weeks)",
            "Cellular": "4G LTE Cat 4 (up to 150 Mbps) / Cat 6 (up to 300 Mbps)",
            "Wi-Fi": "2.4 GHz 802.11 b/g/n",
            "SIM": "Standard SIM slot with multi-carrier support (AT&T, T-Mobile, Verizon)",
            "Antennas": "High-gain external cellular and Wi-Fi antenna ports",
            "Power": "12V DC vehicle input with voltage protection",
            "GPS": "Built-in GPS tracking for trip logging",
            "Warranty": "30-day money-back guarantee",
            "Shipping": "Direct shipping across the United States and Canada via routica.com",
        },
        "features": [
            "Priced from $329.00 USD",
            "Built-in cellular modem - no USB dongles needed",
            "Dual-band Wi-Fi sharing throughout the RV",
            "Works on 12V DC RV house power directly",
            "GPS trip tracking and geo-fencing via Routica Cloud",
            "Hotspot sharing and guest Wi-Fi capability",
            "30-day full money-back guarantee",
        ],
        "source_url": "https://routica.com/explorer",
    },
    {
        "product_name": "Routica Explorer II",
        "product_slug": "explorer-ii",
        "category": "5G RV & Marine Internet Gateway Router",
        "description": "Routica Explorer II is the flagship next-generation 5G & Wi-Fi 6 Wireless Gateway Router engineered for extreme marine environments and premium RV connectivity. Delivers Gigabit speeds up to 3.4 Gbps, dual-SIM auto-failover, and ultra-low latency. Starting price is $499.00 USD.",
        "specifications": {
            "Price": "Starting from $499.00 USD",
            "Financing": "PayPal Pay in 4 (4 interest-free payments over 6 weeks)",
            "Cellular": "5G Sub-6 GHz (up to 3.4 Gbps) and CAT 12 fallback (up to 600 Mbps)",
            "Wi-Fi": "Wi-Fi 6 (802.11ax) dual-band (2.4 GHz + 5 GHz)",
            "SIM": "Dual SIM slots with automatic carrier failover",
            "Enclosure": "Marine-grade IP67 weather-resistant rugged casing",
            "Ethernet": "Gigabit Ethernet LAN/WAN ports",
            "GPS": "High-accuracy GNSS positioning",
            "Warranty": "30-day money-back guarantee",
            "Shipping": "Direct shipping across the United States and Canada via routica.com",
        },
        "features": [
            "Priced from $499.00 USD (Best Seller)",
            "Next-gen 5G high-speed streaming up to 3.4 Gbps on boats, yachts, and RVs",
            "Wi-Fi 6 technology supporting up to 128 simultaneous connected devices",
            "Dual SIM auto-failover for uninterrupted internet across carriers",
            "Marine-grade IP67 corrosion and water resistance",
            "Integrated Routica Sentry security and monitoring",
            "30-day full money-back guarantee",
        ],
        "source_url": "https://routica.com/explorer-ii",
    },
    {
        "product_name": "Routica Company & Availability Information",
        "product_slug": "routica-company-info",
        "category": "Company & Policies",
        "description": "Routica is a division of Ositech Communications Inc., located in Ontario, Canada's technology triangle. Ositech has over 25 years of experience delivering mission-critical wireless data solutions for healthcare, EMS, fire/rescue, and transportation.",
        "specifications": {
            "Parent Company": "Ositech Communications Inc.",
            "Headquarters": "Ontario, Canada",
            "Official Store": "https://routica.com/store (or https://routica.com/product-listing-page)",
            "Shipping Regions": "Direct web sales ship throughout the USA and Canada. For international orders (including India, UK, Europe, Australia), customers should contact Routica sales support at https://routica.com/company/contact-us for custom shipping and carrier band compatibility.",
            "Warranty & Return Policy": "30-day full money-back guarantee on hardware purchased directly through routica.com.",
            "Contact Email": "support@routica.com",
        },
        "features": [
            "Division of Ositech Communications Inc. with 25+ years in mobile data tech",
            "Based in Ontario, Canada",
            "30-day money-back guarantee on all routers",
            "Direct online store shipping to USA & Canada",
            "Dedicated customer support via https://routica.com/company/contact-us",
        ],
        "source_url": "https://routica.com/company/about-us",
    },
    {
        "product_name": "Routica Sentry & Cloud Services",
        "product_slug": "routica-sentry",
        "category": "Cloud & Security Services",
        "description": "Routica's comprehensive cloud companion service offering remote vehicle monitoring, Sentry security mode, trip tracking, and family hotspot sharing.",
        "specifications": {
            "Platform": "Web dashboard and iOS/Android mobile apps",
            "Features": "Trip logs, GPS alerts, data usage monitoring, security sensors",
        },
        "features": [
            "Remote status monitoring from anywhere in the world",
            "Real-time alerts for unexpected movement or power loss",
            "Trip sharing with friends and family",
            "Centralized data plan usage tracking",
        ],
        "source_url": "https://routica.com/explorer/sentry",
    },
]


async def main():
    print("Connecting to MongoDB Atlas...")
    await MongoDBManager.connect()
    db = MongoDBManager.get_database()

    knowledge_repo = KnowledgeRepository(db)
    product_repo = ProductRepository(db)
    page_repo = WebsitePageRepository(db)
    knowledge_svc = KnowledgeService(knowledge_repo=knowledge_repo)

    # 1. Seed structured products
    print("\n--- Ingesting Structured Products ---")
    for prod_data in PRODUCTS_METADATA:
        prod = Product(**prod_data)
        saved = await product_repo.upsert(prod)
        print(f"Product upserted: {saved.product_name} ({saved.product_slug})")

        # Ingest product as a knowledge chunk as well
        prod_doc = f"# {prod.product_name}\n\nCategory: {prod.category}\n\nDescription: {prod.description}\n\nKey Features:\n" + "\n".join([f"- {f}" for f in prod.features]) + "\n\nSpecifications:\n" + "\n".join([f"- {k}: {v}" for k, v in prod.specifications.items()])
        await knowledge_svc.ingest_content(
            source_id=f"prod_{saved.product_slug}",
            source_type="product",
            source_title=saved.product_name,
            source_url=saved.source_url,
            raw_text=prod_doc,
            metadata={"category": prod.category, "product_slug": prod.product_slug},
        )

    # 2. Discover URLs from routica.com
    print("\n--- Discovering Live URLs from routica.com ---")
    crawler = RouticaCrawler()
    discovered_urls = await crawler.discover_urls(max_pages=50)
    print(f"Discovered {len(discovered_urls)} URLs.")

    # 3. Scrape and index all pages
    scraper = WebScraper()
    success_count = 0
    total_chunks = 0

    print("\n--- Scraping and Ingesting Pages ---")
    dynamic_pages = ["product-listing-page", "general-policies", "refund_returns", "about-us", "contact-us", "faqs-and-knowledge-base"]
    for idx, url in enumerate(discovered_urls, start=1):
        try:
            is_dynamic = any(dp in url.lower() for dp in dynamic_pages)
            print(f"[{idx}/{len(discovered_urls)}] Scraping: {url} (browser={is_dynamic}) ...")
            page_data = await scraper.scrape_page(url, use_browser=is_dynamic)
            content = page_data.get("content", "").strip()
            title = page_data.get("title", "Routica Page")
            canonical = page_data.get("canonical_url", url)

            if len(content) < 100:
                print(f"  Skipped (content too short: {len(content)} chars)")
                continue

            page_model = WebsitePage(
                url=url,
                canonical_url=canonical,
                title=title,
                page_type=page_data.get("page_type", "general"),
                content=content,
                content_hash=compute_content_hash(content),
                status="indexed",
            )
            saved_page = await page_repo.upsert(page_model)
            page_id = str(saved_page.id)

            chunks_ingested = await knowledge_svc.ingest_content(
                source_id=page_id,
                source_type="website",
                source_title=title,
                source_url=canonical,
                raw_text=content,
                metadata={"page_type": page_data.get("page_type", "general")},
            )
            total_chunks += chunks_ingested
            success_count += 1
            print(f"  Ingested {chunks_ingested} chunks from '{title}'")
            await asyncio.sleep(0.3)
        except Exception as exc:
            print(f"  Failed to scrape {url}: {exc}")

    # Check database statistics
    print("\n================ INGESTION SUMMARY ================")
    print(f"Pages indexed: {success_count} / {len(discovered_urls)}")
    print(f"Total knowledge chunks in DB: {await knowledge_repo.count_chunks()}")
    print(f"Total products in DB: {len(await product_repo.list_products(limit=100))}")
    print("===================================================\n")


if __name__ == "__main__":
    asyncio.run(main())

