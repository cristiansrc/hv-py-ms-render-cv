from __future__ import annotations

from fastapi import APIRouter, Response
from fastapi.responses import PlainTextResponse
from starlette import status

from api.core.metrics import CONTENT_TYPE_LATEST, generate_latest, is_metrics_enabled

router = APIRouter(tags=["operational"])


@router.get(
    "/metrics",
    summary="Prometheus metrics",
    description="Expone métricas del servicio en formato Prometheus. "
    "Accesible solo desde red interna.",
    responses={
        200: {
            "description": "Métricas en formato Prometheus",
            "content": {"text/plain": {}},
        },
        503: {
            "description": "Métricas deshabilitadas",
            "content": {"text/plain": {"example": "Metrics disabled"}},
        },
    },
)
async def get_metrics() -> Response:
    """Return Prometheus metrics in text/plain format.

    Returns 503 with 'Metrics disabled' when METRICS_ENABLED=false.
    """
    if not is_metrics_enabled():
        return PlainTextResponse(
            content="Metrics disabled",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            media_type="text/plain",
        )

    metrics_data = generate_latest()
    return Response(
        content=metrics_data,
        media_type=CONTENT_TYPE_LATEST,
    )
