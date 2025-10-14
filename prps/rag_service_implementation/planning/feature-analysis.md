# Feature Analysis: RAG Service Implementation

## INITIAL.md Summary

Build a production-ready standalone RAG (Retrieval Augmented Generation) service based on comprehensive architecture research documented in `prps/rag_service_research/ARCHITECTURE.md`. The service implements a 5-phase development plan (Core Setup, Service Layer, Search Pipeline, Document Ingestion, MCP Tools) using Qdrant for vector storage, PostgreSQL for metadata/full-text search, FastAPI for the backend, OpenAI for embeddings, and Docling for document parsing. The goal is a fully functional, deployable RAG service following task-manager patterns and Archon's proven RAG pipeline design.

## Core Requirements

### Explicit Requirements (from INITIAL.md)

**Phase 1: Core Setup (Week 1)**
- Directory structure following task-manager pattern (backend/, frontend/, database/)
- Docker Compose orchestration (PostgreSQL 15-alpine, Qdrant v1.7.4+, FastAPI, Frontend)
- PostgreSQL schema with 5 tables: sources, documents, chunks, crawl_jobs, embedding_cache
- All indexes (GIN for tsvector, B-tree for foreign keys) and triggers (updated_at, tsvector updates)
- Qdrant collection initialization (1536 dimensions, cosine distance)
- FastAPI with lifespan connection pools (asyncpg + AsyncQdrantClient)
- Health check endpoints validating dual storage readiness
- Frontend scaffolding (Vite + React + TypeScript)

**Phase 2: Service Layer (Week 2)**
- DocumentService with tuple[bool, dict] return pattern
- SourceService with tuple[bool, dict] return pattern
- VectorService for Qdrant operations (upsert, search, delete)
- EmbeddingService with OpenAI integration and quota handling
- Connection pool management following FastAPI lifespan pattern

**Phase 3: Search Pipeline (Week 3)**
- BaseSearchStrategy: Vector similarity search (<50ms p95 target)
- HybridSearchStrategy: 0.7×vector + 0.3×text_rank combined scoring (<100ms p95 target)
- RAGService coordinator using strategy pattern
- Configuration-driven strategy selection (USE_HYBRID_SEARCH)
- Result merging and deduplication
- Pass top-k chunks to LLM integration points

**Phase 4: Document Ingestion (Week 4)**
- Docling parser integration (PDF, HTML, DOCX - not pypdf2/pdfplumber)
- Semantic chunking (~500 tokens, respect boundaries, 50 token overlap)
- Batch embedding via OpenAI (1536-dim vectors, 100 texts per batch)
- Atomic storage pattern (PostgreSQL metadata/FTS + Qdrant vectors)
- EmbeddingBatchResult pattern to prevent quota exhaustion corruption
- MD5 hash-based embedding cache lookup (20-40% hit rate expected)

**Phase 5: MCP Tools (Week 5)**
- search_knowledge_base tool (vector/hybrid/rerank strategies)
- manage_document tool (consolidated CRUD: create, update, delete, get, list)
- manage_source tool (consolidated CRUD)
- JSON string returns (not dicts - MCP protocol requirement)
- Payload optimization (1000 char max truncation)
- Pagination limits (20 items max per page)

### Implicit Requirements (inferred from architecture and best practices)

**Error Handling & Resilience**
- Exponential backoff for OpenAI rate limits (2^retry_count, max 3 retries)
- Graceful degradation when optional strategies fail (log warning, continue with base strategy)
- Comprehensive asyncpg.PostgresError catching with rollback
- Never store null/zero embeddings (corrupts vector search)
- Connection leak prevention via async context managers

**Performance & Scalability**
- Connection pool sizing: min=10, max=20 for asyncpg
- Batch processing for embeddings (100x throughput vs single calls)
- HNSW indexing in Qdrant for <50ms vector search at 1M vectors
- GIN indexes on tsvector columns for <50ms full-text search
- Embedding cache to reduce OpenAI costs by 30%

**Security & Configuration**
- Environment variable-based configuration (12-factor app pattern)
- Pydantic Settings for type-safe configuration
- API key management via .env (never commit credentials)
- CORS configuration for frontend integration
- Health check endpoints for monitoring

**Testing & Validation**
- Unit tests with AsyncMock for connection pools
- Integration tests with test database
- MCP tool protocol compliance tests
- Performance benchmarks (latency percentiles)
- 80% code coverage target

**Documentation & DevOps**
- Docker Compose for local development
- Health check endpoints for all services
- Volume persistence for PostgreSQL and Qdrant
- Service dependency management (depends_on with health checks)
- Log aggregation strategy

## Technical Components

### Data Models

**PostgreSQL Tables (5 total)**

1. **sources** - Ingestion source tracking
   - Fields: id (UUID), source_type (enum: upload/crawl/api), url, status (enum: pending/processing/completed/failed), metadata (JSONB), error_message, created_at, updated_at
   - Indexes: status, source_type, created_at DESC
   - Triggers: updated_at auto-update

2. **documents** - Document metadata
   - Fields: id (UUID), source_id (FK → sources CASCADE), title, document_type, url, metadata (JSONB), search_vector (TSVECTOR), created_at, updated_at
   - Indexes: source_id, search_vector (GIN), document_type, created_at DESC
   - Triggers: search_vector auto-update (weighted: title=A, url=B, metadata=C), updated_at auto-update

3. **chunks** - Text chunks for embedding
   - Fields: id (UUID), document_id (FK → documents CASCADE), chunk_index (INTEGER), text (TEXT), token_count (INTEGER), search_vector (TSVECTOR), metadata (JSONB), created_at
   - Indexes: document_id, search_vector (GIN), (document_id, chunk_index) composite
   - Constraints: UNIQUE(document_id, chunk_index)
   - Triggers: search_vector auto-update from text

4. **crawl_jobs** - Web crawling progress
   - Fields: id (UUID), source_id (FK → sources CASCADE), status (enum: pending/running/completed/failed/cancelled), pages_crawled, pages_total, max_pages, max_depth, current_depth, error_message, error_count, metadata (JSONB), started_at, completed_at, created_at, updated_at
   - Indexes: source_id, status, created_at DESC, (status, pages_crawled) composite
   - Triggers: updated_at auto-update

5. **embedding_cache** - Reusable embeddings
   - Fields: id (UUID), content_hash (TEXT UNIQUE - MD5), embedding (VECTOR(1536)), model_name (TEXT default 'text-embedding-3-small'), created_at, last_accessed_at, access_count (INT)
   - Indexes: content_hash (unique), model_name
   - Purpose: 30% cost savings on re-embedding identical content

**Qdrant Collection**
- Collection name: "documents" (configurable)
- Vector size: 1536 (text-embedding-3-small)
- Distance metric: Cosine
- Indexing: HNSW (10-30ms latency at 1M vectors)
- Payload fields: document_id, chunk_id, text (truncated 1000 chars), metadata
- No full metadata storage (PostgreSQL is source of truth)

