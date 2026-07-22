import json
import httpx
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db, Widget, ChatLog, AbuseLog
from models import WidgetConfigResponse, ProfileResponse


class WidgetCreateRequest(BaseModel):
    name: str = "My Portfolio"


router = APIRouter()

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"


def _get_widget_or_404(db: Session, slug: str) -> Widget:
    widget = db.query(Widget).filter(Widget.slug == slug).first()
    if not widget:
        raise HTTPException(status_code=404, detail=f"Widget '{slug}' not found")
    if not widget.isActive:
        raise HTTPException(status_code=403, detail="Widget is disabled")
    return widget


def _parse_json(value, default=None):
    if default is None:
        default = {}
    if isinstance(value, str):
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return default
    return value if value else default


@router.post("/api/widget/{slug}/create")
async def create_widget(slug: str, data: WidgetCreateRequest = None, db: Session = Depends(get_db)):
    existing = db.query(Widget).filter(Widget.slug == slug).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Widget '{slug}' already exists")
    widget = Widget(slug=slug, name=data.name if data else "My Portfolio")
    db.add(widget)
    db.commit()
    db.refresh(widget)
    return {"slug": widget.slug, "name": widget.name, "id": widget.id}


@router.get("/api/widget/{slug}/config", response_model=WidgetConfigResponse)
async def get_widget_config(slug: str, db: Session = Depends(get_db)):
    widget = _get_widget_or_404(db, slug)
    return WidgetConfigResponse(
        name=widget.name,
        theme=_parse_json(widget.theme, {}),
        personality=_parse_json(widget.personality, {}),
    )


@router.get("/api/widget/{slug}/profile", response_model=ProfileResponse)
async def get_widget_profile(slug: str, db: Session = Depends(get_db)):
    widget = _get_widget_or_404(db, slug)
    profile = _parse_json(widget.profile, {})
    return ProfileResponse(
        name=profile.get("name"),
        title=profile.get("title"),
        bio=profile.get("bio"),
        location=profile.get("location"),
        skills=profile.get("skills", []),
        experience=profile.get("experience", []),
        contact=profile.get("contact", {}),
    )


@router.get("/api/widget/{slug}/projects")
async def get_widget_projects(slug: str, db: Session = Depends(get_db)):
    widget = _get_widget_or_404(db, slug)
    return _parse_json(widget.projects, [])


@router.get("/api/widget/{slug}/services")
async def get_widget_services(slug: str, db: Session = Depends(get_db)):
    widget = _get_widget_or_404(db, slug)
    return _parse_json(widget.services, [])


@router.get("/api/widget/{slug}/faq")
async def get_widget_faq(slug: str, db: Session = Depends(get_db)):
    widget = _get_widget_or_404(db, slug)
    return _parse_json(widget.faq, [])


# --- Google Calendar Credential Endpoints ---


class CalendarConnectRequest(BaseModel):
    access_token: str
    refresh_token: str
    calendar_email: str
    expires_at: str | None = None


@router.get("/api/widget/{slug}/calendar/status")
async def calendar_status(slug: str, db: Session = Depends(get_db)):
    widget = _get_widget_or_404(db, slug)
    connected = widget.google_calendar_email is not None and widget.google_access_token is not None
    return {
        "connected": connected,
        "email": widget.google_calendar_email if connected else None,
    }


@router.post("/api/widget/{slug}/calendar/connect")
async def calendar_connect(slug: str, data: CalendarConnectRequest, db: Session = Depends(get_db)):
    widget = _get_widget_or_404(db, slug)
    widget.google_calendar_email = data.calendar_email
    widget.google_access_token = data.access_token
    widget.google_refresh_token = data.refresh_token
    if data.expires_at:
        widget.google_token_expires_at = datetime.fromisoformat(data.expires_at)
    db.commit()
    return {"message": "Google Calendar connected", "email": data.calendar_email}


