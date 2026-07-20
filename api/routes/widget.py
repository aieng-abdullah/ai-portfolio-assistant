from fastapi import APIRouter, HTTPException
from database import prisma
from models import WidgetConfigResponse, ProfileResponse

router = APIRouter()


async def _get_widget_or_404(slug: str):
    widget = await prisma.widget.find_unique(where={"slug": slug})
    if not widget:
        raise HTTPException(status_code=404, detail=f"Widget '{slug}' not found")
    if not widget.isActive:
        raise HTTPException(status_code=403, detail="Widget is disabled")
    return widget


@router.get("/api/widget/{slug}/config", response_model=WidgetConfigResponse)
async def get_widget_config(slug: str):
    widget = await _get_widget_or_404(slug)
    return WidgetConfigResponse(
        name=widget.name,
        theme=widget.theme if isinstance(widget.theme, dict) else {},
        personality=widget.personality if isinstance(widget.personality, dict) else {},
    )


@router.get("/api/widget/{slug}/profile", response_model=ProfileResponse)
async def get_widget_profile(slug: str):
    widget = await _get_widget_or_404(slug)
    profile = widget.profile if isinstance(widget.profile, dict) else {}
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
async def get_widget_projects(slug: str):
    widget = await _get_widget_or_404(slug)
    return widget.projects if isinstance(widget.projects, list) else []


@router.get("/api/widget/{slug}/services")
async def get_widget_services(slug: str):
    widget = await _get_widget_or_404(slug)
    return widget.services if isinstance(widget.services, list) else []


@router.get("/api/widget/{slug}/faq")
async def get_widget_faq(slug: str):
    widget = await _get_widget_or_404(slug)
    return widget.faq if isinstance(widget.faq, list) else []
