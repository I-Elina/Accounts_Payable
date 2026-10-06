def test_audit_log_events(seeded_client):
    res = seeded_client.get("/api/audit")
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert data["total"] > 0

    event_types = {e["event_type"] for e in data["items"]}
    assert "UPLOAD_RECEIVED" in event_types
    assert "INGESTION_COMPLETED" in event_types
