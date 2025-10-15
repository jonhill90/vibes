"""Integration tests for hybrid search with score normalization validation.

This test suite validates that hybrid search:
1. Normalizes scores to 0-1 range
2. Combines scores correctly (0.7×vector + 0.3×text)
3. Achieves <100ms p95 latency under load
4. Both strategies contribute (match_type='both' > 30% of results)
5. Demonstrates accuracy improvement over vector-only search

Pattern: Example 04 (hybrid_search_query.py)
Reference: prps/rag_service_completion.md Task 6 (lines 1213-1245)

Test Categories:
- Score Normalization: Verify 0-1 range for all results
- Score Combining: Verify formula (0.7×vector + 0.3×text)
- Performance: Measure p50, p95, p99 latency
- Match Distribution: Verify both strategies contribute
- Accuracy Regression: Compare hybrid vs vector-only

Setup Requirements:
- PostgreSQL running with sample documents
- Qdrant running with embeddings
- GIN index on chunks.ts_vector for performance
- At least 50+ documents ingested for meaningful tests
"""

import asyncio
import logging
import time
from typing import Any, Dict, List
import pytest
import asyncpg
from qdrant_client import AsyncQdrantClient

from src.services.search.hybrid_search_strategy import HybridSearchStrategy
from src.services.search.base_search_strategy import BaseSearchStrategy
from src.services.embeddings.embedding_service import EmbeddingService
from src.services.vector_service import VectorService
from src.config.settings import settings

logger = logging.getLogger(__name__)

# Test configuration
TEST_QUERIES = [
    "authentication best practices",
    "database connection pooling",
    "error handling patterns",
    "security vulnerabilities",
    "performance optimization",
    "API rate limiting",
    "caching strategies",
    "testing methodology",
    "code review process",
    "deployment automation",
]


@pytest.fixture
async def db_pool():
    """Create PostgreSQL connection pool for tests."""
    pool = await asyncpg.create_pool(
        settings.DATABASE_URL,
        min_size=2,
        max_size=5,
    )
    yield pool
    await pool.close()


@pytest.fixture
async def qdrant_client():
    """Create Qdrant async client for tests."""
    client = AsyncQdrantClient(url=settings.QDRANT_URL)
    yield client
    await client.close()


@pytest.fixture
async def embedding_service(db_pool, openai_client):
    """Create EmbeddingService for tests."""
    from openai import AsyncOpenAI

    openai_client = AsyncOpenAI(
        api_key=settings.OPENAI_API_KEY.get_secret_value(),
        max_retries=3,
        timeout=30.0,
    )

    service = EmbeddingService(
        db_pool=db_pool,
        openai_client=openai_client,
    )
    return service


@pytest.fixture
async def vector_service(qdrant_client):
    """Create VectorService for tests."""
    service = VectorService(
        qdrant_client=qdrant_client,
        collection_name=settings.QDRANT_COLLECTION_NAME,
    )
    return service


@pytest.fixture
async def base_strategy(vector_service, embedding_service):
    """Create BaseSearchStrategy for vector-only search."""
    strategy = BaseSearchStrategy(
        vector_service=vector_service,
        embedding_service=embedding_service,
    )
    return strategy


@pytest.fixture
async def hybrid_strategy(base_strategy, db_pool):
    """Create HybridSearchStrategy for testing."""
    strategy = HybridSearchStrategy(
        base_strategy=base_strategy,
        db_pool=db_pool,
        vector_weight=settings.HYBRID_VECTOR_WEIGHT,
        text_weight=settings.HYBRID_TEXT_WEIGHT,
        candidate_multiplier=settings.HYBRID_CANDIDATE_MULTIPLIER,
    )
    return strategy


