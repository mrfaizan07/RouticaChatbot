"""Content deduplication using SHA-256 hashes."""

from app.utils.text_cleaner import compute_content_hash


class Deduplicator:
    @staticmethod
    def is_content_changed(old_hash: str | None, new_text: str) -> tuple[bool, str]:
        """Calculates hash of new content and returns (has_changed, new_hash)."""
        new_hash = compute_content_hash(new_text)
        if not old_hash:
            return True, new_hash
        return old_hash != new_hash, new_hash

    @staticmethod
    def filter_duplicate_chunks(chunks: list[dict]) -> list[dict]:
        """Deduplicates a list of chunk dicts by content hash."""
        seen_hashes = set()
        unique_chunks = []
        for ch in chunks:
            ch_hash = compute_content_hash(ch.get("content", ""))
            if ch_hash not in seen_hashes:
                seen_hashes.add(ch_hash)
                ch["content_hash"] = ch_hash
                unique_chunks.append(ch)
        return unique_chunks

