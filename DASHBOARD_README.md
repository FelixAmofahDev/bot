# Twi Speech Admin Dashboard

Professional admin dashboard for managing participants and monitoring recorded speech data for the Twi language speech collection project.

## Features

### 📊 Dashboard
- Overview statistics (total participants, recordings, sentences, completed items, submitted today)
- Recent recordings display (last 10 submissions)
- Real-time data refresh (every 30 seconds)

### 👥 Participant Management
- Add new participants with auto-generated unique Speaker IDs (SPK0001, SPK0002, etc.)
- View all participants with pagination
- Search participants by Speaker ID, age, gender, or region
- Edit participant information
- Delete participants
- Track participant creation dates

### 🎙️ Recording Management
- View all submitted recordings with detailed information
- Search recordings by Speaker ID or Sentence ID
- Filter recordings by:
  - Specific speaker
  - Date range
- Play audio directly in the dashboard
- Download recordings for analysis
- Delete recordings if needed
- Responsive table layout (adapts to mobile/tablet)

## Project Structure

```
twi_bot/
├── twi_bot/              # Backend Python package
│   ├── api/              # FastAPI application
│   │   ├── app.py        # Main FastAPI app with routes
│   │   ├── schemas.py    # Pydantic request/response models
│   │   └── routes/       # API endpoint handlers
│   │       ├── participants.py
│   │       ├── recordings.py
│   │       └── dashboard.py
│   ├── db.py             # Database access layer (extended with admin functions)
│   ├── main.py           # Telegram bot entry point
│   ├── handlers/         # Telegram bot handlers
│   └── requirements.txt  # Python dependencies
├── frontend/             # React dashboard
│   ├── src/
│   │   ├── pages/        # Dashboard, Participants, Recordings pages
│   │   ├── components/   # Layout, reusable UI components
│   │   ├── hooks/        # API calls, data fetching
│   │   ├── types.ts      # TypeScript interfaces
│   │   └── App.tsx       # Main app with routing
│   └── package.json
├── run_api.py            # FastAPI startup script
└── README.md             # This file
```

## Running the System

### Prerequisites
- Python 3.8+
- Node.js 18+
- MySQL database with schema initialized
- .env file configured with database credentials

### Setup

1. **Install Backend Dependencies**
   ```bash
   cd twi_bot
   pip install -r requirements.txt
   ```

2. **Install Frontend Dependencies**
   ```bash
   cd frontend
   npm install
   ```

3. **Database Setup**
   ```bash
   # Initialize the database with the schema
   mysql -u root -p < twi_bot/schema.sql
   ```

4. **Configure Environment**
   ```bash
   # Update .env file in twi_bot/ directory
   TELEGRAM_BOT_TOKEN=your_token_here
   DB_HOST=127.0.0.1
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=your_password
   DB_NAME=twi_speech_db
   API_PORT=8000
   ```

### Running Services

Open three separate terminal windows:

**Terminal 1: Telegram Bot**
```bash
cd twi_bot
python main.py
```

**Terminal 2: FastAPI Admin Dashboard Backend**
```bash
python run_api.py
# Server runs on http://localhost:8000
# API documentation: http://localhost:8000/docs
```

**Terminal 3: React Frontend Development Server**
```bash
cd frontend
npm run dev
# Dashboard runs on http://localhost:5173
```

## API Endpoints

### Participants
- `GET /api/participants` - List all participants (paginated, 50 per page)
- `POST /api/participants` - Create new participant (auto-generates Speaker ID)
- `GET /api/participants/{speaker_id}` - Get participant details
- `PUT /api/participants/{speaker_id}` - Update participant
- `DELETE /api/participants/{speaker_id}` - Delete participant
- `GET /api/participants/search?q=query` - Search participants

### Recordings
- `GET /api/recordings` - List all recordings (paginated)
- `GET /api/recordings/search?q=query` - Search recordings
- `GET /api/recordings/by-speaker/{speaker_id}` - Get recordings for a speaker
- `GET /api/recordings/by-date?start_date=2026-06-21&end_date=2026-06-30` - Filter by date
- `GET /api/recordings/{recording_id}/audio` - Download/stream audio
- `DELETE /api/recordings/{recording_id}` - Delete recording

### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/dashboard/recent-recordings` - Get last 10 recordings
- `GET /api/dashboard/completion-stats` - Per-participant completion stats

### Health
- `GET /health` - API health check

## API Documentation

Once the FastAPI server is running, visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI).

## Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **aiomysql** - Async MySQL driver
- **Pydantic** - Data validation

### Frontend
- **React 19** - UI library
- **TypeScript** - Type safety
- **React Router** - Navigation
- **Axios** - HTTP client
- **TailwindCSS** - Styling
- **Vite** - Build tool

## Features in Detail

### Auto-Generated Speaker IDs
- System automatically generates unique IDs in format SPK0001, SPK0002, etc.
- IDs are used by participants to access the Telegram bot
- Each participant gets a unique ID upon creation

### Pagination
- Tables support pagination with configurable page sizes
- Default: 50 items per page
- Users can navigate between pages

### Responsive Design
- Dashboard adapts to mobile, tablet, and desktop screens
- Sidebar navigation collapses on mobile
- Tables convert to card layout on small screens
- Touch-friendly buttons and forms

### Search & Filtering
- Real-time search across participant database
- Filter recordings by speaker, date range, or text search
- Instant results with visual feedback

### Audio Management
- Stream audio directly from browser
- Download recordings for offline analysis
- Delete recordings when no longer needed
- Audio paths stored in database

## Development Notes

### Database Design
- Participants table: Stores speaker profiles
- Recordings table: Stores submitted audio with metadata
- Sentences table: Master list of prompts
- user_sentence_history table: Tracks sentence assignments and completion

### API Authentication
- Currently no authentication (development mode)
- Can be extended with JWT or API key validation

### Error Handling
- All endpoints return consistent error responses
- API returns 404 for not found, 400 for bad requests, 500 for server errors
- Frontend displays user-friendly error messages

## Future Enhancements

- User authentication and role-based access control
- Data visualization charts (daily submissions, completion rates)
- Bulk operations (import/export participants)
- Advanced analytics and reporting
- Automated backups
- API rate limiting

## Troubleshooting

### Frontend can't connect to API
- Check if FastAPI server is running on http://localhost:8000
- Verify CORS is enabled (should be by default)
- Check browser console for specific errors

### Database connection fails
- Verify MySQL is running
- Check .env credentials
- Ensure database is initialized with schema.sql

### Missing audio files
- Check AUDIO_DIR path in config.py
- Verify audio files exist in storage directory
- Check file permissions

## Support

For issues or questions, check:
1. API documentation: http://localhost:8000/docs
2. FastAPI logs in terminal
3. Browser console (F12) for frontend errors
4. MySQL error logs

---

Built with ❤️ for Twi language speech data collection
