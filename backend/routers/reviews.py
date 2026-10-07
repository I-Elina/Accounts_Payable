from fastapi import APIRouter
from backend.schemas import InvoiceDetailResponse, ReviewRequest
from backend.services.review_service import submit_review

router = APIRouter(prefix="/api/invoices", tags=["reviews"])


@router.post("/{id}/review", response_model=InvoiceDetailResponse)
def review_invoice(id: int, review_req: ReviewRequest) -> InvoiceDetailResponse:
    return submit_review(invoice_pk=id, review_req=review_req)
