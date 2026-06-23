"""
STEP 5: Sentence assignment. A sentence is only ever assigned to a
speaker once — enforced via user_sentence_history.
"""
import logging
from typing import Optional

from telegram import Update
from telegram.ext import ContextTypes

import db
from constants import STATE_RECORDING, UD_CURRENT_SENTENCE, UD_SPEAKER_ID

logger = logging.getLogger(__name__)


async def assign_and_send_sentence(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> Optional[int]:
    """
    Picks an unused sentence for the current speaker, records the
    assignment, and sends it to the user as the next reading prompt.

    Returns STATE_RECORDING on success, or None if there are no
    remaining unused sentences (caller should end the conversation).
    """
    speaker_id = context.user_data[UD_SPEAKER_ID]
    telegram_id = update.effective_user.id

    try:
        sentence = await db.get_unused_sentence(speaker_id)
    except Exception:
        logger.exception("DB error while fetching sentence for speaker=%s", speaker_id)
        await update.effective_chat.send_message(
            "⚠️ A system error occurred while fetching your next sentence. "
            "Please try again later."
        )
        return None

    if not sentence:
        await update.effective_chat.send_message(
            "🎉 You have completed all available sentences. Thank you so "
            "much for your contribution to this research!"
        )
        return None

    try:
        await db.create_history_entry(
            telegram_id=telegram_id,
            speaker_id=speaker_id,
            sentence_id=sentence["id"],
            status="assigned",
        )
    except Exception:
        logger.exception("DB error while recording sentence assignment for speaker=%s", speaker_id)
        await update.effective_chat.send_message(
            "⚠️ A system error occurred. Please try again later."
        )
        return None

    context.user_data[UD_CURRENT_SENTENCE] = sentence

    await update.effective_chat.send_message(
        "📖 Please read the following sentence aloud and send it as a "
        f"*voice message*:\n\n_{sentence['text']}_",
        parse_mode="Markdown",
    )
    return STATE_RECORDING
