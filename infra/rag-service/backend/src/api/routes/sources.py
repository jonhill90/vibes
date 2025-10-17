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
from qdrant_client import AsyncQdrantClient

from src.api.dependencies import get_db_pool, get_qdrant_client
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
    qdrant_client: AsyncQdrantClient = Depends(get_qdrant_client),
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
        # Build metadata with title if provided
        metadata = request.metadata or {}
        if request.title:
            metadata["title"] = request.title

        # Create source (with qdrant_client for per-domain collection creation)
        source_service = SourceService(db_pool, qdrant_client=qdrant_client)
        success, result = await source_service.create_source(
            {
                "source_type": request.source_type,
                "enabled_collections": request.enabled_collections,
                "url": request.url,
                "status": "active",  # Changed from "pending" to "active" (multi-collection migration)
                "metadata": metadata,
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
        metadata = parse_metadata(source.get("metadata"))
        collection_names = parse_metadata(source.get("collection_names"))

        logger.info(
            f"Source created: {source['id']} "
            f"(type: {source['source_type']}, url: {source.get('url')}, "
            f"collections: {list(collection_names.keys()) if collection_names else []})"
        )

        return SourceResponse(
            id=str(source["id"]),
            source_type=source["source_type"],
            enabled_collections=source.get("enabled_collections", ["documents"]),
            collection_names=collection_names if collection_names else None,
            url=source.get("url"),
            title=metadata.get("title"),
            status=source["status"],
            metadata=metadata,
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
        source_responses = []
        for source in sources:
            metadata = parse_metadata(source.get("metadata"))
            collection_names = parse_metadata(source.get("collection_names"))
            source_responses.append(
                SourceResponse(
                    id=str(source["id"]),
                    source_type=source["source_type"],
                    enabled_collections=source.get("enabled_collections", ["documents"]),
                    collection_names=collection_names if collection_names else None,
                    url=source.get("url"),
                    title=metadata.get("title"),
                    status=source["status"],
                    metadata=metadata,
                    error_message=source.get("error_message"),
                    created_at=source["created_at"].isoformat(),
                    updated_at=source["updated_at"].isoformat(),
                )
            )

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
        metadata = parse_metadata(source.get("metadata"))
        collection_names = parse_metadata(source.get("collection_names"))

        return SourceResponse(
            id=str(source["id"]),
            source_type=source["source_type"],
            enabled_collections=source.get("enabled_collections", ["documents"]),
            collection_names=collection_names if collection_names else None,
            url=source.get("url"),
            title=metadata.get("title"),
            status=source["status"],
            metadata=metadata,
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
        if request.error_message is not None:
            updates["error_message"] = request.error_message

        # Handle title in metadata
        if request.title is not None or request.metadata is not None:
            # Get existing metadata if updating title
            if request.title is not None:
                # Fetch current source to merge metadata
                source_service_temp = SourceService(db_pool)
                success_temp, result_temp = await source_service_temp.get_source(src_uuid)
                current_metadata = parse_metadata(result_temp.get("source", {}).get("metadata")) if success_temp else {}

                # Merge with provided metadata or use existing
                metadata = request.metadata if request.metadata is not None else current_metadata
                metadata["title"] = request.title
                updates["metadata"] = metadata
            elif request.metadata is not None:
                updates["metadata"] = request.metadata

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
        metadata = parse_metadata(source.get("metadata"))
        collection_names = parse_metadata(source.get("collection_names"))

        logger.info(f"Source updated: {source_id}")

        return SourceResponse(
            id=str(source["id"]),
            source_type=source["source_type"],
            enabled_collections=source.get("enabled_collections", ["documents"]),
            collection_names=collection_names if collection_names else None,
            url=source.get("url"),
            title=metadata.get("title"),
            status=source["status"],
            metadata=metadata,
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
    qdrant_client: AsyncQdrantClient = Depends(get_qdrant_client),
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

        # Delete source (with qdrant_client for per-domain collection deletion)
        source_service = SourceService(db_pool, qdrant_client=qdrant_client)
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
