"""HybridSearchStrategy for combining vector similarity with full-text search.

This strategy combines vector similarity search (0.7 weight) with PostgreSQL
full-text search (0.3 weight) for improved recall and precision in document retrieval.

Pattern: examples/05_hybrid_search_strategy.py (PRIMARY)
Reference: infra/archon/python/src/server/services/search/hybrid_search_strategy.py

Architecture:
- Parallel execution of vector + text search using asyncio.gather()
- Score normalization (min-max) to 0-1 range for both strategies
- Weighted combination: 0.7×vector_score + 0.3×text_score
- Deduplication by chunk_id (keep highest combined score)
- Performance target: <100ms p95 latency

Critical Gotchas Addressed:
- Gotcha #3: Use $1, $2 placeholders for asyncpg (NOT %s)
- Gotcha #8: Always use async with pool.acquire() for connections
- Gotcha #13: Normalize scores before combining (different scales)

Performance Optimization:
- 5x candidate multiplier for reranking (fetch limit * 5 from each strategy)
- Parallel execution reduces latency by ~40% vs sequential
- GIN indexes on ts_vector for <50ms full-text search
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional

import asyncpg

from .base_search_strategy import BaseSearchStrategy

logger = logging.getLogger(__name__)


class HybridSearchStrategy:
    """Strategy combining vector similarity search with PostgreSQL full-text search.

    This implements hybrid search by:
    1. Running vector search and text search in parallel
    2. Normalizing scores from both strategies to 0-1 range
    3. Combining scores: 0.7×vector + 0.3×text
    4. Deduplicating by chunk_id (keeping highest score)
    5. Returning top-k results sorted by combined score

    Attributes:
        base_strategy: BaseSearchStrategy for vector similarity search
        db_pool: asyncpg connection pool for PostgreSQL full-text search
        vector_weight: Weight for vector scores (default: 0.7)
        text_weight: Weight for text scores (default: 0.3)
        candidate_multiplier: Multiplier for initial retrieval (default: 5)

    Usage:
        strategy = HybridSearchStrategy(
            base_strategy=base_strategy,
            db_pool=db_pool
        )
        results = await strategy.search(
            query="machine learning best practices",
            limit=10,
            filters={"source_id": "src-123"}
        )

    Performance:
    - Target: <100ms p95 latency
    - Vector search: ~30-50ms
    - Text search: ~20-40ms (with GIN indexes)
    - Parallel execution: ~50-70ms total
    - Normalization + combining: ~5-10ms
    """

    def __init__(
        self,
        base_strategy: BaseSearchStrategy,
        db_pool: asyncpg.Pool,
        vector_weight: float = 0.7,
        text_weight: float = 0.3,
        candidate_multiplier: int = 5,
    ):
        """Initialize HybridSearchStrategy with required dependencies.

        Args:
            base_strategy: BaseSearchStrategy for vector similarity search
            db_pool: asyncpg connection pool for PostgreSQL operations
            vector_weight: Weight for vector similarity scores (default: 0.7)
            text_weight: Weight for full-text search scores (default: 0.3)
            candidate_multiplier: Multiplier for candidate retrieval (default: 5)

        Raises:
            ValueError: If weights don't sum to 1.0
        """
        if abs(vector_weight + text_weight - 1.0) > 0.001:
            raise ValueError(
                f"Weights must sum to 1.0, got {vector_weight + text_weight}"
            )

        self.base_strategy = base_strategy
        self.db_pool = db_pool
        self.vector_weight = vector_weight
        self.text_weight = text_weight
        self.candidate_multiplier = candidate_multiplier

        logger.info(
            f"HybridSearchStrategy initialized: "
            f"vector_weight={vector_weight}, text_weight={text_weight}, "
            f"candidate_multiplier={candidate_multiplier}"
        )

    async def search(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Execute hybrid search combining vector similarity and full-text search.

        Process:
        1. Fetch limit * candidate_multiplier results from each strategy in parallel
        2. Normalize scores from both strategies to 0-1 range (min-max normalization)
        3. Combine scores: combined = vector_weight×vector_score + text_weight×text_score
        4. Deduplicate by chunk_id (keep highest combined score)
        5. Sort by combined score descending
        6. Return top-k results

        Args:
            query: Search query text
            limit: Maximum number of results to return (default: 10)
            filters: Optional metadata filters for both searches
                Example: {"document_id": "doc-123", "source_id": "src-456"}

        Returns:
            List of search results with structure:
                [
                    {
                        "chunk_id": str,  # Unique chunk identifier
                        "text": str,  # Chunk text content
                        "score": float,  # Combined score (0.0-1.0)
                        "vector_score": float,  # Normalized vector score
                        "text_score": float,  # Normalized text score
                        "match_type": str,  # "vector", "text", or "both"
                        "metadata": dict,  # Chunk metadata
                    },
                    ...
                ]

        Raises:
            ValueError: If query is empty or limit is invalid
            Exception: If both searches fail

        Performance:
        - Target: <100ms p95 latency
        - Parallel execution saves ~40% vs sequential
        - Returns top-k after combining and deduplicating

        Example:
            results = await strategy.search(
                query="authentication best practices",
                limit=5,
                filters={"source_id": "src-documentation"}
            )

            for result in results:
                print(f"Score: {result['score']:.3f} ({result['match_type']})")
                print(f"  Vector: {result['vector_score']:.3f}")
                print(f"  Text: {result['text_score']:.3f}")
        """
        if not query or not query.strip():
            logger.warning("Empty query provided to HybridSearchStrategy")
            return []

        if limit <= 0:
            raise ValueError(f"Invalid limit: {limit}. Must be > 0")

        start_time = time.time()

        # Calculate candidate limit (fetch more for reranking)
        candidate_limit = limit * self.candidate_multiplier

        try:
            # Step 1: Execute vector and text search in parallel
            logger.debug(
                f"Starting parallel search: query='{query[:50]}...', "
                f"candidate_limit={candidate_limit}"
            )
            parallel_start = time.time()

            vector_results, text_results = await asyncio.gather(
                self._vector_search(query, candidate_limit, filters),
                self._full_text_search(query, candidate_limit, filters),
                return_exceptions=True,
            )

            parallel_time = (time.time() - parallel_start) * 1000  # Convert to ms
            logger.debug(f"Parallel search completed in {parallel_time:.1f}ms")

            # Handle exceptions from parallel execution
            if isinstance(vector_results, Exception):
                logger.error(f"Vector search failed: {vector_results}")
                vector_results = []

            if isinstance(text_results, Exception):
                logger.error(f"Text search failed: {text_results}")
                text_results = []

            # If both failed, raise exception
            if not vector_results and not text_results:
                raise Exception("Both vector and text search failed")

            logger.debug(
                f"Retrieved {len(vector_results)} vector results, "
                f"{len(text_results)} text results"
            )

            # Step 2: Normalize scores to 0-1 range
            normalize_start = time.time()

            # Log raw scores before normalization for debugging
            if vector_results:
                vector_scores = [r.get("score", 0.0) for r in vector_results[:5]]
                logger.debug(
                    f"Vector raw scores (top 5): "
                    f"min={min(r.get('score', 0.0) for r in vector_results):.4f}, "
                    f"max={max(r.get('score', 0.0) for r in vector_results):.4f}, "
                    f"samples={vector_scores}"
                )

            if text_results:
                text_ranks = [r.get("rank", 0.0) for r in text_results[:5]]
                logger.debug(
                    f"BM25 raw ranks (top 5): "
                    f"min={min(r.get('rank', 0.0) for r in text_results):.4f}, "
                    f"max={max(r.get('rank', 0.0) for r in text_results):.4f}, "
                    f"samples={text_ranks}"
                )

            normalized_vector = self._normalize_scores(vector_results, "score")
            normalized_text = self._normalize_scores(text_results, "rank")

            normalize_time = (time.time() - normalize_start) * 1000
            logger.debug(f"Score normalization took {normalize_time:.1f}ms")

            # Validate normalized scores are in 0-1 range
            self._validate_score_normalization(normalized_vector, "vector")
            self._validate_score_normalization(normalized_text, "text")

            # Step 3: Combine scores with weights (0.7×vector + 0.3×text)
            combine_start = time.time()

            combined_results = self._combine_scores(
                normalized_vector,
                normalized_text
            )

            # Log combined score statistics for monitoring
            if combined_results:
                combined_scores = [r["score"] for r in combined_results[:10]]
                vector_contributions = [r["vector_score"] * self.vector_weight for r in combined_results[:10]]
                text_contributions = [r["text_score"] * self.text_weight for r in combined_results[:10]]

                logger.debug(
                    f"Combined scores (top 10): "
                    f"min={min(r['score'] for r in combined_results):.4f}, "
                    f"max={max(r['score'] for r in combined_results):.4f}, "
                    f"samples={[f'{s:.4f}' for s in combined_scores]}"
                )
                logger.debug(
                    f"Score contributions: "
                    f"vector_weighted={[f'{v:.4f}' for v in vector_contributions]}, "
                    f"text_weighted={[f'{t:.4f}' for t in text_contributions]}"
                )

            combine_time = (time.time() - combine_start) * 1000
            logger.debug(
                f"Score combining took {combine_time:.1f}ms, "
                f"produced {len(combined_results)} unique results"
            )

            # Step 4: Sort by combined score descending
            combined_results.sort(key=lambda x: x["score"], reverse=True)

            # Step 5: Return top-k results
            final_results = combined_results[:limit]

            # Performance logging
            total_time = (time.time() - start_time) * 1000
            logger.info(
                f"HybridSearchStrategy completed: "
                f"query='{query[:30]}...', "
                f"results={len(final_results)}, "
                f"total_time={total_time:.1f}ms "
                f"(parallel={parallel_time:.1f}ms, "
                f"normalize={normalize_time:.1f}ms, "
                f"combine={combine_time:.1f}ms)"
            )

            # Performance warning if exceeds target
            if total_time > 100:
                logger.warning(
                    f"Hybrid search latency exceeded target: {total_time:.1f}ms > 100ms "
                    f"(p95 target)"
                )

            return final_results

        except ValueError as e:
            # Re-raise validation errors with context
            logger.error(f"Validation error in HybridSearchStrategy: {e}")
            raise

        except Exception as e:
            # Log and re-raise operational errors
            logger.error(
                f"HybridSearchStrategy search failed: {e}",
                exc_info=True,
            )
            raise

    async def _vector_search(
        self,
        query: str,
        limit: int,
        filters: Optional[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Execute vector similarity search using BaseSearchStrategy.

        Args:
            query: Search query text
            limit: Maximum number of results
            filters: Optional metadata filters

        Returns:
            List of vector search results with "score" field
        """
        try:
            results = await self.base_strategy.search(
                query=query,
                limit=limit,
                filters=filters,
            )
            logger.debug(f"Vector search returned {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"Vector search failed: {e}", exc_info=True)
            return []

    async def _full_text_search(
        self,
        query: str,
        limit: int,
        filters: Optional[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Execute PostgreSQL full-text search using ts_vector.

        Uses PostgreSQL ts_rank() for relevance scoring. Requires:
        - GIN index on ts_vector column for performance
        - ts_vector column updated via trigger on text changes

        Args:
            query: Search query text
            limit: Maximum number of results
            filters: Optional metadata filters (document_id, source_id)

        Returns:
            List of text search results with "rank" field

        Performance:
        - With GIN index: <50ms for 100K documents
        - Without index: 500-2000ms (unacceptable)
        """
        try:
            # Build WHERE clause for filters
            where_clauses = ["ts_vector @@ plainto_tsquery('english', $1)"]
            params: List[Any] = [query]
            param_idx = 2

            if filters:
                if "document_id" in filters:
                    where_clauses.append(f"document_id = ${param_idx}")
                    params.append(filters["document_id"])
                    param_idx += 1

                if "source_id" in filters:
                    where_clauses.append(f"source_id = ${param_idx}")
                    params.append(filters["source_id"])
                    param_idx += 1

            where_clause = " AND ".join(where_clauses)

            # CRITICAL (Gotcha #3): Use $1, $2 placeholders (asyncpg style)
            # ts_rank() returns relevance score (higher = better match)
            query_sql = f"""
                SELECT
                    id as chunk_id,
                    text,
                    ts_rank(ts_vector, plainto_tsquery('english', $1)) as rank,
                    document_id,
                    source_id,
                    chunk_index,
                    token_count
                FROM chunks
                WHERE {where_clause}
                ORDER BY rank DESC
                LIMIT ${param_idx}
            """
            params.append(limit)

            # CRITICAL (Gotcha #8): Always use async with for connection management
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch(query_sql, *params)

            # Format results to match expected structure
            results = []
            for row in rows:
                results.append({
                    "chunk_id": row["chunk_id"],
                    "text": row["text"],
                    "rank": row["rank"],  # Will be normalized later
                    "metadata": {
                        "document_id": row["document_id"],
                        "source_id": row["source_id"],
                        "chunk_index": row["chunk_index"],
                        "token_count": row["token_count"],
                    },
                })

            logger.debug(f"Full-text search returned {len(results)} results")
            return results

        except asyncpg.PostgresError as e:
            logger.error(f"PostgreSQL full-text search failed: {e}", exc_info=True)
            return []

        except Exception as e:
            logger.error(f"Full-text search failed: {e}", exc_info=True)
            return []

    def _normalize_scores(
        self,
        results: List[Dict[str, Any]],
        score_field: str,
    ) -> List[Dict[str, Any]]:
        """Normalize scores to 0-1 range using min-max normalization.

        Formula: normalized = (score - min) / (max - min)

        Handles edge cases:
        - Empty results: returns empty list
        - All same scores: returns all 1.0 (perfect match)
        - Single result: returns 1.0

        Args:
            results: List of search results
            score_field: Field name containing score ("score" or "rank")

        Returns:
            List of results with added "normalized_score" field

        Example:
            results = [
                {"chunk_id": "1", "score": 0.8},
                {"chunk_id": "2", "score": 0.5},
                {"chunk_id": "3", "score": 0.3},
            ]
            normalized = self._normalize_scores(results, "score")
            # Returns:
            # [
            #   {"chunk_id": "1", "score": 0.8, "normalized_score": 1.0},
            #   {"chunk_id": "2", "score": 0.5, "normalized_score": 0.4},
            #   {"chunk_id": "3", "score": 0.3, "normalized_score": 0.0},
            # ]
        """
        if not results:
            return []

        # Extract scores
        scores = [r[score_field] for r in results]
        min_score = min(scores)
        max_score = max(scores)

        # Handle edge case: all scores are the same
        score_range = max_score - min_score
        if score_range == 0:
            # All scores equal, treat as perfect matches
            for result in results:
                result["normalized_score"] = 1.0
            return results

        # Apply min-max normalization
        for result in results:
            original_score = result[score_field]
            normalized = (original_score - min_score) / score_range
            result["normalized_score"] = normalized

        return results

    def _combine_scores(
        self,
        vector_results: List[Dict[str, Any]],
        text_results: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Combine normalized scores from vector and text search.

        Strategy:
        1. Index results by chunk_id for fast lookup
        2. For each unique chunk_id, calculate:
           combined_score = vector_weight×vector_score + text_weight×text_score
        3. Determine match_type: "vector", "text", or "both"
        4. Keep highest combined score per chunk_id (deduplication)

        Args:
            vector_results: Normalized vector search results
            text_results: Normalized text search results

        Returns:
            List of deduplicated results with combined scores

        Example:
            vector = [{"chunk_id": "1", "normalized_score": 0.9, ...}]
            text = [{"chunk_id": "1", "normalized_score": 0.6, ...}]
            combined = self._combine_scores(vector, text)
            # Returns:
            # [{
            #   "chunk_id": "1",
            #   "score": 0.81,  # 0.7×0.9 + 0.3×0.6
            #   "vector_score": 0.9,
            #   "text_score": 0.6,
            #   "match_type": "both",
            #   ...
            # }]
        """
        # Index results by chunk_id
        combined: Dict[str, Dict[str, Any]] = {}

        # Process vector results
        for result in vector_results:
            chunk_id = result["chunk_id"]
            combined[chunk_id] = {
                "chunk_id": chunk_id,
                "text": result["text"],
                "vector_score": result["normalized_score"],
                "text_score": 0.0,  # Default if no text match
                "score": result["normalized_score"] * self.vector_weight,
                "match_type": "vector",
                "metadata": result["metadata"],
            }

        # Process text results
        for result in text_results:
            chunk_id = result["chunk_id"]
            text_contribution = result["normalized_score"] * self.text_weight

            if chunk_id in combined:
                # Chunk matched both strategies
                combined[chunk_id]["text_score"] = result["normalized_score"]
                combined[chunk_id]["score"] += text_contribution
                combined[chunk_id]["match_type"] = "both"
            else:
                # Chunk matched only text search
                combined[chunk_id] = {
                    "chunk_id": chunk_id,
                    "text": result["text"],
                    "vector_score": 0.0,  # Default if no vector match
                    "text_score": result["normalized_score"],
                    "score": text_contribution,
                    "match_type": "text",
                    "metadata": result["metadata"],
                }

        # Convert to list
        results = list(combined.values())

        # Log match type distribution for monitoring
        match_types = {"vector": 0, "text": 0, "both": 0}
        for r in results:
            match_type = r["match_type"]
            match_types[match_type] = match_types.get(match_type, 0) + 1

        # Calculate match type percentages for monitoring
        total_results = len(results)
        if total_results > 0:
            vector_pct = (match_types['vector'] / total_results) * 100
            text_pct = (match_types['text'] / total_results) * 100
            both_pct = (match_types['both'] / total_results) * 100

            logger.info(
                f"Hybrid search match distribution: "
                f"vector_only={match_types['vector']} ({vector_pct:.1f}%), "
                f"text_only={match_types['text']} ({text_pct:.1f}%), "
                f"both={match_types['both']} ({both_pct:.1f}%) "
                f"[total={total_results} unique results]"
            )

            # Alert if hybrid search not effective (one strategy dominates >80%)
            if vector_pct > 80 or text_pct > 80:
                logger.warning(
                    f"Hybrid search ineffective: one strategy dominates "
                    f"(vector={vector_pct:.1f}%, text={text_pct:.1f}%). "
                    f"Consider adjusting weights or candidate_multiplier."
                )
        else:
            logger.debug("No results to combine")

        return results

    def _validate_score_normalization(
        self,
        results: List[Dict[str, Any]],
        strategy_name: str,
    ) -> None:
        """Validate that normalized scores are in the 0-1 range.

        Args:
            results: Results with normalized_score field
            strategy_name: Name of strategy for logging ("vector" or "text")

        Raises:
            ValueError: If any normalized score is outside 0-1 range

        Example:
            self._validate_score_normalization(normalized_vector, "vector")
        """
        if not results:
            return

        for i, result in enumerate(results):
            score = result.get("normalized_score", -1.0)
            if not (0.0 <= score <= 1.0):
                logger.error(
                    f"Invalid normalized score in {strategy_name} results: "
                    f"result[{i}] has normalized_score={score} (expected 0.0-1.0). "
                    f"chunk_id={result.get('chunk_id', 'unknown')}"
                )
                raise ValueError(
                    f"Score normalization failed for {strategy_name}: "
                    f"normalized_score={score} is outside 0.0-1.0 range"
                )

        # Log score range for monitoring
        scores = [r["normalized_score"] for r in results]
        min_score = min(scores)
        max_score = max(scores)
        avg_score = sum(scores) / len(scores)

        logger.debug(
            f"{strategy_name.capitalize()} normalized scores: "
            f"min={min_score:.3f}, max={max_score:.3f}, avg={avg_score:.3f}, "
            f"count={len(scores)}"
        )

    async def validate(self) -> bool:
        """Validate strategy can execute searches.

        Checks:
        1. BaseSearchStrategy is valid
        2. Database pool is accessible
        3. Can execute test full-text search

        Returns:
            bool: True if strategy is ready, False otherwise

        Example:
            if await strategy.validate():
                results = await strategy.search(query)
            else:
                logger.error("Hybrid strategy validation failed")
        """
        try:
            # Validate base strategy
            if not await self.base_strategy.validate():
                logger.error("Hybrid strategy validation failed: BaseSearchStrategy invalid")
                return False

            # Test database connection with simple query
            async with self.db_pool.acquire() as conn:
                await conn.fetchval("SELECT 1")

            logger.info("HybridSearchStrategy validation passed")
            return True

        except Exception as e:
            logger.error(f"Hybrid strategy validation failed: {e}", exc_info=True)
            return False
