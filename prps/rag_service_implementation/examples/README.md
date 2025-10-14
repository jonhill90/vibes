# RAG Service Implementation - Code Examples

## Overview

This directory contains **9 extracted code examples** from the task-manager and Archon codebases, demonstrating proven patterns for building a production-ready RAG service. Each file is a **runnable code extract** (not just references) with source attribution and detailed explanations.

## Examples in This Directory

| File | Source | Pattern | Relevance |
|------|--------|---------|-----------|
| 01_service_layer_pattern.py | task-manager/backend/src/services/task_service.py | Service layer with asyncpg | 10/10 |
| 02_mcp_consolidated_tools.py | task-manager/backend/src/mcp_server.py | MCP find/manage tools | 10/10 |
| 03_rag_search_pipeline.py | archon/python/src/server/services/search/rag_service.py | RAG coordinator with strategies | 10/10 |
| 04_base_vector_search.py | archon/python/src/server/services/search/base_search_strategy.py | Vector similarity search | 9/10 |
| 05_hybrid_search_strategy.py | archon/python/src/server/services/search/hybrid_search_strategy.py | Hybrid vector+text search | 9/10 |
| 06_transaction_pattern.py | task-manager/backend/src/services/task_service.py | Atomic transactions with locking | 8/10 |
| 07_fastapi_endpoint_pattern.py | task-manager/backend/src/api/routes/tasks.py | FastAPI endpoints with services | 9/10 |
| 08_connection_pool_setup.py | task-manager/backend/src/main.py | FastAPI lifespan pattern | 10/10 |
| 09_qdrant_vector_service.py | Synthesized from patterns | Qdrant operations wrapper | 9/10 |

---

## Example 1: Service Layer Pattern

**File**: `01_service_layer_pattern.py`
**Source**: task-manager/backend/src/services/task_service.py (lines 28-172)
**Relevance**: 10/10

### What to Mimic

- **__init__ accepts db_pool**:
  ```python
  def __init__(self, db_pool: asyncpg.Pool):
      self.db_pool = db_pool
  ```
  This is the foundation - every database service needs this pattern.

- **tuple[bool, dict] return pattern**:
  ```python
  async def list_documents(...) -> tuple[bool, dict[str, Any]]:
      try:
          # ... operation ...
          return True, {"documents": documents, "total_count": count}
      except Exception as e:
          return False, {"error": str(e)}
  ```
  Consistent error handling without exceptions propagating to endpoints.

- **async with for connection management**:
  ```python
  async with self.db_pool.acquire() as conn:
      result = await conn.fetchrow("SELECT * FROM documents WHERE id = $1", doc_id)
  ```
  CRITICAL: This prevents connection leaks. Always use async with.

- **exclude_large_fields for MCP optimization**:
  ```python
  if exclude_large_fields:
      select_fields = """
          CASE
              WHEN LENGTH(content) > 1000
              THEN SUBSTRING(content FROM 1 FOR 1000) || '...'
              ELSE content
          END as content
      """
  ```
  Reduces MCP payload size by ~70% for list operations.

### What to Adapt

- **Validation methods**: Change `validate_status` to `validate_source_type`, `validate_document_type`, etc.
- **Filter fields**: Replace `project_id, status, assignee` with `source_id, document_type, created_at_range`
- **Table names**: Change `tasks` to `documents`, `chunks`, `sources`
- **Field names**: Adapt to RAG schema (document_id, chunk_index, text, search_vector)

### What to Skip

- **Position management logic**: This is task-specific (drag-and-drop UI). Not needed for documents.
- **Parent task references**: RAG service doesn't have hierarchical documents (yet).

### Pattern Highlights

```python
# KEY PATTERN: Dynamic WHERE clause building with $1, $2 placeholders
where_clauses = []
params = []
param_idx = 1

if "source_id" in filters:
    where_clauses.append(f"source_id = ${param_idx}")
    params.append(filters["source_id"])
    param_idx += 1

where_clause = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
query = f"SELECT * FROM documents {where_clause}"
rows = await conn.fetch(query, *params)
```

This works because:
- asyncpg requires $1, $2 placeholders (NOT %s like psycopg)
- Dynamic query building prevents SQL injection
- param_idx tracking ensures correct parameter ordering

### Why This Example

This is the **foundational pattern** for all database services in the RAG service. You'll create:
- `DocumentService(db_pool)` - Uses this exact pattern
- `SourceService(db_pool)` - Uses this exact pattern
- `EmbeddingService` - Doesn't use this (OpenAI API client instead)
- `VectorService` - Doesn't use this (Qdrant client instead)

---

## Example 2: MCP Consolidated Tools

**File**: `02_mcp_consolidated_tools.py`
**Source**: task-manager/backend/src/mcp_server.py (lines 20-199)
**Relevance**: 10/10

