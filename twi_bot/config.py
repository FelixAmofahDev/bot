"""
Centralized configuration loaded from environment variables (.env).
"""
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.getenv("AUDIO_DIR", os.path.join(BASE_DIR, "audio"))
TEMP_AUDIO_DIR = os.getenv("TEMP_AUDIO_DIR", os.path.join(BASE_DIR, "temp_audio"))

os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(TEMP_AUDIO_DIR, exist_ok=True)

# Google Drive configuration
GOOGLE_DRIVE_ENABLED = os.getenv("GOOGLE_DRIVE_ENABLED", "false").lower() == "true"
GOOGLE_DRIVE_CREDENTIALS_PATH = os.getenv("GOOGLE_DRIVE_CREDENTIALS_PATH")
GOOGLE_DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")  # Optional: specific folder to upload to

# Cloudflare R2 configuration (legacy, still supported)
R2_ENABLED = os.getenv("R2_ENABLED", "false").lower() == "true"

if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

if GOOGLE_DRIVE_ENABLED and not GOOGLE_DRIVE_CREDENTIALS_PATH and not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
    raise RuntimeError("Google Drive enabled but credentials path not set")