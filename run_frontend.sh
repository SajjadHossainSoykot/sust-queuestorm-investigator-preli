#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/frontend"

[ -f ".env" ] || [ ! -f ".env.example" ] || cp .env.example .env

[ -d "node_modules" ] || npm install

npm run dev