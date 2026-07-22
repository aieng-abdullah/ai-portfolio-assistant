import pytest
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime, timezone


class MockWidget:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", "test-widget-id")
        self.slug = kwargs.get("slug", "test-widget")
        self.name = kwargs.get("name", "Test Widget")
        self.profile = kwargs.get("profile", {"name": "Test User", "title": "Developer"})
        self.projects = kwargs.get("projects", [{"name": "Project 1", "description": "A project"}])
        self.services = kwargs.get("services", [{"name": "Service 1", "description": "A service"}])
        self.faq = kwargs.get("faq", [{"question": "FAQ?", "answer": "Answer"}])
        self.personality = kwargs.get("personality", {"tone": "witty_professional"})
        self.theme = kwargs.get("theme", {"primaryColor": "#4F46E5"})
        self.rateLimit = kwargs.get("rateLimit", 30)
        self.dailyMessageLimit = kwargs.get("dailyMessageLimit", 1000)
        self.isActive = kwargs.get("isActive", True)
        self.createdAt = kwargs.get("createdAt", datetime.now(timezone.utc))
        self.updatedAt = kwargs.get("updatedAt", datetime.now(timezone.utc))
        self.userId = kwargs.get("userId", "test-user-id")
        self.google_calendar_email = kwargs.get("google_calendar_email", None)
        self.google_access_token = kwargs.get("google_access_token", None)
        self.google_refresh_token = kwargs.get("google_refresh_token", None)
        self.google_token_expires_at = kwargs.get("google_token_expires_at", None)


class MockChatSession:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", "test-session-id")
        self.sessionId = kwargs.get("sessionId", "session-123")
        self.widgetId = kwargs.get("widgetId", "test-widget-id")
        self.messageCount = kwargs.get("messageCount", 0)
        self.lastMessageAt = kwargs.get("lastMessageAt", datetime.now(timezone.utc))
        self.createdAt = kwargs.get("createdAt", datetime.now(timezone.utc))


def create_mock_db(widget=None):
    """Create a mock SQLAlchemy session that returns the given widget on query()."""
    db = MagicMock()
    query_mock = MagicMock()
    filter_mock = MagicMock()

    if widget is not None:
        filter_mock.first.return_value = widget
    else:
        filter_mock.first.return_value = None

    query_mock.filter.return_value = filter_mock
    db.query.return_value = query_mock
    return db


def create_mock_db_for_chat(widget=None, session=None, message_count=0):
    """Create a mock DB that handles chat-specific queries (rate limiting, logging)."""
    db = MagicMock()

    def query_side_effect(model):
        q = MagicMock()
        f = MagicMock()
        if model.__name__ == "Widget" or (hasattr(model, '__name__') and model.__name__ == "Widget"):
            f.first.return_value = widget
        elif model.__name__ == "ChatSession" or (hasattr(model, '__name__') and model.__name__ == "ChatSession"):
            f.first.return_value = session
        else:
            f.count.return_value = message_count
        q.filter.return_value = f
        return q

    db.query.side_effect = query_side_effect
    return db


@pytest.fixture
def sample_widget():
    return MockWidget()


@pytest.fixture
def sample_session():
    return MockChatSession()
