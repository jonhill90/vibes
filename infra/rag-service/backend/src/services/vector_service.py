"""VectorService for Qdrant vector database operations.

This service provides vector operations (upsert, search, delete) for RAG document chunks.
Unlike database services, VectorService does NOT use tuple[bool, dict] pattern because
it's a thin wrapper around Qdrant client operations - raises exceptions on errors.

Pattern: Follows examples/09_qdrant_vector_service.py
Critical Gotchas Addressed:
- Gotcha #5: Validates embedding dimension (configurable per collection)
- Gotcha #1: Rejects null/zero embeddings (prevents search corruption)
- Multi-Collection: Collection-agnostic - accepts collection_name as parameter

ARCHITECTURE NOTE:
This service is collection-agnostic as part of the per-domain collection architecture.
All methods accept collection_name as a parameter instead of using hardcoded global collections.
See: prps/per_domain_collections.md
"""

from typing import Any, List, Dict
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter
import logging

from ..config.settings import settings

logger = logging.getLogger(__name__)


class VectorService:
    """Service for Qdrant vector database operations.

    Note: Does NOT use tuple[bool, dict] pattern like database services.
    This is a thin wrapper around Qdrant client - raises exceptions on errors.

    Collection-Agnostic Design:
    All methods accept collection_name as parameter to support per-domain collections.
    No hardcoded collection names - enables dynamic collection management per source.

    Attributes:
        DISTANCE_METRIC: Cosine similarity for vector search
    """

    DISTANCE_METRIC = Distance.COSINE

    def __init__(self, qdrant_client: AsyncQdrantClient):
        """Initialize VectorService with Qdrant client.

        Args:
            qdrant_client: AsyncQdrantClient for vector operations

        Note:
            This service is collection-agnostic. All methods accept collection_name
            as a parameter to support per-domain collection architecture.
        """
        self.client = qdrant_client
        logger.info("VectorService initialized (collection-agnostic mode)")

    @staticmethod
    def get_collection_name(collection_type: str) -> str:
        """Get Qdrant collection name for a given collection type.

        Args:
            collection_type: Collection type (e.g., "documents", "code", "media")

        Returns:
            Full collection name (e.g., "AI_DOCUMENTS", "AI_CODE")

        Example:
            >>> VectorService.get_collection_name("documents")
            "AI_DOCUMENTS"
        """
        return f"{settings.COLLECTION_NAME_PREFIX}{collection_type.upper()}"

    @staticmethod
    def _detect_dimension_from_collection_name(collection_name: str) -> int:
        """Detect expected dimension from collection name.

        Args:
            collection_name: Qdrant collection name (e.g., "AI_DOCUMENTS", "AI_CODE",
                           "AI_Knowledge_documents")

        Returns:
            Expected dimension for this collection type

        Note:
            Handles both legacy global collections (AI_DOCUMENTS) and new per-domain
            collections (Source_Name_documents). Falls back to 1536 (documents) if
            collection type not recognized.
        """
        # Try to extract collection type from name
        # Pattern 1: Legacy global collections (AI_DOCUMENTS, AI_CODE, AI_MEDIA)
        prefix = settings.COLLECTION_NAME_PREFIX
        if collection_name.startswith(prefix):
            collection_type = collection_name[len(prefix):].lower()
            if collection_type in settings.COLLECTION_DIMENSIONS:
                return settings.COLLECTION_DIMENSIONS[collection_type]

        # Pattern 2: Per-domain collections (Source_Name_documents, Source_Name_code)
        # Extract suffix after last underscore
        if "_" in collection_name:
            collection_type = collection_name.split("_")[-1].lower()
            if collection_type in settings.COLLECTION_DIMENSIONS:
                return settings.COLLECTION_DIMENSIONS[collection_type]

        # Fallback to documents dimension for backward compatibility
        logger.warning(
            f"Could not detect dimension for collection '{collection_name}', "
            f"using default: {settings.COLLECTION_DIMENSIONS['documents']}"
        )
        return settings.COLLECTION_DIMENSIONS["documents"]

    def validate_embedding(
        self,
        embedding: List[float],
        collection_name: str | None = None,
        dimension: int | None = None
    ) -> None:
        """Validate embedding dimensions and values.

        Args:
            embedding: Embedding vector to validate
            collection_name: Collection name to auto-detect dimension (if dimension not provided)
            dimension: Expected dimension (overrides auto-detection)

        Raises:
            ValueError: If embedding is invalid or dimension cannot be determined

        Critical Gotchas:
        - Gotcha #5: Validate len(embedding) matches expected dimension before insert
        - Gotcha #1: Reject null/zero embeddings (prevents search corruption)
        """
        if not embedding:
            raise ValueError("Embedding cannot be None or empty")

        # Determine expected dimension
        if dimension is not None:
            expected_dim = dimension
        elif collection_name is not None:
            expected_dim = self._detect_dimension_from_collection_name(collection_name)
        else:
            raise ValueError(
                "Must provide either 'dimension' or 'collection_name' for validation"
            )

        if len(embedding) != expected_dim:
            raise ValueError(
                f"Invalid embedding dimension: {len(embedding)}, "
                f"expected {expected_dim}"
            )

        # Check for null/zero embeddings (Gotcha #1: prevents quota exhaustion corruption)
        if all(v == 0 for v in embedding):
            raise ValueError(
                "Embedding cannot be all zeros (possible OpenAI quota exhaustion)"
            )

    async def ensure_collection_exists(
        self,
        collection_name: str,
        dimension: int | None = None
    ) -> bool:
        """Ensure the collection exists, create if not.

        Args:
            collection_name: Name of the Qdrant collection
            dimension: Vector dimension (auto-detected from collection_name if None)

        Returns:
            bool: True if collection exists or was created

        Raises:
            Exception: If collection cannot be created

        Note:
            Auto-detects dimension from collection name if not provided.
            Supports both legacy (AI_DOCUMENTS) and per-domain (Source_Name_documents) naming.
        """
        try:
            # Auto-detect dimension if not provided
            expected_dimension = dimension if dimension is not None else \
                self._detect_dimension_from_collection_name(collection_name)

            # Check if collection exists
            collections = await self.client.get_collections()
            collection_names = [c.name for c in collections.collections]

            if collection_name in collection_names:
                logger.info(f"Collection '{collection_name}' already exists")
                return True

            # Create collection with HNSW indexing for fast approximate search
            await self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=expected_dimension,
                    distance=self.DISTANCE_METRIC,
                ),
            )

            logger.info(
                f"Created collection '{collection_name}' "
                f"(dimension={expected_dimension})"
            )
            return True

        except Exception as e:
            logger.error(f"Error ensuring collection exists: {e}")
            raise

    async def upsert_vectors(
        self,
        collection_name: str,
        points: List[Dict[str, Any]],
        batch_size: int = 100,
    ) -> int:
        """Upsert vectors to Qdrant collection with batching for large datasets.

        Args:
            collection_name: Name of the Qdrant collection to upsert into
            points: List of point dicts with structure:
                {
                    "id": str,  # Unique chunk ID
                    "embedding": List[float],  # Embedding vector (dimension varies by collection)
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
                self.validate_embedding(embedding, collection_name=collection_name)

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
                    collection_name=collection_name,
                    points=batch,
                )

                total_upserted += len(batch)
                logger.info(f"Upserted batch {i // batch_size + 1}/{(len(point_structs) + batch_size - 1) // batch_size}: {len(batch)} vectors")

            logger.info(f"Successfully upserted {total_upserted} vectors to '{collection_name}'")
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
        collection_name: str,
        query_vector: List[float],
        limit: int = 10,
        score_threshold: float = 0.05,
        filter_conditions: Dict[str, Any] | None = None,
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors using cosine similarity.

        Args:
            collection_name: Name of the Qdrant collection to search
            query_vector: Query embedding vector (dimension varies by collection)
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
            self.validate_embedding(query_vector, collection_name=collection_name)

            # Build Qdrant filter if conditions provided
            search_filter = None
            if filter_conditions:
                search_filter = Filter(**filter_conditions)

            # Perform vector similarity search
            results = await self.client.search(
                collection_name=collection_name,
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
                f"Vector search in '{collection_name}' found {len(formatted_results)} results "
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
        collection_name: str,
        chunk_ids: List[str],
    ) -> int:
        """Delete vectors by chunk IDs.

        Args:
            collection_name: Name of the Qdrant collection to delete from
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
                collection_name=collection_name,
                points_selector=chunk_ids,
            )

            logger.info(f"Deleted {len(chunk_ids)} vectors from '{collection_name}'")
            return len(chunk_ids)

        except Exception as e:
            logger.error(f"Error deleting vectors: {e}")
            raise

    async def delete_vectors_by_filter(
        self,
        collection_name: str,
        filter_conditions: Dict[str, Any],
    ) -> int:
        """Delete vectors matching filter conditions and return count.

        Args:
            collection_name: Name of the Qdrant collection to delete from
            filter_conditions: Qdrant filter dict for deletion
                Example: {"must": [{"key": "document_id", "match": {"value": "doc-123"}}]}

        Returns:
            int: Number of points deleted

        Raises:
            Exception: If deletion fails

        Pattern: Useful for deleting all code blocks for a document
        """
        try:
            # First, count how many points match the filter
            from qdrant_client.models import Filter, FieldCondition, MatchValue

            # Build Qdrant filter from conditions
            search_filter = Filter(**filter_conditions)

            # Scroll to count matching points before deletion
            scroll_result = await self.client.scroll(
                collection_name=collection_name,
                scroll_filter=search_filter,
                limit=10000,  # Should be enough for most documents
                with_payload=False,
                with_vectors=False,
            )

            points_to_delete = scroll_result[0]
            count = len(points_to_delete)

            if count == 0:
                logger.debug(f"No vectors found matching filter in '{collection_name}'")
                return 0

            # Delete the vectors
            await self.client.delete(
                collection_name=collection_name,
                points_selector=search_filter,
            )

            logger.info(
                f"Deleted {count} vectors from '{collection_name}' "
                f"matching filter: {filter_conditions}"
            )
            return count

        except Exception as e:
            logger.error(f"Error deleting vectors by filter: {e}")
            raise

    async def delete_by_filter(
        self,
        collection_name: str,
        filter_conditions: Dict[str, Any],
    ) -> None:
        """Delete vectors matching filter conditions (no count returned).

        Args:
            collection_name: Name of the Qdrant collection to delete from
            filter_conditions: Metadata filter for deletion
                Example: {"document_id": "doc-123"} deletes all chunks for that document

        Raises:
            Exception: If deletion fails

        Pattern: Useful for deleting all chunks for a document
        Note: Use delete_vectors_by_filter() if you need the count of deleted vectors
        """
        try:
            search_filter = Filter(**filter_conditions)

            await self.client.delete(
                collection_name=collection_name,
                points_selector=search_filter,
            )

            logger.info(
                f"Deleted vectors from '{collection_name}' "
                f"matching filter: {filter_conditions}"
            )

        except Exception as e:
            logger.error(f"Error deleting vectors by filter: {e}")
            raise
