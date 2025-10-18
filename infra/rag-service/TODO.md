# RAG Service - Current Status & Action Items

## 📋 Active Tasks (Priority Order)

### Phase 1: Critical Bugs (BLOCKING)
1. **Fix search collection name resolution** (2-3 hours) - BLOCKING all search functionality
   - Problem: Search uses global collections (`AI_DOCUMENTS`) but we have per-domain collections (`MCP_documents`)
   - Impact: All search queries return 0 results (404 errors)
   - Fix: Query database for `source.collection_names` mapping instead of using static method
   - Files: `base_search_strategy.py:373`, `search_service.py`, `vector_service.py`
   - See: Linear JON-12 comment for full details

2. **Fix embedding dimension mismatch in search** (1 hour) - BLOCKING code search
   - Problem: Search generates 1536d embeddings but code collection expects 3072d
   - Impact: Code search fails silently with validation errors
   - Fix: Generate per-collection embeddings or unify embedding models
   - Files: `base_search_strategy.py:196-198`

3. **Implement orphaned vector cleanup** (2-3 hours) - DATA INTEGRITY
   - Problem: Deleting documents leaves orphaned code vectors in MCP_code collection
   - Impact: Stale search results, wasted storage, incorrect counts
   - Fix: Update delete operations to clean up related code vectors
   - Files: `documents.py`, `document_service.py`, `extract_code_blocks.py`

### Phase 2: Quality Improvements (HIGH PRIORITY)
4. **Enable hybrid search** (30 min) - Keyword matching for code queries
   - Set `USE_HYBRID_SEARCH=true` in .env
   - Test with code-focused queries (`"async def @tool decorator"`)
   - Expected: Better keyword coverage (53% → 70%+)

5. **Add code-specific quality tests** (1 hour) - Regression testing
   - Syntax parsing validation
   - Runnable example checks
   - Update `/tmp/rag_quality_test.py` with code search tests

6. **Lower chunk size for code** (2 hours) - Better code isolation
   - Current: 500 tokens (mixes code with documentation)
   - Target: 200 tokens for code blocks
   - Update content classifier threshold: 40% → 20% code ratio

### Phase 3: Production Readiness (MEDIUM PRIORITY)
7. **Add monitoring/metrics** (4-6 hours) - CNCF stack
   - OpenTelemetry instrumentation
   - Prometheus + Grafana dashboards
   - Search quality metrics (score distribution, latency p95)
   - Create evaluation dataset (20+ queries)

8. **Implement document viewer** (2-3 hours) - Backend endpoint + frontend modal
9. **Fix database pool fixture** (30 min) - Returns async generator instead of pool
10. **Fix service mocking paths** (15 min) - IngestionService import location
11. **Debug hybrid search test collection** (1 hour) - Import errors
12. **Re-run full integration suite** (30 min) - Target 80%+ pass rate

### Phase 4: Infrastructure (LOW PRIORITY)
13. **Add volume mounts for temp file storage** (15 min) - Document uploads
14. **Configure log rotation** (30 min) - Backend logs
15. **Document deployment guide** (1 hour) - Production documentation

## ✅ Completed

### Code Extraction (2025-10-18)
- ✅ **Extracted code blocks into MCP_code collection** - 227 code blocks from 916 documentation chunks
- ✅ **Created extract_code_blocks.py script** - Automated extraction with embedding and storage
- ✅ **Used text-embedding-3-large for code** - 3072d embeddings for better code understanding
- ✅ **Fixed VectorService instantiation bug** - Corrected argument passing in base_search_strategy.py
- ✅ **Added .ssh to .gitignore** - Security improvement

### Quality Fixes (2025-10-17)
- ✅ **Raised similarity threshold** - 0.05 → 0.6 (industry standard for better quality)
- ✅ **Fixed VectorService initialization bug** - Removed invalid `collection_name` parameter
- ✅ **Cleaned up empty sources** - Deleted Pydantic_AI and DevOps_Knowledge (0 documents)
- ✅ **Updated quality test suite** - Focused on MCP data (only available source)
- ✅ **RAG service audit** - Production readiness: 4/5 stars (85/100)
- ✅ **Quality validation** - 80% test pass rate, 0.66 avg similarity score (up from 20%, 0.34)

