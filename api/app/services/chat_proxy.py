import httpx
from app.config import get_settings


async def proxy_to_n8n(slug: str, session_id: str, message: str, db=None) -> str:
    settings = get_settings()
    webhook_url = settings.n8n_webhook_url.rstrip("/")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                webhook_url,
                json={
                    "chatInput": message,
                    "sessionId": session_id,
                    "slug": slug,
                    "groqApiKey": settings.groq_api_key,
                },
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            data = response.json()
            return data.get("output", data.get("response", "I couldn't process that request."))
    except (httpx.TimeoutException, httpx.HTTPStatusError, httpx.ConnectError, Exception):
        return "Sorry, the AI assistant is temporarily unavailable. Please try again later."
