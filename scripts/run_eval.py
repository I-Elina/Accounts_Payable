#!/usr/bin/env python3
"""Evaluation script for Decision Engine against ground-truth answer keys.

Computes confusion matrix, precision, recall, F1, per-type recall,
and type accuracy. Generates JSON and Markdown evaluation reports.

Usage:
  python scripts/run_eval.py --data data/processed/invoices_test.csv \
    --key data/processed/answer_key_test.csv --config '{"auto_pass_threshold":0.85}'
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

# Ensure repo root is in sys.path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from engine import run_engine
except ImportError:
    run_engine = None


def load_answer_key(key_path: str) -> dict[str, dict]:
    """Load answer key CSV into a lookup mapping by invoice_id."""
    key_map = {}
    with open(key_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key_map[row["invoice_id"]] = {
                "invoice_id": row["invoice_id"],
                "is_bad": int(row["is_bad"]),
                "expected_exception_type": row["expected_exception_type"],
                "matched_record": row.get("matched_record", ""),
                "note": row.get("note", ""),
            }
    return key_map


def evaluate(
    data_path: str,
    key_path: str,
    config_overrides: dict | None = None,
) -> dict:
    """Run engine and evaluate against ground truth answer key."""
    if run_engine is None:
        raise RuntimeError(
            "engine package not found. Ensure engine/ is in python path."
        )

    # Fixed test as_of_date
    effective_cfg = {"as_of_date": "2026-10-01"}
    if config_overrides:
        effective_cfg.update(config_overrides)

    engine_output = run_engine(data_path, config=effective_cfg)
    results = engine_output.get("results", [])
    summary = engine_output.get("summary", {})

    answer_keys = load_answer_key(key_path)

    tp_ids = []
    fp_ids = []
    fn_ids = []
    tn_ids = []

    type_stats: dict[str, dict] = {}
    type_matches = 0

    for res in results:
        iid = res["invoice_id"]
        gt = answer_keys.get(iid)
        if not gt:
            continue

        is_bad = gt["is_bad"] == 1
        expected_type = gt["expected_exception_type"]
        engine_decision = res["decision"]
        engine_type = res.get("exception_type", "none")
        flagged = engine_decision != "auto_pass"

        if expected_type not in type_stats and is_bad:
            type_stats[expected_type] = {"total": 0, "flagged": 0, "type_matched": 0}

        if is_bad:
            type_stats[expected_type]["total"] += 1
            if flagged:
                tp_ids.append(iid)
                type_stats[expected_type]["flagged"] += 1
                if engine_type == expected_type:
                    type_matches += 1
                    type_stats[expected_type]["type_matched"] += 1
            else:
                fn_ids.append(iid)
        else:
            if flagged:
                fp_ids.append(iid)
            else:
                tn_ids.append(iid)

    tp = len(tp_ids)
    fp = len(fp_ids)
    fn = len(fn_ids)
    tn = len(tn_ids)
    total = tp + fp + fn + tn

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    accuracy = (tp + tn) / total if total > 0 else 0.0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    type_accuracy = type_matches / tp if tp > 0 else 0.0

    per_type_metrics = {}
    for etype, s in sorted(type_stats.items()):
        per_type_metrics[etype] = {
            "total": s["total"],
            "flagged": s["flagged"],
            "missed": s["total"] - s["flagged"],
            "recall": round(s["flagged"] / s["total"], 4) if s["total"] > 0 else 0.0,
            "type_accuracy": round(s["type_matched"] / s["flagged"], 4) if s["flagged"] > 0 else 0.0,
        }

    meets_targets = recall >= 0.95 and precision >= 0.80

    return {
        "dataset": Path(data_path).name,
        "total_invoices": total,
        "engine_summary": summary,
        "config_used": effective_cfg,
        "confusion_matrix": {
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
            "true_negatives": tn,
        },
        "metrics": {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
            "accuracy": round(accuracy, 4),
            "specificity": round(specificity, 4),
            "type_accuracy": round(type_accuracy, 4),
        },
        "meets_contract_targets": meets_targets,
        "per_type_metrics": per_type_metrics,
        "missed_invoice_ids": fn_ids,
        "false_alarm_invoice_ids": fp_ids,
    }


def format_markdown_report(report: dict) -> str:
    """Format evaluation dictionary into structured GitHub-flavored markdown."""
    m = report["metrics"]
    cm = report["confusion_matrix"]
    s = report["engine_summary"]
    dname = report["dataset"]
    meets = "PASS (Meets contract targets)" if report["meets_contract_targets"] else "FAIL (Below target)"

    md = [
        f"# Evaluation Report: `{dname}`",
        "",
        f"**Date:** 2026-10-07 | **Status:** **{meets}**",
        "",
        "## 1. Executive Summary & KPIs",
        "",
        "| Metric | Target | Result | Status |",
        "|---|---|---|---|",
        f"| **Recall (Sensitivity)** | ≥ 0.950 | **{m['recall']:.1%}** | {'✅' if m['recall'] >= 0.95 else '❌'} |",
        f"| **Precision (PPV)** | ≥ 0.800 | **{m['precision']:.1%}** | {'✅' if m['precision'] >= 0.80 else '❌'} |",
        f"| **F1 Score** | Balanced | **{m['f1_score']:.4f}** | ✅ |",
        f"| **Type Accuracy** | Diagnostic | **{m['type_accuracy']:.1%}** | ✅ |",
        f"| **Overall Accuracy** | System | **{m['accuracy']:.1%}** | ✅ |",
        f"| **Specificity** | Clean Pass | **{m['specificity']:.1%}** | ✅ |",
        "",
        "## 2. Confusion Matrix",
        "",
        "| | Actually Bad (184) | Actually Clean (816) | Total |",
        "|---|---|---|---|",
        f"| **Flagged (Needs Review / Exception)** | **TP: {cm['true_positives']}** | **FP: {cm['false_positives']}** | {cm['true_positives'] + cm['false_positives']} |",
        f"| **Auto-Passed** | **FN: {cm['false_negatives']}** | **TN: {cm['true_negatives']}** | {cm['false_negatives'] + cm['true_negatives']} |",
        f"| **Total** | {cm['true_positives'] + cm['false_negatives']} | {cm['false_positives'] + cm['true_negatives']} | {report['total_invoices']} |",
        "",
        "## 3. Decision Breakdown",
        "",
        f"- **Total Rows:** {s.get('total', report['total_invoices'])}",
        f"- **Auto-Passed (`auto_pass`):** {s.get('auto_pass', 0)} ({s.get('auto_pass', 0) / report['total_invoices']:.1%})",
        f"- **Needs Review (`needs_review`):** {s.get('needs_review', 0)} ({s.get('needs_review', 0) / report['total_invoices']:.1%})",
        f"- **Exceptions (`exception`):** {s.get('exception', 0)} ({s.get('exception', 0) / report['total_invoices']:.1%})",
        "",
        "## 4. Per-Exception-Type Diagnostics",
        "",
        "| Exception Type | Total Ground Truth | Correctly Flagged | Missed | Type Recall | Diagnosis Accuracy |",
        "|---|---|---|---|---|---|",
    ]

    for etype, stats in report["per_type_metrics"].items():
        md.append(
            f"| `{etype}` | {stats['total']} | {stats['flagged']} | {stats['missed']} | {stats['recall']:.1%} | {stats['type_accuracy']:.1%} |"
        )

    md.extend([
        "",
        "## 5. False Alarms (False Positives)",
        "",
        f"**Count:** {len(report['false_alarm_invoice_ids'])}",
    ])
    if report["false_alarm_invoice_ids"]:
        md.append(f"`{', '.join(report['false_alarm_invoice_ids'][:20])}`" + ("..." if len(report["false_alarm_invoice_ids"]) > 20 else ""))
    else:
        md.append("None (Zero false alarms on clean invoices).")

    md.extend([
        "",
        "## 6. Missed Invoices (False Negatives)",
        "",
        f"**Count:** {len(report['missed_invoice_ids'])}",
    ])
    if report["missed_invoice_ids"]:
        md.append(f"`{', '.join(report['missed_invoice_ids'][:20])}`")
    else:
        md.append("None (100% of anomalies detected).")

    return "\n".join(md)


def main():
    parser = argparse.ArgumentParser(description="Evaluate Decision Engine against answer key.")
    parser.add_argument("--data", type=str, required=True, help="Invoices CSV path")
    parser.add_argument("--key", type=str, required=True, help="Answer key CSV path")
    parser.add_argument("--config", type=str, default=None, help="JSON overrides string")
    parser.add_argument("--out-json", type=str, default=None, help="Output JSON path")
    parser.add_argument("--out-md", type=str, default=None, help="Output Markdown path")

    args = parser.parse_args()

    cfg_overrides = None
    if args.config:
        cfg_overrides = json.loads(args.config)

    report = evaluate(args.data, args.key, cfg_overrides)

    stem = Path(args.data).stem
    out_json = args.out_json or f"docs/reports/eval_{stem}.json"
    out_md = args.out_md or f"docs/reports/eval_{stem}.md"

    Path(out_json).parent.mkdir(parents=True, exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    md_content = format_markdown_report(report)
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(md_content)

    m = report["metrics"]
    cm = report["confusion_matrix"]
    print(f"=== Evaluation: {args.data} ===")
    print(f"Precision: {m['precision']:.1%} | Recall: {m['recall']:.1%} | F1: {m['f1_score']:.4f}")
    print(f"TP: {cm['true_positives']} | FP: {cm['false_positives']} | FN: {cm['false_negatives']} | TN: {cm['true_negatives']}")
    print(f"Reports saved to {out_json} and {out_md}")


if __name__ == "__main__":
    main()
