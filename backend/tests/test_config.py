def test_get_and_update_config(client):
    # GET config
    res = client.get("/api/config")
    assert res.status_code == 200
    data = res.json()
    assert data["auto_pass_threshold"] == 0.85
    assert data["exception_below"] == 0.40
    assert len(data["rules"]) == 11

    # Invalid update: exception_below > auto_pass
    bad_res = client.put(
        "/api/config",
        json={"auto_pass_threshold": 0.50, "exception_below": 0.70},
    )
    assert bad_res.status_code == 422
    assert bad_res.json()["error"]["code"] == "VALIDATION_ERROR"

    # Valid update
    good_res = client.put(
        "/api/config",
        json={"auto_pass_threshold": 0.80, "exception_below": 0.35},
    )
    assert good_res.status_code == 200
    updated = good_res.json()
    assert updated["auto_pass_threshold"] == 0.80
    assert updated["exception_below"] == 0.35

    # Check audit log for SETTINGS_CHANGED
    audit_res = client.get("/api/audit?event_type=SETTINGS_CHANGED")
    assert audit_res.status_code == 200
    items = audit_res.json()["items"]
    assert len(items) >= 1
    assert items[0]["event_type"] == "SETTINGS_CHANGED"
