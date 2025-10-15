"""Unit tests for IngestionService.

Tests cover:
1. ingest_document pipeline (parse → chunk → embed → store)
2. ingest_from_crawl orchestration (Task 3 integration)
3. Partial embedding failure handling (Gotcha #1)
4. Atomic storage transaction pattern
5. Error handling and rollback

Pattern: pytest-asyncio with mocked dependencies
Reference: prps/rag_service_completion_phase2.md (Task 8)
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.services.ingestion_service import IngestionService
from src.services.chunker import Chunk
from src.models.search_result import EmbeddingBatchResult


@pytest.fixture
def mock_dependencies(mock_db_pool):
    """Create mocked service dependencies for IngestionService."""
    from src.services.document_parser import DocumentParser
    from src.services.chunker import TextChunker
    from src.services.embeddings.embedding_service import EmbeddingService
    from src.services.vector_service import VectorService
    from src.services.document_service import DocumentService
    from src.services.crawler.crawl_service import CrawlerService

    # Create mock services
    document_parser = MagicMock(spec=DocumentParser)
    document_parser.parse_document = AsyncMock()

    text_chunker = MagicMock(spec=TextChunker)
    text_chunker.chunk_text = AsyncMock()

    embedding_service = MagicMock(spec=EmbeddingService)
    embedding_service.batch_embed = AsyncMock()

    vector_service = MagicMock(spec=VectorService)
    vector_service.upsert_vectors = AsyncMock()

    document_service = MagicMock(spec=DocumentService)
    document_service.delete_document = AsyncMock()

    crawler_service = MagicMock(spec=CrawlerService)
    crawler_service.crawl_website = AsyncMock()

    return {
        "db_pool": mock_db_pool,
        "document_parser": document_parser,
        "text_chunker": text_chunker,
        "embedding_service": embedding_service,
        "vector_service": vector_service,
        "document_service": document_service,
        "crawler_service": crawler_service,
    }


@pytest.fixture
def ingestion_service(mock_dependencies):
    """Create IngestionService with mocked dependencies."""
    return IngestionService(**mock_dependencies)


class TestIngestionServiceDocumentFlow:
    """Tests for complete document ingestion pipeline."""

    @pytest.mark.asyncio
    async def test_ingest_document_success(
        self, ingestion_service, mock_dependencies, sample_embedding
    ):
        """Test successful document ingestion: parse → chunk → embed → store.

        Validates:
        - All pipeline steps executed in order
        - Document and chunks created in database
        - Vectors upserted to Qdrant
        - Success metrics returned
        """
        source_id = uuid4()

        # Mock pipeline outputs
        mock_dependencies["document_parser"].parse_document.return_value = (
            "# Test Document\n\nThis is test content." * 50  # ~1000 chars
        )

        # Create sample chunks
        sample_chunks = [
            Chunk(
                text=f"Chunk {i} content",
                chunk_index=i,
                token_count=100,
                start_char=i * 100,
                end_char=(i + 1) * 100,
            )
            for i in range(5)
        ]
        mock_dependencies["text_chunker"].chunk_text.return_value = sample_chunks

        # Mock successful embeddings
        embeddings = [sample_embedding] * 5
        mock_dependencies["embedding_service"].batch_embed.return_value = (
            EmbeddingBatchResult(
                embeddings=embeddings,
                success_count=5,
                failure_count=0,
                failed_items=[],
            )
        )

        # Mock database connection
        mock_conn = MagicMock()
        mock_conn.execute = AsyncMock()
        mock_conn.fetchrow = AsyncMock(
            return_value={"id": uuid4()}  # Document ID
        )
        mock_conn.executemany = AsyncMock()

        # Mock transaction context manager
        class MockTransaction:
            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                pass

        mock_conn.transaction = lambda: MockTransaction()

        async def mock_acquire():
            yield mock_conn

        mock_dependencies["db_pool"].acquire = MagicMock(return_value=mock_acquire())

        # Execute ingestion
        success, result = await ingestion_service.ingest_document(
            source_id=source_id,
            file_path="/tmp/test.pdf",
        )

        # Verify success
        assert success is True
        assert "document_id" in result
        assert result["chunks_stored"] == 5
        assert result["chunks_failed"] == 0
        assert result["total_chunks"] == 5

        # Verify pipeline steps called
        mock_dependencies["document_parser"].parse_document.assert_called_once_with(
            "/tmp/test.pdf"
        )
        mock_dependencies["text_chunker"].chunk_text.assert_called_once()
        mock_dependencies["embedding_service"].batch_embed.assert_called_once()

        # Verify database operations
        assert mock_conn.fetchrow.call_count >= 1  # Document INSERT
        assert mock_conn.executemany.call_count >= 1  # Chunks batch INSERT

        # Verify vector upsert
        mock_dependencies["vector_service"].upsert_vectors.assert_called_once()
        upsert_points = mock_dependencies["vector_service"].upsert_vectors.call_args[
            0
        ][0]
        assert len(upsert_points) == 5

    @pytest.mark.asyncio
    async def test_ingest_document_partial_embedding_failure(
        self, ingestion_service, mock_dependencies, sample_embedding
    ):
        """Test partial embedding failure (Gotcha #1).

        Scenario:
        - 10 chunks created
        - 7 embeddings succeed, 3 fail (quota exhaustion)
        - Only 7 chunks stored (NOT 10)

        Expected:
        - result.chunks_stored == 7
        - result.chunks_failed == 3
        - NO null embeddings stored
        """
        source_id = uuid4()

        # Mock pipeline
        mock_dependencies["document_parser"].parse_document.return_value = (
            "Content" * 200
        )

        sample_chunks = [
            Chunk(text=f"Chunk {i}", chunk_index=i, token_count=100, start_char=0, end_char=100)
            for i in range(10)
        ]
        mock_dependencies["text_chunker"].chunk_text.return_value = sample_chunks

        # CRITICAL: Partial embedding success (Gotcha #1)
        partial_embeddings = [sample_embedding] * 7  # Only 7 succeed
        mock_dependencies["embedding_service"].batch_embed.return_value = (
            EmbeddingBatchResult(
                embeddings=partial_embeddings,
                success_count=7,
                failure_count=3,
                failed_items=[
                    {"index": 7, "text": "Chunk 7", "reason": "quota_exhausted"},
                    {"index": 8, "text": "Chunk 8", "reason": "quota_exhausted"},
                    {"index": 9, "text": "Chunk 9", "reason": "quota_exhausted"},
                ],
            )
        )

        # Mock database
        mock_conn = MagicMock()
        mock_conn.execute = AsyncMock()
        mock_conn.fetchrow = AsyncMock(return_value={"id": uuid4()})
        mock_conn.executemany = AsyncMock()

        class MockTransaction:
            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                pass

        mock_conn.transaction = lambda: MockTransaction()

        async def mock_acquire():
            yield mock_conn

        mock_dependencies["db_pool"].acquire = MagicMock(return_value=mock_acquire())

        # Execute
        success, result = await ingestion_service.ingest_document(
            source_id=source_id,
            file_path="/tmp/test.pdf",
        )

        # Verify partial success
        assert success is True
        assert result["chunks_stored"] == 7  # Only successful embeddings stored
        assert result["chunks_failed"] == 3
        assert result["total_chunks"] == 10

        # CRITICAL: Verify only 7 chunks inserted (not 10)
        executemany_call = mock_conn.executemany.call_args
        chunk_records = executemany_call[0][1]  # Second argument is the data
        assert len(chunk_records) == 7, "Should only store chunks with successful embeddings"

        # Verify vector upsert only has 7 vectors
        upsert_call = mock_dependencies["vector_service"].upsert_vectors.call_args[0][0]
        assert len(upsert_call) == 7

    @pytest.mark.asyncio
    async def test_ingest_document_file_not_found(
        self, ingestion_service, mock_dependencies
    ):
        """Test ingestion with non-existent file.

        Expected:
        - Returns (False, error_dict)
        - Error message indicates file not found
        """
        source_id = uuid4()

        # Mock parser to raise FileNotFoundError
        mock_dependencies["document_parser"].parse_document.side_effect = (
            FileNotFoundError("/tmp/missing.pdf not found")
        )

        # Execute
        success, result = await ingestion_service.ingest_document(
            source_id=source_id,
            file_path="/tmp/missing.pdf",
        )

        # Verify failure
        assert success is False
        assert "error" in result
        assert "File not found" in result["error"]

    @pytest.mark.asyncio
    async def test_ingest_document_empty_parsed_content(
        self, ingestion_service, mock_dependencies
    ):
        """Test ingestion when document parsing produces no text.

        Expected:
        - Returns (False, error_dict)
        - Error indicates no text extracted
        """
        source_id = uuid4()

        # Mock empty parse result
        mock_dependencies["document_parser"].parse_document.return_value = ""

        # Execute
        success, result = await ingestion_service.ingest_document(
            source_id=source_id,
            file_path="/tmp/empty.pdf",
        )

        # Verify failure
        assert success is False
        assert "error" in result
        assert "no text" in result["error"].lower()


class TestIngestionServiceCrawlFlow:
    """Tests for crawl ingestion (Task 3 integration)."""

    @pytest.mark.asyncio
    async def test_ingest_from_crawl_success(
        self, ingestion_service, mock_dependencies, sample_embedding
    ):
        """Test successful crawl → chunk → embed → store pipeline.

        Validates:
        - CrawlerService.crawl_website called
        - Markdown content chunked (skip parsing step)
        - Chunks embedded and stored
        - Crawl job metadata included
        """
        source_id = uuid4()
        job_id = uuid4()

        # Mock crawl result
        crawl_result = {
            "job_id": str(job_id),
            "pages_crawled": 5,
            "content": "# Crawled Page\n\n" + ("Paragraph content. " * 200),  # ~2KB markdown
            "crawl_time_ms": 5000,
        }
        mock_dependencies["crawler_service"].crawl_website.return_value = (
            True,
            crawl_result,
        )

        # Mock chunking
        sample_chunks = [
            Chunk(text=f"Chunk {i}", chunk_index=i, token_count=100, start_char=0, end_char=100)
            for i in range(10)
        ]
        mock_dependencies["text_chunker"].chunk_text.return_value = sample_chunks

        # Mock embeddings
        embeddings = [sample_embedding] * 10
        mock_dependencies["embedding_service"].batch_embed.return_value = (
            EmbeddingBatchResult(
                embeddings=embeddings,
                success_count=10,
                failure_count=0,
                failed_items=[],
            )
        )

        # Mock database
        mock_conn = MagicMock()
        mock_conn.execute = AsyncMock()
        mock_conn.fetchrow = AsyncMock(return_value={"id": uuid4()})
        mock_conn.executemany = AsyncMock()

        class MockTransaction:
            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                pass

        mock_conn.transaction = lambda: MockTransaction()

        async def mock_acquire():
            yield mock_conn

        mock_dependencies["db_pool"].acquire = MagicMock(return_value=mock_acquire())

        # Execute crawl ingestion
        success, result = await ingestion_service.ingest_from_crawl(
            source_id=source_id,
            url="https://docs.example.com",
            max_pages=10,
            recursive=False,
        )

        # Verify success
        assert success is True
        assert "document_id" in result
        assert "crawl_job_id" in result
        assert result["pages_crawled"] == 5
        assert result["chunks_stored"] == 10
        assert "crawl_time_ms" in result
        assert "ingestion_time_ms" in result

        # Verify crawler called
        mock_dependencies["crawler_service"].crawl_website.assert_called_once_with(
            source_id=source_id,
            url="https://docs.example.com",
            max_pages=10,
            recursive=False,
        )

        # Verify document parser NOT called (crawl provides markdown)
        mock_dependencies["document_parser"].parse_document.assert_not_called()

        # Verify chunking called with markdown
        mock_dependencies["text_chunker"].chunk_text.assert_called_once()

        # Verify document metadata includes crawl info
        document_insert_call = mock_conn.fetchrow.call_args
        # Metadata should be in the call arguments
        assert any("crawl_job_id" in str(arg) for arg in document_insert_call[0])

    @pytest.mark.asyncio
    async def test_ingest_from_crawl_crawler_failure(
        self, ingestion_service, mock_dependencies
    ):
        """Test crawl ingestion when crawler fails.

        Expected:
        - Returns (False, error_dict)
        - Error includes crawl_job_id
        - No embedding or storage attempted
        """
        source_id = uuid4()
        job_id = uuid4()

        # Mock crawler failure
        mock_dependencies["crawler_service"].crawl_website.return_value = (
            False,
            {
                "error": "Crawl failed: Network timeout",
                "job_id": str(job_id),
            },
        )

        # Execute
        success, result = await ingestion_service.ingest_from_crawl(
            source_id=source_id,
            url="https://timeout.example.com",
            max_pages=10,
        )

        # Verify failure
        assert success is False
        assert "error" in result
        assert result["crawl_job_id"] == str(job_id)
        assert "Crawl failed" in result["error"]

        # Verify chunking NOT attempted
        mock_dependencies["text_chunker"].chunk_text.assert_not_called()
        mock_dependencies["embedding_service"].batch_embed.assert_not_called()

    @pytest.mark.asyncio
    async def test_ingest_from_crawl_no_crawler_service(
        self, mock_dependencies
    ):
        """Test ingest_from_crawl when crawler_service not initialized.

        Expected:
        - Returns (False, error_dict)
        - Error indicates crawler not available
        """
        # Create IngestionService WITHOUT crawler_service
        ingestion_service = IngestionService(
            db_pool=mock_dependencies["db_pool"],
            document_parser=mock_dependencies["document_parser"],
            text_chunker=mock_dependencies["text_chunker"],
            embedding_service=mock_dependencies["embedding_service"],
            vector_service=mock_dependencies["vector_service"],
            document_service=mock_dependencies["document_service"],
            crawler_service=None,  # NOT initialized
        )

        # Execute
        success, result = await ingestion_service.ingest_from_crawl(
            source_id=uuid4(),
            url="https://example.com",
            max_pages=10,
        )

        # Verify failure
        assert success is False
        assert "CrawlerService not initialized" in result["error"]


class TestIngestionServiceDeleteDocument:
    """Tests for document deletion (inverse of ingestion)."""

    @pytest.mark.asyncio
    async def test_delete_document_success(
        self, ingestion_service, mock_dependencies
    ):
        """Test successful document deletion from PostgreSQL + Qdrant.

        Expected:
        - Qdrant vectors deleted first
        - PostgreSQL document deleted (CASCADE deletes chunks)
        - Success result returned
        """
        document_id = uuid4()

        # Mock vector deletion
        mock_dependencies["vector_service"].delete_by_filter = AsyncMock()

        # Mock document service deletion
        mock_dependencies["document_service"].delete_document.return_value = (
            True,
            {"message": "Document deleted"},
        )

        # Execute
        success, result = await ingestion_service.delete_document(document_id)

        # Verify success
        assert success is True
        assert "Document" in result["message"]
        assert str(document_id) in result["message"]

        # Verify Qdrant deletion called
        mock_dependencies["vector_service"].delete_by_filter.assert_called_once_with(
            {"document_id": str(document_id)}
        )

        # Verify PostgreSQL deletion called
        mock_dependencies["document_service"].delete_document.assert_called_once_with(
            document_id
        )

    @pytest.mark.asyncio
    async def test_delete_document_qdrant_failure_continues(
        self, ingestion_service, mock_dependencies
    ):
        """Test that PostgreSQL deletion continues if Qdrant fails.

        Expected:
        - Qdrant deletion fails (logged)
        - PostgreSQL deletion still attempted
        - Success if PostgreSQL succeeds
        """
        document_id = uuid4()

        # Mock Qdrant failure
        mock_dependencies["vector_service"].delete_by_filter = AsyncMock(
            side_effect=Exception("Qdrant connection lost")
        )

        # Mock PostgreSQL success
        mock_dependencies["document_service"].delete_document.return_value = (
            True,
            {"message": "Document deleted from database"},
        )

        # Execute
        success, result = await ingestion_service.delete_document(document_id)

        # Verify success (PostgreSQL deletion succeeded)
        assert success is True

        # Verify both deletion attempts made
        mock_dependencies["vector_service"].delete_by_filter.assert_called_once()
        mock_dependencies["document_service"].delete_document.assert_called_once()


class TestIngestionServiceErrorHandling:
    """Tests for error handling and edge cases."""

    @pytest.mark.asyncio
    async def test_ingest_document_all_embeddings_fail(
        self, ingestion_service, mock_dependencies
    ):
        """Test ingestion when ALL embeddings fail (quota exhaustion).

        Expected:
        - Returns (False, error_dict)
        - Error indicates quota exhausted
        - NO chunks stored
        """
        source_id = uuid4()

        # Mock pipeline
        mock_dependencies["document_parser"].parse_document.return_value = "Content"

        sample_chunks = [
            Chunk(text="Chunk", chunk_index=0, token_count=100, start_char=0, end_char=100)
        ]
        mock_dependencies["text_chunker"].chunk_text.return_value = sample_chunks

        # All embeddings fail
        mock_dependencies["embedding_service"].batch_embed.return_value = (
            EmbeddingBatchResult(
                embeddings=[],
                success_count=0,
                failure_count=1,
                failed_items=[{"index": 0, "text": "Chunk", "reason": "quota_exhausted"}],
            )
        )

        # Execute
        success, result = await ingestion_service.ingest_document(
            source_id=source_id,
            file_path="/tmp/test.pdf",
        )

        # Verify failure
        assert success is False
        assert "All embeddings failed" in result["error"]
        assert "failed_items" in result

    @pytest.mark.asyncio
    async def test_ingest_document_chunking_failure(
        self, ingestion_service, mock_dependencies
    ):
        """Test ingestion when text chunking fails.

        Expected:
        - Returns (False, error_dict)
        - Error indicates chunking failed
        """
        source_id = uuid4()

        # Mock parsing success
        mock_dependencies["document_parser"].parse_document.return_value = "Content"

        # Mock chunking failure
        mock_dependencies["text_chunker"].chunk_text.side_effect = Exception(
            "Chunking error"
        )

        # Execute
        success, result = await ingestion_service.ingest_document(
            source_id=source_id,
            file_path="/tmp/test.pdf",
        )

        # Verify failure
        assert success is False
        assert "Text chunking failed" in result["error"]

    @pytest.mark.asyncio
    async def test_ingest_document_zero_chunks_produced(
        self, ingestion_service, mock_dependencies
    ):
        """Test ingestion when chunking produces no chunks.

        Expected:
        - Returns (False, error_dict)
        - Error indicates no chunks
        """
        source_id = uuid4()

        # Mock parsing
        mock_dependencies["document_parser"].parse_document.return_value = "x"

        # Mock chunking returns empty list
        mock_dependencies["text_chunker"].chunk_text.return_value = []

        # Execute
        success, result = await ingestion_service.ingest_document(
            source_id=source_id,
            file_path="/tmp/tiny.pdf",
        )

        # Verify failure
        assert success is False
        assert "no chunks" in result["error"].lower()
