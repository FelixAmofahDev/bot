# Google Drive Integration - Implementation Summary

## Files Created/Modified

### 1. **NEW: `twi_bot/drive_storage.py`**
Complete Google Drive upload module with:
- Service account authentication
- Async file upload using `asyncio.to_thread`
- Shareable URL generation
- Comprehensive error handling
- Full docstrings

**Key Functions:**
- `upload_file_to_drive(file_path, file_name, folder_id) -> str`
  - Async wrapper
  - Returns shareable Google Drive URL
  - Thread-safe for use in async bot

### 2. **MODIFIED: `twi_bot/config.py`**
Added configuration:
```python
GOOGLE_DRIVE_ENABLED = os.getenv("GOOGLE_DRIVE_ENABLED", "false").lower() == "true"
GOOGLE_DRIVE_CREDENTIALS_PATH = os.getenv("GOOGLE_DRIVE_CREDENTIALS_PATH")
GOOGLE_DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
```

With validation:
- Checks credentials exist if Google Drive is enabled
- Runtime error if config is invalid

### 3. **MODIFIED: `twi_bot/handlers/callbacks.py`**
Updated submission flow:

**New Function:**
- `_upload_to_drive(local_path, file_name) -> tuple[bool, str]`
  - Returns (success, url_or_path)
  - Graceful fallback on error

**Modified `review_callback()` function:**
- Tries Google Drive upload first (if enabled)
- Falls back to R2 if Drive upload fails
- Falls back to local storage if both fail
- Deletes local file after successful cloud upload
- Stores URL or path in database

### 4. **MODIFIED: `requirements.txt`**
Added Google Drive dependencies:
```
google-auth==2.25.2
google-auth-oauthlib==1.2.0
google-api-python-client==2.107.0
```

### 5. **NEW: `.env.example`**
Reference .env file with all configuration options:
- Google Drive settings
- Credentials path
- Folder ID (optional)
- Legacy R2 settings

### 6. **NEW: `GOOGLE_DRIVE_SETUP.md`**
Complete setup guide covering:
- Google Cloud project creation
- Service account setup
- JSON key download
- Optional folder creation
- Environment configuration
- Security best practices
- Troubleshooting

## Database Impact

**Zero Schema Changes**: The `audio_path` column stores either:
- Google Drive shareable URL: `https://drive.google.com/uc?id=...`
- R2 key: `speaker_id/sentence_id.ogg`
- Local path: `/absolute/path/to/file.ogg`

All formats work with existing schema.

## Data Flow

```
User records audio (Telegram)
           ↓
Download to temp_audio/{telegram_id}.ogg
           ↓
User submits
           ↓
Move to audio/{speaker_id}/{sentence_id}.ogg
           ↓
┌──────────────────────────────┐
│ Try Google Drive Upload       │
├──────────────────────────────┤
│ ✓ Success → Save URL          │ Delete local file
│ ✗ Fail → Try R2              │ (if R2 enabled)
│ ✗ Fail → Use Local Path      │
└──────────────────────────────┘
           ↓
Save to PostgreSQL (recordings.audio_path)
```

## Configuration Priority

1. **Google Drive** (if enabled)
2. **Cloudflare R2** (if enabled)
3. **Local Storage** (fallback)

## Error Handling

- All API calls wrapped in try/except
- Failures logged with full context
- Bot continues operating
- User gets appropriate feedback
- No data loss (always stores something)

## Async Compatibility

- `upload_file_to_drive()` is fully async
- Blocking Google API calls run via `asyncio.run_in_executor()`
- Non-blocking for Telegram bot
- Service account auth is cached

## Testing Checklist

After setup:
- [ ] Google Cloud project created
- [ ] Service account created
- [ ] JSON key downloaded
- [ ] `.env` configured
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Bot starts: `python main.py`
- [ ] User can record and submit
- [ ] File appears in Google Drive
- [ ] URL stored in database
- [ ] URL is accessible via browser

## Fallback Scenarios

| Scenario | Behavior |
|----------|----------|
| Google Drive enabled, succeeds | Store Drive URL |
| Google Drive fails, R2 enabled | Store R2 path |
| Both fail | Store local path |
| Google Drive disabled | Skip to R2/local |

## Notes

- Files are uploaded with naming: `{speaker_id}/{sentence_id}.ogg`
- Files are made publicly accessible (anyone with URL can view)
- Service account credentials should never be committed to Git
- Support for multiple storage backends ensures reliability
