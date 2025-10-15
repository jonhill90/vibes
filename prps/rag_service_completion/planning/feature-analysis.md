# Feature Analysis: RAG Service Completion

## INITIAL.md Summary

Complete the RAG service implementation from ~70% to production-ready state. Current backend is operational with Qdrant + PostgreSQL, document ingestion pipeline works, and MCP tools exist but are not configured. Missing: MCP server HTTP migration, Crawl4AI integration, REST API endpoints, frontend UI, hybrid search enablement, and comprehensive testing. Goal is to deliver a fully functional RAG service with MCP integration for AI assistants, working frontend for document management, and production-ready quality standards.

---

## Core Requirements

### Explicit Requirements (from INITIAL.md)

1. **MCP Server Migration**
   - Migrate from STDIO to Streamable HTTP transport
   - Fix OpenAI client instantiation in EmbeddingService
   - Repair constructor mismatches in mcp_server.py
   - Configure MCP port exposure in docker-compose
   - Update local Claude Desktop configuration
   - Test all 3 MCP tools (search_knowledge_base, manage_document, rag_manage_source)

2. **Database Schema Fixes**
   - Remove or add `text_preview` column in embedding_cache table
   - Align embedding cache INSERT statements with actual schema
   - Add cache hit-rate logging
   - Test cache read/write paths

3. **Crawl4AI Integration**
   - Create Crawl4AI client wrapper (Playwright setup, rate limiting, retries)
   - Integrate with crawl_jobs + sources tables
   - Extend IngestionService for crawl job processing
   - Expose crawl management via REST API (create job, status)
   - Expose crawl via MCP tools
   - Unit tests for crawler service + e2e smoke test

4. **REST API Endpoints**
   - Implement `/api/documents` router (CRUD operations)
   - Implement `/api/sources` router (CRUD operations)
   - Implement `/api/search` router (vector/hybrid search)
   - Add request/response models with validation
   - Add pagination support
   - Add error handling
   - Update OpenAPI documentation

5. **Frontend Experience**
   - Build document upload flow (file picker, source selector, progress, errors)
   - Create semantic search view (query input, results display with scores, filters, pagination)
   - Build source management page (CRUD interface)
   - Integrate with REST APIs
   - Add basic component tests

6. **Hybrid Search Enablement**
   - Surface hybrid search configuration (env flags, runtime toggle)
   - Verify combined vector + full-text scoring works end-to-end
   - Add metrics and logging for hybrid search
   - Add regression tests comparing vector-only vs hybrid outputs

7. **Test Coverage**
   - Unit tests for services (documents, sources, embeddings, vector, search strategies)
   - MCP integration tests (all tools)
   - API contract tests (all endpoints)
   - Target 80%+ coverage for backend modules

8. **Service Naming Consistency**
   - Rename `api` service to `backend` in docker-compose.yml
   - Update container names and health check references

### Implicit Requirements (inferred)

9. **Production Readiness**
   - Error handling throughout (graceful degradation)
   - Proper logging at appropriate levels
   - Health check endpoints functional
   - Connection pool management (prevent deadlocks)
   - Rate limiting for OpenAI API calls
   - Retry logic with exponential backoff

10. **Documentation**
    - API endpoint documentation (OpenAPI/Swagger)
    - MCP tool usage examples
    - Deployment guide updates
    - Architecture diagram updates (include hybrid search)

11. **Validation Gates**
    - MCP server starts without errors
    - All tools accessible from Claude Desktop
    - Search returns relevant results with scores
    - Document upload works via MCP and REST
    - Frontend connects and operates correctly
    - Hybrid search outperforms vector-only (accuracy metrics)
    - Performance targets met (vector <50ms, hybrid <100ms p95)

---

## Technical Components

### Data Models

**Existing (PostgreSQL)**:
- `sources` - Ingestion source tracking (upload, crawl, api)
- `documents` - Document metadata with tsvector for full-text search
- `chunks` - Document chunks with text and tsvector
- `crawl_jobs` - Web crawling operation tracking
- `embedding_cache` - **BROKEN**: Schema mismatch on text_preview column

