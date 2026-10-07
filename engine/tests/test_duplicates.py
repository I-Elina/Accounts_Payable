"""Tests for fuzzy duplicates and the invoice_number gate."""

import pytest
import pandas as pd

from engine import run_engine


def test_fuzzy_duplicate_worked_example(base_config):
    """Test 7: Worked example from section 5 — needs_review, 0.50."""
    df = pd.DataFrame([
        {
            "invoice_id": "INV-0987",
            "invoice_number": "AC/2026/0345",
            "vendor_name": "Acme Private Limited",
            "invoice_date": "02/09/2026",
            "total_amount": "10020",
        },
        {
            "invoice_id": "INV-1042",
            "invoice_number": "AC/2026/0345",
            "vendor_name": "Acme Pvt Ltd",
            "invoice_date": "03/09/2026",
            "total_amount": "10000",
        },
    ])
    result = run_engine(df, config=base_config)
    inv = [r for r in result["results"] if r["invoice_id"] == "INV-1042"][0]
    assert inv["decision"] == "needs_review"
    assert inv["confidence"] == 0.50
    assert inv["exception_type"] == "fuzzy_duplicate"
    assert inv["matched_record"] == "INV-0987"
    assert inv["pass_resolved_in"] == 2


def test_different_invoice_number_not_flagged(base_config):
    """Test 8: Same vendor, nearby date, similar amount but DIFFERENT invoice
    number -> NOT flagged (gate works)."""
    df = pd.DataFrame([
        {
            "invoice_id": "INV-001",
            "invoice_number": "X/2026/001",
            "vendor_name": "Vendor A Pvt Ltd",
            "invoice_date": "01/09/2026",
            "total_amount": "10000",
        },
        {
            "invoice_id": "INV-002",
            "invoice_number": "Y/2026/999",
            "vendor_name": "Vendor A Private Limited",
            "invoice_date": "02/09/2026",
            "total_amount": "10050",
        },
    ])
    result = run_engine(df, config=base_config)
    inv = [r for r in result["results"] if r["invoice_id"] == "INV-002"][0]
    # Should NOT have R09 because invoice numbers are different (gate fails)
    assert not any(v["rule_id"] == "R09" for v in inv["violations"])
