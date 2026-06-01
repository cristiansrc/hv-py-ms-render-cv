from __future__ import annotations

import asyncio
import os

from fastapi import APIRouter
from starlette.concurrency import run_in_threadpool

from api.schemas import RenderRequest, RenderResponse
from api.services.rendercv_service import render_pdf_base64
from rendercv.exception import RenderCVInternalError

router = APIRouter()


@router.post(
    "/render",
    response_model=RenderResponse,
    summary="Generar PDF de CV",
    description="Genera un PDF ATS-friendly a partir de datos de CV estructurados.",
    tags=["render"],
)
async def render_cv(request: RenderRequest) -> RenderResponse:
    """Render a CV PDF from structured data."""
    timeout_seconds = float(os.environ.get("RENDER_TIMEOUT", "30"))
    payload = request.model_dump(mode="json")
    try:
        async with asyncio.timeout(timeout_seconds):
            pdf_base64 = await run_in_threadpool(render_pdf_base64, payload)
    except TimeoutError:
        raise RenderCVInternalError("PDF generation timed out.")
    return RenderResponse(pdf_base64=pdf_base64)
