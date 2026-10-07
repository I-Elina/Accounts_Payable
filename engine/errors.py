"""Custom exceptions for the engine package."""


class IngestionError(Exception):
    """Raised when a file-level problem prevents processing.

    Attributes:
        message: Human-readable description of the problem.
        details: List of specific issues found (e.g. missing columns).
    """

    def __init__(self, message: str, details: list[str] | None = None):
        self.message = message
        self.details = details or []
        super().__init__(self.message)
