from typing import Any
from backend.database import get_conn
from backend.errors import ApiError
from backend.schemas import ConfigResponse, ConfigRule, ConfigUpdateRequest
from backend.services.audit_service import log_event

RULE_CATALOGUE = [
    {"rule_id": "R01", "name": "Missing required field", "severity": "hard", "penalty": 0.50, "enabled": True, "exception_type": "missing_field"},
    {"rule_id": "R02", "name": "Invalid amount", "severity": "hard", "penalty": 0.60, "enabled": True, "exception_type": "invalid_amount"},
    {"rule_id": "R03", "name": "Invalid date", "severity": "hard", "penalty": 0.40, "enabled": True, "exception_type": "invalid_date"},
    {"rule_id": "R04", "name": "Future date", "severity": "soft", "penalty": 0.30, "enabled": True, "exception_type": "future_date"},
    {"rule_id": "R05", "name": "Calculation mismatch", "severity": "soft", "penalty": 0.35, "enabled": True, "exception_type": "calculation_mismatch"},
    {"rule_id": "R06", "name": "Exact duplicate", "severity": "hard", "penalty": 0.80, "enabled": True, "exception_type": "exact_duplicate"},
    {"rule_id": "R07", "name": "Policy limit exceeded", "severity": "soft", "penalty": 0.20, "enabled": True, "exception_type": "policy_limit"},
    {"rule_id": "R08", "name": "Unknown vendor or category", "severity": "soft", "penalty": 0.20, "enabled": True, "exception_type": "unknown_vendor"},
    {"rule_id": "R09", "name": "Fuzzy duplicate", "severity": "soft", "penalty": 0.35, "enabled": True, "exception_type": "fuzzy_duplicate"},
    {"rule_id": "R10", "name": "Near-identical amount", "severity": "soft", "penalty": 0.15, "enabled": True, "exception_type": "fuzzy_duplicate"},
    {"rule_id": "R11", "name": "Amount outlier", "severity": "soft", "penalty": 0.20, "enabled": True, "exception_type": "amount_outlier"},
]


def get_current_config() -> ConfigResponse:
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM settings")
        rows = dict(cursor.fetchall())

        auto_pass = float(rows.get("auto_pass_threshold", "0.85"))
        exception_below = float(rows.get("exception_below", "0.40"))
        policy_limit = float(rows.get("policy_limit", "100000"))

        rules = [ConfigRule(**r) for r in RULE_CATALOGUE]

        return ConfigResponse(
            auto_pass_threshold=auto_pass,
            exception_below=exception_below,
            policy_limit=policy_limit,
            rules=rules,
        )
    finally:
        conn.close()


def update_config(update_req: ConfigUpdateRequest) -> ConfigResponse:
    current = get_current_config()
    new_auto_pass = update_req.auto_pass_threshold if update_req.auto_pass_threshold is not None else current.auto_pass_threshold
    new_exception_below = update_req.exception_below if update_req.exception_below is not None else current.exception_below

    if not (0.0 <= new_exception_below < new_auto_pass <= 1.0):
        raise ApiError(
            code="VALIDATION_ERROR",
            message=f"Invalid threshold configuration: expected 0 <= exception_below < auto_pass_threshold <= 1, got exception_below={new_exception_below}, auto_pass_threshold={new_auto_pass}",
            details=["exception_below must be strictly less than auto_pass_threshold and both between 0 and 1"],
            status_code=422,
        )

    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", ("auto_pass_threshold", str(new_auto_pass)))
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", ("exception_below", str(new_exception_below)))
        conn.commit()

        log_event(
            actor="system",
            actor_type="system",
            event_type="SETTINGS_CHANGED",
            details={
                "auto_pass_threshold": new_auto_pass,
                "exception_below": new_exception_below,
            },
        )
        return get_current_config()
    finally:
        conn.close()
