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

### ❌ What's Missing / Needs Fixes
- MCP server not configured/tested; still on STDIO transport and constructor mismatches cause runtime failures
- OpenAI client wiring missing (EmbeddingService instantiation fails) and embedding cache INSERT uses non-existent `text_preview` column
- Crawl4AI ingestion pipeline absent (no crawler service, crawl job executor, or MCP/REST hooks)
- REST API routers beyond health endpoint unimplemented (documents, sources, search)
- Frontend UI limited to scaffold; upload/search/source management still need constructing
- Hybrid search exists in code but is unreachable until MCP wiring/REST surfaces it, and needs validation toggles
- Test coverage thin (single integration test); unit/service/MCP tests required
- Service naming (`api` should be `backend`) still inconsistent in Docker Compose and references

---

## Tasks

### 1. Rename Service (Quick Fix)
**Priority**: Low | **Effort**: 5 minutes

Rename `api` to `backend` in `docker-compose.yml` (and related health checks/container names) so the service label matches reality. Validate with `docker-compose up`.

### 2. Repair and Migrate MCP Server
**Priority**: High | **Effort**: 0.5 day

1. Instantiate `openai.AsyncOpenAI` and pass it into `EmbeddingService`; update Base/Hybrid strategy constructors in `backend/src/mcp_server.py` to match signatures.
2. Switch FastMCP to streamable HTTP, expose the MCP port in docker-compose, and update local Claude config.
3. Re-run MCP smoke tests (`search_knowledge_base`, `manage_document`, `rag_manage_source`) to confirm JSON responses and hybrid toggle behaviour.

### 3. Crawl4AI Ingestion Pipeline
**Priority**: High | **Effort**: 1-2 days

- Add a Crawl4AI client wrapper (Playwright setup, rate limiting, retries) and integrate it with `crawl_jobs` + `sources` tables.
- Extend IngestionService to enqueue and process crawl jobs through Docling → chunking → embedding.
- Expose crawl management via REST (create job, status) and MCP (action on manage_source or new tool).
- Tests: unit tests for crawler service, e2e crawl smoke test with mocked outputs.

### 4. REST API Endpoints
**Priority**: High | **Effort**: 1 day

- Implement `/api/documents`, `/api/sources`, `/api/search` routers (CRUD, search) following task-manager patterns.
- Add request/response models, validation, pagination, and error handling.
- Update OpenAPI docs and add route-level tests.

### 5. Frontend Experience
**Priority**: Medium | **Effort**: 1-2 days

- Build document upload flow (file picker, source selector, progress, errors).
- Create semantic search view (query, results with scores, filters, pagination) and source management page.
- Integrate with new REST APIs and add basic unit/component tests.

### 6. Hybrid Search Enablement
**Priority**: Medium | **Effort**: 0.5 day

- After MCP/REST wiring fixes, surface hybrid search configuration (env flags, runtime toggle) and verify combined scoring works end-to-end.
- Add metrics/logging and regression tests comparing vector vs hybrid outputs.

### 7. Embedding Cache Alignment
**Priority**: Medium | **Effort**: 0.5 day

- Align schema and SQL insert (add `text_preview` column or remove it from `_cache_embedding`).
- Add cache hit-rate logging and tests covering cache read/write paths.

### 8. Test Coverage & Tooling
**Priority**: Medium | **Effort**: 1 day

- Add unit tests for services (documents, sources, embeddings, vector, search strategies).
- Introduce MCP integration tests and API contract tests.
- Hook lint/type/test commands into CI guidance; target 80%+ coverage for backend modules.

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
