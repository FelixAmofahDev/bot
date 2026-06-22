# Admin Dashboard - Quick Start Guide

## System Overview

The admin dashboard consists of three components running independently:

1. **FastAPI Backend API** (Port 8000) - Provides REST endpoints for data management
2. **React Frontend** (Port 5173) - Professional web interface for researchers
3. **MySQL Database** - Stores participants, recordings, and metadata
4. **Telegram Bot** (Optional) - Collects voice recordings from participants

## Getting Started (5 minutes)

### Step 1: Prerequisites
- ✅ Python 3.8+ installed
- ✅ Node.js 18+ installed
- ✅ MySQL 5.7+ installed and running
- ✅ Database initialized with schema

### Step 2: Initialize Database

```bash
# Create database and tables
mysql -u root -p < twi_bot/schema.sql

# Insert sample data (optional)
mysql -u root -p twi_speech_db << EOF
INSERT INTO sentences (sentence_id, text) VALUES
  ('SENT0001', 'Mede me ho akyi'),
  ('SENT0002', 'Wo ho te sɛn?'),
  ('SENT0003', 'Me din de Kofi');
EOF
```

### Step 3: Configure Environment

```bash
cd twi_bot

# Copy example config
cp .env.example .env

# Edit .env with your database credentials
# DB_HOST=127.0.0.1
# DB_PORT=3306
# DB_USER=root
# DB_PASSWORD=your_password
# DB_NAME=twi_speech_db
```

### Step 4: Install Dependencies

```bash
# Backend
pip install -r twi_bot/requirements.txt

# Frontend
cd frontend && npm install
```

### Step 5: Start Services

Open three terminal windows and run:

**Terminal 1 - FastAPI Backend:**
```bash
cd twi_bot
python -m uvicorn api.app:app --reload --host 0.0.0.0 --port 8000
# Output: Uvicorn running on http://0.0.0.0:8000
```

**Terminal 2 - React Frontend:**
```bash
cd frontend
npm run dev
# Output: VITE v... ready in ... ms
#         ➜  Local: http://localhost:5173/
```

**Terminal 3 - Telegram Bot (Optional):**
```bash
cd twi_bot
python main.py
# Output: Twi speech data collection bot is up and polling.
```

## Accessing the Dashboard

1. Open your browser and navigate to: **http://localhost:5173**
2. You should see the professional admin dashboard with:
   - Clean sidebar navigation
   - Dashboard statistics overview
   - Participant management interface
   - Recordings viewer with search and filters

## Testing Workflows

### Workflow 1: Create a Participant

1. Click **"Participants"** in the sidebar
2. Click **"+ Add Participant"** button
3. Fill in the form:
   - Age Group: `18-25`
   - Gender: `Male` or `Female`
   - Region: `Ashanti`
4. Click **"Create Participant"**
5. ✅ System auto-generates unique ID like **SPK0001**
6. Participant appears in table immediately

**Test API directly:**
```bash
curl -X POST http://localhost:8000/api/participants \
  -H "Content-Type: application/json" \
  -d '{"age":"18-25","gender":"Male","region":"Ashanti"}'

# Response: {"speaker_id":"SPK0001","message":"Participant created..."}
```

### Workflow 2: Search Participants

1. Go to **Participants** page
2. Type in search box: `SPK0001`
3. Results filter in real-time
4. Try searching by age, gender, or region

**Test API directly:**
```bash
curl "http://localhost:8000/api/participants/search?q=SPK0001"
```

### Workflow 3: Add Test Recording Data

For testing without the Telegram bot, manually add test data:

```bash
mysql -u root -p twi_speech_db << EOF
-- Create test participant if not exists
INSERT IGNORE INTO participants (speaker_id, age, gender, region)
VALUES ('SPK0001', '18-25', 'Male', 'Ashanti');

-- Insert test recording
INSERT INTO recordings (telegram_id, speaker_id, sentence_id, audio_path, created_at)
SELECT 123456789, 'SPK0001', s.id, '/audio/sample.wav', NOW()
FROM sentences s
WHERE s.sentence_id = 'SENT0001'
LIMIT 1;
EOF
```

### Workflow 4: View Dashboard Statistics

1. Click **"Dashboard"** in sidebar
2. See real-time stats:
   - **Total Participants**: 1
   - **Total Recordings**: 1
   - **Total Sentences**: 3
   - **Completed**: Count of submitted
   - **Submitted Today**: Today's count
3. Recent recordings table shows latest submissions

