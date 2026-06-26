#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/backend"

[ -d ".venv" ] || python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

[ -f ".env" ] || [ ! -f ".env.example" ] || cp .env.example .env

python run.py