"""Integration tests for Document API endpoints.

Tests cover:
1. POST /api/documents (upload document)
2. GET /api/documents (list documents with filters)
3. GET /api/documents/{document_id} (get single document)
4. DELETE /api/documents/{document_id} (delete with cascade)
5. Validation (invalid UUIDs, file size, file type)
6. Error handling (400, 404, 413, 422, 500)

Pattern: FastAPI TestClient with mocked dependencies
Reference: tests/integration/test_crawl_api.py
PRP: prps/rag_service_testing_validation.md (Task 4)
"""

import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
from io import BytesIO


@pytest.fixture
def app_with_document_routes(mock_db_pool):
    """Create FastAPI app with document routes for testing.

    This fixture creates a minimal FastAPI app with only the document routes
    and overrides the database dependency with a mock pool.

    Critical: Dependency override must use exact function object from dependencies module.
    Pattern: Same as test_crawl_api.py app_with_crawl_routes fixture.
    """
    from fastapi import FastAPI
    from src.api.routes.documents import router as document_router
    from src.api.dependencies import get_db_pool

    app = FastAPI()
    app.include_router(document_router)

    # Mock Qdrant client in app state (required by upload endpoint)
    app.state.qdrant_client = MagicMock()

    # Override dependency
    app.dependency_overrides[get_db_pool] = lambda: mock_db_pool

    yield app

    # CRITICAL: Reset overrides after test (prevents test pollution)
    app.dependency_overrides = {}


@pytest.fixture
def client(app_with_document_routes):
    """Create TestClient for API tests."""
    return TestClient(app_with_document_routes)


