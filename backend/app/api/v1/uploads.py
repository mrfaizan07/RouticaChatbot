"""Administrator file upload and document ingestion endpoints."""

import hashlib
import uuid
from fastapi import APIRouter, Depends, File, UploadFile, status

from app.core.exceptions import NotFoundException, ValidationException
from app.database.repositories.documents import DocumentRepository
from app.database.repositories.knowledge import KnowledgeRepository
from app.dependencies import (
    get_current_admin,
    get_document_repo,
    get_knowledge_repo,
)
from app.file_processors.excel_processor import ExcelProcessor
from app.file_processors.json_processor import JSONProcessor
from app.models.document import Document
from app.models.user import User
from app.schemas.upload import DocumentDetailResponse, DocumentUploadResponse
from app.services.knowledge_service import KnowledgeService
from app.storage.object_storage import get_storage
from app.utils.text_cleaner import normalize_whitespace
from app.utils.validators import validate_file_upload

router = APIRouter(prefix="/uploads", tags=["Uploads"])


@router.post("", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def upload_document(
    file: UploadFile = File(...),
    current_admin: User = Depends(get_current_admin),
    doc_repo: DocumentRepository = Depends(get_document_repo),
    knowledge_repo: KnowledgeRepository = Depends(get_knowledge_repo),
) -> DocumentUploadResponse:
    """Accepts and processes administrator-uploaded documents (Excel and JSON only)."""
    file_bytes = await file.read()
    clean_filename = validate_file_upload(
        filename=file.filename or "upload.bin",
        content_type=file.content_type or "",
        file_size_bytes=len(file_bytes),
    )

    content_hash = hashlib.sha256(file_bytes).hexdigest()

    # Check for existing duplicate document
    existing_doc = await doc_repo.get_by_content_hash(content_hash)
    if existing_doc and existing_doc.processing_status == "processed":
        return DocumentUploadResponse(
            document_id=str(existing_doc.id),
            filename=existing_doc.filename,
            file_type=existing_doc.file_type,
            file_size=existing_doc.file_size,
            status="already_processed",
            total_chunks=existing_doc.total_chunks,
            message="Document with identical content already exists and is indexed.",
        )

    # Save to storage abstraction
    ext = "." + clean_filename.split(".")[-1].lower()
    storage_key = f"docs/{uuid.uuid4()}{ext}"
    storage = get_storage()
    await storage.save_file(file_bytes, storage_key=storage_key, content_type=file.content_type or "")

    # Create document record
    doc_record = Document(
        filename=clean_filename,
        original_filename=file.filename or clean_filename,
        file_type=ext.lstrip("."),
        file_size=len(file_bytes),
        storage_key=storage_key,
        content_hash=content_hash,
        processing_status="processing",
        uploaded_by=str(current_admin.email),
    )
    saved_doc = await doc_repo.create(doc_record)
    doc_id = str(saved_doc.id)

    # Extract text based on extension (Excel and JSON only)
    extracted_text = ""
    try:
        if ext in (".xlsx", ".xls"):
            extracted_text = ExcelProcessor.extract_text(file_bytes)
        elif ext == ".json":
            extracted_text = JSONProcessor.extract_text(file_bytes)
        else:
            raise ValidationException(f"Unsupported file format '{ext}'. Only Excel (.xlsx, .xls) and JSON (.json) files are permitted.")

        if not extracted_text or len(extracted_text.strip()) < 5:
            raise ValidationException(f"No extractable data rows or keys found in {clean_filename}")

        # Chunk and embed
        knowledge_svc = KnowledgeService(knowledge_repo=knowledge_repo)
        total_chunks = await knowledge_svc.ingest_content(
            source_id=doc_id,
            source_type="document",
            source_title=clean_filename,
            source_url=f"/uploads/{clean_filename}",
            raw_text=extracted_text,
            metadata={"filename": clean_filename, "file_type": ext.lstrip(".")},
        )

        await doc_repo.update_status(doc_id=doc_id, status="processed", total_chunks=total_chunks)

        return DocumentUploadResponse(
            document_id=doc_id,
            filename=clean_filename,
            file_type=ext.lstrip("."),
            file_size=len(file_bytes),
            status="processed",
            total_chunks=total_chunks,
            message=f"Document successfully parsed ({total_chunks} chunks indexed).",
        )
    except Exception as exc:
        await doc_repo.update_status(doc_id=doc_id, status="failed", error=str(exc))
        raise ValidationException(f"Failed to process uploaded document: {exc}")


@router.get("/{document_id}", response_model=DocumentDetailResponse)
async def get_document_details(
    document_id: str,
    current_admin: User = Depends(get_current_admin),
    doc_repo: DocumentRepository = Depends(get_document_repo),
) -> DocumentDetailResponse:
    """Retrieves document details and ingestion status."""
    doc = await doc_repo.get_by_id(document_id)
    if not doc:
        raise NotFoundException("Document not found")
    return DocumentDetailResponse(
        id=str(doc.id),
        filename=doc.filename,
        original_filename=doc.original_filename,
        file_type=doc.file_type,
        file_size=doc.file_size,
        storage_key=doc.storage_key,
        processing_status=doc.processing_status,
        processing_error=doc.processing_error,
        total_chunks=doc.total_chunks,
        uploaded_by=doc.uploaded_by,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
    )


@router.delete("/{document_id}", status_code=status.HTTP_200_OK)
async def delete_document(
    document_id: str,
    current_admin: User = Depends(get_current_admin),
    doc_repo: DocumentRepository = Depends(get_document_repo),
    knowledge_repo: KnowledgeRepository = Depends(get_knowledge_repo),
) -> dict[str, str]:
    """Deletes uploaded document and cleans up its vector knowledge chunks."""
    doc = await doc_repo.get_by_id(document_id)
    if not doc:
        raise NotFoundException("Document not found")

    # Delete storage file
    storage = get_storage()
    await storage.delete_file(doc.storage_key)

    # Delete knowledge chunks
    deleted_chunks = await knowledge_repo.delete_by_source_id(document_id)

    # Delete document record
    await doc_repo.delete(document_id)

    return {"message": f"Document deleted and {deleted_chunks} associated vector chunks removed."}

