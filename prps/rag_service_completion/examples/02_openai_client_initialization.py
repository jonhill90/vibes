# Source: Archon RAG search (pydantic.ai examples) + infra/rag-service/backend/src/services/embeddings/embedding_service.py
# Lines: 60-80 (EmbeddingService __init__)
# Pattern: AsyncOpenAI client initialization and injection
# Extracted: 2025-10-14
# Relevance: 10/10 - Fixes OpenAI client instantiation bug (INITIAL.md Task 2)

"""
WHAT THIS DEMONSTRATES:
- AsyncOpenAI client initialization with API key
- Dependency injection pattern for services
- Settings-based configuration
- Proper async client usage
"""

from openai import AsyncOpenAI
import asyncpg
from pydantic_settings import BaseSettings

# ==============================================================================
# PATTERN 1: Settings Configuration (pydantic-settings)
# ==============================================================================

class Settings(BaseSettings):
    """Application settings with validation."""

    OPENAI_API_KEY: str  # Required, will fail if not set
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_EMBEDDING_DIMENSION: int = 1536
    EMBEDDING_BATCH_SIZE: int = 100

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Load settings globally
settings = Settings()


# ==============================================================================
# PATTERN 2: AsyncOpenAI Client Initialization
# ==============================================================================

# CORRECT: Initialize client with API key
openai_client = AsyncOpenAI(
    api_key=settings.OPENAI_API_KEY
)

# ALTERNATIVE: Initialize with custom HTTP client (for advanced config)
import httpx

custom_http_client = httpx.AsyncClient(
    timeout=httpx.Timeout(60.0),  # 60s timeout
    limits=httpx.Limits(max_connections=20)
)

openai_client_custom = AsyncOpenAI(
    api_key=settings.OPENAI_API_KEY,
    http_client=custom_http_client
)


# ==============================================================================
# PATTERN 3: Dependency Injection into EmbeddingService
# ==============================================================================

class EmbeddingService:
    """OpenAI embedding service with cache and quota handling.

    CRITICAL: This service REQUIRES an initialized AsyncOpenAI client.
    DO NOT instantiate AsyncOpenAI inside __init__ - inject it!
    """

    def __init__(
        self,
        db_pool: asyncpg.Pool,
        openai_client: AsyncOpenAI,  # INJECT the client, don't create it here
    ):
        """Initialize EmbeddingService.

        Args:
            db_pool: asyncpg connection pool for cache operations
            openai_client: OpenAI async client for embedding generation
        """
        # Store injected dependencies
        self.db_pool = db_pool
        self.openai_client = openai_client  # THIS WAS MISSING - caused line 33 error

        # Load configuration from settings
        self.model_name = settings.OPENAI_EMBEDDING_MODEL
        self.expected_dimension = settings.OPENAI_EMBEDDING_DIMENSION
        self.batch_size = settings.EMBEDDING_BATCH_SIZE

        logger.info(
            f"EmbeddingService initialized: model={self.model_name}, "
            f"dimension={self.expected_dimension}, batch_size={self.batch_size}"
        )

    async def embed_text(self, text: str) -> list[float] | None:
        """Generate embedding using the injected OpenAI client."""
        try:
            # Use self.openai_client (injected dependency)
            response = await self.openai_client.embeddings.create(
                model=self.model_name,
                input=text,
            )

            return response.data[0].embedding

        except Exception as e:
            logger.error(f"Embedding generation error: {e}")
            return None


# ==============================================================================
# PATTERN 4: Service Initialization in FastAPI Lifespan
# ==============================================================================

from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager with service initialization."""

    # Startup: Initialize all clients and services

    # 1. Initialize database pool
    db_pool = await asyncpg.create_pool(
        settings.DATABASE_URL,
        min_size=10,
        max_size=20,
    )

    # 2. Initialize OpenAI client (ONCE, globally)
    openai_client = AsyncOpenAI(
        api_key=settings.OPENAI_API_KEY
    )

    # 3. Initialize services with dependency injection
    embedding_service = EmbeddingService(
        db_pool=db_pool,
        openai_client=openai_client,  # Inject the client
    )

    # 4. Store in app.state for route handlers
    app.state.db_pool = db_pool
    app.state.openai_client = openai_client
    app.state.embedding_service = embedding_service

    yield  # Application runs

    # Shutdown: Cleanup resources
    await db_pool.close()
    # AsyncOpenAI client doesn't need explicit close


app = FastAPI(lifespan=lifespan)


# ==============================================================================
# PATTERN 5: Service Initialization in MCP Server
# ==============================================================================

# For MCP server (similar pattern, but different context)

async def initialize_services():
    """Initialize services for MCP server."""

    # 1. Create database pool
    db_pool = await asyncpg.create_pool(settings.DATABASE_URL)

    # 2. Initialize OpenAI client
    openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    # 3. Initialize embedding service with injection
    embedding_service = EmbeddingService(
        db_pool=db_pool,
        openai_client=openai_client,
    )

    # 4. Store in MCP context
    mcp.app.state.embedding_service = embedding_service

    return db_pool, openai_client


# Main entry point for MCP server
if __name__ == "__main__":
    import asyncio

    async def main():
        db_pool, openai_client = await initialize_services()

        try:
            await mcp.run(transport="streamable-http")
        finally:
            await db_pool.close()

    asyncio.run(main())


# ==============================================================================
# COMMON MISTAKES (AVOID THESE)
# ==============================================================================

# ❌ WRONG: Creating client inside __init__ without API key
class BadEmbeddingService:
    def __init__(self, db_pool):
        self.openai_client = AsyncOpenAI()  # No API key, will fail


# ❌ WRONG: Not storing the client (line 33 error in INITIAL.md)
class AnotherBadService:
    def __init__(self, db_pool, openai_client):
        self.db_pool = db_pool
        # Missing: self.openai_client = openai_client

    async def embed_text(self, text):
        # This will fail: self.openai_client is not defined
        response = await self.openai_client.embeddings.create(...)


# ❌ WRONG: Creating new client for every request
async def bad_embed_route(text: str):
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)  # Don't do this
    response = await client.embeddings.create(model="...", input=text)
    return response.data[0].embedding


# ✅ CORRECT: Initialize once, inject everywhere
# 1. Create AsyncOpenAI(api_key=...) once in lifespan/main
# 2. Inject into EmbeddingService via constructor
# 3. Store service in app.state or mcp.app.state
# 4. Use the same service instance for all requests
