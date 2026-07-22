import httpx
import json
from urllib.parse import urlencode
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session

from app.database import get_db, Widget
from app.config import get_settings

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
REDIRECT_URI = "http://localhost:3000/api/auth/google/callback"
SCOPES = "https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/calendar.events"

router = APIRouter()


@router.get("/api/auth/google")
async def google_auth(slug: str = "portfolio", db: Session = Depends(get_db)):
    widget = db.query(Widget).filter(Widget.slug == slug).first()
    if not widget:
        raise HTTPException(status_code=404, detail=f"Widget '{slug}' not found")

    settings = get_settings()
    if not settings.google_oauth_client_id or not settings.google_oauth_client_secret:
        raise HTTPException(status_code=500, detail="Google OAuth credentials not configured")

    params = {
        "client_id": settings.google_oauth_client_id,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPES,
        "access_type": "offline",
        "prompt": "consent",
        "state": slug,
    }
    qs = urlencode(params)
    return RedirectResponse(url=f"{GOOGLE_AUTH_URL}?{qs}")


@router.get("/api/auth/google/callback")
async def google_callback(code: str, state: str = "portfolio", db: Session = Depends(get_db)):
    settings = get_settings()

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "client_id": settings.google_oauth_client_id,
                "client_secret": settings.google_oauth_client_secret,
                "code": code,
                "redirect_uri": REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )
        if resp.status_code != 200:
            return HTMLResponse(
                f"<h2>Error</h2><p>Failed to exchange code: {resp.text}</p>",
                status_code=400,
            )
        token_data = resp.json()

    widget = db.query(Widget).filter(Widget.slug == state).first()
    if not widget:
        return HTMLResponse("<h2>Error</h2><p>Widget not found</p>", status_code=404)

    widget.google_access_token = token_data["access_token"]
    widget.google_refresh_token = token_data.get("refresh_token", widget.google_refresh_token)
    widget.google_token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=token_data.get("expires_in", 3600))
    widget.google_calendar_email = token_data.get("email", "")
    db.commit()

    return HTMLResponse("""
    <html><body style="font-family:sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;background:#1a1a1a;color:#f3ebe4;">
    <div style="text-align:center;max-width:400px;">
        <h1 style="color:#fcaa2d;">✓ Google Calendar Connected</h1>
        <p>You can close this window and test booking via <a href="/docs" style="color:#fcaa2d;">Swagger</a>.</p>
    </div></body></html>
    """)
