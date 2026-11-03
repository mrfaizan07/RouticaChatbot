"""Document upload schemas."""

from datetime import datetime
from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    file_type: str
    file_size: int
    status: str
    total_chunks: int = 0
    message: str


class DocumentDetailResponse(BaseModel):
    id: str
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    storage_key: str
    processing_status: str
    processing_error: str | None = None
    total_chunks: int = 0
    uploaded_by: str
    created_at: datetime
    updated_at: datetime