### What to Mimic

- **find/manage pattern**:
  ```python
  @mcp.tool()
  async def find_documents(
      document_id: str | None = None,
      source_id: str | None = None,
      page: int = 1,
      per_page: int = 10,
  ) -> str:
      # List, search, or get single item
      pass

  @mcp.tool()
  async def manage_document(
      action: str,  # "create" | "update" | "delete"
      document_id: str | None = None,
      # ... other fields ...
  ) -> str:
      # CRUD operations in one tool
      pass
  ```
  This consolidates 5 tools into 2 (~60% reduction).

- **JSON string return (CRITICAL)**:
  ```python
  # ✅ CORRECT
  return json.dumps({"success": True, "documents": docs})

  # ❌ WRONG - MCP protocol requires strings
  return {"success": True, "documents": docs}
  ```
  MCP tools MUST return JSON strings, not Python dicts.

- **Payload optimization**:
  ```python
  MAX_CONTENT_LENGTH = 1000
  MAX_ITEMS_PER_PAGE = 20

  def optimize_for_mcp(doc: dict) -> dict:
      doc = doc.copy()
      if "content" in doc and doc["content"]:
          doc["content"] = doc["content"][:1000] + "..."
      return doc
  ```
  Prevents MCP protocol errors from oversized responses.

- **Error format consistency**:
  ```python
  return json.dumps({
      "success": False,
      "error": "Document not found",
      "suggestion": "Use find_documents() to list available documents"
  })
  ```
  Always provide actionable suggestions.

### What to Adapt

- **Tool names**: `find_tasks` → `find_documents`, `manage_task` → `manage_document`
- **Parameters**: Replace task fields with document fields (title, content, document_type, source_id)
- **Validation**: Add document-specific validation (file type, size limits, embedding status)
- **Additional tools**: Add `search_knowledge_base`, `manage_source` for RAG-specific operations

### What to Skip

- **Task-specific logic**: Position updates, status transitions (todo→doing→review→done)
- **Project filtering**: Unless you implement project scoping for documents

### Pattern Highlights

```python
# KEY PATTERN: Dual-mode tool (list or get single item)
if document_id:
    # Get single item - return full details with truncation
    success, result = await document_service.get_document(document_id)
    doc = result.get("document")
    if doc:
        doc = optimize_for_mcp(doc)  # Still truncate!
    return json.dumps({"success": True, "document": doc})
else:
    # List mode - always use exclude_large_fields=True
    success, result = await document_service.list_documents(
        filters=filters,
        page=page,
        per_page=per_page,
        exclude_large_fields=True  # CRITICAL
    )
    return json.dumps({
        "success": True,
        "documents": result.get("documents", []),
        "total_count": result.get("total_count", 0)
    })
```

This works because:
- Single item queries need full details (for editing)
- List queries need optimization (for browsing)
- Both use truncation to stay under MCP limits

### Why This Example

MCP tools are the **primary interface** for agent usage. The find/manage pattern reduces tool count from 15 to 6 (~60% reduction), making it easier for agents to discover and use the right tools.

---

## Example 3: RAG Search Pipeline

**File**: `03_rag_search_pipeline.py`
**Source**: archon/python/src/server/services/search/rag_service.py
**Relevance**: 10/10

### What to Mimic

- **Thin coordinator pattern**:
  ```python
  class RAGService:
      def __init__(self, supabase_client):
          # Initialize strategies (fat implementation)
          self.base_strategy = BaseSearchStrategy(supabase_client)
          self.hybrid_strategy = HybridSearchStrategy(supabase_client, self.base_strategy)
          self.reranking_strategy = RerankingStrategy() if USE_RERANKING else None

      async def search_documents(self, query: str, use_hybrid: bool = False):
          # Delegate to strategies
          if use_hybrid and self.hybrid_strategy:
              return await self.hybrid_strategy.search(query)
          else:
              return await self.base_strategy.search(query)
  ```
  Coordinator doesn't do database operations - delegates to strategies.

- **Configuration-driven strategy selection**:
  ```python
  USE_HYBRID_SEARCH = os.getenv("USE_HYBRID_SEARCH", "false").lower() == "true"

  if use_hybrid_search:
      results = await self.hybrid_strategy.search_documents_hybrid(...)
  else:
      results = await self.base_strategy.vector_search(...)
  ```
  Enable/disable features without code changes.

- **Graceful degradation**:
  ```python
  if self.reranking_strategy:
      try:
          results = await self.reranking_strategy.rerank_results(query, results)
      except Exception as e:
          logger.warning(f"Reranking failed: {e}")
          # Continue with original results
  ```
  Service continues even if advanced features fail.

