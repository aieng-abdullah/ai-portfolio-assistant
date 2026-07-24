from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db, Widget, AbuseLog

router = APIRouter()


class AbuseLogRequest(BaseModel):
    sessionId: str
    reason: str
    originalMessage: str | None = None


@router.post("/api/widget/{slug}/abuse-log")
async def log_abuse(slug: str, data: AbuseLogRequest, db: Session = Depends(get_db)):
    widget = db.query(Widget).filter(Widget.slug == slug).first()
    if not widget:
        raise HTTPException(status_code=404, detail=f"Widget '{slug}' not found")

    log = AbuseLog(
        widgetId=widget.id,
        sessionId=data.sessionId,
        reason=data.reason,
        originalMessage=data.originalMessage[:2000] if data.originalMessage else None,
    )
    db.add(log)
    db.commit()

    return {"message": "Abuse logged", "reason": data.reason}
