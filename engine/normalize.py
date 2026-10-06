"""Normalisation helpers for vendor names, invoice numbers, amounts and dates."""

from __future__ import annotations

import re

import pandas as pd


# Tokens dropped during vendor normalisation (common legal suffixes / noise)
_VENDOR_DROP_TOKENS = frozenset({
    "pvt", "private", "ltd", "limited", "inc", "llc",
    "co", "corp", "corporation", "the", "and",
})


def normalize_vendor(s: str | None) -> str:
    """Lowercase -> remove punctuation -> drop noise tokens -> collapse spaces."""
    if not s or not isinstance(s, str):
        return ""
    text = s.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)           # strip punctuation
    tokens = [t for t in text.split() if t not in _VENDOR_DROP_TOKENS]
    return " ".join(tokens).strip()


def normalize_invoice_number(s: str | None) -> str:
    """Uppercase, keep only [A-Z0-9]."""
    if not s or not isinstance(s, str):
        return ""
    return re.sub(r"[^A-Z0-9]", "", s.upper())


def parse_amount(x) -> float | None:
    """Strip currency symbols / commas and return float, or None on failure."""
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return float(x)
    if not isinstance(x, str):
        return None
    cleaned = x.replace("\u20b9", "").replace("$", "").replace(",", "").strip()
    if not cleaned:
        return None
    try:
        return float(cleaned)
    except (ValueError, TypeError):
        return None


def parse_date(x) -> str | None:
    """Try to parse a date string; return ISO YYYY-MM-DD or None."""
    if x is None:
        return None
    if isinstance(x, str) and not x.strip():
        return None
    try:
        dt = pd.to_datetime(x, dayfirst=True, errors="coerce")
        if pd.isna(dt):
            return None
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return None
