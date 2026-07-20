import httpx
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from database import get_db, Widget, ChatSession, ChatLog
from config import get_settings


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
    except httpx.HTTPStatusError:
        return "Sorry, something went wrong. Please try again later."
    except Exception:
        return "Sorry, I'm temporarily unavailable. Please try again."
