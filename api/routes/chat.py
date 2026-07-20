from fastapi import APIRouter

router = APIRouter()


@router.post("/api/chat/{slug}")
async def chat(slug: str):
    return {"error": "Not implemented yet"}, 501
