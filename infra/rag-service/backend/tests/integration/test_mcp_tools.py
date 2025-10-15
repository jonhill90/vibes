"""Integration tests for MCP tools with JSON string validation.

Tests cover (PRP Task 8 requirements):
1. All MCP tools return JSON strings (NOT dicts) - Gotcha #3
2. Payload truncation (<1000 chars per field, max 20 items) - Gotcha #7
3. Error responses have correct structure
4. Tools are callable from MCP context
5. End-to-end tool functionality

Pattern: pytest-asyncio with mocked services
Reference: prps/rag_service_completion.md (Task 8, lines 1349-1361)
"""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

# Import MCP tool modules
from src.tools import search_tools, document_tools, source_tools


class TestSearchToolsJSONValidation:
    """Tests for search_knowledge_base JSON string returns (Gotcha #3)."""

    @pytest.mark.asyncio
    async def test_search_knowledge_base_returns_json_string(
        self, mock_mcp_context, sample_embedding
    ):
        """Test that search_knowledge_base returns JSON string, NOT dict.

        CRITICAL: MCP protocol requires JSON strings (Gotcha #3).

        Expected:
        - Return type is str
        - String is valid JSON
        - Parsed JSON has expected structure
        """
        # Register tools
        mcp = MagicMock()
        mcp.tool = lambda: lambda func: func  # Passthrough decorator
        search_tools.register_search_tools(mcp)

        # Get the tool function
        search_fn = search_tools.register_search_tools.__wrapped__

        # Mock RAGService.search to return results
        mock_results = [
            {
                "chunk_id": str(uuid4()),
                "text": "Test content " * 100,  # Long text for truncation test
                "score": 0.95,
                "metadata": {"title": "Test Document"}
            }
        ]

        mock_mcp_context.request_context.app.state.rag_service.search = AsyncMock(
            return_value=mock_results
        )

        # Call tool
        # Need to get the actual decorated function
        # Since we can't easily introspect the decorator, we'll test the function directly
        from src.tools.search_tools import register_search_tools

        # Create a mock MCP instance
        class MockMCP:
            def __init__(self):
                self.tools = {}

            def tool(self):
                def decorator(func):
                    self.tools[func.__name__] = func
                    return func
                return decorator

        mock_mcp_instance = MockMCP()
        register_search_tools(mock_mcp_instance)

        # Get the registered tool
        search_tool_fn = mock_mcp_instance.tools['search_knowledge_base']

        # Execute tool with mock context
        result = await search_tool_fn(
            ctx=mock_mcp_context,
            query="test query",
            search_type="vector",
            limit=10,
        )

        # CRITICAL: Verify return type is string
        assert isinstance(result, str), (
            f"MCP tool MUST return JSON string, got {type(result)}. "
            "This violates Gotcha #3 and breaks MCP protocol!"
        )

        # Verify string is valid JSON
        try:
            data = json.loads(result)
        except json.JSONDecodeError as e:
            pytest.fail(f"Tool returned invalid JSON: {e}")

        # Verify JSON structure
        assert "success" in data
        assert "results" in data
        assert "count" in data
        assert "search_type" in data
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_search_truncates_content_to_1000_chars(
        self, mock_mcp_context
    ):
        """Test that search results truncate content to 1000 chars (Gotcha #7).

        Expected:
        - Long text fields truncated to 1000 chars
        - Truncation indicated with "..."
        """
        # Mock long content
        long_text = "x" * 2000
        mock_results = [
            {
                "chunk_id": str(uuid4()),
                "text": long_text,
                "score": 0.95,
                "metadata": {}
            }
        ]

        mock_mcp_context.request_context.app.state.rag_service.search = AsyncMock(
            return_value=mock_results
        )

        # Register and get tool
        class MockMCP:
            def __init__(self):
                self.tools = {}
            def tool(self):
                return lambda func: (self.tools.update({func.__name__: func}), func)[1]

        mock_mcp_instance = MockMCP()
        search_tools.register_search_tools(mock_mcp_instance)
        search_tool_fn = mock_mcp_instance.tools['search_knowledge_base']

        # Execute
        result = await search_tool_fn(
            ctx=mock_mcp_context,
            query="test query",
            limit=10,
        )

        data = json.loads(result)

        # Verify truncation
        result_text = data["results"][0]["text"]
        assert len(result_text) <= 1000, "Text should be truncated to 1000 chars"
        assert result_text.endswith("..."), "Truncated text should end with ..."

    @pytest.mark.asyncio
    async def test_search_limits_results_to_20_items(
        self, mock_mcp_context
    ):
        """Test that search limits results to 20 items max (Gotcha #7).

        Expected:
        - Even if limit=100, only 20 results returned
        - Payload optimization for MCP protocol
        """
        # Mock 100 results
        mock_results = [
            {
                "chunk_id": str(uuid4()),
                "text": f"Result {i}",
                "score": 0.9 - (i * 0.01),
                "metadata": {}
            }
            for i in range(100)
        ]

        mock_mcp_context.request_context.app.state.rag_service.search = AsyncMock(
            return_value=mock_results
        )

        # Register and get tool
        class MockMCP:
            def __init__(self):
                self.tools = {}
            def tool(self):
                return lambda func: (self.tools.update({func.__name__: func}), func)[1]

        mock_mcp_instance = MockMCP()
        search_tools.register_search_tools(mock_mcp_instance)
        search_tool_fn = mock_mcp_instance.tools['search_knowledge_base']

        # Execute with limit=100
        result = await search_tool_fn(
            ctx=mock_mcp_context,
            query="test query",
            limit=100,  # Request 100 results
        )

        data = json.loads(result)

        # Verify limited to 20
        assert len(data["results"]) <= 20, "Results should be limited to 20 items"

    @pytest.mark.asyncio
    async def test_search_empty_query_returns_error_json_string(
        self, mock_mcp_context
    ):
        """Test that validation errors return JSON strings with error structure.

        Expected:
        - Empty query validation fails
        - Returns JSON string (not exception)
        - Has error and suggestion fields
        """
        # Register and get tool
        class MockMCP:
            def __init__(self):
                self.tools = {}
            def tool(self):
                return lambda func: (self.tools.update({func.__name__: func}), func)[1]

        mock_mcp_instance = MockMCP()
        search_tools.register_search_tools(mock_mcp_instance)
        search_tool_fn = mock_mcp_instance.tools['search_knowledge_base']

        # Execute with empty query
        result = await search_tool_fn(
            ctx=mock_mcp_context,
            query="",  # Empty query
            limit=10,
        )

        # Verify JSON string returned
        assert isinstance(result, str)
        data = json.loads(result)

        # Verify error structure
        assert data["success"] is False
        assert "error" in data
        assert "suggestion" in data
        assert "Query cannot be empty" in data["error"]


