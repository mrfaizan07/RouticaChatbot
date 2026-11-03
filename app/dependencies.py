"""FastAPI dependency injection providers."""

from fastapi import Depends, Header
from fastapi.security import OAuth2PasswordBearer
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.security import decode_access_token
from app.database.mongodb import MongoDBManager
from app.database.repositories.conversations import ConversationRepository
from app.database.repositories.documents import DocumentRepository
from app.database.repositories.knowledge import KnowledgeRepository
from app.database.repositories.products import ProductRepository
from app.database.repositories.scraping_jobs import ScrapingJobRepository
from app.database.repositories.users import UserRepository
from app.database.repositories.website_pages import WebsitePageRepository
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


# Database dependency
async def get_db() -> AsyncIOMotorDatabase:
    return MongoDBManager.get_database()


# Repository dependencies
def get_user_repo(db: AsyncIOMotorDatabase = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_product_repo(db: AsyncIOMotorDatabase = Depends(get_db)) -> ProductRepository:
    return ProductRepository(db)


def get_website_page_repo(db: AsyncIOMotorDatabase = Depends(get_db)) -> WebsitePageRepository:
    return WebsitePageRepository(db)


def get_knowledge_repo(db: AsyncIOMotorDatabase = Depends(get_db)) -> KnowledgeRepository:
    return KnowledgeRepository(db)


def get_conversation_repo(db: AsyncIOMotorDatabase = Depends(get_db)) -> ConversationRepository:
    return ConversationRepository(db)


def get_document_repo(db: AsyncIOMotorDatabase = Depends(get_db)) -> DocumentRepository:
    return DocumentRepository(db)


def get_scraping_job_repo(db: AsyncIOMotorDatabase = Depends(get_db)) -> ScrapingJobRepository:
    return ScrapingJobRepository(db)


# Authentication dependencies
async def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    user_repo: UserRepository = Depends(get_user_repo),
) -> User:
    """Extracts and verifies JWT bearer token, returning the authenticated user."""
    if not token:
        raise UnauthorizedException("Authentication token required")

    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Invalid token payload: subject missing")

    user = await user_repo.get_by_id(user_id)
    if not user or not user.is_active:
        raise UnauthorizedException("User not found or account is deactivated")

    return user


async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """Restricts access strictly to administrator users."""
    if current_user.role != "admin":
        raise ForbiddenException("Administrator privileges required")
    return current_user


# Session ID header extractor for public chat
def get_session_id(x_session_id: str | None = Header(default=None)) -> str:
    """Extracts session ID from headers or generates an ephemeral one."""
    import uuid
    return x_session_id.strip() if x_session_id and x_session_id.strip() else str(uuid.uuid4())
