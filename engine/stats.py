"""Vendor statistics for outlier detection (R11)."""

from __future__ import annotations

import math

from engine.normalize import normalize_vendor


def build_vendor_stats(
    records: list[dict],
    history: list[dict] | None = None,
) -> dict[str, dict]:
    """Compute per-vendor mean and std of total_amount.

    Returns:
        dict[normalized_vendor_name -> {"mean": float, "std": float, "count": int}]
    """
    from collections import defaultdict

    amounts: dict[str, list[float]] = defaultdict(list)

    all_records = list(records)
    if history:
        all_records.extend(history)

    for rec in all_records:
        vendor = normalize_vendor(rec.get("vendor_name"))
        total = rec.get("total_amount")
        if vendor and total is not None:
            amounts[vendor].append(float(total))

    stats: dict[str, dict] = {}
    for vendor, vals in amounts.items():
        n = len(vals)
        if n == 0:
            continue
        mean = sum(vals) / n
        if n >= 2:
            variance = sum((v - mean) ** 2 for v in vals) / (n - 1)  # sample std
            std = math.sqrt(variance)
        else:
            std = 0.0
        stats[vendor] = {"mean": mean, "std": std, "count": n}

    return stats
