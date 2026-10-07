# Cache Me If You Can: REST API Documentation 📡

All endpoints are served under the `/api` prefix, accept and return JSON payloads in `snake_case`, and follow the binding contracts in `contracts/CONTRACT.md`.

---

## Endpoint Summary

| Method | Endpoint | Description | Auth / Actor |
|---|---|---|---|
| `GET` | `/api/health` | Liveness and AI mode status | Public |
| `POST` | `/api/uploads` | Upload CSV/Excel and execute decision engine | Multipart File |
| `GET` | `/api/uploads` | List recent invoice upload batches | Public |
| `GET` | `/api/invoices` | Paginated invoice queue with multi-facet filters | Public |
| `GET` | `/api/invoices/{id}` | Detailed invoice record with violations & compare | Public |
| `POST` | `/api/invoices/{id}/summary` | Trigger / refresh AI explanation | Reviewer |
| `POST` | `/api/invoices/{id}/review` | Submit human approval or rejection | Reviewer |
| `GET` | `/api/stats` | Executive KPI aggregations & confidence histograms | Public |
| `GET` | `/api/audit` | Query append-only audit trail | Auditor |
| `POST` | `/api/chat` | Chatbot query endpoint with inline card responses | Public |
| `GET` | `/api/uploads/{id}/report` | Download sanitized exception CSV report | Public |
| `GET` | `/api/config` | Retrieve current thresholds & rule parameters | Public |
| `PUT` | `/api/config` | Update routing thresholds (`auto_pass`, `exception_below`) | Admin |

---

## Detailed Endpoint Specifications & cURL Examples

### 1. Health Check
```bash
curl -X GET http://localhost:8000/api/health
```
**Response (200 OK):**
```json
{
  "status": "ok",
  "ai_mode": "mock"
}
```

### 2. Upload Invoice Batch
```bash
curl -X POST http://localhost:8000/api/uploads \
  -F "file=@data/processed/invoices_demo.csv" \
  -F "uploaded_by=Shree" \
  -F "use_history=false"
```
**Response (201 Created):**
```json
{
  "upload_id": 1,
  "filename": "invoices_demo.csv",
  "summary": {
    "total": 1000,
    "auto_pass": 816,
    "needs_review": 88,
    "exception": 96,
    "engine_version": "1.0.0",
    "auto_pass_threshold": 0.85,
    "exception_below": 0.40
  },
  "warnings": []
}
```

### 3. Query Review Queue
```bash
curl -X GET "http://localhost:8000/api/invoices?decision=needs_review,exception&page=1&page_size=10"
```
**Response (200 OK):**
```json
{
  "items": [
    {
      "id": 42,
      "upload_id": 1,
      "invoice_id": "INV-1042",
      "invoice_number": "AC/2026/0345",
      "vendor_name": "Acme Pvt Ltd",
      "invoice_date": "2026-09-03",
      "total_amount": 10000.0,
      "currency": "INR",
      "category": "Office Supplies",
      "decision": "needs_review",
      "confidence": 0.50,
      "exception_type": "fuzzy_duplicate",
      "primary_reason": "Probable duplicate of INV-0987 (98% similar)",
      "review_status": "pending"
    }
  ],
  "total": 184,
  "page": 1,
  "page_size": 10
}
```

### 4. Review and Approve an Invoice
```bash
curl -X POST http://localhost:8000/api/invoices/42/review \
  -H "Content-Type: application/json" \
  -d '{
    "action": "approve",
    "reviewer": "Shree",
    "comment": "Confirmed separate physical dispatch delivery"
  }'
```
**Response (200 OK):**
```json
{
  "id": 42,
  "invoice_id": "INV-1042",
  "decision": "needs_review",
  "review_status": "approved",
  "reviewed_by": "Shree",
  "reviewed_at": "2026-10-07T10:15:00Z"
}
```

### 5. Chat Assistant Interaction
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Why was INV-1042 flagged?",
    "upload_id": 1
  }'
```
**Response (200 OK):**
```json
{
  "reply": "INV-1042 was flagged as a probable duplicate because it shares the same vendor invoice number AC/2026/0345 with INV-0987, with an amount within 0.2% and dates only 1 day apart.",
  "session_id": "sess_default",
  "referenced_invoice_ids": ["INV-1042", "INV-0987"],
  "tools_used": [
    {"name": "explain_decision", "arguments": {"invoice_id": "INV-1042"}}
  ],
  "cards": [
    {
      "type": "invoice",
      "id": 42,
      "invoice_id": "INV-1042",
      "vendor_name": "Acme Pvt Ltd",
      "total_amount": 10000.0,
      "currency": "INR",
      "decision": "needs_review",
      "confidence": 0.50,
      "primary_reason": "Probable duplicate of INV-0987 (98% similar)",
      "matched_record": "INV-0987",
      "review_status": "pending"
    }
  ],
  "proposal": null
}
```

### 6. Download Short Exception Report
```bash
curl -X GET "http://localhost:8000/api/uploads/1/report?decision=needs_review,exception" \
  -o ap_exception_report_1.csv
```
Returns sanitized CSV with columns: `invoice_id, invoice_number, vendor_name, invoice_date, total_amount, currency, decision, confidence, exception_type, primary_reason, matched_record, review_status`.
