"""Contract tests: Validates that all canonical example payloads match schemas and enums."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
EXAMPLES_DIR = ROOT / "contracts" / "examples"


def test_contracts_labels_completeness(labels_dict):
    """Ensure all required enum categories exist in labels.json."""
    required_keys = ["decision", "exception_type", "review_status", "suggested_action", "event_type"]
    for k in required_keys:
        assert k in labels_dict, f"Missing category '{k}' in contracts/labels.json"

    # Specific mandatory values
    assert "auto_pass" in labels_dict["decision"]
    assert "needs_review" in labels_dict["decision"]
    assert "exception" in labels_dict["decision"]

    assert "fuzzy_duplicate" in labels_dict["exception_type"]
    assert "exact_duplicate" in labels_dict["exception_type"]
    assert "policy_limit" in labels_dict["exception_type"]

    assert "UPLOAD_RECEIVED" in labels_dict["event_type"]
    assert "REVIEW_APPROVED" in labels_dict["event_type"]


def test_engine_output_example(labels_dict):
    """Verify engine_output.json shape and enums."""
    path = EXAMPLES_DIR / "engine_output.json"
    assert path.exists(), "engine_output.json is missing"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "summary" in data
    assert "warnings" in data
    assert "results" in data

    for res in data["results"]:
        assert res["decision"] in labels_dict["decision"]
        assert res["exception_type"] in labels_dict["exception_type"]
        assert 0.0 <= res["confidence"] <= 1.0
        assert res["pass_resolved_in"] in (1, 2)
        rec = res["record"]
        assert "invoice_id" in rec
        assert "total_amount" in rec


def test_invoice_detail_example(labels_dict):
    """Verify invoice_detail.json matches canonical structure."""
    path = EXAMPLES_DIR / "invoice_detail.json"
    assert path.exists(), "invoice_detail.json is missing"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "invoice" in data
    assert "decision" in data
    assert "reviews" in data

    inv = data["invoice"]
    dec = data["decision"]
    assert inv["invoice_id"] == "INV-1042"
    assert dec["decision"] in labels_dict["decision"]
    assert dec["review_status"] in labels_dict["review_status"]
    if dec.get("ai_suggested_action"):
        assert dec["ai_suggested_action"] in labels_dict["suggested_action"]


def test_chat_example(labels_dict):
    """Verify chat.json response has cards, proposal, and correct shapes."""
    path = EXAMPLES_DIR / "chat.json"
    assert path.exists(), "chat.json is missing"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "reply" in data
    assert "cards" in data
    assert len(data["cards"]) <= 5, "Chat response must return at most 5 cards"

    for card in data["cards"]:
        assert card["type"] in ["invoice", "stats", "report"]
        if card["type"] == "invoice":
            assert card["decision"] in labels_dict["decision"]
            assert card["review_status"] in labels_dict["review_status"]

    prop = data.get("proposal")
    if prop:
        assert prop["type"] == "review_proposal"
        assert prop["action"] in ["approve", "reject"]
        assert "invoice_id" in prop


def test_report_sample_csv():
    """Verify report_sample.csv columns match contract §8."""
    path = EXAMPLES_DIR / "report_sample.csv"
    assert path.exists(), "report_sample.csv is missing"
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, [])

    expected = [
        "invoice_id", "invoice_number", "vendor_name", "invoice_date",
        "total_amount", "currency", "decision", "confidence",
        "exception_type", "primary_reason", "matched_record", "review_status"
    ]
    assert header == expected, f"Header mismatch: expected {expected}, got {header}"
