"""Unit tests for text chunker and table preservation."""

from app.ingestion.chunker import Chunker


def test_chunker_basic_splitting():
    chunker = Chunker(chunk_size=300, chunk_overlap=50)
    sample_text = (
        "Routica Explorer I is a robust mobile router designed for off-grid travelers.\n\n"
        "It features dual SIM slots and carrier aggregation for high-speed connectivity.\n\n"
        "Explorer II introduces 5G capabilities and Wi-Fi 6 technology for marine yachts and modern RVs."
    )
    chunks = chunker.split_text(sample_text)
    assert len(chunks) >= 1
    assert all("content" in c for c in chunks)
    assert all(len(c["content"]) >= 30 for c in chunks)


def test_chunker_preserves_markdown_tables():
    chunker = Chunker(chunk_size=500, chunk_overlap=50)
    table_text = (
        "### Product Specifications\n\n"
        "| Feature | Explorer I | Explorer II |\n"
        "| --- | --- | --- |\n"
        "| Cellular | 4G LTE Cat 12 | 5G Sub-6GHz + 4G LTE |\n"
        "| Wi-Fi | Wi-Fi 5 (802.11ac) | Wi-Fi 6 (802.11ax) |\n"
        "| SIM Slots | Dual Micro SIM | Dual Nano SIM + eSIM |\n"
    )
    chunks = chunker.split_text(table_text)
    assert len(chunks) == 1
    assert "Explorer I" in chunks[0]["content"]
    assert "Explorer II" in chunks[0]["content"]
    assert "|" in chunks[0]["content"]

