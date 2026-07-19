"""Base Pydantic schemas and the standard API response envelope.

The envelope shape mirrors docs/TECHNICAL_DESIGN.md ("Response Format").
"""

from datetime import datetime, timezone
from typing import Any, Generic, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class BaseSchema(BaseModel):
    """Base for schemas that may be built from ORM objects."""

    model_config = ConfigDict(from_attributes=True)


class ErrorDetail(BaseModel):
    """Error payload carried by an error response."""

    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class ResponseMeta(BaseModel):
    """Per-response metadata for tracing and debugging."""

    timestamp: datetime = Field(default_factory=_utc_now)
    request_id: str | None = None


class ApiResponse(BaseModel, Generic[T]):
    """Envelope wrapping every API response.

    Use :meth:`ok` / :meth:`fail` rather than constructing directly, so the
    ``status`` field always agrees with which of data/error is populated.
    """

    status: Literal["success", "error"]
    data: T | None = None
    error: ErrorDetail | None = None
    meta: ResponseMeta = Field(default_factory=ResponseMeta)

    @classmethod
    def ok(cls, data: T | None = None, *, request_id: str | None = None) -> "ApiResponse[T]":
        """Build a success response."""
        return cls(
            status="success",
            data=data,
            meta=ResponseMeta(request_id=request_id),
        )

    @classmethod
    def fail(
        cls,
        code: str,
        message: str,
        *,
        details: dict[str, Any] | None = None,
        request_id: str | None = None,
    ) -> "ApiResponse[T]":
        """Build an error response."""
        return cls(
            status="error",
            error=ErrorDetail(code=code, message=message, details=details or {}),
            meta=ResponseMeta(request_id=request_id),
        )


class PaginationMeta(BaseModel):
    """Pagination metadata for list endpoints."""

    total: int
    limit: int
    offset: int

    @property
    def has_more(self) -> bool:
        """Whether more records exist beyond this page."""
        return self.offset + self.limit < self.total
