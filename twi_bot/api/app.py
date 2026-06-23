"""FastAPI application for the admin dashboard."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import db
from api.routes import participants, recordings, dashboard, sentences

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle app startup and shutdown."""
    await db.init_pool()
    logger.info("Admin API started with PostgreSQL pool initialized.")
    yield
    await db.close_pool()
    logger.info("Admin API shutdown, PostgreSQL pool closed.")


app = FastAPI(
    title="Twi Speech Admin Dashboard API",
    description="REST API for managing speech data collection",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(participants.router, prefix="/api", tags=["Participants"])
app.include_router(recordings.router, prefix="/api", tags=["Recordings"])
app.include_router(sentences.router, prefix="/api", tags=["Sentences"])
app.include_router(dashboard.router, prefix="/api", tags=["Dashboard"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


# Serve static frontend files
# Source layout: <project>/twi_bot/api/app.py  → parent.parent.parent = project root
# Container layout: /app/api/app.py              → parent.parent = /app (project root)
frontend_dist = Path(__file__).parent.parent.parent / "frontend" / "dist"
if not frontend_dist.exists():
    frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="static")
