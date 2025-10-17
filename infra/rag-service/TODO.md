# RAG Service - Current Status & Action Items

## ✅ Task List (Priority Order)

1. ✅ **Remove Source Type dropdown** (HIGH - 15 min) - `frontend/src/components/SourceManagement.tsx` - COMPLETED
2. **Fix crawl page count display** (10 min) - Frontend/backend mismatch
3. **Add chunk count to documents** (30 min) - `document_service.py`, `DocumentResponse`
4. **Implement document viewer** (2-3 hours) - Backend endpoint + frontend modal
5. **Fix database pool fixture** (30 min) - Returns async generator instead of pool
6. **Fix service mocking paths** (15 min) - IngestionService import location
7. **Debug hybrid search test collection** (1 hour) - Import errors
8. **Re-run full integration suite** (30 min) - Target 80%+ pass rate
9. **Add volume mounts for temp file storage** (15 min) - Document uploads
10. **Configure log rotation** (30 min) - Backend logs
11. **Add monitoring/metrics endpoints** (1-2 hours) - Production readiness
12. **Document deployment guide** (1 hour) - Production documentation

---

## 📋 Active Issues

### CRITICAL: Multi-Collection Implementation Status (2025-10-16)
1. **✅ RESOLVED: 500 Error on Source List**
   - **Root Cause**: Migration 003 not applied to database
   - **Fix**: Applied migration 003 → Added `enabled_collections` column
   - **Status**: API working, sources loading successfully
   - **Verification**: Browser testing confirmed UI working with collection checkboxes
   - **Screenshot**: source-management-ui.png shows 📄 Documents, 💻 Code, 🖼️ Media (disabled)

### UI/UX Issues
1. **Remove Source Type dropdown** - UX confusion (Priority: HIGH)
   - **Issue**: "Create New Source" form shows dropdown with "Upload", "Web Crawl", "API" options
   - **Impact**: Confusing UX - users don't understand the difference, creates unnecessary complexity
   - **Desired**: Remove source type selection entirely, auto-detect or simplify
   - **Files**: `frontend/src/components/SourceManagement.tsx`
   - **Related**: Backend source_type field may need to be optional or auto-set

2. **Crawl page count incorrect** - Frontend showing wrong number of pages crawled

3. **Chunk count missing** - Documents don't display chunk count (shows "TODO" in API)

4. **Document viewer missing** - No way to view original imported document or rendered markdown/HTML version of crawled websites

---

## 🎯 Next Steps

### 1. Architecture Decision: Multi-Collection Approach (IMPLEMENTED)
**Decision**: Multi-collection architecture with per-source collection selection
**Implementation Date**: 2025-10-16
**PRP Reference**: prps/multi_collection_architecture.md

**Approach Chosen**: Three specialized collections (AI_DOCUMENTS, AI_CODE, AI_MEDIA)
- Users select which collections to enable per source (default: ["documents"])
- Each collection uses optimized embedding models for content type
- Content classification automatically routes chunks to appropriate collections
- Search aggregates results across enabled collections

**Rationale**:
- **Better Embeddings**: Code content gets code-optimized embeddings (text-embedding-3-large, 3072 dimensions), documents get fast general embeddings (text-embedding-3-small, 1536 dimensions)
- **User Control**: Explicit opt-in prevents unexpected behavior and controls embedding costs
- **Scalability**: Per-collection HNSW indices perform better than single massive index
- **Domain Isolation**: Different content types are physically separated in vector space
- **Flexibility**: Cross-collection search enabled by default, per-source filtering available

**Implementation Details**:
- Database: `enabled_collections TEXT[]` field on sources table (Migration 003)
- Collections: AI_DOCUMENTS (1536d), AI_CODE (3072d), AI_MEDIA (512d, future)
- Classification: 40% code indicator threshold (lenient to avoid false positives)
- Models: text-embedding-3-small (documents), text-embedding-3-large (code)
- Status Change: Removed "pending" status, sources now default to "active" on creation

### 2. Fix Test Infrastructure (Priority: MEDIUM)
**Blocks 28 integration tests** - See INTEGRATION_TEST_REPORT.md for details

- [ ] Fix database pool fixture (30 min) - Returns async generator instead of pool
- [ ] Fix service mocking paths (15 min) - IngestionService import location
- [ ] Debug hybrid search test collection (1 hour) - Import errors
- [ ] Re-run full integration suite
- [ ] Target: 80%+ test pass rate

**Current Status**: 35/67 integration tests passing (52%)
- Core functionality: ✅ Excellent (search, document CRUD working)
- Test infrastructure: ⚠️ Fixture issues blocking 28 tests

