"""Application exception hierarchy.

Every exception carries an ``error_code`` from the catalogue documented in
docs/TECHNICAL_DESIGN.md ("Error Codes") and an HTTP ``status_code``, so an
API error handler can translate any of these into the standard response
envelope without a lookup table.
"""

from typing import Any


class AppError(Exception):
    """Base class for all application errors.

    Args:
        message: Human-readable description, safe to return to clients.
        error_code: Stable code from the documented catalogue (e.g. AUTH_001).
        details: Optional structured context (field errors, identifiers).
            Never put secrets or raw upstream payloads here — it is serialized
            into API responses.
    """

    error_code: str = "INTERNAL_001"
    status_code: int = 500

    def __init__(
        self,
        message: str,
        *,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}
        if error_code is not None:
            self.error_code = error_code


class ValidationError(AppError):
    """Request data failed validation."""

    error_code = "VALIDATION_001"
    status_code = 422


class AuthenticationError(AppError):
    """Caller could not be authenticated (missing/invalid credentials)."""

    error_code = "AUTH_001"
    status_code = 401


class AuthorizationError(AppError):
    """Caller is authenticated but not allowed to access the resource."""

    error_code = "AUTH_007"
    status_code = 403


class NotFoundError(AppError):
    """Requested resource does not exist."""

    error_code = "NOT_FOUND_001"
    status_code = 404


class ConflictError(AppError):
    """Request conflicts with current state (e.g. duplicate email)."""

    error_code = "CONFLICT_001"
    status_code = 409


class RateLimitError(AppError):
    """Caller exceeded a rate limit."""

    error_code = "RATE_LIMIT_001"
    status_code = 429


class DatabaseError(AppError):
    """Database operation failed."""

    error_code = "DB_001"
    status_code = 500


class ExternalServiceError(AppError):
    """An upstream dependency (LLM API, Pushover, S3) failed."""

    error_code = "EXTERNAL_001"
    status_code = 502