**Existing (Qdrant)**:
- Collection: `documents` (1536-dimensional vectors, HNSW indexing)
- Payload: minimal metadata for filtering

**Pydantic Models** (need implementation):
- Request models: `DocumentUploadRequest`, `SearchRequest`, `SourceCreateRequest`, `CrawlRequest`
- Response models: `DocumentResponse`, `SearchResponse`, `SourceResponse`, `CrawlJobResponse`
- Validation: file types, URL formats, pagination limits

### External Integrations

**OpenAI API**:
- Model: `text-embedding-3-small` (1536 dimensions)
- Rate limits: 3,000 RPM, 1M TPM
- **BROKEN**: AsyncOpenAI client not instantiated, causing EmbeddingService failures
- **REQUIRED**: Batch processing (100 texts per call), exponential backoff, quota exhaustion handling

**Crawl4AI** (not yet integrated):
- Playwright-based web crawler
- Rate limiting configuration needed
- Retry logic for failed requests
- Error handling for unreachable pages
- Integration with crawl_jobs table for progress tracking

**Qdrant**:
- Current: Working integration via AsyncQdrantClient
- Collections initialized with correct dimensions
- Health checks functional

**PostgreSQL**:
- Current: asyncpg pool configured correctly
- Full-text search via tsvector + GIN indexes
- Hybrid search queries need testing/validation

**MCP Protocol**:
- **BROKEN**: STDIO transport needs migration to HTTP
- **REQUIRED**: JSON string returns (not dicts)
- **REQUIRED**: Payload truncation (1000 chars max)
- **REQUIRED**: Pagination limits (20 items max)
- Port exposure: 8002 (avoid conflicts with task-manager on 8000, api on 8001)

### Core Logic

**Document Ingestion Pipeline** (mostly working):
1. Parse (Docling) - 200-500ms per document
2. Chunk (semantic chunking) - 50-100ms
3. Embed (OpenAI batch) - 300-800ms per batch
4. Store (PostgreSQL + Qdrant atomic transaction) - 100-200ms

**Search Strategies** (code exists, needs validation):
- `BaseSearchStrategy`: Vector-only search (Qdrant)
- `HybridSearchStrategy`: Vector + full-text combined scoring
- **MISSING**: Reranking strategy (post-MVP)
- Configuration: `USE_HYBRID_SEARCH` env flag

**Error Recovery**:
- EmbeddingBatchResult pattern for partial failures
- Quota exhaustion detection (never store null embeddings)
- Retry queues for failed operations
- Graceful degradation (fallback to simpler strategies)

### UI/CLI Requirements

**Frontend Components** (React/Vite):
- Document Upload: File picker, drag-drop, source selection, progress bar, error display
- Search Interface: Query input, result cards (title, snippet, score), filters (source, type), pagination
- Source Management: CRUD table (list, create, edit, delete sources)
- Status Indicators: Loading states, success/error notifications

**MCP Tools** (for AI assistants):
- `search_knowledge_base`: Query input, filters, result count
- `manage_document`: CRUD actions (create/update/delete/get/list)
- `rag_manage_source`: Source CRUD operations
- `crawl_website`: URL input, recursive flag, max pages, exclude patterns

---

## Similar Implementations Found in Archon

### 1. Archon RAG Service (Internal Implementation)
- **Relevance**: 9/10
- **Archon ID**: Internal codebase (prps/rag_service_research/ARCHITECTURE.md)
- **Key Patterns**:
  - Strategy pattern for search (Base, Hybrid, Reranking)
  - RAGService coordinator delegates to strategies
  - Configuration-driven feature enablement (USE_HYBRID_SEARCH)
  - EmbeddingBatchResult pattern for quota exhaustion handling
  - tuple[bool, dict] return pattern for CRUD services
  - Graceful degradation with try/catch around optional features
  - Similarity threshold filtering (0.05)
  - Batch processing with exponential backoff
