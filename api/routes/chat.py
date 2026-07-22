import json
import re
import httpx
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from models import ChatRequest, ChatResponse, RateLimitResponse
from services.chat_proxy import proxy_to_n8n, local_fallback
from services.llm import call_llm, call_llm_stream
from services.input_guard import check_input
from services.output_guard import check_output
from database import get_db, Widget, ChatSession, ChatLog, AbuseLog

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_CALENDAR_API = "https://www.googleapis.com/calendar/v3"


async def _ensure_valid_token(widget, db):
    now = datetime.now(timezone.utc)
    if widget.google_token_expires_at and widget.google_token_expires_at.replace(tzinfo=timezone.utc) > now:
        return widget.google_access_token

    from config import get_settings
    settings = get_settings()

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "client_id": settings.google_oauth_client_id,
                "client_secret": settings.google_oauth_client_secret,
                "refresh_token": widget.google_refresh_token,
                "grant_type": "refresh_token",
            },
        )
        if resp.status_code != 200:
            return None
        token_data = resp.json()

    widget.google_access_token = token_data["access_token"]
    widget.google_token_expires_at = now + timedelta(seconds=token_data.get("expires_in", 3600))
    db.commit()
    return widget.google_access_token


async def _book_calendar_event(widget: Widget, db: Session, name: str, email: str, start_dt: str, end_dt: str, tz: str) -> dict | None:
    if not widget.google_access_token or not widget.google_refresh_token:
        return None

    access_token = await _ensure_valid_token(widget, db)
    if not access_token:
        return None

    event = {
        "summary": f"Meeting with {name}",
        "description": f"Booked via portfolio assistant\nAttendee: {name} ({email})",
        "start": {"dateTime": start_dt, "timeZone": tz},
        "end": {"dateTime": end_dt, "timeZone": tz},
        "attendees": [{"email": email, "displayName": name}] if email else [],
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(
            f"{GOOGLE_CALENDAR_API}/calendars/primary/events",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            json=event,
        )
        if resp.status_code != 200:
            return None
        return resp.json()

router = APIRouter()


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


async def _log_abuse(db: Session, widget: Widget, session_id: str, reason: str, original: str | None = None):
    log = AbuseLog(
        widgetId=widget.id,
        sessionId=session_id,
        reason=reason,
        originalMessage=original[:2000] if original else None,
    )
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

    guard = await check_input(request.message)
    if not guard["clean"]:
        await _log_abuse(db, widget, request.sessionId, guard["reason"], request.message)
        return ChatResponse(
            response="I can't process that request. Please ask something about the portfolio.",
            sessionId=request.sessionId,
        )

    await _log_message(db, widget, request.sessionId, "user", request.message)

    response = await proxy_to_n8n(slug, request.sessionId, request.message, db)

    if response.startswith("Sorry, the AI assistant is temporarily unavailable"):
        response = await call_llm(slug, request.message, request.sessionId, db)

    if response in ("LLM API key is not configured.", "Sorry, I'm having trouble right now. Please try again later."):
        response = local_fallback(slug, request.message, db)

    guard = await check_output(response)
    if not guard["safe"]:
        await _log_abuse(db, widget, request.sessionId, guard["reason"], response)
        response = guard["sanitized"]
    elif guard["reason"] == "sanitized":
        response = guard["sanitized"]

    await _log_message(db, widget, request.sessionId, "assistant", response)

    return ChatResponse(response=response, sessionId=request.sessionId)


@router.post("/api/chat/{slug}/stream")
async def chat_stream(slug: str, request: ChatRequest, db: Session = Depends(get_db)):
    widget = db.query(Widget).filter(Widget.slug == slug).first()
    if not widget:
        raise HTTPException(status_code=404, detail=f"Widget '{slug}' not found")
    if not widget.isActive:
        raise HTTPException(status_code=403, detail="Chat is temporarily unavailable")

    limits = await _check_rate_limit(db, widget, request.sessionId)
    if limits.get("over_limit"):
        async def limit_gen():
            yield "data: " + json.dumps({"token": "You've reached the chat limit. Please try again later."}) + "\n\n"
            yield "data: " + json.dumps({"done": True}) + "\n\n"
        return StreamingResponse(limit_gen(), media_type="text/event-stream", headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"})

    guard = await check_input(request.message)
    if not guard["clean"]:
        await _log_abuse(db, widget, request.sessionId, guard["reason"], request.message)
        async def blocked_gen():
            yield "data: " + json.dumps({"token": "I can't process that request. Please ask something about the portfolio."}) + "\n\n"
            yield "data: " + json.dumps({"done": True}) + "\n\n"
        return StreamingResponse(blocked_gen(), media_type="text/event-stream", headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"})

    await _log_message(db, widget, request.sessionId, "user", request.message)

    async def stream_response():
        full = ""
        async for event in call_llm_stream(slug, request.message, request.sessionId, db):
            yield event
            parsed = json.loads(event[6:].strip())
            if parsed.get("token"):
                full += parsed["token"]

        booking_match = re.search(r'\[\[BOOK:(.*?)\]\]', full)
        if booking_match:
            try:
                parts = booking_match.group(1).split('|')
                if len(parts) >= 5:
                    b_name, b_email, b_start, b_end, b_tz = parts[:5]
                    result = await _book_calendar_event(widget, db, b_name.strip(), b_email.strip(), b_start.strip(), b_end.strip(), b_tz.strip())
                    if result:
                        confirm = f"\n\n✅ Meeting confirmed! Check your calendar."
                        yield "data: " + json.dumps({"token": confirm}) + "\n\n"
                    else:
                        yield "data: " + json.dumps({"token": "\n\n⚠️ Could not book automatically. Please try again."}) + "\n\n"
            except Exception:
                pass

        full_clean = re.sub(r'\[\[BOOK:.*?\]\]', '', full).strip()

        guard = await check_output(full_clean)
        if not guard["safe"]:
            full_clean = guard["sanitized"]
        elif guard["reason"] == "sanitized":
            full_clean = guard["sanitized"]

        await _log_message(db, widget, request.sessionId, "assistant", full_clean)

    return StreamingResponse(
        stream_response(),
        media_type="text/event-stream",
        headers={
            "X-Accel-Buffering": "no",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


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
