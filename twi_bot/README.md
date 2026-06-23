# Twi Speech Data Collection Bot

A controlled-access Telegram bot for collecting Twi (Akan) speech recordings
for Whisper fine-tuning. Participants are pre-registered by researchers in
MySQL (via an admin dashboard, not covered here) and identified by a
`speaker_id` — there is no self-registration.

## 1. Project structure

```
twi_bot/
├── main.py              # Application wiring + entry point
├── config.py             # Env-based configuration
├── constants.py          # Conversation states, callback_data, user_data keys
├── db.py                 # Async MySQL access layer (aiomysql, raw SQL)
├── schema.sql             # Full database schema
├── requirements.txt
├── .env.example
├── handlers/
│   ├── auth.py            # STEP 1–2: Speaker ID entry + validation
│   ├── consent.py         # STEP 4: consent prompt
│   ├── sentences.py       # STEP 5: non-repeating sentence assignment
│   ├── recording.py       # STEP 6: voice capture to temp storage
│   └── callbacks.py       # STEP 3 & 7: all inline-button logic
├── audio/                 # Permanent recordings (audio/<speaker_id>/<sentence_id>.ogg)
└── temp_audio/             # Scratch space, one file per active user (<telegram_id>.ogg)
```

## 2. Setup

### 2.1 MySQL

```bash
mysql -u root -p < schema.sql
```

This creates the `twi_speech_db` database and all four tables
(`participants`, `sentences`, `recordings`, `user_sentence_history`).
Use the commented `INSERT` statements at the bottom of `schema.sql` as a
starting point for seeding test participants and sentences — in
production these rows are written by your admin dashboard.

### 2.2 Python environment

```bash
cd twi_bot
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2.3 Configuration

```bash
cp .env.example .env
```

Edit `.env`:

```
TELEGRAM_BOT_TOKEN=<token from @BotFather>
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=yourpassword
DB_NAME=twi_speech_db
```

## 3. Run

```bash
python main.py
```

The bot starts polling. Send `/start` to it on Telegram with an account
that has never used it before, or `/cancel` at any point to reset your
session.

## 4. Conversation flow

| Step | Trigger | Handler | Notes |
|---|---|---|---|
| 1 | `/start` | `handlers/auth.py::start` | Clears any stale session state, asks for Speaker ID |
| 2 | text reply | `handlers/auth.py::receive_speaker_id` | Looks up `participants` by `speaker_id`; on mismatch, re-prompts |
| 3 | inline buttons | `handlers/callbacks.py::confirm_id_callback` | "Confirm" binds `telegram_id` → `speaker_id` (first time only) and proceeds to consent; "Wrong ID" loops back to step 2 |
| 4 | inline buttons | `handlers/callbacks.py::consent_callback` | "I Do Not Consent" ends the conversation immediately, no data is written |
| 5 | (automatic) | `handlers/sentences.py::assign_and_send_sentence` | Picks a random sentence the speaker has *never* seen (checked against `user_sentence_history`), inserts an `assigned` row, sends the prompt |
| 6 | voice message | `handlers/recording.py::receive_voice` | Downloads to `temp_audio/<telegram_id>.ogg`, shows Submit/Redo/Delete |
| 7 | inline buttons | `handlers/callbacks.py::review_callback` | Submit → moves file to permanent storage, writes `recordings` row, flips history to `completed`, immediately assigns the next sentence. Redo → re-prompts for a new recording (overwrites temp file). Delete → removes temp file and re-prompts. |

The cycle repeats from step 5 → 6 → 7 until `get_unused_sentence` returns
nothing, at which point the participant is thanked and the conversation
ends.

## 5. Design notes / assumptions

- **No-repeat guarantee**: `user_sentence_history` is checked for *both*
  `assigned` and `completed` rows, so even a sentence a user is
  currently mid-recording on (not yet submitted) can never be handed to
  them again. This is enforced at the SQL level (`NOT IN` subquery), not
  just in application logic.
- **Audio is only persisted on Submit**: Redo and Delete only ever touch
  `temp_audio/`. The `recordings` table and permanent `audio/` directory
  are written to exclusively inside the Submit branch of
  `review_callback`.
- **Speaker ID ↔ Telegram binding**: the first Telegram account to
  confirm a given `speaker_id` gets bound to it (`participants.telegram_id`
  is set once and never overwritten). This stops the same recordings
  from quietly being attributed to two different Telegram accounts, but
  doesn't hard-block a second person from entering the same ID and
  participating (their data is still correctly tagged by `speaker_id`).
  If you need strict one-device enforcement, add a check in
  `confirm_id_callback` that rejects confirmation when
  `participant['telegram_id']` is already set to a different ID.
- **Concurrency**: because Telegram updates for a single `ConversationHandler`
  user are processed sequentially, there's no race condition for one
  speaker getting the same sentence twice. Two *different* speakers can
  safely be assigned sentences concurrently since the uniqueness check is
  scoped per `speaker_id`.
- **`.ogg` audio**: Telegram voice messages are already Opus-in-OGG, so
  the bot stores them as-is — no transcoding step is needed before
  Whisper fine-tuning, though you may want a separate offline pass to
  resample/normalize for your training pipeline.
- **Error handling**: every DB call and file operation in the hot path
  (`auth.py`, `sentences.py`, `recording.py`, `callbacks.py`) is wrapped
  in try/except with logging, and the user is shown a friendly retry
  message rather than the bot silently dying mid-conversation.

## 6. Extending toward production

- Swap `persistent=False` in `main.py`'s `ConversationHandler` for a
  `PicklePersistence`/`DjangoPersistence`-backed store if you want
  sessions to survive bot restarts.
- Add a `python-telegram-bot` job to periodically purge orphaned files
  in `temp_audio/` (e.g. from users who abandoned the conversation
  mid-recording).
- The admin dashboard (not included here) just needs write access to
  `participants` and `sentences` — no bot-side changes are required to
  add new researchers' participants or sentence pools.
