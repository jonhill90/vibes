"""MCP Server for Task Management UI.

This module provides FastMCP tools for AI assistant integration with the task management system.

KEY PATTERNS IMPLEMENTED:
1. Consolidated tool pattern: find_tasks (list/search/get), manage_task (create/update/delete)
2. Response optimization for MCP: truncate large fields to reduce payload size
3. Structured error handling with suggestion messages
4. Support for multiple query modes: search, filter, get single item

CRITICAL GOTCHAS ADDRESSED:
- Gotcha #3: MCP tools MUST return JSON strings (not dicts)
- Gotcha #3: ALWAYS truncate description to 1000 chars
- Gotcha #3: Limit per_page to MAX_TASKS_PER_PAGE (20)
- Return structured errors: {"success": false, "error": "...", "suggestion": "..."}

Pattern Source: prps/task_management_ui/examples/mcp/task_tools.py
"""

import json
import logging
import os
from typing import Any

from mcp.server.fastmcp import FastMCP

from src.config.database import get_pool
from src.services.task_service import TaskService
from src.services.project_service import ProjectService
from src.models.task import TaskCreate, TaskUpdate
from src.models.project import ProjectCreate, ProjectUpdate

logger = logging.getLogger(__name__)

# MCP server instance
mcp = FastMCP("Task Manager")

# Optimization constants (from PRP and pattern)
MAX_DESCRIPTION_LENGTH = 1000
MAX_TASKS_PER_PAGE = 20
DEFAULT_PAGE_SIZE = 10


def truncate_text(text: str | None, max_length: int = MAX_DESCRIPTION_LENGTH) -> str | None:
    """Truncate text to maximum length with ellipsis.

    Args:
        text: Text to truncate
        max_length: Maximum length before truncation

    Returns:
        Truncated text or None if input was None
    """
    if text and len(text) > max_length:
        return text[:max_length - 3] + "..."
    return text


def optimize_task_for_mcp(task: dict) -> dict:
    """Optimize task object for MCP response.

    CRITICAL: Always optimize list responses to reduce payload size.
    Single task GET operations still truncate descriptions but keep other fields.

    Pattern from Archon: Truncate description, remove large fields.

    Args:
        task: Task dictionary from database

    Returns:
        Optimized task dictionary
    """
    task = task.copy()  # Don't modify original

    # Truncate description if present (Gotcha #3)
    if "description" in task and task["description"]:
        task["description"] = truncate_text(task["description"])

    return task


@mcp.tool()
async def find_tasks(
    query: str | None = None,
    task_id: str | None = None,
    filter_by: str | None = None,
    filter_value: str | None = None,
    project_id: str | None = None,
    page: int = 1,
    per_page: int = DEFAULT_PAGE_SIZE,
) -> str:
    """Find and search tasks (consolidated: list + search + get).

    PATTERN: Single tool for multiple query modes
    - task_id provided: Returns single task with full details
    - filter_by provided: Filters by status/project/assignee
    - No params: Returns all tasks (paginated)

    Args:
        query: Keyword search (not implemented in this version)
        task_id: Get specific task by ID (returns full details)
        filter_by: "status" | "project" | "assignee" (optional)
        filter_value: Filter value (e.g., "todo", "doing", "review", "done")
        project_id: Project UUID (optional, for additional filtering)
        page: Page number for pagination (default: 1)
        per_page: Items per page (default: 10, max: 20)

    Returns:
        JSON string with tasks or error (NEVER returns dict - Gotcha #3)

    Examples:
        find_tasks() # All tasks
        find_tasks(task_id="task-123") # Get specific task (full details)
        find_tasks(filter_by="status", filter_value="todo") # Only todo tasks
        find_tasks(project_id="proj-456") # Tasks in project
    """
    try:
        # Limit per_page to MAX_TASKS_PER_PAGE (Gotcha #3)
        per_page = min(per_page, MAX_TASKS_PER_PAGE)

        # Get database pool and initialize services
        db_pool = await get_pool()
        task_service = TaskService(db_pool)

        # Single task get mode - return full details with truncation
        if task_id:
            success, result = await task_service.get_task(task_id)

            if not success:
                return json.dumps({
                    "success": False,
                    "error": result.get("error", "Task not found"),
                    "suggestion": "Verify the task ID is correct or use find_tasks() without task_id to list all tasks"
                })

            task = result.get("task")
            if task:
                # Truncate description even for single task (Gotcha #3)
                task = optimize_task_for_mcp(task)

            return json.dumps({
                "success": True,
                "task": task
            })

        # List mode with filters
        filters: dict[str, Any] = {}

        # Build filters based on parameters
        if filter_by == "status" and filter_value:
            filters["status"] = filter_value
        elif filter_by == "assignee" and filter_value:
            filters["assignee"] = filter_value
        elif filter_by == "project" and filter_value:
            filters["project_id"] = filter_value

        # Add project_id filter if provided
        if project_id:
            filters["project_id"] = project_id

        # List tasks with filters and pagination
        # CRITICAL: exclude_large_fields=True for MCP responses (Gotcha #3)
        success, result = await task_service.list_tasks(
            filters=filters,
            page=page,
            per_page=per_page,
            exclude_large_fields=True
        )

        if not success:
            return json.dumps({
                "success": False,
                "error": result.get("error", "Failed to list tasks"),
                "suggestion": "Check error message and try again"
            })

        tasks = result.get("tasks", [])
        total_count = result.get("total_count", 0)

        # Optimize each task (extra safety, service should already truncate)
        optimized_tasks = [optimize_task_for_mcp(task) for task in tasks]

        return json.dumps({
            "success": True,
            "tasks": optimized_tasks,
            "total_count": total_count,
            "count": len(optimized_tasks),
            "page": page,
            "per_page": per_page
        })

    except Exception as e:
        logger.error(f"Error in find_tasks: {e}", exc_info=True)
        return json.dumps({
            "success": False,
            "error": str(e),
            "suggestion": "Check error message and try again"
        })


