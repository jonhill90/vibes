"""MCP Integration Tests - End-to-End Tool Validation.

This module tests the MCP server tools end-to-end to ensure:
1. Tools return JSON strings (not dicts) - Critical MCP requirement
2. find_tasks() works in all modes (list, filter, get single)
3. manage_task() handles create/update/delete actions
4. Error responses have structured format with success, error, suggestion
5. Response sizes are optimized (descriptions truncated, pagination limits)
6. All critical gotchas from PRP are addressed

Pattern Source: prps/task_management_ui.md Task 23
Reference Pattern: infra/archon/python/tests/mcp_server/features/tasks/test_task_tools.py
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.mcp_server import mcp


@pytest.fixture
def mock_db_pool():
    """Create a mock database pool for testing."""
    mock_pool = MagicMock()
    return mock_pool


@pytest.fixture
def mock_task_service():
    """Create a mock TaskService for testing."""
    mock_service = MagicMock()
    # Default success responses
    mock_service.list_tasks = AsyncMock(return_value=(
        True,
        {
            "tasks": [
                {
                    "id": "task-123",
                    "project_id": "proj-456",
                    "title": "Test Task",
                    "description": "Short description",
                    "status": "todo",
                    "assignee": "User",
                    "priority": "medium",
                    "position": 0,
                },
                {
                    "id": "task-789",
                    "project_id": "proj-456",
                    "title": "Another Task",
                    "description": "Another description",
                    "status": "doing",
                    "assignee": "AI",
                    "priority": "high",
                    "position": 1,
                },
            ],
            "total_count": 2,
        }
    ))
    mock_service.get_task = AsyncMock(return_value=(
        True,
        {
            "task": {
                "id": "task-123",
                "project_id": "proj-456",
                "title": "Test Task",
                "description": "Full description here",
                "status": "todo",
                "assignee": "User",
                "priority": "medium",
                "position": 0,
            }
        }
    ))
    mock_service.create_task = AsyncMock(return_value=(
        True,
        {
            "task": {
                "id": "task-new",
                "project_id": "proj-456",
                "title": "New Task",
                "description": "Created task",
                "status": "todo",
                "assignee": "User",
                "priority": "medium",
                "position": 0,
            },
            "message": "Task created successfully"
        }
    ))
    mock_service.update_task = AsyncMock(return_value=(
        True,
        {
            "task": {
                "id": "task-123",
                "project_id": "proj-456",
                "title": "Updated Task",
                "description": "Updated description",
                "status": "doing",
                "assignee": "User",
                "priority": "high",
                "position": 0,
            },
            "message": "Task updated successfully"
        }
    ))
    mock_service.delete_task = AsyncMock(return_value=(
        True,
        {"message": "Task deleted successfully"}
    ))
    return mock_service


@pytest.mark.asyncio
async def test_find_tasks_returns_json_string(mock_db_pool, mock_task_service):
    """Test that find_tasks() returns a JSON string, not a dict.

    CRITICAL: MCP tools MUST return JSON strings (Gotcha #3).
    This test validates the most important MCP requirement.
    """
    with patch("src.mcp_server.get_pool", new_callable=AsyncMock) as mock_get_pool, \
         patch("src.mcp_server.TaskService") as mock_service_class:

        mock_get_pool.return_value = mock_db_pool
        mock_service_class.return_value = mock_task_service

        # Get the find_tasks tool function directly
        find_tasks = None
        for tool in mcp._tools:
            if tool.fn.__name__ == "find_tasks":
                find_tasks = tool.fn
                break

        assert find_tasks is not None, "find_tasks tool not found"

        # Call the tool
        result = await find_tasks()

        # CRITICAL: Must be a string, not dict
        assert isinstance(result, str), "MCP tools must return JSON strings, not dicts"

        # Verify it's valid JSON
        parsed = json.loads(result)
        assert isinstance(parsed, dict), "Result should parse to a dict"
        assert "success" in parsed, "Response should have success field"
        assert parsed["success"] is True, "Should be successful"


@pytest.mark.asyncio
async def test_find_tasks_with_task_id_returns_single_task(mock_db_pool, mock_task_service):
    """Test that find_tasks(task_id='uuid') returns a single task with full details.

    When task_id is provided, the tool should:
    - Return single task object (not array)
    - Include full details
    - Still truncate description (Gotcha #3)
    """
    with patch("src.mcp_server.get_pool", new_callable=AsyncMock) as mock_get_pool, \
         patch("src.mcp_server.TaskService") as mock_service_class:

        mock_get_pool.return_value = mock_db_pool
        mock_service_class.return_value = mock_task_service

        # Get the find_tasks tool function
        find_tasks = None
        for tool in mcp._tools:
            if tool.fn.__name__ == "find_tasks":
                find_tasks = tool.fn
                break

        # Call with task_id
        result = await find_tasks(task_id="task-123")

        # Verify string response
        assert isinstance(result, str), "Must return JSON string"

        # Parse and validate structure
        parsed = json.loads(result)
        assert parsed["success"] is True
        assert "task" in parsed, "Should return single task object"
        assert "tasks" not in parsed, "Should not return tasks array for single item"

        # Verify task structure
        task = parsed["task"]
        assert task["id"] == "task-123"
        assert "title" in task
        assert "description" in task
        assert "status" in task

        # Verify service was called correctly
        mock_task_service.get_task.assert_called_once_with("task-123")


@pytest.mark.asyncio
async def test_find_tasks_with_filters(mock_db_pool, mock_task_service):
    """Test that find_tasks() supports filtering by status, project, assignee.

    Filtering should:
    - Accept filter_by and filter_value parameters
    - Build correct filters dict for service
    - Return paginated results
    """
    with patch("src.mcp_server.get_pool", new_callable=AsyncMock) as mock_get_pool, \
         patch("src.mcp_server.TaskService") as mock_service_class:

        mock_get_pool.return_value = mock_db_pool
        mock_service_class.return_value = mock_task_service

        # Get the find_tasks tool function
        find_tasks = None
        for tool in mcp._tools:
            if tool.fn.__name__ == "find_tasks":
                find_tasks = tool.fn
                break

        # Call with status filter
        result = await find_tasks(filter_by="status", filter_value="todo")

        # Verify string response
        assert isinstance(result, str), "Must return JSON string"

        # Parse and validate
        parsed = json.loads(result)
        assert parsed["success"] is True
        assert "tasks" in parsed, "Should return tasks array"
        assert "total_count" in parsed, "Should include total count"
        assert "page" in parsed, "Should include pagination info"
        assert "per_page" in parsed

        # Verify service called with correct filters
        call_args = mock_task_service.list_tasks.call_args
        filters = call_args.kwargs["filters"]
        assert filters["status"] == "todo", "Should pass status filter"


@pytest.mark.asyncio
async def test_find_tasks_respects_per_page_limit(mock_db_pool, mock_task_service):
    """Test that find_tasks() limits per_page to MAX_TASKS_PER_PAGE (20).

    CRITICAL: Gotcha #3 - Must limit per_page to prevent oversized responses.
    """
    with patch("src.mcp_server.get_pool", new_callable=AsyncMock) as mock_get_pool, \
         patch("src.mcp_server.TaskService") as mock_service_class:

        mock_get_pool.return_value = mock_db_pool
        mock_service_class.return_value = mock_task_service

        # Get the find_tasks tool function
        find_tasks = None
        for tool in mcp._tools:
            if tool.fn.__name__ == "find_tasks":
                find_tasks = tool.fn
                break

        # Try to request 100 items per page (should be limited to 20)
        result = await find_tasks(per_page=100)

        # Verify service was called with limited per_page
        call_args = mock_task_service.list_tasks.call_args
        actual_per_page = call_args.kwargs["per_page"]
        assert actual_per_page == 20, "Should limit per_page to MAX_TASKS_PER_PAGE (20)"


@pytest.mark.asyncio
async def test_manage_task_create_action(mock_db_pool, mock_task_service):
    """Test that manage_task('create', ...) creates a new task.

    Create action should:
    - Require project_id and title
    - Accept optional fields with defaults
    - Return created task with server ID
    """
    with patch("src.mcp_server.get_pool", new_callable=AsyncMock) as mock_get_pool, \
         patch("src.mcp_server.TaskService") as mock_service_class:

        mock_get_pool.return_value = mock_db_pool
        mock_service_class.return_value = mock_task_service

        # Get the manage_task tool function
        manage_task = None
        for tool in mcp._tools:
            if tool.fn.__name__ == "manage_task":
                manage_task = tool.fn
                break

        assert manage_task is not None, "manage_task tool not found"

        # Create a task
        result = await manage_task(
            action="create",
            project_id="proj-456",
            title="New Test Task",
            description="Task description",
            status="todo",
            assignee="User",
            priority="high"
        )

        # Verify string response
        assert isinstance(result, str), "Must return JSON string"

        # Parse and validate
        parsed = json.loads(result)
        assert parsed["success"] is True
        assert "task" in parsed, "Should return created task"
        assert "task_id" in parsed, "Should include task_id for convenience"
        assert parsed["task"]["id"] == "task-new"
        assert "message" in parsed

        # Verify service was called
        mock_task_service.create_task.assert_called_once()


@pytest.mark.asyncio
async def test_manage_task_create_requires_project_and_title(mock_db_pool, mock_task_service):
    """Test that manage_task('create') validates required fields.

    Should return structured error when project_id or title missing.
    """
    with patch("src.mcp_server.get_pool", new_callable=AsyncMock) as mock_get_pool, \
         patch("src.mcp_server.TaskService") as mock_service_class:

        mock_get_pool.return_value = mock_db_pool
        mock_service_class.return_value = mock_task_service

        # Get the manage_task tool function
        manage_task = None
        for tool in mcp._tools:
            if tool.fn.__name__ == "manage_task":
                manage_task = tool.fn
                break

        # Try to create without project_id
        result = await manage_task(action="create", title="Test")

        # Verify error response
        parsed = json.loads(result)
        assert parsed["success"] is False
        assert "error" in parsed
        assert "suggestion" in parsed, "Should include helpful suggestion"
        assert "project_id" in parsed["error"].lower()


@pytest.mark.asyncio
async def test_manage_task_update_action(mock_db_pool, mock_task_service):
    """Test that manage_task('update', ...) updates an existing task.

    Update action should:
    - Require task_id
    - Accept partial updates
    - Return updated task
    """
    with patch("src.mcp_server.get_pool", new_callable=AsyncMock) as mock_get_pool, \
         patch("src.mcp_server.TaskService") as mock_service_class:

        mock_get_pool.return_value = mock_db_pool
        mock_service_class.return_value = mock_task_service

        # Get the manage_task tool function
        manage_task = None
        for tool in mcp._tools:
            if tool.fn.__name__ == "manage_task":
                manage_task = tool.fn
                break

        # Update task status
        result = await manage_task(
            action="update",
            task_id="task-123",
            status="doing",
            assignee="AI"
        )

        # Verify string response
        assert isinstance(result, str), "Must return JSON string"

        # Parse and validate
        parsed = json.loads(result)
        assert parsed["success"] is True
        assert "task" in parsed
        assert parsed["task"]["status"] == "doing"
        assert "message" in parsed

        # Verify service called with task_id and updates
        mock_task_service.update_task.assert_called_once()


@pytest.mark.asyncio
async def test_manage_task_delete_action(mock_db_pool, mock_task_service):
    """Test that manage_task('delete', ...) deletes a task.

    Delete action should:
    - Require task_id
    - Return success message
    - Not return task object
    """
    with patch("src.mcp_server.get_pool", new_callable=AsyncMock) as mock_get_pool, \
         patch("src.mcp_server.TaskService") as mock_service_class:

        mock_get_pool.return_value = mock_db_pool
        mock_service_class.return_value = mock_task_service

        # Get the manage_task tool function
        manage_task = None
        for tool in mcp._tools:
            if tool.fn.__name__ == "manage_task":
                manage_task = tool.fn
                break

        # Delete task
        result = await manage_task(action="delete", task_id="task-123")

        # Verify string response
        assert isinstance(result, str), "Must return JSON string"

        # Parse and validate
        parsed = json.loads(result)
        assert parsed["success"] is True
        assert "message" in parsed
        assert "task" not in parsed, "Delete should not return task object"

        # Verify service called
        mock_task_service.delete_task.assert_called_once_with("task-123")


@pytest.mark.asyncio
async def test_error_responses_have_structured_format(mock_db_pool, mock_task_service):
    """Test that errors return structured format with success, error, suggestion.

    Error responses must have:
    - success: false
    - error: descriptive error message
    - suggestion: helpful next steps
    """
    # Mock a service error
    mock_task_service.get_task = AsyncMock(return_value=(
        False,
        {"error": "Task not found"}
    ))

    with patch("src.mcp_server.get_pool", new_callable=AsyncMock) as mock_get_pool, \
         patch("src.mcp_server.TaskService") as mock_service_class:

        mock_get_pool.return_value = mock_db_pool
        mock_service_class.return_value = mock_task_service

        # Get the find_tasks tool function
        find_tasks = None
        for tool in mcp._tools:
            if tool.fn.__name__ == "find_tasks":
                find_tasks = tool.fn
                break

        # Try to get non-existent task
        result = await find_tasks(task_id="nonexistent")

        # Verify string response
        assert isinstance(result, str), "Must return JSON string"

        # Parse and validate error structure
        parsed = json.loads(result)
        assert parsed["success"] is False, "Should indicate failure"
        assert "error" in parsed, "Should include error message"
        assert "suggestion" in parsed, "Should include helpful suggestion"
        assert isinstance(parsed["error"], str), "Error should be string"
        assert isinstance(parsed["suggestion"], str), "Suggestion should be string"


@pytest.mark.asyncio
async def test_description_truncation_works(mock_db_pool, mock_task_service):
    """Test that descriptions are truncated to prevent oversized responses.

    CRITICAL: Gotcha #3 - Always truncate descriptions to 1000 chars.
    This test verifies the truncation logic works correctly.
    """
    # Create mock task with very long description
    long_description = "x" * 2000  # 2000 characters
    mock_task_service.get_task = AsyncMock(return_value=(
        True,
        {
            "task": {
                "id": "task-123",
                "project_id": "proj-456",
                "title": "Test Task",
                "description": long_description,
                "status": "todo",
                "assignee": "User",
                "priority": "medium",
                "position": 0,
            }
        }
    ))

    with patch("src.mcp_server.get_pool", new_callable=AsyncMock) as mock_get_pool, \
         patch("src.mcp_server.TaskService") as mock_service_class:

        mock_get_pool.return_value = mock_db_pool
        mock_service_class.return_value = mock_task_service

        # Get the find_tasks tool function
        find_tasks = None
        for tool in mcp._tools:
            if tool.fn.__name__ == "find_tasks":
                find_tasks = tool.fn
                break

        # Get task with long description
        result = await find_tasks(task_id="task-123")

        # Parse response
        parsed = json.loads(result)
        task = parsed["task"]

        # Verify description was truncated
        assert len(task["description"]) <= 1000, "Description should be truncated to max 1000 chars"
        assert task["description"].endswith("..."), "Truncated description should end with ..."


@pytest.mark.asyncio
async def test_response_size_under_100kb(mock_db_pool, mock_task_service):
    """Test that response sizes are reasonable (< 100KB for list of 20 tasks).

    This validates the optimization strategies work:
    - Description truncation
    - Pagination limits
    - Field optimization
    """
    # Create 20 tasks with moderate data
    tasks = []
    for i in range(20):
        tasks.append({
            "id": f"task-{i}",
            "project_id": "proj-456",
            "title": f"Task {i}",
            "description": "x" * 500,  # 500 char description
            "status": "todo",
            "assignee": "User",
            "priority": "medium",
            "position": i,
        })

    mock_task_service.list_tasks = AsyncMock(return_value=(
        True,
        {"tasks": tasks, "total_count": 20}
    ))

    with patch("src.mcp_server.get_pool", new_callable=AsyncMock) as mock_get_pool, \
         patch("src.mcp_server.TaskService") as mock_service_class:

        mock_get_pool.return_value = mock_db_pool
        mock_service_class.return_value = mock_task_service

        # Get the find_tasks tool function
        find_tasks = None
        for tool in mcp._tools:
            if tool.fn.__name__ == "find_tasks":
                find_tasks = tool.fn
                break

        # Get max page of tasks
        result = await find_tasks(per_page=20)

        # Verify response size
        response_size = len(result.encode('utf-8'))
        assert response_size < 100_000, f"Response size ({response_size} bytes) should be under 100KB"


@pytest.mark.asyncio
async def test_find_tasks_handles_exceptions(mock_db_pool, mock_task_service):
    """Test that unexpected exceptions are caught and returned as structured errors."""
    # Mock an exception
    mock_task_service.list_tasks = AsyncMock(side_effect=Exception("Database connection failed"))

    with patch("src.mcp_server.get_pool", new_callable=AsyncMock) as mock_get_pool, \
         patch("src.mcp_server.TaskService") as mock_service_class:

        mock_get_pool.return_value = mock_db_pool
        mock_service_class.return_value = mock_task_service

        # Get the find_tasks tool function
        find_tasks = None
        for tool in mcp._tools:
            if tool.fn.__name__ == "find_tasks":
                find_tasks = tool.fn
                break

        # Call should not raise, should return error
        result = await find_tasks()

        # Verify error response
        parsed = json.loads(result)
        assert parsed["success"] is False
        assert "error" in parsed
        assert "Database connection failed" in parsed["error"]
        assert "suggestion" in parsed


@pytest.mark.asyncio
async def test_manage_task_handles_exceptions(mock_db_pool, mock_task_service):
    """Test that manage_task handles exceptions gracefully."""
    # Mock an exception
    mock_task_service.create_task = AsyncMock(side_effect=Exception("Validation failed"))

    with patch("src.mcp_server.get_pool", new_callable=AsyncMock) as mock_get_pool, \
         patch("src.mcp_server.TaskService") as mock_service_class:

        mock_get_pool.return_value = mock_db_pool
        mock_service_class.return_value = mock_task_service

        # Get the manage_task tool function
        manage_task = None
        for tool in mcp._tools:
            if tool.fn.__name__ == "manage_task":
                manage_task = tool.fn
                break

        # Try to create task
        result = await manage_task(
            action="create",
            project_id="proj-456",
            title="Test"
        )

        # Verify error response
        parsed = json.loads(result)
        assert parsed["success"] is False
        assert "error" in parsed
        assert "Validation failed" in parsed["error"]
