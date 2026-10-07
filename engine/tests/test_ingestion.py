"""Tests for ingestion module."""

import pytest
import pandas as pd

from engine.ingestion import ingest
from engine.errors import IngestionError
from engine.config_loader import load_config


def test_column_aliases(base_config):
    """Test 13: Column aliases (Inv No., Supplier, Amount) ingest correctly."""
    df = pd.DataFrame([{
        "Inv No.": "X/2026/001",
        "Supplier": "Some Vendor",
        "Date": "01/09/2026",
        "Amount": "1000",
    }])
    cfg = load_config(base_config)
    records, warnings = ingest(df, cfg)
    assert len(records) == 1
    assert records[0]["invoice_number"] == "X/2026/001"
    assert records[0]["vendor_name"] == "Some Vendor"
    assert records[0]["total_amount"] == 1000.0


def test_missing_all_required_columns(base_config):
    """Test 14: Missing all required columns -> IngestionError."""
    df = pd.DataFrame([{"foo": "bar", "baz": "qux"}])
    cfg = load_config(base_config)
    with pytest.raises(IngestionError) as exc_info:
        ingest(df, cfg)
    assert len(exc_info.value.details) > 0


def test_generated_invoice_id(base_config):
    """No invoice_id column -> generates ROW-0001 etc."""
    df = pd.DataFrame([{
        "invoice_number": "X/001",
        "vendor_name": "V",
        "invoice_date": "01/01/2026",
        "total_amount": "100",
    }])
    cfg = load_config(base_config)
    records, warnings = ingest(df, cfg)
    assert records[0]["invoice_id"] == "ROW-0001"
    assert any("invoice_id" in w for w in warnings)
