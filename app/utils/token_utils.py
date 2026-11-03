"""Token estimation utilities."""


def estimate_token_count(text: str) -> int:
    """Estimates tokens for prompt construction (approx 4 chars per token)."""
    if not text:
        return 0
    return max(1, len(text) // 4)


def truncate_to_max_tokens(text: str, max_tokens: int) -> str:
    """Truncates text to approximately fit within max token bounds."""
    max_chars = max_tokens * 4
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "..."

