"""CSV document extraction using Pandas."""

import io
import pandas as pd
from app.core.exceptions import DocumentProcessingError
from app.core.logging import logger
from app.utils.text_cleaner import normalize_whitespace


class CSVProcessor:
    @staticmethod
    def extract_text(file_bytes: bytes) -> str:
        """Extracts structured key-value records from CSV bytes."""
        try:
            csv_str = file_bytes.decode("utf-8", errors="replace")
            df = pd.read_csv(io.StringIO(csv_str))
            df = df.dropna(how="all")

            lines = []
            for idx, row in df.iterrows():
                row_items = []
                for col in df.columns:
                    val = row[col]
                    if pd.notna(val):
                        row_items.append(f"{col}: {val}")
                if row_items:
                    lines.append(f"Record {idx + 1}: " + " | ".join(row_items))

            return normalize_whitespace("\n".join(lines))
        except Exception as exc:
            logger.error("Failed to extract CSV content: %s", exc)
            raise DocumentProcessingError(f"Could not extract content from CSV: {exc}")

