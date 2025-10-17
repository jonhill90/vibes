"""CollectionManager: Manage per-domain Qdrant collection lifecycle.

This service creates and deletes Qdrant collections for sources using sanitized
collection names. Each source gets its own isolated set of collections based on
enabled_collections (documents, code, media).

Pattern: Service Layer with AsyncQdrantClient
Architecture: Per-Domain Collections (not shared global collections)
Critical Gotchas Addressed:
- Sanitize collection names (alphanumeric + underscores only)
- Limit name length to 64 chars (leave room for suffix)
- Handle collection deletion gracefully (log but don't fail if missing)
- Create payload index for source_id filtering
"""

import re
import logging
from typing import Dict
from uuid import UUID

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, PayloadSchemaType

from ..config.settings import settings

logger = logging.getLogger(__name__)


class CollectionManager:
    """Manage per-domain Qdrant collection lifecycle.

    This service handles creation and deletion of Qdrant collections for sources.
    Each source creates its own set of collections (e.g., "AI_Knowledge_documents",
    "AI_Knowledge_code") based on the enabled_collections list.

    Attributes:
        client: AsyncQdrantClient for Qdrant operations
    """

    def __init__(self, qdrant_client: AsyncQdrantClient):
        """Initialize CollectionManager with Qdrant client.

        Args:
            qdrant_client: AsyncQdrantClient for collection operations
        """
        self.client = qdrant_client
        logger.info("CollectionManager initialized")

    @staticmethod
    def sanitize_collection_name(source_title: str, collection_type: str) -> str:
        """Convert source title to valid Qdrant collection name.

        Rules:
        - Replace spaces with underscores
        - Remove special chars (keep alphanumeric + underscore)
        - Collapse multiple underscores into one
        - Remove leading/trailing underscores
        - Limit to 64 chars total (leave room for suffix)
        - Append collection type suffix

        Args:
            source_title: Original source title (e.g., "AI Knowledge", "Network & Security!")
            collection_type: Collection type (e.g., "documents", "code", "media")

        Returns:
            str: Sanitized collection name (e.g., "AI_Knowledge_documents")

        Examples:
            >>> CollectionManager.sanitize_collection_name("AI Knowledge", "documents")
            "AI_Knowledge_documents"
            >>> CollectionManager.sanitize_collection_name("Network & Security!", "code")
            "Network_Security_code"
            >>> CollectionManager.sanitize_collection_name("Very Long Source Name That Exceeds Limit Characters", "media")
            "Very_Long_Source_Name_That_Exceeds_Limit_Charact_media"

        Critical Gotcha: Collection names must be unique and valid for Qdrant
        """
        # Step 1: Replace non-alphanumeric chars with underscores (keep underscore)
        # This converts spaces and special chars to underscores
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', source_title)

        # Step 2: Collapse multiple consecutive underscores into single underscore
        # "Test___Source" → "Test_Source"
        sanitized = re.sub(r'_+', '_', sanitized)

        # Step 3: Remove leading and trailing underscores
        # "_Test_Source_" → "Test_Source"
        sanitized = sanitized.strip('_')

        # Step 4: Limit length (64 total - leave room for suffix)
        # Calculate max prefix length to ensure full name fits in 64 chars
        suffix = f"_{collection_type}"
        max_prefix_len = 64 - len(suffix)

        if len(sanitized) > max_prefix_len:
            sanitized = sanitized[:max_prefix_len]

        # Step 5: Append collection type suffix
        collection_name = f"{sanitized}{suffix}"

        logger.debug(
            f"Sanitized collection name: '{source_title}' + '{collection_type}' → '{collection_name}'"
        )

        return collection_name

    async def create_collections_for_source(
        self,
        source_id: UUID,
        source_title: str,
        enabled_collections: list[str],
    ) -> dict[str, str]:
        """Create Qdrant collections for a new source.

        For each enabled collection type (documents, code, media), this method:
        1. Generates a unique collection name from source title
        2. Creates the collection in Qdrant with appropriate vector dimensions
        3. Creates a payload index on source_id for efficient filtering

        Args:
            source_id: UUID of the source (stored in payload for filtering)
            source_title: Human-readable source title (e.g., "AI Knowledge")
            enabled_collections: List of collection types to create (e.g., ["documents", "code"])

        Returns:
            dict[str, str]: Mapping of collection_type → Qdrant collection name
                Example: {"documents": "AI_Knowledge_documents", "code": "AI_Knowledge_code"}

        Raises:
            Exception: If collection creation fails (propagates Qdrant errors)

        Example:
            >>> manager = CollectionManager(qdrant_client)
            >>> collection_names = await manager.create_collections_for_source(
            ...     source_id=UUID("..."),
            ...     source_title="AI Knowledge",
            ...     enabled_collections=["documents", "code"]
            ... )
            >>> print(collection_names)
            {"documents": "AI_Knowledge_documents", "code": "AI_Knowledge_code"}

        Critical Gotchas:
        - Collection dimensions vary by type (1536 for documents, 3072 for code)
        - Payload index on source_id required for efficient domain-based search
        - Collection names must be unique across all sources
        """
        collection_names: dict[str, str] = {}

        logger.info(
            f"Creating collections for source '{source_title}' (id={source_id}): "
            f"{enabled_collections}"
        )

        for collection_type in enabled_collections:
            # Step 1: Generate unique collection name
            collection_name = self.sanitize_collection_name(source_title, collection_type)

            # Step 2: Get dimension for this collection type
            if collection_type not in settings.COLLECTION_DIMENSIONS:
                logger.warning(
                    f"Unknown collection type '{collection_type}', skipping. "
                    f"Valid types: {list(settings.COLLECTION_DIMENSIONS.keys())}"
                )
                continue

            dimension = settings.COLLECTION_DIMENSIONS[collection_type]

            try:
                # Step 3: Create collection in Qdrant with proper vector config
                logger.info(
                    f"Creating collection '{collection_name}' "
                    f"(dimension={dimension}, distance=COSINE)"
                )

                await self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=dimension,
                        distance=Distance.COSINE,
                    ),
                )

                # Step 4: Create payload index for source_id filtering
                # This enables efficient filtering like: filter={"source_id": "uuid"}
                await self.client.create_payload_index(
                    collection_name=collection_name,
                    field_name="source_id",
                    field_schema=PayloadSchemaType.KEYWORD,
                )

                logger.info(
                    f"✅ Created collection '{collection_name}' with source_id index"
                )

                # Store mapping
                collection_names[collection_type] = collection_name

            except Exception as e:
                logger.error(
                    f"❌ Failed to create collection '{collection_name}': {e}"
                )
                raise

        logger.info(
            f"Successfully created {len(collection_names)} collections for source {source_id}"
        )

        return collection_names

    async def delete_collections_for_source(
        self,
        collection_names: dict[str, str],
    ) -> None:
        """Delete all Qdrant collections for a source.

        This method is called when a source is deleted. It removes all associated
        collections from Qdrant. Errors are logged but don't fail the operation
        (graceful degradation).

        Args:
            collection_names: Mapping of collection_type → collection_name
                Example: {"documents": "AI_Knowledge_documents", "code": "AI_Knowledge_code"}

        Returns:
            None

        Example:
            >>> manager = CollectionManager(qdrant_client)
            >>> await manager.delete_collections_for_source({
            ...     "documents": "AI_Knowledge_documents",
            ...     "code": "AI_Knowledge_code"
            ... })

        Critical Gotcha: Handle missing collections gracefully
        - Collection may already be deleted
        - Don't fail if collection doesn't exist
        - Log errors but continue with other collections
        """
        if not collection_names:
            logger.warning("No collections to delete (empty collection_names)")
            return

        logger.info(f"Deleting {len(collection_names)} collections: {list(collection_names.values())}")

        for collection_type, collection_name in collection_names.items():
            try:
                logger.info(f"Deleting collection '{collection_name}' (type={collection_type})")

                await self.client.delete_collection(collection_name=collection_name)

                logger.info(f"✅ Deleted collection '{collection_name}'")

            except Exception as e:
                # Log error but continue with other collections
                # Collection may already be deleted or may not exist
                logger.error(
                    f"⚠️  Failed to delete collection '{collection_name}': {e}"
                )
                # Don't raise - allow other collections to be deleted

        logger.info("Collection deletion complete")
