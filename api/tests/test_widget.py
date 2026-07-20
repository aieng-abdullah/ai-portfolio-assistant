import pytest
from unittest.mock import patch, AsyncMock
from conftest import MockWidget


@pytest.mark.asyncio
async def test_get_widget_config(mock_prisma, sample_widget):
    mock_prisma.widget.find_unique = AsyncMock(return_value=sample_widget)

    from routes.widget import get_widget_config
    result = await get_widget_config("test-widget")

    assert result.name == "Test Widget"
    assert result.theme == {"primaryColor": "#4F46E5"}
    assert result.personality == {"tone": "witty_professional"}


@pytest.mark.asyncio
async def test_get_widget_config_not_found(mock_prisma):
    mock_prisma.widget.find_unique = AsyncMock(return_value=None)

    from routes.widget import get_widget_config
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc:
        await get_widget_config("nonexistent")
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_get_widget_config_inactive(mock_prisma):
    widget = MockWidget(isActive=False)
    mock_prisma.widget.find_unique = AsyncMock(return_value=widget)

    from routes.widget import get_widget_config
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc:
        await get_widget_config("test-widget")
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_get_widget_profile(mock_prisma, sample_widget):
    mock_prisma.widget.find_unique = AsyncMock(return_value=sample_widget)

    from routes.widget import get_widget_profile
    result = await get_widget_profile("test-widget")

    assert result.name == "Test User"
    assert result.title == "Developer"
    assert "React" not in result.skills  # sample doesn't have skills in profile


@pytest.mark.asyncio
async def test_get_widget_projects(mock_prisma, sample_widget):
    mock_prisma.widget.find_unique = AsyncMock(return_value=sample_widget)

    from routes.widget import get_widget_projects
    result = await get_widget_projects("test-widget")

    assert len(result) == 1
    assert result[0]["name"] == "Project 1"


@pytest.mark.asyncio
async def test_get_widget_services(mock_prisma, sample_widget):
    mock_prisma.widget.find_unique = AsyncMock(return_value=sample_widget)

    from routes.widget import get_widget_services
    result = await get_widget_services("test-widget")

    assert len(result) == 1
    assert result[0]["name"] == "Service 1"


@pytest.mark.asyncio
async def test_get_widget_faq(mock_prisma, sample_widget):
    mock_prisma.widget.find_unique = AsyncMock(return_value=sample_widget)

    from routes.widget import get_widget_faq
    result = await get_widget_faq("test-widget")

    assert len(result) == 1
    assert result[0]["question"] == "FAQ?"
