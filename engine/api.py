"""Main engine entry point: run_engine()."""

from __future__ import annotations

import os
from datetime import date
from pathlib import Path

import pandas as pd

from engine.config_loader import load_config
from engine.errors import IngestionError
from engine.ingestion import ingest
from engine.duplicates import build_exact_index, build_candidates
from engine.stats import build_vendor_stats
from engine.normalize import normalize_vendor
from engine.rules.pass1 import PASS1_RULES
from engine.rules.pass2 import r09_r10, r11
from engine.scoring import compute_score
from engine.routing import route
from engine.evidence import resolve_primary
from engine.schemas import Violation, build_result
from engine.analytics import confidence_calibration, vendor_risk_profiles


__version__ = "1.0.0"


def _load_vendor_master(path: str | None) -> set[str]:
    """Load the vendor master CSV and return a set of normalised vendor names."""
    if not path:
        return set()
    full = Path(path) if not os.path.isabs(path) else Path(path)
    if not full.exists():
        return set()
    try:
        df = pd.read_csv(full, dtype=str)
        col = None
        for c in df.columns:
            if c.lower().replace(" ", "_") in (
                "vendor_name", "vendor", "supplier", "supplier_name", "name"
            ):
                col = c
                break
        if col is None and len(df.columns) > 0:
            col = df.columns[0]
        if col is None:
            return set()
        return {normalize_vendor(v) for v in df[col].dropna()}
    except Exception:
        return set()


def run_engine(
    source,
    history: list[dict] | None = None,
    config: dict | None = None,
) -> dict:
    """Process invoices and return decisions + analytics.

    Args:
        source: str/Path to .csv/.xlsx, or a pandas DataFrame.
        history: optional list of canonical invoice dicts from earlier uploads.
        config: optional dict that overrides default_config.json (deep-merged).

    Returns:
        dict with keys: summary, warnings, results, analytics.

    Raises:
        IngestionError: On file-level problems.
    """
    cfg = load_config(config)
    as_of = cfg.get("as_of_date") or date.today().isoformat()

    # -- Ingest ---------------------------------------------------------------
    records, warnings = ingest(source, cfg)

    # -- Load vendor master ---------------------------------------------------
    vendor_master = _load_vendor_master(cfg.get("vendor_master_path"))
    if not vendor_master and cfg.get("vendor_master_path"):
        warnings.append("Vendor master file not found; R08 will only check category")

    # -- Build indexes --------------------------------------------------------
    exact_matches = build_exact_index(records, history)
    candidates = build_candidates(
        records, history,
        blocking_days=cfg.get("blocking", {}).get("days", 30),
        blocking_amount_pct=cfg.get("blocking", {}).get("amount_pct", 10),
    )
    vendor_stats = build_vendor_stats(records, history)

    ctx = {
        "cfg": cfg,
        "as_of_date": as_of,
        "vendor_master": vendor_master,
        "exact_matches": exact_matches,
    }

    # -- Process each record --------------------------------------------------
    results: list[dict] = []
    counts = {"auto_pass": 0, "needs_review": 0, "exception": 0}

    for rec in records:
        all_violations: list[Violation] = []

        # Pass 1 (R01-R08)
        for rule_fn in PASS1_RULES:
            v = rule_fn(rec, ctx)
            if v is not None:
                all_violations.append(v)

        has_hard = any(v.severity == "hard" for v in all_violations)

        if not has_hard:
            has_candidates = len(candidates.get(rec["invoice_id"], [])) > 0
            uncertain = len(all_violations) > 0 or has_candidates
            pass_resolved_in = 2 if uncertain else 1

            if uncertain:
                # R09 + R10 (fuzzy duplicate)
                cands = candidates.get(rec["invoice_id"], [])
                exact_match_id = exact_matches.get(rec["invoice_id"])
                all_violations.extend(r09_r10(rec, cands, exact_match_id, cfg))

            # R11 (outlier) -- always runs when no hard violation
            v11 = r11(rec, vendor_stats, cfg)
            if v11 is not None:
                all_violations.append(v11)
                if not uncertain:
                    pass_resolved_in = 2
        else:
            pass_resolved_in = 1

        score = compute_score(all_violations)
        decision = route(score, all_violations, cfg)
        exception_type, primary_reason, matched_record, evidence = resolve_primary(
            all_violations
        )

        results.append(build_result(
            rec=rec,
            violations=all_violations,
            decision=decision,
            confidence=score,
            pass_resolved_in=pass_resolved_in,
            exception_type=exception_type,
            primary_reason=primary_reason,
            matched_record=matched_record,
            evidence=evidence,
        ))
        counts[decision] += 1

    results.sort(key=lambda r: r["row_index"])

    # -- Analytics ------------------------------------------------------------
    analytics = {
        "confidence_calibration": confidence_calibration(results),
        "vendor_risk": vendor_risk_profiles(results, history),
    }

    return {
        "summary": {
            "total": len(results),
            "auto_pass": counts["auto_pass"],
            "needs_review": counts["needs_review"],
            "exception": counts["exception"],
            "engine_version": __version__,
            "auto_pass_threshold": cfg["auto_pass_threshold"],
            "exception_below": cfg["exception_below"],
        },
        "warnings": warnings,
        "results": results,
        "analytics": analytics,
    }