def test_list_invoices_basic(seeded_client):
    res = seeded_client.get("/api/invoices")
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] > 0
    assert len(data["items"]) > 0

    first = data["items"][0]
    for key in ("id", "invoice_id", "decision", "confidence", "exception_type", "primary_reason"):
        assert key in first


def test_list_invoices_filters(seeded_client):
    # Filter by search
    res = seeded_client.get("/api/invoices?search=INV-1042")
    assert res.status_code == 200
    items = res.json()["items"]
    assert any("INV-1042" in item["invoice_id"] for item in items)

    # Filter by decision
    res = seeded_client.get("/api/invoices?decision=needs_review")
    assert res.status_code == 200
    for item in res.json()["items"]:
        assert item["decision"] == "needs_review"

    # Filter by confidence range
    res = seeded_client.get("/api/invoices?min_confidence=0.4&max_confidence=0.6")
    assert res.status_code == 200
    for item in res.json()["items"]:
        assert 0.4 <= item["confidence"] <= 0.6


def test_get_invoice_detail(seeded_client):
    # Get first invoice id
    list_res = seeded_client.get("/api/invoices")
    first_id = list_res.json()["items"][0]["id"]

    res = seeded_client.get(f"/api/invoices/{first_id}")
    assert res.status_code == 200
    data = res.json()
    assert "invoice" in data
    assert "decision" in data
    assert "reviews" in data
    assert data["invoice"]["id"] == first_id


def test_get_nonexistent_invoice(seeded_client):
    res = seeded_client.get("/api/invoices/999999")
    assert res.status_code == 404
    assert res.json()["error"]["code"] == "NOT_FOUND"


def test_generate_ai_summary(seeded_client):
    list_res = seeded_client.get("/api/invoices")
    first_id = list_res.json()["items"][0]["id"]

    res = seeded_client.post(f"/api/invoices/{first_id}/summary")
    assert res.status_code == 200
    data = res.json()
    assert "ai_summary" in data
    assert "ai_suggested_action" in data
    assert data["ai_summary_status"] == "ready"
    assert len(data["ai_summary"]) > 0
