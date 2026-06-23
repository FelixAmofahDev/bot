"""
Async PostgreSQL access layer using asyncpg with a shared connection pool.
Raw SQL is used deliberately (per spec) for transparency and simplicity —
no ORM layer to reason about.
"""
import logging
import secrets
from typing import Optional
import os

import asyncpg

logger = logging.getLogger(__name__)

_pool: Optional[asyncpg.Pool] = None


async def init_pool() -> None:
    """Create the global connection pool. Call once at application startup."""
    global _pool

    _pool = await asyncpg.create_pool(
        dsn=os.getenv("DATABASE_URL"),
        min_size=1,
        max_size=10,
        ssl="require"
    )

    logger.info("PostgreSQL pool created using Neon DATABASE_URL")


async def close_pool() -> None:
    """Close the global connection pool. Call once at application shutdown."""
    global _pool
    if _pool is not None:
        await _pool.close()
        logger.info("PostgreSQL connection pool closed.")
        _pool = None


def _get_pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("DB pool not initialized — call db.init_pool() first.")
    return _pool


# ---------------------------------------------------------------------
# participants
# ---------------------------------------------------------------------
async def get_participant_by_speaker_id(speaker_id: str) -> Optional[dict]:
    row = await _get_pool().fetchrow(
        "SELECT id, telegram_id, speaker_id, name, age, gender, region "
        "FROM participants WHERE speaker_id = $1",
        speaker_id,
    )
    return dict(row) if row else None


async def bind_telegram_id(speaker_id: str, telegram_id: int) -> None:
    """
    Link a Telegram account to a speaker_id the first time it is verified.
    Only fills in telegram_id if it was previously NULL.
    """
    await _get_pool().execute(
        "UPDATE participants SET telegram_id = $1 "
        "WHERE speaker_id = $2 AND telegram_id IS NULL",
        telegram_id, speaker_id,
    )


# ---------------------------------------------------------------------
# sentences / user_sentence_history
# ---------------------------------------------------------------------
async def get_unused_sentence(speaker_id: str) -> Optional[dict]:
    """
    Pick a random sentence that has never appeared in this speaker's
    history (in either 'assigned' or 'completed' state), so a sentence
    can never repeat for the same speaker.
    """
    row = await _get_pool().fetchrow(
        """
        SELECT s.id, s.sentence_id, s.text
        FROM sentences s
        WHERE s.id NOT IN (
            SELECT ush.sentence_id
            FROM user_sentence_history ush
            WHERE ush.speaker_id = $1
        )
        ORDER BY RANDOM()
        LIMIT 1
        """,
        speaker_id,
    )
    return dict(row) if row else None


async def create_history_entry(
    telegram_id: int, speaker_id: str, sentence_id: int, status: str = "assigned"
) -> None:
    await _get_pool().execute(
        "INSERT INTO user_sentence_history "
        "(telegram_id, speaker_id, sentence_id, status) "
        "VALUES ($1, $2, $3, $4)",
        telegram_id, speaker_id, sentence_id, status,
    )


async def mark_sentence_completed(speaker_id: str, sentence_id: int) -> None:
    await _get_pool().execute(
        "UPDATE user_sentence_history "
        "SET status = 'completed' "
        "WHERE speaker_id = $1 AND sentence_id = $2 AND status = 'assigned'",
        speaker_id, sentence_id,
    )


# --- Sentences Admin ----------------------------------------------------
async def _get_next_sentence_code() -> str:
    """Generate the next sequential sentence code (SENT0001, SENT0002, ...)."""
    row = await _get_pool().fetchrow(
        "SELECT sentence_id FROM sentences ORDER BY sentence_id DESC LIMIT 1"
    )
    if row:
        last_code = row["sentence_id"]
        num = int(last_code.replace("SENT", "")) + 1
    else:
        num = 1
    return f"SENT{num:04d}"


async def list_sentences(limit: int = 50, offset: int = 0) -> list[dict]:
    """Get paginated list of all sentences."""
    rows = await _get_pool().fetch(
        "SELECT id, sentence_id, text, created_at "
        "FROM sentences ORDER BY created_at DESC LIMIT $1 OFFSET $2",
        limit, offset,
    )
    return [dict(r) for r in rows]


