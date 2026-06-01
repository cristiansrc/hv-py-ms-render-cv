from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from api.schemas import ApiErrorDetail, ApiErrorResponse
from rendercv.exception import (
    RenderCVInternalError,
    RenderCVUserError,
    RenderCVUserValidationError,
)

logger = logging.getLogger("api.errors")


def _get_trace_id(request: Request) -> str:
    """Get trace_id from request state or generate a fallback UUID4."""
    trace_id = getattr(request.state, "trace_id", None)
    if trace_id:
        return trace_id
    return str(uuid.uuid4())


def _make_error_response(
    request: Request,
    status_code: int,
    code: str,
    error: str,
    message: str,
    details: list[ApiErrorDetail] | None = None,
) -> JSONResponse:
    """Build a JSON response with ApiErrorResponse structure."""
    error_response = ApiErrorResponse(
        timestamp=datetime.now(timezone.utc),
        status=status_code,
        error=error,
        code=code,
        message=message,
        path=request.url.path,
        trace_id=_get_trace_id(request),
        details=details or [],
    )
    return JSONResponse(
        status_code=status_code,
        content=error_response.model_dump(mode="json"),
    )


async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle FastAPI/Pydantic validation errors (400 VALIDATION_ERROR)."""
    details: list[ApiErrorDetail] = []
    for error in exc.errors():
        loc_parts = [str(p) for p in error.get("loc", [])]
        # Skip "body" prefix from loc for cleaner field paths
        if loc_parts and loc_parts[0] == "body":
            loc_parts = loc_parts[1:]
        details.append(
            ApiErrorDetail(
                field=".".join(loc_parts) if loc_parts else None,
                code="FIELD_INVALID",
                message=error.get("msg", "Invalid field"),
                rejected_value=error.get("input"),
            )
        )

    return _make_error_response(
        request=request,
        status_code=status.HTTP_400_BAD_REQUEST,
        code="VALIDATION_ERROR",
        error="Bad Request",
        message="The request contains invalid fields.",
        details=details,
    )


async def rendercv_user_validation_error_handler(
    request: Request, exc: RenderCVUserValidationError
) -> JSONResponse:
    """Handle RenderCVUserValidationError (400 VALIDATION_ERROR)."""
    details: list[ApiErrorDetail] = []
    for validation_error in exc.validation_errors:
        details.append(
            ApiErrorDetail(
                field=".".join(str(p) for p in validation_error.location) if validation_error.location else None,
                code="FIELD_INVALID",
                message=getattr(validation_error, "message", str(validation_error)),
                rejected_value=getattr(validation_error, "input", None),
            )
        )

    return _make_error_response(
        request=request,
        status_code=status.HTTP_400_BAD_REQUEST,
        code="VALIDATION_ERROR",
        error="Bad Request",
        message="The CV data contains invalid fields.",
        details=details,
    )


async def rendercv_user_error_handler(
    request: Request, exc: RenderCVUserError
) -> JSONResponse:
    """Handle RenderCVUserError (400 RENDERCV_USER_ERROR)."""
    return _make_error_response(
        request=request,
        status_code=status.HTTP_400_BAD_REQUEST,
        code="RENDERCV_USER_ERROR",
        error="Bad Request",
        message=getattr(exc, "message", "The CV data is incomplete or invalid."),
        details=[],
    )


async def rendercv_internal_error_handler(
    request: Request, exc: RenderCVInternalError
) -> JSONResponse:
    """Handle RenderCVInternalError (500 INTERNAL_ERROR).

    Does NOT expose exc.message to avoid leaking internal details.
    """
    logger.exception("RenderCVInternalError trace_id=%s", _get_trace_id(request))
    return _make_error_response(
        request=request,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="INTERNAL_ERROR",
        error="Internal Server Error",
        message="An unexpected error occurred.",
        details=[],
    )


async def fallback_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Fallback handler for any unhandled Exception (500 INTERNAL_ERROR).

    Does NOT expose str(exc) or stack traces in the response body.
    The stack trace is logged internally.
    """
    logger.exception(
        "Unhandled exception trace_id=%s: %s",
        _get_trace_id(request),
        type(exc).__name__,
    )
    return _make_error_response(
        request=request,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="INTERNAL_ERROR",
        error="Internal Server Error",
        message="An unexpected error occurred.",
        details=[],
    )
