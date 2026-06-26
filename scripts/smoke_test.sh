#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-http://localhost:8000}"

echo "Checking $BASE_URL/health"
curl -sS "$BASE_URL/health"
echo

echo "Checking $BASE_URL/analyze-ticket"
curl -sS -X POST "$BASE_URL/analyze-ticket" \
  -H 'Content-Type: application/json' \
  --data-binary @samples/sample_request_wrong_transfer.json | python3 -m json.tool

