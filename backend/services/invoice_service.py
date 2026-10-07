import json
from typing import Any
from backend.database import get_conn, row_to_dict
from backend.errors import ApiError
from backend.schemas import (
    CanonicalInvoice,
    DecisionDetail,
    InvoiceDetailResponse,
    InvoiceListItem,
    PaginatedInvoicesResponse,
    ReviewHistoryItem,
)


SORT_COLUMN_MAP = {
    "confidence": "d.confidence",
    "invoice_date": "i.invoice_date",
    "total_amount": "i.total_amount",
    "vendor_name": "i.vendor_name",
    "invoice_id": "i.invoice_id",
}


def list_invoices(
    upload_id: int | None = None,
    decision: str | None = None,
    exception_type: str | None = None,
    review_status: str | None = None,
    category: str | None = None,
    search: str | None = None,
    min_confidence: float | None = None,
    max_confidence: float | None = None,
    sort: str | None = None,
    order: str | None = "asc",
    page: int = 1,
    page_size: int = 25,
) -> PaginatedInvoicesResponse:
    page = max(1, page)
    page_size = min(200, max(1, page_size))
    offset = (page - 1) * page_size

    where_clauses = []
    params: list[Any] = []

    if upload_id is not None:
        where_clauses.append("i.upload_id = ?")
        params.append(upload_id)

    if decision:
        decisions = [d.strip() for d in decision.split(",") if d.strip()]
        if decisions:
            placeholders = ",".join("?" for _ in decisions)
            where_clauses.append(f"d.decision IN ({placeholders})")
            params.extend(decisions)

    if exception_type:
        where_clauses.append("d.exception_type = ?")
        params.append(exception_type)

    if review_status:
        where_clauses.append("d.review_status = ?")
        params.append(review_status)

    if category:
        where_clauses.append("i.category = ?")
        params.append(category)

    if min_confidence is not None:
        where_clauses.append("d.confidence >= ?")
        params.append(min_confidence)

    if max_confidence is not None:
        where_clauses.append("d.confidence <= ?")
        params.append(max_confidence)

    if search:
        search_term = f"%{search.strip()}%"
        where_clauses.append("(i.invoice_id LIKE ? OR i.invoice_number LIKE ? OR i.vendor_name LIKE ?)")
        params.extend([search_term, search_term, search_term])

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    # Sort determination
    order_direction = "DESC" if order and order.lower() == "desc" else "ASC"
    if sort and sort in SORT_COLUMN_MAP:
        sort_column = SORT_COLUMN_MAP[sort]
    elif review_status:
        sort_column = "d.confidence"
    else:
        sort_column = "i.invoice_id"

    conn = get_conn()
    try:
        count_cursor = conn.cursor()
        count_query = f"""
            SELECT COUNT(*)
            FROM invoices i
            JOIN decisions d ON i.id = d.invoice_pk
            {where_sql}
        """
        count_cursor.execute(count_query, params)
        total = count_cursor.fetchone()[0]

        data_cursor = conn.cursor()
        data_query = f"""
            SELECT i.id, i.upload_id, i.invoice_id, i.invoice_number, i.vendor_name,
                   i.invoice_date, i.total_amount, i.currency, i.category,
                   d.decision, d.confidence, d.exception_type, d.primary_reason, d.review_status
            FROM invoices i
            JOIN decisions d ON i.id = d.invoice_pk
            {where_sql}
            ORDER BY {sort_column} {order_direction}, i.id ASC
            LIMIT ? OFFSET ?
        """
        data_cursor.execute(data_query, params + [page_size, offset])
        rows = data_cursor.fetchall()

        items = [InvoiceListItem(**row_to_dict(r)) for r in rows]

        return PaginatedInvoicesResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )
    finally:
        conn.close()


def get_invoice_detail(invoice_pk: int) -> InvoiceDetailResponse:
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT i.id, i.upload_id, i.invoice_id, i.invoice_number, i.vendor_name,
                   i.invoice_date, i.due_date, i.currency, i.subtotal, i.tax_amount,
                   i.total_amount, i.category, i.po_number, i.description,
                   d.id as decision_id, d.decision, d.confidence, d.pass_resolved_in,
                   d.exception_type, d.primary_reason, d.matched_record,
                   d.violations_json, d.evidence_json, d.ai_summary,
                   d.ai_suggested_action, d.ai_summary_status, d.review_status
            FROM invoices i
            JOIN decisions d ON i.id = d.invoice_pk
            WHERE i.id = ?
            """,
            (invoice_pk,),
        )
        row = cursor.fetchone()
        if not row:
            raise ApiError(
                code="NOT_FOUND",
                message=f"Invoice with ID {invoice_pk} not found",
                details=[],
                status_code=404,
            )

        data = row_to_dict(row)
        invoice_obj = CanonicalInvoice(
            id=data["id"],
            upload_id=data["upload_id"],
            invoice_id=data["invoice_id"],
            invoice_number=data["invoice_number"],
            vendor_name=data["vendor_name"],
            invoice_date=data["invoice_date"],
            due_date=data["due_date"],
            currency=data["currency"],
            subtotal=data["subtotal"],
            tax_amount=data["tax_amount"],
            total_amount=data["total_amount"],
            category=data["category"],
            po_number=data["po_number"],
            description=data["description"],
        )

        violations = json.loads(data["violations_json"]) if data["violations_json"] else []
        evidence = json.loads(data["evidence_json"]) if data["evidence_json"] else {}

        decision_obj = DecisionDetail(
            decision=data["decision"],
            confidence=data["confidence"],
            pass_resolved_in=data["pass_resolved_in"],
            exception_type=data["exception_type"],
            primary_reason=data["primary_reason"],
            matched_record=data["matched_record"],
            violations=violations,
            evidence=evidence,
            ai_summary=data["ai_summary"],
            ai_suggested_action=data["ai_suggested_action"],
            ai_summary_status=data["ai_summary_status"],
            review_status=data["review_status"],
        )

        # Lookup matched invoice if present
        matched_invoice_obj = None
        if data["matched_record"]:
            cursor.execute(
                """
                SELECT id, upload_id, invoice_id, invoice_number, vendor_name,
                       invoice_date, due_date, currency, subtotal, tax_amount,
                       total_amount, category, po_number, description
                FROM invoices
                WHERE upload_id = ? AND invoice_id = ?
                """,
                (data["upload_id"], data["matched_record"]),
            )
            matched_row = cursor.fetchone()
            if matched_row:
                matched_invoice_obj = CanonicalInvoice(**row_to_dict(matched_row))

        # Reviews
        cursor.execute(
            """
            SELECT id, reviewer, action, comment, reviewed_at
            FROM reviews
            WHERE decision_pk = ?
            ORDER BY id ASC
            """,
            (data["decision_id"],),
        )
        review_rows = cursor.fetchall()
        reviews = [ReviewHistoryItem(**row_to_dict(r)) for r in review_rows]

        return InvoiceDetailResponse(
            invoice=invoice_obj,
            decision=decision_obj,
            matched_invoice=matched_invoice_obj,
            reviews=reviews,
        )
    finally:
        conn.close()
