"""FastAPI dependency injection for database and vector database clients.

This module provides dependency functions that inject database pool and
Qdrant client into endpoint handlers.

CRITICAL GOTCHA #2: Return POOL, NOT connection!
- Dependencies return the pool object
- Services acquire connections using: async with pool.acquire() as conn
- This prevents connection leaks and deadlocks

Critical Gotchas Addressed:
- Gotcha #2: get_db_pool returns Pool, NOT Connection (prevents deadlock)
- Gotcha #12: Services must use async with pool.acquire() for connections
- Proper error handling if pool/client not initialized

Pattern: FastAPI Dependency Injection
Reference: examples/08_connection_pool_setup.py
"""

import asyncpg
from fastapi import Request, HTTPException
from qdrant_client import AsyncQdrantClient


async def get_db_pool(request: Request) -> asyncpg.Pool:
    """Get database connection pool from application state.

    CRITICAL: This returns the POOL, NOT a connection!

    Services must acquire connections explicitly:
    ```python
    async def my_service_method(self, db_pool: asyncpg.Pool):
        async with db_pool.acquire() as conn:
            result = await conn.fetch("SELECT * FROM documents")
        # Connection automatically released here
    ```

    Why this matters (Gotcha #2):
    - Returning a connection would cause deadlock (connection never released)
    - Pool allows services to acquire/release connections per operation
    - Enables transaction management across multiple queries

    Args:
        request: FastAPI request object containing app state

    Returns:
        asyncpg.Pool: Database connection pool (NOT a connection!)

    Raises:
        HTTPException: 503 if database pool not initialized

    Example:
        @app.get("/api/documents")
        async def list_docs(db_pool: asyncpg.Pool = Depends(get_db_pool)):
            service = DocumentService(db_pool)
            return await service.list_documents()
    """
    pool = getattr(request.app.state, "db_pool", None)

    if pool is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "Database pool not initialized. "
                "Service may be starting up or database connection failed."
            ),
        )

    return pool


async def get_qdrant_client(request: Request) -> AsyncQdrantClient:
    """Get Qdrant vector database client from application state.

    The Qdrant client is initialized during application startup and stored
    in app.state for reuse across requests.

    Args:
        request: FastAPI request object containing app state

    Returns:
        AsyncQdrantClient: Qdrant vector database client

    Raises:
        HTTPException: 503 if Qdrant client not initialized

    Example:
        @app.get("/api/search")
        async def search(
            qdrant: AsyncQdrantClient = Depends(get_qdrant_client)
        ):
            results = await qdrant.search(
                collection_name="documents",
                query_vector=[0.1, 0.2, ...],
                limit=10
            )
            return results
    """
    client = getattr(request.app.state, "qdrant_client", None)

    if client is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "Qdrant client not initialized. "
                "Service may be starting up or Qdrant connection failed."
            ),
        )

    return client


# Additional dependency examples for common patterns:


async def get_db_connection(request: Request) -> asyncpg.Connection:
    """Get a database connection from the pool (alternative pattern).

    WARNING: Use this sparingly! Prefer get_db_pool() and let services
    manage connections. This is only for simple endpoints that need
    a single query.

    IMPORTANT: FastAPI's dependency system does NOT automatically release
    this connection. You must use try/finally or context manager.

    Args:
        request: FastAPI request object

    Yields:
        asyncpg.Connection: Database connection (will be released)

    Example (NOT RECOMMENDED - prefer get_db_pool):
        @app.get("/api/count")
        async def get_count(conn: asyncpg.Connection = Depends(get_db_connection)):
            count = await conn.fetchval("SELECT COUNT(*) FROM documents")
            return {"count": count}
    """
    pool = await get_db_pool(request)

    # Acquire connection
    connection = await pool.acquire()

    try:
        yield connection
    finally:
        # CRITICAL: Always release connection back to pool
        await pool.release(connection)


# Dependency pattern for service initialization:
# Services should be initialized in endpoints, not as dependencies,
# to avoid complexity. Example:
#
# @app.get("/api/documents")
# async def list_documents(db_pool: asyncpg.Pool = Depends(get_db_pool)):
#     # Initialize service with pool
#     document_service = DocumentService(db_pool)
#
#     # Call service method
#     success, result = await document_service.list_documents()
#
#     if not success:
#         raise HTTPException(status_code=500, detail=result.get("error"))
#
#     return result
