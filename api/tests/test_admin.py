import pytest
from unittest.mock import patch, AsyncMock
from conftest import MockWidget


@pytest.mark.asyncio
async def test_disable_widget(mock_prisma, sample_widget):
    mock_prisma.widget.find_unique = AsyncMock(return_value=sample_widget)
    mock_prisma.widget.update = AsyncMock()

    from routes.admin import disable_widget
    result = await disable_widget("test-widget")

    assert result["isActive"] is False
    assert "disabled" in result["message"]


@pytest.mark.asyncio
async def test_enable_widget(mock_prisma):
    widget = MockWidget(isActive=False)
    mock_prisma.widget.find_unique = AsyncMock(return_value=widget)
    mock_prisma.widget.update = AsyncMock()

    from routes.admin import enable_widget
    result = await enable_widget("test-widget")

    assert result["isActive"] is True
    assert "enabled" in result["message"]


@pytest.mark.asyncio
async def test_disable_widget_not_found(mock_prisma):
    mock_prisma.widget.find_unique = AsyncMock(return_value=None)

    from routes.admin import disable_widget
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc:
        await disable_widget("nonexistent")
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_get_stats(mock_prisma, sample_widget):
    mock_prisma.widget.find_unique = AsyncMock(return_value=sample_widget)
    mock_prisma.chatlog.count = AsyncMock(return_value=100)
    mock_prisma.chatsession.count = AsyncMock(return_value=5)

    from routes.admin import get_widget_stats
    result = await get_widget_stats("test-widget")

    assert result["slug"] == "test-widget"
    assert result["isActive"] is True
    assert result["totalMessages"] == 100
    assert result["activeSessions"] == 5
