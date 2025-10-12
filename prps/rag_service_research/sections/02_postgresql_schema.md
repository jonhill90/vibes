# PostgreSQL Schema Design

**Task 2: Complete Database Schema for RAG Service**

## Overview

This section provides the complete PostgreSQL database schema for the RAG service, including normalized table structures, foreign key relationships, indexes for performance optimization, and design rationale. The schema is designed to support document ingestion, chunking, vector search coordination, and full-text search capabilities.

**Key Design Principles**:
- Normalized structure with proper foreign key relationships
- Metadata stored in PostgreSQL for filtering and management
- Full-text search vectors (tsvector) for hybrid search
- Separate storage of text content (PostgreSQL) and embeddings (Qdrant)
- Atomic operations via CASCADE constraints
- Performance-optimized indexes for common query patterns

---

## Complete Schema

### Table 1: `sources`

The `sources` table tracks ingestion sources (uploads, crawls, API imports) and their processing status.

```sql
CREATE TABLE sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_type TEXT NOT NULL CHECK (source_type IN ('upload', 'crawl', 'api')),
    url TEXT,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    metadata JSONB DEFAULT '{}'::jsonb,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for filtering by status (common query pattern)
CREATE INDEX idx_sources_status ON sources(status);

-- Index for filtering by source_type
CREATE INDEX idx_sources_source_type ON sources(source_type);

-- Index for timestamp-based queries (recent sources)
CREATE INDEX idx_sources_created_at ON sources(created_at DESC);

-- Trigger to automatically update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER sources_updated_at
    BEFORE UPDATE ON sources
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

**Design Rationale**:
- **UUID primary key**: Prevents ID collision in distributed systems
- **CHECK constraints**: Enforces valid source_type and status values at database level
- **JSONB metadata**: Flexible storage for source-specific configuration (e.g., crawl depth, API endpoints)
- **error_message**: Stores failure details for debugging and retry logic
- **Indexes on status**: Fast filtering for "pending" sources in batch processing jobs

---

### Table 2: `documents`

The `documents` table stores document-level metadata and references to source ingestion.

```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    document_type TEXT,
    url TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    search_vector TSVECTOR,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Foreign key index for JOIN optimization
CREATE INDEX idx_documents_source_id ON documents(source_id);

-- GIN index for full-text search on title + metadata
CREATE INDEX idx_documents_search_vector ON documents USING GIN(search_vector);

-- Index for document type filtering
CREATE INDEX idx_documents_document_type ON documents(document_type);

-- Index for timestamp-based queries
CREATE INDEX idx_documents_created_at ON documents(created_at DESC);

-- Trigger to update search_vector automatically
CREATE OR REPLACE FUNCTION documents_search_vector_update()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector =
        setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.url, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(NEW.metadata::text, '')), 'C');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER documents_search_vector_trigger
    BEFORE INSERT OR UPDATE OF title, url, metadata
    ON documents
    FOR EACH ROW
    EXECUTE FUNCTION documents_search_vector_update();

-- Trigger for updated_at
CREATE TRIGGER documents_updated_at
    BEFORE UPDATE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

**Design Rationale**:
- **ON DELETE CASCADE**: When source deleted, all associated documents removed (atomic cleanup)
- **TSVECTOR for full-text**: Enables hybrid search combining vector + keyword matching
- **Weighted search_vector**: Title (A) more important than URL (B) more important than metadata (C)
- **Automatic triggers**: search_vector updates automatically when title/url/metadata changes
- **JSONB metadata**: Stores document-specific attributes (author, tags, language, custom fields)

---

### Table 3: `chunks`

The `chunks` table stores document chunks with text content and full-text search vectors. Embeddings are stored separately in Qdrant.

