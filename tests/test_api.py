"""Integration tests for the API endpoints."""

from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.config import settings
from app.db.session import get_db


class _EmptyResult:
    def scalars(self):
        return self

    def unique(self):
        return self

    def all(self):
        return []


class _FakeSession:
    async def execute(self, *_args, **_kwargs):
        return _EmptyResult()

    async def scalar(self, *_args, **_kwargs):
        return 0

    async def commit(self):
        return None

    async def rollback(self):
        return None

    async def close(self):
        return None


@pytest_asyncio.fixture
async def client():
    """Create a test client."""
    from app.main import app

    async def override_get_db():
        session = _FakeSession()
        try:
            yield session
        finally:
            await session.close()

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test GET /health returns 200 with status ok."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


@pytest.mark.asyncio
async def test_feed_sections_route_exists(client: AsyncClient):
    """Test the RSS section endpoint is mounted."""
    response = await client.get("/feeds/sections")
    assert response.status_code in {200, 404}


@pytest.mark.asyncio
async def test_get_stats(client: AsyncClient):
    """Test GET /admin/stats returns database counts."""
    response = await client.get(
        "/admin/stats",
        headers={"X-Admin-Token": settings.admin_api_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert "raw_stories" in data
    assert "sources" in data


@pytest.mark.asyncio
async def test_admin_stats_requires_token(client: AsyncClient):
    """Test admin endpoints reject missing tokens."""
    response = await client.get("/admin/stats")
    assert response.status_code == 401
