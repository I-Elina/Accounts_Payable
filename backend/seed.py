import asyncio
from pathlib import Path
from fastapi import UploadFile
from backend.database import init_db
from backend.services.upload_service import process_upload
from backend.settings import REPO_ROOT

DEMO_CSV_CONTENT = """invoice_id,invoice_number,vendor_name,invoice_date,due_date,currency,subtotal,tax_amount,total_amount,category,po_number,description
INV-0987,AC/2026/0345,Acme Private Limited,2026-09-02,2026-10-02,INR,8491.53,1528.47,10020.00,Office Supplies,PO-9812,Office supplies and stationery
INV-1042,AC/2026/0345,Acme Pvt Ltd,2026-09-03,2026-10-03,INR,8474.58,1525.42,10000.00,Office Supplies,PO-9815,Paper and pens
INV-1001,AC/2026/0001,Infosys Limited,2026-08-15,2026-09-15,INR,12711.86,2288.14,15000.00,IT Equipment,,Laptops maintenance
INV-1055,TC/2026/9912,Tata Consultancy Services,2026-09-10,2026-10-10,INR,105932.20,19067.80,125000.00,Professional Services,,Consulting retainer
INV-1088,DL/2026/1102,Dell Technologies Inc,2026-09-15,2026-10-15,INR,38135.59,6864.41,45000.00,IT Equipment,,Servers
INV-1110,MS/2026/0091,Microsoft India Pvt Ltd,2026-09-20,2026-10-20,INR,0.00,0.00,0.00,Software & Licenses,,Azure credit adjustment
"""


async def run_seed():
    print("Initializing database...")
    init_db()

    demo_path = REPO_ROOT / "data" / "processed" / "invoices_demo.csv"
    if not demo_path.exists():
        print("Demo CSV not found in data/processed/, generating standalone seed data...")
        demo_path.parent.mkdir(parents=True, exist_ok=True)
        with open(demo_path, "w", encoding="utf-8") as f:
            f.write(DEMO_CSV_CONTENT)

    print(f"Loading seed file from {demo_path}...")
    with open(demo_path, "rb") as f:
        file_bytes = f.read()

    from io import BytesIO
    upload_file = UploadFile(
        file=BytesIO(file_bytes),
        filename="invoices_demo.csv",
        headers={"content-type": "text/csv"},
    )

    result = await process_upload(file=upload_file, uploaded_by="system-seed", use_history=False)
    print(f"Seed complete! Upload ID: {result.upload_id}, Processed: {result.summary.total} rows.")
    print(f"Auto-pass: {result.summary.auto_pass}, Needs review: {result.summary.needs_review}, Exception: {result.summary.exception}")


if __name__ == "__main__":
    asyncio.run(run_seed())
