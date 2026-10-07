"""Exact duplicate detection and blocking/candidate set generation."""

from __future__ import annotations

from engine.normalize import normalize_vendor, normalize_invoice_number


def build_exact_index(
    records: list[dict],
    history: list[dict] | None = None,
) -> dict[str, str]:
    """Build exact-duplicate lookup.

    Key = (normalized_vendor, normalized_invoice_number, round(total, 2)).
    Records processed in (invoice_date, row_index) order.
    First occurrence is the original; later ones map to the original invoice_id.
    History items are always treated as earlier than batch items.

    Returns:
        dict mapping duplicate invoice_id -> original invoice_id.
    """
    seen: dict[tuple, str] = {}
    exact_matches: dict[str, str] = {}

    # History first (always "earlier")
    if history:
        for rec in history:
            total = rec.get("total_amount")
            if total is None:
                continue
            key = (
                normalize_vendor(rec.get("vendor_name")),
                normalize_invoice_number(rec.get("invoice_number")),
                round(total, 2),
            )
            if key not in seen:
                seen[key] = rec["invoice_id"]

    def _sort_key(r):
        return (r.get("invoice_date") or "", r.get("row_index", 0))

    for rec in sorted(records, key=_sort_key):
        total = rec.get("total_amount")
        if total is None:
            continue
        key = (
            normalize_vendor(rec.get("vendor_name")),
            normalize_invoice_number(rec.get("invoice_number")),
            round(total, 2),
        )
        if key in seen:
            exact_matches[rec["invoice_id"]] = seen[key]
        else:
            seen[key] = rec["invoice_id"]

    return exact_matches


def build_candidates(
    records: list[dict],
    history: list[dict] | None = None,
    blocking_days: int = 30,
    blocking_amount_pct: float = 10.0,
) -> dict[str, list[dict]]:
    """For each batch record, find earlier candidate records for fuzzy matching.

    A candidate is a record (batch or history) with:
    - invoice_date within +-blocking_days of this record
    - total_amount within blocking_amount_pct% of this record
    - dated strictly before this record (by date+row_index)

    Uses a sorted sliding window: O(n * window_size) instead of O(n^2).

    Returns:
        dict mapping invoice_id -> list of candidate record dicts.
    """
    from datetime import datetime

    # Build enriched list of ALL records (history + batch)
    all_records: list[dict] = []
    if history:
        for h in history:
            hr = dict(h)
            hr.setdefault("row_index", 0)
            hr["_is_history"] = True
            all_records.append(hr)
    for r in records:
        rr = dict(r)
        rr["_is_history"] = False
        all_records.append(rr)

    # Filter to records with valid dates and amounts; parse dates once
    valid: list[dict] = []
    for r in all_records:
        if r.get("invoice_date") and r.get("total_amount") is not None:
            try:
                r["_date_obj"] = datetime.strptime(r["invoice_date"], "%Y-%m-%d")
                valid.append(r)
            except (ValueError, TypeError):
                pass

    # Sort by (date, row_index) ascending
    valid.sort(key=lambda r: (r["_date_obj"], r.get("row_index", 0)))

    candidates: dict[str, list[dict]] = {}

    for i, rec in enumerate(valid):
        if rec["_is_history"]:
            continue  # build candidates for batch records only

        rec_date = rec["_date_obj"]
        rec_amount = rec["total_amount"]
        cands: list[dict] = []

        # Scan backwards from i-1; break when date gap exceeds blocking_days
        for j in range(i - 1, -1, -1):
            other = valid[j]
            days_diff = (rec_date - other["_date_obj"]).days
            if days_diff > blocking_days:
                break  # sorted: all earlier entries are also too far back

            # Amount within percentage
            other_amount = other.get("total_amount")
            if other_amount is None or rec_amount is None:
                continue
            denom = max(abs(rec_amount), abs(other_amount))
            if denom == 0:
                continue
            pct_diff = abs(rec_amount - other_amount) / denom * 100
            if pct_diff <= blocking_amount_pct:
                cands.append(other)

        candidates[rec["invoice_id"]] = cands

    return candidates