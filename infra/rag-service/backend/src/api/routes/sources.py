"""Source CRUD API routes.

This module provides REST API endpoints for source management with:
- Source creation with validation
- Source listing with filters and pagination
- Source retrieval, update, and deletion
- Integration with document cascade deletion

Critical Gotchas Addressed:
- Gotcha #2: Inject db_pool, services acquire connections
- Gotcha #3: Use $1, $2 placeholders in SQL
- CASCADE deletion: Deleting source deletes all documents

Pattern: Example 05 (FastAPI route pattern)
Reference: infra/task-manager/backend/src/api/routes/
"""

import json
import logging
from typing import Optional
from uuid import UUID

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.dependencies import get_db_pool
from src.models.requests import SourceCreateRequest, SourceUpdateRequest
from src.models.responses import (
    SourceResponse,
    SourceListResponse,
    ErrorResponse,
    MessageResponse,
)
from src.services.source_service import SourceService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/sources", tags=["sources"])


def parse_metadata(metadata):
    """Parse metadata field from database (handles JSONB as string)."""
    if metadata is None:
        return {}
    if isinstance(metadata, dict):
        return metadata
    if isinstance(metadata, str):
        try:
            return json.loads(metadata) if metadata else {}
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse metadata JSON: {metadata}")
            return {}
    return {}


@router.post(
    "",
    response_model=SourceResponse,
    status_code=201,
    responses={
        201: {"description": "Source created successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Server error"},
    },
)
async def create_source(
    request: SourceCreateRequest,
    db_pool: asyncpg.Pool = Depends(get_db_pool),
) -> SourceResponse:
    """Create a new source.

    Sources represent ingestion origins:
    - "upload": Manual file uploads
    - "crawl": Web crawling jobs
    - "api": External API integrations

    Args:
        request: SourceCreateRequest with source data
        db_pool: Database pool (injected)

    Returns:
        SourceResponse with created source data

    Raises:
        HTTPException: 400 for validation errors, 500 for server errors
    """
    try:
        # Create source
        source_service = SourceService(db_pool)
        success, result = await source_service.create_source(
            {
                "source_type": request.source_type,
                "url": request.url,
                "status": "pending",
                "metadata": request.metadata or {},
            }
        )

        if not success:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": "Failed to create source",
                    "detail": result.get("error", "Unknown error"),
                },
            )

        source = result["source"]

        logger.info(
            f"Source created: {source['id']} "
            f"(type: {source['source_type']}, url: {source.get('url')})"
        )

        return SourceResponse(
            id=str(source["id"]),
            source_type=source["source_type"],
            url=source.get("url"),
            status=source["status"],
            metadata=parse_metadata(source.get("metadata")),
            error_message=source.get("error_message"),
            created_at=source["created_at"].isoformat(),
            updated_at=source["updated_at"].isoformat(),
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Create source error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "Failed to create source",
                "detail": str(e),
            },
        )


@router.get(
    "",
    response_model=SourceListResponse,
    responses={
        200: {"description": "Sources retrieved successfully"},
        500: {"model": ErrorResponse, "description": "Server error"},
    },
)
async def list_sources(
    source_type: Optional[str] = Query(None, description="Filter by source type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100, description="Maximum items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    db_pool: asyncpg.Pool = Depends(get_db_pool),
) -> SourceListResponse:
    """List sources with filters and pagination.

    Args:
        source_type: Optional filter by source type (upload, crawl, api)
        status: Optional filter by status (pending, processing, completed, failed)
        limit: Maximum items to return (1-100)
        offset: Number of items to skip for pagination
        db_pool: Database pool (injected)

    Returns:
        SourceListResponse with paginated results

    Raises:
        HTTPException: 500 for server errors
    """
    try:
        # List sources
        source_service = SourceService(db_pool)
        success, result = await source_service.list_sources(
            source_type=source_type,
            status=status,
            limit=limit,
            offset=offset,
            exclude_large_fields=False,
        )

        if not success:
            raise HTTPException(
                status_code=500,
                detail={
                    "success": False,
                    "error": "Failed to list sources",
                    "detail": result.get("error", "Unknown error"),
                },
            )

        sources = result["sources"]
        total_count = result["total_count"]

        # Convert sources to response model
        source_responses = [
            SourceResponse(
                id=str(source["id"]),
                source_type=source["source_type"],
                url=source.get("url"),
                status=source["status"],
                metadata=parse_metadata(source.get("metadata")),
                error_message=source.get("error_message"),
                created_at=source["created_at"].isoformat(),
                updated_at=source["updated_at"].isoformat(),
            )
            for source in sources
        ]

        return SourceListResponse(
            sources=source_responses,
            total_count=total_count,
            limit=limit,
            offset=offset,
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"List sources error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "Failed to list sources",
                "detail": str(e),
            },
        )


