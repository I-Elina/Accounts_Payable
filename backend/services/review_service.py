import datetime
from backend.database import get_conn, row_to_dict
from backend.errors import ApiError
from backend.schemas import InvoiceDetailResponse, ReviewRequest
from backend.services.audit_service import log_event
from backend.services.invoice_service import get_invoice_detail


def submit_review(invoice_pk: int, review_req: ReviewRequest) -> InvoiceDetailResponse:
    reviewer = review_req.reviewer.strip() if review_req.reviewer else ""
    if not reviewer:
        raise ApiError(
            code="VALIDATION_ERROR",
            message="Reviewer name is required and cannot be empty",
            details=["reviewer field cannot be empty"],
            status_code=422,
        )

    if review_req.action not in ["approve", "reject"]:
        raise ApiError(
            code="VALIDATION_ERROR",
            message=f"Invalid review action: {review_req.action}",
            details=["action must be either 'approve' or 'reject'"],
            status_code=422,
        )

    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT d.id, d.decision, d.confidence, d.review_status, i.invoice_id, i.upload_id
            FROM decisions d
            JOIN invoices i ON d.invoice_pk = i.id
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
        decision_pk = data["id"]
        review_status = data["review_status"]
        invoice_id = data["invoice_id"]
        upload_id = data["upload_id"]
        prev_confidence = data["confidence"]

        if review_status != "pending":
            raise ApiError(
                code="CONFLICT",
                message=f"Invoice {invoice_id} cannot be reviewed because its current review status is '{review_status}'",
                details=[f"review_status must be 'pending', currently '{review_status}'"],
                status_code=409,
            )

        new_status = "approved" if review_req.action == "approve" else "rejected"
        event_type = "REVIEW_APPROVED" if review_req.action == "approve" else "REVIEW_REJECTED"
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        cursor.execute(
            """
            UPDATE decisions
            SET review_status = ?
            WHERE id = ?
            """,
            (new_status, decision_pk),
        )

        cursor.execute(
            """
            INSERT INTO reviews (decision_pk, reviewer, action, comment, reviewed_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (decision_pk, reviewer, review_req.action, review_req.comment, now_iso),
        )

        log_event(
            actor=reviewer,
            actor_type="user",
            event_type=event_type,
            invoice_id=invoice_id,
            upload_id=upload_id,
            details={
                "action": review_req.action,
                "comment": review_req.comment,
                "previous_confidence": prev_confidence,
            },
            conn=conn,
        )

        conn.commit()
    finally:
        conn.close()

    return get_invoice_detail(invoice_pk)
