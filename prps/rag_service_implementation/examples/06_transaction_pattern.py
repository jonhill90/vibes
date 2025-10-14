# Source: infra/task-manager/backend/src/services/task_service.py
# Lines: 288-378
# Pattern: Atomic Transactions with Row Locking
# Extracted: 2025-10-11
# Relevance: 8/10 - Important for data integrity in multi-step operations

"""
PATTERN: Atomic Database Transactions with Row Locking

This demonstrates how to handle multi-step database operations atomically:
1. Start transaction with async with conn.transaction()
2. Lock affected rows in consistent order (ORDER BY id) to prevent deadlocks
3. Perform batch updates
4. Update target record
5. Commit transaction (automatic on exit)

CRITICAL GOTCHAS:
- Gotcha #2: Lock rows ORDER BY id to prevent deadlocks
- Gotcha #12: Always use async with for connection management
- Gotcha #7: Use $1, $2 placeholders (asyncpg), not %s
"""

import asyncpg
import logging
from typing import Any

logger = logging.getLogger(__name__)


async def update_task_position(
    db_pool: asyncpg.Pool,
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
        db_pool: asyncpg connection pool
        task_id: UUID of task to move
        new_status: Target status column
        new_position: Target position in that column

    Returns:
        Tuple of (success, result_dict with updated task or error)
    """
    try:
        # PATTERN: async with for both connection AND transaction
        async with db_pool.acquire() as conn:
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
