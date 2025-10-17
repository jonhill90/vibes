"""Crawl Job API routes.

This module provides REST API endpoints for web crawling operations with:
- Start new crawl jobs with URL and depth/page limits
- List crawl jobs with filters (status, source_id) and pagination
- Get crawl job status and progress
- Abort running crawl jobs

Critical Gotchas Addressed:
- Gotcha #2: Inject db_pool, services acquire connections
- Gotcha #3: Use $1, $2 placeholders in SQL
- Gotcha #9: Crawler service manages browser memory limits

Pattern: Example 05 (FastAPI route pattern)
Reference: infra/task-manager/backend/src/api/routes/
"""

import json
import logging
from typing import Optional
from uuid import UUID

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from src.api.dependencies import get_db_pool
from src.models.responses import ErrorResponse, MessageResponse
from src.services.crawler.crawl_service import CrawlerService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/crawls", tags=["crawls"])


# Request/Response Models
class CrawlStartRequest(BaseModel):
    """Request model for starting a new crawl job."""

    source_id: str = Field(
        ...,
        description="UUID of the source this crawl belongs to"
    )
    url: str = Field(
        ...,
        description="Starting URL to crawl",
        min_length=1,
        max_length=2000
    )
    max_pages: int = Field(
        default=100,
        description="Maximum number of pages to crawl",
        ge=1,
        le=1000
    )
    max_depth: int = Field(
        default=3,
        description="Maximum crawl depth (0 = start page only)",
        ge=0,
        le=10
    )


class CrawlJobResponse(BaseModel):
    """Response model for single crawl job operations."""

    id: str = Field(..., description="Crawl job UUID")
    source_id: str = Field(..., description="Parent source UUID")
    status: str = Field(
        ...,
        description="Job status: 'pending', 'running', 'completed', 'failed', 'cancelled'"
    )
    pages_crawled: int = Field(..., description="Number of pages crawled so far")
    pages_total: Optional[int] = Field(None, description="Total pages discovered (if known)")
    max_pages: int = Field(..., description="Maximum pages limit")
    max_depth: int = Field(..., description="Maximum depth limit")
    current_depth: int = Field(..., description="Current crawl depth")
    error_message: Optional[str] = Field(None, description="Error message if status is 'failed'")
    error_count: int = Field(..., description="Number of errors encountered")
    metadata: dict = Field(default_factory=dict, description="Additional metadata as JSON")
    started_at: Optional[str] = Field(None, description="ISO 8601 timestamp when crawl started")
    completed_at: Optional[str] = Field(None, description="ISO 8601 timestamp when crawl completed")
    created_at: str = Field(..., description="ISO 8601 timestamp when job was created")
    updated_at: str = Field(..., description="ISO 8601 timestamp of last update")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "source_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "running",
                "pages_crawled": 42,
                "pages_total": None,
                "max_pages": 100,
                "max_depth": 3,
                "current_depth": 2,
                "error_message": None,
                "error_count": 0,
                "metadata": {"domain": "example.com"},
                "started_at": "2025-10-14T10:00:00Z",
                "completed_at": None,
                "created_at": "2025-10-14T09:59:00Z",
                "updated_at": "2025-10-14T10:05:00Z"
            }
        }
    }


class CrawlJobListResponse(BaseModel):
    """Response model for paginated crawl job list."""

    crawl_jobs: list[CrawlJobResponse] = Field(..., description="List of crawl jobs")
    total_count: int = Field(..., description="Total number of jobs matching filters")
    limit: int = Field(..., description="Maximum items returned")
    offset: int = Field(..., description="Number of items skipped")

    model_config = {
        "json_schema_extra": {
            "example": {
                "crawl_jobs": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "source_id": "123e4567-e89b-12d3-a456-426614174000",
                        "status": "completed",
                        "pages_crawled": 85,
                        "pages_total": 85,
                        "max_pages": 100,
                        "max_depth": 3,
                        "current_depth": 3,
                        "error_message": None,
                        "error_count": 0,
                        "metadata": {},
                        "started_at": "2025-10-14T10:00:00Z",
                        "completed_at": "2025-10-14T10:15:00Z",
                        "created_at": "2025-10-14T09:59:00Z",
                        "updated_at": "2025-10-14T10:15:00Z"
                    }
                ],
                "total_count": 25,
                "limit": 50,
                "offset": 0
            }
        }
    }


# Route Handlers

