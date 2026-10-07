import os
from pathlib import Path
from dotenv import load_dotenv

# Load backend/.env if present, otherwise .env from root
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

REPO_ROOT = Path(__file__).resolve().parent.parent

AI_MODE = os.getenv("AI_MODE", "mock").lower()
DB_PATH = os.getenv("DB_PATH", "backend/data/app.db")
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "10"))

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# Normalize DB_PATH to absolute path based on repo root if relative
def get_db_file_path() -> Path:
    p = Path(DB_PATH)
    if not p.is_absolute():
        return REPO_ROOT / p
    return p
