"""Test suite running curated edge cases through the decision engine.

Validates that each rule R01-R11, boundaries (0.5% tolerance, 100,000 ceiling),
clean passes, and compound violations produce the exact expected decisions and confidences.
"""

from __future__ import annotations

import csv
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent.parent


def load_rule_cases() -> list[dict]:
    """Load test cases from cases.csv."""
    cases_path = Path(__file__).parent / "cases.csv"
    with open(cases_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def test_rule_cases_suite(base_config):
    """Run all 32 curated cases through run_engine and assert expected outputs."""
    engine_module = pytest.importorskip("engine", reason="engine package required for rule tests")
    run_engine = engine_module.run_engine

    cases_path = Path(__file__).parent / "cases.csv"
    cases = load_rule_cases()
    assert len(cases) >= 30, f"Expected at least 30 rule cases, found {len(cases)}"

    # Run engine on the CSV
    output = run_engine(str(cases_path), config=base_config)
    results = {r["invoice_id"]: r for r in output["results"]}

    failures = []
    for c in cases:
        cid = c["case_id"]
        iid = c["invoice_id"]
        exp_dec = c["expected_decision"]
        exp_type = c["expected_exception_type"]
        exp_conf = float(c["expected_confidence"])

        res = results.get(iid)
        if not res:
            failures.append(f"Case {cid} ({iid}): Record missing from engine results!")
            continue

        act_dec = res["decision"]
        act_type = res["exception_type"]
        act_conf = res["confidence"]

        # Validate decision
        if act_dec != exp_dec:
            failures.append(
                f"Case {cid} ({c['note']}): Expected decision '{exp_dec}', got '{act_dec}'"
            )

        # Validate exception type
        if act_type != exp_type:
            failures.append(
                f"Case {cid} ({c['note']}): Expected exception_type '{exp_type}', got '{act_type}'"
            )

        # Validate confidence score within ±0.05
        if abs(act_conf - exp_conf) > 0.05:
            failures.append(
                f"Case {cid} ({c['note']}): Expected confidence {exp_conf:.2f}, got {act_conf:.2f}"
            )

    assert not failures, "\n".join(failures)
