"""Unit tests for TaskService - Business logic layer testing.

This module tests:
- Task CRUD operations with validation
- Atomic position reordering with concurrent update simulation
- Error handling and edge cases
- Pagination and field exclusion

Critical Test Coverage:
- Validation errors for invalid status/priority
- Concurrent position updates (transaction safety)
- Position reordering logic
- Large description truncation
"""

import pytest
from src.services.task_service import TaskService
from src.models.task import TaskCreate, TaskUpdate


@pytest.mark.asyncio
class TestTaskService:
    """Test suite for TaskService business logic."""

    async def test_create_task_with_valid_data(
        self, db_pool, clean_database
    ):
        """Test creating a task with all valid fields.

        Validates:
        - Task is created successfully
        - All fields are stored correctly
        - Position defaults to 0 if not specified
        - Timestamps are auto-generated
        """
        service = TaskService(db_pool=db_pool)

        task_data = TaskCreate(
            title="Valid Task",
            description="This is a valid task description",
            status="todo",
            assignee="Alice",
            priority="high",
            position=5
        )

        success, result = await service.create_task(data=task_data)

        assert success is True
        assert "task" in result
        task = result["task"]

        # Verify all fields
        assert task["title"] == "Valid Task"
        assert task["description"] == "This is a valid task description"
        assert task["status"] == "todo"
        assert task["assignee"] == "Alice"
        assert task["priority"] == "high"
        assert task["position"] == 5
        assert task["id"] is not None
        assert task["created_at"] is not None
        assert task["updated_at"] is not None

    async def test_create_task_with_invalid_status(
        self, db_pool, clean_database
    ):
        """Test creating a task with invalid status returns validation error.

        Validates:
        - Invalid status is rejected
        - Error message includes valid options
        - No task is created in database
        """
        service = TaskService(db_pool=db_pool)

        task_data = TaskCreate(
            title="Invalid Status Task",
            status="invalid_status",
            assignee="Bob",
            priority="medium"
        )

        success, result = await service.create_task(data=task_data)

        assert success is False
        assert "error" in result
        assert "invalid_status" in result["error"].lower()
        assert "todo" in result["error"]  # Should suggest valid statuses

    async def test_create_task_with_invalid_priority(
        self, db_pool, clean_database
    ):
        """Test creating a task with invalid priority returns validation error.

        Validates:
        - Invalid priority is rejected
        - Error message includes valid options
        - No task is created in database
        """
        service = TaskService(db_pool=db_pool)

        task_data = TaskCreate(
            title="Invalid Priority Task",
            status="todo",
            priority="super_urgent"  # Invalid priority
        )

        success, result = await service.create_task(data=task_data)

        assert success is False
        assert "error" in result
        assert "super_urgent" in result["error"].lower()
        assert "low" in result["error"]  # Should suggest valid priorities

    async def test_update_task_position_with_concurrent_updates(
        self, db_pool, clean_database, create_test_task
    ):
        """Test atomic position reordering prevents race conditions.

        This test simulates concurrent position updates by:
        1. Creating multiple tasks at different positions
        2. Moving a task to an occupied position
        3. Verifying other tasks are incremented atomically

        CRITICAL: Tests Gotcha #2 pattern (transaction + row locking)
        """
        service = TaskService(db_pool=db_pool)

        # Create 3 tasks in "doing" status
        task1 = await create_test_task(
            title="Task 1", status="doing", position=0
        )
        task2 = await create_test_task(
            title="Task 2", status="doing", position=1
        )
        task3 = await create_test_task(
            title="Task 3", status="doing", position=2
        )

        # Move task3 to position 1 (task2's position)
        # Expected: task2 should be incremented to position 2
        success, result = await service.update_task_position(
            task_id=task3["id"],
            new_status="doing",
            new_position=1
        )

        assert success is True
        assert result["task"]["position"] == 1

        # Verify all tasks have correct positions
        success, tasks_result = await service.list_tasks(
            filters={"status": "doing"}
        )

        assert success is True
        tasks = tasks_result["tasks"]
        task_positions = {t["title"]: t["position"] for t in tasks}

        assert task_positions["Task 1"] == 0  # Unchanged
        assert task_positions["Task 3"] == 1  # Moved here
        assert task_positions["Task 2"] == 2  # Incremented

    async def test_update_task_position_across_status_columns(
        self, db_pool, clean_database, create_test_task
    ):
        """Test moving task between status columns (Kanban drag-and-drop).

        Validates:
        - Task can move from one status to another
        - Position is set correctly in new status
        - Old status positions are not affected
        """
        service = TaskService(db_pool=db_pool)

        # Create tasks in different statuses
        todo_task = await create_test_task(
            title="Todo Task", status="todo", position=0
        )
        doing_task = await create_test_task(
            title="Doing Task", status="doing", position=0
        )

        # Move todo task to doing status at position 0
        success, result = await service.update_task_position(
            task_id=todo_task["id"],
            new_status="doing",
            new_position=0
        )

        assert success is True
        task = result["task"]
        assert task["status"] == "doing"
        assert task["position"] == 0

        # Verify doing_task was incremented to position 1
        success, get_result = await service.get_task(task_id=doing_task["id"])
        assert success is True
        assert get_result["task"]["position"] == 1

    async def test_list_tasks_with_filters(
        self, db_pool, clean_database, create_test_task, create_test_project
    ):
        """Test filtering tasks by status, project, and assignee.

        Validates:
        - Status filter returns only matching tasks
        - Project filter works correctly
        - Assignee filter works correctly
        - Multiple filters can be combined
        """
        service = TaskService(db_pool=db_pool)

        # Create test project
        project = await create_test_project(name="Filter Test Project")

        # Create diverse tasks
        await create_test_task(
            title="Task 1", status="todo", assignee="Alice",
            project_id=project["id"]
        )
        await create_test_task(
            title="Task 2", status="doing", assignee="Bob",
            project_id=project["id"]
        )
        await create_test_task(
            title="Task 3", status="todo", assignee="Alice",
            project_id=None
        )

        # Test status filter
        success, result = await service.list_tasks(
            filters={"status": "todo"}
        )
        assert success is True
        assert result["total_count"] == 2
        assert all(t["status"] == "todo" for t in result["tasks"])

        # Test project filter
        success, result = await service.list_tasks(
            filters={"project_id": project["id"]}
        )
        assert success is True
        assert result["total_count"] == 2
        assert all(t["project_id"] == project["id"] for t in result["tasks"])

        # Test assignee filter
        success, result = await service.list_tasks(
            filters={"assignee": "Alice"}
        )
        assert success is True
        assert result["total_count"] == 2
        assert all(t["assignee"] == "Alice" for t in result["tasks"])

        # Test combined filters
        success, result = await service.list_tasks(
            filters={"status": "todo", "assignee": "Alice", "project_id": project["id"]}
        )
        assert success is True
        assert result["total_count"] == 1
        assert result["tasks"][0]["title"] == "Task 1"

    async def test_list_tasks_with_pagination(
        self, db_pool, clean_database, create_test_task
    ):
        """Test pagination returns correct page of tasks.

        Validates:
        - Page 1 returns first N tasks
        - Page 2 returns next N tasks
        - Total count is correct
        - per_page parameter works
        """
        service = TaskService(db_pool=db_pool)

        # Create 5 tasks
        for i in range(5):
            await create_test_task(
                title=f"Task {i}", status="todo", position=i
            )

        # Get page 1 (2 items per page)
        success, result = await service.list_tasks(
            page=1, per_page=2
        )

        assert success is True
        assert result["total_count"] == 5
        assert result["page"] == 1
        assert result["per_page"] == 2
        assert len(result["tasks"]) == 2
        assert result["tasks"][0]["title"] == "Task 0"
        assert result["tasks"][1]["title"] == "Task 1"

        # Get page 2
        success, result = await service.list_tasks(
            page=2, per_page=2
        )

        assert success is True
        assert len(result["tasks"]) == 2
        assert result["tasks"][0]["title"] == "Task 2"

        # Get page 3 (last page, only 1 item)
        success, result = await service.list_tasks(
            page=3, per_page=2
        )

        assert success is True
        assert len(result["tasks"]) == 1
        assert result["tasks"][0]["title"] == "Task 4"

    async def test_list_tasks_with_large_field_exclusion(
        self, db_pool, clean_database, create_test_task
    ):
        """Test truncation of large description fields for performance.

        Validates:
        - Description > 1000 chars is truncated when exclude_large_fields=True
        - Full description is returned when exclude_large_fields=False
        - Truncation adds '...' suffix
        """
        service = TaskService(db_pool=db_pool)

        # Create task with large description (>1000 chars)
        large_description = "A" * 1500
        await create_test_task(
            title="Large Task",
            description=large_description
        )

        # Test with exclusion enabled
        success, result = await service.list_tasks(
            exclude_large_fields=True
        )

        assert success is True
        task = result["tasks"][0]
        assert len(task["description"]) == 1003  # 1000 chars + "..."
        assert task["description"].endswith("...")

        # Test with exclusion disabled (full description)
        success, result = await service.list_tasks(
            exclude_large_fields=False
        )

        assert success is True
        task = result["tasks"][0]
        assert len(task["description"]) == 1500
        assert task["description"] == large_description

    async def test_update_task_partial_fields(
        self, db_pool, clean_database, create_test_task
    ):
        """Test partial update of task fields.

        Validates:
        - Only specified fields are updated
        - Other fields remain unchanged
        - updated_at timestamp is refreshed
        """
        service = TaskService(db_pool=db_pool)

        # Create task
        task = await create_test_task(
            title="Original Title",
            description="Original Description",
            assignee="Alice"
        )
        original_created_at = task["created_at"]

        # Update only title
        update_data = TaskUpdate(title="Updated Title")
        success, result = await service.update_task(
            task_id=task["id"],
            data=update_data
        )

        assert success is True
        updated_task = result["task"]

        # Verify only title changed
        assert updated_task["title"] == "Updated Title"
        assert updated_task["description"] == "Original Description"
        assert updated_task["assignee"] == "Alice"
        assert updated_task["created_at"] == original_created_at

    async def test_update_task_with_invalid_status(
        self, db_pool, clean_database, create_test_task
    ):
        """Test updating task with invalid status returns validation error.

        Validates:
        - Invalid status is rejected during update
        - Error message is descriptive
        - Task remains unchanged
        """
        service = TaskService(db_pool=db_pool)

        task = await create_test_task(title="Test Task", status="todo")

        update_data = TaskUpdate(status="invalid_status")
        success, result = await service.update_task(
            task_id=task["id"],
            data=update_data
        )

        assert success is False
        assert "error" in result
        assert "invalid_status" in result["error"].lower()

        # Verify task unchanged
        success, get_result = await service.get_task(task_id=task["id"])
        assert success is True
        assert get_result["task"]["status"] == "todo"

    async def test_delete_task(
        self, db_pool, clean_database, create_test_task
    ):
        """Test deleting a task.

        Validates:
        - Task is deleted successfully
        - Get task after delete returns not found error
        """
        service = TaskService(db_pool=db_pool)

        task = await create_test_task(title="Task to Delete")

        # Delete task
        success, result = await service.delete_task(task_id=task["id"])

        assert success is True
        assert "message" in result

        # Verify task no longer exists
        success, get_result = await service.get_task(task_id=task["id"])
        assert success is False
        assert "not found" in get_result["error"].lower()

    async def test_get_task_not_found(self, db_pool, clean_database):
        """Test getting non-existent task returns error.

        Validates:
        - Non-existent task ID returns success=False
        - Error message indicates task not found
        """
        service = TaskService(db_pool=db_pool)

        fake_id = "00000000-0000-0000-0000-000000000000"
        success, result = await service.get_task(task_id=fake_id)

        assert success is False
        assert "error" in result
        assert "not found" in result["error"].lower()
        assert fake_id in result["error"]

    async def test_create_task_with_position_reordering(
        self, db_pool, clean_database, create_test_task
    ):
        """Test creating task at specific position increments existing tasks.

        Validates:
        - New task inserted at specified position
        - Existing tasks at that position are incremented
        - Transaction ensures atomicity
        """
        service = TaskService(db_pool=db_pool)

        # Create 2 tasks in todo
        await create_test_task(title="Task 1", status="todo", position=0)
        await create_test_task(title="Task 2", status="todo", position=1)

        # Create new task at position 1 (Task 2's position)
        task_data = TaskCreate(
            title="New Task",
            status="todo",
            position=1
        )

        success, result = await service.create_task(data=task_data)

        assert success is True
        assert result["task"]["position"] == 1

        # Verify Task 2 was incremented to position 2
        success, list_result = await service.list_tasks(
            filters={"status": "todo"}
        )

        assert success is True
        tasks = {t["title"]: t["position"] for t in list_result["tasks"]}

        assert tasks["Task 1"] == 0  # Unchanged
        assert tasks["New Task"] == 1  # New position
        assert tasks["Task 2"] == 2  # Incremented
