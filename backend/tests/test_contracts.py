import json
from pathlib import Path
from backend.schemas import (
    ChatResponse,
    ConfigResponse,
    InvoiceDetailResponse,
    PaginatedAuditResponse,
    PaginatedInvoicesResponse,
    StatsResponse,
    UploadResponse,
)
from backend.settings import REPO_ROOT

EXAMPLES_DIR = REPO_ROOT / "contracts" / "examples"


def test_contract_examples_validate_against_schemas():
    # upload_response
    with open(EXAMPLES_DIR / "upload_response.json", "r", encoding="utf-8") as f:
        UploadResponse(**json.load(f))

    # invoice_list
    with open(EXAMPLES_DIR / "invoice_list.json", "r", encoding="utf-8") as f:
        PaginatedInvoicesResponse(**json.load(f))

    # invoice_detail
    with open(EXAMPLES_DIR / "invoice_detail.json", "r", encoding="utf-8") as f:
        InvoiceDetailResponse(**json.load(f))

    # stats
    with open(EXAMPLES_DIR / "stats.json", "r", encoding="utf-8") as f:
        StatsResponse(**json.load(f))

    # audit
    with open(EXAMPLES_DIR / "audit.json", "r", encoding="utf-8") as f:
        PaginatedAuditResponse(**json.load(f))

    # chat
    with open(EXAMPLES_DIR / "chat.json", "r", encoding="utf-8") as f:
        ChatResponse(**json.load(f))

    # config
    with open(EXAMPLES_DIR / "config.json", "r", encoding="utf-8") as f:
        ConfigResponse(**json.load(f))
