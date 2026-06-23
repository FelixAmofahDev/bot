"""
STEP 4: Consent prompt.
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from constants import CB_CONSENT_NO, CB_CONSENT_YES


async def ask_consent(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✅ I Consent", callback_data=CB_CONSENT_YES),
                InlineKeyboardButton("🚫 I Do Not Consent", callback_data=CB_CONSENT_NO),
            ]
        ]
    )
    await update.effective_chat.send_message(
        "Do you consent to participate in Twi speech data collection?\n\n"
        "Your voice recordings will be used for research purposes, "
        "including training speech recognition models for the Twi "
        "language.",
        reply_markup=keyboard,
    )
