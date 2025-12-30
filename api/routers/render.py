from fastapi import APIRouter
from starlette.concurrency import run_in_threadpool

from api.schemas import RenderRequest, RenderResponse
from api.services.rendercv_service import render_pdf_base64

router = APIRouter()


@router.post("/render", response_model=RenderResponse)
async def render_cv(request: RenderRequest) -> RenderResponse:
    payload = request.root
    pdf_base64 = await run_in_threadpool(render_pdf_base64, payload)
    return RenderResponse(pdf_base64=pdf_base64)
