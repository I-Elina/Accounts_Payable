import datetime
import json
import os
import uuid
from pathlib import Path
from typing import Any
from fastapi import UploadFile
from backend.database import get_conn, row_to_dict
from backend.errors import ApiError
from backend.schemas import UploadListItem, UploadListResponse, UploadResponse, UploadSummary
from backend.services.audit_service import log_event
from backend.services.config_service import get_current_config
from backend.settings import MAX_UPLOAD_MB, REPO_ROOT


def _run_engine_or_stub(file_path: Path, history: list[dict] | None, config: dict) -> dict:
    use_stub = os.getenv("USE_ENGINE_STUB", "false").lower() == "true"
    if not use_stub:
        try:
            from engine import run_engine
            from engine.errors import IngestionError
            try:
                return run_engine(str(file_path), history=history, config=config)
            except IngestionError as e:
                raise ApiError(
                    code="VALIDATION_ERROR",
                    message=e.message,
                    details=e.details,
                    status_code=422,
                )
        except ImportError:
            use_stub = True

    if use_stub:
        # Load contract example stub
        stub_path = REPO_ROOT / "contracts" / "examples" / "engine_output.json"
        if stub_path.exists():
            with open(stub_path, "r", encoding="utf-8") as f:
                return json.load(f)
        raise ApiError(
            code="INTERNAL",
            message="Decision engine not available and stub not found",
            details=[],
            status_code=500,
        )


