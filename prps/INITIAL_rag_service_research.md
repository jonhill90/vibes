# INITIAL: RAG Service Research & Architecture

## FEATURE

Research and design a standalone RAG (Retrieval Augmented Generation) service architecture that will be extracted from Archon patterns and built as an independent, modular service following the task-manager design principles.

**Core Goal**: Make informed technology decisions for vector database, embedding providers, PostgreSQL schema, and search strategies before implementation.

**Output**: Architecture document that will guide INITIAL_rag_service_implementation.md

## EXAMPLES

### Reference Implementations

**Archon RAG Pipeline** (`~/source/vibes/infra/archon/python/src/server/services/`):
- **Study**: `search/rag_service.py` - Multi-strategy pipeline (base, hybrid, reranking, agentic)
- **Study**: `search/hybrid_search_strategy.py` - Vector + ts_vector full-text search
- **Study**: `search/reranking_strategy.py` - CrossEncoder result reranking
- **Study**: `embeddings/embedding_service.py` - Multi-provider support (OpenAI, Gemini, Ollama)
- **Study**: `storage/document_storage_service.py` - Document metadata management
- **Study**: Migration `migration/0.1.0/002_add_hybrid_search_tsvector.sql` - PostgreSQL hybrid search functions
- **Key Pattern**: Strategy pattern for swappable search approaches
- **Key Pattern**: Multi-dimensional embedding support (384, 768, 1024, 1536, 3072)

**Cole Medin's Docling RAG Agent** (`~/source/vibes/repos/ottomator-agents/docling-rag-agent/`):
- **Study**: Docling integration for document parsing
- **Study**: Hybrid chunking strategy (semantic boundaries)
- **Study**: PydanticAI agent framework
- **Study**: PostgreSQL + pgVector usage patterns
- **Key Concept**: Docling handles complex documents (tables, layout, hierarchy)
- **Key Concept**: crawl4ai for website extraction

**Task Manager Service** (`~/source/vibes/infra/task-manager/backend/src/`):
- **Study**: `services/task_service.py` - Clean service layer pattern
- **Study**: `mcp_server.py` - Consolidated MCP tools (find/manage pattern)
- **Study**: Connection pooling, async patterns, tuple[bool, dict] error handling
- **Study**: Response optimization (exclude_large_fields for MCP)
- **Reference**: This is the pattern to follow for RAG service structure

## DOCUMENTATION

### Vector Databases to Research

**Qdrant** (Primary candidate):
- Documentation: https://qdrant.tech/documentation/
- Docker: https://qdrant.tech/documentation/guides/installation/#docker
- Python client: https://github.com/qdrant/qdrant-client
- **Research**: Performance, ease of use, filtering capabilities, Docker setup

**Alternatives to Compare**:
- **Weaviate**: https://weaviate.io/developers/weaviate
- **Milvus**: https://milvus.io/docs
- **Chroma**: https://docs.trychroma.com/
- **pgvector** (PostgreSQL extension): https://github.com/pgvector/pgvector

**Evaluation Criteria**:
1. Docker deployment simplicity
2. Python async client support
3. Filtering and metadata support
4. Performance benchmarks for RAG use cases
5. Multi-vector support (different embedding dimensions)
6. Hybrid search capabilities
7. Memory footprint and resource requirements

### Document Processing

**Docling** (Decided):
- GitHub: https://github.com/docling-project/docling
- Documentation: https://docling-project.github.io/docling/
- **Already researched**: See `01-notes/01r-research/202510111423`
- **Key Features**: Table preservation, document hierarchy, hybrid chunking, audio support
- **Better than**: Archon's pypdf2/pdfplumber approach

