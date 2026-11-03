"""Chat service managing end-to-end user chat conversations and SSE streaming."""

import json
import time
from typing import AsyncGenerator
from app.config import get_settings
from app.core.logging import logger
from app.database.repositories.conversations import ConversationRepository
from app.models.conversation import Message
from app.schemas.chat import ChatRequest, ChatResponse, CitationSource
from app.services.provider_router import ProviderRouter
from app.services.rag_service import RAGService

settings = get_settings()


class ChatService:
    def __init__(
        self,
        conv_repo: ConversationRepository,
        rag_service: RAGService,
        router: ProviderRouter | None = None,
    ):
        self.conv_repo = conv_repo
        self.rag = rag_service
        self.router = router or ProviderRouter()

    async def handle_chat_message(self, request: ChatRequest, session_id: str) -> ChatResponse:
        """Processes standard JSON chat request and saves messages asynchronously."""
        start_time = time.perf_counter()

        # 1. Retrieve or create conversation
        conv = None
        if request.conversation_id:
            conv = await self.conv_repo.get_conversation(request.conversation_id, session_id=session_id)
        if not conv:
            conv = await self.conv_repo.create_conversation(
                session_id=session_id,
                title=request.message[:40] + "...",
            )

        conv_id = str(conv.id)

        # 2. Fetch recent conversation history
        history = await self.conv_repo.get_recent_history(
            conv_id=conv_id,
            max_messages=settings.MAX_CONVERSATION_HISTORY,
        )

        # 3. Save incoming user message
        user_msg = Message(
            conversation_id=conv_id,
            role="user",
            content=request.message,
        )
        await self.conv_repo.add_message(user_msg)

        # 4. Generate answer via RAG
        rag_result = await self.rag.answer_question(
            query=request.message,
            conversation_history=history,
            page_context=request.page_context,
        )

        duration_ms = int((time.perf_counter() - start_time) * 1000)

        # 5. Save assistant response
        assistant_msg = Message(
            conversation_id=conv_id,
            role="assistant",
            content=rag_result["answer"],
            sources=rag_result["sources"],
            model_used=rag_result["model"],
            provider_used=rag_result["provider"],
            response_time_ms=duration_ms,
        )
        saved_assistant = await self.conv_repo.add_message(assistant_msg)

        sources = [CitationSource(**s) for s in rag_result["sources"]]

        return ChatResponse(
            conversation_id=conv_id,
            message_id=str(saved_assistant.id),
            answer=rag_result["answer"],
            sources=sources,
            provider=rag_result["provider"],
            model=rag_result["model"],
            response_time_ms=duration_ms,
            created_at=saved_assistant.created_at,
        )

    async def stream_chat_message(
        self,
        request: ChatRequest,
        session_id: str,
    ) -> AsyncGenerator[str, None]:
        """Streams response tokens using Server-Sent Events (SSE)."""
        start_time = time.perf_counter()

        # 1. Resolve conversation
        conv = None
        if request.conversation_id:
            conv = await self.conv_repo.get_conversation(request.conversation_id, session_id=session_id)
        if not conv:
            conv = await self.conv_repo.create_conversation(
                session_id=session_id,
                title=request.message[:40] + "...",
            )

        conv_id = str(conv.id)

        # Initial event: status
        yield f"event: status\ndata: {json.dumps({'status': 'retrieving', 'conversation_id': conv_id})}\n\n"

        history = await self.conv_repo.get_recent_history(
            conv_id=conv_id,
            max_messages=settings.MAX_CONVERSATION_HISTORY,
        )

        user_msg = Message(
            conversation_id=conv_id,
            role="user",
            content=request.message,
        )
        await self.conv_repo.add_message(user_msg)

        # Prepare context and sources
        try:
            messages, sources = await self.rag.prepare_stream_context(
                query=request.message,
                conversation_history=history,
                page_context=request.page_context,
            )
        except Exception as exc:
            logger.warning("RAG context preparation degraded: %s", exc)
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are Routica AI Assistant, an intelligent website assistant for Routica (routica.com). "
                        "You help users with Routica Explorer I, Explorer II, RV connectivity, marine/boat connectivity, "
                        "high-speed Internet solutions, troubleshooting, and specifications."
                    ),
                }
            ]
            for h in history:
                messages.append({"role": h.role, "content": h.content})
            messages.append({"role": "user", "content": request.message})
            sources = []

        # Send sources event early so UI can show citations
        yield f"event: sources\ndata: {json.dumps({'sources': sources})}\n\n"

        try:
            token_gen, chosen_model, provider_name = await self.router.execute_stream_with_fallback(messages)
            collected_tokens = []

            async for token in token_gen:
                collected_tokens.append(token)
                yield f"event: token\ndata: {json.dumps({'token': token})}\n\n"

            full_answer = "".join(collected_tokens)
            duration_ms = int((time.perf_counter() - start_time) * 1000)

            # Save assistant message
            assistant_msg = Message(
                conversation_id=conv_id,
                role="assistant",
                content=full_answer,
                sources=sources,
                model_used=chosen_model,
                provider_used=provider_name,
                response_time_ms=duration_ms,
            )
            saved_msg = await self.conv_repo.add_message(assistant_msg)

            # Completion event
            complete_payload = {
                "message_id": str(saved_msg.id),
                "conversation_id": conv_id,
                "model": chosen_model,
                "provider": provider_name,
                "duration_ms": duration_ms,
            }
            yield f"event: complete\ndata: {json.dumps(complete_payload)}\n\n"

        except Exception as exc:
            logger.error("SSE stream error: %s", exc)
            yield f"event: error\ndata: {json.dumps({'error': 'Response generation failed. Please try again.'})}\n\n"