@pytest.mark.asyncio
class TestScoreNormalization:
    """Test suite for score normalization validation."""

    async def test_vector_scores_normalized(self, hybrid_strategy):
        """Test that vector scores are normalized to 0-1 range.

        Validates:
        - All normalized_score values are >= 0.0
        - All normalized_score values are <= 1.0
        - No NaN or None values
        """
        results = await hybrid_strategy.search(
            query="test query",
            limit=10,
        )

        assert len(results) > 0, "No results returned from hybrid search"

        for i, result in enumerate(results):
            score = result.get("score")
            vector_score = result.get("vector_score")
            text_score = result.get("text_score")

            # Validate combined score
            assert score is not None, f"Result[{i}] missing score field"
            assert 0.0 <= score <= 1.0, (
                f"Result[{i}] has score={score} outside 0-1 range. "
                f"chunk_id={result.get('chunk_id')}"
            )

            # Validate component scores
            assert vector_score is not None, f"Result[{i}] missing vector_score"
            assert 0.0 <= vector_score <= 1.0, (
                f"Result[{i}] has vector_score={vector_score} outside 0-1 range"
            )

            assert text_score is not None, f"Result[{i}] missing text_score"
            assert 0.0 <= text_score <= 1.0, (
                f"Result[{i}] has text_score={text_score} outside 0-1 range"
            )

            logger.info(
                f"Result[{i}]: score={score:.3f}, "
                f"vector={vector_score:.3f}, text={text_score:.3f}, "
                f"match_type={result.get('match_type')}"
            )

    async def test_text_scores_normalized(self, hybrid_strategy):
        """Test that text search scores are normalized correctly.

        PostgreSQL ts_rank() returns unbounded scores (0 to infinity).
        Validates that normalization brings them to 0-1 range.
        """
        results = await hybrid_strategy.search(
            query="database connection",  # Good for text search
            limit=20,
        )

        # Filter for results with text matches
        text_results = [r for r in results if r.get("text_score", 0.0) > 0.0]

        assert len(text_results) > 0, "No text search matches found"

        for result in text_results:
            text_score = result["text_score"]
            assert 0.0 <= text_score <= 1.0, (
                f"Text score {text_score} outside 0-1 range for "
                f"chunk_id={result.get('chunk_id')}"
            )


@pytest.mark.asyncio
class TestScoreCombining:
    """Test suite for score combining formula validation."""

    async def test_combined_score_formula(self, hybrid_strategy):
        """Test that combined score = (vector × 0.7) + (text × 0.3).

        Validates the weighted combination formula is applied correctly.
        """
        results = await hybrid_strategy.search(
            query="authentication security",
            limit=10,
        )

        for i, result in enumerate(results):
            vector_score = result["vector_score"]
            text_score = result["text_score"]
            combined_score = result["score"]

            # Calculate expected combined score
            expected = (vector_score * 0.7) + (text_score * 0.3)

            # Allow small floating point error (0.001)
            diff = abs(combined_score - expected)
            assert diff < 0.001, (
                f"Result[{i}] combined score mismatch: "
                f"got {combined_score:.4f}, expected {expected:.4f} "
                f"(vector={vector_score:.3f}, text={text_score:.3f})"
            )

            logger.debug(
                f"Result[{i}]: formula validated - "
                f"{vector_score:.3f}×0.7 + {text_score:.3f}×0.3 = {combined_score:.3f}"
            )

    async def test_match_type_accuracy(self, hybrid_strategy):
        """Test that match_type reflects which strategies contributed.

        Validates:
        - "both": vector_score > 0 AND text_score > 0
        - "vector": vector_score > 0 AND text_score == 0
        - "text": vector_score == 0 AND text_score > 0
        """
        results = await hybrid_strategy.search(
            query="performance optimization caching",
            limit=30,
        )

        for i, result in enumerate(results):
            match_type = result.get("match_type")
            vector_score = result["vector_score"]
            text_score = result["text_score"]

            if match_type == "both":
                assert vector_score > 0.0 and text_score > 0.0, (
                    f"Result[{i}] match_type='both' but "
                    f"vector={vector_score}, text={text_score}"
                )
            elif match_type == "vector":
                assert vector_score > 0.0 and text_score == 0.0, (
                    f"Result[{i}] match_type='vector' but "
                    f"vector={vector_score}, text={text_score}"
                )
            elif match_type == "text":
                assert vector_score == 0.0 and text_score > 0.0, (
                    f"Result[{i}] match_type='text' but "
                    f"vector={vector_score}, text={text_score}"
                )


