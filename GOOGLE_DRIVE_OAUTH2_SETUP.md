# Google Drive OAuth2 Setup (Fix for Storage Quota Error)

If you're seeing this error:
```
Service Accounts do not have storage quota
```

**Solution:** Use OAuth2 authentication (your personal Google account) instead of service account.

## Step-by-Step Setup

### 1. Delete Old Credentials
```bash
# Remove the old service account JSON file from your project
rm twi_bot/original-bot-500323-r8-49b900108289.json
```

### 2. Create OAuth2 Credentials in Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Go to **APIs & Services** → **Credentials**
4. Click **+ CREATE CREDENTIALS** → **OAuth client ID**
5. Choose **Desktop app** (or **Other** if Desktop isn't available)
6. Click **CREATE**
7. Click the download icon next to your new credential
8. Save as `credentials.json` in your project folder:
   ```
   twi_bot/credentials.json
   ```

### 3. Update `.env`

```env
GOOGLE_DRIVE_ENABLED=true
GOOGLE_DRIVE_CREDENTIALS_PATH=credentials.json
GOOGLE_DRIVE_FOLDER_ID=1r8zVYRHBLa3mtCH5gBVqPBdQRT8C4UYL
```

### 4. First Run - Browser Authentication

When you start the bot:
```bash
python main.py
```

**You will see:**
```
🔐 Starting OAuth2 authentication flow...
⚠️ A browser window will open - please authorize the application
```

1. A browser window will open
2. Click **Allow** to authorize the app to access your Google Drive
3. Close the browser window
4. Bot will save `token.json` for future runs
5. Subsequent runs will use the cached token automatically

### 5. All Done! ✅

Now when you submit recordings:
- Bot will upload to your Google Drive
- Files will appear in your folder
- Shareable URLs will be stored in the database

## How It Works

- **First time:** Opens browser → you authenticate → bot saves token
- **Subsequent times:** Bot uses cached token automatically
- **Token refreshes:** Automatically refreshes if expired
- **Your account:** Uses YOUR personal Google account, not a service account

## Troubleshooting

### Browser doesn't open
```python
# The browser should open automatically
# If not, you'll see a URL in the console - copy/paste it manually
```

### "credentials.json not found"
- Make sure you downloaded the OAuth2 credentials (not service account!)
- Place it in the project root as `credentials.json`
- Verify path: `twi_bot/credentials.json`

### Permission denied errors
- Ensure the Google Drive folder is shared with your account
- If using a different Google account, give it Editor access

### Token expired
- Token refreshes automatically
- If you see auth errors, delete `token.json` and restart bot
- You'll be prompted to re-authorize

## Files Created
- `token.json` - Cached authentication token (auto-generated)
- `credentials.json` - OAuth2 credentials (you download this)

**Important:** Add both to `.gitignore`:
```
token.json
credentials.json
```
