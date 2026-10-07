#!/usr/bin/env python3
"""Dataset generator for Accounts Payable Exception Assistant.

Generates synthetic invoices and corresponding answer keys matching
the specifications in contracts/CONTRACT.md and docs/team_guides/04_MEMBER4_DATA_QA_DOCS.md.

Usage:
  python scripts/generate_dataset.py --n 1000 --error-rate 0.184 --seed 42 \
    --out data/processed/invoices_train.csv --key-out data/processed/answer_key_train.csv
"""

from __future__ import annotations

import argparse
import csv
import math
import os
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Ensure repository root is in python path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.inject_errors import (
    inject_amount_outlier,
    inject_calculation_mismatch,
    inject_exact_duplicate,
    inject_future_date,
    inject_fuzzy_duplicate,
    inject_invalid_amount,
    inject_invalid_date,
    inject_missing_field,
    inject_policy_limit,
    inject_unknown_vendor,
    make_clean_invoice,
)

CANONICAL_COLUMNS = [
    "invoice_id",
    "invoice_number",
    "vendor_name",
    "invoice_date",
    "due_date",
    "currency",
    "subtotal",
    "tax_amount",
    "total_amount",
    "category",
    "po_number",
    "description",
]

ANSWER_KEY_COLUMNS = [
    "invoice_id",
    "is_bad",
    "expected_exception_type",
    "matched_record",
    "note",
]

ALLOWED_CATEGORIES = [
    "Office Supplies",
    "IT Equipment",
    "Software & Licenses",
    "Travel",
    "Utilities",
    "Professional Services",
    "Marketing",
    "Logistics",
    "Maintenance",
    "Raw Materials",
]

VENDOR_PREFIXES = {
    "Acme Pvt Ltd": "AC",
    "Apex Solutions Private Limited": "APX",
    "Blue Dart Express Ltd": "BD",
    "Cognizant Technology Solutions": "CTS",
    "Dell Technologies Inc": "DELL",
    "FedEx Express Logistics": "FDX",
    "Godrej Interio Ltd": "GDJ",
    "HCL Technologies Limited": "HCL",
    "HP India Sales Pvt Ltd": "HP",
    "Infosys Limited": "INFY",
    "ITC Infotech India Ltd": "ITC",
    "KPMG Advisory Services": "KPMG",
    "Larsen and Toubro Infotech": "LTI",
    "Lenovo India Private Limited": "LEN",
    "MakeMyTrip India Pvt Ltd": "MMT",
    "Microsoft India Pvt Ltd": "MSFT",
    "Oracle India Private Limited": "ORCL",
    "Persistent Systems Ltd": "PSYS",
    "PwC India Advisory": "PWC",
    "Reliance Retail Limited": "REL",
    "Samsung India Electronics": "SMSG",
    "Siemens Industry Software": "SIEM",
    "Tata Consultancy Services": "TCS",
    "Wipro Enterprises Limited": "WIP",
    "Zoho Corporation Pvt Ltd": "ZOHO",
}


