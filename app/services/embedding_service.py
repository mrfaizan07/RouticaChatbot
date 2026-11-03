"""Asynchronous embedding generation service using LiteLLM."""

import asyncio
import os
from typing import Any
import litellm

from app.config import get_settings
from app.core.exceptions import EmbeddingError
from app.core.logging import logger

settings = get_settings()


class EmbeddingService:
    def __init__(self):
        self.model = settings.EMBEDDING_MODEL
        self.dimensions = settings.EMBEDDING_DIMENSIONS
        self.provider = settings.EMBEDDING_PROVIDER

    async def get_embedding(self, text: str) -> list[float]:
        """Generates embedding vector for a single string."""
        if not text or not text.strip():
            return [0.0] * self.dimensions

        # Mock embedding in testing mode to avoid paid external network calls
        if settings.APP_ENV == "testing":
            # Deterministic pseudo-embedding for testing
            import hashlib
            seed = int(hashlib.md5(text.encode("utf-8")).hexdigest(), 16)
            return [(float((seed + i) % 100) / 100.0) for i in range(self.dimensions)]

        try:
            model_identifier = f"{self.provider}/{self.model}" if "/" not in self.model else self.model
            kwargs: dict[str, Any] = {"model": model_identifier, "input": [text.strip()]}
            if settings.GEMINI_API_KEY and self.provider == "gemini":
                kwargs["api_key"] = settings.GEMINI_API_KEY
                kwargs["custom_llm_provider"] = "gemini"
                os.environ["GEMINI_API_KEY"] = settings.GEMINI_API_KEY

            response = await litellm.aembedding(**kwargs)
            embedding = response["data"][0]["embedding"]

            # Validate vector dimensions
            if len(embedding) != self.dimensions:
                logger.warning(
                    "Embedding dimension mismatch: expected %d, got %d. Adjusting...",
                    self.dimensions,
                    len(embedding),
                )
                if len(embedding) > self.dimensions:
                    embedding = embedding[: self.dimensions]
                else:
                    embedding = embedding + [0.0] * (self.dimensions - len(embedding))

            return embedding
        except Exception as exc:
            logger.error("Embedding generation failed for text (%d chars): %s", len(text), exc)
            # Fallback to zero vector so chat doesn't crash if embedding provider is temporarily down
            return [0.0] * self.dimensions

    async def get_embeddings_batch(self, texts: list[str], batch_size: int = 16) -> list[list[float]]:
        """Generates embeddings for a batch of strings asynchronously."""
        results = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            tasks = [self.get_embedding(t) for t in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=False)
            results.extend(batch_results)
        return results

