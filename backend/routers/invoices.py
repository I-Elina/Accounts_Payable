import json
from fastapi import APIRouter, Query
from backend.ai.summary import generate_summary
from backend.database import get_conn, row_to_dict
from backend.errors import ApiError
from backend.schemas import (
    InvoiceDetailResponse,
    PaginatedInvoicesResponse,
    SummaryResponse,
)
from backend.services.audit_service import log_event
from backend.services.invoice_service import get_invoice_detail, list_invoices

router = APIRouter(prefix="/api/invoices", tags=["invoices"])


@router.get("", response_model=PaginatedInvoicesResponse)
def get_invoices(
    upload_id: int | None = Query(None),
    decision: str | None = Query(None),
    exception_type: str | None = Query(None),
    review_status: str | None = Query(None),
    category: str | None = Query(None),
    search: str | None = Query(None),
    min_confidence: float | None = Query(None),
    max_confidence: float | None = Query(None),
    sort: str | None = Query(None),
    order: str | None = Query("asc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
) -> PaginatedInvoicesResponse:
    return list_invoices(
        upload_id=upload_id,
        decision=decision,
        exception_type=exception_type,
        review_status=review_status,
        category=category,
        search=search,
        min_confidence=min_confidence,
        max_confidence=max_confidence,
        sort=sort,
        order=order,
        page=page,
        page_size=page_size,
    )


@router.get("/{id}", response_model=InvoiceDetailResponse)
def get_invoice(id: int) -> InvoiceDetailResponse:
    return get_invoice_detail(invoice_pk=id)


@router.post("/{id}/summary", response_model=SummaryResponse)
def generate_invoice_summary(id: int) -> SummaryResponse:
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT i.id, i.invoice_id, i.upload_id, i.invoice_number, i.vendor_name,
                   i.total_amount, i.invoice_date, d.id as decision_id,
                   d.decision, d.confidence, d.exception_type, d.primary_reason,
                   d.matched_record, d.violations_json, d.evidence_json,
                   d.ai_summary, d.ai_suggested_action, d.ai_summary_status
            FROM invoices i
            JOIN decisions d ON i.id = d.invoice_pk
            WHERE i.id = ?
            """,
            (id,),
        )
        row = cursor.fetchone()
        if not row:
            raise ApiError(
                code="NOT_FOUND",
                message=f"Invoice with ID {id} not found",
                details=[],
                status_code=404,
            )

        data = row_to_dict(row)
        # If summary already ready, return stored summary (idempotent)
        if data.get("ai_summary_status") == "ready" and data.get("ai_summary"):
            return SummaryResponse(
                ai_summary=data["ai_summary"],
                ai_suggested_action=data["ai_suggested_action"] or "investigate",
                ai_summary_status="ready",
            )

        violations = json.loads(data["violations_json"]) if data["violations_json"] else []
        decision_record = {
            "invoice_id": data["invoice_id"],
            "decision": data["decision"],
            "confidence": data["confidence"],
            "exception_type": data["exception_type"],
            "primary_reason": data["primary_reason"],
            "matched_record": data["matched_record"],
            "violations": violations,
            "record": {
                "invoice_id": data["invoice_id"],
                "invoice_number": data["invoice_number"],
                "vendor_name": data["vendor_name"],
                "total_amount": data["total_amount"],
                "invoice_date": data["invoice_date"],
            },
        }

        summary_res = generate_summary(decision_record)
        ai_summary = summary_res.get("summary", "")
        ai_suggested_action = summary_res.get("suggested_action", "investigate")
        ai_status = "ready"

        cursor.execute(
            """
            UPDATE decisions
            SET ai_summary = ?, ai_suggested_action = ?, ai_summary_status = ?
            WHERE id = ?
            """,
            (ai_summary, ai_suggested_action, ai_status, data["decision_id"]),
        )

        log_event(
            actor="ai-assistant",
            actor_type="ai",
            event_type="AI_SUMMARY_GENERATED",
            invoice_id=data["invoice_id"],
            upload_id=data["upload_id"],
            details={"suggested_action": ai_suggested_action},
            conn=conn,
        )

        conn.commit()

        return SummaryResponse(
            ai_summary=ai_summary,
            ai_suggested_action=ai_suggested_action,
            ai_summary_status=ai_status,
        )
    finally:
        conn.close()
