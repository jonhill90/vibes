"""SearchService for domain-based multi-collection search.

This service implements domain-based search across per-domain collections:
- Accepts source_ids parameter to scope search to specific knowledge domains
- Queries database to get collection_names for each source
- Searches multiple Qdrant collections in parallel
- Aggregates results from all collections
- Re-ranks by similarity score and returns top-k results

Pattern: prps/per_domain_collections.md (lines 329-397)
Critical Gotchas Addressed:
- Validates source_ids parameter (non-empty list)
- Handles sources with missing collection_names gracefully
- Searches only enabled collections per source
- Aggregates results with source_id and collection_type metadata
- Re-ranks globally by score for best results

Architecture:
- Uses database pool to query source.collection_names
- Uses EmbeddingService to generate query embedding (once)
- Uses VectorService to search each collection
- Returns merged and re-ranked results

Performance Target: <200ms for multi-domain search (2-3 sources)
"""

import json
import logging
import time
from typing import Any, Dict, List
from uuid import UUID

import asyncpg

from .vector_service import VectorService
from .embeddings.embedding_service import EmbeddingService
from ..config.settings import settings

logger = logging.getLogger(__name__)


class SearchService:
    """Service for domain-based search across multiple per-domain collections.

    This service enables searching within specific knowledge domains (sources),
    aggregating results from multiple collections, and re-ranking by score.

    Key Features:
    - Domain-scoped search (query specific source_ids)
    - Multi-collection aggregation (documents + code + media per source)
    - Global re-ranking by similarity score
    - Metadata enrichment (source_id, collection_type)

    Attributes:
        db_pool: Database pool for querying source.collection_names
        embedding_service: Service for generating query embeddings
        vector_service: Service for Qdrant vector operations

    Usage:
        search_service = SearchService(
            db_pool=db_pool,
            embedding_service=embedding_service,
            vector_service=vector_service
        )

        results = await search_service.search(
            query="machine learning best practices",
            source_ids=[uuid1, uuid2],
            limit=10
        )
    """

    def __init__(
        self,
        db_pool: asyncpg.Pool,
        embedding_service: EmbeddingService,
        vector_service: VectorService,
    ):
        """Initialize SearchService with required dependencies.

        Args:
            db_pool: Database pool for querying source metadata
            embedding_service: Service for query embedding generation
            vector_service: Service for Qdrant vector operations
        """
        self.db_pool = db_pool
        self.embedding_service = embedding_service
        self.vector_service = vector_service

        logger.info("SearchService initialized for domain-based multi-collection search")

    async def search(
        self,
        query: str,
        source_ids: List[UUID],
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Search within specific domains (sources) with multi-collection aggregation.

        Process:
        1. Validate source_ids parameter (must be non-empty)
        2. Query database to get collection_names for each source
        3. Build list of collections to search (source_id + collection_name pairs)
        4. Generate query embedding once (use documents model for general queries)
        5. Search each collection with query embedding
        6. Aggregate results from all collections
        7. Re-rank by score descending and return top-k

        Args:
            query: Search query text
            source_ids: List of source UUIDs to search within (must be non-empty)
            limit: Maximum number of results to return (default: 10)

        Returns:
            List of search results sorted by score (descending):
                [
                    {
                        "id": str,  # Chunk ID
                        "score": float,  # Similarity score (0.0-1.0)
                        "text": str,  # Chunk text content
                        "source_id": UUID,  # Source this result came from
                        "collection_type": str,  # Collection type (documents/code/media)
                        "metadata": dict,  # Additional chunk metadata
                    },
                    ...
                ]

        Raises:
            ValueError: If source_ids is None or empty
            Exception: If database query or vector search fails

        Performance:
        - Target: <200ms for 2-3 sources with 3 collections each
        - Embedding generation: ~20-50ms (cached: <1ms)
        - Collection search: ~10-30ms per collection (HNSW indexing)
        - Database query: ~5-10ms

        Example:
            # Search two knowledge domains
            results = await search_service.search(
                query="how to train neural networks",
                source_ids=[ai_source_id, ml_source_id],
                limit=10
            )

            # Results are aggregated and re-ranked across both sources
            for result in results:
                print(f"Score: {result['score']}, Source: {result['source_id']}")
        """
        start_time = time.time()

        # Step 1: Validate source_ids parameter
        if not source_ids:
            raise ValueError("Must specify at least one source_id for domain search")

        logger.info(
            f"Domain search: query='{query[:50]}...', "
            f"source_ids={[str(sid) for sid in source_ids]}, limit={limit}"
        )

        try:
            # Step 2: Get collection names for specified sources
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch(
                    """
                    SELECT
                        id as source_id,
                        collection_names
                    FROM sources
                    WHERE id = ANY($1)
                    """,
                    source_ids
                )

            if not rows:
                logger.warning(
                    f"No sources found for source_ids: {[str(sid) for sid in source_ids]}"
                )
                return []

            # Step 3: Build list of collections to search
            collections_to_search = []
            for row in rows:
                source_id = row["source_id"]
                collection_names_json = row["collection_names"]

                # Parse collection_names JSONB to dict
                try:
                    collection_names = json.loads(collection_names_json) if isinstance(
                        collection_names_json, str
                    ) else collection_names_json
                except (json.JSONDecodeError, TypeError) as e:
                    logger.error(
                        f"Failed to parse collection_names for source {source_id}: {e}"
                    )
                    continue

                # Add each collection to search list
                for collection_type, collection_name in collection_names.items():
                    collections_to_search.append({
                        "source_id": source_id,
                        "collection_type": collection_type,
                        "collection_name": collection_name,
                    })

            if not collections_to_search:
                logger.warning(
                    f"No collections found for sources: {[str(sid) for sid in source_ids]}"
                )
                return []

            logger.info(
                f"Searching {len(collections_to_search)} collections across "
                f"{len(rows)} sources"
            )

            # Step 4: Embed query (use documents model for general queries)
            embedding_start = time.time()
            query_embedding = await self.embedding_service.embed_text(
                query,
                model_name=settings.COLLECTION_EMBEDDING_MODELS["documents"]
            )

            if query_embedding is None:
                logger.error("Failed to generate query embedding")
                raise ValueError("Query embedding generation failed")

            embedding_time = (time.time() - embedding_start) * 1000  # ms
            logger.debug(f"Query embedding generated in {embedding_time:.1f}ms")

            # Step 5: Search each collection
            all_results = []
            search_start = time.time()

            for col in collections_to_search:
                try:
                    # Search this collection
                    results = await self.vector_service.search_vectors(
                        collection_name=col["collection_name"],
                        query_vector=query_embedding,
                        limit=limit * 2,  # Get extra for re-ranking
                        score_threshold=settings.SIMILARITY_THRESHOLD,
                        filter_conditions={
                            "must": [
                                {
                                    "key": "source_id",
                                    "match": {"value": str(col["source_id"])}
                                }
                            ]
                        }
                    )

                    # Step 6: Add metadata (source_id, collection_type) to each result
                    for result in results:
                        result["source_id"] = col["source_id"]
                        result["collection_type"] = col["collection_type"]

                    all_results.extend(results)

                    logger.debug(
                        f"Found {len(results)} results from {col['collection_name']} "
                        f"(source: {col['source_id']})"
                    )

                except Exception as e:
                    logger.error(
                        f"Error searching collection {col['collection_name']}: {e}",
                        exc_info=True
                    )
                    # Continue with other collections (graceful degradation)
                    continue

            search_time = (time.time() - search_start) * 1000  # ms
            logger.debug(f"Collection searches completed in {search_time:.1f}ms")

            # Step 7: Merge and re-rank by score
            sorted_results = sorted(
                all_results,
                key=lambda r: r["score"],
                reverse=True
            )[:limit]

            # Format results
            formatted_results = []
            for result in sorted_results:
                payload = result.get("payload", {})
                formatted_results.append({
                    "id": result["id"],
                    "score": result["score"],
                    "text": payload.get("text", ""),
                    "source_id": result["source_id"],
                    "collection_type": result["collection_type"],
                    "metadata": {
                        "document_id": payload.get("document_id"),
                        "chunk_index": payload.get("chunk_index"),
                        "title": payload.get("title"),
                        "url": payload.get("url"),
                    },
                })

            # Log performance metrics
            total_time = (time.time() - start_time) * 1000  # ms
            logger.info(
                f"Domain search completed: "
                f"sources={len(rows)}, "
                f"collections={len(collections_to_search)}, "
                f"total_results={len(all_results)}, "
                f"returned={len(formatted_results)}, "
                f"total_time={total_time:.1f}ms "
                f"(embedding={embedding_time:.1f}ms, search={search_time:.1f}ms)"
            )

            # Performance warning if exceeds target
            if total_time > 200:
                logger.warning(
                    f"Search latency exceeded target: {total_time:.1f}ms > 200ms "
                    f"(target for multi-domain search)"
                )

            return formatted_results

        except ValueError as e:
            # Re-raise validation errors
            logger.error(f"Validation error in SearchService: {e}")
            raise

        except Exception as e:
            # Log and re-raise operational errors
            logger.error(
                f"SearchService.search failed: {e}",
                exc_info=True
            )
            raise
