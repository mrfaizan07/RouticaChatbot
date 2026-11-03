"""Crawler discovering URLs via sitemaps and navigation links."""

import asyncio
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import httpx

from app.config import get_settings
from app.core.exceptions import ScrapingSSRFError
from app.core.logging import logger
from app.utils.url_utils import normalize_canonical_url
from app.utils.validators import validate_crawl_url

settings = get_settings()


class RouticaCrawler:
    def __init__(self, start_url: str = "https://routica.com"):
        self.start_url = start_url
        self.user_agent = settings.SCRAPE_USER_AGENT

    async def discover_urls(self, max_pages: int = 50) -> list[str]:
        """Discovers public URLs by checking sitemap.xml first, then page links."""
        discovered: set[str] = set()

        # 1. Try sitemap.xml
        sitemap_urls = await self._fetch_sitemap(f"{self.start_url}/sitemap.xml")
        for u in sitemap_urls:
            try:
                valid_u = validate_crawl_url(u)
                discovered.add(normalize_canonical_url(valid_u))
                if len(discovered) >= max_pages:
                    return list(discovered)
            except Exception:
                continue

        # 2. Scrape root navigation links if sitemap was empty or insufficient
        if len(discovered) < 5:
            nav_urls = await self._discover_from_page(self.start_url)
            for u in nav_urls:
                try:
                    valid_u = validate_crawl_url(u)
                    discovered.add(normalize_canonical_url(valid_u))
                    if len(discovered) >= max_pages:
                        break
                except Exception:
                    continue

        # Ensure start_url is always included
        discovered.add(normalize_canonical_url(self.start_url))
        return list(discovered)[:max_pages]

    async def _fetch_sitemap(self, sitemap_url: str) -> list[str]:
        urls = []
        try:
            validate_crawl_url(sitemap_url)
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(sitemap_url, headers={"User-Agent": self.user_agent})
                if resp.status_code == 200:
                    root = ET.fromstring(resp.content)
                    # Handle namespaces
                    for elem in root.iter():
                        if elem.tag.endswith("loc") and elem.text:
                            urls.append(elem.text.strip())
        except Exception as exc:
            logger.info("Sitemap discovery skipped or unavailable at %s: %s", sitemap_url, exc)
        return urls

    async def _discover_from_page(self, page_url: str) -> list[str]:
        urls = []
        try:
            valid_url = validate_crawl_url(page_url)
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                resp = await client.get(valid_url, headers={"User-Agent": self.user_agent})
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "html.parser")
                    for a_tag in soup.find_all("a", href=True):
                        href = a_tag["href"]
                        try:
                            norm = normalize_canonical_url(href, base_url=page_url)
                            validate_crawl_url(norm)
                            urls.append(norm)
                        except Exception:
                            continue
        except Exception as exc:
            logger.warning("Failed to extract links from %s: %s", page_url, exc)
        return urls

