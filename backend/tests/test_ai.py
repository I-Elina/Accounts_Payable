from backend.ai.summary import generate_summary
from backend.ai.validate import validate_summary


def test_ai_mock_summary_generation():
    record = {
        "invoice_id": "INV-1042",
        "decision": "needs_review",
        "confidence": 0.50,
        "exception_type": "fuzzy_duplicate",
        "primary_reason": "Probable duplicate of INV-0987 (96% similar)",
        "matched_record": "INV-0987",
        "violations": [
            {
                "rule_id": "R09",
                "name": "Fuzzy duplicate",
                "severity": "soft",
                "penalty": 0.35,
                "exception_type": "fuzzy_duplicate",
                "message": "Probable duplicate of INV-0987 (96% similar)",
            }
        ],
    }

    res = generate_summary(record)
    assert "summary" in res
    assert "suggested_action" in res
    assert "referenced_rule_ids" in res
    assert res["suggested_action"] == "investigate"
    assert "R09" in res["referenced_rule_ids"]
    assert validate_summary(res, record) is True


def test_validate_summary_rejects_hallucinated_id():
    record = {
        "invoice_id": "INV-1042",
        "matched_record": "INV-0987",
        "violations": [{"rule_id": "R09"}],
    }

    bad_output = {
        "summary": "Invoice INV-9999 is a duplicate of INV-1042.",
        "suggested_action": "investigate",
        "referenced_rule_ids": ["R09"],
    }

    assert validate_summary(bad_output, record) is False
