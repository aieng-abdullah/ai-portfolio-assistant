from fastapi import APIRouter
from models import AbuseLogRequest
import json
from datetime import datetime, timezone

router = APIRouter()


@router.post("/api/widget/{slug}/abuse-log")
async def log_abuse(slug: str, request: AbuseLogRequest):
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "slug": slug,
        "sessionId": request.sessionId,
        "filtered": request.filtered,
    }
    print(f"[ABUSE] {json.dumps(log_entry)}")
    return {"status": "logged"}