class TestDocumentToolsJSONValidation:
    """Tests for manage_document JSON string returns (Gotcha #3)."""

    @pytest.mark.asyncio
    async def test_manage_document_returns_json_string(
        self, mock_mcp_context
    ):
        """Test that manage_document returns JSON string.

        Expected:
        - All actions return JSON strings
        - Parsed JSON has correct structure
        """
        # Mock ingestion service
        mock_ingestion_result = {
            "document_id": str(uuid4()),
            "chunks_stored": 10,
            "chunks_failed": 0,
            "total_chunks": 10,
            "ingestion_time_ms": 1500,
            "message": "Document created successfully"
        }

        mock_mcp_context.request_context.app.state.ingestion_service.ingest_document = AsyncMock(
            return_value=(True, mock_ingestion_result)
        )

        # Register and get tool
        class MockMCP:
            def __init__(self):
                self.tools = {}
            def tool(self):
                return lambda func: (self.tools.update({func.__name__: func}), func)[1]

        mock_mcp_instance = MockMCP()
        document_tools.register_document_tools(mock_mcp_instance)
        document_tool_fn = mock_mcp_instance.tools['manage_document']

        # Execute create action
        result = await document_tool_fn(
            ctx=mock_mcp_context,
            action="create",
            title="Test Document",
            source_id=str(uuid4()),
            file_path="/tmp/test.pdf",
        )

        # CRITICAL: Verify JSON string
        assert isinstance(result, str), "manage_document must return JSON string"
        data = json.loads(result)
        assert data["success"] is True
        assert "document_id" in data

    @pytest.mark.asyncio
    async def test_manage_document_list_truncates_payload(
        self, mock_mcp_context
    ):
        """Test that list action truncates documents (Gotcha #7).

        Expected:
        - per_page limited to 20 max
        - Document metadata minimized
        """
        # Mock 50 documents
        mock_documents = [
            {
                "id": str(uuid4()),
                "title": f"Document {i}" * 100,  # Long title
                "source_id": str(uuid4()),
                "document_type": "pdf",
                "metadata": {
                    "large_field": "x" * 5000,
                    "author": "Test Author",
                },
                "created_at": "2025-10-14T10:00:00",
            }
            for i in range(50)
        ]

        mock_mcp_context.request_context.app.state.document_service.list_documents = AsyncMock(
            return_value=(True, {
                "documents": mock_documents,
                "total_count": 50
            })
        )

        # Register and get tool
        class MockMCP:
            def __init__(self):
                self.tools = {}
            def tool(self):
                return lambda func: (self.tools.update({func.__name__: func}), func)[1]

        mock_mcp_instance = MockMCP()
        document_tools.register_document_tools(mock_mcp_instance)
        document_tool_fn = mock_mcp_instance.tools['manage_document']

        # Execute list with high per_page
        result = await document_tool_fn(
            ctx=mock_mcp_context,
            action="list",
            page=1,
            per_page=50,  # Request 50 items
        )

        data = json.loads(result)

        # Verify limited to 20
        assert data["per_page"] <= 20, "per_page should be limited to 20"

        # Verify each document is optimized
        for doc in data["documents"]:
            if "title" in doc:
                assert len(doc["title"]) <= 1000, "Title should be truncated"


