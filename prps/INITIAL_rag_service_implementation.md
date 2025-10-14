# INITIAL: RAG Service Implementation

## FEATURE

Implement a production-ready standalone RAG (Retrieval Augmented Generation) service based on the comprehensive architecture documented in `prps/rag_service_research/ARCHITECTURE.md`.

**Core Goal**: Build a fully functional RAG service with vector search, hybrid search, document ingestion, and MCP tools following task-manager patterns and Archon's proven RAG pipeline design.

**Output**: Working RAG service deployable via Docker Compose with all Phase 1-5 features complete.

## EXAMPLES

### Reference Architecture

**Architecture Document** (`~/source/vibes/prps/rag_service_research/ARCHITECTURE.md`):
- **Study**: Complete architecture with technology decisions
- **Study**: PostgreSQL schema with indexes and triggers (lines 2150-2306)
- **Study**: Service layer patterns with tuple[bool, dict] (lines 992-1219)
- **Study**: MCP tools specification (lines 812-988)
- **Study**: Docker Compose configuration (lines 1222-1467)
- **Study**: 8 critical gotchas with solutions (from research PRP)

**Flow Diagrams** (`~/source/vibes/repos/Notes.md`):
- **Reference**: High-level RAG flow (ASCII + Mermaid diagrams)
- **9-Step Pipeline**: Crawl/Upload → Parse (Docling) → Chunk → Embed → Store → Search → Merge/Rerank → LLM Query → Generate Response
- **Key Insight**: Docling is the parsing entry point (not just chunking)
- **Key Insight**: Dual storage pattern (PostgreSQL metadata/FTS + Qdrant vectors)
- **Performance Notes**: Base vector ~50ms, Hybrid ~100ms, Ingestion ~650-1600ms/doc

### Reference Code Patterns

**Code Examples** (`~/source/vibes/prps/rag_service_research/examples/`):
- **Pattern 1**: `01_service_layer_pattern.py` - DocumentService with asyncpg
- **Pattern 2**: `02_mcp_consolidated_tools.py` - find/manage consolidated tools
- **Pattern 3**: `03_rag_search_pipeline.py` - Strategy coordinator pattern
- **Pattern 4**: `04_base_vector_search.py` - Vector similarity search
- **Pattern 5**: `05_hybrid_search_strategy.py` - Vector + full-text combined
- **Pattern 6**: `06_transaction_pattern.py` - Atomic multi-step operations
- **Pattern 7**: `07_fastapi_endpoint_pattern.py` - REST API structure

**Archon RAG Implementation** (`~/source/vibes/infra/archon/python/src/server/services/`):
- **Extract**: `search/rag_service.py` - Strategy coordinator
- **Extract**: `search/base_search_strategy.py` - Vector search
- **Extract**: `search/hybrid_search_strategy.py` - Hybrid search
- **Extract**: `embeddings/embedding_service.py` - Batch embedding

**Task Manager Patterns** (`~/source/vibes/infra/task-manager/backend/src/`):
- **Follow**: `services/task_service.py` - Service layer pattern
- **Follow**: `mcp_server.py` - Consolidated MCP tools
- **Follow**: `config/database.py` - Connection pooling

## DOCUMENTATION

### Technology Stack

**Vector Database**:
- Qdrant: https://qdrant.tech/documentation/
- AsyncQdrantClient: https://github.com/qdrant/qdrant-client
- Docker setup: https://qdrant.tech/documentation/guides/installation/#docker

**PostgreSQL + pgvector**:
- PostgreSQL 15: https://www.postgresql.org/docs/15/
- asyncpg: https://magicstack.github.io/asyncpg/current/
- Full-text search: https://www.postgresql.org/docs/current/textsearch.html
- pgvector extension: https://github.com/pgvector/pgvector

**FastAPI**:
- Async patterns: https://fastapi.tiangolo.com/async/
- Lifespan events: https://fastapi.tiangolo.com/advanced/events/
- Dependency injection: https://fastapi.tiangolo.com/tutorial/dependencies/

