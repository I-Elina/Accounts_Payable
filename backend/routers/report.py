from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from backend.services.report_service import generate_report_csv

router = APIRouter(prefix="/api/uploads", tags=["report"])


@router.get("/{upload_id}/report")
def download_exception_report(
    upload_id: int,
    decision: str | None = Query("needs_review,exception"),
) -> StreamingResponse:
    stream = generate_report_csv(upload_id=upload_id, decision=decision)
    filename = f"ap_exception_report_{upload_id}.csv"
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Content-Type": "text/csv; charset=utf-8",
    }
    return StreamingResponse(stream, media_type="text/csv", headers=headers)
