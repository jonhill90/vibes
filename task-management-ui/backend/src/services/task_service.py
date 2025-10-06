"""Task Service Module - Business Logic for Task CRUD with Position Management.

This module provides:
- Task CRUD operations with validation
- Atomic position reordering using transactions and row locking
- Pagination and field exclusion for performance
- Proper error handling with tuple[bool, dict] return pattern

Critical Gotchas Addressed:
- Gotcha #2: Position reordering uses transaction + row locking (SELECT ... FOR UPDATE)
- Lock rows ORDER BY id to prevent deadlocks
- Gotcha #12: Always uses async with for connection management
- Gotcha #7: Uses $1, $2 placeholders (asyncpg style, not %s)

Pattern Source: prps/task_management_ui/examples/backend/task_service.py
"""

from typing import Any
import asyncpg
import logging
from datetime import datetime

from ..models.task import TaskCreate, TaskUpdate, TaskResponse, TaskStatus, TaskPriority

logger = logging.getLogger(__name__)


class TaskService:
    """Service class for task operations with atomic position management."""

    VALID_STATUSES = ["todo", "doing", "review", "done"]
    VALID_PRIORITIES = ["low", "medium", "high", "urgent"]

    def __init__(self, db_pool: asyncpg.Pool):
        """Initialize TaskService with database connection pool.

        Args:
            db_pool: asyncpg connection pool for database operations
        """
        self.db_pool = db_pool

    def validate_status(self, status: str) -> tuple[bool, str]:
        """Validate task status against allowed enum values.

        Args:
            status: Status string to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if status not in self.VALID_STATUSES:
            return (
                False,
                f"Invalid status '{status}'. Must be one of: {', '.join(self.VALID_STATUSES)}",
            )
        return True, ""

    def validate_priority(self, priority: str) -> tuple[bool, str]:
        """Validate task priority against allowed enum values.

        Args:
            priority: Priority string to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if priority not in self.VALID_PRIORITIES:
            return (
                False,
                f"Invalid priority '{priority}'. Must be one of: {', '.join(self.VALID_PRIORITIES)}",
            )
        return True, ""

    async def list_tasks(
        self,
        filters: dict[str, Any] | None = None,
        page: int = 1,
        per_page: int = 50,
        exclude_large_fields: bool = False,
    ) -> tuple[bool, dict[str, Any]]:
        """List tasks with filters, pagination, and optional field exclusion.

        PATTERN: Conditional field selection for performance
        - exclude_large_fields=True: Truncate description > 1000 chars
        - exclude_large_fields=False: Return full description

        Args:
            filters: Optional filters (project_id, status, assignee)
            page: Page number (1-indexed)
            per_page: Items per page
            exclude_large_fields: If True, truncate long descriptions

        Returns:
            Tuple of (success, result_dict with tasks and total_count)
        """
        try:
            filters = filters or {}
            offset = (page - 1) * per_page

            # Build base query with conditional field selection
            if exclude_large_fields:
                # Truncate description to 1000 chars
                select_fields = """
                    id, project_id, parent_task_id, title,
                    CASE
                        WHEN LENGTH(description) > 1000
                        THEN SUBSTRING(description FROM 1 FOR 1000) || '...'
                        ELSE description
                    END as description,
                    status, assignee, priority, position,
                    created_at, updated_at
                """
            else:
                select_fields = "*"

            where_clauses = []
            params = []
            param_idx = 1

            # Apply filters
            if "project_id" in filters:
                where_clauses.append(f"project_id = ${param_idx}")
                params.append(filters["project_id"])
                param_idx += 1

            if "status" in filters:
                status = filters["status"]
                is_valid, error_msg = self.validate_status(status)
                if not is_valid:
                    return False, {"error": error_msg}
                where_clauses.append(f"status = ${param_idx}")
                params.append(status)
                param_idx += 1

            if "assignee" in filters:
                where_clauses.append(f"assignee = ${param_idx}")
                params.append(filters["assignee"])
                param_idx += 1

            where_clause = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

            # Get total count
            count_query = f"SELECT COUNT(*) FROM tasks {where_clause}"
            async with self.db_pool.acquire() as conn:
                total_count = await conn.fetchval(count_query, *params)

                # Get paginated tasks
                query = f"""
                    SELECT {select_fields}
                    FROM tasks
                    {where_clause}
                    ORDER BY position ASC, created_at ASC
                    LIMIT ${param_idx} OFFSET ${param_idx + 1}
                """
                params.extend([per_page, offset])
                rows = await conn.fetch(query, *params)

            tasks = [dict(row) for row in rows]

            return True, {
                "tasks": tasks,
                "total_count": total_count,
                "page": page,
                "per_page": per_page,
            }

        except asyncpg.PostgresError as e:
            logger.error(f"Database error listing tasks: {e}")
            return False, {"error": f"Database error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error listing tasks: {e}")
            return False, {"error": f"Error listing tasks: {str(e)}"}

    async def get_task(self, task_id: str) -> tuple[bool, dict[str, Any]]:
        """Get a single task by ID.

        Args:
            task_id: UUID of the task to retrieve

        Returns:
            Tuple of (success, result_dict with task data or error)
        """
        try:
            async with self.db_pool.acquire() as conn:
                query = "SELECT * FROM tasks WHERE id = $1"
                row = await conn.fetchrow(query, task_id)

            if row is None:
                return False, {"error": f"Task with ID {task_id} not found"}

            task = dict(row)
            return True, {"task": task}

        except asyncpg.PostgresError as e:
            logger.error(f"Database error getting task {task_id}: {e}")
            return False, {"error": f"Database error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error getting task {task_id}: {e}")
            return False, {"error": f"Error getting task: {str(e)}"}

    async def create_task(self, data: TaskCreate) -> tuple[bool, dict[str, Any]]:
        """Create a new task with position reordering if necessary.

        CRITICAL PATTERN: If position > 0, increment existing tasks at that position
        Uses the same reordering logic as update_task_position but simpler.

        Args:
            data: TaskCreate model with task data

        Returns:
            Tuple of (success, result_dict with created task or error)
        """
        try:
            # Validate inputs
            is_valid, error_msg = self.validate_status(data.status)
            if not is_valid:
                return False, {"error": error_msg}

            is_valid, error_msg = self.validate_priority(data.priority)
            if not is_valid:
                return False, {"error": error_msg}

            async with self.db_pool.acquire() as conn:
                async with conn.transaction():
                    # If inserting at specific position, increment existing tasks
                    if data.position > 0:
                        # Lock and increment positions >= new position
                        # ORDER BY id for consistent lock order (prevent deadlocks)
                        await conn.execute(
                            """
                            SELECT id FROM tasks
                            WHERE status = $1 AND position >= $2
                            ORDER BY id
                            FOR UPDATE
                            """,
                            data.status,
                            data.position,
                        )

                        # Atomic batch update - increment positions
                        await conn.execute(
                            """
                            UPDATE tasks
                            SET position = position + 1, updated_at = NOW()
                            WHERE status = $1 AND position >= $2
                            """,
                            data.status,
                            data.position,
                        )

                    # Insert new task
                    query = """
                        INSERT INTO tasks (
                            project_id, parent_task_id, title, description,
                            status, assignee, priority, position,
                            created_at, updated_at
                        )
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW(), NOW())
                        RETURNING *
                    """
                    row = await conn.fetchrow(
                        query,
                        data.project_id,
                        None,  # parent_task_id - not in TaskCreate model
                        data.title,
                        data.description,
                        data.status,
                        data.assignee,
                        data.priority,
                        data.position,
                    )

            task = dict(row)
            logger.info(f"Created task {task['id']} at position {data.position}")

            return True, {
                "task": task,
                "message": "Task created successfully",
            }

        except asyncpg.PostgresError as e:
            logger.error(f"Database error creating task: {e}")
            return False, {"error": f"Database error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return False, {"error": f"Error creating task: {str(e)}"}

    async def update_task_position(
        self,
        task_id: str,
        new_status: str,
        new_position: int,
    ) -> tuple[bool, dict[str, Any]]:
        """Update task position with atomic reordering logic.

        CRITICAL IMPLEMENTATION - Gotcha #2 Pattern:
        1. Start transaction
        2. Lock affected rows in consistent order (ORDER BY id) to prevent deadlocks
        3. Batch update: increment positions >= new_position
        4. Update target task to new status and position
        5. Commit transaction

        This ensures concurrent position updates don't create duplicate positions.

        Args:
            task_id: UUID of task to move
            new_status: Target status column
            new_position: Target position in that column

        Returns:
            Tuple of (success, result_dict with updated task or error)
        """
        try:
            # Validate status
            is_valid, error_msg = self.validate_status(new_status)
            if not is_valid:
                return False, {"error": error_msg}

            async with self.db_pool.acquire() as conn:
                async with conn.transaction():
                    # CRITICAL: Lock rows in consistent order (ORDER BY id)
                    # This prevents deadlocks when multiple concurrent updates occur
                    await conn.execute(
                        """
                        SELECT id FROM tasks
                        WHERE status = $1 AND position >= $2
                        ORDER BY id
                        FOR UPDATE
                        """,
                        new_status,
                        new_position,
                    )

                    # Atomic batch update - increment positions
                    # This makes space for the task being moved
                    await conn.execute(
                        """
                        UPDATE tasks
                        SET position = position + 1, updated_at = NOW()
                        WHERE status = $1 AND position >= $2
                        """,
                        new_status,
                        new_position,
                    )

                    # Update target task to new status and position
                    query = """
                        UPDATE tasks
                        SET status = $1, position = $2, updated_at = NOW()
                        WHERE id = $3
                        RETURNING *
                    """
                    row = await conn.fetchrow(
                        query,
                        new_status,
                        new_position,
                        task_id,
                    )

                if row is None:
                    return False, {"error": f"Task with ID {task_id} not found"}

            task = dict(row)
            logger.info(
                f"Moved task {task_id} to {new_status} position {new_position}"
            )

            return True, {
                "task": task,
                "message": "Task position updated successfully",
            }

        except asyncpg.PostgresError as e:
            logger.error(f"Database error updating task position: {e}")
            return False, {"error": f"Database error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error updating task position: {e}")
            return False, {"error": f"Error updating task position: {str(e)}"}

    async def update_task(
        self,
        task_id: str,
        data: TaskUpdate,
    ) -> tuple[bool, dict[str, Any]]:
        """Update task fields (excluding position - use update_task_position for that).

        PATTERN: Partial updates with validation
        - Only update provided fields
        - Validate each field before updating
        - Always update updated_at timestamp

        Args:
            task_id: UUID of task to update
            data: TaskUpdate model with fields to update

        Returns:
            Tuple of (success, result_dict with updated task or error)
        """
        try:
            update_fields = []
            params = []
            param_idx = 1

            # Build dynamic update query
            if data.title is not None:
                update_fields.append(f"title = ${param_idx}")
                params.append(data.title)
                param_idx += 1

            if data.description is not None:
                update_fields.append(f"description = ${param_idx}")
                params.append(data.description)
                param_idx += 1

            if data.status is not None:
                is_valid, error_msg = self.validate_status(data.status)
                if not is_valid:
                    return False, {"error": error_msg}
                update_fields.append(f"status = ${param_idx}")
                params.append(data.status)
                param_idx += 1

            if data.assignee is not None:
                update_fields.append(f"assignee = ${param_idx}")
                params.append(data.assignee)
                param_idx += 1

            if data.priority is not None:
                is_valid, error_msg = self.validate_priority(data.priority)
                if not is_valid:
                    return False, {"error": error_msg}
                update_fields.append(f"priority = ${param_idx}")
                params.append(data.priority)
                param_idx += 1

            if data.position is not None:
                update_fields.append(f"position = ${param_idx}")
                params.append(data.position)
                param_idx += 1

            if not update_fields:
                return False, {"error": "No fields to update"}

            # Always update timestamp
            update_fields.append("updated_at = NOW()")

            # Add task_id as final parameter
            params.append(task_id)

            query = f"""
                UPDATE tasks
                SET {', '.join(update_fields)}
                WHERE id = ${param_idx}
                RETURNING *
            """

            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow(query, *params)

            if row is None:
                return False, {"error": f"Task with ID {task_id} not found"}

            task = dict(row)
            logger.info(f"Updated task {task_id}")

            return True, {
                "task": task,
                "message": "Task updated successfully",
            }

        except asyncpg.PostgresError as e:
            logger.error(f"Database error updating task {task_id}: {e}")
            return False, {"error": f"Database error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error updating task {task_id}: {e}")
            return False, {"error": f"Error updating task: {str(e)}"}

    async def delete_task(self, task_id: str) -> tuple[bool, dict[str, Any]]:
        """Delete a task by ID.

        Args:
            task_id: UUID of task to delete

        Returns:
            Tuple of (success, result_dict with message or error)
        """
        try:
            async with self.db_pool.acquire() as conn:
                query = "DELETE FROM tasks WHERE id = $1 RETURNING id"
                row = await conn.fetchrow(query, task_id)

            if row is None:
                return False, {"error": f"Task with ID {task_id} not found"}

            logger.info(f"Deleted task {task_id}")

            return True, {"message": f"Task {task_id} deleted successfully"}

        except asyncpg.PostgresError as e:
            logger.error(f"Database error deleting task {task_id}: {e}")
            return False, {"error": f"Database error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error deleting task {task_id}: {e}")
            return False, {"error": f"Error deleting task: {str(e)}"}
