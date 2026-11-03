"""System-wide constants and configurations."""

# Application Info
API_VERSION = "v1"
API_V1_STR = f"/api/{API_VERSION}"

# Supported Providers
PROVIDER_GEMINI = "gemini"
PROVIDER_GROQ = "groq"
PROVIDER_OPENROUTER = "openrouter"
SUPPORTED_PROVIDERS = [PROVIDER_GEMINI, PROVIDER_GROQ, PROVIDER_OPENROUTER]

# Embedding Models
DEFAULT_EMBEDDING_PROVIDER = "gemini"
DEFAULT_EMBEDDING_MODEL = "text-embedding-004"
DEFAULT_EMBEDDING_DIMENSIONS = 768

# Chunking Defaults
DEFAULT_CHUNK_SIZE = 800
DEFAULT_CHUNK_OVERLAP = 150
MIN_CHUNK_SIZE = 100
MAX_CHUNK_SIZE = 2000

# File Upload Constraints (Excel and JSON only)
ALLOWED_MIME_TYPES = {
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
    "application/vnd.ms-excel": ".xls",
    "application/excel": ".xls",
    "application/x-excel": ".xls",
    "application/x-msexcel": ".xls",
    "application/json": ".json",
    "text/json": ".json",
    "application/octet-stream": ".xlsx",
}

ALLOWED_EXTENSIONS = {".xlsx", ".xls", ".json"}

# Scraping Constraints
ROUTICA_ALLOWED_DOMAINS = ["routica.com", "www.routica.com"]
DEFAULT_CRAWL_MAX_PAGES = 100
DEFAULT_CRAWL_TIMEOUT_SECONDS = 30

# Role Constants
ROLE_ADMIN = "admin"

# Source Types
SOURCE_TYPE_WEBSITE = "website"
SOURCE_TYPE_DOCUMENT = "document"
SOURCE_TYPE_PRODUCT = "product"
