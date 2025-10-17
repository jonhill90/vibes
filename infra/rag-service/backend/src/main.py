"""FastAPI application for RAG Service.

This is the main entry point for the RAG Service backend API.
Provides RESTful endpoints for document ingestion, vector search, and RAG operations
with proper CORS configuration and database lifecycle management.

KEY FEATURES:
- Environment-specific CORS configuration (Gotcha #8)
- Database connection pool lifecycle management (Gotcha #2)
- Qdrant client initialization and cleanup
- Qdrant collection initialization with HNSW disabled for bulk upload (Gotcha #9)
- Health check endpoint
- OpenAPI documentation with metadata
- API router organization with /api prefix

CRITICAL GOTCHAS ADDRESSED:
- Gotcha #2: Returns POOL from dependencies, NOT connections
- Gotcha #8: CORS configured with specific origins (NEVER allow_origins=["*"])
- Gotcha #9: HNSW disabled (m=0) during bulk upload for 60-90x speedup
- Gotcha #12: Services use async with pool.acquire() for connection management
"""

import logging
from contextlib import asynccontextmanager

import asyncpg
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import VectorParams, Distance, HnswConfigDiff

from src.config.settings import settings
from src.api.routes import health, documents, search, sources, crawls

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown tasks.

    Startup:
    - Initialize database connection pool
    - Initialize Qdrant vector database client
    - Create Qdrant collection with HNSW disabled for bulk upload (Gotcha #9)

    Shutdown:
    - Close database connection pool gracefully
    - Close Qdrant client gracefully

    CRITICAL PATTERNS:
    - Store POOL in app.state, not connections (Gotcha #2)
    - Dependencies return pool, services acquire connections as needed
    - HNSW disabled (m=0) during bulk upload for 60-90x speedup (Gotcha #9)
    """
    # Startup
    logger.info("🚀 Starting RAG Service API...")

    try:
        # CRITICAL: Create connection pool with proper sizing
        # Use settings from environment variables
        app.state.db_pool = await asyncpg.create_pool(
            settings.DATABASE_URL,
            min_size=settings.DATABASE_POOL_MIN_SIZE,
            max_size=settings.DATABASE_POOL_MAX_SIZE,
            command_timeout=60,
        )
        logger.info(
            f"✅ Database pool initialized "
            f"(min_size={settings.DATABASE_POOL_MIN_SIZE}, "
            f"max_size={settings.DATABASE_POOL_MAX_SIZE})"
        )
    except Exception as e:
        logger.error(f"❌ Failed to initialize database pool: {e}")
        raise

    try:
        # Initialize Qdrant vector database client with increased timeout
        # Default timeout (5s) was causing httpx.WriteTimeout on large document uploads (2.7MB → 400 chunks)
        # Increased to 60s to handle batch upserts of large documents
        app.state.qdrant_client = AsyncQdrantClient(
            url=settings.QDRANT_URL,
            timeout=60,  # 60 second timeout for large batch operations
        )
        logger.info(f"✅ Qdrant client initialized (url={settings.QDRANT_URL}, timeout=60s)")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Qdrant client: {e}")
        # Clean up database pool if Qdrant fails
        await app.state.db_pool.close()
        raise

    try:
        # Initialize OpenAI client for embeddings
        from openai import AsyncOpenAI
        # CRITICAL: SecretStr must be unwrapped with .get_secret_value()
        app.state.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY.get_secret_value())
        logger.info(f"✅ OpenAI client initialized (model={settings.OPENAI_EMBEDDING_MODEL})")
    except Exception as e:
        logger.error(f"❌ Failed to initialize OpenAI client: {e}")
        # Clean up resources if OpenAI client fails
        await app.state.qdrant_client.close()
        await app.state.db_pool.close()
        raise

    # NOTE: Per-domain collection architecture - collections created dynamically per source
    # Old global collections (AI_DOCUMENTS, AI_CODE, AI_MEDIA, documents) are deprecated
    # Collections now created on-demand when sources are created via SourceService
    logger.info("✅ Using per-domain collection architecture (collections created per source)")

    yield

    # Shutdown
    logger.info("🛑 Shutting down RAG Service API...")

    try:
        # Close Qdrant client
        await app.state.qdrant_client.close()
        logger.info("✅ Qdrant client closed")
    except Exception as e:
        logger.error(f"❌ Error during Qdrant client shutdown: {e}", exc_info=True)

    try:
        # CRITICAL: Close pool to release all connections
        await app.state.db_pool.close()
        logger.info("✅ Database pool closed")
    except Exception as e:
        logger.error(f"❌ Error during database pool shutdown: {e}", exc_info=True)


# Create FastAPI application with lifespan
app = FastAPI(
    title="RAG Service API",
    description="RAG service with vector search, document ingestion, and hybrid search capabilities",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS - Environment-specific origins (Gotcha #8)
# Use settings.cors_origins_list which handles both development and production
origins = settings.cors_origins_list

logger.info(f"CORS configured with origins: {origins}")

# CRITICAL: NEVER use allow_origins=["*"] in production (Gotcha #8)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Specific origins only
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
)

# Health check (no prefix)
app.include_router(health.router, tags=["health"])

# API routes (already have /api prefix in router definitions)
app.include_router(documents.router, tags=["documents"])
app.include_router(search.router, tags=["search"])
app.include_router(sources.router, tags=["sources"])
app.include_router(crawls.router, tags=["crawls"])


@app.get("/")
async def root():
    """Root endpoint returning API information.

    Returns:
        dict: API metadata and available endpoints
    """
    return {
        "name": "RAG Service API",
        "version": "1.0.0",
        "description": "Vector search and document ingestion service",
        "status": "healthy",
        "docs": "/docs",
        "health": "/health",
        "features": {
            "vector_search": True,
            "document_ingestion": True,
            "hybrid_search": settings.USE_HYBRID_SEARCH,
            "embedding_model": settings.OPENAI_EMBEDDING_MODEL,
        },
    }
