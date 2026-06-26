"""Case classification, routing, and severity rules."""
from __future__ import annotations

from app.schemas import CaseType, Department, Severity, TransactionEntry
from app.text_utils import contains_any, extract_amounts, normalize_text

PHISHING_KEYWORDS = [
    "otp",
    "o.t.p",
    "pin",
    "password",
    "passcode",
    "verification code",
    "secret code",
    "secret credential",
    "credential",
    "cvv",
    "full card number",
    "scam",
    "fraud",
    "fake call",
    "fake sms",
    "suspicious call",
    "suspicious sms",
    "bkash officer",
    "agent called",
    "prize",
    "lottery",
    "account block",
    "account unlock",
    "ওটিপি",
    "ও টি পি",
    "পিন",
    "পাসওয়ার্ড",
    "পাসওয়ার্ড",
    "ভেরিফিকেশন কোড",
    "গোপন নম্বর",
    "প্রতারক",
    "প্রতারণা",
]

WRONG_TRANSFER_KEYWORDS = [
    "wrong number",
    "wrong recipient",
    "wrong person",
    "mistakenly sent",
    "sent by mistake",
    "sent to wrong",
    "vul number",
    "bhul number",
    "ভুল নম্বর",
    "ভুল নাম্বার",
    "ভুলে পাঠিয়েছি",
    "ভুলে পাঠিয়েছি",
    "ভুল ব্যক্তিকে",
    "didn't get",
    "did not get",
    "didn't receive",
    "did not receive",
    "not received",
    "পায়নি",
    "পায়নি",
    "পায় নাই",
    "পায় নাই",
]

PAYMENT_FAILED_KEYWORDS = [
    "payment failed",
    "transaction failed",
    "failed but deducted",
    "failed but balance",
    "money deducted",
    "balance deducted",
    "amount deducted",
    "tk deducted",
    "taka deducted",
    "টাকা কাটা",
    "টাকা কেটে",
    "ব্যর্থ",
    "ফেইল",
    "ফেল",
    "failed",
    "failure",
    "error",
    "deducted",
    "deduct",
    "কেটেছে",
    "কেটে নিলো",
]

DUPLICATE_PAYMENT_KEYWORDS = [
    "duplicate",
    "twice",
    "two times",
    "double charged",
    "charged twice",
    "same payment",
    "দুইবার",
    "২ বার",
    "ডাবল",
]

MERCHANT_SETTLEMENT_KEYWORDS = [
    "settlement",
    "merchant settlement",
    "settled",
    "merchant portal",
    "merchant payment not received",
    "মার্চেন্ট",
    "সেটেলমেন্ট",
]

AGENT_CASH_IN_KEYWORDS = [
    "cash in",
    "cash-in",
    "cashin",
    "agent cash",
    "agent deposit",
    "agent gave",
    "agent took",
    "এজেন্ট",
    "ক্যাশ ইন",
    "ক্যাশইন",
    "জমা",
]

REFUND_KEYWORDS = [
    "refund",
    "return my money",
    "money back",
    "give back",
    "reversal",
    "reverse the transaction",
    "ফেরত",
    "রিফান্ড",
]

DEPARTMENT_BY_CASE: dict[CaseType, Department] = {
    "wrong_transfer": "dispute_resolution",
    "payment_failed": "payments_ops",
    "refund_request": "customer_support",
    "duplicate_payment": "payments_ops",
    "merchant_settlement_delay": "merchant_operations",
    "agent_cash_in_issue": "agent_operations",
    "phishing_or_social_engineering": "fraud_risk",
    "other": "customer_support",
}


def classify_case(complaint: str, user_type: str | None = None, channel: str | None = None) -> CaseType:
    text = normalize_text(complaint)

    # Safety/scam classification must win over ordinary refund/payment requests.
    if contains_any(text, PHISHING_KEYWORDS):
        return "phishing_or_social_engineering"

    if contains_any(text, DUPLICATE_PAYMENT_KEYWORDS):
        return "duplicate_payment"

    if contains_any(text, MERCHANT_SETTLEMENT_KEYWORDS) or user_type == "merchant" or channel == "merchant_portal":
        return "merchant_settlement_delay"

    if contains_any(text, AGENT_CASH_IN_KEYWORDS) or user_type == "agent" or channel == "field_agent":
        return "agent_cash_in_issue"

    if contains_any(text, WRONG_TRANSFER_KEYWORDS):
        return "wrong_transfer"

    if contains_any(text, PAYMENT_FAILED_KEYWORDS):
        return "payment_failed"

    if contains_any(text, REFUND_KEYWORDS):
        return "refund_request"

    return "other"


def route_department(case_type: CaseType, verdict: str, amount: float | None = None) -> Department:
    if case_type == "refund_request" and (verdict in {"inconsistent", "insufficient_data"} or (amount or 0) >= 10000):
        return "dispute_resolution"
    return DEPARTMENT_BY_CASE[case_type]


def estimate_amount(complaint: str, txn: TransactionEntry | None = None) -> float | None:
    if txn is not None:
        return float(txn.amount)
    amounts = extract_amounts(normalize_text(complaint))
    # Pick the highest mentioned number as the likely amount. This avoids selecting dates/hours when
    # the complaint says "around 2pm, 5000 taka".
    return max(amounts) if amounts else None


def determine_severity(case_type: CaseType, verdict: str, amount: float | None) -> Severity:
    value = float(amount or 0)

    if case_type == "phishing_or_social_engineering":
        return "critical"

    if value >= 50000:
        return "critical"

    if case_type == "wrong_transfer":
        return "high" if value >= 5000 else "medium"

    if case_type in {"payment_failed", "duplicate_payment", "agent_cash_in_issue"}:
        return "high"

    if case_type == "merchant_settlement_delay":
        return "medium"

    if case_type == "refund_request":
        return "low"

    return "low"


def needs_human_review(case_type: CaseType, verdict: str, severity: Severity, amount: float | None, relevant_txn_found: bool) -> bool:
    if case_type in {
        "wrong_transfer",
        "duplicate_payment",
        "merchant_settlement_delay",
        "agent_cash_in_issue",
        "phishing_or_social_engineering",
    }:
        return True

    if verdict in {"inconsistent", "insufficient_data"} and case_type != "other":
        return True

    if severity in {"high", "critical"}:
        return True

    if (amount or 0) >= 10000:
        return True

    if not relevant_txn_found and case_type in {"payment_failed", "refund_request"}:
        return True

    return False
