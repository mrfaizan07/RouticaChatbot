"""PDF document extraction using PyMuPDF."""

import pymupdf as fitz
from app.core.exceptions import DocumentProcessingError
from app.core.logging import logger
from app.utils.text_cleaner import normalize_whitespace


class PDFProcessor:
    @staticmethod
    def extract_text(file_bytes: bytes) -> str:
        """Extracts text and table layout from PDF bytes."""
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            extracted_pages = []
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text")
                if text.strip():
                    extracted_pages.append(f"--- PAGE {page_num + 1} ---\n{text.strip()}")
            doc.close()
            return normalize_whitespace("\n\n".join(extracted_pages))
        except Exception as exc:
            logger.error("Failed to extract PDF content: %s", exc)
            raise DocumentProcessingError(f"Could not extract content from PDF: {exc}")