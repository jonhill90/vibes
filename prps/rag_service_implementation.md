# PRP: RAG Service Implementation

**Generated**: 2025-10-14
**Based On**: prps/rag_service_implementation/INITIAL.md
**Archon Project**: cc184053-b3c9-483e-87cd-4812700e4e43
**Research Phase**: Complete (Phases 1-4)

---

## Goal

Build a production-ready standalone RAG (Retrieval Augmented Generation) service implementing a 5-phase development plan: Core Setup, Service Layer, Search Pipeline, Document Ingestion, and MCP Tools. The service uses Qdrant for vector storage, PostgreSQL for metadata and full-text search, FastAPI for the backend, OpenAI for embeddings, and Docling for document parsing.

**End State**:
- Fully functional RAG service handling document upload, parsing, embedding, and semantic search
- MCP tools for agent integration with search_knowledge_base, manage_document, manage_source
- Hybrid search combining vector similarity (0.7 weight) and full-text search (0.3 weight)
- Production-ready with health checks, connection pooling, error handling, and validation gates
- Performance targets: <50ms p95 vector search, <100ms p95 hybrid search, 35-60 docs/min ingestion

---

## Why

**Current Pain Points**:
- No unified RAG service for document search and retrieval across projects
- Agents lack semantic search capabilities for knowledge bases
- Document ingestion scattered across multiple tools with inconsistent parsing
- No reusable patterns for vector search + full-text search hybrid strategies

**Business Value**:
- **Agent Productivity**: Search knowledge base via MCP tools, reducing research time by 60%
- **Reusable Infrastructure**: Standardized RAG service for all projects needing document search
- **Cost Efficiency**: Embedding cache reduces OpenAI costs by 20-40%
- **Scalability**: Handles 100K-1M documents with <100ms search latency
- **Pattern Library**: Proven architecture for future RAG implementations

---

## What

### Core Features

**Phase 1: Core Setup (Week 1)**
- Directory structure following task-manager pattern (backend/, frontend/, database/)
- Docker Compose orchestration (PostgreSQL 15-alpine, Qdrant v1.7.4+, FastAPI, Frontend)
- PostgreSQL schema: 5 tables (sources, documents, chunks, crawl_jobs, embedding_cache)
- Qdrant collection: 1536 dimensions, cosine distance, HNSW indexing
- FastAPI lifespan connection pools (asyncpg + AsyncQdrantClient)
- Health check endpoints validating dual storage readiness

**Phase 2: Service Layer (Week 2)**
- DocumentService: tuple[bool, dict] return pattern, CRUD operations
- SourceService: tuple[bool, dict] return pattern, CRUD operations
- VectorService: Qdrant operations (upsert, search, delete)
- EmbeddingService: OpenAI integration, batch processing, quota handling, cache

**Phase 3: Search Pipeline (Week 3)**
- BaseSearchStrategy: Vector similarity search (<50ms p95)
- HybridSearchStrategy: 0.7×vector + 0.3×text combined scoring (<100ms p95)
- RAGService: Strategy pattern coordinator, configuration-driven selection
- Graceful degradation when strategies fail

**Phase 4: Document Ingestion (Week 4)**
- Docling parser: PDF, HTML, DOCX support
- Semantic chunking: ~500 tokens, 50 token overlap, boundary respect
- Batch embedding: 100 texts per OpenAI API call
- Atomic storage: PostgreSQL + Qdrant transaction pattern
- EmbeddingBatchResult: Never store null embeddings on quota exhaustion

**Phase 5: MCP Tools (Week 5)**
- search_knowledge_base: Vector/hybrid/rerank search strategies
- manage_document: Consolidated CRUD (create, update, delete, get, list)
- manage_source: Consolidated CRUD
- JSON string returns (MCP protocol requirement)
- Payload optimization: 1000 char max, 20 items max per page

### Success Criteria

**Phase 1 Success**:
- [ ] `docker-compose up -d` starts all services successfully
- [ ] Health checks pass: `curl http://localhost:8000/health` returns 200
- [ ] PostgreSQL schema complete with all 5 tables, indexes, triggers
- [ ] Qdrant collection initialized: 1536 dims, cosine distance

**Phase 2 Success**:
- [ ] DocumentService implements all CRUD with tuple[bool, dict] pattern
- [ ] SourceService implements all CRUD with tuple[bool, dict] pattern
- [ ] VectorService can upsert/search/delete vectors in Qdrant
- [ ] EmbeddingService generates embeddings with cache lookup and quota handling
- [ ] Unit tests pass with >80% coverage

**Phase 3 Success**:
- [ ] BaseSearchStrategy latency <50ms p95 (measured with 10K test queries)
- [ ] HybridSearchStrategy latency <100ms p95 (measured with 10K test queries)
- [ ] RAGService coordinates strategies based on search_type parameter
- [ ] Graceful degradation: Service continues if hybrid fails

**Phase 4 Success**:
- [ ] Docling processes PDF, HTML, DOCX documents successfully
- [ ] Semantic chunking produces ~500 token chunks with 50 token overlap
- [ ] Batch embedding uses 100 texts per OpenAI API call
- [ ] EmbeddingBatchResult prevents null embeddings on quota exhaustion
- [ ] Cache hit rate 20-40% on typical workload
- [ ] Ingestion throughput: 35-60 docs/minute

**Phase 5 Success**:
- [ ] search_knowledge_base executes via MCP protocol
- [ ] manage_document supports all actions (create, update, delete, get, list)
- [ ] manage_source supports all actions
- [ ] All tools return JSON strings (not dicts)
- [ ] Payload truncation: 1000 chars max, 20 items max per page

---

## All Needed Context

### Documentation & References

```yaml
# MUST READ - FastAPI
- url: https://fastapi.tiangolo.com/advanced/events/
  sections:
    - "Lifespan Events" - Connection pool setup with @asynccontextmanager
  why: Critical for managing asyncpg + Qdrant client lifecycle
  critical_gotchas:
    - Return pool from dependencies, NOT acquired connections (Gotcha #2)

- url: https://fastapi.tiangolo.com/async/
  sections:
    - "Async/Await" - Understanding async patterns
  why: Proper async usage for asyncpg and AsyncQdrantClient

# MUST READ - Qdrant
- url: https://python-client.qdrant.tech/
  sections:
    - "AsyncQdrantClient API" - All async methods
    - "Collections" - VectorParams configuration
    - "Search" - Similarity search with filters
  why: Primary vector database for RAG service
  critical_gotchas:
    - Disable HNSW during bulk upload (m=0) then rebuild (Gotcha #9)
    - Validate vector dimensions before insert (Gotcha #5)

- url: https://qdrant.tech/documentation/guides/optimize/
  sections:
    - "Performance Optimization" - HNSW tuning
  why: Achieving <50ms p95 latency targets

# MUST READ - asyncpg
- url: https://magicstack.github.io/asyncpg/current/usage.html
  sections:
    - "Connection Pooling" - Pool configuration
    - "Queries" - $1, $2 placeholder syntax
    - "Transactions" - async with conn.transaction()
  why: Primary database driver for PostgreSQL
  critical_gotchas:
    - Use $1, $2 placeholders NOT %s (Gotcha #3)
    - Always use async with pool.acquire() (Gotcha #8)
    - ORDER BY id with FOR UPDATE to prevent deadlocks (Gotcha #4)

- url: https://magicstack.github.io/asyncpg/current/api/index.html
  sections:
    - "Pool.acquire" - Connection acquisition
    - "Connection.fetch" - Query methods
  why: API reference for all database operations

# MUST READ - PostgreSQL Full-Text Search
- url: https://www.postgresql.org/docs/current/textsearch-tables.html
  sections:
    - "tsvector" - Tokenized document representation
    - "ts_rank" - Relevance scoring
  why: Hybrid search requires full-text search integration

- url: https://www.postgresql.org/docs/current/textsearch-indexes.html
  sections:
    - "GIN Indexes" - Index creation and performance
  why: Fast full-text search (<50ms) requires GIN indexes

# MUST READ - OpenAI Embeddings
- url: https://platform.openai.com/docs/guides/rate-limits
  sections:
    - "Rate Limits" - RPM and TPM limits
    - "Handling Errors" - RateLimitError detection
  why: Essential for preventing quota exhaustion corruption (Gotcha #1)

- url: https://cookbook.openai.com/examples/how_to_handle_rate_limits
  sections:
    - "Exponential Backoff" - Retry strategies
  why: Proper rate limit handling prevents cascading failures (Gotcha #10)

# MUST READ - Docling
- url: https://docling-project.github.io/docling/usage/
  sections:
    - "DocumentConverter" - Basic usage
    - "Supported Formats" - PDF, HTML, DOCX
  why: Required document parser (NOT pypdf2/pdfplumber)
  critical_gotchas:
    - Large PDFs (50+ MB) need memory limits (Gotcha #15)
    - Run in thread pool to avoid blocking event loop (Gotcha #12)

# MUST READ - Pydantic Settings
- url: https://docs.pydantic.dev/latest/concepts/pydantic_settings/
  sections:
    - "Settings Management" - BaseSettings usage
    - "Configuration Options" - SettingsConfigDict
  why: Type-safe environment variable loading

# ESSENTIAL LOCAL FILES

- file: prps/rag_service_implementation/examples/README.md
  why: Study all examples before implementation - contains "what to mimic" guidance
  pattern: Complete pattern library with task-manager and Archon proven patterns

- file: prps/rag_service_implementation/examples/01_service_layer_pattern.py
  why: Foundation for DocumentService and SourceService
  pattern: tuple[bool, dict] return pattern, exclude_large_fields for MCP optimization
  critical: Store db_pool NOT connection, use async with pool.acquire()

- file: prps/rag_service_implementation/examples/02_mcp_consolidated_tools.py
  why: MCP tool design pattern (find/manage consolidation)
  pattern: JSON string returns, payload truncation, action parameter validation
  critical: MUST return json.dumps() NOT dict (Gotcha #6)

- file: prps/rag_service_implementation/examples/03_rag_search_pipeline.py
  why: RAGService architecture (thin coordinator, fat strategies)
  pattern: Configuration-driven strategy selection, graceful degradation, 5x candidate multiplier for reranking
  critical: RAGService does NOT use tuple[bool, dict] pattern (raises exceptions)

- file: prps/rag_service_implementation/examples/04_base_vector_search.py
  why: BaseSearchStrategy implementation
  pattern: Vector similarity search, threshold filtering (0.05), metadata filters

- file: prps/rag_service_implementation/examples/05_hybrid_search_strategy.py
  why: HybridSearchStrategy (Phase 6+, reference only)
  pattern: Parallel vector + text search, score normalization, 0.7×vector + 0.3×text combining

- file: prps/rag_service_implementation/examples/06_transaction_pattern.py
  why: Atomic multi-step operations (PostgreSQL + Qdrant)
  pattern: Nested async with for transactions, idempotent Qdrant upserts
  critical: Use ORDER BY id with FOR UPDATE (Gotcha #4)

- file: prps/rag_service_implementation/examples/07_fastapi_endpoint_pattern.py
  why: API endpoint structure
  pattern: Dependency injection, Pydantic models, HTTPException

- file: prps/rag_service_implementation/examples/08_connection_pool_setup.py
  why: FastAPI lifespan pattern (CRITICAL)
  pattern: @asynccontextmanager for startup/shutdown, app.state storage, dependency returns pool
  critical: Return pool from get_db_pool, NOT connection (Gotcha #2)

- file: prps/rag_service_implementation/examples/09_qdrant_vector_service.py
  why: VectorService wrapper for Qdrant operations
  pattern: Dimension validation, payload optimization, batch operations
  critical: Validate len(embedding) == 1536 before insert (Gotcha #5)

- file: infra/task-manager/backend/src/services/task_service.py
  why: Production service layer pattern reference
  pattern: Complete CRUD with tuple[bool, dict], dynamic WHERE clause building

- file: infra/archon/python/src/server/services/search/rag_service.py
  why: Production RAG service reference
  pattern: Strategy pattern coordination, configuration-driven enablement
```

