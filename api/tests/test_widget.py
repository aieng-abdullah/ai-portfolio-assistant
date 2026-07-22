import pytest
from unittest.mock import AsyncMock
from conftest import MockWidget, create_mock_db


@pytest.mark.asyncio
async def test_get_widget_config(sample_widget):
    db = create_mock_db(widget=sample_widget)

    from routes.widget import get_widget_config
    result = await get_widget_config("test-widget", db=db)

    assert result.name == "Test Widget"
    assert result.theme == {"primaryColor": "#4F46E5"}
    assert result.personality == {"tone": "witty_professional"}


@pytest.mark.asyncio
async def test_get_widget_config_not_found():
    db = create_mock_db(widget=None)

    from routes.widget import get_widget_config
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc:
        await get_widget_config("nonexistent", db=db)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_get_widget_config_inactive():
    widget = MockWidget(isActive=False)
    db = create_mock_db(widget=widget)

    from routes.widget import get_widget_config
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc:
        await get_widget_config("test-widget", db=db)
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_get_widget_profile(sample_widget):
    db = create_mock_db(widget=sample_widget)

    from routes.widget import get_widget_profile
    result = await get_widget_profile("test-widget", db=db)

    assert result.name == "Test User"
    assert result.title == "Developer"


@pytest.mark.asyncio
async def test_get_widget_projects(sample_widget):
    db = create_mock_db(widget=sample_widget)

    from routes.widget import get_widget_projects
    result = await get_widget_projects("test-widget", db=db)

    assert len(result) == 1
    assert result[0]["name"] == "Project 1"


@pytest.mark.asyncio
async def test_get_widget_services(sample_widget):
    db = create_mock_db(widget=sample_widget)

    from routes.widget import get_widget_services
    result = await get_widget_services("test-widget", db=db)

    assert len(result) == 1
    assert result[0]["name"] == "Service 1"


@pytest.mark.asyncio
async def test_get_widget_faq(sample_widget):
    db = create_mock_db(widget=sample_widget)

    from routes.widget import get_widget_faq
    result = await get_widget_faq("test-widget", db=db)

    assert len(result) == 1
    assert result[0]["question"] == "FAQ?"
