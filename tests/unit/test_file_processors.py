"""Unit tests for document file extractors (CSV, JSON, DOCX, TXT)."""

import json
from app.file_processors.csv_processor import CSVProcessor
from app.file_processors.docx_processor import DOCXProcessor
from app.file_processors.json_processor import JSONProcessor


def test_csv_processor():
    csv_bytes = b"product,cellular,wifi\nExplorer I,4G LTE,WiFi 5\nExplorer II,5G,WiFi 6"
    extracted = CSVProcessor.extract_text(csv_bytes)
    assert "Explorer I" in extracted
    assert "Explorer II" in extracted
    assert "5G" in extracted


def test_json_processor():
    json_data = {
        "company": "Routica",
        "products": [
            {"name": "Explorer I", "type": "RV Router"},
            {"name": "Explorer II", "type": "Marine & Yacht Router"},
        ],
    }
    json_bytes = json.dumps(json_data).encode("utf-8")
    extracted = JSONProcessor.extract_text(json_bytes)
    assert "Routica" in extracted
    assert "Explorer I" in extracted
    assert "Marine & Yacht Router" in extracted

