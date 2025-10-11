# Feature Analysis: RAG Service Research

## INITIAL.md Summary

This is a research-focused PRP to design a standalone RAG (Retrieval Augmented Generation) service architecture extracted from Archon patterns. The goal is to make informed technology decisions for vector database, embedding providers, PostgreSQL schema, and search strategies before implementation. The output will be an architecture document guiding the subsequent implementation PRP.

## Core Requirements

### Explicit Requirements

1. **Research Phase**: Evaluate and document technology choices before implementation
2. **Standalone Service**: Independent from Archon and other MCP servers
3. **Technology Decisions**: Choose vector database, embedding providers, PostgreSQL schema design, and search strategies
4. **Architecture Document**: Comprehensive documentation to guide implementation
5. **Reference Implementations**: Study Archon RAG pipeline, Cole Medin's Docling RAG Agent, and Task Manager service patterns
6. **Deliverable**: ARCHITECTURE.md file with complete specifications

### Implicit Requirements

1. **Production-Ready Design**: Must be deployable and maintainable from day one
2. **MCP Integration**: Follow task-manager consolidated MCP tool pattern
3. **Docker Deployment**: Must run in Docker Compose environment
4. **Scalability Considerations**: Support multiple embedding dimensions and swappable components
5. **Service Layer Pattern**: Follow established backend architecture (FastAPI, async, service layer)
6. **Error Handling**: Comprehensive error handling with tuple[bool, dict] pattern
7. **Testing Strategy**: Unit, integration, and MCP tool testing approach
8. **Performance Optimization**: Response optimization, connection pooling, async patterns

## Technical Components

### Data Models

**PostgreSQL Tables**:
- `documents` - Document metadata (title, source, url, type, timestamps)
- `sources` - Ingestion source tracking (uploaded files, crawled sites)
- `chunks` - Chunk metadata (document_id, chunk_index, token_count, optional text storage)
- `crawl_jobs` - Web crawl status tracking (pending, running, completed, failed)

**Key Design Question**: Store chunk text in PostgreSQL or only in vector DB?

**Vector Database Records**:
- Document vectors with embeddings (384, 768, 1024, 1536, 3072 dimensions)
- Metadata for filtering (source, document_id, chunk_index)
- Link to PostgreSQL via document_id/chunk_id

### External Integrations

**Vector Databases (To Evaluate)**:
- Qdrant (primary candidate)
- Weaviate
- Milvus
- Chroma
- pgvector (PostgreSQL extension)

**Document Processing**:
- Docling (decided) - Table preservation, document hierarchy, hybrid chunking, audio support
- crawl4ai (decided) - Web crawling with JavaScript rendering and smart doc site detection

**Embedding Providers**:
- OpenAI (text-embedding-3-small, text-embedding-3-large, text-embedding-ada-002)
- Google Gemini (text-embedding-004/005)
- Ollama (local models, various dimensions)
- Sentence Transformers (local, 384/768/1024 dimensions)

**Infrastructure**:
- PostgreSQL 15+ with asyncpg
- Docker and Docker Compose
- Python 3.11+ with FastAPI

### Core Logic

**Document Ingestion Pipeline**:
1. Upload/Crawl → Raw document
2. Parse → Docling (structured format)
3. Chunk → Hybrid chunking (semantic boundaries)
4. Embed → Generate vectors
5. Store → Vector DB + PostgreSQL metadata

**Search Strategies** (from Archon analysis):
- Base vector search (cosine similarity)
- Hybrid search (vector + PostgreSQL ts_vector full-text)
- Reranking (CrossEncoder for better ordering)
- Code example extraction (specialized search)

**MCP Tools** (consolidated pattern):
- `search_knowledge_base(query, source_id?, match_count?, search_type?)` - Main search
- `manage_document(action, document_id?, file_path?, source_id?)` - Document CRUD
- `manage_source(action, source_id?, url?, source_type?)` - Source management
- `crawl_website(url, recursive?, max_pages?)` - Web crawling

### UI/CLI Requirements

**Frontend** (following task-manager):
- React + TypeScript
- TanStack Query for data fetching
- Tailwind CSS
- Component structure mirroring backend resources

**REST API Endpoints**:
- `/api/documents` - Document CRUD
- `/api/sources` - Source management
- `/api/search` - Search operations
- `/api/crawl` - Crawl operations

## Similar Implementations Found in Archon

### 1. Archon RAG Service Implementation

