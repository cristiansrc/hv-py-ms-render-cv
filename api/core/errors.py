from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse

from rendercv.exception import (
    RenderCVInternalError,
    RenderCVUserError,
    RenderCVUserValidationError,
)


def _format_validation_errors(error: RenderCVUserValidationError) -> list[dict[str, Any]]:
    formatted: list[dict[str, Any]] = []
    for validation_error in error.validation_errors:
        formatted.append(
            {
                "location": validation_error.location,
                "yaml_location": validation_error.yaml_location,
                "message": validation_error.message,
                "input": validation_error.input,
            }
        )
    return formatted


async def rendercv_user_validation_error_handler(
    _: Request, exc: RenderCVUserValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"type": "validation_error", "errors": _format_validation_errors(exc)},
    )


async def rendercv_user_error_handler(
    _: Request, exc: RenderCVUserError
) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"type": "user_error", "message": exc.message},
    )


async def rendercv_internal_error_handler(
    _: Request, exc: RenderCVInternalError
) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"type": "internal_error", "message": exc.message},
    )
