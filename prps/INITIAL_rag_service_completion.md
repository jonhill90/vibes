# RAG Service - Complete MVP Implementation

**Status**: Implementation ~70% complete, needs finishing touches
**Context**: Backend operational with Qdrant + PostgreSQL, MCP tools exist but not configured, frontend structure only
**Related**: `prps/rag_service_research/ARCHITECTURE.md`, `infra/rag-service/`

---

## Goal

Complete the RAG service implementation to match the architecture plan with:
- Fully functional MCP server for AI assistant integration
- Working frontend for document management
- Hybrid search for better accuracy
- Complete REST API endpoints
- Production-ready with proper testing

---

## Current State

### ✅ What's Working
- FastAPI backend with async PostgreSQL (asyncpg)
- Qdrant vector database with HNSW indexing
- Document ingestion pipeline (Docling → chunking → embeddings → storage)
- Base vector search (10-50ms latency)
- MCP server code (`mcp_server.py`) and tools (`search_tools.py`, `document_tools.py`, `source_tools.py`)
- Docker Compose with health checks
- End-to-end integration test

### ❌ What's Missing
- MCP server not configured/tested
- Frontend not implemented (structure only)
- Hybrid search (vector + full-text)
- Embedding cache (30% cost savings)
- REST API routes (only health endpoint exists)
- Unit tests (only integration test)
- Service naming (`api` should be `backend`)

---

## Tasks

### 1. Rename Service (Quick Fix)
**Priority**: Low | **Effort**: 5 minutes

Rename `api` to `backend` in `docker-compose.yml` for semantic accuracy:
- Service contains MCP server, Docling parsing, not just API
- Changes: service name, container name, frontend dependency
- Test: `docker-compose up` and verify all services start

### 2. Migrate MCP Server to Streamable HTTP
**Priority**: High | **Effort**: 2-3 hours

**2.1 Update MCP Server Configuration**
Change from STDIO to Streamable HTTP transport (following vibesbox pattern):

In `backend/src/mcp_server.py`:
```python
# Create FastMCP server with HTTP configuration
# PATTERN FROM: vibesbox/src/mcp_server.py
mcp = FastMCP(
    "RAG Service",
    host="0.0.0.0",
    port=8000  # Internal port (mapped to 8052 externally)
)

# In main():
if __name__ == "__main__":
    logger.info("Starting RAG Service MCP server...")
    logger.info(f"   Mode: Streamable HTTP")
    logger.info(f"   URL: http://0.0.0.0:8000/mcp")

    try:
        mcp.run(transport="streamable-http")  # Changed from "stdio"
    except KeyboardInterrupt:
        logger.info("RAG Service MCP server stopped by user")
```

**2.2 Update Docker Compose**
Add MCP port exposure to `docker-compose.yml`:

```yaml
backend:
  ports:
    - "${API_PORT:-8001}:8001"  # FastAPI server
    - "${MCP_PORT:-8052}:8000"  # MCP server (internal 8000 -> external 8052)
  environment:
    - MCP_PORT=${MCP_PORT:-8052}
```

**2.3 Update Claude Desktop Configuration**
Change to HTTP transport in `~/.config/claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "rag-service": {
      "transport": {
        "type": "streamable-http",
        "url": "http://localhost:8052/mcp"
      },
      "env": {
        "OPENAI_API_KEY": "..."
      }
    }
  }
}
```

**2.4 Test MCP Tools**
- Restart Docker services: `docker-compose restart backend`
- Restart Claude Desktop
- Test `search_knowledge_base(query="test", match_count=5)` - should search vectors
- Test `manage_document(action="list")` - should list documents
- Test `rag_manage_source(action="list")` - should list sources
- Verify all tools return JSON strings (not dicts) per MCP spec

**2.5 Validation**
- MCP server accessible at `http://localhost:8052/mcp`
- All 3 tools accessible from Claude Desktop
- Tools return proper JSON strings
- Search results include document content and scores
- Error handling returns structured errors
- Service persists across container restarts

### 3. Implement Frontend
**Priority**: Medium | **Effort**: 1-2 days

**3.1 Document Upload Interface**
- File upload component (PDF, DOCX, HTML, Markdown)
- Source selection dropdown
- Progress indicator during ingestion
- Success/error feedback

**3.2 Search Interface**
- Query input with submit
- Results list with:
  - Document title
  - Chunk content preview (1000 chars)
  - Similarity score
  - Source attribution
- Pagination (20 results max)

