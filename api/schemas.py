from typing import Any

from pydantic import BaseModel, RootModel


class RenderRequest(RootModel[dict[str, Any]]):
    pass


class RenderResponse(BaseModel):
    pdf_base64: str
