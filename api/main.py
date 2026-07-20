from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from config import get_settings
from database import connect_db, disconnect_db
from models import HealthResponse
from routes.widget import router as widget_router
from routes.chat import router as chat_router

STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    await connect_db()
    yield
    await disconnect_db()


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


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    from database import prisma

    db_status = "connected" if prisma.is_connected() else "disconnected"

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