async def get_sentence_by_id(sentence_id: int) -> Optional[dict]:
    """Get a single sentence by its auto-increment ID."""
    row = await _get_pool().fetchrow(
        "SELECT id, sentence_id, text, created_at "
        "FROM sentences WHERE id = $1",
        sentence_id,
    )
    return dict(row) if row else None


async def get_sentence_by_code(sentence_code: str) -> Optional[dict]:
    """Get a single sentence by its human-readable code (e.g. SENT0001)."""
    row = await _get_pool().fetchrow(
        "SELECT id, sentence_id, text, created_at "
        "FROM sentences WHERE sentence_id = $1",
        sentence_code,
    )
    return dict(row) if row else None


async def create_sentence(text: str) -> int:
    """Create a new sentence with an auto-generated code (SENT0001, ...) and return its ID."""
    sentence_id = await _get_next_sentence_code()
    row = await _get_pool().fetchrow(
        "INSERT INTO sentences (sentence_id, text) VALUES ($1, $2) RETURNING id",
        sentence_id, text,
    )
    return row["id"]


async def update_sentence(id: int, sentence_id: str, text: str) -> None:
    """Update an existing sentence by its auto-increment ID."""
    await _get_pool().execute(
        "UPDATE sentences SET sentence_id = $1, text = $2 WHERE id = $3",
        sentence_id, text, id,
    )


async def delete_sentence(id: int) -> dict:
    """Delete a sentence and all related recordings + history entries."""
    pool = _get_pool()
    recording_count = await pool.fetchval(
        "SELECT COUNT(*) FROM recordings WHERE sentence_id = $1", id
    )
    history_count = await pool.fetchval(
        "SELECT COUNT(*) FROM user_sentence_history WHERE sentence_id = $1", id
    )
    await pool.execute("DELETE FROM recordings WHERE sentence_id = $1", id)
    await pool.execute("DELETE FROM user_sentence_history WHERE sentence_id = $1", id)
    await pool.execute("DELETE FROM sentences WHERE id = $1", id)

    return {
        "recordings_deleted": recording_count,
        "history_deleted": history_count,
    }


async def get_sentence_count() -> int:
    """Get total count of sentences."""
    return await _get_pool().fetchval("SELECT COUNT(*) FROM sentences")


async def get_sentence_related_counts(sentence_db_id: int) -> dict:
    """Count related recordings and history entries for a sentence."""
    pool = _get_pool()
    recording_count = await pool.fetchval(
        "SELECT COUNT(*) FROM recordings WHERE sentence_id = $1", sentence_db_id
    )
    history_count = await pool.fetchval(
        "SELECT COUNT(*) FROM user_sentence_history WHERE sentence_id = $1", sentence_db_id
    )
    return {
        "recordings": recording_count,
        "history": history_count,
    }


async def search_sentences(query: str, limit: int = 50, offset: int = 0) -> list[dict]:
    """Search sentences by sentence_id or text."""
    search_term = f"%{query}%"
    rows = await _get_pool().fetch(
        "SELECT id, sentence_id, text, created_at "
        "FROM sentences WHERE sentence_id LIKE $1 OR text LIKE $2 "
        "ORDER BY created_at DESC LIMIT $3 OFFSET $4",
        search_term, search_term, limit, offset,
    )
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------
# recordings
# ---------------------------------------------------------------------
async def save_recording(
    telegram_id: int, speaker_id: str, sentence_id: int, audio_path: str
) -> None:
    await _get_pool().execute(
        "INSERT INTO recordings "
        "(telegram_id, speaker_id, sentence_id, audio_path) "
        "VALUES ($1, $2, $3, $4)",
        telegram_id, speaker_id, sentence_id, audio_path,
    )


# =====================================================================
# ADMIN DASHBOARD FUNCTIONS
# =====================================================================

# --- Participants Admin ------------------------------------------------
_VALID_SPK_CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZ0123456789"


def _generate_spk_suffix(length: int = 8) -> str:
    return "".join(secrets.choice(_VALID_SPK_CHARS) for _ in range(length))


async def get_next_speaker_id() -> str:
    """Generate a unique Speaker ID: SPK + 8 alphanumeric chars (no O/I to avoid visual confusion)."""
    while True:
        speaker_id = f"SPK{_generate_spk_suffix(8)}"
        row = await _get_pool().fetchrow(
            "SELECT id FROM participants WHERE speaker_id = $1",
            speaker_id,
        )
        if row is None:
            return speaker_id


