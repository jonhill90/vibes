# Document Ingestion Pipeline Design

## Overview

This section describes the complete document processing flow from upload/crawl to searchable vector embeddings. The pipeline is designed with robust error handling, progress tracking, and failure recovery to ensure data integrity even under API quota constraints or processing failures.

**Pipeline Flow**: Raw Document → Parse → Chunk → Embed → Store → Index

**Key Design Principles**:
- **NEVER store null/zero embeddings** (prevents vector search corruption)
- **Fail-safe error handling** (track failures, enable retry)
- **Atomic operations** (all-or-nothing per document)
- **Progress transparency** (emit events, update status)
- **Cost optimization** (cache embeddings, minimize API calls)

---

## 1. Ingestion Flow Design

### Five-Step Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    DOCUMENT INGESTION PIPELINE                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: UPLOAD/CRAWL
   ↓
   Input: PDF, HTML, DOCX, Markdown, etc.
   Output: Raw binary/text data
   Storage: Temporary file storage or S3

Step 2: PARSE (Docling)
   ↓
   Input: Raw document
   Output: Structured document object (text + tables + metadata)
   Tool: Docling (https://docling-project.github.io/docling/)
   Features:
   - Preserves tables in structured format
   - Extracts document hierarchy (headings, sections)
   - OCR for scanned PDFs
   - Handles multi-column layouts

Step 3: CHUNK (Hybrid Semantic Chunking)
   ↓
   Input: Structured document
   Output: List of text chunks (avg 500 tokens each)
   Strategy: Hybrid chunking with semantic boundaries
   Rules:
   - Respect paragraph/section boundaries
   - Keep tables intact (don't split)
   - Keep code blocks intact
   - Max 512 tokens per chunk (OpenAI limit)
   - Min 100 tokens per chunk (avoid fragments)
   - Overlap: 50 tokens between chunks

Step 4: EMBED (Batch OpenAI API)
   ↓
   Input: List of text chunks
   Output: List of 1536-dim embeddings (text-embedding-3-small)
   Batch Size: 100 chunks per API call
   Cache: Check MD5(content) → embedding cache before API call
   Error Handling: CRITICAL - Use EmbeddingBatchResult pattern (see Gotcha #1)

Step 5: STORE (PostgreSQL + Qdrant)
   ↓
   PostgreSQL: document metadata + chunk text + search_vector (tsvector)
   Qdrant: vector embeddings + minimal payload
   Batch Upsert: 500 vectors per Qdrant batch
   Transaction: All-or-nothing per document (atomic)

   Output: Searchable document ready for RAG queries
```

### Pipeline Pseudocode

```python
async def ingest_document(
    document_path: str,
    source_id: str,
    document_type: str,
) -> dict:
    """
    Complete document ingestion pipeline with robust error handling.

    Returns:
        {
            "success": bool,
            "document_id": str,
            "chunks_processed": int,
            "chunks_failed": int,
            "failures": list[dict],
            "cost_estimate": float  # USD
        }
    """

    # Step 1: Upload/Crawl (already handled by caller)
    logger.info(f"Starting ingestion for: {document_path}")

    # Step 2: Parse with Docling
    try:
        parsed_doc = await parse_document_docling(document_path)
    except ParsingError as e:
        logger.error(f"Parsing failed: {e}")
        await update_document_status(source_id, "failed", str(e))
        return {
            "success": False,
            "error": f"Parsing failed: {e}",
            "stage": "parse"
        }

    # Step 3: Chunk
    chunks = hybrid_chunk_document(
        content=parsed_doc.content,
        metadata=parsed_doc.metadata,
        max_tokens=500,
        overlap_tokens=50,
        preserve_tables=True,
        preserve_code_blocks=True
    )

    logger.info(f"Created {len(chunks)} chunks from document")

    # Step 4: Embed (with quota handling)
    embedding_result = await embed_chunks_safe(chunks)

    if embedding_result.failure_count > 0:
        logger.warning(
            f"Embedding failures: {embedding_result.failure_count}/{len(chunks)}"
        )

    # Step 5: Store (only successful embeddings)
    try:
        document_id = await store_document_atomic(
            source_id=source_id,
            document_type=document_type,
            title=parsed_doc.title,
            metadata=parsed_doc.metadata,
            chunks=chunks[:embedding_result.success_count],
            embeddings=embedding_result.embeddings,
        )
    except Exception as e:
        logger.error(f"Storage failed: {e}")
        return {
            "success": False,
            "error": f"Storage failed: {e}",
            "stage": "store"
        }

    # Calculate cost (OpenAI: $0.00002 per 1K tokens)
    total_tokens = sum(chunk.token_count for chunk in chunks[:embedding_result.success_count])
    cost_estimate = (total_tokens / 1000) * 0.00002

    return {
        "success": embedding_result.failure_count == 0,
        "document_id": document_id,
        "chunks_processed": embedding_result.success_count,
        "chunks_failed": embedding_result.failure_count,
        "failures": embedding_result.failed_items,
        "cost_estimate": cost_estimate
    }
```

---

## 2. Error Handling Strategy

### Critical: OpenAI Quota Exhaustion (Gotcha #1)

**NEVER store null/zero embeddings**. This corrupts vector search by making documents match every query with equal irrelevance.

**Solution**: Use `EmbeddingBatchResult` pattern to track failures and stop on quota exhaustion.

```python
from dataclasses import dataclass, field
import openai
import hashlib

@dataclass
class EmbeddingBatchResult:
    """Track successes and failures during batch embedding."""
    embeddings: list[list[float]] = field(default_factory=list)
    failed_items: list[dict] = field(default_factory=list)
    success_count: int = 0
    failure_count: int = 0

    def add_success(self, embedding: list[float], text: str):
        """Record successful embedding."""
        self.embeddings.append(embedding)
        self.success_count += 1

    def add_failure(self, text: str, error: Exception):
        """Record failed embedding for retry."""
        self.failed_items.append({
            "text_preview": text[:200],
            "error": str(error),
            "error_type": type(error).__name__,
            "timestamp": datetime.utcnow().isoformat()
        })
        self.failure_count += 1


async def embed_chunks_safe(chunks: list[Chunk]) -> EmbeddingBatchResult:
    """
    Batch embed chunks with quota exhaustion handling.

    CRITICAL: Stops on quota exhaustion to prevent data corruption.
    Only returns embeddings that succeeded.
    """
    result = EmbeddingBatchResult()

    # Process in batches of 100 (OpenAI recommended)
    for batch in batched(chunks, size=100):
        try:
            # Check cache first (MD5 content hash)
            cached_embeddings = await get_cached_embeddings(batch)

            # Separate cached and uncached
            uncached = []
            for chunk, cached_emb in zip(batch, cached_embeddings):
                if cached_emb is not None:
                    result.add_success(cached_emb, chunk.text)
                else:
                    uncached.append(chunk)

            # Embed uncached chunks
            if uncached:
                response = await openai_client.embeddings.create(
                    model="text-embedding-3-small",
                    input=[chunk.text for chunk in uncached]
                )

                for chunk, emb_data in zip(uncached, response.data):
                    embedding = emb_data.embedding
                    result.add_success(embedding, chunk.text)

                    # Cache for future use
                    await cache_embedding(chunk.content_hash, embedding)

        except openai.RateLimitError as e:
            if "insufficient_quota" in str(e):
                # STOP IMMEDIATELY - quota exhausted
                logger.error(
                    f"OpenAI quota exhausted after {result.success_count} chunks. "
                    f"Remaining {len(chunks) - result.success_count} chunks will be marked for retry."
                )

                # Mark all remaining chunks as failed
                remaining_chunks = chunks[result.success_count:]
                for chunk in remaining_chunks:
                    result.add_failure(chunk.text, e)

                break  # Don't corrupt data with null embeddings
            else:
                # Regular rate limit (429 but not quota) - add to retry queue
                logger.warning(f"Rate limit hit: {e}")
                for chunk in batch:
                    result.add_failure(chunk.text, e)

        except Exception as e:
            logger.error(f"Unexpected error during embedding: {e}")
            for chunk in batch:
                result.add_failure(chunk.text, e)

    # Save failures for manual retry
    if result.failed_items:
        await save_embedding_failures(result.failed_items)

    return result
```

### Error Handling by Stage

| Stage | Failure Type | Action | Retry Strategy |
|-------|--------------|--------|----------------|
| **Parse** | Parsing failure (corrupted PDF, unsupported format) | Log error, mark document as 'failed', skip | Manual retry after format conversion |
| **Chunk** | Chunk too large (>512 tokens) | Split further or truncate with warning | Auto-retry with smaller max_tokens |
| **Embed** | OpenAI quota exhausted | STOP, track failures, wait for quota refill | Manual retry after quota reset |
| **Embed** | OpenAI rate limit (429) | Exponential backoff, retry up to 3 times | Auto-retry with 1s, 2s, 4s delays |
| **Embed** | Network timeout | Retry 3x with exponential backoff | Auto-retry |
| **Store** | PostgreSQL constraint violation | Log error, rollback transaction | Manual investigation |
| **Store** | Qdrant insert failure | Retry 3x with exponential backoff | Auto-retry |
| **Store** | Transaction timeout | Rollback, reduce batch size, retry | Auto-retry with smaller batch |

### Retry Queue Design

```python
# PostgreSQL table for tracking retry queue
CREATE TABLE embedding_retry_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL,
    chunk_index INT NOT NULL,
    chunk_text TEXT NOT NULL,
    content_hash TEXT NOT NULL,  -- MD5 for deduplication
    error_type TEXT NOT NULL,
    error_message TEXT,
    retry_count INT DEFAULT 0,
    last_retry_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(document_id, chunk_index)
);

CREATE INDEX idx_retry_queue_document ON embedding_retry_queue(document_id);
CREATE INDEX idx_retry_queue_retry_count ON embedding_retry_queue(retry_count);
```

---

## 3. Progress Tracking

### Status Flow

```
Source Status Flow:
'pending' → 'processing' → 'completed' | 'failed' | 'partially_failed'

Document Status Flow:
'pending' → 'parsing' → 'chunking' → 'embedding' → 'storing' → 'completed' | 'failed'
```

### Progress Events

Emit progress events during ingestion for real-time monitoring:

```python
class IngestionProgress:
    """Progress tracker for document ingestion."""

    def __init__(self, total_documents: int):
        self.total_documents = total_documents
        self.processed = 0
        self.failed = 0
        self.current_stage = "initializing"

    async def emit_progress(self, document_id: str, stage: str, details: dict):
        """Emit progress event (WebSocket, SSE, or logging)."""
        self.current_stage = stage

        event = {
            "document_id": document_id,
            "stage": stage,
            "progress": f"{self.processed}/{self.total_documents}",
            "percentage": int((self.processed / self.total_documents) * 100),
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Emit via WebSocket or Server-Sent Events
        await broadcast_progress_event(event)

        # Also log for debugging
        logger.info(f"Progress: {event['stage']} - {event['percentage']}%")


# Usage in ingestion pipeline
progress = IngestionProgress(total_documents=len(documents))

for doc in documents:
    await progress.emit_progress(doc.id, "parsing", {"file": doc.filename})
    parsed = await parse_document_docling(doc.path)

    await progress.emit_progress(doc.id, "chunking", {"chunks": len(chunks)})
    chunks = hybrid_chunk_document(parsed.content)

    await progress.emit_progress(
        doc.id,
        "embedding",
        {"chunks": len(chunks), "batch_size": 100}
    )
    result = await embed_chunks_safe(chunks)

    await progress.emit_progress(
        doc.id,
        "storing",
        {"success": result.success_count, "failed": result.failure_count}
    )
    await store_document_atomic(doc.id, chunks, result.embeddings)

    progress.processed += 1
    if result.failure_count > 0:
        progress.failed += 1
```

### Source Table Status Tracking

```sql
-- Update source status with error details
UPDATE sources
SET
    status = $1,  -- 'processing', 'completed', 'failed', 'partially_failed'
    documents_processed = $2,
    documents_failed = $3,
    error_message = $4,
    updated_at = NOW()
WHERE id = $5;
```

---

## 4. Batch Processing Design

### Batch Sizes (Optimized for Performance)

| Stage | Batch Size | Rationale |
|-------|------------|-----------|
| **Document Processing** | 10 documents | Parallel processing without overwhelming memory |
| **Chunk Embedding** | 100 chunks | OpenAI recommended batch size for embeddings API |
| **Vector Upsert** | 500 vectors | Qdrant optimal batch size for bulk inserts |
| **PostgreSQL Commit** | 1 document (atomic) | All-or-nothing per document for consistency |

### Batch Processing Pseudocode

```python
async def batch_ingest_documents(
    documents: list[Document],
    source_id: str,
    batch_size: int = 10,
) -> dict:
    """
    Process multiple documents in batches with progress tracking.
    """
    results = {
        "total": len(documents),
        "succeeded": 0,
        "failed": 0,
        "partially_failed": 0,
        "total_cost": 0.0,
    }

    # Process documents in batches of 10
    for doc_batch in batched(documents, size=batch_size):
        # Parallel processing within batch
        tasks = [
            ingest_document(doc.path, source_id, doc.type)
            for doc in doc_batch
        ]

        batch_results = await asyncio.gather(*tasks, return_exceptions=True)

        for doc, result in zip(doc_batch, batch_results):
            if isinstance(result, Exception):
                logger.error(f"Document {doc.id} failed: {result}")
                results["failed"] += 1
            elif result["success"]:
                results["succeeded"] += 1
                results["total_cost"] += result.get("cost_estimate", 0.0)
            else:
                results["partially_failed"] += 1
                results["total_cost"] += result.get("cost_estimate", 0.0)

    # Update source status
    await update_source_status(
        source_id=source_id,
        status="completed" if results["failed"] == 0 else "partially_failed",
        documents_processed=results["succeeded"] + results["partially_failed"],
        documents_failed=results["failed"],
    )

    return results
```

### Atomic Transaction per Document

```python
async def store_document_atomic(
    source_id: str,
    document_type: str,
    title: str,
    metadata: dict,
    chunks: list[Chunk],
    embeddings: list[list[float]],
) -> str:
    """
    Store document and chunks atomically (all-or-nothing).

    Uses PostgreSQL transaction to ensure consistency.
    If any step fails, entire document is rolled back.
    """
    document_id = str(uuid.uuid4())

    async with db_pool.acquire() as conn:
        async with conn.transaction():
            # 1. Insert document metadata
            await conn.execute(
                """
                INSERT INTO documents (id, source_id, document_type, title, metadata, created_at)
                VALUES ($1, $2, $3, $4, $5, NOW())
                """,
                document_id, source_id, document_type, title, json.dumps(metadata)
            )

            # 2. Insert chunks (PostgreSQL)
            for i, chunk in enumerate(chunks):
                # Generate tsvector for full-text search
                await conn.execute(
                    """
                    INSERT INTO chunks (
                        id, document_id, chunk_index, text, token_count,
                        search_vector, created_at
                    )
                    VALUES (
                        $1, $2, $3, $4, $5,
                        to_tsvector('english', $4),
                        NOW()
                    )
                    """,
                    chunk.id, document_id, i, chunk.text, chunk.token_count
                )

            # 3. Upsert vectors to Qdrant (outside transaction)
            # Note: Qdrant operations can't be in PostgreSQL transaction,
            # but we can roll back PostgreSQL if Qdrant fails
            try:
                await qdrant_client.upsert(
                    collection_name="documents",
                    points=[
                        {
                            "id": chunk.id,
                            "vector": embedding,
                            "payload": {
                                "document_id": document_id,
                                "chunk_index": i,
                                "text": chunk.text[:1000],  # Truncate for payload
                            }
                        }
                        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings))
                    ]
                )
            except Exception as e:
                logger.error(f"Qdrant upsert failed: {e}")
                # Rollback PostgreSQL transaction
                raise  # Will rollback entire transaction

            # 4. Update document status
            await conn.execute(
                """
                UPDATE documents
                SET status = 'completed', chunk_count = $2, updated_at = NOW()
                WHERE id = $1
                """,
                document_id, len(chunks)
            )

    # Transaction commits automatically on exit
    logger.info(f"Document {document_id} stored atomically with {len(chunks)} chunks")
    return document_id
```

---

## 5. Caching Strategy

### Embedding Cache Design

**Goal**: Avoid re-embedding identical content (saves cost and time).

**Strategy**: Cache embeddings by MD5(content) hash.

```python
# PostgreSQL table for embedding cache
CREATE TABLE embedding_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_hash TEXT NOT NULL UNIQUE,  -- MD5(text)
    embedding VECTOR(1536) NOT NULL,     -- pgvector for storage
    model_name TEXT NOT NULL DEFAULT 'text-embedding-3-small',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_accessed_at TIMESTAMPTZ DEFAULT NOW(),
    access_count INT DEFAULT 1
);

