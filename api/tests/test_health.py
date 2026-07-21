from unittest.mock import MagicMock


def test_health_check_connected():
    from main import health_check
    import asyncio

    db = MagicMock()
    result = asyncio.run(health_check(db=db))
    assert result.status == "healthy"
    assert result.services["database"] == "connected"


def test_health_check_disconnected():
    from main import health_check
    import asyncio

    db = MagicMock()
    db.execute.side_effect = Exception("Connection failed")
    result = asyncio.run(health_check(db=db))
    assert result.status == "degraded"
    assert result.services["database"] == "disconnected"


def test_root():
    from main import root
    import asyncio

    result = asyncio.run(root())
    assert result["message"] == "AI Portfolio Assistant API"
    assert result["docs"] == "/docs"
