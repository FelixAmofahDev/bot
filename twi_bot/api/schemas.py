"""Pydantic schemas for API request/response validation."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ParticipantCreate(BaseModel):
    name: str = Field(..., description="Participant full name", min_length=1, max_length=128)
    age: str = Field(..., description="Age group (e.g., '18-25')")
    gender: str = Field(..., description="Gender")
    region: str = Field(..., description="Region/District")


class ParticipantUpdate(BaseModel):
    age: Optional[str] = None
    gender: Optional[str] = None
    region: Optional[str] = None


class ParticipantResponse(BaseModel):
    id: int
    speaker_id: str
    name: str
    age: str
    gender: str
    region: str
    telegram_id: Optional[int] = None
    created_at: datetime


class RecordingResponse(BaseModel):
    id: int
    speaker_id: str
    telegram_id: int
    sentence_id: int
    sentence_code: str
    twi_text: str
    audio_path: str
    created_at: datetime


class DashboardStats(BaseModel):
    total_participants: int
    total_recordings: int
    total_sentences: int
    total_completed: int
    submitted_today: int


class CompletionStat(BaseModel):
    speaker_id: str
    recordings_count: int
    completed_count: int


class PaginatedResponse(BaseModel):
    data: list
    total: int
    limit: int
    offset: int


class SentenceCreate(BaseModel):
    text: str = Field(..., description="Twi sentence text", min_length=1)


class SentenceUpdate(BaseModel):
    sentence_id: Optional[str] = Field(None, description="Human-readable code", min_length=1, max_length=32)
    text: Optional[str] = Field(None, description="Twi sentence text", min_length=1)


class SentenceResponse(BaseModel):
    id: int
    sentence_id: str
    text: str
    created_at: datetime


class DeleteCascadeResponse(BaseModel):
    message: str
    recordings_deleted: int
    history_deleted: int
