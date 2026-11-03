"""RAG Orchestrator coordinating retrieval, prompt formatting, LLM routing, and citations."""

import time
from typing import Any
from app.core.logging import logger
from app.prompts.system_prompt import ROUTICA_SYSTEM_PROMPT, build_rag_prompt
from app.services.citation_service import CitationService
from app.services.provider_router import ProviderRouter
from app.services.retrieval_service import RetrievalService


class RAGService:
    def __init__(
        self,
        retrieval_service: RetrievalService,
        provider_router: ProviderRouter | None = None,
    ):
        self.retrieval = retrieval_service
        self.router = provider_router or ProviderRouter()

    async def answer_question(
        self,
        query: str,
        conversation_history: list[dict[str, str]] | None = None,
        page_context: str | None = None,
    ) -> dict[str, Any]:
        """Runs the complete RAG pipeline synchronously returning structured answer and citations."""
        start_time = time.perf_counter()

        # 1. Retrieve knowledge chunks
        chunks = await self.retrieval.retrieve_context(query)
        citations = CitationService.extract_citations(chunks)

        # 2. Build grounded prompt
        user_prompt = build_rag_prompt(query, chunks, page_context=page_context)

        # 3. Assemble message list with conversation history window
        messages = [{"role": "system", "content": ROUTICA_SYSTEM_PROMPT}]
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_prompt})

        # 4. Execute with fallback
        llm_response = await self.router.execute_with_fallback(messages)
        duration_ms = int((time.perf_counter() - start_time) * 1000)

        return {
            "answer": llm_response["content"],
            "sources": [c.model_dump() for c in citations],
            "provider": llm_response["provider"],
            "model": llm_response["model"],
            "response_time_ms": duration_ms,
        }

    async def prepare_stream_context(
        self,
        query: str,
        conversation_history: list[dict[str, str]] | None = None,
        page_context: str | None = None,
    ) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
        """Prepares grounded messages and citations for SSE streaming."""
        chunks = await self.retrieval.retrieve_context(query)
        citations = CitationService.extract_citations(chunks)
        user_prompt = build_rag_prompt(query, chunks, page_context=page_context)

        messages = [{"role": "system", "content": ROUTICA_SYSTEM_PROMPT}]
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_prompt})

        return messages, [c.model_dump() for c in citations]

