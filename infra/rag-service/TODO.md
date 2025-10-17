# RAG Service - Current Status & Action Items

## ✅ Task List (Priority Order)

1. ✅ **Remove Source Type dropdown** (HIGH - 15 min) - `frontend/src/components/SourceManagement.tsx` - COMPLETED
2. ✅ **Per-Domain Collections Architecture** (HIGH - 8 hours) - COMPLETED 2025-10-17
   - Replaces shared global collections with per-source domain-isolated collections
   - See prps/per_domain_collections.md and execution reports
3. ✅ **Fix integration test data format** (15 min) - Changed .md test files to .html format - COMPLETED 2025-10-17
4. ✅ **Add Qdrant collection cleanup fixture** (15 min) - Prevent test pollution - COMPLETED 2025-10-17
5. **Fix crawl page count display** (10 min) - Frontend/backend mismatch
6. **Add chunk count to documents** (30 min) - `document_service.py`, `DocumentResponse`
7. **Implement document viewer** (2-3 hours) - Backend endpoint + frontend modal
8. **Fix database pool fixture** (30 min) - Returns async generator instead of pool
9. **Fix service mocking paths** (15 min) - IngestionService import location
10. **Debug hybrid search test collection** (1 hour) - Import errors
11. **Re-run full integration suite** (30 min) - Target 80%+ pass rate
12. **Add volume mounts for temp file storage** (15 min) - Document uploads
13. **Configure log rotation** (30 min) - Backend logs
14. **Add monitoring/metrics endpoints** (1-2 hours) - Production readiness
15. **Document deployment guide** (1 hour) - Production documentation

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

### 1. Architecture Evolution: Multi-Collection → Per-Domain Collections (IMPLEMENTED)

#### Phase 1: Multi-Collection Architecture (IMPLEMENTED 2025-10-16)
**Decision**: Three specialized global collections (AI_DOCUMENTS, AI_CODE, AI_MEDIA)
**PRP Reference**: prps/multi_collection_architecture.md

**Approach**: Content-type based collections
- Users select which collections to enable per source (default: ["documents"])
- Each collection uses optimized embedding models for content type
- Content classification automatically routes chunks to appropriate collections
- Search aggregates results across enabled collections

**Rationale**:
- **Better Embeddings**: Code content gets code-optimized embeddings (text-embedding-3-large, 3072 dimensions), documents get fast general embeddings (text-embedding-3-small, 1536 dimensions)
- **User Control**: Explicit opt-in prevents unexpected behavior and controls embedding costs
- **Scalability**: Per-collection HNSW indices perform better than single massive index
- **Flexibility**: Cross-collection search enabled by default, per-source filtering available

**Implementation Details**:
- Database: `enabled_collections TEXT[]` field on sources table (Migration 003)
- Collections: AI_DOCUMENTS (1536d), AI_CODE (3072d), AI_MEDIA (512d, future)
- Classification: 40% code indicator threshold (lenient to avoid false positives)
- Models: text-embedding-3-small (documents), text-embedding-3-large (code)
- Status Change: Removed "pending" status, sources now default to "active" on creation

#### Phase 2: Per-Domain Collection Architecture (IMPLEMENTED 2025-10-17)
**Decision**: Per-source domain-isolated collections with unique naming
**PRP Reference**: prps/per_domain_collections.md

**Approach**: Each source creates its own set of collections
- Source "AI Knowledge" + [Documents, Code] → `AI_Knowledge_documents`, `AI_Knowledge_code`
- Source "Network Knowledge" + [Documents] → `Network_Knowledge_documents`
- Complete domain isolation in vector space
- Search within specific domains only (cross-domain search supported)

**Rationale**:
- **Domain Isolation**: No vector from one domain appears in another domain's search results
- **Clean Deletion**: Deleting a source removes all its collections (no orphaned vectors)
- **Unique Collections**: Each source has dedicated collections (no shared vector space)
- **Better Search**: Search filtered by source_id returns only that domain's results
- **Scalability**: Supports 100+ domains (300+ collections total)