- **Relevance**: 10/10
- **Archon Location**: `~/source/vibes/infra/archon/python/src/server/services/search/`
- **Key Patterns**:
  - **Strategy Pattern**: Swappable search approaches (base, hybrid, reranking, agentic)
  - **Service Coordinator**: `rag_service.py` acts as thin coordinator delegating to strategies
  - **Multi-dimensional Support**: Handles embeddings of 384, 768, 1024, 1536, 3072 dimensions
  - **Pipeline Architecture**: Base → Hybrid (if enabled) → Reranking (if enabled)
  - **Configuration-Driven**: Settings control which strategies are active
  - **Error Handling**: Graceful degradation (e.g., reranking fails → continue with vector results)

**What to Reuse**:
- Strategy pattern for search approaches
- Multi-dimensional embedding support
- Pipeline architecture with optional stages
- Configuration-driven feature enablement
- Service layer coordination pattern

**Gotchas to Avoid**:
- Tight coupling between components (Archon is refactoring this)
- Complex initialization logic
- Settings retrieval from credential service (simpler env vars for standalone)

### 2. Task Manager Service Pattern

- **Relevance**: 9/10
- **Archon Location**: `~/source/vibes/infra/task-manager/backend/src/services/task_service.py`
- **Key Patterns**:
  - **Service Layer Design**: Clean separation of concerns
  - **Async Patterns**: asyncpg with connection pooling
  - **Error Handling**: `tuple[bool, dict]` return pattern for all operations
  - **Validation**: Field validation before database operations
  - **Transaction Management**: `async with conn.transaction()` for atomic operations
  - **Row Locking**: `SELECT ... FOR UPDATE ORDER BY id` to prevent deadlocks
  - **Response Optimization**: Conditional field selection for performance

**What to Reuse**:
- Service class structure with db_pool in __init__
- tuple[bool, dict] error handling pattern
- Async context managers for connections
- Validation methods
- Pagination with offset/limit
- Response field optimization (exclude_large_fields pattern)