**Test API directly:**
```bash
curl http://localhost:8000/api/dashboard/stats
# Response: {"total_participants":1,"total_recordings":1,...}
```

### Workflow 5: Browse Recordings

1. Click **"Recordings"** in sidebar
2. See table of all recordings with:
   - Speaker ID (clickable to filter)
   - Telegram ID
   - Sentence code
   - Twi text
   - **▶ Play button** for audio
   - **Download button** for offline access
3. Use filters:
   - **Search**: By speaker or sentence ID
   - **By Speaker**: Filter recordings for one participant
   - **By Date**: Filter by date range

### Workflow 6: Play & Download Audio

1. Go to **Recordings** page
2. Click **"▶ Play"** to stream audio in browser
3. Click **"Download"** to save audio file locally
4. Audio player controls: play, pause, volume, seek

## API Endpoints Reference

### Get Statistics
```bash
GET http://localhost:8000/api/dashboard/stats
```

### List Participants
```bash
GET http://localhost:8000/api/participants?limit=50&offset=0
```

### Create Participant
```bash
POST http://localhost:8000/api/participants
Content-Type: application/json

{"age":"18-25","gender":"Male","region":"Ashanti"}
```

### List Recordings
```bash
GET http://localhost:8000/api/recordings?limit=50&offset=0
```

### Search Recordings
```bash
GET http://localhost:8000/api/recordings/search?q=SPK0001
```

### Filter Recordings by Date
```bash
GET "http://localhost:8000/api/recordings/by-date?start_date=2026-06-21&end_date=2026-06-30"
```

### Get Recording Audio
```bash
GET http://localhost:8000/api/recordings/1/audio
```

### Interactive API Docs
- Visit: **http://localhost:8000/docs**
- Swagger UI for testing all endpoints
- Auto-generated from FastAPI code

## Troubleshooting

### "Cannot reach http://localhost:8000"
- Check if FastAPI is running: `curl http://localhost:8000/health`
- Check terminal for error messages
- Verify port 8000 is not in use: `lsof -i :8000`

### "Database connection refused"
- Verify MySQL is running: `mysql -u root -p -e "SELECT 1"`
- Check .env credentials match your MySQL setup
- Ensure database `twi_speech_db` exists

### "Frontend shows connection error"
- Check both API and frontend are running
- Check browser console (F12) for specific errors
- Verify frontend is trying to connect to `http://localhost:8000`
- Check CORS is enabled in FastAPI (should be by default)

### "No recordings appear"
- Manually insert test data using SQL commands above
- Or wait for actual Telegram bot submissions
- Check database: `SELECT COUNT(*) FROM recordings;`

## Development Tips

### Hot Reload
- **Frontend**: Changes to `.tsx` files auto-reload
- **Backend**: API reload enabled with `--reload` flag
- **Database**: Changes persist across restarts

### Database Inspection
```bash
# Connect to database
mysql -u root -p twi_speech_db

# Check participants
SELECT speaker_id, age, gender, region, created_at FROM participants LIMIT 5;

# Check recordings
SELECT r.id, r.speaker_id, s.sentence_id, r.created_at 
FROM recordings r 
JOIN sentences s ON r.sentence_id = s.id 
LIMIT 5;

# Check stats
SELECT COUNT(*) as total_participants FROM participants;
SELECT COUNT(*) as total_recordings FROM recordings;
```

### Build for Production
```bash
# Frontend production build
cd frontend
npm run build
# Output: dist/ folder with optimized files

# Backend deployment
# Use Gunicorn or similar: gunicorn -w 4 -k uvicorn.workers.UvicornWorker twi_bot.api.app:app
```

## Performance Notes

- Dashboard stats auto-refresh every 30 seconds
- Tables paginate at 50 items per page
- Searches execute in real-time
- Audio streams directly from disk
- Database queries indexed for speed

## Security Considerations

- No authentication currently (dev mode)
- Add JWT or API key for production
- All database queries use parameterized statements (SQL injection safe)
- CORS enabled for localhost:5173
- Database credentials in .env (not in git)

## Next Steps

1. ✅ Backend working? Test with `/docs`
2. ✅ Frontend working? See dashboard
3. ✅ Can create participants? IDs auto-generate
4. ✅ Can see recordings? Check database
5. Deploy to production when ready

---

**Need help?** Check:
- FastAPI logs in Terminal 1
- Frontend console (F12)
- MySQL error log
- DASHBOARD_README.md for detailed docs