async def process_upload(
    file: UploadFile,
    uploaded_by: str | None = None,
    use_history: bool = False,
) -> UploadResponse:
    filename = file.filename or "upload.csv"
    ext = Path(filename).suffix.lower()
    if ext not in [".csv", ".xlsx"]:
        raise ApiError(
            code="VALIDATION_ERROR",
            message=f"Unsupported file extension: {ext}. Only .csv and .xlsx files are supported.",
            details=["File must end with .csv or .xlsx"],
            status_code=422,
        )

    content = await file.read()
    if len(content) == 0:
        raise ApiError(
            code="VALIDATION_ERROR",
            message="Uploaded file is empty",
            details=["File size is 0 bytes"],
            status_code=422,
        )

    max_bytes = MAX_UPLOAD_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise ApiError(
            code="VALIDATION_ERROR",
            message=f"File exceeds maximum upload size of {MAX_UPLOAD_MB}MB",
            details=[f"File size is {len(content)} bytes"],
            status_code=422,
        )

    # Save to storage/uploads
    storage_dir = Path(__file__).resolve().parent.parent / "storage" / "uploads"
    storage_dir.mkdir(parents=True, exist_ok=True)
    saved_filename = f"{uuid.uuid4().hex}_{Path(filename).name}"
    saved_path = storage_dir / saved_filename
    with open(saved_path, "wb") as f:
        f.write(content)

    # Audit UPLOAD_RECEIVED
    log_event(
        actor="system",
        actor_type="system",
        event_type="UPLOAD_RECEIVED",
        details={"filename": filename, "uploaded_by": uploaded_by},
    )

    # Fetch history if requested
    history = None
    if use_history:
        conn = get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT invoice_id, invoice_number, vendor_name, invoice_date, due_date, currency,
                       subtotal, tax_amount, total_amount, category, po_number, description
                FROM invoices
            """)
            history = [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    # Load engine config from settings
    cfg = get_current_config()
    engine_cfg = {
        "auto_pass_threshold": cfg.auto_pass_threshold,
        "exception_below": cfg.exception_below,
        "policy_limit": cfg.policy_limit,
    }

    # Execute engine
    engine_result = _run_engine_or_stub(saved_path, history=history, config=engine_cfg)

    summary_data = engine_result.get("summary", {})
    results = engine_result.get("results", [])
    warnings = engine_result.get("warnings", [])

    total_rows = summary_data.get("total", len(results))
    auto_pass_count = summary_data.get("auto_pass", 0)
    needs_review_count = summary_data.get("needs_review", 0)
    exception_count = summary_data.get("exception", 0)

    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

    conn = get_conn()
    try:
        cursor = conn.cursor()

        # Insert upload
        cursor.execute(
            """
            INSERT INTO uploads (filename, uploaded_at, uploaded_by, total_rows, auto_pass_count, needs_review_count, exception_count, used_history)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                filename,
                now_iso,
                uploaded_by,
                total_rows,
                auto_pass_count,
                needs_review_count,
                exception_count,
                1 if use_history else 0,
            ),
        )
        upload_id = cursor.lastrowid

        # Insert invoices and decisions
        for r in results:
            rec = r.get("record", {})
            decision = r.get("decision", "exception")
            confidence = float(r.get("confidence", 0.0))
            pass_resolved_in = r.get("pass_resolved_in", 1)
            exception_type = r.get("exception_type", "none")
            primary_reason = r.get("primary_reason", "")
            matched_record = r.get("matched_record")
            violations_json = json.dumps(r.get("violations", []))
            evidence_json = json.dumps(r.get("evidence", {}))
            review_status = "not_required" if decision == "auto_pass" else "pending"

            cursor.execute(
                """
                INSERT INTO invoices (upload_id, invoice_id, invoice_number, vendor_name, invoice_date, due_date, currency, subtotal, tax_amount, total_amount, category, po_number, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    upload_id,
                    rec.get("invoice_id", f"ROW-{r.get('row_index', 0):04d}"),
                    rec.get("invoice_number"),
                    rec.get("vendor_name"),
                    rec.get("invoice_date"),
                    rec.get("due_date"),
                    rec.get("currency", "INR"),
                    rec.get("subtotal"),
                    rec.get("tax_amount"),
                    rec.get("total_amount"),
                    rec.get("category"),
                    rec.get("po_number"),
                    rec.get("description"),
                ),
            )
            invoice_pk = cursor.lastrowid

            cursor.execute(
                """
                INSERT INTO decisions (invoice_pk, decision, confidence, pass_resolved_in, exception_type, primary_reason, matched_record, violations_json, evidence_json, review_status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    invoice_pk,
                    decision,
                    confidence,
                    pass_resolved_in,
                    exception_type,
                    primary_reason,
                    matched_record,
                    violations_json,
                    evidence_json,
                    review_status,
                    now_iso,
                ),
            )

            # Audit event per invoice
            event_type = "INVOICE_AUTO_PASSED" if decision == "auto_pass" else "INVOICE_FLAGGED"
            log_event(
                actor="decision-engine",
                actor_type="engine",
                event_type=event_type,
                invoice_id=rec.get("invoice_id"),
                upload_id=upload_id,
                details={
                    "decision": decision,
                    "confidence": confidence,
                    "exception_type": exception_type,
                    "primary_reason": primary_reason,
                },
                conn=conn,
            )

        # Audit INGESTION_COMPLETED
        log_event(
            actor="system",
            actor_type="system",
            event_type="INGESTION_COMPLETED",
            upload_id=upload_id,
            details={
                "total": total_rows,
                "auto_pass": auto_pass_count,
                "needs_review": needs_review_count,
                "exception": exception_count,
            },
            conn=conn,
        )

        conn.commit()

        return UploadResponse(
            upload_id=upload_id,
            filename=filename,
            summary=UploadSummary(
                total=total_rows,
                auto_pass=auto_pass_count,
                needs_review=needs_review_count,
                exception=exception_count,
            ),
            warnings=warnings,
        )
    finally:
        conn.close()


def list_uploads() -> UploadListResponse:
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, filename, uploaded_at, uploaded_by, total_rows, auto_pass_count, needs_review_count, exception_count
            FROM uploads
            ORDER BY id DESC
        """)
        rows = cursor.fetchall()
        items = [UploadListItem(**row_to_dict(r)) for r in rows]
        return UploadListResponse(items=items)
    finally:
        conn.close()
