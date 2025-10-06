"""FastAPI application for Task Management UI.

This is the main entry point for the Task Management backend API.
Provides RESTful endpoints for project and task management with proper
CORS configuration and database lifecycle management.

KEY FEATURES:
- Environment-specific CORS configuration (Gotcha #8)
- Database connection pool lifecycle management
- Health check endpoint
- OpenAPI documentation with metadata
- API router organization with /api prefix

CRITICAL GOTCHAS ADDRESSED:
- Gotcha #8: CORS configured with specific origins (NEVER allow_origins=["*"] in production)
- Database pool initialized on startup, closed on shutdown
- Async application lifespan for proper resource management
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import projects_router, tasks_router
from config.database import init_db_pool, close_db_pool

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
    logger.info("🚀 Starting Task Management API...")

    try:
        await init_db_pool()
        logger.info("✅ Database pool initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database pool: {e}")
        raise

    yield

    # Shutdown
    logger.info("🛑 Shutting down Task Management API...")

    try:
        await close_db_pool()
        logger.info("✅ Database pool closed")
    except Exception as e:
        logger.error(f"❌ Error during database pool shutdown: {e}", exc_info=True)


# Create FastAPI application
app = FastAPI(
    title="Task Management API",
    description="RESTful API for managing projects and tasks with hierarchical organization",
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

# Include API routers with /api prefix
app.include_router(projects_router, prefix="/api")
app.include_router(tasks_router, prefix="/api")


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring and load balancers.

    Returns:
        dict: Health status with service name and status
    """
    return {
        "status": "healthy",
        "service": "task-management-api",
        "version": "1.0.0",
    }


@app.get("/")
async def root():
    """Root endpoint returning API information.

    Returns:
        dict: API metadata and available endpoints
    """
    return {
        "name": "Task Management API",
        "version": "1.0.0",
        "description": "RESTful API for managing projects and tasks",
        "status": "healthy",
        "docs": "/docs",
        "health": "/health",
    }
