"""Pass 1 rules: R01-R08 — fast, exact checks run on every invoice."""

from __future__ import annotations

from datetime import datetime

from engine.schemas import Violation


def r01(rec: dict, ctx: dict) -> Violation | None:
    """R01 — Missing required field(s)."""
    cfg = ctx["cfg"]
    if not cfg["rules"]["R01"]["enabled"]:
        return None
    required = cfg.get("required_fields",
                       ["invoice_number", "vendor_name", "invoice_date", "total_amount"])
    missing = [f for f in required
               if rec.get(f) is None or (isinstance(rec.get(f), str) and not rec[f].strip())]
    if not missing:
        return None
    return Violation(
        rule_id="R01",
        name="Missing field",
        severity="hard",
        penalty=cfg["rules"]["R01"]["penalty"],
        exception_type="missing_field",
        message=f"Missing required field(s): {', '.join(missing)}",
        evidence={"missing_fields": missing},
    )


def r02(rec: dict, ctx: dict) -> Violation | None:
    """R02 — Invalid total_amount (not numeric or <= 0)."""
    cfg = ctx["cfg"]
    if not cfg["rules"]["R02"]["enabled"]:
        return None
    total = rec.get("total_amount")
    if total is not None and total > 0:
        return None
    return Violation(
        rule_id="R02",
        name="Invalid amount",
        severity="hard",
        penalty=cfg["rules"]["R02"]["penalty"],
        exception_type="invalid_amount",
        message=f"Invalid amount: {rec.get('raw_total_amount')}",
        evidence={"raw_total_amount": rec.get("raw_total_amount")},
    )


def r03(rec: dict, ctx: dict) -> Violation | None:
    """R03 — Unparseable invoice_date."""
    cfg = ctx["cfg"]
    if not cfg["rules"]["R03"]["enabled"]:
        return None
    if rec.get("invoice_date") is not None:
        return None
    return Violation(
        rule_id="R03",
        name="Invalid date",
        severity="hard",
        penalty=cfg["rules"]["R03"]["penalty"],
        exception_type="invalid_date",
        message=f"Invalid invoice date: {rec.get('raw_invoice_date')}",
        evidence={"raw_invoice_date": rec.get("raw_invoice_date")},
    )


def r04(rec: dict, ctx: dict) -> Violation | None:
    """R04 — Future-dated invoice. Skip if date is invalid."""
    cfg = ctx["cfg"]
    if not cfg["rules"]["R04"]["enabled"]:
        return None
    date_str = rec.get("invoice_date")
    if date_str is None:
        return None  # R03 handles invalid dates
    as_of = ctx["as_of_date"]
    try:
        inv_date = datetime.strptime(date_str, "%Y-%m-%d")
        ref_date = datetime.strptime(as_of, "%Y-%m-%d")
    except (ValueError, TypeError):
        return None
    if inv_date <= ref_date:
        return None
    return Violation(
        rule_id="R04",
        name="Future date",
        severity="soft",
        penalty=cfg["rules"]["R04"]["penalty"],
        exception_type="future_date",
        message=f"Invoice date {date_str} is in the future",
        evidence={"invoice_date": date_str, "as_of_date": as_of},
    )


def r05(rec: dict, ctx: dict) -> Violation | None:
    """R05 — Calculation mismatch (subtotal + tax != total). Skip if inputs invalid."""
    cfg = ctx["cfg"]
    if not cfg["rules"]["R05"]["enabled"]:
        return None
    subtotal = rec.get("subtotal")
    tax = rec.get("tax_amount")
    total = rec.get("total_amount")
    # Only fire if both subtotal and tax are present, and total is valid
    if subtotal is None or tax is None or total is None or total <= 0:
        return None
    expected = subtotal + tax
    tolerance = cfg.get("calc_tolerance_pct", 0.5)
    diff_pct = abs(expected - total) / total * 100
    if diff_pct <= tolerance:
        return None
    return Violation(
        rule_id="R05",
        name="Calculation mismatch",
        severity="soft",
        penalty=cfg["rules"]["R05"]["penalty"],
        exception_type="calculation_mismatch",
        message=f"Total {total} does not equal subtotal + tax ({expected})",
        evidence={
            "subtotal": subtotal,
            "tax_amount": tax,
            "total_amount": total,
            "expected_total": expected,
            "difference": round(abs(expected - total), 2),
        },
    )


def r06(rec: dict, ctx: dict) -> Violation | None:
    """R06 — Exact duplicate."""
    cfg = ctx["cfg"]
    if not cfg["rules"]["R06"]["enabled"]:
        return None
    exact_matches: dict = ctx.get("exact_matches", {})
    matched = exact_matches.get(rec["invoice_id"])
    if matched is None:
        return None
    from engine.normalize import normalize_vendor, normalize_invoice_number
    return Violation(
        rule_id="R06",
        name="Exact duplicate",
        severity="hard",
        penalty=cfg["rules"]["R06"]["penalty"],
        exception_type="exact_duplicate",
        message=f"Exact duplicate of {matched}",
        matched_record=matched,
        evidence={
            "matched_invoice_id": matched,
            "key": {
                "vendor": rec.get("vendor_name"),
                "invoice_number": rec.get("invoice_number"),
                "total": rec.get("total_amount"),
            },
        },
    )


def r07(rec: dict, ctx: dict) -> Violation | None:
    """R07 — Over policy limit. Skip if total is invalid."""
    cfg = ctx["cfg"]
    if not cfg["rules"]["R07"]["enabled"]:
        return None
    total = rec.get("total_amount")
    if total is None or total <= 0:
        return None
    limit = cfg.get("policy_limit", 100000)
    if total <= limit:
        return None
    return Violation(
        rule_id="R07",
        name="Over policy limit",
        severity="soft",
        penalty=cfg["rules"]["R07"]["penalty"],
        exception_type="policy_limit",
        message=f"Amount {total} exceeds policy limit {limit}",
        evidence={"total_amount": total, "policy_limit": limit},
    )


def r08(rec: dict, ctx: dict) -> Violation | None:
    """R08 — Unknown vendor or disallowed category."""
    cfg = ctx["cfg"]
    if not cfg["rules"]["R08"]["enabled"]:
        return None
    vendor_master: set = ctx.get("vendor_master", set())
    allowed_cats = cfg.get("allowed_categories", [])
    reasons = []

    # Check vendor (only if vendor_master is non-empty)
    if vendor_master:
        from engine.normalize import normalize_vendor
        nv = normalize_vendor(rec.get("vendor_name"))
        if nv and nv not in vendor_master:
            reasons.append("vendor_not_in_master")

    # Check category
    cat = rec.get("category")
    if cat and allowed_cats and cat not in allowed_cats:
        reasons.append("category_not_allowed")

    if not reasons:
        return None

    reason_text = " and ".join(r.replace("_", " ") for r in reasons)
    return Violation(
        rule_id="R08",
        name="Unknown vendor/category",
        severity="soft",
        penalty=cfg["rules"]["R08"]["penalty"],
        exception_type="unknown_vendor",
        message="Vendor or category not in approved list",
        evidence={
            "vendor_name": rec.get("vendor_name"),
            "category": rec.get("category"),
            "reason": reason_text,
        },
    )


# All Pass 1 rules in order
PASS1_RULES = [r01, r02, r03, r04, r05, r06, r07, r08]