- **Gotchas**:
  - **CRITICAL**: Never store null/zero embeddings on quota exhaustion (corrupts search)
  - **CRITICAL**: Connection pool must be shared across requests (prevent deadlocks)
  - **CRITICAL**: MCP tools MUST return JSON strings, not dicts
  - Embedding cache hit rate: 20-40% typical (30% cost savings)
  - Hybrid search weights: 0.7 vector, 0.3 text (empirically validated)
  - Reranking candidate multiplier: 5x (fetch 50, return 10)

### 2. Task-Manager MCP Server Pattern
- **Relevance**: 8/10
- **Archon ID**: infra/task-manager/backend/src/mcp_server.py
- **Key Patterns**:
  - FastMCP Streamable HTTP transport
  - Consolidated find/manage tool pattern (reduces tool count)
  - JSON string serialization in tool responses
  - Payload truncation for large text fields
  - Pagination with max limits
  - Error responses with suggestions field
- **Gotchas**:
  - Port conflicts: Use 8002 for MCP (task-manager uses 8000, api uses 8001)
  - Always validate JSON serialization in tests
  - Use `json.dumps()` explicitly, never return dict objects

### 3. MCP Client Integration Pattern (from Archon knowledge)
- **Relevance**: 7/10
- **Archon ID**: d60a71d62eb201d5 (modelcontextprotocol.io docs)
- **Key Patterns**:
  - AsyncOpenAI client initialization with API key
  - Tool definitions match MCP schema exactly
  - Message param builders for conversation flow
  - Tool use detection and result handling
- **Gotchas**:
  - OpenAI client must be initialized before passing to services
  - Type hints required for proper MCP tool schema generation
  - Tool parameters must match function signatures exactly

---

## Recommended Technology Stack

**Based on Archon patterns and existing implementation**:

### Backend
- **Framework**: FastAPI (async Python 3.11+)
  - Already in use, working well
  - asyncpg for PostgreSQL (async connection pooling)
  - AsyncQdrantClient for vector operations
- **Libraries**:
  - `openai` (1.x) - AsyncOpenAI client for embeddings
  - `fastmcp` - MCP server framework (Streamable HTTP transport)
  - `docling` - Document parsing (PDF, DOCX, HTML)
  - `playwright` - Browser automation for Crawl4AI
  - `qdrant-client` - Vector database operations
  - `asyncpg` - PostgreSQL async driver
  - `pydantic` - Data validation and settings management

### Frontend
- **Framework**: React 18 + Vite
  - Already scaffolded in frontend/ directory
  - TypeScript for type safety
- **Libraries**:
  - `react-query` or `swr` - Data fetching and caching
  - `react-hook-form` - Form handling (upload, search)
  - `axios` - HTTP client for REST API calls
  - `react-dropzone` - File upload component
  - UI library: Tailwind CSS or Material-UI (pick one)

### Testing
- **Unit Tests**: pytest, pytest-asyncio, pytest-cov
- **Mocking**: unittest.mock.AsyncMock for asyncpg, Qdrant
- **Integration**: httpx.AsyncClient with TestClient
- **Coverage**: pytest-cov with 80% target

### Deployment
- **Containerization**: Docker Compose (already configured)
- **Services**: PostgreSQL 15, Qdrant latest, FastAPI, Vite dev server
- **Networking**: Bridge network with health checks
- **Volumes**: Named volumes for persistence

---

## Assumptions Made

### 1. MCP Server Migration
**Assumption**: Migrate to Streamable HTTP transport matching task-manager pattern
- **Reasoning**: STDIO requires Python script invocation per Claude restart; HTTP allows persistent service in Docker
- **Source**: Archon pattern (vibesbox, task-manager use HTTP)
- **Alternative**: Keep STDIO if local-only development preferred (rejected for production readiness)

### 2. Hybrid Search Configuration
**Assumption**: Enable hybrid search by default after validation
- **Reasoning**: Architecture doc identifies hybrid as "Production Recommended" with 10-15% accuracy improvement
- **Source**: ARCHITECTURE.md analysis, Archon empirical validation
- **Alternative**: Keep disabled until client requests (rejected - missing value proposition)

