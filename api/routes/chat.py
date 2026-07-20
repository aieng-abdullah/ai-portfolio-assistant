import json
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models import ChatRequest, ChatResponse, RateLimitResponse
from services.chat_proxy import proxy_to_n8n
from database import get_db, Widget, ChatSession, ChatLog

router = APIRouter()


def _parse_json(value, default=None):
    if default is None:
        default = {}
    if isinstance(value, str):
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return default
    return value if value else default


async def _check_rate_limit(db: Session, widget: Widget, session_id: str) -> dict:
    session_limit = widget.rateLimit
    daily_limit = widget.dailyMessageLimit

    one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
    start_of_day = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    session = db.query(ChatSession).filter(
        ChatSession.sessionId == session_id,
        ChatSession.widgetId == widget.id,
    ).first()

    session_messages = 0
    if session:
        session_messages = db.query(ChatLog).filter(
            ChatLog.widgetId == widget.id,
            ChatLog.sessionId == session_id,
            ChatLog.createdAt >= one_hour_ago,
        ).count()

    daily_messages = db.query(ChatLog).filter(
        ChatLog.widgetId == widget.id,
        ChatLog.createdAt >= start_of_day,
    ).count()

    return {
        "over_limit": session_messages >= session_limit or daily_messages >= daily_limit,
        "session_messages": session_messages,
        "session_limit": session_limit,
        "daily_messages": daily_messages,
        "daily_limit": daily_limit,
    }


async def _log_message(db: Session, widget: Widget, session_id: str, role: str, message: str):
    session = db.query(ChatSession).filter(
        ChatSession.sessionId == session_id,
        ChatSession.widgetId == widget.id,
    ).first()

    if session:
        session.messageCount += 1
        session.lastMessageAt = datetime.now(timezone.utc)
    else:
        session = ChatSession(sessionId=session_id, widgetId=widget.id, messageCount=1)
        db.add(session)

    db.commit()

    log = ChatLog(widgetId=widget.id, sessionId=session_id, role=role, message=message[:2000])
    db.add(log)
    db.commit()


@router.post("/api/chat/{slug}", response_model=ChatResponse)
async def chat(slug: str, request: ChatRequest, db: Session = Depends(get_db)):
    widget = db.query(Widget).filter(Widget.slug == slug).first()
    if not widget:
        raise HTTPException(status_code=404, detail=f"Widget '{slug}' not found")
    if not widget.isActive:
        raise HTTPException(status_code=403, detail="Chat is temporarily unavailable")

    limits = await _check_rate_limit(db, widget, request.sessionId)
    if limits.get("over_limit"):
        return ChatResponse(
            response="You've reached the chat limit. Please try again later.",
            sessionId=request.sessionId,
        )

    await _log_message(db, widget, request.sessionId, "user", request.message)

    response = await proxy_to_n8n(slug, request.sessionId, request.message)

    await _log_message(db, widget, request.sessionId, "assistant", response)

    return ChatResponse(response=response, sessionId=request.sessionId)


@router.get("/api/widget/{slug}/rate-limit", response_model=RateLimitResponse)
async def get_rate_limit(slug: str, sessionId: str, db: Session = Depends(get_db)):
    widget = db.query(Widget).filter(Widget.slug == slug).first()
    if not widget:
        raise HTTPException(status_code=404, detail=f"Widget '{slug}' not found")

    limits = await _check_rate_limit(db, widget, sessionId)
    return RateLimitResponse(
        over_limit=limits.get("over_limit", True),
        session_messages=limits.get("session_messages", 0),
        session_limit=limits.get("session_limit", 30),
        daily_messages=limits.get("daily_messages", 0),
        daily_limit=limits.get("daily_limit", 1000),
    )
