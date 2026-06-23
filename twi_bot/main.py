"""
Entry point. Wires all handlers into a single ConversationHandler that
drives the full STEP 1 → STEP 7 flow, and manages the PostgreSQL pool
lifecycle around the bot's polling loop.
"""
import logging

import asyncpg
from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from telegram.request import HTTPXRequest

import config
import db
from constants import (
    STATE_CONFIRM_ID,
    STATE_CONSENT,
    STATE_RECORDING,
    STATE_REVIEW,
    STATE_SPEAKER_ID,
)
from handlers.auth import receive_speaker_id, start
from handlers.callbacks import confirm_id_callback, consent_callback, review_callback
from handlers.recording import receive_voice, remind_voice_only

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
# Quiet down noisy third-party loggers.
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text("Session ended. Send /start to begin again.")
    return ConversationHandler.END


async def post_init(application: Application) -> None:
    await db.init_pool()
    logger.info("Twi speech data collection bot is up and polling.")


async def post_shutdown(application: Application) -> None:
    await db.close_pool()


def build_application() -> Application:
    request = HTTPXRequest(
        connect_timeout=20.0,
        read_timeout=30.0,
        write_timeout=30.0,
        pool_timeout=20.0,
    )

    application = (
        ApplicationBuilder()
        .token(config.TELEGRAM_BOT_TOKEN)
        .request(request)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            STATE_SPEAKER_ID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_speaker_id),
            ],
            STATE_CONFIRM_ID: [
                CallbackQueryHandler(confirm_id_callback),
            ],
            STATE_CONSENT: [
                CallbackQueryHandler(consent_callback),
            ],
            STATE_RECORDING: [
                MessageHandler(filters.VOICE, receive_voice),
                MessageHandler(filters.TEXT & ~filters.COMMAND, remind_voice_only),
            ],
            STATE_REVIEW: [
                CallbackQueryHandler(review_callback),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        name="twi_speech_conversation",
        persistent=False,
    )

    application.add_handler(conv_handler)
    return application


def main() -> None:
    application = build_application()
    try:
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except (OSError, asyncpg.PostgresError) as exc:
        logger.error(
            "Unable to connect to PostgreSQL at %s:%s/%s. Start the database or update DB_HOST/DB_PORT/DB_NAME in .env, then run main.py again.",
            config.DB_HOST,
            config.DB_PORT,
            config.DB_NAME,
        )
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
