"""Centralized application configuration using Pydantic Settings v2."""

from functools import lru_cache
from typing import Literal
from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.exceptions import ConfigurationError


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Application Info
    APP_NAME: str = "Routica AI Assistant"
    APP_ENV: str = "development"
    DEBUG: bool = False

    @field_validator("APP_ENV", mode="before")
    @classmethod
    def normalize_app_env(cls, v: str) -> str:
        if isinstance(v, str):
            clean_v = v.strip().lower()
            if clean_v in ("development", "production", "testing"):
                return clean_v
        return "development"
    API_V1_PREFIX: str = "/api/v1"
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # Security & JWT
    SECRET_KEY: str = Field(
        default="dev-secret-key-must-be-changed-in-production-min-32-chars",
        description="Master secret key for application cryptographic tasks",
    )
    JWT_SECRET_KEY: str = Field(
        default="dev-jwt-secret-key-must-be-changed-in-production-min-32-chars",
        description="Secret key used for signing JWT tokens",
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ADMIN_EMAIL: str = Field(
        default="admin@routica.com",
        description="Administrator login email configured in .env",
    )
    ADMIN_PASSWORD: str = Field(
        default="admin123",
        description="Administrator login password configured in .env",
    )

    # MongoDB Atlas
    MONGODB_URI: str = Field(
        default="mongodb://localhost:27017",
        description="MongoDB connection string URI",
    )
    MONGODB_DATABASE: str = "routica_chatbot"
    MONGODB_MAX_POOL_SIZE: int = 50
    MONGODB_MIN_POOL_SIZE: int = 5
    MONGODB_CONNECT_TIMEOUT_MS: int = 5000

    # Vector Search
    VECTOR_SEARCH_INDEX_NAME: str = "vector_index"
    EMBEDDING_PROVIDER: str = "gemini"
    EMBEDDING_MODEL: str = "text-embedding-004"
    EMBEDDING_DIMENSIONS: int = 768

    # AI Providers & Keys
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    GROQ_API_KEY1: str = ""
    OPENROUTER_API_KEY: str = ""
    CHAT_PRIMARY_PROVIDER: str = "groq"
    CHAT_PRIMARY_MODEL: str = "groq/llama-3.3-70b-versatile"
    CHAT_FALLBACK_MODELS: str = "groq/llama-3.1-8b-instant,gemini/gemini-1.5-flash"

    # CORS & Web
    FRONTEND_URL: str = "http://localhost:5173"
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # Storage & Uploads
    STORAGE_BACKEND: Literal["local", "s3"] = "local"
    LOCAL_STORAGE_PATH: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 15
    OBJECT_STORAGE_ENDPOINT: str = ""
    OBJECT_STORAGE_BUCKET: str = ""
    OBJECT_STORAGE_ACCESS_KEY: str = ""
    OBJECT_STORAGE_SECRET_KEY: str = ""

    # Chat & Retrieval
    MAX_CHAT_MESSAGE_LENGTH: int = 5000
    RETRIEVAL_TOP_K: int = 5
    RETRIEVAL_SCORE_THRESHOLD: float = 0.65
    MAX_CONVERSATION_HISTORY: int = 6

    # Web Scraping
    SCRAPE_ALLOWED_DOMAINS: str = "routica.com,www.routica.com"
    SCRAPE_INTERVAL_HOURS: int = 24
    SCRAPE_USER_AGENT: str = "RouticaBot/1.0 (+https://routica.com)"
    SCRAPE_RATE_LIMIT_DELAY_SECONDS: float = 1.0

    # Redis & Rate Limiting
    REDIS_URL: str = ""
    RATE_LIMIT_PER_MINUTE: int = 60

    # Logging
    LOG_LEVEL: str = "INFO"

    @property
    def allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    @property
    def scrape_allowed_domains_list(self) -> list[str]:
        return [domain.strip().lower() for domain in self.SCRAPE_ALLOWED_DOMAINS.split(",") if domain.strip()]

    @property
    def fallback_models_list(self) -> list[str]:
        return [model.strip() for model in self.CHAT_FALLBACK_MODELS.split(",") if model.strip()]

    @field_validator("MAX_UPLOAD_SIZE_MB")
    @classmethod
    def validate_max_upload_size(cls, v: int) -> int:
        if v <= 0 or v > 50:
            raise ValueError("MAX_UPLOAD_SIZE_MB must be between 1 and 50 MB")
        return v

    @model_validator(mode="after")
    def validate_production_requirements(self) -> "Settings":
        """Strict validation in production environment."""
        if self.APP_ENV == "production":
            if self.DEBUG:
                raise ConfigurationError("DEBUG mode must be False in production.")
            if "dev-secret" in self.SECRET_KEY or len(self.SECRET_KEY) < 32:
                raise ConfigurationError("SECRET_KEY must be a secure random key of at least 32 characters in production.")
            if "dev-jwt" in self.JWT_SECRET_KEY or len(self.JWT_SECRET_KEY) < 32:
                raise ConfigurationError("JWT_SECRET_KEY must be a secure random key of at least 32 characters in production.")
            if not self.MONGODB_URI or "localhost" in self.MONGODB_URI:
                raise ConfigurationError("A valid production MONGODB_URI (e.g., MongoDB Atlas) is required in production.")
            if self.STORAGE_BACKEND == "s3" and (not self.OBJECT_STORAGE_BUCKET or not self.OBJECT_STORAGE_ACCESS_KEY):
                raise ConfigurationError("S3 storage configuration requires OBJECT_STORAGE_BUCKET and credentials.")
        return self


@lru_cache()
def get_settings() -> Settings:
    """Returns cached application settings."""
    return Settings()
