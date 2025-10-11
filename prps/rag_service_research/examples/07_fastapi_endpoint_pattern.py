# Source: infra/task-manager/backend/src/api_routes/
# Pattern: FastAPI Endpoint Structure with Service Layer
# Extracted: 2025-10-11
# Relevance: 9/10 - Standard API endpoint pattern

"""
PATTERN: FastAPI Endpoint with Service Layer

This demonstrates the standard pattern for FastAPI endpoints:
1. Route definition with HTTP method and path
2. Request validation with Pydantic models
3. Service layer delegation
4. Consistent error handling
5. Proper HTTP status codes

Architecture: API Route → Service → Database
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import Any
import logging

from ..services.task_service import TaskService
from ..models.task import TaskCreate, TaskUpdate, TaskResponse
from ..config.database import get_pool

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


# PATTERN: Dependency injection for service initialization
async def get_task_service() -> TaskService:
    """Dependency to get TaskService instance with database pool."""
    pool = await get_pool()
    return TaskService(pool)


@router.get("/", response_model=dict[str, Any])
async def list_tasks(
    project_id: str | None = None,
    status: str | None = None,
    assignee: str | None = None,
    page: int = 1,
    per_page: int = 50,
    exclude_large_fields: bool = False,
    task_service: TaskService = Depends(get_task_service),
):
    """
    List tasks with optional filters and pagination.

    PATTERN: Query parameters for filtering and pagination
    - Optional filters (project_id, status, assignee)
    - Pagination (page, per_page)
    - Performance optimization (exclude_large_fields)

    Args:
        project_id: Filter by project UUID
        status: Filter by status (todo, doing, review, done)
        assignee: Filter by assignee name
        page: Page number (1-indexed)
        per_page: Items per page
        exclude_large_fields: If True, truncate long descriptions
        task_service: Injected TaskService dependency

    Returns:
        JSON response with tasks and metadata
    """
    try:
        # Build filters dict from query parameters
        filters = {}
        if project_id:
            filters["project_id"] = project_id
        if status:
            filters["status"] = status
        if assignee:
            filters["assignee"] = assignee

        # PATTERN: Delegate to service layer
        success, result = await task_service.list_tasks(
            filters=filters,
            page=page,
            per_page=per_page,
            exclude_large_fields=exclude_large_fields,
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to list tasks"),
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in list_tasks endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    task_service: TaskService = Depends(get_task_service),
):
    """
    Get a single task by ID.

    PATTERN: Path parameter for resource ID
    - Returns 404 if not found
    - Returns task data if found

    Args:
        task_id: Task UUID
        task_service: Injected TaskService dependency

    Returns:
        Task data
    """
    try:
        success, result = await task_service.get_task(task_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get("error", "Task not found"),
            )

        return result.get("task")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_task endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    task_service: TaskService = Depends(get_task_service),
):
    """
    Create a new task.

    PATTERN: POST with Pydantic model for validation
    - Request body validated by TaskCreate model
    - Returns 201 Created on success
    - Returns created task with server-generated fields

    Args:
        task_data: Task creation data (validated by Pydantic)
        task_service: Injected TaskService dependency

    Returns:
        Created task data
    """
    try:
        success, result = await task_service.create_task(task_data)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to create task"),
            )

        return result.get("task")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in create_task endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_data: TaskUpdate,
    task_service: TaskService = Depends(get_task_service),
):
    """
    Update a task.

    PATTERN: PUT with path parameter and request body
    - Partial updates supported (only provided fields updated)
    - Returns 404 if task not found
    - Returns updated task data

    Args:
        task_id: Task UUID
        task_data: Task update data (validated by Pydantic)
        task_service: Injected TaskService dependency

    Returns:
        Updated task data
    """
    try:
        success, result = await task_service.update_task(task_id, task_data)

        if not success:
            error = result.get("error", "Failed to update task")
            if "not found" in error.lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=error,
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error,
            )

        return result.get("task")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in update_task endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    task_service: TaskService = Depends(get_task_service),
):
    """
    Delete a task.

    PATTERN: DELETE with path parameter
    - Returns 204 No Content on success
    - Returns 404 if task not found

    Args:
        task_id: Task UUID
        task_service: Injected TaskService dependency

    Returns:
        None (204 No Content)
    """
    try:
        success, result = await task_service.delete_task(task_id)

        if not success:
            error = result.get("error", "Failed to delete task")
            if "not found" in error.lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=error,
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error,
            )

        # 204 No Content - no response body
        return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in delete_task endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
