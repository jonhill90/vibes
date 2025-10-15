# Source: infra/rag-service/backend/src/main.py
# Lines: 38-133 (lifespan context manager)
# Pattern: FastAPI lifespan for connection pool management
# Extracted: 2025-10-14
# Relevance: 9/10 - Critical pattern for preventing connection pool deadlocks (Gotcha #2)

"""
WHAT THIS DEMONSTRATES:
- FastAPI lifespan context manager
- Database connection pool initialization
- Qdrant client initialization
- Graceful shutdown with resource cleanup
- HNSW disabled for bulk upload (Gotcha #9)
"""

import logging
from contextlib import asynccontextmanager
import asyncpg
from fastapi import FastAPI
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import VectorParams, Distance, HnswConfigDiff

logger = logging.getLogger(__name__)


# ==============================================================================
# PATTERN 1: Lifespan Context Manager
# ==============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown tasks.

    CRITICAL PATTERNS:
    - Store POOL in app.state, not connections (Gotcha #2)
    - Dependencies return pool, services acquire connections as needed
    - HNSW disabled (m=0) during bulk upload for 60-90x speedup (Gotcha #9)

    Startup:
    - Initialize database connection pool
    - Initialize Qdrant vector database client
    - Create Qdrant collection with HNSW disabled for bulk upload

    Shutdown:
    - Close database connection pool gracefully
    - Close Qdrant client gracefully
    """
    # ==========================================================================
    # STARTUP PHASE
    # ==========================================================================

    logger.info("🚀 Starting RAG Service API...")

    try:
        # ----------------------------------------------------------------------
        # Step 1: Initialize Database Connection Pool
        # ----------------------------------------------------------------------

        # CRITICAL (Gotcha #2): Create connection pool with proper sizing
        # Use settings from environment variables
        app.state.db_pool = await asyncpg.create_pool(
            dsn="postgresql://user:pass@localhost:5433/rag_service",
            min_size=10,  # Minimum pool size
            max_size=20,  # Maximum pool size
            command_timeout=60,  # Query timeout in seconds
        )

        logger.info(
            f"✅ Database pool initialized "
            f"(min_size=10, max_size=20)"
        )

    except Exception as e:
        logger.error(f"❌ Failed to initialize database pool: {e}")
        raise

    try:
        # ----------------------------------------------------------------------
        # Step 2: Initialize Qdrant Vector Database Client
        # ----------------------------------------------------------------------

        app.state.qdrant_client = AsyncQdrantClient(
            url="http://localhost:6333"
        )

        logger.info(f"✅ Qdrant client initialized (url=http://localhost:6333)")

    except Exception as e:
        logger.error(f"❌ Failed to initialize Qdrant client: {e}")
        # Clean up database pool if Qdrant fails
        await app.state.db_pool.close()
        raise

    try:
        # ----------------------------------------------------------------------
        # Step 3: Initialize Qdrant Collection with HNSW Disabled
        # ----------------------------------------------------------------------

        # CRITICAL (Gotcha #9): HNSW enabled during bulk upload is 60-90x slower
        # Disable with m=0, re-enable after bulk upload completes

        collections = await app.state.qdrant_client.get_collections()
        collection_names = [c.name for c in collections.collections]

        if "documents" not in collection_names:
            await app.state.qdrant_client.create_collection(
                collection_name="documents",
                vectors_config=VectorParams(
                    size=1536,  # text-embedding-3-small dimension
                    distance=Distance.COSINE,
                    hnsw_config=HnswConfigDiff(m=0),  # Disable HNSW for bulk (Gotcha #9)
                ),
            )

            logger.info(
                f"✅ Qdrant collection created: documents "
                f"(dims=1536, distance=COSINE, HNSW disabled for bulk)"
            )
        else:
            logger.info(f"✅ Qdrant collection already exists: documents")

    except Exception as e:
        logger.error(f"❌ Failed to initialize Qdrant collection: {e}")
        # Clean up resources if collection initialization fails
        await app.state.qdrant_client.close()
        await app.state.db_pool.close()
        raise

    # ==========================================================================
    # APPLICATION RUNS (yield control back to FastAPI)
    # ==========================================================================

    yield  # Application is running, handle requests

    # ==========================================================================
    # SHUTDOWN PHASE
    # ==========================================================================

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


# ==============================================================================
# PATTERN 2: Create FastAPI Application with Lifespan
# ==============================================================================

app = FastAPI(
    title="RAG Service API",
    description="RAG service with vector search, document ingestion, and hybrid search",
    version="1.0.0",
    lifespan=lifespan,  # Register lifespan context manager
)


# ==============================================================================
# PATTERN 3: Dependency for Database Pool Access
# ==============================================================================

from fastapi import Request

async def get_db_pool(request: Request) -> asyncpg.Pool:
    """Dependency that returns database pool from app state.

    CRITICAL (Gotcha #2): Return POOL, not connection.
    Route handlers and services will acquire connections as needed using:
        async with pool.acquire() as conn:
            # Use connection
    """
    return request.app.state.db_pool


# ==============================================================================
# PATTERN 4: Example Route Using Pool Dependency
# ==============================================================================

from fastapi import Depends

@app.get("/documents")
async def list_documents(
    db_pool: asyncpg.Pool = Depends(get_db_pool)  # Inject pool
):
    """List documents using connection from pool.

    CRITICAL (Gotcha #8): Always use async with pool.acquire()
    Never store connections in app.state or class attributes.
    """
    # CORRECT: Acquire connection from pool for this request
    async with db_pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM documents LIMIT 10")

    # Connection is automatically released back to pool when exiting async with

    return {"documents": [dict(row) for row in rows]}


# ==============================================================================
# PATTERN 5: Re-enabling HNSW After Bulk Upload
# ==============================================================================

async def enable_hnsw_after_bulk():
    """Re-enable HNSW after bulk upload completes.

    Call this after ingesting large batches of documents (>1000).
    HNSW indexing will occur in background, improving search performance.

    Performance impact:
    - Bulk upload with HNSW disabled (m=0): ~2-3 docs/sec
    - Bulk upload with HNSW enabled (m=16): ~0.03-0.05 docs/sec (60-90x slower)
    - After re-enabling: Search latency improves from ~200ms to ~20ms
    """
    from qdrant_client.models import OptimizersConfigDiff

    # Update collection to re-enable HNSW
    await app.state.qdrant_client.update_collection(
        collection_name="documents",
        hnsw_config=HnswConfigDiff(
            m=16,  # Re-enable HNSW with default parameters
            ef_construct=100,
            on_disk=False,
        ),
    )

    logger.info("✅ HNSW re-enabled for collection: documents")

    # Trigger indexing (optional, happens automatically in background)
    # await app.state.qdrant_client.update_collection(
    #     collection_name="documents",
    #     optimizer_config=OptimizersConfigDiff(indexing_threshold=0)
    # )


# ==============================================================================
# PATTERN 6: Service Initialization (Alternative Pattern)
# ==============================================================================

# For more complex apps, you can initialize services in lifespan and store them:

@asynccontextmanager
async def lifespan_with_services(app: FastAPI):
    """Lifespan with service initialization."""

    # Startup
    db_pool = await asyncpg.create_pool(...)
    qdrant_client = AsyncQdrantClient(...)

    # Initialize services
    from services.embedding_service import EmbeddingService
    from services.vector_service import VectorService
    from services.rag_service import RAGService

    embedding_service = EmbeddingService(db_pool=db_pool, openai_client=...)
    vector_service = VectorService(qdrant_client=qdrant_client)
    rag_service = RAGService(
        embedding_service=embedding_service,
        vector_service=vector_service,
    )

    # Store in app.state
    app.state.db_pool = db_pool
    app.state.qdrant_client = qdrant_client
    app.state.embedding_service = embedding_service
    app.state.vector_service = vector_service
    app.state.rag_service = rag_service

    yield  # Application runs

    # Shutdown
    await qdrant_client.close()
    await db_pool.close()


# ==============================================================================
# KEY TAKEAWAYS
# ==============================================================================

# ✅ DO THIS:
# 1. Use @asynccontextmanager for lifespan
# 2. Initialize connection pool in startup
# 3. Store POOL in app.state (not connections)
# 4. Use async with pool.acquire() in routes/services
# 5. Disable HNSW (m=0) for bulk upload (60-90x faster)
# 6. Re-enable HNSW after bulk upload completes
# 7. Close resources gracefully in shutdown
# 8. Handle exceptions during startup (cleanup partially initialized resources)

# ❌ DON'T DO THIS:
# 1. Create new pool for each request (pool exhaustion)
# 2. Store connections in app.state (connection leaks)
# 3. Forget to close pool in shutdown (connection leaks)
# 4. Use HNSW during bulk upload (60-90x slower)
# 5. Skip error handling in startup (resource leaks)
# 6. Acquire connection without async with (connection not released)
