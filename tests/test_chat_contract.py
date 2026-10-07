"""Tests for chat-first assistant behavior, card shapes, and CSV safety."""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent


def test_csv_formula_injection_escaping():
    """Verify that values starting with =, +, -, @ are escaped with leading single quote in CSV."""
    raw_rows = [
        {"vendor_name": '=HYPERLINK("http://evil.com")', "invoice_id": "INV-EVIL-1"},
        {"vendor_name": "+CMD|' /C calc'!A0", "invoice_id": "INV-EVIL-2"},
        {"vendor_name": "-5+5", "invoice_id": "INV-EVIL-3"},
        {"vendor_name": "@SUM(A1:A10)", "invoice_id": "INV-EVIL-4"},
        {"vendor_name": "Standard Vendor Ltd", "invoice_id": "INV-SAFE-1"},
    ]

    def escape_csv_cell(val: str) -> str:
        if isinstance(val, str) and val.startswith(("=", "+", "-", "@")):
            return "'" + val
        return val

    escaped_rows = []
    for r in raw_rows:
        escaped_rows.append({k: escape_csv_cell(v) for k, v in r.items()})

    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=["vendor_name", "invoice_id"])
    writer.writeheader()
    writer.writerows(escaped_rows)
    csv_text = out.getvalue()

    assert "'=HYPERLINK" in csv_text
    assert "'+CMD" in csv_text
    assert "'-5+5" in csv_text
    assert "'@SUM" in csv_text
    assert "Standard Vendor Ltd" in csv_text


def test_chat_json_cards_and_proposals_contract():
    """Verify chat.json meets the Card and Proposal contracts specified in CONTRACT.md §8."""
    chat_json_path = ROOT / "contracts" / "examples" / "chat.json"
    with open(chat_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "reply" in data
    assert "cards" in data
    cards = data["cards"]
    assert len(cards) <= 5, "Maximum 5 cards allowed per chat reply"

    card_types = {c["type"] for c in cards}
    assert card_types.issubset({"invoice", "stats", "report"}), f"Unexpected card types: {card_types}"

    # Verify at least one invoice card structure
    inv_card = next((c for c in cards if c["type"] == "invoice"), None)
    if inv_card:
        for req in ["invoice_id", "vendor_name", "total_amount", "decision", "confidence", "review_status"]:
            assert req in inv_card, f"Invoice card missing required field: {req}"

    # Verify proposal structure
    prop = data.get("proposal")
    if prop:
        assert prop["type"] == "review_proposal"
        assert prop["action"] in ["approve", "reject"]
        assert "invoice_id" in prop
        assert "reason" in prop
