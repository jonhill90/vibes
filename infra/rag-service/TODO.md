# RAG Service - Current Status & Action Items

## 📋 Active Tasks (Priority Order)

### Phase 1: Critical Bugs (BLOCKING)
1. ✅ ~~**Fix search collection name resolution**~~ - **COMPLETED 2025-10-18**
   - ✅ Fixed: Query database for `source.collection_names` mapping
   - ✅ Modified: `base_search_strategy.py`, `search_service.py`
   - ✅ Verified: Search correctly routes to per-domain collections

2. ✅ ~~**Fix embedding dimension mismatch in search**~~ - **COMPLETED 2025-10-18**
   - ✅ Fixed: Generate per-collection embeddings (1536d for docs, 3072d for code)
   - ✅ Modified: `base_search_strategy.py`, `search_service.py`
   - ✅ Verified: Code search works without dimension validation errors

3. ✅ ~~**Implement orphaned vector cleanup**~~ - **COMPLETED 2025-10-18**
   - ✅ Fixed: Delete operations now clean up code vectors when documents are deleted
   - ✅ Modified: `document_service.py:380-453`, `vector_service.py:391-448`
   - ✅ Added: `delete_vectors_by_filter()` method with count return
   - ✅ Cleaned up: Removed 227 pre-existing orphaned code vectors
   - ✅ Verified: All collections now clean, no orphaned vectors
   - ✅ Impact: No more orphaned code blocks, maintains data integrity

### Phase 2: Quality Improvements (HIGH PRIORITY)
**✅ RESOLVED**: Search API threshold issue fixed - **COMPLETED 2025-10-18**
   - **Root Cause**: SIMILARITY_THRESHOLD set too high (0.6) for small dataset
   - **Symptoms**: 0 results for all queries, 1.2s latency, "Cache storage error" warnings
   - **Investigation**: Added instrumentation to SearchService, traced full execution path
   - **Finding**: Search working correctly, but scores (0.22-0.54) below 0.6 threshold
   - **Fix**: Lowered SIMILARITY_THRESHOLD from 0.6 → 0.2 (.env:109)
   - **Result**: Search now returns 3-5 results per query with 0.5+ scores
   - **Latency**: 767ms (still needs optimization, but functional)
   - **Collections**: Both MCP_code (3072d) and MCP_documents (1536d) returning results
   - **Impact**: ✅ Search API fully functional, code and document retrieval working
   - **Files Modified**: `.env:109` (SIMILARITY_THRESHOLD), `search_service.py` (debug logging reverted)
4. ✅ ~~**Enable hybrid search**~~ - **COMPLETED 2025-10-18**
   - ✅ Set `USE_HYBRID_SEARCH=true` in .env
   - ✅ Fixed: `HybridSearchStrategy` initialization to pass `base_strategy` instead of individual services
   - ✅ Modified: `search.py:96-101` (routes)
   - ✅ Verified: API responses now show `"search_type": "hybrid"`
   - ✅ Impact: Hybrid search (vector 70% + text 30%) now available for better keyword matching
   - 📝 Note: Testing requires chunks in PostgreSQL (current: 0 chunks after cleanup)

