"""API tests for Chat JSON query and SSE streaming."""

from unittest.mock import AsyncMock
import pytest
from httpx import AsyncClient

from app.api.v1.chat import get_chat_service
from app.models.conversation import Conversation, Message
from app.schemas.chat import ChatResponse, CitationSource


@pytest.mark.asyncio
async def test_chat_json_endpoint(app, async_client: AsyncClient):
    mock_chat_service = AsyncMock()
    mock_chat_service.handle_chat_message.return_value = ChatResponse(
        conversation_id="conv_test_123",
        message_id="msg_test_456",
        answer="Routica Explorer II is a premium 5G router for marine and RV use.",
        sources=[
            CitationSource(
                title="Explorer II Product Page",
                url="https://routica.com/explorer-ii",
                source_type="website",
                relevance_score=0.92,
                snippet="Explorer II supports 5G Sub-6GHz and Wi-Fi 6.",
            )
        ],
        provider="gemini",
        model="gemini/gemini-1.5-flash",
        response_time_ms=120,
        created_at="2026-11-03T00:00:00Z",
    )

    app.dependency_overrides[get_chat_service] = lambda: mock_chat_service

    response = await async_client.post(
        "/api/v1/chat",
        json={"message": "Does Explorer II support 5G?"},
        headers={"X-Session-ID": "test-session-abc"},
    )
    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["conversation_id"] == "conv_test_123"
    assert "Explorer II" in data["answer"]
    assert len(data["sources"]) == 1
    assert data["sources"][0]["url"] == "https://routica.com/explorer-ii"


@pytest.mark.asyncio
async def test_chat_sse_stream_endpoint(app, async_client: AsyncClient):
    async def mock_stream_generator(request, session_id):
        yield 'event: status\ndata: {"status": "retrieving"}\n\n'
        yield 'event: sources\ndata: {"sources": []}\n\n'
        yield 'event: token\ndata: {"token": "Explorer "}\n\n'
        yield 'event: token\ndata: {"token": "II"}\n\n'
        yield 'event: complete\ndata: {"conversation_id": "conv_123"}\n\n'

    mock_chat_service = AsyncMock()
    mock_chat_service.stream_chat_message = mock_stream_generator

    app.dependency_overrides[get_chat_service] = lambda: mock_chat_service

    response = await async_client.post(
        "/api/v1/chat/stream",
        json={"message": "What is Explorer II?"},
        headers={"X-Session-ID": "test-session-abc"},
    )
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    body = response.text
    assert "event: status" in body
    assert "event: token" in body
    assert "Explorer " in body
    assert "event: complete" in body

