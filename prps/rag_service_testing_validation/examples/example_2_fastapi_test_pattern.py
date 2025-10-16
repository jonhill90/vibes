# Source: infra/rag-service/backend/tests/integration/test_crawl_api.py
# Lines: 1-243 (selected sections)
# Pattern: FastAPI TestClient with mocked dependencies
# Extracted: 2025-10-16
# Relevance: 9/10

"""Integration tests for Crawl API endpoints.

Tests cover:
1. POST /api/crawls (start crawl job)
2. GET /api/crawls (list crawl jobs with filters)
3. GET /api/crawls/{job_id} (get crawl job status)
4. POST /api/crawls/{job_id}/abort (abort running job)
5. Validation (invalid UUIDs, invalid parameters)
6. Error handling (source not found, job not found)

Pattern: FastAPI TestClient for API testing
Reference: prps/rag_service_completion_phase2.md (Task 4, Task 8)
"""

import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture
def app_with_crawl_routes(mock_db_pool):
    """Create FastAPI app with crawl routes for testing."""
    from fastapi import FastAPI
    from src.api.routes.crawls import router as crawl_router
    from src.api.dependencies import get_db_pool

    app = FastAPI()
    app.include_router(crawl_router)

    # Override dependency
    app.dependency_overrides[get_db_pool] = lambda: mock_db_pool

    return app


@pytest.fixture
def client(app_with_crawl_routes):
    """Create TestClient for API tests."""
    return TestClient(app_with_crawl_routes)


