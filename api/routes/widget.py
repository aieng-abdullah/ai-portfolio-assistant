from fastapi import APIRouter

router = APIRouter()


@router.get("/api/widget/{slug}/config")
async def get_widget_config(slug: str):
    return {"error": "Not implemented yet"}, 501


@router.get("/api/widget/{slug}/profile")
async def get_widget_profile(slug: str):
    return {"error": "Not implemented yet"}, 501


@router.get("/api/widget/{slug}/projects")
async def get_widget_projects(slug: str):
    return {"error": "Not implemented yet"}, 501


@router.get("/api/widget/{slug}/services")
async def get_widget_services(slug: str):
    return {"error": "Not implemented yet"}, 501


@router.get("/api/widget/{slug}/faq")
async def get_widget_faq(slug: str):
    return {"error": "Not implemented yet"}, 501