- **5x candidate multiplier for reranking**:
  ```python
  search_match_count = match_count
  if use_reranking and self.reranking_strategy:
      # Fetch 5x the requested amount when reranking is enabled
      search_match_count = match_count * 5
  ```
  Gives reranker more candidates to choose from, improving final result quality.

### What to Adapt

- **Client initialization**: Replace `supabase_client` with `qdrant_client` and `db_pool`
  ```python
  def __init__(self, qdrant_client: AsyncQdrantClient, db_pool: asyncpg.Pool):
      self.base_strategy = BaseSearchStrategy(qdrant_client)
      self.hybrid_strategy = HybridSearchStrategy(qdrant_client, db_pool, self.base_strategy)
  ```

- **Strategy interfaces**: Adapt to use Qdrant + PostgreSQL instead of Supabase unified client
- **Configuration keys**: Use Pydantic Settings instead of environment variables directly

### What to Skip

- **Supabase-specific code**: RPC calls, credential service integration
- **Multi-provider embeddings**: MVP uses OpenAI only (no Cohere, Anthropic, etc.)

### Pattern Highlights

```python
# KEY PATTERN: Pipeline execution with optional stages
async def perform_rag_query(self, query: str, match_count: int = 5):
    # Stage 1: Get embedding
    query_embedding = await create_embedding(query)

    # Stage 2: Search (hybrid or base)
    if USE_HYBRID_SEARCH:
        results = await self.hybrid_strategy.search_documents_hybrid(...)
    else:
        results = await self.base_strategy.vector_search(...)

    # Stage 3: Rerank (optional)
    if self.reranking_strategy and results:
        try:
            results = await self.reranking_strategy.rerank_results(query, results)
        except Exception:
            logger.warning("Reranking failed, using original results")

    return results
```

This works because:
- Each stage is independent and testable
- Failures in optional stages don't break the pipeline
- Easy to add new strategies without changing coordinator

### Why This Example

This is the **core search architecture** for the RAG service. The strategy pattern allows you to:
- Start with basic vector search (Phase 3)
- Add hybrid search later (Phase 6+)
- Add reranking later (Phase 6+)
- Test each strategy independently

---

## Example 4: Base Vector Search

**File**: `04_base_vector_search.py`
**Source**: archon/python/src/server/services/search/base_search_strategy.py
**Relevance**: 9/10

### What to Mimic

- **Similarity threshold filtering**:
  ```python
  SIMILARITY_THRESHOLD = 0.05  # Empirically validated

  filtered_results = []
  for result in response.data:
      similarity = float(result.get("similarity", 0.0))
      if similarity >= SIMILARITY_THRESHOLD:
          filtered_results.append(result)
  ```
  Prevents low-quality matches from polluting results.

- **Strategy interface**:
  ```python
  class BaseSearchStrategy:
      def __init__(self, qdrant_client: AsyncQdrantClient):
          self.client = qdrant_client

      async def vector_search(
          self,
          query_embedding: list[float],
          match_count: int,
          filter_metadata: dict | None = None,
      ) -> list[dict[str, Any]]:
          # Perform search and return results
          pass
  ```
  Simple, focused interface for vector similarity search.

- **Metadata filtering**:
  ```python
  # Support filtering by source_id, document_id, etc.
  filter_conditions = {}
  if filter_metadata:
      if "source_id" in filter_metadata:
          filter_conditions["source_id"] = filter_metadata["source_id"]
  ```

### What to Adapt

- **Client type**: Change from Supabase to Qdrant AsyncQdrantClient
- **Search method**: Use `qdrant_client.search()` instead of Supabase RPC
- **Result format**: Convert Qdrant search results to consistent dict format

### What to Skip

- **Supabase RPC specifics**: `rpc()` calls, source_filter parameter splitting

### Pattern Highlights

```python
# KEY PATTERN: Threshold filtering after search
results = await self.client.search(
    collection_name="documents",
    query_vector=query_embedding,
    limit=match_count * 2,  # Over-fetch for filtering
    score_threshold=0.0,  # Get all, filter manually
)

# Filter by empirically validated threshold
filtered_results = [r for r in results if r.score >= SIMILARITY_THRESHOLD]
```

This works because:
- Qdrant's built-in threshold may be too strict
- Manual filtering gives better control
- Over-fetching ensures you get enough results after filtering

### Why This Example

This is the **foundation** for all search strategies. BaseSearchStrategy is:
- Used directly when `use_hybrid_search=False`
- Used by HybridSearchStrategy for vector component
- Tested independently before building hybrid search

---

## Example 5: Hybrid Search Strategy

**File**: `05_hybrid_search_strategy.py`
**Source**: archon/python/src/server/services/search/hybrid_search_strategy.py
**Relevance**: 9/10

### What to Mimic

