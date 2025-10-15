"""
MCP Tool: manage_source (Consolidated Source CRUD)

This tool provides consolidated CRUD operations for RAG sources via MCP protocol.
Follows the MCP consolidated tool pattern with JSON string returns.

PATTERN: Consolidated MCP Tools (manage pattern)
- Single tool for create/update/delete/get/list operations
- Action parameter routes to appropriate service method
- Returns JSON strings (not dicts) per MCP protocol requirement

CRITICAL GOTCHAS ADDRESSED:
- Gotcha #6: MCP tools MUST return JSON strings (not dicts)
- Gotcha #7: Truncate large fields (metadata, error_message) to 1000 chars
- Gotcha #7: Limit list results to 20 items max per page
"""

import json
import logging
from uuid import UUID

logger = logging.getLogger(__name__)

# MCP optimization constants (CRITICAL)
MAX_FIELD_LENGTH = 1000
MAX_SOURCES_PER_PAGE = 20
DEFAULT_PAGE_SIZE = 10


def truncate_text(text: str | None, max_length: int = MAX_FIELD_LENGTH) -> str | None:
    """Truncate text to maximum length with ellipsis.

    Args:
        text: Text to truncate
        max_length: Maximum length before truncation

    Returns:
        Truncated text or None if input was None
    """
    if text and len(text) > max_length:
        return text[:max_length - 3] + "..."
    return text


def optimize_source_for_mcp(source: dict) -> dict:
    """Optimize source object for MCP response.

    CRITICAL: Always optimize list responses to reduce payload size.
    Pattern from MCP consolidated tools: Truncate large fields.

    Args:
        source: Source dictionary from database

    Returns:
        Optimized source dictionary

    Gotcha #7: Truncate metadata and error_message to 1000 chars
    """
    source = source.copy()  # Don't modify original

    # Truncate metadata if present (convert to string for truncation)
    if "metadata" in source and source["metadata"]:
        metadata_str = json.dumps(source["metadata"]) if isinstance(source["metadata"], dict) else str(source["metadata"])
        truncated = truncate_text(metadata_str)
        if truncated != metadata_str:
            source["metadata"] = truncated + " (truncated)"

    # Truncate error_message if present (Gotcha #7)
    if "error_message" in source and source["error_message"]:
        source["error_message"] = truncate_text(source["error_message"])

    return source