**OpenAI Embeddings**:
- API documentation: https://platform.openai.com/docs/guides/embeddings
- text-embedding-3-small: 1536 dimensions, $0.02 per 1M tokens
- Rate limits: 3,000 RPM, 1,000,000 TPM

**Document Processing**:
- Docling: https://docling-project.github.io/docling/
- Already researched in: `01-notes/01r-research/202510111423`

## OTHER CONSIDERATIONS

### Implementation Phases

This INITIAL focuses on **Phases 1-5** (8-week timeline):

**Phase 1: Core Setup** (Week 1)
- Directory structure (backend/, frontend/, database/)
- Docker Compose with PostgreSQL, Qdrant, FastAPI, Frontend
- PostgreSQL schema (database/scripts/init.sql) with all 5 tables (sources, documents, chunks, crawl_jobs, embedding_cache)
- PostgreSQL indexes and triggers (updated_at, tsvector updates)
- Qdrant collection initialization (1536 dims, cosine distance)
- FastAPI with lifespan connection pools (asyncpg + AsyncQdrantClient)
- Health check endpoints (validate dual storage readiness)
- Frontend scaffolding (Vite + React + TypeScript)

**Phase 2: Service Layer** (Week 2)
- DocumentService, SourceService (tuple[bool, dict] pattern)
- VectorService (Qdrant operations)
- EmbeddingService (OpenAI with quota handling)
- Connection pool management

**Phase 3: Search Pipeline** (Week 3)
- **Step 6**: BaseSearchStrategy (vector similarity, <50ms p95)
- **Step 6**: HybridSearchStrategy (0.7×vector + 0.3×text_rank, <100ms p95)
- **Step 7**: Result merging and deduplication
- **Step 8-9**: RAGService coordinator (pass top-k chunks to LLM)
- Configuration-driven strategy selection (USE_HYBRID_SEARCH)

**Phase 4: Document Ingestion** (Week 4)
- **Step 1-2**: Crawl/Upload → Docling parser (PDF, HTML, DOCX)
- **Step 3**: Semantic chunking (~500 tokens, respect boundaries)
- **Step 4**: Batch embedding via OpenAI (1536-dim vectors)
- **Step 5**: Atomic storage (PostgreSQL metadata/FTS + Qdrant vectors)
- EmbeddingBatchResult pattern (prevent quota exhaustion corruption)
- MD5 hash-based embedding cache lookup

**Phase 5: MCP Tools** (Week 5)
- search_knowledge_base tool
- manage_document tool (consolidated CRUD)
- manage_source tool
- JSON string returns, payload optimization

**Phase 6-8**: Testing, Documentation, Deployment (covered in future INITIALs)

### Implementation Guidance (From Notes.md Feedback)

**Critical Design Principles**:

1. **Docling as Parsing Entry Point**
   - Docling handles ALL parsing (PDF, HTML, DOCX, tables, layout)
   - Do NOT use pypdf2/pdfplumber alternatives
   - Docling outputs structured format → then chunk
   - Preserves document hierarchy and tables

2. **Dual Storage Pattern**
   - PostgreSQL: Metadata (title, source, created_at) + Full-text search (tsvector)
   - Qdrant: Vector embeddings only (1536-dim for text-embedding-3-small)
   - Link via document_id/chunk_id
   - NEVER store vectors in PostgreSQL, NEVER store metadata in Qdrant

3. **Hybrid Search Fusion**
   - Vector search score: 1 - cosine_distance (0.0-1.0 range)
   - Text search score: ts_rank normalized (0.0-1.0 range)
   - Combined: 0.7 × vector_score + 0.3 × text_score
   - Normalize BEFORE combining (critical!)

4. **Dimensionality Consistency**
   - OpenAI text-embedding-3-small: Always 1536 dimensions
   - Qdrant collection: Initialize with size=1536, distance=Cosine
   - Validate vector length before insert (prevent dimension mismatch)
   - Document in logs/errors: "Expected 1536 dimensions"

