# Source: infra/archon/python/src/server/services/search/rag_service.py
# Lines: 31-146
# Pattern: RAG Search Pipeline with Strategy Pattern
# Extracted: 2025-10-11
# Relevance: 10/10 - Exact pattern for RAG service architecture

"""
PATTERN: RAG Service as Strategy Coordinator

This demonstrates the Strategy Pattern for RAG search:
1. Coordinator service delegates to strategy implementations
2. Pipeline: Base → Hybrid (optional) → Reranking (optional)
3. Configuration-driven feature enablement
4. Graceful degradation on errors

Key Architectural Decisions:
- Thin coordinator, fat strategies
- Settings control which strategies are active
- Reranking gets 5x candidates for better selection
- Each strategy is independently testable
"""

import os
from typing import Any

from .base_search_strategy import BaseSearchStrategy
from .hybrid_search_strategy import HybridSearchStrategy
from .reranking_strategy import RerankingStrategy

logger = get_logger(__name__)


class RAGService:
    """
    Coordinator service that orchestrates multiple RAG strategies.

    This service delegates to strategy implementations and combines them
    based on configuration settings.
    """

    def __init__(self, supabase_client=None):
        """Initialize RAG service as a coordinator for search strategies"""
        self.supabase_client = supabase_client or get_supabase_client()

        # Initialize base strategy (always needed)
        self.base_strategy = BaseSearchStrategy(self.supabase_client)

        # Initialize optional strategies
        self.hybrid_strategy = HybridSearchStrategy(self.supabase_client, self.base_strategy)

        # Initialize reranking strategy based on settings
        self.reranking_strategy = None
        use_reranking = self.get_bool_setting("USE_RERANKING", False)
        if use_reranking:
            try:
                self.reranking_strategy = RerankingStrategy()
                logger.info("Reranking strategy loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load reranking strategy: {e}")
                self.reranking_strategy = None

    def get_setting(self, key: str, default: str = "false") -> str:
        """Get a setting from environment or credential service."""
        # Simplified for standalone service - use env vars
        return os.getenv(key, default)

    def get_bool_setting(self, key: str, default: bool = False) -> bool:
        """Get a boolean setting."""
        value = self.get_setting(key, "false" if not default else "true")
        return value.lower() in ("true", "1", "yes", "on")

    async def search_documents(
        self,
        query: str,
        match_count: int = 5,
        filter_metadata: dict | None = None,
        use_hybrid_search: bool = False,
    ) -> list[dict[str, Any]]:
        """
        Document search with hybrid search capability.

        PATTERN: Conditional strategy selection
        - use_hybrid_search=True: Use hybrid strategy
        - use_hybrid_search=False: Use base vector search

        Args:
            query: Search query string
            match_count: Number of results to return
            filter_metadata: Optional metadata filter dict
            use_hybrid_search: Whether to use hybrid search

        Returns:
            List of matching documents
        """
        try:
            # Create embedding for the query
            query_embedding = await create_embedding(query)

            if not query_embedding:
                logger.error("Failed to create embedding for query")
                return []

            if use_hybrid_search:
                # Use hybrid strategy
                results = await self.hybrid_strategy.search_documents_hybrid(
                    query=query,
                    query_embedding=query_embedding,
                    match_count=match_count,
                    filter_metadata=filter_metadata,
                )
            else:
                # Use basic vector search from base strategy
                results = await self.base_strategy.vector_search(
                    query_embedding=query_embedding,
                    match_count=match_count,
                    filter_metadata=filter_metadata,
                )

            return results

        except Exception as e:
            logger.error(f"Document search failed: {e}")
            return []

    async def perform_rag_query(
        self, query: str, source: str = None, match_count: int = 5
    ) -> tuple[bool, dict[str, Any]]:
        """
        Perform a comprehensive RAG query that combines all enabled strategies.

        PATTERN: Multi-stage pipeline with graceful degradation
        1. Start with vector or hybrid search
        2. Apply reranking if enabled (fetch 5x candidates)
        3. Return formatted results

        Args:
            query: The search query
            source: Optional source domain to filter results
            match_count: Maximum number of results to return

        Returns:
            Tuple of (success, result_dict)
        """
        try:
            logger.info(f"RAG query started: {query[:100]}{'...' if len(query) > 100 else ''}")

            # Build filter metadata
            filter_metadata = {"source": source} if source else None

            # Check which strategies are enabled
            use_hybrid_search = self.get_bool_setting("USE_HYBRID_SEARCH", False)
            use_reranking = self.get_bool_setting("USE_RERANKING", False)

            # CRITICAL PATTERN: If reranking enabled, fetch more candidates
            # The reranker selects best from larger pool
            search_match_count = match_count
            if use_reranking and self.reranking_strategy:
                # Fetch 5x the requested amount when reranking is enabled
                search_match_count = match_count * 5
                logger.debug(f"Reranking enabled - fetching {search_match_count} candidates for {match_count} final results")

            # Step 1 & 2: Get results (with hybrid search if enabled)
            results = await self.search_documents(
                query=query,
                match_count=search_match_count,
                filter_metadata=filter_metadata,
                use_hybrid_search=use_hybrid_search,
            )

            # Format results for processing
            formatted_results = []
            for i, result in enumerate(results):
                try:
                    formatted_result = {
                        "id": result.get("id", f"result_{i}"),
                        "content": result.get("content", "")[:1000],  # Limit content
                        "metadata": result.get("metadata", {}),
                        "similarity_score": result.get("similarity", 0.0),
                    }
                    formatted_results.append(formatted_result)
                except Exception as format_error:
                    logger.warning(f"Failed to format result {i}: {format_error}")
                    continue

            # Step 3: Apply reranking if available
            # PATTERN: Graceful degradation - continue if reranking fails
            reranking_applied = False
            if self.reranking_strategy and formatted_results:
                try:
                    # Pass top_k to limit results to the originally requested count
                    formatted_results = await self.reranking_strategy.rerank_results(
                        query, formatted_results, content_key="content", top_k=match_count
                    )
                    reranking_applied = True
                    logger.debug(f"Reranking applied: {search_match_count} candidates -> {len(formatted_results)} final results")
                except Exception as e:
                    logger.warning(f"Reranking failed: {e}")
                    reranking_applied = False
                    # If reranking fails but we fetched extra results, trim to requested count
                    if len(formatted_results) > match_count:
                        formatted_results = formatted_results[:match_count]

            # Build response
            response_data = {
                "results": formatted_results,
                "query": query,
                "source": source,
                "match_count": match_count,
                "total_found": len(formatted_results),
                "execution_path": "rag_service_pipeline",
                "search_mode": "hybrid" if use_hybrid_search else "vector",
                "reranking_applied": reranking_applied,
            }

            logger.info(f"RAG query completed - {len(formatted_results)} results found")
            return True, response_data

        except Exception as e:
            logger.error(f"RAG query failed: {e}")

            return False, {
                "error": str(e),
                "error_type": type(e).__name__,
                "query": query,
                "source": source,
                "execution_path": "rag_service_pipeline",
            }
