"""Excel document extraction using Pandas and openpyxl."""

import io
import pandas as pd
from app.core.exceptions import DocumentProcessingError
from app.core.logging import logger
from app.utils.text_cleaner import normalize_whitespace


class ExcelProcessor:
    @staticmethod
    def extract_text(file_bytes: bytes) -> str:
        """Extracts sheets and structured table records from Excel workbook."""
        try:
            excel_file = io.BytesIO(file_bytes)
            xls = pd.ExcelFile(excel_file, engine="openpyxl")
            sheet_sections = []

            for sheet_name in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet_name)
                # Drop all-NaN rows/cols
                df = df.dropna(how="all")
                if df.empty:
                    continue

                sheet_lines = [f"=== SHEET: {sheet_name} ==="]
                # Format each row as structured key-value pairs
                for idx, row in df.iterrows():
                    row_items = []
                    for col in df.columns:
                        val = row[col]
                        if pd.notna(val):
                            row_items.append(f"{col}: {val}")
                    if row_items:
                        sheet_lines.append(f"Row {idx + 1}: " + " | ".join(row_items))

                sheet_sections.append("\n".join(sheet_lines))

            return normalize_whitespace("\n\n".join(sheet_sections))
        except Exception as exc:
            logger.error("Failed to extract Excel content: %s", exc)
            raise DocumentProcessingError(f"Could not extract content from Excel: {exc}")

