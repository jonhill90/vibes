"""Document Management MCP Tools for RAG Service.

This module provides consolidated document CRUD operations via MCP tools:
- manage_document: Consolidated create/update/delete/get/list operations

Critical Gotchas Addressed:
- Gotcha #6: Return json.dumps() NOT dict (MCP protocol requirement)
- Gotcha #7: Truncate content to 1000 chars, limit to 20 items per page

Pattern Source: prps/rag_service_implementation/examples/02_mcp_consolidated_tools.py
Reference: infra/archon/python/src/mcp_server/features/projects/project_tools.py
"""

import json
import logging
from typing import Any
from uuid import UUID

from mcp.server.fastmcp import Context

logger = logging.getLogger(__name__)

# MCP optimization constants (Gotcha #7)
MAX_CONTENT_LENGTH = 1000
MAX_ITEMS_PER_PAGE = 20
DEFAULT_PAGE_SIZE = 10


def truncate_text(text: str | None, max_length: int = MAX_CONTENT_LENGTH) -> str | None:
    """Truncate text to maximum length with ellipsis.

    Pattern: examples/02_mcp_consolidated_tools.py

    Args:
        text: Text to truncate
        max_length: Maximum length before truncation

    Returns:
        Truncated text or None if input was None
    """
    if text and len(text) > max_length:
        return text[:max_length - 3] + "..."
    return text


def optimize_document_for_mcp(document: dict[str, Any]) -> dict[str, Any]:
    """Optimize document object for MCP response.

    CRITICAL: Always optimize list responses to reduce payload size (Gotcha #7).

    Pattern: Truncate large text fields, minimize metadata

    Args:
        document: Document dictionary from database

    Returns:
        Optimized document dictionary
    """
    document = document.copy()  # Don't modify original

    # Truncate title if present
    if "title" in document and document["title"]:
        document["title"] = truncate_text(document["title"])

    # Minimize metadata JSONB field if present
    if "metadata" in document and isinstance(document["metadata"], dict):
        # Keep only essential metadata keys
        essential_keys = ["author", "created", "format", "pages"]
        document["metadata"] = {
            k: v for k, v in document["metadata"].items()
            if k in essential_keys
        }

    return document