### Architecture (2025-10-17)
- ✅ Per-Domain Collections Architecture - Domain-isolated collections with unique naming
- ✅ Recursive web crawling - BFS traversal with URL deduplication and same-domain filtering
- ✅ Token-aware batching - Fixed 47,445 token OpenAI limit errors
- ✅ Embedding cache validation - Auto-cleanup of corrupted embeddings
- ✅ Integration tests (8/8 passing) - Test data format, cleanup fixtures, VectorService signatures
- ✅ UI fixes - Source type dropdown removal, crawl page count, chunk count display

---

## 📊 Current System State

### Quality Metrics (as of 2025-10-17)
**Overall RAG Quality**: 7/10 (Good for concepts, weak for code)

| Metric | Value | Status |
|--------|-------|--------|
| **Test Pass Rate** | 80% (4/5) | ✅ Good |
| **Avg Similarity Score** | 0.66 | ✅ Above threshold |
| **Avg Latency** | 399ms | ⚠️ Target: <200ms |
| **Keyword Coverage** | 53% | ⚠️ Target: 70%+ |

**By Query Type**:
- Conceptual queries: 0.66 avg score ✅ (100% pass rate)
- Navigation queries: 0.65 avg score ✅ (80% pass rate)
- Code-focused queries: 0.41 avg score ❌ (0% pass - below 0.6 threshold)

### Data Status
**Sources**: 1 active
- MCP Documentation (604659af-f494-4f3a-afce-bd87820bf983)
  - Type: crawl
  - URL: https://modelcontextprotocol.io/llms-full.txt
  - Pages: 117 crawled
  - Status: active

**Collections**:
- `MCP_documents`: 916 points ✅ (active)
- `MCP_code`: 0 points ❌ (empty - blocks code search)
- `Pydantic_AI_*`: DELETED (no documents)
- `DevOps_Knowledge_*`: DELETED (no documents)

**Database**:
- Documents: 1 (MCP crawl)
- Chunks: 916 (semantic chunks, 500 tokens each)
- Embedding cache: Active with MD5 validation

### Configuration
- **Similarity Threshold**: 0.6 (60% - industry standard)
- **Chunk Size**: 500 tokens (documents), 500 tokens (code - needs lowering to 200)
- **Chunk Overlap**: 50 tokens
- **Hybrid Search**: DISABLED (needs enabling for code queries)
- **Code Detection Threshold**: 40% (needs lowering to 20% for better classification)

---

## 📋 Active Issues

### Critical Issues
1. **MCP_code collection empty (0 points)** - Blocks code search functionality
   - Problem: Code examples classified as "documents" (embedded in 500-token chunks)
   - Impact: Code queries score 0.41 (below 0.6 threshold)
   - Fix: Extract code blocks into separate collection
   - Priority: HIGH (Phase 1, Task 1)

2. **No monitoring/observability** - Production gap
   - Missing: OpenTelemetry, Prometheus, Grafana
   - Impact: Cannot track search quality, latency trends, or errors
   - Fix: Add CNCF stack (OpenTelemetry + Prometheus + Grafana + Loki)
   - Priority: MEDIUM (Phase 2, Task 5)

### UI/UX Issues
3. **Document viewer missing** - No way to view original imported documents
   - **Backend**: New endpoint `/api/documents/{id}/content`
   - **Frontend**: Modal with markdown renderer, PDF viewer, syntax highlighting
   - Priority: MEDIUM (Phase 2, Task 6)

### Test Infrastructure Issues
4. **35/67 integration tests failing** - Blocks regression detection
   - Database pool fixture returns async generator
   - Service mocking paths incorrect
   - Hybrid search test collection import errors
   - Priority: MEDIUM (Phase 2, Tasks 7-10)

