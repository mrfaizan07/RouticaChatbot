"""Knowledge inspection and reindexing endpoints."""

from fastapi import APIRouter, Depends, Query, status
from app.core.exceptions import NotFoundException
from app.database.repositories.knowledge import KnowledgeRepository
from app.database.repositories.website_pages import WebsitePageRepository
from app.dependencies import get_current_admin, get_knowledge_repo, get_website_page_repo
from app.models.knowledge import KnowledgeChunk
from app.models.user import User
from app.schemas.knowledge import KnowledgeChunkResponse, KnowledgeListResponse, ReindexResponse
from app.services.knowledge_service import KnowledgeService

router = APIRouter(prefix="/knowledge", tags=["Knowledge"])


@router.get("", response_model=KnowledgeListResponse)
async def list_knowledge_chunks(
    limit: int = Query(default=100, ge=1, le=1000),
    skip: int = Query(default=0, ge=0),
    current_admin: User = Depends(get_current_admin),
    knowledge_repo: KnowledgeRepository = Depends(get_knowledge_repo),
) -> KnowledgeListResponse:
    """Lists indexed knowledge chunks directly from MongoDB Atlas vector storage."""
    chunks = await knowledge_repo.list_chunks(limit=limit, skip=skip)
    total = await knowledge_repo.count_chunks()

    chunk_responses = [
        KnowledgeChunkResponse(
            id=str(c.id),
            source_id=c.source_id,
            source_type=c.source_type,
            source_title=c.source_title,
            source_url=c.source_url,
            chunk_index=c.chunk_index,
            content=c.content,
            embedding_model=c.embedding_model,
            embedding_dimensions=c.embedding_dimensions,
            metadata=c.metadata,
            is_active=c.is_active,
            created_at=c.created_at,
        )
        for c in chunks
    ]

    return KnowledgeListResponse(total=total, chunks=chunk_responses)


@router.post("/reindex", response_model=ReindexResponse)
async def reindex_knowledge(
    current_admin: User = Depends(get_current_admin),
    knowledge_repo: KnowledgeRepository = Depends(get_knowledge_repo),
    pages_repo: WebsitePageRepository = Depends(get_website_page_repo),
) -> ReindexResponse:
    """Reindexes all stored website pages into fresh vector chunks."""
    pages = await pages_repo.list_pages(limit=500)
    knowledge_svc = KnowledgeService(knowledge_repo=knowledge_repo)

    total_indexed = 0
    for page in pages:
        if page.content:
            count = await knowledge_svc.ingest_content(
                source_id=str(page.id),
                source_type="website",
                source_title=page.title,
                source_url=page.canonical_url,
                raw_text=page.content,
                metadata={"page_type": page.page_type, "url": page.url},
            )
            total_indexed += count

    return ReindexResponse(
        success=True,
        message=f"Reindexed {len(pages)} pages into {total_indexed} vector chunks.",
        chunks_indexed=total_indexed,
    )


@router.delete("/{knowledge_id}", status_code=status.HTTP_200_OK)
async def delete_knowledge_chunk(
    knowledge_id: str,
    current_admin: User = Depends(get_current_admin),
    knowledge_repo: KnowledgeRepository = Depends(get_knowledge_repo),
) -> dict[str, bool]:
    deleted = await knowledge_repo.delete_chunk(knowledge_id)
    if not deleted:
        raise NotFoundException(resource_type="KnowledgeChunk", identifier=knowledge_id)
    return {"success": True}
