import sys
import pytest
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime, timezone

# Mock prisma before any app imports
mock_prisma_module = MagicMock()
mock_prisma_instance = MagicMock()
mock_prisma_module.Prisma.return_value = mock_prisma_instance
sys.modules["prisma"] = mock_prisma_module
sys.modules["prisma.models"] = MagicMock()


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


class MockChatSession:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", "test-session-id")
        self.sessionId = kwargs.get("sessionId", "session-123")
        self.widgetId = kwargs.get("widgetId", "test-widget-id")
        self.messageCount = kwargs.get("messageCount", 0)
        self.lastMessageAt = kwargs.get("lastMessageAt", datetime.now(timezone.utc))
        self.createdAt = kwargs.get("createdAt", datetime.now(timezone.utc))


@pytest.fixture
def mock_prisma():
    return mock_prisma_instance


@pytest.fixture
def sample_widget():
    return MockWidget()


@pytest.fixture
def sample_session():
    return MockChatSession()