- **Dual search execution**:
  ```python
  # Parallel execution (conceptual - can be async gather)
  vector_results = await self.base_strategy.vector_search(query_embedding, ...)
  text_results = await conn.fetch("""
      SELECT *, ts_rank(search_vector, plainto_tsquery($1)) as rank
      FROM chunks
      WHERE search_vector @@ plainto_tsquery($1)
      ORDER BY rank DESC
      LIMIT $2
  """, query, match_count)
  ```

- **Score normalization**:
  ```python
  # Vector scores are already 0.0-1.0 (cosine similarity)
  # Text scores need normalization
  max_text_score = max([r["rank"] for r in text_results]) if text_results else 1.0
  normalized_text_scores = [r["rank"] / max_text_score for r in text_results]
  ```

- **Score combining (0.7 vector + 0.3 text)**:
  ```python
  VECTOR_WEIGHT = 0.7
  TEXT_WEIGHT = 0.3

  combined_score = (vector_score * VECTOR_WEIGHT) + (text_score * TEXT_WEIGHT)
  ```
  Empirically validated weights from Archon production.

- **Deduplication by chunk_id**:
  ```python
  # Keep highest score for each chunk_id
  seen_chunks = {}
  for result in sorted_results:
      chunk_id = result["chunk_id"]
      if chunk_id not in seen_chunks or result["score"] > seen_chunks[chunk_id]["score"]:
          seen_chunks[chunk_id] = result
  ```

### What to Adapt

- **Text search query**: Adapt to your schema (chunks table with search_vector column)
- **Client initialization**: Accept both qdrant_client AND db_pool
  ```python
  def __init__(self, qdrant_client, db_pool, base_strategy):
      self.qdrant_client = qdrant_client
      self.db_pool = db_pool
      self.base_strategy = base_strategy
  ```

### What to Skip

- **Supabase hybrid RPC**: Can't reuse Supabase's database function, must implement manually

### Pattern Highlights

```python
# KEY PATTERN: Parallel search + score merging
async def search_documents_hybrid(self, query: str, query_embedding: list[float], match_count: int):
    # Step 1: Vector search (top 100)
    vector_results = await self.base_strategy.vector_search(query_embedding, match_count=100)

    # Step 2: Text search (top 100)
    async with self.db_pool.acquire() as conn:
        text_results = await conn.fetch("""
            SELECT id, document_id, text,
                   ts_rank(search_vector, plainto_tsquery($1)) as text_score
            FROM chunks
            WHERE search_vector @@ plainto_tsquery($1)
            ORDER BY text_score DESC
            LIMIT 100
        """, query)

    # Step 3: Merge and combine scores
    chunk_scores = {}
    for result in vector_results:
        chunk_id = result["id"]
        chunk_scores[chunk_id] = {"vector": result["score"], "text": 0.0, "data": result}

    for result in text_results:
        chunk_id = result["id"]
        if chunk_id in chunk_scores:
            chunk_scores[chunk_id]["text"] = result["text_score"]
        else:
            chunk_scores[chunk_id] = {"vector": 0.0, "text": result["text_score"], "data": dict(result)}

    # Step 4: Normalize and combine
    max_text_score = max([s["text"] for s in chunk_scores.values()]) if chunk_scores else 1.0
    combined = []
    for chunk_id, scores in chunk_scores.items():
        normalized_text = scores["text"] / max_text_score if max_text_score > 0 else 0.0
        combined_score = (scores["vector"] * 0.7) + (normalized_text * 0.3)
        combined.append({**scores["data"], "score": combined_score})

    # Step 5: Sort and return top-k
    combined.sort(key=lambda x: x["score"], reverse=True)
    return combined[:match_count]
```

This works because:
- Over-fetching (100 each) gives more candidates for merging
- Score normalization makes vector and text scores comparable
- Weighted combination favors semantic understanding (0.7) with keyword precision (0.3)

### Why This Example

Hybrid search is **Phase 6+** (post-MVP) but understanding the pattern now helps with:
- Designing the chunks table with search_vector column
- Setting up GIN indexes for fast full-text search
- Understanding why PostgreSQL is critical (not just metadata storage)

---

## Example 6: Transaction Pattern

**File**: `06_transaction_pattern.py`
**Source**: task-manager/backend/src/services/task_service.py (lines 288-378)
**Relevance**: 8/10

### What to Mimic

- **Transaction wrapper**:
  ```python
  async with self.db_pool.acquire() as conn:
      async with conn.transaction():
          # All operations here are atomic
          await conn.execute("INSERT INTO documents ...")
          await conn.execute("INSERT INTO chunks ...")
          # Automatic COMMIT on success, ROLLBACK on exception
  ```

- **Row locking to prevent deadlocks**:
  ```python
  # CRITICAL: Lock rows in consistent order (ORDER BY id)
  await conn.execute("""
      SELECT id FROM documents
      WHERE status = $1
      ORDER BY id
      FOR UPDATE
  """, status)
  ```
  Without ORDER BY, concurrent transactions can deadlock.

