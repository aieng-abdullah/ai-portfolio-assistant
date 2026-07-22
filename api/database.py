import os
from sqlalchemy import create_engine, Column, String, Integer, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime, timezone

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://portfolio:portfolio_dev@localhost:5432/portfolio"
)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Widget(Base):
    __tablename__ = "widgets"

    id = Column(String, primary_key=True, default=lambda: __import__("uuid").uuid4().hex)
    slug = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    profile = Column(Text, default="{}")
    projects = Column(Text, default="[]")
    services = Column(Text, default="[]")
    faq = Column(Text, default="[]")
    personality = Column(Text, default="{}")
    theme = Column(Text, default="{}")
    rateLimit = Column(Integer, default=30)
    dailyMessageLimit = Column(Integer, default=1000)
    isActive = Column(Boolean, default=True)
    userId = Column(String, default="default")
    google_calendar_email = Column(String, nullable=True)
    google_access_token = Column(Text, nullable=True)
    google_refresh_token = Column(Text, nullable=True)
    google_token_expires_at = Column(DateTime, nullable=True)
    createdAt = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updatedAt = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    chatSessions = relationship("ChatSession", back_populates="widget")
    chatLogs = relationship("ChatLog", back_populates="widget")


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True, default=lambda: __import__("uuid").uuid4().hex)
    sessionId = Column(String, nullable=False, index=True)
    widgetId = Column(String, ForeignKey("widgets.id"), nullable=False)
    messageCount = Column(Integer, default=0)
    lastMessageAt = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    createdAt = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    widget = relationship("Widget", back_populates="chatSessions")


class ChatLog(Base):
    __tablename__ = "chat_logs"

    id = Column(String, primary_key=True, default=lambda: __import__("uuid").uuid4().hex)
    widgetId = Column(String, ForeignKey("widgets.id"), nullable=False)
    sessionId = Column(String, nullable=False)
    role = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    createdAt = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    widget = relationship("Widget", back_populates="chatLogs")


class AbuseLog(Base):
    __tablename__ = "abuse_logs"

    id = Column(String, primary_key=True, default=lambda: __import__("uuid").uuid4().hex)
    widgetId = Column(String, ForeignKey("widgets.id"), nullable=False)
    sessionId = Column(String, nullable=False)
    reason = Column(String, nullable=False)
    originalMessage = Column(Text, nullable=True)
    createdAt = Column(DateTime, default=lambda: datetime.now(timezone.utc))


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