CREATE INDEX idx_embedding_cache_hash ON embedding_cache(content_hash);
CREATE INDEX idx_embedding_cache_model ON embedding_cache(model_name);
```

### Cache Implementation

```python
import hashlib

async def get_cached_embeddings(chunks: list[Chunk]) -> list[list[float] | None]:
    """
    Check cache for embeddings of chunks.

    Returns:
        List of embeddings (or None if not cached) matching input chunks.
    """
    # Calculate content hashes
    hashes = [
        hashlib.md5(chunk.text.encode('utf-8')).hexdigest()
        for chunk in chunks
    ]

    # Fetch from cache
    async with db_pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT content_hash, embedding
            FROM embedding_cache
            WHERE content_hash = ANY($1::text[])
              AND model_name = $2
            """,
            hashes,
            "text-embedding-3-small"
        )

    # Build hash → embedding map
    cache_map = {row["content_hash"]: row["embedding"] for row in rows}

    # Update access stats
    if cache_map:
        async with db_pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE embedding_cache
                SET last_accessed_at = NOW(), access_count = access_count + 1
                WHERE content_hash = ANY($1::text[])
                """,
                list(cache_map.keys())
            )

    # Return embeddings (None if not cached)
    return [cache_map.get(hash_val) for hash_val in hashes]