async def manage_source(
    action: str,
    source_id: str | None = None,
    source_type: str | None = None,
    url: str | None = None,
    status: str | None = None,
    metadata: dict | None = None,
    error_message: str | None = None,
    limit: int = DEFAULT_PAGE_SIZE,
    offset: int = 0,
) -> str:
    """Manage RAG sources (consolidated: create/update/delete/get/list).

    PATTERN: Single tool for multiple CRUD operations
    - action="create": Create new source
    - action="update": Update existing source
    - action="delete": Delete source (cascades to documents)
    - action="get": Get single source by ID
    - action="list": List sources with optional filters

    Args:
        action: "create" | "update" | "delete" | "get" | "list"
        source_id: Source UUID (required for update/delete/get)
        source_type: "upload" | "crawl" | "api" (required for create)
        url: Source URL (optional)
        status: "pending" | "processing" | "completed" | "failed" (optional)
        metadata: JSONB metadata (optional)
        error_message: Error details (optional)
        limit: Max items per page for list (default: 10, max: 20)
        offset: Number of items to skip for list (default: 0)

    Returns:
        JSON string with result (NEVER returns dict - Gotcha #6)

    Examples:
        manage_source("create", source_type="upload", url="https://...", status="pending")
        manage_source("update", source_id="src-123", status="completed")
        manage_source("delete", source_id="src-123")
        manage_source("get", source_id="src-123")
        manage_source("list")
        manage_source("list", source_type="upload", status="completed")
    """
    try:
        # Import here to avoid circular imports
        from ..database import get_pool
        from ..services.source_service import SourceService

        # Get database pool and initialize service
        db_pool = await get_pool()
        source_service = SourceService(db_pool)

        # ACTION: CREATE
        if action == "create":
            # VALIDATION: Require source_type for create
            if not source_type:
                return json.dumps({
                    "success": False,
                    "error": "source_type is required for create",
                    "suggestion": "Provide source_type ('upload', 'crawl', or 'api')"
                })

            # Build source data
            source_data = {
                "source_type": source_type,
                "url": url,
                "status": status or "pending",
                "metadata": metadata or {},
                "error_message": error_message,
            }

            success, result = await source_service.create_source(source_data)

            if not success:
                return json.dumps({
                    "success": False,
                    "error": result.get("error", "Failed to create source"),
                    "suggestion": "Check error message and ensure all required fields are valid"
                })

            source = result.get("source")
            if source:
                source = optimize_source_for_mcp(source)

            return json.dumps({
                "success": True,
                "source": source,
                "source_id": str(source.get("id")) if source else None,
                "message": "Source created successfully"
            })

        # ACTION: UPDATE
        elif action == "update":
            if not source_id:
                return json.dumps({
                    "success": False,
                    "error": "source_id is required for update",
                    "suggestion": "Provide source_id to update"
                })

            # Build updates dictionary
            updates = {}
            if source_type is not None:
                updates["source_type"] = source_type
            if url is not None:
                updates["url"] = url
            if status is not None:
                updates["status"] = status
            if metadata is not None:
                updates["metadata"] = metadata
            if error_message is not None:
                updates["error_message"] = error_message

            if not updates:
                return json.dumps({
                    "success": False,
                    "error": "No fields provided to update",
                    "suggestion": "Provide at least one field to update"
                })

            try:
                source_uuid = UUID(source_id)
            except ValueError:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid source_id format: {source_id}",
                    "suggestion": "Provide a valid UUID for source_id"
                })

            success, result = await source_service.update_source(source_uuid, updates)

            if not success:
                return json.dumps({
                    "success": False,
                    "error": result.get("error", "Failed to update source"),
                    "suggestion": "Check source_id is valid and field values are correct"
                })

            source = result.get("source")
            if source:
                source = optimize_source_for_mcp(source)

            return json.dumps({
                "success": True,
                "source": source,
                "message": "Source updated successfully"
            })

        # ACTION: DELETE
        elif action == "delete":
            if not source_id:
                return json.dumps({
                    "success": False,
                    "error": "source_id is required for delete",
                    "suggestion": "Provide source_id to delete"
                })

            try:
                source_uuid = UUID(source_id)
            except ValueError:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid source_id format: {source_id}",
                    "suggestion": "Provide a valid UUID for source_id"
                })

            success, result = await source_service.delete_source(source_uuid)

            if not success:
                return json.dumps({
                    "success": False,
                    "error": result.get("error", "Failed to delete source"),
                    "suggestion": "Check source_id is valid"
                })

            return json.dumps({
                "success": True,
                "message": "Source deleted successfully (documents and chunks also deleted via CASCADE)"
            })

        # ACTION: GET
        elif action == "get":
            if not source_id:
                return json.dumps({
                    "success": False,
                    "error": "source_id is required for get",
                    "suggestion": "Provide source_id or use action='list' to see all sources"
                })

            try:
                source_uuid = UUID(source_id)
            except ValueError:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid source_id format: {source_id}",
                    "suggestion": "Provide a valid UUID for source_id"
                })

            success, result = await source_service.get_source(source_uuid)

            if not success:
                return json.dumps({
                    "success": False,
                    "error": result.get("error", "Source not found"),
                    "suggestion": "Verify the source_id is correct or use action='list' to see all sources"
                })

            source = result.get("source")
            if source:
                # Truncate even for single source (Gotcha #7)
                source = optimize_source_for_mcp(source)

            return json.dumps({
                "success": True,
                "source": source
            })

        # ACTION: LIST
        elif action == "list":
            # Limit per page to MAX_SOURCES_PER_PAGE (Gotcha #7)
            limit = min(limit, MAX_SOURCES_PER_PAGE)

            # List sources with optional filters
            # CRITICAL: exclude_large_fields=True for MCP responses (Gotcha #7)
            success, result = await source_service.list_sources(
                source_type=source_type,
                status=status,
                limit=limit,
                offset=offset,
                exclude_large_fields=True
            )

            if not success:
                return json.dumps({
                    "success": False,
                    "error": result.get("error", "Failed to list sources"),
                    "suggestion": "Check error message and try again"
                })

            sources = result.get("sources", [])
            total_count = result.get("total_count", 0)

            # Optimize each source (extra safety, service should already truncate)
            optimized_sources = [optimize_source_for_mcp(source) for source in sources]

            # CRITICAL: Return JSON string, NOT dict (Gotcha #6)
            return json.dumps({
                "success": True,
                "sources": optimized_sources,
                "total_count": total_count,
                "count": len(optimized_sources),
                "limit": limit,
                "offset": offset
            })

        # UNKNOWN ACTION
        else:
            return json.dumps({
                "success": False,
                "error": f"Unknown action: {action}",
                "suggestion": "Use 'create', 'update', 'delete', 'get', or 'list'"
            })

    except Exception as e:
        logger.error(f"Error in manage_source ({action}): {e}", exc_info=True)
        return json.dumps({
            "success": False,
            "error": str(e),
            "suggestion": "Check error message and try again"
        })
