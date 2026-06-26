"""Core QueueStorm Investigator orchestration."""
from __future__ import annotations

from app.matcher import evidence_verdict, match_transaction
from app.safety import build_agent_summary, build_customer_reply, build_next_action, make_safe_response
from app.schemas import AnalyzeTicketRequest, AnalyzeTicketResponse
from app.taxonomy import classify_case, determine_severity, estimate_amount, needs_human_review, route_department
from app.text_utils import looks_like_prompt_injection, normalize_text


def analyze_ticket(payload: AnalyzeTicketRequest) -> AnalyzeTicketResponse:
    complaint = payload.complaint.strip()
    normalized = normalize_text(complaint)
    reason_codes: list[str] = []

    if looks_like_prompt_injection(normalized):
        reason_codes.append("prompt_injection_ignored")

    case_type = classify_case(complaint, user_type=payload.user_type, channel=payload.channel)
    reason_codes.append(case_type)

    match = match_transaction(complaint, case_type, payload.transaction_history)
    txn = match.transaction
    reason_codes.extend(match.reason_codes)

    verdict = evidence_verdict(case_type, txn, payload.transaction_history)
    reason_codes.append(verdict)

    amount = estimate_amount(complaint, txn)
    severity = determine_severity(case_type, verdict, amount)
    department = route_department(case_type, verdict, amount)
    human_review_required = needs_human_review(case_type, verdict, severity, amount, txn is not None)

    confidence = estimate_confidence(
        case_type=case_type,
        verdict=verdict,
        match_score=match.score,
        transaction_found=txn is not None,
        transaction_count=len(payload.transaction_history),
    )

    response = AnalyzeTicketResponse(
        ticket_id=payload.ticket_id,
        relevant_transaction_id=txn.transaction_id if txn else None,
        evidence_verdict=verdict,
        case_type=case_type,
        severity=severity,
        department=department,
        agent_summary=build_agent_summary(complaint, case_type, verdict, txn),
        recommended_next_action=build_next_action(case_type, verdict, txn),
        customer_reply=build_customer_reply(case_type, verdict, txn),
        human_review_required=human_review_required,
        confidence=confidence,
        reason_codes=list(dict.fromkeys(reason_codes)),
    )
    return make_safe_response(response)


def estimate_confidence(
    case_type: str,
    verdict: str,
    match_score: int,
    transaction_found: bool,
    transaction_count: int,
) -> float:
    if case_type == "phishing_or_social_engineering":
        return 0.88

    if not transaction_found:
        return 0.45 if transaction_count else 0.35

    score_based = min(0.95, 0.50 + (match_score / 200))

    if verdict == "consistent":
        return round(max(score_based, 0.72), 2)
    if verdict == "inconsistent":
        return round(max(score_based - 0.05, 0.65), 2)
    return round(min(score_based, 0.68), 2)
