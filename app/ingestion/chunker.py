"""Intelligent text chunker preserving markdown tables, headings, and specifications."""

import re
from typing import Any
from app.core.constants import DEFAULT_CHUNK_OVERLAP, DEFAULT_CHUNK_SIZE
from app.utils.text_cleaner import normalize_whitespace


class Chunker:
    def __init__(
        self,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str, metadata: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Splits text into contextually cohesive chunks, respecting paragraph and table boundaries."""
        if not text:
            return []

        # Split on markdown headers or double newlines first
        sections = re.split(r"(\n#{1,4}\s+[^\n]+|\n={3,}[^\n]*|\n-{3,}[^\n]*)", text)
        reconstructed_blocks = []
        current_block = ""

        for part in sections:
            if not part:
                continue
            if re.match(r"^(\n#{1,4}\s+|\n={3,}|\n-{3,})", part):
                if current_block.strip():
                    reconstructed_blocks.append(current_block.strip())
                current_block = part.strip() + "\n"
            else:
                current_block += part

        if current_block.strip():
            reconstructed_blocks.append(current_block.strip())

        chunks = []
        running_chunk = ""

        for block in reconstructed_blocks:
            # If adding this block exceeds chunk_size, flush current chunk
            if len(running_chunk) + len(block) > self.chunk_size and running_chunk:
                chunks.append(normalize_whitespace(running_chunk))
                # Retain overlap from end of running_chunk
                running_chunk = running_chunk[-self.chunk_overlap:] if len(running_chunk) > self.chunk_overlap else ""

            # If single block is huge, split on paragraphs or sentences
            if len(block) > self.chunk_size:
                sub_parts = block.split("\n\n")
                for sp in sub_parts:
                    if len(running_chunk) + len(sp) > self.chunk_size and running_chunk:
                        chunks.append(normalize_whitespace(running_chunk))
                        running_chunk = running_chunk[-self.chunk_overlap:] if len(running_chunk) > self.chunk_overlap else ""
                    running_chunk += ("\n\n" if running_chunk else "") + sp
            else:
                running_chunk += ("\n\n" if running_chunk else "") + block

        if running_chunk.strip():
            chunks.append(normalize_whitespace(running_chunk))

        result = []
        for idx, chunk_text in enumerate(chunks):
            if len(chunk_text) >= 50:  # Skip tiny fragments
                chunk_meta = dict(metadata or {})
                chunk_meta["chunk_index"] = idx
                result.append({"content": chunk_text, "metadata": chunk_meta})

        return result