class TestUploadDocumentEndpoint:
    """Tests for POST /api/documents endpoint."""

    def test_upload_document_success(self, client, mock_db_pool, mock_uploaded_file):
        """Test successful document upload.

        Expected:
        - Returns 201 Created
        - Response includes document_id, filename, chunk_count
        - Database INSERT called
        - Ingestion pipeline executed
        """
        source_id = str(uuid4())
        document_id = uuid4()

        # Mock database operations
        mock_conn = MagicMock()

        # Mock document creation
        mock_conn.fetchrow = AsyncMock(return_value={
            "id": document_id,
            "source_id": uuid4(),
            "title": "test.pdf",
            "document_type": "pdf",
            "url": None,
            "created_at": "2025-10-16T10:00:00",
            "updated_at": "2025-10-16T10:00:00",
            "metadata": {"filename": "test.pdf", "file_size": 1024},
        })

        mock_conn.fetchval = AsyncMock(return_value=None)
        mock_conn.execute = AsyncMock()
        mock_conn.fetch = AsyncMock(return_value=[])

        async def mock_acquire():
            yield mock_conn

        mock_db_pool.acquire = MagicMock(return_value=mock_acquire())

        # Mock ingestion services
        with patch("src.api.routes.documents.IngestionService") as MockIngestion, \
             patch("src.api.routes.documents.DocumentParser"), \
             patch("src.api.routes.documents.TextChunker"), \
             patch("src.api.routes.documents.EmbeddingService"), \
             patch("src.api.routes.documents.VectorService"), \
             patch("src.api.routes.documents.DocumentService") as MockDocService, \
             patch("src.api.routes.documents.SourceService") as MockSourceService:

            # Mock DocumentService for initial create and subsequent operations
            mock_doc_service = MagicMock()
            mock_doc_service.create_document = AsyncMock(return_value=(True, {
                "document": {
                    "id": document_id,
                    "source_id": uuid4(),
                    "title": "test.pdf",
                    "document_type": "pdf",
                    "url": None,
                    "created_at": "2025-10-16T10:00:00",
                    "updated_at": "2025-10-16T10:00:00",
                    "metadata": {},
                }
            }))
            mock_doc_service.delete_document = AsyncMock(return_value=(True, {}))
            mock_doc_service.get_document = AsyncMock(return_value=(True, {
                "document": {
                    "id": document_id,
                    "source_id": uuid4(),
                    "title": "test.pdf",
                    "document_type": "pdf",
                    "url": None,
                    "created_at": "2025-10-16T10:00:00",
                    "updated_at": "2025-10-16T10:00:00",
                    "metadata": {"filename": "test.pdf"},
                }
            }))
            MockDocService.return_value = mock_doc_service

            # Mock IngestionService
            mock_ingestion = MagicMock()
            mock_ingestion.ingest_document = AsyncMock(return_value=(True, {
                "document_id": str(document_id),
                "chunks_stored": 5,
                "ingestion_time_ms": 1234,
            }))
            MockIngestion.return_value = mock_ingestion

            # Mock SourceService
            mock_source_service = MagicMock()
            mock_source_service.update_source = AsyncMock(return_value=(True, {}))
            MockSourceService.return_value = mock_source_service

            # Make request with multipart/form-data
            # CRITICAL: Use files parameter with tuple (filename, content, content_type)
            response = client.post(
                "/api/documents",
                data={
                    "source_id": source_id,
                    "title": "Test Document",
                },
                files={
                    "file": ("test.pdf", mock_uploaded_file, "application/pdf")
                }
            )

        # Verify response
        assert response.status_code == 201
        data = response.json()

        assert "id" in data
        assert "title" in data
        assert "source_id" in data
        assert data["document_type"] == "pdf"

    def test_upload_document_invalid_extension(self, client, mock_db_pool):
        """Test upload with invalid file extension.

        Expected:
        - Returns 400 Bad Request
        - Error message indicates invalid file type
        - Suggests allowed extensions
        """
        source_id = str(uuid4())

        # Create file with invalid extension
        file_content = BytesIO(b"malicious content")

        response = client.post(
            "/api/documents",
            data={"source_id": source_id},
            files={
                "file": ("malware.exe", file_content, "application/x-executable")
            }
        )

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        detail = data["detail"]
        assert "invalid file type" in str(detail).lower() or "not allowed" in str(detail).lower()

    def test_upload_document_file_too_large(self, client, mock_db_pool):
        """Test upload with file exceeding size limit.

        Expected:
        - Returns 413 Payload Too Large
        - Error message indicates file size limit
        - Suggests compression
        """
        source_id = str(uuid4())

        # Create file larger than 10MB
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB
        file_content = BytesIO(large_content)

        response = client.post(
            "/api/documents",
            data={"source_id": source_id},
            files={
                "file": ("large.pdf", file_content, "application/pdf")
            }
        )

        assert response.status_code == 413
        data = response.json()
        assert "detail" in data
        detail = data["detail"]
        assert "too large" in str(detail).lower() or "exceeds" in str(detail).lower()

    def test_upload_document_missing_file(self, client, mock_db_pool):
        """Test upload without file parameter.

        Expected:
        - Returns 422 Unprocessable Entity (Pydantic validation)
        - Error indicates missing required field
        """
        source_id = str(uuid4())

        response = client.post(
            "/api/documents",
            data={
                "source_id": source_id,
                # Missing: file
            }
        )

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_upload_document_missing_source_id(self, client, mock_db_pool):
        """Test upload without source_id parameter.

        Expected:
        - Returns 422 Unprocessable Entity
        - Error indicates missing required field
        """
        file_content = BytesIO(b"%PDF-1.4\ntest content\n%%EOF")

        response = client.post(
            "/api/documents",
            data={
                # Missing: source_id
            },
            files={
                "file": ("test.pdf", file_content, "application/pdf")
            }
        )

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data