async def cache_embedding(content_hash: str, embedding: list[float]):
    """Store embedding in cache for future use."""
    async with db_pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO embedding_cache (content_hash, embedding, model_name)
            VALUES ($1, $2, $3)
            ON CONFLICT (content_hash) DO UPDATE
            SET last_accessed_at = NOW(), access_count = embedding_cache.access_count + 1
            """,
            content_hash,
            embedding,
            "text-embedding-3-small"
        )
```

### Cost Savings Estimate

**Scenario**: Ingesting 10,000 documents with 30% duplicate content across documents.

| Metric | Without Cache | With Cache | Savings |
|--------|---------------|------------|---------|
| **Total Chunks** | 50,000 | 50,000 | - |
| **Unique Chunks** | 50,000 | 35,000 | 30% |
| **API Calls** | 500 (batches of 100) | 350 | 150 fewer |
| **Total Tokens** | 25M tokens | 17.5M tokens | 7.5M tokens |
| **API Cost** | $0.50 | $0.35 | **$0.15 (30% savings)** |
| **Processing Time** | 50 seconds | 35 seconds | 15 seconds faster |

**Cache Hit Rate**: Typical 20-40% for technical documentation, 10-20% for diverse content.

**Cache Eviction**: Optional - remove entries not accessed in 90 days to reduce storage.

---

## 6. Pseudocode Implementation (Complete)

### Full Pipeline with All Gotcha Fixes

```python
from dataclasses import dataclass, field
from typing import List, Dict, Any
import hashlib
import asyncio
import openai
from qdrant_client import QdrantClient
import asyncpg

# ============================================================================
# CRITICAL: Gotcha #1 - OpenAI Quota Exhaustion Handling
# ============================================================================

@dataclass
class EmbeddingBatchResult:
    """Track embedding successes and failures (prevents data corruption)."""
    embeddings: list[list[float]] = field(default_factory=list)
    failed_items: list[dict] = field(default_factory=list)
    success_count: int = 0
    failure_count: int = 0

    def add_success(self, embedding: list[float], text: str):
        self.embeddings.append(embedding)
        self.success_count += 1

    def add_failure(self, text: str, error: Exception):
        self.failed_items.append({
            "text_preview": text[:200],
            "error": str(error),
            "error_type": type(error).__name__,
        })
        self.failure_count += 1


# ============================================================================
# Document Ingestion Pipeline (5 Steps)
# ============================================================================

async def ingest_document_pipeline(
    document_path: str,
    source_id: str,
    document_type: str,
    db_pool: asyncpg.Pool,
    qdrant_client: QdrantClient,
    openai_client: openai.AsyncClient,
) -> dict:
    """
    Complete document ingestion with robust error handling.

    Pipeline:
        1. Parse (Docling)
        2. Chunk (Hybrid semantic)
        3. Embed (OpenAI with quota handling)
        4. Cache (MD5 content hash)
        5. Store (PostgreSQL + Qdrant atomic)

    Returns:
        {
            "success": bool,
            "document_id": str,
            "chunks_processed": int,
            "chunks_failed": int,
            "cost_estimate": float
        }
    """

    # ========================================================================
    # STEP 1: PARSE (Docling)
    # ========================================================================
    try:
        from docling.document_converter import DocumentConverter

        converter = DocumentConverter()
        result = converter.convert(document_path)

        parsed_doc = {
            "title": result.document.name,
            "content": result.document.export_to_markdown(),
            "metadata": result.document.metadata,
        }

        logger.info(f"Parsed document: {parsed_doc['title']}")

    except Exception as e:
        logger.error(f"Parsing failed for {document_path}: {e}")
        await update_document_status(source_id, "failed", f"Parse error: {e}")
        return {
            "success": False,
            "error": f"Parsing failed: {e}",
            "stage": "parse"
        }

    # ========================================================================
    # STEP 2: CHUNK (Hybrid Semantic Chunking)
    # ========================================================================
    chunks = hybrid_chunk_document(
        content=parsed_doc["content"],
        max_tokens=500,
        overlap_tokens=50,
        preserve_tables=True,
        preserve_code_blocks=True
    )

    logger.info(f"Created {len(chunks)} chunks from {parsed_doc['title']}")

    if len(chunks) == 0:
        return {
            "success": False,
            "error": "No chunks created (document too short or parsing failed)",
            "stage": "chunk"
        }

    # ========================================================================
    # STEP 3: EMBED (Batch with Quota Handling)
    # ========================================================================
    embedding_result = await embed_chunks_with_cache(
        chunks=chunks,
        db_pool=db_pool,
        openai_client=openai_client,
    )

    if embedding_result.failure_count > 0:
        logger.warning(
            f"Embedding failures: {embedding_result.failure_count}/{len(chunks)}"
        )

    # If ALL chunks failed, don't proceed
    if embedding_result.success_count == 0:
        return {
            "success": False,
            "error": "All chunks failed to embed",
            "stage": "embed",
            "failures": embedding_result.failed_items
        }

    # ========================================================================
    # STEP 4: STORE (Atomic PostgreSQL + Qdrant)
    # ========================================================================
    try:
        document_id = await store_document_atomic(
            source_id=source_id,
            document_type=document_type,
            title=parsed_doc["title"],
            metadata=parsed_doc["metadata"],
            chunks=chunks[:embedding_result.success_count],
            embeddings=embedding_result.embeddings,
            db_pool=db_pool,
            qdrant_client=qdrant_client,
        )

        logger.info(
            f"Stored document {document_id} with "
            f"{embedding_result.success_count} chunks"
        )

    except Exception as e:
        logger.error(f"Storage failed: {e}")
        return {
            "success": False,
            "error": f"Storage failed: {e}",
            "stage": "store"
        }

    # ========================================================================
    # STEP 5: CALCULATE COST
    # ========================================================================
    total_tokens = sum(chunk.token_count for chunk in chunks[:embedding_result.success_count])
    cost_estimate = (total_tokens / 1000) * 0.00002  # OpenAI pricing

    return {
        "success": embedding_result.failure_count == 0,
        "document_id": document_id,
        "chunks_processed": embedding_result.success_count,
        "chunks_failed": embedding_result.failure_count,
        "failures": embedding_result.failed_items,
        "cost_estimate": cost_estimate
    }


# ============================================================================
# Embedding with Cache and Quota Handling
# ============================================================================

async def embed_chunks_with_cache(
    chunks: list,
    db_pool: asyncpg.Pool,
    openai_client: openai.AsyncClient,
) -> EmbeddingBatchResult:
    """
    Embed chunks with caching and quota exhaustion handling.

    CRITICAL: Implements Gotcha #1 fix - never stores null embeddings.
    """
    result = EmbeddingBatchResult()

    # Process in batches of 100 (OpenAI recommendation)
    for batch in batched(chunks, size=100):
        # Check cache first
        cache_results = await get_cached_embeddings(batch, db_pool)

        uncached_chunks = []
        for chunk, cached_emb in zip(batch, cache_results):
            if cached_emb is not None:
                result.add_success(cached_emb, chunk.text)
            else:
                uncached_chunks.append(chunk)

        # Embed uncached chunks
        if uncached_chunks:
            try:
                response = await openai_client.embeddings.create(
                    model="text-embedding-3-small",
                    input=[chunk.text for chunk in uncached_chunks]
                )

                for chunk, emb_data in zip(uncached_chunks, response.data):
                    embedding = emb_data.embedding
                    result.add_success(embedding, chunk.text)

                    # Cache for future use
                    await cache_embedding(chunk.content_hash, embedding, db_pool)

            except openai.RateLimitError as e:
                if "insufficient_quota" in str(e):
                    # CRITICAL: Stop on quota exhaustion
                    logger.error(
                        f"OpenAI quota exhausted! Processed {result.success_count} chunks. "
                        f"Stopping to prevent data corruption."
                    )

                    # Mark ALL remaining as failed
                    remaining = chunks[result.success_count:]
                    for chunk in remaining:
                        result.add_failure(chunk.text, e)

                    break  # STOP - don't corrupt database
                else:
                    # Regular rate limit - mark batch as failed
                    for chunk in uncached_chunks:
                        result.add_failure(chunk.text, e)

            except Exception as e:
                logger.error(f"Embedding error: {e}")
                for chunk in uncached_chunks:
                    result.add_failure(chunk.text, e)

    # Save failures for retry
    if result.failed_items:
        await save_embedding_failures(result.failed_items, db_pool)

    return result


# ============================================================================
# Helper Functions
# ============================================================================

def batched(iterable, size: int):
    """Batch iterator (Python 3.12+ has itertools.batched)."""
    iterator = iter(iterable)
    while batch := list(itertools.islice(iterator, size)):
        yield batch


def hybrid_chunk_document(
    content: str,
    max_tokens: int = 500,
    overlap_tokens: int = 50,
    preserve_tables: bool = True,
    preserve_code_blocks: bool = True,
) -> list:
    """
    Chunk document with semantic boundaries.

    TODO: Implement using LangChain RecursiveCharacterTextSplitter
    or Docling's built-in chunking with table preservation.
    """
    # Placeholder - actual implementation would use semantic chunking
    pass


async def get_cached_embeddings(chunks: list, db_pool: asyncpg.Pool) -> list:
    """Fetch cached embeddings by content hash."""
    hashes = [chunk.content_hash for chunk in chunks]

    async with db_pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT content_hash, embedding
            FROM embedding_cache
            WHERE content_hash = ANY($1::text[])
            """,
            hashes
        )

    cache_map = {row["content_hash"]: row["embedding"] for row in rows}
    return [cache_map.get(chunk.content_hash) for chunk in chunks]


