"""Recording management endpoints."""
from fastapi import APIRouter, HTTPException, Query
from starlette.responses import FileResponse, RedirectResponse
from datetime import date
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import db
import config
from api.schemas import RecordingResponse, PaginatedResponse

router = APIRouter()


@router.get("/recordings", response_model=PaginatedResponse)
async def list_recordings(limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0)):
    """Get all recordings with pagination."""
    recordings = await db.list_recordings(limit, offset)
    count = await db.get_recordings_count()
    return {
        "data": recordings,
        "total": count,
        "limit": limit,
        "offset": offset,
    }


@router.get("/recordings/search", response_model=PaginatedResponse)
async def search_recordings(
    q: str = Query(..., min_length=1),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Search recordings by speaker_id or sentence_id."""
    recordings = await db.search_recordings(q, limit, offset)
    return {
        "data": recordings,
        "total": len(recordings),
        "limit": limit,
        "offset": offset,
    }


@router.get("/recordings/by-speaker/{speaker_id}", response_model=PaginatedResponse)
async def get_recordings_by_speaker(
    speaker_id: str,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Get recordings for a specific speaker."""
    recordings = await db.get_recordings_by_speaker(speaker_id, limit, offset)
    return {
        "data": recordings,
        "total": len(recordings),
        "limit": limit,
        "offset": offset,
    }


@router.get("/recordings/by-date", response_model=PaginatedResponse)
async def get_recordings_by_date(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Get recordings within a date range."""
    recordings = await db.get_recordings_by_date_range(start_date, end_date, limit, offset)
    return {
        "data": recordings,
        "total": len(recordings),
        "limit": limit,
        "offset": offset,
    }


@router.get("/recordings/{recording_id}/audio")
async def download_audio(recording_id: int):
    """Download or stream audio file for a recording."""
    recording = await db.get_recording_by_id(recording_id)
    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")

    audio_path = recording["audio_path"]

    # If audio_path is already a full URL (Google Drive, R2 public, etc.), redirect to it
    if audio_path.startswith("http://") or audio_path.startswith("https://"):
        return RedirectResponse(url=audio_path, status_code=302)

    # Check if R2 is enabled
    if os.getenv("R2_ENABLED", "false").lower() == "true":
        public_url = os.getenv("R2_PUBLIC_URL")
        if public_url:
            return RedirectResponse(url=f"{public_url.rstrip('/')}/{audio_path}", status_code=302)
        endpoint = os.getenv("R2_ENDPOINT", "").rstrip("/")
        bucket = os.getenv("R2_BUCKET_NAME", "twi-audio")
        if endpoint and bucket:
            return RedirectResponse(url=f"{endpoint}/{bucket}/{audio_path}", status_code=302)
        raise HTTPException(status_code=500, detail="R2 is enabled but not configured")

    # Otherwise, serve from local filesystem
    full_path = os.path.join(config.AUDIO_DIR, audio_path.lstrip("/"))
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="Audio file not found")

    return FileResponse(
        full_path,
        media_type="audio/mpeg",
        filename=os.path.basename(full_path),
    )


@router.delete("/recordings/{recording_id}", response_model=dict)
async def delete_recording(recording_id: int):
    """Delete a recording."""
    recording = await db.get_recording_by_id(recording_id)
    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")

    await db.delete_recording(recording_id)
    return {"message": "Recording deleted successfully"}
