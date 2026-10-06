from typing import Any


def build_invoice_card(invoice_row: dict[str, Any]) -> dict[str, Any]:
    """Build verified invoice card from database row dictionary."""
    return {
        "type": "invoice",
        "id": invoice_row["id"],
        "invoice_id": invoice_row["invoice_id"],
        "vendor_name": invoice_row.get("vendor_name"),
        "total_amount": invoice_row.get("total_amount"),
        "currency": invoice_row.get("currency", "INR"),
        "decision": invoice_row["decision"],
        "confidence": invoice_row["confidence"],
        "primary_reason": invoice_row.get("primary_reason", ""),
        "matched_record": invoice_row.get("matched_record"),
        "review_status": invoice_row.get("review_status", "pending"),
    }


def build_stats_card(stats: dict[str, Any]) -> dict[str, Any]:
    """Build stats card from stats dict."""
    return {
        "type": "stats",
        "upload_id": stats.get("upload_id"),
        "total": stats["total"],
        "auto_pass": stats["by_decision"]["auto_pass"],
        "needs_review": stats["by_decision"]["needs_review"],
        "exception": stats["by_decision"]["exception"],
    }


def build_report_card(upload_id: int) -> dict[str, Any]:
    """Build report card linking to CSV download."""
    return {
        "type": "report",
        "upload_id": upload_id,
        "url": f"/api/uploads/{upload_id}/report",
    }


def build_proposal_card(
    invoice_pk: int,
    invoice_id: str,
    action: str,
    reason: str,
) -> dict[str, Any]:
    """Build review proposal card (never writes to DB)."""
    return {
        "type": "review_proposal",
        "id": invoice_pk,
        "invoice_id": invoice_id,
        "action": action,
        "reason": reason,
    }
