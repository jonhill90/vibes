"""Document Service Module - Business Logic for Document CRUD Operations.

This module provides:
- Document CRUD operations with validation
- Pagination and field exclusion for performance
- Proper error handling with tuple[bool, dict] return pattern
- Integration with sources table via foreign keys

Critical Gotchas Addressed:
- Gotcha #2: Store db_pool (NOT connection) in __init__
- Gotcha #3: Use $1, $2 placeholders (asyncpg style, NOT %s)
- Gotcha #8: Always use async with pool.acquire() for connections

Pattern Source: prps/rag_service_implementation/examples/01_service_layer_pattern.py
Reference: infra/task-manager/backend/src/services/task_service.py
"""

from typing import Any
from uuid import UUID
import asyncpg
import logging
import json

logger = logging.getLogger(__name__)


class DocumentService:
    """Service class for document operations with asyncpg connection pooling."""

    VALID_DOCUMENT_TYPES = ["pdf", "markdown", "html", "text", "docx"]

    def __init__(self, db_pool: asyncpg.Pool):
        """Initialize DocumentService with database connection pool.

        CRITICAL PATTERN (Gotcha #2):
        - Store db_pool, NOT connection
        - Connections acquired per-operation via async with pool.acquire()

        Args:
            db_pool: asyncpg connection pool for database operations
        """
        self.db_pool = db_pool

    def validate_document_type(self, document_type: str) -> tuple[bool, str]:
        """Validate document type against allowed values.

        Args:
            document_type: Document type string to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if document_type and document_type not in self.VALID_DOCUMENT_TYPES:
            return (
                False,
                f"Invalid document_type '{document_type}'. Must be one of: {', '.join(self.VALID_DOCUMENT_TYPES)}",
            )
        return True, ""

    async def list_documents(
        self,
        filters: dict[str, Any] | None = None,
        page: int = 1,
        per_page: int = 50,
        exclude_large_fields: bool = False,
    ) -> tuple[bool, dict[str, Any]]:
        """List documents with filters, pagination, and optional field exclusion.

        PATTERN: Conditional field selection for MCP optimization
        - exclude_large_fields=True: Exclude metadata JSONB field
        - exclude_large_fields=False: Return full document data

        Args:
            filters: Optional filters (source_id, document_type)
            page: Page number (1-indexed)
            per_page: Items per page
            exclude_large_fields: If True, exclude large JSONB fields

        Returns:
            Tuple of (success, result_dict with documents and total_count)
        """
        try:
            filters = filters or {}
            offset = (page - 1) * per_page

            # Build base query with conditional field selection
            if exclude_large_fields:
                # Exclude metadata JSONB field for MCP optimization
                select_fields = """
                    id, source_id, title, document_type, url,
                    created_at, updated_at
                """
            else:
                select_fields = "*"

            where_clauses = []
            params = []
            param_idx = 1

            # Apply filters
            if "source_id" in filters:
                where_clauses.append(f"source_id = ${param_idx}")
                params.append(filters["source_id"])
                param_idx += 1

            if "document_type" in filters:
                document_type = filters["document_type"]
                is_valid, error_msg = self.validate_document_type(document_type)
                if not is_valid:
                    return False, {"error": error_msg}
                where_clauses.append(f"document_type = ${param_idx}")
                params.append(document_type)
                param_idx += 1

            where_clause = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

            # Get total count
            count_query = f"SELECT COUNT(*) FROM documents {where_clause}"

            # CRITICAL PATTERN (Gotcha #8): Always use async with for connection management
            async with self.db_pool.acquire() as conn:
                total_count = await conn.fetchval(count_query, *params)

                # Get paginated documents
                # CRITICAL (Gotcha #3): Use $1, $2 placeholders (asyncpg), not %s
                query = f"""
                    SELECT {select_fields}
                    FROM documents
                    {where_clause}
                    ORDER BY created_at DESC
                    LIMIT ${param_idx} OFFSET ${param_idx + 1}
                """
                params.extend([per_page, offset])
                rows = await conn.fetch(query, *params)

            documents = [dict(row) for row in rows]

            return True, {
                "documents": documents,
                "total_count": total_count,
                "page": page,
                "per_page": per_page,
            }

        except asyncpg.PostgresError as e:
            logger.error(f"Database error listing documents: {e}")
            return False, {"error": f"Database error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            return False, {"error": f"Error listing documents: {str(e)}"}

    async def get_document(self, document_id: UUID) -> tuple[bool, dict[str, Any]]:
        """Get a single document by ID.

        Args:
            document_id: UUID of the document to retrieve

        Returns:
            Tuple of (success, result_dict with document data or error)
        """
        try:
            async with self.db_pool.acquire() as conn:
                query = "SELECT * FROM documents WHERE id = $1"
                row = await conn.fetchrow(query, document_id)

            if row is None:
                return False, {"error": f"Document with ID {document_id} not found"}

            document = dict(row)
            return True, {"document": document}

        except asyncpg.PostgresError as e:
            logger.error(f"Database error getting document {document_id}: {e}")
            return False, {"error": f"Database error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error getting document {document_id}: {e}")
            return False, {"error": f"Error getting document: {str(e)}"}

    async def create_document(
        self, document_data: dict[str, Any]
    ) -> tuple[bool, dict[str, Any]]:
        """Create a new document.

        PATTERN: Validate inputs, insert with RETURNING clause

        Args:
            document_data: Dictionary with document fields:
                - source_id (UUID, required): Foreign key to sources table
                - title (str, required): Document title
                - document_type (str, optional): Type of document
                - url (str, optional): Document URL
                - metadata (dict, optional): Additional metadata as JSONB

        Returns:
            Tuple of (success, result_dict with created document or error)
        """
        try:
            # Validate required fields
            if "source_id" not in document_data:
                return False, {"error": "Missing required field: source_id"}
            if "title" not in document_data:
                return False, {"error": "Missing required field: title"}

            # Validate document_type if provided
            document_type = document_data.get("document_type")
            if document_type:
                is_valid, error_msg = self.validate_document_type(document_type)
                if not is_valid:
                    return False, {"error": error_msg}

            # Extract fields with defaults
            source_id = document_data["source_id"]
            title = document_data["title"]
            url = document_data.get("url")
            metadata = document_data.get("metadata", {})

            # Convert metadata dict to JSON string for JSONB column
            metadata_json = json.dumps(metadata) if isinstance(metadata, dict) else metadata

            async with self.db_pool.acquire() as conn:
                # CRITICAL: Use $1, $2 placeholders (asyncpg style)
                query = """
                    INSERT INTO documents (
                        source_id, title, document_type, url, metadata,
                        created_at, updated_at
                    )
                    VALUES ($1, $2, $3, $4, $5::jsonb, NOW(), NOW())
                    RETURNING *
                """
                row = await conn.fetchrow(
                    query,
                    source_id,
                    title,
                    document_type,
                    url,
                    metadata_json,
                )

                document = dict(row)
                logger.info(f"Created document {document['id']} with title '{title}'")

                return True, {
                    "document": document,
                    "message": "Document created successfully",
                }

        except asyncpg.ForeignKeyViolationError as e:
            logger.error(f"Foreign key violation creating document: {e}")
            return False, {"error": "Invalid source_id: source does not exist"}
        except asyncpg.PostgresError as e:
            logger.error(f"Database error creating document: {e}")
            return False, {"error": f"Database error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error creating document: {e}")
            return False, {"error": f"Error creating document: {str(e)}"}

    async def update_document(
        self,
        document_id: UUID,
        updates: dict[str, Any],
    ) -> tuple[bool, dict[str, Any]]:
        """Update document fields.

        PATTERN: Partial updates with validation
        - Only update provided fields
        - Validate each field before updating
        - Always update updated_at timestamp

        Args:
            document_id: UUID of document to update
            updates: Dictionary with fields to update (title, document_type, url, metadata)

        Returns:
            Tuple of (success, result_dict with updated document or error)
        """
        try:
            update_fields = []
            params = []
            param_idx = 1

            # Build dynamic update query
            if "title" in updates:
                update_fields.append(f"title = ${param_idx}")
                params.append(updates["title"])
                param_idx += 1

            if "document_type" in updates:
                document_type = updates["document_type"]
                is_valid, error_msg = self.validate_document_type(document_type)
                if not is_valid:
                    return False, {"error": error_msg}
                update_fields.append(f"document_type = ${param_idx}")
                params.append(document_type)
                param_idx += 1

            if "url" in updates:
                update_fields.append(f"url = ${param_idx}")
                params.append(updates["url"])
                param_idx += 1

            if "metadata" in updates:
                update_fields.append(f"metadata = ${param_idx}")
                params.append(updates["metadata"])
                param_idx += 1

            if not update_fields:
                return False, {"error": "No fields to update"}

            # Always update timestamp
            update_fields.append("updated_at = NOW()")

            # Add document_id as final parameter
            params.append(document_id)

            query = f"""
                UPDATE documents
                SET {', '.join(update_fields)}
                WHERE id = ${param_idx}
                RETURNING *
            """

            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow(query, *params)

            if row is None:
                return False, {"error": f"Document with ID {document_id} not found"}

            document = dict(row)
            logger.info(f"Updated document {document_id}")

            return True, {
                "document": document,
                "message": "Document updated successfully",
            }

        except asyncpg.PostgresError as e:
            logger.error(f"Database error updating document {document_id}: {e}")
            return False, {"error": f"Database error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error updating document {document_id}: {e}")
            return False, {"error": f"Error updating document: {str(e)}"}

    async def delete_document(
        self,
        document_id: UUID,
        vector_service = None,
    ) -> tuple[bool, dict[str, Any]]:
        """Delete a document by ID with Qdrant vector cleanup.

        CRITICAL: This method performs atomic deletion from both PostgreSQL and Qdrant:
        1. Query chunk IDs from PostgreSQL
        2. Delete vectors from Qdrant using chunk IDs
        3. Delete document from PostgreSQL (CASCADE deletes chunks)

        If Qdrant deletion fails, PostgreSQL deletion is skipped to prevent orphaned vectors.

        NOTE: PostgreSQL CASCADE constraint deletes chunks automatically after document deletion.

        Args:
            document_id: UUID of document to delete
            vector_service: Optional VectorService instance for Qdrant cleanup

        Returns:
            Tuple of (success, result_dict with message or error)
        """
        try:
            async with self.db_pool.acquire() as conn:
                # Step 1: Get all chunk IDs for this document before deletion
                chunk_query = "SELECT id FROM chunks WHERE document_id = $1"
                chunk_rows = await conn.fetch(chunk_query, document_id)
                chunk_ids = [str(row["id"]) for row in chunk_rows]

                logger.info(f"Found {len(chunk_ids)} chunks to delete for document {document_id}")

                # Step 2: Delete vectors from Qdrant first (if vector_service provided)
                if vector_service and chunk_ids:
                    try:
                        deleted_count = await vector_service.delete_vectors(chunk_ids)
                        logger.info(f"Deleted {deleted_count} vectors from Qdrant for document {document_id}")
                    except Exception as e:
                        # Qdrant deletion failed - abort to prevent orphaned vectors
                        logger.error(f"Qdrant deletion failed for document {document_id}: {e}")
                        return False, {
                            "error": f"Failed to delete vectors from Qdrant: {str(e)}",
                            "detail": "Document not deleted to prevent orphaned vectors"
                        }

                # Step 3: Delete document from PostgreSQL (CASCADE deletes chunks)
                delete_query = "DELETE FROM documents WHERE id = $1 RETURNING id"
                row = await conn.fetchrow(delete_query, document_id)

                if row is None:
                    return False, {"error": f"Document with ID {document_id} not found"}

                logger.info(
                    f"Deleted document {document_id} with {len(chunk_ids)} chunks "
                    f"(Qdrant cleanup: {bool(vector_service and chunk_ids)})"
                )

                return True, {
                    "message": f"Document {document_id} deleted successfully",
                    "chunks_deleted": len(chunk_ids),
                    "qdrant_cleanup": bool(vector_service and chunk_ids),
                }

        except asyncpg.PostgresError as e:
            logger.error(f"Database error deleting document {document_id}: {e}")
            return False, {"error": f"Database error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            return False, {"error": f"Error deleting document: {str(e)}"}