5. **Latency Annotations**
   - Base vector search: Target <50ms p95
   - Hybrid search: Target <100ms p95
   - Document ingestion: 650-1600ms per document
   - Log actual latencies during development for comparison

### Technology Stack Summary

**Backend** (from ARCHITECTURE.md):
- **Python**: 3.11+ (async improvements)
- **FastAPI**: Latest (async web framework)
- **PostgreSQL**: 15-alpine
- **Qdrant**: v1.7.4+ (vector database)
- **asyncpg**: Latest (async PostgreSQL client)
- **OpenAI SDK**: Latest (embeddings)
- **Docling**: Latest (document parsing)
- **Pydantic**: 2.x (settings and validation)

**Frontend** (following task-manager pattern):
- **React**: 18+ with TypeScript
- **Vite**: Latest (dev server and build tool)
- **TanStack Query**: v5 (data fetching and caching)
- **React Router**: v6 (routing)
- **Tailwind CSS**: v3 (styling)
- **Shadcn/ui**: Component library (optional)

### Directory Structure

Target structure (following task-manager pattern):

```
infra/rag-service/
├── backend/
│   ├── src/
│   │   ├── main.py                  # FastAPI app with lifespan
│   │   ├── mcp_server.py            # MCP server entry
│   │   ├── config/
│   │   │   ├── settings.py          # Pydantic Settings
│   │   │   └── database.py          # asyncpg + Qdrant pool setup
│   │   ├── models/
│   │   │   ├── document.py          # Pydantic models
│   │   │   ├── source.py
│   │   │   └── chunk.py
│   │   ├── services/
│   │   │   ├── document_service.py  # Document CRUD
│   │   │   ├── source_service.py    # Source management
│   │   │   ├── vector_service.py    # Qdrant operations
│   │   │   ├── embeddings/
│   │   │   │   └── embedding_service.py
│   │   │   └── search/
│   │   │       ├── rag_service.py   # Coordinator
│   │   │       ├── base_search_strategy.py
│   │   │       └── hybrid_search_strategy.py
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── health.py        # Health checks
│   │   │   │   ├── documents.py     # Document endpoints
│   │   │   │   └── search.py        # Search endpoints
│   │   │   └── dependencies.py      # FastAPI dependencies
│   │   ├── tools/
│   │   │   ├── search_tools.py      # MCP search tools
│   │   │   ├── document_tools.py    # MCP document tools
│   │   │   └── source_tools.py      # MCP source tools
│   │   └── utils/
│   │       ├── logging.py
│   │       └── response.py          # MCP optimization
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── mcp/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── pyproject.toml
├── database/
│   ├── migrations/
│   │   └── 001_initial_schema.sql
│   ├── seeds/
│   │   └── README.md
│   └── scripts/
│       └── init.sql                 # Initial schema
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── DocumentList.tsx
│   │   │   ├── SearchBar.tsx
│   │   │   └── SearchResults.tsx
│   │   ├── pages/
│   │   │   ├── Documents.tsx
│   │   │   └── Search.tsx
│   │   ├── services/
│   │   │   └── api.ts               # API client
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── docker-compose.yml
├── .env.example
└── README.md
```

### Critical Gotchas (From Research PRP)

**NEVER Violate These Patterns**:

1. **OpenAI Quota Exhaustion** → Use EmbeddingBatchResult, NEVER store null embeddings
2. **FastAPI Connection Pool** → Return pool (not connections) from dependencies
3. **asyncpg Placeholders** → Use $1, $2 (NOT %s) to prevent SQL injection
4. **Row Locking Deadlock** → Always use ORDER BY id with FOR UPDATE
5. **Qdrant Dimension** → Validate vector dimensions before insert (1536 for text-embedding-3-small)
6. **MCP JSON Strings** → Tools MUST return json.dumps(), not dicts
7. **MCP Payload Size** → Truncate content to 1000 chars max
8. **Connection Leaks** → Always use async with for connection acquisition

### Success Criteria

