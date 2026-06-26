#!/usr/bin/env bash
set -euo pipefail

# Try to set up venv, but if it fails or gets blocked, fallback to using the global python packages
if python3 -m venv .venv 2>/dev/null && source .venv/bin/activate 2>/dev/null; then
  # Use --no-cache-dir to prevent sandbox violations from accessing global cache directories
  if pip install --no-cache-dir --upgrade pip 2>/dev/null && pip install --no-cache-dir -r requirements.txt 2>/dev/null; then
    echo "Virtual environment successfully created and dependencies installed."
  else
    echo "Warning: pip install failed. Deactivating venv and falling back to global packages."
    deactivate 2>/dev/null || true
  fi
else
  echo "Warning: venv creation failed. Falling back to global packages."
fi

PORT="${PORT:-8000}"
echo "Attempting to start uvicorn on port $PORT..."
if ! python3 -m uvicorn app.main:app --host 0.0.0.0 --port "$PORT" --reload; then
  if [ "$PORT" -eq 8000 ]; then
    echo "Failed to bind to port 8000 (possibly due to system/sandbox restrictions). Trying fallback port 8080..."
    python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
  else
    exit 1
  fi
fi
