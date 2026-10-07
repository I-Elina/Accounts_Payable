"""Error injection utilities for Accounts Payable synthetic dataset generation.

Provides deterministic corruption functions for each canonical exception type:
- exact_duplicate (R06)
- fuzzy_duplicate (R09, R10)
- missing_field (R01)
- invalid_amount (R02)
- invalid_date (R03)
- future_date (R04)
- calculation_mismatch (R05)
- policy_limit (R07)
- unknown_vendor (R08)
- amount_outlier (R11)
"""

from __future__ import annotations

import copy
import random
from datetime import datetime, timedelta


def make_clean_invoice(
    invoice_id: str,
    invoice_number: str,
    vendor_name: str,
    invoice_date: str,
    subtotal: float,
    category: str,
    po_number: str | None = None,
    description: str | None = None,
    currency: str = "INR",
) -> dict:
    """Construct a clean, valid invoice dictionary matching canonical contract schema."""
    subtotal = round(subtotal, 2)
    tax_amount = round(subtotal * 0.18, 2)
    total_amount = round(subtotal + tax_amount, 2)

    try:
        inv_dt = datetime.strptime(invoice_date, "%Y-%m-%d")
        due_date = (inv_dt + timedelta(days=30)).strftime("%Y-%m-%d")
    except Exception:
        due_date = None

    if po_number is None:
        po_number = f"PO-2026-{random.randint(1000, 9999)}"

    if description is None:
        description = f"Standard invoice for {category.lower()}"

    return {
        "invoice_id": invoice_id,
        "invoice_number": invoice_number,
        "vendor_name": vendor_name,
        "invoice_date": invoice_date,
        "due_date": due_date,
        "currency": currency,
        "subtotal": subtotal,
        "tax_amount": tax_amount,
        "total_amount": total_amount,
        "category": category,
        "po_number": po_number,
        "description": description,
    }


def inject_exact_duplicate(
    source_row: dict,
    new_invoice_id: str,
    rng: random.Random,
) -> tuple[dict, str]:
    """Create an exact duplicate of an earlier invoice.
    
    Shares vendor, invoice_number, and total_amount. Date is identical or +1-3 days later.
    """
    row = copy.deepcopy(source_row)
    row["invoice_id"] = new_invoice_id

    # Keep date identical or within 1-3 days (keeping day in 13..28)
    orig_dt = datetime.strptime(source_row["invoice_date"], "%Y-%m-%d")
    shift = rng.choice([0, 1, 2, 3])
    new_day = min(28, orig_dt.day + shift)
    new_dt = orig_dt.replace(day=new_day)
    row["invoice_date"] = new_dt.strftime("%Y-%m-%d")
    if row.get("due_date"):
        row["due_date"] = (new_dt + timedelta(days=30)).strftime("%Y-%m-%d")

    return row, source_row["invoice_id"]


def inject_fuzzy_duplicate(
    source_row: dict,
    new_invoice_id: str,
    rng: random.Random,
) -> tuple[dict, str]:
    """Create a fuzzy duplicate of an earlier invoice.
    
    Shares invoice_number, uses legal vendor name variation (Pvt Ltd <-> Private Limited),
    total within ±0.1% to 1.0%, date ±1 to 3 days.
    """
    row = copy.deepcopy(source_row)
    row["invoice_id"] = new_invoice_id

    vname = source_row["vendor_name"]
    variants = [
        ("Pvt Ltd", "Private Limited"),
        ("Private Limited", "Pvt Ltd"),
        ("Ltd", "Limited"),
        ("Limited", "Ltd"),
        ("Inc", "Technologies Inc"),
    ]
    applied = False
    for k, v in variants:
        if k in vname:
            vname = vname.replace(k, v)
            applied = True
            break
    if not applied:
        vname = vname + " Pvt Ltd"
    row["vendor_name"] = vname

    # Amount variation within ±0.2% to 0.8%
    delta_pct = rng.uniform(0.002, 0.008) * (-1 if rng.random() > 0.5 else 1)
    new_total = round(source_row["total_amount"] * (1.0 + delta_pct), 2)
    new_subtotal = round(new_total / 1.18, 2)
    new_tax = round(new_total - new_subtotal, 2)
    row["subtotal"] = new_subtotal
    row["tax_amount"] = new_tax
    row["total_amount"] = new_total

    # Date shift 1 to 3 days (safe day in 13..28)
    orig_dt = datetime.strptime(source_row["invoice_date"], "%Y-%m-%d")
    shift = rng.choice([1, 2, 3])
    new_day = min(28, max(13, orig_dt.day + shift))
    new_dt = orig_dt.replace(day=new_day)
    row["invoice_date"] = new_dt.strftime("%Y-%m-%d")
    if row.get("due_date"):
        row["due_date"] = (new_dt + timedelta(days=30)).strftime("%Y-%m-%d")

    return row, source_row["invoice_id"]