async def create_participant(name: str, age: str, gender: str, region: str) -> str:
    """Create a new participant and return the generated speaker_id."""
    speaker_id = await get_next_speaker_id()
    await _get_pool().execute(
        "INSERT INTO participants (speaker_id, name, age, gender, region) "
        "VALUES ($1, $2, $3, $4, $5)",
        speaker_id, name, age, gender, region,
    )
    return speaker_id


async def list_participants(limit: int = 50, offset: int = 0) -> list[dict]:
    """Get paginated list of all participants."""
    rows = await _get_pool().fetch(
        "SELECT id, speaker_id, name, age, gender, region, telegram_id, created_at "
        "FROM participants ORDER BY created_at DESC LIMIT $1 OFFSET $2",
        limit, offset,
    )
    return [dict(r) for r in rows]


async def get_participant_count() -> int:
    """Get total count of participants."""
    return await _get_pool().fetchval("SELECT COUNT(*) FROM participants")


async def search_participants(query: str, limit: int = 50, offset: int = 0) -> list[dict]:
    """Search participants by speaker_id, name, age, gender, or region."""
    search_term = f"%{query}%"
    rows = await _get_pool().fetch(
        "SELECT id, speaker_id, name, age, gender, region, telegram_id, created_at "
        "FROM participants WHERE speaker_id LIKE $1 OR name LIKE $2 OR age LIKE $3 "
        "OR gender LIKE $4 OR region LIKE $5 "
        "ORDER BY created_at DESC LIMIT $6 OFFSET $7",
        search_term, search_term, search_term, search_term, search_term, limit, offset,
    )
    return [dict(r) for r in rows]


async def update_participant(speaker_id: str, age: str = None, gender: str = None, region: str = None) -> None:
    """Update participant information."""
    updates = []
    params = []
    if age is not None:
        updates.append("age = $1")
        params.append(age)
    if gender is not None:
        updates.append(f"gender = ${len(updates) + 1}")
        params.append(gender)
    if region is not None:
        updates.append(f"region = ${len(updates) + 1}")
        params.append(region)

    if updates:
        params.append(speaker_id)
        query = f"UPDATE participants SET {', '.join(updates)} WHERE speaker_id = ${len(params)}"
        await _get_pool().execute(query, *params)


async def delete_participant(speaker_id: str) -> None:
    """Delete a participant by speaker_id."""
    await _get_pool().execute("DELETE FROM participants WHERE speaker_id = $1", speaker_id)


# --- Recordings Admin --------------------------------------------------
async def list_recordings(limit: int = 50, offset: int = 0) -> list[dict]:
    """Get paginated list of all recordings."""
    rows = await _get_pool().fetch(
        "SELECT r.id, r.telegram_id, r.speaker_id, r.sentence_id, "
        "s.sentence_id as sentence_code, s.text as twi_text, "
        "r.audio_path, r.created_at "
        "FROM recordings r "
        "JOIN sentences s ON r.sentence_id = s.id "
        "ORDER BY r.created_at DESC LIMIT $1 OFFSET $2",
        limit, offset,
    )
    return [dict(r) for r in rows]


async def get_recordings_count() -> int:
    """Get total count of recordings."""
    return await _get_pool().fetchval("SELECT COUNT(*) FROM recordings")


async def get_recordings_by_speaker(speaker_id: str, limit: int = 50, offset: int = 0) -> list[dict]:
    """Get recordings for a specific speaker."""
    rows = await _get_pool().fetch(
        "SELECT r.id, r.telegram_id, r.speaker_id, r.sentence_id, "
        "s.sentence_id as sentence_code, s.text as twi_text, "
        "r.audio_path, r.created_at "
        "FROM recordings r "
        "JOIN sentences s ON r.sentence_id = s.id "
        "WHERE r.speaker_id = $1 "
        "ORDER BY r.created_at DESC LIMIT $2 OFFSET $3",
        speaker_id, limit, offset,
    )
    return [dict(r) for r in rows]


