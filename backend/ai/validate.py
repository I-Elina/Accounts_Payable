import re
from typing import Any

VALID_ACTIONS = {"approve", "reject", "investigate", "contact_vendor"}
INVOICE_ID_PATTERN = re.compile(r"\b[A-Z]{2,5}-\d{2,}\b")


def validate_summary(output: dict[str, Any], record: dict[str, Any]) -> bool:
    """Validate AI summary adherence to strict factual consistency and format limits.

    Returns True if valid, False otherwise.
    """
    if not isinstance(output, dict):
        return False

    summary = output.get("summary")
    suggested_action = output.get("suggested_action")
    referenced_rule_ids = output.get("referenced_rule_ids")

    if not summary or not isinstance(summary, str):
        return False
    if len(summary) > 600:
        return False

    # Sentence count check (split by punctuation followed by space or end)
    sentences = [s.strip() for s in re.split(r"[.!?]+(?:\s+|$)", summary) if s.strip()]
    if len(sentences) > 3:
        return False

    if suggested_action not in VALID_ACTIONS:
        return False

    if not isinstance(referenced_rule_ids, list):
        return False

    # Valid invoice IDs in record
    allowed_ids = set()
    if record.get("invoice_id"):
        allowed_ids.add(record["invoice_id"])
    if record.get("matched_record"):
        allowed_ids.add(record["matched_record"])
    if record.get("record", {}).get("invoice_id"):
        allowed_ids.add(record["record"]["invoice_id"])

    found_ids = INVOICE_ID_PATTERN.findall(summary)
    for fid in found_ids:
        if fid not in allowed_ids:
            return False

    # Valid rule IDs
    violations = record.get("violations", [])
    valid_rules = {v.get("rule_id") for v in violations if isinstance(v, dict)}
    for rid in referenced_rule_ids:
        if rid not in valid_rules:
            return False

    return True
