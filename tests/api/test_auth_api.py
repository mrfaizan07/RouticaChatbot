"""API tests for administrator login and user verification."""

from unittest.mock import AsyncMock
import pytest
from httpx import AsyncClient

from app.core.security import create_access_token, hash_password
from app.dependencies import get_user_repo
from app.models.user import User


@pytest.mark.asyncio
async def test_admin_login_success(app, async_client: AsyncClient):
    mock_user = User(
        _id="65f1234567890abcdef12345",
        email="admin@routica.com",
        password_hash=hash_password("ValidPassword123!"),
        role="admin",
        is_active=True,
    )
    mock_repo = AsyncMock()
    mock_repo.get_by_email.return_value = mock_user
    mock_repo.update_last_login.return_value = None

    app.dependency_overrides[get_user_repo] = lambda: mock_repo

    response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@routica.com", "password": "ValidPassword123!"},
    )
    app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "admin"


@pytest.mark.asyncio
async def test_admin_login_failure_wrong_password(app, async_client: AsyncClient):
    mock_user = User(
        _id="65f1234567890abcdef12345",
        email="admin@routica.com",
        password_hash=hash_password("ValidPassword123!"),
        role="admin",
        is_active=True,
    )
    mock_repo = AsyncMock()
    mock_repo.get_by_email.return_value = mock_user

    app.dependency_overrides[get_user_repo] = lambda: mock_repo

    response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@routica.com", "password": "WrongPassword!"},
    )
    app.dependency_overrides.clear()

    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["error"]["message"]


@pytest.mark.asyncio
async def test_protected_me_endpoint_requires_auth(async_client: AsyncClient):
    response = await async_client.get("/api/v1/auth/me")
    assert response.status_code == 401

