from fastapi import APIRouter, HTTPException
from models import ChatRequest, ChatResponse, RateLimitResponse
from services.chat_proxy import check_rate_limit, log_message, proxy_to_n8n
from database import prisma

router = APIRouter()


@router.post("/api/chat/{slug}", response_model=ChatResponse)
async def chat(slug: str, request: ChatRequest):
    # Verify widget exists and is active
    widget = await prisma.widget.find_unique(where={"slug": slug})
    if not widget:
        raise HTTPException(status_code=404, detail=f"Widget '{slug}' not found")
    if not widget.isActive:
        raise HTTPException(status_code=403, detail="Chat is temporarily unavailable")

    # Rate limit check
    limits = await check_rate_limit(slug, request.sessionId)
    if limits.get("over_limit"):
        return ChatResponse(
            response="You've reached the chat limit. Please try again later.",
            sessionId=request.sessionId,
        )

    # Log user message
    await log_message(slug, request.sessionId, "user", request.message)

    # Proxy to n8n
    response = await proxy_to_n8n(slug, request.sessionId, request.message)

    # Log assistant response
    await log_message(slug, request.sessionId, "assistant", response)

    return ChatResponse(response=response, sessionId=request.sessionId)


@router.get("/api/widget/{slug}/rate-limit", response_model=RateLimitResponse)
async def get_rate_limit(slug: str, sessionId: str):
    limits = await check_rate_limit(slug, sessionId)
    return RateLimitResponse(
        over_limit=limits.get("over_limit", True),
        session_messages=limits.get("session_messages", 0),
        session_limit=limits.get("session_limit", 30),
        daily_messages=limits.get("daily_messages", 0),
        daily_limit=limits.get("daily_limit", 1000),
    )
