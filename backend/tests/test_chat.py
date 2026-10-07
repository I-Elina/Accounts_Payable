def test_chat_explain_decision(seeded_client):
    res = seeded_client.post("/api/chat", json={"message": "Why was INV-1042 flagged?"})
    assert res.status_code == 200
    data = res.json()
    assert "reply" in data
    assert "session_id" in data
    assert len(data["cards"]) > 0
    assert data["cards"][0]["invoice_id"] == "INV-1042"
    assert any(t["name"] == "explain_decision" for t in data["tools_used"])


def test_chat_riskiest_invoices(seeded_client):
    res = seeded_client.post("/api/chat", json={"message": "Show me the riskiest invoices"})
    assert res.status_code == 200
    data = res.json()
    assert len(data["cards"]) <= 5
    if len(data["cards"]) > 1:
        # Check ascending confidence
        for i in range(len(data["cards"]) - 1):
            assert data["cards"][i]["confidence"] <= data["cards"][i + 1]["confidence"]


def test_chat_proposal_never_writes(seeded_client):
    # Chat suggests approve for INV-1042
    res = seeded_client.post("/api/chat", json={"message": "Approve INV-1042"})
    assert res.status_code == 200
    data = res.json()
    assert data["proposal"] is not None
    assert data["proposal"]["invoice_id"] == "INV-1042"
    assert data["proposal"]["action"] == "approve"

    # Verify DB record is STILL pending!
    inv_res = seeded_client.get(f"/api/invoices/{data['proposal']['id']}")
    assert inv_res.json()["decision"]["review_status"] == "pending"

    # Verify audit log does NOT have REVIEW_APPROVED
    audit_res = seeded_client.get("/api/audit?invoice_id=INV-1042")
    events = [e["event_type"] for e in audit_res.json()["items"]]
    assert "REVIEW_APPROVED" not in events


def test_chat_unknown_invoice(seeded_client):
    res = seeded_client.post("/api/chat", json={"message": "Why was INV-9999 flagged?"})
    assert res.status_code == 200
    data = res.json()
    assert "could not find" in data["reply"].lower()
    assert len(data["cards"]) == 0
