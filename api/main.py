from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy.orm import Session

from config import get_settings
from database import init_db, get_db
from models import HealthResponse
from routes.widget import router as widget_router
from routes.chat import router as chat_router
from routes.admin import router as admin_router
from routes.abuse import router as abuse_router

STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="AI Portfolio Assistant API",
    description="Backend API for the AI Portfolio Assistant SaaS",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(widget_router)
app.include_router(chat_router)
app.include_router(admin_router)
app.include_router(abuse_router)


@app.get("/api/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return HealthResponse(
        status="healthy" if db_status == "connected" else "degraded",
        services={
            "database": db_status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@app.get("/")
async def root():
    return {"message": "AI Portfolio Assistant API", "docs": "/docs"}


@app.get("/widget.js")
async def serve_widget_js():
    return FileResponse(STATIC_DIR / "widget.js", media_type="application/javascript")


@app.get("/widget/{slug}", response_class=HTMLResponse)
async def serve_widget(slug: str):
    html = (STATIC_DIR / "widget.html").read_text()
    return HTMLResponse(content=html)
