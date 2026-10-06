"""Shared fixtures for engine tests."""

import pytest
import pandas as pd


FIXED_DATE = "2026-10-01"


@pytest.fixture
def base_config():
    """Config overrides for testing: fixed date, no vendor master dependency."""
    return {
        "as_of_date": FIXED_DATE,
        "vendor_master_path": "",  # skip vendor master
    }


@pytest.fixture
def clean_invoice():
    """A single clean invoice row as a DataFrame."""
    return pd.DataFrame([{
        "invoice_id": "INV-0001",
        "invoice_number": "TEST/2026/001",
        "vendor_name": "Test Vendor Pvt Ltd",
        "invoice_date": "15/09/2026",
        "total_amount": "5000",
        "currency": "INR",
        "category": "Office Supplies",
    }])
