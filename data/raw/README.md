# Raw Data Sources & Synthetic Accounting Generation

## Overview
This directory contains raw base reference schemas, generator outputs, and receipt/invoice extraction structures used for the **Cache Me If You Can** Accounts Payable Exception Assistant (Microsoft Innovate Hackathon 2026).

## Upstream Sources
1. **Synthetic Accounting Data Generator**
   - **Repository:** [`https://github.com/R3n0va/synthetic-accounting-data-generator`](https://github.com/R3n0va/synthetic-accounting-data-generator)
   - **Author:** Artur Tolasov (R3n0va)
   - **Domain:** Enterprise relational accounting datasets spanning 35 relational tables across General Ledger, Accounts Payable, Accounts Receivable, and Cash Operations.
   - **Role in Project:** Informs the realistic distributions of transaction amounts, invoice frequencies, vendor hierarchies, and controlled data-quality anomaly types.

2. **SROIE / Enterprise Invoicing Patterns**
   - Realistic naming variants for Indian business entities (`Pvt Ltd`, `Private Limited`, `Ltd`, `Inc`).
   - Standard 18% GST calculation conventions (`tax_amount = round(subtotal * 0.18, 2)`, `total_amount = round(subtotal + tax_amount, 2)`).
   - Enterprise purchase order (`PO-2026-XXXX`) and vendor invoice numbering conventions (`AC/2026/XXXX`, `TCS/2026/XXXX`, etc.).

## Canonical Mapping
All raw accounting structures are transformed into the canonical single-table Accounts Payable schema defined in `contracts/CONTRACT.md` (§5):
- `invoice_id`: Canonical internal identifier (`INV-0001`, `INV-1042`, etc.)
- `invoice_number`: Vendor's invoice number (`AC/2026/0345`, etc.)
- `vendor_name`: Vendor legal name from `data/reference/vendor_master.csv`
- `invoice_date`: ISO `YYYY-MM-DD` between `2025-10-01` and `2026-09-25`
- `due_date`: ISO `YYYY-MM-DD` (typically invoice_date + 30 days)
- `currency`: Fixed `INR`
- `subtotal`: Net taxable amount (₹500 to ₹90,000 log-normal)
- `tax_amount`: 18% GST
- `total_amount`: Subtotal + Tax
- `category`: Approved expense categories
- `po_number`: Associated PO reference
- `description`: Line item or expense memo

## Maintenance Rule
Files in `data/raw/` are immutable snapshots. Processed datasets in `data/processed/` are deterministically generated and reproduced via `scripts/generate_dataset.py`.
