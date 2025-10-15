# Source: infra/task-manager/backend/src/api/routes/*.py patterns
# Pattern: FastAPI route with Pydantic models, validation, and error handling
# Extracted: 2025-10-14
# Relevance: 8/10 - Standard pattern for Task 4 (REST API Endpoints)

"""
WHAT THIS DEMONSTRATES:
- Pydantic request/response models
- FastAPI route with dependency injection
- Error handling with structured responses
- Pagination support
- Request validation
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile
from pydantic import BaseModel, Field, validator
import asyncpg
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


# ==============================================================================
# PATTERN 1: Pydantic Request/Response Models
# ==============================================================================

class DocumentUploadRequest(BaseModel):
    """Request model for document upload.

    Pydantic automatically validates:
    - Required fields are present
    - Field types are correct
    - Custom validators pass
    """
    source_id: str = Field(..., description="Source UUID where document belongs")
    filename: str = Field(..., min_length=1, max_length=255, description="Document filename")
    metadata: Optional[dict] = Field(default=None, description="Optional metadata")

    @validator("filename")
    def validate_filename(cls, v):
        """Validate filename has allowed extension."""
        allowed_extensions = [".pdf", ".docx", ".txt", ".md", ".html"]
        if not any(v.lower().endswith(ext) for ext in allowed_extensions):
            raise ValueError(
                f"Invalid file extension. Allowed: {', '.join(allowed_extensions)}"
            )
        return v


class DocumentResponse(BaseModel):
    """Response model for document operations."""
    id: str = Field(..., description="Document UUID")
    source_id: str
    filename: str
    status: str = Field(..., description="processing | completed | failed")
    created_at: str
    metadata: Optional[dict] = None


class DocumentListResponse(BaseModel):
    """Response model for paginated document list."""
    documents: List[DocumentResponse]
    total_count: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool


class SearchRequest(BaseModel):
    """Request model for semantic search."""
    query: str = Field(..., min_length=1, max_length=1000, description="Search query")
    limit: int = Field(default=10, ge=1, le=100, description="Max results (1-100)")
    filters: Optional[dict] = Field(default=None, description="Metadata filters")
    search_type: str = Field(default="hybrid", description="vector | hybrid")

    @validator("search_type")
    def validate_search_type(cls, v):
        """Validate search type is allowed."""
        if v not in ["vector", "hybrid"]:
            raise ValueError("search_type must be 'vector' or 'hybrid'")
        return v


class SearchResultItem(BaseModel):
    """Single search result."""
    chunk_id: str
    text: str
    score: float = Field(..., ge=0.0, le=1.0, description="Relevance score (0-1)")
    match_type: Optional[str] = Field(None, description="vector | text | both")
    metadata: dict


class SearchResponse(BaseModel):
    """Response model for search results."""
    results: List[SearchResultItem]
    query: str
    search_type: str
    count: int
    latency_ms: float


class ErrorResponse(BaseModel):
    """Structured error response."""
    success: bool = False
    error: str
    detail: Optional[str] = None
    suggestion: Optional[str] = None


# ==============================================================================
# PATTERN 2: Dependency Injection for Database Pool
# ==============================================================================

from fastapi import Request

async def get_db_pool(request: Request) -> asyncpg.Pool:
    """Dependency that returns database pool from app state.

    CRITICAL (Gotcha #2): Return POOL, not connection.
    Services will acquire connections as needed using async with pool.acquire().
    """
    return request.app.state.db_pool


# ==============================================================================
# PATTERN 3: Document Upload Route with File Handling
# ==============================================================================

@router.post(
    "/documents",
    response_model=DocumentResponse,
    status_code=201,
    responses={
        201: {"description": "Document uploaded successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        413: {"model": ErrorResponse, "description": "File too large"},
        500: {"model": ErrorResponse, "description": "Server error"},
    }
)
async def upload_document(
    file: UploadFile = File(..., description="Document file to upload"),
    source_id: str = Query(..., description="Source UUID"),
    db_pool: asyncpg.Pool = Depends(get_db_pool),
) -> DocumentResponse:
    """Upload document for ingestion.

    Process:
    1. Validate file type and size
    2. Save file to temporary location
    3. Create document record in database
    4. Trigger async ingestion pipeline
    5. Return document metadata

    Args:
        file: Uploaded file (multipart/form-data)
        source_id: UUID of the source
        db_pool: Database pool (injected)

    Returns:
        DocumentResponse with document metadata

    Raises:
        HTTPException: 400 for validation errors, 413 for file too large, 500 for server errors
    """
    try:
        # Validate file size (10MB max)
        MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
        file_content = await file.read()

        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail={
                    "success": False,
                    "error": "File too large",
                    "detail": f"File size {len(file_content)} bytes exceeds max {MAX_FILE_SIZE} bytes",
                    "suggestion": "Compress file or split into smaller documents"
                }
            )

        # Validate file type
        allowed_extensions = [".pdf", ".docx", ".txt", ".md", ".html"]
        if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": "Invalid file type",
                    "detail": f"File extension not allowed: {file.filename}",
                    "suggestion": f"Upload one of: {', '.join(allowed_extensions)}"
                }
            )

        # Create document record
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO documents (source_id, filename, status, file_size)
                VALUES ($1, $2, $3, $4)
                RETURNING id, source_id, filename, status, created_at
                """,
                source_id,
                file.filename,
                "processing",
                len(file_content)
            )

        # TODO: Trigger async ingestion pipeline
        # await ingestion_service.process_document(row["id"], file_content)

        # Return response
        return DocumentResponse(
            id=str(row["id"]),
            source_id=str(row["source_id"]),
            filename=row["filename"],
            status=row["status"],
            created_at=row["created_at"].isoformat(),
        )

    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is

    except Exception as e:
        logger.error(f"Document upload error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "Failed to upload document",
                "detail": str(e),
                "suggestion": "Check server logs for details"
            }
        )


