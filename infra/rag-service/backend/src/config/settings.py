"""Settings configuration for RAG Service.

Type-safe environment variable loading with BaseSettings for DATABASE_URL,
QDRANT_URL, OPENAI_API_KEY, and all RAG service configuration.

Pattern: Pydantic Settings with SettingsConfigDict
Reference: https://docs.pydantic.dev/latest/concepts/pydantic_settings/
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator, SecretStr


class Settings(BaseSettings):
    """Application settings with environment variable support.

    All settings can be loaded from:
    1. Environment variables (highest priority)
    2. .env file (if present)
    3. Default values (lowest priority)

    Security:
    - OPENAI_API_KEY is SecretStr (excluded from logs)
    - frozen=True prevents runtime modification
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        frozen=True  # Prevent runtime modification for security
    )

    # Database Configuration
    DATABASE_URL: str = Field(
        ...,
        description="PostgreSQL connection URL (must start with postgresql://)"
    )

    DATABASE_POOL_MIN_SIZE: int = Field(
        default=2,
        description="Minimum database connection pool size",
        ge=1,
        le=10
    )

    DATABASE_POOL_MAX_SIZE: int = Field(
        default=10,
        description="Maximum database connection pool size",
        ge=2,
        le=50
    )

    # Qdrant Vector Database Configuration
    QDRANT_URL: str = Field(
        ...,
        description="Qdrant server URL (must start with http:// or https://)"
    )

    QDRANT_COLLECTION_NAME: str = Field(
        default="rag_documents",
        description="Qdrant collection name for vector storage"
    )

    # OpenAI Configuration
    OPENAI_API_KEY: SecretStr = Field(
        ...,
        description="OpenAI API key for embeddings and LLM (marked as secret)"
    )

    OPENAI_EMBEDDING_MODEL: str = Field(
        default="text-embedding-3-small",
        description="OpenAI embedding model (1536 dimensions)"
    )

    OPENAI_EMBEDDING_DIMENSION: int = Field(
        default=1536,
        description="Embedding vector dimension for text-embedding-3-small"
    )

    # API Configuration
    API_PORT: int = Field(
        default=8001,
        description="FastAPI server port",
        ge=1024,
        le=65535
    )

    MCP_PORT: int = Field(
        default=8052,
        description="MCP server port for agent tools",
        ge=1024,
        le=65535
    )

    CORS_ORIGINS: str = Field(
        default="",
        description="Comma-separated list of allowed CORS origins (empty = development defaults)"
    )

    # Search Configuration
    USE_HYBRID_SEARCH: bool = Field(
        default=False,
        description="Enable hybrid search (vector + full-text)"
    )

    HYBRID_VECTOR_WEIGHT: float = Field(
        default=0.7,
        description="Weight for vector similarity scores in hybrid search",
        ge=0.0,
        le=1.0
    )

    HYBRID_TEXT_WEIGHT: float = Field(
        default=0.3,
        description="Weight for text search scores in hybrid search",
        ge=0.0,
        le=1.0
    )

    HYBRID_CANDIDATE_MULTIPLIER: int = Field(
        default=5,
        description="Multiplier for candidate retrieval in hybrid search (fetch limit * multiplier)",
        ge=2,
        le=10
    )

    SIMILARITY_THRESHOLD: float = Field(
        default=0.05,
        description="Minimum similarity score for search results",
        ge=0.0,
        le=1.0
    )

    # Multi-Collection Configuration
    COLLECTION_NAME_PREFIX: str = Field(
        default="AI_",
        description="Prefix for Qdrant collection names (e.g., AI_DOCUMENTS, AI_CODE)"
    )

    COLLECTION_EMBEDDING_MODELS: dict[str, str] = Field(
        default={
            "documents": "text-embedding-3-small",  # Fast, cheap for general text
            "code": "text-embedding-3-large",       # Better for technical content
            "media": "clip-vit-base-patch32",       # Multimodal (future)
        },
        description="Embedding model per collection type"
    )

    COLLECTION_DIMENSIONS: dict[str, int] = Field(
        default={
            "documents": 1536,   # text-embedding-3-small
            "code": 3072,        # text-embedding-3-large
            "media": 512,        # clip-vit (future)
        },
        description="Vector dimensions per collection type"
    )

    # Content Classification Configuration
    CODE_DETECTION_THRESHOLD: float = Field(
        default=0.4,
        description="Threshold for code content detection (40% code indicators = code collection)",
        ge=0.0,
        le=1.0
    )

    # Embedding Batch Configuration
    EMBEDDING_BATCH_SIZE: int = Field(
        default=100,
        description="Number of texts to embed per OpenAI API call",
        ge=1,
        le=2048
    )

    # Document Chunking Configuration
    CHUNK_SIZE: int = Field(
        default=500,
        description="Target token count per chunk",
        ge=100,
        le=2000
    )

    CHUNK_OVERLAP: int = Field(
        default=50,
        description="Token overlap between chunks",
        ge=0,
        le=500
    )

    # Validators
    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Validate DATABASE_URL starts with postgresql:// scheme.

        Args:
            v: Database URL string

        Returns:
            Validated URL string

        Raises:
            ValueError: If URL doesn't use postgresql:// scheme
        """
        if not v.startswith("postgresql://"):
            raise ValueError(
                "DATABASE_URL must start with postgresql:// "
                f"(got: {v[:20]}...)"
            )
        return v

    @field_validator("QDRANT_URL")
    @classmethod
    def validate_qdrant_url(cls, v: str) -> str:
        """Validate QDRANT_URL uses http:// or https:// scheme.

        Args:
            v: Qdrant URL string

        Returns:
            Validated URL string

        Raises:
            ValueError: If URL doesn't use http:// or https:// scheme
        """
        if not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError(
                "QDRANT_URL must start with http:// or https:// "
                f"(got: {v[:20]}...)"
            )
        return v

    @field_validator("DATABASE_POOL_MAX_SIZE")
    @classmethod
    def validate_pool_sizes(cls, v: int, info) -> int:
        """Validate max pool size is greater than min pool size.

        Args:
            v: Maximum pool size
            info: Validation context with other field values

        Returns:
            Validated max pool size

        Raises:
            ValueError: If max <= min pool size
        """
        # Access via info.data instead of values
        min_size = info.data.get("DATABASE_POOL_MIN_SIZE", 2)
        if v <= min_size:
            raise ValueError(
                f"DATABASE_POOL_MAX_SIZE ({v}) must be greater than "
                f"DATABASE_POOL_MIN_SIZE ({min_size})"
            )
        return v

    @field_validator("CHUNK_OVERLAP")
    @classmethod
    def validate_chunk_overlap(cls, v: int, info) -> int:
        """Validate chunk overlap is less than chunk size.

        Args:
            v: Chunk overlap token count
            info: Validation context with other field values

        Returns:
            Validated chunk overlap

        Raises:
            ValueError: If overlap >= chunk size
        """
        chunk_size = info.data.get("CHUNK_SIZE", 500)
        if v >= chunk_size:
            raise ValueError(
                f"CHUNK_OVERLAP ({v}) must be less than CHUNK_SIZE ({chunk_size})"
            )
        return v

    @field_validator("HYBRID_TEXT_WEIGHT")
    @classmethod
    def validate_hybrid_weights(cls, v: float, info) -> float:
        """Validate hybrid search weights sum to 1.0.

        Args:
            v: Text weight value
            info: Validation context with other field values

        Returns:
            Validated text weight

        Raises:
            ValueError: If weights don't sum to 1.0
        """
        vector_weight = info.data.get("HYBRID_VECTOR_WEIGHT", 0.7)
        total = vector_weight + v
        if abs(total - 1.0) > 0.001:
            raise ValueError(
                f"HYBRID_VECTOR_WEIGHT ({vector_weight}) + HYBRID_TEXT_WEIGHT ({v}) "
                f"must sum to 1.0 (got {total})"
            )
        return v

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS_ORIGINS into a list of origins.

        Returns:
            List of allowed origins (development defaults if CORS_ORIGINS is empty)
        """
        if not self.CORS_ORIGINS:
            # Development defaults
            return [
                "http://localhost:3000",
                "http://localhost:5173",
                "http://localhost:5174",
                "http://host.docker.internal:3000",
                "http://host.docker.internal:5173",
            ]

        # Parse comma-separated origins
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


def load_settings() -> Settings:
    """Load settings with proper error handling.

    Returns:
        Configured Settings instance

    Raises:
        ValueError: If required environment variables are missing or invalid
    """
    try:
        return Settings()
    except Exception as e:
        error_msg = f"Failed to load settings: {e}"

        # Provide helpful error messages for common issues
        error_str = str(e).lower()
        if "database_url" in error_str:
            error_msg += "\nMake sure to set DATABASE_URL in your .env file"
            error_msg += "\nExample: DATABASE_URL=postgresql://user:pass@localhost:5432/rag_db"
        if "qdrant_url" in error_str:
            error_msg += "\nMake sure to set QDRANT_URL in your .env file"
            error_msg += "\nExample: QDRANT_URL=http://localhost:6333"
        if "openai_api_key" in error_str:
            error_msg += "\nMake sure to set OPENAI_API_KEY in your .env file"
            error_msg += "\nExample: OPENAI_API_KEY=sk-..."

        raise ValueError(error_msg) from e


# Global settings instance (loaded once at module import)
settings = load_settings()
