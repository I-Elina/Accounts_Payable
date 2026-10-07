"""Route an invoice to a decision based on score and violations."""

from __future__ import annotations

from engine.schemas import Violation


def route(score: float, violations: list[Violation], cfg: dict) -> str:
    """Return 'auto_pass', 'needs_review', or 'exception'."""
    if any(v.severity == "hard" for v in violations):
        return "exception"
    if score >= cfg["auto_pass_threshold"]:
        return "auto_pass"
    if score >= cfg["exception_below"]:
        return "needs_review"
    return "exception"