@router.post(
    "",
    response_model=CrawlJobResponse,
    status_code=201,
    responses={
        201: {"description": "Crawl job created and started successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request or source not found"},
        500: {"model": ErrorResponse, "description": "Server error"},
    },
)
async def start_crawl(
    request: CrawlStartRequest,
    db_pool: asyncpg.Pool = Depends(get_db_pool),
) -> CrawlJobResponse:
    """Start a new web crawl job.

    This endpoint creates a crawl job record and initiates the crawl process
    asynchronously. The crawl will:
    1. Create a job record with 'pending' status
    2. Start crawling from the provided URL
    3. Update progress as pages are crawled
    4. Feed parsed content to ingestion pipeline

    Performance:
    - Max 3 concurrent browser instances (600MB RAM)
    - Rate limiting: 2-3 seconds between page requests
    - Exponential backoff for failed pages (3 retries max)

    Args:
        request: CrawlStartRequest with URL and crawl limits
        db_pool: Database pool (injected)

    Returns:
        CrawlJobResponse with created job details

    Raises:
        HTTPException: 400 for validation errors or invalid source_id, 500 for server errors
    """
    try:
        # Validate source_id format
        try:
            source_uuid = UUID(request.source_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": "Invalid source ID",
                    "detail": f"'{request.source_id}' is not a valid UUID",
                },
            )

        # Verify source exists
        async with db_pool.acquire() as conn:
            source_exists = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM sources WHERE id = $1)",
                source_uuid
            )

        if not source_exists:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": "Source not found",
                    "detail": f"Source with ID {request.source_id} does not exist",
                    "suggestion": "Create a source first using POST /api/sources"
                },
            )

        # Start crawl and ingestion using CrawlerService integrated with IngestionService
        # NOTE: crawl_website() will create the crawl job, NOT this endpoint
        # NOTE: This is synchronous for now - for large crawls, consider async background tasks
        try:
            import openai
            from src.services.ingestion_service import IngestionService
            from src.services.document_service import DocumentService
            from src.services.vector_service import VectorService
            from src.services.embeddings.embedding_service import EmbeddingService
            from src.services.chunker import TextChunker
            from src.services.document_parser import DocumentParser
            from src.config.settings import settings
            from qdrant_client import AsyncQdrantClient

            # Initialize services (normally done at app startup)
            crawler_service = CrawlerService(
                db_pool=db_pool,
                max_concurrent=3,
                rate_limit_delay=2.5,
                max_retries=3,
            )

            document_parser = DocumentParser()
            text_chunker = TextChunker()

            # Initialize OpenAI client (PATTERN FROM: mcp_server.py line 178-182)
            openai_client = openai.AsyncOpenAI(
                api_key=settings.OPENAI_API_KEY.get_secret_value()
            )

            # Initialize EmbeddingService with correct parameters (db_pool + openai_client)
            # FIX: Constructor takes (db_pool, openai_client), NOT (openai_api_key, model_name, batch_size)
            # Model name and batch size are read from settings inside the constructor
            embedding_service = EmbeddingService(
                db_pool=db_pool,
                openai_client=openai_client,
            )

            qdrant_client = AsyncQdrantClient(
                url=settings.QDRANT_URL,
                timeout=60,  # 60s timeout for large batch operations
            )
            vector_service = VectorService(
                qdrant_client=qdrant_client,
                collection_name=settings.QDRANT_COLLECTION_NAME,
            )

            document_service = DocumentService(db_pool)

            ingestion_service = IngestionService(
                db_pool=db_pool,
                document_parser=document_parser,
                text_chunker=text_chunker,
                embedding_service=embedding_service,
                vector_service=vector_service,
                document_service=document_service,
                crawler_service=crawler_service,
            )

            # Execute crawl ingestion (synchronous for now)
            # For async background processing, use: asyncio.create_task(...)
            success, crawl_result = await ingestion_service.ingest_from_crawl(
                source_id=source_uuid,
                url=request.url,
                max_pages=request.max_pages,
                recursive=(request.max_depth > 1),  # Recursive if depth > 1
            )

            # Extract job_id from crawl_result (created by crawl_website)
            job_id = UUID(crawl_result.get("crawl_job_id"))

            if not success:
                logger.error(
                    f"Crawl ingestion failed for job {job_id}: {crawl_result.get('error')}"
                )
                # Job status already updated by CrawlerService to 'failed'

            else:
                logger.info(
                    f"Crawl job {job_id} completed successfully: "
                    f"document={crawl_result.get('document_id')}, "
                    f"chunks={crawl_result.get('chunks_stored')}"
                )

            # Fetch updated job row to return latest status
            async with db_pool.acquire() as conn:
                job_row = await conn.fetchrow(
                    """
                    SELECT
                        id, source_id, status, pages_crawled, pages_total,
                        max_pages, max_depth, current_depth, error_message,
                        error_count, metadata, started_at, completed_at,
                        created_at, updated_at
                    FROM crawl_jobs
                    WHERE id = $1
                    """,
                    job_id
                )

        except Exception as crawl_error:
            logger.error(f"Crawl execution failed: {crawl_error}", exc_info=True)
            # If crawl_result has job_id, update it to failed, otherwise re-raise
            if 'crawl_result' in locals() and crawl_result.get("crawl_job_id"):
                job_id = UUID(crawl_result.get("crawl_job_id"))
                logger.error(f"Updating failed job {job_id}")
                # Update job status to failed
                async with db_pool.acquire() as conn:
                    job_row = await conn.fetchrow(
                        """
                        UPDATE crawl_jobs
                        SET status = 'failed',
                            error_message = $2,
                            completed_at = NOW(),
                            updated_at = NOW()
                        WHERE id = $1
                        RETURNING
                            id, source_id, status, pages_crawled, pages_total,
                            max_pages, max_depth, current_depth, error_message,
                            error_count, metadata, started_at, completed_at,
                            created_at, updated_at
                        """,
                        job_id,
                        str(crawl_error)
                    )
            else:
                # No job created yet, re-raise to outer exception handler
                raise

        # Convert to response model
        # Parse metadata if it's a string (asyncpg may return JSONB as string)
        metadata = job_row["metadata"]
        if isinstance(metadata, str):
            metadata = json.loads(metadata)

        return CrawlJobResponse(
            id=str(job_row["id"]),
            source_id=str(job_row["source_id"]),
            status=job_row["status"],
            pages_crawled=job_row["pages_crawled"],
            pages_total=job_row["pages_total"],
            max_pages=job_row["max_pages"],
            max_depth=job_row["max_depth"],
            current_depth=job_row["current_depth"],
            error_message=job_row["error_message"],
            error_count=job_row["error_count"],
            metadata=metadata,
            started_at=job_row["started_at"].isoformat() if job_row["started_at"] else None,
            completed_at=job_row["completed_at"].isoformat() if job_row["completed_at"] else None,
            created_at=job_row["created_at"].isoformat(),
            updated_at=job_row["updated_at"].isoformat(),
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Start crawl error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "Failed to start crawl",
                "detail": str(e),
                "suggestion": "Check server logs for details"
            },
        )


