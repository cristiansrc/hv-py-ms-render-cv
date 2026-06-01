from __future__ import annotations

import os
from datetime import datetime, timezone

from fastapi import APIRouter, Response, status

from api.core.typst_check import is_typst_available
from api.schemas import HealthResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Verifica que el servicio está operativo y Typst está disponible.",
    tags=["operational"],
)
async def get_health(response: Response) -> HealthResponse:
    """Health check endpoint.

    Returns 200 with status="healthy" if Typst is available.
    Returns 503 with status="unhealthy" if Typst is not available.
    """
    app_version = os.environ.get("APP_VERSION", "1.0.0")
    typst_ok = is_typst_available()

    response.status_code = status.HTTP_200_OK if typst_ok else status.HTTP_503_SERVICE_UNAVAILABLE

    return HealthResponse(
        status="healthy" if typst_ok else "unhealthy",
        timestamp=datetime.now(timezone.utc),
        version=app_version,
    )
