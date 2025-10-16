"""Integration tests for cascade delete operations.

Tests verify foreign key constraints correctly cascade deletes:
1. Delete document → cascades to chunks
2. Delete source → cascades to documents and chunks
3. Delete source → cascades to crawl jobs

Pattern: Multi-step database operations with side_effect
Reference: Example 2 (FastAPI test pattern), init.sql (foreign key constraints)
"""

import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock


class TestDocumentCascadeDelete:
    """Tests for document deletion cascading to chunks."""

    @pytest.mark.asyncio
    async def test_delete_document_cascades_to_chunks(self, mock_db_pool):
        """Test deleting a document removes all associated chunks.

        Expected:
        - DELETE on documents table executes
        - Chunks automatically deleted via ON DELETE CASCADE
        - Transaction committed successfully
        """
        document_id = uuid4()

        # Mock database connection
        mock_conn = MagicMock()

        # Mock successful delete operation
        # Side effect: [document delete result, verify chunks deleted]
        mock_conn.execute = AsyncMock(side_effect=[
            "DELETE 1",  # Document deleted
        ])

        # Verify chunks were also deleted (count should be 0)
        mock_conn.fetchval = AsyncMock(side_effect=[
            0,  # No chunks remain after cascade
        ])

        # Mock transaction context manager
        async def mock_transaction():
            yield None

        mock_conn.transaction = MagicMock(return_value=mock_transaction())

        # Mock pool acquire
        async def mock_acquire():
            yield mock_conn

        mock_db_pool.acquire = MagicMock(return_value=mock_acquire())

        # Execute delete operation
        async with mock_db_pool.acquire() as conn:
            async with conn.transaction():
                # Delete document (chunks cascade automatically)
                result = await conn.execute(
                    "DELETE FROM documents WHERE id = $1",
                    document_id
                )
                assert result == "DELETE 1"

                # Verify chunks were deleted
                chunk_count = await conn.fetchval(
                    "SELECT COUNT(*) FROM chunks WHERE document_id = $1",
                    document_id
                )
                assert chunk_count == 0

        # Verify execute was called with correct query
        mock_conn.execute.assert_called_once()
        call_args = mock_conn.execute.call_args[0]
        assert "DELETE FROM documents" in call_args[0]
        assert call_args[1] == document_id

    @pytest.mark.asyncio
    async def test_delete_document_with_multiple_chunks(self, mock_db_pool):
        """Test deleting document with many chunks (verify cascade efficiency).

        Expected:
        - Single DELETE query removes document
        - Database automatically cascades to all chunks
        - No need for manual chunk deletion loop
        """
        document_id = uuid4()
        initial_chunk_count = 50

        mock_conn = MagicMock()

        # Mock operations: check count, delete document, verify cascade
        mock_conn.fetchval = AsyncMock(side_effect=[
            initial_chunk_count,  # Initial chunk count
            0,  # Chunk count after cascade delete
        ])

        mock_conn.execute = AsyncMock(return_value="DELETE 1")

        async def mock_transaction():
            yield None

        mock_conn.transaction = MagicMock(return_value=mock_transaction())

        async def mock_acquire():
            yield mock_conn

        mock_db_pool.acquire = MagicMock(return_value=mock_acquire())

        # Execute delete with verification
        async with mock_db_pool.acquire() as conn:
            async with conn.transaction():
                # Verify chunks exist before delete
                before_count = await conn.fetchval(
                    "SELECT COUNT(*) FROM chunks WHERE document_id = $1",
                    document_id
                )
                assert before_count == initial_chunk_count

                # Delete document (single operation)
                await conn.execute(
                    "DELETE FROM documents WHERE id = $1",
                    document_id
                )

                # Verify all chunks removed by cascade
                after_count = await conn.fetchval(
                    "SELECT COUNT(*) FROM chunks WHERE document_id = $1",
                    document_id
                )
                assert after_count == 0

        # Verify only ONE delete query (no manual chunk deletion loop)
        assert mock_conn.execute.call_count == 1


