"""MCP search tools for RAG knowledge base queries.

This module provides MCP tools for searching the knowledge base using different
search strategies (vector, hybrid, auto).

Pattern: examples/02_mcp_consolidated_tools.py (PRIMARY)
Reference: infra/archon/python/src/mcp_server/features/rag/rag_tools.py

CRITICAL GOTCHAS ADDRESSED:
- Gotcha #6: MCP tools MUST return JSON strings (not dicts) - use json.dumps()
- Gotcha #7: Truncate content to 1000 chars max, limit to 20 items max per page
- Gotcha #2: Get pool from dependency, acquire connections in services

Key Design:
- JSON string return (NOT dict - MCP protocol requirement)
- Content truncation to 1000 chars (payload optimization)
- Result limiting to 20 items max (prevent oversized responses)
- search_type validation (vector, hybrid, auto)
- Dependency injection for RAGService initialization
"""

import json
import logging
from typing import Any, Dict, Optional

from mcp.server.fastmcp import Context, FastMCP

logger = logging.getLogger(__name__)

# MCP payload optimization constants (CRITICAL for MCP protocol)
MAX_CONTENT_LENGTH = 1000  # Truncate content to 1000 chars (Gotcha #7)
MAX_RESULTS_PER_PAGE = 20  # Limit results to 20 items max (Gotcha #7)


def truncate_content(text: str | None, max_length: int = MAX_CONTENT_LENGTH) -> str | None:
    """Truncate text to maximum length with ellipsis.

    CRITICAL: Always truncate content in MCP responses to prevent payload issues.

    Args:
        text: Text to truncate
        max_length: Maximum length before truncation (default: 1000)

    Returns:
        Truncated text or None if input was None

    Example:
        truncated = truncate_content("Very long text...", 100)
        # Returns: "Very long text... (truncated at 97 chars)..."
    """
    if text is None:
        return None

    if len(text) > max_length:
        return text[: max_length - 3] + "..."

    return text


def optimize_result_for_mcp(result: Dict[str, Any]) -> Dict[str, Any]:
    """Optimize search result for MCP response.

    CRITICAL: Always optimize results to reduce payload size.

    Optimizations:
    1. Truncate 'text' field to MAX_CONTENT_LENGTH
    2. Truncate any other large text fields
    3. Remove unnecessary nested fields

    Args:
        result: Search result dictionary from RAGService

    Returns:
        Optimized result dictionary

    Example:
        result = {"chunk_id": "123", "text": "Very long text...", "score": 0.95}
        optimized = optimize_result_for_mcp(result)
        # optimized["text"] is now truncated to 1000 chars
    """
    result = result.copy()  # Don't modify original

    # Truncate main text field (Gotcha #7)
    if "text" in result and result["text"]:
        result["text"] = truncate_content(result["text"])

    # Truncate any content fields in metadata
    if "metadata" in result and isinstance(result["metadata"], dict):
        metadata = result["metadata"].copy()
        for key in ["content", "text", "summary", "description"]:
            if key in metadata and metadata[key]:
                metadata[key] = truncate_content(metadata[key])
        result["metadata"] = metadata

    return result


