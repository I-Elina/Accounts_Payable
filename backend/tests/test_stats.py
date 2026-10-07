def test_stats_metrics(seeded_client):
    res = seeded_client.get("/api/stats")
    assert res.status_code == 200
    data = res.json()

    total = data["total"]
    auto_pass = data["by_decision"]["auto_pass"]
    needs_review = data["by_decision"]["needs_review"]
    exception = data["by_decision"]["exception"]

    assert total == auto_pass + needs_review + exception
    assert 0.0 <= data["auto_pass_rate"] <= 1.0
    assert data["estimated_minutes_saved"] == auto_pass * 5

    # Check 10 histogram buckets
    hist = data["confidence_histogram"]
    assert len(hist) == 10
    assert sum(h["count"] for h in hist) == total