**Phase 1 Complete When**:
- [ ] Directory structure matches task-manager pattern (backend/, frontend/, database/)
- [ ] Docker Compose starts all services (postgres, qdrant, api, frontend)
- [ ] PostgreSQL schema created from database/scripts/init.sql with all 5 tables
- [ ] All indexes and triggers created
- [ ] Qdrant collection initialized (1536 dims, cosine)
- [ ] Health check endpoints return 200
- [ ] Connection pools working (no deadlock)
- [ ] Frontend dev server accessible (http://localhost:5173)

**Phase 2 Complete When**:
- [ ] DocumentService implements all CRUD methods
- [ ] SourceService implements all CRUD methods
- [ ] All methods return tuple[bool, dict]
- [ ] VectorService can upsert/search/delete vectors
- [ ] EmbeddingService handles quota exhaustion correctly
- [ ] Unit tests pass for all services

**Phase 3 Complete When**:
- [ ] BaseSearchStrategy performs vector search
- [ ] HybridSearchStrategy combines vector + full-text
- [ ] RAGService coordinates strategies
- [ ] Configuration toggles work (USE_HYBRID_SEARCH)
- [ ] Search results include scores and metadata
- [ ] Search latency <100ms for hybrid

**Phase 4 Complete When**:
- [ ] Docling parser can process PDF/HTML/DOCX
- [ ] Semantic chunking respects boundaries
- [ ] Batch embedding uses OpenAI API correctly
- [ ] EmbeddingBatchResult tracks successes/failures
- [ ] Cache lookup works (MD5 hash)
- [ ] PostgreSQL + Qdrant atomic transaction
- [ ] Can ingest 35+ docs/minute

**Phase 5 Complete When**:
- [ ] search_knowledge_base tool works
- [ ] manage_document tool works (all actions)
- [ ] manage_source tool works (all actions)
- [ ] All tools return JSON strings (not dicts)
- [ ] Payload truncation implemented
- [ ] Pagination limits enforced (20 max)
- [ ] MCP tests pass

### Quality Gates

**Before Moving to Phase 2**:
- All Phase 1 success criteria met
- docker-compose up succeeds
- Health checks pass
- No connection pool errors in logs

**Before Moving to Phase 3**:
- All Phase 2 success criteria met
- Unit tests >80% coverage for services
- No tuple[bool, dict] violations

**Before Moving to Phase 4**:
- All Phase 3 success criteria met
- Search accuracy validated (manual testing)
- Latency benchmarks met

**Before Moving to Phase 5**:
- All Phase 4 success criteria met
- Can ingest 100+ documents successfully
- No quota exhaustion data corruption

**Final Gate (Phase 5)**:
- All MCP tools tested and working
- Integration tests pass
- Ready for Phase 6 (testing/deployment)

### Known Constraints

**From ARCHITECTURE.md**:
- MVP uses OpenAI only (no multi-provider yet)
- No reranking in initial phases (post-MVP)
- No web crawling in Phase 1-5 (optional later)
- Standard Python logging (no Logfire)
- Simple rate limiting (no complex threading service)

**From Task Manager Experience**:
- Must use tuple[bool, dict] for service returns
- Must use consolidated find/manage tool pattern
- Must optimize MCP responses (exclude_large_fields)
- Must use asyncpg connection pooling correctly

**Infrastructure**:
- Docker Compose for local development
- PostgreSQL 15-alpine
- Qdrant latest
- Self-hosted (not managed services)

### Validation Strategy

**Manual Testing Checklist (Per Phase)**:

Phase 1:
- docker-compose up -d (all services start: postgres, qdrant, api, frontend)
- docker-compose ps (all healthy)
- curl http://localhost:8000/health (200 OK - Backend)
- curl http://localhost:5173 (Frontend accessible)
- curl http://localhost:6333/collections (Qdrant accessible)
- psql connection test (PostgreSQL accessible)
- Verify database/scripts/init.sql executed successfully

Phase 2:
- Create document via DocumentService
- List documents with pagination
- Delete document (cascades to chunks)
- Check tuple[bool, dict] returns

Phase 3:
- Search with base strategy
- Search with hybrid strategy
- Toggle USE_HYBRID_SEARCH config
- Verify score combining

Phase 4:
- Ingest PDF document
- Ingest HTML document
- Check embedding cache hit
- Verify no null embeddings

Phase 5:
- Call search_knowledge_base via MCP
- Call manage_document via MCP
- Verify JSON string returns
- Check payload truncation

### Performance Targets (From ARCHITECTURE.md)

**Search Latency**:
- Base vector: <50ms p95
- Hybrid: <100ms p95

**Ingestion**:
- 35-60 docs/minute
- Per document: 650-1600ms

**Memory**:
- 100K vectors: 750MB total
- 1M vectors: 4GB total

**Cost (MVP)**:
- Infrastructure: $40-60/month
- Embeddings: $1/month
- Total: $41-61/month

### Future Enhancements (Not This INITIAL)

**Phase 6**: Testing (Week 6)
- Unit tests (80% coverage)
- Integration tests
- Performance tests
- MCP tool tests

**Phase 7**: Documentation & Deployment (Week 7)
- API documentation
- Deployment guide
- Production docker-compose

**Phase 8**: Production Launch (Week 8)
- Load testing
- Security review
- Monitoring setup
- Deploy to staging

**Post-MVP**:
- Reranking strategy (CrossEncoder)
- Web crawling (crawl4ai)
- Multi-provider embeddings
- Advanced analytics
- Real-time search updates (WebSockets)
- Document collaboration features

### Risk Mitigation

**High Risk Areas**:

1. **OpenAI Quota Exhaustion**
   - Mitigation: EmbeddingBatchResult pattern
   - Validation: Test with low quota limit
   - Reference: Gotcha #1 in research PRP

2. **Connection Pool Deadlock**
   - Mitigation: Return pool (not connections)
   - Validation: Load test with 100 concurrent requests
   - Reference: Gotcha #2 in research PRP

3. **Qdrant Dimension Mismatch**
   - Mitigation: Validate vector length before insert
   - Validation: Unit tests with wrong dimensions
   - Reference: Gotcha #5 in research PRP

4. **MCP Protocol Violations**
   - Mitigation: JSON string returns, payload optimization
   - Validation: MCP tool tests
   - Reference: Gotchas #6, #7 in research PRP

### Integration with Vibes

**Location**: `/Users/jon/source/vibes/infra/rag-service/`

**Standalone Nature**:
- Independent service (own database, own Docker Compose)
- Can run without other MCP servers
- Optional: Future integration with task-manager

**MCP Server Configuration**:
Add to vibes MCP config after implementation:
```json
{
  "mcpServers": {
    "rag-service": {
      "command": "python",
      "args": ["-m", "mcp_server.main"],
      "cwd": "/Users/jon/source/vibes/infra/rag-service/backend",
      "env": {
        "DATABASE_URL": "postgresql://...",
        "QDRANT_URL": "http://localhost:6333",
        "OPENAI_API_KEY": "..."
      }
    }
  }
}
```

### Development Workflow

**Phase-by-Phase Approach**:

1. Start with Phase 1 (Core Setup)
2. Validate Phase 1 success criteria
3. Commit Phase 1 work
4. Move to Phase 2 (Service Layer)
5. Validate Phase 2 success criteria
6. Commit Phase 2 work
7. Continue through Phase 5

**Git Workflow**:
- Branch: `feature/rag-service-phase-{N}`
- Commit after each phase completion
- Tag: `rag-service-phase-{N}-complete`

**Testing Strategy**:
- Manual testing after each phase
- Unit tests written alongside services
- Integration tests in Phase 6

### Next Steps After This INITIAL

**INITIAL_rag_service_testing.md** (Phase 6):
- Unit test suite (80% coverage)
- Integration test suite
- Performance benchmarks
- MCP tool testing

**INITIAL_rag_service_deployment.md** (Phases 7-8):
- Production Docker Compose
- Monitoring setup
- Security hardening
- Deployment guide
