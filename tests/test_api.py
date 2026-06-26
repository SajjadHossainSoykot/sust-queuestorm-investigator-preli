from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_wrong_transfer_analysis():
    payload = {
        "ticket_id": "TKT-001",
        "complaint": "I sent 5000 taka to a wrong number around 2pm today. Please help.",
        "language": "en",
        "channel": "in_app_chat",
        "user_type": "customer",
        "transaction_history": [
            {
                "transaction_id": "TXN-9101",
                "timestamp": "2026-04-14T14:08:22Z",
                "type": "transfer",
                "amount": 5000,
                "counterparty": "+8801719876543",
                "status": "completed",
            }
        ],
    }
    response = client.post("/analyze-ticket", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["ticket_id"] == "TKT-001"
    assert body["relevant_transaction_id"] == "TXN-9101"
    assert body["evidence_verdict"] == "consistent"
    assert body["case_type"] == "wrong_transfer"
    assert body["department"] == "dispute_resolution"
    assert body["human_review_required"] is True
    assert "will refund" not in body["customer_reply"].lower()


def test_phishing_safety():
    payload = {
        "ticket_id": "TKT-002",
        "complaint": "A fake support person asked for my OTP and PIN.",
        "transaction_history": [],
    }
    response = client.post("/analyze-ticket", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["case_type"] == "phishing_or_social_engineering"
    assert body["department"] == "fraud_risk"
    assert body["severity"] == "critical"
    assert body["human_review_required"] is True
    assert "do not share" in body["customer_reply"].lower()


def test_duplicate_payment():
    payload = {
        "ticket_id": "TKT-003",
        "complaint": "I paid the merchant 1200 taka but I was charged twice.",
        "transaction_history": [
            {
                "transaction_id": "TXN-2001",
                "timestamp": "2026-04-14T16:01:00Z",
                "type": "payment",
                "amount": 1200,
                "counterparty": "MER-7788",
                "status": "completed",
            },
            {
                "transaction_id": "TXN-2002",
                "timestamp": "2026-04-14T16:01:40Z",
                "type": "payment",
                "amount": 1200,
                "counterparty": "MER-7788",
                "status": "completed",
            },
        ],
    }
    response = client.post("/analyze-ticket", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["case_type"] == "duplicate_payment"
    assert body["evidence_verdict"] == "consistent"
    assert body["department"] == "payments_ops"


def test_blank_complaint_returns_422():
    response = client.post("/analyze-ticket", json={"ticket_id": "TKT-004", "complaint": "   "})
    assert response.status_code == 422
    assert "error" in response.json()