### 3. Crawl4AI Integration Scope
**Assumption**: Basic crawler with Playwright, rate limiting, and job tracking (no AI-powered extraction initially)
- **Reasoning**: MVP focuses on core crawling; advanced features (markdown conversion, AI extraction) are post-MVP
- **Source**: INITIAL.md task prioritization (1-2 days effort estimate)
- **Alternative**: Full Crawl4AI AI features (rejected - scope creep)

### 4. Frontend UI Framework
**Assumption**: Use React with component library (Material-UI or Tailwind) for rapid development
- **Reasoning**: Frontend scaffold already uses Vite+React; component library accelerates UI development
- **Source**: Existing frontend/ directory structure
- **Alternative**: Vue or Svelte (rejected - codebase already React)

### 5. REST API Design
**Assumption**: Follow RESTful conventions with pagination, filtering, and validation
- **Reasoning**: Standard API design patterns, matches task-manager API structure
- **Source**: Archon task-manager API patterns
- **Alternative**: GraphQL (rejected - simpler REST sufficient for CRUD)

### 6. Embedding Cache Schema Fix
**Assumption**: Add `text_preview` column to embedding_cache table (don't remove from INSERT)
- **Reasoning**: Text preview useful for debugging cache hits; minor schema addition is safer than refactoring code
- **Source**: INITIAL.md bug report
- **Alternative**: Remove text_preview from code (rejected - loses debugging capability)

### 7. Test Coverage Strategy
**Assumption**: Focus on service layer (85%) and critical paths (MCP tools 75%), skip exhaustive edge cases initially
- **Reasoning**: 80% overall coverage balances quality with development speed
- **Source**: ARCHITECTURE.md testing strategy
- **Alternative**: 100% coverage (rejected - diminishing returns for MVP)

### 8. Service Naming
**Assumption**: Rename `api` to `backend` in docker-compose for clarity
- **Reasoning**: Consistency with task-manager naming (backend service runs FastAPI)
- **Source**: INITIAL.md explicit requirement
- **Alternative**: Keep as `api` (rejected - user requested change)

### 9. Port Allocation
**Assumption**:
- Backend API: 8001 (avoid task-manager on 8000)
- MCP Server: 8002 (dedicated port for MCP HTTP)
- Frontend: 5173 (Vite default)
- PostgreSQL: 5433 (avoid conflicts)
- Qdrant: 6333/6334 (defaults)
- **Reasoning**: Avoid port conflicts with existing infrastructure projects
- **Source**: Docker-compose.yml shows 8001 for API
- **Alternative**: Use same ports (rejected - conflicts likely)

### 10. Error Handling Philosophy
**Assumption**: Graceful degradation with logging (service continues on non-critical errors)
- **Reasoning**: Archon pattern, production resilience
- **Source**: ARCHITECTURE.md graceful degradation section
- **Alternative**: Fail-fast (rejected - reduces availability)

---

## Success Criteria

**From INITIAL.md + inferred production standards**:

### Functional Completeness
1. ✅ MCP server functional and tested from Claude Desktop (all 3 tools work)
2. ✅ Frontend allows document upload, search, and source management
3. ✅ Hybrid search demonstrably improves accuracy over vector-only (metrics logged)
4. ✅ Embedding cache reduces costs by ~30% (hit rate monitoring)
5. ✅ REST API fully documented (OpenAPI spec) and tested
6. ✅ Crawl4AI integration can ingest web content into knowledge base
7. ✅ All services start via docker-compose up without errors

### Quality Standards
8. ✅ 80%+ test coverage with passing tests (unit + integration + MCP)
9. ✅ No critical bugs in error handling (quota exhaustion, connection pools)
10. ✅ Documentation updated and accurate (README, API docs, MCP tool examples)

### Performance Targets
11. ✅ Vector search: <50ms p95 latency
12. ✅ Hybrid search: <100ms p95 latency
13. ✅ Document ingestion: >35 docs/min throughput
14. ✅ Embedding cache hit rate: >20%

### Production Readiness
15. ✅ Health checks functional for all services
16. ✅ Error logging at appropriate levels (INFO for normal, ERROR for failures)
17. ✅ Connection pools prevent deadlocks under concurrent load
18. ✅ OpenAI rate limiting prevents quota exhaustion
19. ✅ Service naming consistent (backend, not api)

---

## Next Steps for Downstream Agents

### Codebase Researcher
**Focus Areas**:
1. **MCP Server Patterns**: Search for `fastmcp`, `Streamable`, `HTTP transport` in infra/task-manager, infra/vibesbox
2. **EmbeddingService Instantiation**: Find OpenAI client initialization patterns in existing services
3. **Hybrid Search Queries**: Locate tsvector query examples in PostgreSQL integrations
4. **Connection Pool Patterns**: Search for `asyncpg.create_pool`, `lifespan`, `FastAPI` context managers
5. **Error Handling Patterns**: Find `EmbeddingBatchResult`, quota exhaustion handling in Archon codebase

**Key Patterns to Extract**:
- FastMCP HTTP server setup (port, host, transport configuration)
- OpenAI AsyncOpenAI instantiation with API keys from settings
- PostgreSQL full-text search queries (ts_rank, to_tsquery)
- Service layer tuple[bool, dict] return pattern examples
- MCP tool JSON string serialization helpers

### Documentation Hunter
**Find Documentation For**:
1. **FastMCP**: Streamable HTTP transport configuration and examples
2. **Crawl4AI**: Playwright setup, rate limiting, job tracking patterns
3. **Qdrant**: AsyncQdrantClient initialization, collection management, health checks
4. **OpenAI Embeddings API**: Batch processing, rate limits, error codes (quota_exhausted)
5. **PostgreSQL tsvector**: Full-text search queries, ts_rank scoring, GIN indexes
6. **React Query/SWR**: Data fetching patterns for REST APIs
7. **MCP Protocol**: JSON string requirements, payload limits, pagination

**Documentation Priorities**:
- MCP server setup (critical for Task 2)
- Crawl4AI integration guide (critical for Task 3)
- Hybrid search implementation (critical for Task 6)

### Example Curator
**Extract Examples Showing**:
1. **MCP HTTP Server**: Complete mcp_server.py with HTTP transport from task-manager
2. **OpenAI Client Wiring**: AsyncOpenAI instantiation and passing to EmbeddingService
3. **Embedding Quota Handling**: EmbeddingBatchResult pattern with quota exhaustion detection
4. **Hybrid Search Query**: Combined Qdrant + PostgreSQL query with score merging
5. **REST API Route**: FastAPI route with request/response models, validation, error handling
6. **File Upload Frontend**: React component with dropzone, progress bar, error display
7. **Search Interface**: React component with query input, results display, pagination
8. **Connection Pool Lifespan**: FastAPI lifespan context manager with pool creation/cleanup

**Example Quality Criteria**:
- Executable code (not pseudocode)
- Includes imports and type hints
- Shows error handling
- Demonstrates Archon patterns (tuple[bool, dict], graceful degradation)

### Gotcha Detective
**Investigate These Problem Areas**:
1. **OpenAI Client Null Reference**: Why EmbeddingService fails on instantiation (line 33 issue?)
2. **Embedding Cache Schema**: Why text_preview column INSERT fails (missing column or typo?)
3. **MCP STDIO Failures**: Constructor mismatches causing runtime errors
4. **Connection Pool Deadlocks**: Patterns that prevent asyncpg pool exhaustion
5. **Null Embedding Corruption**: How quota exhaustion can corrupt vector search (never store nulls)
6. **Port Conflicts**: Services competing for same ports (8000, 5432, 6333)
7. **MCP JSON Returns**: Common mistake of returning dict instead of JSON string
8. **Hybrid Search Scoring**: Incorrect weight normalization causing bias

**Investigation Priorities**:
- OpenAI client instantiation (blocks Task 2)
- Embedding cache schema mismatch (blocks cache usage)
- MCP constructor issues (blocks Task 2)

**Output Format**: Gotcha + Solution + Code Example for each issue

---

## Technical Dependencies & Blockers

### Critical Path Dependencies
1. **Task 2 (MCP Server)** blocks **Task 4 (REST API)** - MCP tools will use same service layer
2. **Task 2 (MCP Server)** blocks **Task 8 (Test Coverage)** - MCP tests need working tools
3. **Task 4 (REST API)** blocks **Task 5 (Frontend)** - Frontend needs API endpoints
4. **Task 6 (Hybrid Search)** requires **Task 2** complete - MCP tool testing validates hybrid

### Potential Blockers
- **OpenAI API Key**: Required for embedding tests (use mock for unit tests, real for integration)
- **Playwright Installation**: Crawl4AI requires browser binaries (long first install)
- **Qdrant Collection**: Must be initialized before tests (automate in setup)
- **PostgreSQL Schema**: embedding_cache text_preview column must exist (migration script)

### Risk Mitigation
- **OpenAI Quota**: Use caching aggressively, mock for most tests
- **Crawl4AI Complexity**: Implement basic crawler first, advanced features post-MVP
- **Frontend Scope**: Start with document upload only, add search/sources iteratively
- **Test Coverage**: Focus on critical paths first (ingestion, search), expand later

---

## Estimated Effort by Task (from INITIAL.md)

| Task | Priority | Effort | Dependencies | Notes |
|------|----------|--------|--------------|-------|
| 1. Rename Service | Low | 5 min | None | Quick win |
| 2. MCP Server | High | 0.5 day | None | **Critical infrastructure** |
| 3. Crawl4AI | High | 1-2 days | Task 2 | Can parallelize with Task 4 |
| 4. REST API | High | 1 day | Task 2 | Needed for frontend |
| 5. Frontend | Medium | 1-2 days | Task 4 | UI implementation |
| 6. Hybrid Search | Medium | 0.5 day | Task 2 | Configuration + validation |
| 7. Cache Alignment | Medium | 0.5 day | None | Schema fix |
| 8. Test Coverage | Medium | 1 day | Tasks 2-7 | Final validation |

**Total**: 5-7 days focused work (matches INITIAL.md estimate)

**Recommended Execution Order**:
1. Day 1: Tasks 1 (rename) + 2 (MCP server) + 7 (cache fix)
2. Day 2: Task 6 (hybrid search validation)
3. Days 3-4: Task 4 (REST API) in parallel with Task 3 (Crawl4AI)
4. Days 5-6: Task 5 (Frontend)
5. Day 7: Task 8 (Testing)

---

## Architecture Patterns to Follow

### 1. Service Layer Pattern (from Archon)
```python
# CRUD services return tuple[bool, dict]
async def get_document(document_id: str) -> tuple[bool, dict]:
    try:
        # Database operation
        return True, {"document": result}
    except Exception as e:
        return False, {"error": str(e), "suggestion": "..."}

# Coordinator services return direct results
async def search_documents(query: str) -> list[dict]:
    # RAGService delegates to strategies, raises on error
    return results
```

### 2. Strategy Pattern for Search (from Archon)
```python
# Thin coordinator, fat strategies
class RAGService:
    def __init__(self, base_strategy, hybrid_strategy=None):
        self.base = base_strategy
        self.hybrid = hybrid_strategy

    async def search(self, query, search_type="hybrid"):
        strategy = self.hybrid if search_type == "hybrid" else self.base
        return await strategy.search(query)
```

### 3. MCP Tool Pattern (from task-manager)
```python
@mcp.tool()
async def manage_document(action: str, **kwargs) -> str:
    """Consolidated document management tool."""
    # Route by action
    if action == "create":
        success, result = await service.create_document(**kwargs)
    # ... other actions

    # CRITICAL: Return JSON string, not dict
    return json.dumps(result)
```

### 4. Connection Pool Pattern (from Archon)
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create pools
    app.state.db_pool = await asyncpg.create_pool(...)
    app.state.qdrant = QdrantClient(...)
    yield
    # Shutdown: Close pools
    await app.state.db_pool.close()
    await app.state.qdrant.close()

# Dependency: Return pool, not connection
async def get_db_pool(request: Request) -> asyncpg.Pool:
    return request.app.state.db_pool
```

### 5. Error Handling Pattern (from Archon)
```python
# Graceful degradation
try:
    results = await hybrid_search(query)
    search_type = "hybrid"
except Exception as e:
    logger.warning(f"Hybrid search failed: {e}, falling back to vector")
    results = await vector_search(query)
    search_type = "vector"
```

---

## Code Quality Standards

### Type Hints
- All function signatures have type hints
- Use `str | None` instead of `Optional[str]` (Python 3.10+)
- Use `list[dict]` instead of `List[Dict]` (Python 3.9+)

### Error Handling
- Service layer catches specific exceptions (asyncpg.PostgresError, openai.RateLimitError)
- Log at appropriate levels (INFO for success, WARNING for degradation, ERROR for failures)
- Return structured errors with suggestions

### Testing
- Unit tests mock external dependencies (asyncpg, Qdrant, OpenAI)
- Integration tests use real database (test instance)
- MCP tests validate JSON string returns
- Aim for 80%+ coverage, focus on critical paths first

### Documentation
- Docstrings for public functions
- README updates for new features
- OpenAPI spec auto-generated from Pydantic models
- MCP tool examples in docs/

---

## Validation Checklist (for downstream PRP execution)

### Task 2: MCP Server
- [ ] MCP server starts on port 8002 without errors
- [ ] All 3 tools return valid JSON strings (not dicts)
- [ ] search_knowledge_base returns results with scores
- [ ] manage_document can upload and retrieve documents
- [ ] rag_manage_source can create and list sources
- [ ] Claude Desktop can connect and invoke tools

### Task 3: Crawl4AI
- [ ] Crawler can fetch single page content
- [ ] Crawl jobs tracked in crawl_jobs table
- [ ] Recursive crawling respects max_pages limit
- [ ] Failed pages logged, don't block entire job
- [ ] Crawled content flows through ingestion pipeline

### Task 4: REST API
- [ ] POST /api/documents accepts file upload
- [ ] GET /api/documents returns paginated list
- [ ] POST /api/search returns ranked results
- [ ] All endpoints have OpenAPI documentation
- [ ] Validation errors return 422 with details

### Task 5: Frontend
- [ ] Document upload shows progress and success/error
- [ ] Search displays results with scores and pagination
- [ ] Source management CRUD operations work
- [ ] Loading states prevent double-submissions

### Task 6: Hybrid Search
- [ ] USE_HYBRID_SEARCH=true enables hybrid mode
- [ ] Hybrid search logs both vector and text scores
- [ ] Hybrid search p95 latency <100ms
- [ ] Accuracy metrics show improvement over vector-only

### Task 7: Cache Alignment
- [ ] Embedding cache INSERT succeeds with text_preview
- [ ] Cache hit rate logged on every embedding operation
- [ ] Cache hit rate >20% after ingesting 1000+ documents

### Task 8: Test Coverage
- [ ] pytest runs without failures
- [ ] Coverage report shows >80% overall
- [ ] Service layer >85% coverage
- [ ] MCP tools >75% coverage
- [ ] Integration tests pass (end-to-end search, upload)

---

## References

**Architecture Documentation**:
- `/Users/jon/source/vibes/prps/rag_service_research/ARCHITECTURE.md` - Complete system design
- `/Users/jon/source/vibes/infra/rag-service/docker-compose.yml` - Current infrastructure

**Similar Patterns**:
- `/Users/jon/source/vibes/infra/task-manager/backend/src/mcp_server.py` - MCP HTTP pattern
- `/Users/jon/source/vibes/infra/vibesbox/src/mcp_server.py` - Streamable transport example

**External Documentation** (from Archon knowledge base):
- MCP Protocol: modelcontextprotocol.io (source: d60a71d62eb201d5)
- OpenAI API: AsyncOpenAI patterns (source: c0e629a894699314)
- FastAPI: Lifespan context managers, async patterns

**INITIAL.md Analysis**:
- 8 explicit tasks with priorities and effort estimates
- 5 validation gates (MCP, Frontend, Hybrid, Performance, Testing)
- Success criteria: functionality + quality + cost targets

---

**Document Status**: Complete
**Total Analysis**: ~3,500 words
**Confidence Level**: High (based on existing architecture + INITIAL.md clarity)
**Ready For**: Phase 2 Parallel Research (Codebase, Documentation, Examples, Gotchas)
