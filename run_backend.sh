#!/usr/bin/env bash
set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"

if [ ! -d "$BACKEND_DIR" ]; then
  echo "Error: backend folder not found at $BACKEND_DIR"
  exit 1
fi

cd "$BACKEND_DIR"

echo "Starting QueueStorm Investigator backend..."

if [ ! -d ".venv" ]; then
  echo "Creating Python virtual environment in backend/.venv ..."
  python3 -m venv .venv
fi

source .venv/bin/activate

echo "Installing/updating backend dependencies..."
pip install -r requirements.txt

if [ ! -f ".env" ] && [ -f ".env.example" ]; then
  echo "No backend/.env found. Creating backend/.env from backend/.env.example ..."
  cp .env.example .env
  echo "Please edit backend/.env later if you want to add GEMINI_API_KEY."
fi

echo "Backend will run at: http://localhost:8000"
echo "Health check:       http://localhost:8000/health"
python run.py