@mcp.tool()
async def manage_task(
    action: str,
    task_id: str | None = None,
    project_id: str | None = None,
    title: str | None = None,
    description: str | None = None,
    status: str | None = None,
    assignee: str | None = None,
    priority: str | None = None,
    position: int | None = None
) -> str:
    """Manage tasks (consolidated: create/update/delete).

    TASK GRANULARITY GUIDANCE:
    - For feature-specific projects: Create detailed implementation tasks
    - For codebase-wide projects: Create feature-level tasks
    - Default to more granular tasks when project scope is unclear
    - Each task should represent 30 minutes to 4 hours of work

    Args:
        action: "create" | "update" | "delete"
        task_id: Task UUID for update/delete
        project_id: Project UUID for create
        title: Task title text
        description: Detailed task description
        status: "todo" | "doing" | "review" | "done"
        assignee: String name of assignee (User, Archon, agent names)
        priority: "low" | "medium" | "high" | "urgent"
        position: Position in status column (0 = end)

    Examples:
        manage_task("create", project_id="p-1", title="Research patterns", status="todo")
        manage_task("update", task_id="t-1", status="doing", assignee="User")
        manage_task("delete", task_id="t-1")

    Returns:
        JSON string with result (NEVER returns dict - Gotcha #3)
    """
    try:
        # Get database pool and initialize services
        db_pool = await get_pool()
        task_service = TaskService(db_pool)

        if action == "create":
            # VALIDATION: Require project_id and title for create
            if not project_id or not title:
                return json.dumps({
                    "success": False,
                    "error": "project_id and title required for create",
                    "suggestion": "Provide both project_id and title"
                })

            # Create TaskCreate model with defaults
            task_data = TaskCreate(
                project_id=project_id,
                title=title,
                description=description or "",
                status=status or "todo",
                assignee=assignee or "User",
                priority=priority or "medium",
                position=position or 0
            )

            success, result = await task_service.create_task(task_data)

            if not success:
                return json.dumps({
                    "success": False,
                    "error": result.get("error", "Failed to create task"),
                    "suggestion": "Check error message and ensure all required fields are valid"
                })

            task = result.get("task")
            if task:
                task = optimize_task_for_mcp(task)

            return json.dumps({
                "success": True,
                "task": task,
                "task_id": task.get("id") if task else None,
                "message": result.get("message", "Task created successfully")
            })

        elif action == "update":
            if not task_id:
                return json.dumps({
                    "success": False,
                    "error": "task_id required for update",
                    "suggestion": "Provide task_id to update"
                })

            # Build TaskUpdate model with only provided fields
            task_data = TaskUpdate(
                title=title,
                description=description,
                status=status,
                assignee=assignee,
                priority=priority,
                position=position
            )

            success, result = await task_service.update_task(task_id, task_data)

            if not success:
                return json.dumps({
                    "success": False,
                    "error": result.get("error", "Failed to update task"),
                    "suggestion": "Check task_id is valid and field values are correct"
                })

            task = result.get("task")
            if task:
                task = optimize_task_for_mcp(task)

            return json.dumps({
                "success": True,
                "task": task,
                "message": result.get("message", "Task updated successfully")
            })

        elif action == "delete":
            if not task_id:
                return json.dumps({
                    "success": False,
                    "error": "task_id required for delete",
                    "suggestion": "Provide task_id to delete"
                })

            success, result = await task_service.delete_task(task_id)

            if not success:
                return json.dumps({
                    "success": False,
                    "error": result.get("error", "Failed to delete task"),
                    "suggestion": "Check task_id is valid"
                })

            return json.dumps({
                "success": True,
                "message": result.get("message", "Task deleted successfully")
            })

        else:
            return json.dumps({
                "success": False,
                "error": f"Unknown action: {action}",
                "suggestion": "Use 'create', 'update', or 'delete'"
            })

    except Exception as e:
        logger.error(f"Error in manage_task ({action}): {e}", exc_info=True)
        return json.dumps({
            "success": False,
            "error": str(e),
            "suggestion": "Check error message and try again"
        })


