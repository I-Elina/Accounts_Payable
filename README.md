# Cache Me If You Can ⚡

> **Microsoft Innovate Hackathon 2026** — *The Accounts-Payable Exception Pile Assistant*  
> **Theme:** Smart Assistants & Chatbots (Chat-First AP Assistant)

A deterministic, rules-based decision engine combined with an evidence-grounded AI assistant and a chat-first React interface to process accounts payable exception piles with speed, transparency, and complete auditability.

**Core Philosophy:** *Rules decide. AI explains. A person confirms.*

---

## 👥 Team & Ownership

| Member | Role | Directory Owned | Primary Deliverables |
|---|---|---|---|
| **Member 1** | Decision Engine | `engine/` | Deterministic 2-pass engine, R01–R11 rules, normalization, scoring |
| **Member 2** | Backend & AI | `backend/` | FastAPI, SQLite DB, append-only audit trail, Azure/Mock AI chat assistant |
| **Member 3** | Frontend & UI | `frontend/` | React 18 + Vite, Design Tokens, Assistant chat home, Review queue, Detail views |
| **Member 4** | Data, QA & Scaffolding | `data/`, `scripts/`, `tests/`, `docs/` | Datasets, answer keys, threshold sweep, test suites, documentation |

---

## 🚀 Quick Start (From Repository Root)

### 1. Environment Setup
```bash
# Create virtual environment
python -m venv .venv

# Activate environment
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Backend API
```bash
uvicorn backend.main:app --reload --port 8000
# OpenAPI Docs: http://localhost:8000/docs
```

### 3. Run Frontend UI
```bash
cd frontend
npm install
npm run dev
# Web Interface: http://localhost:5173
```

### 4. Run Test Suite
```bash
pytest
```

### 5. Seed Demo Data
```bash
python -m backend.seed
```

---

## 📂 Repository Layout

```
cache-me-if-you-can/
├── contracts/        # Binding contracts, enums (labels.json), and canonical API examples
├── engine/           # [Member 1] Deterministic Decision Engine Python package
├── backend/          # [Member 2] FastAPI application, database schema, AI summaries & chat
├── frontend/         # [Member 3] React + Vite chat-first user interface
├── data/             # [Member 4] Raw, reference (vendor_master), and processed synthetic datasets
├── scripts/          # [Member 4] Dataset generation, threshold sweep, and evaluation scripts
├── tests/            # [Member 4] Cross-module contract, integration, and AI reliability tests
└── docs/             # [Member 4] Architecture, API specs, setup instructions, and team guides
```

---

## 📜 Canonical Enums & Ground Truth

All components must adhere character-for-character to the specifications in [`contracts/CONTRACT.md`](contracts/CONTRACT.md) and [`contracts/labels.json`](contracts/labels.json).
No direct edits are allowed outside your assigned directory without a team-reviewed Pull Request.
