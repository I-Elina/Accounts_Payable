"""Data classes and helpers for building engine result dicts."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class Violation:
    """A single rule violation found for an invoice."""
    rule_id: str
    name: str
    severity: str          # "hard" | "soft"
    penalty: float
    exception_type: str
    message: str
    matched_record: str | None = None
    evidence: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = asdict(self)
        if d["matched_record"] is None:
            del d["matched_record"]
        return d


# Canonical invoice field names (the only ones included in output `record`)
CANONICAL_FIELDS = [
    "invoice_id", "invoice_number", "vendor_name", "invoice_date",
    "due_date", "currency", "subtotal", "tax_amount", "total_amount",
    "category", "po_number", "description",
]


def build_record(rec: dict) -> dict:
    """Extract only canonical fields from a working record dict."""
    return {k: rec.get(k) for k in CANONICAL_FIELDS}


def build_result(
    rec: dict,
    violations: list[Violation],
    decision: str,
    confidence: float,
    pass_resolved_in: int,
    exception_type: str,
    primary_reason: str,
    matched_record: str | None,
    evidence: dict,
) -> dict:
    """Build a single invoice result dict matching the contract shape."""
    return {
        "invoice_id": rec["invoice_id"],
        "row_index": rec["row_index"],
        "decision": decision,
        "confidence": confidence,
        "pass_resolved_in": pass_resolved_in,
        "exception_type": exception_type,
        "primary_reason": primary_reason,
        "matched_record": matched_record,
        "violations": [v.to_dict() for v in violations],
        "evidence": evidence,
        "record": build_record(rec),
    }
