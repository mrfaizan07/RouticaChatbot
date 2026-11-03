"""Web scraping engine supporting Playwright (for JS rendering) and HTTPX fallback."""

import asyncio
import httpx
from app.config import get_settings
from app.core.exceptions import ScrapingSSRFError
from app.core.logging import logger
from app.ingestion.extractor import HTMLExtractor
from app.utils.validators import validate_crawl_url

settings = get_settings()


class WebScraper:
    def __init__(self):
        self.user_agent = settings.SCRAPE_USER_AGENT

    async def scrape_page(self, url: str, use_browser: bool = False) -> dict:
        """Validates URL security, fetches HTML, and extracts structured content."""
        clean_url = validate_crawl_url(url)

        if use_browser:
            return await self._scrape_with_playwright(clean_url)
        return await self._scrape_with_httpx(clean_url)

    async def _scrape_with_httpx(self, url: str) -> dict:
        headers = {"User-Agent": self.user_agent}
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            try:
                response = await client.get(url, headers=headers)
                # Re-validate redirect destination for SSRF prevention
                validate_crawl_url(str(response.url))

                if response.status_code != 200:
                    raise ScrapingSSRFError(f"HTTP request to {url} returned status {response.status_code}")

                html = response.text
                return HTMLExtractor.extract_page_data(html, str(response.url))
            except Exception as exc:
                logger.warning("HTTPX scrape failed for %s: %s. Attempting Playwright...", url, exc)
                return await self._scrape_with_playwright(url)

    async def _scrape_with_playwright(self, url: str) -> dict:
        from playwright.async_api import async_playwright

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page(user_agent=self.user_agent)
                await page.goto(url, wait_until="domcontentloaded", timeout=20000)
                final_url = page.url
                validate_crawl_url(final_url)

                html = await page.content()
                await browser.close()
                return HTMLExtractor.extract_page_data(html, final_url)
        except Exception as exc:
            logger.error("Playwright scraping failed for %s: %s", url, exc)
            raise ScrapingSSRFError(f"Failed to scrape {url}: {exc}")

