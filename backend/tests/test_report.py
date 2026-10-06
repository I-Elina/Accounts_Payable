def test_download_report_csv(seeded_client):
    # Get upload ID
    uploads = seeded_client.get("/api/uploads").json()["items"]
    upload_id = uploads[0]["id"]

    res = seeded_client.get(f"/api/uploads/{upload_id}/report")
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
    assert f"ap_exception_report_{upload_id}.csv" in res.headers["content-disposition"]

    # Verify BOM and header
    content = res.content
    assert content.startswith(b"\xef\xbb\xbf")
    text = content.decode("utf-8-sig")
    lines = text.strip().splitlines()
    assert len(lines) >= 1
    header = lines[0].split(",")
    expected_header = [
        "invoice_id",
        "invoice_number",
        "vendor_name",
        "invoice_date",
        "total_amount",
        "currency",
        "decision",
        "confidence",
        "exception_type",
        "primary_reason",
        "matched_record",
        "review_status",
    ]
    assert header == expected_header
