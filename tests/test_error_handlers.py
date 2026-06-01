from __future__ import annotations

import uuid
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from fastapi import Request
from httpx import AsyncClient

from api.core.errors import (
    fallback_exception_handler,
)
from api.core.typst_check import reset_typst_cache


@pytest.mark.asyncio
async def test_fallback_exception() -> None:
    """fallback_exception_handler should return 500 INTERNAL_ERROR without stack trace."""
    mock_request = MagicMock(spec=Request)
    mock_request.url.path = "/render"
    mock_request.state.trace_id = str(uuid.uuid4())

    response = await fallback_exception_handler(
        mock_request, RuntimeError("something unexpected")
    )

    assert response.status_code == 500
    data = response.body
    import json

    body = json.loads(data)
    assert body["code"] == "INTERNAL_ERROR"
    assert body["error"] == "Internal Server Error"

    # Must NOT expose internal error message or stack trace
    assert "something unexpected" not in body["message"]
    assert "RuntimeError" not in body["message"]

    # Must have trace_id
    assert "trace_id" in body
    assert len(body["trace_id"]) > 0

    # Verify timestamp is ISO 8601
    datetime.fromisoformat(body["timestamp"])


@pytest.mark.asyncio
async def test_trace_id_in_error_response(client: AsyncClient) -> None:
    """Error responses should include trace_id."""
    response = await client.post("/render", json={})

    assert response.status_code == 400
    data = response.json()
    assert "trace_id" in data
    assert len(data["trace_id"]) > 0

    # Should be UUID format
    uuid.UUID(data["trace_id"])


@pytest.mark.asyncio
async def test_trace_id_propagation(client: AsyncClient) -> None:
    """X-Trace-Id header should be propagated to error response."""
    custom_trace_id = "550e8400-e29b-41d4-a716-446655440000"
    response = await client.post(
        "/render",
        json={},
        headers={"X-Trace-Id": custom_trace_id},
    )

    assert response.status_code == 400
    data = response.json()
    assert data["trace_id"] == custom_trace_id


@pytest.mark.asyncio
async def test_validation_error_format(client: AsyncClient) -> None:
    """Validation errors should return 400 with details array."""
    response = await client.post(
        "/render",
        json={"cv": {"name": "", "email": "bad", "sections": {}}},
    )

    assert response.status_code == 400
    data = response.json()
    assert data["code"] == "VALIDATION_ERROR"
    assert "details" in data
    assert len(data["details"]) > 0

    # Each detail should have code and message
    for detail in data["details"]:
        assert "code" in detail
        assert "message" in detail
        assert detail["code"] == "FIELD_INVALID"


@pytest.mark.asyncio
async def test_rendercv_user_validation_error() -> None:
    """RenderCVUserValidationError should return 400 with mapped details."""
    from api.core.errors import rendercv_user_validation_error_handler
    from rendercv.exception import RenderCVUserValidationError, RenderCVValidationError

    mock_request = MagicMock(spec=Request)
    mock_request.url.path = "/render"
    mock_request.state.trace_id = str(uuid.uuid4())

    validation_err = RenderCVValidationError(
        location=("cv", "name"),
        yaml_location=None,
        message="Name is required",
        input="",
    )
    exc = RenderCVUserValidationError(validation_errors=[validation_err])

    response = await rendercv_user_validation_error_handler(mock_request, exc)

    assert response.status_code == 400
    import json

    body = json.loads(response.body)
    assert body["code"] == "VALIDATION_ERROR"
    assert len(body["details"]) == 1
    assert body["details"][0]["message"] == "Name is required"
