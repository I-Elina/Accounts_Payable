import datetime
import json
from typing import Any
from backend.database import get_conn, row_to_dict
from backend.schemas import AuditEvent, PaginatedAuditResponse


def log_event(
    actor: str,
    actor_type: str,
    event_type: str,
    invoice_id: str | None = None,
    upload_id: int | None = None,
    details: dict[str, Any] | None = None,
    conn=None,
) -> int:
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    details_json = json.dumps(details) if details is not None else None

    query = """
    INSERT INTO audit_log (timestamp, actor, actor_type, event_type, invoice_id, upload_id, details_json)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    params = (timestamp, actor, actor_type, event_type, invoice_id, upload_id, details_json)

    if conn is not None:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.lastrowid

    with get_conn() as connection:
        cursor = connection.cursor()
        cursor.execute(query, params)
        connection.commit()
        return cursor.lastrowid


def get_audit_events(
    upload_id: int | None = None,
    invoice_id: str | None = None,
    event_type: str | None = None,
    page: int = 1,
    page_size: int = 25,
) -> PaginatedAuditResponse:
    page = max(1, page)
    page_size = min(200, max(1, page_size))
    offset = (page - 1) * page_size

    where_clauses = []
    params = []

    if upload_id is not None:
        where_clauses.append("upload_id = ?")
        params.append(upload_id)
    if invoice_id:
        where_clauses.append("invoice_id = ?")
        params.append(invoice_id)
    if event_type:
        where_clauses.append("event_type = ?")
        params.append(event_type)

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    conn = get_conn()
    try:
        count_cursor = conn.cursor()
        count_cursor.execute(f"SELECT COUNT(*) FROM audit_log {where_sql}", params)
        total = count_cursor.fetchone()[0]

        data_cursor = conn.cursor()
        data_query = f"""
        SELECT id, timestamp, actor, actor_type, event_type, invoice_id, upload_id, details_json
        FROM audit_log
        {where_sql}
        ORDER BY id DESC
        LIMIT ? OFFSET ?
        """
        data_cursor.execute(data_query, params + [page_size, offset])
        rows = data_cursor.fetchall()

        items = []
        for r in rows:
            d = row_to_dict(r)
            details_obj = None
            if d.get("details_json"):
                try:
                    details_obj = json.loads(d["details_json"])
                except Exception:
                    details_obj = None
            items.append(
                AuditEvent(
                    id=d["id"],
                    timestamp=d["timestamp"],
                    actor=d["actor"],
                    actor_type=d["actor_type"],
                    event_type=d["event_type"],
                    invoice_id=d["invoice_id"],
                    upload_id=d["upload_id"],
                    details=details_obj,
                )
            )

        return PaginatedAuditResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )
    finally:
        conn.close()
