"""Tests for analytics module: confidence calibration + vendor risk profiles."""

import pytest
import pandas as pd

from engine import run_engine


@pytest.fixture
def mixed_batch(base_config):
    """A batch with clean, duplicate, and future-dated invoices across 2 vendors."""
    df = pd.DataFrame([
        # Vendor A - clean
        {"invoice_id": "A1", "invoice_number": "A/001", "vendor_name": "Vendor Alpha",
         "invoice_date": "01/09/2026", "total_amount": "5000"},
        {"invoice_id": "A2", "invoice_number": "A/002", "vendor_name": "Vendor Alpha",
         "invoice_date": "05/09/2026", "total_amount": "5200"},
        # Vendor A - exact duplicate of A1
        {"invoice_id": "A3", "invoice_number": "A/001", "vendor_name": "Vendor Alpha",
         "invoice_date": "06/09/2026", "total_amount": "5000"},
        # Vendor B - clean
        {"invoice_id": "B1", "invoice_number": "B/001", "vendor_name": "Vendor Beta",
         "invoice_date": "01/09/2026", "total_amount": "8000"},
        # Vendor B - future date (soft)
        {"invoice_id": "B2", "invoice_number": "B/002", "vendor_name": "Vendor Beta",
         "invoice_date": "15/12/2026", "total_amount": "8500"},
    ])
    return run_engine(df, config=base_config)


def test_analytics_key_present(mixed_batch):
    """Output has top-level 'analytics' key."""
    assert "analytics" in mixed_batch


def test_calibration_keys(mixed_batch):
    """Confidence calibration has all required keys."""
    cal = mixed_batch["analytics"]["confidence_calibration"]
    for key in ("mean", "median", "std", "bands", "per_decision"):
        assert key in cal, f"Missing calibration key: {key}"


def test_calibration_bands_cover_all(mixed_batch):
    """Band counts sum to total invoices."""
    cal = mixed_batch["analytics"]["confidence_calibration"]
    total = mixed_batch["summary"]["total"]
    band_total = sum(b["count"] for b in cal["bands"].values())
    assert band_total == total


def test_calibration_per_decision_counts(mixed_batch):
    """Per-decision counts in calibration match summary counts."""
    cal = mixed_batch["analytics"]["confidence_calibration"]
    summary = mixed_batch["summary"]
    for decision in ("auto_pass", "needs_review", "exception"):
        assert cal["per_decision"][decision]["count"] == summary[decision]


def test_vendor_risk_profiles_present(mixed_batch):
    """Vendor risk list is non-empty."""
    risk = mixed_batch["analytics"]["vendor_risk"]
    assert isinstance(risk, list)
    assert len(risk) >= 1


def test_vendor_risk_fields(mixed_batch):
    """Each vendor profile has required fields."""
    required = {"vendor_name", "total_invoices", "auto_pass", "needs_review",
                "exceptions", "exception_rate_pct", "top_violations", "risk_flag"}
    for profile in mixed_batch["analytics"]["vendor_risk"]:
        assert required.issubset(set(profile.keys()))


def test_vendor_risk_flag_values(mixed_batch):
    """risk_flag is one of: high, medium, low."""
    for profile in mixed_batch["analytics"]["vendor_risk"]:
        assert profile["risk_flag"] in ("high", "medium", "low")


def test_vendor_alpha_has_exception(mixed_batch):
    """Vendor Alpha has >= 1 exception (the duplicate A3)."""
    risk = mixed_batch["analytics"]["vendor_risk"]
    alpha = next((p for p in risk if "alpha" in p["vendor_name"].lower()), None)
    assert alpha is not None
    assert alpha["exceptions"] >= 1


def test_high_risk_vendor_sorted_first(base_config):
    """A vendor with 5 exceptions out of 5 invoices is flagged high and sorted first."""
    rows = []
    for i in range(5):
        rows.append({"invoice_id": f"BAD-{i}", "invoice_number": f"BAD/{i}",
                     "vendor_name": "Dodgy Vendor", "invoice_date": f"{i+1:02d}/09/2026",
                     "total_amount": str(-100 - i)})   # negative -> R02 exception
    rows.append({"invoice_id": "GOOD-1", "invoice_number": "GOOD/001",
                 "vendor_name": "Good Vendor", "invoice_date": "01/09/2026",
                 "total_amount": "5000"})
    df = pd.DataFrame(rows)
    result = run_engine(df, config=base_config)
    risk = result["analytics"]["vendor_risk"]
    # First profile should be Dodgy Vendor
    assert "dodgy" in risk[0]["vendor_name"].lower() or risk[0]["risk_flag"] == "high"
    assert risk[0]["exception_rate_pct"] == 100.0