@router.get(
    "",
    response_model=CrawlJobListResponse,
    responses={
        200: {"description": "Crawl jobs retrieved successfully"},
        500: {"model": ErrorResponse, "description": "Server error"},
    },
)
async def list_crawl_jobs(
    source_id: Optional[str] = Query(None, description="Filter by source ID"),
    status: Optional[str] = Query(
        None,
        description="Filter by status (pending, running, completed, failed, cancelled)"
    ),
    limit: int = Query(50, ge=1, le=100, description="Maximum items to return (1-100)"),
    offset: int = Query(0, ge=0, description="Number of items to skip for pagination"),
    db_pool: asyncpg.Pool = Depends(get_db_pool),
) -> CrawlJobListResponse:
    """List crawl jobs with filters and pagination.

    Args:
        source_id: Optional filter by source UUID
        status: Optional filter by job status
        limit: Maximum items to return (1-100)
        offset: Number of items to skip for pagination
        db_pool: Database pool (injected)

    Returns:
        CrawlJobListResponse with paginated results

    Raises:
        HTTPException: 400 for invalid filters, 500 for server errors
    """
    try:
        # Build WHERE clause dynamically
        where_clauses = []
        params = []
        param_idx = 1

        if source_id:
            # Validate UUID
            try:
                source_uuid = UUID(source_id)
                where_clauses.append(f"source_id = ${param_idx}")
                params.append(source_uuid)
                param_idx += 1
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "success": False,
                        "error": "Invalid source ID",
                        "detail": f"'{source_id}' is not a valid UUID",
                    },
                )

        if status:
            # Validate status enum
            valid_statuses = ["pending", "running", "completed", "failed", "cancelled"]
            if status not in valid_statuses:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "success": False,
                        "error": "Invalid status",
                        "detail": f"Status must be one of: {', '.join(valid_statuses)}",
                    },
                )
            where_clauses.append(f"status = ${param_idx}")
            params.append(status)
            param_idx += 1

        where_clause = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        # Get total count
        count_query = f"SELECT COUNT(*) FROM crawl_jobs {where_clause}"

        async with db_pool.acquire() as conn:
            total_count = await conn.fetchval(count_query, *params)

            # Get paginated crawl jobs
            query = f"""
                SELECT
                    id, source_id, status, pages_crawled, pages_total,
                    max_pages, max_depth, current_depth, error_message,
                    error_count, metadata, started_at, completed_at,
                    created_at, updated_at
                FROM crawl_jobs
                {where_clause}
                ORDER BY created_at DESC
                LIMIT ${param_idx} OFFSET ${param_idx + 1}
            """
            params.extend([limit, offset])
            rows = await conn.fetch(query, *params)

        # Convert to response models
        crawl_job_responses = []
        for row in rows:
            # Parse metadata if it's a string (asyncpg may return JSONB as string)
            metadata = row["metadata"]
            if isinstance(metadata, str):
                metadata = json.loads(metadata)

            crawl_job_responses.append(
                CrawlJobResponse(
                    id=str(row["id"]),
                    source_id=str(row["source_id"]),
                    status=row["status"],
                    pages_crawled=row["pages_crawled"],
                    pages_total=row["pages_total"],
                    max_pages=row["max_pages"],
                    max_depth=row["max_depth"],
                    current_depth=row["current_depth"],
                    error_message=row["error_message"],
                    error_count=row["error_count"],
                    metadata=metadata,
                    started_at=row["started_at"].isoformat() if row["started_at"] else None,
                    completed_at=row["completed_at"].isoformat() if row["completed_at"] else None,
                    created_at=row["created_at"].isoformat(),
                    updated_at=row["updated_at"].isoformat(),
                )
            )

        logger.info(
            f"Listed {len(crawl_job_responses)} crawl jobs "
            f"(total: {total_count}, limit: {limit}, offset: {offset})"
        )

        return CrawlJobListResponse(
            crawl_jobs=crawl_job_responses,
            total_count=total_count,
            limit=limit,
            offset=offset,
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"List crawl jobs error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "Failed to list crawl jobs",
                "detail": str(e),
            },
        )


