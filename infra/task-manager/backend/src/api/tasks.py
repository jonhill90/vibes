"""Task API Routes - FastAPI endpoints for task CRUD operations.

This module provides:
- RESTful endpoints for task management
- ETag support for list endpoint (304 Not Modified caching)
- Dependency injection for TaskService
- Query parameter filtering (project_id, status, assignee)
- Pagination support (page, per_page)
- Separate endpoint for atomic position updates

Critical Gotchas Addressed:
- Gotcha #1: All endpoints use async def (non-blocking)
- Gotcha #14: ETag headers added to list responses for HTTP caching
- Position updates use separate endpoint (not generic PATCH)

Pattern Source: prps/task_management_ui/planning/codebase-patterns.md
"""

import hashlib
import json
import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel

from ..config.database import get_pool
from ..models.task import TaskCreate, TaskResponse, TaskUpdate
from ..services.task_service import TaskService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks")


# Dependency injection for TaskService
async def get_task_service() -> TaskService:
    """FastAPI dependency to inject TaskService with database pool.

    Returns:
        TaskService: Initialized service with database pool

    Raises:
        RuntimeError: If database pool not initialized
    """
    pool = await get_pool()
    return TaskService(db_pool=pool)


# ETag utility functions
def generate_etag(data: dict[str, Any]) -> str:
    """Generate ETag from response data for HTTP caching.

    Args:
        data: Response dictionary to hash

    Returns:
        ETag string in quoted format (e.g., "a1b2c3d4")
    """
    json_str = json.dumps(data, sort_keys=True, default=str)
    hash_value = hashlib.md5(json_str.encode()).hexdigest()
    return f'"{hash_value}"'


def check_etag(request: Request, current_etag: str) -> bool:
    """Check if client's ETag matches current data.

    Args:
        request: FastAPI request object
        current_etag: Current ETag value to compare against

    Returns:
        True if client's ETag matches (data unchanged), False otherwise
    """
    client_etag = request.headers.get("If-None-Match")
    return client_etag == current_etag


# Pydantic model for position update request
class TaskPositionUpdate(BaseModel):
    """Request model for atomic position updates."""

    status: str
    position: int


# --- API Endpoints ---


@router.get("/", response_model=dict[str, Any])
async def list_tasks(
    request: Request,
    response: Response,
    project_id: str | None = None,
    status: str | None = None,
    assignee: str | None = None,
    page: int = 1,
    per_page: int = 50,
    service: TaskService = Depends(get_task_service),
) -> dict[str, Any]:
    """List tasks with optional filters and pagination.

    Query Parameters:
        project_id: Filter by project UUID
        status: Filter by task status (todo, doing, review, done)
        assignee: Filter by assignee username
        page: Page number (1-indexed, default: 1)
        per_page: Items per page (default: 50)

    Returns:
        {
            "tasks": [...],
            "total_count": int,
            "page": int,
            "per_page": int
        }

    HTTP Headers:
        ETag: Content hash for caching
        Cache-Control: no-cache, must-revalidate

    Response Codes:
        200: Success
        304: Not Modified (ETag match)
        400: Invalid filters or parameters
    """
    # Build filters dict
    filters = {}
    if project_id:
        filters["project_id"] = project_id
    if status:
        filters["status"] = status
    if assignee:
        filters["assignee"] = assignee

    # Call service layer
    success, result = await service.list_tasks(
        filters=filters,
        page=page,
        per_page=per_page,
        exclude_large_fields=True,  # Optimize for API - truncate long descriptions
    )

    if not success:
        error_msg = result.get("error", "Unknown error")
        logger.warning(f"Failed to list tasks: {error_msg}")
        raise HTTPException(status_code=400, detail=error_msg)

    # ETag support for HTTP caching
    etag = generate_etag(result)

    # Check if client's cached version is still valid
    if check_etag(request, etag):
        logger.info("ETag match - returning 304 Not Modified")
        return Response(status_code=304)

    # Set cache headers
    response.headers["ETag"] = etag
    response.headers["Cache-Control"] = "no-cache, must-revalidate"

    logger.info(
        f"Listed {len(result['tasks'])} tasks "
        f"(page {page}, total: {result['total_count']})"
    )

    return result


@router.get("/{task_id}", response_model=dict[str, Any])
async def get_task(
    task_id: str,
    service: TaskService = Depends(get_task_service),
) -> dict[str, Any]:
    """Get a single task by ID.

    Path Parameters:
        task_id: UUID of the task

    Returns:
        {"task": {...}}

    Response Codes:
        200: Success
        404: Task not found
        400: Invalid task_id or database error
    """
    success, result = await service.get_task(task_id=task_id)

    if not success:
        error_msg = result.get("error", "Unknown error")

        # Check if it's a not-found error
        if "not found" in error_msg.lower():
            logger.warning(f"Task {task_id} not found")
            raise HTTPException(status_code=404, detail=error_msg)

        logger.error(f"Failed to get task {task_id}: {error_msg}")
        raise HTTPException(status_code=400, detail=error_msg)

    logger.info(f"Retrieved task {task_id}")
    return result