### 3. Fix UI/UX Issues (Priority: MEDIUM)
- [ ] Fix crawl page count display (10 min)
  - Investigate frontend/backend mismatch
  - Verify correct count is stored in database

- [ ] Add chunk count to documents (30 min)
  - Backend: Query chunk count in `document_service.py`
  - Update DocumentResponse to include chunk_count
  - Frontend: Display chunk count in document list/details

- [ ] Implement document viewer (2-3 hours)
  - Backend: Add endpoint to retrieve document content/markdown
  - Frontend: Create modal viewer component
  - Support: Original files (PDF, DOCX) + rendered markdown for crawled pages
  - Consider: Syntax highlighting for code blocks

### 4. Production Readiness (Priority: LOW)
- [ ] Add volume mounts for temp file storage (document uploads)
- [ ] Configure log rotation for backend logs
- [ ] Add monitoring/metrics endpoints
- [ ] Document deployment guide for production

---

## 📊 System Health

**Working Features**:
- ✅ Source management (create, list, update, delete)
- ✅ Multi-collection architecture with per-source collection selection
- ✅ Content type classification (code vs documents vs media)
- ✅ Web crawling with Crawl4AI + Playwright
- ✅ Document upload (HTML, PDF, DOCX) with full ingestion pipeline
- ✅ OpenAI embeddings with multiple models (text-embedding-3-small, text-embedding-3-large)
- ✅ Multi-collection vector search with result aggregation
- ✅ Document deletion with Qdrant cleanup
- ✅ Frontend UI for all core operations (including collection selection)
- ✅ Cache persistence across container restarts

**Known Limitations**:
- ⚠️ Document parser only supports: `.docx`, `.html`, `.htm`, `.pdf` (not `.txt` or `.md`)
- ⚠️ Container disk at 98% usage (persisted cache prevents exhaustion)
- ⚠️ Media collection (AI_MEDIA) currently disabled - future feature pending CLIP embeddings

**Active Qdrant Collections**:
- **AI_DOCUMENTS**: 1536 dimensions (text-embedding-3-small) - General text, articles, documentation
- **AI_CODE**: 3072 dimensions (text-embedding-3-large) - Source code, technical examples
- **AI_MEDIA**: 512 dimensions (clip-vit) - DISABLED (future: images, diagrams, visual content)

**Current Data**:
- Sources: 2+ (with enabled_collections field - Migration 003 applied)
- Documents: ~1,227+ chunks from crawl + test uploads
- Vectors: Distributed across AI_DOCUMENTS and AI_CODE collections based on content type
- Default: New sources use enabled_collections=["documents"] unless specified

---

## 📝 Technical Reference

### Architecture Decisions

#### Multi-Collection Architecture (CURRENT)
- **Three Qdrant Collections**: AI_DOCUMENTS, AI_CODE, AI_MEDIA
  - Per-source collection selection via `enabled_collections` array
  - Content classification routes chunks to appropriate collections
  - Different embedding models per collection (optimized for content type)
  - Search aggregates results across enabled collections
  - Migration 003 adds `enabled_collections` field with default ["documents"]

**Collection Details**:
- **AI_DOCUMENTS**: General text, articles, documentation (text-embedding-3-small, 1536d)
- **AI_CODE**: Source code, technical examples (text-embedding-3-large, 3072d)
- **AI_MEDIA**: Images, diagrams, visual content (clip-vit, 512d, FUTURE - currently disabled)

**Trade-offs**:
- ✅ Better embeddings per content type
- ✅ User control over embedding costs
- ✅ Scalability: separate HNSW indices per collection
- ⚠️ Increased complexity vs single collection
- ⚠️ Search must aggregate across multiple collections (handled transparently)

### Critical Gotchas to Remember

#### Database & Connection Gotchas
- **Gotcha #2**: Store db_pool, not connections (all services)
- **Gotcha #3**: Use $1, $2 placeholders, not %s (asyncpg)
- **Gotcha #12**: async with pool.acquire() for connections
- **Gotcha #13**: SecretStr must be unwrapped with `.get_secret_value()`
- **Gotcha #14**: PostgreSQL timestamps via asyncpg are ISO strings, check type before `.isoformat()`

#### Vector & Embedding Gotchas
- **Gotcha #9**: HNSW disabled (m=0) for bulk upload (60-90x faster)
- **Gotcha #15**: Qdrant collection names are case-sensitive: "AI_DOCUMENTS" != "ai_documents"
- **Gotcha #16**: Each collection needs correct dimension in VectorParams (1536 for documents, 3072 for code)
- **Gotcha #17**: Qdrant collections must be created before first upsert (use qdrant_init.py on startup)

