import io


def test_upload_valid_csv(client):
    csv_data = "invoice_number,vendor_name,invoice_date,total_amount\nINV-001,Acme,2026-09-01,1000\n"
    response = client.post(
        "/api/uploads",
        files={"file": ("test.csv", io.BytesIO(csv_data.encode("utf-8")), "text/csv")},
        data={"uploaded_by": "Shree"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "upload_id" in data
    assert data["filename"] == "test.csv"
    assert "summary" in data
    assert data["summary"]["total"] > 0


def test_upload_unsupported_extension(client):
    response = client.post(
        "/api/uploads",
        files={"file": ("test.txt", io.BytesIO(b"some content"), "text/plain")},
    )
    assert response.status_code == 422
    err = response.json()["error"]
    assert err["code"] == "VALIDATION_ERROR"
    assert "Unsupported file extension" in err["message"]


def test_upload_empty_file(client):
    response = client.post(
        "/api/uploads",
        files={"file": ("empty.csv", io.BytesIO(b""), "text/csv")},
    )
    assert response.status_code == 422
    err = response.json()["error"]
    assert err["code"] == "VALIDATION_ERROR"
    assert "empty" in err["message"].lower()


def test_list_uploads(seeded_client):
    response = seeded_client.get("/api/uploads")
    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) >= 1
    assert "total_rows" in items[0]
