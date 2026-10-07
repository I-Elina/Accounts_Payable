"""Post-processing analytics: confidence calibration + vendor risk profiles."""

from __future__ import annotations

from collections import defaultdict


# Confidence score bands (label: [low, high))
CONFIDENCE_BANDS = [
    ("exception_zone",  0.00, 0.40),
    ("review_zone",     0.40, 0.85),
    ("pass_zone",       0.85, 1.01),  # 1.01 so 1.0 is included
]


def confidence_calibration(results: list[dict]) -> dict:
    """Compute confidence score distribution across all invoices.

    Returns:
        {
          "mean": float,
          "median": float,
          "std": float,
          "bands": {
              "exception_zone": {"count": int, "pct": float, "range": "0.00-0.40"},
              "review_zone":    {"count": int, "pct": float, "range": "0.40-0.85"},
              "pass_zone":      {"count": int, "pct": float, "range": "0.85-1.00"},
          },
          "per_decision": {
              "auto_pass":    {"count": int, "avg_confidence": float},
              "needs_review": {"count": int, "avg_confidence": float},
              "exception":    {"count": int, "avg_confidence": float},
          }
        }
    """
    if not results:
        return {}

    scores = [r["confidence"] for r in results]
    n = len(scores)

    mean = round(sum(scores) / n, 3)
    sorted_scores = sorted(scores)
    mid = n // 2
    median = round(
        sorted_scores[mid] if n % 2 else (sorted_scores[mid - 1] + sorted_scores[mid]) / 2,
        3,
    )
    variance = sum((s - mean) ** 2 for s in scores) / n
    std = round(variance ** 0.5, 3)

    # Bands
    bands: dict[str, dict] = {}
    for label, low, high in CONFIDENCE_BANDS:
        count = sum(1 for s in scores if low <= s < high)
        display_high = min(high, 1.0)
        bands[label] = {
            "count": count,
            "pct": round(count / n * 100, 1),
            "range": f"{low:.2f}-{display_high:.2f}",
        }

    # Per decision
    per_decision: dict[str, dict] = {}
    for decision in ("auto_pass", "needs_review", "exception"):
        group = [r["confidence"] for r in results if r["decision"] == decision]
        per_decision[decision] = {
            "count": len(group),
            "avg_confidence": round(sum(group) / len(group), 3) if group else 0.0,
        }

    return {
        "mean": mean,
        "median": median,
        "std": std,
        "bands": bands,
        "per_decision": per_decision,
    }


def vendor_risk_profiles(results: list[dict], history: list[dict] | None = None) -> list[dict]:
    """Compute per-vendor exception rates and flag high-risk vendors.

    A vendor is "high_risk" if their exception_rate >= 30% with >= 3 invoices.

    Returns:
        List of vendor profile dicts, sorted by exception_rate desc:
        [
          {
            "vendor_name": str,
            "total_invoices": int,
            "auto_pass": int,
            "needs_review": int,
            "exceptions": int,
            "exception_rate_pct": float,
            "top_violations": list[str],   # top 3 rule IDs by frequency
            "risk_flag": "high" | "medium" | "low",
          },
          ...
        ]
    """
    from engine.normalize import normalize_vendor

    # vendor_name -> stats
    vendor_stats: dict[str, dict] = defaultdict(lambda: {
        "raw_name": "",
        "total": 0,
        "auto_pass": 0,
        "needs_review": 0,
        "exception": 0,
        "violations": defaultdict(int),
    })

    for r in results:
        raw_name = (r.get("record") or {}).get("vendor_name") or ""
        nv = normalize_vendor(raw_name) or "__unknown__"
        vs = vendor_stats[nv]
        if not vs["raw_name"]:
            vs["raw_name"] = raw_name or nv
        vs["total"] += 1
        vs[r["decision"]] += 1
        for v in r.get("violations", []):
            vs["violations"][v["rule_id"]] += 1

    profiles: list[dict] = []
    for nv, vs in vendor_stats.items():
        total = vs["total"]
        exceptions = vs["exception"]
        exc_rate = round(exceptions / total * 100, 1) if total else 0.0

        # Top 3 rule IDs by frequency
        top_violations = sorted(vs["violations"], key=lambda k: -vs["violations"][k])[:3]

        # Risk flag
        if total >= 3 and exc_rate >= 30:
            risk_flag = "high"
        elif total >= 2 and exc_rate >= 15:
            risk_flag = "medium"
        else:
            risk_flag = "low"

        profiles.append({
            "vendor_name": vs["raw_name"],
            "total_invoices": total,
            "auto_pass": vs["auto_pass"],
            "needs_review": vs["needs_review"],
            "exceptions": exceptions,
            "exception_rate_pct": exc_rate,
            "top_violations": top_violations,
            "risk_flag": risk_flag,
        })

    # Sort: high risk first, then by exception rate desc
    risk_order = {"high": 0, "medium": 1, "low": 2}
    profiles.sort(key=lambda p: (risk_order[p["risk_flag"]], -p["exception_rate_pct"]))
    return profiles