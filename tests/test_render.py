from __future__ import annotations

from unittest.mock import patch

import pytest
from httpx import AsyncClient

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
async def test_render_valid(client: AsyncClient) -> None:
    """POST /render with valid payload should return 200 with pdf_base64."""
    with patch(
        "api.routers.render.render_pdf_base64",
        return_value="JVBERi0xLjQKfakebase64",
    ):
        response = await client.post("/render", json=VALID_CV_PAYLOAD)

    assert response.status_code == 200
    data = response.json()
    assert "pdf_base64" in data
    assert data["pdf_base64"] == "JVBERi0xLjQKfakebase64"


@pytest.mark.asyncio
async def test_render_missing_cv(client: AsyncClient) -> None:
    """POST /render without cv field should return 400."""
    response = await client.post("/render", json={})

    assert response.status_code == 400
    data = response.json()
    assert data["code"] == "VALIDATION_ERROR"
    assert "details" in data
    assert len(data["details"]) > 0


@pytest.mark.asyncio
async def test_render_invalid_email(client: AsyncClient) -> None:
    """POST /render with invalid email should return 400 with field detail."""
    payload = {
        "cv": {
            "name": "John Doe",
            "email": "not-an-email",
            "sections": {"experience": []},
        }
    }
    response = await client.post("/render", json=payload)

    assert response.status_code == 400
    data = response.json()
    assert data["code"] == "VALIDATION_ERROR"
    assert "details" in data

    # Should have at least one detail mentioning email
    email_details = [d for d in data["details"] if "email" in d.get("field", "")]
    assert len(email_details) > 0, "Expected a validation detail about the email field"


@pytest.mark.asyncio
async def test_render_empty_payload(client: AsyncClient) -> None:
    """POST /render with empty object should return 400."""
    response = await client.post("/render", json={})

    assert response.status_code == 400
    data = response.json()
    assert data["code"] == "VALIDATION_ERROR"
    assert "trace_id" in data
    assert "path" in data
    assert data["path"] == "/render"

    # Verify timestamp is ISO 8601
    from datetime import datetime

    datetime.fromisoformat(data["timestamp"])
