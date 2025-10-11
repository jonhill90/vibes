# Source: infra/archon/python/src/server/services/search/base_search_strategy.py
# Lines: 1-86
# Pattern: Base Vector Search Strategy
# Extracted: 2025-10-11
# Relevance: 9/10 - Foundational search implementation

"""
PATTERN: Base Vector Search Strategy

This demonstrates the foundational vector similarity search that all
other strategies build upon. Key aspects:

1. Clean strategy class with single responsibility
2. Similarity threshold filtering
3. Metadata-based filtering support
4. RPC function pattern for vector search

Note: This uses Supabase RPC functions. For standalone service with Qdrant,
the pattern would be similar but using Qdrant client instead of Supabase.
"""

from typing import Any

from supabase import Client

logger = get_logger(__name__)

# Fixed similarity threshold for vector results
SIMILARITY_THRESHOLD = 0.05


class BaseSearchStrategy:
    """Base strategy implementing fundamental vector similarity search"""

    def __init__(self, supabase_client: Client):
        """Initialize with database client"""
        self.supabase_client = supabase_client

    async def vector_search(
        self,
        query_embedding: list[float],
        match_count: int,
        filter_metadata: dict | None = None,
        table_rpc: str = "match_archon_crawled_pages",
    ) -> list[dict[str, Any]]:
        """
        Perform basic vector similarity search.

        PATTERN: RPC function call with metadata filtering
        - Uses database RPC function for vector search
        - Applies similarity threshold
        - Supports optional metadata filtering

        This is the foundational semantic search that all strategies use.

        Args:
            query_embedding: The embedding vector for the query
            match_count: Number of results to return
            filter_metadata: Optional metadata filters
            table_rpc: The RPC function to call (match_archon_crawled_pages or match_archon_code_examples)

        Returns:
            List of matching documents with similarity scores
        """
        try:
            # Build RPC parameters
            rpc_params = {"query_embedding": query_embedding, "match_count": match_count}

            # Add filter parameters
            if filter_metadata:
                if "source" in filter_metadata:
                    rpc_params["source_filter"] = filter_metadata["source"]
                    rpc_params["filter"] = {}
                else:
                    rpc_params["filter"] = filter_metadata
            else:
                rpc_params["filter"] = {}

            # Execute search
            response = self.supabase_client.rpc(table_rpc, rpc_params).execute()

            # PATTERN: Filter by similarity threshold
            # This ensures only relevant results are returned
            filtered_results = []
            if response.data:
                for result in response.data:
                    similarity = float(result.get("similarity", 0.0))
                    if similarity >= SIMILARITY_THRESHOLD:
                        filtered_results.append(result)

            return filtered_results

        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []
