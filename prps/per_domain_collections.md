# Per-Domain Collection Architecture

## Problem Statement

Current RAG service uses **global shared collections** (AI_DOCUMENTS, AI_CODE, AI_MEDIA) where all sources share the same 3 collections. This doesn't align with the intended use case where each source represents a distinct **knowledge domain** (e.g., "AI Knowledge", "Network Knowledge", "DevOps Knowledge").

**Current Architecture Issues:**
- All sources dump content into same 3 shared collections
- Search returns results from ALL domains mixed together
- No way to isolate knowledge by domain
- Can't delete or manage a specific domain without affecting others
- "AI Knowledge" and "Network Knowledge" chunks are physically mixed in same collection

**Desired Architecture:**
- Each source creates its own set of collections based on checkboxes
- Source "AI Knowledge" + [Documents, Code] → `AI_Knowledge_documents`, `AI_Knowledge_code`
- Source "Network Knowledge" + [Documents] → `Network_Knowledge_documents`
- Complete domain isolation in vector space
- Search within specific domains only

## User Story

As a knowledge base curator:
- I want to create separate knowledge domains (AI, Networking, DevOps)
- Each domain should have isolated vector collections
- When I search "AI Knowledge", I only get AI-related results (no network/devops noise)
- I can select which content types (documents, code, media) per domain
- I can delete entire domains without affecting other domains

## Requirements

### Functional Requirements

**FR1: Per-Source Collection Creation**
- When user creates source "AI Knowledge" with [Documents, Code] checked
- System creates 2 Qdrant collections: `AI_Knowledge_documents`, `AI_Knowledge_code`
- Collections are unique to this source (isolated vector space)
- Collection names sanitized from source title (alphanumeric + underscores)

**FR2: Domain-Based Search**
- Search API accepts `source_id` or `domain_name` parameter
- Queries only collections for specified domain
- Returns results ranked by score within that domain
- Cross-domain search optional (query multiple source_ids)

**FR3: Content Type Classification Per Domain**
- Content classifier detects code vs documents vs media (existing)
- Only chunks matching enabled_collections are stored
- Each chunk stored in domain-specific collection with appropriate embedding model

**FR4: Collection Lifecycle Management**
- Creating source → auto-creates domain collections in Qdrant
- Deleting source → auto-deletes domain collections from Qdrant
- Updating enabled_collections → creates new collections, migrates data

**FR5: Collection Naming Convention**
```
Pattern: {sanitized_source_title}_{collection_type}
Examples:
- "AI Knowledge" → AI_Knowledge_documents, AI_Knowledge_code
- "Network & Security" → Network_Security_documents
- "DevOps-2024" → DevOps_2024_documents
```

### Non-Functional Requirements

**NFR1: Performance**
- Domain search must be < 200ms for 10k vectors per domain
- Collection creation must be < 1 second
- Support 100+ domains (300+ collections total)

**NFR2: Data Isolation**
- No vector from one domain should appear in another domain's search
- Deleting domain must remove ALL vectors (no orphans)
- Collection names must be globally unique

**NFR3: Backward Compatibility**
- Migrate existing sources to new architecture
- Existing global collections (AI_DOCUMENTS, AI_CODE, AI_MEDIA) can be deleted or archived
- Existing data can be migrated to per-domain collections

## Success Criteria

**Must Have:**
- [ ] Source creation creates unique Qdrant collections per domain
- [ ] Collection naming follows `{source_title}_{collection_type}` pattern
- [ ] Search filtered by source_id returns only that domain's results
- [ ] Deleting source deletes all domain collections from Qdrant
- [ ] Content classification routes chunks to correct domain collections
- [ ] Frontend shows which collections exist for each source
- [ ] All existing tests pass with new architecture

**Nice to Have:**
- [ ] Cross-domain search (query multiple source_ids simultaneously)
- [ ] Collection metadata shows source_id, created_at, document_count
- [ ] API endpoint to list all collections for a source
- [ ] Migration script to move data from shared collections to per-domain

## Technical Approach

### Collection Naming Strategy

```python
def sanitize_collection_name(source_title: str, collection_type: str) -> str:
    """
    Convert source title to valid Qdrant collection name.

    Rules:
    - Replace spaces with underscores
    - Remove special chars (keep alphanumeric + underscore)
    - Limit to 64 chars (Qdrant limit is 255, but keep shorter)
    - Append collection type suffix

    Examples:
    - "AI Knowledge" + "documents" → "AI_Knowledge_documents"
    - "Network & Security!" + "code" → "Network_Security_code"
    - "Very Long Source Name That Exceeds Limit" → "Very_Long_Source_Name_That_Exceeds_Limi_documents"
    """
    # Sanitize title
    sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', source_title)
    sanitized = re.sub(r'_+', '_', sanitized)  # Collapse multiple underscores
    sanitized = sanitized.strip('_')  # Remove leading/trailing underscores

    # Limit length (leave room for suffix)
    max_prefix_len = 64 - len(f"_{collection_type}")
    if len(sanitized) > max_prefix_len:
        sanitized = sanitized[:max_prefix_len]

    # Append collection type
    return f"{sanitized}_{collection_type}"
```

### Database Schema Changes

```sql
-- Add collection_names JSONB field to sources table
ALTER TABLE sources
ADD COLUMN collection_names JSONB DEFAULT '{}'::JSONB;

-- Stores mapping of collection_type → Qdrant collection name
-- Example: {"documents": "AI_Knowledge_documents", "code": "AI_Knowledge_code"}

-- Add index for efficient JSON queries
CREATE INDEX idx_sources_collection_names ON sources USING GIN(collection_names);

-- Migration: Populate collection_names for existing sources
UPDATE sources
SET collection_names = (
    SELECT jsonb_object_agg(
        collection_type,
        -- Generate collection name from source title
        regexp_replace(
            regexp_replace(
                COALESCE(metadata->>'title', 'Untitled_' || id::text),
                '[^a-zA-Z0-9_]', '_', 'g'
            ),
            '_+', '_', 'g'
        ) || '_' || collection_type
    )
    FROM unnest(enabled_collections) AS collection_type
);
```

### API Changes

```python
# POST /api/sources
{
  "title": "AI Knowledge",
  "source_type": "upload",
  "enabled_collections": ["documents", "code"]
}

# Response includes collection_names
{
  "id": "uuid",
  "title": "AI Knowledge",
  "enabled_collections": ["documents", "code"],
  "collection_names": {
    "documents": "AI_Knowledge_documents",
    "code": "AI_Knowledge_code"
  },
  "status": "active"
}

# GET /api/sources/{id}
# Returns same format with collection_names

# POST /api/search
{
  "query": "how to train neural networks",
  "source_ids": ["uuid1", "uuid2"],  # Search specific domains
  "limit": 10
}
```

### Qdrant Collection Management

```python
class CollectionManager:
    """Manage per-domain Qdrant collections."""

    async def create_collections_for_source(
        self,
        source_id: UUID,
        source_title: str,
        enabled_collections: list[str]
    ) -> dict[str, str]:
        """
        Create Qdrant collections for a new source.

        Returns:
            dict mapping collection_type → Qdrant collection name
        """
        collection_names = {}

        for collection_type in enabled_collections:
            # Generate unique collection name
            collection_name = sanitize_collection_name(source_title, collection_type)

            # Get dimension for this collection type
            dimension = settings.COLLECTION_DIMENSIONS[collection_type]

            # Create collection in Qdrant
            await self.qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=dimension,
                    distance=Distance.COSINE
                )
            )

            # Store payload schema (for filtering)
            await self.qdrant_client.create_payload_index(
                collection_name=collection_name,
                field_name="source_id",
                field_schema=PayloadSchemaType.KEYWORD
            )

            collection_names[collection_type] = collection_name
            logger.info(f"Created collection: {collection_name} ({dimension}d)")

        return collection_names

    async def delete_collections_for_source(
        self,
        collection_names: dict[str, str]
    ) -> None:
        """Delete all Qdrant collections for a source."""
        for collection_type, collection_name in collection_names.items():
            try:
                await self.qdrant_client.delete_collection(collection_name)
                logger.info(f"Deleted collection: {collection_name}")
            except Exception as e:
                logger.error(f"Failed to delete collection {collection_name}: {e}")
```

### Ingestion Pipeline Changes

```python
async def ingest_document(
    self,
    source_id: UUID,
    file_path: str,
    document_metadata: dict[str, Any] | None = None,
) -> tuple[bool, dict[str, Any]]:
    """Ingest document into per-domain collections."""

    # Get source configuration
    async with self.db_pool.acquire() as conn:
        source = await conn.fetchrow(
            """
            SELECT
                enabled_collections,
                collection_names,
                metadata->>'title' as title
            FROM sources
            WHERE id = $1
            """,
            source_id
        )

    enabled_collections = source["enabled_collections"]
    collection_names = json.loads(source["collection_names"])  # type → collection_name mapping

    # Parse and chunk document (existing)
    markdown_text = await self.document_parser.parse_document(file_path)
    chunks = await self.text_chunker.chunk_text(markdown_text)

    # Classify chunks by content type
    classified_chunks = self._classify_chunks(chunks, enabled_collections)

    # Embed and store per collection type
    total_stored = 0
    for collection_type, chunk_list in classified_chunks.items():
        if not chunk_list:
            continue

        # Get domain-specific collection name
        collection_name = collection_names[collection_type]

        # Get embedding model for this collection type
        model_name = settings.COLLECTION_EMBEDDING_MODELS[collection_type]

        # Embed chunks
        embeddings = await self.embedding_service.batch_embed(
            [c.text for c in chunk_list],
            model_name=model_name
        )

        # Store in domain-specific collection
        await self._store_chunks(
            collection_name=collection_name,
            source_id=source_id,
            chunks=chunk_list,
            embeddings=embeddings
        )

        total_stored += len(chunk_list)
        logger.info(
            f"Stored {len(chunk_list)} chunks in {collection_name} "
            f"(model: {model_name})"
        )

    return True, {"chunks_stored": total_stored}
```