```sql
CREATE TABLE chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    text TEXT NOT NULL,
    token_count INTEGER,
    search_vector TSVECTOR,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Ensure unique chunk ordering per document
    CONSTRAINT unique_document_chunk UNIQUE(document_id, chunk_index)
);

-- Foreign key index for JOIN optimization
CREATE INDEX idx_chunks_document_id ON chunks(document_id);

-- GIN index for full-text search on chunk text
CREATE INDEX idx_chunks_search_vector ON chunks USING GIN(search_vector);

-- Index for ordered retrieval (chunk sequence matters for context)
CREATE INDEX idx_chunks_document_id_chunk_index ON chunks(document_id, chunk_index);

-- Trigger to update search_vector automatically
CREATE OR REPLACE FUNCTION chunks_search_vector_update()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector = to_tsvector('english', COALESCE(NEW.text, ''));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER chunks_search_vector_trigger
    BEFORE INSERT OR UPDATE OF text
    ON chunks
    FOR EACH ROW
    EXECUTE FUNCTION chunks_search_vector_update();
```

**Design Rationale**:
- **ON DELETE CASCADE**: Deleting document removes all chunks (maintains referential integrity)
- **UNIQUE(document_id, chunk_index)**: Prevents duplicate chunks, enforces ordering
- **TEXT storage**: Full chunk text stored for retrieval and display (not just metadata)
- **token_count**: Enables token budget management for LLM context windows
- **TSVECTOR per chunk**: Enables precise keyword matching at chunk level (better than document-level only)
- **Composite index**: Fast retrieval of chunks in order (critical for context reconstruction)