@router.post("/", response_model=dict[str, Any], status_code=201)
async def create_task(
    data: TaskCreate,
    service: TaskService = Depends(get_task_service),
) -> dict[str, Any]:
    """Create a new task.

    Request Body:
        TaskCreate model with:
        - title (required, 1-500 chars)
        - description (optional)
        - status (default: "todo")
        - assignee (default: "User")
        - priority (default: "medium")
        - position (default: 0)
        - project_id (optional)

    Returns:
        {
            "task": {...},
            "message": "Task created successfully"
        }

    Response Codes:
        201: Created
        400: Validation error or database error
    """
    success, result = await service.create_task(data=data)

    if not success:
        error_msg = result.get("error", "Unknown error")
        logger.error(f"Failed to create task: {error_msg}")
        raise HTTPException(status_code=400, detail=error_msg)

    logger.info(f"Created task {result['task']['id']}: {data.title}")
    return result


@router.patch("/{task_id}", response_model=dict[str, Any])
async def update_task(
    task_id: str,
    data: TaskUpdate,
    service: TaskService = Depends(get_task_service),
) -> dict[str, Any]:
    """Update task fields (excluding position - use PATCH /tasks/{id}/position).

    Path Parameters:
        task_id: UUID of the task

    Request Body:
        TaskUpdate model with optional fields:
        - title
        - description
        - status
        - assignee
        - priority
        - position (not recommended, use position endpoint instead)

    Returns:
        {
            "task": {...},
            "message": "Task updated successfully"
        }

    Response Codes:
        200: Success
        404: Task not found
        400: Validation error or database error
    """
    success, result = await service.update_task(task_id=task_id, data=data)

    if not success:
        error_msg = result.get("error", "Unknown error")

        # Check if it's a not-found error
        if "not found" in error_msg.lower():
            logger.warning(f"Task {task_id} not found for update")
            raise HTTPException(status_code=404, detail=error_msg)

        logger.error(f"Failed to update task {task_id}: {error_msg}")
        raise HTTPException(status_code=400, detail=error_msg)

    logger.info(f"Updated task {task_id}")
    return result


@router.patch("/{task_id}/position", response_model=dict[str, Any])
async def update_task_position(
    task_id: str,
    data: TaskPositionUpdate,
    service: TaskService = Depends(get_task_service),
) -> dict[str, Any]:
    """Update task position with atomic reordering.

    CRITICAL: This endpoint handles concurrent position updates safely using
    database transactions and row locking. DO NOT use the generic PATCH endpoint
    for position updates - it doesn't have the same atomicity guarantees.

    Path Parameters:
        task_id: UUID of the task to move

    Request Body:
        {
            "status": "todo" | "doing" | "review" | "done",
            "position": int (0-indexed position in target column)
        }

    Returns:
        {
            "task": {...},
            "message": "Task position updated successfully"
        }

    Response Codes:
        200: Success
        404: Task not found
        400: Validation error or database error

    Implementation Notes:
        - Uses SELECT ... FOR UPDATE to lock affected rows
        - Locks rows in consistent order (ORDER BY id) to prevent deadlocks
        - Batch updates positions atomically within transaction
        - See TaskService.update_task_position for full implementation
    """
    success, result = await service.update_task_position(
        task_id=task_id,
        new_status=data.status,
        new_position=data.position,
    )

    if not success:
        error_msg = result.get("error", "Unknown error")

        # Check if it's a not-found error
        if "not found" in error_msg.lower():
            logger.warning(f"Task {task_id} not found for position update")
            raise HTTPException(status_code=404, detail=error_msg)

        logger.error(f"Failed to update position for task {task_id}: {error_msg}")
        raise HTTPException(status_code=400, detail=error_msg)

    logger.info(
        f"Updated position for task {task_id}: "
        f"{data.status} position {data.position}"
    )
    return result


@router.delete("/{task_id}", response_model=dict[str, Any])
async def delete_task(
    task_id: str,
    service: TaskService = Depends(get_task_service),
) -> dict[str, Any]:
    """Delete a task by ID.

    Path Parameters:
        task_id: UUID of the task to delete

    Returns:
        {"message": "Task {task_id} deleted successfully"}

    Response Codes:
        200: Success
        404: Task not found
        400: Database error
    """
    success, result = await service.delete_task(task_id=task_id)

    if not success:
        error_msg = result.get("error", "Unknown error")

        # Check if it's a not-found error
        if "not found" in error_msg.lower():
            logger.warning(f"Task {task_id} not found for deletion")
            raise HTTPException(status_code=404, detail=error_msg)

        logger.error(f"Failed to delete task {task_id}: {error_msg}")
        raise HTTPException(status_code=400, detail=error_msg)

    logger.info(f"Deleted task {task_id}")
    return result
