"""Transaction matching and evidence verdict logic."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from app.schemas import CaseType, EvidenceVerdict, TransactionEntry
from app.taxonomy import (
    AGENT_CASH_IN_KEYWORDS,
    DUPLICATE_PAYMENT_KEYWORDS,
    MERCHANT_SETTLEMENT_KEYWORDS,
    PAYMENT_FAILED_KEYWORDS,
    REFUND_KEYWORDS,
    WRONG_TRANSFER_KEYWORDS,
)
from app.text_utils import amount_mentioned, contains_any, last_digits_in_text, normalize_text


@dataclass(frozen=True)
class MatchResult:
    transaction: TransactionEntry | None
    score: int
    reason_codes: list[str]


CASE_TYPE_TO_TRANSACTION_TYPES: dict[CaseType, set[str]] = {
    "wrong_transfer": {"transfer"},
    "payment_failed": {"payment", "transfer", "cash_out"},
    "refund_request": {"payment", "transfer", "cash_out", "refund"},
    "duplicate_payment": {"payment", "transfer"},
    "merchant_settlement_delay": {"settlement", "payment"},
    "agent_cash_in_issue": {"cash_in"},
    "phishing_or_social_engineering": set(),
    "other": {"transfer", "payment", "cash_in", "cash_out", "settlement", "refund"},
}

CASE_KEYWORDS: dict[CaseType, list[str]] = {
    "wrong_transfer": WRONG_TRANSFER_KEYWORDS,
    "payment_failed": PAYMENT_FAILED_KEYWORDS,
    "refund_request": REFUND_KEYWORDS,
    "duplicate_payment": DUPLICATE_PAYMENT_KEYWORDS,
    "merchant_settlement_delay": MERCHANT_SETTLEMENT_KEYWORDS,
    "agent_cash_in_issue": AGENT_CASH_IN_KEYWORDS,
    "phishing_or_social_engineering": [],
    "other": [],
}


def find_duplicate_cluster(transactions: list[TransactionEntry]) -> list[TransactionEntry]:
    groups: dict[tuple[str, float, str, str], list[TransactionEntry]] = defaultdict(list)
    for txn in transactions:
        if txn.status != "completed":
            continue
        key = (txn.type, float(txn.amount), normalize_text(txn.counterparty), txn.status)
        groups[key].append(txn)
    duplicates = [items for items in groups.values() if len(items) >= 2]
    if not duplicates:
        return []
    return max(duplicates, key=len)


def match_transaction(complaint: str, case_type: CaseType, transactions: list[TransactionEntry]) -> MatchResult:
    text = normalize_text(complaint)

    if case_type == "phishing_or_social_engineering" or not transactions:
        return MatchResult(None, 0, ["no_transaction_match"] if not transactions else ["safety_case_no_transaction_required"])

    if case_type == "duplicate_payment":
        duplicate_cluster = find_duplicate_cluster(transactions)
        if duplicate_cluster:
            # Return the latest item in the duplicate cluster as the relevant duplicate payment.
            return MatchResult(duplicate_cluster[-1], 90, ["duplicate_pattern", "transaction_match"])

    best_score = -1
    best_reasons: list[str] = []

    expected_types = CASE_TYPE_TO_TRANSACTION_TYPES[case_type]

    scored_txns = []
    for txn in transactions:
        score = 0
        reasons = []

        if normalize_text(txn.transaction_id) and normalize_text(txn.transaction_id) in text:
            score += 120
            reasons.append("transaction_id_mentioned")

        if amount_mentioned(text, txn.amount):
            score += 35
            reasons.append("amount_match")

        if expected_types and txn.type in expected_types:
            score += 25
            reasons.append("type_match")

        if last_digits_in_text(txn.counterparty, text):
            score += 25
            reasons.append("counterparty_match")

        if txn.status in text:
            score += 15
            reasons.append("status_mentioned")

        if contains_any(text, CASE_KEYWORDS.get(case_type, [])) and txn.type in expected_types:
            score += 15
            reasons.append("complaint_intent_match")

        if case_type == "payment_failed" and txn.status in {"failed", "pending"}:
            score += 20
            reasons.append("failure_status_match")

        if case_type == "wrong_transfer" and txn.status == "completed" and txn.type == "transfer":
            score += 15
            reasons.append("completed_transfer_match")

        scored_txns.append((score, txn, reasons))

    if not scored_txns:
        return MatchResult(None, 0, ["no_transaction_match"])

    max_score = max(item[0] for item in scored_txns)

    if max_score < 30:
        return MatchResult(None, max_score, ["no_transaction_match"])

    best_candidates = [item for item in scored_txns if item[0] == max_score]

    if len(best_candidates) > 1:
        # Check if the candidates have distinct counterparties
        import re
        distinct_counterparties = {re.sub(r"\D", "", c[1].counterparty or "") for c in best_candidates}
        if len(distinct_counterparties) > 1:
            return MatchResult(None, max_score, ["ambiguous_match", "no_transaction_match"])

    best_score, best_txn, best_reasons = best_candidates[0]
    clean_reasons = list(dict.fromkeys(best_reasons + ["transaction_match"]))
    return MatchResult(best_txn, best_score, clean_reasons)


def evidence_verdict(case_type: CaseType, txn: TransactionEntry | None, transactions: list[TransactionEntry]) -> EvidenceVerdict:
    if case_type == "phishing_or_social_engineering":
        return "insufficient_data"

    if txn is None:
        return "insufficient_data"

    if case_type == "wrong_transfer":
        if txn.type == "transfer" and txn.status == "completed":
            # Check if there are other completed transfers or payments to the same counterparty in the history.
            import re
            def clean_phone(p):
                return re.sub(r"\D", "", p or "")
            clean_tgt = clean_phone(txn.counterparty)
            if clean_tgt:
                other_txns = [
                    t for t in transactions 
                    if t.transaction_id != txn.transaction_id 
                    and clean_phone(t.counterparty) == clean_tgt
                    and t.status == "completed" 
                    and t.type in {"transfer", "payment"}
                ]
                if len(other_txns) > 0:
                    return "inconsistent"
            return "consistent"
        return "inconsistent"

    if case_type == "payment_failed":
        if txn.status in {"failed", "pending"}:
            return "consistent"
        if txn.status in {"completed", "reversed"}:
            return "inconsistent"
        return "insufficient_data"

    if case_type == "duplicate_payment":
        duplicate_cluster = find_duplicate_cluster(transactions)
        if duplicate_cluster:
            return "consistent"
        # A matched single transaction contradicts a clear duplicate claim more than no data does.
        return "inconsistent"

    if case_type == "merchant_settlement_delay":
        if txn.type == "settlement" and txn.status in {"pending", "failed"}:
            return "consistent"
        if txn.type == "settlement" and txn.status in {"completed", "reversed"}:
            return "inconsistent"
        return "insufficient_data"

    if case_type == "agent_cash_in_issue":
        if txn.type == "cash_in" and txn.status in {"pending", "failed"}:
            return "consistent"
        if txn.type == "cash_in" and txn.status == "completed":
            return "insufficient_data"
        return "inconsistent"

    if case_type == "refund_request":
        # A matching transaction shows what the customer refers to, but refund eligibility is not proven.
        if txn.type == "refund" and txn.status == "completed":
            return "inconsistent"
        return "consistent"

    return "consistent" if txn else "insufficient_data"