---

## 🎯 Success Criteria

### Phase 1: Quality (1-2 weeks)
- [ ] MCP_code collection populated (target: ~150 points)
- [ ] Code search avg score: 0.65+ (currently 0.41)
- [ ] Agent rating: 9/10 (currently 7/10)
- [ ] Hybrid search enabled and tested
- [ ] Code-specific quality tests passing

### Phase 2: Production (2-3 weeks)
- [ ] OpenTelemetry + Prometheus + Grafana deployed
- [ ] Evaluation dataset created (20+ queries)
- [ ] Search latency: <200ms p95 (currently 640ms)
- [ ] Integration test pass rate: 80%+ (currently 52%)
- [ ] Document viewer implemented

### Phase 3: Infrastructure (1 week)
- [ ] Volume mounts configured
- [ ] Log rotation enabled
- [ ] Deployment guide documented

---

## 📝 Technical Reference

### Code Extraction Strategy (Phase 1, Task 1)

**Current Problem**:
```markdown
# MCP Server Guide [300 tokens of explanation]

Example:
```python
@mcp.tool()
async def weather(city: str):
    return fetch(city)
```

[200 more tokens of documentation]

→ Chunk classified as "documents" (80% docs, 20% code)
→ Code search fails (0.41 score, below 0.6 threshold)
```

**Proposed Solution**:
1. **Re-process existing 916 chunks** from PostgreSQL
2. **Extract code blocks** using regex: ` ` `(python|typescript|javascript|bash)\n(.+?)\n` ` `
3. **Create new chunks** with only code content
4. **Store in MCP_code collection** (separate from documentation)
5. **Update content classifier** threshold: 40% → 20% code ratio

**Implementation Steps**:
```python
# Pseudo-code for extraction script
for chunk in get_all_chunks():
    code_blocks = extract_code_blocks(chunk.text)
    for code in code_blocks:
        if len(code) >= 50:  # Minimum viable code snippet
            new_chunk = create_code_chunk(
                text=code,
                collection_type="code",
                source_id=chunk.source_id,
                document_id=chunk.document_id
            )
            embed_and_store(new_chunk, collection="MCP_code")
```

**Expected Impact**:
- **Code search score**: 0.41 → 0.65+ (above threshold)
- **Agent rating**: 7/10 → 9/10
- **MCP_code points**: 0 → ~150 (estimated from 916 doc chunks)
- **Use cases enabled**: Code generation, debugging, implementation examples

### Architecture Decisions

#### Per-Domain Collection Architecture (CURRENT)
**Migration Date**: 2025-10-17 (Replaced Multi-Collection Architecture)

- **Per-Source Collections**: Each source creates its own set of collections
  - Collection Naming: `{sanitized_source_title}_{collection_type}`
  - Example: "MCP Documentation" + ["documents", "code"] → `MCP_documents`, `MCP_code`
  - Complete domain isolation in vector space
  - Per-source collection selection via `enabled_collections` array
  - Content classification routes chunks to appropriate domain collections
  - Different embedding models per collection type (optimized for content type)
  - Search queries specific domain collections (filtered by source_ids)
  - Migration 004 adds `collection_names` JSONB field (mapping collection_type → collection_name)

**Collection Naming Pattern**:
- **Pattern**: `{sanitized_title}_{collection_type}`
- **Sanitization**: Replace special chars with underscores, collapse duplicates, limit to 64 chars
- **Examples**:
  - "MCP Documentation" + "documents" → `MCP_documents`
  - "Network & Security" + "code" → `Network_Security_code`
  - "DevOps-2024" + "documents" → `DevOps_2024_documents`

**Collection Types & Dimensions**:
- **documents**: General text, articles, documentation (text-embedding-3-small, 1536d)
- **code**: Source code, technical examples (text-embedding-3-large, 3072d)
- **media**: Images, diagrams, visual content (clip-vit, 512d, FUTURE - currently disabled)

