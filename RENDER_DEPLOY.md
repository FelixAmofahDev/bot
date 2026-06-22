# Deploying to Render

## Architecture

```
Render Web Service (Docker)  ──►  Frontend + API  ──►  PlanetScale MySQL
Render Background Worker      ──►  Telegram Bot     ──┘
```

## Step 1 — Set up PlanetScale (free MySQL database)

1. Go to [planetscale.com](https://planetscale.com) and sign up
2. Click **"Create a new database"**
   - Name: `twi_speech_db`
   - Region: choose the one closest to you (e.g. `AWS us-east-1`)
   - Plan: **Scaler** (free, 5 GB)
3. After creation, click **"Connect"** → **"Connect with Docker"** or **"General"** to get:
   - **Host** (e.g. `aws.connect.psdb.cloud`)
   - **Username** (e.g. `root`)
   - **Password**
4. **Important**: On PlanetScale, you need to enable the "branch" and get a connection string. The easiest way is to use their CLI or dashboard to get the connection details.

Alternatively, use **Railway MySQL** (also free tier):
1. Go to [railway.app](https://railway.app)
2. New → Database → MySQL
3. Copy the `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE` from the Variables tab

## Step 2 — Push your code to GitHub

```bash
cd C:\Users\Felix\Downloads\twi_bot

git init
git add .
git commit -m "Initial commit for Render deployment"
git remote add origin https://github.com/your-username/twi_bot.git
git push -u origin main
```

## Step 3 — Deploy on Render

1. Go to [render.com](https://render.com) and sign up / log in
2. Click **"New"** → **"Blueprint"**
3. Connect your GitHub repo
4. Render will auto-detect `render.yaml` and show the services:
   - `twi-api` (Web Service)
   - `twi-bot` (Background Worker)
5. Click **"Apply"**

## Step 4 — Set environment variables

After the blueprint deploys, you'll need to fill in the **sync: false** variables:

### For `twi-api`:
Go to the `twi-api` service → **Environment** tab, set:
| Key | Value |
|-----|-------|
| `TELEGRAM_BOT_TOKEN` | Your bot token from @BotFather |
| `DB_HOST` | Your PlanetScale/Railway host |
| `DB_USER` | Your DB user |
| `DB_PASSWORD` | Your DB password |
| `DB_NAME` | `twi_speech_db` |

### For `twi-bot`:
Same variables as above.

## Step 5 — Initialize the database schema

If your DB is empty, you need to run the schema. Use PlanetScale's CLI or connect via MySQL client:

```bash
# Using PlanetScale CLI
pscale connect twi_speech_db main --port 3309

# Then in another terminal:
mysql -h 127.0.0.1 -P 3309 -u root -p twi_speech_db < twi_bot/schema.sql
mysql -h 127.0.0.1 -P 3309 -u root -p twi_speech_db < twi_bot/migration_add_name.sql
```

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