def register_document_tools(mcp):
    """Register document management tools with MCP server.

    Args:
        mcp: FastMCP server instance
    """

    @mcp.tool()
    async def manage_document(
        ctx: Context,
        action: str,  # "create" | "update" | "delete" | "get" | "list"
        document_id: str | None = None,
        title: str | None = None,
        source_id: str | None = None,
        file_path: str | None = None,
        document_type: str | None = None,
        url: str | None = None,
        metadata: dict[str, Any] | None = None,
        page: int = 1,
        per_page: int = DEFAULT_PAGE_SIZE,
    ) -> str:
        """Manage documents (consolidated: create/update/delete/get/list).

        PATTERN: Single tool for all document CRUD operations
        - create: Ingest document from file (parse → chunk → embed → store)
        - update: Update document metadata
        - delete: Delete document and all chunks
        - get: Get single document by ID
        - list: List documents with filters and pagination

        Args:
            action: "create" | "update" | "delete" | "get" | "list"
            document_id: Document UUID for get/update/delete
            title: Document title (required for create)
            source_id: Source UUID (required for create)
            file_path: File path for upload (required for create)
            document_type: Document type (pdf, html, docx, text, markdown)
            url: Document URL (optional)
            metadata: Additional metadata as dict (optional)
            page: Page number for list (default: 1)
            per_page: Items per page (default: 10, max: 20)

        Returns:
            JSON string with {success: bool, ...} (NEVER returns dict - Gotcha #6)

        Examples:
            manage_document("create", title="Guide", source_id="src-123", file_path="/tmp/doc.pdf")
            manage_document("get", document_id="doc-456")
            manage_document("update", document_id="doc-456", title="Updated Title")
            manage_document("delete", document_id="doc-456")
            manage_document("list", page=1, per_page=10)
        """
        try:
            # Get services from app state
            document_service = ctx.app.state.document_service
            ingestion_service = ctx.app.state.ingestion_service

            # ACTION: create - Ingest document
            if action == "create":
                # Validate required fields
                if not all([title, source_id, file_path]):
                    return json.dumps({
                        "success": False,
                        "error": "title, source_id, and file_path required for create",
                        "suggestion": "Provide all required fields: title, source_id, file_path"
                    })

                # Parse UUID
                try:
                    source_uuid = UUID(source_id)
                except ValueError:
                    return json.dumps({
                        "success": False,
                        "error": f"Invalid source_id format: {source_id}",
                        "suggestion": "source_id must be a valid UUID"
                    })

                # Prepare metadata
                doc_metadata = metadata or {}
                doc_metadata["title"] = title
                if url:
                    doc_metadata["url"] = url

                # Ingest document (parse → chunk → embed → store)
                success, result = await ingestion_service.ingest_document(
                    source_id=source_uuid,
                    file_path=file_path,
                    document_metadata=doc_metadata,
                )

                if not success:
                    return json.dumps({
                        "success": False,
                        "error": result.get("error", "Document ingestion failed"),
                        "suggestion": "Check file_path exists and is valid document format"
                    })

                # Truncate success response (Gotcha #7)
                return json.dumps({
                    "success": True,
                    "document_id": result.get("document_id"),
                    "chunks_stored": result.get("chunks_stored"),
                    "chunks_failed": result.get("chunks_failed"),
                    "total_chunks": result.get("total_chunks"),
                    "ingestion_time_ms": result.get("ingestion_time_ms"),
                    "message": result.get("message", "Document created successfully")
                })

            # ACTION: update - Update document metadata
            elif action == "update":
                if not document_id:
                    return json.dumps({
                        "success": False,
                        "error": "document_id required for update",
                        "suggestion": "Provide document_id to update"
                    })

                # Parse UUID
                try:
                    doc_uuid = UUID(document_id)
                except ValueError:
                    return json.dumps({
                        "success": False,
                        "error": f"Invalid document_id format: {document_id}",
                        "suggestion": "document_id must be a valid UUID"
                    })

                # Build updates dictionary
                updates = {}
                if title is not None:
                    updates["title"] = title
                if document_type is not None:
                    updates["document_type"] = document_type
                if url is not None:
                    updates["url"] = url
                if metadata is not None:
                    updates["metadata"] = metadata

                if not updates:
                    return json.dumps({
                        "success": False,
                        "error": "No fields to update",
                        "suggestion": "Provide at least one field to update"
                    })

                # Update document
                success, result = await document_service.update_document(
                    doc_uuid, updates
                )

                if not success:
                    return json.dumps({
                        "success": False,
                        "error": result.get("error", "Document update failed"),
                        "suggestion": "Check document_id is valid and fields are correct"
                    })

                # Optimize response (Gotcha #7)
                document = result.get("document")
                if document:
                    document = optimize_document_for_mcp(document)

                return json.dumps({
                    "success": True,
                    "document": document,
                    "message": result.get("message", "Document updated successfully")
                })

            # ACTION: delete - Delete document and all chunks
            elif action == "delete":
                if not document_id:
                    return json.dumps({
                        "success": False,
                        "error": "document_id required for delete",
                        "suggestion": "Provide document_id to delete"
                    })

                # Parse UUID
                try:
                    doc_uuid = UUID(document_id)
                except ValueError:
                    return json.dumps({
                        "success": False,
                        "error": f"Invalid document_id format: {document_id}",
                        "suggestion": "document_id must be a valid UUID"
                    })

                # Delete document (also deletes vectors and chunks)
                success, result = await ingestion_service.delete_document(doc_uuid)

                if not success:
                    return json.dumps({
                        "success": False,
                        "error": result.get("error", "Document deletion failed"),
                        "suggestion": "Check document_id is valid"
                    })

                return json.dumps({
                    "success": True,
                    "message": result.get("message", "Document deleted successfully")
                })

            # ACTION: get - Get single document by ID
            elif action == "get":
                if not document_id:
                    return json.dumps({
                        "success": False,
                        "error": "document_id required for get",
                        "suggestion": "Provide document_id to retrieve"
                    })

                # Parse UUID
                try:
                    doc_uuid = UUID(document_id)
                except ValueError:
                    return json.dumps({
                        "success": False,
                        "error": f"Invalid document_id format: {document_id}",
                        "suggestion": "document_id must be a valid UUID"
                    })

                # Get document
                success, result = await document_service.get_document(doc_uuid)

                if not success:
                    return json.dumps({
                        "success": False,
                        "error": result.get("error", "Document not found"),
                        "suggestion": "Verify document_id is correct"
                    })

                # Optimize response (Gotcha #7)
                document = result.get("document")
                if document:
                    document = optimize_document_for_mcp(document)

                return json.dumps({
                    "success": True,
                    "document": document
                })

            # ACTION: list - List documents with filters and pagination
            elif action == "list":
                # Limit per_page to MAX_ITEMS_PER_PAGE (Gotcha #7)
                per_page = min(per_page, MAX_ITEMS_PER_PAGE)

                # Build filters
                filters = {}
                if source_id:
                    try:
                        source_uuid = UUID(source_id)
                        filters["source_id"] = source_uuid
                    except ValueError:
                        return json.dumps({
                            "success": False,
                            "error": f"Invalid source_id format: {source_id}",
                            "suggestion": "source_id must be a valid UUID"
                        })

                if document_type:
                    filters["document_type"] = document_type

                # List documents with optimization (exclude large fields)
                success, result = await document_service.list_documents(
                    filters=filters,
                    page=page,
                    per_page=per_page,
                    exclude_large_fields=True,  # MCP optimization (Gotcha #7)
                )

                if not success:
                    return json.dumps({
                        "success": False,
                        "error": result.get("error", "Failed to list documents"),
                        "suggestion": "Check error message and try again"
                    })

                documents = result.get("documents", [])
                total_count = result.get("total_count", 0)

                # Optimize each document (extra safety)
                optimized_documents = [
                    optimize_document_for_mcp(doc) for doc in documents
                ]

                # CRITICAL: Return JSON string, NOT dict (Gotcha #6)
                return json.dumps({
                    "success": True,
                    "documents": optimized_documents,
                    "total_count": total_count,
                    "count": len(optimized_documents),
                    "page": page,
                    "per_page": per_page
                })

            else:
                return json.dumps({
                    "success": False,
                    "error": f"Unknown action: {action}",
                    "suggestion": "Use 'create', 'update', 'delete', 'get', or 'list'"
                })

        except Exception as e:
            logger.error(f"Error in manage_document ({action}): {e}", exc_info=True)
            return json.dumps({
                "success": False,
                "error": str(e),
                "suggestion": "Check error message and try again"
            })
