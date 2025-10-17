"""Search API routes.

This module provides REST API endpoints for semantic and hybrid search with:
- Vector similarity search
- Hybrid search (vector + full-text)
- Auto mode (uses best available strategy)
- Performance metrics (latency tracking)

Critical Gotchas Addressed:
- Gotcha #2: Inject db_pool and qdrant_client, services manage connections
- Search result validation and error handling

Pattern: Example 05 (FastAPI route pattern)
Reference: RAGService for search delegation
"""

import logging
import time
from typing import Optional, Dict, Any

import asyncpg
from fastapi import APIRouter, Depends, HTTPException
from qdrant_client import AsyncQdrantClient

from src.api.dependencies import get_db_pool, get_qdrant_client
from src.models.requests import SearchRequest
from src.models.responses import SearchResponse, SearchResultItem, ErrorResponse
from src.services.embeddings.embedding_service import EmbeddingService
from src.services.vector_service import VectorService
from src.services.search.base_search_strategy import BaseSearchStrategy
from src.services.search.hybrid_search_strategy import HybridSearchStrategy
from src.services.search.rag_service import RAGService
from src.config.settings import settings
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["search"])


async def get_rag_service(
    db_pool: asyncpg.Pool = Depends(get_db_pool),
    qdrant_client: AsyncQdrantClient = Depends(get_qdrant_client),
) -> RAGService:
    """Dependency to initialize RAGService with all strategies.

    This dependency creates a fresh RAGService instance for each request,
    initializing the appropriate search strategies based on settings.

    Args:
        db_pool: Database pool (injected)
        qdrant_client: Qdrant client (injected)

    Returns:
        Configured RAGService instance

    Raises:
        HTTPException: 503 if service initialization fails
    """
    try:
        # Initialize OpenAI client for embeddings
        openai_client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY.get_secret_value(),
            max_retries=3,
            timeout=30.0,
        )

        # Initialize embedding service
        embedding_service = EmbeddingService(
            db_pool=db_pool,
            openai_client=openai_client,
        )

        # Initialize vector service
        vector_service = VectorService(
            qdrant_client=qdrant_client,
            collection_name=settings.QDRANT_COLLECTION_NAME,
        )

        # Initialize base search strategy (required)
        # Pass db_pool and qdrant_client for multi-collection support (Task 8)
        base_strategy = BaseSearchStrategy(
            embedding_service=embedding_service,
            vector_service=vector_service,
            db_pool=db_pool,
            qdrant_client=qdrant_client,
        )

        # Initialize hybrid search strategy if enabled
        hybrid_strategy = None
        if settings.USE_HYBRID_SEARCH:
            try:
                hybrid_strategy = HybridSearchStrategy(
                    embedding_service=embedding_service,
                    vector_service=vector_service,
                    db_pool=db_pool,
                    vector_weight=settings.HYBRID_VECTOR_WEIGHT,
                    text_weight=settings.HYBRID_TEXT_WEIGHT,
                )
                logger.debug("Hybrid search strategy initialized")
            except Exception as e:
                logger.warning(
                    f"Failed to initialize hybrid search strategy: {e}. "
                    "Only vector search will be available."
                )

        # Initialize RAG service
        rag_service = RAGService(
            base_strategy=base_strategy,
            hybrid_strategy=hybrid_strategy,
            use_hybrid=settings.USE_HYBRID_SEARCH,
        )

        return rag_service

    except Exception as e:
        logger.error(f"Failed to initialize RAG service: {e}", exc_info=True)
        raise HTTPException(
            status_code=503,
            detail={
                "success": False,
                "error": "Search service unavailable",
                "detail": str(e),
                "suggestion": "Check if OpenAI API key is configured and Qdrant is accessible",
            },
        )


@router.post(
    "/search",
    response_model=SearchResponse,
    responses={
        200: {"description": "Search completed successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Server error"},
    },
)
async def search_documents(
    request: SearchRequest,
    rag_service: RAGService = Depends(get_rag_service),
) -> SearchResponse:
    """Semantic search across documents.

    Supports three search modes:
    1. "vector": Vector similarity search only
    2. "hybrid": Combined vector + full-text search (if enabled)
    3. "auto": Use hybrid if available, otherwise vector

    Performance:
    - Vector mode: <50ms p95 latency
    - Hybrid mode: <100ms p95 latency

    Args:
        request: SearchRequest with query and filters
        rag_service: RAG service (injected)

    Returns:
        SearchResponse with ranked results and performance metrics

    Raises:
        HTTPException: 400 for validation errors, 500 for server errors
    """
    start_time = time.time()

    try:
        # Build filters dict from request
        filters: Optional[Dict[str, Any]] = None
        if request.source_id:
            filters = {"source_id": request.source_id}

        # Execute search
        logger.info(
            f"Search request: query='{request.query[:50]}...', "
            f"limit={request.limit}, "
            f"search_type={request.search_type}"
        )

        results = await rag_service.search(
            query=request.query,
            limit=request.limit,
            search_type=request.search_type,
            filters=filters,
        )

        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000

        # Convert results to response model
        result_items = [
            SearchResultItem(
                chunk_id=result.get("chunk_id", ""),
                text=result.get("text", ""),
                score=result.get("score", 0.0),
                match_type=result.get("match_type"),
                metadata=result.get("metadata", {}),
            )
            for result in results
        ]

        logger.info(
            f"Search completed: results={len(result_items)}, "
            f"latency={latency_ms:.1f}ms"
        )

        return SearchResponse(
            results=result_items,
            query=request.query,
            search_type=request.search_type,
            count=len(result_items),
            latency_ms=round(latency_ms, 2),
        )

    except ValueError as e:
        # Validation errors from RAGService
        logger.warning(f"Search validation error: {e}")
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": "Invalid search request",
                "detail": str(e),
            },
        )

    except Exception as e:
        logger.error(f"Search error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "Search failed",
                "detail": str(e),
                "suggestion": "Check server logs for details",
            },
        )
