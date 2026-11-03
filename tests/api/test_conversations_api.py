"""API tests for conversation listing, message history, and deletion."""

from unittest.mock import AsyncMock
import pytest
from httpx import AsyncClient

from app.dependencies import get_conversation_repo
from app.models.conversation import Conversation, Message


@pytest.mark.asyncio
async def test_list_conversations_for_session(app, async_client: AsyncClient):
    mock_conv = Conversation(_id="conv_1", session_id="user_session_1", title="Explorer Chat")
    mock_repo = AsyncMock()
    mock_repo.list_by_session.return_value = [mock_conv]

    app.dependency_overrides[get_conversation_repo] = lambda: mock_repo

    response = await async_client.get(
        "/api/v1/conversations",
        headers={"X-Session-ID": "user_session_1"},
    )
    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Explorer Chat"


@pytest.mark.asyncio
async def test_get_conversation_messages_found(app, async_client: AsyncClient):
    mock_conv = Conversation(_id="conv_1", session_id="user_session_1", title="Explorer Chat")
    mock_msg = Message(_id="msg_1", conversation_id="conv_1", role="user", content="Hello Routica")

    mock_repo = AsyncMock()
    mock_repo.get_conversation.return_value = mock_conv
    mock_repo.get_messages.return_value = [mock_msg]

    app.dependency_overrides[get_conversation_repo] = lambda: mock_repo

    response = await async_client.get(
        "/api/v1/conversations/conv_1",
        headers={"X-Session-ID": "user_session_1"},
    )
    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["content"] == "Hello Routica"


@pytest.mark.asyncio
async def test_get_conversation_messages_not_found(app, async_client: AsyncClient):
    mock_repo = AsyncMock()
    mock_repo.get_conversation.return_value = None

    app.dependency_overrides[get_conversation_repo] = lambda: mock_repo

    response = await async_client.get(
        "/api/v1/conversations/nonexistent_conv",
        headers={"X-Session-ID": "user_session_1"},
    )
    app.dependency_overrides.clear()

    assert response.status_code == 404