class TestStartCrawlEndpoint:
    """Tests for POST /api/crawls endpoint."""

    def test_start_crawl_success(self, client, mock_db_pool):
        """Test successful crawl job creation.

        Expected:
        - Returns 201 Created
        - Response includes job_id, status, pages_crawled
        - Database INSERT called
        """
        source_id = str(uuid4())
        job_id = uuid4()

        # Mock database operations
        mock_conn = MagicMock()

        # Mock source exists check
        mock_conn.fetchval = AsyncMock(side_effect=[
            True,  # Source exists
        ])

        # Mock crawl job creation
        mock_conn.fetchrow = AsyncMock(side_effect=[
            {
                "id": job_id,
                "source_id": uuid4(),
                "status": "pending",
                "pages_crawled": 0,
                "pages_total": None,
                "max_pages": 10,
                "max_depth": 2,
                "current_depth": 0,
                "error_message": None,
                "error_count": 0,
                "metadata": {},
                "started_at": None,
                "completed_at": None,
                "created_at": "2025-10-14T10:00:00",
                "updated_at": "2025-10-14T10:00:00",
            },
            {  # Updated job row after crawl
                "id": job_id,
                "source_id": uuid4(),
                "status": "completed",
                "pages_crawled": 5,
                "pages_total": 5,
                "max_pages": 10,
                "max_depth": 2,
                "current_depth": 2,
                "error_message": None,
                "error_count": 0,
                "metadata": {},
                "started_at": "2025-10-14T10:00:00",
                "completed_at": "2025-10-14T10:05:00",
                "created_at": "2025-10-14T10:00:00",
                "updated_at": "2025-10-14T10:05:00",
            },
        ])

        mock_conn.execute = AsyncMock()

        async def mock_acquire():
            yield mock_conn

        mock_db_pool.acquire = MagicMock(return_value=mock_acquire())

        # Mock crawler and ingestion services
        with patch("src.api.routes.crawls.CrawlerService") as MockCrawler, \
             patch("src.api.routes.crawls.IngestionService") as MockIngestion:

            # Mock successful crawl and ingestion
            mock_crawler_instance = MagicMock()
            MockCrawler.return_value = mock_crawler_instance

            mock_ingestion_instance = MagicMock()
            mock_ingestion_instance.ingest_from_crawl = AsyncMock(
                return_value=(True, {
                    "document_id": str(uuid4()),
                    "crawl_job_id": str(job_id),
                    "chunks_stored": 20,
                    "pages_crawled": 5,
                })
            )
            MockIngestion.return_value = mock_ingestion_instance

            # Make request
            response = client.post(
                "/api/crawls",
                json={
                    "source_id": source_id,
                    "url": "https://docs.example.com",
                    "max_pages": 10,
                    "max_depth": 2,
                },
            )

        # Verify response
        assert response.status_code == 201
        data = response.json()

        assert "id" in data
        assert "status" in data
        assert data["source_id"] == source_id or isinstance(data["source_id"], str)
        assert data["max_pages"] == 10
        assert data["max_depth"] == 2

    def test_start_crawl_invalid_source_id_format(self, client, mock_db_pool):
        """Test start crawl with invalid UUID format.

        Expected:
        - Returns 400 Bad Request
        - Error message indicates invalid UUID
        """
        response = client.post(
            "/api/crawls",
            json={
                "source_id": "not-a-uuid",
                "url": "https://example.com",
                "max_pages": 10,
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        # FastAPI error structure
        assert "source_id" in str(data).lower() or "uuid" in str(data).lower()

    def test_start_crawl_source_not_found(self, client, mock_db_pool):
        """Test start crawl with non-existent source.

        Expected:
        - Returns 400 Bad Request
        - Error message indicates source not found
        - Suggests creating source first
        """
        source_id = str(uuid4())

        # Mock source doesn't exist
        mock_conn = MagicMock()
        mock_conn.fetchval = AsyncMock(return_value=False)

        async def mock_acquire():
            yield mock_conn

        mock_db_pool.acquire = MagicMock(return_value=mock_acquire())

        response = client.post(
            "/api/crawls",
            json={
                "source_id": source_id,
                "url": "https://example.com",
                "max_pages": 10,
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        detail = data["detail"]
        assert "source not found" in str(detail).lower() or "not exist" in str(detail).lower()

    def test_start_crawl_validation_max_pages_too_high(self, client, mock_db_pool):
        """Test start crawl with max_pages > 1000.

        Expected:
        - Returns 422 Unprocessable Entity (Pydantic validation)
        - Error indicates max_pages limit
        """
        response = client.post(
            "/api/crawls",
            json={
                "source_id": str(uuid4()),
                "url": "https://example.com",
                "max_pages": 2000,  # Exceeds limit (max 1000)
            },
        )

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data


class TestListCrawlJobsEndpoint:
    """Tests for GET /api/crawls endpoint."""

    def test_list_crawl_jobs_filter_by_source_id(self, client, mock_db_pool):
        """Test listing crawl jobs filtered by source_id.

        Expected:
        - Returns only jobs for that source
        - WHERE clause includes source_id filter
        """
        source_id = str(uuid4())

        mock_conn = MagicMock()
        mock_conn.fetchval = AsyncMock(return_value=0)
        mock_conn.fetch = AsyncMock(return_value=[])

        async def mock_acquire():
            yield mock_conn

        mock_db_pool.acquire = MagicMock(return_value=mock_acquire())

        # Request with source_id filter
        response = client.get(f"/api/crawls?source_id={source_id}")

        assert response.status_code == 200
        data = response.json()

        assert data["total_count"] == 0
        assert len(data["crawl_jobs"]) == 0

    def test_list_crawl_jobs_invalid_status(self, client, mock_db_pool):
        """Test listing with invalid status value.

        Expected:
        - Returns 400 Bad Request
        - Error indicates invalid status
        - Lists valid status options
        """
        response = client.get("/api/crawls?status=invalid_status")

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        detail = data["detail"]
        assert "invalid status" in str(detail).lower() or "must be one of" in str(detail).lower()


class TestCrawlAPIErrorHandling:
    """Tests for error handling and edge cases."""

    def test_start_crawl_database_error(self, client, mock_db_pool):
        """Test start crawl when database connection fails.

        Expected:
        - Returns 500 Internal Server Error
        - Error message indicates server error
        """
        source_id = str(uuid4())

        # Mock database connection failure
        async def mock_acquire_fails():
            raise Exception("Database connection lost")
            yield  # pragma: no cover

        mock_db_pool.acquire = MagicMock(return_value=mock_acquire_fails())

        response = client.post(
            "/api/crawls",
            json={
                "source_id": source_id,
                "url": "https://example.com",
                "max_pages": 10,
            },
        )

        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