@router.get(
    "/{source_id}",
    response_model=SourceResponse,
    responses={
        200: {"description": "Source retrieved successfully"},
        404: {"model": ErrorResponse, "description": "Source not found"},
        500: {"model": ErrorResponse, "description": "Server error"},
    },
)
async def get_source(
    source_id: str,
    db_pool: asyncpg.Pool = Depends(get_db_pool),
) -> SourceResponse:
    """Get a single source by ID.

    Args:
        source_id: UUID of the source
        db_pool: Database pool (injected)

    Returns:
        SourceResponse with source data

    Raises:
        HTTPException: 404 if not found, 500 for server errors
    """
    try:
        # Parse UUID
        try:
            src_uuid = UUID(source_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": "Invalid source ID",
                    "detail": f"'{source_id}' is not a valid UUID",
                },
            )

        # Get source
        source_service = SourceService(db_pool)
        success, result = await source_service.get_source(src_uuid)

        if not success:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": "Source not found",
                    "detail": result.get("error", "Unknown error"),
                },
            )

        source = result["source"]

        return SourceResponse(
            id=str(source["id"]),
            source_type=source["source_type"],
            url=source.get("url"),
            status=source["status"],
            metadata=parse_metadata(source.get("metadata")),
            error_message=source.get("error_message"),
            created_at=source["created_at"].isoformat(),
            updated_at=source["updated_at"].isoformat(),
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Get source error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "Failed to get source",
                "detail": str(e),
            },
        )


@router.put(
    "/{source_id}",
    response_model=SourceResponse,
    responses={
        200: {"description": "Source updated successfully"},
        404: {"model": ErrorResponse, "description": "Source not found"},
        500: {"model": ErrorResponse, "description": "Server error"},
    },
)
async def update_source(
    source_id: str,
    request: SourceUpdateRequest,
    db_pool: asyncpg.Pool = Depends(get_db_pool),
) -> SourceResponse:
    """Update a source with partial updates.

    All fields are optional - only provided fields will be updated.

    Args:
        source_id: UUID of the source
        request: SourceUpdateRequest with fields to update
        db_pool: Database pool (injected)

    Returns:
        SourceResponse with updated source data

    Raises:
        HTTPException: 404 if not found, 500 for server errors
    """
    try:
        # Parse UUID
        try:
            src_uuid = UUID(source_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": "Invalid source ID",
                    "detail": f"'{source_id}' is not a valid UUID",
                },
            )

        # Build updates dict (exclude None values)
        updates = {}
        if request.source_type is not None:
            updates["source_type"] = request.source_type
        if request.url is not None:
            updates["url"] = request.url
        if request.status is not None:
            updates["status"] = request.status
        if request.metadata is not None:
            updates["metadata"] = request.metadata
        if request.error_message is not None:
            updates["error_message"] = request.error_message

        if not updates:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": "No fields to update",
                    "detail": "At least one field must be provided for update",
                },
            )

        # Update source
        source_service = SourceService(db_pool)
        success, result = await source_service.update_source(src_uuid, updates)

        if not success:
            # Check if 404 or 500
            error_message = result.get("error", "")
            if "not found" in error_message.lower():
                status_code = 404
            else:
                status_code = 500

            raise HTTPException(
                status_code=status_code,
                detail={
                    "success": False,
                    "error": "Failed to update source",
                    "detail": error_message,
                },
            )

        source = result["source"]

        logger.info(f"Source updated: {source_id}")

        return SourceResponse(
            id=str(source["id"]),
            source_type=source["source_type"],
            url=source.get("url"),
            status=source["status"],
            metadata=parse_metadata(source.get("metadata")),
            error_message=source.get("error_message"),
            created_at=source["created_at"].isoformat(),
            updated_at=source["updated_at"].isoformat(),
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Update source error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "Failed to update source",
                "detail": str(e),
            },
        )


@router.delete(
    "/{source_id}",
    response_model=MessageResponse,
    responses={
        200: {"description": "Source deleted successfully"},
        404: {"model": ErrorResponse, "description": "Source not found"},
        500: {"model": ErrorResponse, "description": "Server error"},
    },
)
async def delete_source(
    source_id: str,
    db_pool: asyncpg.Pool = Depends(get_db_pool),
) -> MessageResponse:
    """Delete a source by ID.

    WARNING: This will CASCADE delete:
    - All documents associated with this source
    - All chunks from those documents
    - All crawl jobs for this source

    Args:
        source_id: UUID of the source
        db_pool: Database pool (injected)

    Returns:
        MessageResponse with success message

    Raises:
        HTTPException: 404 if not found, 500 for server errors
    """
    try:
        # Parse UUID
        try:
            src_uuid = UUID(source_id)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": "Invalid source ID",
                    "detail": f"'{source_id}' is not a valid UUID",
                },
            )

        # Delete source
        source_service = SourceService(db_pool)
        success, result = await source_service.delete_source(src_uuid)

        if not success:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": "Source not found",
                    "detail": result.get("error", "Unknown error"),
                },
            )

        logger.info(f"Source deleted: {source_id}")

        return MessageResponse(
            success=True,
            message=f"Source {source_id} and all associated documents deleted successfully",
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Delete source error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "Failed to delete source",
                "detail": str(e),
            },
        )
