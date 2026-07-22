import json
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

        guard = await check_output(full)
        if not guard["safe"]:
            full = guard["sanitized"]
        elif guard["reason"] == "sanitized":
            full = guard["sanitized"]

        await _log_message(db, widget, request.sessionId, "assistant", full)

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
