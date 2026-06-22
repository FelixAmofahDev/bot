# Architecture & File Structure

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Admin Dashboard                          │
│                   React + TypeScript                        │
│            http://localhost:5173                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Dashboard  │  Participants  │  Recordings          │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                    CORS + Axios
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    FastAPI Backend                          │
│                   http://localhost:8000                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  /api/participants   │  /api/recordings             │  │
│  │  /api/dashboard      │  /health                     │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                    aiomysql
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    MySQL Database                           │
│            twi_speech_db                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  participants  │  recordings  │  sentences           │  │
│  │  user_sentence_history                               │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Complete File Structure

```
twi_bot/
│
├── 📄 run_api.py                      # FastAPI startup script
├── 📄 DASHBOARD_README.md             # Main documentation
├── 📄 QUICKSTART.md                   # Quick start guide
├── 📄 ARCHITECTURE.md                 # This file
│
├── twi_bot/                           # Python package
│   ├── 📄 main.py                     # Telegram bot entry point
│   ├── 📄 db.py                       # Database access layer (EXTENDED)
│   ├── 📄 config.py                   # Configuration from .env
│   ├── 📄 constants.py                # Constants (bot states, etc.)
│   ├── 📄 schema.sql                  # Database schema
│   ├── 📄 requirements.txt            # Python dependencies
│   ├── 📄 .env.example                # Environment template
│   ├── 📄 .env                        # Local config (gitignored)
│   │
│   ├── api/                           # FastAPI admin dashboard (NEW)
│   │   ├── 📄 __init__.py             # Package init
│   │   ├── 📄 app.py                  # FastAPI app + middleware
│   │   ├── 📄 schemas.py              # Pydantic models for validation
│   │   │
│   │   └── routes/                    # API endpoint handlers
│   │       ├── 📄 __init__.py
│   │       ├── 📄 participants.py     # Participant CRUD endpoints
│   │       ├── 📄 recordings.py       # Recording list/filter endpoints
│   │       └── 📄 dashboard.py        # Stats/overview endpoints
│   │
│   ├── handlers/                      # Telegram bot handlers (existing)
│   │   ├── 📄 auth.py
│   │   ├── 📄 callbacks.py
│   │   ├── 📄 consent.py
│   │   ├── 📄 recording.py
│   │   └── 📄 sentences.py
│   │
│   ├── audio/                         # Audio storage directory
│   └── temp_audio/                    # Temporary audio files
│
└── frontend/                          # React dashboard (NEW)
    ├── 📄 package.json                # Node dependencies
    ├── 📄 tsconfig.json               # TypeScript config
    ├── 📄 vite.config.ts              # Vite build config
    ├── 📄 tailwind.config.js          # Tailwind CSS config
    ├── 📄 postcss.config.js           # PostCSS config
    ├── 📄 index.html                  # HTML entry point
    │
    └── src/
        ├── 📄 main.tsx                # React entry point
        ├── 📄 App.tsx                 # Main app + routing
        ├── 📄 App.css                 # Global styles
        ├── 📄 index.css               # Tailwind + CSS reset
        ├── 📄 types.ts                # TypeScript interfaces
        │
        ├── components/
        │   ├── 📄 index.ts            # Component exports
        │   └── 📄 Layout.tsx          # Main layout with sidebar
        │
        ├── pages/
        │   ├── 📄 index.ts            # Page exports
        │   ├── 📄 Dashboard.tsx       # Dashboard overview
        │   ├── 📄 Participants.tsx    # Participant management
        │   └── 📄 Recordings.tsx      # Recording viewer
        │
        └── hooks/
            ├── 📄 index.ts            # Hook exports
            ├── 📄 useApi.ts           # Axios API wrapper
            ├── 📄 useParticipants.ts  # Participant data fetching
            └── 📄 useRecordings.ts    # Recording data fetching
```

## Database Schema

### participants
```sql
CREATE TABLE participants (
    id BIGINT PRIMARY KEY,
    telegram_id BIGINT UNIQUE NULL,      -- Bound after first bot verification
    speaker_id VARCHAR(32) UNIQUE,        -- SPK0001, SPK0002, etc.
    age VARCHAR(32),                      -- "18-25", "26-35", etc.
    gender VARCHAR(16),                   -- "Male", "Female", "Other"
    region VARCHAR(64),                   -- "Ashanti", "Greater Accra", etc.
    created_at TIMESTAMP
);
```

### recordings
```sql
CREATE TABLE recordings (
    id BIGINT PRIMARY KEY,
    telegram_id BIGINT,                   -- Who submitted
    speaker_id VARCHAR(32),               -- SPK0001, etc.
    sentence_id BIGINT,                   -- Foreign key to sentences
    audio_path VARCHAR(512),              -- Path to stored audio
    created_at TIMESTAMP
);
```

### sentences
```sql
CREATE TABLE sentences (
    id BIGINT PRIMARY KEY,
    sentence_id VARCHAR(32),              -- SENT0001, SENT0002, etc.
    text TEXT,                            -- Twi sentence prompt
    created_at TIMESTAMP
);
```

