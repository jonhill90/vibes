"""VectorService for Qdrant vector database operations.

This service provides vector operations (upsert, search, delete) for RAG document chunks.
Unlike database services, VectorService does NOT use tuple[bool, dict] pattern because
it's a thin wrapper around Qdrant client operations - raises exceptions on errors.

Pattern: Follows examples/09_qdrant_vector_service.py
Critical Gotchas Addressed:
- Gotcha #5: Validates embedding dimension (1536 for text-embedding-3-small)
- Gotcha #1: Rejects null/zero embeddings (prevents search corruption)
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

    Attributes:
        EXPECTED_DIMENSION: Required embedding dimension (1536 for text-embedding-3-small)
        DISTANCE_METRIC: Cosine similarity for vector search
    """

    EXPECTED_DIMENSION = 1536  # text-embedding-3-small dimension
    DISTANCE_METRIC = Distance.COSINE

    def __init__(self, qdrant_client: AsyncQdrantClient, collection_name: str):
        """Initialize VectorService with Qdrant client and collection name.

        Args:
            qdrant_client: AsyncQdrantClient for vector operations
            collection_name: Name of the Qdrant collection to use
        """
        self.client = qdrant_client
        self.collection_name = collection_name
        logger.info(f"VectorService initialized for collection '{collection_name}'")

    def validate_embedding(self, embedding: List[float]) -> None:
        """Validate embedding dimensions and values.

        Args:
            embedding: Embedding vector to validate

        Raises:
            ValueError: If embedding is invalid

        Critical Gotchas:
        - Gotcha #5: Validate len(embedding) == 1536 before insert
        - Gotcha #1: Reject null/zero embeddings (prevents search corruption)
        """
        if not embedding:
            raise ValueError("Embedding cannot be None or empty")

        if len(embedding) != self.EXPECTED_DIMENSION:
            raise ValueError(
                f"Invalid embedding dimension: {len(embedding)}, "
                f"expected {self.EXPECTED_DIMENSION}"
            )

        # Check for null/zero embeddings (Gotcha #1: prevents quota exhaustion corruption)
        if all(v == 0 for v in embedding):
            raise ValueError(
                "Embedding cannot be all zeros (possible OpenAI quota exhaustion)"
            )

    async def ensure_collection_exists(self) -> bool:
        """Ensure the collection exists, create if not.

        Returns:
            bool: True if collection exists or was created

        Raises:
            Exception: If collection cannot be created
        """
        try:
            # Check if collection exists
            collections = await self.client.get_collections()
            collection_names = [c.name for c in collections.collections]

            if self.collection_name in collection_names:
                logger.info(f"Collection '{self.collection_name}' already exists")
                return True

            # Create collection with HNSW indexing for fast approximate search
            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.EXPECTED_DIMENSION,
                    distance=self.DISTANCE_METRIC,
                ),
            )

            logger.info(f"Created collection '{self.collection_name}'")
            return True

        except Exception as e:
            logger.error(f"Error ensuring collection exists: {e}")
            raise

    async def upsert_vectors(
        self,
        points: List[Dict[str, Any]],
        batch_size: int = 100,
    ) -> int:
        """Upsert vectors to Qdrant collection with batching for large datasets.

        Args:
            points: List of point dicts with structure:
                {
                    "id": str,  # Unique chunk ID
                    "embedding": List[float],  # 1536-dimensional vector
                    "payload": dict  # Metadata (document_id, chunk_index, text, etc.)
                }
            batch_size: Number of points to upsert per batch (default 100)
                        Smaller batches prevent httpx.WriteTimeout on large documents

        Returns:
            int: Number of points successfully upserted

        Raises:
            ValueError: If embeddings are invalid (wrong dimension or all zeros)

        Pattern: Batch upserts to prevent timeout on large documents (e.g., 2.7MB → 400 chunks)
        Critical Fix: Large documents were failing with httpx.WriteTimeout when upserting
                      all chunks at once. Batching fixes this by breaking into smaller requests.
        """
        if not points:
            logger.warning("No points to upsert")
            return 0

        try:
            # Validate all embeddings first (fail fast before any DB operations)
            for i, point in enumerate(points):
                embedding = point.get("embedding")
                if embedding is None:
                    raise ValueError(f"Point {i} missing 'embedding' field")
                self.validate_embedding(embedding)

            # Convert to PointStruct format for Qdrant
            point_structs = []
            for point in points:
                point_structs.append(
                    PointStruct(
                        id=point["id"],
                        vector=point["embedding"],
                        payload=point.get("payload", {}),
                    )
                )

            # Batch upsert to prevent timeout on large documents
            total_upserted = 0
            for i in range(0, len(point_structs), batch_size):
                batch = point_structs[i:i + batch_size]

                await self.client.upsert(
                    collection_name=self.collection_name,
                    points=batch,
                )

                total_upserted += len(batch)
                logger.info(f"Upserted batch {i // batch_size + 1}/{(len(point_structs) + batch_size - 1) // batch_size}: {len(batch)} vectors")

            logger.info(f"Successfully upserted {total_upserted} vectors to '{self.collection_name}'")
            return total_upserted

        except ValueError as e:
            # Re-raise validation errors with context
            logger.error(f"Validation error during upsert: {e}")
            raise
        except Exception as e:
            logger.error(f"Error upserting vectors: {e}")
            raise

    async def search_vectors(
        self,
        query_vector: List[float],
        limit: int = 10,
        score_threshold: float = 0.05,
        filter_conditions: Dict[str, Any] | None = None,
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors using cosine similarity.

        Args:
            query_vector: Query embedding vector (1536 dimensions)
            limit: Maximum number of results to return
            score_threshold: Minimum similarity score (0.0-1.0, default 0.05)
            filter_conditions: Optional metadata filters (e.g., {"document_id": "doc-123"})

        Returns:
            List of matching documents with structure:
                {
                    "id": str,  # Chunk ID
                    "score": float,  # Similarity score (0.0-1.0)
                    "payload": dict  # Chunk metadata
                }

        Raises:
            ValueError: If query_vector is invalid

        Pattern: Validate query vector dimension (Gotcha #5)
        """
        try:
            # Validate query embedding dimension
            self.validate_embedding(query_vector)

            # Build Qdrant filter if conditions provided
            search_filter = None
            if filter_conditions:
                search_filter = Filter(**filter_conditions)

            # Perform vector similarity search
            results = await self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold,
                query_filter=search_filter,
            )

            # Convert Qdrant results to dict format
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "id": result.id,
                    "score": result.score,
                    "payload": result.payload,
                })

            logger.info(
                f"Vector search found {len(formatted_results)} results "
                f"(threshold={score_threshold})"
            )
            return formatted_results

        except ValueError as e:
            # Re-raise validation errors with context
            logger.error(f"Validation error during search: {e}")
            raise
        except Exception as e:
            logger.error(f"Error searching vectors: {e}")
            raise

    async def delete_vectors(
        self,
        chunk_ids: List[str],
    ) -> int:
        """Delete vectors by chunk IDs.

        Args:
            chunk_ids: List of chunk IDs to delete

        Returns:
            int: Number of points deleted

        Raises:
            Exception: If deletion fails
        """
        if not chunk_ids:
            logger.warning("No chunk IDs provided for deletion")
            return 0

        try:
            await self.client.delete(
                collection_name=self.collection_name,
                points_selector=chunk_ids,
            )

            logger.info(f"Deleted {len(chunk_ids)} vectors from '{self.collection_name}'")
            return len(chunk_ids)

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
                Example: {"document_id": "doc-123"} deletes all chunks for that document

        Raises:
            Exception: If deletion fails

        Pattern: Useful for deleting all chunks for a document
        """
        try:
            search_filter = Filter(**filter_conditions)

            await self.client.delete(
                collection_name=self.collection_name,
                points_selector=search_filter,
            )

            logger.info(
                f"Deleted vectors from '{self.collection_name}' "
                f"matching filter: {filter_conditions}"
            )

        except Exception as e:
            logger.error(f"Error deleting vectors by filter: {e}")
            raise