**Pydantic Models**
- DocumentModel: title, document_type, url, metadata, source_id
- ChunkModel: text, token_count, chunk_index, document_id
- SourceModel: source_type, url, status, metadata
- SearchResultModel: chunk_id, document_id, document_title, text, score, match_type, metadata
- EmbeddingBatchResult: embeddings (list[list[float]]), failed_items (list[dict]), success_count, failure_count

### External Integrations

**OpenAI API**
- Endpoint: https://api.openai.com/v1/embeddings
- Model: text-embedding-3-small (1536 dimensions, $0.02/1M tokens)
- Rate limits: 3,000 RPM, 1,000,000 TPM
- Batch size: 100 texts per request
- Error handling: RateLimitError detection, exponential backoff, quota exhaustion tracking
- Integration: openai Python SDK (latest) with async support

**Docling Parser**
- Library: docling (latest from https://docling-project.github.io/docling/)
- Supported formats: PDF, HTML, DOCX, Markdown
- Capabilities: Table preservation, OCR, multi-column layouts, hierarchy preservation
- Processing time: 200-500ms per document
- Output: Structured document format ready for chunking

**Qdrant Vector Database**
- Docker image: qdrant/qdrant:latest
- API ports: 6333 (REST), 6334 (gRPC)
- Client: AsyncQdrantClient (qdrant-client Python package)
- Operations: create_collection, upsert, search, delete
- Configuration: API key optional, max_request_size_mb=32

**PostgreSQL Database**
- Docker image: postgres:15-alpine
- Extensions: uuid-ossp, pg_trgm (trigram), vector (pgvector)
- Client: asyncpg (MagicStack) - NOT psycopg3
- Pool config: min_size=10, max_size=20
- Critical: Use $1, $2 placeholders (NOT %s)

**MCP Protocol**
- Version: Latest MCP specification
- Transport: STDIO or HTTP
- Tool return type: JSON string (NEVER dict)
- Payload limits: 1000 chars for text fields, 20 items max pagination
- Error format: {success: false, error: str, suggestion: str}

### Core Logic

**Vector Search Pipeline (BaseSearchStrategy)**
```
1. Generate query embedding (OpenAI API)
2. Search Qdrant with cosine similarity
3. Filter results by similarity threshold (>= 0.05)
4. Apply metadata filters (source_id, document_id)
5. Return top-k results with scores
Target latency: <50ms p95
```

**Hybrid Search Pipeline (HybridSearchStrategy)**
```
1. Generate query embedding (OpenAI API)
2. Parallel execution:
   a. Qdrant vector search (top 100 candidates)
   b. PostgreSQL full-text search on chunks.search_vector (top 100 candidates)
3. Normalize scores to 0.0-1.0 range:
   - Vector score: 1 - cosine_distance
   - Text score: ts_rank normalized
4. Combine scores: 0.7 × vector_score + 0.3 × text_score
5. Deduplicate by chunk_id (keep highest score)
6. Sort by combined score descending
7. Return top-k results
Target latency: <100ms p95
```

**Document Ingestion Pipeline**
```
1. UPLOAD/CRAWL: Receive document (PDF/HTML/DOCX)
2. PARSE: Docling extracts text + structure (200-500ms)
3. CHUNK: Semantic chunking (~500 tokens, 50 token overlap)
4. EMBED:
   - Check cache by MD5(content)
   - Batch embed uncached chunks (100 per API call)
   - Track successes/failures in EmbeddingBatchResult
   - NEVER store null embeddings on quota exhaustion
5. STORE (Atomic transaction):
   - PostgreSQL: INSERT document, chunks (with search_vector)
   - Qdrant: Upsert vectors with minimal payload
   - Cache: Store embeddings with content hash
Total time: 650-1600ms per document
Throughput: 35-60 docs/min
```

**RAG Service Coordination (Strategy Pattern)**
```
class RAGService:
    def __init__(self):
        self.base_strategy = BaseSearchStrategy(qdrant_client)
        self.hybrid_strategy = HybridSearchStrategy(qdrant_client, db_pool) if USE_HYBRID_SEARCH
        self.reranking_strategy = RerankingStrategy() if USE_RERANKING

    async def search_documents(query, search_type):
        if search_type == "hybrid" and self.hybrid_strategy:
            return await self.hybrid_strategy.search(query)
        elif search_type == "rerank" and self.reranking_strategy:
            candidates = await self.hybrid_strategy.search(query, match_count * 5)
            return await self.reranking_strategy.rerank(query, candidates, top_k=match_count)
        else:
            return await self.base_strategy.search(query)
```

**Connection Pool Management (Critical Pattern)**
```python
# FastAPI lifespan pattern (CORRECT)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.db_pool = await asyncpg.create_pool(DATABASE_URL, min_size=10, max_size=20)
    app.state.qdrant_client = AsyncQdrantClient(QDRANT_URL)
    yield
    # Shutdown
    await app.state.db_pool.close()
    await app.state.qdrant_client.close()

# Dependency injection (CRITICAL: Return pool, not connection)
async def get_db_pool(request: Request) -> asyncpg.Pool:
    return request.app.state.db_pool

# Service usage (CRITICAL: Use async with)
async with db_pool.acquire() as conn:
    result = await conn.fetchrow("SELECT * FROM documents WHERE id = $1", doc_id)
```

### UI/CLI Requirements

**Backend API Endpoints (FastAPI)**
- GET /health - Database and Qdrant connectivity checks
- POST /api/documents - Upload and ingest document
- GET /api/documents - List documents with pagination
- GET /api/documents/{id} - Get document details
- DELETE /api/documents/{id} - Delete document (cascade to chunks and vectors)
- POST /api/search - Search with strategy selection
- GET /api/sources - List ingestion sources
- POST /api/sources - Create source
- DELETE /api/sources/{id} - Delete source (cascade to documents)

**Frontend Components (React + TypeScript)**
- DocumentList.tsx - Display paginated documents with filters
- SearchBar.tsx - Query input with strategy selector (vector/hybrid/rerank)
- SearchResults.tsx - Display results with scores and metadata
- DocumentUpload.tsx - File upload with progress tracking
- SourceManager.tsx - Manage ingestion sources

**MCP Tools CLI Interface**
```bash
# Search knowledge base
mcp search --query "FastAPI async patterns" --search-type hybrid --match-count 10

# Upload document
mcp manage-document --action create --file-path research.pdf --source-id src_123

# List documents
mcp manage-document --action list --source-id src_123 --per-page 20

# Create source
mcp manage-source --action create --title "Technical Docs" --source-type upload
```

## Similar Implementations Found in Archon

### 1. Archon RAG Service (infra/archon/python/src/server/services/)
- **Relevance**: 10/10
- **Archon Source ID**: Internal codebase reference
- **Key Patterns**:
  - Strategy pattern for search (BaseSearchStrategy, HybridSearchStrategy, RerankingStrategy)
  - Configuration-driven feature enablement (USE_HYBRID_SEARCH, USE_RERANKING)
  - Graceful degradation on strategy failures
  - 5x candidate multiplier for reranking
- **Gotchas**:
  - Similarity threshold filtering (0.05) is empirically validated
  - Reranking requires fetching more candidates than final results
  - Strategy coordinator does NOT use tuple[bool, dict] (it's not a database service)
- **Code Location**: `infra/archon/python/src/server/services/search/rag_service.py`
- **What to Reuse**:
  - Exact strategy pattern architecture
  - Configuration-driven initialization
  - Graceful degradation error handling
  - Reranking candidate expansion logic
- **What to Adapt**:
  - Replace Supabase with Qdrant + asyncpg
  - Replace credential service with Pydantic Settings + env vars
  - Simplify multi-provider embeddings to OpenAI-only for MVP

### 2. Task Manager Service Layer (infra/task-manager/backend/src/)
- **Relevance**: 9/10
- **Archon Source ID**: Internal codebase reference
- **Key Patterns**:
  - Service classes with asyncpg connection pools
  - tuple[bool, dict] return pattern for all service methods
  - exclude_large_fields parameter for MCP payload optimization
  - Validation before database operations
  - Dynamic WHERE clause building with parameterized queries
- **Gotchas**:
  - CRITICAL: Use $1, $2 placeholders (asyncpg), NOT %s (psycopg)
  - CRITICAL: Return pool from dependencies, NOT connections
  - CRITICAL: Always use async with for connection acquisition
  - ORDER BY with FOR UPDATE to prevent row locking deadlocks
- **Code Location**: `infra/task-manager/backend/src/services/task_service.py`
- **What to Reuse**:
  - Exact service layer pattern for DocumentService, SourceService
  - tuple[bool, dict] return convention
  - exclude_large_fields pattern for MCP tools
  - Connection pool setup in FastAPI lifespan
- **What to Adapt**:
  - Add VectorService for Qdrant operations (doesn't use tuple[bool, dict])
  - Add EmbeddingService for OpenAI operations
  - Coordinate with RAGService which delegates to strategies

### 3. Qdrant Configuration Example (Archon Knowledge Base)
- **Relevance**: 8/10
- **Archon Source ID**: d9ed3609bfd437c0 (mem0.ai documentation)
- **Key Patterns**:
  - Qdrant config: host, port (6333 for REST)
  - OpenAI embedder config: model=text-embedding-3-small
  - 1536 dimension vector configuration
- **Gotchas**:
  - Must explicitly set vector size at collection creation
  - Cosine distance is standard for OpenAI embeddings
- **Code Reference**:
```python
config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {"host": "localhost", "port": 6333}
    },
    "embedder": {
        "provider": "openai",
        "config": {
            "api_key": "your-api-key",
            "model": "text-embedding-3-small"
        }
    }
}
```
- **What to Reuse**:
  - Qdrant connection pattern
  - OpenAI embedding configuration
  - Dimension consistency (1536)

### 4. MCP Tools Pattern (Archon Knowledge Base)
- **Relevance**: 9/10
- **Archon Source ID**: c0e629a894699314 (Pydantic AI documentation)
- **Key Patterns**:
  - Load MCP server configurations from JSON
  - Tools return JSON strings (json.dumps() not dict)
  - Async context managers for server lifecycle
  - Tool listing and dynamic loading
- **Gotchas**:
  - MCP protocol requires string returns, not Python dicts
  - Payload truncation essential for large responses
- **Code Reference**:
```python
from pydantic_ai.mcp import load_mcp_servers

servers = load_mcp_servers('mcp_config.json')
agent = Agent('openai:gpt-5', toolsets=servers)

async with agent:
    result = await agent.run('What is 7 plus 5?')
```
- **What to Reuse**:
  - MCP server configuration pattern
  - JSON string return requirement
  - Async context manager for lifecycle
- **What to Adapt**:
  - Implement 4 RAG-specific tools (search, manage_document, manage_source, crawl)
  - Add payload optimization and pagination

## Recommended Technology Stack

Based on INITIAL.md requirements and Archon patterns:

**Backend Framework**
- **FastAPI**: Latest (async web framework with automatic OpenAPI docs)
- **Python**: 3.11+ (async improvements, performance gains)
- **Rationale**: Industry standard for async Python APIs, excellent async support

**Vector Database**
- **Qdrant**: v1.7.4+ (dedicated vector database)
- **Rationale**: 10-30ms latency at 1M vectors, simpler than alternatives (Weaviate, Milvus), native async Python client

**Relational Database**
- **PostgreSQL**: 15-alpine (metadata and full-text search)
- **asyncpg**: Latest (async PostgreSQL driver)
- **Extensions**: uuid-ossp, pg_trgm, vector (pgvector for cache)
- **Rationale**: Proven PostgreSQL + asyncpg pattern from task-manager, GIN indexes for fast full-text search

**Embedding Provider**
- **OpenAI**: text-embedding-3-small (1536 dimensions)
- **SDK**: openai Python package (latest with async support)
- **Cost**: $0.02 per 1M tokens (30% savings with caching)
- **Rationale**: Highest quality embeddings, industry standard, well-documented

**Document Parser**
- **Docling**: Latest from https://docling-project.github.io/docling/
- **Rationale**: INITIAL.md explicitly requires Docling (NOT pypdf2/pdfplumber), handles tables/layout/OCR

**Configuration Management**
- **Pydantic Settings**: v2.x (type-safe environment variable loading)
- **python-dotenv**: For .env file support
- **Rationale**: 12-factor app pattern, type safety, validation

**Frontend Stack**
- **React**: 18+ with TypeScript
- **Vite**: Latest (fast dev server, optimized builds)
- **TanStack Query**: v5 (data fetching, caching)
- **React Router**: v6 (routing)
- **Tailwind CSS**: v3 (utility-first styling)
- **Rationale**: Matches task-manager frontend stack, modern best practices

**Testing Stack**
- **pytest**: Latest (test framework)
- **pytest-asyncio**: For async test support
- **pytest-cov**: Code coverage reporting
- **httpx**: AsyncClient for API testing
- **unittest.mock.AsyncMock**: For mocking async components
- **Rationale**: Standard Python testing tools, excellent async support

**DevOps**
- **Docker Compose**: Multi-service orchestration
- **Docker**: PostgreSQL 15-alpine, Qdrant latest, custom FastAPI image
- **Rationale**: Local development simplicity, production-ready patterns

## Assumptions Made

### 1. **Deployment Environment**: Docker Compose (self-hosted)
- **Assumption**: Service will run on self-hosted infrastructure via Docker Compose
- **Reasoning**: INITIAL.md specifies Docker Compose configuration, cost estimates assume self-hosting
- **Source**: ARCHITECTURE.md lines 1222-1467 (complete docker-compose.yml)
- **Alternative Considered**: Kubernetes deployment (deferred to post-MVP)

### 2. **MVP Scope**: OpenAI embeddings only (no multi-provider)
- **Assumption**: Single embedding provider (OpenAI) sufficient for initial release
- **Reasoning**: ARCHITECTURE.md explicitly states "MVP uses OpenAI only (no multi-provider yet)" (line 345)
- **Source**: Migration notes section, Archon comparison table (lines 1971-1984)
- **Future Enhancement**: Add provider abstraction in Phase 6-8

### 3. **Frontend Scope**: Basic UI for document management and search
- **Assumption**: Frontend is for human interaction, not primary interface
- **Reasoning**: MCP tools are primary interface for agent usage, frontend is supplementary
- **Source**: Directory structure shows frontend/ but focus is on backend/MCP (lines 184-253)
- **Future Enhancement**: Advanced analytics, collaboration features (lines 442-445)

### 4. **Reranking**: Optional post-MVP feature
- **Assumption**: CrossEncoder reranking is Phase 6+ (not Phases 1-5)
- **Reasoning**: INITIAL.md Phase 5 covers MCP tools, reranking mentioned as "optional" in search pipeline
- **Source**: Implementation phases (lines 83-124), Optional reranking section (lines 547-575)
- **Future Enhancement**: Add RerankingStrategy with GPU support (lines 2110-2113)

### 5. **Web Crawling**: Optional Phase 6+ feature
- **Assumption**: crawl_website tool implementation deferred
- **Reasoning**: INITIAL.md focuses on upload/manual ingestion, crawling is "optional later"
- **Source**: Known constraints (line 347), crawl_website tool marked optional (line 2050)
- **Future Enhancement**: Implement crawl4ai integration (line 440)

### 6. **Testing Coverage**: 80% minimum, comprehensive integration tests
- **Assumption**: Need strong test coverage before production deployment
- **Reasoning**: Best practice for production services, ARCHITECTURE.md specifies 80% target
- **Source**: Testing strategy section (lines 1607-1830), coverage targets table (lines 1610-1618)
- **Validation**: CI/CD with pytest, coverage reporting

### 7. **Performance Targets**: Based on ARCHITECTURE.md benchmarks
- **Assumption**: Latency targets achievable with specified architecture
- **Reasoning**: Benchmarks from Archon implementation and research
- **Source**: Performance targets (lines 400-417), benchmarks (lines 2369-2398)
- **Validation**: Performance tests in Phase 6 (lines 2074-2078)

### 8. **Cost Estimates**: Accurate for 100K-1M document scale
- **Assumption**: Cost projections based on research are reliable
- **Reasoning**: Detailed breakdown in ARCHITECTURE.md with real-world examples
- **Source**: Cost estimates section (lines 1471-1605), scale targets table (lines 52-57)
- **Validation**: Monitor actual costs in production, optimize as needed

### 9. **Database Schema**: Complete and production-ready
- **Assumption**: 5-table schema covers all MVP requirements
- **Reasoning**: Schema includes all entities mentioned in INITIAL.md, matches Archon patterns
- **Source**: PostgreSQL schema section (lines 245-449), Appendix A (lines 2150-2309)
- **Future Migrations**: Add tables only if new features require them

### 10. **MCP Protocol Compliance**: JSON string returns, payload limits
- **Assumption**: Strict adherence to MCP protocol prevents integration issues
- **Reasoning**: Critical gotcha from research PRP, Archon MCP servers follow same pattern
- **Source**: Gotcha #6, #7 (lines 265-267), MCP tools specification (lines 812-988)
- **Validation**: MCP tool tests verify protocol compliance (line 2311)

## Success Criteria

### Phase 1 Success (Core Setup)
- [ ] Directory structure matches task-manager pattern (`backend/`, `frontend/`, `database/`)
- [ ] `docker-compose up -d` starts all services successfully (postgres, qdrant, api, frontend)
- [ ] `docker-compose ps` shows all services healthy
- [ ] PostgreSQL schema created from `database/scripts/init.sql` with all 5 tables
- [ ] All indexes present: GIN on tsvector columns, B-tree on foreign keys, composite indexes
- [ ] All triggers functional: updated_at, search_vector auto-updates
- [ ] Qdrant collection initialized: 1536 dims, cosine distance, HNSW indexing
- [ ] Health check endpoints return 200: `curl http://localhost:8000/health` (backend)
- [ ] Frontend accessible: `curl http://localhost:5173` (Vite dev server)
- [ ] Connection pools working: No deadlock errors in logs, pool metrics available
- [ ] Environment variables loaded correctly: `.env` file parsed, Pydantic Settings validates

### Phase 2 Success (Service Layer)
- [ ] DocumentService implements all CRUD: list, get, create, update, delete
- [ ] SourceService implements all CRUD: list, get, create, update, delete
- [ ] All service methods return tuple[bool, dict] consistently
- [ ] VectorService can upsert vectors to Qdrant with payload
- [ ] VectorService can search vectors by embedding with filters
- [ ] VectorService can delete vectors by document_id or chunk_id
- [ ] EmbeddingService generates embeddings via OpenAI API
- [ ] EmbeddingService handles quota exhaustion correctly (no null embeddings stored)
- [ ] EmbeddingService implements EmbeddingBatchResult pattern
- [ ] EmbeddingService checks cache before API calls (MD5 hash lookup)
- [ ] Unit tests pass for all services with >80% coverage
- [ ] No connection pool leaks: All `async with` blocks close properly

### Phase 3 Success (Search Pipeline)
- [ ] BaseSearchStrategy performs vector search via Qdrant
- [ ] BaseSearchStrategy filters by similarity threshold (>= 0.05)
- [ ] BaseSearchStrategy applies metadata filters (source_id, document_id)
- [ ] BaseSearchStrategy latency <50ms p95 (measured with 10K test queries)
- [ ] HybridSearchStrategy performs parallel vector + full-text search
- [ ] HybridSearchStrategy normalizes scores to 0.0-1.0 range
- [ ] HybridSearchStrategy combines scores: 0.7×vector + 0.3×text
- [ ] HybridSearchStrategy deduplicates by chunk_id (keeps highest score)
- [ ] HybridSearchStrategy latency <100ms p95 (measured with 10K test queries)
- [ ] RAGService coordinates strategies based on search_type parameter
- [ ] Configuration toggles work: USE_HYBRID_SEARCH enables/disables hybrid strategy
- [ ] Search results include: chunk_id, document_id, text, score, match_type, metadata
- [ ] Graceful degradation: Service continues if hybrid fails, falls back to base

### Phase 4 Success (Document Ingestion)
- [ ] Docling parser processes PDF documents successfully (tested with 10+ PDFs)
- [ ] Docling parser processes HTML documents (tested with 5+ web pages)
- [ ] Docling parser processes DOCX documents (tested with 5+ Word files)
- [ ] Semantic chunking produces ~500 token chunks with 50 token overlap
- [ ] Chunking respects boundaries: No mid-sentence cuts, tables kept intact
- [ ] Batch embedding uses OpenAI API with 100 texts per request
- [ ] EmbeddingBatchResult tracks successes and failures separately
- [ ] Quota exhaustion detected: STOP immediately, mark remaining as failed
- [ ] Cache lookup works: MD5 hash query finds existing embeddings, skips API call
- [ ] Cache hit rate 20-40% on typical workload (measured over 1000 documents)
- [ ] Atomic transaction: PostgreSQL INSERT + Qdrant upsert succeed together or rollback
- [ ] Ingestion throughput: 35-60 docs/minute (measured with 100 document batch)
- [ ] No null embeddings in Qdrant: Validation check passes on all vectors
- [ ] Error handling: Parse failures logged, document marked 'failed', no data corruption

### Phase 5 Success (MCP Tools)
- [ ] search_knowledge_base tool executes successfully via MCP protocol
- [ ] search_knowledge_base accepts parameters: query, source_id, match_count, search_type, similarity_threshold
- [ ] search_knowledge_base returns JSON string (NOT dict) per MCP spec
- [ ] manage_document tool supports all actions: create, update, delete, get, list
- [ ] manage_document validates action parameter (rejects invalid actions)
- [ ] manage_document returns JSON string with success/error structure
- [ ] manage_source tool supports all actions: create, update, delete, get, list
- [ ] manage_source returns JSON string with proper error handling
- [ ] Payload truncation works: text fields limited to 1000 chars with "..." suffix
- [ ] Pagination enforced: Maximum 20 items per page, additional items require next page
- [ ] Error format consistent: {success: false, error: str, suggestion: str}
- [ ] MCP tool tests pass: Protocol compliance verified for all 3 tools
- [ ] Integration with Archon project: Tools callable from vibes MCP configuration

### Overall Quality Gates
- [ ] All Phase 1-5 success criteria met
- [ ] Unit test coverage >80% (measured with pytest-cov)
- [ ] Integration tests pass: Full pipeline tested with real database
- [ ] Performance benchmarks met: <50ms base search, <100ms hybrid search, 35+ docs/min ingestion
- [ ] No critical security issues: API keys not committed, CORS configured, input validation present
- [ ] Documentation complete: README.md, API docs (OpenAPI), .env.example
- [ ] Docker Compose deployment verified: Clean `docker-compose up` on fresh system
- [ ] Health checks pass consistently: All services respond within 5 seconds
- [ ] Log quality: Structured logging at appropriate levels (DEBUG/INFO/WARNING/ERROR)
- [ ] No connection leaks: All async context managers properly closed

## Next Steps for Downstream Agents

### Codebase Researcher
**Focus Areas:**
1. **Task Manager Service Patterns**: Study `infra/task-manager/backend/src/services/task_service.py` for tuple[bool, dict] pattern
2. **Archon RAG Service**: Study `infra/archon/python/src/server/services/search/rag_service.py` for strategy pattern
3. **FastAPI Lifespan**: Find connection pool setup patterns in existing FastAPI apps
4. **asyncpg Patterns**: Search for `async with.*acquire` patterns to understand connection management
5. **MCP Server Implementations**: Study existing MCP servers for tool registration and JSON return patterns

**Key Questions to Answer:**
- How does task-manager implement exclude_large_fields in service methods?
- How does Archon's RAGService coordinate multiple strategies?
- What validation patterns exist for enum fields (status, priority)?
- How are async context managers used with asyncpg pools?
- What error handling patterns prevent connection leaks?

### Documentation Hunter
**Priority Documentation:**
1. **Qdrant Python Client**: AsyncQdrantClient API reference, collection creation, upsert/search patterns
   - URL: https://qdrant.tech/documentation/
   - Focus: Async client methods, HNSW configuration, payload filtering
2. **asyncpg**: Connection pooling, query parameterization ($1, $2), transaction management
   - URL: https://magicstack.github.io/asyncpg/current/
   - Focus: Pool configuration, cursor patterns, error handling
3. **OpenAI Embeddings**: text-embedding-3-small API, batch processing, rate limit handling
   - URL: https://platform.openai.com/docs/guides/embeddings
   - Focus: Batch API calls, rate limit headers, quota exhaustion errors
4. **Docling**: Document parsing API, supported formats, chunking integration
   - URL: https://docling-project.github.io/docling/
   - Focus: PDF parsing, table extraction, output format
5. **FastAPI Lifespan**: Async context manager for app lifecycle, dependency injection
   - URL: https://fastapi.tiangolo.com/advanced/events/
   - Focus: lifespan parameter, startup/shutdown hooks, state management

**Specific Sections to Extract:**
- Qdrant: Collection creation with HNSW, search with metadata filters
- asyncpg: Pool min_size/max_size configuration, placeholder syntax
- OpenAI: Batch embedding request format, RateLimitError handling
- Docling: Supported MIME types, parsing options, output structure
- FastAPI: app.state usage for connection pools, dependency injection

### Example Curator
**Extraction Goals:**
1. **Service Layer Examples**: Extract complete service class with tuple[bool, dict] pattern
   - Source: `prps/rag_service_research/examples/01_service_layer_pattern.py`
   - Focus: __init__ with db_pool, list/get/create methods, error handling
2. **RAG Search Pipeline**: Extract strategy coordinator pattern
   - Source: `prps/rag_service_research/examples/03_rag_search_pipeline.py`
   - Focus: Strategy initialization, search method delegation, graceful degradation
3. **Hybrid Search**: Extract score combining logic
   - Source: `prps/rag_service_research/examples/05_hybrid_search_strategy.py`
   - Focus: Parallel query execution, score normalization, deduplication
4. **MCP Tool Pattern**: Extract tool with JSON string return
   - Source: `prps/rag_service_research/examples/02_mcp_consolidated_tools.py`
   - Focus: @mcp.tool() decorator, parameter validation, json.dumps() return
5. **Transaction Pattern**: Extract atomic multi-step operation
   - Source: `prps/rag_service_research/examples/06_transaction_pattern.py`
   - Focus: BEGIN/COMMIT/ROLLBACK, error handling, cleanup

**Code Snippet Priorities:**
- Complete service class initialization (db_pool parameter)
- List method with pagination and exclude_large_fields
- Create method with validation and tuple[bool, dict] return
- RAGService __init__ with strategy initialization
- Hybrid search score combining formula
- MCP tool with JSON string return validation
- Transaction with asyncpg pool and error handling

### Gotcha Detective
**Critical Investigation Areas:**
1. **OpenAI Quota Exhaustion**: How to detect and prevent null embeddings
   - Search Pattern: "insufficient_quota", "RateLimitError", "EmbeddingBatchResult"
   - Find: Code that stops immediately on quota exhaustion, tracks failures
2. **asyncpg Connection Pool Deadlock**: Why returning connections causes issues
   - Search Pattern: "db_pool.acquire", "depends_on", "get_db_pool"
   - Find: Patterns that return pool (correct) vs connection (incorrect)
3. **asyncpg Placeholder Syntax**: Why $1, $2 is required (not %s)
   - Search Pattern: "fetchrow.*\$\d", "execute.*\$\d"
   - Find: Examples of correct parameterized queries
4. **Row Locking Deadlock**: Why ORDER BY is needed with FOR UPDATE
   - Search Pattern: "FOR UPDATE", "ORDER BY.*FOR UPDATE"
   - Find: Examples that prevent deadlock with proper ordering
5. **Qdrant Dimension Mismatch**: How to validate vector length before insert
   - Search Pattern: "dimension", "vector.length", "validate.*embedding"
   - Find: Validation code that checks len(embedding) == 1536
6. **MCP JSON String Return**: Why tools must return strings not dicts
   - Search Pattern: "json.dumps", "MCP.*return", "tool.*str"
   - Find: Examples that explicitly convert dict to JSON string
7. **MCP Payload Size**: How to truncate large content fields
   - Search Pattern: "truncate", "MAX_CONTENT_LENGTH", "[:1000]"
   - Find: Utility functions for content truncation
8. **Connection Leaks**: Why async with is critical
   - Search Pattern: "async with.*acquire", "connection leak"
   - Find: Examples of proper context manager usage

**Documentation Priorities:**
- Gotcha #1: EmbeddingBatchResult pattern with example code
- Gotcha #2: FastAPI dependency injection returning pool
- Gotcha #3: asyncpg placeholder syntax comparison ($1 vs %s)
- Gotcha #5: Vector dimension validation before Qdrant insert
- Gotcha #6: MCP tool return type enforcement
- Gotcha #7: Content truncation utility function
- Gotcha #8: Async context manager examples

**Expected Deliverables:**
- List of 8+ critical gotchas with explanations
- Code examples showing correct vs incorrect patterns
- Links to documentation sections explaining each gotcha
- Validation tests to detect gotcha violations
- Mitigation strategies for each potential issue

## Implementation Phases Analysis

### Phase 1: Core Setup (Week 1) - Foundation
**Complexity**: Medium
**Dependencies**: None (greenfield setup)
**Risk Level**: Low
**Key Deliverables**:
- Directory structure matching task-manager pattern
- Docker Compose with 4 services (postgres, qdrant, api, frontend)
- PostgreSQL schema with all 5 tables, indexes, triggers
- Qdrant collection with 1536-dim vectors, cosine distance
- FastAPI app with lifespan connection pools
- Health check endpoints
- .env.example template

**Critical Path Items**:
1. PostgreSQL schema correctness (triggers, indexes, constraints)
2. Qdrant collection initialization (dimension, distance metric)
3. Connection pool configuration (min_size, max_size)
4. Health check validation (both databases accessible)

**Success Metrics**: All services start, health checks pass, schema complete

---

### Phase 2: Service Layer (Week 2) - Business Logic
**Complexity**: High
**Dependencies**: Phase 1 complete (database schema, connection pools)
**Risk Level**: Medium (connection pool patterns critical)
**Key Deliverables**:
- DocumentService (list, get, create, update, delete)
- SourceService (list, get, create, update, delete)
- VectorService (upsert, search, delete for Qdrant)
- EmbeddingService (OpenAI integration, batch processing, cache)
- Unit tests for all services (>80% coverage)

**Critical Path Items**:
1. tuple[bool, dict] pattern implementation consistency
2. exclude_large_fields for MCP payload optimization
3. asyncpg placeholder syntax ($1, $2 not %s)
4. EmbeddingBatchResult pattern for quota exhaustion
5. Embedding cache lookup by MD5 hash

**Success Metrics**: All CRUD operations work, no connection leaks, quota exhaustion handled

---

### Phase 3: Search Pipeline (Week 3) - Core RAG Functionality
**Complexity**: Very High
**Dependencies**: Phase 2 complete (VectorService, EmbeddingService)
**Risk Level**: High (performance targets, score combining logic)
**Key Deliverables**:
- BaseSearchStrategy (vector similarity search)
- HybridSearchStrategy (vector + full-text combined)
- RAGService coordinator (strategy pattern)
- Configuration-driven strategy selection
- Result merging and deduplication

**Critical Path Items**:
1. Vector search latency <50ms p95
2. Hybrid search latency <100ms p95
3. Score normalization to 0.0-1.0 range (CRITICAL)
4. Score combining formula: 0.7×vector + 0.3×text (validated)
5. Deduplication by chunk_id (keep highest score)
6. Similarity threshold filtering (>= 0.05)
7. Graceful degradation when strategies fail

**Success Metrics**: Latency targets met, hybrid search more accurate than base, graceful failures

---

### Phase 4: Document Ingestion (Week 4) - Data Pipeline
**Complexity**: Very High
**Dependencies**: Phase 2 complete (services), Phase 3 helpful but not blocking
**Risk Level**: High (quota exhaustion, atomic transactions, parsing edge cases)
**Key Deliverables**:
- Docling parser integration (PDF, HTML, DOCX)
- Semantic chunking (~500 tokens, 50 token overlap)
- Batch embedding with OpenAI (100 texts per request)
- EmbeddingBatchResult pattern implementation
- Atomic storage (PostgreSQL + Qdrant transaction)
- Embedding cache with MD5 hash lookup

**Critical Path Items**:
1. Docling installation and configuration
2. Semantic chunking boundary respect (no mid-sentence cuts)
3. Table preservation during chunking
4. Batch embedding API calls (100 texts)
5. Quota exhaustion detection (STOP immediately, no null embeddings)
6. EmbeddingBatchResult tracks successes/failures separately
7. Atomic transaction: Both databases succeed or rollback
8. Cache hit rate 20-40% validation
9. Ingestion throughput 35-60 docs/min

**Success Metrics**: 100+ documents ingested successfully, no null embeddings, throughput target met

---

### Phase 5: MCP Tools (Week 5) - Agent Interface
**Complexity**: Medium
**Dependencies**: Phase 2 (services), Phase 3 (search), Phase 4 (ingestion) complete
**Risk Level**: Medium (MCP protocol compliance)
**Key Deliverables**:
- search_knowledge_base tool
- manage_document tool (consolidated CRUD)
- manage_source tool (consolidated CRUD)
- JSON string returns (not dicts)
- Payload truncation (1000 chars max)
- Pagination limits (20 items max)

**Critical Path Items**:
1. MCP protocol compliance: JSON string returns (json.dumps())
2. Payload optimization: Truncate content to 1000 chars
3. Pagination enforcement: Max 20 items per page
4. Error format consistency: {success, error, suggestion}
5. Action parameter validation (create/update/delete/get/list)
6. Integration with vibes MCP configuration

**Success Metrics**: All tools callable via MCP, protocol tests pass, Archon project integration works

---

### Phase 6-8: Testing, Documentation, Deployment (Weeks 6-8) - Production Readiness
**Complexity**: High
**Dependencies**: All phases 1-5 complete
**Risk Level**: Low (validation and polish)
**Key Deliverables**:
- Unit tests (80% coverage)
- Integration tests (full pipeline)
- Performance tests (latency benchmarks)
- MCP tool tests (protocol compliance)
- API documentation (OpenAPI/Swagger)
- Deployment guide
- Troubleshooting guide
- Production docker-compose.yml
- Monitoring and alerting setup
- Backup procedures

**Critical Path Items**:
1. Performance benchmarks confirm targets
2. Load testing at expected scale (100 concurrent requests)
3. Security review (API keys, CORS, rate limiting)
4. Cost analysis at production scale
5. Monitoring dashboards (latency, errors, costs)
6. Backup and restore procedures tested

**Success Metrics**: Production deployment succeeds, monitoring works, documentation complete

## Critical Design Decisions

### 1. **Vector Database: Qdrant (not pgvector)**
**Decision**: Use dedicated Qdrant vector database instead of pgvector extension
**Rationale**:
- Performance: 10-30ms vs 50-100ms at 1M vectors (2-3x faster)
- Scalability: Handles 10M+ vectors efficiently, pgvector degrades after 5M
- Native async support: AsyncQdrantClient prevents event loop blocking
- Memory efficiency: 2.5GB per 1M vectors vs 2.8GB for pgvector
**Trade-offs**: Additional service to manage, dual storage pattern
**Source**: ARCHITECTURE.md vector database comparison (lines 175-243)
**Validation**: Archon uses dedicated vector DB (Supabase), pattern proven

### 2. **Dual Storage Pattern: PostgreSQL + Qdrant**
**Decision**: Store metadata in PostgreSQL, vectors in Qdrant (not all-in-one)
**Rationale**:
- PostgreSQL: Source of truth for metadata, full-text search, analytics
- Qdrant: Fast vector retrieval, payload filtering, HNSW indexing
- Operational simplicity: Each database optimized for its purpose
**Trade-offs**: 20% storage overhead (text in both), cross-database queries
**Source**: ARCHITECTURE.md schema design (lines 245-449)
**Validation**: Archon uses dual storage (Supabase + Supabase vectors), pattern proven

### 3. **Service Layer Return Pattern: tuple[bool, dict]**
**Decision**: All service methods return tuple[bool, dict] for consistent error handling
**Rationale**:
- Consistency: Task-manager pattern proven in production
- Error handling: Caller can check success without exceptions
- MCP integration: Easy to convert to JSON string response
**Trade-offs**: RAGService coordinator doesn't use pattern (raises exceptions)
**Source**: Task-manager service layer (example file lines 28-172)
**Validation**: Task-manager in production, Archon uses similar pattern

### 4. **Strategy Pattern for Search: Coordinator + Strategies**
**Decision**: Thin RAGService coordinator delegates to fat strategy implementations
**Rationale**:
- Separation of concerns: Each strategy independently testable
- Configuration-driven: Enable/disable strategies without code changes
- Graceful degradation: Service continues if advanced strategies fail
**Trade-offs**: More classes to maintain, coordinator doesn't do database operations
**Source**: Archon RAGService (example file lines 31-146)
**Validation**: Archon production pattern, proven in 1M+ queries

### 5. **Hybrid Search Weights: 0.7×vector + 0.3×text**
**Decision**: Weight vector similarity 70%, full-text search 30%
**Rationale**:
- Empirically validated: Archon production tuning
- Semantic understanding primary: Vector captures meaning
- Keyword precision: Text rank adds exact match accuracy
**Trade-offs**: Fixed weights (not adaptive), may need tuning per dataset
**Source**: ARCHITECTURE.md hybrid search (lines 509-547)
**Validation**: Archon production metrics, industry research

### 6. **Embedding Provider: OpenAI Only (MVP)**
**Decision**: Use only OpenAI text-embedding-3-small for MVP, defer multi-provider
**Rationale**:
- Simplicity: Single provider reduces complexity by 3x
- Quality: OpenAI embeddings are industry standard
- Cost: $0.02 per 1M tokens is competitive
**Trade-offs**: Vendor lock-in, no cost comparison
**Source**: ARCHITECTURE.md migration notes (lines 1900-1905)
**Validation**: Can add providers post-MVP if needed

### 7. **Document Parser: Docling (not pypdf2/pdfplumber)**
**Decision**: Use Docling for all document parsing (PDF, HTML, DOCX)
**Rationale**:
- INITIAL.md explicit requirement (line 131)
- Comprehensive: Handles tables, layout, OCR, multi-column
- Output structure: Ready for semantic chunking
**Trade-offs**: Larger dependency, 200-500ms per document
**Source**: INITIAL.md lines 126-135
**Validation**: Archon research PRP recommends Docling

### 8. **Chunking Strategy: Semantic with Overlap**
**Decision**: ~500 token chunks with 50 token overlap, respect boundaries
**Rationale**:
- Context preservation: Overlap prevents context loss at boundaries
- Boundary respect: No mid-sentence cuts, tables kept intact
- Token budget: 500 tokens fits in most LLM context windows with room for query
**Trade-offs**: 10% storage overhead from overlap, chunking complexity
**Source**: ARCHITECTURE.md ingestion pipeline (lines 665-809)
**Validation**: Industry standard pattern (LangChain, LlamaIndex)

### 9. **Quota Exhaustion Handling: EmbeddingBatchResult Pattern**
**Decision**: NEVER store null embeddings, track successes/failures separately
**Rationale**:
- Data integrity: Null embeddings corrupt vector search (match every query equally)
- Observability: Separate tracking shows partial successes
- Recovery: Can retry only failed items
**Trade-offs**: More complex error handling, partial ingestion possible
**Source**: ARCHITECTURE.md critical pattern (lines 706-745)
**Validation**: Archon gotcha #1, real production incident

### 10. **MCP Protocol: JSON String Returns (not dicts)**
**Decision**: All MCP tools return json.dumps() strings, never Python dicts
**Rationale**:
- Protocol compliance: MCP specification requires string returns
- Serialization control: Explicit control over JSON encoding
- Error prevention: Type system prevents dict returns
**Trade-offs**: Extra json.dumps() call, harder to test (must parse)
**Source**: ARCHITECTURE.md gotcha #6 (line 265)
**Validation**: Archon MCP servers, Pydantic AI documentation

### 11. **Connection Pool: Return Pool (not Connection) from Dependencies**
**Decision**: FastAPI dependencies return db_pool, not acquired connections
**Rationale**:
- Deadlock prevention: Services acquire/release connections as needed
- Resource management: Pool shared across requests prevents exhaustion
- Correct pattern: Task-manager proven implementation
**Trade-offs**: Services must remember to use async with
**Source**: ARCHITECTURE.md gotcha #2, service pattern (lines 1102-1154)
**Validation**: Task-manager production pattern

### 12. **Frontend Scope: Basic UI (not advanced analytics)**
**Decision**: Simple document management and search UI for MVP
**Rationale**:
- Primary interface is MCP tools (for agents)
- Frontend is supplementary (for human oversight)
- Time constraint: 8-week timeline focuses on backend/MCP
**Trade-offs**: Limited UI features, no real-time updates
**Source**: INITIAL.md phases 1-5 focus, post-MVP enhancements (lines 442-445)
**Validation**: Archon doesn't have frontend, proves agent-first approach

---

## Risk Assessment & Mitigation

### High Risks

**Risk 1: OpenAI Quota Exhaustion Corruption**
- **Impact**: High (data corruption, null embeddings break search)
- **Probability**: Medium (depends on quota limit, batch size)
- **Mitigation**: EmbeddingBatchResult pattern, immediate stop on quota error, retry queue
- **Validation**: Unit tests with quota exhaustion simulation
- **Reference**: ARCHITECTURE.md gotcha #1 (lines 706-745)

**Risk 2: Connection Pool Deadlock**
- **Impact**: High (service unavailable, timeouts)
- **Probability**: Medium (easy to misconfigure)
- **Mitigation**: Return pool from dependencies (not connections), load testing
- **Validation**: 100 concurrent request test, monitor pool metrics
- **Reference**: ARCHITECTURE.md gotcha #2 (lines 1102-1154)

**Risk 3: Search Latency Exceeds Targets**
- **Impact**: High (poor user experience, agent timeouts)
- **Probability**: Medium (depends on data volume, query complexity)
- **Mitigation**: HNSW indexing, parallel queries, caching, performance tests
- **Validation**: Latency benchmarks at 100K, 1M, 10M vectors
- **Reference**: ARCHITECTURE.md performance targets (lines 400-417)

### Medium Risks

**Risk 4: Qdrant Dimension Mismatch**
- **Impact**: Medium (runtime errors, failed inserts)
- **Probability**: Low (validation prevents)
- **Mitigation**: Validate vector length before insert, unit tests
- **Validation**: Test with wrong dimension vectors
- **Reference**: ARCHITECTURE.md gotcha #5 (line 263)

**Risk 5: MCP Protocol Violations**
- **Impact**: Medium (integration failures with Archon)
- **Probability**: Low (tests catch)
- **Mitigation**: JSON string return enforcement, protocol compliance tests
- **Validation**: MCP tool test suite, integration with Archon project
- **Reference**: ARCHITECTURE.md gotchas #6, #7 (lines 265-267)

**Risk 6: Document Parsing Failures**
- **Impact**: Medium (some documents not ingested)
- **Probability**: Medium (diverse document formats)
- **Mitigation**: Robust error handling, mark documents 'failed', manual retry
- **Validation**: Test with 100+ diverse documents (PDFs, HTML, DOCX)
- **Reference**: ARCHITECTURE.md error handling (lines 746-762)

### Low Risks

**Risk 7: Frontend Build Issues**
- **Impact**: Low (MCP tools are primary interface)
- **Probability**: Low (Vite standard setup)
- **Mitigation**: Use proven Vite + React setup, minimal custom configuration
- **Validation**: Frontend build succeeds, dev server accessible

**Risk 8: Docker Compose Configuration**
- **Impact**: Low (local development only)
- **Probability**: Low (well-documented pattern)
- **Mitigation**: Use ARCHITECTURE.md template, health checks, depends_on
- **Validation**: Clean docker-compose up on fresh system

---

## Appendix: File Structure Reference

Based on INITIAL.md lines 180-253, target directory structure:

```
/Users/jon/source/vibes/infra/rag-service/
├── backend/
│   ├── src/
│   │   ├── main.py                          # FastAPI app with lifespan
│   │   ├── mcp_server.py                    # MCP server entry point
│   │   ├── config/
│   │   │   ├── settings.py                  # Pydantic Settings
│   │   │   └── database.py                  # asyncpg + Qdrant pool setup
│   │   ├── models/
│   │   │   ├── document.py                  # Pydantic models
│   │   │   ├── source.py
│   │   │   └── chunk.py
│   │   ├── services/
│   │   │   ├── document_service.py          # DocumentService (tuple[bool, dict])
│   │   │   ├── source_service.py            # SourceService (tuple[bool, dict])
│   │   │   ├── vector_service.py            # VectorService (Qdrant operations)
│   │   │   ├── embeddings/
│   │   │   │   └── embedding_service.py     # EmbeddingService (OpenAI)
│   │   │   └── search/
│   │   │       ├── rag_service.py           # RAGService coordinator
│   │   │       ├── base_search_strategy.py  # Vector search
│   │   │       └── hybrid_search_strategy.py # Vector + text combined
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── health.py                # Health check endpoints
│   │   │   │   ├── documents.py             # Document CRUD endpoints
│   │   │   │   └── search.py                # Search endpoints
│   │   │   └── dependencies.py              # FastAPI dependencies (get_db_pool)
│   │   ├── tools/
│   │   │   ├── search_tools.py              # MCP search_knowledge_base
│   │   │   ├── document_tools.py            # MCP manage_document
│   │   │   └── source_tools.py              # MCP manage_source
│   │   └── utils/
│   │       ├── logging.py                   # Logging configuration
│   │       └── response.py                  # MCP payload optimization
│   ├── tests/
│   │   ├── unit/                            # Unit tests (AsyncMock)
│   │   ├── integration/                     # Integration tests (test DB)
│   │   └── mcp/                             # MCP protocol tests
│   ├── Dockerfile                           # Production FastAPI image
│   ├── requirements.txt                     # Python dependencies
│   └── pyproject.toml                       # Project metadata, pytest config
├── database/
│   ├── migrations/
│   │   └── 001_initial_schema.sql           # Migration scripts (future)
│   ├── seeds/
│   │   └── README.md                        # Sample data documentation
│   └── scripts/
│       └── init.sql                         # Initial schema (5 tables, indexes, triggers)
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── DocumentList.tsx             # Document listing with pagination
│   │   │   ├── SearchBar.tsx                # Query input, strategy selector
│   │   │   └── SearchResults.tsx            # Display results with scores
│   │   ├── pages/
│   │   │   ├── Documents.tsx                # Document management page
│   │   │   └── Search.tsx                   # Search interface page
│   │   ├── services/
│   │   │   └── api.ts                       # API client (axios/fetch)
│   │   ├── App.tsx                          # Main app component
│   │   └── main.tsx                         # Entry point
│   ├── package.json                         # Node dependencies
│   ├── tsconfig.json                        # TypeScript configuration
│   └── vite.config.ts                       # Vite dev server config
├── docker-compose.yml                       # Development environment
├── .env.example                             # Environment variable template
└── README.md                                # Setup and usage guide
```

---

**Document Complete**
**Word Count**: ~8,500 words
**Sections**: 12 major sections + appendix
**Ready For**: Phase 2 parallel research agents (Codebase Researcher, Documentation Hunter, Example Curator, Gotcha Detective)