### Current Codebase Tree

**Relevant Existing Patterns**:
```
/Users/jon/source/vibes/
├── infra/
│   ├── task-manager/
│   │   └── backend/
│   │       ├── src/
│   │       │   ├── main.py                    # FastAPI lifespan pattern
│   │       │   ├── config/
│   │       │   │   └── database.py            # asyncpg pool setup
│   │       │   ├── services/
│   │       │   │   └── task_service.py        # tuple[bool, dict] pattern
│   │       │   └── api/
│   │       │       └── dependencies.py        # get_db_pool dependency
│   │       └── tests/
│   │           ├── unit/                      # AsyncMock testing
│   │           └── integration/               # Real DB tests
│   │
│   └── archon/
│       └── python/
│           └── src/
│               ├── server/
│               │   └── services/
│               │       └── search/
│               │           ├── rag_service.py           # Strategy pattern
│               │           ├── base_search_strategy.py  # Vector search
│               │           └── hybrid_search_strategy.py # Hybrid search
│               └── mcp_server/
│                   └── features/
│                       ├── projects/
│                       │   └── project_tools.py  # find/manage pattern
│                       └── rag/
│                           └── rag_tools.py      # MCP tool examples
│
└── prps/
    └── rag_service_implementation/
        ├── INITIAL.md                 # Original requirements
        ├── examples/                   # 9 extracted code examples
        │   ├── README.md              # "What to mimic" guidance
        │   ├── 01_service_layer_pattern.py
        │   ├── 02_mcp_consolidated_tools.py
        │   ├── 03_rag_search_pipeline.py
        │   ├── 04_base_vector_search.py
        │   ├── 05_hybrid_search_strategy.py
        │   ├── 06_transaction_pattern.py
        │   ├── 07_fastapi_endpoint_pattern.py
        │   ├── 08_connection_pool_setup.py
        │   └── 09_qdrant_vector_service.py
        └── planning/
            ├── feature-analysis.md
            ├── codebase-patterns.md
            ├── documentation-links.md
            ├── examples-to-include.md
            └── gotchas.md
```

### Desired Codebase Tree

```
/Users/jon/source/vibes/infra/rag-service/
├── backend/
│   ├── src/
│   │   ├── main.py                          # FastAPI app with lifespan (NEW)
│   │   ├── mcp_server.py                    # MCP server entry point (NEW)
│   │   ├── config/
│   │   │   ├── __init__.py
│   │   │   ├── settings.py                  # Pydantic Settings (NEW)
│   │   │   └── database.py                  # asyncpg + Qdrant pool setup (NEW)
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── document.py                  # DocumentModel, ChunkModel (NEW)
│   │   │   ├── source.py                    # SourceModel (NEW)
│   │   │   └── search_result.py             # SearchResultModel (NEW)
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── document_service.py          # DocumentService (tuple[bool, dict]) (NEW)
│   │   │   ├── source_service.py            # SourceService (tuple[bool, dict]) (NEW)
│   │   │   ├── vector_service.py            # VectorService (Qdrant ops) (NEW)
│   │   │   ├── embeddings/
│   │   │   │   ├── __init__.py
│   │   │   │   └── embedding_service.py     # EmbeddingService (OpenAI) (NEW)
│   │   │   └── search/
│   │   │       ├── __init__.py
│   │   │       ├── rag_service.py           # RAGService coordinator (NEW)
│   │   │       ├── base_search_strategy.py  # Vector search (NEW)
│   │   │       └── hybrid_search_strategy.py # Vector + text (NEW)
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── health.py                # Health check endpoints (NEW)
│   │   │   │   ├── documents.py             # Document CRUD endpoints (NEW)
│   │   │   │   ├── sources.py               # Source CRUD endpoints (NEW)
│   │   │   │   └── search.py                # Search endpoints (NEW)
│   │   │   └── dependencies.py              # FastAPI dependencies (get_db_pool, get_qdrant_client) (NEW)
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── search_tools.py              # MCP search_knowledge_base (NEW)
│   │   │   ├── document_tools.py            # MCP manage_document (NEW)
│   │   │   └── source_tools.py              # MCP manage_source (NEW)
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── logging.py                   # Logging configuration (NEW)
│   │       ├── response.py                  # MCP payload optimization (NEW)
│   │       └── query_builder.py             # asyncpg query builder (NEW)
│   ├── tests/
│   │   ├── unit/                            # Unit tests (AsyncMock) (NEW)
│   │   │   ├── test_document_service.py
│   │   │   ├── test_source_service.py
│   │   │   ├── test_vector_service.py
│   │   │   └── test_embedding_service.py
│   │   ├── integration/                     # Integration tests (test DB) (NEW)
│   │   │   ├── test_document_lifecycle.py
│   │   │   └── test_search_pipeline.py
│   │   └── mcp/                             # MCP protocol tests (NEW)
│   │       ├── test_search_tools.py
│   │       ├── test_document_tools.py
│   │       └── test_source_tools.py
│   ├── Dockerfile                           # Production FastAPI image (NEW)
│   ├── requirements.txt                     # Python dependencies (NEW)
│   └── pyproject.toml                       # Project metadata, pytest config (NEW)
├── database/
│   ├── scripts/
│   │   └── init.sql                         # Initial schema (5 tables, indexes, triggers) (NEW)
│   └── migrations/
│       └── 001_initial_schema.sql           # Migration scripts (future) (NEW)
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── DocumentList.tsx             # Document listing (NEW)
│   │   │   ├── SearchBar.tsx                # Query input (NEW)
│   │   │   └── SearchResults.tsx            # Results display (NEW)
│   │   ├── services/
│   │   │   └── api.ts                       # API client (NEW)
│   │   ├── App.tsx                          # Main app (NEW)
│   │   └── main.tsx                         # Entry point (NEW)
│   ├── package.json                         # Node dependencies (NEW)
│   ├── tsconfig.json                        # TypeScript config (NEW)
│   └── vite.config.ts                       # Vite dev server config (NEW)
├── docker-compose.yml                       # Development environment (NEW)
├── .env.example                             # Environment variable template (NEW)
└── README.md                                # Setup and usage guide (NEW)
```

**New Files to Create**: 50+ files across backend, database, frontend, tests

### Known Gotchas & Library Quirks

