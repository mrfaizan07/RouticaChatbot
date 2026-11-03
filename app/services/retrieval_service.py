"""Hybrid retrieval service: MongoDB Atlas Vector Search + Keyword + Structured Products."""

from typing import Any
from app.config import get_settings
from app.core.logging import logger
from app.database.repositories.knowledge import KnowledgeRepository
from app.database.repositories.products import ProductRepository
from app.services.embedding_service import EmbeddingService
from app.utils.text_cleaner import compute_content_hash

settings = get_settings()


class RetrievalService:
    def __init__(
        self,
        knowledge_repo: KnowledgeRepository,
        product_repo: ProductRepository,
        embedding_service: EmbeddingService | None = None,
    ):
        self.knowledge_repo = knowledge_repo
        self.product_repo = product_repo
        self.embedding_service = embedding_service or EmbeddingService()
        self.top_k = settings.RETRIEVAL_TOP_K
        self.score_threshold = settings.RETRIEVAL_SCORE_THRESHOLD

    async def retrieve_context(self, query: str) -> list[dict[str, Any]]:
        """Executes hybrid retrieval: vector search + keyword fallback + structured product lookup."""
        results: list[dict[str, Any]] = []
        seen_hashes = set()

        # 1. Structured product match
        try:
            matched_products = await self.product_repo.search_by_query(query)
            for prod in matched_products:
                spec_lines = [f"- {k}: {v}" for k, v in prod.specifications.items()]
                prod_content = f"Product: {prod.product_name}\nCategory: {prod.category}\nDescription: {prod.description}\nSpecifications:\n" + "\n".join(spec_lines)
                p_hash = compute_content_hash(prod_content)
                if p_hash not in seen_hashes:
                    seen_hashes.add(p_hash)
                    results.append({
                        "source_title": prod.product_name,
                        "source_url": prod.source_url,
                        "source_type": "product",
                        "content": prod_content,
                        "score": 0.95,
                    })
        except Exception as exc:
            logger.warning("Product lookup error: %s", exc)

        # 2. Vector Search
        try:
            query_vector = await self.embedding_service.get_embedding(query)
            vector_docs = await self.knowledge_repo.search_vector(
                query_vector=query_vector,
                top_k=self.top_k,
                score_threshold=self.score_threshold,
            )
            for doc in vector_docs:
                c_hash = compute_content_hash(doc.get("content", ""))
                if c_hash not in seen_hashes:
                    seen_hashes.add(c_hash)
                    results.append(doc)
        except Exception as exc:
            logger.warning("Vector search step failed or unavailable: %s", exc)

        # 3. Keyword / Text search fallback if vector search yielded few results
        if len(results) < self.top_k:
            try:
                keyword_docs = await self.knowledge_repo.search_keyword(
                    query=query,
                    limit=self.top_k - len(results),
                )
                for doc in keyword_docs:
                    c_hash = compute_content_hash(doc.get("content", ""))
                    if c_hash not in seen_hashes:
                        seen_hashes.add(c_hash)
                        results.append(doc)
            except Exception as exc:
                logger.warning("Keyword search fallback failed: %s", exc)

        # 4. Rank results by score descending
        results.sort(key=lambda x: x.get("score", 0.0), reverse=True)
        return results[: self.top_k]

