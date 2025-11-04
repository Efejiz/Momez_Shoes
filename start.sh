#!/bin/sh
# POSIX-compatible startup for Railpack (container may use /bin/sh)
set -eu

# Railpack startup script: run Python backend with Uvicorn

# Move into backend directory
cd backend

# Upgrade pip and install dependencies
# Install dependencies
python -m pip install --upgrade pip || true
python -m pip install -r requirements.txt

# Pick port from environment (Railpack sets $PORT)
PORT=${PORT:-8000}

# Start FastAPI app
exec python -m uvicorn server:app --host 0.0.0.0 --port "$PORT"