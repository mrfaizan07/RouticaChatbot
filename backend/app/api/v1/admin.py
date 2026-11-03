"""Admin dashboard and provider monitoring endpoints."""

from fastapi import APIRouter, Depends, Query

from app.config import get_settings
from app.database.mongodb import MongoDBManager
from app.database.repositories.conversations import ConversationRepository
from app.database.repositories.documents import DocumentRepository
from app.database.repositories.knowledge import KnowledgeRepository
from app.database.repositories.products import ProductRepository
from app.database.repositories.scraping_jobs import ScrapingJobRepository
from app.database.repositories.users import UserRepository
from app.database.repositories.website_pages import WebsitePageRepository
from app.dependencies import (
    get_conversation_repo,
    get_current_admin,
    get_document_repo,
    get_knowledge_repo,
    get_product_repo,
    get_scraping_job_repo,
    get_user_repo,
    get_website_page_repo,
)
from app.models.document import Document
from app.models.scraping_job import ScrapingJob
from app.models.user import User
from app.schemas.admin import DashboardStats, ProviderStatusResponse, ScrapingJobResponse
from app.schemas.knowledge import KnowledgeChunkResponse, KnowledgeListResponse

router = APIRouter(prefix="/admin", tags=["Admin"])
settings = get_settings()


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_metrics(
    current_admin: User = Depends(get_current_admin),
    user_repo: UserRepository = Depends(get_user_repo),
    product_repo: ProductRepository = Depends(get_product_repo),
    page_repo: WebsitePageRepository = Depends(get_website_page_repo),
    knowledge_repo: KnowledgeRepository = Depends(get_knowledge_repo),
    doc_repo: DocumentRepository = Depends(get_document_repo),
) -> DashboardStats:
    """Returns overview metrics across users, products, pages, documents, and vector index."""
    total_users = await user_repo.count_admins()
    products = await product_repo.list_products(limit=1000)
    total_pages = await page_repo.count()
    total_chunks = await knowledge_repo.count_chunks()
    total_docs = await doc_repo.count()

    vector_info = await MongoDBManager.check_vector_index()
    vector_ready = vector_info.get("status") in ("ready", "READY")

    return DashboardStats(
        total_users=total_users,
        total_products=len(products),
        total_pages_scraped=total_pages,
        total_knowledge_chunks=total_chunks,
        total_documents_uploaded=total_docs,
        total_conversations=0,
        total_messages=0,
        vector_search_ready=vector_ready,
        storage_backend=settings.STORAGE_BACKEND,
    )


@router.get("/providers/status", response_model=ProviderStatusResponse)
async def get_providers_status(
    current_admin: User = Depends(get_current_admin),
) -> ProviderStatusResponse:
    """Returns status of configured AI providers and embedding model."""
    return ProviderStatusResponse(
        primary_provider=settings.CHAT_PRIMARY_PROVIDER,
        primary_model=settings.CHAT_PRIMARY_MODEL,
        fallback_models=settings.fallback_models_list,
        configured_keys={
            "gemini": bool(settings.GEMINI_API_KEY),
            "groq": bool(settings.GROQ_API_KEY),
            "openrouter": bool(settings.OPENROUTER_API_KEY),
        },
        embedding_provider=settings.EMBEDDING_PROVIDER,
        embedding_model=settings.EMBEDDING_MODEL,
        embedding_dimensions=settings.EMBEDDING_DIMENSIONS,
    )


@router.get("/documents", response_model=list[Document])
async def list_admin_documents(
    limit: int = Query(default=50, ge=1, le=100),
    skip: int = Query(default=0, ge=0),
    current_admin: User = Depends(get_current_admin),
    doc_repo: DocumentRepository = Depends(get_document_repo),
) -> list[Document]:
    """Lists uploaded document metadata for admin review."""
    return await doc_repo.list_documents(limit=limit, skip=skip)


@router.get("/scraping/jobs", response_model=list[ScrapingJobResponse])
async def list_scraping_jobs(
    limit: int = Query(default=20, ge=1, le=50),
    current_admin: User = Depends(get_current_admin),
    job_repo: ScrapingJobRepository = Depends(get_scraping_job_repo),
) -> list[ScrapingJobResponse]:
    """Lists historical and active scraping jobs."""
    jobs = await job_repo.list_jobs(limit=limit)
    return [
        ScrapingJobResponse(
            id=str(j.id),
            job_type=j.job_type,
            status=j.status,
            started_at=j.started_at,
            completed_at=j.completed_at,
            pages_discovered=j.pages_discovered,
            pages_processed=j.pages_processed,
            pages_failed=j.pages_failed,
            error_summary=j.error_summary,
        )
        for j in jobs
    ]

