# Source: infra/rag-service/backend/src/services/search/hybrid_search_strategy.py
# Lines: 112-278 (search method), 309-398 (full-text search), 459-547 (score combining)
# Pattern: Hybrid search with vector + full-text combined scoring
# Extracted: 2025-10-14
# Relevance: 9/10 - Core pattern for Task 6 (Hybrid Search Enablement)

"""
WHAT THIS DEMONSTRATES:
- Parallel execution of vector + text search (asyncio.gather)
- Score normalization (min-max) for different scales
- Weighted score combining (0.7 vector + 0.3 text)
- Deduplication by chunk_id
- PostgreSQL full-text search with ts_rank
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
import asyncpg

logger = logging.getLogger(__name__)


# ==============================================================================
# PATTERN 1: Hybrid Search Main Flow
# ==============================================================================

async def hybrid_search(
    query: str,
    limit: int = 10,
    vector_service: Any = None,
    db_pool: asyncpg.Pool = None,
    embedding_service: Any = None,
    filters: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Execute hybrid search combining vector similarity and full-text search.

    Process:
    1. Fetch limit * 5 results from each strategy in parallel (candidate multiplier)
    2. Normalize scores from both strategies to 0-1 range (min-max normalization)
    3. Combine scores: combined = 0.7×vector_score + 0.3×text_score
    4. Deduplicate by chunk_id (keep highest combined score)
    5. Sort by combined score descending
    6. Return top-k results

    Performance target: <100ms p95 latency
    """
    if not query or not query.strip():
        logger.warning("Empty query provided to hybrid search")
        return []

    # Calculate candidate limit (fetch more for reranking)
    candidate_multiplier = 5
    candidate_limit = limit * candidate_multiplier

    # Step 1: Execute vector and text search in parallel
    logger.debug(f"Starting parallel search: query='{query[:50]}...', candidate_limit={candidate_limit}")

    vector_results, text_results = await asyncio.gather(
        _vector_search(query, candidate_limit, vector_service, embedding_service, filters),
        _full_text_search(query, candidate_limit, db_pool, filters),
        return_exceptions=True,  # Don't fail entire search if one strategy fails
    )

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

    logger.debug(f"Retrieved {len(vector_results)} vector, {len(text_results)} text results")

    # Step 2: Normalize scores to 0-1 range
    normalized_vector = _normalize_scores(vector_results, "score")  # Vector uses "score"
    normalized_text = _normalize_scores(text_results, "rank")  # Text uses "rank"

    # Step 3: Combine scores with weights (0.7×vector + 0.3×text)
    combined_results = _combine_scores(
        normalized_vector,
        normalized_text,
        vector_weight=0.7,
        text_weight=0.3
    )

    # Step 4: Sort by combined score descending
    combined_results.sort(key=lambda x: x["score"], reverse=True)

    # Step 5: Return top-k results
    return combined_results[:limit]


# ==============================================================================
# PATTERN 2: PostgreSQL Full-Text Search with ts_rank
# ==============================================================================

