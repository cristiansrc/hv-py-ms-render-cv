from __future__ import annotations

from fastapi import APIRouter
from starlette.concurrency import run_in_threadpool

from api.schemas import RenderRequest, RenderResponse
from api.services.rendercv_service import render_pdf_base64

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
    payload = request.model_dump(mode="json")
    pdf_base64 = await run_in_threadpool(render_pdf_base64, payload)
    return RenderResponse(pdf_base64=pdf_base64)
