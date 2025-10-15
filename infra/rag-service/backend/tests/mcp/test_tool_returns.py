"""MCP Tool Return Type Validation Tests.

This module tests the CRITICAL requirement that all MCP tools return
JSON strings (NOT dicts). This is Gotcha #3 from the PRP.

CRITICAL: MCP protocol requires JSON strings. Returning dicts breaks
the protocol and causes "Tool execution failed" errors in Claude Desktop.

Pattern: Unit tests for return type validation
Reference: prps/rag_service_completion.md (Task 8, lines 1353-1361, Gotcha #3)
"""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4


class TestToolReturnTypes:
    """Test that ALL MCP tools return JSON strings, never dicts (Gotcha #3)."""

    @pytest.mark.asyncio
    async def test_search_knowledge_base_returns_string_not_dict(
        self, mock_mcp_context
    ):
        """CRITICAL: search_knowledge_base must return JSON string, NOT dict.

        This is the most common MCP protocol violation. Developers often
        return dicts because it's more natural in Python, but MCP requires
        JSON strings.

        Expected:
        - Return type: str
        - NOT dict, list, or any other type
        """
        # Register tool
        from src.tools.search_tools import register_search_tools

        class MockMCP:
            def __init__(self):
                self.tools = {}
            def tool(self):
                return lambda func: (self.tools.update({func.__name__: func}), func)[1]

        mock_mcp = MockMCP()
        register_search_tools(mock_mcp)
        search_fn = mock_mcp.tools['search_knowledge_base']

        # Mock successful search
        mock_mcp_context.request_context.app.state.rag_service.search = AsyncMock(
            return_value=[
                {
                    "chunk_id": str(uuid4()),
                    "text": "Test content",
                    "score": 0.95,
                    "metadata": {}
                }
            ]
        )

        # Execute tool
        result = await search_fn(
            ctx=mock_mcp_context,
            query="test query",
        )

        # CRITICAL ASSERTION: Must be string
        assert isinstance(result, str), (
            f"PROTOCOL VIOLATION: search_knowledge_base returned {type(result).__name__}, "
            f"expected str. MCP tools MUST return JSON strings (Gotcha #3). "
            f"This will break Claude Desktop integration!"
        )

        # Should not be dict
        assert not isinstance(result, dict), (
            "PROTOCOL VIOLATION: Tool returned dict. Use json.dumps() to convert to string!"
        )

    @pytest.mark.asyncio
    async def test_manage_document_returns_string_not_dict(
        self, mock_mcp_context
    ):
        """CRITICAL: manage_document must return JSON string.

        Expected:
        - ALL actions return str (create, get, update, delete, list)
        - No action returns dict
        """
        from src.tools.document_tools import register_document_tools

        class MockMCP:
            def __init__(self):
                self.tools = {}
            def tool(self):
                return lambda func: (self.tools.update({func.__name__: func}), func)[1]

        mock_mcp = MockMCP()
        register_document_tools(mock_mcp)
        document_fn = mock_mcp.tools['manage_document']

        # Mock list action
        mock_mcp_context.request_context.app.state.document_service.list_documents = AsyncMock(
            return_value=(True, {"documents": [], "total_count": 0})
        )

        # Execute list action
        result = await document_fn(
            ctx=mock_mcp_context,
            action="list",
        )

        # CRITICAL ASSERTION
        assert isinstance(result, str), (
            f"PROTOCOL VIOLATION: manage_document returned {type(result).__name__}, "
            f"expected str (Gotcha #3)"
        )

    @pytest.mark.asyncio
    async def test_rag_manage_source_returns_string_not_dict(
        self, mock_mcp_context
    ):
        """CRITICAL: rag_manage_source must return JSON string.

        Expected:
        - ALL actions return str
        """
        from src.tools.source_tools import register_source_tools

        class MockMCP:
            def __init__(self):
                self.tools = {}
            def tool(self):
                return lambda func: (self.tools.update({func.__name__: func}), func)[1]

        mock_mcp = MockMCP()
        register_source_tools(mock_mcp)
        source_fn = mock_mcp.tools['rag_manage_source']

        # Mock list action
        mock_mcp_context.request_context.app.state.source_service.list_sources = AsyncMock(
            return_value=(True, {"sources": [], "total_count": 0})
        )

        # Execute list action
        result = await source_fn(
            ctx=mock_mcp_context,
            action="list",
        )

        # CRITICAL ASSERTION
        assert isinstance(result, str), (
            f"PROTOCOL VIOLATION: rag_manage_source returned {type(result).__name__}, "
            f"expected str (Gotcha #3)"
        )