**Why Store Text in PostgreSQL AND Qdrant?**
- **PostgreSQL**: Source of truth for text content, enables keyword search, supports transactions
- **Qdrant**: Stores embeddings and small payload (truncated text for display), optimized for vector similarity
- **Trade-off**: Slight storage duplication vs. operational simplicity (single DB failure doesn't break both search modes)

---

### Table 4: `crawl_jobs`

The `crawl_jobs` table tracks web crawling operations with progress and error reporting.

```sql
CREATE TABLE crawl_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    pages_crawled INTEGER NOT NULL DEFAULT 0,
    pages_total INTEGER,
    max_pages INTEGER DEFAULT 100,
    max_depth INTEGER DEFAULT 3,
    current_depth INTEGER DEFAULT 0,
    error_message TEXT,
    error_count INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}'::jsonb,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Foreign key index for finding crawl jobs by source
CREATE INDEX idx_crawl_jobs_source_id ON crawl_jobs(source_id);

-- Index for filtering by status (find active/pending jobs)
CREATE INDEX idx_crawl_jobs_status ON crawl_jobs(status);

-- Index for monitoring recent jobs
CREATE INDEX idx_crawl_jobs_created_at ON crawl_jobs(created_at DESC);

-- Composite index for dashboard queries (status + progress)
CREATE INDEX idx_crawl_jobs_status_pages ON crawl_jobs(status, pages_crawled);

-- Trigger for updated_at
CREATE TRIGGER crawl_jobs_updated_at
    BEFORE UPDATE ON crawl_jobs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

**Design Rationale**:
- **ON DELETE CASCADE**: Deleting source removes crawl job history (cleanup)
- **Progress tracking**: pages_crawled, pages_total, current_depth for UI progress bars
- **Error resilience**: error_count tracks transient failures, error_message for debugging
- **Crawl limits**: max_pages, max_depth prevent runaway crawls
- **Status granularity**: Distinguishes "running" vs "pending" for job queue management
- **Metadata JSONB**: Stores crawl-specific config (user_agent, rate_limits, excluded_patterns)

---

## Index Specifications & Performance

### GIN Indexes (Full-Text Search)

**Purpose**: Enable fast full-text search using PostgreSQL's tsvector

```sql
-- Documents: Search by title, URL, metadata
CREATE INDEX idx_documents_search_vector ON documents USING GIN(search_vector);

-- Chunks: Search by chunk text content
CREATE INDEX idx_chunks_search_vector ON chunks USING GIN(search_vector);
```

**Performance**:
- **Query time**: O(log n) for keyword lookup, ~10-50ms for 1M chunks
- **Index size**: ~30% of text data size (compressed inverted index)
- **Build time**: Created AFTER bulk data load (30-60 seconds for 1M chunks)

**Usage Example**:
```sql
-- Hybrid search: Combine vector results with keyword search
SELECT c.id, c.text, ts_rank(c.search_vector, query) AS rank
FROM chunks c, to_tsquery('english', 'machine & learning') AS query
WHERE c.search_vector @@ query
ORDER BY rank DESC
LIMIT 100;
```

---

### B-Tree Indexes (Foreign Keys & Filtering)

**Purpose**: Fast JOIN operations and status filtering

```sql
-- Foreign key indexes (critical for JOIN performance)
CREATE INDEX idx_documents_source_id ON documents(source_id);
CREATE INDEX idx_chunks_document_id ON chunks(document_id);
CREATE INDEX idx_crawl_jobs_source_id ON crawl_jobs(source_id);

-- Status filtering indexes (common in batch processing)
CREATE INDEX idx_sources_status ON sources(status);
CREATE INDEX idx_crawl_jobs_status ON crawl_jobs(status);
```

**Performance**:
- **JOIN time**: O(log n) lookup, ~1-5ms for 1M rows
- **Filter time**: O(log n) + scan, ~5-20ms for status queries
- **Index size**: ~5-10% of table size

**Usage Example**:
```sql
-- Find all chunks for a document (uses idx_chunks_document_id)
SELECT * FROM chunks
WHERE document_id = 'abc-123-def'
ORDER BY chunk_index;

-- Find pending sources (uses idx_sources_status)
SELECT * FROM sources
WHERE status = 'pending'
ORDER BY created_at
LIMIT 100;
```

---

### Composite Indexes (Complex Queries)

**Purpose**: Optimize queries with multiple conditions

```sql
-- Chunk retrieval in order (critical for context reconstruction)
CREATE INDEX idx_chunks_document_id_chunk_index ON chunks(document_id, chunk_index);

-- Crawl job monitoring (status + progress)
CREATE INDEX idx_crawl_jobs_status_pages ON crawl_jobs(status, pages_crawled);
```

**Performance**:
- **Composite query**: Single index lookup, ~1-3ms
- **vs. Multiple indexes**: 2-3x faster than using separate indexes
- **Use case**: Dashboard queries filtering + sorting

**Usage Example**:
```sql
-- Get chunks in order (uses composite index)
SELECT id, text, chunk_index
FROM chunks
WHERE document_id = 'abc-123'
ORDER BY chunk_index;
-- Execution plan: Index Scan using idx_chunks_document_id_chunk_index
```

---

## Design Decisions & Rationale

### Decision 1: Store Text in Both PostgreSQL and Qdrant

**Question**: Should chunk text be stored in PostgreSQL, Qdrant, or both?

**Decision**: Store in BOTH

**Rationale**:

| Storage Location | Purpose | Trade-offs |
|-----------------|---------|-----------|
| **PostgreSQL (Full Text)** | Source of truth, transactional updates, full-text search, analytics | Requires separate vector DB |
| **Qdrant (Truncated Text)** | Fast retrieval with vector results, payload filtering | Limited by payload size (recommended <1KB) |
| **Both (Chosen)** | Best of both: PostgreSQL for management, Qdrant for search | ~20% storage overhead |

**Benefits**:
1. **Hybrid Search**: Combine Qdrant vector search + PostgreSQL keyword search for better recall
2. **Operational Resilience**: If Qdrant unavailable, can still query metadata and text from PostgreSQL
3. **Analytics**: SQL queries on chunks for insights (avg token_count, text statistics)
4. **Transactional Integrity**: PostgreSQL ensures atomic document + chunks insertion

**Cost**:
- **Storage**: ~20% overhead (Qdrant payload is truncated, not full duplication)
- **Sync Complexity**: Must keep PostgreSQL and Qdrant in sync (use transactions)

**Alternative Considered**: Store text ONLY in Qdrant
- **Rejected because**: No transactional guarantees, limited analytics, tightly couples search and storage

---

### Decision 2: ON DELETE CASCADE vs. RESTRICT

**Question**: What happens when parent record deleted?

**Chosen Constraints**:

```sql
-- CASCADE: Deleting parent removes children
documents.source_id REFERENCES sources(id) ON DELETE CASCADE
chunks.document_id REFERENCES documents(id) ON DELETE CASCADE
crawl_jobs.source_id REFERENCES sources(id) ON DELETE CASCADE
```

**Rationale**:

| Scenario | Constraint | Behavior | Use Case |
|----------|-----------|----------|----------|
| Delete source | CASCADE | All documents + chunks deleted | User removes entire ingestion source |
| Delete document | CASCADE | All chunks deleted | Document outdated or incorrect |
| Delete crawl job | CASCADE | Job history removed | Cleanup old crawl records |

**When to use RESTRICT** (NOT used in this schema):
- If deleting parent should fail unless children manually removed first
- Example: `user_id` in documents (don't allow deleting user who owns documents)
- **Not applicable here**: Sources/documents/chunks form strict hierarchy

**Safety Mechanism**:
```sql
-- Soft delete pattern (alternative to CASCADE)
ALTER TABLE sources ADD COLUMN deleted_at TIMESTAMPTZ;

-- Query only non-deleted sources
SELECT * FROM sources WHERE deleted_at IS NULL;

-- "Delete" without cascade (preserves children)
UPDATE sources SET deleted_at = NOW() WHERE id = 'abc-123';
```

**Why CASCADE is safe here**:
1. **Logical grouping**: Documents belong to source, chunks belong to document
2. **Referential integrity**: No orphaned chunks (avoids confusion)
3. **Storage cleanup**: Prevents accumulation of unused data
4. **Vector DB sync**: Can listen to DELETE events and remove Qdrant points

---

### Decision 3: UUID vs. Serial IDs

**Question**: Use UUID or auto-incrementing integers for primary keys?

**Decision**: UUID (gen_random_uuid())

**Rationale**:

| ID Type | Pros | Cons | Use Case |
|---------|------|------|----------|
| **UUID** | No collision in distributed systems, portable across databases, secure (non-guessable) | Larger storage (16 bytes vs 4-8 bytes), slower index performance | Multi-node systems, public APIs |
| **SERIAL/BIGSERIAL** | Smaller (4-8 bytes), faster index, ordered by insertion | Collision risk in distributed systems, reveals record count | Single-node, internal systems |

**Why UUID for RAG service**:
1. **Qdrant Integration**: Qdrant uses string IDs, UUID maps cleanly
2. **Distributed Ingestion**: Multiple workers can generate IDs without coordination
3. **Security**: Document IDs not sequential (prevents enumeration attacks)
4. **Migration**: Can merge databases without ID conflicts

**Performance Impact**:
- **Index size**: ~30% larger than BIGSERIAL
- **Insert speed**: ~10-15% slower than SERIAL
- **Mitigation**: Use `gen_random_uuid()` (Postgres 13+) which is faster than uuid-ossp extension

---

### Decision 4: JSONB for Metadata

**Question**: Should metadata be separate columns or JSONB?

**Decision**: JSONB (with optional GIN index for querying)

**Rationale**:

```sql
-- Flexible metadata storage
metadata JSONB DEFAULT '{}'::jsonb

-- Optional: Index for fast queries on metadata keys
CREATE INDEX idx_documents_metadata ON documents USING GIN(metadata);

-- Query example: Find documents with specific metadata
SELECT * FROM documents
WHERE metadata @> '{"language": "en", "category": "technical"}';
```

**Benefits**:
1. **Schema flexibility**: Add custom fields without migrations (e.g., author, tags, language)
2. **Per-source customization**: Different sources have different metadata requirements
3. **Fast queries**: GIN index enables fast JSON containment queries (`@>` operator)

**When to use separate columns instead**:
- Frequently filtered fields (e.g., `language TEXT` if filtering by language is primary use case)
- Fields needing foreign keys (e.g., `user_id UUID REFERENCES users`)
- Fields requiring CHECK constraints (e.g., `priority INTEGER CHECK (priority BETWEEN 1 AND 5)`)

**Best Practice**:
- Store critical, frequently-queried fields as columns (title, status, created_at)
- Store optional, variable fields in JSONB (tags, custom attributes)

---

### Decision 5: Automatic Triggers vs. Application Updates

**Question**: Should search_vector and updated_at be managed by triggers or application code?

**Decision**: Database triggers (automatic)

**Rationale**:

```sql
-- Trigger approach (chosen)
CREATE TRIGGER documents_search_vector_trigger
    BEFORE INSERT OR UPDATE OF title, url, metadata
    ON documents
    FOR EACH ROW
    EXECUTE FUNCTION documents_search_vector_update();
```

**Benefits**:
1. **Consistency**: Can't forget to update search_vector (enforced at database level)
2. **DRY principle**: Single implementation, all applications benefit
3. **Performance**: Updates happen in same transaction (no additional round-trip)

**Trade-offs**:
- **Debugging**: Harder to trace (trigger logic hidden from application logs)
- **Testing**: Must test with actual database (can't easily mock)
- **Migration**: If changing trigger logic, must run migration on all environments

**Alternative**: Application updates
```python
# Application code (NOT used)
async def create_document(title: str, url: str):
    search_vector = f"to_tsvector('english', '{title} {url}')"
    await conn.execute(
        "INSERT INTO documents (title, url, search_vector) VALUES ($1, $2, $3)",
        title, url, search_vector
    )
```

**Why triggers are better here**:
- **Full-text indexing**: Complex logic (language detection, stemming) better in database
- **updated_at**: Forgetting to set causes stale timestamps (triggers prevent)
- **Performance**: to_tsvector() is optimized SQL function (faster than Python string manipulation)

---

## Query Patterns & Performance

### Pattern 1: Hybrid Search (Vector + Full-Text)

**Use Case**: Find relevant chunks combining semantic similarity (Qdrant) and keyword matching (PostgreSQL)

**Query Flow**:
1. **Qdrant vector search** → Top 100 results by cosine similarity
2. **PostgreSQL keyword search** → Top 100 results by ts_rank
3. **Combine scores** → Weighted average (0.7 vector + 0.3 keyword)
4. **Return top 10** → Best of both worlds

**PostgreSQL Query**:
```sql
-- Step 2: Full-text search on chunks
WITH keyword_results AS (
    SELECT
        c.id,
        c.document_id,
        c.text,
        ts_rank(c.search_vector, query) AS text_rank
    FROM chunks c, to_tsquery('english', 'embeddings & vectors') AS query
    WHERE c.search_vector @@ query
    ORDER BY text_rank DESC
    LIMIT 100
)
SELECT * FROM keyword_results;
```

**Performance**:
- **Vector search (Qdrant)**: 10-30ms for 1M vectors
- **Keyword search (PostgreSQL)**: 20-50ms for 1M chunks
- **Total hybrid**: 50-100ms (parallel execution possible)

**Index Usage**:
- Uses `idx_chunks_search_vector` (GIN index)
- Query plan: `Bitmap Index Scan on idx_chunks_search_vector`

---

### Pattern 2: Document Ingestion (Transaction)

**Use Case**: Atomically insert document + chunks + Qdrant vectors

**Query Flow**:
```python
async def ingest_document(doc: Document, chunks: list[Chunk], embeddings: list[list[float]]):
    async with db_pool.acquire() as conn:
        async with conn.transaction():
            # 1. Insert document metadata
            doc_id = await conn.fetchval(
                """
                INSERT INTO documents (source_id, title, document_type, url, metadata)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id
                """,
                doc.source_id, doc.title, doc.type, doc.url, doc.metadata
            )

            # 2. Insert chunks (batch)
            await conn.executemany(
                """
                INSERT INTO chunks (document_id, chunk_index, text, token_count, metadata)
                VALUES ($1, $2, $3, $4, $5)
                """,
                [(doc_id, i, c.text, c.token_count, c.metadata)
                 for i, c in enumerate(chunks)]
            )

            # 3. If transaction succeeds, insert to Qdrant (outside transaction)
            # Note: Qdrant not transactional, but we have PostgreSQL as source of truth

    # 4. Upsert vectors to Qdrant (after PostgreSQL commit)
    await qdrant_client.upsert(
        collection_name="documents",
        points=[
            {
                "id": str(chunk_id),
                "vector": embedding,
                "payload": {"document_id": str(doc_id), "text": chunk.text[:1000]}
            }
            for chunk_id, chunk, embedding in zip(chunk_ids, chunks, embeddings)
        ]
    )
```

**Performance**:
- **Single document (10 chunks)**: 50-100ms (PostgreSQL) + 20-50ms (Qdrant)
- **Batch (100 documents)**: 2-5 seconds (PostgreSQL) + 500ms-1s (Qdrant)
- **Optimization**: Use `executemany()` for chunk inserts (single round-trip)

**Error Handling**:
- If PostgreSQL fails → Transaction rolls back, no partial data
- If Qdrant fails → PostgreSQL data committed, mark document as "embedding_pending" for retry

---

### Pattern 3: Source Cleanup (Cascade Delete)

**Use Case**: Remove all data associated with a source

**Query**:
```sql
-- Single DELETE cascades to documents, chunks, crawl_jobs
DELETE FROM sources WHERE id = 'abc-123-def';

-- Behind the scenes (automatic):
-- 1. DELETE FROM crawl_jobs WHERE source_id = 'abc-123-def'
-- 2. For each document in sources:
--    a. DELETE FROM chunks WHERE document_id = document.id
--    b. DELETE FROM documents WHERE id = document.id
-- 3. DELETE FROM sources WHERE id = 'abc-123-def'
```

**Performance**:
- **1 source, 100 documents, 1000 chunks**: 200-500ms
- **Index usage**: idx_documents_source_id, idx_chunks_document_id
- **Locking**: Row-level locks (won't block concurrent reads)

**Qdrant Cleanup**:
```python
# Listen to PostgreSQL DELETE events and sync to Qdrant
async def cleanup_source(source_id: str):
    # Get all chunk IDs before deletion
    chunk_ids = await conn.fetch(
        """
        SELECT c.id
        FROM chunks c
        JOIN documents d ON c.document_id = d.id
        WHERE d.source_id = $1
        """,
        source_id
    )

    # Delete from PostgreSQL (cascades)
    await conn.execute("DELETE FROM sources WHERE id = $1", source_id)

    # Sync to Qdrant
    await qdrant_client.delete(
        collection_name="documents",
        points_selector=[str(chunk_id) for chunk_id in chunk_ids]
    )
```

---

### Pattern 4: Progress Tracking (Crawl Jobs)

**Use Case**: Monitor active crawl jobs and display progress

**Query**:
```sql
-- Dashboard query: Active crawls with progress
SELECT
    cj.id,
    cj.source_id,
    s.url AS source_url,
    cj.status,
    cj.pages_crawled,
    cj.pages_total,
    CASE
        WHEN cj.pages_total > 0
        THEN ROUND((cj.pages_crawled::numeric / cj.pages_total) * 100, 2)
        ELSE 0
    END AS progress_percentage,
    cj.current_depth,
    cj.max_depth,
    cj.error_count,
    cj.started_at,
    NOW() - cj.started_at AS elapsed_time
FROM crawl_jobs cj
JOIN sources s ON cj.source_id = s.id
WHERE cj.status IN ('running', 'pending')
ORDER BY cj.started_at DESC;
```

**Performance**:
- **Query time**: 5-20ms (uses idx_crawl_jobs_status, idx_crawl_jobs_source_id)
- **Update frequency**: Every 10-30 seconds from crawler workers
- **Concurrency**: Multiple crawlers updating different jobs (no contention)

**Update Pattern**:
```sql
-- Crawler updates progress atomically
UPDATE crawl_jobs
SET
    pages_crawled = pages_crawled + 1,
    current_depth = $1,
    updated_at = NOW()
WHERE id = $2 AND status = 'running';
```

---

## Validation & Testing

### Schema Validation Queries

```sql
-- Check 1: Verify all tables exist
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ('sources', 'documents', 'chunks', 'crawl_jobs');
-- Expected: 4 rows

-- Check 2: Verify foreign key constraints
SELECT
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name,
    rc.delete_rule
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
JOIN information_schema.referential_constraints AS rc
    ON tc.constraint_name = rc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY';
-- Expected: 3 constraints (all with delete_rule = 'CASCADE')

-- Check 3: Verify indexes
SELECT
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename IN ('sources', 'documents', 'chunks', 'crawl_jobs')
ORDER BY tablename, indexname;
-- Expected: 15+ indexes (GIN, B-tree, composite)

-- Check 4: Verify triggers
SELECT
    trigger_name,
    event_object_table,
    action_statement
FROM information_schema.triggers
WHERE event_object_table IN ('sources', 'documents', 'chunks', 'crawl_jobs');
-- Expected: 5 triggers (search_vector updates + updated_at)
```

---

## Migration Scripts

### Initial Schema Creation

```sql
-- schema_v1.sql
-- Run with: psql -U postgres -d rag_service -f schema_v1.sql

BEGIN;

-- Create extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create tables (sources first, then dependents)
\i tables/01_sources.sql
\i tables/02_documents.sql
\i tables/03_chunks.sql
\i tables/04_crawl_jobs.sql

-- Create indexes
\i indexes/01_sources_indexes.sql
\i indexes/02_documents_indexes.sql
\i indexes/03_chunks_indexes.sql
\i indexes/04_crawl_jobs_indexes.sql

-- Create triggers
\i triggers/01_updated_at_trigger.sql
\i triggers/02_search_vector_triggers.sql

COMMIT;
```

### Schema Verification Test

```python
import asyncpg
import pytest

@pytest.fixture
async def db_pool():
    pool = await asyncpg.create_pool("postgresql://localhost/rag_service_test")
    yield pool
    await pool.close()

async def test_schema_complete(db_pool):
    """Verify all tables, indexes, and constraints exist"""
    async with db_pool.acquire() as conn:
        # Check tables
        tables = await conn.fetch(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            """
        )
        table_names = {t['table_name'] for t in tables}
        assert {'sources', 'documents', 'chunks', 'crawl_jobs'}.issubset(table_names)

        # Check foreign keys have CASCADE
        fks = await conn.fetch(
            """
            SELECT tc.table_name, rc.delete_rule
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.referential_constraints AS rc
                ON tc.constraint_name = rc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
            """
        )
        for fk in fks:
            assert fk['delete_rule'] == 'CASCADE', f"Foreign key in {fk['table_name']} not CASCADE"

        # Check search_vector columns exist
        search_vector_cols = await conn.fetch(
            """
            SELECT table_name
            FROM information_schema.columns
            WHERE column_name = 'search_vector' AND data_type = 'tsvector'
            """
        )
        assert len(search_vector_cols) == 2  # documents and chunks

async def test_cascade_delete(db_pool):
    """Verify CASCADE deletes work correctly"""
    async with db_pool.acquire() as conn:
        async with conn.transaction():
            # Create source
            source_id = await conn.fetchval(
                "INSERT INTO sources (source_type, url) VALUES ('upload', 'test.pdf') RETURNING id"
            )

            # Create document
            doc_id = await conn.fetchval(
                "INSERT INTO documents (source_id, title) VALUES ($1, 'Test Doc') RETURNING id",
                source_id
            )

            # Create chunks
            await conn.execute(
                "INSERT INTO chunks (document_id, chunk_index, text) VALUES ($1, 0, 'Test chunk')",
                doc_id
            )

            # Delete source (should cascade)
            await conn.execute("DELETE FROM sources WHERE id = $1", source_id)

            # Verify cascade worked
            doc_count = await conn.fetchval(
                "SELECT COUNT(*) FROM documents WHERE id = $1", doc_id
            )
            assert doc_count == 0, "Document not deleted by CASCADE"

            chunk_count = await conn.fetchval(
                "SELECT COUNT(*) FROM chunks WHERE document_id = $1", doc_id
            )
            assert chunk_count == 0, "Chunks not deleted by CASCADE"
```

---

## Summary

**Schema Complete**: 4 tables (sources, documents, chunks, crawl_jobs)

**Key Features**:
- Normalized structure with CASCADE constraints for atomic cleanup
- Full-text search vectors (tsvector) for hybrid search capabilities
- Automatic triggers for search_vector and updated_at maintenance
- Performance-optimized indexes for common query patterns
- JSONB metadata for flexibility without schema migrations
- UUID primary keys for distributed system compatibility

**Performance Characteristics**:
- Single document insert: 50-100ms (10 chunks)
- Hybrid search: 50-100ms (1M chunks)
- Source deletion: 200-500ms (100 documents, 1000 chunks)
- Progress query: 5-20ms (active jobs dashboard)

**Design Rationale**:
- Store text in both PostgreSQL and Qdrant for operational resilience and hybrid search
- Use CASCADE for hierarchical cleanup (sources → documents → chunks)
- Use triggers for automatic search_vector updates (consistency)
- Use JSONB for flexible metadata (schema evolution)

This schema provides a solid foundation for the RAG service, balancing performance, flexibility, and operational simplicity.
