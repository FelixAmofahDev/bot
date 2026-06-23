"""
STEP 6: Recording capture. Audio is only ever written to temp_audio/ here.
It is moved to permanent storage exclusively by the Submit action in
handlers/callbacks.py.
"""
import asyncio
import logging
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

import config
from constants import (
    CB_DELETE,
    CB_REDO,
    CB_SUBMIT,
    STATE_RECORDING,
    STATE_REVIEW,
    UD_TEMP_AUDIO_PATH,
)

logger = logging.getLogger(__name__)

DOWNLOAD_MAX_ATTEMPTS = 3
DOWNLOAD_RETRY_DELAY_SECONDS = 2.0


def temp_path_for(telegram_id: int) -> str:
    """Deterministic temp filename per user so Redo simply overwrites it."""
    return os.path.join(config.TEMP_AUDIO_DIR, f"{telegram_id}.ogg")


async def _download_with_retry(context: ContextTypes.DEFAULT_TYPE, file_id: str, dest_path: str) -> None:
    """
    Download a Telegram file to disk, retrying on transient network errors
    (dropped connections, timeouts) before giving up.
    """
    last_error: Exception | None = None
    for attempt in range(1, DOWNLOAD_MAX_ATTEMPTS + 1):
        try:
            tg_file = await context.bot.get_file(file_id)
            await tg_file.download_to_drive(dest_path)
            return
        except Exception as exc:  # network/timeout errors from httpx/httpcore
            last_error = exc
            logger.warning(
                "Voice download attempt %s/%s failed: %s",
                attempt, DOWNLOAD_MAX_ATTEMPTS, exc,
            )
            if attempt < DOWNLOAD_MAX_ATTEMPTS:
                await asyncio.sleep(DOWNLOAD_RETRY_DELAY_SECONDS * attempt)
    raise last_error


async def receive_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    telegram_id = update.effective_user.id
    voice = update.message.voice

    if voice is None:
        await update.message.reply_text(
            "Please send your reading as a *voice message* 🎙️.",
            parse_mode="Markdown",
        )
        return STATE_RECORDING

    temp_path = temp_path_for(telegram_id)

    try:
        await _download_with_retry(context, voice.file_id, temp_path)
    except Exception:
        logger.exception("Failed to download voice file for telegram_id=%s", telegram_id)
        await update.message.reply_text(
            "⚠️ Failed to save your recording — your connection may be "
            "unstable. Please try sending it again."
        )
        return STATE_RECORDING

    context.user_data[UD_TEMP_AUDIO_PATH] = temp_path

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✔ Submit", callback_data=CB_SUBMIT),
                InlineKeyboardButton("🔁 Redo", callback_data=CB_REDO),
                InlineKeyboardButton("🗑 Delete", callback_data=CB_DELETE),
            ]
        ]
    )

    await update.message.reply_text(
        "Recording received. What would you like to do?",
        reply_markup=keyboard,
    )
    return STATE_REVIEW


async def remind_voice_only(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Fallback for any non-voice message while we're waiting for a recording."""
    await update.message.reply_text(
        "Please send your reading as a *voice message* 🎙️, not text.",
        parse_mode="Markdown",
    )
    return STATE_RECORDING