# ==============================================================================
# PATTERN 4: List Route with Pagination
# ==============================================================================

@router.get(
    "/documents",
    response_model=DocumentListResponse,
    responses={
        200: {"description": "Documents retrieved successfully"},
        500: {"model": ErrorResponse, "description": "Server error"},
    }
)
async def list_documents(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page (1-100)"),
    status: Optional[str] = Query(None, description="Filter by status"),
    source_id: Optional[str] = Query(None, description="Filter by source ID"),
    db_pool: asyncpg.Pool = Depends(get_db_pool),
) -> DocumentListResponse:
    """List documents with pagination and filters.

    Args:
        page: Page number (1-indexed)
        per_page: Items per page (max 100)
        status: Optional status filter (processing | completed | failed)
        source_id: Optional source ID filter
        db_pool: Database pool (injected)

    Returns:
        DocumentListResponse with paginated results
    """
    try:
        # Calculate offset
        offset = (page - 1) * per_page

        # Build WHERE clause
        where_clauses = []
        params = []
        param_idx = 1

        if status:
            where_clauses.append(f"status = ${param_idx}")
            params.append(status)
            param_idx += 1

        if source_id:
            where_clauses.append(f"source_id = ${param_idx}")
            params.append(source_id)
            param_idx += 1

        where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

        # Get total count
        async with db_pool.acquire() as conn:
            total_count = await conn.fetchval(
                f"SELECT COUNT(*) FROM documents {where_clause}",
                *params
            )

            # Get paginated results
            rows = await conn.fetch(
                f"""
                SELECT id, source_id, filename, status, created_at
                FROM documents
                {where_clause}
                ORDER BY created_at DESC
                LIMIT ${param_idx} OFFSET ${param_idx + 1}
                """,
                *params, per_page, offset
            )

        # Format response
        documents = [
            DocumentResponse(
                id=str(row["id"]),
                source_id=str(row["source_id"]),
                filename=row["filename"],
                status=row["status"],
                created_at=row["created_at"].isoformat(),
            )
            for row in rows
        ]

        return DocumentListResponse(
            documents=documents,
            total_count=total_count,
            page=page,
            per_page=per_page,
            has_next=offset + per_page < total_count,
            has_prev=page > 1,
        )

    except Exception as e:
        logger.error(f"List documents error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "Failed to list documents",
                "detail": str(e)
            }
        )


# ==============================================================================
# PATTERN 5: Search Route with Request Body
# ==============================================================================

@router.post(
    "/search",
    response_model=SearchResponse,
    responses={
        200: {"description": "Search completed successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Server error"},
    }
)
async def search_documents(
    request: SearchRequest,
    db_pool: asyncpg.Pool = Depends(get_db_pool),
) -> SearchResponse:
    """Semantic search across documents.

    Args:
        request: SearchRequest with query and filters
        db_pool: Database pool (injected)

    Returns:
        SearchResponse with ranked results
    """
    import time

    try:
        start_time = time.time()

        # TODO: Implement actual search logic
        # results = await rag_service.search(
        #     query=request.query,
        #     limit=request.limit,
        #     search_type=request.search_type,
        #     filters=request.filters
        # )

        # Placeholder results
        results = []

        latency_ms = (time.time() - start_time) * 1000

        return SearchResponse(
            results=results,
            query=request.query,
            search_type=request.search_type,
            count=len(results),
            latency_ms=round(latency_ms, 2)
        )

    except ValueError as e:
        # Validation errors
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": "Invalid search request",
                "detail": str(e)
            }
        )

    except Exception as e:
        logger.error(f"Search error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "Search failed",
                "detail": str(e)
            }
        )


# ==============================================================================
# KEY TAKEAWAYS
# ==============================================================================

# ✅ DO THIS:
# 1. Use Pydantic models for request/response validation
# 2. Add custom validators for complex validation logic
# 3. Use dependency injection for database pool
# 4. Return structured error responses (ErrorResponse model)
# 5. Add response_model and status_code to routes
# 6. Document routes with OpenAPI responses dict
# 7. Use Query/Body/File for parameter documentation
# 8. Log errors before raising HTTPException

# ❌ DON'T DO THIS:
# 1. Return raw dicts (use Pydantic models)
# 2. Skip validation (Pydantic does it automatically)
# 3. Return database connections (return pool, acquire in route)
# 4. Return unstructured error strings
# 5. Skip OpenAPI documentation
# 6. Forget to log errors before raising HTTPException
