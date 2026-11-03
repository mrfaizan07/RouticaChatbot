"""API integration tests for /health and /ready probes."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_probe(async_client: AsyncClient):
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "app_name" in data


@pytest.mark.asyncio
async def test_ready_probe(async_client: AsyncClient):
    response = await async_client.get("/ready")
    assert response.status_code in (200, 503)
    data = response.json()
    assert "database" in data
    assert "vector_search" in data
    assert "ai_providers" in data


@pytest.mark.asyncio
async def test_api_v1_health_prefix(async_client: AsyncClient):
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