async def get_recordings_by_date_range(start_date: str, end_date: str, limit: int = 50, offset: int = 0) -> list[dict]:
    """Get recordings within a date range (YYYY-MM-DD format)."""
    rows = await _get_pool().fetch(
        "SELECT r.id, r.telegram_id, r.speaker_id, r.sentence_id, "
        "s.sentence_id as sentence_code, s.text as twi_text, "
        "r.audio_path, r.created_at "
        "FROM recordings r "
        "JOIN sentences s ON r.sentence_id = s.id "
        "WHERE DATE(r.created_at) BETWEEN $1 AND $2 "
        "ORDER BY r.created_at DESC LIMIT $3 OFFSET $4",
        start_date, end_date, limit, offset,
    )
    return [dict(r) for r in rows]


async def search_recordings(query: str, limit: int = 50, offset: int = 0) -> list[dict]:
    """Search recordings by speaker_id or sentence_id."""
    search_term = f"%{query}%"
    rows = await _get_pool().fetch(
        "SELECT r.id, r.telegram_id, r.speaker_id, r.sentence_id, "
        "s.sentence_id as sentence_code, s.text as twi_text, "
        "r.audio_path, r.created_at "
        "FROM recordings r "
        "JOIN sentences s ON r.sentence_id = s.id "
        "WHERE r.speaker_id LIKE $1 OR s.sentence_id LIKE $2 "
        "ORDER BY r.created_at DESC LIMIT $3 OFFSET $4",
        search_term, search_term, limit, offset,
    )
    return [dict(r) for r in rows]


async def get_recording_by_id(recording_id: int) -> Optional[dict]:
    """Get a single recording by ID."""
    row = await _get_pool().fetchrow(
        "SELECT r.id, r.telegram_id, r.speaker_id, r.sentence_id, "
        "s.sentence_id as sentence_code, s.text as twi_text, "
        "r.audio_path, r.created_at "
        "FROM recordings r "
        "JOIN sentences s ON r.sentence_id = s.id "
        "WHERE r.id = $1",
        recording_id,
    )
    return dict(row) if row else None


async def delete_recording(recording_id: int) -> None:
    """Delete a recording by ID."""
    await _get_pool().execute("DELETE FROM recordings WHERE id = $1", recording_id)


# --- Dashboard Stats ---------------------------------------------------
async def get_dashboard_stats() -> dict:
    """Get overall dashboard statistics."""
    pool = _get_pool()
    total_participants = await pool.fetchval("SELECT COUNT(*) FROM participants")
    total_recordings = await pool.fetchval("SELECT COUNT(*) FROM recordings")
    total_sentences = await pool.fetchval("SELECT COUNT(*) FROM sentences")
    total_completed = await pool.fetchval(
        "SELECT COUNT(*) FROM user_sentence_history WHERE status = 'completed'"
    )
    submitted_today = await pool.fetchval(
        "SELECT COUNT(*) FROM recordings WHERE DATE(created_at) = CURRENT_DATE"
    )

    return {
        "total_participants": total_participants,
        "total_recordings": total_recordings,
        "total_sentences": total_sentences,
        "total_completed": total_completed,
        "submitted_today": submitted_today,
    }


async def get_recent_recordings(limit: int = 10) -> list[dict]:
    """Get the most recent recordings."""
    rows = await _get_pool().fetch(
        "SELECT r.id, r.telegram_id, r.speaker_id, r.sentence_id, "
        "s.sentence_id as sentence_code, s.text as twi_text, "
        "r.audio_path, r.created_at "
        "FROM recordings r "
        "JOIN sentences s ON r.sentence_id = s.id "
        "ORDER BY r.created_at DESC LIMIT $1",
        limit,
    )
    return [dict(r) for r in rows]


async def get_completion_stats() -> list[dict]:
    """Get per-participant completion stats."""
    rows = await _get_pool().fetch(
        "SELECT p.speaker_id, COUNT(DISTINCT r.id) as recordings_count, "
        "COUNT(DISTINCT ush.sentence_id) as completed_count "
        "FROM participants p "
        "LEFT JOIN recordings r ON p.speaker_id = r.speaker_id "
        "LEFT JOIN user_sentence_history ush ON p.speaker_id = ush.speaker_id "
        "AND ush.status = 'completed' "
        "GROUP BY p.speaker_id "
        "ORDER BY completed_count DESC"
    )
    return [dict(r) for r in rows]