class TestSourceToolsJSONValidation:
    """Tests for rag_manage_source JSON string returns (Gotcha #3)."""

    @pytest.mark.asyncio
    async def test_rag_manage_source_returns_json_string(
        self, mock_mcp_context
    ):
        """Test that rag_manage_source returns JSON string.

        Expected:
        - All actions return JSON strings
        - Correct structure for create action
        """
        # Mock source service
        mock_source = {
            "id": str(uuid4()),
            "source_type": "upload",
            "url": None,
            "status": "completed",
            "created_at": "2025-10-14T10:00:00",
        }

        mock_mcp_context.request_context.app.state.source_service.create_source = AsyncMock(
            return_value=(True, {"source": mock_source})
        )

        # Register and get tool
        class MockMCP:
            def __init__(self):
                self.tools = {}
            def tool(self):
                return lambda func: (self.tools.update({func.__name__: func}), func)[1]

        mock_mcp_instance = MockMCP()
        source_tools.register_source_tools(mock_mcp_instance)
        source_tool_fn = mock_mcp_instance.tools['rag_manage_source']

        # Execute create action
        result = await source_tool_fn(
            ctx=mock_mcp_context,
            action="create",
            source_type="upload",
        )

        # CRITICAL: Verify JSON string
        assert isinstance(result, str), "rag_manage_source must return JSON string"
        data = json.loads(result)
        assert data["success"] is True
        assert "source" in data


