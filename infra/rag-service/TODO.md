# RAG Service - Current Status & Action Items

## 📋 Active Issues

### UI/UX Issues
1. **Crawl page count incorrect** - Frontend showing wrong number of pages crawled
2. **Chunk count missing** - Documents don't display chunk count (shows "TODO" in API)
3. **Document viewer missing** - No way to view original imported document or rendered markdown/HTML version of crawled websites

---

## 🎯 Next Steps

### 1. Architecture Decision: Single vs Multi-Collection (Priority: HIGH)
**Current**: Single Qdrant collection for all sources (metadata filtering)
**Context**: Greenfield project, planning to ingest large amounts of data

**Evaluate**:
- Keep single collection (simpler, cross-domain search)
- Switch to collection-per-source (isolation, per-domain optimization)
- Hybrid approach (general + sensitive collections)

**Decision criteria**:
- Expected total vector count across all sources
- Need for multi-tenancy or domain isolation
- Different embedding models per domain?
- Compliance/security requirements?

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
- ✅ Web crawling with Crawl4AI + Playwright
- ✅ Document upload (HTML, PDF, DOCX) with full ingestion pipeline
- ✅ OpenAI embeddings (text-embedding-3-small, 1536 dimensions)
- ✅ Vector search with source filtering
- ✅ Document deletion with Qdrant cleanup
- ✅ Frontend UI for all core operations
- ✅ Cache persistence across container restarts

**Known Limitations**:
- ⚠️ Document parser only supports: `.docx`, `.html`, `.htm`, `.pdf` (not `.txt` or `.md`)
- ⚠️ Container disk at 98% usage (persisted cache prevents exhaustion)

**Current Data**:
- Sources: 2 (Pydantic AI Documentation + Xerox test source)
- Documents: ~1,227 chunks from crawl + test uploads
- Vectors: 1,227+ in "documents" collection

---

## 📝 Technical Reference

### Architecture Decisions
- **Single Qdrant Collection**: All sources use one "documents" collection
  - Filtering via metadata (source_id field)
  - Enables cross-domain search by default
  - Simple management, efficient for current scale
  - Reconsider if: multi-tenancy, different embedding models, or >500K vectors

### Critical Gotchas to Remember
- **Gotcha #2**: Store db_pool, not connections (all services)
- **Gotcha #3**: Use $1, $2 placeholders, not %s (asyncpg)
- **Gotcha #9**: HNSW disabled (m=0) for bulk upload (60-90x faster)
- **Gotcha #12**: async with pool.acquire() for connections
- **Gotcha #13**: SecretStr must be unwrapped with `.get_secret_value()`
- **Gotcha #14**: PostgreSQL timestamps via asyncpg are ISO strings, check type before `.isoformat()`

### Database Schema
```
sources (id, source_type, url, status, metadata)
  └── documents (id, source_id, title, document_type, url)
       └── chunks (id, document_id, chunk_index, text)
            └── vectors in Qdrant (point_id = chunk.id, payload includes source_id)
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

**Last Updated**: 2025-10-16 22:12 PST
