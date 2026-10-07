"""Read invoice files (CSV/Excel), map columns, canonicalise types."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from engine.errors import IngestionError
from engine.normalize import parse_amount, parse_date


# ── Column alias mapping ────────────────────────────────────────────
COLUMN_ALIASES: dict[str, list[str]] = {
    "invoice_id":      ["invoice_id", "record_id", "id"],
    "invoice_number":  ["invoice_number", "invoice_no", "inv_no", "inv_number",
                        "bill_number", "bill_no"],
    "vendor_name":     ["vendor_name", "vendor", "supplier", "supplier_name"],
    "invoice_date":    ["invoice_date", "date", "bill_date"],
    "due_date":        ["due_date", "payment_due"],
    "currency":        ["currency", "curr"],
    "subtotal":        ["subtotal", "net_amount", "amount_before_tax"],
    "tax_amount":      ["tax_amount", "tax", "gst", "vat"],
    "total_amount":    ["total_amount", "total", "amount", "grand_total"],
    "category":        ["category", "expense_category"],
    "po_number":       ["po_number", "po", "purchase_order"],
    "description":     ["description", "details", "memo"],
}


def _normalize_header(col: str) -> str:
    """Lowercase, non-alphanumerics -> underscore."""
    import re
    return re.sub(r"[^a-z0-9]+", "_", col.lower()).strip("_")


def _map_columns(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, str]]:
    """Rename columns using the alias table.  Returns (df, mapping_used)."""
    normalised = {_normalize_header(c): c for c in df.columns}
    mapping: dict[str, str] = {}
    for canonical, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            if alias in normalised:
                mapping[normalised[alias]] = canonical
                break
    return df.rename(columns=mapping), mapping


def ingest(source, cfg: dict) -> tuple[list[dict], list[str]]:
    """Read *source* and return (records, warnings).

    *source* may be a file path (str / Path) or a pandas DataFrame.

    Raises:
        IngestionError: On unsupported format or missing required columns.
    """
    warnings: list[str] = []

    # ── 1. Read the data ────────────────────────────────────────────
    if isinstance(source, pd.DataFrame):
        df = source.copy()
    else:
        path = Path(source)
        ext = path.suffix.lower()
        if ext == ".csv":
            df = pd.read_csv(path, dtype=str)
        elif ext in (".xlsx", ".xls"):
            df = pd.read_excel(path, dtype=str)
        else:
            raise IngestionError(
                f"Unsupported file format: {ext}",
                [f"Expected .csv or .xlsx, got {ext}"],
            )

    if df.empty:
        raise IngestionError("File is empty", ["The uploaded file contains no rows"])

    # ── 2. Map columns ──────────────────────────────────────────────
    df, _ = _map_columns(df)

    # ── 3. Check required columns exist ─────────────────────────────
    required = cfg.get("required_fields",
                       ["invoice_number", "vendor_name", "invoice_date", "total_amount"])
    missing_cols = [f for f in required if f not in df.columns]
    if missing_cols:
        raise IngestionError(
            "Missing required columns",
            [f"Column not found: {c}" for c in missing_cols],
        )

    # ── 4. invoice_id handling ──────────────────────────────────────
    if "invoice_id" not in df.columns:
        df["invoice_id"] = [f"ROW-{i:04d}" for i in range(1, len(df) + 1)]
        warnings.append("invoice_id column missing; generated ROW-0001, ROW-0002, …")
    else:
        # Make duplicated invoice_ids unique
        dupes = df["invoice_id"].duplicated(keep=False)
        if dupes.any():
            counts: dict[str, int] = {}
            new_ids = []
            for val in df["invoice_id"]:
                if val in counts:
                    counts[val] += 1
                    new_ids.append(f"{val}-dup{counts[val]}")
                else:
                    counts[val] = 0
                    new_ids.append(val)
            df["invoice_id"] = new_ids
            warnings.append("Duplicate invoice_id values found; suffixed with -dupN")

    # ── 5. Add row_index, parse types, keep raw values ──────────────
    df["row_index"] = range(1, len(df) + 1)

    # Currency default
    currency_default = cfg.get("currency_default", "INR")
    if "currency" not in df.columns:
        df["currency"] = currency_default
    else:
        df["currency"] = df["currency"].fillna(currency_default)

    records: list[dict] = []
    for _, row in df.iterrows():
        rec: dict = {}
        for col in df.columns:
            rec[col] = row[col] if pd.notna(row[col]) else None

        # Keep raw values for evidence
        rec["raw_total_amount"] = rec.get("total_amount")
        rec["raw_invoice_date"] = rec.get("invoice_date")
        rec["raw_subtotal"] = rec.get("subtotal")
        rec["raw_tax_amount"] = rec.get("tax_amount")

        # Parse amounts
        rec["total_amount"] = parse_amount(rec.get("total_amount"))
        rec["subtotal"] = parse_amount(rec.get("subtotal"))
        rec["tax_amount"] = parse_amount(rec.get("tax_amount"))

        # Parse dates
        rec["invoice_date"] = parse_date(rec.get("invoice_date"))
        rec["due_date"] = parse_date(rec.get("due_date"))

        # Ensure row_index is int
        rec["row_index"] = int(rec["row_index"])

        records.append(rec)

    return records, warnings