class TestMCPToolsErrorHandling:
    """Tests for MCP tool error handling and validation."""

    @pytest.mark.asyncio
    async def test_search_invalid_search_type_returns_error_json(
        self, mock_mcp_context
    ):
        """Test invalid search_type parameter returns error JSON string.

        Expected:
        - success: false
        - error message describes invalid type
        - suggestion provides valid options
        """
        # Register and get tool
        class MockMCP:
            def __init__(self):
                self.tools = {}
            def tool(self):
                return lambda func: (self.tools.update({func.__name__: func}), func)[1]

        mock_mcp_instance = MockMCP()
        search_tools.register_search_tools(mock_mcp_instance)
        search_tool_fn = mock_mcp_instance.tools['search_knowledge_base']

        # Execute with invalid search_type
        result = await search_tool_fn(
            ctx=mock_mcp_context,
            query="test query",
            search_type="invalid_type",  # Invalid
        )

        data = json.loads(result)

        assert data["success"] is False
        assert "Invalid search_type" in data["error"]
        assert "suggestion" in data
        assert "vector" in data["suggestion"] or "hybrid" in data["suggestion"]

    @pytest.mark.asyncio
    async def test_manage_document_invalid_uuid_returns_error_json(
        self, mock_mcp_context
    ):
        """Test invalid UUID returns error JSON string.

        Expected:
        - success: false
        - error describes invalid UUID format
        """
        # Register and get tool
        class MockMCP:
            def __init__(self):
                self.tools = {}
            def tool(self):
                return lambda func: (self.tools.update({func.__name__: func}), func)[1]

        mock_mcp_instance = MockMCP()
        document_tools.register_document_tools(mock_mcp_instance)
        document_tool_fn = mock_mcp_instance.tools['manage_document']

        # Execute get with invalid UUID
        result = await document_tool_fn(
            ctx=mock_mcp_context,
            action="get",
            document_id="not-a-uuid",  # Invalid UUID
        )

        data = json.loads(result)

        assert data["success"] is False
        assert "Invalid document_id format" in data["error"]
        assert "UUID" in data["suggestion"]

    @pytest.mark.asyncio
    async def test_manage_document_missing_required_fields_returns_error(
        self, mock_mcp_context
    ):
        """Test missing required fields returns error JSON.

        Expected:
        - success: false
        - error describes missing fields
        - suggestion lists required fields
        """
        # Register and get tool
        class MockMCP:
            def __init__(self):
                self.tools = {}
            def tool(self):
                return lambda func: (self.tools.update({func.__name__: func}), func)[1]

        mock_mcp_instance = MockMCP()
        document_tools.register_document_tools(mock_mcp_instance)
        document_tool_fn = mock_mcp_instance.tools['manage_document']

        # Execute create with missing required fields
        result = await document_tool_fn(
            ctx=mock_mcp_context,
            action="create",
            # Missing: title, source_id, file_path
        )

        data = json.loads(result)

        assert data["success"] is False
        assert "required" in data["error"].lower()


class TestMCPToolsIntegration:
    """Integration tests for MCP tools end-to-end functionality."""

    @pytest.mark.asyncio
    async def test_search_to_document_workflow(
        self, mock_mcp_context
    ):
        """Test complete workflow: search → get document → view content.

        Scenario:
        1. Search for "authentication"
        2. Get first result's document_id
        3. Use manage_document to get full document

        Expected:
        - All steps return JSON strings
        - Data flows correctly between tools
        """
        # Setup mocks
        mock_search_results = [
            {
                "chunk_id": str(uuid4()),
                "document_id": str(uuid4()),
                "text": "Authentication guide content",
                "score": 0.95,
                "metadata": {"title": "Auth Guide"}
            }
        ]

        mock_document = {
            "id": mock_search_results[0]["document_id"],
            "title": "Authentication Guide",
            "source_id": str(uuid4()),
            "document_type": "pdf",
            "created_at": "2025-10-14T10:00:00",
        }

        mock_mcp_context.request_context.app.state.rag_service.search = AsyncMock(
            return_value=mock_search_results
        )
        mock_mcp_context.request_context.app.state.document_service.get_document = AsyncMock(
            return_value=(True, {"document": mock_document})
        )

        # Register tools
        class MockMCP:
            def __init__(self):
                self.tools = {}
            def tool(self):
                return lambda func: (self.tools.update({func.__name__: func}), func)[1]

        mock_mcp_instance = MockMCP()
        search_tools.register_search_tools(mock_mcp_instance)
        document_tools.register_document_tools(mock_mcp_instance)

        search_fn = mock_mcp_instance.tools['search_knowledge_base']
        document_fn = mock_mcp_instance.tools['manage_document']

        # Step 1: Search
        search_result_str = await search_fn(
            ctx=mock_mcp_context,
            query="authentication",
        )

        search_data = json.loads(search_result_str)
        assert search_data["success"] is True
        document_id = search_data["results"][0]["document_id"]

        # Step 2: Get document
        doc_result_str = await document_fn(
            ctx=mock_mcp_context,
            action="get",
            document_id=document_id,
        )

        doc_data = json.loads(doc_result_str)
        assert doc_data["success"] is True
        assert doc_data["document"]["id"] == document_id
        assert doc_data["document"]["title"] == "Authentication Guide"
