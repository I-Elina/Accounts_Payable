"""Tests for Pass 1 rules R01-R08."""

import pytest
import pandas as pd

from engine import run_engine


def test_r01_missing_vendor(base_config):
    """Test 1: Missing vendor -> R01, decision exception, confidence <= 0.50."""
    df = pd.DataFrame([{
        "invoice_id": "INV-001",
        "invoice_number": "X/001",
        "vendor_name": "",
        "invoice_date": "01/09/2026",
        "total_amount": "5000",
    }])
    result = run_engine(df, config=base_config)
    inv = result["results"][0]
    assert inv["decision"] == "exception"
    assert inv["confidence"] <= 0.50
    assert any(v["rule_id"] == "R01" for v in inv["violations"])


def test_r02_negative_amount(base_config):
    """Test 2: total -5 -> R02 exception."""
    df = pd.DataFrame([{
        "invoice_id": "INV-001",
        "invoice_number": "X/001",
        "vendor_name": "Vendor A",
        "invoice_date": "01/09/2026",
        "total_amount": "-5",
    }])
    result = run_engine(df, config=base_config)
    inv = result["results"][0]
    assert inv["decision"] == "exception"
    assert any(v["rule_id"] == "R02" for v in inv["violations"])


def test_r02_zero_amount(base_config):
    """Test 2 variant: total 0 -> R02 exception."""
    df = pd.DataFrame([{
        "invoice_id": "INV-001",
        "invoice_number": "X/001",
        "vendor_name": "Vendor A",
        "invoice_date": "01/09/2026",
        "total_amount": "0",
    }])
    result = run_engine(df, config=base_config)
    inv = result["results"][0]
    assert inv["decision"] == "exception"


def test_r02_non_numeric_amount(base_config):
    """Test 2 variant: total 'abc' -> R02 exception."""
    df = pd.DataFrame([{
        "invoice_id": "INV-001",
        "invoice_number": "X/001",
        "vendor_name": "Vendor A",
        "invoice_date": "01/09/2026",
        "total_amount": "abc",
    }])
    result = run_engine(df, config=base_config)
    inv = result["results"][0]
    assert inv["decision"] == "exception"


def test_r03_unparseable_date(base_config):
    """Test 3: '31/31/2026' -> R03."""
    df = pd.DataFrame([{
        "invoice_id": "INV-001",
        "invoice_number": "X/001",
        "vendor_name": "Vendor A",
        "invoice_date": "31/31/2026",
        "total_amount": "5000",
    }])
    result = run_engine(df, config=base_config)
    inv = result["results"][0]
    assert inv["decision"] == "exception"
    assert any(v["rule_id"] == "R03" for v in inv["violations"])


def test_r04_future_date(base_config):
    """Test 4: Date after as_of_date -> R04, needs_review, confidence 0.70."""
    df = pd.DataFrame([{
        "invoice_id": "INV-001",
        "invoice_number": "X/001",
        "vendor_name": "Vendor A",
        "invoice_date": "15/12/2026",
        "total_amount": "5000",
    }])
    result = run_engine(df, config=base_config)
    inv = result["results"][0]
    assert inv["decision"] == "needs_review"
    assert inv["confidence"] == 0.70
    assert any(v["rule_id"] == "R04" for v in inv["violations"])


def test_r05_calculation_mismatch(base_config):
    """Test 5: subtotal 100 + tax 18 vs total 150 -> R05."""
    df = pd.DataFrame([{
        "invoice_id": "INV-001",
        "invoice_number": "X/001",
        "vendor_name": "Vendor A",
        "invoice_date": "01/09/2026",
        "total_amount": "150",
        "subtotal": "100",
        "tax_amount": "18",
    }])
    result = run_engine(df, config=base_config)
    inv = result["results"][0]
    assert any(v["rule_id"] == "R05" for v in inv["violations"])


def test_r05_no_mismatch(base_config):
    """Test 5 variant: total 118 = subtotal 100 + tax 18 -> no R05."""
    df = pd.DataFrame([{
        "invoice_id": "INV-001",
        "invoice_number": "X/001",
        "vendor_name": "Vendor A",
        "invoice_date": "01/09/2026",
        "total_amount": "118",
        "subtotal": "100",
        "tax_amount": "18",
    }])
    result = run_engine(df, config=base_config)
    inv = result["results"][0]
    assert not any(v["rule_id"] == "R05" for v in inv["violations"])


def test_r06_exact_duplicate(base_config):
    """Test 6: Exact duplicate pair -> second flagged R06 exception, first not."""
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
    result = run_engine(df, config=base_config)
    first = [r for r in result["results"] if r["invoice_id"] == "INV-001"][0]
    second = [r for r in result["results"] if r["invoice_id"] == "INV-002"][0]
    assert first["decision"] == "auto_pass"
    assert second["decision"] == "exception"
    assert any(v["rule_id"] == "R06" for v in second["violations"])


def test_r07_over_policy_limit(base_config):
    """Test 9: Total 150000 -> R07, 0.80, needs_review."""
    df = pd.DataFrame([{
        "invoice_id": "INV-001",
        "invoice_number": "X/001",
        "vendor_name": "Vendor A",
        "invoice_date": "01/09/2026",
        "total_amount": "150000",
    }])
    result = run_engine(df, config=base_config)
    inv = result["results"][0]
    assert inv["decision"] == "needs_review"
    assert inv["confidence"] == 0.80
    assert any(v["rule_id"] == "R07" for v in inv["violations"])
