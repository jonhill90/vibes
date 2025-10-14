"""Health check endpoints for RAG Service.

This module provides health check endpoints to validate PostgreSQL and Qdrant
connectivity. Returns 200 if healthy, 503 if unhealthy.

CRITICAL GOTCHAS ADDRESSED:
- Gotcha #2: Uses get_db_pool (returns pool), services acquire connections
- Returns 503 (Service Unavailable) on unhealthy, not 500

Pattern Reference: examples/07_fastapi_endpoint_pattern.py
"""

import asyncpg
from fastapi import APIRouter, Depends, HTTPException
from qdrant_client import AsyncQdrantClient

from ..dependencies import get_db_pool, get_qdrant_client

router = APIRouter()


@router.get("/health")
async def health_check(
    db_pool: asyncpg.Pool = Depends(get_db_pool),
    qdrant_client: AsyncQdrantClient = Depends(get_qdrant_client),
):
    """Comprehensive health check for RAG Service.

    Validates connectivity to both PostgreSQL and Qdrant vector database.
    Returns detailed component-level status for monitoring and debugging.

    Args:
        db_pool: Database connection pool (injected by FastAPI)
        qdrant_client: Qdrant vector database client (injected by FastAPI)

    Returns:
        dict: Health status with component details
            - status: "healthy" | "unhealthy"
            - checks: Component-level status for postgresql and qdrant

    Raises:
        HTTPException: 503 if any component is unhealthy

    Example Response (Healthy):
        {
            "status": "healthy",
            "checks": {
                "postgresql": "healthy",
                "qdrant": "healthy"
            }
        }

    Example Response (Unhealthy):
        {
            "status": "unhealthy",
            "checks": {
                "postgresql": "healthy",
                "qdrant": "unhealthy: Connection refused"
            }
        }

    Pattern:
        - Use Depends() for dependency injection (Gotcha #2)
        - Use async with pool.acquire() to get connection
        - Return 503 (Service Unavailable) on unhealthy, not 500
        - Include component-level details in response
    """
    health_status = {"status": "healthy", "checks": {}}

    # Check PostgreSQL connectivity
    # CRITICAL: Use async with pool.acquire() to get connection (Gotcha #2)
    try:
        async with db_pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        health_status["checks"]["postgresql"] = "healthy"
    except Exception as e:
        health_status["checks"]["postgresql"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"

    # Check Qdrant connectivity
    try:
        # Quick health check - list collections validates connection
        await qdrant_client.get_collections()
        health_status["checks"]["qdrant"] = "healthy"
    except Exception as e:
        health_status["checks"]["qdrant"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"

    # Return 503 (Service Unavailable) if any component unhealthy
    if health_status["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=health_status)

    return health_status