**Gotchas Addressed**:
- Always use `async with` for connection management (Gotcha #12)
- Use $1, $2 placeholders (asyncpg), not %s (Gotcha #7)
- Row locking with ORDER BY id to prevent deadlocks (Gotcha #2)

### 3. MCP Server Consolidated Tools

- **Relevance**: 9/10
- **Archon Location**: `~/source/vibes/infra/task-manager/backend/src/mcp_server.py`
- **Key Patterns**:
  - **Consolidated Tools**: `find_tasks()` handles list/search/get, `manage_task()` handles create/update/delete
  - **Action-Based Operations**: Single tool with "action" parameter ("create", "update", "delete")
  - **Response Optimization**: Truncate descriptions to 1000 chars for MCP (Gotcha #3)
  - **JSON Returns**: Tools MUST return JSON strings, never dicts (Gotcha #3)
  - **Structured Errors**: `{"success": false, "error": "...", "suggestion": "..."}`
  - **Multi-Mode Queries**: Single tool handles different query modes (by ID, by filter, all)

**What to Reuse**:
- find/manage tool consolidation pattern
- Response truncation for MCP (MAX_DESCRIPTION_LENGTH = 1000)
- Structured error responses with suggestions
- Multi-mode query handling in single tool
- Per-page limits for MCP (MAX_PER_PAGE = 20)

**Gotchas to Avoid**:
- MCP tools MUST return JSON strings (use json.dumps())
- ALWAYS truncate large fields for MCP responses
- Limit pagination to prevent huge payloads

### 4. Embedding Service Multi-Provider

- **Relevance**: 8/10
- **Archon Location**: `~/source/vibes/infra/archon/python/src/server/services/embeddings/embedding_service.py`
- **Key Patterns**:
  - **Provider Abstraction**: Single interface for multiple embedding providers
  - **Dimension Detection**: Automatically detect embedding dimensions
  - **Error Handling**: Provider-specific error adapters
  - **Caching Strategy**: (Not implemented in current Archon, but design consideration)
  - **Rate Limiting**: (Not implemented, but needed for production)

**What to Consider**:
- Single provider initially (OpenAI) or multi-provider from start?
- How to handle dimension mismatches?
- Caching embeddings to avoid regeneration?
- Rate limiting for external APIs?

## Recommended Technology Stack

Based on Archon patterns, Docling RAG Agent reference, and best practices:

### Backend Core
- **Framework**: FastAPI 0.104+ (async, OpenAPI docs, dependency injection)
- **Python**: 3.11+ (improved async performance, better type hints)
- **Database**: PostgreSQL 15+ (better full-text search, performance improvements)
- **Vector DB**: **Qdrant** (primary recommendation - see evaluation criteria below)
- **Database Client**: asyncpg (async PostgreSQL driver, connection pooling)
- **Migrations**: Alembic (database schema versioning)

### Document Processing
- **Parser**: Docling (table preservation, document hierarchy, hybrid chunking)
- **Web Crawler**: crawl4ai v0.6.2+ (AI-optimized, JavaScript rendering)
- **Chunking**: Hybrid semantic chunking (from Docling RAG Agent)

### Embeddings
- **Initial Provider**: OpenAI text-embedding-3-small (cost-effective, 1536 dimensions)
- **Future Support**: Multi-provider (Gemini, Ollama, Sentence Transformers)
- **Dimensions**: Support for 384, 768, 1024, 1536, 3072

### Search
- **MVP Strategy**: Base vector search + PostgreSQL ts_vector hybrid search
- **Post-MVP**: CrossEncoder reranking, code example extraction
- **Full-Text**: PostgreSQL ts_vector with GIN indexes

### Testing
- **Unit Tests**: pytest with pytest-asyncio
- **Integration Tests**: TestClient from FastAPI
- **MCP Tests**: Direct tool invocation tests
- **Coverage**: pytest-cov

### Infrastructure
- **Containerization**: Docker with multi-stage builds
- **Orchestration**: Docker Compose (local dev and production)
- **Reverse Proxy**: Nginx (if needed for production)
- **Logging**: Python logging with structured logs

## Assumptions Made

### 1. Vector Database Selection: Qdrant
- **Reasoning**: Docker deployment simplicity, Python async client, good filtering support, lower memory footprint than alternatives, active community
- **Source**: Research questions in INITIAL.md, NLWeb example from Archon knowledge base mentions Qdrant alongside other options
- **Alternative**: pgvector if we want to keep everything in PostgreSQL (simpler deployment, but potentially less performant at scale)

### 2. MVP Search Strategy: Vector + Hybrid (No Reranking Initially)
- **Reasoning**: Hybrid search provides significant improvement over pure vector search (from Archon analysis), reranking adds complexity and latency, can be added later
- **Source**: Archon's rag_service.py shows optional reranking strategy, implemented as separate layer
- **Decision**: Start with base + hybrid, add reranking in post-MVP

### 3. Chunk Storage: Store in Both PostgreSQL and Vector DB
- **Reasoning**: PostgreSQL for ts_vector full-text search, vector DB for vector similarity, redundancy acceptable for reliability
- **Source**: Archon's hybrid search strategy uses both PostgreSQL ts_vector and Supabase vector storage
- **Trade-off**: Storage duplication vs search flexibility and performance

### 4. Document Processing: Synchronous Initially, Async Post-MVP
- **Reasoning**: Simpler to implement and debug, async processing adds queue management complexity
- **Source**: Task Manager pattern shows how to handle long operations, but doesn't use job queues
- **Decision**: Process inline with progress tracking, add Celery/RQ in post-MVP if needed

### 5. MCP Tools: Consolidated Pattern (find/manage)
- **Reasoning**: Follows established task-manager pattern, reduces tool proliferation, easier for AI assistants to use
- **Source**: Direct reference from INITIAL.md and task-manager MCP implementation
- **Pattern**: `search_knowledge_base()`, `manage_document()`, `manage_source()`, `crawl_website()`

### 6. Embedding Provider: OpenAI Only for MVP
- **Reasoning**: Industry standard, reliable API, good documentation, multi-provider adds complexity
- **Source**: Archon has multi-provider but it's complex, INITIAL.md asks if we should support multiple initially
- **Decision**: Single provider for MVP, design for easy addition of others later

### 7. PostgreSQL Schema: Separate tables for documents, chunks, sources
- **Reasoning**: Clear separation of concerns, allows independent querying, follows normalized design
- **Source**: Archon's schema analysis (documents table in Supabase)
- **Design**: Foreign keys link records, soft delete for documents/chunks

### 8. Web Crawling: Included in MVP
- **Reasoning**: crawl4ai is decided technology, essential for knowledge base population
- **Source**: INITIAL.md lists crawl4ai as decided and includes crawl_jobs table design
- **Decision**: Include in initial implementation with progress tracking

### 9. Rate Limiting: Configuration-Based (Not Implemented in Code Initially)
- **Reasoning**: Can be handled at infrastructure level (nginx) or added to service layer later
- **Source**: Best practice for external APIs, but not critical for MVP
- **Decision**: Document in configuration, implement if issues arise

### 10. Cost Optimization: Embedding Caching
- **Reasoning**: Avoid regenerating embeddings for same content, significant cost savings
- **Source**: Listed in INITIAL.md research questions
- **Decision**: Cache embeddings by content hash, implement in MVP

## Success Criteria

The research phase is successful when ARCHITECTURE.md includes:

### Must Have (Critical)
- [ ] Vector database choice with comparison table (performance, setup, filtering, cost)
- [ ] Rationale for vector DB selection with benchmarks or analysis
- [ ] Complete PostgreSQL schema with CREATE TABLE statements
- [ ] Index specifications for common queries
- [ ] Embedding provider strategy (OpenAI initially, multi-provider design)
- [ ] Search pipeline design with flow diagram (base → hybrid → optional reranking)
- [ ] Document ingestion pipeline with error handling strategy
- [ ] MCP tools specification (tool names, parameters, return types, examples)
- [ ] Service layer architecture (classes, responsibilities, dependencies)
- [ ] Technology stack summary with versions
- [ ] Docker compose structure (services, ports, volumes, health checks)
- [ ] Environment variable template (.env.example content)

### Should Have (Important)
- [ ] Performance considerations (query latency targets, throughput expectations)
- [ ] Cost estimates (embedding API costs per 1M tokens, infrastructure monthly cost)
- [ ] Migration strategy (Alembic setup, versioning approach)
- [ ] Testing strategy (unit, integration, MCP tool testing, coverage targets)
- [ ] Comparison with Archon approach (what we're keeping, changing, reasons)
- [ ] Error handling patterns (exceptions, recovery, logging)
- [ ] Monitoring and observability approach (logs, metrics, tracing)

### Nice to Have (Desirable)
- [ ] API endpoint documentation (OpenAPI spec outline)
- [ ] Frontend component structure (pages, components, hooks)
- [ ] Deployment notes (production considerations, scaling strategy)
- [ ] Security considerations (API keys, rate limiting, input validation)
- [ ] Data retention and cleanup policies
- [ ] Backup and disaster recovery strategy

## Next Steps for Downstream Agents

This feature analysis serves as the foundation for the research and architecture design phase:

### Research Phase (INITIAL_rag_service_research.md Execution)

**Phase 1: Vector Database Research** (2-3 hours)
- Read documentation for Qdrant, Weaviate, Milvus
- Set up minimal Docker containers for top 2 candidates
- Test basic operations (insert, query, filter) with sample data
- Benchmark query performance (10K, 100K, 1M vectors)
- Document findings in comparison table with scores

**Phase 2: Schema Design** (1-2 hours)
- Review Archon's current schema in detail
- Design PostgreSQL tables for standalone service
- Plan indexes for common query patterns
- Document relationships with vector DB (linking strategy)
- Write CREATE TABLE statements with constraints

**Phase 3: Search Strategy Design** (1-2 hours)
- Review Archon's search strategies in depth
- Design MVP search pipeline (base + hybrid)
- Plan for post-MVP enhancements (reranking, code extraction)
- Document query flow with diagrams
- Define response format and metadata

**Phase 4: Integration Planning** (1 hour)
- Design MCP tools following task-manager pattern
- Plan service layer structure (classes, methods)
- Define API contracts (REST endpoints, request/response)
- Document configuration strategy (env vars, settings)

**Phase 5: Documentation** (1 hour)
- Compile all research into ARCHITECTURE.md
- Add architecture diagrams (system, data flow, search pipeline)
- List dependencies with exact versions
- Create .env.example template with all variables
- Document deployment steps

**Total Estimated Time**: 6-9 hours

### Output Deliverable

**File**: `prps/rag_service_research/ARCHITECTURE.md`

**Structure**:
```markdown
# RAG Service Architecture

## Executive Summary
[Key decisions, rationale, quick reference]

## Technology Stack
[Complete list with versions and justifications]

## Vector Database Evaluation
[Comparison table, benchmarks, final choice with rationale]

## PostgreSQL Schema
[Complete CREATE TABLE statements with indexes and constraints]

## Search Pipeline
[Strategy design, flow diagram, implementation notes]

## Document Ingestion
[Pipeline steps, error handling, progress tracking]

## Service Layer
[Class structure, responsibilities, interaction diagram]

## MCP Tools
[Tool specifications with examples]

## API Endpoints
[REST API documentation]

## Docker Compose
[Service structure, configuration]

## Configuration
[Environment variables, .env.example]

## Performance Considerations
[Benchmarks, optimization strategies, scaling]

## Cost Estimates
[API costs, infrastructure, monthly projection]

## Migration from Archon
[What we keep, what we change, why]

## Testing Strategy
[Unit, integration, MCP testing approach]

## Deployment Notes
[Production considerations, monitoring, maintenance]

## Next Steps
[Ready for INITIAL_rag_service_implementation.md]
```

### Follow-Up Implementation PRP

After ARCHITECTURE.md is complete:
1. **INITIAL_rag_service_implementation.md** - Implement the designed architecture
2. Use ARCHITECTURE.md as the source of truth for all implementation decisions
3. Include references to specific sections when implementing features
4. Document any deviations from the architecture with rationale

## Additional Context

### Archon Integration Points (For Future)

While this is a standalone service, potential future integrations:
- Link documents to task-manager tasks (task_id foreign key)
- Cross-reference with basic-memory notes
- Shared credential service (optional)
- Unified logging and monitoring

### Design Principles to Follow

From task-manager and Archon experience:
1. **Service Layer Pattern**: API route → Service → Database
2. **Error Handling**: tuple[bool, dict] for all service methods
3. **Async First**: All database operations async with connection pooling
4. **Validation**: Validate inputs before processing
5. **Optimization**: Response field selection for performance
6. **Testing**: Comprehensive unit and integration tests
7. **Documentation**: Inline comments explaining patterns and gotchas
8. **MCP Optimization**: Truncate large fields, limit pagination

### Known Constraints and Gotchas

From Archon and task-manager analysis:

**Database Patterns**:
- Use `async with db_pool.acquire() as conn` (Gotcha #12)
- Use `$1, $2` placeholders with asyncpg, not `%s` (Gotcha #7)
- Row locking with `ORDER BY id` to prevent deadlocks (Gotcha #2)
- Always use transactions for multi-step operations

**MCP Patterns**:
- Tools MUST return JSON strings (use `json.dumps()`) (Gotcha #3)
- ALWAYS truncate descriptions to 1000 chars (Gotcha #3)
- Limit per_page to 20 for MCP tools (Gotcha #3)
- Structured errors with suggestions

**Service Patterns**:
- Connection pooling with health checks
- Graceful degradation (e.g., reranking fails → continue)
- Configuration-driven feature enablement
- Response optimization for large payloads

### Research Questions to Answer

These questions from INITIAL.md must be addressed in ARCHITECTURE.md:

**High Priority** (MVP Decisions):
1. Which vector database? Qdrant vs alternatives (comparison + rationale)
2. PostgreSQL schema design? (complete with CREATE statements)
3. Which embedding provider(s) initially? (OpenAI or multi-provider)
4. Which search strategies in MVP? (vector only vs hybrid vs reranking)
5. MCP tools consolidation pattern? (find/manage confirmed)

**Medium Priority** (Design Decisions):
6. Async processing for ingestion? (sync MVP, async post-MVP)
7. Reranking in MVP or later? (post-MVP recommended)
8. Chunk text storage location? (both PostgreSQL and vector DB)
9. Rate limiting strategy? (configuration-based, implement if needed)
10. Web crawling in MVP? (yes, with progress tracking)

**Low Priority** (Post-MVP):
11. Multi-tenancy support? (design consideration, not MVP)
12. Advanced filtering features? (basic filters MVP, advanced later)
13. Analytics and usage tracking? (post-MVP)

## Summary

This feature analysis establishes the foundation for RAG service research and architecture design. The research phase will:

1. **Evaluate vector databases** with hands-on testing and benchmarking
2. **Design PostgreSQL schema** based on Archon patterns and new requirements
3. **Plan search strategies** using proven Archon patterns
4. **Define service architecture** following task-manager best practices
5. **Document everything** in comprehensive ARCHITECTURE.md

**Key Takeaways**:
- Standalone service following task-manager patterns
- Leverage Archon's proven RAG pipeline design
- Start simple (vector + hybrid search), add complexity later
- Production-ready from start with comprehensive error handling
- MCP-first tool design for AI assistant integration
- Research-driven decisions with documented rationale

**Success Metric**: ARCHITECTURE.md becomes the single source of truth for implementation PRP, requiring minimal clarifications or revisions during actual development.
