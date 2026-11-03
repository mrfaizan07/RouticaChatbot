"""Pytest global configuration, test environment setup, and shared fixtures."""

import os
import sys
from pathlib import Path
import pytest
from httpx import ASGITransport, AsyncClient

# 1. Ensure backend path is on sys.path
backend_path = Path(__file__).parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

# 2. Force testing environment variables before importing app modules
os.environ["APP_ENV"] = "testing"
os.environ["DEBUG"] = "false"
os.environ["LITELLM_LOCAL_MODEL_COST_MAP"] = "True"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["MONGODB_URI"] = "mongodb://localhost:27017"
os.environ["MONGODB_DATABASE"] = "routica_test"
os.environ["SECRET_KEY"] = "test-secret-key-32-characters-minimum-for-testing"
os.environ["JWT_SECRET_KEY"] = "test-jwt-secret-key-32-characters-minimum"

import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


from app.core.security import hash_password
from app.main import create_application
from app.models.user import User


@pytest.fixture
def app():
    """Provides the main FastAPI application instance."""
    return create_application()


@pytest.fixture
async def async_client(app):
    """Provides an HTTPX AsyncClient bound to the FastAPI ASGI application."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.fixture
def mock_admin_user():
    """Provides a sample active administrator user."""
    return User(
        _id="65f1234567890abcdef12345",
        email="admin@routica.com",
        password_hash=hash_password("AdminSecurePassword123!"),
        role="admin",
        is_active=True,
    )
