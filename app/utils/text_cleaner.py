"""Text cleaning, normalization, and content hashing utilities."""

import hashlib
import re
import unicodedata
from bs4 import BeautifulSoup


def compute_content_hash(text: str) -> str:
    """Computes SHA-256 hash of normalized content."""
    normalized = normalize_whitespace(text)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def normalize_whitespace(text: str) -> str:
    """Collapses consecutive spaces and excessive blank lines."""
    if not text:
        return ""
    # Normalize unicode
    text = unicodedata.normalize("NFKC", text)
    # Replace carriage returns
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Replace multiple spaces/tabs with single space
    text = re.sub(r"[ \t]+", " ", text)
    # Replace 3 or more newlines with two
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def clean_html(html_content: str) -> str:
    """Strips irrelevant HTML tags, scripts, and styles while preserving structure."""
    if not html_content:
        return ""

    soup = BeautifulSoup(html_content, "html.parser")

    # Remove non-content tags
    for tag in soup(["script", "style", "noscript", "iframe", "svg", "header", "footer", "nav", "aside"]):
        tag.decompose()

    # Extract text with line breaks
    text = soup.get_text(separator="\n")
    return normalize_whitespace(text)


def extract_table_as_markdown(table_element) -> str:
    """Converts an HTML table element into readable markdown format."""
    rows = []
    for tr in table_element.find_all("tr"):
        cells = [normalize_whitespace(td.get_text()) for td in tr.find_all(["th", "td"])]
        if any(cells):
            rows.append(cells)

    if not rows:
        return ""

    # Normalize column count
    max_cols = max(len(row) for row in rows)
    normalized_rows = [row + [""] * (max_cols - len(row)) for row in rows]

    header = normalized_rows[0]
    separator = ["---"] * max_cols
    markdown_lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(separator) + " |",
    ]

    for row in normalized_rows[1:]:
        markdown_lines.append("| " + " | ".join(row) + " |")

    return "\n".join(markdown_lines)

