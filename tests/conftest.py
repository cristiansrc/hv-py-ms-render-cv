from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from api.main import app


@pytest.fixture
def app_fixture():
    """Return the FastAPI app instance."""
    return app


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Return an async HTTP client for testing.

    Uses ASGITransport to run the FastAPI app without a server.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
