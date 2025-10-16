"""Integration tests for Search API endpoints.

Tests cover:
1. POST /api/search without source_id filter
2. POST /api/search with valid source_id filter
3. POST /api/search with invalid source_id (400 error)
4. POST /api/search with non-existent source_id (empty results)
5. Validation (invalid query, invalid limit)
6. Error handling (service failures)

Pattern: FastAPI TestClient with mocked dependencies
Reference: prps/rag_service_testing_validation.md (Task 5)
"""

import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture
def app_with_search_routes(mock_db_pool, mock_qdrant_client, mock_openai_client):
    """Create FastAPI app with search routes for testing.

    Args:
        mock_db_pool: Mocked database pool
        mock_qdrant_client: Mocked Qdrant client
        mock_openai_client: Mocked OpenAI client

    Returns:
        FastAPI app with search routes and overridden dependencies
    """
    from fastapi import FastAPI
    from src.api.routes.search import router as search_router
    from src.api.dependencies import get_db_pool, get_qdrant_client

    app = FastAPI()
    app.include_router(search_router)

    # Override dependencies
    app.dependency_overrides[get_db_pool] = lambda: mock_db_pool
    app.dependency_overrides[get_qdrant_client] = lambda: mock_qdrant_client

    return app


@pytest.fixture
def client(app_with_search_routes):
    """Create TestClient for API tests."""
    return TestClient(app_with_search_routes)


@pytest.fixture
def mock_search_results():
    """Sample search results for testing.

    Returns:
        List of search result dictionaries
    """
    return [
        {
            "chunk_id": "chunk-1",
            "text": "Machine learning is a subset of artificial intelligence.",
            "score": 0.92,
            "match_type": "vector",
            "metadata": {
                "document_id": str(uuid4()),
                "source_id": str(uuid4()),
                "title": "ML Best Practices",
                "chunk_index": 0,
            }
        },
        {
            "chunk_id": "chunk-2",
            "text": "Deep learning uses neural networks with multiple layers.",
            "score": 0.85,
            "match_type": "vector",
            "metadata": {
                "document_id": str(uuid4()),
                "source_id": str(uuid4()),
                "title": "Deep Learning Guide",
                "chunk_index": 1,
            }
        }
    ]


class TestSearchWithoutFilter:
    """Tests for POST /api/search without source_id filter."""

    def test_search_success_no_filter(self, client, mock_search_results):
        """Test search without source_id filter.

        Expected:
        - Returns 200 OK
        - Response includes results array, query, count, latency_ms
        - All matching chunks returned (no source filtering)
        """
        # Mock RAG service search
        with patch("src.api.routes.search.RAGService") as MockRAGService:
            mock_service = MagicMock()
            mock_service.search = AsyncMock(return_value=mock_search_results)
            MockRAGService.return_value = mock_service

            # Make request without source_id
            response = client.post(
                "/api/search",
                json={
                    "query": "machine learning best practices",
                    "limit": 10,
                    "search_type": "vector"
                }
            )

        # Verify response
        assert response.status_code == 200
        data = response.json()

        assert "results" in data
        assert "query" in data
        assert "count" in data
        assert "latency_ms" in data
        assert "search_type" in data

        assert data["query"] == "machine learning best practices"
        assert data["count"] == 2
        assert len(data["results"]) == 2

        # Verify result structure
        result = data["results"][0]
        assert "chunk_id" in result
        assert "text" in result
        assert "score" in result
        assert "metadata" in result
        assert result["chunk_id"] == "chunk-1"
        assert result["score"] == 0.92