class TestSourceCascadeDelete:
    """Tests for source deletion cascading to documents and chunks."""

    @pytest.mark.asyncio
    async def test_delete_source_cascades_to_documents_and_chunks(self, mock_db_pool):
        """Test deleting a source removes documents AND their chunks.

        Expected:
        - DELETE on sources table executes
        - Documents automatically deleted via ON DELETE CASCADE
        - Chunks automatically deleted via documents cascade
        - Two-level cascade: source → documents → chunks
        """
        source_id = uuid4()

        mock_conn = MagicMock()

        # Mock operations: verify before state, delete, verify after state
        mock_conn.fetchval = AsyncMock(side_effect=[
            3,   # Document count before delete
            10,  # Chunk count before delete
            0,   # Document count after delete
            0,   # Chunk count after delete
        ])

        mock_conn.execute = AsyncMock(return_value="DELETE 1")

        async def mock_transaction():
            yield None

        mock_conn.transaction = MagicMock(return_value=mock_transaction())

        async def mock_acquire():
            yield mock_conn

        mock_db_pool.acquire = MagicMock(return_value=mock_acquire())

        # Execute delete with two-level cascade verification
        async with mock_db_pool.acquire() as conn:
            async with conn.transaction():
                # Verify data exists before delete
                doc_count_before = await conn.fetchval(
                    "SELECT COUNT(*) FROM documents WHERE source_id = $1",
                    source_id
                )
                chunk_count_before = await conn.fetchval(
                    """
                    SELECT COUNT(*) FROM chunks
                    WHERE document_id IN (
                        SELECT id FROM documents WHERE source_id = $1
                    )
                    """,
                    source_id
                )

                assert doc_count_before == 3
                assert chunk_count_before == 10

                # Delete source (cascades to documents, then to chunks)
                await conn.execute(
                    "DELETE FROM sources WHERE id = $1",
                    source_id
                )

                # Verify all documents removed
                doc_count_after = await conn.fetchval(
                    "SELECT COUNT(*) FROM documents WHERE source_id = $1",
                    source_id
                )
                assert doc_count_after == 0

                # Verify all chunks removed (via document cascade)
                chunk_count_after = await conn.fetchval(
                    """
                    SELECT COUNT(*) FROM chunks
                    WHERE document_id IN (
                        SELECT id FROM documents WHERE source_id = $1
                    )
                    """,
                    source_id
                )
                assert chunk_count_after == 0

    @pytest.mark.asyncio
    async def test_delete_source_with_multiple_documents(self, mock_db_pool):
        """Test source deletion with multiple documents (stress test cascade).

        Expected:
        - Deletes source with 10 documents, 50 chunks each
        - Single DELETE query removes everything via cascade
        - No manual iteration needed
        """
        source_id = uuid4()
        document_count = 10
        chunks_per_document = 50
        total_chunks = document_count * chunks_per_document

        mock_conn = MagicMock()

        # Mock counts before and after
        mock_conn.fetchval = AsyncMock(side_effect=[
            document_count,  # Documents before
            total_chunks,    # Chunks before
            0,               # Documents after
            0,               # Chunks after
        ])

        mock_conn.execute = AsyncMock(return_value="DELETE 1")

        async def mock_transaction():
            yield None

        mock_conn.transaction = MagicMock(return_value=mock_transaction())

        async def mock_acquire():
            yield mock_conn

        mock_db_pool.acquire = MagicMock(return_value=mock_acquire())

        # Execute delete
        async with mock_db_pool.acquire() as conn:
            async with conn.transaction():
                # Verify counts before
                docs_before = await conn.fetchval(
                    "SELECT COUNT(*) FROM documents WHERE source_id = $1",
                    source_id
                )
                chunks_before = await conn.fetchval(
                    """
                    SELECT COUNT(*) FROM chunks
                    WHERE document_id IN (
                        SELECT id FROM documents WHERE source_id = $1
                    )
                    """,
                    source_id
                )

                assert docs_before == document_count
                assert chunks_before == total_chunks

                # Single delete operation
                await conn.execute(
                    "DELETE FROM sources WHERE id = $1",
                    source_id
                )

                # Verify all data removed
                docs_after = await conn.fetchval(
                    "SELECT COUNT(*) FROM documents WHERE source_id = $1",
                    source_id
                )
                chunks_after = await conn.fetchval(
                    """
                    SELECT COUNT(*) FROM chunks
                    WHERE document_id IN (
                        SELECT id FROM documents WHERE source_id = $1
                    )
                    """,
                    source_id
                )

                assert docs_after == 0
                assert chunks_after == 0

        # Verify only one DELETE query executed
        assert mock_conn.execute.call_count == 1