class TestListDocumentsEndpoint:
    """Tests for GET /api/documents endpoint."""

    def test_list_documents_success(self, client, mock_db_pool):
        """Test listing documents with pagination.

        Expected:
        - Returns 200 OK
        - Response includes documents array, total_count, pagination info
        - Documents sorted by created_at DESC
        """
        doc_id_1 = uuid4()
        doc_id_2 = uuid4()
        source_id = uuid4()

        # Mock database
        mock_conn = MagicMock()

        # Mock document service operations
        with patch("src.api.routes.documents.DocumentService") as MockDocService:
            mock_doc_service = MagicMock()
            mock_doc_service.list_documents = AsyncMock(return_value=(True, {
                "documents": [
                    {
                        "id": doc_id_1,
                        "source_id": source_id,
                        "title": "Document 1",
                        "document_type": "pdf",
                        "url": None,
                        "created_at": "2025-10-16T10:00:00",
                        "updated_at": "2025-10-16T10:00:00",
                    },
                    {
                        "id": doc_id_2,
                        "source_id": source_id,
                        "title": "Document 2",
                        "document_type": "markdown",
                        "url": "https://example.com/doc",
                        "created_at": "2025-10-16T09:00:00",
                        "updated_at": "2025-10-16T09:00:00",
                    },
                ],
                "total_count": 2,
            }))
            MockDocService.return_value = mock_doc_service

            async def mock_acquire():
                yield mock_conn

            mock_db_pool.acquire = MagicMock(return_value=mock_acquire())

            # Make request
            response = client.get("/api/documents?page=1&per_page=10")

        # Verify response
        assert response.status_code == 200
        data = response.json()

        assert "documents" in data
        assert "total_count" in data
        assert "page" in data
        assert "per_page" in data
        assert "has_next" in data
        assert "has_prev" in data

        assert data["total_count"] == 2
        assert data["page"] == 1
        assert data["per_page"] == 10
        assert len(data["documents"]) == 2

        # Verify document structure
        doc = data["documents"][0]
        assert "id" in doc
        assert "title" in doc
        assert "document_type" in doc

    def test_list_documents_filter_by_source_id(self, client, mock_db_pool):
        """Test listing documents filtered by source_id.

        Expected:
        - Returns only documents for that source
        - Filter applied to service call
        """
        source_id = str(uuid4())

        mock_conn = MagicMock()

        with patch("src.api.routes.documents.DocumentService") as MockDocService:
            mock_doc_service = MagicMock()
            mock_doc_service.list_documents = AsyncMock(return_value=(True, {
                "documents": [],
                "total_count": 0,
            }))
            MockDocService.return_value = mock_doc_service

            async def mock_acquire():
                yield mock_conn

            mock_db_pool.acquire = MagicMock(return_value=mock_acquire())

            # Request with source_id filter
            response = client.get(f"/api/documents?source_id={source_id}")

        assert response.status_code == 200
        data = response.json()

        assert data["total_count"] == 0
        assert len(data["documents"]) == 0

        # Verify filter was passed to service
        mock_doc_service.list_documents.assert_called_once()
        call_kwargs = mock_doc_service.list_documents.call_args[1]
        assert "filters" in call_kwargs
        assert call_kwargs["filters"]["source_id"] == source_id

    def test_list_documents_filter_by_document_type(self, client, mock_db_pool):
        """Test listing documents filtered by document_type.

        Expected:
        - Returns only documents of that type
        - Filter applied to service call
        """
        mock_conn = MagicMock()

        with patch("src.api.routes.documents.DocumentService") as MockDocService:
            mock_doc_service = MagicMock()
            mock_doc_service.list_documents = AsyncMock(return_value=(True, {
                "documents": [],
                "total_count": 0,
            }))
            MockDocService.return_value = mock_doc_service

            async def mock_acquire():
                yield mock_conn

            mock_db_pool.acquire = MagicMock(return_value=mock_acquire())

            # Request with document_type filter
            response = client.get("/api/documents?document_type=pdf")

        assert response.status_code == 200
        data = response.json()

        # Verify filter was passed to service
        mock_doc_service.list_documents.assert_called_once()
        call_kwargs = mock_doc_service.list_documents.call_args[1]
        assert "filters" in call_kwargs
        assert call_kwargs["filters"]["document_type"] == "pdf"

    def test_list_documents_pagination(self, client, mock_db_pool):
        """Test pagination with page and per_page parameters.

        Expected:
        - Page and per_page applied to service call
        - Response reflects requested pagination
        """
        mock_conn = MagicMock()

        with patch("src.api.routes.documents.DocumentService") as MockDocService:
            mock_doc_service = MagicMock()
            mock_doc_service.list_documents = AsyncMock(return_value=(True, {
                "documents": [],
                "total_count": 100,
            }))
            MockDocService.return_value = mock_doc_service

            async def mock_acquire():
                yield mock_conn

            mock_db_pool.acquire = MagicMock(return_value=mock_acquire())

            # Request page 2 (per_page 20)
            response = client.get("/api/documents?page=2&per_page=20")

        assert response.status_code == 200
        data = response.json()

        assert data["page"] == 2
        assert data["per_page"] == 20
        assert data["total_count"] == 100
        assert data["has_next"] is True  # 100 total, page 2 of 20 per page
        assert data["has_prev"] is True  # page 2, so has previous

    def test_list_documents_invalid_pagination(self, client, mock_db_pool):
        """Test list with invalid pagination parameters.

        Expected:
        - Returns 422 Unprocessable Entity for per_page > 100
        - Pydantic validation enforces limits
        """
        response = client.get("/api/documents?per_page=200")

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data


