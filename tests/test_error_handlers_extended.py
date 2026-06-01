from __future__ import annotations

import json
import uuid
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from fastapi import Request

from api.core.errors import (
    rendercv_internal_error_handler,
    rendercv_user_error_handler,
)
from rendercv.exception import RenderCVInternalError, RenderCVUserError


@pytest.mark.asyncio
async def test_rendercv_user_error_handler() -> None:
    """RenderCVUserError should return 400 with RENDERCV_USER_ERROR code."""
    mock_request = MagicMock(spec=Request)
    mock_request.url.path = "/render"
    mock_request.state.trace_id = str(uuid.uuid4())

    exc = RenderCVUserError("Missing required field: name")
    response = await rendercv_user_error_handler(mock_request, exc)

    assert response.status_code == 400
    body = json.loads(response.body)
    assert body["code"] == "RENDERCV_USER_ERROR"
    assert body["error"] == "Bad Request"
    assert body["status"] == 400
    assert body["path"] == "/render"
    assert body["details"] == []
    # Should include the message from the exception
    assert "Missing required field" in body["message"]

    # Verify timestamp is ISO 8601
    datetime.fromisoformat(body["timestamp"])


@pytest.mark.asyncio
async def test_rendercv_user_error_handler_with_custom_message() -> None:
    """RenderCVUserError with custom message should include it in response."""
    mock_request = MagicMock(spec=Request)
    mock_request.url.path = "/render"
    mock_request.state.trace_id = str(uuid.uuid4())

    exc = RenderCVUserError(message="Custom error message")
    response = await rendercv_user_error_handler(mock_request, exc)

    assert response.status_code == 400
    body = json.loads(response.body)
    assert body["code"] == "RENDERCV_USER_ERROR"
    assert body["message"] == "Custom error message"


@pytest.mark.asyncio
async def test_rendercv_user_error_handler_with_none_message() -> None:
    """RenderCVUserError with message=None should use default message."""
    mock_request = MagicMock(spec=Request)
    mock_request.url.path = "/render"
    mock_request.state.trace_id = str(uuid.uuid4())

    exc = RenderCVUserError(message=None)
    response = await rendercv_user_error_handler(mock_request, exc)

    assert response.status_code == 400
    body = json.loads(response.body)
    assert body["code"] == "RENDERCV_USER_ERROR"
    assert body["message"] == "The CV data is incomplete or invalid."


@pytest.mark.asyncio
async def test_rendercv_internal_error_handler() -> None:
    """RenderCVInternalError should return 500 without leaking internal details."""
    mock_request = MagicMock(spec=Request)
    mock_request.url.path = "/render"
    mock_request.state.trace_id = str(uuid.uuid4())

    exc = RenderCVInternalError("Database connection failed: password=secret")
    response = await rendercv_internal_error_handler(mock_request, exc)

    assert response.status_code == 500
    body = json.loads(response.body)
    assert body["code"] == "INTERNAL_ERROR"
    assert body["error"] == "Internal Server Error"
    assert body["status"] == 500
    assert body["path"] == "/render"
    assert body["details"] == []

    # Must NOT expose internal error message
    assert "Database connection failed" not in body["message"]
    assert "password=secret" not in body["message"]
    assert body["message"] == "An unexpected error occurred."

    # Verify timestamp is ISO 8601
    datetime.fromisoformat(body["timestamp"])


@pytest.mark.asyncio
async def test_rendercv_internal_error_handler_logs_exception() -> None:
    """RenderCVInternalError handler should log the exception."""
    mock_request = MagicMock(spec=Request)
    mock_request.url.path = "/render"
    mock_request.state.trace_id = str(uuid.uuid4())

    exc = RenderCVInternalError("Something went wrong")

    with patch("api.core.errors.logger.exception") as mock_log:
        await rendercv_internal_error_handler(mock_request, exc)

    mock_log.assert_called_once()
    call_args = mock_log.call_args[0]
    assert "RenderCVInternalError" in call_args[0]
    assert mock_request.state.trace_id in call_args[1]


@pytest.mark.asyncio
async def test_get_trace_id_generates_uuid_when_missing() -> None:
    """_get_trace_id should generate UUID when request.state has no trace_id."""
    from api.core.errors import _get_trace_id

    mock_request = MagicMock(spec=Request)
    # Simulate missing trace_id attribute
    del mock_request.state.trace_id

    trace_id = _get_trace_id(mock_request)

    # Should be a valid UUID
    uuid.UUID(trace_id)
    assert len(trace_id) == 36  # UUID4 format
