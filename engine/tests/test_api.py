"""Integration tests for the run_engine API."""

import pytest
import pandas as pd

from engine import run_engine
from engine.errors import IngestionError


def test_unsupported_format(base_config):
    """IngestionError on unsupported file type."""
    with pytest.raises(IngestionError):
        run_engine("test.txt", config=base_config)


def test_history_duplicates(base_config):
    """Exact duplicate against history record is flagged."""
    history = [{
        "invoice_id": "HIST-001",
        "invoice_number": "X/001",
        "vendor_name": "Vendor A",
        "invoice_date": "2026-08-01",
        "total_amount": 5000,
        "currency": "INR",
    }]
    df = pd.DataFrame([{
        "invoice_id": "INV-001",
        "invoice_number": "X/001",
        "vendor_name": "Vendor A",
        "invoice_date": "01/09/2026",
        "total_amount": "5000",
    }])
    result = run_engine(df, history=history, config=base_config)
    inv = result["results"][0]
    assert inv["decision"] == "exception"
    assert any(v["rule_id"] == "R06" for v in inv["violations"])


def test_warnings_are_list(base_config):
    """Warnings is always a list."""
    df = pd.DataFrame([{
        "invoice_number": "X/001",
        "vendor_name": "V",
        "invoice_date": "01/01/2026",
        "total_amount": "100",
    }])
    result = run_engine(df, config=base_config)
    assert isinstance(result["warnings"], list)
