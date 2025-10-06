"""Database connection pool configuration using asyncpg.

This module provides:
- Async connection pool initialization and cleanup
- FastAPI dependency injection for database connections
- Proper async context management for connection lifecycle

Critical Gotchas Addressed:
- Gotcha #1: Uses async def for all database operations (non-blocking)
- Gotcha #12: Always uses async with pool.acquire() for proper cleanup
- Gotcha #7: Configured for $1, $2 placeholders (asyncpg style, not %s)
"""

import os
from typing import AsyncGenerator
import asyncpg
import logging

logger = logging.getLogger(__name__)

# Global connection pool instance
_db_pool: asyncpg.Pool | None = None


async def init_db_pool() -> asyncpg.Pool:
    """Initialize asyncpg connection pool.

    Configuration:
    - min_size=5: Minimum number of connections to maintain
    - max_size=20: Maximum number of connections allowed
    - command_timeout=60: Timeout for queries (seconds)

    Returns:
        asyncpg.Pool: Configured connection pool

    Raises:
        ValueError: If DATABASE_URL environment variable is not set
        asyncpg.PostgresError: If connection to database fails
    """
    global _db_pool

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError(
            "DATABASE_URL environment variable is required. "
            "Expected format: postgresql://user:password@host:port/database"
        )

    logger.info("Initializing asyncpg connection pool...")

    try:
        _db_pool = await asyncpg.create_pool(
            database_url,
            min_size=5,  # Minimum connections to keep open
            max_size=20,  # Maximum connections allowed
            command_timeout=60,  # Query timeout in seconds
        )
        logger.info(
            f"Database pool initialized successfully "
            f"(min_size=5, max_size=20, timeout=60s)"
        )
        return _db_pool
    except asyncpg.PostgresError as e:
        logger.error(f"Failed to initialize database pool: {e}")
        raise


async def close_db_pool() -> None:
    """Close the database connection pool gracefully.

    This should be called during application shutdown to ensure
    all connections are properly closed.
    """
    global _db_pool

    if _db_pool is not None:
        logger.info("Closing database pool...")
        await _db_pool.close()
        _db_pool = None
        logger.info("Database pool closed successfully")


async def get_db() -> AsyncGenerator[asyncpg.Connection, None]:
    """FastAPI dependency for injecting database connections.

    Usage in endpoints:
        @app.get("/tasks")
        async def get_tasks(db: asyncpg.Connection = Depends(get_db)):
            tasks = await db.fetch("SELECT * FROM tasks")
            return tasks

    Critical:
    - Uses async with pool.acquire() to ensure connection is released
    - Connection is automatically returned to pool after request completes
    - Handles connection errors gracefully

    Yields:
        asyncpg.Connection: Database connection from the pool

    Raises:
        RuntimeError: If database pool has not been initialized
        asyncpg.PostgresError: If connection acquisition fails
    """
    global _db_pool

    if _db_pool is None:
        raise RuntimeError(
            "Database pool not initialized. "
            "Call init_db_pool() during application startup."
        )

    # Gotcha #12: ALWAYS use async with for connection management
    # This ensures the connection is returned to the pool even if an error occurs
    async with _db_pool.acquire() as connection:
        try:
            yield connection
        except asyncpg.PostgresError as e:
            logger.error(f"Database error during request: {e}")
            raise
        finally:
            # Connection is automatically released back to pool
            # by the async context manager
            pass


async def get_pool() -> asyncpg.Pool:
    """Get the global connection pool instance.

    Useful for service layers that need to manage transactions
    across multiple operations.

    Returns:
        asyncpg.Pool: Global connection pool

    Raises:
        RuntimeError: If database pool has not been initialized
    """
    global _db_pool

    if _db_pool is None:
        raise RuntimeError(
            "Database pool not initialized. "
            "Call init_db_pool() during application startup."
        )

    return _db_pool
