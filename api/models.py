from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


# Request Models
class ChatRequest(BaseModel):
    sessionId: str
    message: str


class LogRequest(BaseModel):
    sessionId: str
    role: str
    message: str


class AbuseLogRequest(BaseModel):
    sessionId: str
    filtered: bool
    timestamp: str


# Response Models
class ChatResponse(BaseModel):
    response: str
    sessionId: str


class RateLimitResponse(BaseModel):
    over_limit: bool
    session_messages: int
    session_limit: int
    daily_messages: int
    daily_limit: int


class WidgetConfigResponse(BaseModel):
    name: Optional[str] = None
    theme: dict = {}
    personality: dict = {}


class ProfileResponse(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    skills: list = []
    experience: list = []
    contact: dict = {}


class HealthResponse(BaseModel):
    status: str
    services: dict
    timestamp: str
