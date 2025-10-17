"""
SourceService: CRUD operations for RAG sources

This service handles all database operations for source management
(upload, crawl, api) with comprehensive validation and error handling.

Pattern: Service Layer with asyncpg Connection Pooling
Returns: All methods return tuple[bool, dict] for consistent error handling
"""

from typing import Any
import asyncpg
import logging
import json
from uuid import UUID

logger = logging.getLogger(__name__)


class SourceService:
    """Service class for source CRUD operations.

    Handles ingestion sources (upload, crawl, api) with status tracking
    and metadata management.
    """

    VALID_SOURCE_TYPES = ["upload", "crawl", "api"]
    VALID_STATUSES = ["active", "processing", "failed", "archived"]

    def __init__(self, db_pool: asyncpg.Pool):
        """Initialize SourceService with database connection pool.

        Args:
            db_pool: asyncpg connection pool for database operations

        Critical Gotcha #2: Store pool NOT connection
        """
        self.db_pool = db_pool

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
        """Create a new source in the database.

        Args:
            source_data: Dictionary with keys:
                - source_type (required): 'upload', 'crawl', or 'api'
                - url (optional): Source URL
                - status (optional): Defaults to 'active'
                - metadata (optional): JSONB metadata
                - error_message (optional): Error details

        Returns:
            Tuple of (success, result_dict with source or error)

        Critical Gotcha #3: Use $1, $2 placeholders (asyncpg), NOT %s
        Critical Gotcha #8: Always use async with pool.acquire()
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

            # Convert metadata dict to JSON string for JSONB column
            metadata_json = json.dumps(metadata) if isinstance(metadata, dict) else metadata

            # Insert source using asyncpg $1, $2 placeholders
            query = """
                INSERT INTO sources (source_type, enabled_collections, url, status, metadata, error_message)
                VALUES ($1, $2, $3, $4, $5::jsonb, $6)
                RETURNING id, source_type, enabled_collections, url, status, metadata, error_message,
                          created_at, updated_at
            """

            # Critical Gotcha #8: Always use async with for connection management
            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow(
                    query, source_type, enabled_collections, url, status, metadata_json, error_message
                )

            source = dict(row)
            logger.info(f"Created source: {source['id']}")

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

        Critical Gotcha #3: Use $1, $2 placeholders
        Critical Gotcha #8: Always use async with
        """
        try:
            query = """
                SELECT id, source_type, enabled_collections, url, status, metadata, error_message,
                       created_at, updated_at
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
                    created_at, updated_at
                """
            else:
                select_fields = """
                    id, source_type, enabled_collections, url, status, metadata, error_message,
                    created_at, updated_at
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
                          created_at, updated_at
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
        """Delete a source and all associated documents (CASCADE).

        Args:
            source_id: UUID of the source to delete

        Returns:
            Tuple of (success, result_dict with deleted source or error)

        Critical Gotcha #3: Use $1, $2 placeholders
        Critical Gotcha #8: Always use async with

        Note: Due to CASCADE foreign keys, this will also delete:
        - All documents associated with this source
        - All chunks from those documents
        - All crawl_jobs for this source
        """
        try:
            query = """
                DELETE FROM sources
                WHERE id = $1
                RETURNING id, source_type, enabled_collections, url, status, metadata, error_message,
                          created_at, updated_at
            """

            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow(query, source_id)

            if not row:
                return False, {"error": f"Source not found: {source_id}"}

            source = dict(row)
            logger.info(f"Deleted source: {source_id}")

            return True, {"source": source}

        except asyncpg.PostgresError as e:
            logger.error(f"Database error deleting source: {e}")
            return False, {"error": f"Database error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error deleting source: {e}")
            return False, {"error": f"Error deleting source: {str(e)}"}
