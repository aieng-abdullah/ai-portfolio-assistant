import httpx
import json
from sqlalchemy.orm import Session
from database import Widget
from config import get_settings


def _parse_json(value, default=None):
    if default is None:
        default = {}
    if isinstance(value, str):
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return default
    return value if value else default


def _local_fallback(slug: str, message: str, db: Session) -> str:
    widget = db.query(Widget).filter(Widget.slug == slug).first()
    if not widget:
        return "I don't have any information about this portfolio."

    profile = _parse_json(widget.profile, {})
    projects = _parse_json(widget.projects, [])
    services = _parse_json(widget.services, [])
    name = profile.get("name", "the portfolio owner")

    msg = message.lower()

    # Skill questions
    if any(w in msg for w in ["skill", "tech", "stack", "know", "use", "language"]):
        skills = profile.get("skills", [])
        if skills:
            return f"{name} works with: {', '.join(skills)}. Pretty solid stack, right?"
        return f"I'd check {name}'s profile for the latest on their skills."

    # Project questions
    if any(w in msg for w in ["project", "portfolio", "work", "built", "made", "created"]):
        if projects:
            lines = [f"- {p.get('name', 'Unknown')}: {p.get('description', 'No description')}" for p in projects[:3]]
            return f"Here are some of {name}'s projects:\n" + "\n".join(lines)
        return f"I don't have project details loaded yet. Try asking about {name}'s skills or services."

    # Service questions
    if any(w in msg for w in ["service", "offer", "help", "do you", "provide", "pricing"]):
        if services:
            lines = [f"- {s.get('name', 'Unknown')}: {s.get('description', 'No description')}" for s in services[:3]]
            return f"Here's what {name} offers:\n" + "\n".join(lines)
        return f"I don't have service details loaded yet."

    # Contact questions
    if any(w in msg for w in ["contact", "email", "reach", "linkedin", "website", "hire"]):
        contact = profile.get("contact", {})
        parts = []
        if contact.get("email"):
            parts.append(f"Email: {contact['email']}")
        if contact.get("website"):
            parts.append(f"Website: {contact['website']}")
        if contact.get("linkedin"):
            parts.append(f"LinkedIn: {contact['linkedin']}")
        if parts:
            return "Here's how to reach " + name + ":\n" + "\n".join(parts)
        return f"Contact info isn't loaded yet. Check back later!"

    # Bio/about questions
    if any(w in msg for w in ["who", "about", "bio", "tell me", "what do you do", "introduce"]):
        bio = profile.get("bio", "")
        title = profile.get("title", "")
        location = profile.get("location", "")
        parts = []
        if title:
            parts.append(f"{name} is a {title}")
        if bio:
            parts.append(bio)
        if location:
            parts.append(f"Based in {location}")
        if parts:
            return ". ".join(parts) + "."
        return f"I'm {name}'s AI assistant. Ask me about their skills, projects, or services!"

    # Meeting/booking
    if any(w in msg for w in ["meeting", "book", "calendar", "schedule", "call"]):
        return f"To book a meeting with {name}, please provide your name, email, and preferred date/time. I'll check availability!"

    # Default
    return f"I'm {name}'s AI assistant! I can tell you about their skills, projects, services, or help book a meeting. What would you like to know?"


async def proxy_to_n8n(slug: str, session_id: str, message: str, db: Session = None) -> str:
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
                },
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            data = response.json()
            return data.get("output", data.get("response", "I couldn't process that request."))
    except (httpx.TimeoutException, httpx.HTTPStatusError, httpx.ConnectError, Exception):
        # n8n not available — use local fallback
        if db:
            return _local_fallback(slug, message, db)
        return "Sorry, the AI assistant is temporarily unavailable. Please try again later."
