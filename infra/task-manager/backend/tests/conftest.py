"""Pytest fixtures for task management backend tests.

This module provides:
- Database connection pool fixture for async tests
- Test database cleanup utilities
- Mock data factories for creating test entities
- Async test client for FastAPI endpoints

Critical Gotchas Addressed:
- Gotcha #1: All database fixtures use async def (non-blocking)
- Gotcha #12: Always uses async with for connection management
- Clean up test data after each test to prevent state leakage
"""

import os
from typing import AsyncGenerator
import asyncpg
import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app
from src.config.database import init_db_pool, close_db_pool


@pytest.fixture(scope="session")
def event_loop_policy():
    """Configure asyncio event loop policy for pytest-asyncio."""
    import asyncio
    return asyncio.get_event_loop_policy()


@pytest.fixture(scope="session")
async def db_pool() -> AsyncGenerator[asyncpg.Pool, None]:
    """Create a database connection pool for the test session.

    This fixture:
    - Initializes connection pool once per test session
    - Ensures DATABASE_URL environment variable is set
    - Cleans up pool after all tests complete

    Yields:
        asyncpg.Pool: Database connection pool for tests
    """
    # Ensure test database URL is set
    if not os.getenv("DATABASE_URL"):
        pytest.skip("DATABASE_URL not set - skipping database tests")

    # Initialize pool
    pool = await init_db_pool()

    yield pool

    # Cleanup
    await close_db_pool()


@pytest.fixture
async def db_connection(db_pool: asyncpg.Pool) -> AsyncGenerator[asyncpg.Connection, None]:
    """Provide a database connection for a single test.

    This fixture:
    - Acquires connection from pool
    - Automatically releases connection after test
    - Uses async with for proper cleanup

    Args:
        db_pool: Session-scoped database pool

    Yields:
        asyncpg.Connection: Database connection for test
    """
    async with db_pool.acquire() as conn:
        yield conn


@pytest.fixture
async def clean_database(db_connection: asyncpg.Connection):
    """Clean all test data from database before and after each test.

    This fixture:
    - Deletes all tasks and projects before test runs
    - Yields control to test
    - Deletes all tasks and projects after test completes
    - Prevents test data leakage between tests

    Args:
        db_connection: Database connection from db_connection fixture
    """
    # Clean before test
    await db_connection.execute("DELETE FROM tasks")
    await db_connection.execute("DELETE FROM projects")

    yield

    # Clean after test
    await db_connection.execute("DELETE FROM tasks")
    await db_connection.execute("DELETE FROM projects")


@pytest.fixture
async def test_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async HTTP client for testing FastAPI endpoints.

    This fixture:
    - Creates AsyncClient with ASGI transport
    - Properly handles async context manager
    - Cleans up client after test

    Yields:
        AsyncClient: HTTP client for testing API endpoints
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


# --- Mock Data Factories ---

@pytest.fixture
def sample_project_data():
    """Factory for creating sample project data.

    Returns:
        dict: Project creation data with name and description
    """
    return {
        "name": "Test Project",
        "description": "A test project for unit tests"
    }


@pytest.fixture
def sample_task_data():
    """Factory for creating sample task data.

    Returns:
        dict: Task creation data with all required fields
    """
    return {
        "title": "Test Task",
        "description": "A test task description",
        "status": "todo",
        "assignee": "TestUser",
        "priority": "medium",
        "position": 0,
        "project_id": None
    }


@pytest.fixture
async def create_test_project(db_connection: asyncpg.Connection):
    """Factory fixture for creating test projects in database.

    This fixture returns an async function that:
    - Creates a project with provided data
    - Returns the created project as a dict
    - Automatically cleaned up by clean_database fixture

    Args:
        db_connection: Database connection

    Returns:
        Async function that creates projects
    """
    async def _create_project(name: str = "Test Project", description: str = "Test"):
        query = """
            INSERT INTO projects (name, description)
            VALUES ($1, $2)
            RETURNING *
        """
        row = await db_connection.fetchrow(query, name, description)
        return dict(row)

    return _create_project


@pytest.fixture
async def create_test_task(db_connection: asyncpg.Connection):
    """Factory fixture for creating test tasks in database.

    This fixture returns an async function that:
    - Creates a task with provided data
    - Returns the created task as a dict
    - Automatically cleaned up by clean_database fixture

    Args:
        db_connection: Database connection

    Returns:
        Async function that creates tasks
    """
    async def _create_task(
        title: str = "Test Task",
        status: str = "todo",
        position: int = 0,
        project_id: str = None,
        assignee: str = "TestUser",
        priority: str = "medium",
        description: str = None
    ):
        query = """
            INSERT INTO tasks (
                title, description, status, position,
                project_id, assignee, priority
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING *
        """
        row = await db_connection.fetchrow(
            query, title, description, status, position,
            project_id, assignee, priority
        )
        return dict(row)

    return _create_task
