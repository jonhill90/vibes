"""FastAPI application for RAG Service.

This is the main entry point for the RAG Service backend API.
Provides RESTful endpoints for document ingestion, vector search, and RAG operations
with proper CORS configuration and database lifecycle management.

KEY FEATURES:
- Environment-specific CORS configuration (Gotcha #8)
- Database connection pool lifecycle management (Gotcha #2)
- Qdrant client initialization and cleanup
- Health check endpoint
- OpenAPI documentation with metadata
- API router organization with /api prefix

CRITICAL GOTCHAS ADDRESSED:
- Gotcha #2: Returns POOL from dependencies, NOT connections
- Gotcha #8: CORS configured with specific origins (NEVER allow_origins=["*"])
- Gotcha #12: Services use async with pool.acquire() for connection management
"""

import logging
import os
from contextlib import asynccontextmanager

import asyncpg
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from qdrant_client import AsyncQdrantClient

from src.config.settings import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown tasks.

    Startup:
    - Initialize database connection pool
    - Initialize Qdrant vector database client

    Shutdown:
    - Close database connection pool gracefully
    - Close Qdrant client gracefully

    CRITICAL PATTERN:
    - Store POOL in app.state, not connections (Gotcha #2)
    - Dependencies return pool, services acquire connections as needed
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
        # Initialize Qdrant vector database client
        app.state.qdrant_client = AsyncQdrantClient(url=settings.QDRANT_URL)
        logger.info(f"✅ Qdrant client initialized (url={settings.QDRANT_URL})")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Qdrant client: {e}")
        # Clean up database pool if Qdrant fails
        await app.state.db_pool.close()
        raise

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
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "development":
    # Development: Allow local frontend origins
    origins = [
        "http://localhost:3000",  # React default port
        "http://localhost:5173",  # Vite default port
        "http://localhost:5174",  # Vite alternate port
        "http://host.docker.internal:3000",  # Docker Desktop internal DNS
        "http://host.docker.internal:5173",  # Docker Desktop Vite
    ]
elif ENVIRONMENT == "production":
    # Production: Use environment variable for allowed origins
    cors_origins = os.getenv("CORS_ORIGINS", "")
    origins = [origin.strip() for origin in cors_origins.split(",") if origin.strip()]
else:
    # Unknown environment: No origins allowed
    origins = []

# CRITICAL: NEVER use allow_origins=["*"] in production (Gotcha #8)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Specific origins only
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
)

# Include API routers
from src.api.routes import health

app.include_router(health.router, tags=["health"])

# TODO: Include additional API routers when implemented
# from src.api import documents_router, search_router, sources_router
# app.include_router(documents_router, prefix="/api")
# app.include_router(search_router, prefix="/api")
# app.include_router(sources_router, prefix="/api")


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
