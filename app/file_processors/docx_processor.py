"""DOCX document extraction using python-docx."""

import io
import docx
from app.core.exceptions import DocumentProcessingError
from app.core.logging import logger
from app.utils.text_cleaner import normalize_whitespace


class DOCXProcessor:
    @staticmethod
    def extract_text(file_bytes: bytes) -> str:
        """Extracts headings, paragraphs, and tables from DOCX bytes."""
        try:
            doc = docx.Document(io.BytesIO(file_bytes))
            sections = []

            # Paragraphs
            for p in doc.paragraphs:
                if p.text.strip():
                    sections.append(p.text.strip())

            # Tables
            for table in doc.tables:
                table_lines = []
                for row in table.rows:
                    cells = [c.text.strip() for c in row.cells]
                    if any(cells):
                        table_lines.append(" | ".join(cells))
                if table_lines:
                    sections.append("\n".join(table_lines))

            return normalize_whitespace("\n\n".join(sections))
        except Exception as exc:
            logger.error("Failed to extract DOCX content: %s", exc)
            raise DocumentProcessingError(f"Could not extract content from DOCX: {exc}")