class TestSearchWithValidFilter:
    """Tests for POST /api/search with valid source_id filter."""

    def test_search_with_valid_source_id(self, client):
        """Test search with valid source_id filter.

        Expected:
        - Returns 200 OK
        - Only results from specified source_id
        - Filters passed to RAG service
        """
        source_id = str(uuid4())

        # Mock search results from specific source
        filtered_results = [
            {
                "chunk_id": "chunk-3",
                "text": "Python is a popular programming language.",
                "score": 0.88,
                "match_type": "vector",
                "metadata": {
                    "document_id": str(uuid4()),
                    "source_id": source_id,
                    "title": "Python Guide",
                    "chunk_index": 0,
                }
            }
        ]

        # Mock RAG service
        with patch("src.api.routes.search.RAGService") as MockRAGService:
            mock_service = MagicMock()
            mock_service.search = AsyncMock(return_value=filtered_results)
            MockRAGService.return_value = mock_service

            # Make request with source_id filter
            response = client.post(
                "/api/search",
                json={
                    "query": "python programming",
                    "limit": 10,
                    "search_type": "vector",
                    "source_id": source_id
                }
            )

        # Verify response
        assert response.status_code == 200
        data = response.json()

        assert data["count"] == 1
        assert len(data["results"]) == 1

        # Verify result is from correct source
        result = data["results"][0]
        assert result["metadata"]["source_id"] == source_id

        # Verify filters were passed to search
        mock_service.search.assert_called_once()
        call_args = mock_service.search.call_args
        assert call_args.kwargs["filters"] == {"source_id": source_id}


class TestSearchWithInvalidFilter:
    """Tests for POST /api/search with invalid source_id."""

    def test_search_with_invalid_source_id_format(self, client):
        """Test search with invalid UUID format for source_id.

        Expected:
        - Returns 400 Bad Request
        - Error message indicates invalid UUID
        - Helpful error message provided
        """
        # Mock RAG service to raise ValueError for invalid UUID
        with patch("src.api.routes.search.RAGService") as MockRAGService:
            mock_service = MagicMock()
            mock_service.search = AsyncMock(
                side_effect=ValueError("Invalid UUID format for source_id")
            )
            MockRAGService.return_value = mock_service

            # Make request with invalid source_id
            response = client.post(
                "/api/search",
                json={
                    "query": "test query",
                    "limit": 10,
                    "search_type": "vector",
                    "source_id": "not-a-valid-uuid"
                }
            )

        # Verify error response
        assert response.status_code == 400
        data = response.json()

        assert "detail" in data
        detail = data["detail"]
        assert detail["success"] is False
        assert "error" in detail
        assert "Invalid search request" in detail["error"]
        assert "Invalid UUID format" in detail["detail"]

    def test_search_validation_empty_query(self, client):
        """Test search with empty query string.

        Expected:
        - Returns 422 Unprocessable Entity (Pydantic validation)
        - Error indicates query is required
        """
        response = client.post(
            "/api/search",
            json={
                "query": "",  # Empty query
                "limit": 10
            }
        )

        # Pydantic validation fails before reaching route handler
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_search_validation_limit_too_high(self, client):
        """Test search with limit > 100.

        Expected:
        - Returns 422 Unprocessable Entity
        - Error indicates limit exceeds maximum
        """
        response = client.post(
            "/api/search",
            json={
                "query": "test query",
                "limit": 500  # Exceeds max of 100
            }
        )

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_search_validation_negative_limit(self, client):
        """Test search with negative limit.

        Expected:
        - Returns 422 Unprocessable Entity
        - Error indicates invalid limit
        """
        response = client.post(
            "/api/search",
            json={
                "query": "test query",
                "limit": -5
            }
        )

        assert response.status_code == 422


class TestSearchWithNonExistentSource:
    """Tests for POST /api/search with non-existent source_id."""

    def test_search_with_nonexistent_source_id(self, client):
        """Test search with valid UUID but non-existent source.

        Expected:
        - Returns 200 OK (not 404)
        - Empty results array (no matches for that source)
        - Count is 0
        """
        nonexistent_source_id = str(uuid4())

        # Mock RAG service returns empty results
        with patch("src.api.routes.search.RAGService") as MockRAGService:
            mock_service = MagicMock()
            mock_service.search = AsyncMock(return_value=[])
            MockRAGService.return_value = mock_service

            # Make request with non-existent source_id
            response = client.post(
                "/api/search",
                json={
                    "query": "test query",
                    "limit": 10,
                    "search_type": "vector",
                    "source_id": nonexistent_source_id
                }
            )

        # Verify response
        assert response.status_code == 200
        data = response.json()

        assert data["count"] == 0
        assert len(data["results"]) == 0
        assert data["query"] == "test query"

        # Verify filters were passed
        mock_service.search.assert_called_once()
        call_args = mock_service.search.call_args
        assert call_args.kwargs["filters"] == {"source_id": nonexistent_source_id}


