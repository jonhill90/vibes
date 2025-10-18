# RAG Service - Current Status & Action Items

## 📋 Active Tasks (Priority Order)

1. **Implement document viewer** (2-3 hours) - Backend endpoint + frontend modal
2. **Fix database pool fixture** (30 min) - Returns async generator instead of pool
3. **Fix service mocking paths** (15 min) - IngestionService import location
4. **Debug hybrid search test collection** (1 hour) - Import errors
5. **Re-run full integration suite** (30 min) - Target 80%+ pass rate
6. **Add volume mounts for temp file storage** (15 min) - Document uploads
7. **Configure log rotation** (30 min) - Backend logs
8. **Add monitoring/metrics endpoints** (1-2 hours) - Production readiness
9. **Document deployment guide** (1 hour) - Production documentation

## ✅ Completed (2025-10-17)

- ✅ Per-Domain Collections Architecture - Domain-isolated collections with unique naming
- ✅ Recursive web crawling - BFS traversal with URL deduplication and same-domain filtering
- ✅ Token-aware batching - Fixed 47,445 token OpenAI limit errors
- ✅ Embedding cache validation - Auto-cleanup of corrupted embeddings
- ✅ Integration tests (8/8 passing) - Test data format, cleanup fixtures, VectorService signatures
- ✅ UI fixes - Source type dropdown removal, crawl page count, chunk count display

---

## 📋 Active Issues

### UI/UX
1. **Document viewer missing** - No way to view original imported document or rendered markdown/HTML version of crawled websites
   - **Backend**: New endpoint `/api/documents/{id}/content`
   - **Frontend**: Modal component with markdown renderer, PDF viewer, syntax highlighting

---

## 🎯 Next Steps

### 1. Test Infrastructure (Priority: HIGH)
**Remaining Test Infrastructure** - Blocks 28 integration tests
- [ ] Fix database pool fixture (30 min) - Returns async generator instead of pool
- [ ] Fix service mocking paths (15 min) - IngestionService import location
- [ ] Debug hybrid search test collection (1 hour) - Import errors
- [ ] Re-run full integration suite - Target: 80%+ test pass rate

**Current Status**: 35/67 integration tests passing (52%) + 8/8 per-domain tests passing (100%)

### 2. Production Readiness (Priority: MEDIUM)
- [ ] Run migration script on production database (10 min)
- [ ] Verify all domain collections created in Qdrant
- [ ] Monitor search latency per domain (target: <200ms)
- [ ] Verify 0% cross-domain contamination in search results
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
- ✅ Web crawling with Crawl4AI + Playwright (recursive BFS crawling)
- ✅ Document upload (HTML, PDF, DOCX) with full ingestion pipeline
- ✅ OpenAI embeddings with multiple models (text-embedding-3-small, text-embedding-3-large)
- ✅ Token-aware batching (respects 8,192 token OpenAI limit)
- ✅ Embedding cache with automatic validation and corruption cleanup
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

**Last Updated**: 2025-10-17 20:52 PST (Fixed token batching bug - RESOLVED 47,445 token errors)