**crawl4ai** (For web crawling):
- GitHub: https://github.com/unclecode/crawl4ai
- Archon uses: v0.6.2
- **Key Features**: Built for AI/LLM use cases, smart doc site detection, JavaScript rendering
- **Decision**: Keep this from Archon (it's actually good)

### Embedding Providers to Research

**OpenAI** (Industry standard):
- Models: text-embedding-3-small, text-embedding-3-large, text-embedding-ada-002
- Dimensions: 1536 (small), 3072 (large)
- Documentation: https://platform.openai.com/docs/guides/embeddings

**Alternatives**:
- **Local models via Ollama**: Free, private, various dimensions
- **Google Gemini**: text-embedding-004/005
- **Sentence Transformers**: Local, various dimensions (384, 768, 1024)

**Research Questions**:
1. Which provider(s) to support initially?
2. Multi-provider switching strategy (like Archon)?
3. Caching strategy for embeddings?
4. Cost vs quality trade-offs?

## OTHER CONSIDERATIONS

### Architecture Decisions to Make

#### 1. Vector Database Selection

**Compare**: Qdrant vs Weaviate vs Milvus vs pgvector

**Research Areas**:
- Setup complexity (Docker, configuration)
- Query performance (benchmark with test data)
- Filtering capabilities (metadata, date ranges, source filtering)
- Python async client quality
- Resource usage (memory, CPU)
- Hybrid search support
- Community and documentation quality

**Decision Criteria**:
- Must: Docker deployment, Python async client
- Must: Good filtering and metadata support
- Prefer: Low memory footprint
- Prefer: Simple setup and maintenance
- Nice: Built-in hybrid search

**Output**: Documented choice with rationale

#### 2. PostgreSQL Schema Design

**Tables to Design**:

**documents**:
- Metadata storage (title, source, url, type, created_at, etc.)
- NOT storing vectors (that's in vector DB)
- Link to vector DB via document_id

**sources**:
- Track ingestion sources (uploaded files, crawled sites)
- Source metadata (url, type, last_crawled, status)

**chunks** (if needed):
- Chunk metadata (document_id, chunk_index, token_count)
- Link to vector DB vectors
- Optional: Store chunk text or rely on vector DB?

**crawl_jobs** (if web crawling):
- Track crawl status (pending, running, completed, failed)
- Progress tracking, error logs

**Research Questions**:
1. Store chunk text in PostgreSQL or only in vector DB?
2. How to link PostgreSQL records to vector DB records?
3. What indexes are needed for common queries?
4. Timestamp strategy (created_at, updated_at, last_accessed)?
5. Soft delete vs hard delete?

**Output**: Complete schema with CREATE TABLE statements

#### 3. Search Strategy Design

**From Archon, consider**:
- Base vector search (cosine similarity)
- Hybrid search (vector + full-text PostgreSQL ts_vector)
- Reranking (CrossEncoder for better ordering)
- Code example extraction (specialized search)

**Research Questions**:
1. Start with simple vector search only, or implement hybrid from day 1?
2. If hybrid: Use vector DB's hybrid search or separate PostgreSQL ts_vector?
3. Reranking: Include initially or add later?
4. How to handle result deduplication?
5. Pagination strategy for large result sets?

**Decision**: Which strategies to include in MVP vs future

**Output**: Search pipeline design

#### 4. Embedding Provider Strategy

**Research Questions**:
1. Single provider initially (OpenAI?) or multi-provider from start?
2. If multi-provider: How to handle different dimensions?
3. Caching strategy (cache embeddings to avoid regeneration)?
4. Rate limiting and error handling?
5. Cost optimization strategies?

**Output**: Provider support plan and configuration design

#### 5. Document Processing Pipeline

**Steps**:
1. Upload/Crawl → Raw document
2. Parse → Docling (structured format)
3. Chunk → Hybrid chunking (semantic boundaries)
4. Embed → Generate vectors
5. Store → Vector DB + PostgreSQL metadata

**Research Questions**:
1. Synchronous or async processing (job queue)?
2. Progress tracking for large documents?
3. Error handling and retry strategy?
4. Temporary storage for uploaded files?
5. Webhook or polling for completion status?

**Output**: Pipeline flow diagram and implementation notes

### Service Architecture Design

**Following Task Manager Pattern**:

**Backend Structure**:
```
backend/
├── src/
│   ├── main.py              # FastAPI app
│   ├── mcp_server.py        # MCP tools (consolidated)
│   ├── config/
│   │   └── database.py      # PostgreSQL + Vector DB connections
│   ├── models/
│   │   ├── document.py      # Document data models
│   │   └── source.py        # Source data models
│   ├── services/
│   │   ├── rag_service.py   # Search, embed, retrieve
│   │   ├── document_service.py  # Document CRUD
│   │   └── ingestion_service.py # Parse, chunk, embed pipeline
│   ├── api/
│   │   ├── documents.py     # REST endpoints
│   │   └── search.py        # REST endpoints
│   └── utils/
│       └── etag.py          # Response optimization
├── tests/
└── alembic/                 # Migrations
```

**MCP Tools to Design**:
```python
# Consolidated search tool
search_knowledge_base(
    query: str,
    source_id: str | None = None,
    match_count: int = 5,
    search_type: str = "vector"  # "vector" | "hybrid" | "code"
)

# Document management tool
manage_document(
    action: str,  # "upload" | "delete" | "get"
    document_id: str | None = None,
    file_path: str | None = None,
    source_id: str | None = None
)

# Source management tool
manage_source(
    action: str,  # "list" | "create" | "delete" | "get"
    source_id: str | None = None,
    url: str | None = None,
    source_type: str | None = None  # "upload" | "crawl"
)

# Crawl tool (if web crawling in MVP)
crawl_website(
    url: str,
    recursive: bool = False,
    max_pages: int = 100
)
```

**Research Question**: What other tools are needed for MVP?

### Technology Stack Summary

**To Decide**:
- Vector DB: Qdrant | Weaviate | Milvus | pgvector
- Embedding: OpenAI only | Multi-provider
- PostgreSQL version: 15+ (for better performance)
- Python: 3.11+ (async improvements)
- Document parsing: Docling (decided)
- Web crawling: crawl4ai (decided)
- Frontend: React + TypeScript (following task-manager)

**Output**: Complete tech stack with versions

### Key Research Questions Summary

**High Priority** (Must answer for INITIAL 2):
1. Which vector database? (Qdrant vs alternatives)
2. PostgreSQL schema design?
3. Which embedding provider(s) initially?
4. Which search strategies in MVP? (vector only vs hybrid)
5. MCP tools consolidation pattern?

**Medium Priority** (Decide but can adjust):
6. Async processing for ingestion?
7. Reranking in MVP or later?
8. Chunk text storage location?
9. Rate limiting strategy?
10. Web crawling in INITIAL 2 or separate INITIAL 3?

**Low Priority** (Can defer):
11. Multi-tenancy support?
12. Advanced filtering features?
13. Analytics and usage tracking?

### Success Criteria for This INITIAL

**Deliverable**: Architecture document (`prps/rag_service_research/ARCHITECTURE.md`)

**Must Include**:
- [ ] Vector database choice with comparison table and rationale
- [ ] Complete PostgreSQL schema (CREATE TABLE statements)
- [ ] Embedding provider strategy (which to support, configuration)
- [ ] Search pipeline design (which strategies, flow diagram)
- [ ] Document ingestion pipeline design (steps, error handling)
- [ ] MCP tools specification (tool names, parameters, return types)
- [ ] Service layer architecture (classes, responsibilities)
- [ ] Technology stack summary (versions, dependencies)
- [ ] Docker compose structure (services, ports, volumes)
- [ ] Environment variable template (.env.example content)

**Should Include**:
- [ ] Performance considerations and benchmarks
- [ ] Cost estimates (embedding API costs, infrastructure)
- [ ] Migration strategy (alembic setup)
- [ ] Testing strategy (unit, integration, MCP tool testing)
- [ ] Comparison with Archon approach (what we're keeping/changing)

**Nice to Have**:
- [ ] API endpoint documentation (OpenAPI spec outline)
- [ ] Frontend component structure
- [ ] Deployment notes (production considerations)

### Research Process

**Phase 1: Vector Database Research** (2-3 hours)
1. Read documentation for Qdrant, Weaviate, Milvus
2. Set up minimal Docker containers for top 2 candidates
3. Test basic operations (insert, query, filter)
4. Benchmark query performance with sample data
5. Document findings in comparison table

**Phase 2: Schema Design** (1-2 hours)
1. Review Archon's schema
2. Design PostgreSQL tables
3. Plan indexes and constraints
4. Document relationships with vector DB
5. Write CREATE TABLE statements

**Phase 3: Search Strategy Design** (1-2 hours)
1. Review Archon's search strategies
2. Design MVP search pipeline
3. Plan for future enhancements (reranking, etc.)
4. Document query flow and response format

**Phase 4: Integration Planning** (1 hour)
1. Design MCP tools (parameters, responses)
2. Plan service layer structure
3. Define API contracts (REST endpoints)
4. Document configuration strategy

**Phase 5: Documentation** (1 hour)
1. Compile all research into ARCHITECTURE.md
2. Add diagrams (architecture, data flow)
3. List dependencies and versions
4. Create .env.example template

**Total Estimated Time**: 6-9 hours

### Output Format

**File**: `prps/rag_service_research/ARCHITECTURE.md`

**Structure**:
```markdown
# RAG Service Architecture

## Executive Summary
[Key decisions and rationale]

## Technology Stack
[Versions and dependencies]

## Vector Database
[Choice, comparison, rationale]

## PostgreSQL Schema
[Complete CREATE TABLE statements]

## Search Pipeline
[Strategy design, flow diagram]

## Document Ingestion
[Pipeline steps, error handling]

## Service Layer
[Class structure, responsibilities]

## MCP Tools
[Tool specifications]

## Docker Compose
[Service structure]

## Configuration
[Environment variables, .env.example]

## Performance Considerations
[Benchmarks, optimizations]

## Cost Estimates
[API costs, infrastructure]

## Migration from Archon
[What we keep, what we change]

## Testing Strategy
[Unit, integration, MCP testing]

## Next Steps
[Ready for INITIAL_rag_service_implementation]
```

### Integration with Vibes

**Proposed Location**: `/Users/jon/source/vibes/infra/rag-service/`

**Standalone Nature**:
- Does NOT depend on task-manager or other MCP servers
- Own database (PostgreSQL + vector DB)
- Can run independently
- Listed in main vibes README under MCP servers
- Optional: Future integration with task-manager (link tasks to documents)

### Known Constraints

**From Task Manager Experience**:
- Follow service layer pattern (like TaskService)
- Use consolidated MCP tools (find/manage pattern)
- Implement response optimization (exclude_large_fields)
- Use tuple[bool, dict] error handling
- PostgreSQL connection pooling with asyncpg
- Docker compose with health checks

**From Archon Analysis**:
- Don't tightly couple components
- Make embedding provider swappable
- Make vector DB swappable
- Support multiple embedding dimensions
- Plan for future enhancements (reranking, etc.)

**General**:
- Must be production-ready from start
- Must follow MCP best practices
- Must have comprehensive error handling
- Must be well-documented

### Future Enhancements (Not This INITIAL)

**After MVP**:
- Advanced reranking strategies
- Multiple embedding providers
- Knowledge graph integration (Graphiti + Neo4j)
- Agent memory integration (Mem0)
- Advanced filtering and faceting
- Usage analytics
- Multi-user support with permissions
- API key management
- Webhook notifications
- Export/import capabilities
- Advanced chunking strategies
- Document version control
- Collaboration features (annotations, sharing)

**Integration Possibilities**:
- Link to task-manager (attach documents to tasks)
- Link to basic-memory (cross-reference notes)
- Build on this foundation for agentic workflows
