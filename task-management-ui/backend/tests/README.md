# MCP Integration Tests

## Overview

This directory contains end-to-end integration tests for the MCP (Model Context Protocol) server tools.

## Test Coverage

### `test_mcp.py` - MCP Tool Validation (13 tests)

#### Critical MCP Requirements (Gotcha #3)
1. **test_find_tasks_returns_json_string** - Validates tools return JSON strings, not dicts
2. **test_find_tasks_respects_per_page_limit** - Ensures per_page limited to MAX_TASKS_PER_PAGE (20)
3. **test_description_truncation_works** - Verifies descriptions truncated to 1000 chars
4. **test_response_size_under_100kb** - Validates response size optimization

#### find_tasks() Tool Tests
5. **test_find_tasks_with_task_id_returns_single_task** - Single task GET mode
6. **test_find_tasks_with_filters** - Filter by status/project/assignee
7. **test_find_tasks_handles_exceptions** - Exception handling and error structure

#### manage_task() Tool Tests
8. **test_manage_task_create_action** - Task creation with all fields
9. **test_manage_task_create_requires_project_and_title** - Required field validation
10. **test_manage_task_update_action** - Partial task updates
11. **test_manage_task_delete_action** - Task deletion
12. **test_manage_task_handles_exceptions** - Exception handling

#### Error Response Format
13. **test_error_responses_have_structured_format** - Validates {success, error, suggestion} structure

## Running Tests

### Prerequisites

Install dependencies:
```bash
# Using uv (recommended)
uv sync --group dev

# Or using pip
pip install -e ".[dev]"
```

### Run All MCP Tests

```bash
# Run all MCP tests with verbose output
pytest tests/test_mcp.py -v

# Run with coverage
pytest tests/test_mcp.py --cov=src.mcp_server --cov-report=term-missing

# Run specific test
pytest tests/test_mcp.py::test_find_tasks_returns_json_string -v
```

### Expected Output

All 13 tests should pass:
```
tests/test_mcp.py::test_find_tasks_returns_json_string PASSED
tests/test_mcp.py::test_find_tasks_with_task_id_returns_single_task PASSED
tests/test_mcp.py::test_find_tasks_with_filters PASSED
tests/test_mcp.py::test_find_tasks_respects_per_page_limit PASSED
tests/test_mcp.py::test_manage_task_create_action PASSED
tests/test_mcp.py::test_manage_task_create_requires_project_and_title PASSED
tests/test_mcp.py::test_manage_task_update_action PASSED
tests/test_mcp.py::test_manage_task_delete_action PASSED
tests/test_error_responses_have_structured_format PASSED
tests/test_description_truncation_works PASSED
tests/test_response_size_under_100kb PASSED
tests/test_find_tasks_handles_exceptions PASSED
tests/test_manage_task_handles_exceptions PASSED

========================= 13 passed in X.XXs =========================
```

## Test Patterns

### Mocking Strategy

Tests use pytest mocks to avoid database dependencies:
- `mock_db_pool` - Mocks database connection pool
- `mock_task_service` - Mocks TaskService with configurable responses
- `patch("src.mcp_server.get_pool")` - Patches async pool getter
- `patch("src.mcp_server.TaskService")` - Patches service class

### Accessing MCP Tools

Tools are accessed from the FastMCP instance:
```python
find_tasks = None
for tool in mcp._tools:
    if tool.fn.__name__ == "find_tasks":
        find_tasks = tool.fn
        break

result = await find_tasks(task_id="task-123")
```

### Validating JSON String Responses

All MCP tools MUST return JSON strings:
```python
# Verify it's a string
assert isinstance(result, str), "MCP tools must return JSON strings, not dicts"

# Parse and validate structure
parsed = json.loads(result)
assert "success" in parsed
assert parsed["success"] is True
```

## Critical Gotchas Addressed

### Gotcha #3: MCP Response Format
- **Issue**: MCP tools must return JSON strings, not Python dicts
- **Solution**: All tools use `json.dumps()` to serialize responses
- **Test**: `test_find_tasks_returns_json_string`

### Gotcha #3: Description Truncation
- **Issue**: Large descriptions cause oversized MCP responses
- **Solution**: Truncate descriptions to 1000 chars with "..." suffix
- **Test**: `test_description_truncation_works`

### Gotcha #3: Pagination Limits
- **Issue**: Requesting too many tasks can exceed MCP size limits
- **Solution**: Limit per_page to MAX_TASKS_PER_PAGE (20)
- **Test**: `test_find_tasks_respects_per_page_limit`

### Structured Error Responses
- **Issue**: Errors need consistent format for AI consumption
- **Solution**: All errors return {success: false, error: "...", suggestion: "..."}
- **Test**: `test_error_responses_have_structured_format`

## Validation Checklist

Before merging MCP changes, verify:
- [ ] All 13 tests pass
- [ ] Tools return JSON strings (not dicts)
- [ ] Descriptions truncated to 1000 chars
- [ ] per_page limited to 20
- [ ] Error responses have structured format
- [ ] Response sizes < 100KB for max page
- [ ] Exception handling works correctly

## Reference Documentation

- PRP Task 23: `prps/task_management_ui.md` (lines 1953-1976)
- MCP Implementation: `src/mcp_server.py`
- Service Layer: `src/services/task_service.py`
- Archon MCP Tests: `infra/archon/python/tests/mcp_server/features/tasks/test_task_tools.py`
