# QueueStorm Investigator — SUST Preliminary API

A lightweight, rule-based FastAPI service for the **SUST CSE Carnival 2026 Codex Community Hackathon preliminary round**.

The service exposes the required endpoints:

- `GET /health`
- `POST /analyze-ticket`

It accepts a customer complaint plus recent transaction history and returns a structured JSON investigation response with transaction matching, evidence verdict, case classification, routing, severity, safe customer reply, and human-review decision.

## Why this implementation

The preliminary round mainly rewards:

1. Exact API/schema compliance
2. Evidence reasoning over complaint + transaction history
3. Fintech safety guardrails
4. Reliability and fast response time
5. Clear reproducibility

This project intentionally avoids databases, frontend dependencies, GPU, huge local models, runtime training, and paid API calls. That keeps the service small, fast, and judgeable.

## Tech stack

- Python 3.11
- FastAPI
- Pydantic v2
- Uvicorn
- Deterministic rule-based reasoning

## Project structure

```text
.
├── app/
│   ├── main.py          # FastAPI routes and safe error handlers
│   ├── schemas.py       # Strict request/response schemas and enums
│   ├── investigator.py  # Main orchestration logic
│   ├── matcher.py       # Transaction matching and evidence verdicts
│   ├── taxonomy.py      # Case classification, department, severity rules
│   ├── safety.py        # Safe templates and final output guardrails
│   └── text_utils.py    # Text normalization, amount/phone helpers
├── samples/
│   ├── sample_request_wrong_transfer.json
│   ├── sample_request_phishing.json
│   ├── sample_request_duplicate_payment.json
│   └── sample_output_wrong_transfer.json
├── tests/
│   └── test_api.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── RUNBOOK.md
└── .env.example
```

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Or use the helper:

```bash
./run_local.sh
```

## Run with Docker

```bash
docker build -t queuestorm-investigator .
docker run -p 8000:8000 --env-file .env.example queuestorm-investigator
```

Docker Compose:

```bash
docker compose up --build
```

## Required endpoints

### Health

```bash
curl http://localhost:8000/health
```

Expected:

```json
{"status":"ok"}
```

### Analyze ticket

```bash
curl -X POST http://localhost:8000/analyze-ticket \
  -H "Content-Type: application/json" \
  --data-binary @samples/sample_request_wrong_transfer.json | python -m json.tool
```

## Request schema summary

`POST /analyze-ticket` accepts:

```json
{
  "ticket_id": "TKT-001",
  "complaint": "I sent 5000 taka to a wrong number around 2pm today...",
  "language": "en",
  "channel": "in_app_chat",
  "user_type": "customer",
  "campaign_context": "boishakh_bonanza_day_1",
  "transaction_history": [
    {
      "transaction_id": "TXN-9101",
      "timestamp": "2026-04-14T14:08:22Z",
      "type": "transfer",
      "amount": 5000,
      "counterparty": "+8801719876543",
      "status": "completed"
    }
  ]
}
```

## Response schema summary

The API returns all required fields:

```json
{
  "ticket_id": "TKT-001",
  "relevant_transaction_id": "TXN-9101",
  "evidence_verdict": "consistent",
  "case_type": "wrong_transfer",
  "severity": "high",
  "department": "dispute_resolution",
  "agent_summary": "...",
  "recommended_next_action": "...",
  "customer_reply": "...",
  "human_review_required": true,
  "confidence": 0.95,
  "reason_codes": ["wrong_transfer", "transaction_match", "consistent"]
}
```

## Evidence reasoning approach

The service is an investigator, not only a classifier.

It compares the complaint against `transaction_history` using:

- Explicit transaction ID mentions
- Amount match
- Transaction type match
- Counterparty/last-digit match
- Status match
- Case-intent keywords
- Duplicate transaction clustering

Then it sets:

- `relevant_transaction_id`
- `evidence_verdict`: `consistent`, `inconsistent`, or `insufficient_data`
- `case_type`
- `department`
- `severity`
- `human_review_required`

## Safety logic

The service uses fixed safe templates and a final guardrail pass.

It never asks the customer for:

- PIN
- OTP
- password
- verification code
- full card number
- CVV
- secret credentials

It does not promise:

- refund
- reversal
- account unblock
- money recovery

Instead, it uses safe wording like:

> If any amount is found eligible, it will be processed through official channels.

For phishing/social engineering cases, it warns the customer not to share credentials and routes the case to `fraud_risk`.

## MODELS

No external LLM or local ML model is used by default.

| Model | Where it runs | Why chosen |
|---|---|---|
| `rule_based_v1` | Inside FastAPI service | Fast, deterministic, no API cost, no GPU, no secrets, low latency |

The `.env.example` includes optional placeholders only. Do not commit real secrets.

## Known limitations

- Keyword-based Bangla/Banglish support is practical but not exhaustive.
- It does not verify real ledger state or call real payment APIs.
- It does not calculate exact time-window matching beyond transaction fields provided in the input.
- It prioritizes safe escalation when evidence is ambiguous.
- It is optimized for the preliminary judge contract, not production fintech operations.

## Testing

Install test dependency if needed:

```bash
pip install pytest httpx
pytest -q
```

Or smoke test a running server:

```bash
./scripts/smoke_test.sh http://localhost:8000
```

## Deployment notes

Submit a public base URL where judges can call:

```text
GET  https://your-service-url/health
POST https://your-service-url/analyze-ticket
```

No login, dashboard access, manual approval, or private network should be required.

## No real customer data

This repository uses synthetic sample data only. It does not integrate with real payment APIs or real customer records.