class TestToolReturnJSONValidity:
    """Test that returned JSON strings are valid and parseable."""

    @pytest.mark.asyncio
    async def test_search_returns_valid_json(
        self, mock_mcp_context
    ):
        """Test that search_knowledge_base returns valid JSON.

        Expected:
        - String can be parsed with json.loads()
        - No JSONDecodeError
        """
        from src.tools.search_tools import register_search_tools

        class MockMCP:
            def __init__(self):
                self.tools = {}
            def tool(self):
                return lambda func: (self.tools.update({func.__name__: func}), func)[1]

        mock_mcp = MockMCP()
        register_search_tools(mock_mcp)
        search_fn = mock_mcp.tools['search_knowledge_base']

        mock_mcp_context.request_context.app.state.rag_service.search = AsyncMock(
            return_value=[]
        )

        result = await search_fn(
            ctx=mock_mcp_context,
            query="test",
        )

        # Should parse without error
        try:
            data = json.loads(result)
        except json.JSONDecodeError as e:
            pytest.fail(f"Tool returned invalid JSON: {e}\nResult: {result}")

        # Should have expected structure
        assert isinstance(data, dict), "Parsed JSON should be a dict"
        assert "success" in data, "JSON must have 'success' field"

    @pytest.mark.asyncio
    async def test_error_responses_return_valid_json(
        self, mock_mcp_context
    ):
        """Test that error responses are valid JSON strings.

        Expected:
        - Even errors return JSON strings
        - JSON has error structure
        """
        from src.tools.search_tools import register_search_tools

        class MockMCP:
            def __init__(self):
                self.tools = {}
            def tool(self):
                return lambda func: (self.tools.update({func.__name__: func}), func)[1]

        mock_mcp = MockMCP()
        register_search_tools(mock_mcp)
        search_fn = mock_mcp.tools['search_knowledge_base']

        # Execute with empty query (validation error)
        result = await search_fn(
            ctx=mock_mcp_context,
            query="",  # Empty query triggers validation error
        )

        # Should still be valid JSON string
        assert isinstance(result, str)
        data = json.loads(result)

        # Error structure
        assert data["success"] is False
        assert "error" in data
        assert "suggestion" in data


class TestPayloadOptimization:
    """Test payload optimization (Gotcha #7)."""

    @pytest.mark.asyncio
    async def test_search_truncates_text_fields(
        self, mock_mcp_context
    ):
        """Test that text fields are truncated to 1000 chars.

        Expected:
        - Long text truncated
        - Truncated text <= 1000 chars
        """
        from src.tools.search_tools import register_search_tools

        class MockMCP:
            def __init__(self):
                self.tools = {}
            def tool(self):
                return lambda func: (self.tools.update({func.__name__: func}), func)[1]

        mock_mcp = MockMCP()
        register_search_tools(mock_mcp)
        search_fn = mock_mcp.tools['search_knowledge_base']

        # Mock result with long text
        long_text = "x" * 2000
        mock_mcp_context.request_context.app.state.rag_service.search = AsyncMock(
            return_value=[
                {
                    "chunk_id": str(uuid4()),
                    "text": long_text,
                    "score": 0.95,
                    "metadata": {}
                }
            ]
        )

        result = await search_fn(
            ctx=mock_mcp_context,
            query="test",
        )

        data = json.loads(result)

        # Verify truncation
        result_text = data["results"][0]["text"]
        assert len(result_text) <= 1000, (
            f"Text field should be truncated to 1000 chars, got {len(result_text)} chars (Gotcha #7)"
        )

    @pytest.mark.asyncio
    async def test_search_limits_result_count(
        self, mock_mcp_context
    ):
        """Test that results are limited to 20 items.

        Expected:
        - Even if RAGService returns 100 results, tool returns max 20
        """
        from src.tools.search_tools import register_search_tools

        class MockMCP:
            def __init__(self):
                self.tools = {}
            def tool(self):
                return lambda func: (self.tools.update({func.__name__: func}), func)[1]

        mock_mcp = MockMCP()
        register_search_tools(mock_mcp)
        search_fn = mock_mcp.tools['search_knowledge_base']

        # Mock 100 results
        mock_results = [
            {
                "chunk_id": str(uuid4()),
                "text": f"Result {i}",
                "score": 0.9,
                "metadata": {}
            }
            for i in range(100)
        ]

        mock_mcp_context.request_context.app.state.rag_service.search = AsyncMock(
            return_value=mock_results
        )

        result = await search_fn(
            ctx=mock_mcp_context,
            query="test",
            limit=100,  # Request 100
        )

        data = json.loads(result)

        # Should be limited to 20
        assert len(data["results"]) <= 20, (
            f"Results should be limited to 20 items, got {len(data['results'])} (Gotcha #7)"
        )