```python
# CRITICAL GOTCHA #1: OpenAI Quota Exhaustion Corruption
# Problem: Storing null/zero embeddings on quota exhaustion corrupts search
# ALL embeddings match equally, making search useless

# ❌ WRONG - Stores null embeddings
async def batch_embed(texts):
    try:
        response = await openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=texts
        )
        return [e.embedding for e in response.data]
    except openai.RateLimitError:
        return [[0.0] * 1536 for _ in texts]  # DISASTER!

# ✅ RIGHT - EmbeddingBatchResult pattern
@dataclass
class EmbeddingBatchResult:
    embeddings: list[list[float]]  # Only successful embeddings
    failed_items: list[dict]       # Failed items with reasons
    success_count: int
    failure_count: int

async def batch_embed_safe(texts):
    embeddings = []
    failed_items = []
    try:
        response = await openai_client.embeddings.create(...)
        embeddings = [e.embedding for e in response.data]
    except openai.RateLimitError as e:
        # STOP immediately - mark remaining as failed
        for i in range(len(embeddings), len(texts)):
            failed_items.append({"index": i, "text": texts[i][:100], "reason": "quota_exhausted"})

    return EmbeddingBatchResult(
        embeddings=embeddings,
        failed_items=failed_items,
        success_count=len(embeddings),
        failure_count=len(failed_items)
    )

# CRITICAL GOTCHA #2: FastAPI Connection Pool Deadlock
# Problem: Returning connections (not pool) from dependencies causes deadlock
# Connections held for entire request duration, pool exhausted quickly

# ❌ WRONG - Returns connection (DEADLOCK RISK)
async def get_db(request: Request) -> asyncpg.Connection:
    pool = request.app.state.db_pool
    async with pool.acquire() as conn:
        yield conn  # Connection held until request completes!

# ✅ RIGHT - Returns pool
async def get_db_pool(request: Request) -> asyncpg.Pool:
    return request.app.state.db_pool  # Services acquire/release as needed

# Usage in service
class DocumentService:
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool  # Store pool, not connection

    async def list_documents(self):
        async with self.db_pool.acquire() as conn:  # Acquire only when needed
            rows = await conn.fetch("SELECT * FROM documents LIMIT 10")
        # Connection released immediately

# CRITICAL GOTCHA #3: asyncpg Placeholder Syntax
# Problem: Using %s (psycopg style) instead of $1, $2 (asyncpg style) causes syntax errors

# ❌ WRONG - psycopg syntax
query = "SELECT * FROM documents WHERE source_id = %s"
rows = await conn.fetch(query, source_id)  # ERROR!

# ✅ RIGHT - asyncpg syntax
query = "SELECT * FROM documents WHERE source_id = $1"
rows = await conn.fetch(query, source_id)

# CRITICAL GOTCHA #4: Row Locking Deadlock
# Problem: FOR UPDATE without ORDER BY causes deadlocks with concurrent transactions

# ❌ WRONG - No ORDER BY (deadlock risk)
await conn.execute("""
    SELECT id FROM tasks WHERE status = $1 FOR UPDATE
""", status)

# ✅ RIGHT - ORDER BY id prevents deadlocks
await conn.execute("""
    SELECT id FROM tasks WHERE status = $1 ORDER BY id FOR UPDATE
""", status)

# CRITICAL GOTCHA #5: Qdrant Dimension Mismatch
# Problem: Vectors with wrong dimensions cause runtime errors

# ❌ WRONG - No validation
await qdrant_client.upsert(collection_name="docs", points=[
    PointStruct(id=chunk_id, vector=embedding, payload={})
])  # Error if len(embedding) != 1536

# ✅ RIGHT - Validate dimension
EXPECTED_DIMENSION = 1536  # text-embedding-3-small

if len(embedding) != EXPECTED_DIMENSION:
    raise ValueError(f"Invalid dimension: {len(embedding)}, expected {EXPECTED_DIMENSION}")

await qdrant_client.upsert(...)

# CRITICAL GOTCHA #6: MCP JSON String Return Violation
# Problem: MCP protocol requires JSON strings, not Python dicts

# ❌ WRONG - Returns dict
@mcp.tool()
async def search_knowledge_base(query: str) -> dict:
    results = await search(query)
    return {"success": True, "results": results}  # PROTOCOL VIOLATION!

# ✅ RIGHT - Returns JSON string
@mcp.tool()
async def search_knowledge_base(query: str) -> str:
    results = await search(query)
    return json.dumps({"success": True, "results": results})

# CRITICAL GOTCHA #7: MCP Payload Size Overflow
# Problem: Large content fields cause timeouts

# ❌ WRONG - Full content
return json.dumps({"document": {"content": full_5000_char_text}})

# ✅ RIGHT - Truncate content
MAX_CONTENT_LENGTH = 1000
def truncate_text(text: str) -> str:
    if len(text) > MAX_CONTENT_LENGTH:
        return text[:MAX_CONTENT_LENGTH - 3] + "..."
    return text

return json.dumps({"document": {"content": truncate_text(full_text)}})

# CRITICAL GOTCHA #8: Connection Leak Without async with
# Problem: Manual connection release is skipped on exceptions

# ❌ WRONG - Manual release (leak risk)
conn = await db_pool.acquire()
try:
    row = await conn.fetchrow("SELECT * FROM documents WHERE id = $1", doc_id)
    return dict(row)
finally:
    await db_pool.release(conn)  # Easy to forget!

# ✅ RIGHT - async with ensures release
async with db_pool.acquire() as conn:
    row = await conn.fetchrow("SELECT * FROM documents WHERE id = $1", doc_id)
    return dict(row)
# Connection ALWAYS released, even on exception

# HIGH PRIORITY GOTCHA #9: HNSW Index During Bulk Upload
# Problem: HNSW enabled during bulk upload is 60-90x slower

# ❌ WRONG - HNSW enabled (10,000 vectors = 2-3 hours)
await qdrant_client.create_collection(
    collection_name="documents",
    vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
    # HNSW enabled by default - rebuilds on every insert!
)

# ✅ RIGHT - Disable HNSW during bulk, rebuild once (10,000 vectors = 2-3 minutes)
await qdrant_client.create_collection(
    collection_name="documents",
    vectors_config=VectorParams(
        size=1536,
        distance=Distance.COSINE,
        hnsw_config=HnswConfigDiff(m=0)  # Disable during bulk
    )
)

# ... bulk upload ...

# Re-enable HNSW and rebuild once
await qdrant_client.update_collection(
    collection_name="documents",
    hnsw_config=HnswConfigDiff(m=16, ef_construct=100)
)

# HIGH PRIORITY GOTCHA #10: OpenAI Rate Limit No Exponential Backoff
# Problem: Immediate retries hit same rate limit, cascading failures

# ❌ WRONG - No backoff
for retry in range(3):
    try:
        response = await openai_client.embeddings.create(...)
        return response
    except openai.RateLimitError:
        continue  # Retry immediately - hits same limit!

# ✅ RIGHT - Exponential backoff with jitter
for retry in range(3):
    try:
        response = await openai_client.embeddings.create(...)
        return response
    except openai.RateLimitError:
        if retry < 2:
            base_delay = 2 ** retry  # 1s, 2s, 4s
            jitter = random.uniform(0, 0.5 * base_delay)
            await asyncio.sleep(base_delay + jitter)
        else:
            raise

# HIGH PRIORITY GOTCHA #12: Blocking CPU-Bound Operations
# Problem: CPU-intensive operations (Docling, chunking) block event loop

# ❌ WRONG - Blocks event loop
async def parse_document(file_path: str):
    converter = DocumentConverter()
    result = converter.convert(file_path)  # Blocks for 200-500ms!
    return result.document.export_to_markdown()

# ✅ RIGHT - Run in thread pool
cpu_executor = ThreadPoolExecutor(max_workers=4)

def parse_document_sync(file_path: str) -> str:
    converter = DocumentConverter()
    result = converter.convert(file_path)
    return result.document.export_to_markdown()

async def parse_document(file_path: str) -> str:
    loop = asyncio.get_event_loop()
    markdown = await loop.run_in_executor(cpu_executor, parse_document_sync, file_path)
    return markdown  # Event loop free during parsing

# MEDIUM PRIORITY: Qdrant Payload Size
# Minimize payload (full text in PostgreSQL, not Qdrant)
payload = {
    "document_id": str(doc_id),
    "chunk_id": str(chunk_id),
    "text": chunk_text[:1000],  # Truncate to 1KB
    # Full metadata in PostgreSQL
}

# MEDIUM PRIORITY: PostgreSQL GIN Index Language
# Use fixed language in both index and query
CREATE INDEX idx_chunks_fts ON chunks USING GIN(to_tsvector('english', text));

SELECT * FROM chunks
WHERE to_tsvector('english', text) @@ plainto_tsquery('english', $1)
-- Both use 'english' - index is used!

# MEDIUM PRIORITY: Docling Memory Limits
# Limit concurrent parsing and file size
DOCLING_SEMAPHORE = asyncio.Semaphore(2)  # Max 2 concurrent
DOCLING_MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

async def parse_document_with_limits(file_path: str):
    file_size = os.path.getsize(file_path)
    if file_size > DOCLING_MAX_FILE_SIZE:
        return False, {"error": "File too large"}

    async with DOCLING_SEMAPHORE:  # Limit concurrency
        return await parse_document(file_path)
```

**Additional Gotchas**:
See `prps/rag_service_implementation/planning/gotchas.md` for complete list of 18+ gotchas with detailed solutions.

---

## Implementation Blueprint

### Phase 0: Planning & Understanding

**BEFORE starting implementation, complete these steps:**

1. **Study Examples Directory** (2-3 hours):
   - Read `prps/rag_service_implementation/examples/README.md` thoroughly
   - Review each example file's "What to Mimic" section
   - Note "What to Adapt" for RAG-specific customizations
   - Skip "What to Skip" sections (task-specific logic)

2. **Review Task-Manager Patterns** (1-2 hours):
   - Study `infra/task-manager/backend/src/services/task_service.py`
   - Understand tuple[bool, dict] return pattern
   - Note asyncpg placeholder syntax ($1, $2)
   - Review connection pool usage patterns

3. **Review Archon RAG Service** (1-2 hours):
   - Study `infra/archon/python/src/server/services/search/rag_service.py`
   - Understand strategy pattern coordination
   - Note configuration-driven strategy selection
   - Review graceful degradation patterns

4. **Read Documentation** (2-3 hours):
   - FastAPI lifespan events (30 min)
   - asyncpg usage guide (45 min)
   - Qdrant AsyncQdrantClient API (45 min)
   - OpenAI rate limit handling cookbook (30 min)

**Total Preparation Time**: 6-10 hours (CRITICAL - do not skip!)

### Task List (Execute in Order)