class TestSearchErrorHandling:
    """Tests for error handling and edge cases."""

    def test_search_service_initialization_failure(self, client):
        """Test search when RAG service initialization fails.

        Expected:
        - Returns 503 Service Unavailable
        - Error message indicates service unavailable
        - Suggests checking configuration
        """
        # Mock get_rag_service to raise exception
        with patch("src.api.routes.search.get_rag_service") as mock_get_service:
            from fastapi import HTTPException
            mock_get_service.side_effect = HTTPException(
                status_code=503,
                detail={
                    "success": False,
                    "error": "Search service unavailable",
                    "detail": "Failed to initialize OpenAI client",
                    "suggestion": "Check if OpenAI API key is configured"
                }
            )

            response = client.post(
                "/api/search",
                json={
                    "query": "test query",
                    "limit": 10
                }
            )

        assert response.status_code == 503
        data = response.json()
        assert "detail" in data

    def test_search_service_execution_failure(self, client):
        """Test search when RAG service execution fails.

        Expected:
        - Returns 500 Internal Server Error
        - Error message indicates search failed
        - Suggests checking logs
        """
        # Mock RAG service to raise exception during search
        with patch("src.api.routes.search.RAGService") as MockRAGService:
            mock_service = MagicMock()
            mock_service.search = AsyncMock(
                side_effect=Exception("Qdrant connection timeout")
            )
            MockRAGService.return_value = mock_service

            response = client.post(
                "/api/search",
                json={
                    "query": "test query",
                    "limit": 10
                }
            )

        assert response.status_code == 500
        data = response.json()

        assert "detail" in data
        detail = data["detail"]
        assert detail["success"] is False
        assert "Search failed" in detail["error"]
        assert "Qdrant connection timeout" in detail["detail"]


class TestSearchTypes:
    """Tests for different search types (vector, hybrid, auto)."""

    def test_search_type_vector(self, client, mock_search_results):
        """Test vector-only search mode."""
        with patch("src.api.routes.search.RAGService") as MockRAGService:
            mock_service = MagicMock()
            mock_service.search = AsyncMock(return_value=mock_search_results)
            MockRAGService.return_value = mock_service

            response = client.post(
                "/api/search",
                json={
                    "query": "test query",
                    "limit": 10,
                    "search_type": "vector"
                }
            )

        assert response.status_code == 200
        data = response.json()
        assert data["search_type"] == "vector"

    def test_search_type_hybrid(self, client, mock_search_results):
        """Test hybrid search mode (vector + full-text)."""
        with patch("src.api.routes.search.RAGService") as MockRAGService:
            mock_service = MagicMock()
            mock_service.search = AsyncMock(return_value=mock_search_results)
            MockRAGService.return_value = mock_service

            response = client.post(
                "/api/search",
                json={
                    "query": "test query",
                    "limit": 10,
                    "search_type": "hybrid"
                }
            )

        assert response.status_code == 200
        data = response.json()
        assert data["search_type"] == "hybrid"

    def test_search_type_auto(self, client, mock_search_results):
        """Test auto search mode (uses best available)."""
        with patch("src.api.routes.search.RAGService") as MockRAGService:
            mock_service = MagicMock()
            mock_service.search = AsyncMock(return_value=mock_search_results)
            MockRAGService.return_value = mock_service

            response = client.post(
                "/api/search",
                json={
                    "query": "test query",
                    "limit": 10,
                    "search_type": "auto"
                }
            )

        assert response.status_code == 200
        data = response.json()
        assert data["search_type"] == "auto"
