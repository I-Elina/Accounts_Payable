# Cache Me If You Can: Setup & Developer Guide 🛠️

A complete 10-step setup guide for Windows, macOS, and Linux workstations.

---

## Prerequisites
- **Python 3.11.x** (Verify with `python --version`)
- **Node.js 20.x** & **npm 10.x** (Verify with `node -v` and `npm -v`)
- **Git** (Verify with `git --version`)

---

## 10-Step Setup Walkthrough

### Step 1: Clone the Repository
```bash
git clone https://github.com/I-Elina/Accounts_Payable.git
cd Accounts_Payable
```

### Step 2: Create Python Virtual Environment
**Windows:**
```powershell
python -m venv .venv
.venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Backend Environment Variables
Copy the template in `backend/.env.example` to `backend/.env`:
```bash
# Windows PowerShell:
Copy-Item backend/.env.example backend/.env

# macOS / Linux:
cp backend/.env.example backend/.env
```

Contents of `backend/.env`:
```ini
AI_MODE=mock
DB_PATH=backend/data/app.db
MAX_UPLOAD_MB=10

# Optional Azure OpenAI settings (required only for live cloud demo):
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

### Step 5: Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

### Step 6: Verify Contracts and Enums
```bash
python scripts/validate_contracts.py
```
Expected output: `All contract examples and labels match specifications character-for-character!`

### Step 7: Run Automated Test Suites
```bash
pytest
```
Runs engine tests, contract tests, AI reliability tests, and integration tests.

### Step 8: Seed Demo Database (Optional Quick Start)
```bash
python -m backend.seed
```
Seeds SQLite database (`backend/data/app.db`) with 1,000 processed demo invoices, AI summaries, and audit trail records.

### Step 9: Launch Backend API Server
```bash
uvicorn backend.main:app --reload --port 8000
```
- Swagger API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health Check: [http://localhost:8000/api/health](http://localhost:8000/api/health)

### Step 10: Launch Frontend Web UI
In a separate terminal window:
```bash
cd frontend
npm run dev
```
- Web Application: [http://localhost:5173](http://localhost:5173)

---

## Common Troubleshooting

| Issue | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'engine'` | Python command run from subfolder | Always execute commands from repository root with `.venv` active |
| `UserWarning: Parsing dates in %Y-%m-%d format...` | Pandas `dayfirst=True` heuristic | Expected warning handled by normalization layer; clean datasets use safe day values |
| Port 8000 already in use | Stale uvicorn instance | Run `Get-Process python | Stop-Process` (Windows) or `killall uvicorn` (Mac) |
| Missing Azure API keys | `AI_MODE=azure` without credentials | Keep `AI_MODE=mock` in `backend/.env` for local testing |