**Implementation Details**:
- Database: `collection_names JSONB` field on sources table (Migration 004)
- Collection Naming Pattern: `{sanitized_source_title}_{collection_type}`
- Sanitization: Replace special chars with underscores, limit to 64 chars
- Collection Management: Auto-create on source creation, auto-delete on source deletion
- Migration Script: `scripts/migrate_to_per_domain_collections.py` (creates Qdrant collections)
- Payload Index: source_id indexed on all collections for efficient filtering

**Migration Status**:
- ✅ Migration 004 applied (collection_names column added)
- ✅ Migration script created and tested (scripts/migrate_to_per_domain_collections.py)
- ✅ All sources have collection_names populated
- ✅ Per-domain collection creation implemented in SourceService
- ✅ CollectionManager service created (create/delete collection lifecycle)
- ✅ IngestionService updated to route chunks to domain-specific collections
- ✅ VectorService refactored to accept collection_name parameter (collection-agnostic)
- ✅ SearchService implemented for domain-based search with multi-collection aggregation
- ✅ API routes updated (sources return collection_names, search accepts source_ids)
- ✅ Frontend updated to display collection_names and domain selector
- ✅ 30 tests created (22 unit + 8 integration, 85%+ coverage)
- ✅ Documentation updated (TODO.md, README.md, migration guide)
- ✅ All integration tests passing (8/8 pass, 100% - 2025-10-17)

**Next Steps for Production**:
1. ✅ Fix integration test data format (.md → .html) - COMPLETED 2025-10-17
2. ✅ Fix VectorService.upsert_vectors() call signature in IngestionService - COMPLETED 2025-10-17
3. ✅ Add Qdrant collection cleanup fixture to prevent test pollution - COMPLETED 2025-10-17
4. Run migration script on production database - 10 min
5. Verify all domain collections created in Qdrant
6. Monitor search latency per domain (target: <200ms)
7. Verify 0% cross-domain contamination in search results

### 2. Fix Test Infrastructure (Priority: HIGH)
**Per-Domain Collections Tests**: ✅ COMPLETED (8/8 passing, 100% - 2025-10-17)
- ✅ Fixed test data format (.md → .html) - COMPLETED 2025-10-17
- ✅ Fixed VectorService.upsert_vectors() call signature - COMPLETED 2025-10-17
- ✅ Added Qdrant collection cleanup fixture - COMPLETED 2025-10-17

**Remaining Test Infrastructure** (Priority: MEDIUM)
**Blocks 28 integration tests** - See INTEGRATION_TEST_REPORT.md for details
- [ ] Fix database pool fixture (30 min) - Returns async generator instead of pool
- [ ] Fix service mocking paths (15 min) - IngestionService import location
- [ ] Debug hybrid search test collection (1 hour) - Import errors
- [ ] Re-run full integration suite
- [ ] Target: 80%+ test pass rate

**Current Status**: 35/67 integration tests passing (52%) + 8/8 per-domain tests passing (100%)
- Core functionality: ✅ Excellent (search, document CRUD, per-domain collections working)
- Per-domain tests: ✅ All passing (100%)
- Remaining tests: ⚠️ Fixture issues + import path issues

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

**Active Qdrant Collections** (Per-Domain Architecture):
- Collections are created dynamically per source (e.g., `DevOps_Knowledge_documents`, `DevOps_Knowledge_code`)
- No global shared collections - each source has its own isolated collections
- Old global collections (AI_DOCUMENTS, AI_CODE, AI_MEDIA, documents) removed - DEPRECATED

**Current Data**:
- Sources: 1 (DevOps Knowledge)
- Collections: Per-domain (DevOps_Knowledge_documents, DevOps_Knowledge_code)
- Default: New sources use enabled_collections=["documents"] unless specified

---

## 📝 Technical Reference

### Architecture Decisions

#### Per-Domain Collection Architecture (CURRENT)
**Migration Date**: 2025-10-17 (Replaced Multi-Collection Architecture)