@router.get(
    "/{job_id}",
    response_model=CrawlJobResponse,
    responses={
        200: {"description": "Crawl job retrieved successfully"},
        404: {"model": ErrorResponse, "description": "Crawl job not found"},
        500: {"model": ErrorResponse, "description": "Server error"},
    },
)
async def get_crawl_job(
    job_id: str,
    db_pool: asyncpg.Pool = Depends(get_db_pool),
) -> CrawlJobResponse:
    """Get a single crawl job by ID with current status and progress.

    Args:
        job_id: UUID of the crawl job
        db_pool: Database pool (injected)

    Returns:
        CrawlJobResponse with job details

    Raises:
        HTTPException: 404 if not found, 500 for server errors
    """
    try:
        # Parse UUID
        try:
            job_uuid = UUID(job_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": "Invalid job ID",
                    "detail": f"'{job_id}' is not a valid UUID",
                },
            )

        # Get crawl job
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT
                    id, source_id, status, pages_crawled, pages_total,
                    max_pages, max_depth, current_depth, error_message,
                    error_count, metadata, started_at, completed_at,
                    created_at, updated_at
                FROM crawl_jobs
                WHERE id = $1
                """,
                job_uuid
            )

        if not row:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": "Crawl job not found",
                    "detail": f"No crawl job found with ID {job_id}",
                },
            )

        # Parse metadata if it's a string (asyncpg may return JSONB as string)
        metadata = row["metadata"]
        if isinstance(metadata, str):
            metadata = json.loads(metadata)

        return CrawlJobResponse(
            id=str(row["id"]),
            source_id=str(row["source_id"]),
            status=row["status"],
            pages_crawled=row["pages_crawled"],
            pages_total=row["pages_total"],
            max_pages=row["max_pages"],
            max_depth=row["max_depth"],
            current_depth=row["current_depth"],
            error_message=row["error_message"],
            error_count=row["error_count"],
            metadata=metadata,
            started_at=row["started_at"].isoformat() if row["started_at"] else None,
            completed_at=row["completed_at"].isoformat() if row["completed_at"] else None,
            created_at=row["created_at"].isoformat(),
            updated_at=row["updated_at"].isoformat(),
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Get crawl job error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "Failed to get crawl job",
                "detail": str(e),
            },
        )


@router.post(
    "/{job_id}/abort",
    response_model=MessageResponse,
    responses={
        200: {"description": "Crawl job aborted successfully"},
        404: {"model": ErrorResponse, "description": "Crawl job not found"},
        400: {"model": ErrorResponse, "description": "Job cannot be aborted (not running)"},
        500: {"model": ErrorResponse, "description": "Server error"},
    },
)
async def abort_crawl_job(
    job_id: str,
    db_pool: asyncpg.Pool = Depends(get_db_pool),
) -> MessageResponse:
    """Abort a running crawl job.

    Only jobs with status 'pending' or 'running' can be aborted.
    The job status will be set to 'cancelled'.

    Args:
        job_id: UUID of the crawl job to abort
        db_pool: Database pool (injected)

    Returns:
        MessageResponse with success confirmation

    Raises:
        HTTPException: 404 if not found, 400 if job cannot be aborted, 500 for server errors
    """
    try:
        # Parse UUID
        try:
            job_uuid = UUID(job_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": "Invalid job ID",
                    "detail": f"'{job_id}' is not a valid UUID",
                },
            )

        # Update job status to cancelled (only if pending or running)
        async with db_pool.acquire() as conn:
            # First check if job exists and is abortable
            job_row = await conn.fetchrow(
                "SELECT status FROM crawl_jobs WHERE id = $1",
                job_uuid
            )

            if not job_row:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "success": False,
                        "error": "Crawl job not found",
                        "detail": f"No crawl job found with ID {job_id}",
                    },
                )

            current_status = job_row["status"]

            if current_status not in ["pending", "running"]:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "success": False,
                        "error": "Cannot abort job",
                        "detail": f"Job status is '{current_status}'. Only 'pending' or 'running' jobs can be aborted.",
                        "suggestion": "Job may have already completed, failed, or been cancelled"
                    },
                )

            # Update status to cancelled
            await conn.fetchrow(
                """
                UPDATE crawl_jobs
                SET status = 'cancelled',
                    completed_at = NOW(),
                    updated_at = NOW()
                WHERE id = $1
                RETURNING id, status
                """,
                job_uuid
            )

        logger.info(
            f"Crawl job {job_id} aborted "
            f"(previous status: {current_status})"
        )

        # TODO (Task 3): Signal running crawler to stop
        # This will be implemented when integrating async crawl execution

        return MessageResponse(
            success=True,
            message=f"Crawl job {job_id} aborted successfully"
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Abort crawl job error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "Failed to abort crawl job",
                "detail": str(e),
            },
        )


@router.delete(
    "/{job_id}",
    response_model=MessageResponse,
    responses={
        200: {"description": "Crawl job deleted successfully"},
        404: {"model": ErrorResponse, "description": "Crawl job not found"},
        500: {"model": ErrorResponse, "description": "Server error"},
    },
)
async def delete_crawl_job(
    job_id: str,
    db_pool: asyncpg.Pool = Depends(get_db_pool),
) -> MessageResponse:
    """Delete a crawl job by ID.

    This removes the crawl job record from the database.
    Note: This does NOT delete the documents/chunks created by the crawl.
    To delete those, use DELETE /api/sources/{source_id} to remove the entire source.

    Args:
        job_id: UUID of the crawl job to delete
        db_pool: Database pool (injected)

    Returns:
        MessageResponse with success confirmation

    Raises:
        HTTPException: 404 if not found, 500 for server errors
    """
    try:
        # Parse UUID
        try:
            job_uuid = UUID(job_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": "Invalid job ID",
                    "detail": f"'{job_id}' is not a valid UUID",
                },
            )

        # Delete crawl job
        async with db_pool.acquire() as conn:
            # Check if job exists
            job_exists = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM crawl_jobs WHERE id = $1)",
                job_uuid
            )

            if not job_exists:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "success": False,
                        "error": "Crawl job not found",
                        "detail": f"No crawl job found with ID {job_id}",
                    },
                )

            # Delete the job
            await conn.execute(
                "DELETE FROM crawl_jobs WHERE id = $1",
                job_uuid
            )

        logger.info(f"Crawl job deleted: {job_id}")

        return MessageResponse(
            success=True,
            message=f"Crawl job {job_id} deleted successfully"
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Delete crawl job error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "Failed to delete crawl job",
                "detail": str(e),
            },
        )