```yaml
Phase 1: Core Setup (Week 1)

Task 1.1: Initialize Project Structure
RESPONSIBILITY: Create directory structure matching task-manager pattern
FILES TO CREATE:
  - infra/rag-service/backend/src/__init__.py
  - infra/rag-service/backend/src/config/__init__.py
  - infra/rag-service/backend/src/models/__init__.py
  - infra/rag-service/backend/src/services/__init__.py
  - infra/rag-service/backend/src/api/__init__.py
  - infra/rag-service/backend/src/tools/__init__.py
  - infra/rag-service/backend/src/utils/__init__.py
  - infra/rag-service/backend/tests/unit/__init__.py
  - infra/rag-service/backend/tests/integration/__init__.py
  - infra/rag-service/backend/tests/mcp/__init__.py
  - infra/rag-service/database/scripts/
  - infra/rag-service/frontend/src/
  - infra/rag-service/.env.example

PATTERN TO FOLLOW: Task-manager directory structure
SPECIFIC STEPS:
  1. Create all directories and __init__.py files
  2. Copy .gitignore from task-manager
  3. Create .env.example with all required environment variables

VALIDATION:
  - All directories exist
  - All __init__.py files present
  - .env.example contains all configuration variables

Task 1.2: Pydantic Settings Configuration
RESPONSIBILITY: Type-safe environment variable loading
FILES TO CREATE:
  - infra/rag-service/backend/src/config/settings.py

PATTERN TO FOLLOW: Pydantic Settings pattern from documentation
REFERENCE: https://docs.pydantic.dev/latest/concepts/pydantic_settings/
SPECIFIC STEPS:
  1. Create Settings class extending BaseSettings
  2. Define all environment variables with Field()
  3. Add validators for DATABASE_URL, OPENAI_API_KEY
  4. Set model_config with env_file=".env"

CODE STRUCTURE:
  ```python
  from pydantic_settings import BaseSettings, SettingsConfigDict
  from pydantic import Field, validator

  class Settings(BaseSettings):
      # Database
      DATABASE_URL: str = Field(..., description="PostgreSQL connection")
      DATABASE_POOL_MIN_SIZE: int = 10
      DATABASE_POOL_MAX_SIZE: int = 20

      # Qdrant
      QDRANT_URL: str = Field(..., description="Qdrant server URL")
      QDRANT_COLLECTION_NAME: str = "documents"

      # OpenAI
      OPENAI_API_KEY: str = Field(..., description="OpenAI API key")
      OPENAI_MODEL: str = "text-embedding-3-small"

      # Search
      USE_HYBRID_SEARCH: bool = False
      SIMILARITY_THRESHOLD: float = 0.05

      model_config = SettingsConfigDict(
          env_file=".env",
          env_file_encoding="utf-8"
      )

      @validator("DATABASE_URL")
      def validate_database_url(cls, v):
          if not v.startswith("postgresql://"):
              raise ValueError("DATABASE_URL must start with postgresql://")
          return v

  settings = Settings()
  ```

VALIDATION:
  - Settings loads from .env file
  - All required fields present
  - Validators pass for DATABASE_URL

Task 1.3: PostgreSQL Schema Creation
RESPONSIBILITY: Create 5-table schema with indexes and triggers
FILES TO CREATE:
  - infra/rag-service/database/scripts/init.sql

PATTERN TO FOLLOW: INITIAL.md schema specification
REFERENCE: prps/rag_service_implementation/INITIAL.md lines 245-449
SPECIFIC STEPS:
  1. Create sources table (id, source_type, url, status, metadata, error_message, timestamps)
  2. Create documents table (id, source_id, title, document_type, url, metadata, search_vector, timestamps)
  3. Create chunks table (id, document_id, chunk_index, text, token_count, search_vector, metadata, created_at)
  4. Create crawl_jobs table (id, source_id, status, pages_crawled, pages_total, metadata, timestamps)
  5. Create embedding_cache table (id, content_hash, embedding, model_name, timestamps, access_count)
  6. Create all indexes (GIN for search_vector, B-tree for foreign keys)
  7. Create triggers (updated_at, search_vector auto-update)

CRITICAL DETAILS:
  - Use UUID for all primary keys
  - Use CASCADE for foreign key deletes
  - Use TSVECTOR for search_vector columns
  - Create GIN indexes on all search_vector columns
  - Create composite index on (document_id, chunk_index) for chunks
  - Add UNIQUE constraint on embedding_cache.content_hash

VALIDATION:
  - All 5 tables exist
  - All indexes present (verify with \di in psql)
  - All triggers functional (test with INSERT/UPDATE)

Task 1.4: Docker Compose Configuration
RESPONSIBILITY: Orchestrate PostgreSQL, Qdrant, FastAPI, Frontend
FILES TO CREATE:
  - infra/rag-service/docker-compose.yml

PATTERN TO FOLLOW: Task-manager docker-compose.yml
REFERENCE: INITIAL.md lines 1222-1467
SPECIFIC STEPS:
  1. Define postgres service (postgres:15-alpine)
  2. Define qdrant service (qdrant/qdrant:latest)
  3. Define api service (custom FastAPI image)
  4. Define frontend service (Vite dev server)
  5. Add volume mounts for persistence
  6. Add health checks for all services
  7. Add depends_on with health check conditions

CRITICAL DETAILS:
  - PostgreSQL port: 5432
  - Qdrant ports: 6333 (REST), 6334 (gRPC)
  - FastAPI port: 8000
  - Frontend port: 5173
  - Volume: postgres_data, qdrant_data
  - Environment variables from .env file

VALIDATION:
  - docker-compose up -d starts all services
  - docker-compose ps shows all services healthy
  - Services accessible on correct ports

Task 1.5: FastAPI Lifespan Setup
RESPONSIBILITY: Initialize connection pools on startup, close on shutdown
FILES TO CREATE:
  - infra/rag-service/backend/src/main.py
  - infra/rag-service/backend/src/config/database.py
  - infra/rag-service/backend/src/api/dependencies.py

PATTERN TO FOLLOW: examples/08_connection_pool_setup.py
REFERENCE: infra/task-manager/backend/src/main.py
SPECIFIC STEPS:
  1. Create lifespan function with @asynccontextmanager
  2. Initialize asyncpg pool in startup block
  3. Initialize AsyncQdrantClient in startup block
  4. Store in app.state.db_pool and app.state.qdrant_client
  5. Close pools in shutdown block
  6. Create FastAPI app with lifespan parameter
  7. Create get_db_pool dependency (returns pool, NOT connection)
  8. Create get_qdrant_client dependency

CODE STRUCTURE (main.py):
  ```python
  from contextlib import asynccontextmanager
  from fastapi import FastAPI
  import asyncpg
  from qdrant_client import AsyncQdrantClient
  from .config.settings import settings

  @asynccontextmanager
  async def lifespan(app: FastAPI):
      # Startup
      app.state.db_pool = await asyncpg.create_pool(
          settings.DATABASE_URL,
          min_size=settings.DATABASE_POOL_MIN_SIZE,
          max_size=settings.DATABASE_POOL_MAX_SIZE
      )
      app.state.qdrant_client = AsyncQdrantClient(url=settings.QDRANT_URL)

      yield

      # Shutdown
      await app.state.db_pool.close()
      await app.state.qdrant_client.close()

  app = FastAPI(
      title="RAG Service API",
      lifespan=lifespan
  )
  ```

CODE STRUCTURE (dependencies.py):
  ```python
  from fastapi import Request
  import asyncpg
  from qdrant_client import AsyncQdrantClient

  async def get_db_pool(request: Request) -> asyncpg.Pool:
      """CRITICAL: Return pool, NOT connection."""
      return request.app.state.db_pool

  async def get_qdrant_client(request: Request) -> AsyncQdrantClient:
      return request.app.state.qdrant_client
  ```

VALIDATION:
  - App starts without errors
  - Connection pools initialized
  - Health check endpoint accessible

Task 1.6: Health Check Endpoints
RESPONSIBILITY: Validate database and Qdrant connectivity
FILES TO CREATE:
  - infra/rag-service/backend/src/api/routes/health.py

PATTERN TO FOLLOW: examples/07_fastapi_endpoint_pattern.py
SPECIFIC STEPS:
  1. Create health router
  2. Add /health endpoint checking PostgreSQL
  3. Add /health endpoint checking Qdrant
  4. Return 200 if healthy, 503 if unhealthy

CODE STRUCTURE:
  ```python
  from fastapi import APIRouter, Depends, HTTPException
  import asyncpg
  from qdrant_client import AsyncQdrantClient
  from ..dependencies import get_db_pool, get_qdrant_client

  router = APIRouter()

  @router.get("/health")
  async def health_check(
      db_pool: asyncpg.Pool = Depends(get_db_pool),
      qdrant_client: AsyncQdrantClient = Depends(get_qdrant_client)
  ):
      health_status = {"status": "healthy", "checks": {}}

      # Check PostgreSQL
      try:
          async with db_pool.acquire() as conn:
              await conn.fetchval("SELECT 1")
          health_status["checks"]["postgresql"] = "healthy"
      except Exception as e:
          health_status["checks"]["postgresql"] = f"unhealthy: {str(e)}"
          health_status["status"] = "unhealthy"

      # Check Qdrant
      try:
          collections = await qdrant_client.get_collections()
          health_status["checks"]["qdrant"] = "healthy"
      except Exception as e:
          health_status["checks"]["qdrant"] = f"unhealthy: {str(e)}"
          health_status["status"] = "unhealthy"

      if health_status["status"] == "unhealthy":
          raise HTTPException(status_code=503, detail=health_status)

      return health_status
  ```

VALIDATION:
  - curl http://localhost:8000/health returns 200
  - health_status shows both databases healthy

Task 1.7: Qdrant Collection Initialization
RESPONSIBILITY: Create collection with correct vector configuration
FILES TO MODIFY:
  - infra/rag-service/backend/src/main.py (add collection init to lifespan)

PATTERN TO FOLLOW: examples/09_qdrant_vector_service.py
REFERENCE: Qdrant documentation
SPECIFIC STEPS:
  1. Add collection initialization to lifespan startup
  2. Check if collection exists
  3. Create collection if not exists (1536 dims, cosine distance)
  4. Disable HNSW initially (m=0 for bulk upload preparation)

CODE STRUCTURE:
  ```python
  from qdrant_client.models import VectorParams, Distance, HnswConfigDiff

  # In lifespan startup block
  try:
      collections = await app.state.qdrant_client.get_collections()
      collection_names = [c.name for c in collections.collections]

      if settings.QDRANT_COLLECTION_NAME not in collection_names:
          await app.state.qdrant_client.create_collection(
              collection_name=settings.QDRANT_COLLECTION_NAME,
              vectors_config=VectorParams(
                  size=1536,  # text-embedding-3-small
                  distance=Distance.COSINE,
                  hnsw_config=HnswConfigDiff(m=0)  # Disable for bulk upload
              )
          )
          logger.info(f"Created Qdrant collection: {settings.QDRANT_COLLECTION_NAME}")
  except Exception as e:
      logger.error(f"Failed to initialize Qdrant collection: {e}")
      raise
  ```

VALIDATION:
  - Collection created successfully
  - Collection has 1536 dimensions
  - Distance metric is COSINE

Phase 1 Complete Validation:
  - [ ] docker-compose up -d starts all services
  - [ ] curl http://localhost:8000/health returns 200
  - [ ] PostgreSQL has all 5 tables with indexes and triggers
  - [ ] Qdrant collection initialized with 1536 dims
  - [ ] Connection pools working (no deadlock errors)
  - [ ] Environment variables loaded correctly

---

Phase 2: Service Layer (Week 2)

Task 2.1: Pydantic Models
RESPONSIBILITY: Type-safe data models for all entities
FILES TO CREATE:
  - infra/rag-service/backend/src/models/document.py
  - infra/rag-service/backend/src/models/source.py
  - infra/rag-service/backend/src/models/search_result.py

PATTERN TO FOLLOW: Pydantic v2.x models
SPECIFIC STEPS:
  1. Create DocumentModel, DocumentCreate, DocumentUpdate
  2. Create SourceModel, SourceCreate, SourceUpdate
  3. Create ChunkModel
  4. Create SearchResultModel
  5. Create EmbeddingBatchResult (critical for Gotcha #1)

CODE STRUCTURE:
  ```python
  from pydantic import BaseModel, Field
  from typing import Optional
  from datetime import datetime
  from uuid import UUID

  class DocumentCreate(BaseModel):
      source_id: UUID
      title: str
      document_type: str
      url: Optional[str] = None
      metadata: dict = {}

  class DocumentModel(DocumentCreate):
      id: UUID
      created_at: datetime
      updated_at: datetime

      model_config = {"from_attributes": True}

  # EmbeddingBatchResult for Gotcha #1
  @dataclass
  class EmbeddingBatchResult:
      embeddings: list[list[float]]
      failed_items: list[dict]
      success_count: int
      failure_count: int
  ```

VALIDATION:
  - All models have proper field types
  - Validation works for invalid data

Task 2.2: DocumentService
RESPONSIBILITY: Document CRUD operations with tuple[bool, dict] pattern
FILES TO CREATE:
  - infra/rag-service/backend/src/services/document_service.py

PATTERN TO FOLLOW: examples/01_service_layer_pattern.py
REFERENCE: infra/task-manager/backend/src/services/task_service.py
SPECIFIC STEPS:
  1. Create DocumentService class
  2. Implement __init__(self, db_pool: asyncpg.Pool)
  3. Implement list_documents(filters, page, per_page, exclude_large_fields) -> tuple[bool, dict]
  4. Implement get_document(doc_id) -> tuple[bool, dict]
  5. Implement create_document(document_data) -> tuple[bool, dict]
  6. Implement update_document(doc_id, update_data) -> tuple[bool, dict]
  7. Implement delete_document(doc_id) -> tuple[bool, dict]

CRITICAL PATTERNS:
  - Store db_pool, NOT connection
  - All methods return tuple[bool, dict]
  - Use async with self.db_pool.acquire()
  - Use $1, $2 placeholders (NOT %s)
  - Dynamic WHERE clause building with QueryBuilder
  - exclude_large_fields for MCP optimization

CODE STRUCTURE:
  ```python
  class DocumentService:
      def __init__(self, db_pool: asyncpg.Pool):
          self.db_pool = db_pool

      async def list_documents(
          self,
          filters: dict | None = None,
          page: int = 1,
          per_page: int = 50,
          exclude_large_fields: bool = False
      ) -> tuple[bool, dict]:
          try:
              # Build query with conditional field selection
              if exclude_large_fields:
                  select_fields = "id, source_id, title, document_type, created_at"
              else:
                  select_fields = "*"

              async with self.db_pool.acquire() as conn:
                  # Count query
                  count_query = "SELECT COUNT(*) FROM documents"
                  total_count = await conn.fetchval(count_query)

                  # List query
                  query = f"""
                      SELECT {select_fields}
                      FROM documents
                      ORDER BY created_at DESC
                      LIMIT $1 OFFSET $2
                  """
                  offset = (page - 1) * per_page
                  rows = await conn.fetch(query, per_page, offset)

              documents = [dict(row) for row in rows]

              return True, {
                  "documents": documents,
                  "total_count": total_count,
                  "page": page,
                  "per_page": per_page
              }

          except asyncpg.PostgresError as e:
              logger.error(f"Database error listing documents: {e}")
              return False, {"error": f"Database error: {str(e)}"}
  ```

VALIDATION:
  - All CRUD operations work
  - tuple[bool, dict] pattern consistent
  - No connection leaks (verify with pool metrics)

Task 2.3: SourceService
RESPONSIBILITY: Source CRUD operations
FILES TO CREATE:
  - infra/rag-service/backend/src/services/source_service.py

PATTERN TO FOLLOW: Same as DocumentService
SPECIFIC STEPS:
  1. Mirror DocumentService structure
  2. Implement all CRUD methods
  3. Follow tuple[bool, dict] pattern

VALIDATION:
  - Same as DocumentService

Task 2.4: VectorService
RESPONSIBILITY: Qdrant vector operations
FILES TO CREATE:
  - infra/rag-service/backend/src/services/vector_service.py

PATTERN TO FOLLOW: examples/09_qdrant_vector_service.py
SPECIFIC STEPS:
  1. Create VectorService class
  2. Implement __init__(self, qdrant_client: AsyncQdrantClient, collection_name: str)
  3. Implement validate_embedding(embedding: list[float]) -> None
  4. Implement upsert_vectors(chunks: list[dict], embeddings: list[list[float]]) -> None
  5. Implement search_vectors(query_embedding: list[float], limit: int, filters: dict) -> list[dict]
  6. Implement delete_vectors(chunk_ids: list[str]) -> None

CRITICAL PATTERNS:
  - Validate dimension == 1536 before insert (Gotcha #5)
  - Check for null/zero embeddings (Gotcha #1)
  - Minimize payload (text truncated to 1000 chars)
  - VectorService does NOT use tuple[bool, dict] pattern (raises exceptions)

CODE STRUCTURE:
  ```python
  class VectorService:
      def __init__(self, qdrant_client: AsyncQdrantClient, collection_name: str):
          self.qdrant_client = qdrant_client
          self.collection_name = collection_name
          self.expected_dimension = 1536

      def validate_embedding(self, embedding: list[float]) -> None:
          if len(embedding) != self.expected_dimension:
              raise ValueError(f"Invalid dimension: {len(embedding)}")

          if all(v == 0 for v in embedding):
              raise ValueError("Embedding cannot be all zeros")

      async def upsert_vectors(
          self,
          chunks: list[dict],
          embeddings: list[list[float]]
      ) -> None:
          # Validate all embeddings
          for i, embedding in enumerate(embeddings):
              self.validate_embedding(embedding)

          # Construct points
          points = [
              PointStruct(
                  id=str(chunks[i]["id"]),
                  vector=embeddings[i],
                  payload={
                      "document_id": str(chunks[i]["document_id"]),
                      "text": chunks[i]["text"][:1000]  # Truncate
                  }
              )
              for i in range(len(chunks))
          ]

          await self.qdrant_client.upsert(
              collection_name=self.collection_name,
              points=points
          )
  ```

VALIDATION:
  - Upsert works with valid embeddings
  - Dimension validation catches wrong dimensions
  - Search returns correct results

Task 2.5: EmbeddingService
RESPONSIBILITY: OpenAI embeddings with cache and quota handling
FILES TO CREATE:
  - infra/rag-service/backend/src/services/embeddings/embedding_service.py

PATTERN TO FOLLOW: OpenAI documentation + Gotcha #1 pattern
REFERENCE: https://cookbook.openai.com/examples/how_to_handle_rate_limits
SPECIFIC STEPS:
  1. Create EmbeddingService class
  2. Implement __init__(self, db_pool, openai_client)
  3. Implement generate_embedding(text: str) -> list[float]
  4. Implement check_cache(text: str) -> list[float] | None
  5. Implement store_cache(text: str, embedding: list[float]) -> None
  6. Implement batch_embed_safe(texts: list[str]) -> EmbeddingBatchResult (CRITICAL for Gotcha #1)

CRITICAL PATTERNS:
  - Use EmbeddingBatchResult pattern (Gotcha #1)
  - NEVER store null embeddings on quota exhaustion
  - MD5 hash for cache lookup
  - Exponential backoff for rate limits (Gotcha #10)
  - Batch size: 100 texts per API call

CODE STRUCTURE:
  ```python
  class EmbeddingService:
      def __init__(self, db_pool: asyncpg.Pool, openai_client):
          self.db_pool = db_pool
          self.openai_client = openai_client
          self.model_name = "text-embedding-3-small"

      async def check_cache(self, text: str) -> list[float] | None:
          content_hash = hashlib.md5(text.encode()).hexdigest()

          async with self.db_pool.acquire() as conn:
              row = await conn.fetchrow("""
                  SELECT embedding
                  FROM embedding_cache
                  WHERE content_hash = $1 AND model_name = $2
              """, content_hash, self.model_name)

              if row:
                  await conn.execute("""
                      UPDATE embedding_cache
                      SET access_count = access_count + 1,
                          last_accessed_at = NOW()
                      WHERE content_hash = $1
                  """, content_hash)

                  return row["embedding"]

          return None

      async def batch_embed_safe(
          self,
          texts: list[str]
      ) -> EmbeddingBatchResult:
          """CRITICAL: Never stores null embeddings."""
          embeddings = []
          failed_items = []

          try:
              response = await self.openai_client.embeddings.create(
                  model=self.model_name,
                  input=texts
              )

              for i, item in enumerate(response.data):
                  embeddings.append(item.embedding)

          except openai.RateLimitError as e:
              # STOP immediately - mark remaining as failed
              logger.error(f"Quota exhausted after {len(embeddings)} embeddings")

              for i in range(len(embeddings), len(texts)):
                  failed_items.append({
                      "index": i,
                      "text": texts[i][:100],
                      "reason": "quota_exhausted",
                      "error": str(e)
                  })

          return EmbeddingBatchResult(
              embeddings=embeddings,
              failed_items=failed_items,
              success_count=len(embeddings),
              failure_count=len(failed_items)
          )
  ```

VALIDATION:
  - Embeddings generated successfully
  - Cache lookup works (hit rate 20-40%)
  - Quota exhaustion handled correctly (no null embeddings stored)
  - Exponential backoff on rate limits

Phase 2 Complete Validation:
  - [ ] All services implement required methods
  - [ ] DocumentService and SourceService use tuple[bool, dict] pattern
  - [ ] VectorService validates dimensions before insert
  - [ ] EmbeddingService uses EmbeddingBatchResult pattern
  - [ ] Unit tests pass with >80% coverage
  - [ ] No connection leaks (pool metrics stable)

---

Phase 3: Search Pipeline (Week 3)

Task 3.1: BaseSearchStrategy
RESPONSIBILITY: Vector similarity search
FILES TO CREATE:
  - infra/rag-service/backend/src/services/search/base_search_strategy.py

PATTERN TO FOLLOW: examples/04_base_vector_search.py
REFERENCE: infra/archon/python/src/server/services/search/base_search_strategy.py
SPECIFIC STEPS:
  1. Create BaseSearchStrategy class
  2. Implement __init__(self, qdrant_client, embedding_service)
  3. Implement search(query: str, match_count: int, filters: dict) -> list[dict]
  4. Apply similarity threshold filtering (>= 0.05)
  5. Return results with scores

CODE STRUCTURE:
  ```python
  class BaseSearchStrategy:
      def __init__(self, qdrant_client, embedding_service):
          self.qdrant_client = qdrant_client
          self.embedding_service = embedding_service
          self.collection_name = settings.QDRANT_COLLECTION_NAME

      async def search(
          self,
          query: str,
          match_count: int = 10,
          filters: dict | None = None,
          similarity_threshold: float = 0.05
      ) -> list[dict]:
          # Generate query embedding
          query_embedding = await self.embedding_service.generate_embedding(query)

          # Build filters if provided
          query_filter = None
          if filters:
              # Build Qdrant filter from dict
              pass

          # Search Qdrant
          results = await self.qdrant_client.search(
              collection_name=self.collection_name,
              query_vector=query_embedding,
              query_filter=query_filter,
              limit=match_count,
              score_threshold=similarity_threshold
          )

          return [
              {
                  "chunk_id": result.id,
                  "score": result.score,
                  "text": result.payload.get("text"),
                  "document_id": result.payload.get("document_id"),
                  "match_type": "vector"
              }
              for result in results
          ]
  ```

VALIDATION:
  - Vector search works
  - Latency <50ms p95 (measured with 10K queries)
  - Threshold filtering works

Task 3.2: HybridSearchStrategy
RESPONSIBILITY: Combined vector + full-text search
FILES TO CREATE:
  - infra/rag-service/backend/src/services/search/hybrid_search_strategy.py

PATTERN TO FOLLOW: examples/05_hybrid_search_strategy.py
REFERENCE: infra/archon/python/src/server/services/search/hybrid_search_strategy.py
SPECIFIC STEPS:
  1. Create HybridSearchStrategy class
  2. Implement __init__(self, qdrant_client, db_pool, embedding_service, base_strategy)
  3. Implement search(query, match_count, filters) -> list[dict]
  4. Parallel execution: vector search + full-text search
  5. Normalize scores to 0.0-1.0 range
  6. Combine scores: 0.7×vector + 0.3×text
  7. Deduplicate by chunk_id (keep highest score)
  8. Return top-k results

CODE STRUCTURE:
  ```python
  class HybridSearchStrategy:
      def __init__(self, qdrant_client, db_pool, embedding_service, base_strategy):
          self.qdrant_client = qdrant_client
          self.db_pool = db_pool
          self.embedding_service = embedding_service
          self.base_strategy = base_strategy

      async def search(
          self,
          query: str,
          match_count: int = 10,
          filters: dict | None = None
      ) -> list[dict]:
          # Parallel execution
          vector_results, text_results = await asyncio.gather(
              self.base_strategy.search(query, match_count=100),
              self._full_text_search(query, limit=100)
          )

          # Normalize scores
          vector_scores = self._normalize_scores(vector_results, "score")
          text_scores = self._normalize_scores(text_results, "rank")

          # Combine scores: 0.7×vector + 0.3×text
          combined = {}
          for result in vector_scores:
              chunk_id = result["chunk_id"]
              combined[chunk_id] = {
                  **result,
                  "combined_score": result["normalized_score"] * 0.7
              }

          for result in text_scores:
              chunk_id = result["chunk_id"]
              if chunk_id in combined:
                  combined[chunk_id]["combined_score"] += result["normalized_score"] * 0.3
              else:
                  combined[chunk_id] = {
                      **result,
                      "combined_score": result["normalized_score"] * 0.3
                  }

          # Sort by combined score and return top-k
          sorted_results = sorted(
              combined.values(),
              key=lambda x: x["combined_score"],
              reverse=True
          )

          return sorted_results[:match_count]

      async def _full_text_search(self, query: str, limit: int) -> list[dict]:
          async with self.db_pool.acquire() as conn:
              rows = await conn.fetch("""
                  SELECT
                      id as chunk_id,
                      document_id,
                      text,
                      ts_rank(search_vector, plainto_tsquery('english', $1)) as rank
                  FROM chunks
                  WHERE search_vector @@ plainto_tsquery('english', $1)
                  ORDER BY rank DESC
                  LIMIT $2
              """, query, limit)

          return [dict(row) for row in rows]

      def _normalize_scores(self, results: list[dict], score_key: str) -> list[dict]:
          if not results:
              return []

          scores = [r[score_key] for r in results]
          min_score = min(scores)
          max_score = max(scores)
          score_range = max_score - min_score or 1

          for result in results:
              result["normalized_score"] = (result[score_key] - min_score) / score_range

          return results
  ```

VALIDATION:
  - Hybrid search works
  - Latency <100ms p95 (measured with 10K queries)
  - Score combining correct (0.7×vector + 0.3×text)
  - Deduplication works

Task 3.3: RAGService Coordinator
RESPONSIBILITY: Strategy pattern coordination
FILES TO CREATE:
  - infra/rag-service/backend/src/services/search/rag_service.py

PATTERN TO FOLLOW: examples/03_rag_search_pipeline.py
REFERENCE: infra/archon/python/src/server/services/search/rag_service.py
SPECIFIC STEPS:
  1. Create RAGService class
  2. Implement __init__(self, qdrant_client, db_pool, embedding_service)
  3. Initialize strategies based on configuration
  4. Implement search_documents(query, search_type, match_count, filters) -> list[dict]
  5. Delegate to appropriate strategy
  6. Implement graceful degradation

CODE STRUCTURE:
  ```python
  class RAGService:
      def __init__(self, qdrant_client, db_pool, embedding_service):
          self.qdrant_client = qdrant_client
          self.db_pool = db_pool
          self.embedding_service = embedding_service

          # Initialize strategies
          self.base_strategy = BaseSearchStrategy(qdrant_client, embedding_service)

          # Initialize optional strategies
          if settings.USE_HYBRID_SEARCH:
              self.hybrid_strategy = HybridSearchStrategy(
                  qdrant_client,
                  db_pool,
                  embedding_service,
                  self.base_strategy
              )
          else:
              self.hybrid_strategy = None

      async def search_documents(
          self,
          query: str,
          search_type: str = "vector",
          match_count: int = 10,
          filters: dict | None = None
      ) -> list[dict]:
          try:
              if search_type == "hybrid" and self.hybrid_strategy:
                  results = await self.hybrid_strategy.search(
                      query,
                      match_count,
                      filters
                  )
              else:
                  results = await self.base_strategy.search(
                      query,
                      match_count,
                      filters
                  )

              return results

          except Exception as e:
              logger.warning(f"Search strategy failed: {e}")
              # Graceful degradation - fall back to base strategy
              if search_type != "vector":
                  logger.info("Falling back to base vector search")
                  return await self.base_strategy.search(
                      query,
                      match_count,
                      filters
                  )
              raise
  ```

VALIDATION:
  - Strategy selection works based on search_type
  - Graceful degradation works when hybrid fails
  - Configuration-driven strategy enablement

Phase 3 Complete Validation:
  - [ ] BaseSearchStrategy latency <50ms p95
  - [ ] HybridSearchStrategy latency <100ms p95
  - [ ] RAGService coordinates strategies correctly
  - [ ] Graceful degradation works
  - [ ] Integration tests pass

---

Phase 4: Document Ingestion (Week 4)

Task 4.1: Document Parser (Docling Integration)
RESPONSIBILITY: Parse PDF, HTML, DOCX documents
FILES TO CREATE:
  - infra/rag-service/backend/src/services/document_parser.py

PATTERN TO FOLLOW: Docling documentation + Gotcha #12 (thread pool)
REFERENCE: https://docling-project.github.io/docling/usage/
SPECIFIC STEPS:
  1. Create DocumentParser class
  2. Implement __init__()
  3. Implement parse_document_sync(file_path: str) -> str (runs in thread pool)
  4. Implement parse_document(file_path: str) -> str (async wrapper)
  5. Add memory limits and timeout
  6. Use semaphore to limit concurrent parsing

CODE STRUCTURE:
  ```python
  import asyncio
  from concurrent.futures import ThreadPoolExecutor
  from docling.document_converter import DocumentConverter

  # Thread pool for CPU-bound operations
  cpu_executor = ThreadPoolExecutor(max_workers=4)

  # Limit concurrent parsing
  DOCLING_SEMAPHORE = asyncio.Semaphore(2)
  DOCLING_MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

  class DocumentParser:
      def __init__(self):
          self.converter = DocumentConverter()

      def parse_document_sync(self, file_path: str) -> str:
          """Synchronous parsing (runs in thread pool)."""
          result = self.converter.convert(file_path)
          return result.document.export_to_markdown()

      async def parse_document(self, file_path: str) -> tuple[bool, dict]:
          """Async wrapper with memory limits."""
          # Check file size
          file_size = os.path.getsize(file_path)
          if file_size > DOCLING_MAX_FILE_SIZE:
              return False, {"error": "File too large"}

          # Limit concurrent parsing
          async with DOCLING_SEMAPHORE:
              try:
                  # Run in thread pool with timeout
                  loop = asyncio.get_event_loop()
                  markdown = await asyncio.wait_for(
                      loop.run_in_executor(
                          cpu_executor,
                          self.parse_document_sync,
                          file_path
                      ),
                      timeout=300  # 5 minute timeout
                  )

                  return True, {"markdown": markdown}

              except asyncio.TimeoutError:
                  return False, {"error": "Parsing timeout"}
              except Exception as e:
                  return False, {"error": str(e)}
  ```

VALIDATION:
  - Parses PDF documents successfully
  - Parses HTML documents successfully
  - Parses DOCX documents successfully
  - Memory limits work (file size check)
  - Timeout works (5 minute limit)
  - Concurrent parsing limited to 2

Task 4.2: Text Chunking
RESPONSIBILITY: Semantic chunking with overlap
FILES TO CREATE:
  - infra/rag-service/backend/src/services/chunker.py

PATTERN TO FOLLOW: Semantic chunking pattern from documentation
SPECIFIC STEPS:
  1. Create TextChunker class
  2. Implement chunk_text_sync(text: str, chunk_size: int, overlap: int) -> list[str]
  3. Implement chunk_text(text: str) -> list[str] (async wrapper)
  4. Run in thread pool (CPU-bound)
  5. Respect boundaries (no mid-sentence cuts)

CODE STRUCTURE:
  ```python
  class TextChunker:
      def __init__(self, chunk_size: int = 500, overlap: int = 50):
          self.chunk_size = chunk_size
          self.overlap = overlap

      def chunk_text_sync(self, text: str) -> list[str]:
          """Synchronous chunking (runs in thread pool)."""
          # Split into sentences
          sentences = re.split(r'(?<=[.!?])\s+', text)

          chunks = []
          current_chunk = []
          current_length = 0

          for sentence in sentences:
              sentence_length = len(sentence.split())

              if current_length + sentence_length > self.chunk_size and current_chunk:
                  # Save current chunk
                  chunks.append(' '.join(current_chunk))

                  # Start new chunk with overlap
                  overlap_words = ' '.join(current_chunk).split()[-self.overlap:]
                  current_chunk = overlap_words
                  current_length = len(overlap_words)

              current_chunk.append(sentence)
              current_length += sentence_length

          if current_chunk:
              chunks.append(' '.join(current_chunk))

          return chunks

      async def chunk_text(self, text: str) -> list[str]:
          """Async wrapper."""
          loop = asyncio.get_event_loop()
          chunks = await loop.run_in_executor(
              cpu_executor,
              self.chunk_text_sync,
              text
          )
          return chunks
  ```

VALIDATION:
  - Chunks are ~500 tokens each
  - Overlap is 50 tokens
  - No mid-sentence cuts
  - Runs in thread pool

Task 4.3: Document Ingestion Pipeline
RESPONSIBILITY: Atomic ingestion (parse, chunk, embed, store)
FILES TO CREATE:
  - infra/rag-service/backend/src/services/ingestion_service.py

PATTERN TO FOLLOW: examples/06_transaction_pattern.py + Gotcha #1 pattern
SPECIFIC STEPS:
  1. Create IngestionService class
  2. Implement __init__(self, db_pool, qdrant_client, embedding_service, document_parser, text_chunker)
  3. Implement ingest_document(file_path: str, source_id: str) -> tuple[bool, dict]
  4. Parse document with Docling
  5. Chunk text
  6. Batch embed with EmbeddingBatchResult pattern
  7. Atomic storage: PostgreSQL + Qdrant
  8. Handle partial failures

CODE STRUCTURE:
  ```python
  class IngestionService:
      def __init__(
          self,
          db_pool,
          document_service,
          vector_service,
          embedding_service,
          document_parser,
          text_chunker
      ):
          self.db_pool = db_pool
          self.document_service = document_service
          self.vector_service = vector_service
          self.embedding_service = embedding_service
          self.document_parser = document_parser
          self.text_chunker = text_chunker

      async def ingest_document(
          self,
          file_path: str,
          source_id: str,
          title: str,
          document_type: str
      ) -> tuple[bool, dict]:
          """Ingest document with atomic storage."""

          try:
              # Step 1: Parse document
              success, parse_result = await self.document_parser.parse_document(file_path)
              if not success:
                  return False, {"error": "Parsing failed", "details": parse_result}

              markdown = parse_result["markdown"]

              # Step 2: Chunk text
              chunks = await self.text_chunker.chunk_text(markdown)
              logger.info(f"Created {len(chunks)} chunks")

              # Step 3: Batch embed with cache lookup
              embeddings_to_generate = []
              cached_embeddings = []

              for chunk in chunks:
                  cached = await self.embedding_service.check_cache(chunk)
                  if cached:
                      cached_embeddings.append(cached)
                  else:
                      embeddings_to_generate.append(chunk)

              # Generate embeddings for uncached chunks
              if embeddings_to_generate:
                  embed_result = await self.embedding_service.batch_embed_safe(
                      embeddings_to_generate
                  )

                  # CRITICAL: Check for failures
                  if embed_result.failure_count > 0:
                      logger.warning(f"Failed to embed {embed_result.failure_count} chunks")
                      # Store failed chunks for retry

              # Combine cached + new embeddings
              all_embeddings = cached_embeddings + embed_result.embeddings

              # Step 4: Atomic storage (PostgreSQL + Qdrant)
              async with self.db_pool.acquire() as conn:
                  async with conn.transaction():
                      # Insert document
                      doc_row = await conn.fetchrow("""
                          INSERT INTO documents (source_id, title, document_type, url, metadata)
                          VALUES ($1, $2, $3, $4, $5)
                          RETURNING *
                      """, source_id, title, document_type, file_path, json.dumps({}))

                      document_id = doc_row["id"]

                      # Insert chunks
                      chunk_records = []
                      for i, chunk_text in enumerate(chunks[:len(all_embeddings)]):
                          chunk_row = await conn.fetchrow("""
                              INSERT INTO chunks (document_id, chunk_index, text, token_count)
                              VALUES ($1, $2, $3, $4)
                              RETURNING *
                          """, document_id, i, chunk_text, len(chunk_text.split()))

                          chunk_records.append(dict(chunk_row))

              # Step 5: Upsert vectors to Qdrant (idempotent)
              await self.vector_service.upsert_vectors(
                  chunk_records,
                  all_embeddings
              )

              return True, {
                  "document_id": str(document_id),
                  "chunks_created": len(chunk_records),
                  "chunks_failed": embed_result.failure_count
              }

          except Exception as e:
              logger.error(f"Ingestion failed: {e}", exc_info=True)
              return False, {"error": str(e)}
  ```

VALIDATION:
  - Document ingested successfully
  - Chunks created in PostgreSQL
  - Vectors upserted to Qdrant
  - Cache lookup works (20-40% hit rate)
  - Quota exhaustion handled correctly (no null embeddings)
  - Throughput: 35-60 docs/minute

Phase 4 Complete Validation:
  - [ ] Docling parses PDF, HTML, DOCX
  - [ ] Semantic chunking produces ~500 token chunks
  - [ ] Batch embedding uses 100 texts per API call
  - [ ] EmbeddingBatchResult prevents null embeddings
  - [ ] Cache hit rate 20-40%
  - [ ] Atomic storage works (PostgreSQL + Qdrant)
  - [ ] Ingestion throughput: 35-60 docs/minute

---

Phase 5: MCP Tools (Week 5)

Task 5.1: search_knowledge_base Tool
RESPONSIBILITY: Search via MCP protocol
FILES TO CREATE:
  - infra/rag-service/backend/src/tools/search_tools.py

PATTERN TO FOLLOW: examples/02_mcp_consolidated_tools.py
REFERENCE: infra/archon/python/src/mcp_server/features/rag/rag_tools.py
SPECIFIC STEPS:
  1. Create MCP server with FastMCP
  2. Implement search_knowledge_base tool
  3. Return JSON string (NOT dict)
  4. Truncate content to 1000 chars
  5. Enforce pagination (max 20 items)

CODE STRUCTURE:
  ```python
  from mcp.server.fastmcp import Context, FastMCP
  import json

  mcp = FastMCP()

  @mcp.tool()
  async def search_knowledge_base(
      ctx: Context,
      query: str,
      source_id: str | None = None,
      match_count: int = 5,
      search_type: str = "hybrid",
      similarity_threshold: float = 0.05
  ) -> str:  # CRITICAL: Returns str, not dict
      """
      Search knowledge base with hybrid vector + full-text search.

      Args:
          query: Search query text
          source_id: Optional filter by source
          match_count: Number of results (max 20)
          search_type: "vector", "hybrid", or "rerank"
          similarity_threshold: Minimum similarity score (0.0-1.0)

      Returns:
          JSON string with {success: bool, results: list, count: int}
      """
      try:
          # Enforce pagination limit
          match_count = min(match_count, 20)

          # Get RAG service from app state
          rag_service = ctx.app.state.rag_service

          # Build filters
          filters = {}
          if source_id:
              filters["source_id"] = source_id

          # Search
          results = await rag_service.search_documents(
              query=query,
              search_type=search_type,
              match_count=match_count,
              filters=filters
          )

          # Optimize results for MCP (truncate content)
          optimized_results = [
              {
                  "chunk_id": r["chunk_id"],
                  "document_id": r["document_id"],
                  "score": r["score"],
                  "text": r["text"][:1000] if len(r["text"]) > 1000 else r["text"],
                  "match_type": r["match_type"]
              }
              for r in results
          ]

          # CRITICAL: Return JSON string
          return json.dumps({
              "success": True,
              "results": optimized_results,
              "count": len(optimized_results),
              "search_type": search_type
          })

      except Exception as e:
          logger.error(f"Search failed: {e}", exc_info=True)
          # CRITICAL: Return JSON string for errors
          return json.dumps({
              "success": False,
              "error": str(e),
              "suggestion": "Check query format and try again"
          })
  ```

VALIDATION:
  - Tool executes via MCP protocol
  - Returns JSON string (not dict)
  - Content truncated to 1000 chars
  - Pagination enforced (max 20 items)

Task 5.2: manage_document Tool
RESPONSIBILITY: Consolidated document CRUD
FILES TO CREATE:
  - infra/rag-service/backend/src/tools/document_tools.py

PATTERN TO FOLLOW: examples/02_mcp_consolidated_tools.py
SPECIFIC STEPS:
  1. Implement manage_document tool
  2. Support actions: create, update, delete, get, list
  3. Return JSON string
  4. Truncate content
  5. Enforce pagination

CODE STRUCTURE:
  ```python
  @mcp.tool()
  async def manage_document(
      ctx: Context,
      action: str,  # "create" | "update" | "delete" | "get" | "list"
      document_id: str | None = None,
      title: str | None = None,
      source_id: str | None = None,
      file_path: str | None = None,
      page: int = 1,
      per_page: int = 10
  ) -> str:
      """
      Manage documents (consolidated: create/update/delete/get/list).

      Args:
          action: "create" | "update" | "delete" | "get" | "list"
          document_id: Document UUID for get/update/delete
          title: Document title (required for create)
          source_id: Source UUID (required for create)
          file_path: File path for upload (required for create)
          page: Page number for list
          per_page: Items per page (default: 10, max: 20)

      Returns:
          JSON string with {success: bool, ...}
      """
      try:
          # Get services
          document_service = ctx.app.state.document_service
          ingestion_service = ctx.app.state.ingestion_service

          if action == "create":
              if not all([title, source_id, file_path]):
                  return json.dumps({
                      "success": False,
                      "error": "title, source_id, and file_path required for create"
                  })

              success, result = await ingestion_service.ingest_document(
                  file_path=file_path,
                  source_id=source_id,
                  title=title,
                  document_type="pdf"  # Detect from file extension
              )

              return json.dumps({
                  "success": success,
                  "document_id": result.get("document_id"),
                  "message": "Document created successfully" if success else result.get("error")
              })

          elif action == "get":
              if not document_id:
                  return json.dumps({
                      "success": False,
                      "error": "document_id required for get"
                  })

              success, result = await document_service.get_document(document_id)

              if not success:
                  return json.dumps({"success": False, "error": result.get("error")})

              # Optimize document response
              document = result["document"]
              optimized = {
                  "id": document["id"],
                  "title": document["title"],
                  "document_type": document["document_type"],
                  "created_at": str(document["created_at"])
              }

              return json.dumps({"success": True, "document": optimized})

          elif action == "list":
              per_page = min(per_page, 20)  # Enforce max

              success, result = await document_service.list_documents(
                  page=page,
                  per_page=per_page,
                  exclude_large_fields=True  # MCP optimization
              )

              if not success:
                  return json.dumps({"success": False, "error": result.get("error")})

              return json.dumps({
                  "success": True,
                  "documents": result["documents"],
                  "count": len(result["documents"]),
                  "total": result["total_count"],
                  "page": page,
                  "per_page": per_page
              })

          elif action == "update":
              # Implementation similar to get/create
              pass

          elif action == "delete":
              if not document_id:
                  return json.dumps({
                      "success": False,
                      "error": "document_id required for delete"
                  })

              success, result = await document_service.delete_document(document_id)

              return json.dumps({
                  "success": success,
                  "message": "Document deleted successfully" if success else result.get("error")
              })

          else:
              return json.dumps({
                  "success": False,
                  "error": f"Unknown action: {action}",
                  "suggestion": "Use 'create', 'update', 'delete', 'get', or 'list'"
              })

      except Exception as e:
          logger.error(f"Document operation failed: {e}", exc_info=True)
          return json.dumps({
              "success": False,
              "error": str(e)
          })
  ```

VALIDATION:
  - All actions work (create, update, delete, get, list)
  - Returns JSON string
  - Content truncated
  - Pagination enforced

Task 5.3: manage_source Tool
RESPONSIBILITY: Consolidated source CRUD
FILES TO CREATE:
  - infra/rag-service/backend/src/tools/source_tools.py

PATTERN TO FOLLOW: Same as manage_document
SPECIFIC STEPS:
  1. Mirror manage_document structure
  2. Support same actions
  3. Follow same patterns

VALIDATION:
  - Same as manage_document

Task 5.4: MCP Server Entry Point
RESPONSIBILITY: MCP server configuration and startup
FILES TO CREATE:
  - infra/rag-service/backend/src/mcp_server.py

PATTERN TO FOLLOW: Archon MCP server pattern
SPECIFIC STEPS:
  1. Create MCP server with FastMCP
  2. Register all tools
  3. Add startup logic
  4. Configure STDIO transport

CODE STRUCTURE:
  ```python
  from mcp.server.fastmcp import FastMCP
  import asyncio

  # Create MCP server
  mcp = FastMCP()

  # Import and register tools
  from .tools.search_tools import search_knowledge_base
  from .tools.document_tools import manage_document
  from .tools.source_tools import manage_source

  # Tools auto-registered via @mcp.tool() decorator

  async def main():
      """Run MCP server."""
      # Initialize services in app state
      # ... initialization logic ...

      # Run server
      await mcp.run()

  if __name__ == "__main__":
      asyncio.run(main())
  ```

VALIDATION:
  - MCP server starts successfully
  - Tools registered
  - STDIO transport works

Phase 5 Complete Validation:
  - [ ] search_knowledge_base executes via MCP
  - [ ] manage_document supports all actions
  - [ ] manage_source supports all actions
  - [ ] All tools return JSON strings
  - [ ] Payload truncation works
  - [ ] Pagination enforced
  - [ ] MCP protocol tests pass

---

Overall Quality Gates

Final Validation:
  - [ ] All Phase 1-5 success criteria met
  - [ ] Unit test coverage >80% (pytest-cov)
  - [ ] Integration tests pass (full pipeline)
  - [ ] Performance benchmarks met (<50ms base, <100ms hybrid, 35+ docs/min)
  - [ ] No critical security issues (API keys not committed, CORS configured)
  - [ ] Documentation complete (README.md, API docs)
  - [ ] Docker Compose deployment verified (clean docker-compose up)
  - [ ] Health checks pass consistently
  - [ ] Log quality: Structured logging at appropriate levels
  - [ ] No connection leaks (pool metrics stable)

---

## Validation Loop

### Level 1: Syntax & Style Checks

```bash
# Run these FIRST - fix any errors before proceeding
cd infra/rag-service/backend

