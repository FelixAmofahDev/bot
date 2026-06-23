"""Participant management endpoints."""
from fastapi import APIRouter, HTTPException, Query
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import db
from api.schemas import (
    ParticipantCreate,
    ParticipantUpdate,
    ParticipantResponse,
    PaginatedResponse,
)

router = APIRouter()


@router.get("/participants", response_model=PaginatedResponse)
async def list_participants(limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0)):
    """Get all participants with pagination."""
    participants = await db.list_participants(limit, offset)
    count = await db.get_participant_count()
    return {
        "data": participants,
        "total": count,
        "limit": limit,
        "offset": offset,
    }


@router.get("/participants/search", response_model=PaginatedResponse)
async def search_participants(
    q: str = Query(..., min_length=1),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Search participants by speaker_id, age, gender, or region."""
    participants = await db.search_participants(q, limit, offset)
    return {
        "data": participants,
        "total": len(participants),
        "limit": limit,
        "offset": offset,
    }


@router.get("/participants/{speaker_id}", response_model=ParticipantResponse)
async def get_participant(speaker_id: str):
    """Get participant details by Speaker ID."""
    participant = await db.get_participant_by_speaker_id(speaker_id)
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    return participant


@router.post("/participants", response_model=dict)
async def create_participant(data: ParticipantCreate):
    """Create a new participant and auto-generate Speaker ID."""
    speaker_id = await db.create_participant(data.name, data.age, data.gender, data.region)
    return {
        "speaker_id": speaker_id,
        "message": f"Participant created successfully with Speaker ID: {speaker_id}",
    }


@router.put("/participants/{speaker_id}", response_model=dict)
async def update_participant(speaker_id: str, data: ParticipantUpdate):
    """Update participant information."""
    participant = await db.get_participant_by_speaker_id(speaker_id)
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")

    await db.update_participant(speaker_id, data.age, data.gender, data.region)
    return {"message": "Participant updated successfully"}


@router.delete("/participants/{speaker_id}", response_model=dict)
async def delete_participant(speaker_id: str):
    """Delete a participant."""
    participant = await db.get_participant_by_speaker_id(speaker_id)
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")

    await db.delete_participant(speaker_id)
    return {"message": "Participant deleted successfully"}
