from backend.database import get_conn
from backend.schemas import (
    ByDecisionStats,
    ExceptionTypeCount,
    HistogramBucket,
    StatsResponse,
)


def get_stats(upload_id: int | None = None) -> StatsResponse:
    conn = get_conn()
    try:
        cursor = conn.cursor()

        where_sql = "WHERE i.upload_id = ?" if upload_id is not None else ""
        params = [upload_id] if upload_id is not None else []

        # Total counts by decision
        cursor.execute(
            f"""
            SELECT d.decision, COUNT(*)
            FROM decisions d
            JOIN invoices i ON d.invoice_pk = i.id
            {where_sql}
            GROUP BY d.decision
            """,
            params,
        )
        dec_counts = dict(cursor.fetchall())
        auto_pass = dec_counts.get("auto_pass", 0)
        needs_review = dec_counts.get("needs_review", 0)
        exception = dec_counts.get("exception", 0)
        total = auto_pass + needs_review + exception

        auto_pass_rate = round(auto_pass / total, 3) if total > 0 else 0.0

        # Pending reviews count
        cursor.execute(
            f"""
            SELECT COUNT(*)
            FROM decisions d
            JOIN invoices i ON d.invoice_pk = i.id
            {where_sql} {"AND" if where_sql else "WHERE"} d.review_status = 'pending'
            """,
            params,
        )
        pending_reviews = cursor.fetchone()[0]

        # By exception type
        cursor.execute(
            f"""
            SELECT d.exception_type, COUNT(*)
            FROM decisions d
            JOIN invoices i ON d.invoice_pk = i.id
            {where_sql}
            GROUP BY d.exception_type
            ORDER BY COUNT(*) DESC
            """,
            params,
        )
        exc_rows = cursor.fetchall()
        by_exception_type = [
            ExceptionTypeCount(exception_type=r[0], count=r[1]) for r in exc_rows
        ]

        # Confidence histogram (10 buckets: 0.0-0.1, ..., 0.9-1.0)
        cursor.execute(
            f"""
            SELECT d.confidence
            FROM decisions d
            JOIN invoices i ON d.invoice_pk = i.id
            {where_sql}
            """,
            params,
        )
        confidences = [row[0] for row in cursor.fetchall()]

        buckets = [0] * 10
        for c in confidences:
            if c >= 1.0:
                idx = 9
            elif c < 0.0:
                idx = 0
            else:
                idx = min(9, int(c * 10))
            buckets[idx] += 1

        histogram = [
            HistogramBucket(
                bucket=f"{i / 10.0:.1f}-{(i + 1) / 10.0:.1f}",
                count=buckets[i],
            )
            for i in range(10)
        ]

        estimated_minutes_saved = auto_pass * 5

        return StatsResponse(
            upload_id=upload_id,
            total=total,
            by_decision=ByDecisionStats(
                auto_pass=auto_pass,
                needs_review=needs_review,
                exception=exception,
            ),
            auto_pass_rate=auto_pass_rate,
            pending_reviews=pending_reviews,
            by_exception_type=by_exception_type,
            confidence_histogram=histogram,
            estimated_minutes_saved=estimated_minutes_saved,
        )
    finally:
        conn.close()
