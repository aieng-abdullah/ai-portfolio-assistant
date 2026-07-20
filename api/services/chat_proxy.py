import httpx
from datetime import datetime, timezone, timedelta
from database import prisma
from config import get_settings


async def check_rate_limit(slug: str, session_id: str) -> dict:
    settings = get_settings()

    widget = await prisma.widget.find_unique(where={"slug": slug})
    if not widget:
        return {"over_limit": True, "reason": "widget_not_found"}

    session_limit = widget.rateLimit
    daily_limit = widget.dailyMessageLimit

    # Check session rate limit (per hour)
    one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
    session = await prisma.chatsession.find_unique(
        where={"sessionId_widgetId": {"sessionId": session_id, "widgetId": widget.id}}
    )

    session_messages = 0
    if session:
        session_messages = await prisma.chatlog.count(
            where={
                "widgetId": widget.id,
                "sessionId": session_id,
                "createdAt": {"gte": one_hour_ago},
            }
        )

    # Check daily limit
    start_of_day = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    daily_messages = await prisma.chatlog.count(
        where={
            "widgetId": widget.id,
            "createdAt": {"gte": start_of_day},
        }
    )

    return {
        "over_limit": session_messages >= session_limit or daily_messages >= daily_limit,
        "session_messages": session_messages,
        "session_limit": session_limit,
        "daily_messages": daily_messages,
        "daily_limit": daily_limit,
    }


async def log_message(slug: str, session_id: str, role: str, message: str):
    widget = await prisma.widget.find_unique(where={"slug": slug})
    if not widget:
        return

    # Upsert session
    session = await prisma.chatsession.find_unique(
        where={"sessionId_widgetId": {"sessionId": session_id, "widgetId": widget.id}}
    )
    if session:
        await prisma.chatsession.update(
            where={"id": session.id},
            data={"messageCount": session.messageCount + 1, "lastMessageAt": datetime.now(timezone.utc)},
        )
    else:
        await prisma.chatsession.create(
            data={"sessionId": session_id, "widgetId": widget.id, "messageCount": 1}
        )

    # Log message
    await prisma.chatlog.create(
        data={"widgetId": widget.id, "sessionId": session_id, "role": role, "message": message[:2000]}
    )


async def proxy_to_n8n(slug: str, session_id: str, message: str) -> str:
    settings = get_settings()
    webhook_url = settings.n8n_webhook_url.rstrip("/")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                webhook_url,
                json={
                    "chatInput": message,
                    "sessionId": session_id,
                    "slug": slug,
                },
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            data = response.json()
            return data.get("output", data.get("response", "I couldn't process that request."))
    except httpx.TimeoutException:
        return "Sorry, I'm taking too long to respond. Please try again."
    except httpx.HTTPStatusError as e:
        return f"Sorry, something went wrong. Please try again later."
    except Exception as e:
        return "Sorry, I'm temporarily unavailable. Please try again."
