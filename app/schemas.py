"""Pydantic schemas for QueueStorm Investigator.

The enum values are intentionally strict because the preliminary judge scores exact
field names, field types, and enum spellings.
"""
from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

Language = Literal["en", "bn", "mixed"]
Channel = Literal["in_app_chat", "call_center", "email", "merchant_portal", "field_agent"]
UserType = Literal["customer", "merchant", "agent", "unknown"]

TransactionType = Literal["transfer", "payment", "cash_in", "cash_out", "settlement", "refund"]
TransactionStatus = Literal["completed", "failed", "pending", "reversed"]

EvidenceVerdict = Literal["consistent", "inconsistent", "insufficient_data"]
CaseType = Literal[
    "wrong_transfer",
    "payment_failed",
    "refund_request",
    "duplicate_payment",
    "merchant_settlement_delay",
    "agent_cash_in_issue",
    "phishing_or_social_engineering",
    "other",
]
Severity = Literal["low", "medium", "high", "critical"]
Department = Literal[
    "customer_support",
    "dispute_resolution",
    "payments_ops",
    "merchant_operations",
    "agent_operations",
    "fraud_risk",
]


class TransactionEntry(BaseModel):
    """One transaction from the provided transaction history."""

    model_config = ConfigDict(extra="ignore")

    transaction_id: str = Field(min_length=1)
    timestamp: str = Field(min_length=1, description="ISO 8601 timestamp string")
    type: TransactionType
    amount: float = Field(ge=0)
    counterparty: str = ""
    status: TransactionStatus

    @field_validator("transaction_id", "timestamp", "counterparty", mode="before")
    @classmethod
    def strip_text(cls, value: Any) -> Any:
        if isinstance(value, str):
            return value.strip()
        return value


class AnalyzeTicketRequest(BaseModel):
    """Input schema for POST /analyze-ticket."""

    model_config = ConfigDict(extra="ignore")

    ticket_id: str = Field(min_length=1)
    complaint: str = Field(min_length=1)
    language: Optional[Language] = None
    channel: Optional[Channel] = None
    user_type: Optional[UserType] = None
    campaign_context: Optional[str] = None
    transaction_history: list[TransactionEntry] = Field(default_factory=list)
    metadata: Optional[dict[str, Any]] = None

    @field_validator("ticket_id", "complaint", mode="before")
    @classmethod
    def strip_required_text(cls, value: Any) -> Any:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("complaint")
    @classmethod
    def complaint_must_not_be_blank(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("complaint must not be empty")
        return value


class AnalyzeTicketResponse(BaseModel):
    """Required output schema for POST /analyze-ticket."""

    ticket_id: str
    relevant_transaction_id: Optional[str]
    evidence_verdict: EvidenceVerdict
    case_type: CaseType
    severity: Severity
    department: Department
    agent_summary: str
    recommended_next_action: str
    customer_reply: str
    human_review_required: bool
    confidence: float = Field(ge=0, le=1)
    reason_codes: list[str] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    error: str
