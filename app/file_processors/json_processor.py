"""JSON document extraction and structural flattening."""

import json
from app.core.exceptions import DocumentProcessingError
from app.core.logging import logger
from app.utils.text_cleaner import normalize_whitespace


class JSONProcessor:
    @staticmethod
    def extract_text(file_bytes: bytes) -> str:
        """Parses and formats JSON records into human- and vector-readable representations."""
        try:
            data = json.loads(file_bytes.decode("utf-8", errors="replace"))

            def flatten_item(item, prefix="") -> list[str]:
                lines = []
                if isinstance(item, dict):
                    for k, v in item.items():
                        new_prefix = f"{prefix}.{k}" if prefix else str(k)
                        lines.extend(flatten_item(v, new_prefix))
                elif isinstance(item, list):
                    for idx, elem in enumerate(item):
                        lines.extend(flatten_item(elem, f"{prefix}[{idx}]"))
                else:
                    lines.append(f"{prefix}: {item}")
                return lines

            lines = flatten_item(data)
            return normalize_whitespace("\n".join(lines))
        except Exception as exc:
            logger.error("Failed to parse JSON document: %s", exc)
            raise DocumentProcessingError(f"Could not extract content from JSON: {exc}")

