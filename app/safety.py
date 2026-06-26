"""Fintech safety templates and output guardrails."""
from __future__ import annotations

import re

from app.schemas import AnalyzeTicketResponse, CaseType, TransactionEntry

_CREDENTIAL_TERMS = r"(?:pin|otp|o\.t\.p|password|passcode|verification code|secret code|full card number|cvv|ওটিপি|পিন|পাসওয়ার্ড|পাসওয়ার্ড)"
_REQUEST_PATTERNS = [
    re.compile(rf"(?:please|kindly)?\s*(?:share|send|provide|tell|give|submit|enter)\s+(?:your\s+)?{_CREDENTIAL_TERMS}", re.I),
    re.compile(rf"{_CREDENTIAL_TERMS}\s+(?:share|send|provide|tell|give|submit|enter)\s*(?:করুন|করেন)?", re.I),
]
_PROMISE_PATTERNS = [
    re.compile(r"\bwe\s+will\s+(?:refund|reverse|recover|unblock)\b", re.I),
    re.compile(r"\byour\s+(?:money|amount|account)\s+will\s+be\s+(?:refunded|reversed|recovered|unblocked)\b", re.I),
    re.compile(r"\brefund\s+(?:is|has been)\s+confirmed\b", re.I),
    re.compile(r"\breversal\s+(?:is|has been)\s+confirmed\b", re.I),
]


def _is_negated_warning(text: str, start: int) -> bool:
    window = text[max(0, start - 30) : start].lower()
    return any(negation in window for negation in ["do not", "don't", "never", "must not", "avoid", "কখনো", "দিবেন না", "শেয়ার করবেন না"])


def contains_credential_request(text: str) -> bool:
    for pattern in _REQUEST_PATTERNS:
        for match in pattern.finditer(text or ""):
            if not _is_negated_warning(text, match.start()):
                return True
    return False


def contains_unauthorized_promise(text: str) -> bool:
    return any(pattern.search(text or "") for pattern in _PROMISE_PATTERNS)


def build_agent_summary(
    complaint: str,
    case_type: CaseType,
    verdict: str,
    txn: TransactionEntry | None,
) -> str:
    reference = f"Transaction {txn.transaction_id}" if txn else "No matching transaction"
    amount_text = f" for {txn.amount:g} BDT" if txn else ""
    status_text = f" with status {txn.status}" if txn else " in the provided history"
    complaint_preview = complaint.strip()
    if len(complaint_preview) > 120:
        complaint_preview = complaint_preview[:117].rstrip() + "..."

    return (
        f"{reference}{amount_text}{status_text}; classified as {case_type}. "
        f"Evidence verdict is {verdict}. Customer said: {complaint_preview}"
    )


def build_next_action(case_type: CaseType, verdict: str, txn: TransactionEntry | None) -> str:
    txn_ref = f"transaction {txn.transaction_id}" if txn else "the customer's account history"

    if case_type == "phishing_or_social_engineering":
        return (
            "Escalate to fraud_risk, record the suspicious contact details if provided, "
            "and remind the customer to use official support channels only."
        )

    if verdict == "inconsistent":
        return (
            f"Review {txn_ref} manually and explain that the available transaction history does not fully support "
            "the complaint. Do not confirm any financial action without authorized verification."
        )

    if verdict == "insufficient_data":
        return (
            f"Request a human support review and verify {txn_ref} through official internal records. "
            "Do not ask for PIN, OTP, password, or other secret credentials."
        )

    if case_type == "wrong_transfer":
        return (
            f"Verify {txn_ref}, confirm the recipient identifier through safe non-secret details, "
            "and route the dispute for human review."
        )

    if case_type == "payment_failed":
        return (
            f"Check payment status and ledger movement for {txn_ref}; if eligible, process through official channels."
        )

    if case_type == "duplicate_payment":
        return (
            f"Compare duplicate transaction records around {txn_ref} and send to payments_ops for verification."
        )

    if case_type == "merchant_settlement_delay":
        return (
            f"Check merchant settlement status for {txn_ref} and route to merchant_operations for SLA verification."
        )

    if case_type == "agent_cash_in_issue":
        return (
            f"Check agent cash-in status for {txn_ref} and route to agent_operations for reconciliation."
        )

    return f"Review {txn_ref} and respond through the standard support workflow."


