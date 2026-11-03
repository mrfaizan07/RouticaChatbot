"""API tests for administrator file upload and document management."""

from unittest.mock import AsyncMock, patch
import pytest
from httpx import AsyncClient

from app.dependencies import get_current_admin, get_document_repo, get_knowledge_repo
from app.models.document import Document
from app.models.user import User


@pytest.mark.asyncio
async def test_upload_requires_admin_auth(async_client: AsyncClient):
    response = await async_client.post(
        "/api/v1/uploads",
        files={"file": ("specs.txt", b"Test content", "text/plain")},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_upload_unsupported_file_extension(app, async_client: AsyncClient, mock_admin_user: User):
    app.dependency_overrides[get_current_admin] = lambda: mock_admin_user

    response = await async_client.post(
        "/api/v1/uploads",
        files={"file": ("malicious.exe", b"binary executable", "application/x-msdownload")},
    )
    app.dependency_overrides.clear()

    assert response.status_code == 422
    assert "Unsupported file extension" in response.json()["error"]["message"]


@pytest.mark.asyncio
async def test_upload_valid_json(app, async_client: AsyncClient, mock_admin_user: User):
    app.dependency_overrides[get_current_admin] = lambda: mock_admin_user

    mock_doc = Document(
        _id="doc_123",
        filename="explorer_specs.json",
        original_filename="explorer_specs.json",
        file_type="json",
        file_size=100,
        storage_key="docs/test.json",
        content_hash="dummy_hash_123",
        processing_status="processing",
        uploaded_by="admin@routica.com",
    )

    mock_doc_repo = AsyncMock()
    mock_doc_repo.get_by_content_hash.return_value = None
    mock_doc_repo.create.return_value = mock_doc
    mock_doc_repo.update_status.return_value = None

    mock_knowledge_repo = AsyncMock()
    mock_knowledge_repo.delete_by_source_id.return_value = 0
    mock_knowledge_repo.insert_chunks_batch.return_value = ["chk_1"]

    app.dependency_overrides[get_document_repo] = lambda: mock_doc_repo
    app.dependency_overrides[get_knowledge_repo] = lambda: mock_knowledge_repo

    json_content = b'{"product": "Explorer II", "spec": "5G Sub-6GHz", "price": 499}'
    response = await async_client.post(
        "/api/v1/uploads",
        files={"file": ("explorer_specs.json", json_content, "application/json")},
    )
    app.dependency_overrides.clear()

    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "explorer_specs.json"
    assert data["status"] == "processed"

