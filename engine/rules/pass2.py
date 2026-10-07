"""Pass 2 rules: R09-R11 -- fuzzy duplicate + outlier checks on uncertain invoices."""

from __future__ import annotations

from datetime import datetime

from rapidfuzz import fuzz

from engine.normalize import normalize_vendor, normalize_invoice_number
from engine.schemas import Violation


def r09_r10(
    rec: dict,
    candidates: list[dict],
    exact_match_id: str | None,
    cfg: dict,
) -> list[Violation]:
    """R09 -- Fuzzy duplicate and R10 -- Near-identical amount.

    Returns 0, 1, or 2 violations.
    """
    violations: list[Violation] = []
    r09_cfg = cfg["rules"]["R09"]
    r10_cfg = cfg["rules"]["R10"]
    fuzzy_cfg = cfg.get("fuzzy", {})
    weights = fuzzy_cfg.get("weights", {"vendor": 0.35, "invoice_number": 0.30,
                                         "amount": 0.20, "date": 0.15})
    gate = fuzzy_cfg.get("invoice_number_gate", 0.80)
    strong = fuzzy_cfg.get("strong", 0.85)
    weak = fuzzy_cfg.get("weak", 0.70)
    near_amt_pct = fuzzy_cfg.get("near_amount_pct", 1.0)
    date_window = fuzzy_cfg.get("date_window_days", 7)

    if not r09_cfg.get("enabled", True):
        return violations

    nv_rec = normalize_vendor(rec.get("vendor_name"))
    ninv_rec = normalize_invoice_number(rec.get("invoice_number"))
    rec_amount = rec.get("total_amount")
    rec_date_str = rec.get("invoice_date")

    best_combined = 0.0
    best_cand = None
    best_detail = {}

    for cand in candidates:
        # Skip if this candidate is the exact-duplicate match
        if exact_match_id and cand["invoice_id"] == exact_match_id:
            continue

        nv_cand = normalize_vendor(cand.get("vendor_name"))
        ninv_cand = normalize_invoice_number(cand.get("invoice_number"))

        # Invoice number gate (cheap string op -- do first)
        inv_sim = fuzz.ratio(ninv_rec, ninv_cand) / 100.0
        if inv_sim < gate:
            continue

        # Vendor similarity
        vendor_sim = fuzz.token_set_ratio(nv_rec, nv_cand) / 100.0

        # Amount similarity
        cand_amount = cand.get("total_amount")
        if rec_amount and cand_amount and max(rec_amount, cand_amount) > 0:
            amount_sim = 1 - abs(rec_amount - cand_amount) / max(rec_amount, cand_amount)
            amount_diff_pct = abs(rec_amount - cand_amount) / max(rec_amount, cand_amount) * 100
        else:
            amount_sim = 0.0
            amount_diff_pct = 100.0

        # Date similarity
        days_apart = 0
        if rec_date_str and cand.get("invoice_date"):
            try:
                d1 = datetime.strptime(rec_date_str, "%Y-%m-%d")
                d2 = datetime.strptime(cand["invoice_date"], "%Y-%m-%d")
                days_apart = abs((d1 - d2).days)
            except (ValueError, TypeError):
                days_apart = date_window
        date_sim = 1 - min(days_apart, date_window) / date_window

        # Combined score
        combined = (
            weights["vendor"] * vendor_sim
            + weights["invoice_number"] * inv_sim
            + weights["amount"] * amount_sim
            + weights["date"] * date_sim
        )

        if combined > best_combined:
            best_combined = combined
            best_cand = cand
            best_detail = {
                "vendor_similarity": round(vendor_sim, 2),
                "invoice_number_similarity": round(inv_sim, 2),
                "amount_difference_pct": round(amount_diff_pct, 1),
                "days_apart": days_apart,
                "combined_similarity": round(combined, 2),
            }

    if best_cand is None or best_combined < weak:
        return violations

    # R09 fires
    if best_combined >= strong:
        penalty = r09_cfg.get("penalty", 0.35)
    else:
        penalty = r09_cfg.get("penalty_weak", 0.20)

    matched_id = best_cand["invoice_id"]
    violations.append(Violation(
        rule_id="R09",
        name="Fuzzy duplicate",
        severity="soft",
        penalty=penalty,
        exception_type="fuzzy_duplicate",
        message=f"Probable duplicate of {matched_id} ({best_combined:.0%} similar)",
        matched_record=matched_id,
        evidence=best_detail,
    ))

    # R10 -- near-identical amount
    if r10_cfg.get("enabled", True):
        if best_detail.get("amount_difference_pct", 100) <= near_amt_pct:
            violations.append(Violation(
                rule_id="R10",
                name="Near-identical amount",
                severity="soft",
                penalty=r10_cfg.get("penalty", 0.15),
                exception_type="fuzzy_duplicate",
                message=f"Amount within {best_detail['amount_difference_pct']:.1f}% of matched record {matched_id}",
                matched_record=matched_id,
                evidence={"amount_difference_pct": best_detail["amount_difference_pct"]},
            ))

    return violations


def r11(rec: dict, vendor_stats: dict, cfg: dict) -> Violation | None:
    """R11 -- Amount outlier (z-score > threshold vs vendor history).

    Uses vendor stats computed over all batch+history records for that vendor.
    Requires at least min_history+1 total records (so min_history other records exist).
    """
    r11_cfg = cfg["rules"]["R11"]
    if not r11_cfg.get("enabled", True):
        return None
    outlier_cfg = cfg.get("outlier", {})
    min_history = outlier_cfg.get("min_history", 5)
    z_threshold = outlier_cfg.get("z_threshold", 3.0)

    total = rec.get("total_amount")
    if total is None:
        return None

    nv = normalize_vendor(rec.get("vendor_name"))
    stats = vendor_stats.get(nv)
    if stats is None:
        return None

    count = stats["count"]
    mean = stats["mean"]
    std = stats["std"]

    # Need at least min_history OTHER records (this invoice is included in count)
    if count <= min_history:
        return None

    if std <= 0:
        return None

    # Use inclusive z-score (valid when count is large; avoids numerical instability)
    z = abs(total - mean) / std
    if z <= z_threshold:
        return None

    return Violation(
        rule_id="R11",
        name="Amount outlier",
        severity="soft",
        penalty=r11_cfg.get("penalty", 0.20),
        exception_type="amount_outlier",
        message=f"Amount is {z:.1f} standard deviations from this vendor's usual",
        evidence={"z_score": round(z, 2), "vendor_mean": round(mean, 2),
                   "vendor_std": round(std, 2)},
    )