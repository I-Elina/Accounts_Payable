"""Tests for scoring, routing, and overall engine behaviour."""

import pytest
import pandas as pd
import time

from engine import run_engine
from engine.scoring import compute_score
from engine.schemas import Violation


def test_clean_invoice_auto_pass(base_config):
    """Test 11: Clean invoice with no candidates -> auto_pass, 1.00, pass 1."""
    df = pd.DataFrame([{
        "invoice_id": "INV-001",
        "invoice_number": "UNIQUE/2026/001",
        "vendor_name": "Unique Vendor",
        "invoice_date": "15/09/2026",
        "total_amount": "5000",
        "category": "Office Supplies",
    }])
    result = run_engine(df, config=base_config)
    inv = result["results"][0]
    assert inv["decision"] == "auto_pass"
    assert inv["confidence"] == 1.00
    assert inv["pass_resolved_in"] == 1


def test_threshold_override(base_config):
    """Test 12: Threshold override 0.75 makes a 0.80 invoice auto_pass."""
    df = pd.DataFrame([{
        "invoice_id": "INV-001",
        "invoice_number": "X/001",
        "vendor_name": "Vendor A",
        "invoice_date": "01/09/2026",
        "total_amount": "150000",  # triggers R07 -> confidence 0.80
    }])
    config = {**base_config, "auto_pass_threshold": 0.75}
    result = run_engine(df, config=config)
    inv = result["results"][0]
    assert inv["confidence"] == 0.80
    assert inv["decision"] == "auto_pass"


def test_deterministic_output(base_config):
    """Test 15: Two runs -> equal output."""
    df = pd.DataFrame([
        {
            "invoice_id": "INV-001",
            "invoice_number": "X/001",
            "vendor_name": "Vendor A",
            "invoice_date": "01/09/2026",
            "total_amount": "5000",
        },
        {
            "invoice_id": "INV-002",
            "invoice_number": "X/001",
            "vendor_name": "Vendor A",
            "invoice_date": "02/09/2026",
            "total_amount": "5000",
        },
    ])
    r1 = run_engine(df, config=base_config)
    r2 = run_engine(df, config=base_config)
    assert r1 == r2


def test_performance_5000_rows(base_config):
    """Test 16: 5,000-row synthetic frame runs in < 10 s."""
    import random
    random.seed(42)
    rows = []
    for i in range(5000):
        rows.append({
            "invoice_id": f"INV-{i:05d}",
            "invoice_number": f"PERF/{i:05d}",
            "vendor_name": f"Vendor-{random.randint(1, 50)}",
            "invoice_date": f"{random.randint(1,28):02d}/09/2026",
            "total_amount": str(random.randint(100, 99999)),
        })
    df = pd.DataFrame(rows)
    start = time.time()
    result = run_engine(df, config=base_config)
    elapsed = time.time() - start
    assert elapsed < 10, f"Took {elapsed:.1f}s, expected < 10s"
    assert result["summary"]["total"] == 5000


def test_output_contract_shape(base_config):
    """Test 17: Output validates against the contract shape."""
    df = pd.DataFrame([{
        "invoice_id": "INV-001",
        "invoice_number": "X/001",
        "vendor_name": "Vendor A",
        "invoice_date": "01/09/2026",
        "total_amount": "5000",
    }])
    result = run_engine(df, config=base_config)

    # Check top-level keys
    assert set(result.keys()) == {"summary", "warnings", "results", "analytics"}

    # Check summary keys
    summary = result["summary"]
    for key in ["total", "auto_pass", "needs_review", "exception",
                 "engine_version", "auto_pass_threshold", "exception_below"]:
        assert key in summary, f"Missing summary key: {key}"

    # Check result item keys
    inv = result["results"][0]
    required_keys = {
        "invoice_id", "row_index", "decision", "confidence",
        "pass_resolved_in", "exception_type", "primary_reason",
        "matched_record", "violations", "evidence", "record",
    }
    assert required_keys.issubset(set(inv.keys()))

    # Check decision enum
    assert inv["decision"] in ("auto_pass", "needs_review", "exception")

    # Check exception_type enum
    valid_types = {
        "none", "missing_field", "invalid_amount", "invalid_date",
        "future_date", "calculation_mismatch", "exact_duplicate",
        "fuzzy_duplicate", "policy_limit", "unknown_vendor", "amount_outlier",
    }
    assert inv["exception_type"] in valid_types

    # Check record has canonical fields
    from engine.schemas import CANONICAL_FIELDS
    for field in CANONICAL_FIELDS:
        assert field in inv["record"]


def test_r11_amount_outlier(base_config):
    """Test 10: Vendor with 30 normal invoices + one 10x larger -> R11."""
    rows = []
    for i in range(30):
        rows.append({
            "invoice_id": f"INV-{i:04d}",
            "invoice_number": f"NORM/{i:04d}",
            "vendor_name": "Outlier Vendor Ltd",
            "invoice_date": f"{(i % 28) + 1:02d}/09/2026",
            "total_amount": "1000",
        })
    # Add one 10x larger
    rows.append({
        "invoice_id": "INV-OUTLIER",
        "invoice_number": "OUT/9999",
        "vendor_name": "Outlier Vendor Ltd",
        "invoice_date": "30/09/2026",
        "total_amount": "10000",
    })
    df = pd.DataFrame(rows)
    result = run_engine(df, config=base_config)
    outlier = [r for r in result["results"] if r["invoice_id"] == "INV-OUTLIER"][0]
    assert any(v["rule_id"] == "R11" for v in outlier["violations"])