**3.3 Source Management**
- List all sources
- Create new source
- View source details (document count)
- Delete source (with confirmation)

**Tech Stack**: React + TypeScript + Vite (already configured in docker-compose)

### 4. Add Hybrid Search
**Priority**: High | **Effort**: 1 day

**4.1 PostgreSQL Schema Updates**
Add to `database/scripts/init.sql`:
```sql
-- Add tsvector columns for full-text search
ALTER TABLE documents ADD COLUMN search_vector tsvector;
ALTER TABLE chunks ADD COLUMN search_vector tsvector;

-- Create GIN indexes
CREATE INDEX idx_documents_search_vector ON documents USING GIN(search_vector);
CREATE INDEX idx_chunks_search_vector ON chunks USING GIN(search_vector);

-- Add triggers for automatic updates
CREATE OR REPLACE FUNCTION documents_search_vector_update()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector =
        setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.url, '')), 'B');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER documents_search_vector_trigger
    BEFORE INSERT OR UPDATE OF title, url
    ON documents
    FOR EACH ROW
    EXECUTE FUNCTION documents_search_vector_update();
```

**4.2 Implement HybridSearchStrategy**
File: `backend/src/services/search/hybrid_search_strategy.py`
- Fetch top 100 from Qdrant (vector search)
- Fetch top 100 from PostgreSQL (ts_rank full-text search)
- Combine scores: `0.7 * vector_score + 0.3 * text_score`
- Deduplicate and sort by combined score
- Return top N results

**4.3 Update RAGService**
- Add `use_hybrid` parameter to `search_documents()`
- Route to HybridSearchStrategy when enabled
- Add `USE_HYBRID_SEARCH=true` to `.env`

**4.4 Validation**
- Test hybrid search accuracy vs vector-only
- Benchmark latency (should be 50-100ms)
- Verify keyword queries improve with full-text matching

### 5. Add Embedding Cache
**Priority**: Medium | **Effort**: 4 hours

**5.1 Schema**
Add to `database/scripts/init.sql`:
```sql
CREATE TABLE embedding_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_hash TEXT NOT NULL UNIQUE,  -- MD5(text)
    embedding JSONB NOT NULL,  -- 1536-dimensional vector as JSON array
    model_name TEXT NOT NULL DEFAULT 'text-embedding-3-small',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_accessed_at TIMESTAMPTZ DEFAULT NOW(),
    access_count INT DEFAULT 1
);

CREATE INDEX idx_embedding_cache_hash ON embedding_cache(content_hash);
CREATE INDEX idx_embedding_cache_model ON embedding_cache(model_name);
```

**5.2 Update EmbeddingService**
- Before OpenAI call: Check cache by MD5(text)
- On cache hit: Return cached embedding, update `last_accessed_at`
- On cache miss: Call OpenAI, store in cache
- Track cache hit rate in logs

**5.3 Validation**
- Ingest duplicate content, verify cache hit
- Monitor cost savings (should see ~30% reduction)
- Verify cache lookup doesn't add significant latency (<5ms)

### 6. Implement REST API Routes
**Priority**: Medium | **Effort**: 1 day

Add routes to `backend/src/api/routes/`:

**6.1 Document Routes** (`documents.py`)
- `POST /api/documents` - Upload and ingest document
- `GET /api/documents` - List documents (paginated)
- `GET /api/documents/{id}` - Get document details
- `DELETE /api/documents/{id}` - Delete document and vectors

**6.2 Search Routes** (`search.py`)
- `POST /api/search` - Vector/hybrid search
  - Body: `{query, match_count, search_type, similarity_threshold}`
  - Response: `{results: [{id, title, content, score, metadata}]}`

**6.3 Source Routes** (`sources.py`)
- `GET /api/sources` - List sources
- `POST /api/sources` - Create source
- `GET /api/sources/{id}` - Get source details
- `DELETE /api/sources/{id}` - Delete source (cascades to documents)

**6.4 Include Routers in main.py**
```python
from src.api.routes import documents, search, sources
app.include_router(documents.router, prefix="/api", tags=["documents"])
app.include_router(search.router, prefix="/api", tags=["search"])
app.include_router(sources.router, prefix="/api", tags=["sources"])
```

### 7. Add Unit Tests
**Priority**: Medium | **Effort**: 2 days

**7.1 Service Layer Tests** (`tests/unit/`)
- `test_document_service.py` - Mock asyncpg pool, test CRUD operations
- `test_source_service.py` - Test source management
- `test_vector_service.py` - Mock Qdrant client, test vector operations
- `test_embedding_service.py` - Mock OpenAI, test batch processing
- `test_chunker.py` - Test chunking logic with edge cases

