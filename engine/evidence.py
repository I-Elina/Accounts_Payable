"""Derive primary violation, reason, matched record and evidence dict."""

from __future__ import annotations

from engine.schemas import Violation


def _rule_number(rule_id: str) -> int:
    """Extract numeric part of rule ID for tie-breaking (e.g. 'R09' -> 9)."""
    return int(rule_id[1:])


def resolve_primary(violations: list[Violation]) -> tuple[str, str, str | None, dict]:
    """Determine the primary violation from a list.

    Primary = highest penalty; tie -> lowest rule number.

    Returns:
        (exception_type, primary_reason, matched_record, evidence_dict)
    """
    if not violations:
        return "none", "No issues found", None, {}

    # Sort: highest penalty first, then lowest rule number
    primary = sorted(
        violations,
        key=lambda v: (-v.penalty, _rule_number(v.rule_id)),
    )[0]

    # matched_record = first non-null among violations (by rule order)
    matched_record = None
    for v in sorted(violations, key=lambda v: _rule_number(v.rule_id)):
        if v.matched_record:
            matched_record = v.matched_record
            break

    evidence: dict = {}
    if matched_record:
        evidence["matched_invoice_id"] = matched_record

    return primary.exception_type, primary.message, matched_record, evidence