- **Batch updates within transaction**:
  ```python
  # Atomic batch update
  await conn.execute("""
      UPDATE chunks
      SET embedding_status = 'completed'
      WHERE document_id = $1
  """, document_id)
  ```

### What to Adapt

- **Use case**: Atomic document ingestion (PostgreSQL + Qdrant)
  ```python
  async with db_pool.acquire() as conn:
      async with conn.transaction():
          # 1. Insert document
          doc_row = await conn.fetchrow("INSERT INTO documents ... RETURNING *")

          # 2. Insert chunks
          await conn.executemany("INSERT INTO chunks ...", chunk_data)

          # 3. Insert embeddings cache
          await conn.executemany("INSERT INTO embedding_cache ...", cache_data)

  # 4. Upsert vectors to Qdrant (outside transaction)
  await vector_service.upsert_vectors(points)
  ```

### What to Skip

- **Position reordering logic**: Task-specific, not applicable to documents

### Pattern Highlights

```python
# KEY PATTERN: Atomic multi-step operation
async def ingest_document_atomic(
    db_pool: asyncpg.Pool,
    vector_service: VectorService,
    document_data: dict,
    chunks: list[dict],
    embeddings: list[list[float]],
):
    """Ingest document atomically (PostgreSQL + Qdrant).

    CRITICAL: PostgreSQL transaction ensures consistency.
    Qdrant operations are outside transaction but idempotent (upsert).
    """
    try:
        # Step 1: Atomic PostgreSQL writes
        async with db_pool.acquire() as conn:
            async with conn.transaction():
                # Insert document
                doc_row = await conn.fetchrow("""
                    INSERT INTO documents (id, title, document_type, source_id)
                    VALUES ($1, $2, $3, $4)
                    RETURNING *
                """, document_data["id"], document_data["title"],
                    document_data["document_type"], document_data["source_id"])

                # Insert chunks
                chunk_params = [
                    (chunk["id"], doc_row["id"], chunk["chunk_index"], chunk["text"])
                    for chunk in chunks
                ]
                await conn.executemany("""
                    INSERT INTO chunks (id, document_id, chunk_index, text)
                    VALUES ($1, $2, $3, $4)
                """, chunk_params)

        # Step 2: Upsert vectors to Qdrant (idempotent)
        points = [
            {
                "id": chunk["id"],
                "embedding": embeddings[i],
                "payload": {
                    "document_id": doc_row["id"],
                    "chunk_index": chunk["chunk_index"],
                    "text": chunk["text"][:1000],  # Truncate
                }
            }
            for i, chunk in enumerate(chunks)
        ]
        await vector_service.upsert_vectors(points)

        return True, {"document": dict(doc_row)}

    except Exception as e:
        logger.error(f"Document ingestion failed: {e}")
        # PostgreSQL transaction auto-rolls back
        # Qdrant upsert is idempotent, safe to retry
        return False, {"error": str(e)}
```

