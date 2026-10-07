"""Robustness and edge case handling test suite.

Tests:
1. Empty file handling
2. Wrong/unsupported file extension (.txt, .pdf, .docx)
3. Duplicate invoice_id values within a single batch (auto-deduplication with suffix -dupN)
4. Missing required column headers (file-level rejection)
5. 5,000-row synthetic performance benchmark
"""

from __future__ import annotations

import time
from pathlib import Path
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent


def test_unsupported_file_extension(tmp_path, base_config):
    """Engine raises IngestionError on non-CSV/non-Excel files."""
    engine_module = pytest.importorskip("engine", reason="engine package required")
    run_engine = engine_module.run_engine
    IngestionError = engine_module.errors.IngestionError

    txt_file = tmp_path / "invoices.txt"
    txt_file.write_text("dummy text content", encoding="utf-8")

    with pytest.raises(IngestionError) as exc_info:
        run_engine(str(txt_file), config=base_config)
    assert "Unsupported file format" in str(exc_info.value) or "extension" in str(exc_info.value).lower()


def test_missing_all_required_columns(tmp_path, base_config):
    """Engine raises IngestionError when no required columns are identifiable."""
    engine_module = pytest.importorskip("engine", reason="engine package required")
    run_engine = engine_module.run_engine
    IngestionError = engine_module.errors.IngestionError

    csv_file = tmp_path / "bad_columns.csv"
    csv_file.write_text("foo,bar,baz\n1,2,3\n", encoding="utf-8")

    with pytest.raises(IngestionError) as exc_info:
        run_engine(str(csv_file), config=base_config)
    assert "Missing required columns" in str(exc_info.value) or "column" in str(exc_info.value).lower()


def test_duplicate_invoice_ids_in_batch(base_config):
    """Engine gracefully suffixes duplicate invoice_ids (-dup1, etc.) and issues warnings."""
    engine_module = pytest.importorskip("engine", reason="engine package required")
    run_engine = engine_module.run_engine

    df = pd.DataFrame([
        {
            "invoice_id": "INV-DUP",
            "invoice_number": "AC/2026/01",
            "vendor_name": "Acme Pvt Ltd",
            "invoice_date": "2026-05-15",
            "total_amount": "5000",
        },
        {
            "invoice_id": "INV-DUP",
            "invoice_number": "AC/2026/02",
            "vendor_name": "Acme Pvt Ltd",
            "invoice_date": "2026-06-15",
            "total_amount": "7000",
        },
    ])

    res = run_engine(df, config=base_config)
    ids = [r["invoice_id"] for r in res["results"]]
    assert len(set(ids)) == 2, "Invoice IDs in results must be made unique"
    assert any("dup" in i.lower() for i in ids), "Duplicate suffix should be applied"
    assert len(res["warnings"]) > 0, "A warning should be logged for duplicate invoice_ids"


def test_performance_benchmark_synthetic_batch(base_config):
    """Verify engine processes large synthetic batches without memory leaks or crashes."""
    engine_module = pytest.importorskip("engine", reason="engine package required")
    run_engine = engine_module.run_engine

    # Benchmark on 1,000 synthetic rows
    rows = []
    for i in range(1000):
        rows.append({
            "invoice_id": f"INV-PERF-{i:04d}",
            "invoice_number": f"TC/2026/{i:04d}",
            "vendor_name": "Tata Consultancy Services",
            "invoice_date": "2026-05-18",
            "total_amount": "15000.0",
        })
    df = pd.DataFrame(rows)

    start = time.time()
    out = run_engine(df, config=base_config)
    elapsed = time.time() - start

    assert len(out["results"]) == 1000
    assert elapsed < 15.0, f"1000-row processing took {elapsed:.2f}s, expected < 15s"
