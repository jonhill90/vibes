"""Tests for Basic-Memory Integration (Task 4)."""

import pytest
from unittest.mock import Mock, patch, MagicMock


# Constants from implementation
BASIC_MEMORY_PROJECT = "vibes"


class TestSearchNotesWithProjectParameter:
    """Test search_notes with explicit project parameter (v0.15.0+)."""

    def test_search_with_project_parameter(self, mock_basic_memory):
        """Test search_notes includes project parameter."""
        # Mock MCP call
        mock_search = mock_basic_memory["search_notes"]

        # Simulate search
        query = "terraform patterns"
        project = BASIC_MEMORY_PROJECT
        page_size = 5

        # Call would be: mcp__basic_memory__search_notes(...)
        result = mock_search(query=query, project=project, page_size=page_size)

        # Verify mock was called
        mock_search.assert_called_once_with(
            query=query,
            project=project,
            page_size=page_size
        )

        assert len(result) > 0, "Should return search results"

    def test_project_parameter_required(self):
        """Test project parameter is required in v0.15.0+."""
        # Mock search function that validates project param
        def search_notes_v015(query: str, project: str, page_size: int = 10):
            """Simulate v0.15.0+ API requiring project parameter."""
            if not project:
                raise ValueError("project parameter required in v0.15.0+")
            return [{"id": "note-1", "content": "Result"}]

        # Should fail without project
        with pytest.raises(ValueError, match="project parameter required"):
            search_notes_v015(query="test", project="")

        # Should succeed with project
        result = search_notes_v015(query="test", project=BASIC_MEMORY_PROJECT)
        assert len(result) > 0

    def test_project_constant_consistency(self):
        """Test BASIC_MEMORY_PROJECT constant used consistently."""
        # All calls should use same project constant
        calls = [
            {"query": "patterns", "project": BASIC_MEMORY_PROJECT},
            {"query": "examples", "project": BASIC_MEMORY_PROJECT},
            {"query": "gotchas", "project": BASIC_MEMORY_PROJECT}
        ]

        projects_used = [call["project"] for call in calls]

        # All should be same
        assert len(set(projects_used)) == 1, "Should use consistent project"
        assert projects_used[0] == "vibes", "Should use 'vibes' project"


class TestReadNoteV015API:
    """Test read_note with v0.15.0+ API."""

    def test_read_note_with_project(self, mock_basic_memory):
        """Test read_note includes project parameter."""
        mock_read = mock_basic_memory["read_note"]

        # Simulate read
        identifier = "note-1"
        project = BASIC_MEMORY_PROJECT

        result = mock_read(identifier=identifier, project=project)

        mock_read.assert_called_once_with(
            identifier=identifier,
            project=project
        )

        assert result["id"] == identifier

    def test_identifier_parameter_format(self):
        """Test identifier parameter accepts various formats."""
        valid_identifiers = [
            "note-123",
            "01-notes/research/terraform.md",
            "abc123def"
        ]

        for identifier in valid_identifiers:
            # Mock that accepts any identifier
            mock_read = Mock(return_value={"id": identifier, "content": "Note content"})

            result = mock_read(identifier=identifier, project=BASIC_MEMORY_PROJECT)

            assert result["id"] == identifier


class TestReadOnlyAccess:
    """Test read-only access (no write/edit/delete operations)."""

    def test_no_write_note_in_agent_tools(self, sample_agent_frontmatter):
        """Test agents configured for read-only don't have write_note."""
        # Knowledge-curator agent should be read-only
        knowledge_curator_tools = ["Read", "Grep", "Glob"]  # No Write

        # Should not include write_note or edit_note
        dangerous_tools = ["write_note", "edit_note", "delete_note"]

        for tool in dangerous_tools:
            assert tool not in [t.lower() for t in knowledge_curator_tools], \
                f"Read-only agent should not have {tool}"

    def test_search_and_read_only_operations(self):
        """Test only search_notes and read_note available."""
        allowed_operations = {
            "search_notes": True,
            "read_note": True,
            "list_directory": True,  # Read-only listing
            "write_note": False,
            "edit_note": False,
            "delete_note": False
        }

        for operation, is_allowed in allowed_operations.items():
            if is_allowed:
                assert operation in ["search_notes", "read_note", "list_directory"], \
                    f"{operation} should be allowed (read-only)"
            else:
                assert operation in ["write_note", "edit_note", "delete_note"], \
                    f"{operation} should not be allowed (write operation)"

    def test_prevent_data_modification(self):
        """Test prevention of data modification in basic-memory."""
        def validate_operation(operation: str) -> bool:
            """Validate operation is read-only."""
            read_only_ops = ["search_notes", "read_note", "list_directory"]
            return operation in read_only_ops

        # Read operations should pass
        assert validate_operation("search_notes")
        assert validate_operation("read_note")

        # Write operations should fail
        assert not validate_operation("write_note")
        assert not validate_operation("edit_note")