### user_sentence_history
```sql
CREATE TABLE user_sentence_history (
    id BIGINT PRIMARY KEY,
    telegram_id BIGINT,
    speaker_id VARCHAR(32),
    sentence_id BIGINT,
    status ENUM('assigned', 'completed'), -- Track sentence assignment status
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

## API Routes Overview

### Participants Endpoints
- `GET    /api/participants` - List (paginated)
- `POST   /api/participants` - Create (auto-generates speaker_id)
- `GET    /api/participants/{speaker_id}` - Get one
- `PUT    /api/participants/{speaker_id}` - Update
- `DELETE /api/participants/{speaker_id}` - Delete
- `GET    /api/participants/search` - Search

### Recordings Endpoints
- `GET    /api/recordings` - List (paginated)
- `GET    /api/recordings/search` - Search
- `GET    /api/recordings/by-speaker/{id}` - Filter by speaker
- `GET    /api/recordings/by-date` - Filter by date range
- `GET    /api/recordings/{id}/audio` - Download/stream audio
- `DELETE /api/recordings/{id}` - Delete

### Dashboard Endpoints
- `GET    /api/dashboard/stats` - Overall statistics
- `GET    /api/dashboard/recent-recordings` - Last N recordings
- `GET    /api/dashboard/completion-stats` - Per-participant stats

### System Endpoints
- `GET    /health` - Health check
- `GET    /docs` - Swagger API documentation

## Data Flow: Creating a Participant

```
1. User fills form in React (Age, Gender, Region)
   ↓
2. Frontend sends POST to /api/participants
   ↓
3. FastAPI routes to participants.create_participant()
   ↓
4. Backend calls db.create_participant()
   ↓
5. db.py queries for next speaker_id (SPK0001, SPK0002, etc.)
   ↓
6. INSERT into database
   ↓
7. Return speaker_id to frontend
   ↓
8. React displays success message + new participant in table
```

## Data Flow: Playing a Recording

```
1. User clicks "▶ Play" in Recordings table
   ↓
2. Frontend calls getAudioUrl(recording_id)
   ↓
3. Requests GET /api/recordings/{id}/audio
   ↓
4. FastAPI retrieves audio_path from database
   ↓
5. Serves file via FileResponse (streams to browser)
   ↓
6. HTML5 audio player controls playback
```

## Backend Technologies

### FastAPI
- Modern Python web framework (async support)
- Auto-generates Swagger documentation
- Type hints with Pydantic validation
- Built-in request/response serialization

### aiomysql
- Asynchronous MySQL driver
- Connection pooling for efficiency
- Compatible with FastAPI's async architecture

### Database Layer (db.py)
- Raw SQL with parameterized queries (SQL injection safe)
- DictCursor for readable row results
- No ORM layer (transparency, as per spec)
- Global connection pool managed by FastAPI lifespan hooks

## Frontend Technologies

### React 19
- Latest React with automatic re-rendering
- Functional components + hooks pattern
- TypeScript for type safety

### React Router
- Client-side routing (no page reloads)
- Three main routes: Dashboard, Participants, Recordings

### TailwindCSS
- Utility-first CSS framework
- Responsive design (mobile-first)
- Professional component styling

### Axios
- Promise-based HTTP client
- Centralized API configuration
- Error handling

### Vite
- Lightning-fast development server
- Optimized production builds
- Hot module reloading (HMR)

## Key Design Decisions

### 1. Separate API & Frontend
- Independent scaling
- Flexibility in deployment
- Clear separation of concerns

### 2. No ORM Layer
- Raw SQL for transparency
- Direct control over queries
- Simpler for small to medium datasets

### 3. Async Database Access
- Handles concurrent requests efficiently
- Compatible with FastAPI's async model
- Scalable to many simultaneous users

### 4. Client-Side Routing
- Single-page application (SPA)
- Fast navigation without server round trips
- Responsive user experience

### 5. TypeScript Throughout Frontend
- Catches errors at compile time
- Excellent IDE support
- Better code documentation

### 6. TailwindCSS for Styling
- No CSS conflicts or specificity issues
- Consistent design system
- Responsive by default

## Development Workflow

### Adding a New Participant Feature
1. Add API endpoint in `api/routes/participants.py`
2. Add Pydantic model in `api/schemas.py`
3. Add database function in `db.py`
4. Update React hook in `hooks/useParticipants.ts`
5. Update React component/page
6. Test in browser + API docs

### Adding a New Page
1. Create `pages/NewPage.tsx`
2. Add route in `App.tsx`
3. Add navigation link in `Layout.tsx`
4. Create hooks if needed
5. Style with Tailwind classes

### Database Changes
1. Update `schema.sql`
2. Add new database functions to `db.py`
3. Update API endpoints to use new functions
4. Update TypeScript types in `frontend/src/types.ts`

## Performance Optimizations

### Backend
- Database indexes on speaker_id, sentence_id
- Connection pooling (max 10 connections)
- Pagination to limit query results
- Async processing for concurrent requests

### Frontend
- Component-level re-renders only
- Pagination of large tables
- Auto-refresh every 30 seconds (not real-time)
- Lazy loading on demand

### Database
- Indexed foreign keys
- UNIQUE constraints on speaker_id
- Efficient JOIN queries for recording details

## Security Considerations

### Currently (Development)
- No authentication required
- CORS enabled for localhost:5173
- Raw SQL with parameterized queries (safe)
- Audio files served directly from disk

### Production Recommendations
- Add JWT authentication
- Implement role-based access control (RBAC)
- Use environment secrets for API keys
- Add rate limiting
- Enable HTTPS
- Implement proper audit logging
- Sanitize file uploads

## Deployment Considerations

### Backend
- Use Gunicorn with multiple workers
- Deploy behind nginx reverse proxy
- Configure for production database
- Set environment variables securely

### Frontend
- Build with `npm run build`
- Serve dist/ folder via web server
- Configure API_BASE for production URL
- Enable gzip compression

### Database
- Daily backups
- Read-only replicas for scaling
- Proper indexing and optimization
- Connection pooling at application level

---

For detailed documentation, see DASHBOARD_README.md and QUICKSTART.md
