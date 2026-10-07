"""End-to-end integration test for the Accounts Payable Exception Assistant."""

from __future__ import annotations

import io
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent.parent


def test_end_to_end_upload_review_audit_flow(tmp_path, monkeypatch):
    """Full lifecycle: upload demo CSV -> check counts -> inspect INV-1042 -> review -> audit log."""
    backend_main = pytest.importorskip("backend.main", reason="backend package required for end-to-end test")
    db_file = tmp_path / "test_e2e.db"
    monkeypatch.setattr("backend.settings.DB_PATH", str(db_file))
    from backend.database import init_db
    init_db()

    from fastapi.testclient import TestClient
    app = backend_main.app
    client = TestClient(app)

    # 1. Health check
    res_health = client.get("/api/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "ok"

    # 2. Upload demo CSV
    demo_csv = ROOT / "data" / "processed" / "invoices_demo.csv"
    assert demo_csv.exists(), "invoices_demo.csv not found"

    with open(demo_csv, "rb") as f:
        upload_resp = client.post(
            "/api/uploads",
            files={"file": ("invoices_demo.csv", f, "text/csv")},
            data={"uploaded_by": "TestReviewer"},
        )
    assert upload_resp.status_code in (200, 201)
    up_data = upload_resp.json()
    assert "upload_id" in up_data
    upload_id = up_data["upload_id"]
    summary = up_data["summary"]
    assert summary["total"] == 1000

    # 3. Retrieve review queue
    queue_resp = client.get("/api/invoices", params={"upload_id": upload_id, "decision": "needs_review,exception"})
    assert queue_resp.status_code == 200
    queue_data = queue_resp.json()
    assert queue_data["total"] > 0

    # 4. Find planted showcase record INV-1042
    inv_resp = client.get("/api/invoices", params={"upload_id": upload_id, "search": "INV-1042"})
    assert inv_resp.status_code == 200
    inv_items = inv_resp.json()["items"]
    assert len(inv_items) >= 1
    target_pk = inv_items[0]["id"]

    # 5. Get detail for INV-1042
    detail_resp = client.get(f"/api/invoices/{target_pk}")
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert detail["invoice"]["invoice_id"] == "INV-1042"
    assert detail["decision"]["matched_record"] == "INV-0987"
    assert detail["decision"]["exception_type"] == "fuzzy_duplicate"

    # 6. Generate AI Summary
    summary_resp = client.post(f"/api/invoices/{target_pk}/summary")
    assert summary_resp.status_code == 200
    sum_data = summary_resp.json()
    assert "ai_summary" in sum_data
    assert "INV-0987" in sum_data["ai_summary"]

    # 7. Review and Approve INV-1042
    review_resp = client.post(
        f"/api/invoices/{target_pk}/review",
        json={"action": "approve", "reviewer": "Shree", "comment": "Legitimate separate branch delivery verified"},
    )
    assert review_resp.status_code == 200
    rev_data = review_resp.json()
    assert rev_data["decision"]["review_status"] == "approved"

    # 8. Check audit log event sequence
    audit_upload = client.get("/api/audit", params={"event_type": "UPLOAD_RECEIVED"})
    assert audit_upload.status_code == 200
    assert audit_upload.json()["total"] >= 1

    audit_review = client.get("/api/audit", params={"invoice_id": "INV-1042", "event_type": "REVIEW_APPROVED"})
    assert audit_review.status_code == 200
    assert audit_review.json()["total"] >= 1
