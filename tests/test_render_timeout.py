from __future__ import annotations

import time
from unittest.mock import patch

import pytest
from httpx import AsyncClient

from api.core.typst_check import reset_typst_cache

VALID_CV_PAYLOAD = {
    "cv": {
        "name": "John Doe",
        "email": "john.doe@email.com",
        "sections": {
            "experience": [
                {
                    "company": "Acme Corp",
                    "position": "Senior Engineer",
                    "start_date": "2023-01",
                    "end_date": "present",
                }
            ]
        },
        "locale": {"language": "english"},
        "design": {"theme": "engineeringclassic"},
    }
}


@pytest.mark.asyncio
async def test_render_timeout_raises_internal_error(client: AsyncClient) -> None:
    """POST /render should return 500 when render_pdf_base64 times out."""
    reset_typst_cache()

    def slow_render(*args, **kwargs):
        # Simulate a render that takes longer than the timeout
        time.sleep(10)
        return "fake_pdf_base64"

    # Set a very short timeout to trigger the timeout path
    with patch.dict(__import__("os").environ, {"RENDER_TIMEOUT": "0.1"}, clear=False):
        with patch(
            "api.routers.render.render_pdf_base64",
            side_effect=slow_render,
        ):
            response = await client.post("/render", json=VALID_CV_PAYLOAD)

    assert response.status_code == 500
    data = response.json()
    assert data["code"] == "INTERNAL_ERROR"
    assert data["error"] == "Internal Server Error"
    # Should not leak internal timeout details
    assert "timed out" not in data["message"].lower()
    assert data["message"] == "An unexpected error occurred."
