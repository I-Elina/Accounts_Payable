"""Compute confidence score from rule violations."""

from __future__ import annotations

from engine.schemas import Violation


def compute_score(violations: list[Violation]) -> float:
    """confidence = max(0, 1 - sum(penalties)), rounded to 2 decimals."""
    total_penalty = sum(v.penalty for v in violations)
    return round(max(0.0, 1.0 - total_penalty), 2)
