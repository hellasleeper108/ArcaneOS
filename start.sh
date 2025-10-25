#!/bin/bash
# ArcaneOS Startup Script for Railway
# Handles dynamic PORT environment variable

# Use Railway's PORT if provided, otherwise default to 8000
PORT=${PORT:-8000}

echo "🔮 Starting ArcaneOS on port $PORT..."

# Start uvicorn with the configured port
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
