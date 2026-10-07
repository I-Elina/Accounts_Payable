import csv
import io
from typing import Any
from backend.database import get_conn, row_to_dict
from backend.errors import ApiError


def _escape_cell(val: Any) -> Any:
    if isinstance(val, str) and len(val) > 0 and val[0] in ("=", "+", "-", "@"):
        return f"'{val}"
    return val


def generate_report_csv(upload_id: int, decision: str | None = None) -> io.BytesIO:
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM uploads WHERE id = ?", (upload_id,))
        if not cursor.fetchone():
            raise ApiError(
                code="NOT_FOUND",
                message=f"Upload with ID {upload_id} not found",
                details=[],
                status_code=404,
            )

        filter_decision = decision or "needs_review,exception"
        decisions = [d.strip() for d in filter_decision.split(",") if d.strip()]
        placeholders = ",".join("?" for _ in decisions)

        cursor.execute(
            f"""
            SELECT i.invoice_id, i.invoice_number, i.vendor_name, i.invoice_date,
                   i.total_amount, i.currency, d.decision, d.confidence,
                   d.exception_type, d.primary_reason, d.matched_record, d.review_status
            FROM invoices i
            JOIN decisions d ON i.id = d.invoice_pk
            WHERE i.upload_id = ? AND d.decision IN ({placeholders})
            ORDER BY d.confidence ASC, i.invoice_id ASC
            """,
            [upload_id] + decisions,
        )
        rows = cursor.fetchall()

        fieldnames = [
            "invoice_id",
            "invoice_number",
            "vendor_name",
            "invoice_date",
            "total_amount",
            "currency",
            "decision",
            "confidence",
            "exception_type",
            "primary_reason",
            "matched_record",
            "review_status",
        ]

        # Use StringIO and encode to UTF-8 with BOM
        stream = io.StringIO()
        writer = csv.writer(stream)
        writer.writerow(fieldnames)

        for r in rows:
            d = row_to_dict(r)
            row_values = [
                d["invoice_id"] or "",
                _escape_cell(d["invoice_number"] or ""),
                _escape_cell(d["vendor_name"] or ""),
                d["invoice_date"] or "",
                f"{d['total_amount']:.2f}" if d["total_amount"] is not None else "",
                d["currency"] or "INR",
                d["decision"] or "",
                f"{d['confidence']:.2f}" if d["confidence"] is not None else "",
                d["exception_type"] or "",
                _escape_cell(d["primary_reason"] or ""),
                _escape_cell(d["matched_record"] or ""),
                d["review_status"] or "",
            ]
            writer.writerow(row_values)

        # Prepend UTF-8 BOM (\ufeff)
        csv_bytes = ("\ufeff" + stream.getvalue()).encode("utf-8")
        return io.BytesIO(csv_bytes)
    finally:
        conn.close()
