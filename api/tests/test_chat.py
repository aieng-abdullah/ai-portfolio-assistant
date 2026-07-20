import pytest
from unittest.mock import patch, AsyncMock
from conftest import MockWidget, MockChatSession
from models import ChatRequest


@pytest.mark.asyncio
async def test_chat_success(mock_prisma, sample_widget):
    mock_prisma.widget.find_unique = AsyncMock(return_value=sample_widget)
    mock_prisma.chatsession.find_unique = AsyncMock(return_value=None)
    mock_prisma.chatsession.create = AsyncMock(return_value=MockChatSession())
    mock_prisma.chatlog.count = AsyncMock(return_value=5)
    mock_prisma.chatlog.create = AsyncMock()

    with patch("services.chat_proxy.proxy_to_n8n", new_callable=AsyncMock) as mock_proxy:
        mock_proxy.return_value = "I'm a test response"

        from routes.chat import chat
        request = ChatRequest(sessionId="session-123", message="Hello")
        result = await chat("test-widget", request)

        assert result.response == "I'm a test response"
        assert result.sessionId == "session-123"


@pytest.mark.asyncio
async def test_chat_widget_not_found(mock_prisma):
    mock_prisma.widget.find_unique = AsyncMock(return_value=None)

    from routes.chat import chat
    from models import ChatRequest
    from fastapi import HTTPException

    request = ChatRequest(sessionId="session-123", message="Hello")
    with pytest.raises(HTTPException) as exc:
        await chat("nonexistent", request)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_chat_widget_inactive(mock_prisma):
    widget = MockWidget(isActive=False)
    mock_prisma.widget.find_unique = AsyncMock(return_value=widget)

    from routes.chat import chat
    from models import ChatRequest
    from fastapi import HTTPException

    request = ChatRequest(sessionId="session-123", message="Hello")
    with pytest.raises(HTTPException) as exc:
        await chat("test-widget", request)
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_chat_rate_limited(mock_prisma, sample_widget):
    mock_prisma.widget.find_unique = AsyncMock(return_value=sample_widget)
    mock_prisma.chatsession.find_unique = AsyncMock(return_value=MockChatSession())
    mock_prisma.chatlog.count = AsyncMock(return_value=35)  # Over limit of 30

    from routes.chat import chat
    from models import ChatRequest

    request = ChatRequest(sessionId="session-123", message="Hello")
    result = await chat("test-widget", request)

    assert "chat limit" in result.response.lower()