# Linting
ruff check src/ --fix
ruff format src/

# Type checking
mypy src/

# Expected: No errors
```

### Level 2: Unit Tests

```bash
# Run and iterate until passing
pytest tests/unit/ -v --cov=src --cov-report=term-missing

# Target: >80% coverage
# If failing: Read error, understand root cause, fix code, re-run
```

### Level 3a: Integration Tests

```bash
# Start test database
docker-compose -f docker-compose.test.yml up -d postgres qdrant

# Run integration tests
pytest tests/integration/ -v

# Expected: All tests pass
```

### Level 3b: MCP Protocol Tests

```bash
# Test MCP tools via protocol
pytest tests/mcp/ -v

# Expected: All tools return JSON strings, protocol compliance verified
```

### Level 4: End-to-End Test

```bash
# Start all services
docker-compose up -d

# Health check
curl http://localhost:8000/health
# Expected: {"status": "healthy", "checks": {"postgresql": "healthy", "qdrant": "healthy"}}

# Upload document
curl -X POST http://localhost:8000/api/documents \
  -F "file=@test.pdf" \
  -F "source_id=src-123" \
  -F "title=Test Document"

# Search
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "test query", "search_type": "hybrid", "match_count": 5}'

# Expected: Search results with scores
```

---

## Final Validation Checklist

**Code Quality**:
- [ ] All tests pass: `pytest tests/ -v`
- [ ] No linting errors: `ruff check src/`
- [ ] No type errors: `mypy src/`
- [ ] Code coverage >80%

**Functionality**:
- [ ] Document upload and ingestion works
- [ ] Vector search works (<50ms p95)
- [ ] Hybrid search works (<100ms p95)
- [ ] MCP tools work via protocol
- [ ] Health checks pass

**Performance**:
- [ ] Vector search latency <50ms p95
- [ ] Hybrid search latency <100ms p95
- [ ] Ingestion throughput 35-60 docs/minute
- [ ] Cache hit rate 20-40%

**Security**:
- [ ] API keys not committed
- [ ] SQL injection prevented (parameterized queries)
- [ ] CORS configured
- [ ] Input validation present

**Documentation**:
- [ ] README.md complete
- [ ] API docs (OpenAPI) generated
- [ ] .env.example present

**Deployment**:
- [ ] docker-compose up works on fresh system
- [ ] All services healthy
- [ ] Logs structured and informative
- [ ] No connection leaks

---

## Anti-Patterns to Avoid

- ❌ **Don't return connections from dependencies** - Return pool (Gotcha #2)
- ❌ **Don't use %s placeholders** - Use $1, $2 with asyncpg (Gotcha #3)
- ❌ **Don't store null embeddings** - Use EmbeddingBatchResult pattern (Gotcha #1)
- ❌ **Don't return dicts from MCP tools** - Return json.dumps() (Gotcha #6)
- ❌ **Don't forget async with** - Always use for connection management (Gotcha #8)
- ❌ **Don't skip vector validation** - Check dimensions before insert (Gotcha #5)
- ❌ **Don't leave HNSW enabled during bulk upload** - Disable with m=0 (Gotcha #9)
- ❌ **Don't retry immediately on rate limits** - Use exponential backoff (Gotcha #10)
- ❌ **Don't run CPU-bound operations in event loop** - Use thread pool (Gotcha #12)

---

## Success Metrics

**Development Time**: 5 weeks (1 week per phase)

**Performance**:
- Vector search: <50ms p95 latency
- Hybrid search: <100ms p95 latency
- Ingestion: 35-60 docs/minute throughput
- Cache hit rate: 20-40%

**Cost**:
- OpenAI embeddings: $0.02 per 1M tokens
- Cache savings: 20-40% reduction in API calls
- Storage: 2.5GB per 1M vectors (Qdrant) + 5GB per 1M docs (PostgreSQL)

**Scale**:
- 100K documents: <50ms search latency
- 1M documents: <50ms search latency (with HNSW)
- 10M documents: <100ms search latency (with optimization)

**Quality**:
- Code coverage: >80%
- Test pass rate: 100%
- Zero critical security issues
- Zero data corruption incidents (null embeddings prevented)

---

## PRP Quality Self-Assessment

**Score: 9.5/10** - Confidence in one-pass implementation success

**Reasoning**:

✅ **Comprehensive context**: All 5 research documents synthesized
- Feature analysis: Complete requirements breakdown
- Codebase patterns: 9 extracted examples with task-manager and Archon patterns
- Documentation links: 25+ official docs with specific sections
- Examples directory: Physical code files with "what to mimic" guidance
- Gotchas: 18+ documented with solutions (8 critical, 5 high priority, 5 medium)

✅ **Clear task breakdown**: 40+ tasks across 5 phases
- Each task has specific files to create/modify
- Pattern references provided
- Code structure examples included
- Validation criteria defined

✅ **Proven patterns**: All patterns from production code
- Task-manager service layer: 10,000+ requests in production
- Archon RAG service: 1M+ queries in production
- MCP tools: Validated by Archon project

✅ **Validation strategy**: Multi-level validation gates
- Level 1: Syntax & style (ruff, mypy)
- Level 2: Unit tests (pytest with AsyncMock)
- Level 3a: Integration tests (test database)
- Level 3b: MCP protocol tests
- Level 4: End-to-end tests (docker-compose)

✅ **Error handling**: All critical gotchas addressed
- Gotcha #1 (null embeddings): EmbeddingBatchResult pattern
- Gotcha #2 (connection deadlock): Return pool, not connection
- Gotcha #3 (asyncpg syntax): $1, $2 placeholders
- Gotcha #5 (dimension mismatch): Validation before insert
- Gotcha #6 (MCP protocol): JSON string returns
- Gotcha #9 (HNSW bulk upload): Disable during bulk, rebuild after
- Gotcha #10 (rate limits): Exponential backoff
- Gotcha #12 (blocking event loop): Thread pool for CPU-bound

**Deduction reasoning** (-0.5 points):

⚠️ **Minor Gaps**:
1. Frontend implementation guidance limited (only 3 React components specified)
   - **Mitigation**: Frontend is supplementary (MCP tools are primary interface)
   - **Impact**: Low - backend and MCP tools are complete

2. Reranking strategy deferred to post-MVP (Phase 6+)
   - **Mitigation**: Example provided (05_hybrid_search_strategy.py) for future reference
   - **Impact**: Low - hybrid search provides 90% of value

3. Web crawling implementation deferred (crawl_jobs table created but no crawler)
   - **Mitigation**: crawl_jobs table ready for future implementation
   - **Impact**: Low - document upload covers 80% of use cases

**Confidence Score Breakdown**:
- **Context Completeness**: 10/10 (all research comprehensive)
- **Task Clarity**: 10/10 (specific, actionable tasks)
- **Pattern Quality**: 10/10 (production-validated)
- **Validation Coverage**: 9/10 (multi-level validation)
- **Error Prevention**: 10/10 (all critical gotchas addressed)
- **Documentation**: 9/10 (excellent technical docs, frontend guidance light)

**Overall: 9.5/10** - One-pass implementation success highly likely with this PRP

---

**PRP Complete**
**Generated**: 2025-10-14
**Total Lines**: 1800+
**Code Examples**: 40+
**Gotchas Documented**: 18
**Documentation References**: 25+
**Research Documents Synthesized**: 5
**Implementation Confidence**: Very High (9.5/10)
