"""Knowledge service managing chunking, embeddings, and vector index sync."""

from typing import Any
from app.config import get_settings
from app.core.exceptions import DocumentProcessingError
from app.core.logging import logger
from app.database.repositories.knowledge import KnowledgeRepository
from app.ingestion.chunker import Chunker
from app.ingestion.deduplicator import Deduplicator
from app.models.knowledge import KnowledgeChunk
from app.services.embedding_service import EmbeddingService
from app.utils.text_cleaner import compute_content_hash

settings = get_settings()


class KnowledgeService:
    def __init__(
        self,
        knowledge_repo: KnowledgeRepository,
        embedding_service: EmbeddingService | None = None,
        chunker: Chunker | None = None,
    ):
        self.knowledge_repo = knowledge_repo
        self.embedding = embedding_service or EmbeddingService()
        self.chunker = chunker or Chunker()

    async def ingest_content(
        self,
        source_id: str,
        source_type: str,
        source_title: str,
        source_url: str,
        raw_text: str,
        metadata: dict[str, Any] | None = None,
    ) -> int:
        """Chunks content, generates embeddings, and saves active KnowledgeChunks."""
        if not raw_text or len(raw_text.strip()) < 30:
            logger.warning("Skipping ingestion for %s: text too short", source_title)
            return 0

        # Delete existing chunks for this source to ensure idempotency
        await self.knowledge_repo.delete_by_source_id(source_id)

        meta = dict(metadata or {})
        meta["source_id"] = source_id
        meta["source_type"] = source_type
        meta["source_title"] = source_title

        chunks = self.chunker.split_text(raw_text, metadata=meta)
        unique_chunks = Deduplicator.filter_duplicate_chunks(chunks)

        if not unique_chunks:
            return 0

        texts = [c["content"] for c in unique_chunks]
        embeddings = await self.embedding.get_embeddings_batch(texts)

        chunk_models = []
        for idx, (ch, emb) in enumerate(zip(unique_chunks, embeddings)):
            chunk_models.append(
                KnowledgeChunk(
                    source_id=source_id,
                    source_type=source_type,
                    source_title=source_title,
                    source_url=source_url,
                    chunk_index=idx,
                    content=ch["content"],
                    embedding=emb,
                    embedding_model=self.embedding.model,
                    embedding_dimensions=self.embedding.dimensions,
                    content_hash=ch.get("content_hash", compute_content_hash(ch["content"])),
                    metadata=ch.get("metadata", {}),
                    is_active=True,
                )
            )

        await self.knowledge_repo.insert_chunks_batch(chunk_models)
        logger.info("Successfully ingested %d chunks for source: %s", len(chunk_models), source_title)
        return len(chunk_models)

    async def remove_source_knowledge(self, source_id: str) -> int:
        """Removes all chunks associated with a source."""
        return await self.knowledge_repo.delete_by_source_id(source_id)
