"""MongoDB index definitions and creation routines."""

from pymongo import ASCENDING, DESCENDING
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.logging import logger


async def create_database_indexes(db: AsyncIOMotorDatabase) -> dict[str, list[str]]:
    """Creates standard B-Tree indexes across all 8 MongoDB collections."""
    created_indexes = {}

    try:
        # 1. users: unique email
        u_idx = await db["users"].create_index([("email", ASCENDING)], unique=True, name="idx_users_email_unique")
        created_indexes["users"] = [u_idx]

        # 2. products: unique slug, category index
        p_idx1 = await db["products"].create_index([("product_slug", ASCENDING)], unique=True, name="idx_products_slug_unique")
        p_idx2 = await db["products"].create_index([("category", ASCENDING)], name="idx_products_category")
        created_indexes["products"] = [p_idx1, p_idx2]

        # 3. website_pages: unique canonical_url, status
        w_idx1 = await db["website_pages"].create_index([("canonical_url", ASCENDING)], unique=True, name="idx_pages_canonical_unique")
        w_idx2 = await db["website_pages"].create_index([("status", ASCENDING)], name="idx_pages_status")
        created_indexes["website_pages"] = [w_idx1, w_idx2]

        # 4. knowledge_chunks: compound (source_id, is_active), content_hash
        k_idx1 = await db["knowledge_chunks"].create_index(
            [("source_id", ASCENDING), ("is_active", ASCENDING)],
            name="idx_knowledge_source_active",
        )
        k_idx2 = await db["knowledge_chunks"].create_index([("content_hash", ASCENDING)], name="idx_knowledge_content_hash")
        created_indexes["knowledge_chunks"] = [k_idx1, k_idx2]

        # 5. documents: content_hash, uploaded_by, processing_status
        d_idx1 = await db["documents"].create_index([("content_hash", ASCENDING)], name="idx_documents_hash")
        d_idx2 = await db["documents"].create_index([("processing_status", ASCENDING)], name="idx_documents_status")
        created_indexes["documents"] = [d_idx1, d_idx2]

        # 6. conversations: session_id, updated_at
        c_idx1 = await db["conversations"].create_index([("session_id", ASCENDING)], name="idx_conversations_session")
        c_idx2 = await db["conversations"].create_index([("updated_at", DESCENDING)], name="idx_conversations_updated")
        created_indexes["conversations"] = [c_idx1, c_idx2]

        # 7. messages: compound (conversation_id, created_at)
        m_idx = await db["messages"].create_index(
            [("conversation_id", ASCENDING), ("created_at", ASCENDING)],
            name="idx_messages_conv_created",
        )
        created_indexes["messages"] = [m_idx]

        # 8. scraping_jobs: status, started_at
        s_idx1 = await db["scraping_jobs"].create_index([("status", ASCENDING)], name="idx_scraping_status")
        s_idx2 = await db["scraping_jobs"].create_index([("started_at", DESCENDING)], name="idx_scraping_started")
        created_indexes["scraping_jobs"] = [s_idx1, s_idx2]

        logger.info("Successfully created MongoDB indexes for collections: %s", list(created_indexes.keys()))
        return created_indexes
    except Exception as exc:
        logger.error("Error creating database indexes: %s", str(exc))
        raise