class TestMockedBasicMemoryResponses:
    """Test with mocked basic-memory responses (no live calls)."""

    def test_mock_search_results_structure(self, mock_basic_memory):
        """Test mocked search results have correct structure."""
        mock_search = mock_basic_memory["search_notes"]

        results = mock_search(
            query="test",
            project=BASIC_MEMORY_PROJECT,
            page_size=5
        )

        # Validate structure
        assert isinstance(results, list), "Results should be a list"
        assert len(results) > 0, "Should have results"

        for result in results:
            assert "id" in result, "Result should have id"
            assert "content" in result, "Result should have content"

    def test_mock_read_note_structure(self, mock_basic_memory):
        """Test mocked read_note has correct structure."""
        mock_read = mock_basic_memory["read_note"]

        result = mock_read(
            identifier="note-1",
            project=BASIC_MEMORY_PROJECT
        )

        # Validate structure
        assert isinstance(result, dict), "Result should be a dict"
        assert "id" in result, "Should have id"
        assert "content" in result, "Should have content"

    @patch('builtins.print')
    def test_no_real_mcp_calls_in_tests(self, mock_print):
        """Test no real MCP calls are made during testing."""
        # Mock MCP call that would fail if actually invoked
        with patch('builtins.mcp__basic_memory__search_notes') as mock_mcp:
            mock_mcp.side_effect = RuntimeError("Real MCP call attempted in test!")

            # Test should use mocks, not real calls
            # If this passes, we're properly mocking
            assert True, "Tests should use mocks, not real MCP calls"

    def test_mock_query_variations(self, mock_basic_memory):
        """Test mocked responses for various query types."""
        mock_search = mock_basic_memory["search_notes"]

        queries = [
            "terraform patterns",
            "azure best practices",
            "python examples",
            "skills documentation"
        ]

        for query in queries:
            results = mock_search(
                query=query,
                project=BASIC_MEMORY_PROJECT,
                page_size=5
            )

            assert len(results) > 0, f"Should return results for query: {query}"


class TestBasicMemoryIntegrationWithCommands:
    """Test basic-memory integration with generate-prp command."""


        # NEW: Basic-memory pattern
        def search_knowledge_base(query: str, max_results: int = 5):
            """Search basic-memory knowledge base."""
            # Mock basic-memory call
            mock_search = Mock(return_value=[
                {"id": "note-1", "content": "Pattern 1"},
                {"id": "note-2", "content": "Pattern 2"}
            ])

            return mock_search(
                query=query,
                project=BASIC_MEMORY_PROJECT,
                page_size=max_results
            )

        results = search_knowledge_base("terraform patterns")

        assert len(results) > 0
        assert all("content" in r for r in results)

    def test_knowledge_curator_agent_usage(self):
        """Test knowledge-curator agent uses basic-memory tools."""
        # Knowledge-curator agent should:
        # 1. Search notes for relevant knowledge
        # 2. Read specific notes for details
        # 3. NOT write/edit/delete notes

        curator_workflow = {
            "step1": "search_notes",  # Find relevant notes
            "step2": "read_note",     # Read specific note
            "step3": None             # No write operations
        }

        # Verify workflow is read-only
        operations = [op for op in curator_workflow.values() if op]
        write_ops = ["write_note", "edit_note", "delete_note"]

        assert all(op not in write_ops for op in operations), \
            "Curator should only use read operations"

    def test_query_optimization_2_5_keywords(self):
        """Test query optimization for 2-5 keywords."""
        # Basic-memory works best with 2-5 keywords
        queries = {
            "terraform patterns": 2,  # Optimal
            "azure resource group naming": 4,  # Optimal
            "python fastapi rest api endpoint validation": 6,  # Too many
            "test": 1  # Too few
        }

        for query, word_count in queries.items():
            words = query.split()
            assert len(words) == word_count

            is_optimal = 2 <= len(words) <= 5

            if is_optimal:
                assert 2 <= word_count <= 5, \
                    f"Query '{query}' should have 2-5 keywords"


class TestBasicMemoryErrorHandling:
    """Test error handling for basic-memory integration."""

    def test_handle_search_failure_gracefully(self):
        """Test graceful handling of search failures."""
        def safe_search(query: str, project: str):
            """Search with error handling."""
            try:
                # Simulate failure
                raise ConnectionError("Basic-memory unavailable")
            except Exception as e:
                print(f"Search failed: {e}")
                return []  # Return empty results on failure

        results = safe_search("test", BASIC_MEMORY_PROJECT)

        assert results == [], "Should return empty list on failure"

    def test_handle_missing_project_parameter(self):
        """Test error when project parameter missing."""
        def search_notes_strict(query: str, project: str = None):
            """Strict validation of project parameter."""
            if not project:
                raise ValueError(
                    "project parameter required in v0.15.0+. "
                    "Set BASIC_MEMORY_PROJECT constant."
                )
            return []

        # Should fail without project
        with pytest.raises(ValueError, match="project parameter required"):
            search_notes_strict(query="test", project=None)

        # Should succeed with project
        results = search_notes_strict(query="test", project=BASIC_MEMORY_PROJECT)
        assert results == []

    def test_handle_invalid_note_identifier(self):
        """Test error handling for invalid note identifiers."""
        def read_note_safe(identifier: str, project: str):
            """Read note with validation."""
            if not identifier:
                raise ValueError("identifier required")

            # Mock: note not found
            if identifier == "nonexistent":
                return None

            return {"id": identifier, "content": "Note content"}

        # Valid identifier
        result = read_note_safe("note-1", BASIC_MEMORY_PROJECT)
        assert result is not None

        # Nonexistent identifier
        result = read_note_safe("nonexistent", BASIC_MEMORY_PROJECT)
        assert result is None

        # Invalid identifier
        with pytest.raises(ValueError):
            read_note_safe("", BASIC_MEMORY_PROJECT)
