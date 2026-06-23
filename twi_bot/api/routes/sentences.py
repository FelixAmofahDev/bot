"""Sentence management endpoints."""
from fastapi import APIRouter, HTTPException, Query
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import db
from api.schemas import (
    SentenceCreate,
    SentenceUpdate,
    SentenceResponse,
    DeleteCascadeResponse,
    PaginatedResponse,
)

router = APIRouter()


@router.get("/sentences", response_model=PaginatedResponse)
async def list_sentences(limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0)):
    """Get all sentences with pagination."""
    sentences = await db.list_sentences(limit, offset)
    count = await db.get_sentence_count()
    return {
        "data": sentences,
        "total": count,
        "limit": limit,
        "offset": offset,
    }


@router.get("/sentences/search", response_model=PaginatedResponse)
async def search_sentences(
    q: str = Query(..., min_length=1),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Search sentences by code or text."""
    sentences = await db.search_sentences(q, limit, offset)
    return {
        "data": sentences,
        "total": len(sentences),
        "limit": limit,
        "offset": offset,
    }


@router.get("/sentences/{sentence_id}", response_model=SentenceResponse)
async def get_sentence(sentence_id: int):
    """Get a single sentence by its database ID."""
    sentence = await db.get_sentence_by_id(sentence_id)
    if not sentence:
        raise HTTPException(status_code=404, detail="Sentence not found")
    return sentence


@router.get("/sentences/{sentence_id}/related-counts")
async def get_related_counts(sentence_id: int):
    """Get counts of related recordings and history entries before deleting."""
    sentence = await db.get_sentence_by_id(sentence_id)
    if not sentence:
        raise HTTPException(status_code=404, detail="Sentence not found")

    counts = await db.get_sentence_related_counts(sentence_id)
    return counts


@router.post("/sentences", response_model=SentenceResponse)
async def create_sentence(data: SentenceCreate):
    """Create a new sentence with an auto-generated sentence code."""
    new_id = await db.create_sentence(data.text)
    sentence = await db.get_sentence_by_id(new_id)
    return sentence


@router.put("/sentences/{sentence_id}", response_model=dict)
async def update_sentence(sentence_id: int, data: SentenceUpdate):
    """Update an existing sentence."""
    sentence = await db.get_sentence_by_id(sentence_id)
    if not sentence:
        raise HTTPException(status_code=404, detail="Sentence not found")

    updates = {}
    if data.sentence_id is not None:
        existing = await db.get_sentence_by_code(data.sentence_id)
        if existing and existing["id"] != sentence_id:
            raise HTTPException(status_code=400, detail=f"Sentence code '{data.sentence_id}' already exists")
        updates["sentence_id"] = data.sentence_id
    if data.text is not None:
        updates["text"] = data.text

    if updates:
        await db.update_sentence(sentence_id, updates.get("sentence_id", sentence["sentence_id"]), updates.get("text", sentence["text"]))

    return {"message": "Sentence updated successfully"}


@router.delete("/sentences/{sentence_id}", response_model=DeleteCascadeResponse)
async def delete_sentence(sentence_id: int):
    """Delete a sentence and all related recordings + history entries."""
    sentence = await db.get_sentence_by_id(sentence_id)
    if not sentence:
        raise HTTPException(status_code=404, detail="Sentence not found")

    result = await db.delete_sentence(sentence_id)
    return {
        "message": f"Sentence '{sentence['sentence_id']}' deleted along with {result['recordings_deleted']} recording(s) and {result['history_deleted']} history entry/entries",
        "recordings_deleted": result["recordings_deleted"],
        "history_deleted": result["history_deleted"],
    }
