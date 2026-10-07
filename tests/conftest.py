"""Pytest configuration and shared test fixtures for Cache Me If You Can."""

from __future__ import annotations

import os
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def fixed_as_of_date() -> str:
    """Canonical frozen evaluation date for all deterministic tests."""
    return "2026-10-01"


@pytest.fixture(scope="session")
def base_config(fixed_as_of_date: str) -> dict:
    """Base config override dictionary for engine tests."""
    return {
        "as_of_date": fixed_as_of_date,
        "vendor_master_path": str(ROOT / "data" / "reference" / "vendor_master.csv"),
    }


@pytest.fixture(scope="session")
def demo_csv_path() -> Path:
    """Path to processed demo invoice dataset."""
    return ROOT / "data" / "processed" / "invoices_demo.csv"


@pytest.fixture(scope="session")
def contracts_dir() -> Path:
    """Path to contracts root."""
    return ROOT / "contracts"


@pytest.fixture(scope="session")
def labels_dict(contracts_dir: Path) -> dict:
    """Parsed contracts/labels.json dictionary."""
    import json
    with open(contracts_dir / "labels.json", "r", encoding="utf-8") as f:
        return json.load(f)
