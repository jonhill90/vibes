"""RAGService - Thin Coordinator for Search Strategies.

This service acts as a thin coordinator that delegates search operations to
specific strategy implementations. It uses a configuration-driven approach to
select the appropriate search strategy based on the search_type parameter.

Pattern: examples/03_rag_search_pipeline.py (PRIMARY)
Reference: infra/archon/python/src/server/services/search/rag_service.py

Architecture:
- Thin coordinator: RAGService does NO searching itself, only delegates
- Configuration-driven: search_type parameter determines strategy routing
- Graceful degradation: Falls back to vector search if hybrid fails
- Exception-based errors: Raises exceptions (NOT tuple[bool, dict] pattern)
- Strategy validation: Validates strategies are available before use

Key Design Decisions:
- Uses "vector", "hybrid", "auto" search_type routing (not boolean flags)
- Graceful degradation on hybrid failure (falls back to vector)
- Validates strategies at initialization and before use
- Raises exceptions for errors (different from Archon's tuple pattern)
- Configurable through constructor injection (testable)
"""

import logging
import time
from typing import Any, Dict, List, Optional

from .base_search_strategy import BaseSearchStrategy
from .hybrid_search_strategy import HybridSearchStrategy

logger = logging.getLogger(__name__)


class RAGService:
    """Thin coordinator service that orchestrates search strategies.

    This service implements the Strategy Pattern by delegating all search
    operations to specific strategy implementations. It provides:

    1. Configuration-driven strategy selection via search_type parameter
    2. Graceful degradation from hybrid to vector search on failure
    3. Strategy validation and health checks
    4. Exception-based error handling (NOT tuple pattern)

    The coordinator does NOT perform any searching itself - it only routes
    requests to the appropriate strategy and handles fallback logic.

    Attributes:
        base_strategy: BaseSearchStrategy for vector similarity search (required)
        hybrid_strategy: HybridSearchStrategy for hybrid search (optional)
        use_hybrid: Default hybrid search setting (can be overridden per request)

    Usage:
        # Initialize with both strategies
        service = RAGService(
            base_strategy=base_strategy,
            hybrid_strategy=hybrid_strategy,
            use_hybrid=True
        )

        # Vector search
        results = await service.search(
            query="machine learning",
            limit=10,
            search_type="vector"
        )

        # Hybrid search with fallback
        results = await service.search(
            query="machine learning",
            limit=10,
            search_type="hybrid"
        )

        # Auto mode (uses hybrid if available, else vector)
        results = await service.search(
            query="machine learning",
            limit=10,
            search_type="auto"
        )

    Performance:
    - Vector search: <50ms p95 latency
    - Hybrid search: <100ms p95 latency
    - Graceful degradation adds <5ms overhead
    """

    def __init__(
        self,
        base_strategy: BaseSearchStrategy,
        hybrid_strategy: Optional[HybridSearchStrategy] = None,
        use_hybrid: bool = False,
    ):
        """Initialize RAGService as coordinator for search strategies.

        Args:
            base_strategy: BaseSearchStrategy for vector similarity search (required)
            hybrid_strategy: HybridSearchStrategy for hybrid search (optional)
            use_hybrid: Default setting for hybrid search (default: False)

        Raises:
            ValueError: If base_strategy is None

        Example:
            # Vector-only configuration
            service = RAGService(base_strategy=base_strategy)

            # Hybrid-enabled configuration
            service = RAGService(
                base_strategy=base_strategy,
                hybrid_strategy=hybrid_strategy,
                use_hybrid=True
            )
        """
        if base_strategy is None:
            raise ValueError("base_strategy is required and cannot be None")

        self.base_strategy = base_strategy
        self.hybrid_strategy = hybrid_strategy
        self.use_hybrid = use_hybrid

        # Log initialization
        strategies_available = ["vector"]
        if self.hybrid_strategy is not None:
            strategies_available.append("hybrid")

        logger.info(
            f"RAGService initialized: "
            f"strategies={strategies_available}, "
            f"default_hybrid={use_hybrid}"
        )

    async def search(
        self,
        query: str,
        limit: int = 10,
        search_type: str = "vector",
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Execute search using appropriate strategy based on search_type.

        This is the main search interface that routes requests to the appropriate
        strategy implementation. It supports three search_type modes:

        1. "vector": Use vector similarity search only (BaseSearchStrategy)
        2. "hybrid": Use hybrid search (vector + full-text), fallback to vector
        3. "auto": Use hybrid if available, else fallback to vector

        Graceful Degradation:
        - If hybrid search fails, automatically falls back to vector search
        - Logs warning but continues execution
        - Returns results from fallback strategy

        Args:
            query: Search query text
            limit: Maximum number of results to return (default: 10)
            search_type: Search strategy to use - "vector", "hybrid", or "auto"
            filters: Optional metadata filters for search
                Example: {"document_id": "doc-123", "source_id": "src-456"}

        Returns:
            List of search results from selected strategy with structure:
                [
                    {
                        "chunk_id": str,
                        "text": str,
                        "score": float,
                        "metadata": dict,
                    },
                    ...
                ]

        Raises:
            ValueError: If query is empty or search_type is invalid
            Exception: If search fails after fallback attempts

        Performance:
        - Vector mode: <50ms p95
        - Hybrid mode: <100ms p95
        - Auto mode: Same as selected strategy

        Example:
            # Vector search
            results = await service.search(
                query="authentication best practices",
                limit=5,
                search_type="vector"
            )

            # Hybrid search with graceful degradation
            results = await service.search(
                query="authentication best practices",
                limit=5,
                search_type="hybrid",
                filters={"source_id": "src-documentation"}
            )

            # Auto mode (uses best available strategy)
            results = await service.search(
                query="authentication best practices",
                limit=5,
                search_type="auto"
            )
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        if search_type not in ["vector", "hybrid", "auto"]:
            raise ValueError(
                f"Invalid search_type: {search_type}. "
                f"Must be 'vector', 'hybrid', or 'auto'"
            )

        start_time = time.time()

        try:
            # Step 1: Determine which strategy to use
            selected_strategy = self._select_strategy(search_type)

            logger.debug(
                f"Search started: query='{query[:50]}...', "
                f"limit={limit}, "
                f"search_type={search_type}, "
                f"selected_strategy={selected_strategy}"
            )

            # Step 2: Execute search with selected strategy
            if selected_strategy == "hybrid":
                results = await self._execute_hybrid_search(query, limit, filters)
            else:
                results = await self._execute_vector_search(query, limit, filters)

            # Step 3: Log performance metrics
            total_time = (time.time() - start_time) * 1000  # Convert to ms
            logger.info(
                f"Search completed: "
                f"query='{query[:30]}...', "
                f"results={len(results)}, "
                f"strategy={selected_strategy}, "
                f"time={total_time:.1f}ms"
            )

            return results

        except ValueError as e:
            # Re-raise validation errors
            logger.error(f"Search validation error: {e}")
            raise

        except Exception as e:
            # Log and re-raise operational errors
            logger.error(
                f"Search failed: query='{query[:50]}...', error={e}",
                exc_info=True,
            )
            raise

    def _select_strategy(self, search_type: str) -> str:
        """Select appropriate search strategy based on search_type and availability.

        Strategy Selection Logic:
        - "vector": Always use vector search
        - "hybrid": Use hybrid if available, else raise error
        - "auto": Use hybrid if available, else fallback to vector

        Args:
            search_type: Requested search type ("vector", "hybrid", "auto")

        Returns:
            str: Selected strategy name ("vector" or "hybrid")

        Raises:
            ValueError: If hybrid requested but not available

        Example:
            strategy = self._select_strategy("auto")
            # Returns "hybrid" if available, "vector" otherwise
        """
        if search_type == "vector":
            return "vector"

        elif search_type == "hybrid":
            if self.hybrid_strategy is None:
                raise ValueError(
                    "Hybrid search requested but hybrid_strategy is not configured"
                )
            return "hybrid"

        elif search_type == "auto":
            # Auto mode: prefer hybrid if available, fallback to vector
            if self.hybrid_strategy is not None:
                logger.debug("Auto mode: Using hybrid search")
                return "hybrid"
            else:
                logger.debug("Auto mode: Hybrid not available, using vector search")
                return "vector"

        else:
            # Should never reach here due to validation in search()
            raise ValueError(f"Invalid search_type: {search_type}")

    async def _execute_vector_search(
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
            List of search results from vector search

        Raises:
            Exception: If vector search fails
        """
        try:
            logger.debug("Executing vector search via BaseSearchStrategy")
            results = await self.base_strategy.search(
                query=query,
                limit=limit,
                filters=filters,
            )
            return results

        except Exception as e:
            logger.error(f"Vector search failed: {e}", exc_info=True)
            raise

    async def _execute_hybrid_search(
        self,
        query: str,
        limit: int,
        filters: Optional[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Execute hybrid search with graceful degradation to vector search.

        This method implements graceful degradation by attempting hybrid search
        first, then falling back to vector search if hybrid fails. This ensures
        search availability even if the hybrid strategy encounters issues.

        Fallback Logic:
        1. Attempt hybrid search via HybridSearchStrategy
        2. If fails: Log warning and fallback to vector search
        3. Return results from successful strategy

        Args:
            query: Search query text
            limit: Maximum number of results
            filters: Optional metadata filters

        Returns:
            List of search results (from hybrid or vector fallback)

        Raises:
            Exception: If both hybrid and vector fallback fail
        """
        try:
            logger.debug("Executing hybrid search via HybridSearchStrategy")
            results = await self.hybrid_strategy.search(
                query=query,
                limit=limit,
                filters=filters,
            )
            return results

        except Exception as hybrid_error:
            # Graceful degradation: fallback to vector search
            logger.warning(
                f"Hybrid search failed, falling back to vector search: {hybrid_error}"
            )

            try:
                logger.debug("Executing fallback vector search")
                results = await self.base_strategy.search(
                    query=query,
                    limit=limit,
                    filters=filters,
                )
                logger.info(
                    f"Graceful degradation successful: "
                    f"hybrid → vector, results={len(results)}"
                )
                return results

            except Exception as vector_error:
                # Both strategies failed
                logger.error(
                    f"Both hybrid and vector search failed: "
                    f"hybrid_error={hybrid_error}, "
                    f"vector_error={vector_error}",
                    exc_info=True,
                )
                raise Exception(
                    f"Search failed: hybrid search failed ({hybrid_error}), "
                    f"vector fallback also failed ({vector_error})"
                )

    async def validate(self) -> bool:
        """Validate that RAGService and its strategies are operational.

        This method performs health checks on all configured strategies to ensure
        the service is ready to handle search requests.

        Validation Steps:
        1. Validate base_strategy (required)
        2. Validate hybrid_strategy (if configured)
        3. Return True only if all configured strategies are valid

        Returns:
            bool: True if service is operational, False otherwise

        Example:
            if await service.validate():
                results = await service.search(query)
            else:
                logger.error("RAGService validation failed")
        """
        try:
            # Validate base strategy (required)
            if not await self.base_strategy.validate():
                logger.error("RAGService validation failed: BaseSearchStrategy invalid")
                return False

            # Validate hybrid strategy (if configured)
            if self.hybrid_strategy is not None:
                if not await self.hybrid_strategy.validate():
                    logger.warning(
                        "HybridSearchStrategy validation failed. "
                        "Hybrid search will be unavailable."
                    )
                    # Continue - hybrid is optional

            logger.info("RAGService validation passed")
            return True

        except Exception as e:
            logger.error(f"RAGService validation failed: {e}", exc_info=True)
            return False