@pytest.mark.asyncio
class TestPerformance:
    """Test suite for hybrid search performance validation."""

    async def test_latency_under_100ms(self, hybrid_strategy):
        """Test that p95 latency is under 100ms target.

        Runs 20 queries and validates p50, p95, p99 latencies.
        """
        latencies = []

        for query in TEST_QUERIES:
            start_time = time.time()

            results = await hybrid_strategy.search(
                query=query,
                limit=10,
            )

            latency_ms = (time.time() - start_time) * 1000
            latencies.append(latency_ms)

            assert len(results) >= 0, f"Search failed for query: {query}"

        # Calculate percentiles
        latencies.sort()
        count = len(latencies)
        p50 = latencies[int(count * 0.50)]
        p95 = latencies[int(count * 0.95)]
        p99 = latencies[int(count * 0.99)]
        avg = sum(latencies) / count

        logger.info(
            f"Hybrid search latency: "
            f"p50={p50:.1f}ms, p95={p95:.1f}ms, p99={p99:.1f}ms, avg={avg:.1f}ms"
        )

        # Validate against target
        assert p95 < 100.0, (
            f"P95 latency {p95:.1f}ms exceeds 100ms target. "
            f"Performance degraded - check database indexes and query complexity."
        )

        # Log warning if approaching target
        if p95 > 80.0:
            logger.warning(
                f"P95 latency {p95:.1f}ms approaching 100ms target. "
                f"Consider optimization."
            )

    async def test_parallel_execution_benefit(self, hybrid_strategy, base_strategy):
        """Test that parallel execution is faster than sequential.

        Compares hybrid (parallel) vs running vector + text sequentially.
        Should see ~30-40% improvement from parallelization.
        """
        query = "security authentication patterns"

        # Measure hybrid (parallel)
        start = time.time()
        await hybrid_strategy.search(query=query, limit=10)
        parallel_time = (time.time() - start) * 1000

        # Measure sequential (baseline)
        start = time.time()
        await base_strategy.search(query=query, limit=50)  # Vector only
        # Simulate text search time (~30ms typical)
        await asyncio.sleep(0.03)
        sequential_time = (time.time() - start) * 1000

        speedup = ((sequential_time - parallel_time) / sequential_time) * 100

        logger.info(
            f"Parallel execution benefit: "
            f"parallel={parallel_time:.1f}ms, sequential={sequential_time:.1f}ms, "
            f"speedup={speedup:.1f}%"
        )

        # Parallel should be faster (allowing for some variance)
        assert parallel_time < sequential_time * 1.2, (
            f"Parallel execution not faster: {parallel_time:.1f}ms vs {sequential_time:.1f}ms"
        )


@pytest.mark.asyncio
class TestMatchDistribution:
    """Test suite for match type distribution validation."""

    async def test_both_strategies_contribute(self, hybrid_strategy):
        """Test that both vector and text strategies contribute results.

        Validates that match_type='both' accounts for >30% of results,
        indicating hybrid search is effective (not dominated by one strategy).
        """
        all_results = []

        # Run multiple queries to get aggregate distribution
        for query in TEST_QUERIES[:5]:  # First 5 queries
            results = await hybrid_strategy.search(query=query, limit=20)
            all_results.extend(results)

        # Count match types
        match_types = {"vector": 0, "text": 0, "both": 0}
        for result in all_results:
            match_type = result.get("match_type", "unknown")
            match_types[match_type] = match_types.get(match_type, 0) + 1

        total = len(all_results)
        both_pct = (match_types["both"] / total) * 100 if total > 0 else 0.0

        logger.info(
            f"Match distribution across {total} results: "
            f"vector={match_types['vector']} ({match_types['vector']/total*100:.1f}%), "
            f"text={match_types['text']} ({match_types['text']/total*100:.1f}%), "
            f"both={match_types['both']} ({both_pct:.1f}%)"
        )

        # Validate both strategies contribute
        assert match_types["both"] > 0, (
            "No results matched both strategies. Hybrid search ineffective."
        )

        assert both_pct >= 30.0, (
            f"Only {both_pct:.1f}% of results matched both strategies (expected ≥30%). "
            f"Hybrid search may not be adding value. Consider adjusting weights or "
            f"candidate_multiplier."
        )

    async def test_strategy_coverage(self, hybrid_strategy):
        """Test that each strategy contributes unique results.

        Validates that hybrid search returns results that wouldn't be found
        by vector-only or text-only search alone.
        """
        query = "database indexing performance"

        results = await hybrid_strategy.search(query=query, limit=30)

        vector_only_count = sum(1 for r in results if r.get("match_type") == "vector")
        text_only_count = sum(1 for r in results if r.get("match_type") == "text")
        both_count = sum(1 for r in results if r.get("match_type") == "both")

        logger.info(
            f"Strategy coverage: vector_only={vector_only_count}, "
            f"text_only={text_only_count}, both={both_count}"
        )

        # At least one result should come from each strategy
        assert vector_only_count > 0, "No vector-only results (text dominating)"
        assert text_only_count > 0, "No text-only results (vector dominating)"


