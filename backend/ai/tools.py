import json
from typing import Any
from backend.ai.cards import (
    build_invoice_card,
    build_proposal_card,
    build_report_card,
    build_stats_card,
)
from backend.database import get_conn, row_to_dict
from backend.services.stats_service import get_stats as fetch_stats


def get_invoice(invoice_id: str) -> dict[str, Any]:
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT i.id, i.upload_id, i.invoice_id, i.invoice_number, i.vendor_name,
                   i.invoice_date, i.due_date, i.currency, i.subtotal, i.tax_amount,
                   i.total_amount, i.category, i.po_number, i.description,
                   d.decision, d.confidence, d.exception_type, d.primary_reason,
                   d.matched_record, d.review_status
            FROM invoices i
            JOIN decisions d ON i.id = d.invoice_pk
            WHERE i.invoice_id = ?
            LIMIT 1
            """,
            (invoice_id.strip(),),
        )
        row = cursor.fetchone()
        if not row:
            return {"error": "not_found", "message": f"Invoice {invoice_id} not found", "cards": []}

        data = row_to_dict(row)
        card = build_invoice_card(data)
        return {"data": data, "cards": [card]}
    finally:
        conn.close()


def explain_decision(invoice_id: str) -> dict[str, Any]:
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT i.id, i.upload_id, i.invoice_id, i.invoice_number, i.vendor_name,
                   i.invoice_date, i.total_amount, i.currency,
                   d.decision, d.confidence, d.exception_type, d.primary_reason,
                   d.matched_record, d.violations_json, d.evidence_json, d.review_status
            FROM invoices i
            JOIN decisions d ON i.id = d.invoice_pk
            WHERE i.invoice_id = ?
            LIMIT 1
            """,
            (invoice_id.strip(),),
        )
        row = cursor.fetchone()
        if not row:
            return {"error": "not_found", "message": f"Invoice {invoice_id} not found", "cards": []}

        data = row_to_dict(row)
        violations = json.loads(data["violations_json"]) if data["violations_json"] else []
        evidence = json.loads(data["evidence_json"]) if data["evidence_json"] else {}
        card = build_invoice_card(data)

        # Include matched invoice card if available
        matched_card = None
        if data["matched_record"]:
            cursor.execute(
                """
                SELECT i.id, i.upload_id, i.invoice_id, i.invoice_number, i.vendor_name,
                       i.invoice_date, i.total_amount, i.currency,
                       d.decision, d.confidence, d.exception_type, d.primary_reason,
                       d.matched_record, d.review_status
                FROM invoices i
                JOIN decisions d ON i.id = d.invoice_pk
                WHERE i.upload_id = ? AND i.invoice_id = ?
                LIMIT 1
                """,
                (data["upload_id"], data["matched_record"]),
            )
            matched_row = cursor.fetchone()
            if matched_row:
                matched_card = build_invoice_card(row_to_dict(matched_row))

        cards = [card]
        if matched_card:
            cards.append(matched_card)

        return {
            "data": {
                "invoice_id": data["invoice_id"],
                "decision": data["decision"],
                "confidence": data["confidence"],
                "primary_reason": data["primary_reason"],
                "matched_record": data["matched_record"],
                "violations": violations,
                "evidence": evidence,
            },
            "cards": cards,
        }
    finally:
        conn.close()


