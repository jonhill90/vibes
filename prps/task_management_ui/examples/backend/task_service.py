# Source: /Users/jon/source/vibes/repos/Archon/python/src/server/services/projects/task_service.py
# Lines: 1-527
# Pattern: Service layer architecture with validation and async operations
# Extracted: 2025-10-06
# Relevance: 9/10 - Core business logic patterns

"""
Task Service Module - Service Layer Pattern

KEY PATTERNS TO MIMIC:
1. Service class with validation methods
2. Async operations with Supabase
3. Reordering logic for drag-and-drop position management
4. Response normalization and error handling
5. Exclude large fields optimization for list queries
"""

from datetime import datetime
from typing import Any

class TaskService:
    """Service class for task operations"""

    VALID_STATUSES = ["todo", "doing", "review", "done"]

    def __init__(self, supabase_client=None):
        """Initialize with optional supabase client"""
        self.supabase_client = supabase_client or get_supabase_client()

    def validate_status(self, status: str) -> tuple[bool, str]:
        """Validate task status"""
        if status not in self.VALID_STATUSES:
            return (
                False,
                f"Invalid status '{status}'. Must be one of: {', '.join(self.VALID_STATUSES)}",
            )
        return True, ""

    def validate_assignee(self, assignee: str) -> tuple[bool, str]:
        """Validate task assignee"""
        if not assignee or not isinstance(assignee, str) or len(assignee.strip()) == 0:
            return False, "Assignee must be a non-empty string"
        return True, ""

    def validate_priority(self, priority: str) -> tuple[bool, str]:
        """Validate task priority against allowed enum values"""
        VALID_PRIORITIES = ["low", "medium", "high", "critical"]
        if priority not in VALID_PRIORITIES:
            return (
                False,
                f"Invalid priority '{priority}'. Must be one of: {', '.join(VALID_PRIORITIES)}",
            )
        return True, ""

    async def create_task(
        self,
        project_id: str,
        title: str,
        description: str = "",
        assignee: str = "User",
        task_order: int = 0,
        priority: str = "medium",
        feature: str | None = None,
        sources: list[dict[str, Any]] = None,
        code_examples: list[dict[str, Any]] = None,
    ) -> tuple[bool, dict[str, Any]]:
        """
        Create a new task under a project with automatic reordering.

        CRITICAL PATTERN: Position reordering logic
        When inserting at a specific position:
        1. Get all tasks with position >= new task's order
        2. Increment each by 1
        3. Insert new task at position

        Returns:
            Tuple of (success, result_dict)
        """
        try:
            # Validate inputs
            if not title or not isinstance(title, str) or len(title.strip()) == 0:
                return False, {"error": "Task title is required and must be a non-empty string"}

            if not project_id or not isinstance(project_id, str):
                return False, {"error": "Project ID is required and must be a string"}

            # Validate assignee
            is_valid, error_msg = self.validate_assignee(assignee)
            if not is_valid:
                return False, {"error": error_msg}

            # Validate priority
            is_valid, error_msg = self.validate_priority(priority)
            if not is_valid:
                return False, {"error": error_msg}

            task_status = "todo"

            # REORDERING LOGIC: If inserting at a specific position, increment existing tasks
            if task_order > 0:
                # Get all tasks in the same project and status with task_order >= new task's order
                existing_tasks_response = (
                    self.supabase_client.table("archon_tasks")
                    .select("id, task_order")
                    .eq("project_id", project_id)
                    .eq("status", task_status)
                    .gte("task_order", task_order)
                    .execute()
                )

                if existing_tasks_response.data:
                    logger.info(f"Reordering {len(existing_tasks_response.data)} existing tasks")

                    # Increment task_order for all affected tasks
                    for existing_task in existing_tasks_response.data:
                        new_order = existing_task["task_order"] + 1
                        self.supabase_client.table("archon_tasks").update({
                            "task_order": new_order,
                            "updated_at": datetime.now().isoformat(),
                        }).eq("id", existing_task["id"]).execute()

            task_data = {
                "project_id": project_id,
                "title": title,
                "description": description,
                "status": task_status,
                "assignee": assignee,
                "task_order": task_order,
                "priority": priority,
                "sources": sources or [],
                "code_examples": code_examples or [],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            }

            if feature:
                task_data["feature"] = feature

            response = self.supabase_client.table("archon_tasks").insert(task_data).execute()

            if response.data:
                task = response.data[0]

                return True, {
                    "task": {
                        "id": task["id"],
                        "project_id": task["project_id"],
                        "title": task["title"],
                        "description": task["description"],
                        "status": task["status"],
                        "assignee": task["assignee"],
                        "task_order": task["task_order"],
                        "priority": task["priority"],
                        "created_at": task["created_at"],
                    }
                }
            else:
                return False, {"error": "Failed to create task"}

        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return False, {"error": f"Error creating task: {str(e)}"}

    def list_tasks(
        self,
        project_id: str = None,
        status: str = None,
        include_closed: bool = False,
        exclude_large_fields: bool = False,
        include_archived: bool = False,
        search_query: str = None
    ) -> tuple[bool, dict[str, Any]]:
        """
        List tasks with various filters.

        CRITICAL PATTERN: Conditional field exclusion for performance
        - exclude_large_fields=True: Select specific columns, add counts for JSONB arrays
        - exclude_large_fields=False: Select all fields

        Args:
            project_id: Filter by project
            status: Filter by status
            include_closed: Include done tasks
            exclude_large_fields: If True, excludes sources and code_examples fields
            include_archived: If True, includes archived tasks
            search_query: Keyword search in title, description, and feature fields

        Returns:
            Tuple of (success, result_dict)
        """
        try:
            # PATTERN: Conditional field selection
            if exclude_large_fields:
                # Select all fields except large JSONB ones
                query = self.supabase_client.table("archon_tasks").select(
                    "id, project_id, parent_task_id, title, description, "
                    "status, assignee, task_order, priority, feature, archived, "
                    "archived_at, archived_by, created_at, updated_at, "
                    "sources, code_examples"  # Still fetch for counting
                )
            else:
                query = self.supabase_client.table("archon_tasks").select("*")

            # Apply filters
            if project_id:
                query = query.eq("project_id", project_id)

            if status:
                # Validate status
                is_valid, error_msg = self.validate_status(status)
                if not is_valid:
                    return False, {"error": error_msg}
                query = query.eq("status", status)
            elif not include_closed:
                # Only exclude done tasks if no specific status filter
                query = query.neq("status", "done")

            # PATTERN: Keyword search across multiple fields
            if search_query:
                search_terms = search_query.lower().split()

                if len(search_terms) == 1:
                    # Single term: simple OR across fields
                    term = search_terms[0]
                    query = query.or_(
                        f"title.ilike.%{term}%,"
                        f"description.ilike.%{term}%,"
                        f"feature.ilike.%{term}%"
                    )
                else:
                    # Multiple terms: search for full phrase
                    full_query = search_query.lower()
                    query = query.or_(
                        f"title.ilike.%{full_query}%,"
                        f"description.ilike.%{full_query}%,"
                        f"feature.ilike.%{full_query}%"
                    )

            # Filter archived tasks
            if not include_archived:
                query = query.or_("archived.is.null,archived.is.false")

            # Execute query
            response = (
                query.order("task_order", desc=False).order("created_at", desc=False).execute()
            )

            tasks = []
            for task in response.data:
                task_data = {
                    "id": task["id"],
                    "project_id": task["project_id"],
                    "title": task["title"],
                    "description": task["description"],
                    "status": task["status"],
                    "assignee": task.get("assignee", "User"),
                    "task_order": task.get("task_order", 0),
                    "priority": task.get("priority", "medium"),
                    "feature": task.get("feature"),
                    "created_at": task["created_at"],
                    "updated_at": task["updated_at"],
                    "archived": task.get("archived", False),
                }

                # PATTERN: Conditionally include large fields or counts
                if not exclude_large_fields:
                    task_data["sources"] = task.get("sources", [])
                    task_data["code_examples"] = task.get("code_examples", [])
                else:
                    task_data["stats"] = {
                        "sources_count": len(task.get("sources", [])),
                        "code_examples_count": len(task.get("code_examples", []))
                    }

                tasks.append(task_data)

            return True, {
                "tasks": tasks,
                "total_count": len(tasks),
            }

        except Exception as e:
            logger.error(f"Error listing tasks: {e}")
            return False, {"error": f"Error listing tasks: {str(e)}"}

    async def update_task(
        self, task_id: str, update_fields: dict[str, Any]
    ) -> tuple[bool, dict[str, Any]]:
        """
        Update task with specified fields.

        PATTERN: Partial updates with validation
        - Only update provided fields
        - Validate each field before updating
        - Always update updated_at timestamp

        Returns:
            Tuple of (success, result_dict)
        """
        try:
            # Build update data
            update_data = {"updated_at": datetime.now().isoformat()}

            # Validate and add fields
            if "title" in update_fields:
                update_data["title"] = update_fields["title"]

            if "description" in update_fields:
                update_data["description"] = update_fields["description"]

            if "status" in update_fields:
                is_valid, error_msg = self.validate_status(update_fields["status"])
                if not is_valid:
                    return False, {"error": error_msg}
                update_data["status"] = update_fields["status"]

            if "assignee" in update_fields:
                is_valid, error_msg = self.validate_assignee(update_fields["assignee"])
                if not is_valid:
                    return False, {"error": error_msg}
                update_data["assignee"] = update_fields["assignee"]

            if "priority" in update_fields:
                is_valid, error_msg = self.validate_priority(update_fields["priority"])
                if not is_valid:
                    return False, {"error": error_msg}
                update_data["priority"] = update_fields["priority"]

            if "task_order" in update_fields:
                update_data["task_order"] = update_fields["task_order"]

            if "feature" in update_fields:
                update_data["feature"] = update_fields["feature"]

            # Update task
            response = (
                self.supabase_client.table("archon_tasks")
                .update(update_data)
                .eq("id", task_id)
                .execute()
            )

            if response.data:
                task = response.data[0]

                return True, {"task": task, "message": "Task updated successfully"}
            else:
                return False, {"error": f"Task with ID {task_id} not found"}

        except Exception as e:
            logger.error(f"Error updating task: {e}")
            return False, {"error": f"Error updating task: {str(e)}"}