class TestGetDocumentEndpoint:
    """Tests for GET /api/documents/{document_id} endpoint."""

    def test_get_document_success(self, client, mock_db_pool):
        """Test getting a single document by ID.

        Expected:
        - Returns 200 OK
        - Response includes full document details
        """
        document_id = str(uuid4())

        mock_conn = MagicMock()

        with patch("src.api.routes.documents.DocumentService") as MockDocService:
            mock_doc_service = MagicMock()
            mock_doc_service.get_document = AsyncMock(return_value=(True, {
                "document": {
                    "id": uuid4(),
                    "source_id": uuid4(),
                    "title": "Test Document",
                    "document_type": "pdf",
                    "url": None,
                    "created_at": "2025-10-16T10:00:00",
                    "updated_at": "2025-10-16T10:00:00",
                    "metadata": {"filename": "test.pdf"},
                }
            }))
            MockDocService.return_value = mock_doc_service

            async def mock_acquire():
                yield mock_conn

            mock_db_pool.acquire = MagicMock(return_value=mock_acquire())

            # Make request
            response = client.get(f"/api/documents/{document_id}")

        # Verify response
        assert response.status_code == 200
        data = response.json()

        assert "id" in data
        assert "title" in data
        assert data["title"] == "Test Document"
        assert data["document_type"] == "pdf"

    def test_get_document_not_found(self, client, mock_db_pool):
        """Test getting non-existent document.

        Expected:
        - Returns 404 Not Found
        - Error message indicates document not found
        """
        document_id = str(uuid4())

        mock_conn = MagicMock()

        with patch("src.api.routes.documents.DocumentService") as MockDocService:
            mock_doc_service = MagicMock()
            mock_doc_service.get_document = AsyncMock(return_value=(False, {
                "error": "Document not found"
            }))
            MockDocService.return_value = mock_doc_service

            async def mock_acquire():
                yield mock_conn

            mock_db_pool.acquire = MagicMock(return_value=mock_acquire())

            # Make request
            response = client.get(f"/api/documents/{document_id}")

        # Verify response
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        detail = data["detail"]
        assert "not found" in str(detail).lower()

    def test_get_document_invalid_uuid(self, client, mock_db_pool):
        """Test getting document with invalid UUID.

        Expected:
        - Returns 400 Bad Request
        - Error indicates invalid UUID format
        """
        response = client.get("/api/documents/not-a-valid-uuid")

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        detail = data["detail"]
        assert "invalid" in str(detail).lower() and "uuid" in str(detail).lower()