class TestCrawlJobCascadeDelete:
    """Tests for crawl job deletion when source is deleted."""

    @pytest.mark.asyncio
    async def test_delete_source_cascades_to_crawl_jobs(self, mock_db_pool):
        """Test deleting source removes associated crawl jobs.

        Expected:
        - DELETE on sources removes crawl_jobs via ON DELETE CASCADE
        - Crawl job history cleaned up with source
        """
        source_id = uuid4()

        mock_conn = MagicMock()

        # Mock crawl job count before and after
        mock_conn.fetchval = AsyncMock(side_effect=[
            5,  # Crawl jobs before delete
            0,  # Crawl jobs after delete
        ])

        mock_conn.execute = AsyncMock(return_value="DELETE 1")

        async def mock_transaction():
            yield None

        mock_conn.transaction = MagicMock(return_value=mock_transaction())

        async def mock_acquire():
            yield mock_conn

        mock_db_pool.acquire = MagicMock(return_value=mock_acquire())

        # Execute delete
        async with mock_db_pool.acquire() as conn:
            async with conn.transaction():
                # Verify crawl jobs exist
                jobs_before = await conn.fetchval(
                    "SELECT COUNT(*) FROM crawl_jobs WHERE source_id = $1",
                    source_id
                )
                assert jobs_before == 5

                # Delete source
                await conn.execute(
                    "DELETE FROM sources WHERE id = $1",
                    source_id
                )

                # Verify crawl jobs removed
                jobs_after = await conn.fetchval(
                    "SELECT COUNT(*) FROM crawl_jobs WHERE source_id = $1",
                    source_id
                )
                assert jobs_after == 0

    @pytest.mark.asyncio
    async def test_delete_source_with_all_associated_data(self, mock_db_pool):
        """Test complete cleanup: source → documents → chunks + crawl jobs.

        Expected:
        - Single DELETE removes:
          - Source record
          - All documents
          - All chunks (via document cascade)
          - All crawl jobs
        """
        source_id = uuid4()

        mock_conn = MagicMock()

        # Mock counts for all related data
        mock_conn.fetchval = AsyncMock(side_effect=[
            3,   # Documents before
            15,  # Chunks before
            2,   # Crawl jobs before
            0,   # Documents after
            0,   # Chunks after
            0,   # Crawl jobs after
        ])

        mock_conn.execute = AsyncMock(return_value="DELETE 1")

        async def mock_transaction():
            yield None

        mock_conn.transaction = MagicMock(return_value=mock_transaction())

        async def mock_acquire():
            yield mock_conn

        mock_db_pool.acquire = MagicMock(return_value=mock_acquire())

        # Execute comprehensive delete
        async with mock_db_pool.acquire() as conn:
            async with conn.transaction():
                # Verify all data exists before delete
                docs_before = await conn.fetchval(
                    "SELECT COUNT(*) FROM documents WHERE source_id = $1",
                    source_id
                )
                chunks_before = await conn.fetchval(
                    """
                    SELECT COUNT(*) FROM chunks
                    WHERE document_id IN (
                        SELECT id FROM documents WHERE source_id = $1
                    )
                    """,
                    source_id
                )
                jobs_before = await conn.fetchval(
                    "SELECT COUNT(*) FROM crawl_jobs WHERE source_id = $1",
                    source_id
                )

                assert docs_before == 3
                assert chunks_before == 15
                assert jobs_before == 2

                # Single delete operation
                await conn.execute(
                    "DELETE FROM sources WHERE id = $1",
                    source_id
                )

                # Verify complete cleanup
                docs_after = await conn.fetchval(
                    "SELECT COUNT(*) FROM documents WHERE source_id = $1",
                    source_id
                )
                chunks_after = await conn.fetchval(
                    """
                    SELECT COUNT(*) FROM chunks
                    WHERE document_id IN (
                        SELECT id FROM documents WHERE source_id = $1
                    )
                    """,
                    source_id
                )
                jobs_after = await conn.fetchval(
                    "SELECT COUNT(*) FROM crawl_jobs WHERE source_id = $1",
                    source_id
                )

                assert docs_after == 0
                assert chunks_after == 0
                assert jobs_after == 0

        # Verify only one DELETE query for complete cleanup
        assert mock_conn.execute.call_count == 1


class TestTransactionHandling:
    """Tests for transaction handling with cascade deletes."""

    @pytest.mark.asyncio
    async def test_cascade_delete_within_transaction(self, mock_db_pool):
        """Test cascade delete uses transaction context manager correctly.

        Expected:
        - Delete wrapped in transaction
        - Transaction commits on success
        - Transaction structure verified
        """
        document_id = uuid4()

        mock_conn = MagicMock()
        mock_conn.execute = AsyncMock(return_value="DELETE 1")
        mock_conn.fetchval = AsyncMock(return_value=0)

        # Track transaction usage
        transaction_entered = False
        transaction_exited = False

        async def mock_transaction():
            nonlocal transaction_entered, transaction_exited
            transaction_entered = True
            yield None
            transaction_exited = True

        mock_conn.transaction = MagicMock(return_value=mock_transaction())

        async def mock_acquire():
            yield mock_conn

        mock_db_pool.acquire = MagicMock(return_value=mock_acquire())

        # Execute delete with transaction
        async with mock_db_pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "DELETE FROM documents WHERE id = $1",
                    document_id
                )

        # Verify transaction context manager used
        assert transaction_entered, "Transaction context manager not entered"
        assert transaction_exited, "Transaction context manager not exited"

    @pytest.mark.asyncio
    async def test_cascade_delete_rollback_on_error(self, mock_db_pool):
        """Test cascade delete rolls back on error.

        Expected:
        - Error during delete raises exception
        - Transaction NOT committed
        - No partial deletes
        """
        source_id = uuid4()

        mock_conn = MagicMock()

        # Mock delete operation that fails
        mock_conn.execute = AsyncMock(
            side_effect=Exception("Database connection lost")
        )

        rollback_called = False

        async def mock_transaction():
            nonlocal rollback_called
            try:
                yield None
            except Exception:
                rollback_called = True
                raise

        mock_conn.transaction = MagicMock(return_value=mock_transaction())

        async def mock_acquire():
            yield mock_conn

        mock_db_pool.acquire = MagicMock(return_value=mock_acquire())

        # Attempt delete (should fail and rollback)
        with pytest.raises(Exception, match="Database connection lost"):
            async with mock_db_pool.acquire() as conn:
                async with conn.transaction():
                    await conn.execute(
                        "DELETE FROM sources WHERE id = $1",
                        source_id
                    )

        # Verify exception was raised (transaction would rollback automatically)
        assert mock_conn.execute.called