- **Per-Source Collections**: Each source creates its own set of collections
  - Collection Naming: `{sanitized_source_title}_{collection_type}`
  - Example: "AI Knowledge" + ["documents", "code"] → `AI_Knowledge_documents`, `AI_Knowledge_code`
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
  - "AI Knowledge" + "documents" → `AI_Knowledge_documents`
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
- New: Per-source collections (AI_Knowledge_documents, Network_Security_code, etc.)
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
sources (id, source_type, url, status, enabled_collections[], collection_names, metadata)
  ├── status: 'active' | 'processing' | 'failed' | 'archived' (no more "pending"/"completed")
  ├── enabled_collections: TEXT[] - collection types to use for this source (default: ["documents"])
  │   ├── Valid values: 'documents', 'code', 'media'
  │   ├── Constraint: array_length > 0 (at least one collection required)
  │   └── GIN index for efficient array queries
  ├── collection_names: JSONB - mapping of collection_type → Qdrant collection name
  │   ├── Example: {"documents": "AI_Knowledge_documents", "code": "AI_Knowledge_code"}
  │   ├── Pattern: {sanitized_source_title}_{collection_type}
  │   ├── GIN index for efficient JSON queries
  │   └── Auto-populated on source creation from source title + enabled_collections
  └── documents (id, source_id, title, document_type, url)
       └── chunks (id, document_id, chunk_index, text)
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

### Per-Domain Collections Integration Tests & Cleanup Fixed (2025-10-17 01:45)
- **Issue**: 5/8 integration tests failing + tests deleting production collections
- **Root Causes**:
  1. Test files using `.md` format (unsupported by Docling parser)
  2. Wrong `VectorService.upsert_vectors()` call signature in `IngestionService`
  3. Test using "DevOps Knowledge" name conflicting with production source
  4. Session-scoped cleanup fixture guessing which collections were "test" collections
  5. Old global collections (AI_DOCUMENTS, AI_CODE, AI_MEDIA, documents) auto-created on startup
- **Fixes**:
  1. **Test Data Format** (`test_per_domain_collections.py`):
     - Changed all test files from `.md` to `.html` format
     - HTML is supported by Docling parser (`.htm`, `.pdf`, `.docx`, `.html`)
  2. **VectorService Call Signature** (`ingestion_service.py:587`):
     - Fixed: `await self.vector_service.upsert_vectors(collection_name, points)`
     - Old (broken): `await self.vector_service.upsert_vectors(points, collection_name=collection_name)`
     - Issue: `collection_name` is first positional argument, not keyword argument
  3. **Test Collection Names** (`test_per_domain_collections.py:473`):
     - Renamed test source from "DevOps Knowledge" to "Test_DevOps_Knowledge"
     - Prevents conflict with production "DevOps Knowledge" source
  4. **Safe Cleanup Strategy** (`test_per_domain_collections.py:120-139`):
     - Removed dangerous session-scoped cleanup that guessed test collections by prefix
     - Now tracks only source IDs created during current test run
     - Deletes ONLY those specific sources (by ID, not name pattern)
     - No prefix matching, no guessing - completely safe for production data
  5. **Removed Global Collection Auto-Creation** (`main.py:105-108`):
     - Removed `initialize_collections()` call that created AI_DOCUMENTS, AI_CODE, AI_MEDIA
     - Removed legacy collection creation for "documents" collection
     - Collections now created ONLY when sources are created (per-domain architecture)
     - Deleted old global collections from Qdrant
- **Result**:
  - All 8 integration tests passing (100% pass rate)
  - Production collections safe from test cleanup
  - No more auto-creation of deprecated global collections
- **Pattern**:
  - Never guess which data is "test data" - track explicitly by ID
  - Tests clean up by tracking source IDs, not name patterns
  - Per-domain architecture = collections created on-demand, not at startup

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

**Last Updated**: 2025-10-17 01:45 PST (Per-Domain Collections: Tests Fixed, Production-Safe Cleanup, Global Collections Removed)
