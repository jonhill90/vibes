"""Qdrant collection initialization for multi-collection architecture.

This module provides startup initialization to ensure all required Qdrant collections
exist (AI_DOCUMENTS, AI_CODE, AI_MEDIA) with appropriate vector dimensions.

Pattern: Startup script called during app lifespan
Critical Gotchas Addressed:
- Collections must be created before first upsert
- Each collection needs appropriate VectorParams with correct dimensions
- Collection names are case-sensitive: "AI_DOCUMENTS" != "ai_documents"
- Handle existing collections gracefully (skip if exists)
"""

from typing import Dict
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams
import logging

from ..config.settings import settings

logger = logging.getLogger(__name__)


async def initialize_collections(
    qdrant_client: AsyncQdrantClient,
) -> Dict[str, bool]:
    """Initialize all required Qdrant collections for multi-collection architecture.

    Creates AI_DOCUMENTS, AI_CODE, and AI_MEDIA collections if they don't exist.
    Each collection is configured with appropriate vector dimensions for its
    embedding model.

    Args:
        qdrant_client: AsyncQdrantClient instance

    Returns:
        Dict[str, bool]: Status for each collection (True=created, False=already existed)
            Example: {"AI_DOCUMENTS": True, "AI_CODE": False, "AI_MEDIA": True}

    Raises:
        Exception: If collection creation fails

    Pattern:
        - Check if collection exists before creating
        - Use dimensions from settings.COLLECTION_DIMENSIONS
        - Use collection prefix from settings.COLLECTION_NAME_PREFIX
        - Skip existing collections gracefully
        - Log all operations for debugging

    Example:
        >>> client = AsyncQdrantClient(url="http://localhost:6333")
        >>> result = await initialize_collections(client)
        >>> print(result)
        {"AI_DOCUMENTS": True, "AI_CODE": True, "AI_MEDIA": True}
    """
    logger.info("🔧 Initializing Qdrant collections for multi-collection architecture...")

    # Track which collections were created vs already existed
    creation_status: Dict[str, bool] = {}

    try:
        # Get list of existing collections
        collections_response = await qdrant_client.get_collections()
        existing_collections = [c.name for c in collections_response.collections]

        logger.info(f"📋 Found {len(existing_collections)} existing collections: {existing_collections}")

        # Initialize each required collection from settings
        for collection_type, dimension in settings.COLLECTION_DIMENSIONS.items():
            # Build full collection name with prefix (e.g., "documents" → "AI_DOCUMENTS")
            full_collection_name = f"{settings.COLLECTION_NAME_PREFIX}{collection_type.upper()}"

            if full_collection_name in existing_collections:
                logger.info(f"✅ Collection '{full_collection_name}' already exists (dimension={dimension})")
                creation_status[full_collection_name] = False
                continue

            # Create collection with appropriate vector dimensions
            logger.info(
                f"🆕 Creating collection '{full_collection_name}' "
                f"(dimension={dimension}, distance=COSINE)"
            )

            await qdrant_client.create_collection(
                collection_name=full_collection_name,
                vectors_config=VectorParams(
                    size=dimension,
                    distance=Distance.COSINE,  # Cosine similarity for all collections
                ),
            )

            logger.info(f"✅ Successfully created collection '{full_collection_name}'")
            creation_status[full_collection_name] = True

        # Summary logging
        created_count = sum(1 for v in creation_status.values() if v)
        existing_count = len(creation_status) - created_count

        logger.info(
            f"✅ Collection initialization complete: "
            f"{created_count} created, {existing_count} already existed"
        )

        return creation_status

    except Exception as e:
        logger.error(f"❌ Failed to initialize Qdrant collections: {e}")
        raise


async def verify_collections(
    qdrant_client: AsyncQdrantClient,
) -> Dict[str, Dict[str, int]]:
    """Verify all collections exist and return their configurations.

    Args:
        qdrant_client: AsyncQdrantClient instance

    Returns:
        Dict[str, Dict[str, int]]: Collection info with dimensions
            Example: {
                "AI_DOCUMENTS": {"dimension": 1536, "vectors_count": 1200},
                "AI_CODE": {"dimension": 3072, "vectors_count": 450},
            }

    Raises:
        Exception: If collection verification fails
    """
    logger.info("🔍 Verifying Qdrant collections...")

    collection_info = {}

    try:
        collections_response = await qdrant_client.get_collections()
        existing_collections = {c.name: c for c in collections_response.collections}

        for collection_type in settings.COLLECTION_DIMENSIONS.keys():
            full_collection_name = f"{settings.COLLECTION_NAME_PREFIX}{collection_type.upper()}"

            if full_collection_name not in existing_collections:
                logger.warning(f"⚠️  Collection '{full_collection_name}' does not exist")
                continue

            # Get detailed collection info
            collection_detail = await qdrant_client.get_collection(full_collection_name)

            collection_info[full_collection_name] = {
                "dimension": collection_detail.config.params.vectors.size,
                "vectors_count": collection_detail.vectors_count or 0,
                "distance": str(collection_detail.config.params.vectors.distance),
            }

            logger.info(
                f"✅ Verified '{full_collection_name}': "
                f"{collection_info[full_collection_name]['vectors_count']} vectors, "
                f"{collection_info[full_collection_name]['dimension']} dimensions"
            )

        return collection_info

    except Exception as e:
        logger.error(f"❌ Failed to verify collections: {e}")
        raise