def load_vendors(vendor_master_path: str = "data/reference/vendor_master.csv") -> list[str]:
    """Load vendor names from reference CSV."""
    p = Path(vendor_master_path)
    if not p.exists():
        return list(VENDOR_PREFIXES.keys())
    vendors = []
    with open(p, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            vendors.append(row["vendor_name"])
    return vendors or list(VENDOR_PREFIXES.keys())


def random_safe_date(rng: random.Random) -> str:
    """Generate ISO date between 2025-10-13 and 2026-09-25 with day in 13..28 to avoid month-swapping."""
    year_months = [
        (2025, 10), (2025, 11), (2025, 12),
        (2026, 1), (2026, 2), (2026, 3), (2026, 4), (2026, 5), (2026, 6), (2026, 7), (2026, 8), (2026, 9)
    ]
    yr, mo = rng.choice(year_months)
    day = rng.randint(13, 28)
    return f"{yr:04d}-{mo:02d}-{day:02d}"


def compute_error_counts(total_n: int, error_rate: float) -> dict[str, int]:
    """Compute error distribution scaled proportionally from 184 errors per 1000 rows."""
    base_counts = {
        "exact_duplicate": 40,
        "fuzzy_duplicate": 30,
        "missing_field": 30,
        "invalid_amount": 12,
        "invalid_date": 5,
        "future_date": 10,
        "calculation_mismatch": 25,
        "policy_limit": 15,
        "unknown_vendor": 10,
        "amount_outlier": 7,
    }
    base_total = sum(base_counts.values())  # 184
    target_errors = int(round(total_n * error_rate))

    scale = target_errors / base_total
    scaled_counts = {}
    current_sum = 0
    keys = list(base_counts.keys())
    for k in keys[:-1]:
        c = max(1, int(round(base_counts[k] * scale)))
        scaled_counts[k] = c
        current_sum += c
    scaled_counts[keys[-1]] = max(1, target_errors - current_sum)
    return scaled_counts


def generate_dataset(
    n: int = 1000,
    error_rate: float = 0.184,
    seed: int = 42,
    plant_demo: bool = False,
    vendor_master_path: str = "data/reference/vendor_master.csv",
) -> tuple[list[dict], list[dict]]:
    """Generate invoices and corresponding answer keys with exact count guarantees."""
    rng = random.Random(seed)
    vendors = load_vendors(vendor_master_path)
    error_counts = compute_error_counts(n, error_rate)
    total_errors = sum(error_counts.values())
    clean_n = n - total_errors

    # Deterministic base mean per vendor between 4,000 and 8,000 INR
    vendor_means = {}
    for i, v in enumerate(vendors):
        vendor_means[v] = 4000.0 + ((hash(v) % 15) * 350.0)

    clean_invoices: list[dict] = []
    corrupted_invoices: list[dict] = []
    answer_key_map: dict[str, dict] = {}
    used_ids: set[str] = set()

    # Pre-generate unique random invoice numbers per vendor with low similarity to prevent false R09
    vendor_used_numbers: dict[str, set[str]] = {v: set() for v in vendors}

    def generate_unique_inv_num(v: str) -> str:
        prefix = VENDOR_PREFIXES.get(v, "INV")
        chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
        while True:
            code = "".join(rng.choices(chars, k=6))
            num = f"{prefix}/2026/{code}"
            if num not in vendor_used_numbers[v]:
                vendor_used_numbers[v].add(num)
                return num

    planted_bad_by_type: dict[str, list[dict]] = {k: [] for k in error_counts.keys()}

    if plant_demo:
        inv_0987 = {
            "invoice_id": "INV-0987",
            "invoice_number": "AC/2026/0345",
            "vendor_name": "Acme Private Limited",
            "invoice_date": "2026-09-02",
            "due_date": "2026-10-02",
            "currency": "INR",
            "subtotal": 8491.53,
            "tax_amount": 1528.47,
            "total_amount": 10020.0,
            "category": "Office Supplies",
            "po_number": "PO-2026-0345",
            "description": "Ergonomic workstations and office setup",
        }
        inv_0500 = {
            "invoice_id": "INV-0500",
            "invoice_number": "TCS/2026/0890",
            "vendor_name": "Tata Consultancy Services",
            "invoice_date": "2026-06-15",
            "due_date": "2026-07-15",
            "currency": "INR",
            "subtotal": 45000.0,
            "tax_amount": 8100.0,
            "total_amount": 53100.0,
            "category": "Professional Services",
            "po_number": "PO-2026-0890",
            "description": "IT enterprise cloud migration milestone 1",
        }
        for r in [inv_0987, inv_0500]:
            clean_invoices.append(r)
            used_ids.add(r["invoice_id"])
            vendor_used_numbers[r["vendor_name"] if r["vendor_name"] in vendor_used_numbers else vendors[0]].add(r["invoice_number"])
            answer_key_map[r["invoice_id"]] = {
                "invoice_id": r["invoice_id"],
                "is_bad": 0,
                "expected_exception_type": "none",
                "matched_record": "",
                "note": "Clean showcase baseline",
            }

        inv_1042 = {
            "invoice_id": "INV-1042",
            "invoice_number": "AC/2026/0345",
            "vendor_name": "Acme Pvt Ltd",
            "invoice_date": "2026-09-03",
            "due_date": "2026-10-03",
            "currency": "INR",
            "subtotal": 8474.58,
            "tax_amount": 1525.42,
            "total_amount": 10000.0,
            "category": "Office Supplies",
            "po_number": "PO-2026-0345",
            "description": "Ergonomic workstations duplicate claim",
        }
        inv_0501 = {
            "invoice_id": "INV-0501",
            "invoice_number": "TCS/2026/0890",
            "vendor_name": "Tata Consultancy Services",
            "invoice_date": "2026-06-17",
            "due_date": "2026-07-17",
            "currency": "INR",
            "subtotal": 45000.0,
            "tax_amount": 8100.0,
            "total_amount": 53100.0,
            "category": "Professional Services",
            "po_number": "PO-2026-0890",
            "description": "IT enterprise cloud migration duplicate claim",
        }
        inv_0100 = {
            "invoice_id": "INV-0100",
            "invoice_number": "MSFT/2026/0112",
            "vendor_name": "",
            "invoice_date": "2026-05-18",
            "due_date": "2026-06-18",
            "currency": "INR",
            "subtotal": 25000.0,
            "tax_amount": 4500.0,
            "total_amount": 29500.0,
            "category": "Software & Licenses",
            "po_number": "PO-2026-0112",
            "description": "Cloud subscription enterprise seat renewal",
        }
        inv_0200 = {
            "invoice_id": "INV-0200",
            "invoice_number": "DELL/2026/0441",
            "vendor_name": "Dell Technologies Inc",
            "invoice_date": "2026-11-15",
            "due_date": "2026-12-15",
            "currency": "INR",
            "subtotal": 35000.0,
            "tax_amount": 6300.0,
            "total_amount": 41300.0,
            "category": "IT Equipment",
            "po_number": "PO-2026-0441",
            "description": "High performance server development unit",
        }
        inv_0300 = {
            "invoice_id": "INV-0300",
            "invoice_number": "INFY/2026/0772",
            "vendor_name": "Infosys Limited",
            "invoice_date": "2026-07-22",
            "due_date": "2026-08-22",
            "currency": "INR",
            "subtotal": 200000.0,
            "tax_amount": 36000.0,
            "total_amount": 236000.0,
            "category": "Professional Services",
            "po_number": "PO-2026-0772",
            "description": "Global ERP consolidation master retainership",
        }

        planted_bad_by_type["fuzzy_duplicate"].append(inv_1042)
        planted_bad_by_type["exact_duplicate"].append(inv_0501)
        planted_bad_by_type["missing_field"].append(inv_0100)
        planted_bad_by_type["future_date"].append(inv_0200)
        planted_bad_by_type["policy_limit"].append(inv_0300)

        demo_keys = [
            ("INV-1042", "fuzzy_duplicate", "INV-0987", "Planted showcase fuzzy duplicate"),
            ("INV-0501", "exact_duplicate", "INV-0500", "Planted showcase exact duplicate"),
            ("INV-0100", "missing_field", "", "Planted showcase missing vendor"),
            ("INV-0200", "future_date", "", "Planted showcase future date"),
            ("INV-0300", "policy_limit", "", "Planted showcase policy limit"),
        ]
        for iid, etype, mrec, note in demo_keys:
            used_ids.add(iid)
            answer_key_map[iid] = {
                "invoice_id": iid,
                "is_bad": 1,
                "expected_exception_type": etype,
                "matched_record": mrec,
                "note": note,
            }

    # Generate remaining clean invoices
    seq = 1
    while len(clean_invoices) < clean_n:
        inv_id = f"INV-{seq:04d}"
        seq += 1
        if inv_id in used_ids:
            continue
        used_ids.add(inv_id)

        vendor = vendors[len(clean_invoices) % len(vendors)]
        inv_num = generate_unique_inv_num(vendor)
        inv_date = random_safe_date(rng)

        # Normal variance ±10% around base mean (guaranteed z < 1.5, never an outlier)
        base_mean = vendor_means[vendor]
        subtotal = round(base_mean * rng.uniform(0.90, 1.10), 2)

        category = ALLOWED_CATEGORIES[len(clean_invoices) % len(ALLOWED_CATEGORIES)]
        rec = make_clean_invoice(
            invoice_id=inv_id,
            invoice_number=inv_num,
            vendor_name=vendor,
            invoice_date=inv_date,
            subtotal=subtotal,
            category=category,
        )
        clean_invoices.append(rec)
        answer_key_map[inv_id] = {
            "invoice_id": inv_id,
            "is_bad": 0,
            "expected_exception_type": "none",
            "matched_record": "",
            "note": "Clean baseline invoice",
        }

    # Generate corrupted invoices
    for err_type, count in error_counts.items():
        # First include planted items of this type
        for p in planted_bad_by_type[err_type]:
            corrupted_invoices.append(p)

        rem_count = count - len(planted_bad_by_type[err_type])
        for _ in range(rem_count):
            while True:
                new_id = f"INV-{seq:04d}"
                seq += 1
                if new_id not in used_ids:
                    used_ids.add(new_id)
                    break

            if err_type == "exact_duplicate":
                source = rng.choice(clean_invoices[:len(clean_invoices)//2])
                dup_row, matched_id = inject_exact_duplicate(source, new_id, rng)
                corrupted_invoices.append(dup_row)
                answer_key_map[new_id] = {
                    "invoice_id": new_id,
                    "is_bad": 1,
                    "expected_exception_type": "exact_duplicate",
                    "matched_record": matched_id,
                    "note": f"Exact duplicate of {matched_id}",
                }

            elif err_type == "fuzzy_duplicate":
                source = rng.choice(clean_invoices[:len(clean_invoices)//2])
                dup_row, matched_id = inject_fuzzy_duplicate(source, new_id, rng)
                corrupted_invoices.append(dup_row)
                answer_key_map[new_id] = {
                    "invoice_id": new_id,
                    "is_bad": 1,
                    "expected_exception_type": "fuzzy_duplicate",
                    "matched_record": matched_id,
                    "note": f"Fuzzy duplicate of {matched_id}",
                }

            else:
                vendor = vendors[rng.randint(0, len(vendors) - 1)]
                inv_num = generate_unique_inv_num(vendor)
                base_inv = make_clean_invoice(
                    invoice_id=new_id,
                    invoice_number=inv_num,
                    vendor_name=vendor,
                    invoice_date=random_safe_date(rng),
                    subtotal=round(vendor_means[vendor], 2),
                    category=rng.choice(ALLOWED_CATEGORIES),
                )

                if err_type == "missing_field":
                    row = inject_missing_field(base_inv, rng)
                    corrupted_invoices.append(row)
                    answer_key_map[new_id] = {
                        "invoice_id": new_id,
                        "is_bad": 1,
                        "expected_exception_type": "missing_field",
                        "matched_record": "",
                        "note": "Required field omitted",
                    }
                elif err_type == "invalid_amount":
                    row = inject_invalid_amount(base_inv, rng)
                    corrupted_invoices.append(row)
                    answer_key_map[new_id] = {
                        "invoice_id": new_id,
                        "is_bad": 1,
                        "expected_exception_type": "invalid_amount",
                        "matched_record": "",
                        "note": "Amount is non-positive or unparseable",
                    }
                elif err_type == "invalid_date":
                    row = inject_invalid_date(base_inv, rng)
                    corrupted_invoices.append(row)
                    answer_key_map[new_id] = {
                        "invoice_id": new_id,
                        "is_bad": 1,
                        "expected_exception_type": "invalid_date",
                        "matched_record": "",
                        "note": "Date format unparseable",
                    }
                elif err_type == "future_date":
                    row = inject_future_date(base_inv, rng, as_of_date="2026-10-01")
                    corrupted_invoices.append(row)
                    answer_key_map[new_id] = {
                        "invoice_id": new_id,
                        "is_bad": 1,
                        "expected_exception_type": "future_date",
                        "matched_record": "",
                        "note": "Invoice date occurs after as_of_date",
                    }
                elif err_type == "calculation_mismatch":
                    row = inject_calculation_mismatch(base_inv, rng)
                    corrupted_invoices.append(row)
                    answer_key_map[new_id] = {
                        "invoice_id": new_id,
                        "is_bad": 1,
                        "expected_exception_type": "calculation_mismatch",
                        "matched_record": "",
                        "note": "Total does not equal subtotal + tax",
                    }
                elif err_type == "policy_limit":
                    row = inject_policy_limit(base_inv, rng, limit=100000.0)
                    corrupted_invoices.append(row)
                    answer_key_map[new_id] = {
                        "invoice_id": new_id,
                        "is_bad": 1,
                        "expected_exception_type": "policy_limit",
                        "matched_record": "",
                        "note": "Total amount exceeds policy ceiling 100,000",
                    }
                elif err_type == "unknown_vendor":
                    row = inject_unknown_vendor(base_inv, rng)
                    corrupted_invoices.append(row)
                    answer_key_map[new_id] = {
                        "invoice_id": new_id,
                        "is_bad": 1,
                        "expected_exception_type": "unknown_vendor",
                        "matched_record": "",
                        "note": "Vendor not in master or disallowed category",
                    }
                elif err_type == "amount_outlier":
                    row = inject_amount_outlier(base_inv, vendor_means[vendor], rng)
                    corrupted_invoices.append(row)
                    answer_key_map[new_id] = {
                        "invoice_id": new_id,
                        "is_bad": 1,
                        "expected_exception_type": "amount_outlier",
                        "matched_record": "",
                        "note": "Amount exceeds 3 standard deviations for vendor",
                    }

    combined = clean_invoices + corrupted_invoices

    def sort_key(row):
        d_str = row.get("invoice_date") or "2099-12-31"
        try:
            dt = datetime.strptime(d_str, "%Y-%m-%d")
        except Exception:
            dt = datetime(2099, 1, 1)
        return dt

    combined.sort(key=sort_key)

    seen_ids = set()
    for idx, row in enumerate(combined):
        iid = row["invoice_id"]
        key_info = answer_key_map.get(iid)
        if key_info and key_info["matched_record"]:
            matched_id = key_info["matched_record"]
            if matched_id not in seen_ids:
                orig_idx = next((i for i, r in enumerate(combined) if r["invoice_id"] == matched_id), None)
                if orig_idx is not None and orig_idx > idx:
                    combined[idx], combined[orig_idx] = combined[orig_idx], combined[idx]
        seen_ids.add(combined[idx]["invoice_id"])

    final_keys = []
    for row in combined:
        iid = row["invoice_id"]
        final_keys.append(answer_key_map[iid])

    return combined, final_keys


def save_dataset(
    invoices: list[dict],
    keys: list[dict],
    out_csv: str,
    key_csv: str,
) -> None:
    """Save invoices and answer keys to CSV."""
    Path(out_csv).parent.mkdir(parents=True, exist_ok=True)
    Path(key_csv).parent.mkdir(parents=True, exist_ok=True)

    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CANONICAL_COLUMNS)
        writer.writeheader()
        writer.writerows(invoices)

    with open(key_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=ANSWER_KEY_COLUMNS)
        writer.writeheader()
        writer.writerows(keys)


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic AP invoices and answer keys.")
    parser.add_argument("--n", type=int, default=1000, help="Total number of invoices")
    parser.add_argument("--error-rate", type=float, default=0.184, help="Fraction of bad invoices")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--out", type=str, required=True, help="Output invoices CSV path")
    parser.add_argument("--key-out", type=str, required=True, help="Output answer key CSV path")
    parser.add_argument("--plant-demo", action="store_true", help="Plant demo showcase records")
    parser.add_argument("--vendor-master", type=str, default="data/reference/vendor_master.csv", help="Vendor master CSV")

    args = parser.parse_args()

    invoices, keys = generate_dataset(
        n=args.n,
        error_rate=args.error_rate,
        seed=args.seed,
        plant_demo=args.plant_demo,
        vendor_master_path=args.vendor_master,
    )

    save_dataset(invoices, keys, args.out, args.key_out)

    bad_count = sum(1 for k in keys if k["is_bad"] == 1)
    clean_count = sum(1 for k in keys if k["is_bad"] == 0)
    print(f"Dataset generated: {args.out}")
    print(f"Total rows: {len(invoices)} | Clean: {clean_count} | Bad: {bad_count} ({bad_count / len(invoices):.1%})")


if __name__ == "__main__":
    main()
