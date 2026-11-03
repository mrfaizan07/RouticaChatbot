"""Chat and SSE streaming endpoints."""

from fastapi import APIRouter, Depends, Header, Request, status
from fastapi.responses import StreamingResponse

from app.core.exceptions import ValidationException
from app.dependencies import (
    get_conversation_repo,
    get_knowledge_repo,
    get_product_repo,
    get_session_id,
)
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService
from app.services.rag_service import RAGService
from app.services.retrieval_service import RetrievalService

router = APIRouter(prefix="/chat", tags=["Chat"])


def get_chat_service(
    conv_repo=Depends(get_conversation_repo),
    knowledge_repo=Depends(get_knowledge_repo),
    product_repo=Depends(get_product_repo),
) -> ChatService:
    retrieval = RetrievalService(knowledge_repo=knowledge_repo, product_repo=product_repo)
    rag = RAGService(retrieval_service=retrieval)
    return ChatService(conv_repo=conv_repo, rag_service=rag)


@router.post("", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat(
    request: ChatRequest,
    session_id: str = Depends(get_session_id),
    chat_service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    """Processes a user question, retrieves verified Routica context, and returns a grounded answer."""
    effective_session_id = request.session_id or session_id
    if not effective_session_id:
        raise ValidationException("A valid session identifier is required")
    return await chat_service.handle_chat_message(request, session_id=effective_session_id)


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    session_id: str = Depends(get_session_id),
    chat_service: ChatService = Depends(get_chat_service),
) -> StreamingResponse:
    """Streams token chunks, sources, and completion status using Server-Sent Events (SSE)."""
    effective_session_id = request.session_id or session_id
    if not effective_session_id:
        raise ValidationException("A valid session identifier is required")

    return StreamingResponse(
        chat_service.stream_chat_message(request, session_id=effective_session_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