async def cache_embedding(content_hash: str, embedding: list[float], db_pool: asyncpg.Pool):
    """Store embedding in cache."""
    async with db_pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO embedding_cache (content_hash, embedding)
            VALUES ($1, $2)
            ON CONFLICT (content_hash) DO UPDATE
            SET access_count = embedding_cache.access_count + 1
            """,
            content_hash,
            embedding
        )


async def store_document_atomic(
    source_id: str,
    document_type: str,
    title: str,
    metadata: dict,
    chunks: list,
    embeddings: list[list[float]],
    db_pool: asyncpg.Pool,
    qdrant_client: QdrantClient,
) -> str:
    """Store document atomically (all-or-nothing)."""
    document_id = str(uuid.uuid4())

    async with db_pool.acquire() as conn:
        async with conn.transaction():
            # Insert document
            await conn.execute(
                """
                INSERT INTO documents (id, source_id, document_type, title, metadata)
                VALUES ($1, $2, $3, $4, $5)
                """,
                document_id, source_id, document_type, title, json.dumps(metadata)
            )

            # Insert chunks
            for i, chunk in enumerate(chunks):
                await conn.execute(
                    """
                    INSERT INTO chunks (id, document_id, chunk_index, text, token_count, search_vector)
                    VALUES ($1, $2, $3, $4, $5, to_tsvector('english', $4))
                    """,
                    chunk.id, document_id, i, chunk.text, chunk.token_count
                )

            # Upsert to Qdrant
            await qdrant_client.upsert(
                collection_name="documents",
                points=[
                    {
                        "id": chunk.id,
                        "vector": embedding,
                        "payload": {"document_id": document_id, "chunk_index": i}
                    }
                    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings))
                ]
            )

    return document_id
```

---

## Summary

### Key Takeaways

1. **NEVER store null/zero embeddings** - Use `EmbeddingBatchResult` pattern to track failures
2. **Stop on quota exhaustion** - Don't corrupt data by continuing without embeddings
3. **Cache embeddings by content hash** - Save 20-40% on API costs
4. **Process in batches** - 100 chunks per OpenAI call, 500 vectors per Qdrant upsert
5. **Atomic per document** - All-or-nothing transactions prevent partial failures
6. **Emit progress events** - Real-time visibility into ingestion status
7. **Track failures for retry** - Manual retry queue after quota refill

### Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Docling for parsing** | Best table preservation, handles complex layouts |
| **Hybrid chunking** | Respects semantic boundaries, better search quality |
| **MD5 cache key** | Fast, deterministic, good enough for deduplication |
| **PostgreSQL + Qdrant** | PostgreSQL for metadata/text, Qdrant for vectors |
| **Atomic per document** | Simpler than global transaction, prevents partial corruption |
| **100 chunk batches** | OpenAI recommendation for optimal throughput |

### Anti-Patterns Avoided

- ❌ Storing null/zero embeddings on API failure
- ❌ Continuing ingestion after quota exhaustion
- ❌ Re-embedding identical content
- ❌ Processing all documents in single transaction
- ❌ No progress tracking during long ingestion jobs

---

**Next Section**: MCP Tools Specification (search, manage documents, manage sources, crawl website)
