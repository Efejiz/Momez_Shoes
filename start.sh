#!/usr/bin/env bash
set -euo pipefail

# Railpack startup script: run Python backend with Uvicorn

# Move into backend directory
cd backend

# Upgrade pip and install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# Pick port from environment (Railpack sets $PORT)
PORT="${PORT:-8000}"

# Start FastAPI app
python -m uvicorn server:app --host 0.0.0.0 --port "$PORT"