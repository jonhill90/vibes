"""Settings configuration for RAG Service.

Type-safe environment variable loading with BaseSettings for DATABASE_URL,
QDRANT_URL, OPENAI_API_KEY, and all RAG service configuration.

Pattern: Pydantic Settings with SettingsConfigDict
Reference: https://docs.pydantic.dev/latest/concepts/pydantic_settings/
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator, SecretStr
from typing import Optional


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

    # Search Configuration
    USE_HYBRID_SEARCH: bool = Field(
        default=False,
        description="Enable hybrid search (vector + full-text)"
    )

    SIMILARITY_THRESHOLD: float = Field(
        default=0.05,
        description="Minimum similarity score for search results",
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