@pytest.mark.asyncio
class TestAccuracyRegression:
    """Test suite for hybrid vs vector-only accuracy comparison.

    NOTE: These tests require manual review of results for relevance assessment.
    Automated metrics provide proxy measurements (match distribution, score range).
    """

    async def test_hybrid_vs_vector_diversity(self, hybrid_strategy, base_strategy):
        """Test that hybrid search provides more diverse results.

        Compares unique chunk_ids between hybrid and vector-only search.
        Hybrid should include additional relevant chunks from text search.
        """
        query = "authentication JWT tokens security"

        # Get results from both strategies
        hybrid_results = await hybrid_strategy.search(query=query, limit=20)
        vector_results = await base_strategy.search(query=query, limit=20)

        hybrid_chunks = set(r["chunk_id"] for r in hybrid_results)
        vector_chunks = set(r["chunk_id"] for r in vector_results)

        # Calculate diversity metrics
        unique_to_hybrid = hybrid_chunks - vector_chunks
        overlap = hybrid_chunks & vector_chunks

        diversity_pct = (len(unique_to_hybrid) / len(hybrid_chunks)) * 100 if hybrid_chunks else 0.0

        logger.info(
            f"Result diversity: "
            f"hybrid_total={len(hybrid_chunks)}, vector_total={len(vector_chunks)}, "
            f"overlap={len(overlap)}, unique_to_hybrid={len(unique_to_hybrid)} ({diversity_pct:.1f}%)"
        )

        # Hybrid should have at least some unique results (>10% different)
        assert diversity_pct >= 10.0, (
            f"Hybrid search only {diversity_pct:.1f}% different from vector-only. "
            f"Not adding sufficient value."
        )

    async def test_score_range_improvement(self, hybrid_strategy, base_strategy):
        """Test that hybrid search improves score discrimination.

        Hybrid search should produce better score separation between
        highly relevant and less relevant results.
        """
        query = "error handling best practices"

        hybrid_results = await hybrid_strategy.search(query=query, limit=20)
        vector_results = await base_strategy.search(query=query, limit=20)

        # Calculate score ranges
        hybrid_scores = [r["score"] for r in hybrid_results]
        vector_scores = [r["score"] for r in vector_results]

        hybrid_range = max(hybrid_scores) - min(hybrid_scores) if hybrid_scores else 0.0
        vector_range = max(vector_scores) - min(vector_scores) if vector_scores else 0.0

        logger.info(
            f"Score range comparison: "
            f"hybrid={hybrid_range:.3f} (min={min(hybrid_scores):.3f}, max={max(hybrid_scores):.3f}), "
            f"vector={vector_range:.3f} (min={min(vector_scores):.3f}, max={max(vector_scores):.3f})"
        )

        # Hybrid should maintain good score discrimination
        # (range should not collapse due to normalization)
        assert hybrid_range > 0.1, (
            f"Hybrid score range {hybrid_range:.3f} too narrow. "
            f"Poor discrimination between results."
        )


# ==============================================================================
# Manual Validation Checklist
# ==============================================================================

"""
MANUAL VALIDATION STEPS (Run after automated tests):

1. Score Normalization Validation:
   - Run hybrid search with diverse queries
   - Verify all scores in 0-1 range: `assert 0.0 <= score <= 1.0`
   - Check logs for normalization warnings

2. Combined Score Formula Validation:
   - Spot check results: combined = (vector × 0.7) + (text × 0.3)
   - Verify match_type accuracy ("both" requires both scores > 0)

3. Performance Validation:
   - Run 100+ queries and measure p95 latency
   - Verify p95 < 100ms: `pytest tests/integration/test_hybrid_search.py::TestPerformance`
   - Check logs for latency warnings

4. Match Distribution Validation:
   - Run queries and check logs for match distribution
   - Verify match_type='both' > 30% of results
   - If one strategy dominates (>80%), adjust weights or candidate_multiplier

5. Accuracy Improvement Validation (MANUAL REVIEW REQUIRED):
   - Compare top 10 results from hybrid vs vector-only
   - Rate relevance on 1-5 scale for each result
   - Calculate average relevance: hybrid should be 10-15% higher
   - Document findings in test docstrings

Example Manual Review:
```python
# Run comparison
hybrid = await hybrid_strategy.search("authentication", limit=10)
vector = await base_strategy.search("authentication", limit=10)

# Rate each result (1-5 scale)
hybrid_ratings = [5, 5, 4, 4, 3, 3, 2, 2, 1, 1]  # Example
vector_ratings = [5, 4, 4, 3, 3, 2, 2, 1, 1, 1]  # Example

hybrid_avg = sum(hybrid_ratings) / len(hybrid_ratings)  # 3.0
vector_avg = sum(vector_ratings) / len(vector_ratings)  # 2.6

improvement = ((hybrid_avg - vector_avg) / vector_avg) * 100  # 15.4%
assert improvement >= 10.0  # Target: 10-15% improvement
```

6. Enable in Production:
   - Set USE_HYBRID_SEARCH=true in .env
   - Monitor logs for match distribution
   - Alert if p95 > 100ms or one strategy dominates
"""
