def test_review_approve_and_conflict(seeded_client):
    # Find a pending invoice
    list_res = seeded_client.get("/api/invoices?review_status=pending")
    items = list_res.json()["items"]
    assert len(items) > 0
    inv_id = items[0]["id"]

    # Approve
    res = seeded_client.post(
        f"/api/invoices/{inv_id}/review",
        json={"action": "approve", "reviewer": "Shree", "comment": "All good"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["decision"]["review_status"] == "approved"
    assert len(data["reviews"]) == 1
    assert data["reviews"][0]["reviewer"] == "Shree"
    assert data["reviews"][0]["action"] == "approve"

    # Second review attempt should return 409 conflict
    res2 = seeded_client.post(
        f"/api/invoices/{inv_id}/review",
        json={"action": "reject", "reviewer": "Alex"},
    )
    assert res2.status_code == 409
    assert res2.json()["error"]["code"] == "CONFLICT"


def test_review_missing_reviewer(seeded_client):
    list_res = seeded_client.get("/api/invoices?review_status=pending")
    inv_id = list_res.json()["items"][0]["id"]

    res = seeded_client.post(
        f"/api/invoices/{inv_id}/review",
        json={"action": "approve", "reviewer": "   "},
    )
    assert res.status_code == 422
    assert res.json()["error"]["code"] == "VALIDATION_ERROR"
