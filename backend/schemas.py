from typing import Any, Literal
from pydantic import BaseModel, Field


# --- Health ---
class HealthResponse(BaseModel):
    status: str = "ok"
    ai_mode: str = "mock"


# --- Uploads ---
class UploadSummary(BaseModel):
    total: int
    auto_pass: int
    needs_review: int
    exception: int


class UploadResponse(BaseModel):
    upload_id: int
    filename: str
    summary: UploadSummary
    warnings: list[str] = Field(default_factory=list)


class UploadListItem(BaseModel):
    id: int
    filename: str
    uploaded_at: str
    uploaded_by: str | None = None
    total_rows: int
    auto_pass_count: int
    needs_review_count: int
    exception_count: int


class UploadListResponse(BaseModel):
    items: list[UploadListItem]


# --- Invoices ---
class InvoiceListItem(BaseModel):
    id: int
    upload_id: int
    invoice_id: str
    invoice_number: str | None = None
    vendor_name: str | None = None
    invoice_date: str | None = None
    total_amount: float | None = None
    currency: str | None = "INR"
    category: str | None = None
    decision: str
    confidence: float
    exception_type: str
    primary_reason: str
    review_status: str


class PaginatedInvoicesResponse(BaseModel):
    items: list[InvoiceListItem]
    total: int
    page: int
    page_size: int


class CanonicalInvoice(BaseModel):
    id: int
    upload_id: int
    invoice_id: str
    invoice_number: str | None = None
    vendor_name: str | None = None
    invoice_date: str | None = None
    due_date: str | None = None
    currency: str | None = "INR"
    subtotal: float | None = None
    tax_amount: float | None = None
    total_amount: float | None = None
    category: str | None = None
    po_number: str | None = None
    description: str | None = None


class DecisionDetail(BaseModel):
    decision: str
    confidence: float
    pass_resolved_in: int | None = 1
    exception_type: str
    primary_reason: str
    matched_record: str | None = None
    violations: list[dict[str, Any]] = Field(default_factory=list)
    evidence: dict[str, Any] = Field(default_factory=dict)
    ai_summary: str | None = None
    ai_suggested_action: str | None = None
    ai_summary_status: str = "not_generated"
    review_status: str = "pending"


class ReviewHistoryItem(BaseModel):
    id: int
    reviewer: str
    action: str
    comment: str | None = None
    reviewed_at: str


class InvoiceDetailResponse(BaseModel):
    invoice: CanonicalInvoice
    decision: DecisionDetail
    matched_invoice: CanonicalInvoice | None = None
    reviews: list[ReviewHistoryItem] = Field(default_factory=list)


class ReviewRequest(BaseModel):
    action: Literal["approve", "reject"]
    reviewer: str
    comment: str | None = None


class SummaryResponse(BaseModel):
    ai_summary: str
    ai_suggested_action: str
    ai_summary_status: str


# --- Stats ---
class ByDecisionStats(BaseModel):
    auto_pass: int
    needs_review: int
    exception: int


class ExceptionTypeCount(BaseModel):
    exception_type: str
    count: int


class HistogramBucket(BaseModel):
    bucket: str
    count: int


class StatsResponse(BaseModel):
    upload_id: int | None = None
    total: int
    by_decision: ByDecisionStats
    auto_pass_rate: float
    pending_reviews: int
    by_exception_type: list[ExceptionTypeCount]
    confidence_histogram: list[HistogramBucket]
    estimated_minutes_saved: int


# --- Audit ---
class AuditEvent(BaseModel):
    id: int
    timestamp: str
    actor: str
    actor_type: str
    event_type: str
    invoice_id: str | None = None
    upload_id: int | None = None
    details: dict[str, Any] | None = None


class PaginatedAuditResponse(BaseModel):
    items: list[AuditEvent]
    total: int
    page: int
    page_size: int


# --- Chat ---
class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    upload_id: int | None = None


class ChatProposal(BaseModel):
    type: Literal["review_proposal"] = "review_proposal"
    id: int
    invoice_id: str
    action: Literal["approve", "reject"]
    reason: str


class ToolUsed(BaseModel):
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class ChatResponse(BaseModel):
    reply: str
    session_id: str
    referenced_invoice_ids: list[str] = Field(default_factory=list)
    tools_used: list[ToolUsed] = Field(default_factory=list)
    cards: list[dict[str, Any]] = Field(default_factory=list)
    proposal: ChatProposal | None = None


# --- Config ---
class ConfigRule(BaseModel):
    rule_id: str
    name: str
    severity: str
    penalty: float
    enabled: bool
    exception_type: str


class ConfigResponse(BaseModel):
    auto_pass_threshold: float
    exception_below: float
    policy_limit: float
    rules: list[ConfigRule]


class ConfigUpdateRequest(BaseModel):
    auto_pass_threshold: float | None = None
    exception_below: float | None = None