**7.2 MCP Tool Tests** (`tests/mcp/`)
- `test_search_tools.py` - Verify JSON string returns
- `test_document_tools.py` - Test CRUD via MCP
- `test_source_tools.py` - Test source management via MCP
- Validate payload truncation (1000 chars max)
- Validate pagination limits (20 items max)

**7.3 Coverage Target**
- Service layer: 85% coverage
- MCP tools: 75% coverage
- Overall: 80% minimum

**7.4 Run Tests**
```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test types
pytest tests/unit/ -v
pytest tests/mcp/ -v
```

### 8. Update Documentation
**Priority**: Low | **Effort**: 2 hours

**8.1 Update README.md**
- Add MCP server setup instructions
- Add frontend development instructions
- Update architecture diagram (include hybrid search)
- Add API endpoint documentation links

**8.2 Update IMPLEMENTATION_COMPARISON.md**
- Correct vector database analysis (Qdrant is used, not pgvector)
- Update "What's Missing" section after completion
- Add final implementation notes

**8.3 Add MCP Tool Documentation**
Create `docs/MCP_TOOLS.md`:
- Tool signatures with parameters
- Example usage from Claude Desktop
- Response format examples
- Error handling examples

---

## Validation Gates

After completing tasks, validate:

### Gate 1: MCP Integration
- [ ] MCP server starts without errors
- [ ] All 3 tools accessible from Claude Desktop
- [ ] Search returns relevant results with scores
- [ ] Document upload works via MCP
- [ ] Error handling returns structured JSON

### Gate 2: Frontend Functionality
- [ ] Frontend starts and connects to backend
- [ ] Document upload completes successfully
- [ ] Search interface returns and displays results
- [ ] Source management CRUD operations work
- [ ] Error states display properly

### Gate 3: Hybrid Search Accuracy
- [ ] Hybrid search outperforms vector-only for keyword queries
- [ ] Latency stays under 100ms (p95)
- [ ] Full-text search catches queries vector search misses
- [ ] Score combining produces better ranking

### Gate 4: Performance & Cost
- [ ] Vector search: <50ms p95
- [ ] Hybrid search: <100ms p95
- [ ] Embedding cache hit rate: >20%
- [ ] Cost savings from cache: ~30%

### Gate 5: Test Coverage
- [ ] Unit tests pass (80%+ coverage)
- [ ] Integration test passes
- [ ] MCP tool tests pass
- [ ] No critical bugs in error handling

---

## Success Criteria

Implementation complete when:
1. ✅ MCP server functional and tested from Claude Desktop
2. ✅ Frontend allows document upload and search
3. ✅ Hybrid search improves accuracy over vector-only
4. ✅ Embedding cache reduces costs by ~30%
5. ✅ REST API fully documented and tested
6. ✅ 80%+ test coverage with passing tests
7. ✅ Documentation updated and accurate

---

## Estimated Timeline

- **Quick wins** (rename, MCP config): 3 hours
- **Hybrid search**: 1 day
- **Embedding cache**: 4 hours
- **REST API routes**: 1 day
- **Frontend**: 2 days
- **Unit tests**: 2 days
- **Documentation**: 2 hours

**Total**: ~5-6 days of focused work

---

## Notes

- Architecture plan in `prps/rag_service_research/ARCHITECTURE.md` is comprehensive and accurate
- Current implementation follows plan closely (Qdrant + PostgreSQL dual database)
- Main gaps are polish features (hybrid search, caching, UI) not core functionality
- Backend is production-ready, just needs frontend and testing
- MCP tools exist but need migration from STDIO to Streamable HTTP

**Why Streamable HTTP vs STDIO?**
- STDIO requires Python script invocation per Claude Desktop restart
- HTTP allows service to run in Docker container persistently
- Better for development: service stays running with hot reload
- Matches vibesbox and task-manager patterns for consistency
- Easier debugging: can test MCP endpoints with curl/httpie

**Pattern References:**
- `infra/vibesbox/src/mcp_server.py` - Streamable HTTP transport pattern
- `infra/vibesbox/docker-compose.yml` - Port mapping and health checks
- `infra/task-manager/backend/src/mcp_server.py` - Consolidated tool pattern
- `infra/task-manager/docker-compose.yml` - Multi-service Docker setup

---

**Next Action**: Start with Task 2 (Migrate MCP to HTTP) - critical infrastructure change, enables all other tasks