### Search Service Changes

```python
async def search(
    self,
    query: str,
    source_ids: list[UUID] | None = None,
    limit: int = 10,
) -> list[SearchResult]:
    """Search within specific domains (sources)."""

    if not source_ids:
        raise ValueError("Must specify at least one source_id for domain search")

    # Get collection names for specified sources
    async with self.db_pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT
                id as source_id,
                collection_names
            FROM sources
            WHERE id = ANY($1)
            """,
            source_ids
        )

    # Build list of collections to search
    collections_to_search = []
    for row in rows:
        collection_names = json.loads(row["collection_names"])
        for collection_type, collection_name in collection_names.items():
            collections_to_search.append({
                "source_id": row["source_id"],
                "collection_type": collection_type,
                "collection_name": collection_name,
            })

    if not collections_to_search:
        return []

    # Embed query (use documents model for general queries)
    query_embedding = await self.embedding_service.embed_text(
        query,
        model_name=settings.COLLECTION_EMBEDDING_MODELS["documents"]
    )

    # Search each collection
    all_results = []
    for col in collections_to_search:
        results = await self.vector_service.search_vectors(
            collection_name=col["collection_name"],
            query_vector=query_embedding,
            limit=limit * 2,  # Get extra for re-ranking
            filter_conditions={
                "must": [{"key": "source_id", "match": {"value": str(col["source_id"])}}]
            }
        )

        # Add metadata
        for result in results:
            result["source_id"] = col["source_id"]
            result["collection_type"] = col["collection_type"]

        all_results.extend(results)

    # Merge and re-rank by score
    sorted_results = sorted(all_results, key=lambda r: r["score"], reverse=True)
    return sorted_results[:limit]
```

## Implementation Tasks

### Phase 1: Core Infrastructure (2-3 hours)
1. **Add collection_names column to sources table** (30 min)
   - Create migration 004_add_collection_names.sql
   - Add JSONB column with GIN index
   - Populate for existing sources

2. **Create CollectionManager service** (1 hour)
   - Implement sanitize_collection_name()
   - Implement create_collections_for_source()
   - Implement delete_collections_for_source()
   - Add unit tests

3. **Update SourceService** (30 min)
   - On create_source: Call CollectionManager to create Qdrant collections
   - On delete_source: Call CollectionManager to delete Qdrant collections
   - Store collection_names in database

### Phase 2: Ingestion Pipeline (1-2 hours)
4. **Update IngestionService** (1 hour)
   - Read collection_names from source
   - Route chunks to domain-specific collections
   - Update _store_chunks to accept collection_name parameter

5. **Update VectorService** (30 min)
   - Remove hardcoded collection_name
   - Make all methods accept collection_name parameter
   - Update search_vectors for per-domain queries

### Phase 3: Search & API (1-2 hours)
6. **Update SearchService** (1 hour)
   - Implement domain-based search (source_ids → collection_names)
   - Multi-domain search aggregation
   - Score-based result ranking

7. **Update API Routes** (30 min)
   - sources.py: Return collection_names in responses
   - search.py: Accept source_ids parameter
   - Add validation for source_ids

### Phase 4: Frontend & Testing (2-3 hours)
8. **Update Frontend** (1 hour)
   - Display collection names in source table
   - Add domain selector to search interface
   - Show which collections exist per source

9. **Integration Tests** (1 hour)
   - Test per-domain collection creation
   - Test domain-isolated search
   - Test collection deletion on source delete

10. **Migration & Documentation** (30 min)
    - Migration script for existing data
    - Update TODO.md with new architecture
    - Update API documentation

## Migration Strategy

```sql
-- Migration 004: Add collection_names and populate
ALTER TABLE sources ADD COLUMN collection_names JSONB DEFAULT '{}'::JSONB;

-- Populate collection_names for existing sources
UPDATE sources
SET collection_names = (
    SELECT jsonb_object_agg(
        collection_type,
        regexp_replace(
            COALESCE(metadata->>'title', 'Source_' || id::text),
            '[^a-zA-Z0-9_]', '_', 'g'
        ) || '_' || collection_type
    )
    FROM unnest(enabled_collections) AS collection_type
);

-- Create GIN index
CREATE INDEX idx_sources_collection_names ON sources USING GIN(collection_names);
```

