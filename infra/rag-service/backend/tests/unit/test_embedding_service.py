"""Unit tests for EmbeddingService with quota handling and cache tests.

Tests cover (PRP Task 8 requirements):
1. Quota handling with EmbeddingBatchResult pattern (Gotcha #1)
2. Cache hit rate tracking (Task 7)
3. Exponential backoff retries (Gotcha #10)
4. Batch processing with 100-text limit
5. Null embedding prevention

Pattern: pytest-asyncio with mocked OpenAI and asyncpg
Reference: prps/rag_service_completion.md (Task 8, lines 1329-1334)
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import openai

from src.services.embeddings.embedding_service import EmbeddingService
from src.models.search_result import EmbeddingBatchResult


class TestEmbeddingServiceQuotaHandling:
    """Tests for OpenAI quota exhaustion handling (Gotcha #1)."""

    @pytest.mark.asyncio
    async def test_batch_embed_quota_exhaustion_stops_immediately(
        self, mock_db_pool, mock_openai_client, sample_embedding
    ):
        """Test that batch_embed stops immediately on quota exhaustion.

        CRITICAL: Gotcha #1 protection - NEVER stores null embeddings.

        Scenario:
        - Process 300 texts in batches of 100
        - Batch 1: Success (100 embeddings)
        - Batch 2: RateLimitError (quota exhausted)
        - Batch 3: Should NOT be processed

        Expected:
        - result.success_count = 100
        - result.failure_count = 200
        - All failed items have reason="quota_exhausted"
        - NO null embeddings in result.embeddings
        """
        service = EmbeddingService(
            db_pool=mock_db_pool,
            openai_client=mock_openai_client,
        )

        # Create test texts (300 total)
        texts = [f"Text {i}" for i in range(300)]

        # Mock responses: batch 1 success, batch 2 quota exhaustion
        call_count = 0

        async def mock_create(**kwargs):
            nonlocal call_count
            call_count += 1

            if call_count == 1:
                # First batch succeeds (100 embeddings)
                return MagicMock(
                    data=[MagicMock(embedding=sample_embedding) for _ in range(100)]
                )
            else:
                # Second batch fails with quota exhaustion
                raise openai.RateLimitError(
                    "Rate limit exceeded",
                    response=MagicMock(status_code=429),
                    body=None
                )

        mock_openai_client.embeddings.create = mock_create

        # Mock cache misses (force API calls)
        with patch.object(service, '_get_cached_embedding', return_value=None):
            # Execute batch embedding
            result = await service.batch_embed(texts)

        # Verify results
        assert isinstance(result, EmbeddingBatchResult)
        assert result.success_count == 100, "Only first batch should succeed"
        assert result.failure_count == 200, "Batches 2 and 3 should fail"
        assert len(result.embeddings) == 100
        assert len(result.failed_items) == 200

        # Verify failed items all have quota_exhausted reason
        quota_failures = [
            item for item in result.failed_items
            if item["reason"] == "quota_exhausted"
        ]
        assert len(quota_failures) == 200, "All failures should be quota exhaustion"

        # CRITICAL: Verify NO null embeddings
        for embedding in result.embeddings:
            assert embedding is not None
            assert len(embedding) == 1536
            assert not all(v == 0.0 for v in embedding), "No zero vectors"

        # Verify OpenAI API called only twice (not 3 times)
        assert call_count == 2, "Should stop after quota exhaustion, not continue"

    @pytest.mark.asyncio
    async def test_batch_embed_partial_success(
        self, mock_db_pool, mock_openai_client, sample_embedding
    ):
        """Test batch_embed with partial success due to quota exhaustion.

        Scenario:
        - Process 150 texts in batches of 100
        - Batch 1: Success (100 embeddings)
        - Batch 2: RateLimitError (quota exhausted after 50 texts)

        Expected:
        - result.success_count = 100
        - result.failure_count = 50
        - EmbeddingBatchResult.success_count + failure_count == total texts
        """
        service = EmbeddingService(
            db_pool=mock_db_pool,
            openai_client=mock_openai_client,
        )

        texts = [f"Text {i}" for i in range(150)]

        # First batch succeeds, second fails
        call_count = 0

        async def mock_create(**kwargs):
            nonlocal call_count
            call_count += 1

            if call_count == 1:
                return MagicMock(
                    data=[MagicMock(embedding=sample_embedding) for _ in range(100)]
                )
            else:
                raise openai.RateLimitError(
                    "Rate limit exceeded",
                    response=MagicMock(status_code=429),
                    body=None
                )

        mock_openai_client.embeddings.create = mock_create

        with patch.object(service, '_get_cached_embedding', return_value=None):
            result = await service.batch_embed(texts)

        # Verify total count matches
        assert result.success_count + result.failure_count == 150
        assert result.success_count == 100
        assert result.failure_count == 50


class TestEmbeddingServiceCacheHitRate:
    """Tests for cache hit rate tracking (Task 7)."""

    @pytest.mark.asyncio
    async def test_cache_hit_rate_tracking(
        self, mock_db_pool, mock_openai_client, sample_embedding
    ):
        """Test that cache hit rate is tracked correctly.

        Scenario:
        - Request 10 embeddings
        - 3 cache hits, 7 cache misses
        - Expected hit rate: 30%
        """
        service = EmbeddingService(
            db_pool=mock_db_pool,
            openai_client=mock_openai_client,
        )

        texts = [f"Text {i}" for i in range(10)]

        # Mock cache: first 3 texts are cached, rest are misses
        async def mock_get_cached(text):
            if text in ["Text 0", "Text 1", "Text 2"]:
                return sample_embedding  # Cache hit
            return None  # Cache miss

        # Mock OpenAI for cache misses
        mock_openai_client.embeddings.create.return_value = MagicMock(
            data=[MagicMock(embedding=sample_embedding)]
        )

        with patch.object(service, '_get_cached_embedding', side_effect=mock_get_cached):
            with patch.object(service, '_cache_embedding', return_value=None):
                # Embed all texts individually
                for text in texts:
                    await service.embed_text(text)

        # Verify cache statistics
        assert service.total_requests == 10
        assert service.cache_hits == 3
        assert service.cache_misses == 7
        assert service.cache_hit_rate == 30.0  # 3/10 = 30%

    @pytest.mark.asyncio
    async def test_cache_hit_rate_logging_every_100_requests(
        self, mock_db_pool, mock_openai_client, sample_embedding, caplog
    ):
        """Test that cache hit rate is logged every 100 requests.

        Scenario:
        - Process 100 requests
        - Verify log message contains cache hit rate

        Expected:
        - Log message at INFO level every 100 requests
        - Message contains "Cache Performance" and hit rate percentage
        """
        import logging
        caplog.set_level(logging.INFO)

        service = EmbeddingService(
            db_pool=mock_db_pool,
            openai_client=mock_openai_client,
        )

        # Mock all cache misses
        mock_openai_client.embeddings.create.return_value = MagicMock(
            data=[MagicMock(embedding=sample_embedding)]
        )

        with patch.object(service, '_get_cached_embedding', return_value=None):
            with patch.object(service, '_cache_embedding', return_value=None):
                # Process exactly 100 requests
                for i in range(100):
                    await service.embed_text(f"Text {i}")

        # Verify log message was emitted
        cache_logs = [
            record for record in caplog.records
            if "Cache Performance" in record.message
        ]
        assert len(cache_logs) >= 1, "Should log cache stats at 100 requests"
        assert "Hit rate: 0.0%" in cache_logs[-1].message


class TestEmbeddingServiceExponentialBackoff:
    """Tests for exponential backoff retry logic (Gotcha #10)."""

    @pytest.mark.asyncio
    async def test_exponential_backoff_retries(
        self, mock_db_pool, mock_openai_client, sample_embedding
    ):
        """Test exponential backoff on RateLimitError.

        Scenario:
        - First 2 attempts: RateLimitError
        - Third attempt: Success

        Expected:
        - 3 total attempts
        - Delays: ~1s, ~2s (exponential backoff)
        - Final result: success
        """
        service = EmbeddingService(
            db_pool=mock_db_pool,
            openai_client=mock_openai_client,
        )

        # Track attempts and timing
        attempt_count = 0
        import time
        start_time = time.time()

        async def mock_create(**kwargs):
            nonlocal attempt_count
            attempt_count += 1

            if attempt_count < 3:
                # First 2 attempts fail
                raise openai.RateLimitError(
                    "Rate limit exceeded",
                    response=MagicMock(status_code=429),
                    body=None
                )
            else:
                # Third attempt succeeds
                return MagicMock(data=[MagicMock(embedding=sample_embedding)])

        mock_openai_client.embeddings.create = mock_create

        with patch.object(service, '_get_cached_embedding', return_value=None):
            with patch.object(service, '_cache_embedding', return_value=None):
                result = await service.embed_text("Test text")

        elapsed = time.time() - start_time

        # Verify retry behavior
        assert attempt_count == 3, "Should make 3 attempts"
        assert result is not None, "Should succeed on third attempt"
        assert len(result) == 1536

        # Verify exponential backoff delays (1s + 2s ≈ 3s total)
        # Allow some variance for jitter and test execution time
        assert elapsed >= 2.0, "Should have exponential backoff delays"
        assert elapsed < 5.0, "Delays should not be excessive"

    @pytest.mark.asyncio
    async def test_max_retries_exceeded(
        self, mock_db_pool, mock_openai_client
    ):
        """Test that embedding fails after max retries exceeded.

        Scenario:
        - All 3 attempts fail with RateLimitError

        Expected:
        - Result is None (embedding failed)
        - 4 total attempts (initial + 3 retries)
        """
        service = EmbeddingService(
            db_pool=mock_db_pool,
            openai_client=mock_openai_client,
        )

        # Mock all attempts fail
        mock_openai_client.embeddings.create.side_effect = openai.RateLimitError(
            "Rate limit exceeded",
            response=MagicMock(status_code=429),
            body=None
        )

        with patch.object(service, '_get_cached_embedding', return_value=None):
            result = await service.embed_text("Test text")

        # Should return None after all retries exhausted
        assert result is None


class TestEmbeddingServiceValidation:
    """Tests for embedding validation and error handling."""

    @pytest.mark.asyncio
    async def test_rejects_zero_vector_embeddings(
        self, mock_db_pool, mock_openai_client
    ):
        """Test that zero vector embeddings are rejected.

        CRITICAL: Zero vectors occur during quota exhaustion and corrupt search.

        Expected:
        - Zero vector detected and rejected
        - Result is None (not stored in Qdrant)
        """
        service = EmbeddingService(
            db_pool=mock_db_pool,
            openai_client=mock_openai_client,
        )

        # Mock OpenAI returning zero vector
        zero_vector = [0.0] * 1536
        mock_openai_client.embeddings.create.return_value = MagicMock(
            data=[MagicMock(embedding=zero_vector)]
        )

        with patch.object(service, '_get_cached_embedding', return_value=None):
            result = await service.embed_text("Test text")

        # Should reject zero vector
        assert result is None

    @pytest.mark.asyncio
    async def test_rejects_wrong_dimension_embeddings(
        self, mock_db_pool, mock_openai_client
    ):
        """Test that embeddings with wrong dimensions are rejected.

        Expected:
        - 768-dimension embedding detected and rejected
        - Result is None
        """
        service = EmbeddingService(
            db_pool=mock_db_pool,
            openai_client=mock_openai_client,
        )

        # Mock OpenAI returning wrong dimension (768 instead of 1536)
        wrong_dim_vector = [0.1] * 768
        mock_openai_client.embeddings.create.return_value = MagicMock(
            data=[MagicMock(embedding=wrong_dim_vector)]
        )

        with patch.object(service, '_get_cached_embedding', return_value=None):
            result = await service.embed_text("Test text")

        # Should reject wrong dimension
        assert result is None

    @pytest.mark.asyncio
    async def test_handles_empty_text_gracefully(
        self, mock_db_pool, mock_openai_client
    ):
        """Test that empty text is handled gracefully.

        Expected:
        - No API call made
        - Result is None
        - Warning logged
        """
        service = EmbeddingService(
            db_pool=mock_db_pool,
            openai_client=mock_openai_client,
        )

        result = await service.embed_text("")

        # Should return None without calling API
        assert result is None
        mock_openai_client.embeddings.create.assert_not_called()


class TestEmbeddingServiceCacheOperations:
    """Tests for cache storage and retrieval."""

    @pytest.mark.asyncio
    async def test_cache_stores_text_preview(
        self, mock_db_pool, mock_openai_client, sample_embedding
    ):
        """Test that text preview is stored in cache (Task 7).

        Expected:
        - text_preview column populated with first 500 chars
        - content_hash used for lookup
        - model_name stored for multi-model support
        """
        service = EmbeddingService(
            db_pool=mock_db_pool,
            openai_client=mock_openai_client,
        )

        # Mock database connection
        mock_conn = MagicMock()
        mock_conn.execute = AsyncMock()

        async def mock_acquire():
            yield mock_conn

        mock_db_pool.acquire = MagicMock(return_value=mock_acquire())

        # Store embedding in cache
        test_text = "x" * 1000  # Long text
        await service._cache_embedding(test_text, sample_embedding)

        # Verify cache INSERT was called
        mock_conn.execute.assert_called_once()
        call_args = mock_conn.execute.call_args[0]

        # Verify SQL includes text_preview column
        sql = call_args[0]
        assert "text_preview" in sql
        assert "content_hash" in sql
        assert "model_name" in sql

        # Verify text preview is truncated to 500 chars
        text_preview = call_args[2]  # Third parameter
        assert len(text_preview) == 500

    @pytest.mark.asyncio
    async def test_cache_updates_access_count_on_hit(
        self, mock_db_pool, mock_openai_client, sample_embedding
    ):
        """Test that access count increments on cache hit (Task 7).

        Expected:
        - access_count incremented
        - last_accessed_at updated
        """
        service = EmbeddingService(
            db_pool=mock_db_pool,
            openai_client=mock_openai_client,
        )

        # Mock cache hit
        mock_conn = MagicMock()
        mock_conn.fetchrow = AsyncMock(return_value={"embedding": sample_embedding})
        mock_conn.execute = AsyncMock()

        async def mock_acquire():
            yield mock_conn

        mock_db_pool.acquire = MagicMock(return_value=mock_acquire())

        # Lookup cached embedding
        result = await service._get_cached_embedding("Test text")

        # Verify embedding returned
        assert result == sample_embedding

        # Verify UPDATE was called to increment access_count
        assert mock_conn.execute.call_count == 1
        update_sql = mock_conn.execute.call_args[0][0]
        assert "UPDATE embedding_cache" in update_sql
        assert "access_count = access_count + 1" in update_sql
        assert "last_accessed_at = NOW()" in update_sql


class TestEmbeddingServiceBatchProcessing:
    """Tests for batch processing with 100-text limit."""

    @pytest.mark.asyncio
    async def test_batch_processes_in_chunks_of_100(
        self, mock_db_pool, mock_openai_client, sample_embedding
    ):
        """Test that large batches are split into 100-text chunks.

        Scenario:
        - 250 texts to embed
        - Should make 3 API calls: 100, 100, 50

        Expected:
        - 3 API calls
        - All embeddings returned
        """
        service = EmbeddingService(
            db_pool=mock_db_pool,
            openai_client=mock_openai_client,
        )

        texts = [f"Text {i}" for i in range(250)]

        # Track API calls
        call_sizes = []

        async def mock_create(**kwargs):
            batch_size = len(kwargs["input"])
            call_sizes.append(batch_size)
            return MagicMock(
                data=[MagicMock(embedding=sample_embedding) for _ in range(batch_size)]
            )

        mock_openai_client.embeddings.create = mock_create

        with patch.object(service, '_get_cached_embedding', return_value=None):
            with patch.object(service, '_cache_embedding', return_value=None):
                result = await service.batch_embed(texts)

        # Verify batch sizes
        assert call_sizes == [100, 100, 50], "Should split into 100-text batches"
        assert result.success_count == 250
        assert result.failure_count == 0

    @pytest.mark.asyncio
    async def test_batch_embed_empty_list(
        self, mock_db_pool, mock_openai_client
    ):
        """Test batch_embed with empty list.

        Expected:
        - No API calls
        - Empty EmbeddingBatchResult
        """
        service = EmbeddingService(
            db_pool=mock_db_pool,
            openai_client=mock_openai_client,
        )

        result = await service.batch_embed([])

        assert result.success_count == 0
        assert result.failure_count == 0
        assert len(result.embeddings) == 0
        assert len(result.failed_items) == 0
        mock_openai_client.embeddings.create.assert_not_called()
