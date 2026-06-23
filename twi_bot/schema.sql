-- =====================================================================
-- Twi Speech Data Collection — PostgreSQL Schema
-- =====================================================================
-- This file is automatically run by the postgres Docker entrypoint
-- against the database specified by POSTGRES_DB, so DO NOT include
-- CREATE DATABASE here.
-- =====================================================================

-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS participants (
    id            BIGSERIAL PRIMARY KEY,
    telegram_id   BIGINT NULL,
    speaker_id    VARCHAR(32)  NOT NULL,
    name          VARCHAR(128) NOT NULL,
    age           VARCHAR(32)  NOT NULL,
    gender        VARCHAR(16)  NOT NULL,
    region        VARCHAR(64)  NOT NULL,
    created_at    TIMESTAMP NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_participants_speaker_id  ON participants(speaker_id);
CREATE UNIQUE INDEX IF NOT EXISTS uq_participants_telegram_id ON participants(telegram_id) WHERE telegram_id IS NOT NULL;

-- ---------------------------------------------------------------------
-- sentences
-- Master pool of Twi prompts to be read aloud.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sentences (
    id            BIGSERIAL PRIMARY KEY,
    sentence_id   VARCHAR(32) NOT NULL,
    text          TEXT NOT NULL,
    created_at    TIMESTAMP NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_sentences_sentence_id ON sentences(sentence_id);

-- ---------------------------------------------------------------------
-- recordings
-- Only written AFTER a user explicitly presses "Submit". Redo/Delete
-- never touch this table.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS recordings (
    id            BIGSERIAL PRIMARY KEY,
    telegram_id   BIGINT NOT NULL,
    speaker_id    VARCHAR(32) NOT NULL,
    sentence_id   BIGINT NOT NULL,
    audio_path    VARCHAR(512) NOT NULL,
    created_at    TIMESTAMP NOT NULL DEFAULT now(),
    CONSTRAINT fk_recordings_sentence FOREIGN KEY (sentence_id) REFERENCES sentences(id),
    CONSTRAINT fk_recordings_speaker  FOREIGN KEY (speaker_id)  REFERENCES participants(speaker_id)
);

CREATE INDEX IF NOT EXISTS idx_recordings_speaker_id  ON recordings(speaker_id);
CREATE INDEX IF NOT EXISTS idx_recordings_sentence_id ON recordings(sentence_id);

-- ---------------------------------------------------------------------
-- user_sentence_history
-- The source of truth for "this sentence was already given to this
-- speaker". A row is inserted with status='assigned' the moment a
-- sentence is handed out, and flipped to 'completed' only on Submit.
-- Both statuses count as "already used" so a sentence a user is
-- mid-recording on can never be reassigned to them either.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS user_sentence_history (
    id            BIGSERIAL PRIMARY KEY,
    telegram_id   BIGINT NOT NULL,
    speaker_id    VARCHAR(32) NOT NULL,
    sentence_id   BIGINT NOT NULL,
    status        VARCHAR(16) NOT NULL DEFAULT 'assigned' CHECK (status IN ('assigned', 'completed')),
    created_at    TIMESTAMP NOT NULL DEFAULT now(),
    updated_at    TIMESTAMP NOT NULL DEFAULT now()
);
ALTER TABLE user_sentence_history ADD CONSTRAINT fk_ush_sentence FOREIGN KEY (sentence_id) REFERENCES sentences(id);
ALTER TABLE user_sentence_history ADD CONSTRAINT fk_ush_speaker  FOREIGN KEY (speaker_id)  REFERENCES participants(speaker_id);

CREATE INDEX IF NOT EXISTS idx_ush_speaker_sentence ON user_sentence_history(speaker_id, sentence_id);
CREATE INDEX IF NOT EXISTS idx_ush_status           ON user_sentence_history(status);

-- Auto-update updated_at on modification of user_sentence_history
CREATE OR REPLACE FUNCTION update_user_sentence_history_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_ush_timestamp ON user_sentence_history;
CREATE TRIGGER trg_ush_timestamp
    BEFORE UPDATE ON user_sentence_history
    FOR EACH ROW EXECUTE FUNCTION update_user_sentence_history_timestamp();

-- ---------------------------------------------------------------------
-- Sample seed data — remove or replace before going to production
-- ---------------------------------------------------------------------
-- INSERT INTO participants (speaker_id, age, gender, region) VALUES
--   ('SPK1001', '18-25', 'Male', 'Ashanti'),
--   ('SPK1002', '26-35', 'Female', 'Greater Accra');
--
-- INSERT INTO sentences (sentence_id, text) VALUES
--   ('SENT0001', 'Mema wo akwaaba.'),
--   ('SENT0002', 'Wo ho te sen?'),
--   ('SENT0003', 'Me din de Kofi.');
