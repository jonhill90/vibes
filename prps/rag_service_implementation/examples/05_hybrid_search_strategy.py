# Source: infra/archon/python/src/server/services/search/hybrid_search_strategy.py
# Lines: 1-107
# Pattern: Hybrid Search (Vector + Full-Text)
# Extracted: 2025-10-11
# Relevance: 10/10 - Hybrid search is MVP requirement

"""
PATTERN: Hybrid Search Strategy

Combines vector similarity search with PostgreSQL ts_vector full-text search
for improved recall and precision.

Strategy combines:
1. Vector/semantic search for conceptual matches
2. Full-text search using ts_vector for efficient keyword matching
3. Returns union of both result sets for maximum coverage

Key Implementation Details:
- Uses PostgreSQL RPC function that combines both searches
- Returns match_type to indicate source (vector, text, or both)
- Inherits from base strategy for fallback capability
"""

from typing import Any

from supabase import Client

logger = get_logger(__name__)


class HybridSearchStrategy:
    """Strategy class implementing hybrid search combining vector and full-text search"""

    def __init__(self, supabase_client: Client, base_strategy):
        self.supabase_client = supabase_client
        self.base_strategy = base_strategy

    async def search_documents_hybrid(
        self,
        query: str,
        query_embedding: list[float],
        match_count: int,
        filter_metadata: dict | None = None,
    ) -> list[dict[str, Any]]:
        """
        Perform hybrid search combining vector and full-text search.

        PATTERN: PostgreSQL RPC function for hybrid search
        - Single RPC call returns union of vector + text matches
        - match_type field indicates source of each result
        - Logs distribution of match types for debugging

        Args:
            query: Original search query text
            query_embedding: Pre-computed query embedding
            match_count: Number of results to return
            filter_metadata: Optional metadata filter dict

        Returns:
            List of matching documents from both vector and text search
        """
        try:
            # Prepare filter and source parameters
            filter_json = filter_metadata or {}
            source_filter = filter_json.pop("source", None) if "source" in filter_json else None

            # Call the hybrid search PostgreSQL function
            # PATTERN: Single RPC call handles both vector and text search
            response = self.supabase_client.rpc(
                "hybrid_search_archon_crawled_pages",
                {
                    "query_embedding": query_embedding,
                    "query_text": query,
                    "match_count": match_count,
                    "filter": filter_json,
                    "source_filter": source_filter,
                },
            ).execute()

            if not response.data:
                logger.debug("No results from hybrid search")
                return []

            # Format results to match expected structure
            results = []
            for row in response.data:
                result = {
                    "id": row["id"],
                    "url": row["url"],
                    "chunk_number": row["chunk_number"],
                    "content": row["content"],
                    "metadata": row["metadata"],
                    "source_id": row["source_id"],
                    "similarity": row["similarity"],
                    "match_type": row["match_type"],  # "vector", "text", or "both"
                }
                results.append(result)

            # PATTERN: Log match type distribution for debugging
            # Helps understand effectiveness of each search component
            match_types = {}
            for r in results:
                mt = r.get("match_type", "unknown")
                match_types[mt] = match_types.get(mt, 0) + 1

            logger.debug(
                f"Hybrid search returned {len(results)} results. "
                f"Match types: {match_types}"
            )

            return results

        except Exception as e:
            logger.error(f"Hybrid document search failed: {e}")
            return []