@mcp.tool()
async def find_projects(
    project_id: str | None = None,
    page: int = 1,
    per_page: int = DEFAULT_PAGE_SIZE
) -> str:
    """Find and list projects (consolidated: list + get).

    PATTERN: Single tool for multiple query modes
    - project_id provided: Returns single project
    - No params: Returns all projects (paginated)

    Args:
        project_id: Project UUID to get specific project
        page: Page number for pagination (default: 1)
        per_page: Items per page (default: 10, max: 20)

    Returns:
        JSON string with projects or error (NEVER returns dict - Gotcha #3)

    Examples:
        find_projects() # All projects
        find_projects(project_id="proj-123") # Get specific project
    """
    try:
        # Limit per_page to MAX_TASKS_PER_PAGE
        per_page = min(per_page, MAX_TASKS_PER_PAGE)

        # Get database pool and initialize services
        db_pool = await get_pool()
        project_service = ProjectService(db_pool)

        # Single project get mode
        if project_id:
            success, result = await project_service.get_project(project_id)

            if not success:
                return json.dumps({
                    "success": False,
                    "error": result.get("error", "Project not found"),
                    "suggestion": "Verify the project ID is correct or use find_projects() to list all projects"
                })

            return json.dumps({
                "success": True,
                "project": result.get("project")
            })

        # List mode with pagination
        success, result = await project_service.list_projects(
            page=page,
            per_page=per_page
        )

        if not success:
            return json.dumps({
                "success": False,
                "error": result.get("error", "Failed to list projects"),
                "suggestion": "Check error message and try again"
            })

        projects = result.get("projects", [])
        total_count = result.get("total_count", 0)

        return json.dumps({
            "success": True,
            "projects": projects,
            "total_count": total_count,
            "count": len(projects),
            "page": page,
            "per_page": per_page
        })

    except Exception as e:
        logger.error(f"Error in find_projects: {e}", exc_info=True)
        return json.dumps({
            "success": False,
            "error": str(e),
            "suggestion": "Check error message and try again"
        })


@mcp.tool()
async def manage_project(
    action: str,
    project_id: str | None = None,
    name: str | None = None,
    description: str | None = None
) -> str:
    """Manage projects (consolidated: create/update/delete).

    Args:
        action: "create" | "update" | "delete"
        project_id: Project UUID for update/delete
        name: Project name (required for create)
        description: Project description

    Examples:
        manage_project("create", name="New Feature", description="Feature work")
        manage_project("update", project_id="p-1", description="Updated description")
        manage_project("delete", project_id="p-1")

    Returns:
        JSON string with result (NEVER returns dict - Gotcha #3)
    """
    try:
        # Get database pool and initialize services
        db_pool = await get_pool()
        project_service = ProjectService(db_pool)

        if action == "create":
            # VALIDATION: Require name for create
            if not name:
                return json.dumps({
                    "success": False,
                    "error": "name required for create",
                    "suggestion": "Provide a project name"
                })

            # Create ProjectCreate model
            project_data = ProjectCreate(
                name=name,
                description=description or ""
            )

            success, result = await project_service.create_project(project_data)

            if not success:
                return json.dumps({
                    "success": False,
                    "error": result.get("error", "Failed to create project"),
                    "suggestion": "Check error message and ensure project name is valid"
                })

            return json.dumps({
                "success": True,
                "project": result.get("project"),
                "message": "Project created successfully"
            })

        elif action == "update":
            if not project_id:
                return json.dumps({
                    "success": False,
                    "error": "project_id required for update",
                    "suggestion": "Provide project_id to update"
                })

            # Build ProjectUpdate model with only provided fields
            project_data = ProjectUpdate(
                name=name,
                description=description
            )

            success, result = await project_service.update_project(project_id, project_data)

            if not success:
                return json.dumps({
                    "success": False,
                    "error": result.get("error", "Failed to update project"),
                    "suggestion": "Check project_id is valid"
                })

            return json.dumps({
                "success": True,
                "project": result.get("project"),
                "message": result.get("message", "Project updated successfully")
            })

        elif action == "delete":
            if not project_id:
                return json.dumps({
                    "success": False,
                    "error": "project_id required for delete",
                    "suggestion": "Provide project_id to delete"
                })

            success, result = await project_service.delete_project(project_id)

            if not success:
                return json.dumps({
                    "success": False,
                    "error": result.get("error", "Failed to delete project"),
                    "suggestion": "Check project_id is valid. Note: Projects with tasks cannot be deleted."
                })

            return json.dumps({
                "success": True,
                "message": result.get("message", "Project deleted successfully")
            })

        else:
            return json.dumps({
                "success": False,
                "error": f"Unknown action: {action}",
                "suggestion": "Use 'create', 'update', or 'delete'"
            })

    except Exception as e:
        logger.error(f"Error in manage_project ({action}): {e}", exc_info=True)
        return json.dumps({
            "success": False,
            "error": str(e),
            "suggestion": "Check error message and try again"
        })


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
