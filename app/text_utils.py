"""Small text helpers for English, Bangla, and Banglish complaints."""
from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from typing import Iterable

_NUMBER_RE = re.compile(r"(?<![\w.])(?:৳|tk|taka|bdt)?\s*(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:৳|tk|taka|bdt)?(?![\w.])", re.I)
_PHONEISH_RE = re.compile(r"(?:\+?88)?01[3-9]\d{8}")


def normalize_text(text: str | None) -> str:
    if not text:
        return ""
    normalized = text.lower()
    normalized = normalized.replace("–", "-").replace("—", "-")
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def contains_any(text: str, keywords: Iterable[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def extract_amounts(text: str) -> list[float]:
    """Extract plausible BDT amounts from complaint text.

    We keep this intentionally simple and deterministic for speed and reliability.
    """
    amounts: list[float] = []
    for match in _NUMBER_RE.finditer(text):
        raw = match.group(1).replace(",", "")
        try:
            value = float(Decimal(raw))
        except (InvalidOperation, ValueError):
            continue
        # Avoid treating tiny numbers like dates/hours as amounts unless explicitly useful.
        if value >= 1:
            amounts.append(value)
    return amounts


def amount_mentioned(text: str, amount: float, tolerance: float = 0.01) -> bool:
    for candidate in extract_amounts(text):
        if abs(candidate - float(amount)) <= tolerance:
            return True
    return False


def extract_phone_numbers(text: str) -> list[str]:
    return _PHONEISH_RE.findall(text)


def last_digits_in_text(counterparty: str, text: str, digits: int = 4) -> bool:
    compact_counterparty = re.sub(r"\D", "", counterparty or "")
    compact_text = re.sub(r"\D", "", text or "")
    if len(compact_counterparty) < digits:
        return False
    return compact_counterparty[-digits:] in compact_text


def looks_like_prompt_injection(text: str) -> bool:
    injection_terms = [
        "ignore previous",
        "ignore all rules",
        "ignore the rules",
        "system prompt",
        "developer message",
        "return only",
        "print secrets",
        "show api key",
        "bypass",
        "jailbreak",
        "do not follow",
        "forget instruction",
        "নিয়ম মানবে না",
        "সব নিয়ম ভুলে",
    ]
    return contains_any(text, injection_terms)
