"""API tests for admin dashboard, provider status, and access restrictions."""

from unittest.mock import AsyncMock
import pytest
from httpx import AsyncClient

from app.dependencies import (
    get_current_admin,
    get_document_repo,
    get_knowledge_repo,
    get_product_repo,
    get_user_repo,
    get_website_page_repo,
)
from app.models.user import User


@pytest.mark.asyncio
async def test_admin_dashboard_requires_authentication(async_client: AsyncClient):
    response = await async_client.get("/api/v1/admin/dashboard")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_admin_dashboard_success(app, async_client: AsyncClient, mock_admin_user: User):
    app.dependency_overrides[get_current_admin] = lambda: mock_admin_user

    mock_user_repo = AsyncMock()
    mock_user_repo.count_admins.return_value = 1
    mock_product_repo = AsyncMock()
    mock_product_repo.list_products.return_value = []
    mock_page_repo = AsyncMock()
    mock_page_repo.count.return_value = 5
    mock_knowledge_repo = AsyncMock()
    mock_knowledge_repo.count_chunks.return_value = 25
    mock_doc_repo = AsyncMock()
    mock_doc_repo.count.return_value = 2

    app.dependency_overrides[get_user_repo] = lambda: mock_user_repo
    app.dependency_overrides[get_product_repo] = lambda: mock_product_repo
    app.dependency_overrides[get_website_page_repo] = lambda: mock_page_repo
    app.dependency_overrides[get_knowledge_repo] = lambda: mock_knowledge_repo
    app.dependency_overrides[get_document_repo] = lambda: mock_doc_repo

    response = await async_client.get("/api/v1/admin/dashboard")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["total_users"] == 1
    assert data["total_pages_scraped"] == 5
    assert data["total_knowledge_chunks"] == 25


@pytest.mark.asyncio
async def test_providers_status_endpoint(app, async_client: AsyncClient, mock_admin_user: User):
    app.dependency_overrides[get_current_admin] = lambda: mock_admin_user
    response = await async_client.get("/api/v1/admin/providers/status")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert "primary_provider" in data
    assert "embedding_dimensions" in data