```python
# One-time migration script to create collections for existing sources
async def migrate_to_per_domain_collections():
    """Migrate existing sources to per-domain collections."""

    async with db_pool.acquire() as conn:
        sources = await conn.fetch(
            "SELECT id, collection_names, enabled_collections FROM sources"
        )

    collection_manager = CollectionManager(qdrant_client)

    for source in sources:
        collection_names = json.loads(source["collection_names"])

        # Create collections in Qdrant
        for collection_type, collection_name in collection_names.items():
            dimension = settings.COLLECTION_DIMENSIONS[collection_type]

            await qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=dimension, distance=Distance.COSINE)
            )

            logger.info(f"Created {collection_name} for source {source['id']}")

    # Optional: Migrate vectors from old shared collections to new per-domain collections
    # This is complex - may be easier to re-ingest documents
```

## Validation Gates

### Level 1: Syntax & Style
```bash
cd infra/rag-service/backend
mypy src/ --strict
ruff check src/ --fix
```

### Level 2: Unit Tests
```python
# Test collection name sanitization
def test_sanitize_collection_name():
    assert sanitize_collection_name("AI Knowledge", "documents") == "AI_Knowledge_documents"
    assert sanitize_collection_name("Network & Security!", "code") == "Network_Security_code"
    assert sanitize_collection_name("Test", "media") == "Test_media"

# Test collection creation
async def test_create_collections_for_source():
    manager = CollectionManager(qdrant_client)

    collection_names = await manager.create_collections_for_source(
        source_id=UUID("..."),
        source_title="AI Knowledge",
        enabled_collections=["documents", "code"]
    )

    assert collection_names == {
        "documents": "AI_Knowledge_documents",
        "code": "AI_Knowledge_code"
    }

    # Verify collections exist in Qdrant
    collections = await qdrant_client.get_collections()
    assert "AI_Knowledge_documents" in [c.name for c in collections]
    assert "AI_Knowledge_code" in [c.name for c in collections]
```

### Level 3: Integration Tests
```python
async def test_per_domain_search():
    # Create two domains
    ai_source_id = await create_source("AI Knowledge", ["documents", "code"])
    network_source_id = await create_source("Network Knowledge", ["documents"])

    # Ingest documents to each domain
    await ingest_document(ai_source_id, "ai_article.md")
    await ingest_document(network_source_id, "network_guide.md")

    # Search AI domain only
    results = await search_service.search(
        query="neural networks",
        source_ids=[ai_source_id],
        limit=10
    )

    # Should only return AI Knowledge results
    assert all(r["source_id"] == ai_source_id for r in results)

    # Search Network domain only
    results = await search_service.search(
        query="TCP/IP",
        source_ids=[network_source_id],
        limit=10
    )

    # Should only return Network Knowledge results
    assert all(r["source_id"] == network_source_id for r in results)
```

## Rollback Plan

If per-domain architecture causes issues:

```sql
-- Remove collection_names column
DROP INDEX IF EXISTS idx_sources_collection_names;
ALTER TABLE sources DROP COLUMN collection_names;

-- Revert to global collections
-- (Re-ingest documents into AI_DOCUMENTS, AI_CODE, AI_MEDIA)
```

## Risks & Mitigations

**Risk 1: Collection Name Collisions**
- *Mitigation*: Include source_id hash in collection name if title collision detected
- *Example*: `AI_Knowledge_abc123_documents` vs `AI_Knowledge_def456_documents`

**Risk 2: Too Many Collections (Qdrant Limits)**
- *Mitigation*: Qdrant supports 1000s of collections easily
- *Monitoring*: Add alert if collection count > 500

**Risk 3: Migration Data Loss**
- *Mitigation*: Keep old collections until migration verified
- *Backup*: Export vectors before migration
- *Validation*: Compare vector counts before/after

**Risk 4: Search Performance Degradation**
- *Mitigation*: Query only specified domains (not all collections)
- *Optimization*: Use Qdrant scroll API for large result sets
- *Monitoring*: Track search latency per domain

## Success Metrics

- [ ] Source creation creates unique collections (verify in Qdrant)
- [ ] Search returns only domain-specific results (0% cross-contamination)
- [ ] Collection deletion works (no orphaned vectors)
- [ ] Migration script completes without data loss
- [ ] Search latency < 200ms per domain
- [ ] All tests pass (unit + integration)

## Confidence Score: 9/10

High confidence because:
- Clear architecture design
- Builds on existing working code
- Well-defined naming strategy
- Comprehensive test coverage
- Rollback plan in place

Minor uncertainty:
- Collection name collision edge cases
- Migration complexity for large datasets
- Frontend UX for domain selection

---

**This PRP replaces the shared collection architecture with per-domain isolated collections, aligning with the knowledge domain use case.**