5. ✅ ~~**Fix crawl ingestion to extract code**~~ - **COMPLETED 2025-10-18**
   - ✅ Fixed ContentClassifier: Any ``` code fence → "code" (removed density requirement)
   - ✅ Modified: `content_classifier.py:98-103` (commit 3a76133)
   - ✅ Fixed: Removed old batch embedding path from `ingest_from_crawl()`
   - ✅ Modified: `ingestion_service.py:785-822` deleted, steps renumbered (commit 1878b80)
   - ✅ Fixed: Settings import moved to module level (commit ea4f0c0)
   - ✅ Added: Verbose classification logging for debugging (commit b9d14bd)
   - ✅ Verified: Full Docker restart resolved caching issue
   - ✅ Tested: Crawled https://modelcontextprotocol.io/docs/develop/build-server
   - ✅ Result: 5 code chunks successfully extracted to MCP_code collection (3072d embeddings)
   - ✅ Result: 7 document chunks extracted to MCP_documents collection (1536d embeddings)
   - ✅ Verified: Search returns code results (scores 0.5+, threshold lowered to 0.2)
   - ✅ Impact: **End-to-end code pipeline working** - ingestion, storage, and retrieval all functional
   - 📝 Note: Verbose logs at line 828 (`Chunk X: classified as`) don't appear due to log level filtering
   - 📝 Note: Warning logs at line 834 (`Skipping chunk`) DO appear and confirm classification working
   - 📝 Note: Similarity threshold lowered to 0.2 for small datasets (will tune with more data)

6. ✅ ~~**Add language type detection for code**~~ - **COMPLETED 2025-10-18**
   - ✅ **Approach**: Inline classification during ingestion with STRICT language requirements
   - ✅ **Implementation**: Modified ContentClassifier + IngestionService for code fence detection
   - ✅ **Strict Classification Rules**:
     - ONLY chunks with ` ```language` code fences are classified as "code"
     - NO "unknown" language fallback (removed completely)
     - Chunks without language tags → reclassified to "documents" collection
     - Final safeguard skips code vectors missing language field
   - ✅ **Code Pattern**: `r'```([a-zA-Z0-9_+-]+)(?:\s+[^\n]*)?'` extracts language from fence
   - ✅ **Reclassification Logic**: If code detected but no language → goes to documents (ingestion_service.py:855-867)
   - ✅ **Safeguard**: Skip code vectors without language field (ingestion_service.py:590-602)
   - ✅ **Files Modified**:
     - `content_classifier.py` - Strict fence-based classification
     - `ingestion_service.py` - Reclassification + safeguard logic
   - ✅ **Test Results** (modelcontextprotocol.io crawl):
     - 122/122 code chunks have language field (100% coverage)
     - 0 chunks with missing or "unknown" language
     - 14 unique languages: bash, csharp, env, groovy, http, java, javascript, json, kotlin, mermaid, powershell, python, typescript, xml
   - ✅ **Impact**: All code chunks guaranteed to have valid language field for filtering and syntax highlighting
   - 📝 **Note**: Alternative approach (`extract_code_blocks.py` script) available for post-crawl extraction from full documents
   - ⏸️ **TODO (Future)**: UI language badges and search filtering by language (frontend work)

7. ✅ **Fix embedding cache dimension constraint** - **COMPLETED 2025-10-18**
   - ✅ Changed `embedding_cache.embedding` from `VECTOR(1536)` to `VECTOR` (variable dimension)
   - ✅ Fixes "expected 1536 dimensions, not 3072" errors when caching large model embeddings
   - ✅ Migration: `006_support_variable_embedding_dimensions.sql`
   - 📝 **Context**: Multi-collection uses text-embedding-3-small (1536d) + text-embedding-3-large (3072d)
   - 📝 **Impact**: Cache now works for both document and code embeddings

8. **Add code-specific quality tests** (1 hour) - Regression testing
   - Syntax parsing validation
   - Runnable example checks
   - Update `/tmp/rag_quality_test.py` with code search tests

9. **Lower chunk size for code** (2 hours) - Better code isolation
   - Current: 500 tokens (mixes code with documentation)
   - Target: 200 tokens for code blocks
   - Update content classifier threshold: 40% → 20% code ratio

### Phase 3: Production Readiness (MEDIUM PRIORITY)
10. **Add monitoring/metrics** (4-6 hours) - CNCF stack
   - OpenTelemetry instrumentation
   - Prometheus + Grafana dashboards
   - Search quality metrics (score distribution, latency p95)
   - Create evaluation dataset (20+ queries)

11. **Implement document viewer** (2-3 hours) - Backend endpoint + frontend modal
12. **Fix database pool fixture** (30 min) - Returns async generator instead of pool
13. **Fix service mocking paths** (15 min) - IngestionService import location
14. **Debug hybrid search test collection** (1 hour) - Import errors
15. **Re-run full integration suite** (30 min) - Target 80%+ pass rate

### Phase 4: Infrastructure (LOW PRIORITY)
16. **Add volume mounts for temp file storage** (15 min) - Document uploads
17. **Configure log rotation** (30 min) - Backend logs
18. **Document deployment guide** (1 hour) - Production documentation

## ✅ Completed

