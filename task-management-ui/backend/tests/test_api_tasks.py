"""Integration tests for Task API endpoints.

This module tests:
- RESTful task endpoints (GET, POST, PATCH, DELETE)
- Request validation and error responses
- ETag caching for list endpoint
- Position update endpoint with atomic reordering

Critical Test Coverage:
- HTTP status codes (200, 201, 400, 404, 304)
- Request/response validation
- Query parameter filtering
- Concurrent position updates via API
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestTaskAPI:
    """Test suite for Task API endpoints."""

    async def test_list_tasks_empty(
        self, test_client: AsyncClient, clean_database
    ):
        """Test GET /api/tasks returns empty list when no tasks exist.

        Validates:
        - Status code 200
        - Empty tasks array
        - Total count is 0
        - ETag header is present
        """
        response = await test_client.get("/api/tasks")

        assert response.status_code == 200
        data = response.json()

        assert data["tasks"] == []
        assert data["total_count"] == 0
        assert data["page"] == 1
        assert data["per_page"] == 50
        assert "ETag" in response.headers

    async def test_list_tasks_with_query_filters(
        self, test_client: AsyncClient, clean_database, create_test_task
    ):
        """Test GET /api/tasks with query parameters filters tasks.

        Validates:
        - status filter works
        - assignee filter works
        - Filtered results are correct
        """
        # Create diverse tasks
        await create_test_task(title="Task 1", status="todo", assignee="Alice")
        await create_test_task(title="Task 2", status="doing", assignee="Bob")
        await create_test_task(title="Task 3", status="todo", assignee="Alice")

        # Filter by status
        response = await test_client.get("/api/tasks?status=todo")
        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 2
        assert all(t["status"] == "todo" for t in data["tasks"])

        # Filter by assignee
        response = await test_client.get("/api/tasks?assignee=Alice")
        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 2
        assert all(t["assignee"] == "Alice" for t in data["tasks"])

        # Combined filters
        response = await test_client.get("/api/tasks?status=todo&assignee=Alice")
        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 2

    async def test_list_tasks_with_pagination(
        self, test_client: AsyncClient, clean_database, create_test_task
    ):
        """Test GET /api/tasks with page and per_page parameters.

        Validates:
        - Pagination parameters work correctly
        - Correct number of items per page
        - Page metadata is accurate
        """
        # Create 5 tasks
        for i in range(5):
            await create_test_task(title=f"Task {i}", position=i)

        # Get page 1 with 2 items
        response = await test_client.get("/api/tasks?page=1&per_page=2")
        assert response.status_code == 200
        data = response.json()

        assert data["page"] == 1
        assert data["per_page"] == 2
        assert data["total_count"] == 5
        assert len(data["tasks"]) == 2

        # Get page 2
        response = await test_client.get("/api/tasks?page=2&per_page=2")
        assert response.status_code == 200
        data = response.json()

        assert data["page"] == 2
        assert len(data["tasks"]) == 2

    async def test_list_tasks_with_invalid_status_filter(
        self, test_client: AsyncClient, clean_database
    ):
        """Test GET /api/tasks with invalid status returns 400.

        Validates:
        - Invalid status filter returns error
        - Error message is descriptive
        """
        response = await test_client.get("/api/tasks?status=invalid_status")

        assert response.status_code == 400
        assert "invalid_status" in response.text.lower()

    async def test_list_tasks_etag_caching(
        self, test_client: AsyncClient, clean_database, create_test_task
    ):
        """Test ETag caching returns 304 Not Modified when data unchanged.

        Validates:
        - First request returns ETag header
        - Second request with If-None-Match returns 304
        - Data change invalidates ETag (returns 200)
        """
        # Create a task
        await create_test_task(title="Cached Task")

        # First request - get ETag
        response1 = await test_client.get("/api/tasks")
        assert response1.status_code == 200
        etag = response1.headers.get("ETag")
        assert etag is not None

        # Second request with ETag - should return 304
        response2 = await test_client.get(
            "/api/tasks",
            headers={"If-None-Match": etag}
        )
        assert response2.status_code == 304

        # Create another task (data changed)
        await create_test_task(title="New Task")

        # Third request with old ETag - should return 200 (data changed)
        response3 = await test_client.get(
            "/api/tasks",
            headers={"If-None-Match": etag}
        )
        assert response3.status_code == 200
        new_etag = response3.headers.get("ETag")
        assert new_etag != etag

    async def test_get_task_by_id(
        self, test_client: AsyncClient, clean_database, create_test_task
    ):
        """Test GET /api/tasks/{id} returns single task.

        Validates:
        - Status code 200
        - Correct task data returned
        - All fields present
        """
        task = await create_test_task(
            title="Test Task",
            description="Test Description",
            assignee="Alice"
        )

        response = await test_client.get(f"/api/tasks/{task['id']}")

        assert response.status_code == 200
        data = response.json()

        assert "task" in data
        task_data = data["task"]
        assert task_data["id"] == str(task["id"])
        assert task_data["title"] == "Test Task"
        assert task_data["description"] == "Test Description"
        assert task_data["assignee"] == "Alice"

    async def test_get_task_not_found(
        self, test_client: AsyncClient, clean_database
    ):
        """Test GET /api/tasks/{id} with non-existent ID returns 404.

        Validates:
        - Status code 404
        - Error message indicates not found
        """
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await test_client.get(f"/api/tasks/{fake_id}")

        assert response.status_code == 404
        assert "not found" in response.text.lower()

    async def test_create_task_with_valid_data(
        self, test_client: AsyncClient, clean_database
    ):
        """Test POST /api/tasks creates task with valid data.

        Validates:
        - Status code 201
        - Task is created with all fields
        - Response includes created task
        """
        task_data = {
            "title": "New API Task",
            "description": "Created via API",
            "status": "todo",
            "assignee": "Bob",
            "priority": "high",
            "position": 0
        }

        response = await test_client.post("/api/tasks", json=task_data)

        assert response.status_code == 201
        data = response.json()

        assert "task" in data
        task = data["task"]
        assert task["title"] == "New API Task"
        assert task["description"] == "Created via API"
        assert task["status"] == "todo"
        assert task["assignee"] == "Bob"
        assert task["priority"] == "high"
        assert task["id"] is not None

    async def test_create_task_with_invalid_data(
        self, test_client: AsyncClient, clean_database
    ):
        """Test POST /api/tasks with invalid data returns 422 validation error.

        Validates:
        - Missing required field (title) returns 422
        - Invalid status returns 400 (service validation)
        - Error messages are descriptive
        """
        # Missing title (Pydantic validation)
        invalid_data = {
            "status": "todo",
            "assignee": "Alice"
        }

        response = await test_client.post("/api/tasks", json=invalid_data)
        assert response.status_code == 422  # FastAPI validation error

        # Invalid status (service validation)
        invalid_data = {
            "title": "Test Task",
            "status": "invalid_status"
        }

        response = await test_client.post("/api/tasks", json=invalid_data)
        assert response.status_code == 400
        assert "invalid_status" in response.text.lower()

    async def test_create_task_with_empty_title(
        self, test_client: AsyncClient, clean_database
    ):
        """Test POST /api/tasks with empty title returns validation error.

        Validates:
        - Empty string title is rejected by Pydantic validator
        - Whitespace-only title is rejected
        """
        # Empty title
        response = await test_client.post("/api/tasks", json={"title": ""})
        assert response.status_code == 422

        # Whitespace-only title
        response = await test_client.post("/api/tasks", json={"title": "   "})
        assert response.status_code == 422

    async def test_update_task(
        self, test_client: AsyncClient, clean_database, create_test_task
    ):
        """Test PATCH /api/tasks/{id} updates task fields.

        Validates:
        - Status code 200
        - Only specified fields are updated
        - Other fields remain unchanged
        """
        task = await create_test_task(
            title="Original Title",
            description="Original Description",
            assignee="Alice"
        )

        update_data = {
            "title": "Updated Title",
            "assignee": "Bob"
        }

        response = await test_client.patch(
            f"/api/tasks/{task['id']}",
            json=update_data
        )

        assert response.status_code == 200
        data = response.json()

        task_data = data["task"]
        assert task_data["title"] == "Updated Title"
        assert task_data["assignee"] == "Bob"
        assert task_data["description"] == "Original Description"

    async def test_update_task_not_found(
        self, test_client: AsyncClient, clean_database
    ):
        """Test PATCH /api/tasks/{id} with non-existent ID returns 404.

        Validates:
        - Status code 404
        - Error message indicates not found
        """
        fake_id = "00000000-0000-0000-0000-000000000000"
        update_data = {"title": "Updated"}

        response = await test_client.patch(
            f"/api/tasks/{fake_id}",
            json=update_data
        )

        assert response.status_code == 404

    async def test_update_task_position_atomic(
        self, test_client: AsyncClient, clean_database, create_test_task
    ):
        """Test PATCH /api/tasks/{id}/position performs atomic reordering.

        Validates:
        - Position update endpoint works
        - Other tasks at position are incremented
        - Transaction ensures atomicity
        """
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

        # Move task3 to position 1
        position_update = {
            "status": "doing",
            "position": 1
        }

        response = await test_client.patch(
            f"/api/tasks/{task3['id']}/position",
            json=position_update
        )

        assert response.status_code == 200
        data = response.json()
        assert data["task"]["position"] == 1

        # Verify task2 was incremented to position 2
        response = await test_client.get(f"/api/tasks/{task2['id']}")
        assert response.status_code == 200
        assert response.json()["task"]["position"] == 2

    async def test_update_task_position_cross_status(
        self, test_client: AsyncClient, clean_database, create_test_task
    ):
        """Test PATCH /api/tasks/{id}/position moves task between status columns.

        Validates:
        - Task can move to different status
        - Position is set correctly in new status
        - Kanban drag-and-drop scenario works
        """
        # Create task in "todo"
        todo_task = await create_test_task(
            title="Todo Task", status="todo", position=0
        )

        # Create task in "doing"
        doing_task = await create_test_task(
            title="Doing Task", status="doing", position=0
        )

        # Move todo task to doing at position 0
        position_update = {
            "status": "doing",
            "position": 0
        }

        response = await test_client.patch(
            f"/api/tasks/{todo_task['id']}/position",
            json=position_update
        )

        assert response.status_code == 200
        data = response.json()
        assert data["task"]["status"] == "doing"
        assert data["task"]["position"] == 0

        # Verify doing_task was incremented
        response = await test_client.get(f"/api/tasks/{doing_task['id']}")
        assert response.status_code == 200
        assert response.json()["task"]["position"] == 1

    async def test_update_task_position_invalid_status(
        self, test_client: AsyncClient, clean_database, create_test_task
    ):
        """Test PATCH /api/tasks/{id}/position with invalid status returns 400.

        Validates:
        - Invalid status is rejected
        - Error message is descriptive
        """
        task = await create_test_task(title="Test Task", status="todo")

        position_update = {
            "status": "invalid_status",
            "position": 0
        }

        response = await test_client.patch(
            f"/api/tasks/{task['id']}/position",
            json=position_update
        )

        assert response.status_code == 400
        assert "invalid_status" in response.text.lower()

    async def test_delete_task(
        self, test_client: AsyncClient, clean_database, create_test_task
    ):
        """Test DELETE /api/tasks/{id} deletes task.

        Validates:
        - Status code 200
        - Task is deleted from database
        - Subsequent GET returns 404
        """
        task = await create_test_task(title="Task to Delete")

        # Delete task
        response = await test_client.delete(f"/api/tasks/{task['id']}")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data

        # Verify task no longer exists
        response = await test_client.get(f"/api/tasks/{task['id']}")
        assert response.status_code == 404

    async def test_delete_task_not_found(
        self, test_client: AsyncClient, clean_database
    ):
        """Test DELETE /api/tasks/{id} with non-existent ID returns 404.

        Validates:
        - Status code 404
        - Error message indicates not found
        """
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await test_client.delete(f"/api/tasks/{fake_id}")

        assert response.status_code == 404

    async def test_create_task_with_project_id(
        self, test_client: AsyncClient, clean_database, create_test_project
    ):
        """Test POST /api/tasks with project_id associates task with project.

        Validates:
        - Task is created with project association
        - project_id is stored correctly
        """
        project = await create_test_project(name="Test Project")

        task_data = {
            "title": "Project Task",
            "project_id": str(project["id"])
        }

        response = await test_client.post("/api/tasks", json=task_data)

        assert response.status_code == 201
        data = response.json()
        assert data["task"]["project_id"] == str(project["id"])

    async def test_list_tasks_by_project(
        self, test_client: AsyncClient, clean_database,
        create_test_task, create_test_project
    ):
        """Test GET /api/tasks?project_id={id} filters by project.

        Validates:
        - project_id filter works correctly
        - Only tasks from specified project are returned
        """
        project1 = await create_test_project(name="Project 1")
        project2 = await create_test_project(name="Project 2")

        await create_test_task(title="Task 1", project_id=project1["id"])
        await create_test_task(title="Task 2", project_id=project2["id"])
        await create_test_task(title="Task 3", project_id=project1["id"])

        response = await test_client.get(
            f"/api/tasks?project_id={project1['id']}"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 2
        assert all(
            str(t["project_id"]) == str(project1["id"])
            for t in data["tasks"]
        )
