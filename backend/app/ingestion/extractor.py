"""HTML Content and specification extractor using BeautifulSoup."""

from bs4 import BeautifulSoup
from app.utils.text_cleaner import extract_table_as_markdown, normalize_whitespace
from app.utils.url_utils import normalize_canonical_url


class HTMLExtractor:
    @staticmethod
    def extract_page_data(html: str, url: str) -> dict:
        """Extracts title, clean content, tables, and page metadata from HTML string."""
        soup = BeautifulSoup(html, "html.parser")

        # 1. Title
        title = ""
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
        elif soup.find("h1"):
            title = soup.find("h1").get_text().strip()
        else:
            title = "Routica Knowledge"

        # 2. Canonical URL
        canonical_link = soup.find("link", rel="canonical")
        canonical_url = normalize_canonical_url(canonical_link.get("href") if canonical_link else url)

        # 3. Detect page type
        url_lower = canonical_url.lower()
        if "product" in url_lower or "explorer" in url_lower:
            page_type = "product"
        elif "solution" in url_lower or "rv" in url_lower or "marine" in url_lower or "boat" in url_lower:
            page_type = "solutions"
        elif "faq" in url_lower:
            page_type = "faq"
        elif "blog" in url_lower or "news" in url_lower:
            page_type = "blog"
        elif "privacy" in url_lower or "terms" in url_lower or "policy" in url_lower:
            page_type = "policy"
        else:
            page_type = "general"

        # 4. Extract tables as markdown before decomposing elements
        tables_markdown = []
        for table in soup.find_all("table"):
            table_md = extract_table_as_markdown(table)
            if table_md:
                tables_markdown.append(table_md)
            table.decompose()  # Remove so it doesn't get extracted twice as flattened text

        # 5. Remove irrelevant noise elements
        for noise in soup(["script", "style", "nav", "footer", "header", "noscript", "aside", "svg"]):
            noise.decompose()

        # 6. Extract structured text blocks (headings + paragraphs + lists)
        content_blocks = []
        for element in soup.find_all(["h1", "h2", "h3", "h4", "p", "li", "dl"]):
            text = normalize_whitespace(element.get_text())
            if not text:
                continue

            tag = element.name.lower()
            if tag.startswith("h"):
                level = tag[1]
                content_blocks.append(f"\n{'#' * int(level)} {text}")
            elif tag == "li":
                content_blocks.append(f"- {text}")
            else:
                content_blocks.append(text)

        # Append markdown tables to content
        if tables_markdown:
            content_blocks.append("\n### Product & Specification Tables")
            content_blocks.extend(tables_markdown)

        main_content = normalize_whitespace("\n\n".join(content_blocks))

        return {
            "title": title,
            "canonical_url": canonical_url,
            "page_type": page_type,
            "content": main_content,
        }