**Trade-offs**:
- ✅ Complete domain isolation (no cross-contamination in search results)
- ✅ Clean deletion (delete source → delete all its collections)
- ✅ Better embeddings per content type
- ✅ User control over embedding costs
- ✅ Scalability: separate HNSW indices per domain
- ✅ Unique collection names prevent conflicts
- ⚠️ More collections (3x more than multi-collection approach)
- ⚠️ Requires collection_names field in database (Migration 004)

**Migration from Multi-Collection**:
- Old: Shared global collections (AI_DOCUMENTS, AI_CODE, AI_MEDIA)
- New: Per-source collections (MCP_documents, MCP_code, etc.)
- Migration Script: `scripts/migrate_to_per_domain_collections.py`
- Migration 004: Adds collection_names JSONB field with GIN index

### Critical Gotchas to Remember

#### Database & Connection Gotchas
- **Gotcha #2**: Store db_pool, not connections (all services)
- **Gotcha #3**: Use $1, $2 placeholders, not %s (asyncpg)
- **Gotcha #12**: async with pool.acquire() for connections
- **Gotcha #13**: SecretStr must be unwrapped with `.get_secret_value()`
- **Gotcha #14**: PostgreSQL timestamps via asyncpg are ISO strings, check type before `.isoformat()`

#### Vector & Embedding Gotchas
- **Gotcha #9**: HNSW disabled (m=0) for bulk upload (60-90x faster)
- **Gotcha #15**: Qdrant collection names are case-sensitive: "MCP_documents" != "mcp_documents"
- **Gotcha #16**: Each collection needs correct dimension in VectorParams (1536 for documents, 3072 for code)
- **Gotcha #17**: Qdrant collections must be created before first upsert (use qdrant_init.py on startup)
- **Gotcha #22**: Token-aware batching prevents OpenAI token limit errors (embedding_service.py:285)
  - OpenAI limit: 8,192 tokens per request
  - Conservative batch limit: 7,000 tokens (margin for encoding overhead)
  - Logic bug: Check token limit BEFORE adding to batch, not after
  - Pattern: `if tokens > limit:` then either break (batch full) or fail (single text too large)
  - Prevents corrupted embeddings from failed batches
- **Gotcha #23**: Cache validation prevents dimension corruption (embedding_service.py:424)
  - Validate embedding dimensions match expected for model (1536 for text-embedding-3-small)
  - Auto-delete corrupted cache entries (wrong dimensions like 19,209)
  - Force re-generation with correct dimensions
  - Warnings like "Invalid cached embedding dimension" are GOOD (self-healing)
- **Gotcha #24**: Similarity threshold affects quality vs recall trade-off
  - Too low (0.05): Returns irrelevant results, poor quality
  - Too high (0.8): Misses relevant results, poor recall
  - Sweet spot: 0.6 (60% similarity - industry standard)
  - Current setting: 0.6 (raised from 0.05 on 2025-10-17)

#### Content Classification Gotchas
- **Gotcha #18**: CODE_DETECTION_THRESHOLD (40%) may need tuning per domain
  - Too low (20%): General text with code examples classified as "code"
  - Too high (60%): Technical documentation with sparse code missed
  - Current: 40% (lenient, optimized for mixed-content docs)
  - **Needs adjustment**: Lower to 20% to extract embedded code blocks
- **Gotcha #19**: Media collection currently disabled (future feature)
  - Media indicators detected but not stored until CLIP embeddings implemented
  - Media chunks currently routed to "documents" collection
- **Gotcha #20**: Content classifier uses multiple indicators (not just syntax highlighting)
  - Code fences, function definitions, imports, class declarations
  - Requires 3+ code indicators OR 40%+ density for "code" classification
  - Defaults to "documents" when ambiguous (safer for search quality)
