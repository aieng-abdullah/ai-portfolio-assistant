import pytest
from unittest.mock import MagicMock


def test_health_check_connected(mock_prisma):
    mock_prisma.is_connected = MagicMock(return_value=True)

    from main import health_check
    import asyncio

    result = asyncio.run(health_check())
    assert result.status == "healthy"
    assert result.services["database"] == "connected"


def test_health_check_disconnected(mock_prisma):
    mock_prisma.is_connected = MagicMock(return_value=False)

    from main import health_check
    import asyncio

    result = asyncio.run(health_check())
    assert result.status == "degraded"
    assert result.services["database"] == "disconnected"


def test_root():
    from main import root
    import asyncio

    result = asyncio.run(root())
    assert result["message"] == "AI Portfolio Assistant API"
    assert result["docs"] == "/docs"
