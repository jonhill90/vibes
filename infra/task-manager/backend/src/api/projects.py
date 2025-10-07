"""FastAPI routes for project CRUD operations.

This module implements RESTful API endpoints for project management.

KEY PATTERNS IMPLEMENTED:
1. APIRouter with prefix and tags for OpenAPI organization
2. Dependency injection for ProjectService
3. Pydantic response_model for type safety and OpenAPI docs
4. Async endpoint handlers (Gotcha #1)
5. HTTPException for error responses
6. Pagination support for list endpoints

CRITICAL GOTCHAS ADDRESSED:
- Gotcha #1: Uses async def for endpoints calling async services
- HTTPException with status codes for proper error handling
- response_model on all endpoints for OpenAPI documentation
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from src.config.database import get_pool
from src.models.project import ProjectCreate, ProjectResponse, ProjectUpdate
from src.services.project_service import ProjectService

logger = logging.getLogger(__name__)

# Create router with prefix and tags for OpenAPI
router = APIRouter(
    prefix="/projects",
    tags=["projects"],
)


# Dependency injection for ProjectService
async def get_project_service() -> ProjectService:
    """FastAPI dependency to inject ProjectService.

    Returns:
        ProjectService: Initialized service with database pool

    Raises:
        HTTPException: If database pool is not initialized
    """
    try:
        db_pool = await get_pool()
        return ProjectService(db_pool)
    except RuntimeError as e:
        logger.error(f"Failed to get database pool: {e}")
        raise HTTPException(
            status_code=500,
            detail="Database connection not available"
        )


# Response models
class ProjectListResponse(BaseModel):
    """Response model for project list endpoint."""

    projects: list[ProjectResponse]
    total_count: int
    page: int
    per_page: int


class ProjectDetailResponse(BaseModel):
    """Response model for single project endpoint."""

    project: ProjectResponse


class ProjectCreateResponse(BaseModel):
    """Response model for project creation endpoint."""

    project: ProjectResponse


class ProjectUpdateResponse(BaseModel):
    """Response model for project update endpoint."""

    project: ProjectResponse
    message: str


class ProjectDeleteResponse(BaseModel):
    """Response model for project deletion endpoint."""

    message: str


class ErrorResponse(BaseModel):
    """Response model for error responses."""

    error: str


@router.get(
    "",
    response_model=ProjectListResponse,
    summary="List all projects",
    description="Retrieve a paginated list of all projects. Supports pagination via page and per_page query parameters.",
    responses={
        200: {"description": "Successfully retrieved project list"},
        400: {"model": ErrorResponse, "description": "Invalid pagination parameters"},
        500: {"model": ErrorResponse, "description": "Database error"},
    }
)
async def list_projects(
    page: Annotated[int, Query(ge=1, description="Page number (1-indexed)")] = 1,
    per_page: Annotated[int, Query(ge=1, le=100, description="Items per page (max 100)")] = 10,
    project_service: ProjectService = Depends(get_project_service),
):
    """List all projects with pagination.

    Args:
        page: Page number (1-indexed, default: 1)
        per_page: Number of items per page (1-100, default: 10)
        project_service: Injected ProjectService instance

    Returns:
        ProjectListResponse: List of projects with pagination metadata

    Raises:
        HTTPException: 400 for invalid parameters, 500 for database errors
    """
    # Gotcha #1: Using async def for async service calls
    success, result = await project_service.list_projects(page=page, per_page=per_page)

    if not success:
        error_msg = result.get("error", "Unknown error occurred")
        logger.warning(f"Failed to list projects: {error_msg}")
        raise HTTPException(status_code=400, detail=error_msg)

    # Convert dict response to ProjectResponse models
    projects = [ProjectResponse(**project) for project in result["projects"]]

    return ProjectListResponse(
        projects=projects,
        total_count=result["total_count"],
        page=result["page"],
        per_page=result["per_page"],
    )


@router.get(
    "/{project_id}",
    response_model=ProjectDetailResponse,
    summary="Get a single project",
    description="Retrieve details for a specific project by its ID.",
    responses={
        200: {"description": "Successfully retrieved project"},
        404: {"model": ErrorResponse, "description": "Project not found"},
        500: {"model": ErrorResponse, "description": "Database error"},
    }
)
async def get_project(
    project_id: str,
    project_service: ProjectService = Depends(get_project_service),
):
    """Get a single project by ID.

    Args:
        project_id: UUID of the project to retrieve
        project_service: Injected ProjectService instance

    Returns:
        ProjectDetailResponse: Project details

    Raises:
        HTTPException: 404 if project not found, 500 for database errors
    """
    # Gotcha #1: Using async def for async service calls
    success, result = await project_service.get_project(project_id)

    if not success:
        error_msg = result.get("error", "Unknown error occurred")
        logger.warning(f"Failed to get project {project_id}: {error_msg}")

        # Determine appropriate status code
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=error_msg)
        else:
            raise HTTPException(status_code=500, detail=error_msg)

    return ProjectDetailResponse(
        project=ProjectResponse(**result["project"])
    )


@router.post(
    "",
    response_model=ProjectCreateResponse,
    status_code=201,
    summary="Create a new project",
    description="Create a new project with the provided name and optional description.",
    responses={
        201: {"description": "Project created successfully"},
        400: {"model": ErrorResponse, "description": "Invalid project data or duplicate name"},
        422: {"description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Database error"},
    }
)
async def create_project(
    data: ProjectCreate,
    project_service: ProjectService = Depends(get_project_service),
):
    """Create a new project.

    Args:
        data: ProjectCreate model with validated project data
        project_service: Injected ProjectService instance

    Returns:
        ProjectCreateResponse: Created project details

    Raises:
        HTTPException: 400 for validation errors, 500 for database errors
    """
    # Gotcha #1: Using async def for async service calls
    success, result = await project_service.create_project(data)

    if not success:
        error_msg = result.get("error", "Unknown error occurred")
        logger.warning(f"Failed to create project: {error_msg}")

        # Determine appropriate status code
        if "already exists" in error_msg.lower():
            raise HTTPException(status_code=400, detail=error_msg)
        else:
            raise HTTPException(status_code=500, detail=error_msg)

    logger.info(f"Created project: {result['project']['id']} - {result['project']['name']}")

    return ProjectCreateResponse(
        project=ProjectResponse(**result["project"])
    )


@router.patch(
    "/{project_id}",
    response_model=ProjectUpdateResponse,
    summary="Update a project",
    description="Update an existing project. Only provided fields will be updated (partial update).",
    responses={
        200: {"description": "Project updated successfully"},
        400: {"model": ErrorResponse, "description": "Invalid data or duplicate name"},
        404: {"model": ErrorResponse, "description": "Project not found"},
        422: {"description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Database error"},
    }
)
async def update_project(
    project_id: str,
    data: ProjectUpdate,
    project_service: ProjectService = Depends(get_project_service),
):
    """Update an existing project.

    Only provided fields are updated (partial update).

    Args:
        project_id: UUID of the project to update
        data: ProjectUpdate model with fields to update
        project_service: Injected ProjectService instance

    Returns:
        ProjectUpdateResponse: Updated project details with success message

    Raises:
        HTTPException: 400 for validation errors, 404 if not found, 500 for database errors
    """
    # Gotcha #1: Using async def for async service calls
    success, result = await project_service.update_project(project_id, data)

    if not success:
        error_msg = result.get("error", "Unknown error occurred")
        logger.warning(f"Failed to update project {project_id}: {error_msg}")

        # Determine appropriate status code
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=error_msg)
        elif "already exists" in error_msg.lower():
            raise HTTPException(status_code=400, detail=error_msg)
        else:
            raise HTTPException(status_code=500, detail=error_msg)

    logger.info(f"Updated project: {result['project']['id']} - {result['project']['name']}")

    return ProjectUpdateResponse(
        project=ProjectResponse(**result["project"]),
        message=result.get("message", "Project updated successfully")
    )


@router.delete(
    "/{project_id}",
    response_model=ProjectDeleteResponse,
    summary="Delete a project",
    description="Delete a project by its ID. Note: This will cascade delete all associated tasks if configured.",
    responses={
        200: {"description": "Project deleted successfully"},
        404: {"model": ErrorResponse, "description": "Project not found"},
        400: {"model": ErrorResponse, "description": "Cannot delete project with associated tasks"},
        500: {"model": ErrorResponse, "description": "Database error"},
    }
)
async def delete_project(
    project_id: str,
    project_service: ProjectService = Depends(get_project_service),
):
    """Delete a project by ID.

    Note: This will cascade delete all tasks associated with the project
    if the foreign key is configured with ON DELETE CASCADE.

    Args:
        project_id: UUID of the project to delete
        project_service: Injected ProjectService instance

    Returns:
        ProjectDeleteResponse: Success message

    Raises:
        HTTPException: 404 if not found, 400 for foreign key violations, 500 for database errors
    """
    # Gotcha #1: Using async def for async service calls
    success, result = await project_service.delete_project(project_id)

    if not success:
        error_msg = result.get("error", "Unknown error occurred")
        logger.warning(f"Failed to delete project {project_id}: {error_msg}")

        # Determine appropriate status code
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=error_msg)
        elif "associated tasks" in error_msg.lower():
            raise HTTPException(status_code=400, detail=error_msg)
        else:
            raise HTTPException(status_code=500, detail=error_msg)

    logger.info(f"Deleted project: {project_id}")

    return ProjectDeleteResponse(
        message=result.get("message", f"Project {project_id} deleted successfully")
    )
