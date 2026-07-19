"""Map application exceptions to the standard API envelope."""

from __future__ import annotations

import logging
from typing import Any
from uuid import uuid4

from backend_shared.exceptions import AppError
from backend_shared.schemas import ApiResponse
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


def _request_id(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


def _json_error(
    *,
    status_code: int,
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
    request_id: str | None = None,
) -> JSONResponse:
    body = ApiResponse[None].fail(
        code=code,
        message=message,
        details=details,
        request_id=request_id,
    )
    return JSONResponse(status_code=status_code, content=body.model_dump(mode="json"))


def register_exception_handlers(app: FastAPI) -> None:
    """Attach handlers so domain errors become consistent JSON responses."""

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        return _json_error(
            status_code=exc.status_code,
            code=exc.error_code,
            message=exc.message,
            details=exc.details,
            request_id=_request_id(request),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return _json_error(
            status_code=422,
            code="VALIDATION_001",
            message="Request validation failed",
            details={"errors": exc.errors()},
            request_id=_request_id(request),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        detail = exc.detail
        details: dict[str, Any]
        if isinstance(detail, dict):
            message = str(detail.get("message", detail))
            code = str(detail.get("code", f"HTTP_{exc.status_code}"))
            raw_details = detail.get("details")
            details = raw_details if isinstance(raw_details, dict) else {}
        else:
            message = str(detail)
            code = f"HTTP_{exc.status_code}"
            details = {}
        return _json_error(
            status_code=exc.status_code,
            code=code,
            message=message,
            details=details,
            request_id=_request_id(request),
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        # Log full traceback server-side; never leak internals to clients.
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        return _json_error(
            status_code=500,
            code="INTERNAL_001",
            message="An unexpected error occurred",
            request_id=_request_id(request) or str(uuid4()),
        )
