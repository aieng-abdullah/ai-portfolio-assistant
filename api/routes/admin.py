from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db, Widget, ChatSession, ChatLog

router = APIRouter()


@router.post("/api/admin/widget/{slug}/disable")
async def disable_widget(slug: str, db: Session = Depends(get_db)):
    widget = db.query(Widget).filter(Widget.slug == slug).first()
    if not widget:
        raise HTTPException(status_code=404, detail=f"Widget '{slug}' not found")

    widget.isActive = False
    db.commit()
    return {"message": f"Widget '{slug}' disabled", "isActive": False}


@router.post("/api/admin/widget/{slug}/enable")
async def enable_widget(slug: str, db: Session = Depends(get_db)):
    widget = db.query(Widget).filter(Widget.slug == slug).first()
    if not widget:
        raise HTTPException(status_code=404, detail=f"Widget '{slug}' not found")

    widget.isActive = True
    db.commit()
    return {"message": f"Widget '{slug}' enabled", "isActive": True}


@router.get("/api/admin/widget/{slug}/stats")
async def get_widget_stats(slug: str, db: Session = Depends(get_db)):
    widget = db.query(Widget).filter(Widget.slug == slug).first()
    if not widget:
        raise HTTPException(status_code=404, detail=f"Widget '{slug}' not found")

    now = datetime.now(timezone.utc)
    one_hour_ago = now - timedelta(hours=1)
    one_day_ago = now - timedelta(days=1)

    total_messages = db.query(ChatLog).filter(ChatLog.widgetId == widget.id).count()
    hourly_messages = db.query(ChatLog).filter(
        ChatLog.widgetId == widget.id, ChatLog.createdAt >= one_hour_ago
    ).count()
    daily_messages = db.query(ChatLog).filter(
        ChatLog.widgetId == widget.id, ChatLog.createdAt >= one_day_ago
    ).count()
    active_sessions = db.query(ChatSession).filter(
        ChatSession.widgetId == widget.id, ChatSession.lastMessageAt >= one_hour_ago
    ).count()

    return {
        "slug": slug,
        "isActive": widget.isActive,
        "rateLimit": widget.rateLimit,
        "dailyMessageLimit": widget.dailyMessageLimit,
        "totalMessages": total_messages,
        "hourlyMessages": hourly_messages,
        "dailyMessages": daily_messages,
        "activeSessions": active_sessions,
    }


@router.post("/api/widget/{slug}/create")
async def create_widget(slug: str, data: dict = {}, db: Session = Depends(get_db)):
    existing = db.query(Widget).filter(Widget.slug == slug).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Widget '{slug}' already exists")

    import json
    widget = Widget(
        slug=slug,
        name=data.get("name", slug),
        profile=json.dumps(data.get("profile", {})),
        projects=json.dumps(data.get("projects", [])),
        services=json.dumps(data.get("services", [])),
        faq=json.dumps(data.get("faq", [])),
        personality=json.dumps(data.get("personality", {"tone": "witty_professional", "humorLevel": 7})),
        theme=json.dumps(data.get("theme", {"primaryColor": "#4F46E5", "chatTitle": "Portfolio Assistant"})),
    )
    db.add(widget)
    db.commit()
    db.refresh(widget)
    return {"message": f"Widget '{slug}' created", "slug": slug}
