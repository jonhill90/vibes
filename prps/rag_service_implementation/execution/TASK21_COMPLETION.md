# Task 5.3 Implementation Complete: manage_source Tool

## Task Information
- **Task ID**: b988bc9d-b40c-4931-8f40-f325a727cc5b
- **Task Name**: Task 5.3 - manage_source Tool
- **Responsibility**: Implement consolidated MCP tool for source CRUD operations
- **Status**: COMPLETE - Ready for Review

## Files Created/Modified

### Created Files:
1. **`/Users/jon/source/vibes/infra/rag-service/backend/src/tools/source_tools.py`** (344 lines)
   - Consolidated MCP tool for source CRUD operations
   - Implements all 5 actions: create, update, delete, get, list
   - JSON string returns per MCP protocol
   - Payload optimization with field truncation
   - Follows MCP consolidated tool pattern from examples/02_mcp_consolidated_tools.py

### Modified Files:
None - This is a new file creation task

## Implementation Details

### Core Features Implemented

#### 1. Consolidated Action Router
- Single `manage_source()` async function
- Action parameter: "create", "update", "delete", "get", "list"
- Routes to appropriate SourceService methods
- Comprehensive validation for each action

#### 2. Create Action
- Validates required `source_type` parameter
- Supports optional fields: url, status, metadata, error_message
- Default status: "pending"
- Returns created source with UUID

#### 3. Update Action
- Requires `source_id` parameter
- Supports partial updates (any combination of fields)
- Validates UUID format
- Returns updated source

#### 4. Delete Action
- Requires `source_id` parameter
- Validates UUID format
- Returns success message
- Note: Cascades to documents and chunks

#### 5. Get Action
- Requires `source_id` parameter
- Validates UUID format
- Returns single source with truncated fields
- Error handling for not found

