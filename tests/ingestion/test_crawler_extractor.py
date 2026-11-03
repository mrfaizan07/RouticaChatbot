"""Unit and integration tests for HTML extraction, change detection, and sitemap handling."""

from app.ingestion.deduplicator import Deduplicator
from app.ingestion.extractor import HTMLExtractor
from app.utils.text_cleaner import compute_content_hash


def test_html_extractor_parses_content_and_tables():
    sample_html = """
    <html>
        <head>
            <title>Routica Explorer II - Marine & RV 5G Router</title>
            <link rel="canonical" href="https://routica.com/explorer-ii" />
        </head>
        <body>
            <header><nav><a href="/">Home</a></nav></header>
            <main>
                <h1>Explorer II 5G Connectivity</h1>
                <p>Designed for yachts, boats, and off-grid RVs with seamless dual-SIM failover.</p>
                <table>
                    <tr><th>Cellular</th><th>Wi-Fi</th></tr>
                    <tr><td>5G Sub-6GHz</td><td>Wi-Fi 6</td></tr>
                </table>
            </main>
            <footer><p>Copyright 2026 Routica</p></footer>
        </body>
    </html>
    """
    data = HTMLExtractor.extract_page_data(sample_html, url="https://routica.com/explorer-ii")

    assert data["title"] == "Routica Explorer II - Marine & RV 5G Router"
    assert data["canonical_url"] == "https://routica.com/explorer-ii"
    assert "Explorer II 5G Connectivity" in data["content"]
    assert "5G Sub-6GHz" in data["content"]
    assert "Home" not in data["content"]  # header nav removed


def test_deduplicator_change_detection():
    text_v1 = "Initial content about Routica RV connectivity."
    hash_v1 = compute_content_hash(text_v1)

    changed, new_hash = Deduplicator.is_content_changed(hash_v1, text_v1)
    assert changed is False
    assert new_hash == hash_v1

    text_v2 = "Updated content about Routica RV and Marine connectivity."
    changed_v2, new_hash_v2 = Deduplicator.is_content_changed(hash_v1, text_v2)
    assert changed_v2 is True
    assert new_hash_v2 != hash_v1

