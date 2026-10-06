from typing import Any
from backend.ai.mock_llm import mock_generate_summary
from backend.ai.validate import validate_summary
from backend.settings import AI_MODE


def generate_summary(decision_record: dict[str, Any]) -> dict[str, Any]:
    """Generate plain-English explanation of flagged invoice decisions.

    Contract function: Never decides, only explains based on verified record facts.
    """
    if AI_MODE == "gemini":
        try:
            from backend.ai.llm_client import call_gemini_summary
            result = call_gemini_summary(decision_record)
            if validate_summary(result, decision_record):
                return result
        except Exception:
            pass
        return mock_generate_summary(decision_record)

    if AI_MODE == "azure":
        try:
            from backend.ai.llm_client import call_azure_summary
            # Attempt 1
            result = call_azure_summary(decision_record)
            if validate_summary(result, decision_record):
                return result
            # Retry once
            result = call_azure_summary(decision_record)
            if validate_summary(result, decision_record):
                return result
        except Exception:
            pass
        # Fall back to deterministic template
        return mock_generate_summary(decision_record)

    # Default mock mode
    return mock_generate_summary(decision_record)
