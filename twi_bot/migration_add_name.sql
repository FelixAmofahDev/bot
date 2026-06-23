-- =====================================================================
-- Migration: add name column to existing participants table
-- Run this against an existing twi_speech_db if the column is missing:
--   psql -U postgres twi_speech_db < migration_add_name.sql
-- =====================================================================

ALTER TABLE participants
  ADD COLUMN IF NOT EXISTS name VARCHAR(128) NOT NULL DEFAULT 'Unknown';
