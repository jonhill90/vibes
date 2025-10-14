"""Database connection pool configuration using asyncpg.

This module provides:
- Async connection pool initialization and cleanup (used in main.py lifespan)
- Database utility functions for schema management
- Proper async context management for connection lifecycle

IMPORTANT: This file does NOT provide get_db_pool dependency!
That dependency lives in src/api/dependencies.py to avoid circular imports.

Critical Gotchas Addressed:
- Gotcha #1: Uses async def for all database operations (non-blocking)
- Gotcha #2: Returns POOL from dependencies, NOT connections (see dependencies.py)
- Gotcha #12: Services must use async with pool.acquire() for proper cleanup
- Gotcha #7: Configured for $1, $2 placeholders (asyncpg style, not %s)

Pattern: FastAPI Lifespan Connection Pool
Reference: infra/task-manager/backend/src/config/database.py
"""

import asyncpg
import logging
from typing import Optional

from src.config.settings import settings

logger = logging.getLogger(__name__)


async def create_db_pool() -> asyncpg.Pool:
    """Create asyncpg connection pool with configuration from settings.

    This function is called during FastAPI lifespan startup to initialize
    the global database connection pool.

    Configuration:
    - DATABASE_URL: From settings (with validation)
    - min_size: From settings.DATABASE_POOL_MIN_SIZE (default: 2)
    - max_size: From settings.DATABASE_POOL_MAX_SIZE (default: 10)
    - command_timeout: 60 seconds for query timeout

    Returns:
        asyncpg.Pool: Configured connection pool

    Raises:
        asyncpg.PostgresError: If connection to database fails
        ValueError: If DATABASE_URL is invalid

    Example:
        # In main.py lifespan:
        app.state.db_pool = await create_db_pool()
    """
    logger.info("Creating asyncpg connection pool...")

    try:
        pool = await asyncpg.create_pool(
            settings.DATABASE_URL,
            min_size=settings.DATABASE_POOL_MIN_SIZE,
            max_size=settings.DATABASE_POOL_MAX_SIZE,
            command_timeout=60,
        )
        logger.info(
            f"Database pool created successfully "
            f"(min_size={settings.DATABASE_POOL_MIN_SIZE}, "
            f"max_size={settings.DATABASE_POOL_MAX_SIZE}, "
            f"timeout=60s)"
        )
        return pool
    except asyncpg.PostgresError as e:
        logger.error(f"Failed to create database pool: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating database pool: {e}")
        raise


async def close_db_pool(pool: asyncpg.Pool) -> None:
    """Close the database connection pool gracefully.

    This should be called during application shutdown (in lifespan context)
    to ensure all connections are properly closed.

    Args:
        pool: The asyncpg connection pool to close

    Example:
        # In main.py lifespan shutdown:
        await close_db_pool(app.state.db_pool)
    """
    if pool is not None:
        logger.info("Closing database pool...")
        await pool.close()
        logger.info("Database pool closed successfully")


async def check_db_connection(pool: asyncpg.Pool) -> bool:
    """Check if database connection is healthy.

    Useful for health checks and monitoring.

    Args:
        pool: Database connection pool to test

    Returns:
        bool: True if connection is healthy, False otherwise

    Example:
        # In health check endpoint:
        healthy = await check_db_connection(app.state.db_pool)
    """
    try:
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        return True
    except Exception as e:
        logger.warning(f"Database health check failed: {e}")
        return False


async def execute_schema_sql(pool: asyncpg.Pool, sql: str) -> None:
    """Execute schema DDL SQL (CREATE TABLE, CREATE INDEX, etc.).

    Useful for database initialization and migrations.

    Args:
        pool: Database connection pool
        sql: SQL DDL statement to execute

    Raises:
        asyncpg.PostgresError: If SQL execution fails

    Example:
        await execute_schema_sql(pool, '''
            CREATE TABLE IF NOT EXISTS documents (
                id UUID PRIMARY KEY,
                title TEXT NOT NULL
            )
        ''')
    """
    try:
        async with pool.acquire() as conn:
            await conn.execute(sql)
        logger.info("Schema SQL executed successfully")
    except asyncpg.PostgresError as e:
        logger.error(f"Failed to execute schema SQL: {e}")
        raise


async def get_db_version(pool: asyncpg.Pool) -> Optional[str]:
    """Get PostgreSQL version from database.

    Useful for debugging and compatibility checks.

    Args:
        pool: Database connection pool

    Returns:
        Optional[str]: PostgreSQL version string, or None if query fails

    Example:
        version = await get_db_version(app.state.db_pool)
        # Returns: "PostgreSQL 15.3 on x86_64-pc-linux-gnu..."
    """
    try:
        async with pool.acquire() as conn:
            version = await conn.fetchval("SELECT version()")
        return version
    except Exception as e:
        logger.error(f"Failed to get database version: {e}")
        return None


# CRITICAL NOTE: get_db_pool dependency is NOT here!
# It must be in src/api/dependencies.py to avoid circular imports
# and to properly integrate with FastAPI's dependency injection.
#
# See src/api/dependencies.py for:
# - async def get_db_pool(request: Request) -> asyncpg.Pool
# - async def get_qdrant_client(request: Request) -> AsyncQdrantClient
