# Source: Synthesized from Archon patterns + feature analysis
# Pattern: VectorService for Qdrant Operations
# Extracted: 2025-10-14
# Relevance: 9/10 - Critical for vector operations

"""
PATTERN: VectorService for Qdrant Operations

This demonstrates how to structure a service for Qdrant vector operations.
Unlike database services, VectorService does NOT use tuple[bool, dict] pattern
because it's a thin wrapper around Qdrant client operations.

Key Patterns:
1. Initialize with AsyncQdrantClient (not connection pool)
2. Async methods for upsert, search, delete
3. Return results directly (not tuple[bool, dict])
4. Validate vector dimensions before operations
5. Handle Qdrant-specific errors

CRITICAL GOTCHAS:
- Gotcha #5: Always validate vector dimension (1536 for text-embedding-3-small)
- NEVER store null/zero embeddings (corrupts search)
"""

from typing import Any, List, Dict
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter
import logging

logger = logging.getLogger(__name__)


class VectorService:
    """Service for Qdrant vector database operations.

    Note: Does NOT use tuple[bool, dict] pattern like database services.
    This is a thin wrapper around Qdrant client - raises exceptions on errors.
    """

    COLLECTION_NAME = "documents"
    VECTOR_SIZE = 1536  # text-embedding-3-small dimension
    DISTANCE_METRIC = Distance.COSINE

    def __init__(self, qdrant_client: AsyncQdrantClient):
        """Initialize VectorService with Qdrant client.

        Args:
            qdrant_client: AsyncQdrantClient for vector operations
        """
        self.client = qdrant_client

    async def ensure_collection_exists(self) -> bool:
        """Ensure the collection exists, create if not.

        Returns:
            bool: True if collection exists or was created
        """
        try:
            # Check if collection exists
            collections = await self.client.get_collections()
            collection_names = [c.name for c in collections.collections]

            if self.COLLECTION_NAME in collection_names:
                logger.info(f"Collection '{self.COLLECTION_NAME}' already exists")
                return True

            # Create collection with HNSW indexing
            await self.client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=self.VECTOR_SIZE,
                    distance=self.DISTANCE_METRIC,
                ),
            )

            logger.info(f"Created collection '{self.COLLECTION_NAME}'")
            return True

        except Exception as e:
            logger.error(f"Error ensuring collection exists: {e}")
            raise

    def validate_embedding(self, embedding: List[float]) -> None:
        """Validate embedding dimensions and values.

        Args:
            embedding: Embedding vector to validate

        Raises:
            ValueError: If embedding is invalid

        CRITICAL: Prevents storing corrupted vectors that break search
        """
        if not embedding:
            raise ValueError("Embedding cannot be None or empty")

        if len(embedding) != self.VECTOR_SIZE:
            raise ValueError(
                f"Invalid embedding dimension: {len(embedding)}, expected {self.VECTOR_SIZE}"
            )

        # Check for null/zero embeddings (Gotcha #1 from feature analysis)
        if all(v == 0 for v in embedding):
            raise ValueError("Embedding cannot be all zeros (quota exhaustion?)")

    async def upsert_vectors(
        self,
        points: List[Dict[str, Any]],
    ) -> int:
        """Upsert vectors to Qdrant collection.

        Args:
            points: List of point dicts with id, embedding, payload

        Returns:
            int: Number of points upserted

        Raises:
            ValueError: If embeddings are invalid
        """
        if not points:
            logger.warning("No points to upsert")
            return 0

        try:
            # Validate all embeddings first
            for point in points:
                embedding = point.get("embedding")
                self.validate_embedding(embedding)

            # Convert to PointStruct format
            point_structs = []
            for point in points:
                point_structs.append(
                    PointStruct(
                        id=point["id"],
                        vector=point["embedding"],
                        payload=point.get("payload", {}),
                    )
                )

            # Upsert to Qdrant
            await self.client.upsert(
                collection_name=self.COLLECTION_NAME,
                points=point_structs,
            )

            logger.info(f"Upserted {len(point_structs)} vectors to Qdrant")
            return len(point_structs)

        except Exception as e:
            logger.error(f"Error upserting vectors: {e}")
            raise

    async def search_vectors(
        self,
        query_embedding: List[float],
        limit: int = 10,
        score_threshold: float = 0.05,
        filter_conditions: Dict[str, Any] | None = None,
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors using cosine similarity.

        Args:
            query_embedding: Query vector (1536 dimensions)
            limit: Maximum number of results
            score_threshold: Minimum similarity score (0.0-1.0)
            filter_conditions: Optional metadata filters

        Returns:
            List of matching documents with scores

        PATTERN: Filter by similarity threshold (0.05 from Archon)
        """
        try:
            # Validate query embedding
            self.validate_embedding(query_embedding)

            # Build filter if provided
            search_filter = None
            if filter_conditions:
                # Convert dict to Qdrant Filter object
                search_filter = Filter(**filter_conditions)

            # Perform search
            results = await self.client.search(
                collection_name=self.COLLECTION_NAME,
                query_vector=query_embedding,
                limit=limit,
                score_threshold=score_threshold,
                query_filter=search_filter,
            )

            # Convert to dict format
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "id": result.id,
                    "score": result.score,
                    "payload": result.payload,
                })

            logger.info(f"Vector search found {len(formatted_results)} results")
            return formatted_results

        except Exception as e:
            logger.error(f"Error searching vectors: {e}")
            raise

    async def delete_vectors(
        self,
        point_ids: List[str],
    ) -> int:
        """Delete vectors by IDs.

        Args:
            point_ids: List of point IDs to delete

        Returns:
            int: Number of points deleted
        """
        if not point_ids:
            logger.warning("No point IDs provided for deletion")
            return 0

        try:
            await self.client.delete(
                collection_name=self.COLLECTION_NAME,
                points_selector=point_ids,
            )

            logger.info(f"Deleted {len(point_ids)} vectors from Qdrant")
            return len(point_ids)

        except Exception as e:
            logger.error(f"Error deleting vectors: {e}")
            raise

    async def delete_by_filter(
        self,
        filter_conditions: Dict[str, Any],
    ) -> None:
        """Delete vectors matching filter conditions.

        Args:
            filter_conditions: Metadata filter for deletion

        Example:
            await vector_service.delete_by_filter({"document_id": "doc-123"})
        """
        try:
            search_filter = Filter(**filter_conditions)

            await self.client.delete(
                collection_name=self.COLLECTION_NAME,
                points_selector=search_filter,
            )

            logger.info(f"Deleted vectors matching filter: {filter_conditions}")

        except Exception as e:
            logger.error(f"Error deleting vectors by filter: {e}")
            raise