#### 6. List Action
- Optional filters: source_type, status
- Pagination support: limit, offset
- Maximum limit: 20 items (Gotcha #7)
- Returns optimized sources array
- Includes total_count for pagination UI

#### 7. MCP Payload Optimization
- `truncate_text()`: Truncates text to 1000 chars with ellipsis
- `optimize_source_for_mcp()`: Truncates metadata and error_message fields
- Applied to all responses (single and list)
- Reduces payload size for MCP transport

### Critical Gotchas Addressed

#### Gotcha #6: MCP Tools MUST Return JSON Strings
**Implementation**: Every return statement uses `json.dumps()` to return JSON string
```python
return json.dumps({
    "success": True,
    "source": source
})
```
**Why Critical**: MCP protocol requires JSON strings, not Python dicts. Returning dicts causes protocol errors.

#### Gotcha #7: Truncate Large Fields and Limit Results
**Implementation**:
- Truncate metadata and error_message to 1000 chars max
- Limit list results to 20 items max per page
```python
MAX_FIELD_LENGTH = 1000
MAX_SOURCES_PER_PAGE = 20

def optimize_source_for_mcp(source: dict) -> dict:
    # Truncate metadata (convert to string first)
    metadata_str = json.dumps(source["metadata"])
    source["metadata"] = truncate_text(metadata_str)

    # Truncate error_message
    source["error_message"] = truncate_text(source["error_message"])
```
**Why Critical**: Large payloads slow MCP transport and cause timeouts. 1000 chars is sufficient for debugging while keeping performance high.

#### Gotcha #3: asyncpg Uses $1, $2 Placeholders (Not %s)
**Implementation**: Delegated to SourceService which handles asyncpg correctly
```python
# SourceService already uses correct placeholder syntax
await source_service.create_source(source_data)
```
**Why Critical**: Using %s placeholders causes asyncpg syntax errors.

#### Gotcha #8: Always Use async with pool.acquire()
**Implementation**: Delegated to SourceService which uses async context managers
```python
# SourceService already uses correct connection management
async with self.db_pool.acquire() as conn:
    row = await conn.fetchrow(query, *params)
```
**Why Critical**: Not using async with causes connection leaks and pool exhaustion.

## Dependencies Verified

### Completed Dependencies:
- **Task 3.2 (SourceService)**: Service exists with all CRUD methods
  - `create_source()` - Validated
  - `get_source()` - Validated
  - `list_sources()` - Validated with exclude_large_fields parameter
  - `update_source()` - Validated
  - `delete_source()` - Validated
- **Database Connection Pool**: get_pool() available for service initialization
- **MCP Consolidated Tool Pattern**: examples/02_mcp_consolidated_tools.py studied and followed

### External Dependencies:
- `json` (Python stdlib): JSON string serialization
- `logging` (Python stdlib): Error logging
- `typing` (Python stdlib): Type hints
- `uuid.UUID` (Python stdlib): UUID validation
- `SourceService`: Database operations (from ../services/source_service.py)
- `get_pool()`: Database pool accessor (from ../database.py)

## Testing Checklist

### Manual Testing (When MCP Server Running):
- [ ] Create source: `manage_source("create", source_type="upload", url="https://example.com")`
- [ ] Get source: `manage_source("get", source_id="<uuid>")`
- [ ] List all sources: `manage_source("list")`
- [ ] List filtered sources: `manage_source("list", source_type="upload", status="completed")`
- [ ] Update source: `manage_source("update", source_id="<uuid>", status="completed")`
- [ ] Delete source: `manage_source("delete", source_id="<uuid>")`
- [ ] Verify JSON string returns (not dicts)
- [ ] Verify metadata truncation for large payloads
- [ ] Verify list pagination (max 20 items)
- [ ] Verify error messages for invalid inputs

### Validation Results:
- **Syntax Check**: Passed (py_compile)
- **Pattern Match**: Mirrors manage_task pattern from examples/02_mcp_consolidated_tools.py
- **All Actions Implemented**: create, update, delete, get, list (5/5)
- **JSON String Returns**: All return statements use json.dumps() (Gotcha #6)
- **Field Truncation**: optimize_source_for_mcp() applied (Gotcha #7)
- **Pagination Limit**: MAX_SOURCES_PER_PAGE = 20 enforced (Gotcha #7)
- **UUID Validation**: try/except blocks for UUID parsing
- **Error Handling**: Comprehensive try/except with logging
- **Service Integration**: Correctly calls SourceService methods

## Success Metrics

**All PRP Requirements Met**:
- [x] Create async function manage_source(action, source_id, **kwargs) -> str
- [x] Validate action: "create", "update", "delete", "get", "list"
- [x] Route to SourceService methods
- [x] Truncate metadata/error_message to 1000 chars (Gotcha #7)
- [x] Limit list to 20 items max (Gotcha #7)
- [x] Return JSON string (Gotcha #6)
- [x] Mirror structure from examples/02_mcp_consolidated_tools.py
- [x] Follow SourceService method signatures
- [x] Comprehensive error handling
- [x] UUID validation for source_id parameters

**Code Quality**:
- Comprehensive docstrings (module, functions, critical gotchas)
- Type hints for all function parameters and returns
- Logging for all errors with exc_info=True
- Clear error messages with suggestions
- Comments explaining critical gotchas
- Consistent code style (matches codebase patterns)
- No syntax errors (validated)
- Follows PEP 8 conventions

## Completion Report

**Status**: COMPLETE - Ready for Review
**Implementation Time**: ~25 minutes
**Confidence Level**: HIGH
**Blockers**: None

### Files Created: 1
### Files Modified: 0
### Total Lines of Code: ~344 lines

**Ready for integration and next steps.**

---

## Next Steps

1. **Task 5.4**: Implement MCP server entry point (mcp_server.py) to register this tool
2. **Integration Testing**: Test tool via MCP protocol with FastMCP server
3. **Unit Tests**: Create test_source_tools.py with AsyncMock for service methods
4. **Documentation**: Add to MCP tools reference documentation

## Notes

- Tool follows exact same pattern as manage_task from examples/02_mcp_consolidated_tools.py
- All critical gotchas from PRP explicitly addressed in code comments
- Service layer (SourceService) already implements database optimization (exclude_large_fields)
- Tool adds additional optimization layer for extra safety (optimize_source_for_mcp)
- UUID validation prevents asyncpg parameter binding errors
- Comprehensive error messages guide agent usage (suggestion field in error responses)
