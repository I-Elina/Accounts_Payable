#!/usr/bin/env python3
"""Contract validation script.

Validates that all JSON payloads in contracts/examples/ adhere strictly to:
- contracts/labels.json enums
- Canonical field schemas specified in contracts/CONTRACT.md (§5, §6, §8)

Usage:
  python scripts/validate_contracts.py
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def validate_contracts(contracts_dir: str = "contracts") -> tuple[bool, list[str]]:
    """Validate all contract examples against labels and schema rules."""
    p_contracts = Path(contracts_dir)
    labels_file = p_contracts / "labels.json"
    examples_dir = p_contracts / "examples"

    errors: list[str] = []

    if not labels_file.exists():
        return False, ["contracts/labels.json is missing!"]

    with open(labels_file, "r", encoding="utf-8") as f:
        labels = json.load(f)

    # Required enums from CONTRACT.md
    valid_decisions = set(labels["decision"].keys())
    valid_exception_types = set(labels["exception_type"].keys())
    valid_review_statuses = set(labels["review_status"].keys())
    valid_suggested_actions = set(labels["suggested_action"].keys())
    valid_event_types = set(labels["event_type"].keys())

    # 1. Validate engine_output.json
    p_engine = examples_dir / "engine_output.json"
    if p_engine.exists():
        with open(p_engine, "r", encoding="utf-8") as f:
            data = json.load(f)
        for req in ["summary", "warnings", "results"]:
            if req not in data:
                errors.append(f"engine_output.json missing root key: {req}")
        for res in data.get("results", []):
            if res.get("decision") not in valid_decisions:
                errors.append(f"engine_output.json invalid decision: {res.get('decision')}")
            if res.get("exception_type") not in valid_exception_types:
                errors.append(f"engine_output.json invalid exception_type: {res.get('exception_type')}")
    else:
        errors.append("contracts/examples/engine_output.json missing")

    # 2. Validate upload_response.json
    p_upload = examples_dir / "upload_response.json"
    if p_upload.exists():
        with open(p_upload, "r", encoding="utf-8") as f:
            data = json.load(f)
        for req in ["upload_id", "filename", "summary", "warnings"]:
            if req not in data:
                errors.append(f"upload_response.json missing root key: {req}")

    # 3. Validate invoice_list.json
    p_list = examples_dir / "invoice_list.json"
    if p_list.exists():
        with open(p_list, "r", encoding="utf-8") as f:
            data = json.load(f)
        for req in ["items", "total", "page", "page_size"]:
            if req not in data:
                errors.append(f"invoice_list.json missing root key: {req}")
        for item in data.get("items", []):
            if item.get("decision") not in valid_decisions:
                errors.append(f"invoice_list.json invalid decision: {item.get('decision')}")
            if item.get("review_status") not in valid_review_statuses:
                errors.append(f"invoice_list.json invalid review_status: {item.get('review_status')}")

    # 4. Validate invoice_detail.json
    p_detail = examples_dir / "invoice_detail.json"
    if p_detail.exists():
        with open(p_detail, "r", encoding="utf-8") as f:
            data = json.load(f)
        for req in ["invoice", "decision", "reviews"]:
            if req not in data:
                errors.append(f"invoice_detail.json missing root key: {req}")
        dec = data.get("decision", {})
        if dec.get("decision") not in valid_decisions:
            errors.append(f"invoice_detail.json invalid decision: {dec.get('decision')}")
        if dec.get("review_status") not in valid_review_statuses:
            errors.append(f"invoice_detail.json invalid review_status: {dec.get('review_status')}")
        if dec.get("ai_suggested_action") and dec.get("ai_suggested_action") not in valid_suggested_actions:
            errors.append(f"invoice_detail.json invalid ai_suggested_action: {dec.get('ai_suggested_action')}")

    # 5. Validate stats.json
    p_stats = examples_dir / "stats.json"
    if p_stats.exists():
        with open(p_stats, "r", encoding="utf-8") as f:
            data = json.load(f)
        for req in ["total", "by_decision", "auto_pass_rate", "pending_reviews", "by_exception_type", "confidence_histogram"]:
            if req not in data:
                errors.append(f"stats.json missing root key: {req}")

    # 6. Validate audit.json
    p_audit = examples_dir / "audit.json"
    if p_audit.exists():
        with open(p_audit, "r", encoding="utf-8") as f:
            data = json.load(f)
        items = data.get("items", []) if isinstance(data, dict) and "items" in data else data
        for ev in items:
            if ev.get("event_type") not in valid_event_types:
                errors.append(f"audit.json invalid event_type: {ev.get('event_type')}")

    # 7. Validate chat.json
    p_chat = examples_dir / "chat.json"
    if p_chat.exists():
        with open(p_chat, "r", encoding="utf-8") as f:
            data = json.load(f)
        for req in ["reply", "cards"]:
            if req not in data:
                errors.append(f"chat.json missing root key: {req}")
        for card in data.get("cards", []):
            if card.get("type") not in ["invoice", "stats", "report"]:
                errors.append(f"chat.json invalid card type: {card.get('type')}")
        prop = data.get("proposal")
        if prop:
            if prop.get("type") != "review_proposal":
                errors.append(f"chat.json invalid proposal type: {prop.get('type')}")
            if prop.get("action") not in ["approve", "reject"]:
                errors.append(f"chat.json invalid proposal action: {prop.get('action')}")

    # 8. Validate config.json
    p_cfg = examples_dir / "config.json"
    if p_cfg.exists():
        with open(p_cfg, "r", encoding="utf-8") as f:
            data = json.load(f)
        for req in ["auto_pass_threshold", "exception_below", "policy_limit", "rules"]:
            if req not in data:
                errors.append(f"config.json missing root key: {req}")

    # 9. Validate report_sample.csv columns
    p_rep = examples_dir / "report_sample.csv"
    if p_rep.exists():
        with open(p_rep, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, [])
            expected_header = [
                "invoice_id", "invoice_number", "vendor_name", "invoice_date",
                "total_amount", "currency", "decision", "confidence",
                "exception_type", "primary_reason", "matched_record", "review_status"
            ]
            if header != expected_header:
                errors.append(f"report_sample.csv header mismatch. Expected {expected_header}, got {header}")

    is_valid = len(errors) == 0
    return is_valid, errors


def main():
    print("Validating contracts and canonical examples...")
    is_valid, errors = validate_contracts()
    if is_valid:
        print("All contract examples and labels match specifications character-for-character!")
        sys.exit(0)
    else:
        print(f"Contract validation FAILED with {len(errors)} error(s):")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)


if __name__ == "__main__":
    main()