class TestJSONStructureConsistency:
    """Test that JSON structure is consistent across all tools."""

    @pytest.mark.asyncio
    async def test_success_response_structure(
        self, mock_mcp_context
    ):
        """Test that successful responses have consistent structure.

        Expected structure:
        {
            "success": true,
            <tool-specific data>,
            "error": null (optional)
        }
        """
        from src.tools.search_tools import register_search_tools

        class MockMCP:
            def __init__(self):
                self.tools = {}
            def tool(self):
                return lambda func: (self.tools.update({func.__name__: func}), func)[1]

        mock_mcp = MockMCP()
        register_search_tools(mock_mcp)
        search_fn = mock_mcp.tools['search_knowledge_base']

        mock_mcp_context.request_context.app.state.rag_service.search = AsyncMock(
            return_value=[]
        )

        result = await search_fn(
            ctx=mock_mcp_context,
            query="test",
        )

        data = json.loads(result)

        # Verify structure
        assert "success" in data, "Response must have 'success' field"
        assert isinstance(data["success"], bool), "'success' must be boolean"
        assert data["success"] is True, "Successful response should have success=true"

    @pytest.mark.asyncio
    async def test_error_response_structure(
        self, mock_mcp_context
    ):
        """Test that error responses have consistent structure.

        Expected structure:
        {
            "success": false,
            "error": "Error message",
            "suggestion": "How to fix" (optional)
        }
        """
        from src.tools.search_tools import register_search_tools

        class MockMCP:
            def __init__(self):
                self.tools = {}
            def tool(self):
                return lambda func: (self.tools.update({func.__name__: func}), func)[1]

        mock_mcp = MockMCP()
        register_search_tools(mock_mcp)
        search_fn = mock_mcp.tools['search_knowledge_base']

        # Trigger validation error with empty query
        result = await search_fn(
            ctx=mock_mcp_context,
            query="",
        )

        data = json.loads(result)

        # Verify error structure
        assert "success" in data
        assert data["success"] is False
        assert "error" in data, "Error response must have 'error' field"
        assert isinstance(data["error"], str), "'error' must be string"
        assert len(data["error"]) > 0, "'error' should not be empty string"

        # Suggestion is helpful but optional
        if "suggestion" in data:
            assert isinstance(data["suggestion"], str)


class TestJSONDumpsUsage:
    """Verify that tools use json.dumps() correctly."""

    @pytest.mark.asyncio
    async def test_json_dumps_with_proper_indentation(
        self, mock_mcp_context
    ):
        """Test that JSON is pretty-printed (indented).

        Expected:
        - JSON should be readable (indented)
        - Makes debugging easier
        """
        from src.tools.search_tools import register_search_tools

        class MockMCP:
            def __init__(self):
                self.tools = {}
            def tool(self):
                return lambda func: (self.tools.update({func.__name__: func}), func)[1]

        mock_mcp = MockMCP()
        register_search_tools(mock_mcp)
        search_fn = mock_mcp.tools['search_knowledge_base']

        mock_mcp_context.request_context.app.state.rag_service.search = AsyncMock(
            return_value=[]
        )

        result = await search_fn(
            ctx=mock_mcp_context,
            query="test",
        )

        # If indented, should contain newlines
        # (optional test - indentation is nice to have but not critical)
        assert "\n" in result or len(result) < 100, (
            "JSON should be indented for readability (or very short)"
        )

    @pytest.mark.asyncio
    async def test_special_characters_escaped_correctly(
        self, mock_mcp_context
    ):
        """Test that special characters are escaped in JSON.

        Expected:
        - Quotes, newlines, etc. properly escaped
        - JSON parses correctly even with special chars
        """
        from src.tools.search_tools import register_search_tools

        class MockMCP:
            def __init__(self):
                self.tools = {}
            def tool(self):
                return lambda func: (self.tools.update({func.__name__: func}), func)[1]

        mock_mcp = MockMCP()
        register_search_tools(mock_mcp)
        search_fn = mock_mcp.tools['search_knowledge_base']

        # Mock result with special characters
        special_text = 'Text with "quotes" and\nnewlines\tand\ttabs'
        mock_mcp_context.request_context.app.state.rag_service.search = AsyncMock(
            return_value=[
                {
                    "chunk_id": str(uuid4()),
                    "text": special_text,
                    "score": 0.95,
                    "metadata": {}
                }
            ]
        )

        result = await search_fn(
            ctx=mock_mcp_context,
            query="test",
        )

        # Should parse correctly despite special chars
        try:
            data = json.loads(result)
        except json.JSONDecodeError as e:
            pytest.fail(f"JSON with special characters failed to parse: {e}")

        # Verify special chars preserved
        assert "quotes" in data["results"][0]["text"]
