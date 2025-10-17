"""Unit tests for DocumentService business logic.

Tests cover:
1. list_documents() with filters (source_id, document_type)
2. list_documents() pagination (page, per_page)
3. create_document() success path
4. create_document() database error handling
5. delete_document() cascade to chunks

Pattern: Async fixtures with side_effect for sequential mock returns
Reference: prps/rag_service_testing_validation/examples/example_1_test_fixtures.py
Reference: prps/rag_service_testing_validation/examples/example_2_fastapi_test_pattern.py
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
import asyncpg
from src.services.document_service import DocumentService


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def document_service(mock_db_pool):
    """DocumentService instance with mocked database pool.

    Returns:
        DocumentService: Service instance for testing
    """
    return DocumentService(db_pool=mock_db_pool)


def setup_mock_connection(mock_db_pool, mock_conn):
    """Helper to properly configure async context manager for database pool.

    CRITICAL PATTERN: asyncpg pool.acquire() returns async context manager
    - Must mock __aenter__ to return connection
    - Must mock __aexit__ to handle context exit
    - __aexit__ must return False/None to not suppress exceptions

    Args:
        mock_db_pool: Mocked database pool
        mock_conn: Mocked connection to return from acquire()
    """
    mock_db_pool.acquire.return_value.__aenter__.return_value = mock_conn
    mock_db_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=False)


# =============================================================================
# Test list_documents() - Filtering
# =============================================================================

class TestListDocumentsFiltering:
    """Tests for list_documents() with various filters."""

    @pytest.mark.asyncio
    async def test_list_documents_no_filters(self, document_service, mock_db_pool, sample_document):
        """Test listing documents without any filters.

        Expected:
        - Returns all documents
        - No WHERE clause in query
        - Pagination applied
        """
        # Mock database responses
        mock_conn = MagicMock()
        mock_conn.fetchval = AsyncMock(return_value=1)  # total_count
        mock_conn.fetch = AsyncMock(return_value=[sample_document])
        setup_mock_connection(mock_db_pool, mock_conn)

        # Call service method
        success, result = await document_service.list_documents()

        # Verify results
        assert success is True
        assert "documents" in result
        assert "total_count" in result
        assert result["total_count"] == 1
        assert len(result["documents"]) == 1
        assert result["documents"][0]["id"] == sample_document["id"]

    @pytest.mark.asyncio
    async def test_list_documents_filter_by_source_id(self, document_service, mock_db_pool, sample_document, sample_source):
        """Test listing documents filtered by source_id.

        Expected:
        - Returns only documents for that source
        - WHERE clause includes source_id = $1
        """
        source_id = sample_source["id"]

        # Mock database responses
        mock_conn = MagicMock()
        mock_conn.fetchval = AsyncMock(return_value=1)  # total_count
        mock_conn.fetch = AsyncMock(return_value=[sample_document])

        setup_mock_connection(mock_db_pool, mock_conn)

        # Call service method with source_id filter
        success, result = await document_service.list_documents(
            filters={"source_id": source_id}
        )

        # Verify results
        assert success is True
        assert result["total_count"] == 1
        assert len(result["documents"]) == 1

        # Verify mock was called with correct parameters
        mock_conn.fetchval.assert_called_once()
        mock_conn.fetch.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_documents_filter_by_document_type(self, document_service, mock_db_pool, sample_document):
        """Test listing documents filtered by document_type.

        Expected:
        - Returns only documents of that type
        - WHERE clause includes document_type = $1
        """
        # Mock database responses
        mock_conn = MagicMock()
        mock_conn.fetchval = AsyncMock(return_value=1)  # total_count
        mock_conn.fetch = AsyncMock(return_value=[sample_document])

        setup_mock_connection(mock_db_pool, mock_conn)

        # Call service method with document_type filter
        success, result = await document_service.list_documents(
            filters={"document_type": "pdf"}
        )

        # Verify results
        assert success is True
        assert result["total_count"] == 1
        assert len(result["documents"]) == 1

    @pytest.mark.asyncio
    async def test_list_documents_invalid_document_type(self, document_service, mock_db_pool):
        """Test listing documents with invalid document_type.

        Expected:
        - Returns error tuple (False, {"error": "..."})
        - Error message lists valid types
        """
        # Call service method with invalid document_type
        success, result = await document_service.list_documents(
            filters={"document_type": "invalid_type"}
        )

        # Verify error response
        assert success is False
        assert "error" in result
        assert "Invalid document_type" in result["error"]
        assert "pdf" in result["error"]  # Valid types listed

    @pytest.mark.asyncio
    async def test_list_documents_combined_filters(self, document_service, mock_db_pool, sample_document, sample_source):
        """Test listing documents with multiple filters.

        Expected:
        - WHERE clause includes both source_id AND document_type
        - Returns only documents matching all filters
        """
        source_id = sample_source["id"]

        # Mock database responses
        mock_conn = MagicMock()
        mock_conn.fetchval = AsyncMock(return_value=1)  # total_count
        mock_conn.fetch = AsyncMock(return_value=[sample_document])

        setup_mock_connection(mock_db_pool, mock_conn)

        # Call service method with combined filters
        success, result = await document_service.list_documents(
            filters={
                "source_id": source_id,
                "document_type": "pdf"
            }
        )

        # Verify results
        assert success is True
        assert result["total_count"] == 1


# =============================================================================
# Test list_documents() - Pagination
# =============================================================================

class TestListDocumentsPagination:
    """Tests for list_documents() pagination parameters."""

    @pytest.mark.asyncio
    async def test_list_documents_default_pagination(self, document_service, mock_db_pool, sample_document):
        """Test listing documents with default pagination.

        Expected:
        - page=1, per_page=50 (defaults)
        - OFFSET 0, LIMIT 50
        """
        # Mock database responses
        mock_conn = MagicMock()
        mock_conn.fetchval = AsyncMock(return_value=100)  # total_count
        mock_conn.fetch = AsyncMock(return_value=[sample_document])

        setup_mock_connection(mock_db_pool, mock_conn)

        # Call service method (no pagination params = defaults)
        success, result = await document_service.list_documents()

        # Verify pagination metadata
        assert success is True
        assert result["page"] == 1
        assert result["per_page"] == 50
        assert result["total_count"] == 100

    @pytest.mark.asyncio
    async def test_list_documents_custom_pagination(self, document_service, mock_db_pool, sample_document):
        """Test listing documents with custom pagination.

        Expected:
        - page=2, per_page=10
        - OFFSET 10, LIMIT 10
        """
        # Mock database responses
        mock_conn = MagicMock()
        mock_conn.fetchval = AsyncMock(return_value=50)  # total_count
        mock_conn.fetch = AsyncMock(return_value=[sample_document])

        setup_mock_connection(mock_db_pool, mock_conn)

        # Call service method with custom pagination
        success, result = await document_service.list_documents(
            page=2,
            per_page=10
        )

        # Verify pagination metadata
        assert success is True
        assert result["page"] == 2
        assert result["per_page"] == 10
        assert result["total_count"] == 50

    @pytest.mark.asyncio
    async def test_list_documents_exclude_large_fields(self, document_service, mock_db_pool):
        """Test listing documents with exclude_large_fields=True.

        Expected:
        - SELECT id, source_id, title, ... (no metadata)
        - Metadata JSONB field excluded for performance
        """
        # Mock database responses (without metadata field)
        doc_without_metadata = {
            "id": str(uuid4()),
            "source_id": str(uuid4()),
            "title": "Test Document",
            "document_type": "pdf",
            "url": None,
            "created_at": "2025-10-16T10:00:00",
            "updated_at": "2025-10-16T10:00:00",
        }

        mock_conn = MagicMock()
        mock_conn.fetchval = AsyncMock(return_value=1)
        mock_conn.fetch = AsyncMock(return_value=[doc_without_metadata])

        setup_mock_connection(mock_db_pool, mock_conn)

        # Call service method with exclude_large_fields=True
        success, result = await document_service.list_documents(
            exclude_large_fields=True
        )

        # Verify results
        assert success is True
        assert len(result["documents"]) == 1
        # Metadata should not be in the document
        assert "metadata" not in result["documents"][0]


# =============================================================================
# Test create_document() - Success Cases
# =============================================================================

class TestCreateDocumentSuccess:
    """Tests for create_document() success paths."""

    @pytest.mark.asyncio
    async def test_create_document_minimal_fields(self, document_service, mock_db_pool, sample_source):
        """Test creating document with only required fields.

        Expected:
        - source_id and title required
        - Returns created document with generated id
        - INSERT query uses $1, $2 placeholders
        """
        source_id = sample_source["id"]
        doc_id = uuid4()

        # Mock database response
        created_doc = {
            "id": doc_id,
            "source_id": source_id,
            "title": "New Document",
            "document_type": None,
            "url": None,
            "metadata": {},
            "created_at": "2025-10-16T10:00:00",
            "updated_at": "2025-10-16T10:00:00",
        }

        mock_conn = MagicMock()
        mock_conn.fetchrow = AsyncMock(return_value=created_doc)

        setup_mock_connection(mock_db_pool, mock_conn)

        # Call service method
        success, result = await document_service.create_document(
            document_data={
                "source_id": source_id,
                "title": "New Document"
            }
        )

        # Verify results
        assert success is True
        assert "document" in result
        assert "message" in result
        assert result["document"]["id"] == doc_id
        assert result["document"]["title"] == "New Document"
        assert result["message"] == "Document created successfully"

    @pytest.mark.asyncio
    async def test_create_document_all_fields(self, document_service, mock_db_pool, sample_source):
        """Test creating document with all optional fields.

        Expected:
        - document_type, url, metadata all included
        - Metadata converted to JSONB
        """
        source_id = sample_source["id"]
        doc_id = uuid4()

        # Mock database response
        created_doc = {
            "id": doc_id,
            "source_id": source_id,
            "title": "Complete Document",
            "document_type": "pdf",
            "url": "https://example.com/doc.pdf",
            "metadata": {"filename": "doc.pdf", "file_size": 102400},
            "created_at": "2025-10-16T10:00:00",
            "updated_at": "2025-10-16T10:00:00",
        }

        mock_conn = MagicMock()
        mock_conn.fetchrow = AsyncMock(return_value=created_doc)

        setup_mock_connection(mock_db_pool, mock_conn)

        # Call service method with all fields
        success, result = await document_service.create_document(
            document_data={
                "source_id": source_id,
                "title": "Complete Document",
                "document_type": "pdf",
                "url": "https://example.com/doc.pdf",
                "metadata": {"filename": "doc.pdf", "file_size": 102400}
            }
        )

        # Verify results
        assert success is True
        assert result["document"]["document_type"] == "pdf"
        assert result["document"]["url"] == "https://example.com/doc.pdf"
        assert "filename" in result["document"]["metadata"]


# =============================================================================
# Test create_document() - Error Cases
# =============================================================================

class TestCreateDocumentErrors:
    """Tests for create_document() error handling."""

    @pytest.mark.asyncio
    async def test_create_document_missing_source_id(self, document_service, mock_db_pool):
        """Test creating document without source_id.

        Expected:
        - Returns error tuple (False, {"error": "..."})
        - Error message mentions missing source_id
        """
        # Call service method without source_id
        success, result = await document_service.create_document(
            document_data={"title": "Test Document"}
        )

        # Verify error response
        assert success is False
        assert "error" in result
        assert "source_id" in result["error"]
        assert "required" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_create_document_missing_title(self, document_service, mock_db_pool, sample_source):
        """Test creating document without title.

        Expected:
        - Returns error tuple (False, {"error": "..."})
        - Error message mentions missing title
        """
        # Call service method without title
        success, result = await document_service.create_document(
            document_data={"source_id": sample_source["id"]}
        )

        # Verify error response
        assert success is False
        assert "error" in result
        assert "title" in result["error"]
        assert "required" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_create_document_invalid_document_type(self, document_service, mock_db_pool, sample_source):
        """Test creating document with invalid document_type.

        Expected:
        - Returns error tuple (False, {"error": "..."})
        - Error message lists valid types
        """
        # Call service method with invalid document_type
        success, result = await document_service.create_document(
            document_data={
                "source_id": sample_source["id"],
                "title": "Test Document",
                "document_type": "invalid_type"
            }
        )

        # Verify error response
        assert success is False
        assert "error" in result
        assert "Invalid document_type" in result["error"]

    @pytest.mark.asyncio
    async def test_create_document_foreign_key_violation(self, document_service, mock_db_pool):
        """Test creating document with non-existent source_id.

        Expected:
        - Database raises ForeignKeyViolationError
        - Service returns user-friendly error message
        """
        # Mock database foreign key violation
        mock_conn = MagicMock()
        mock_conn.fetchrow = AsyncMock(
            side_effect=asyncpg.ForeignKeyViolationError("source_id constraint violated")
        )

        setup_mock_connection(mock_db_pool, mock_conn)

        # Call service method with non-existent source_id
        success, result = await document_service.create_document(
            document_data={
                "source_id": uuid4(),
                "title": "Test Document"
            }
        )

        # Verify error response
        assert success is False
        assert "error" in result
        assert "source does not exist" in result["error"]

    @pytest.mark.asyncio
    async def test_create_document_database_error(self, document_service, mock_db_pool, sample_source):
        """Test creating document when database error occurs.

        Expected:
        - Database raises PostgresError
        - Service returns error tuple with error message
        """
        # Mock database error
        mock_conn = MagicMock()
        mock_conn.fetchrow = AsyncMock(
            side_effect=asyncpg.PostgresError("Connection lost")
        )

        setup_mock_connection(mock_db_pool, mock_conn)

        # Call service method
        success, result = await document_service.create_document(
            document_data={
                "source_id": sample_source["id"],
                "title": "Test Document"
            }
        )

        # Verify error response
        assert success is False
        assert "error" in result
        assert "Database error" in result["error"]


# =============================================================================
# Test delete_document() - Cascade Behavior
# =============================================================================

class TestDeleteDocument:
    """Tests for delete_document() including cascade behavior."""

    @pytest.mark.asyncio
    async def test_delete_document_success(self, document_service, mock_db_pool, sample_document_id):
        """Test successful document deletion with Qdrant cleanup.

        Expected:
        - Query chunk IDs from database
        - Delete vectors from Qdrant (if vector_service provided)
        - Document deleted from database
        - Returns success tuple with message and cleanup details
        """
        doc_id = sample_document_id

        # Mock database response
        mock_conn = MagicMock()
        # Mock chunk query (returns 3 chunks)
        mock_conn.fetch = AsyncMock(return_value=[
            {"chunk_id": uuid4()},
            {"chunk_id": uuid4()},
            {"chunk_id": uuid4()},
        ])
        # Mock delete query
        mock_conn.fetchrow = AsyncMock(return_value={"id": doc_id})

        setup_mock_connection(mock_db_pool, mock_conn)

        # Call service method (without vector_service for simplicity)
        success, result = await document_service.delete_document(doc_id)

        # Verify results
        assert success is True
        assert "message" in result
        assert str(doc_id) in result["message"]
        assert "deleted successfully" in result["message"]
        assert "chunks_deleted" in result
        assert result["chunks_deleted"] == 3
        assert "qdrant_cleanup" in result
        assert result["qdrant_cleanup"] is False  # No vector_service provided

    @pytest.mark.asyncio
    async def test_delete_document_not_found(self, document_service, mock_db_pool):
        """Test deleting non-existent document.

        Expected:
        - Query chunks returns empty list
        - Delete query returns no row
        - Returns error tuple (False, {"error": "..."})
        - Error message mentions document not found
        """
        doc_id = uuid4()

        # Mock database response (no chunks, no row returned)
        mock_conn = MagicMock()
        mock_conn.fetch = AsyncMock(return_value=[])  # No chunks
        mock_conn.fetchrow = AsyncMock(return_value=None)  # Document not found

        setup_mock_connection(mock_db_pool, mock_conn)

        # Call service method
        success, result = await document_service.delete_document(doc_id)

        # Verify error response
        assert success is False
        assert "error" in result
        assert "not found" in result["error"]
        assert str(doc_id) in result["error"]

    @pytest.mark.asyncio
    async def test_delete_document_cascade_to_chunks(self, document_service, mock_db_pool, sample_document_id):
        """Test document deletion cascades to chunks.

        NOTE: Actual cascade happens via ON DELETE CASCADE foreign key
        constraint in database schema. Service now queries chunk IDs first
        for Qdrant cleanup, then deletes document (which cascades to chunks).

        Expected:
        - Query chunk IDs first (for Qdrant cleanup)
        - Document deletion succeeds
        - Associated chunks automatically deleted by database CASCADE
        """
        doc_id = sample_document_id

        # Mock database response
        mock_conn = MagicMock()
        # Mock chunk query (returns 2 chunks)
        mock_conn.fetch = AsyncMock(return_value=[
            {"chunk_id": uuid4()},
            {"chunk_id": uuid4()},
        ])
        # Mock delete query
        mock_conn.fetchrow = AsyncMock(return_value={"id": doc_id})

        setup_mock_connection(mock_db_pool, mock_conn)

        # Call service method
        success, result = await document_service.delete_document(doc_id)

        # Verify deletion succeeds
        assert success is True
        assert result["chunks_deleted"] == 2

        # Verify queries were made in correct order
        # 1. SELECT chunk_id FROM chunks WHERE document_id = $1
        # 2. DELETE FROM documents WHERE id = $1 RETURNING id
        assert mock_conn.fetch.call_count == 1
        assert mock_conn.fetchrow.call_count == 1

    @pytest.mark.asyncio
    async def test_delete_document_database_error(self, document_service, mock_db_pool):
        """Test deleting document when database error occurs.

        Expected:
        - Database raises PostgresError during chunk query
        - Service returns error tuple with error message
        """
        doc_id = uuid4()

        # Mock database error during chunk query
        mock_conn = MagicMock()
        mock_conn.fetch = AsyncMock(
            side_effect=asyncpg.PostgresError("Connection lost")
        )

        setup_mock_connection(mock_db_pool, mock_conn)

        # Call service method
        success, result = await document_service.delete_document(doc_id)

        # Verify error response
        assert success is False
        assert "error" in result
        assert "Database error" in result["error"]


# =============================================================================
# Test get_document()
# =============================================================================

class TestGetDocument:
    """Tests for get_document() method."""

    @pytest.mark.asyncio
    async def test_get_document_success(self, document_service, mock_db_pool, sample_document):
        """Test getting document by ID.

        Expected:
        - Returns document data
        - SELECT * FROM documents WHERE id = $1
        """
        doc_id = sample_document["id"]

        # Mock database response
        mock_conn = MagicMock()
        mock_conn.fetchrow = AsyncMock(return_value=sample_document)

        setup_mock_connection(mock_db_pool, mock_conn)

        # Call service method
        success, result = await document_service.get_document(doc_id)

        # Verify results
        assert success is True
        assert "document" in result
        assert result["document"]["id"] == doc_id
        assert result["document"]["title"] == sample_document["title"]

    @pytest.mark.asyncio
    async def test_get_document_not_found(self, document_service, mock_db_pool):
        """Test getting non-existent document.

        Expected:
        - Returns error tuple (False, {"error": "..."})
        - Error message mentions document not found
        """
        doc_id = uuid4()

        # Mock database response (no row returned)
        mock_conn = MagicMock()
        mock_conn.fetchrow = AsyncMock(return_value=None)

        setup_mock_connection(mock_db_pool, mock_conn)

        # Call service method
        success, result = await document_service.get_document(doc_id)

        # Verify error response
        assert success is False
        assert "error" in result
        assert "not found" in result["error"]
        assert str(doc_id) in result["error"]