def build_customer_reply(case_type: CaseType, verdict: str, txn: TransactionEntry | None, language: str = "en") -> str:
    txn_ref = f" transaction {txn.transaction_id}" if txn else " your concern"
    txn_ref_bn = f" লেনদেন {txn.transaction_id}" if txn else " আপনার অভিযোগ"

    if language == "bn":
        if case_type == "phishing_or_social_engineering":
            return (
                "আমরা আপনার রিপোর্টটি রেকর্ড করেছি। অনুগ্রহ করে কারো সাথে আপনার পিন, ওটিপি, পাসওয়ার্ড, ভেরিফিকেশন কোড, "
                "বা অ্যাকাউন্টের বিবরণ শেয়ার করবেন না। যেকোনো সহযোগিতার জন্য শুধুমাত্র অফিসিয়াল সাপোর্ট চ্যানেল ব্যবহার করুন।"
            )
        if verdict == "inconsistent":
            return (
                f"আমরা{txn_ref_bn} এর বিষয়ে আপনার অভিযোগ পেয়েছি। উপলব্ধ রেকর্ডের ভিত্তিতে, বিবরণগুলো "
                "আমাদের সাপোর্ট টিম দ্বারা আরও যাচাই করা প্রয়োজন। যেকোনো যোগ্য পদক্ষেপ শুধুমাত্র অফিসিয়াল চ্যানেলের মাধ্যমে প্রক্রিয়া করা হবে।"
            )
        if verdict == "insufficient_data":
            return (
                f"আমরা{txn_ref_bn} রেকর্ড করেছি। আমাদের সাপোর্ট টিম অফিসিয়াল রেকর্ডের মাধ্যমে বিবরণগুলো যাচাই করবে। "
                "অনুগ্রহ করে কারো সাথে আপনার পিন, ওটিপি, পাসওয়ার্ড, বা ভেরিফিকেশন কোড শেয়ার করবেন না।"
            )
        
        # Consistent / default cases
        if case_type == "agent_cash_in_issue":
            return (
                f"আপনার{txn_ref_bn} এর বিষয়ে আমরা অবগত হয়েছি। আমাদের এজেন্ট অপারেশন্স দল এটি দ্রুত যাচাই করবে এবং "
                "অফিসিয়াল চ্যানেলে আপনাকে জানাবে। অনুগ্রহ করে কারো সাথে আপনার পিন বা ওটিপি শেয়ার করবেন না।"
            )
        return (
            f"আমরা{txn_ref_bn} এর বিষয়ে অবগত হয়েছি। আমাদের সাপোর্ট টিম লেনদেনের বিবরণ যাচাই করবে। "
            "যদি কোনো পরিমাণ অর্থ পাওয়ার যোগ্য হয়, তা অফিসিয়াল চ্যানেলের মাধ্যমে প্রক্রিয়া করা হবে। অনুগ্রহ করে পিন বা ওটিপি শেয়ার করবেন না।"
        )

    if case_type == "phishing_or_social_engineering":
        return (
            "We have noted your report. Please do not share your PIN, OTP, password, verification code, "
            "or account credentials with anyone. Use only official support channels for further assistance."
        )

    if verdict == "inconsistent":
        return (
            f"We have noted your concern about{txn_ref}. Based on the available records, the details need "
            "further verification by our support team. Any eligible action will be processed only through official channels."
        )

    if verdict == "insufficient_data":
        return (
            f"We have recorded{txn_ref}. Our support team will verify the details through official records. "
            "Please do not share your PIN, OTP, password, or verification code with anyone."
        )

    return (
        f"We have noted your concern about{txn_ref}. Our support team will verify the transaction details. "
        "If any amount is found eligible, it will be processed through official channels."
    )


def make_safe_response(response: AnalyzeTicketResponse) -> AnalyzeTicketResponse:
    """Final guardrail before returning to the judge.

    This keeps output safe even if future edits introduce unsafe templates.
    """
    combined = f"{response.customer_reply} {response.recommended_next_action}"
    reason_codes = list(response.reason_codes)

    if contains_credential_request(combined):
        response.customer_reply = (
            "We have recorded your concern. Our support team will verify the details through official records. "
            "Please do not share your PIN, OTP, password, verification code, or account credentials with anyone."
        )
        response.recommended_next_action = (
            "Escalate for human review and verify only through official internal records without requesting secret credentials."
        )
        response.human_review_required = True
        reason_codes.append("credential_request_blocked")

    if contains_unauthorized_promise(combined):
        response.customer_reply = (
            "We have recorded your concern. Our support team will verify the details through official records. "
            "If any amount is found eligible, it will be processed through official channels."
        )
        response.recommended_next_action = (
            "Verify eligibility through official internal records before any financial action is taken."
        )
        response.human_review_required = True
        reason_codes.append("unauthorized_promise_blocked")

    response.reason_codes = list(dict.fromkeys(reason_codes))
    return response
