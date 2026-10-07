from fastapi import APIRouter, Query
from backend.schemas import PaginatedAuditResponse
from backend.services.audit_service import get_audit_events

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("", response_model=PaginatedAuditResponse)
def get_audit_trail(
    upload_id: int | None = Query(None),
    invoice_id: str | None = Query(None),
    event_type: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
) -> PaginatedAuditResponse:
    return get_audit_events(
        upload_id=upload_id,
        invoice_id=invoice_id,
        event_type=event_type,
        page=page,
        page_size=page_size,
    )
