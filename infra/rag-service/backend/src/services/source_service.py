"""
SourceService: CRUD operations for RAG sources

This service handles all database operations for source management
(upload, crawl, api) with comprehensive validation and error handling.

Pattern: Service Layer with asyncpg Connection Pooling
Returns: All methods return tuple[bool, dict] for consistent error handling

Per-Domain Collection Integration (Task 3 - per_domain_collections):
- Creates unique Qdrant collections for each source
- Automatically deletes collections when source is deleted
- Stores collection_names mapping in database
"""

from typing import Any
import asyncpg
import logging
import json
from uuid import UUID

from qdrant_client import AsyncQdrantClient

from .collection_manager import CollectionManager

logger = logging.getLogger(__name__)


class SourceService:
    """Service class for source CRUD operations.

    Handles ingestion sources (upload, crawl, api) with status tracking
    and metadata management.
    """

    VALID_SOURCE_TYPES = ["upload", "crawl", "api"]
    VALID_STATUSES = ["active", "processing", "failed", "archived"]

    def __init__(self, db_pool: asyncpg.Pool, qdrant_client: AsyncQdrantClient | None = None):
        """Initialize SourceService with database connection pool and Qdrant client.

        Args:
            db_pool: asyncpg connection pool for database operations
            qdrant_client: Optional AsyncQdrantClient for collection management
                          If None, collection management will be skipped

        Critical Gotcha #2: Store pool NOT connection
        """
        self.db_pool = db_pool
        self.qdrant_client = qdrant_client
        self.collection_manager = CollectionManager(qdrant_client) if qdrant_client else None

    def validate_source_type(self, source_type: str) -> tuple[bool, str]:
        """Validate source_type against allowed enum values.

        Args:
            source_type: Source type string to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if source_type not in self.VALID_SOURCE_TYPES:
            return (
                False,
                f"Invalid source_type '{source_type}'. Must be one of: {', '.join(self.VALID_SOURCE_TYPES)}",
            )
        return True, ""

    def validate_status(self, status: str) -> tuple[bool, str]:
        """Validate status against allowed enum values.

        Args:
            status: Status string to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if status not in self.VALID_STATUSES:
            return (
                False,
                f"Invalid status '{status}'. Must be one of: {', '.join(self.VALID_STATUSES)}",
            )
        return True, ""

    async def create_source(self, source_data: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
        """Create a new source in the database and Qdrant collections.

        Args:
            source_data: Dictionary with keys:
                - source_type (required): 'upload', 'crawl', or 'api'
                - url (optional): Source URL
                - status (optional): Defaults to 'active'
                - metadata (optional): JSONB metadata (must contain 'title' for collection naming)
                - error_message (optional): Error details
                - enabled_collections (optional): List of collection types, defaults to ["documents"]

        Returns:
            Tuple of (success, result_dict with source or error)

        Critical Gotcha #3: Use $1, $2 placeholders (asyncpg), NOT %s
        Critical Gotcha #8: Always use async with pool.acquire()

        Per-Domain Collections (Task 3):
        - Creates Qdrant collections for each enabled_collection type
        - Stores collection_names mapping in database
        - Rolls back database insert if collection creation fails
        """
        try:
            # Validate required fields
            if "source_type" not in source_data:
                return False, {"error": "source_type is required"}

            source_type = source_data["source_type"]
            is_valid, error_msg = self.validate_source_type(source_type)
            if not is_valid:
                return False, {"error": error_msg}

            # Validate status if provided
            # Default to "active" - sources are ready immediately (no "pending" confusion)
            status = source_data.get("status", "active")
            is_valid, error_msg = self.validate_status(status)
            if not is_valid:
                return False, {"error": error_msg}

            # Extract optional fields
            url = source_data.get("url")
            metadata = source_data.get("metadata", {})
            error_message = source_data.get("error_message")
            enabled_collections = source_data.get("enabled_collections", ["documents"])

            # Extract source title from metadata (required for collection naming)
            source_title = metadata.get("title", "Untitled")

            # Convert metadata dict to JSON string for JSONB column
            metadata_json = json.dumps(metadata) if isinstance(metadata, dict) else metadata

            # Insert source using asyncpg $1, $2 placeholders
            query = """
                INSERT INTO sources (source_type, enabled_collections, url, status, metadata, error_message, collection_names)
                VALUES ($1, $2, $3, $4, $5::jsonb, $6, $7::jsonb)
                RETURNING id, source_type, enabled_collections, url, status, metadata, error_message,
                          collection_names, created_at, updated_at
            """

            # Critical Gotcha #8: Always use async with for connection management
            async with self.db_pool.acquire() as conn:
                # Step 1: Insert source with empty collection_names (will be updated)
                row = await conn.fetchrow(
                    query, source_type, enabled_collections, url, status, metadata_json, error_message, json.dumps({})
                )

            source = dict(row)
            source_id = source["id"]

            # Step 2: Create Qdrant collections (if CollectionManager available)
            collection_names = {}
            if self.collection_manager and enabled_collections:
                try:
                    logger.info(
                        f"Creating Qdrant collections for source '{source_title}' "
                        f"(id={source_id}): {enabled_collections}"
                    )

                    collection_names = await self.collection_manager.create_collections_for_source(
                        source_id=source_id,
                        source_title=source_title,
                        enabled_collections=enabled_collections
                    )

                    logger.info(
                        f"Created {len(collection_names)} collections for source {source_id}: "
                        f"{list(collection_names.values())}"
                    )

                except Exception as e:
                    # CRITICAL: Rollback database insert if Qdrant collection creation fails
                    logger.error(
                        f"Failed to create Qdrant collections for source {source_id}: {e}. "
                        f"Rolling back source creation."
                    )

                    # Delete the source from database
                    async with self.db_pool.acquire() as conn:
                        await conn.execute("DELETE FROM sources WHERE id = $1", source_id)

                    return False, {
                        "error": f"Failed to create Qdrant collections: {str(e)}",
                        "detail": "Source creation rolled back"
                    }

            # Step 3: Update source with collection_names mapping
            if collection_names:
                collection_names_json = json.dumps(collection_names)

                async with self.db_pool.acquire() as conn:
                    updated_row = await conn.fetchrow(
                        """
                        UPDATE sources
                        SET collection_names = $1::jsonb
                        WHERE id = $2
                        RETURNING id, source_type, enabled_collections, url, status, metadata, error_message,
                                  collection_names, created_at, updated_at
                        """,
                        collection_names_json,
                        source_id
                    )
                    source = dict(updated_row)

            logger.info(
                f"Created source: {source_id} with collections: {collection_names or 'none'}"
            )

            return True, {"source": source}

        except asyncpg.PostgresError as e:
            logger.error(f"Database error creating source: {e}")
            return False, {"error": f"Database error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error creating source: {e}")
            return False, {"error": f"Error creating source: {str(e)}"}

    async def get_source(self, source_id: UUID) -> tuple[bool, dict[str, Any]]:
        """Get a single source by ID.

        Args:
            source_id: UUID of the source to retrieve

        Returns:
            Tuple of (success, result_dict with source or error)
            Source dict includes collection_names field (Task 3 - per_domain_collections)

        Critical Gotcha #3: Use $1, $2 placeholders
        Critical Gotcha #8: Always use async with
        """
        try:
            query = """
                SELECT id, source_type, enabled_collections, url, status, metadata, error_message,
                       collection_names, created_at, updated_at
                FROM sources
                WHERE id = $1
            """

            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow(query, source_id)

            if not row:
                return False, {"error": f"Source not found: {source_id}"}

            source = dict(row)
            return True, {"source": source}

        except asyncpg.PostgresError as e:
            logger.error(f"Database error getting source: {e}")
            return False, {"error": f"Database error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error getting source: {e}")
            return False, {"error": f"Error getting source: {str(e)}"}

    async def list_sources(
        self,
        source_type: str | None = None,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
        exclude_large_fields: bool = False,
    ) -> tuple[bool, dict[str, Any]]:
        """List sources with optional filters and pagination.

        PATTERN: Conditional field selection for MCP performance optimization
        - exclude_large_fields=True: Truncate metadata and error_message
        - exclude_large_fields=False: Return full fields

        Args:
            source_type: Optional filter by source_type ('upload', 'crawl', 'api')
            status: Optional filter by status ('active', 'processing', 'failed', 'archived')
            limit: Maximum number of sources to return (default 50)
            offset: Number of sources to skip (default 0)
            exclude_large_fields: If True, truncate large text fields for MCP optimization

        Returns:
            Tuple of (success, result_dict with sources and total_count)

        Critical Gotcha #3: Use $1, $2 placeholders
        Critical Gotcha #8: Always use async with
        """
        try:
            # Validate source_type if provided
            if source_type is not None:
                is_valid, error_msg = self.validate_source_type(source_type)
                if not is_valid:
                    return False, {"error": error_msg}

            # Validate status if provided
            if status is not None:
                is_valid, error_msg = self.validate_status(status)
                if not is_valid:
                    return False, {"error": error_msg}

            # Build conditional field selection for MCP optimization
            if exclude_large_fields:
                # Truncate metadata and error_message to 1000 chars
                select_fields = """
                    id, source_type, enabled_collections, url, status,
                    CASE
                        WHEN LENGTH(metadata::text) > 1000
                        THEN LEFT(metadata::text, 1000) || '...'
                        ELSE metadata::text
                    END as metadata,
                    CASE
                        WHEN LENGTH(error_message) > 1000
                        THEN LEFT(error_message, 1000) || '...'
                        ELSE error_message
                    END as error_message,
                    collection_names, created_at, updated_at
                """
            else:
                select_fields = """
                    id, source_type, enabled_collections, url, status, metadata, error_message,
                    collection_names, created_at, updated_at
                """

            # Build WHERE clause dynamically
            where_clauses = []
            params = []
            param_idx = 1

            if source_type is not None:
                where_clauses.append(f"source_type = ${param_idx}")
                params.append(source_type)
                param_idx += 1

            if status is not None:
                where_clauses.append(f"status = ${param_idx}")
                params.append(status)
                param_idx += 1

            where_clause = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

            # Get total count
            count_query = f"SELECT COUNT(*) FROM sources {where_clause}"

            async with self.db_pool.acquire() as conn:
                total_count = await conn.fetchval(count_query, *params)

                # Get paginated sources
                # Critical Gotcha #3: Use $1, $2 placeholders
                query = f"""
                    SELECT {select_fields}
                    FROM sources
                    {where_clause}
                    ORDER BY created_at DESC
                    LIMIT ${param_idx} OFFSET ${param_idx + 1}
                """
                params.extend([limit, offset])
                rows = await conn.fetch(query, *params)

            sources = [dict(row) for row in rows]

            return True, {
                "sources": sources,
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
            }

        except asyncpg.PostgresError as e:
            logger.error(f"Database error listing sources: {e}")
            return False, {"error": f"Database error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error listing sources: {e}")
            return False, {"error": f"Error listing sources: {str(e)}"}

    async def update_source(
        self, source_id: UUID, updates: dict[str, Any]
    ) -> tuple[bool, dict[str, Any]]:
        """Update a source with partial updates.

        Args:
            source_id: UUID of the source to update
            updates: Dictionary with fields to update (source_type, url, status, metadata, error_message)

        Returns:
            Tuple of (success, result_dict with updated source or error)

        Critical Gotcha #3: Use $1, $2 placeholders
        Critical Gotcha #8: Always use async with
        """
        try:
            if not updates:
                return False, {"error": "No updates provided"}

            # Validate source_type if being updated
            if "source_type" in updates:
                is_valid, error_msg = self.validate_source_type(updates["source_type"])
                if not is_valid:
                    return False, {"error": error_msg}

            # Validate status if being updated
            if "status" in updates:
                is_valid, error_msg = self.validate_status(updates["status"])
                if not is_valid:
                    return False, {"error": error_msg}

            # Build dynamic UPDATE query
            set_clauses = []
            params = []
            param_idx = 1

            allowed_fields = ["source_type", "enabled_collections", "url", "status", "metadata", "error_message"]

            for field in allowed_fields:
                if field in updates:
                    set_clauses.append(f"{field} = ${param_idx}")
                    params.append(updates[field])
                    param_idx += 1

            if not set_clauses:
                return False, {"error": "No valid fields to update"}

            # Add source_id as final parameter
            params.append(source_id)

            query = f"""
                UPDATE sources
                SET {', '.join(set_clauses)}
                WHERE id = ${param_idx}
                RETURNING id, source_type, enabled_collections, url, status, metadata, error_message,
                          collection_names, created_at, updated_at
            """

            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow(query, *params)

            if not row:
                return False, {"error": f"Source not found: {source_id}"}

            source = dict(row)
            logger.info(f"Updated source: {source_id}")

            return True, {"source": source}

        except asyncpg.PostgresError as e:
            logger.error(f"Database error updating source: {e}")
            return False, {"error": f"Database error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error updating source: {e}")
            return False, {"error": f"Error updating source: {str(e)}"}

    async def delete_source(self, source_id: UUID) -> tuple[bool, dict[str, Any]]:
        """Delete a source and all associated documents and Qdrant collections.

        Args:
            source_id: UUID of the source to delete

        Returns:
            Tuple of (success, result_dict with deleted source or error)

        Critical Gotcha #3: Use $1, $2 placeholders
        Critical Gotcha #8: Always use async with

        Per-Domain Collections (Task 3):
        - Deletes Qdrant collections for this source
        - Logs errors but doesn't fail if Qdrant deletion fails (graceful degradation)

        Note: Due to CASCADE foreign keys, this will also delete:
        - All documents associated with this source
        - All chunks from those documents
        - All crawl_jobs for this source
        """
        try:
            # Step 1: Get source with collection_names before deleting
            async with self.db_pool.acquire() as conn:
                source_row = await conn.fetchrow(
                    """
                    SELECT id, source_type, enabled_collections, url, status, metadata, error_message,
                           collection_names, created_at, updated_at
                    FROM sources
                    WHERE id = $1
                    """,
                    source_id
                )

            if not source_row:
                return False, {"error": f"Source not found: {source_id}"}

            source = dict(source_row)
            collection_names_raw = source.get("collection_names")

            # Step 2: Delete Qdrant collections (if CollectionManager available)
            if self.collection_manager and collection_names_raw:
                try:
                    # Parse collection_names from JSONB (could be string or dict)
                    if isinstance(collection_names_raw, str):
                        collection_names = json.loads(collection_names_raw)
                    elif isinstance(collection_names_raw, dict):
                        collection_names = collection_names_raw
                    else:
                        collection_names = {}

                    if collection_names:
                        logger.info(
                            f"Deleting Qdrant collections for source {source_id}: "
                            f"{list(collection_names.values())}"
                        )

                        await self.collection_manager.delete_collections_for_source(
                            collection_names=collection_names
                        )

                        logger.info(
                            f"Deleted {len(collection_names)} Qdrant collections for source {source_id}"
                        )
                    else:
                        logger.info(f"No collections to delete for source {source_id}")

                except Exception as e:
                    # Log error but continue with database deletion
                    # (Qdrant collections can be manually cleaned up later)
                    logger.error(
                        f"Failed to delete Qdrant collections for source {source_id}: {e}. "
                        f"Continuing with database deletion."
                    )

            # Step 3: Delete source from database
            query = """
                DELETE FROM sources
                WHERE id = $1
                RETURNING id, source_type, enabled_collections, url, status, metadata, error_message,
                          collection_names, created_at, updated_at
            """

            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow(query, source_id)

            if not row:
                return False, {"error": f"Source not found: {source_id}"}

            deleted_source = dict(row)
            logger.info(f"Deleted source: {source_id}")

            return True, {"source": deleted_source}

        except asyncpg.PostgresError as e:
            logger.error(f"Database error deleting source: {e}")
            return False, {"error": f"Database error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error deleting source: {e}")
            return False, {"error": f"Error deleting source: {str(e)}"}