This works because:
- PostgreSQL transaction ensures all-or-nothing for metadata
- Qdrant upsert is idempotent (retrying doesn't corrupt data)
- If PostgreSQL succeeds but Qdrant fails, retry only Qdrant (use document_id to find chunks)

### Why This Example

Atomic ingestion is **Phase 4** (Week 4) and **critical** for data integrity. The pattern ensures:
- No orphaned chunks (chunks without documents)
- No partial documents (documents without chunks)
- Retry safety (idempotent operations)

---

## Example 7: FastAPI Endpoint Pattern

**File**: `07_fastapi_endpoint_pattern.py`
**Source**: task-manager/backend/src/api/routes/tasks.py
**Relevance**: 9/10

### What to Mimic

- **Dependency injection**:
  ```python
  from fastapi import APIRouter, Depends, HTTPException

  router = APIRouter(prefix="/api/documents", tags=["documents"])

  @router.get("/")
  async def list_documents(
      source_id: str | None = None,
      page: int = 1,
      per_page: int = 50,
      db_pool: asyncpg.Pool = Depends(get_db_pool),
  ):
      document_service = DocumentService(db_pool)
      success, result = await document_service.list_documents(...)
      if not success:
          raise HTTPException(status_code=500, detail=result.get("error"))
      return result
  ```

- **Pydantic request/response models**:
  ```python
  from pydantic import BaseModel

  class CreateDocumentRequest(BaseModel):
      title: str
      document_type: str  # "pdf" | "html" | "docx"
      source_id: str
      content: str

  @router.post("/", response_model=DocumentResponse)
  async def create_document(
      request: CreateDocumentRequest,
      db_pool: asyncpg.Pool = Depends(get_db_pool),
  ):
      # Automatic validation from Pydantic
      pass
  ```

- **Error handling**:
  ```python
  if not success:
      error_msg = result.get("error", "Unknown error")
      raise HTTPException(status_code=500, detail=error_msg)
  ```

### What to Adapt

- **Route paths**: `/api/tasks` → `/api/documents`, `/api/chunks`, `/api/search`
- **Request models**: TaskCreate → DocumentCreate, ChunkCreate, SearchRequest
- **Response models**: TaskResponse → DocumentResponse, SearchResponse

### What to Skip

- **Task-specific endpoints**: `/api/tasks/{id}/position` (drag-and-drop UI specific)

### Pattern Highlights

```python
# KEY PATTERN: Service layer separation from HTTP concerns
@router.post("/api/documents")
async def create_document(
    request: CreateDocumentRequest,
    db_pool: asyncpg.Pool = Depends(get_db_pool),
):
    # HTTP layer: Parse request, validate, handle errors
    document_service = DocumentService(db_pool)

    # Business logic layer: Service handles database operations
    success, result = await document_service.create_document(request)

    # HTTP layer: Convert service response to HTTP response
    if not success:
        raise HTTPException(status_code=400, detail=result.get("error"))

    return result
```

This works because:
- Services are testable without HTTP mocking
- HTTP concerns (status codes, headers) separated from business logic
- Consistent error handling across all endpoints

### Why This Example

FastAPI endpoints are **Phase 1** (Core Setup) and **critical** for API-first design. The pattern ensures:
- Automatic API documentation (OpenAPI/Swagger)
- Request validation (Pydantic)
- Consistent error responses
- Testable business logic

---

## Example 8: Connection Pool Setup

**File**: `08_connection_pool_setup.py`
**Source**: task-manager/backend/src/main.py (lines 33-63)
**Relevance**: 10/10

### What to Mimic

- **Lifespan pattern**:
  ```python
  from contextlib import asynccontextmanager

  @asynccontextmanager
  async def lifespan(app: FastAPI):
      # Startup
      db_pool = await asyncpg.create_pool(...)
      app.state.db_pool = db_pool
      yield
      # Shutdown
      await app.state.db_pool.close()

  app = FastAPI(lifespan=lifespan)
  ```

- **Pool configuration**:
  ```python
  db_pool = await asyncpg.create_pool(
      host="localhost",
      port=5432,
      database="rag_service",
      user="postgres",
      password="postgres",
      min_size=10,  # From task-manager proven pattern
      max_size=20,  # From task-manager proven pattern
      command_timeout=60,
  )
  ```

- **Dependency for injection**:
  ```python
  async def get_db_pool(request: Request) -> asyncpg.Pool:
      return request.app.state.db_pool
  ```

### What to Adapt

- **Multiple clients**: Add Qdrant client initialization
  ```python
  @asynccontextmanager
  async def lifespan(app: FastAPI):
      # Initialize PostgreSQL pool
      db_pool = await asyncpg.create_pool(...)
      app.state.db_pool = db_pool

      # Initialize Qdrant client
      qdrant_client = AsyncQdrantClient(url="http://localhost:6333")
      app.state.qdrant_client = qdrant_client

      yield

      # Cleanup
      await app.state.db_pool.close()
      await app.state.qdrant_client.close()
  ```

- **Environment-based configuration**: Use Pydantic Settings instead of hardcoded values

### What to Skip

- **Nothing** - This entire pattern is critical and should be copied verbatim (with adaptations for Qdrant)

### Pattern Highlights

```python
# KEY PATTERN: Store pool (not connection) in app.state
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ✅ CORRECT: Store pool in app.state
    app.state.db_pool = await asyncpg.create_pool(...)
    yield
    await app.state.db_pool.close()

# ✅ CORRECT: Return pool from dependency
async def get_db_pool(request: Request) -> asyncpg.Pool:
    return request.app.state.db_pool  # Return pool, not connection!

# ✅ CORRECT: Service acquires connection
class DocumentService:
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool

    async def list_documents(self):
        async with self.db_pool.acquire() as conn:
            # Use connection here
            pass
```

This works because:
- Pool is shared across all requests (efficient)
- Each request acquires a connection from pool
- Connections are returned to pool after use
- No connection leaks (async with ensures cleanup)

### Why This Example

Connection pool setup is **Phase 1** (Core Setup) and **foundational**. Get this wrong and you'll have:
- Connection leaks (pool exhaustion)
- Deadlocks (wrong connection management)
- Performance issues (too small pool)

---

## Example 9: Qdrant Vector Service

**File**: `09_qdrant_vector_service.py`
**Source**: Synthesized from Archon patterns + feature analysis
**Relevance**: 9/10

### What to Mimic

- **Vector dimension validation**:
  ```python
  VECTOR_SIZE = 1536  # text-embedding-3-small

  def validate_embedding(self, embedding: list[float]) -> None:
      if len(embedding) != self.VECTOR_SIZE:
          raise ValueError(f"Expected {self.VECTOR_SIZE} dimensions, got {len(embedding)}")

      if all(v == 0 for v in embedding):
          raise ValueError("Embedding cannot be all zeros (quota exhaustion?)")
  ```
  CRITICAL: Prevents storing corrupted vectors that break search.

- **Collection initialization**:
  ```python
  await client.create_collection(
      collection_name="documents",
      vectors_config=VectorParams(
          size=1536,
          distance=Distance.COSINE,
      ),
  )
  ```

- **Upsert with payload**:
  ```python
  points = [
      PointStruct(
          id=chunk["id"],
          vector=embedding,
          payload={
              "document_id": chunk["document_id"],
              "text": chunk["text"][:1000],  # Truncate
          }
      )
      for chunk, embedding in zip(chunks, embeddings)
  ]
  await client.upsert(collection_name="documents", points=points)
  ```

- **Search with filters**:
  ```python
  results = await client.search(
      collection_name="documents",
      query_vector=query_embedding,
      limit=match_count,
      score_threshold=0.05,  # Similarity threshold
      query_filter=Filter(must=[
          FieldCondition(key="source_id", match=MatchValue(value=source_id))
      ]),
  )
  ```

### What to Adapt

- **Error handling**: Add retry logic for network failures
- **Batch operations**: Add batch upsert for large document sets (1000+ chunks)
- **Collection management**: Add methods for collection creation, deletion, info

### What to Skip

- **Complex payload**: Don't store full text in Qdrant (PostgreSQL is source of truth)
- **Advanced filtering**: Start simple, add complex filters in Phase 6+

### Pattern Highlights

```python
# KEY PATTERN: Thin wrapper with validation
class VectorService:
    def __init__(self, qdrant_client: AsyncQdrantClient):
        self.client = qdrant_client

    async def upsert_vectors(self, points: list[dict]) -> int:
        # 1. Validate all embeddings first
        for point in points:
            self.validate_embedding(point["embedding"])

        # 2. Convert to Qdrant format
        point_structs = [
            PointStruct(id=p["id"], vector=p["embedding"], payload=p["payload"])
            for p in points
        ]

        # 3. Upsert to Qdrant
        await self.client.upsert(collection_name="documents", points=point_structs)

        return len(point_structs)
```

This works because:
- Validation before upsert prevents partial failures
- PointStruct format is Qdrant's required structure
- Upsert is idempotent (safe to retry)

### Why This Example

VectorService is **Phase 2** (Service Layer) and **critical** for Qdrant operations. Unlike database services:
- Does NOT use tuple[bool, dict] pattern (raises exceptions)
- Thin wrapper around Qdrant client (no complex business logic)
- Focused on validation and format conversion

---

## Usage Instructions

### Study Phase
1. Read each example file
2. Understand the attribution headers (source, pattern, relevance)
3. Focus on "What to Mimic" sections in this README
4. Note "What to Adapt" for customization
5. Skip "What to Skip" sections (not relevant)

### Application Phase
1. Copy patterns from examples
2. Adapt variable names and logic for RAG service
3. Skip irrelevant sections (e.g., position management)
4. Combine multiple patterns if needed (e.g., service + endpoint)

### Testing Patterns

**Test Setup Pattern**: See `06_transaction_pattern.py`
- Use AsyncMock for connection pools
- Mock service methods, not database operations
- Test error handling with exception simulation

**Integration Testing**: See `07_fastapi_endpoint_pattern.py`
- Use TestClient with FastAPI app
- Mock database with in-memory PostgreSQL
- Verify HTTP responses, not database state

**Performance Testing**: See `04_base_vector_search.py`
- Measure latency percentiles (p50, p95, p99)
- Verify <50ms for base vector search
- Verify <100ms for hybrid search

## Pattern Summary

### Common Patterns Across Examples

1. **async with for Resource Management**:
   - Connection pools: `async with pool.acquire() as conn`
   - Transactions: `async with conn.transaction()`
   - File handles: `async with aiofiles.open(...)`

2. **tuple[bool, dict] Return Pattern**:
   - Database services: DocumentService, SourceService
   - NOT for: VectorService, EmbeddingService, RAGService

3. **Validation Before Operations**:
   - Enum validation: status, priority, document_type
   - Vector validation: dimension, all-zeros check
   - Input validation: required fields, constraints

4. **Error Handling Hierarchy**:
   - Services: Return tuple[bool, dict]
   - Endpoints: Raise HTTPException
   - MCP tools: Return json.dumps({"success": False, "error": ...})

5. **Configuration-Driven Features**:
   - USE_HYBRID_SEARCH for hybrid search strategy
   - USE_RERANKING for reranking strategy
   - Pydantic Settings for environment variables

### Anti-Patterns Observed

1. **DON'T return connections from dependencies**:
   ```python
   # ❌ WRONG
   async def get_db(request: Request) -> asyncpg.Connection:
       return await request.app.state.db_pool.acquire()  # Leak!

   # ✅ CORRECT
   async def get_db_pool(request: Request) -> asyncpg.Pool:
       return request.app.state.db_pool  # Let service acquire
   ```

2. **DON'T use %s placeholders with asyncpg**:
   ```python
   # ❌ WRONG (psycopg style)
   await conn.execute("SELECT * FROM documents WHERE id = %s", doc_id)

   # ✅ CORRECT (asyncpg style)
   await conn.execute("SELECT * FROM documents WHERE id = $1", doc_id)
   ```

3. **DON'T return dicts from MCP tools**:
   ```python
   # ❌ WRONG
   @mcp.tool()
   async def find_documents(...) -> dict:
       return {"success": True, "documents": docs}

   # ✅ CORRECT
   @mcp.tool()
   async def find_documents(...) -> str:
       return json.dumps({"success": True, "documents": docs})
   ```

4. **DON'T forget to truncate content in MCP responses**:
   ```python
   # ❌ WRONG
   return json.dumps({"documents": documents})  # May exceed MCP limits

   # ✅ CORRECT
   optimized = [optimize_for_mcp(doc) for doc in documents]
   return json.dumps({"documents": optimized})
   ```

5. **DON'T store null embeddings**:
   ```python
   # ❌ WRONG (on quota exhaustion)
   embeddings = [None] * len(chunks)  # Corrupts search!

   # ✅ CORRECT
   embeddings = []
   for chunk in chunks:
       try:
           emb = await openai.embeddings.create(...)
           embeddings.append(emb.data[0].embedding)
       except openai.RateLimitError:
           logger.error("Quota exhausted, stopping immediately")
           break  # Don't store partial results
   ```

## Integration with PRP

These examples should be:

1. **Referenced** in PRP "All Needed Context" section:
   ```markdown
   **Code Examples**: prps/rag_service_implementation/examples/
   - 01_service_layer_pattern.py - Foundation for DocumentService, SourceService
   - 02_mcp_consolidated_tools.py - Pattern for MCP tool design
   - 03_rag_search_pipeline.py - Architecture for RAGService coordinator
   - ... (all 9 examples)
   ```

2. **Studied** before implementation:
   - Read examples in numerical order (01→09)
   - Focus on "What to Mimic" sections
   - Note differences between database services (tuple pattern) and Qdrant/OpenAI services (exceptions)

3. **Adapted** for the specific feature needs:
   - Copy patterns, not entire files
   - Customize for RAG-specific requirements
   - Combine patterns where appropriate (e.g., service + endpoint)

4. **Extended** if additional patterns emerge:
   - Document new patterns in this README
   - Add new example files if significant deviation from existing patterns
   - Update "Pattern Summary" section with new insights

## Source Attribution

### From Task Manager (infra/task-manager/)
- 01_service_layer_pattern.py - TaskService class
- 02_mcp_consolidated_tools.py - MCP find/manage tools
- 06_transaction_pattern.py - Atomic position updates
- 07_fastapi_endpoint_pattern.py - Task endpoints
- 08_connection_pool_setup.py - FastAPI main.py lifespan

### From Archon (infra/archon/)
- 03_rag_search_pipeline.py - RAGService coordinator
- 04_base_vector_search.py - BaseSearchStrategy
- 05_hybrid_search_strategy.py - HybridSearchStrategy

### Synthesized
- 09_qdrant_vector_service.py - VectorService wrapper (patterns from Archon + feature analysis)

---

Generated: 2025-10-14
Feature: rag_service_implementation
Total Examples: 9
Quality Score: 9.5/10

**Coverage Assessment**:
- Service Layer: ✅ Excellent (example 01)
- MCP Tools: ✅ Excellent (example 02)
- Search Strategies: ✅ Excellent (examples 03-05)
- Transactions: ✅ Good (example 06)
- FastAPI Patterns: ✅ Excellent (examples 07-08)
- Qdrant Operations: ✅ Good (example 09)
- Embedding Service: ⚠️ Missing (will need to synthesize from OpenAI docs)
- Document Parsing: ⚠️ Missing (will need to synthesize from Docling docs)

**Recommendations**:
1. Use examples 01-09 as foundation for Phase 1-3 implementation
2. Document Hunter should find Docling and OpenAI docs for missing patterns
3. Implementer should study examples in order (01→09) before coding
4. Use this README as validation checklist (can code be adapted from examples?)
