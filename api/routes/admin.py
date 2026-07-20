from fastapi import APIRouter, HTTPException
from database import prisma

router = APIRouter()


@router.post("/api/admin/widget/{slug}/disable")
async def disable_widget(slug: str):
    widget = await prisma.widget.find_unique(where={"slug": slug})
    if not widget:
        raise HTTPException(status_code=404, detail=f"Widget '{slug}' not found")

    await prisma.widget.update(where={"slug": slug}, data={"isActive": False})
    return {"message": f"Widget '{slug}' disabled", "isActive": False}


@router.post("/api/admin/widget/{slug}/enable")
async def enable_widget(slug: str):
    widget = await prisma.widget.find_unique(where={"slug": slug})
    if not widget:
        raise HTTPException(status_code=404, detail=f"Widget '{slug}' not found")

    await prisma.widget.update(where={"slug": slug}, data={"isActive": True})
    return {"message": f"Widget '{slug}' enabled", "isActive": True}


@router.get("/api/admin/widget/{slug}/stats")
async def get_widget_stats(slug: str):
    widget = await prisma.widget.find_unique(where={"slug": slug})
    if not widget:
        raise HTTPException(status_code=404, detail=f"Widget '{slug}' not found")

    from datetime import datetime, timezone, timedelta

    now = datetime.now(timezone.utc)
    one_hour_ago = now - timedelta(hours=1)
    one_day_ago = now - timedelta(days=1)

    total_messages = await prisma.chatlog.count(where={"widgetId": widget.id})
    hourly_messages = await prisma.chatlog.count(
        where={"widgetId": widget.id, "createdAt": {"gte": one_hour_ago}}
    )
    daily_messages = await prisma.chatlog.count(
        where={"widgetId": widget.id, "createdAt": {"gte": one_day_ago}}
    )
    active_sessions = await prisma.chatsession.count(
        where={"widgetId": widget.id, "lastMessageAt": {"gte": one_hour_ago}}
    )

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