def inject_missing_field(row: dict, rng: random.Random) -> dict:
    """Blank out one required field: vendor_name, invoice_number, invoice_date, or total_amount."""
    field_to_blank = rng.choice(["vendor_name", "invoice_number", "invoice_date", "total_amount"])
    row[field_to_blank] = ""
    return row


def inject_invalid_amount(row: dict, rng: random.Random) -> dict:
    """Set total_amount to 0, negative, or unparseable text."""
    choice = rng.choice(["zero", "negative", "text"])
    if choice == "zero":
        row["total_amount"] = 0.0
    elif choice == "negative":
        row["total_amount"] = -1 * round(rng.uniform(100.0, 5000.0), 2)
    else:
        row["total_amount"] = "INVALID_AMOUNT"
    return row


def inject_invalid_date(row: dict, rng: random.Random) -> dict:
    """Corrupt invoice_date into an unparseable or nonsensical string."""
    bad_dates = ["31/31/2026", "not a date", "2026-02-30", "99/99/9999", "INVALID-DATE"]
    row["invoice_date"] = rng.choice(bad_dates)
    return row


def inject_future_date(row: dict, rng: random.Random, as_of_date: str = "2026-10-01") -> dict:
    """Set invoice_date strictly after as_of_date using unambiguous future dates."""
    future_dates = [
        "2026-10-15",
        "2026-10-22",
        "2026-11-18",
        "2026-11-25",
        "2026-12-14",
        "2026-12-20",
    ]
    fdate = rng.choice(future_dates)
    row["invoice_date"] = fdate
    if row.get("due_date"):
        fdt = datetime.strptime(fdate, "%Y-%m-%d")
        row["due_date"] = (fdt + timedelta(days=30)).strftime("%Y-%m-%d")
    return row


def inject_calculation_mismatch(row: dict, rng: random.Random) -> dict:
    """Alter total_amount so it differs from subtotal + tax by 2% to 20%."""
    diff_pct = rng.uniform(0.04, 0.18) * (-1 if rng.random() > 0.5 else 1)
    expected = row["subtotal"] + row["tax_amount"]
    altered_total = round(expected * (1.0 + diff_pct), 2)
    if altered_total <= 0 or abs(altered_total - expected) / expected < 0.01:
        altered_total = round(expected * 1.10, 2)
    row["total_amount"] = altered_total
    return row


def inject_policy_limit(row: dict, rng: random.Random, limit: float = 100000.0) -> dict:
    """Set total_amount between 110,000 and 400,000 while maintaining valid math."""
    total = round(rng.uniform(115000.0, 380000.0), 2)
    subtotal = round(total / 1.18, 2)
    tax_amount = round(total - subtotal, 2)
    row["subtotal"] = subtotal
    row["tax_amount"] = tax_amount
    row["total_amount"] = total
    return row


def inject_unknown_vendor(
    row: dict,
    rng: random.Random,
    unknown_vendors: list[str] | None = None,
) -> dict:
    """Assign an unapproved vendor not in vendor master, or an unapproved category."""
    if unknown_vendors is None:
        unknown_vendors = [
            "Global Unknown Corp",
            "Apex Offshore Holdings",
            "Universal Logistics S.A.",
            "Pacific Cybertech LLC",
            "Titan Enterprise Solutions Ltd",
            "Zenith Global Services",
        ]

    mode = rng.choice(["vendor", "category"])
    if mode == "vendor":
        row["vendor_name"] = rng.choice(unknown_vendors)
    else:
        unapproved_categories = ["Cryptocurrency", "Entertainment", "Hospitality Gaming", "Personal Expense"]
        row["category"] = rng.choice(unapproved_categories)
    return row


def inject_amount_outlier(
    row: dict,
    vendor_mean: float,
    rng: random.Random,
) -> dict:
    """Set total_amount to 8-10x vendor mean, keeping it strictly below 98,000 policy ceiling."""
    multiplier = rng.uniform(8.0, 9.5)
    target_total = round(vendor_mean * multiplier, 2)
    # Ensure it stays below policy limit 100,000 so only R11 fires
    if target_total >= 95000.0:
        target_total = round(rng.uniform(75000.0, 92000.0), 2)
    elif target_total < 45000.0:
        target_total = round(rng.uniform(50000.0, 80000.0), 2)

    subtotal = round(target_total / 1.18, 2)
    tax = round(target_total - subtotal, 2)
    row["subtotal"] = subtotal
    row["tax_amount"] = tax
    row["total_amount"] = target_total
    return row