def register_search_tools(mcp: FastMCP):
    """Register all search-related MCP tools.

    This function registers the search_knowledge_base tool with the MCP server.

    Args:
        mcp: FastMCP server instance to register tools with

    Example:
        from mcp.server.fastmcp import FastMCP
        mcp = FastMCP("RAG Service")
        register_search_tools(mcp)
    """

    @mcp.tool()
    async def search_knowledge_base(
        ctx: Context,
        query: str,
        search_type: str = "auto",
        limit: int = 10,
        source_id: str | None = None,
    ) -> str:
        """Search knowledge base for relevant content using RAG.

        This tool provides semantic search over the knowledge base using different
        search strategies. It supports vector similarity search, hybrid search
        (vector + full-text), and automatic strategy selection.

        CRITICAL MCP REQUIREMENTS:
        - Returns JSON string (NOT dict) - MCP protocol requirement (Gotcha #6)
        - Content truncated to 1000 chars max (Gotcha #7)
        - Results limited to 20 items max (Gotcha #7)

        Args:
            query: Search query - Keep SHORT and FOCUSED (2-5 keywords).
                   Good: "vector search", "authentication JWT", "React hooks"
                   Bad: "how to implement user authentication with JWT tokens..."
            search_type: Search strategy to use (default: "auto")
                        - "vector": Vector similarity search only (<50ms p95)
                        - "hybrid": Vector + full-text search (<100ms p95)
                        - "auto": Use hybrid if enabled via USE_HYBRID_SEARCH, else vector (recommended)
            limit: Maximum number of results (default: 10, max: 20)
            source_id: Optional source ID filter from sources table.
                      This is the database 'id' field (UUID), not URL or domain.
                      Example: "550e8400-e29b-41d4-a716-446655440000"

        Returns:
            JSON string with structure:
            {
                "success": bool,
                "results": list[dict],  # Search results with content and metadata
                "count": int,           # Number of results returned
                "search_type": str,     # Strategy used ("vector" or "hybrid")
                "error": str | null     # Error description if success=false
            }

        Examples:
            # Vector search (default)
            search_knowledge_base(query="FastAPI async patterns")

            # Hybrid search with source filter
            search_knowledge_base(
                query="authentication",
                search_type="hybrid",
                limit=5,
                source_id="550e8400-e29b-41d4-a716-446655440000"
            )

            # Auto mode (uses best available strategy)
            search_knowledge_base(
                query="RAG architecture",
                search_type="auto",
                limit=10
            )

        Performance:
        - Vector search: <50ms p95 latency
        - Hybrid search: <100ms p95 latency
        - Graceful degradation if hybrid fails (fallback to vector)
        """
        try:
            # Validate inputs
            if not query or not query.strip():
                return json.dumps(
                    {
                        "success": False,
                        "results": [],
                        "count": 0,
                        "error": "Query cannot be empty",
                        "suggestion": "Provide a search query (2-5 keywords recommended)",
                    },
                    indent=2,
                )

            if search_type not in ["vector", "hybrid", "auto"]:
                return json.dumps(
                    {
                        "success": False,
                        "results": [],
                        "count": 0,
                        "error": f"Invalid search_type: {search_type}",
                        "suggestion": "Use 'vector', 'hybrid', or 'auto'",
                    },
                    indent=2,
                )

            # Limit results to MAX_RESULTS_PER_PAGE (Gotcha #7)
            limit = min(limit, MAX_RESULTS_PER_PAGE)

            # Get RAGService instance from application context
            # Note: This assumes RAGService is initialized in app.state during startup
            rag_service = ctx.request_context.app.state.rag_service

            if rag_service is None:
                return json.dumps(
                    {
                        "success": False,
                        "results": [],
                        "count": 0,
                        "error": "RAGService not initialized",
                        "suggestion": "Service may be starting up or initialization failed",
                    },
                    indent=2,
                )

            # Build filters if source_id provided
            filters: Optional[Dict[str, Any]] = None
            if source_id:
                filters = {"source_id": source_id}

            # Execute search using RAGService
            # RAGService raises exceptions (NOT tuple pattern)
            results = await rag_service.search(
                query=query, limit=limit, search_type=search_type, filters=filters
            )

            # Optimize results for MCP (truncate content, limit size)
            optimized_results = [optimize_result_for_mcp(result) for result in results]

            # CRITICAL: Return JSON string, NOT dict (Gotcha #6)
            return json.dumps(
                {
                    "success": True,
                    "results": optimized_results,
                    "count": len(optimized_results),
                    "search_type": search_type,
                    "error": None,
                },
                indent=2,
            )

        except ValueError as e:
            # Validation errors from RAGService
            logger.error(f"Search validation error: {e}")
            return json.dumps(
                {
                    "success": False,
                    "results": [],
                    "count": 0,
                    "error": str(e),
                    "suggestion": "Check search_type parameter and query format",
                },
                indent=2,
            )

        except Exception as e:
            # Operational errors (database, Qdrant, OpenAI, etc.)
            logger.error(
                f"Error in search_knowledge_base: query='{query[:50]}...', error={e}",
                exc_info=True,
            )
            return json.dumps(
                {
                    "success": False,
                    "results": [],
                    "count": 0,
                    "error": str(e),
                    "suggestion": "Check error message and try again. "
                    "Ensure database and Qdrant are accessible.",
                },
                indent=2,
            )

    # Log successful registration
    logger.info("✓ Search tools registered (search_knowledge_base)")
