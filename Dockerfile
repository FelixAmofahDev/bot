# Multi-stage Docker build for Twi Speech Admin Dashboard

# Stage 1: Build the React frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

# Accept build-time API base (defaults to /api for same-origin serving)
ARG VITE_API_BASE=/api
ENV VITE_API_BASE=${VITE_API_BASE}

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci --silent

COPY frontend/ ./
RUN npm run build

# Stage 2: Python runtime for FastAPI + Telegram bot
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        default-mysql-client \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY twi_bot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY twi_bot/ ./

# Copy built frontend from Stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Create directories for audio storage
RUN mkdir -p audio temp_audio

# Expose port
EXPOSE 8000

# Default command (FastAPI API; bot runs as separate service via docker-compose)
CMD ["sh", "-c", "uvicorn api.app:app --host 0.0.0.0 --port ${PORT:-8000}"]
