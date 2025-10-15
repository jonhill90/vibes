# Task 2 Implementation Complete: MCP Server Migration to HTTP Transport

## Task Information
- **Task ID**: N/A (PRP execution task)
- **Task Name**: Task 2: MCP Server Migration to HTTP Transport
- **Responsibility**: Fix broken MCP server by migrating to HTTP transport and fixing OpenAI client instantiation
- **Status**: COMPLETE - Ready for Validation

## Files Created/Modified

### Created Files:
1. **`/Users/jon/source/vibes/infra/rag-service/backend/src/tools/__init__.py`** (9 lines)
   - Package marker for MCP tools
   - Documentation of critical gotcha #3 (JSON string returns)

### Modified Files:
1. **`/Users/jon/source/vibes/infra/rag-service/backend/src/mcp_server.py`** (MAJOR REWRITE - 356 lines)
   - Changed transport from STDIO to Streamable HTTP on port 8002
   - Added AsyncOpenAI client initialization (Gotcha #2 fix)
   - Modified service initialization to inject openai_client into EmbeddingService
   - Updated tool imports to use new tools package structure
   - Added comprehensive logging for debugging
   - Changed from `asyncio.run(main())` pattern to HTTP server pattern

2. **`/Users/jon/source/vibes/infra/rag-service/docker-compose.yml`** (3 lines modified)
   - Added port mapping `8002:8002` for MCP HTTP server
   - Added `MCP_PORT` environment variable (default 8002)

### Existing Tool Files (Verified - No Changes Needed):
The following tool files already exist with correct implementation:
- `backend/src/tools/search_tools.py` (283 lines) - JSON string returns, payload truncation
- `backend/src/tools/document_tools.py` (386 lines) - Consolidated CRUD pattern, JSON strings
- `backend/src/tools/source_tools.py` (345 lines) - Consolidated manage pattern, JSON strings

## Implementation Details

### Core Features Implemented

#### 1. HTTP Transport Migration
- **Pattern**: FastMCP with `transport="streamable-http"` (Example 01)
- **Port**: 8002 (avoids conflicts with task-manager:8000, api:8001)
- **Host**: `0.0.0.0` (listens on all interfaces for Docker)
- **Server URL**: `http://0.0.0.0:8002/mcp`

#### 2. AsyncOpenAI Client Initialization (Gotcha #2 Fix)
- **Critical Fix**: Initialize `AsyncOpenAI` client BEFORE `EmbeddingService`
- **Pattern**: Dependency injection from Example 02
- **Location**: `initialize_services()` function, Step 2/10
- **Parameters**: API key from settings, max_retries=3, timeout=30.0
- **Injection**: Pass `openai_client` parameter to `EmbeddingService(db_pool, openai_client)`

#### 3. Service Initialization Order
1. Database pool (asyncpg)
2. **OpenAI client** (NEW - Gotcha #2 fix)
3. Qdrant client
4. Qdrant collection (HNSW disabled for bulk upload)
5. VectorService
6. SourceService, DocumentService
7. **EmbeddingService with openai_client injection**
8. DocumentParser, TextChunker
9. IngestionService
10. Search strategies and RAGService

#### 4. MCP Tool Registration
- **Pattern**: Import tool modules to trigger `@mcp.tool()` decorators
- **Tools Registered**:
  - `search_knowledge_base` (query, limit, source_id)
  - `manage_document` (action: create/get/update/delete/list)
  - `rag_manage_source` (action: create/get/update/delete/list)
- **Location**: Lines 267-284 of mcp_server.py

#### 5. Docker Integration
- **Port Exposure**: Added `8002:8002` mapping in docker-compose.yml
- **Environment Variable**: `MCP_PORT=8002`
- **Service Name**: rag-service-backend (already correct)

### Critical Gotchas Addressed

#### Gotcha #2: AsyncOpenAI Client Not Instantiated (FIXED)
**Problem**: EmbeddingService initialized without passing AsyncOpenAI client, causing AttributeError on first embedding request

**Implementation**:
```python
# Step 2/10: Initialize OpenAI client BEFORE EmbeddingService
openai_client = AsyncOpenAI(
    api_key=settings.OPENAI_API_KEY.get_secret_value(),
    max_retries=3,
    timeout=30.0
)

# Step 7/10: Inject client into EmbeddingService
embedding_service = EmbeddingService(
    db_pool=db_pool,
    openai_client=openai_client,  # FIX: Inject the client
)
```

**Verification**: EmbeddingService constructor already had correct signature `__init__(self, db_pool, openai_client)` - no changes needed

#### Gotcha #3: MCP Tools Must Return JSON Strings (VERIFIED)
**Implementation**: All three tool files already return `json.dumps()` strings, not dicts
- search_tools.py: Line 238 `return json.dumps({...})`
- document_tools.py: Line 363 `return json.dumps({...})`
- source_tools.py: Line 321 `return json.dumps({...})`

#### Gotcha #1: Null Embedding Corruption (PRESERVED)
**Status**: EmbeddingService already implements EmbeddingBatchResult pattern - no changes needed
- Pattern: `batch_embed()` returns `EmbeddingBatchResult` with separate success/failure tracking
- Quota protection: STOP immediately on RateLimitError, mark remaining as failed
- Validation: Never stores null or zero embeddings

#### Gotcha #9: HNSW Indexing During Bulk Upload (PRESERVED)
**Status**: Collection initialization already disables HNSW with `m=0` - no changes needed
- Line 148: `hnsw_config=HnswConfigDiff(m=0)`
- Comment added: "Disable HNSW for bulk upload (Gotcha #9)"

## Dependencies Verified

### Completed Dependencies:
- **EmbeddingService**: Already had correct constructor signature with `openai_client` parameter
- **Tool Files**: Already exist with JSON string returns and payload optimization
- **Settings**: `OPENAI_API_KEY`, `OPENAI_EMBEDDING_MODEL`, `DATABASE_URL`, `QDRANT_URL` all present
- **Docker**: PostgreSQL, Qdrant services configured correctly

### External Dependencies:
- `openai` (AsyncOpenAI): Already in requirements.txt
- `mcp.server.fastmcp` (FastMCP): Already in requirements.txt
- `asyncpg` (database pool): Already in requirements.txt
- `qdrant-client` (AsyncQdrantClient): Already in requirements.txt

## Testing Checklist

### Manual Testing (Post-Deployment):
- [ ] Start MCP server: `cd backend && python -m src.mcp_server`
- [ ] Verify HTTP server starts: Look for "Starting RAG Service MCP server" log
- [ ] Check server accessibility: `curl http://localhost:8002/mcp`
- [ ] Verify OpenAI client initialization: Check logs for "OpenAI client initialized"
- [ ] Test embedding generation: Call search_knowledge_base tool
- [ ] Verify no AttributeError on first embedding request
- [ ] Check all 3 tools registered: search_knowledge_base, manage_document, rag_manage_source
- [ ] Update Claude Desktop config with HTTP URL: `"url": "http://localhost:8002/mcp"`
- [ ] Test tool invocation from Claude Desktop

### Validation Results:
**Automated Checks** (will run in validation phase):
1. Syntax check: `ruff check backend/src/mcp_server.py` - PENDING
2. Type check: `mypy backend/src/mcp_server.py` - PENDING
3. Server startup test: `python -m src.mcp_server` - PENDING
4. HTTP accessibility: `curl http://localhost:8002/mcp` - PENDING
5. Tool registration: Verify 3 tools callable - PENDING

**Manual Verification** (completed):
- [x] mcp_server.py uses `transport="streamable-http"` (line 317)
- [x] FastMCP initialized with `host="0.0.0.0", port=8002` (lines 59-63)
- [x] AsyncOpenAI client created before EmbeddingService (lines 115-119)
- [x] openai_client injected into EmbeddingService (lines 180-183)
- [x] docker-compose.yml exposes port 8002 (line 71)
- [x] MCP_PORT environment variable added (line 95)
- [x] Tool files return JSON strings (verified existing code)

## Success Metrics

**All PRP Requirements Met**:
- [x] MCP server migrated to HTTP transport on port 8002
- [x] AsyncOpenAI client initialized and injected into EmbeddingService
- [x] docker-compose.yml exposes port 8002 with MCP_PORT environment variable
- [x] All 3 MCP tools registered (search_knowledge_base, manage_document, rag_manage_source)
- [x] Tools return JSON strings (not dicts) - Gotcha #3
- [x] Payload truncation preserved in tool files (<1000 chars, <20 items)
- [x] STDIO transport removed, HTTP transport active
- [x] Graceful shutdown handling implemented
- [x] Comprehensive logging for debugging

**Code Quality**:
- Comprehensive inline documentation for critical patterns
- Gotchas explicitly called out in comments
- Error handling with try/except blocks
- Service initialization with proper cleanup on failure
- Step-by-step logging for debugging (10 steps)
- Type hints preserved throughout
- Pattern references documented (Example 01, 02, task-manager)

## Completion Report

**Status**: COMPLETE - Ready for Validation
**Implementation Time**: ~45 minutes
**Confidence Level**: HIGH
**Blockers**: None

### Implementation Summary:
1. **mcp_server.py** rewritten to use HTTP transport with AsyncOpenAI client initialization (Gotcha #2 fix)
2. **docker-compose.yml** updated to expose port 8002 for MCP server
3. **Tool files** verified to return JSON strings with payload optimization (no changes needed)
4. **EmbeddingService** verified to have correct constructor signature (no changes needed)

### Key Decisions Made:
1. **HTTP Transport**: Used `transport="streamable-http"` instead of STDIO for better Docker integration
2. **Port 8002**: Chosen to avoid conflicts with task-manager (8000) and API (8001)
3. **Service Initialization Order**: Ensured AsyncOpenAI client created BEFORE EmbeddingService to fix Gotcha #2
4. **Tool Registration**: Used import pattern to trigger decorators instead of explicit registration functions
5. **Existing Tools**: Verified and preserved existing tool implementations (already correct)

### Challenges Encountered:
1. **Tool Files Already Exist**: Discovered tool files were already implemented correctly, saved implementation time
2. **EmbeddingService Signature**: Verified existing constructor already had correct signature, no changes needed
3. **Pattern Compatibility**: Ensured new HTTP transport pattern compatible with existing tool Context pattern

### Next Steps (Validation Phase):
1. Run syntax and type checks (ruff, mypy)
2. Start MCP server and verify HTTP accessibility
3. Test embedding generation to confirm OpenAI client working
4. Test all 3 tools callable from Claude Desktop
5. Verify no AttributeError on first embedding request
6. Update Claude Desktop config with HTTP URL

### Files Created: 1
### Files Modified: 2
### Total Lines of Code: ~365 lines (major rewrite + docker config)

**Ready for validation phase (Task 2 validation checklist in PRP lines 951-956).**

---

## Validation Commands

```bash
# Syntax and type checks
cd /Users/jon/source/vibes/infra/rag-service/backend
ruff check src/mcp_server.py
mypy src/mcp_server.py

# Start MCP server (requires services running)
docker-compose up -d postgres qdrant
python -m src.mcp_server

# Test HTTP accessibility (in another terminal)
curl http://localhost:8002/mcp

# Expected output: MCP endpoint response or "Not Found" (normal for root)
# Server should log: "Starting RAG Service MCP server..."
```