@router.post("/api/widget/{slug}/calendar/disconnect")
async def calendar_disconnect(slug: str, db: Session = Depends(get_db)):
    widget = _get_widget_or_404(db, slug)
    widget.google_calendar_email = None
    widget.google_access_token = None
    widget.google_refresh_token = None
    widget.google_token_expires_at = None
    db.commit()
    return {"message": "Google Calendar disconnected"}


@router.get("/api/widget/{slug}/calendar/token")
async def calendar_token(slug: str, db: Session = Depends(get_db)):
    widget = _get_widget_or_404(db, slug)
    if not widget.google_access_token or not widget.google_refresh_token:
        raise HTTPException(status_code=404, detail="Google Calendar not connected")

    now = datetime.now(timezone.utc)
    if widget.google_token_expires_at and widget.google_token_expires_at.replace(tzinfo=timezone.utc) > now:
        return {"access_token": widget.google_access_token, "email": widget.google_calendar_email}


async def _ensure_valid_token(widget: Widget, db: Session) -> str:
    now = datetime.now(timezone.utc)
    if widget.google_token_expires_at and widget.google_token_expires_at.replace(tzinfo=timezone.utc) > now:
        return widget.google_access_token

    from config import get_settings
    settings = get_settings()

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "client_id": settings.google_oauth_client_id,
                "client_secret": settings.google_oauth_client_secret,
                "refresh_token": widget.google_refresh_token,
                "grant_type": "refresh_token",
            },
        )
        if response.status_code != 200:
            raise HTTPException(status_code=502, detail="Failed to refresh Google token")
        token_data = response.json()

    widget.google_access_token = token_data["access_token"]
    widget.google_token_expires_at = now + timedelta(seconds=token_data.get("expires_in", 3600))
    db.commit()
    return widget.google_access_token


class CalendarBookRequest(BaseModel):
    summary: str
    description: str = ""
    start_time: str
    end_time: str
    attendee_name: str = ""
    attendee_email: str = ""
    timezone: str = "UTC"


GOOGLE_CALENDAR_API = "https://www.googleapis.com/calendar/v3"


@router.post("/api/widget/{slug}/calendar/book")
async def calendar_book(slug: str, data: CalendarBookRequest, db: Session = Depends(get_db)):
    widget = _get_widget_or_404(db, slug)
    if not widget.google_access_token or not widget.google_refresh_token:
        raise HTTPException(status_code=400, detail="Calendar not connected. Set up OAuth first.")

    access_token = await _ensure_valid_token(widget, db)

    event = {
        "summary": data.summary,
        "description": data.description,
        "start": {
            "dateTime": data.start_time,
            "timeZone": data.timezone,
        },
        "end": {
            "dateTime": data.end_time,
            "timeZone": data.timezone,
        },
    }

    if data.attendee_email:
        event["attendees"] = [
            {"email": data.attendee_email, "displayName": data.attendee_name}
        ]

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(
            f"{GOOGLE_CALENDAR_API}/calendars/primary/events",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            json=event,
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=f"Failed to create event: {response.text}",
            )
        result = response.json()

    return {
        "event_id": result.get("id"),
        "html_link": result.get("htmlLink"),
        "summary": result.get("summary"),
        "start": result.get("start", {}).get("dateTime"),
        "end": result.get("end", {}).get("dateTime"),
    }

    from config import get_settings
    settings = get_settings()

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "client_id": settings.google_oauth_client_id,
                "client_secret": settings.google_oauth_client_secret,
                "refresh_token": widget.google_refresh_token,
                "grant_type": "refresh_token",
            },
        )
        if response.status_code != 200:
            raise HTTPException(status_code=502, detail="Failed to refresh Google token")
        token_data = response.json()

    widget.google_access_token = token_data["access_token"]
    widget.google_token_expires_at = now + timedelta(seconds=token_data.get("expires_in", 3600))
    db.commit()

    return {"access_token": widget.google_access_token, "email": widget.google_calendar_email}
