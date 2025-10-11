# Source: infra/task-manager/backend/src/services/task_service.py
# Lines: 28-172
# Pattern: Service Layer with Async Database Operations
# Extracted: 2025-10-11
# Relevance: 10/10 - Core service pattern for RAG service

"""
PATTERN: Service Layer with asyncpg Connection Pooling

This demonstrates the foundational pattern for building service classes
that interact with PostgreSQL using asyncpg.

Key Patterns:
1. __init__ accepts db_pool parameter
2. All methods return tuple[bool, dict]
3. Async context managers for connection handling
4. Validation before database operations
5. Comprehensive error handling
6. Response optimization with exclude_large_fields
"""

from typing import Any
import asyncpg
import logging
from datetime import datetime

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

            # CRITICAL PATTERN: Always use async with for connection management
            async with self.db_pool.acquire() as conn:
                total_count = await conn.fetchval(count_query, *params)

                # Get paginated tasks
                # CRITICAL: Use $1, $2 placeholders (asyncpg), not %s
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
