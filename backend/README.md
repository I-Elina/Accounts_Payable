# Backend Service: Cache Me If You Can 🚀

FastAPI backend service powering the Accounts Payable Exception Pile assistant for Microsoft Innovate Hackathon 2026.

---

## 🏗️ Architecture & Philosophy

- **Rules Decide**: The deterministic decision engine (`engine`) flags invoices into `auto_pass`, `needs_review`, or `exception`.
- **AI Explains**: Grounded AI summaries and chat assistant explain reasons and suggest actions. **AI never modifies records or approves invoices**.
- **Humans Confirm**: Reviews require human reviewers with explicit actions (`approve` or `reject`).
- **Complete Audit Trail**: Every ingestion, flag, AI summary, user review, and settings update is immutably logged to `audit_log`.

---

## ⚙️ Environment Variables

Copy `backend/.env.example` to `backend/.env`:

| Variable | Default | Description |
|---|---|---|
| `AI_MODE` | `mock` | `mock` (offline deterministic template) or `azure` (Azure OpenAI) |
| `DB_PATH` | `backend/data/app.db` | Path to SQLite database file |
| `MAX_UPLOAD_MB` | `10` | Maximum upload file size in megabytes |
| `AZURE_OPENAI_ENDPOINT` | - | Azure OpenAI resource endpoint URL |
| `AZURE_OPENAI_API_KEY` | - | Azure OpenAI API key |
| `AZURE_OPENAI_DEPLOYMENT` | - | Deployment / model name |
| `AZURE_OPENAI_API_VERSION` | `2024-02-15-preview` | API version |

---

## 🏃 Running Locally

```bash
# From repository root
uvicorn backend.main:app --reload --port 8000
```
- Interactive Swagger API Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
- OpenAPI Specification: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

### Seeding Demo Data
```bash
python -m backend.seed
```

---

## 📡 REST API Endpoints & Examples

### 1. Health Check
```bash
curl http://localhost:8000/api/health
```

### 2. Upload Invoice Batch
```bash
curl -X POST http://localhost:8000/api/uploads \
  -F "file=@data/processed/invoices_demo.csv" \
  -F "uploaded_by=Shree" \
  -F "use_history=false"
```

### 3. List Invoices with Filters
```bash
curl "http://localhost:8000/api/invoices?decision=needs_review,exception&sort=confidence&order=asc"
```

### 4. Get Invoice Detail
```bash
curl http://localhost:8000/api/invoices/1
```

### 5. Generate AI Explanation
```bash
curl -X POST http://localhost:8000/api/invoices/1/summary
```

### 6. Review Invoice (Approve / Reject)
```bash
curl -X POST http://localhost:8000/api/invoices/1/review \
  -H "Content-Type: application/json" \
  -d '{"action": "approve", "reviewer": "Shree", "comment": "Verified with vendor"}'
```

### 7. Dashboard Statistics
```bash
curl http://localhost:8000/api/stats
```

### 8. Audit Trail
```bash
curl http://localhost:8000/api/audit?page=1&page_size=25
```

### 9. Assistant Chat (Chat-First Home)
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Why was INV-1042 flagged?"}'
```

### 10. Download Short Report CSV
```bash
curl -O http://localhost:8000/api/uploads/1/report
```

### 11. Configuration Thresholds
```bash
curl http://localhost:8000/api/config
curl -X PUT http://localhost:8000/api/config \
  -H "Content-Type: application/json" \
  -d '{"auto_pass_threshold": 0.80, "exception_below": 0.35}'
```
