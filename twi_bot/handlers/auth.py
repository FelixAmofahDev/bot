"""
STEP 1 & 2: Speaker ID entry and validation against PostgreSQL.
"""
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

import db
from constants import (
    CB_CONFIRM_NO,
    CB_CONFIRM_YES,
    STATE_CONFIRM_ID,
    STATE_SPEAKER_ID,
    UD_PARTICIPANT,
    UD_SPEAKER_ID,
)

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(
        "👋 Welcome to the Twi Speech Data Collection Bot.\n\n"
        "This bot is only for participants who have been registered by a "
        "researcher.\n\n"
        "👉 Please enter your Speaker ID (e.g. SPK1001):"
    )
    return STATE_SPEAKER_ID


async def receive_speaker_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    speaker_id = (update.message.text or "").strip().upper()

    if not speaker_id:
        await update.message.reply_text("👉 Please enter your Speaker ID:")
        return STATE_SPEAKER_ID

    try:
        participant = await db.get_participant_by_speaker_id(speaker_id)
    except Exception:
        logger.exception("DB error while looking up speaker_id=%s", speaker_id)
        await update.message.reply_text(
            "⚠️ A system error occurred. Please try again in a moment."
        )
        return STATE_SPEAKER_ID

    if not participant:
        await update.message.reply_text(
            "❌ Speaker ID not found. Please check with your researcher and "
            "enter your Speaker ID again:"
        )
        return STATE_SPEAKER_ID

    context.user_data[UD_SPEAKER_ID] = speaker_id
    context.user_data[UD_PARTICIPANT] = participant

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✔ Confirm", callback_data=CB_CONFIRM_YES),
                InlineKeyboardButton("❌ Wrong ID", callback_data=CB_CONFIRM_NO),
            ]
        ]
    )

    await update.message.reply_text(
        f"Speaker ID: {participant['speaker_id']}\n"
        f"Name: {participant['name']}\n"
        f"Age: {participant['age']}\n"
        f"Gender: {participant['gender']}\n"
        f"Region: {participant['region']}\n\n"
        "Confirm details?",
        reply_markup=keyboard,
    )
    return STATE_CONFIRM_ID
