# Deploying to Render

## Architecture

```
Render Web Service (Docker)  ──►  Frontend + API  ──►  Render PostgreSQL
Render Background Worker      ──►  Telegram Bot     ──┘
```

## Step 1 — Prepare Your Code

Ensure you have:
- ✅ `render.yaml` configured (already in repo)
- ✅ `Dockerfile` ready (already in repo)
- ✅ `twi_bot/requirements.txt` with all dependencies
- ✅ `twi_bot/schema.sql` for database initialization

## Step 2 — Push Your Code to GitHub

```bash
cd C:\Users\Felix\Downloads\twi_bot

git add .
git commit -m "Deploy to Render with PostgreSQL and Google Drive"
git push origin main
```

## Step 3 — Deploy on Render

1. Go to [render.com](https://render.com) and sign up / log in
2. Click **"New"** → **"Blueprint"**
3. Connect your GitHub repository
4. Render will auto-detect `render.yaml` and show:
   - ✅ `twi-db` (PostgreSQL database) - **FREE**
   - ✅ `twi-api` (Web Service) - **FREE**
   - ✅ `twi-bot` (Background Worker) - **FREE**
5. Click **"Apply"** to deploy

## Step 4 — Set Required Environment Variables

After Render provisions the services, you'll need to set these on both `twi-api` and `twi-bot`:

### 1. Telegram Bot Token
- Key: `TELEGRAM_BOT_TOKEN`
- Value: Your bot token (from BotFather)

### 2. Google Drive (Optional)

If you want to use Google Drive storage:

- Key: `GOOGLE_DRIVE_ENABLED`
- Value: `true`

- Key: `GOOGLE_DRIVE_CREDENTIALS_PATH`
- Value: Path to credentials.json (e.g., `credentials.json`)

- Key: `GOOGLE_DRIVE_FOLDER_ID`
- Value: Your Google Drive folder ID (if uploading to a specific folder)

**Note:** You'll need to upload `credentials.json` or set up OAuth2 separately.

## Step 5 — Database Initialization

Render will automatically:
1. Create the PostgreSQL database
2. Run `twi_bot/schema.sql` on startup
3. Run `twi_bot/migration_add_name.sql` on startup

Your database is ready to use!

## Step 6 — Monitor Deployment

1. Go to your Render dashboard
2. Check each service status (should say "Live" in green)
3. View logs by clicking each service
4. Click the web service URL to access your dashboard

## Accessing Your App

- **Dashboard (Web UI)**: `https://twi-api-xxxxx.onrender.com`
- **API Health**: `https://twi-api-xxxxx.onrender.com/health`
- **Telegram Bot**: Automatically polling for updates

## Environment Variables Summary

| Service | Variable | Example | Required |
|---------|----------|---------|----------|
| Both | `DATABASE_URL` | Auto-set by Render | ✅ |
| Both | `TELEGRAM_BOT_TOKEN` | `8515823034:AAF...` | ✅ |
| Both | `AUDIO_DIR` | `/app/audio` | ✅ (auto) |
| Both | `TEMP_AUDIO_DIR` | `/app/temp_audio` | ✅ (auto) |
| Both | `GOOGLE_DRIVE_ENABLED` | `true`/`false` | ❌ |
| Both | `GOOGLE_DRIVE_CREDENTIALS_PATH` | `credentials.json` | ❌ |
| Both | `GOOGLE_DRIVE_FOLDER_ID` | `1ABC...` | ❌ |

## Free Tier Limits

- **PostgreSQL**: 256 MB storage (more than enough for metadata)
- **Web Service**: 0.5 CPU, 512 MB RAM
- **Worker**: 0.5 CPU, 512 MB RAM
- **Bandwidth**: 100 GB/month

Audio files are stored in Google Drive (free storage), not on Render, so you won't run out of space!

## Troubleshooting

### Services won't start
- Check logs: Click service → **Logs**
- Verify `TELEGRAM_BOT_TOKEN` is set
- Ensure database is healthy

### Database connection errors
- Wait 1-2 minutes for database to fully provision
- Verify `DATABASE_URL` is set correctly (auto-set by Render)

### Bot not responding
- Check if `TELEGRAM_BOT_TOKEN` is correct
- View bot worker logs for errors

### Google Drive uploads failing
- Ensure `GOOGLE_DRIVE_ENABLED=true`
- Verify `GOOGLE_DRIVE_CREDENTIALS_PATH` points to correct file
- Add test user to OAuth consent screen if using OAuth2

## Step 5 — Handle Google Drive Credentials

Since you're using Google Drive OAuth2, you need to get `credentials.json` to Render:

### Option A: Commit credentials.json to GitHub (⚠️ Not recommended for production)
```bash
# Only if you're okay with client ID being public
git add twi_bot/credentials.json
git commit -m "Add Google Drive credentials"
git push
```

Then set in Render environment:
```
GOOGLE_DRIVE_CREDENTIALS_PATH=/app/twi_bot/credentials.json
```

### Option B: Use Render File Mount (Recommended)
1. In Render dashboard, go to `twi-api` service → **Files** tab
2. Upload `credentials.json` to `/app/twi_bot/credentials.json`
3. Do the same for `twi-bot` service
4. Set environment variable:
   ```
   GOOGLE_DRIVE_CREDENTIALS_PATH=/app/twi_bot/credentials.json
   ```

### Option C: Encode credentials as environment variable
If you want zero files committed, base64 encode credentials.json and decode at runtime:
```bash
# On your local machine
[System.Convert]::ToBase64String([System.IO.File]::ReadAllBytes("C:\Users\Felix\Downloads\twi_bot\twi_bot\credentials.json"))
```
Then set `GOOGLE_DRIVE_CREDENTIALS_B64` in Render and modify config.py to decode it.

## Step 6 — Database Auto-Initialization

Render will automatically:
- Create the PostgreSQL database from `render.yaml`
- Run `schema.sql` on first deploy
- Your tables are ready instantly

No manual database setup needed!

For Railway, use the MySQL connection string from their dashboard:
```bash
mysql -h your-host.railway.app -P 3306 -u root -p twi_speech_db < twi_bot/schema.sql
```

## Step 6 — Verify deployment

1. **API health**: Visit `https://twi-api.onrender.com/health` — should return `{"status":"ok"}`
2. **Dashboard**: Visit `https://twi-api.onrender.com` — should show the admin dashboard
3. **API docs**: Visit `https://twi-api.onrender.com/docs`
4. **Bot logs**: Render dashboard → `twi-bot` service → Logs — should show "Twi speech data collection bot is up and polling"

## Step 7 — (Optional) Custom domain

In Render dashboard → `twi-api` → **Settings** → **Custom Domains**:
- Add your domain (e.g. `dashboard.yourdomain.com`)
- Update DNS CNAME to point to `twi-api.onrender.com`
- Render auto-provisions SSL

## Important notes for Render

- **Free tier sleeping**: Render free web services sleep after 15 minutes of inactivity. The first request takes ~30 seconds to wake up. Upgrade to paid ($7/mo) to keep always-on.
- **Free tier workers**: Background workers on the free plan may have similar cold-start behavior.
- **MySQL on Render**: Render doesn't offer managed MySQL. PlanetScale or Railway MySQL are the recommended options.
- **Port**: Render sets the `PORT` env var automatically. The Dockerfile uses `${PORT:-8000}` to handle this.
- **File storage**: Audio files stored in the container filesystem are ephemeral. For production, use an S3-compatible service (Cloudflare R2, Backblaze B2) instead of local disk storage.

## Updating your deployment

After pushing new code to GitHub:
```bash
# Render auto-deploys on push (if Auto-Deploy is enabled in settings)
# Or manually trigger from the Render dashboard
```
