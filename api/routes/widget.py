import json
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db, Widget
from models import WidgetConfigResponse, ProfileResponse

router = APIRouter()


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
