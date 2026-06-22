# Google Drive Integration - Complete Example

## Quick Start

### 1. Install Dependencies

```bash
cd twi_bot
pip install -r requirements.txt
```

### 2. Set Up Google Drive

Follow [GOOGLE_DRIVE_SETUP.md](GOOGLE_DRIVE_SETUP.md) to:
- Create Google Cloud Project
- Set up service account
- Download JSON credentials
- (Optional) Create dedicated Google Drive folder

### 3. Configure Environment

Update `.env`:

```env
GOOGLE_DRIVE_ENABLED=true
GOOGLE_DRIVE_CREDENTIALS_PATH=/path/to/service-account-key.json
GOOGLE_DRIVE_FOLDER_ID=  # Optional
```

### 4. Run Bot

```bash
python main.py
```

---

## How It Works

### Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ User: /start → enters Speaker ID → gives consent            │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ Bot assigns sentence and asks user to record               │
│ "Please read: 'Akwaaba a medua pa wo'"                      │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ User records voice message → Telegram sends to bot           │
│ Bot downloads: temp_audio/{telegram_id}.ogg                 │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ Bot shows: "✔ Submit | 🔁 Redo | 🗑 Delete"                │
│ Buttons: CB_SUBMIT, CB_REDO, CB_DELETE                      │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
        User clicks "✔ Submit" (CB_SUBMIT)
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ Bot moves file:                                             │
│ temp_audio/123456789.ogg → audio/SPKE43YB/sent_001.ogg     │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ if GOOGLE_DRIVE_ENABLED:                                    │
│   upload_to_drive("audio/SPKE43YB/sent_001.ogg",           │
│                   "SPKE43YB/sent_001.ogg")                  │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
            ┌──────────────────┐
            │ Google Drive API │
            └────────┬─────────┘
                     ▼
         ┌───────────────────────────┐
         │ File uploaded              │
         │ File ID: abc123...         │
         │ Made public                │
         └─────────────┬─────────────┘
                       ▼
         ┌────────────────────────────────┐
         │ Return shareable URL:          │
         │ https://drive.google.com/...   │
         └────────────┬───────────────────┘
                      ▼
         ┌────────────────────────────────┐
         │ Delete local file              │
         │ rm audio/SPKE43YB/sent_001.ogg │
         └────────────┬───────────────────┘
                      ▼
         ┌────────────────────────────────────┐
         │ Save to PostgreSQL:                │
         │ INSERT INTO recordings             │
         │   telegram_id: 123456789           │
         │   speaker_id: SPKE43YB             │
         │   sentence_id: sent_001            │
         │   audio_path: https://drive...     │
         └────────────┬───────────────────────┘
                      ▼
         ┌────────────────────────────────────┐
         │ Mark sentence as completed         │
         │ UPDATE sentences_completed         │
         └────────────┬───────────────────────┘
                      ▼
         ┌────────────────────────────────────┐
         │ Send next sentence                 │
         │ "✅ Recording submitted. Thank you!│
         │  Next: Akoo wo din yi..."          │
         └────────────────────────────────────┘
```

---

## Code Examples

### Recording Storage in Database

```python
# In PostgreSQL (recordings table)
id    | telegram_id | speaker_id  | sentence_id | audio_path
------|-------------|-------------|-------------|----------------------------------------------
1     | 123456789   | SPKE43YBPSR | 1           | https://drive.google.com/uc?id=1abc...xyz
2     | 123456789   | SPKE43YBPSR | 2           | https://drive.google.com/uc?id=1def...456
3     | 987654321   | SPK1001     | 1           | https://drive.google.com/uc?id=1ghi...789
```

### API Response (Dashboard)

```python
# GET /api/recordings
{
  "recordings": [
    {
      "id": 1,
      "speaker_id": "SPKE43YBPSR",
      "sentence_id": "sent_001",
      "sentence_text": "Akwaaba a medua pa wo",
      "created_at": "2024-01-15T10:30:00Z",
      "audio_url": "https://drive.google.com/uc?id=1abc...xyz"
    },
    {
      "id": 2,
      "speaker_id": "SPKE43YBPSR", 
      "sentence_id": "sent_002",
      "sentence_text": "Akoo wo din yi?",
      "created_at": "2024-01-15T10:35:00Z",
      "audio_url": "https://drive.google.com/uc?id=1def...456"
    }
  ]
}
```

---

## Configuration Examples

### Minimal Setup (Local Folder Upload)

```env
GOOGLE_DRIVE_ENABLED=true
GOOGLE_DRIVE_CREDENTIALS_PATH=/home/user/twi-bot-sa-key.json
# Files upload to service account's root folder
```

### Organized Setup (Dedicated Folder)

```env
GOOGLE_DRIVE_ENABLED=true
GOOGLE_DRIVE_CREDENTIALS_PATH=/home/user/twi-bot-sa-key.json
GOOGLE_DRIVE_FOLDER_ID=1gX9sK2mP8lQ3vN5rH7wJ9eB6tF4dL0aM
# Files upload to specific folder automatically organized by speaker
```

### Fallback Chain Setup

```env
# Primary: Google Drive
GOOGLE_DRIVE_ENABLED=true
GOOGLE_DRIVE_CREDENTIALS_PATH=/path/to/credentials.json

