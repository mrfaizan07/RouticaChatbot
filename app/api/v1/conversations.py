"""Conversation and session management endpoints."""

from fastapi import APIRouter, Depends, status
from app.core.exceptions import NotFoundException
from app.database.repositories.conversations import ConversationRepository
from app.dependencies import get_conversation_repo, get_session_id
from app.models.conversation import Conversation, Message

router = APIRouter(prefix="/conversations", tags=["Conversations"])


@router.get("", response_model=list[Conversation])
async def list_conversations(
    session_id: str = Depends(get_session_id),
    conv_repo: ConversationRepository = Depends(get_conversation_repo),
) -> list[Conversation]:
    """Retrieves all active conversations belonging to the authorized session."""
    return await conv_repo.list_by_session(session_id=session_id)


@router.get("/{conversation_id}", response_model=list[Message])
async def get_conversation_messages(
    conversation_id: str,
    session_id: str = Depends(get_session_id),
    conv_repo: ConversationRepository = Depends(get_conversation_repo),
) -> list[Message]:
    """Retrieves chronological messages for an accessible conversation."""
    conv = await conv_repo.get_conversation(conv_id=conversation_id, session_id=session_id)
    if not conv:
        raise NotFoundException("Conversation not found or access denied")
    return await conv_repo.get_messages(conv_id=conversation_id)


@router.delete("/{conversation_id}", status_code=status.HTTP_200_OK)
async def delete_conversation(
    conversation_id: str,
    session_id: str = Depends(get_session_id),
    conv_repo: ConversationRepository = Depends(get_conversation_repo),
) -> dict[str, str]:
    """Soft deletes a conversation belonging to the user's session."""
    success = await conv_repo.delete_conversation(conv_id=conversation_id, session_id=session_id)
    if not success:
        raise NotFoundException("Conversation not found or access denied")
    return {"message": "Conversation successfully deleted"}

