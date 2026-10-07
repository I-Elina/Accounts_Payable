import os
import tempfile
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

SAMPLE_CSV = """invoice_id,invoice_number,vendor_name,invoice_date,due_date,currency,subtotal,tax_amount,total_amount,category,po_number,description
INV-0987,AC/2026/0345,Acme Private Limited,2026-09-02,2026-10-02,INR,8491.53,1528.47,10020.00,Office Supplies,PO-9812,Office supplies
INV-1042,AC/2026/0345,Acme Pvt Ltd,2026-09-03,2026-10-03,INR,8474.58,1525.42,10000.00,Office Supplies,PO-9815,Paper
INV-1001,AC/2026/0001,Infosys Limited,2026-08-15,2026-09-15,INR,12711.86,2288.14,15000.00,IT Equipment,,Laptops
INV-1055,TC/2026/9912,Tata Consultancy Services,2026-09-10,2026-10-10,INR,105932.20,19067.80,125000.00,Professional Services,,Consulting
INV-1088,DL/2026/1102,Dell Technologies Inc,2026-09-15,2026-10-15,INR,38135.59,6864.41,45000.00,IT Equipment,,Servers
INV-1110,MS/2026/0091,Microsoft India Pvt Ltd,2026-09-20,2026-10-20,INR,0.00,0.00,0.00,Software & Licenses,,Zero amount
"""


@pytest.fixture(autouse=True)
def setup_test_env(tmp_path, monkeypatch):
    test_db = tmp_path / "test_app.db"
    monkeypatch.setattr("backend.settings.DB_PATH", str(test_db))
    monkeypatch.setenv("AI_MODE", "mock")
    monkeypatch.setenv("USE_ENGINE_STUB", "true")

    from backend.database import init_db
    init_db(test_db)

    yield


@pytest.fixture
def client():
    from backend.main import app
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def seeded_client(client, tmp_path):
    # Upload sample CSV to seed DB
    csv_file = tmp_path / "seed.csv"
    csv_file.write_text(SAMPLE_CSV, encoding="utf-8")
    with open(csv_file, "rb") as f:
        res = client.post(
            "/api/uploads",
            files={"file": ("seed.csv", f, "text/csv")},
            data={"uploaded_by": "TestUser", "use_history": "false"},
        )
    assert res.status_code == 201
    return client