# Fallback: Cloudflare R2
R2_ENABLED=true
R2_ENDPOINT=https://account.r2.cloudflarestorage.com
R2_ACCESS_KEY_ID=your_key_id
R2_SECRET_ACCESS_KEY=your_secret_key
R2_BUCKET_NAME=twi-audio
```

**Fallback Priority:**
1. Google Drive (if enabled and succeeds)
2. R2 (if Google fails and R2 enabled)
3. Local Storage (if both fail)

---

## Error Scenarios

### Scenario 1: Credentials Not Found

**What happens:**
```
[ERROR] Google Drive credentials not configured.
[WARNING] Failed to upload to Google Drive
[INFO] Uploaded to R2: SPKE43YB/sent_001.ogg
```

**Stored in database:**
```
audio_path: "SPKE43YB/sent_001.ogg"  # R2 path, not Google Drive URL
```

**User sees:**
```
✅ Recording submitted. Thank you!
```

**No user impact** - falls back to R2 automatically.

### Scenario 2: Google Drive Quota Exceeded

**What happens:**
```
[ERROR] google.auth.exceptions.TransportError
[WARNING] Failed to upload to Google Drive
[INFO] Uploaded to R2: SPKE43YB/sent_001.ogg
```

**Stored in database:**
```
audio_path: "SPKE43YB/sent_001.ogg"  # Falls back to R2
```

**Recovery:**
1. Check Google Drive quota
2. Free up space
3. Future uploads work normally
4. No data loss

### Scenario 3: All Storage Disabled

**Configuration:**
```env
GOOGLE_DRIVE_ENABLED=false
R2_ENABLED=false
```

**What happens:**
```
[INFO] Google Drive disabled, skipping upload
[INFO] R2 disabled, skipping upload
```

**Stored in database:**
```
audio_path: "/home/user/twi_bot/audio/SPKE43YB/sent_001.ogg"  # Local path
```

**Files remain** in local `audio/` directory.

---

## Monitoring

### Logs to Watch

```bash
# View bot logs
tail -f /var/log/twi_bot.log

# Successful upload
[INFO] Uploaded to Google Drive: SPKE43YB/sent_001.ogg
[INFO] Made file publicly accessible: 1abc...xyz

# Failed upload with fallback
[ERROR] Google Drive API error: ...
[WARNING] Failed to upload SPKE43YB/sent_001.ogg to Google Drive
[INFO] Uploaded to R2: SPKE43YB/sent_001.ogg
```

### Database Queries

```sql
-- Check how many files stored where
SELECT 
  CASE
    WHEN audio_path LIKE 'https://drive.google.com%' THEN 'Google Drive'
    WHEN audio_path LIKE '%/%' AND NOT LIKE 'https://%' THEN 'R2'
    ELSE 'Local'
  END AS storage_type,
  COUNT(*) as count
FROM recordings
GROUP BY storage_type;
```

---

## Performance Notes

### Upload Speed

- **Google Drive**: Depends on internet speed
  - 1 minute audio: ~1-3 seconds
  - Network latency: ~500-1000ms
  
- **No blocking**: Upload runs in background thread
  - Bot remains responsive to other users
  - Multiple uploads can happen in parallel

### Disk Usage

- **Before**: Audio files accumulated in `audio/` directory
- **After**: Files deleted after successful cloud upload
  - Disk usage stays minimal
  - No cleanup needed

---

## Troubleshooting Checklist

- [ ] Google Cloud Project created
- [ ] Service account created
- [ ] Google Drive API enabled
- [ ] JSON key downloaded
- [ ] `.env` configured with correct path
- [ ] Credentials file is readable
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Bot starts without errors
- [ ] Test recording uploads successfully
- [ ] File appears in Google Drive
- [ ] URL is stored in database
- [ ] URL is accessible in browser

---

## Next Steps

1. **Follow [GOOGLE_DRIVE_SETUP.md](GOOGLE_DRIVE_SETUP.md)** for detailed setup
2. **Test locally** before deploying
3. **Monitor logs** during first week
4. **Check database** to verify URLs are stored correctly
5. **Share URLs** with team to verify accessibility
