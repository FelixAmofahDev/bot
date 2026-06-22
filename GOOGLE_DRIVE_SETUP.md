# Google Drive Integration Setup

This document explains how to set up Google Drive storage for audio file uploads in the Twi bot project.

## Overview

The bot now supports uploading audio recordings directly to Google Drive using service account authentication. This provides:
- Cloud storage for audio files
- Automatic shareable URLs
- Centralized data storage
- No local disk usage after upload

## Prerequisites

1. A Google Cloud Project
2. Service account credentials (JSON key file)
3. Google Drive API enabled

## Step-by-Step Setup

### 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click the project dropdown at the top
3. Click "NEW PROJECT"
4. Enter a name (e.g., "Twi Speech Bot")
5. Click "CREATE"
6. Wait for the project to be created, then select it

### 2. Enable Google Drive API

1. In the Cloud Console, go to **APIs & Services** → **Library**
2. Search for "Google Drive API"
3. Click on it and press **ENABLE**
4. Wait for the API to be enabled

### 3. Create a Service Account

1. Go to **APIs & Services** → **Credentials**
2. Click **+ CREATE CREDENTIALS** → **Service Account**
3. Fill in the details:
   - **Service account name**: `twi-bot-sa` (or similar)
   - **Service account ID**: Auto-filled
   - Click **CREATE AND CONTINUE**
4. On the next page, click **CONTINUE** (skip optional steps)
5. Click **DONE**

### 4. Create and Download JSON Key

1. In **Credentials**, find your service account in the "Service Accounts" section
2. Click on the service account email
3. Go to the **KEYS** tab
4. Click **ADD KEY** → **Create new key**
5. Choose **JSON** and click **CREATE**
6. A JSON file will download automatically
7. **Save this file securely** - you'll need it for the bot

### 5. Create a Google Drive Folder (Optional)

If you want to upload files to a specific folder:

1. Go to [Google Drive](https://drive.google.com/)
2. Create a new folder (right-click → "New folder")
3. Name it `twi-audio` or similar
4. Right-click the folder → "Share"
5. Copy the service account email and give it **Editor** access
6. From the folder's URL, copy the folder ID:
   ```
   https://drive.google.com/drive/folders/1ABC123XYZ456...
   Folder ID: 1ABC123XYZ456...
   ```

### 6. Configure the Bot

1. Copy the downloaded JSON key file to a secure location:
   ```bash
   cp ~/Downloads/your-service-account-key.json /path/to/project/credentials/google-drive-key.json
   ```

2. Update `.env` file:
   ```env
   GOOGLE_DRIVE_ENABLED=true
   GOOGLE_DRIVE_CREDENTIALS_PATH=/path/to/project/credentials/google-drive-key.json
   GOOGLE_DRIVE_FOLDER_ID=1ABC123XYZ456  # Optional: your folder ID
   ```

3. Install dependencies (if not already done):
   ```bash
   pip install -r requirements.txt
   ```

## File Naming Convention

Audio files are uploaded to Google Drive with the following naming structure:

```
{speaker_id}/{sentence_id}.ogg
```

**Example:**
```
SPKE43YBPSR/sent_001.ogg
SPKE43YBPSR/sent_002.ogg
```

## How It Works

### Upload Flow

1. User records audio via Telegram
2. File is temporarily saved to `temp_audio/`
3. User submits the recording
4. Bot uploads file to Google Drive
5. Google Drive returns a shareable URL
6. URL is stored in PostgreSQL (`recordings.audio_path`)
7. Local temporary file is deleted

### URL Format

Shareable URLs are generated in this format:

```
https://drive.google.com/uc?id={FILE_ID}&export=download
```

These URLs can be:
- Shared with researchers
- Used to download files programmatically
- Accessed from the admin dashboard

## Error Handling

If Google Drive upload fails:
1. Bot logs the error
2. Falls back to Cloudflare R2 (if enabled)
3. Falls back to local storage (if R2 also disabled)
4. User is notified to retry

The bot will **not crash** - it gracefully degrades to available storage options.

## Security Considerations

### Service Account Security

- **Never commit** the JSON key file to Git
- Add `credentials/` to `.gitignore`
- Restrict file permissions: `chmod 600 google-drive-key.json`
- Use environment variables in production

### Google Drive Sharing

By default, uploaded files are made "publicly accessible" (anyone with the link can view/download).

To restrict access:
1. Remove the `anyone` permission in `drive_storage.py`
2. Or manually manage permissions in Google Drive web interface

### Sensitive Data

Since files are shared via URLs, ensure you:
- Only collect consented audio data
- Anonymize or pseudonymize speaker information
- Implement appropriate data retention policies

## Troubleshooting

### "Credentials file not found"

- Verify the path in `GOOGLE_DRIVE_CREDENTIALS_PATH`
- Ensure the file exists and is readable
- Check file permissions: `chmod 600 google-drive-key.json`

### "Failed to authenticate"

- Verify the JSON key file is valid
- Check that the service account has Google Drive API access
- Ensure the API is enabled in Cloud Console

### "Permission denied"

- Check that the service account has Editor access to the target folder
- Verify you're using the correct folder ID
- Try uploading to the root folder (remove `GOOGLE_DRIVE_FOLDER_ID`)

### Uploads are slow

- This is expected for large files or slow connections
- The bot uses async upload in a thread pool - it won't block other users
- Consider increasing timeout values if needed

## Testing

To test the setup locally:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set environment variables
export GOOGLE_DRIVE_ENABLED=true
export GOOGLE_DRIVE_CREDENTIALS_PATH=/path/to/key.json

# 3. Run the bot
python main.py
```

## Disabling Google Drive

To revert to local storage or R2 only:

```env
GOOGLE_DRIVE_ENABLED=false
```

The bot will automatically fall back to other configured storage options.

## Additional Resources

- [Google Cloud Console](https://console.cloud.google.com/)
- [Google Drive API Documentation](https://developers.google.com/drive/api)
- [Service Account Setup Guide](https://cloud.google.com/docs/authentication/getting-started)