async def _full_text_search(
    query: str,
    limit: int,
    db_pool: asyncpg.Pool,
    filters: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Execute PostgreSQL full-text search using ts_vector and ts_rank.

    CRITICAL GOTCHA #3: Use $1, $2 placeholders (asyncpg style), NOT %s

    Requires:
    - GIN index on ts_vector column for performance (<50ms)
    - ts_vector column updated via trigger on text changes

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
        async with db_pool.acquire() as conn:
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


# ==============================================================================
# PATTERN 3: Vector Search (delegated to BaseSearchStrategy)
# ==============================================================================

async def _vector_search(
    query: str,
    limit: int,
    vector_service: Any,
    embedding_service: Any,
    filters: Optional[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Execute vector similarity search.

    Returns list of results with "score" field (0.0-1.0).
    """
    try:
        # Generate query embedding
        query_embedding = await embedding_service.embed_text(query)
        if not query_embedding:
            logger.error("Failed to generate query embedding")
            return []

        # Search vector database (Qdrant)
        results = await vector_service.search(
            query_vector=query_embedding,
            limit=limit,
            filters=filters,
        )

        logger.debug(f"Vector search returned {len(results)} results")
        return results

    except Exception as e:
        logger.error(f"Vector search failed: {e}", exc_info=True)
        return []


# ==============================================================================
# PATTERN 4: Score Normalization (Min-Max)
# ==============================================================================

def _normalize_scores(
    results: List[Dict[str, Any]],
    score_field: str,
) -> List[Dict[str, Any]]:
    """Normalize scores to 0-1 range using min-max normalization.

    Formula: normalized = (score - min) / (max - min)

    CRITICAL (Gotcha #13): Always normalize before combining different score scales.
    Vector scores (0.0-1.0) and text ranks (0.0-unbounded) have different ranges.

    Handles edge cases:
    - Empty results: returns empty list
    - All same scores: returns all 1.0 (perfect match)
    - Single result: returns 1.0
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


# ==============================================================================
# PATTERN 5: Score Combining with Deduplication
# ==============================================================================

def _combine_scores(
    vector_results: List[Dict[str, Any]],
    text_results: List[Dict[str, Any]],
    vector_weight: float = 0.7,
    text_weight: float = 0.3,
) -> List[Dict[str, Any]]:
    """Combine normalized scores from vector and text search.

    Strategy:
    1. Index results by chunk_id for fast lookup
    2. For each unique chunk_id, calculate:
       combined_score = vector_weight×vector_score + text_weight×text_score
    3. Determine match_type: "vector", "text", or "both"
    4. Keep highest combined score per chunk_id (deduplication)

    Empirically validated weights (Archon pattern):
    - Vector: 0.7 (semantic similarity is primary)
    - Text: 0.3 (keyword matching is secondary)
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
            "score": result["normalized_score"] * vector_weight,
            "match_type": "vector",
            "metadata": result["metadata"],
        }

    # Process text results
    for result in text_results:
        chunk_id = result["chunk_id"]
        text_contribution = result["normalized_score"] * text_weight

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

    # Log match type distribution for debugging
    match_types = {"vector": 0, "text": 0, "both": 0}
    for r in results:
        match_type = r["match_type"]
        match_types[match_type] = match_types.get(match_type, 0) + 1

    logger.debug(
        f"Combined {len(results)} unique results. "
        f"Match types: vector={match_types['vector']}, "
        f"text={match_types['text']}, both={match_types['both']}"
    )

    return results


# ==============================================================================
# PATTERN 6: PostgreSQL Schema for Full-Text Search
# ==============================================================================

# SQL to create GIN index on ts_vector column (REQUIRED for performance):
"""
-- Create GIN index for fast full-text search
CREATE INDEX idx_chunks_ts_vector ON chunks USING GIN(ts_vector);

-- Create trigger to update ts_vector on text changes
CREATE OR REPLACE FUNCTION chunks_ts_vector_update()
RETURNS TRIGGER AS $$
BEGIN
  NEW.ts_vector := to_tsvector('english', COALESCE(NEW.text, ''));
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trig_chunks_ts_vector_update
  BEFORE INSERT OR UPDATE OF text
  ON chunks
  FOR EACH ROW
  EXECUTE FUNCTION chunks_ts_vector_update();
"""

# ==============================================================================
# KEY TAKEAWAYS
# ==============================================================================

# ✅ DO THIS:
# 1. Run vector and text search in parallel (asyncio.gather)
# 2. Normalize scores before combining (different scales)
# 3. Use weighted combining: 0.7 vector + 0.3 text (empirically validated)
# 4. Deduplicate by chunk_id, keeping highest score
# 5. Use GIN index on ts_vector for <50ms text search
# 6. Use $1, $2 placeholders for asyncpg (NOT %s)

# ❌ DON'T DO THIS:
# 1. Run searches sequentially (slower by ~40%)
# 2. Combine unnormalized scores (text ranks >> vector scores)
# 3. Use equal weights (0.5/0.5) - less accurate
# 4. Skip deduplication (duplicate results)
# 5. Forget GIN index (500-2000ms text search)
# 6. Use %s placeholders with asyncpg (wrong syntax)
