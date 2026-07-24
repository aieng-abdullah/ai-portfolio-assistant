import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from conftest import MockWidget, MockChatSession, create_mock_db, create_mock_db_for_chat
from app.models import ChatRequest


@pytest.mark.asyncio
async def test_chat_success(sample_widget):
    db = create_mock_db_for_chat(widget=sample_widget, session=None, message_count=0)

    with patch("app.services.chat_proxy.proxy_to_n8n", new_callable=AsyncMock) as mock_proxy:
        mock_proxy.return_value = "I'm a test response"

        from app.routes.chat import chat
        request = ChatRequest(sessionId="session-123", message="Hello")
        result = await chat("test-widget", request, db=db)

        assert result.response == "I'm a test response"
        assert result.sessionId == "session-123"


@pytest.mark.asyncio
async def test_chat_widget_not_found():
    db = create_mock_db_for_chat(widget=None)

    from app.routes.chat import chat
    from app.models import ChatRequest
    from fastapi import HTTPException

    request = ChatRequest(sessionId="session-123", message="Hello")
    with pytest.raises(HTTPException) as exc:
        await chat("nonexistent", request, db=db)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_chat_widget_inactive():
    widget = MockWidget(isActive=False)
    db = create_mock_db_for_chat(widget=widget)

    from app.routes.chat import chat
    from app.models import ChatRequest
    from fastapi import HTTPException

    request = ChatRequest(sessionId="session-123", message="Hello")
    with pytest.raises(HTTPException) as exc:
        await chat("test-widget", request, db=db)
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_chat_rate_limited(sample_widget):
    db = create_mock_db_for_chat(widget=sample_widget, session=MockChatSession(), message_count=35)

    from app.routes.chat import chat
    from app.models import ChatRequest

    request = ChatRequest(sessionId="session-123", message="Hello")
    result = await chat("test-widget", request, db=db)

    assert "chat limit" in result.response.lower()