- **Gotcha #21**: enabled_collections filters chunks during ingestion
  - If source has enabled_collections=["documents"], code chunks are SKIPPED (not stored)
  - This is intentional: gives users control over what gets embedded (cost management)
  - Warn users if content type mismatch expected (e.g., code-heavy source with only "documents" enabled)
- **Gotcha #25**: Code examples in documentation often misclassified
  - Problem: 500-token chunks with 20% code, 80% docs → classified as "documents"
  - Impact: Code search returns 0.41 avg score (below 0.6 threshold)
  - Fix: Extract code blocks separately, store in dedicated code collection
  - Workaround: Lower chunk size to 200 tokens for code-heavy sources

### Database Schema
```
sources (id, source_type, url, status, enabled_collections[], collection_names, metadata)
  ├── status: 'active' | 'processing' | 'failed' | 'archived' (no more "pending"/"completed")
  ├── enabled_collections: TEXT[] - collection types to use for this source (default: ["documents"])
  │   ├── Valid values: 'documents', 'code', 'media'
  │   ├── Constraint: array_length > 0 (at least one collection required)
  │   └── GIN index for efficient array queries
  ├── collection_names: JSONB - mapping of collection_type → Qdrant collection name
  │   ├── Example: {"documents": "MCP_documents", "code": "MCP_code"}
  │   ├── Pattern: {sanitized_source_title}_{collection_type}
  │   ├── GIN index for efficient JSON queries
  │   └── Auto-populated on source creation from source title + enabled_collections
  └── documents (id, source_id, title, document_type, url)
       └── chunks (id, document_id, chunk_index, text, metadata)
            └── vectors in Qdrant per-domain collections (distributed by content type)
                ├── {source_title}_documents collection (1536d) - general text chunks for this source
                ├── {source_title}_code collection (3072d) - code chunks for this source
                └── {source_title}_media collection (512d) - media chunks for this source (future)
                    └── payload includes: source_id, document_id, collection_type
```

### Cascade Deletion Pattern
- Deleting source → CASCADE deletes documents, chunks, crawl_jobs (PostgreSQL)
- Deleting document → Atomic: Qdrant cleanup → PostgreSQL CASCADE to chunks
- Ensures no orphaned data in either database

---

## 📚 Documentation References

### Quality Analysis
- **RAG Service Audit** - `RAG_SERVICE_AUDIT.md` (Production readiness: 85/100)
- **Quality Report** - `RAG_QUALITY_REPORT.md` (80% pass rate, 0.66 avg score)
- **Agent Experience** - `/tmp/rag_agent_experience.md` (7/10 rating, detailed analysis)
- **Quality Test Suite** - `/tmp/rag_quality_test.py` (Automated testing)

### Architecture & Planning
- **Linear Issue JON-12** - Migration from Archon to Linear, code extraction task
- **Basic-Memory Note 202510172209** - Operational review, CNCF monitoring decision
- **CLAUDE.md** - Project conventions and workflows

### API Documentation
- **Health Check**: `GET /health` - Service health status
- **Search**: `POST /api/search` - Semantic search with source filtering
- **Sources**: `GET/POST/DELETE /api/sources` - Source management
- **Crawl**: `POST /api/crawl/start` - Web crawling

---

## 🔧 Development Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Restart backend after code changes
docker-compose restart backend

# Run quality tests
python3 /tmp/rag_quality_test.py

# Run integration tests
docker exec rag-backend python -m pytest tests/integration/ -v

# Run unit tests
docker exec rag-backend python -m pytest tests/unit/ -v

# Check Qdrant collections
curl http://localhost:6333/collections | jq '.result.collections[] | {name, points_count}'

# Query database
docker exec -i rag-postgres psql -U raguser -d ragservice -c "SELECT COUNT(*) FROM chunks;"

# Check disk space
docker exec rag-backend df -h /

# Clean up (WARNING: deletes all data)
docker-compose down -v
docker system prune -a --volumes
```

---

**Last Updated**: 2025-10-17 23:30 PST (Quality fixes applied, code extraction task planned)
