# RUNBOOK — QueueStorm Investigator

This file gives judges or teammates a copy-paste path to run the service.

## Option A: Local Python

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Health check:

```bash
curl http://localhost:8000/health
```

Expected:

```json
{"status":"ok"}
```

Analyze sample:

```bash
curl -X POST http://localhost:8000/analyze-ticket \
  -H "Content-Type: application/json" \
  --data-binary @samples/sample_request_wrong_transfer.json | python -m json.tool
```

## Option B: Docker

```bash
docker build -t queuestorm-investigator .
docker run -p 8000:8000 --env-file .env.example queuestorm-investigator
```

Then run:

```bash
./scripts/smoke_test.sh http://localhost:8000
```

## Option C: Docker Compose

```bash
docker compose up --build
```

## Environment variables

The default implementation requires no real secrets.

`.env.example` contains placeholders only:

```text
PORT=8000
MODEL_NAME=rule_based_v1
OPENAI_API_KEY=
```

Do not commit real `.env` files or API keys.

## Troubleshooting

| Problem | Fix |
|---|---|
| 404 on `/health` | Confirm the base URL and exact route name. |
| 404 on `/analyze-ticket` | Confirm route spelling and POST method. |
| 422 response | Check required fields, enum values, and non-empty complaint. |
| Timeout | This code is rule-based; restart service and check deployment CPU/memory. |
| Docker unreachable | Ensure container binds to `0.0.0.0` and port `8000` is exposed. |
| Invalid JSON | Ensure request header is `Content-Type: application/json`. |

## Final pre-submit checklist

- [ ] `GET /health` returns `{"status":"ok"}`.
- [ ] `POST /analyze-ticket` returns all required fields.
- [ ] Enum values match the problem statement exactly.
- [ ] Empty/malformed input does not crash the process.
- [ ] Customer reply does not ask for PIN, OTP, password, or secret credentials.
- [ ] Customer reply does not promise refund, reversal, recovery, or account unblock.
- [ ] README includes setup, run command, sample request/response, model usage, safety logic, and limitations.
- [ ] `.env.example` contains placeholders only.
- [ ] No `.env`, database, virtualenv, or secrets are committed.
