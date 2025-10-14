# Source: infra/task-manager/backend/src/main.py
# Lines: 33-63
# Pattern: FastAPI Lifespan with Connection Pool
# Extracted: 2025-10-14
# Relevance: 10/10 - Critical for FastAPI startup/shutdown

"""
PATTERN: FastAPI Lifespan with asyncpg Connection Pool

This demonstrates the correct way to manage database connection pools
in FastAPI applications using the lifespan pattern.

Key Patterns:
1. Use @asynccontextmanager for lifespan
2. Initialize pool in startup phase
3. Store pool in app.state for dependency injection
4. Close pool in shutdown phase
5. Never return connections from dependencies (return pool!)

CRITICAL GOTCHAS:
- Gotcha #2: Return pool from dependencies, NOT connections
- Gotcha #12: Always use async with pool.acquire() in services
"""

import asyncpg
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown tasks.

    Startup:
    - Initialize database connection pool

    Shutdown:
    - Close database connection pool gracefully
    """
    # Startup
    logger.info("🚀 Starting RAG Service API...")

    try:
        # CRITICAL: Create connection pool with proper sizing
        # min_size=10, max_size=20 from task-manager proven pattern
        db_pool = await asyncpg.create_pool(
            host="localhost",
            port=5432,
            database="rag_service",
            user="postgres",
            password="postgres",
            min_size=10,
            max_size=20,
            command_timeout=60,
        )

        # Store pool in app.state (NOT individual connections)
        app.state.db_pool = db_pool

        logger.info("✅ Database pool initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database pool: {e}")
        raise

    yield

    # Shutdown
    logger.info("🛑 Shutting down RAG Service API...")

    try:
        # CRITICAL: Close pool to release all connections
        await app.state.db_pool.close()
        logger.info("✅ Database pool closed")
    except Exception as e:
        logger.error(f"❌ Error during database pool shutdown: {e}", exc_info=True)


# Create FastAPI application with lifespan
app = FastAPI(
    title="RAG Service API",
    description="RAG service with vector search and document ingestion",
    version="1.0.0",
    lifespan=lifespan,
)


# Dependency injection for database pool
async def get_db_pool(request: Request) -> asyncpg.Pool:
    """Get database pool from app state.

    CRITICAL PATTERN: Return the pool, NOT a connection.
    Services will acquire/release connections as needed.

    Args:
        request: FastAPI request object

    Returns:
        asyncpg.Pool: Database connection pool
    """
    return request.app.state.db_pool


# Example service initialization in endpoint
@app.get("/api/documents")
async def list_documents(db_pool: asyncpg.Pool = Depends(get_db_pool)):
    """List documents endpoint demonstrating service usage.

    PATTERN: Inject pool, pass to service, let service manage connections.
    """
    from services.document_service import DocumentService

    # Initialize service with pool (not connection!)
    document_service = DocumentService(db_pool)

    # Service uses: async with db_pool.acquire() as conn
    success, result = await document_service.list_documents()

    if not success:
        raise HTTPException(status_code=500, detail=result.get("error"))

    return result