### Search Fixes & Data Integrity (2025-10-18 Evening)
- ✅ **Fixed collection name resolution** - Search queries database for per-domain `collection_names` mapping
- ✅ **Fixed embedding dimension mismatch** - Generate embeddings per collection type (1536d vs 3072d)
- ✅ **Implemented orphaned vector cleanup** - Document deletion now cleans up code vectors automatically
- ✅ **Added delete_vectors_by_filter()** - New VectorService method returns count of deleted vectors
- ✅ **Cleaned up existing orphans** - Removed 227 pre-existing orphaned code vectors from MCP_code
- ✅ **Verified multi-collection search** - Both code and document searches return results
- ✅ **Verified clean state** - All Qdrant collections now have 0 orphaned vectors
- ✅ **Enabled hybrid search** - Fixed `HybridSearchStrategy` initialization, enabled in .env
- ✅ **Files modified**:
  - `base_search_strategy.py:192-479`
  - `search_service.py:217-326`
  - `document_service.py:380-472`
  - `vector_service.py:391-483`
  - `.env:93` (USE_HYBRID_SEARCH=true)
  - `api/routes/search.py:96-101` (hybrid strategy init)

### Search Threshold Fix (2025-10-18 Late Morning)
- ✅ **Fixed search returning 0 results** - SIMILARITY_THRESHOLD too high for small dataset
- ✅ **Root cause analysis** - Added instrumentation to SearchService to trace execution
- ✅ **Investigation findings** - Search working correctly, scores 0.22-0.54 below 0.6 threshold
- ✅ **Threshold adjustment** - Lowered from 0.6 → 0.2 (.env:109)
- ✅ **Verified fix** - Search returns 3-5 results per query with 0.5+ scores
- ✅ **Collections working** - Both MCP_code and MCP_documents returning results
- ✅ **Impact**: End-to-end pipeline functional (ingestion → storage → retrieval)

### Code Ingestion During Crawl (2025-10-18 Late Morning)
- ✅ **Fixed crawl ingestion to extract code** - ContentClassifier now detects any ``` code fence
- ✅ **Modified ContentClassifier logic** - Removed density requirement (content_classifier.py:98-103)
- ✅ **Cleaned up ingestion pipeline** - Removed old batch embedding path (ingestion_service.py:785-822)
- ✅ **Added verbose classification logging** - Debug logs for chunk classification decisions
- ✅ **Verified Docker restart fix** - Resolved hot-reload caching issue affecting log visibility
- ✅ **Tested with real content** - Crawled MCP build-server docs, extracted 5 code chunks successfully
- ✅ **Impact**: Code search now functional during crawl (no post-processing needed)
- ✅ **Collections**: MCP_code collection now active with code embeddings (3072d)

### Code Extraction (2025-10-18 Afternoon)
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
- `MCP_documents`: 37 points ✅ (active)
- `MCP_code`: 5 points ✅ (active - code extraction working!)
- `Pydantic_AI_*`: Empty (no documents)
- `DevOps_Knowledge_*`: Empty (no documents)

**Database**:
- Documents: 1 (MCP crawl)
- Chunks: 12 total (after Docker restart - old data cleared)
- Embedding cache: Active with MD5 validation and auto-cleanup

### Configuration
- **Similarity Threshold**: 0.2 (20% - tuned for small datasets, will increase with more data)
- **Chunk Size**: 500 tokens (documents and code)
- **Chunk Overlap**: 50 tokens
- **Hybrid Search**: ENABLED ✅ (vector 70% + text 30%)
- **Code Detection**: ``` code fence presence (any code fence → classified as "code")

---

## 📋 Active Issues

### Critical Issues
1. **No monitoring/observability** - Production gap
   - Missing: OpenTelemetry, Prometheus, Grafana
   - Impact: Cannot track search quality, latency trends, or errors
   - Fix: Add CNCF stack (OpenTelemetry + Prometheus + Grafana + Loki)
   - Priority: MEDIUM (Phase 2, Task 8)

### UI/UX Issues
2. **Document viewer missing** - No way to view original imported documents
   - **Backend**: New endpoint `/api/documents/{id}/content`
   - **Frontend**: Modal with markdown renderer, PDF viewer, syntax highlighting
   - Priority: MEDIUM (Phase 2, Task 9)

### Test Infrastructure Issues
3. **35/67 integration tests failing** - Blocks regression detection
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

**Last Updated**: 2025-10-18 16:30 EDT (Task 6 completed - language field implementation working with 100% coverage)
