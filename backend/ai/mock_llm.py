from typing import Any


def mock_generate_summary(decision_record: dict[str, Any]) -> dict[str, Any]:
    """Generate deterministic template-based AI explanation from decision record."""
    exc_type = decision_record.get("exception_type", "none")
    primary_reason = decision_record.get("primary_reason", "No issues detected.")
    inv_id = decision_record.get("invoice_id") or decision_record.get("record", {}).get("invoice_id", "")
    matched = decision_record.get("matched_record")
    violations = decision_record.get("violations", [])

    rule_ids = [v["rule_id"] for v in violations if isinstance(v, dict) and "rule_id" in v]

    # Map suggested action
    if exc_type in ("exact_duplicate", "fuzzy_duplicate"):
        action = "investigate"
        if matched:
            text = f"Invoice {inv_id} appears to duplicate {matched}. {primary_reason}. Please verify with the vendor before proceeding."
        else:
            text = f"Invoice {inv_id} was flagged as a potential duplicate. {primary_reason}. Review prior submissions."
    elif exc_type in ("missing_field", "invalid_amount", "invalid_date", "calculation_mismatch", "future_date"):
        action = "contact_vendor"
        text = f"Invoice {inv_id} has data discrepancies: {primary_reason}. Contact the supplier to request a corrected invoice."
    elif exc_type in ("policy_limit", "amount_outlier", "unknown_vendor"):
        action = "investigate"
        text = f"Invoice {inv_id} requires supervisor investigation: {primary_reason}. Verify approvals and contract terms."
    else:
        action = "approve"
        text = f"Invoice {inv_id} passed all automated validation checks without exceptions. Ready for approval."

    return {
        "summary": text,
        "suggested_action": action,
        "referenced_rule_ids": rule_ids,
    }
