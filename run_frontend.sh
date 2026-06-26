#!/usr/bin/env bash
set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$ROOT_DIR/frontend"

if [ ! -d "$FRONTEND_DIR" ]; then
  echo "Error: frontend folder not found at $FRONTEND_DIR"
  exit 1
fi

cd "$FRONTEND_DIR"

echo "Starting QueueStorm Investigator frontend..."

if [ ! -f ".env" ] && [ -f ".env.example" ]; then
  echo "No frontend/.env found. Creating frontend/.env from frontend/.env.example ..."
  cp .env.example .env
fi

if [ ! -d "node_modules" ]; then
  echo "Installing frontend dependencies..."
  npm install
fi

echo "Frontend will run at: http://localhost:5173"
echo "Make sure frontend/.env contains: VITE_API_BASE_URL=http://localhost:8000 for local backend testing."
npm run dev
