from __future__ import annotations

from datetime import datetime
from unittest.mock import patch

import pytest
from httpx import AsyncClient

from api.core.typst_check import reset_typst_cache


@pytest.mark.asyncio
async def test_health_healthy(client: AsyncClient) -> None:
    """GET /health should return 200 with status='healthy' when Typst is available."""
    reset_typst_cache()
    with patch("api.routers.health.is_typst_available", return_value=True):
        response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"
    assert "timestamp" in data

    # Verify timestamp is ISO 8601
    datetime.fromisoformat(data["timestamp"])


@pytest.mark.asyncio
async def test_health_unhealthy(client: AsyncClient) -> None:
    """GET /health should return 503 with status='unhealthy' when Typst is not available."""
    reset_typst_cache()
    with patch("api.routers.health.is_typst_available", return_value=False):
        response = await client.get("/health")

    assert response.status_code == 503
    data = response.json()
    assert data["status"] == "unhealthy"
    assert data["version"] == "1.0.0"
    assert "timestamp" in data

    # Verify timestamp is ISO 8601
    datetime.fromisoformat(data["timestamp"])