#### Content Classification Gotchas
- **Gotcha #18**: CODE_DETECTION_THRESHOLD (40%) may need tuning per domain
  - Too low: General text with code examples classified as "code"
  - Too high: Technical documentation with sparse code missed
  - Current: 40% (lenient, optimized for mixed-content docs)
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

### Database Schema
```
sources (id, source_type, url, status, enabled_collections[], metadata)
  ├── status: 'active' | 'processing' | 'failed' | 'archived' (no more "pending"/"completed")
  ├── enabled_collections: TEXT[] - collections to use for this source (default: ["documents"])
  │   └── Valid values: 'documents', 'code', 'media'
  │   └── Constraint: array_length > 0 (at least one collection required)
  │   └── GIN index for efficient array queries
  └── documents (id, source_id, title, document_type, url)
       └── chunks (id, document_id, chunk_index, text)
            └── vectors in Qdrant collections (distributed by content type)
                ├── AI_DOCUMENTS collection (1536d) - general text chunks
                ├── AI_CODE collection (3072d) - code chunks
                └── AI_MEDIA collection (512d) - media chunks (future)
                    └── payload includes: source_id, document_id, collection_type
```

### Cascade Deletion Pattern
- Deleting source → CASCADE deletes documents, chunks, crawl_jobs (PostgreSQL)
- Deleting document → Atomic: Qdrant cleanup → PostgreSQL CASCADE to chunks
- Ensures no orphaned data in either database

---

## 🔧 Development Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Restart backend after code changes
docker-compose restart backend

# Run integration tests
docker exec rag-backend python -m pytest tests/integration/ -v

# Run unit tests
docker exec rag-backend python -m pytest tests/unit/ -v

# Check disk space
docker exec rag-backend df -h /

# Clean up (WARNING: deletes all data)
docker-compose down -v
docker system prune -a --volumes
```

---

## 📂 Recent Fixes (Reference Only)

### Multi-Collection Migration Applied (2025-10-17 00:15)
- **Issue**: 500 error on GET /api/sources - "column 'enabled_collections' does not exist"
- **Root Cause**: Migration 003 not applied to database (code deployed without schema update)
- **Fix**: Applied migration 003 to ragservice database
  ```bash
  docker exec -i rag-postgres psql -U raguser -d ragservice < \
    infra/rag-service/database/migrations/003_add_enabled_collections.sql
  ```
- **Result**:
  - enabled_collections column added with default ["documents"]
  - 2 existing sources migrated successfully
  - Status enum updated (pending/completed → active/archived)
  - API now returns enabled_collections field
  - Frontend collection checkboxes working
- **Pattern**: Always apply migrations before deploying code changes that depend on schema

### DateTime Serialization Bug (2025-10-16 22:07)
- **Issue**: Document list/get endpoints returned 500 errors
- **Fix**: `backend/src/api/routes/documents.py:393-394, 490-491`
- **Pattern**: Check `isinstance(str)` before calling `.isoformat()` on timestamps

### OpenAI API Key Bug (2025-10-16 20:15)
- **Issue**: 401 errors despite valid API key
- **Fix**: `backend/src/main.py:96` - Unwrap SecretStr with `.get_secret_value()`

### Cache Volume Mount (2025-10-16 20:10)
- **Issue**: Container disk space exhaustion (100% full)
- **Fix**: `docker-compose.yml` - Mount `/root/.cache` for HuggingFace/Playwright

### Cascade Delete Implementation (2025-10-16)
- **Fix**: `document_service.py:369` - Atomic Qdrant + PostgreSQL deletion
- **Pattern**: Query chunk IDs → Delete Qdrant → Delete PostgreSQL (with rollback)

---

---

## 📌 Quick Fix Notes

### Crawl Page Count Issue
- **Location**: Frontend crawl job display
- **Symptom**: Wrong number of pages shown
- **Check**: Compare frontend state with database `crawl_jobs.pages_crawled`

### Chunk Count Implementation
- **Backend**: `document_service.py` - Add `COUNT(*)` query from chunks table
- **API**: Update `DocumentResponse` model (currently has `chunk_count=None` placeholder)
- **Files to modify**:
  - `backend/src/services/document_service.py`
  - `backend/src/models/responses.py` (if needed)
  - `backend/src/api/routes/documents.py` (remove TODO comments)

### Document Viewer Feature
- **Backend**: New endpoint `/api/documents/{id}/content`
  - Return original file for uploads (from temp storage or re-parse)
  - Return markdown for crawled pages (stored in chunks or regenerate)
- **Frontend**: Modal component with:
  - Markdown renderer (react-markdown)
  - PDF viewer (react-pdf)
  - Syntax highlighting (prism.js or highlight.js)
- **Storage consideration**: May need to persist original content/markdown

---

**Last Updated**: 2025-10-16 23:45 PST (Multi-Collection Architecture Documented)
