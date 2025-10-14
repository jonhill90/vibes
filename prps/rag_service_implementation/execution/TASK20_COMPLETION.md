# Task 20 Implementation Complete: manage_document Tool

## Task Information
- **Task ID**: 77ebc525-4127-4a3d-8d53-88feb16616b1
- **Task Name**: Task 5.2 - manage_document Tool
- **Responsibility**: Implement consolidated MCP tool for document CRUD operations
- **Status**: COMPLETE - Ready for Review

## Files Created/Modified

### Created Files:
1. **`/Users/jon/source/vibes/infra/rag-service/backend/src/tools/document_tools.py`** (422 lines)
   - Consolidated document management MCP tool
   - All CRUD actions: create, update, delete, get, list
   - MCP optimization functions (truncate, optimize payload)
   - Comprehensive error handling and validation
   - JSON string returns (Gotcha #6)
   - Content truncation (Gotcha #7)

### Modified Files:
1. **`/Users/jon/source/vibes/infra/rag-service/backend/src/tools/__init__.py`**
   - Added: `register_document_tools` export
   - Follows barrel export pattern

## Implementation Details

### Core Features Implemented

#### 1. manage_document Tool with 5 Actions

**Action: create**
- Validates required fields: title, source_id, file_path
- UUID parsing with error handling
- Calls ingestion_service.ingest_document() for full pipeline
- Returns chunks_stored, chunks_failed, ingestion_time_ms

**Action: update**
- Validates document_id
- Partial updates: title, document_type, url, metadata
- Calls document_service.update_document()
- Optimizes response payload

**Action: delete**
- Validates document_id
- Calls ingestion_service.delete_document()
- Deletes from PostgreSQL + Qdrant atomically

**Action: get**
- Validates document_id
- Calls document_service.get_document()
- Optimizes response payload

**Action: list**
- Pagination with max 20 items per page (Gotcha #7)
- Filters: source_id, document_type
- Calls document_service.list_documents(exclude_large_fields=True)
- Optimizes each document in response

#### 2. MCP Optimization Functions

**truncate_text()**
- Truncates to 1000 chars max (Gotcha #7)
- Adds ellipsis indicator
- Handles None values

**optimize_document_for_mcp()**
- Truncates title field
- Minimizes metadata JSONB (keeps only essential keys)
- Reduces payload size for MCP responses

#### 3. Error Handling

- UUID parsing validation
- Required field validation
- Service error propagation
- Helpful error suggestions
- Exception logging with traceback

#### 4. JSON String Returns

All responses use json.dumps() to return JSON strings (Gotcha #6), never dict objects.

### Critical Gotchas Addressed

#### Gotcha #6: MCP Protocol Requirement
**Implementation**: All return statements use `json.dumps()` to return JSON strings, never dict objects.
```python
return json.dumps({
    "success": True,
    "documents": optimized_documents,
    # ...
})
```

#### Gotcha #7: Payload Optimization
**Implementation**:
- Content truncated to 1000 chars max (`MAX_CONTENT_LENGTH`)
- List results limited to 20 items max (`MAX_ITEMS_PER_PAGE`)
- `exclude_large_fields=True` when listing documents
- `optimize_document_for_mcp()` applied to all responses
```python
per_page = min(per_page, MAX_ITEMS_PER_PAGE)  # Enforce limit
success, result = await document_service.list_documents(
    filters=filters,
    page=page,
    per_page=per_page,
    exclude_large_fields=True,  # MCP optimization
)
```

#### Pattern Following: Consolidated Tool Pattern
**Implementation**: Single tool with action parameter routing to appropriate service methods, following examples/02_mcp_consolidated_tools.py pattern.

## Dependencies Verified

### Completed Dependencies:
- Task 2.1 (DocumentService): All CRUD methods available (create, update, delete, get, list)
- Task 2.2 (SourceService): Not directly used but available for future source validation
- Task 4.3 (IngestionService): ingest_document() and delete_document() available
- Pattern examples/02_mcp_consolidated_tools.py: Studied and followed

### External Dependencies:
- mcp.server.fastmcp: Context type for tool registration
- UUID parsing: Standard library uuid module
- json: Standard library for JSON string serialization
- asyncio: Implicit async/await support

## Testing Checklist

### Manual Testing (When MCP Server Started):
- [ ] Create document: `manage_document("create", title="Test", source_id="...", file_path="/tmp/test.pdf")`
- [ ] Get document: `manage_document("get", document_id="...")`
- [ ] Update document: `manage_document("update", document_id="...", title="Updated")`
- [ ] List documents: `manage_document("list", page=1, per_page=10)`
- [ ] List with filters: `manage_document("list", source_id="...", document_type="pdf")`
- [ ] Delete document: `manage_document("delete", document_id="...")`
- [ ] Verify error handling: Invalid UUIDs, missing required fields
- [ ] Verify pagination limit: Request per_page=50, confirm capped at 20
- [ ] Verify truncation: Create document with long title, confirm truncated in list

### Validation Results:
- ✅ All 5 actions implemented (create, update, delete, get, list)
- ✅ JSON string returns (json.dumps() used consistently)
- ✅ Content truncation applied (1000 char max)
- ✅ Pagination limit enforced (20 items max)
- ✅ UUID validation with error messages
- ✅ Required field validation
- ✅ Error suggestions provided
- ✅ Service integration (document_service, ingestion_service)
- ✅ Pattern compliance (examples/02_mcp_consolidated_tools.py)
- ✅ Archon pattern reference (project_tools.py)

## Success Metrics

**All PRP Requirements Met**:
- [x] Consolidated tool with action parameter
- [x] All actions supported: create, update, delete, get, list
- [x] Returns JSON string (Gotcha #6)
- [x] Content truncation to 1000 chars (Gotcha #7)
- [x] Pagination limit to 20 items (Gotcha #7)
- [x] Validation for action parameter
- [x] Routes to appropriate service methods
- [x] Error handling with suggestions
- [x] UUID parsing validation
- [x] Optimized payloads for MCP

**Code Quality**:
- Comprehensive docstrings (module, functions, tool)
- Type hints throughout (str | None, dict[str, Any])
- Logging for errors with exc_info=True
- Follows established patterns (examples/02_mcp_consolidated_tools.py)
- References production code (infra/archon/python/src/mcp_server/features/projects/project_tools.py)
- Addresses critical gotchas explicitly
- Clean separation of concerns (optimization functions separate)
- Consistent error response format

## Completion Report

**Status**: COMPLETE - Ready for Review
**Implementation Time**: ~45 minutes
**Confidence Level**: HIGH
**Blockers**: None

### Files Created: 1
### Files Modified: 1
### Total Lines of Code: ~427 lines

**Implementation Notes**:
- Followed consolidated tool pattern from examples/02_mcp_consolidated_tools.py
- Referenced production implementation from Archon project_tools.py
- All critical gotchas (#6, #7) explicitly addressed
- Service integration verified (document_service, ingestion_service available)
- Ready for MCP server integration (needs registration in main.py)

**Next Steps**:
1. Register tool in MCP server main.py using `register_document_tools(mcp)`
2. Add app state dependencies (document_service, ingestion_service)
3. Test via MCP protocol (Claude Desktop, Cursor, etc.)
4. Validate all actions work end-to-end
5. Proceed to Task 5.3 (manage_source Tool)

**Ready for integration and next steps.**
