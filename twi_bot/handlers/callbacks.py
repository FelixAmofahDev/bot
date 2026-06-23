"""
All inline-button (CallbackQueryHandler) logic lives here:
  - Speaker ID confirmation (STEP 3)
  - Consent (STEP 4)
  - Submit / Redo / Delete on a recording (STEP 7)
"""
import asyncio
import logging
import os
import shutil

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

import config
import db
import drive_storage
from constants import (
    CB_CONFIRM_NO,
    CB_CONFIRM_YES,
    CB_CONSENT_NO,
    CB_DELETE,
    CB_REDO,
    CB_SUBMIT,
    STATE_CONSENT,
    STATE_RECORDING,
    STATE_REVIEW,
    STATE_SPEAKER_ID,
    UD_CURRENT_SENTENCE,
    UD_PARTICIPANT,
    UD_SPEAKER_ID,
    UD_TEMP_AUDIO_PATH,
)
from handlers.consent import ask_consent
from handlers.recording import temp_path_for
from handlers.sentences import assign_and_send_sentence

logger = logging.getLogger(__name__)


def _get_r2_client():
    import boto3
    return boto3.client(
        "s3",
        endpoint_url=os.getenv("R2_ENDPOINT"),
        aws_access_key_id=os.getenv("R2_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("R2_SECRET_ACCESS_KEY"),
    )


async def _upload_to_r2(local_path: str, key: str) -> bool:
    """Upload a local file to Cloudflare R2. Returns True on success."""
    if os.getenv("R2_ENABLED", "false").lower() != "true":
        return False
    endpoint = os.getenv("R2_ENDPOINT")
    access_key = os.getenv("R2_ACCESS_KEY_ID")
    secret_key = os.getenv("R2_SECRET_ACCESS_KEY")
    if not endpoint or not access_key or not secret_key:
        return False
    try:
        loop = asyncio.get_running_loop()
        client = _get_r2_client()
        await loop.run_in_executor(
            None,
            lambda: client.upload_file(
                Filename=local_path,
                Bucket=os.getenv("R2_BUCKET_NAME", "twi-audio"),
                Key=key,
            ),
        )
        logger.info("Uploaded to R2: %s", key)
        return True
    except Exception:
        logger.exception("Failed to upload %s to R2", key)
        return False


async def _delete_local(path: str) -> None:
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        logger.warning("Failed to delete local file %s", path)


async def _upload_to_drive(local_path: str, file_name: str) -> tuple[bool, str]:
    """
    Upload a local file to Google Drive.
    
    Returns:
        Tuple of (success: bool, url_or_path: str)
        - If success: (True, shareable_url)
        - If failure: (False, local_path to use as fallback)
    """
    if not config.GOOGLE_DRIVE_ENABLED:
        logger.info("Google Drive disabled, skipping upload for %s", file_name)
        return False, local_path
    
    logger.info("Attempting Google Drive upload for: %s (folder_id: %s)", file_name, config.GOOGLE_DRIVE_FOLDER_ID)
    
    try:
        drive_url = await drive_storage.upload_file_to_drive(
            file_path=local_path,
            file_name=file_name,
            folder_id=config.GOOGLE_DRIVE_FOLDER_ID,
        )
        logger.info("✅ Successfully uploaded to Google Drive: %s → %s", file_name, drive_url)
        return True, drive_url
    except Exception as e:
        logger.exception("❌ Failed to upload %s to Google Drive: %s", file_name, str(e))
        logger.info("⚠️ Falling back to local storage for: %s", file_name)
        return False, local_path


# ---------------------------------------------------------------------
# STEP 3: Speaker ID confirmation
# ---------------------------------------------------------------------
async def confirm_id_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == CB_CONFIRM_NO:
        context.user_data.pop(UD_SPEAKER_ID, None)
        context.user_data.pop(UD_PARTICIPANT, None)
        await query.edit_message_text("No problem. 👉 Please enter your Speaker ID again:")
        return STATE_SPEAKER_ID

    speaker_id = context.user_data[UD_SPEAKER_ID]
    telegram_id = update.effective_user.id

    try:
        await db.bind_telegram_id(speaker_id, telegram_id)
    except Exception:
        # Non-fatal: the participant can still proceed even if binding fails.
        logger.exception("Failed to bind telegram_id for speaker_id=%s", speaker_id)

    await query.edit_message_text(f"✅ Identity confirmed: {speaker_id}")
    await ask_consent(update, context)
    return STATE_CONSENT


# ---------------------------------------------------------------------
# STEP 4: Consent
# ---------------------------------------------------------------------
async def consent_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == CB_CONSENT_NO:
        await query.edit_message_text(
            "Thank you for your time. You have chosen not to participate. "
            "Have a good day! 🙏"
        )
        return ConversationHandler.END

    await query.edit_message_text("✅ Thank you for consenting to participate.")

    next_state = await assign_and_send_sentence(update, context)
    return next_state if next_state is not None else ConversationHandler.END


# ---------------------------------------------------------------------
# STEP 7: Submit / Redo / Delete
# ---------------------------------------------------------------------
async def review_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    telegram_id = update.effective_user.id
    temp_path = context.user_data.get(UD_TEMP_AUDIO_PATH) or temp_path_for(telegram_id)

    if query.data == CB_DELETE:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        context.user_data.pop(UD_TEMP_AUDIO_PATH, None)
        await query.edit_message_text(
            "🗑 Recording deleted. Please send a new voice recording for the "
            "same sentence."
        )
        return STATE_RECORDING

    if query.data == CB_REDO:
        await query.edit_message_text(
            "🔁 Okay — please send a new voice recording, it will replace "
            "the previous one."
        )
        return STATE_RECORDING

    # CB_SUBMIT
    if not os.path.exists(temp_path):
        await query.edit_message_text(
            "⚠️ Could not find your recording. Please record it again."
        )
        return STATE_RECORDING

    speaker_id = context.user_data[UD_SPEAKER_ID]
    sentence = context.user_data[UD_CURRENT_SENTENCE]

    relative_path = os.path.join(speaker_id, f"{sentence['sentence_id']}.ogg")
    permanent_path = os.path.join(config.AUDIO_DIR, relative_path)

    try:
        # Create speaker directory if it doesn't exist
        os.makedirs(os.path.dirname(permanent_path), exist_ok=True)
        
        shutil.move(temp_path, permanent_path)
        
        # Try Google Drive first, then fall back to R2 or local storage
        audio_path = permanent_path
        
        if config.GOOGLE_DRIVE_ENABLED:
            # Generate a descriptive file name for Google Drive
            # Format: {speaker_id}/{sentence_id}/{timestamp}.ogg
            drive_file_name = f"{speaker_id}/{sentence['sentence_id']}.ogg"
            
            drive_success, drive_result = await _upload_to_drive(permanent_path, drive_file_name)
            if drive_success:
                audio_path = drive_result
                logger.info("📍 Storing Google Drive URL: %s", audio_path)
                # Delete local file after successful Drive upload
                await _delete_local(permanent_path)
            else:
                # Fall back to R2 if Drive upload fails
                logger.info("⚠️ Google Drive upload failed, trying R2...")
                r2_success = await _upload_to_r2(permanent_path, relative_path)
                if r2_success:
                    audio_path = relative_path
                    logger.info("📍 Storing R2 path: %s", audio_path)
                    await _delete_local(permanent_path)
                else:
                    logger.info("📍 Storing local path (all uploads failed): %s", audio_path)
        else:
            # R2 upload as fallback (legacy behavior)
            logger.info("Google Drive disabled, using R2/local storage")
            r2_success = await _upload_to_r2(permanent_path, relative_path)
            if r2_success:
                audio_path = relative_path
                logger.info("📍 Storing R2 path: %s", audio_path)
                await _delete_local(permanent_path)
            else:
                logger.info("📍 Storing local path: %s", audio_path)
        
        logger.info("💾 Saving recording with audio_path: %s", audio_path)
        await db.save_recording(
            telegram_id=telegram_id,
            speaker_id=speaker_id,
            sentence_id=sentence["id"],
            audio_path=audio_path,
        )
        await db.mark_sentence_completed(speaker_id, sentence["id"])
    except Exception:
        logger.exception("Failed to finalize submission for speaker=%s", speaker_id)
        await query.edit_message_text(
            "⚠️ A system error occurred while saving your recording. Please "
            "press Submit again."
        )
        return STATE_REVIEW

    context.user_data.pop(UD_TEMP_AUDIO_PATH, None)
    await query.edit_message_text("✅ Recording submitted. Thank you!")

    next_state = await assign_and_send_sentence(update, context)
    return next_state if next_state is not None else ConversationHandler.END
