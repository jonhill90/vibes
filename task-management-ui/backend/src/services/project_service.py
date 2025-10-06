"""Project Service Module - Business logic for project operations.

This service implements the service layer pattern for project CRUD operations.

KEY PATTERNS IMPLEMENTED:
1. Service class with validation methods
2. Async operations with asyncpg
3. tuple[bool, dict] return pattern for error handling
4. Input validation before database operations
5. Pagination support for list operations

CRITICAL GOTCHAS ADDRESSED:
- Gotcha #2: Uses async with pool.acquire() and conn.transaction() for atomic operations
- Gotcha #7: Uses $1, $2 placeholders (asyncpg style, not %s)
- Returns tuple[bool, dict] instead of raising exceptions for business logic errors
"""

import logging
from datetime import datetime
from typing import Any

import asyncpg

from models.project import ProjectCreate, ProjectUpdate

logger = logging.getLogger(__name__)


class ProjectService:
    """Service class for project CRUD operations.

    This service handles all business logic for projects including:
    - Input validation
    - Database operations
    - Error handling
    - Pagination

    Returns:
        All methods return tuple[bool, dict]:
        - (True, {"project": {...}}) on success
        - (False, {"error": "message"}) on failure
    """

    def __init__(self, db_pool: asyncpg.Pool):
        """Initialize service with database connection pool.

        Args:
            db_pool: asyncpg connection pool instance
        """
        self.db_pool = db_pool

    def _validate_project_name(self, name: str | None) -> tuple[bool, str]:
        """Validate project name.

        Args:
            name: Project name to validate

        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        if not name or not isinstance(name, str) or len(name.strip()) == 0:
            return False, "Project name is required and must be a non-empty string"

        if len(name) > 255:
            return False, "Project name must not exceed 255 characters"

        return True, ""

    async def list_projects(
        self,
        page: int = 1,
        per_page: int = 10
    ) -> tuple[bool, dict[str, Any]]:
        """List projects with pagination.

        Args:
            page: Page number (1-indexed)
            per_page: Number of items per page (max 100)

        Returns:
            tuple[bool, dict]: (success, result)
            - On success: {"projects": [...], "total_count": int, "page": int, "per_page": int}
            - On failure: {"error": "message"}
        """
        try:
            # Validate pagination parameters
            if page < 1:
                return False, {"error": "Page number must be >= 1"}

            if per_page < 1 or per_page > 100:
                return False, {"error": "Per page must be between 1 and 100"}

            # Calculate offset
            offset = (page - 1) * per_page

            async with self.db_pool.acquire() as conn:
                # Get total count
                count_result = await conn.fetchval(
                    "SELECT COUNT(*) FROM projects"
                )
                total_count = count_result or 0

                # Get paginated projects
                # Note: Uses $1, $2 placeholders (Gotcha #7)
                projects_result = await conn.fetch(
                    """
                    SELECT id, name, description, created_at, updated_at
                    FROM projects
                    ORDER BY created_at DESC
                    LIMIT $1 OFFSET $2
                    """,
                    per_page,
                    offset
                )

                # Convert records to dicts
                projects = [
                    {
                        "id": str(record["id"]),
                        "name": record["name"],
                        "description": record["description"],
                        "created_at": record["created_at"].isoformat(),
                        "updated_at": record["updated_at"].isoformat(),
                    }
                    for record in projects_result
                ]

                return True, {
                    "projects": projects,
                    "total_count": total_count,
                    "page": page,
                    "per_page": per_page,
                }

        except asyncpg.PostgresError as e:
            logger.error(f"Database error listing projects: {e}")
            return False, {"error": f"Database error: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error listing projects: {e}")
            return False, {"error": f"Unexpected error: {str(e)}"}

    async def get_project(self, project_id: str) -> tuple[bool, dict[str, Any]]:
        """Get a single project by ID.

        Args:
            project_id: UUID of the project

        Returns:
            tuple[bool, dict]: (success, result)
            - On success: {"project": {...}}
            - On failure: {"error": "message"}
        """
        try:
            # Validate project_id
            if not project_id or not isinstance(project_id, str):
                return False, {"error": "Project ID is required and must be a string"}

            async with self.db_pool.acquire() as conn:
                project_result = await conn.fetchrow(
                    """
                    SELECT id, name, description, created_at, updated_at
                    FROM projects
                    WHERE id = $1
                    """,
                    project_id
                )

                if not project_result:
                    return False, {"error": f"Project with ID {project_id} not found"}

                project = {
                    "id": str(project_result["id"]),
                    "name": project_result["name"],
                    "description": project_result["description"],
                    "created_at": project_result["created_at"].isoformat(),
                    "updated_at": project_result["updated_at"].isoformat(),
                }

                return True, {"project": project}

        except asyncpg.PostgresError as e:
            logger.error(f"Database error getting project {project_id}: {e}")
            return False, {"error": f"Database error: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error getting project {project_id}: {e}")
            return False, {"error": f"Unexpected error: {str(e)}"}

    async def create_project(
        self,
        data: ProjectCreate
    ) -> tuple[bool, dict[str, Any]]:
        """Create a new project.

        Args:
            data: ProjectCreate model with validated data

        Returns:
            tuple[bool, dict]: (success, result)
            - On success: {"project": {...}}
            - On failure: {"error": "message"}
        """
        try:
            # Additional validation beyond Pydantic
            is_valid, error_msg = self._validate_project_name(data.name)
            if not is_valid:
                return False, {"error": error_msg}

            async with self.db_pool.acquire() as conn:
                # Use transaction for atomic operation (Gotcha #2)
                async with conn.transaction():
                    project_result = await conn.fetchrow(
                        """
                        INSERT INTO projects (name, description, created_at, updated_at)
                        VALUES ($1, $2, NOW(), NOW())
                        RETURNING id, name, description, created_at, updated_at
                        """,
                        data.name.strip(),
                        data.description.strip() if data.description else None
                    )

                    if not project_result:
                        return False, {"error": "Failed to create project"}

                    project = {
                        "id": str(project_result["id"]),
                        "name": project_result["name"],
                        "description": project_result["description"],
                        "created_at": project_result["created_at"].isoformat(),
                        "updated_at": project_result["updated_at"].isoformat(),
                    }

                    logger.info(f"Created project: {project['id']} - {project['name']}")

                    return True, {"project": project}

        except asyncpg.UniqueViolationError:
            logger.warning(f"Attempted to create duplicate project: {data.name}")
            return False, {"error": f"Project with name '{data.name}' already exists"}
        except asyncpg.PostgresError as e:
            logger.error(f"Database error creating project: {e}")
            return False, {"error": f"Database error: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error creating project: {e}")
            return False, {"error": f"Unexpected error: {str(e)}"}

    async def update_project(
        self,
        project_id: str,
        data: ProjectUpdate
    ) -> tuple[bool, dict[str, Any]]:
        """Update an existing project.

        Only provided fields are updated (partial update).

        Args:
            project_id: UUID of the project to update
            data: ProjectUpdate model with fields to update

        Returns:
            tuple[bool, dict]: (success, result)
            - On success: {"project": {...}, "message": "..."}
            - On failure: {"error": "message"}
        """
        try:
            # Validate project_id
            if not project_id or not isinstance(project_id, str):
                return False, {"error": "Project ID is required and must be a string"}

            # Validate name if provided
            if data.name is not None:
                is_valid, error_msg = self._validate_project_name(data.name)
                if not is_valid:
                    return False, {"error": error_msg}

            # Build update fields dynamically
            update_fields = []
            update_values = []
            param_count = 1

            if data.name is not None:
                update_fields.append(f"name = ${param_count}")
                update_values.append(data.name.strip())
                param_count += 1

            if data.description is not None:
                update_fields.append(f"description = ${param_count}")
                update_values.append(data.description.strip() if data.description else None)
                param_count += 1

            # Always update updated_at
            update_fields.append(f"updated_at = NOW()")

            # If no fields to update, return early
            if not update_values:
                return False, {"error": "No fields provided to update"}

            # Add project_id as final parameter
            update_values.append(project_id)

            async with self.db_pool.acquire() as conn:
                # Use transaction for atomic operation (Gotcha #2)
                async with conn.transaction():
                    update_query = f"""
                        UPDATE projects
                        SET {', '.join(update_fields)}
                        WHERE id = ${param_count}
                        RETURNING id, name, description, created_at, updated_at
                    """

                    project_result = await conn.fetchrow(
                        update_query,
                        *update_values
                    )

                    if not project_result:
                        return False, {"error": f"Project with ID {project_id} not found"}

                    project = {
                        "id": str(project_result["id"]),
                        "name": project_result["name"],
                        "description": project_result["description"],
                        "created_at": project_result["created_at"].isoformat(),
                        "updated_at": project_result["updated_at"].isoformat(),
                    }

                    logger.info(f"Updated project: {project['id']} - {project['name']}")

                    return True, {
                        "project": project,
                        "message": "Project updated successfully"
                    }

        except asyncpg.UniqueViolationError:
            logger.warning(f"Attempted to update project to duplicate name: {data.name}")
            return False, {"error": f"Project with name '{data.name}' already exists"}
        except asyncpg.PostgresError as e:
            logger.error(f"Database error updating project {project_id}: {e}")
            return False, {"error": f"Database error: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error updating project {project_id}: {e}")
            return False, {"error": f"Unexpected error: {str(e)}"}

    async def delete_project(self, project_id: str) -> tuple[bool, dict[str, Any]]:
        """Delete a project by ID.

        Note: This will cascade delete all tasks associated with the project
        if the foreign key is configured with ON DELETE CASCADE.

        Args:
            project_id: UUID of the project to delete

        Returns:
            tuple[bool, dict]: (success, result)
            - On success: {"message": "..."}
            - On failure: {"error": "message"}
        """
        try:
            # Validate project_id
            if not project_id or not isinstance(project_id, str):
                return False, {"error": "Project ID is required and must be a string"}

            async with self.db_pool.acquire() as conn:
                # Use transaction for atomic operation (Gotcha #2)
                async with conn.transaction():
                    # Check if project exists first
                    exists = await conn.fetchval(
                        "SELECT EXISTS(SELECT 1 FROM projects WHERE id = $1)",
                        project_id
                    )

                    if not exists:
                        return False, {"error": f"Project with ID {project_id} not found"}

                    # Delete the project
                    deleted = await conn.execute(
                        "DELETE FROM projects WHERE id = $1",
                        project_id
                    )

                    logger.info(f"Deleted project: {project_id}")

                    return True, {"message": f"Project {project_id} deleted successfully"}

        except asyncpg.ForeignKeyViolationError as e:
            logger.warning(f"Cannot delete project {project_id} due to foreign key constraint: {e}")
            return False, {
                "error": "Cannot delete project because it has associated tasks. "
                "Delete all tasks first or configure cascade delete."
            }
        except asyncpg.PostgresError as e:
            logger.error(f"Database error deleting project {project_id}: {e}")
            return False, {"error": f"Database error: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error deleting project {project_id}: {e}")
            return False, {"error": f"Unexpected error: {str(e)}"}