def list_pending(limit: int = 5) -> dict[str, Any]:
    limit = min(5, max(1, limit))
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT i.id, i.upload_id, i.invoice_id, i.invoice_number, i.vendor_name,
                   i.invoice_date, i.total_amount, i.currency,
                   d.decision, d.confidence, d.exception_type, d.primary_reason,
                   d.matched_record, d.review_status
            FROM invoices i
            JOIN decisions d ON i.id = d.invoice_pk
            WHERE d.review_status = 'pending'
            ORDER BY d.confidence ASC, i.id ASC
            LIMIT ?
            """,
            (limit,),
        )
        rows = [row_to_dict(r) for r in cursor.fetchall()]
        cards = [build_invoice_card(r) for r in rows]
        return {"data": rows, "cards": cards}
    finally:
        conn.close()


def list_exceptions(exception_type: str | None = None, limit: int = 10) -> dict[str, Any]:
    limit = min(10, max(1, limit))
    conn = get_conn()
    try:
        cursor = conn.cursor()
        if exception_type:
            cursor.execute(
                """
                SELECT i.id, i.upload_id, i.invoice_id, i.invoice_number, i.vendor_name,
                       i.invoice_date, i.total_amount, i.currency,
                       d.decision, d.confidence, d.exception_type, d.primary_reason,
                       d.matched_record, d.review_status
                FROM invoices i
                JOIN decisions d ON i.id = d.invoice_pk
                WHERE d.exception_type = ?
                ORDER BY d.confidence ASC, i.id ASC
                LIMIT ?
                """,
                (exception_type, limit),
            )
        else:
            cursor.execute(
                """
                SELECT i.id, i.upload_id, i.invoice_id, i.invoice_number, i.vendor_name,
                       i.invoice_date, i.total_amount, i.currency,
                       d.decision, d.confidence, d.exception_type, d.primary_reason,
                       d.matched_record, d.review_status
                FROM invoices i
                JOIN decisions d ON i.id = d.invoice_pk
                WHERE d.decision != 'auto_pass'
                ORDER BY d.confidence ASC, i.id ASC
                LIMIT ?
                """,
                (limit,),
            )
        rows = [row_to_dict(r) for r in cursor.fetchall()]
        cards = [build_invoice_card(r) for r in rows]
        return {"data": rows, "cards": cards[:5]}
    finally:
        conn.close()


def list_duplicates(limit: int = 10) -> dict[str, Any]:
    limit = min(10, max(1, limit))
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT i.id, i.upload_id, i.invoice_id, i.invoice_number, i.vendor_name,
                   i.invoice_date, i.total_amount, i.currency,
                   d.decision, d.confidence, d.exception_type, d.primary_reason,
                   d.matched_record, d.review_status
            FROM invoices i
            JOIN decisions d ON i.id = d.invoice_pk
            WHERE d.exception_type IN ('exact_duplicate', 'fuzzy_duplicate')
            ORDER BY d.confidence ASC, i.id ASC
            LIMIT ?
            """,
            (limit,),
        )
        rows = [row_to_dict(r) for r in cursor.fetchall()]
        cards = [build_invoice_card(r) for r in rows]
        return {"data": rows, "cards": cards[:5]}
    finally:
        conn.close()


def get_stats(upload_id: int | None = None) -> dict[str, Any]:
    stats_obj = fetch_stats(upload_id)
    stats_dict = stats_obj.model_dump()
    card = build_stats_card(stats_dict)
    return {"data": stats_dict, "cards": [card]}


def get_audit(invoice_id: str, limit: int = 10) -> dict[str, Any]:
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, timestamp, actor, actor_type, event_type, invoice_id, upload_id, details_json
            FROM audit_log
            WHERE invoice_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (invoice_id.strip(), limit),
        )
        rows = [row_to_dict(r) for r in cursor.fetchall()]
        return {"data": rows, "cards": []}
    finally:
        conn.close()


def get_report_link(upload_id: int | None = None) -> dict[str, Any]:
    conn = get_conn()
    try:
        target_upload_id = upload_id
        if target_upload_id is None:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM uploads ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            target_upload_id = row[0] if row else 1

        card = build_report_card(target_upload_id)
        return {
            "data": {"upload_id": target_upload_id, "url": f"/api/uploads/{target_upload_id}/report"},
            "cards": [card],
        }
    finally:
        conn.close()


def propose_review(invoice_id: str, action: str) -> dict[str, Any]:
    """Suggests an approve or reject proposal. Writes ZERO changes to the database."""
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT i.id, i.invoice_id, d.review_status, d.primary_reason
            FROM invoices i
            JOIN decisions d ON i.id = d.invoice_pk
            WHERE i.invoice_id = ?
            LIMIT 1
            """,
            (invoice_id.strip(),),
        )
        row = cursor.fetchone()
        if not row:
            return {"error": "not_found", "message": f"Invoice {invoice_id} not found", "proposal": None}

        data = row_to_dict(row)
        invoice_pk = data["id"]
        status = data["review_status"]
        if status != "pending":
            return {
                "error": "conflict",
                "message": f"Invoice {invoice_id} is already '{status}' and cannot be reviewed",
                "proposal": None,
            }

        act = "approve" if "approve" in action.lower() else "reject"
        proposal = build_proposal_card(
            invoice_pk=invoice_pk,
            invoice_id=data["invoice_id"],
            action=act,
            reason=f"Assistant proposed {act} based on review request",
        )
        return {
            "data": {"invoice_id": invoice_id, "proposed_action": act},
            "proposal": proposal,
        }
    finally:
        conn.close()


TOOL_REGISTRY = {
    "get_invoice": get_invoice,
    "explain_decision": explain_decision,
    "list_pending": list_pending,
    "list_exceptions": list_exceptions,
    "list_duplicates": list_duplicates,
    "get_stats": get_stats,
    "get_audit": get_audit,
    "get_report_link": get_report_link,
    "propose_review": propose_review,
}