class TestDeleteDocumentEndpoint:
    """Tests for DELETE /api/documents/{document_id} endpoint."""

    def test_delete_document_success(self, client, mock_db_pool):
        """Test deleting a document.

        Expected:
        - Returns 200 OK
        - Response includes success message
        - Document removed from database (CASCADE to chunks)
        """
        document_id = str(uuid4())

        mock_conn = MagicMock()

        with patch("src.api.routes.documents.DocumentService") as MockDocService:
            mock_doc_service = MagicMock()
            mock_doc_service.delete_document = AsyncMock(return_value=(True, {
                "message": "Document deleted successfully"
            }))
            MockDocService.return_value = mock_doc_service

            async def mock_acquire():
                yield mock_conn

            mock_db_pool.acquire = MagicMock(return_value=mock_acquire())

            # Make request
            response = client.delete(f"/api/documents/{document_id}")

        # Verify response
        assert response.status_code == 200
        data = response.json()

        assert "success" in data
        assert data["success"] is True
        assert "message" in data
        assert "deleted" in data["message"].lower()

    def test_delete_document_not_found(self, client, mock_db_pool):
        """Test deleting non-existent document.

        Expected:
        - Returns 404 Not Found
        - Error message indicates document not found
        """
        document_id = str(uuid4())

        mock_conn = MagicMock()

        with patch("src.api.routes.documents.DocumentService") as MockDocService:
            mock_doc_service = MagicMock()
            mock_doc_service.delete_document = AsyncMock(return_value=(False, {
                "error": "Document not found"
            }))
            MockDocService.return_value = mock_doc_service

            async def mock_acquire():
                yield mock_conn

            mock_db_pool.acquire = MagicMock(return_value=mock_acquire())

            # Make request
            response = client.delete(f"/api/documents/{document_id}")

        # Verify response
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        detail = data["detail"]
        assert "not found" in str(detail).lower()

    def test_delete_document_invalid_uuid(self, client, mock_db_pool):
        """Test deleting document with invalid UUID.

        Expected:
        - Returns 400 Bad Request
        - Error indicates invalid UUID format
        """
        response = client.delete("/api/documents/invalid-uuid-format")

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        detail = data["detail"]
        assert "invalid" in str(detail).lower() and "uuid" in str(detail).lower()


class TestDocumentAPIErrorHandling:
    """Tests for error handling and edge cases."""

    def test_list_documents_database_error(self, client, mock_db_pool):
        """Test list documents when service fails.

        Expected:
        - Returns 500 Internal Server Error
        - Error message indicates server error
        """
        mock_conn = MagicMock()

        with patch("src.api.routes.documents.DocumentService") as MockDocService:
            mock_doc_service = MagicMock()
            mock_doc_service.list_documents = AsyncMock(return_value=(False, {
                "error": "Database connection failed"
            }))
            MockDocService.return_value = mock_doc_service

            async def mock_acquire():
                yield mock_conn

            mock_db_pool.acquire = MagicMock(return_value=mock_acquire())

            response = client.get("/api/documents")

        assert response.status_code == 500
        data = response.json()
        assert "detail" in data

    def test_upload_document_ingestion_failure(self, client, mock_db_pool, mock_uploaded_file):
        """Test upload when ingestion pipeline fails.

        Expected:
        - Returns 500 Internal Server Error
        - Error indicates ingestion failure
        """
        source_id = str(uuid4())
        document_id = uuid4()

        mock_conn = MagicMock()

        async def mock_acquire():
            yield mock_conn

        mock_db_pool.acquire = MagicMock(return_value=mock_acquire())

        with patch("src.api.routes.documents.IngestionService") as MockIngestion, \
             patch("src.api.routes.documents.DocumentParser"), \
             patch("src.api.routes.documents.TextChunker"), \
             patch("src.api.routes.documents.EmbeddingService"), \
             patch("src.api.routes.documents.VectorService"), \
             patch("src.api.routes.documents.DocumentService") as MockDocService, \
             patch("src.api.routes.documents.SourceService"):

            # Mock DocumentService
            mock_doc_service = MagicMock()
            mock_doc_service.create_document = AsyncMock(return_value=(True, {
                "document": {
                    "id": document_id,
                    "source_id": uuid4(),
                    "title": "test.pdf",
                    "document_type": "pdf",
                    "url": None,
                    "created_at": "2025-10-16T10:00:00",
                    "updated_at": "2025-10-16T10:00:00",
                    "metadata": {},
                }
            }))
            mock_doc_service.delete_document = AsyncMock(return_value=(True, {}))
            MockDocService.return_value = mock_doc_service

            # Mock IngestionService to fail
            mock_ingestion = MagicMock()
            mock_ingestion.ingest_document = AsyncMock(return_value=(False, {
                "error": "Embedding service unavailable"
            }))
            MockIngestion.return_value = mock_ingestion

            response = client.post(
                "/api/documents",
                data={"source_id": source_id},
                files={
                    "file": ("test.pdf", mock_uploaded_file, "application/pdf")
                }
            )

        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        detail = data["detail"]
        assert "ingestion" in str(detail).lower() or "failed" in str(detail).lower()
