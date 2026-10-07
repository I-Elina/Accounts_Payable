# Frontend — Cache Me If You Can (Microsoft Innovate 2026)

React + Vite frontend for **Cache Me If You Can** AP Exception Pile Assistant.

## Routes
- `/` — Assistant (Chat-first home screen with inline exception cards, upload button, and review proposals)
- `/queue` — Review Queue (Pending exceptions & low confidence invoices sorted by risk)
- `/invoices` — Invoices (Full filterable invoice table with search & sorting)
- `/invoices/:id` — Invoice Detail (Score breakdown, matched record comparison, AI explanation, approve/reject review)
- `/dashboard` — Dashboard (Metrics, Decision Donut, Exceptions Bar chart, Confidence Histogram with auto-pass threshold line)
- `/audit` — Audit Log (Complete audit trail of all engine, AI, user, and system events)
- `/upload` — Upload (Drag & drop invoice CSV/Excel upload zone)
- `/settings` — Settings (Auto-pass & exception thresholds, rules catalogue)

## Getting Started

```bash
# Install dependencies
npm install

# Run mock mode (standalone frontend)
npm run dev

# Run sync mocks script
npm run sync:mocks
```

## Environment Variables
- `VITE_USE_MOCK=true` — Standalone mode with realistic mock API & data.
- `VITE_USE_MOCK=false` — Connects to real FastAPI backend at `http://localhost:8000`.
