import pytest
from unittest.mock import AsyncMock
from conftest import MockWidget, create_mock_db


@pytest.mark.asyncio
async def test_disable_widget(sample_widget):
    db = create_mock_db(widget=sample_widget)

    from routes.admin import disable_widget
    result = await disable_widget("test-widget", db=db)

    assert result["isActive"] is False
    assert "disabled" in result["message"]


@pytest.mark.asyncio
async def test_enable_widget():
    widget = MockWidget(isActive=False)
    db = create_mock_db(widget=widget)

    from routes.admin import enable_widget
    result = await enable_widget("test-widget", db=db)

    assert result["isActive"] is True
    assert "enabled" in result["message"]


@pytest.mark.asyncio
async def test_disable_widget_not_found():
    db = create_mock_db(widget=None)

    from routes.admin import disable_widget
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc:
        await disable_widget("nonexistent", db=db)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_get_stats(sample_widget):
    db = create_mock_db(widget=sample_widget)
    db.query.return_value.filter.return_value.count.return_value = 100

    from routes.admin import get_widget_stats
    result = await get_widget_stats("test-widget", db=db)

    assert result["slug"] == "test-widget"
    assert result["isActive"] is True
