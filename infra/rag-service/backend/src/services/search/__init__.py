"""Search strategies for RAG service.

This module provides different search strategies for semantic document retrieval:

- BaseSearchStrategy: Vector similarity search (foundational strategy)
- HybridSearchStrategy: Vector + full-text search combined (0.7×vector + 0.3×text)
- RAGService: Thin coordinator for strategy routing and graceful degradation

Pattern: Strategy pattern for pluggable search implementations
Reference: examples/03_rag_search_pipeline.py

Usage:
    from services.search import BaseSearchStrategy, HybridSearchStrategy, RAGService

    # Vector-only search
    base_strategy = BaseSearchStrategy(vector_service, embedding_service)
    results = await base_strategy.search(query="machine learning", limit=10)

    # Hybrid search (vector + full-text)
    hybrid_strategy = HybridSearchStrategy(
        base_strategy=base_strategy,
        db_pool=db_pool
    )
    results = await hybrid_strategy.search(query="machine learning", limit=10)

    # RAGService coordinator with graceful degradation
    rag_service = RAGService(
        base_strategy=base_strategy,
        hybrid_strategy=hybrid_strategy,
        use_hybrid=True
    )
    results = await rag_service.search(
        query="machine learning",
        limit=10,
        search_type="auto"  # Uses hybrid if available, else vector
    )
"""

from .base_search_strategy import BaseSearchStrategy
from .hybrid_search_strategy import HybridSearchStrategy
from .rag_service import RAGService

__all__ = ["BaseSearchStrategy", "HybridSearchStrategy", "RAGService"]
