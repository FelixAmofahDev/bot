"""Dashboard statistics endpoints."""
from fastapi import APIRouter
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import db
from api.schemas import DashboardStats, RecordingResponse, CompletionStat

router = APIRouter()


@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    """Get overall dashboard statistics."""
    return await db.get_dashboard_stats()


@router.get("/dashboard/recent-recordings", response_model=list[RecordingResponse])
async def get_recent_recordings(limit: int = 10):
    """Get the most recent recordings."""
    return await db.get_recent_recordings(min(limit, 50))


@router.get("/dashboard/completion-stats", response_model=list[CompletionStat])
async def get_completion_stats():
    """Get per-participant completion statistics."""
    return await db.get_completion_stats()
