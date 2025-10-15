# Codebase Patterns: rag_service_completion

## Overview

This document catalogs proven implementation patterns from the local RAG Service codebase and task-manager MCP server for completing the RAG service. Focus areas include FastMCP HTTP transport setup, OpenAI AsyncClient initialization, hybrid search implementation, connection pool management, and error handling for quota exhaustion. These patterns ensure consistency with existing architectural decisions and prevent known gotchas.

---

## Architectural Patterns

### Pattern 1: FastMCP Streamable HTTP Transport

**Source**: `/Users/jon/source/vibes/infra/task-manager/backend/src/mcp_server.py` (lines 36-569)
**Relevance**: 10/10 - **CRITICAL for Task 2 (MCP Server Migration)**

**What it does**: Configures FastMCP server with HTTP transport instead of STDIO, enabling persistent service in Docker containers accessible via HTTP endpoints.

**Key Techniques**:
```python
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server with name only (no host/port for STDIO)
mcp = FastMCP("Task Manager")

# Tool registration using decorator pattern
@mcp.tool()
async def find_tasks(
    query: str | None = None,
    task_id: str | None = None,
    filter_by: str | None = None,
    filter_value: str | None = None,
    page: int = 1,
    per_page: int = 10,
) -> str:
    """Consolidated tool: list + search + get."""
    # CRITICAL: MUST return JSON string, NEVER dict
    return json.dumps({
        "success": True,
        "tasks": optimized_tasks,
        "total_count": total_count
    })

# Main entry point
if __name__ == "__main__":
    mcp.run()  # Defaults to STDIO for task-manager
```

**For HTTP Transport** (from vibesbox pattern):
```python
# Initialize with host/port for HTTP
mcp = FastMCP(
    "RAG Service",
    host="0.0.0.0",
    port=8002  # Use 8002 to avoid conflicts (8000=task-manager, 8001=api)
)

# Run with explicit transport
if __name__ == "__main__":
    mcp.run(transport="streamable-http")
```

**When to use**:
- Migrate RAG Service MCP server from STDIO (broken constructor) to HTTP
- Docker containerized MCP servers that need persistent availability
- Services requiring external network access to MCP tools

**How to adapt for RAG service**:
1. Change server name from "Task Manager" to "RAG Service"
2. Set `host="0.0.0.0"` and `port=8002` (avoid conflicts)
3. Import RAG-specific services (RAGService, DocumentService, SourceService)
4. Replace task-related tools with RAG tools (search_knowledge_base, manage_document, rag_manage_source)
5. Add `transport="streamable-http"` to `mcp.run()` call
6. Update docker-compose.yml to expose port 8002

**Why this pattern**:
- ✅ Proven working in task-manager (production-ready)
- ✅ HTTP transport more robust than STDIO for Docker containers
- ✅ Allows Claude Desktop and other clients to connect via URL
- ✅ Easier debugging (can test with curl/Postman)
- ✅ Avoids STDIO constructor mismatch issues

---

### Pattern 2: AsyncOpenAI Client Initialization

**Source**: Archon knowledge base (c0e629a894699314 - "Initialize LiteLLM Client")
**Relevance**: 10/10 - **CRITICAL for Task 2 (Fix OpenAI Client)**

**What it does**: Properly initializes AsyncOpenAI client with API key validation and optional custom HTTP client, following the pattern from Pydantic AI providers.

**Key Techniques**:
```python
from openai import AsyncOpenAI
import httpx

# Pattern 1: Direct initialization with API key
def __init__(self, api_key: str | None = None, openai_client: AsyncOpenAI | None = None):
    if openai_client is not None:
        self._client = openai_client
        return

    # Get API key from parameter or environment
    api_key = api_key or os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError(
            "Set the `OPENAI_API_KEY` environment variable or "
            "pass it via `api_key=...` parameter"
        )

    # Create client with optional custom HTTP client
    self._client = AsyncOpenAI(api_key=api_key)

# Pattern 2: With custom HTTP client (for rate limiting/monitoring)
http_client = httpx.AsyncClient(timeout=httpx.Timeout(30.0))
self._client = AsyncOpenAI(
    api_key=api_key,
    http_client=http_client
)
```

**Embedding Service Pattern** (from RAG codebase):
```python
# In EmbeddingService.__init__
def __init__(
    self,
    db_pool: asyncpg.Pool,
    openai_client: openai.AsyncOpenAI,  # Pass pre-initialized client
):
    self.db_pool = db_pool
    self.openai_client = openai_client  # Store reference
    self.model_name = settings.OPENAI_EMBEDDING_MODEL

# Usage in embeddings
response = await self.openai_client.embeddings.create(
    model=self.model_name,
    input=text,
)
```

**When to use**:
- EmbeddingService initialization (currently BROKEN - client not instantiated)
- Any service requiring OpenAI API access
- Testing scenarios (pass mock client)

**How to adapt for RAG service**:
1. In `mcp_server.py` initialization, create AsyncOpenAI client:
   ```python
   openai_client = AsyncOpenAI(
       api_key=settings.OPENAI_API_KEY.get_secret_value()
   )
   ```
2. Pass to EmbeddingService constructor:
   ```python
   embedding_service = EmbeddingService(
       db_pool=db_pool,
       openai_client=openai_client  # FIX: Add this parameter
   )
   ```
3. Update EmbeddingService signature to accept `openai_client: AsyncOpenAI`
4. Remove any internal client initialization in EmbeddingService

**Why this pattern**:
- ✅ Explicit dependency injection (testable with mocks)
- ✅ Avoids "NoneType has no attribute 'embeddings'" errors
- ✅ Follows Pydantic AI provider initialization pattern
- ✅ Enables custom HTTP client for monitoring/rate limiting
- ❌ Gotcha prevented: **Client MUST be created before passing to services**

---

### Pattern 3: FastAPI Lifespan Connection Pool Management

**Source**: `/Users/jon/source/vibes/infra/rag-service/backend/src/main.py` (lines 38-133)
**Relevance**: 9/10 - **Essential for preventing connection pool deadlocks**

**What it does**: Manages asyncpg connection pool lifecycle in FastAPI lifespan context, ensuring proper initialization on startup and cleanup on shutdown.

**Key Techniques**:
```python
from contextlib import asynccontextmanager
import asyncpg
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown tasks."""
    # Startup
    logger.info("🚀 Starting RAG Service API...")

    try:
        # CRITICAL: Create connection pool (store POOL, not connections)
        app.state.db_pool = await asyncpg.create_pool(
            settings.DATABASE_URL,
            min_size=settings.DATABASE_POOL_MIN_SIZE,  # 2
            max_size=settings.DATABASE_POOL_MAX_SIZE,  # 10
            command_timeout=60,
        )
        logger.info(
            f"✅ Database pool initialized "
            f"(min_size={settings.DATABASE_POOL_MIN_SIZE}, "
            f"max_size={settings.DATABASE_POOL_MAX_SIZE})"
        )
    except Exception as e:
        logger.error(f"❌ Failed to initialize database pool: {e}")
        raise

    try:
        # Initialize Qdrant client
        app.state.qdrant_client = AsyncQdrantClient(url=settings.QDRANT_URL)
        logger.info(f"✅ Qdrant client initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Qdrant client: {e}")
        await app.state.db_pool.close()  # Cleanup on failure
        raise

    yield  # Application runs here

    # Shutdown
    logger.info("🛑 Shutting down RAG Service API...")

    try:
        await app.state.qdrant_client.close()
        logger.info("✅ Qdrant client closed")
    except Exception as e:
        logger.error(f"❌ Error during Qdrant shutdown: {e}")

    try:
        # CRITICAL: Close pool to release all connections
        await app.state.db_pool.close()
        logger.info("✅ Database pool closed")
    except Exception as e:
        logger.error(f"❌ Error during database shutdown: {e}")

# Create FastAPI app with lifespan
app = FastAPI(
    title="RAG Service API",
    lifespan=lifespan,
)
```

**Dependency Pattern**:
```python
# In api/dependencies.py
from fastapi import Request
import asyncpg

async def get_db_pool(request: Request) -> asyncpg.Pool:
    """Return connection pool (NOT individual connection)."""
    return request.app.state.db_pool

# In service layer
async def create_document(pool: asyncpg.Pool, ...):
    # Services acquire connections as needed
    async with pool.acquire() as conn:
        result = await conn.fetchrow("INSERT INTO documents ...")
    return result
```

**When to use**:
- FastAPI application startup/shutdown (already implemented in main.py)
- Any long-lived resource requiring initialization/cleanup
- Connection pools, HTTP clients, background tasks

**How to adapt for MCP server**:
1. MCP server uses similar pattern but without `@asynccontextmanager` decorator
2. Initialize pool in `initialize_services()` function (see current mcp_server.py)
3. Store in `mcp.app.state` instead of `app.state`
4. Cleanup in `finally` block of `main()` function
5. Return pool from initialize function for cleanup reference

**Why this pattern**:
- ✅ Prevents connection pool leaks (connections properly closed)
- ✅ Graceful degradation (cleanup on initialization failure)
- ✅ Async context management (safe resource handling)
- ✅ Separation of concerns (lifespan separate from request handling)
- ❌ Gotcha prevented: **Always return POOL from dependencies, NEVER connections**

---

### Pattern 4: EmbeddingBatchResult for Quota Exhaustion Handling

**Source**: `/Users/jon/source/vibes/infra/rag-service/backend/src/services/embeddings/embedding_service.py` (lines 130-278)
**Relevance**: 10/10 - **CRITICAL for preventing null embedding corruption**

**What it does**: Implements partial failure handling for batch embedding operations, ensuring quota exhaustion NEVER stores null embeddings that would corrupt vector search.

**Key Techniques**:
```python
from pydantic import BaseModel

# Data model for batch results
class EmbeddingBatchResult(BaseModel):
    """Result of batch embedding with partial failure support."""
    embeddings: list[list[float]]  # Successful embeddings only
    failed_items: list[dict]  # Failed items with reason
    success_count: int
    failure_count: int

    @model_validator(mode='after')
    def validate_counts(self):
        """Ensure counts match lists."""
        if len(self.embeddings) != self.success_count:
            raise ValueError("Embedding count mismatch")
        if len(self.failed_items) != self.failure_count:
            raise ValueError("Failed items count mismatch")
        return self

# Batch embedding with quota protection
async def batch_embed(self, texts: list[str]) -> EmbeddingBatchResult:
    """Batch embed with CRITICAL quota exhaustion handling."""
    embeddings: list[list[float]] = []
    failed_items: list[dict] = []

    # Process in batches of 100
    for batch_start in range(0, len(texts), self.batch_size):
        batch_texts = texts[batch_start:batch_start + self.batch_size]

        try:
            batch_embeddings = await self._generate_batch_embeddings_with_retry(
                batch_texts
            )

            # Add successful embeddings
            for embedding in batch_embeddings:
                embeddings.append(embedding)

        except openai.RateLimitError as e:
            # CRITICAL: Quota exhausted - STOP immediately
            logger.error(
                f"Quota exhausted after {batch_start} items. "
                f"Marking remaining {len(texts) - batch_start} items as failed."
            )

            # Mark ALL remaining items as failed
            for i in range(batch_start, len(texts)):
                failed_items.append({
                    "index": i,
                    "text": texts[i][:100],
                    "reason": "quota_exhausted",
                    "error": str(e),
                })

            # STOP processing - do NOT continue to next batch
            break

        except Exception as e:
            # Other errors - fail current batch, continue to next
            logger.error(f"Batch embedding error: {e}")
            for i in range(batch_start, batch_start + len(batch_texts)):
                failed_items.append({
                    "index": i,
                    "text": texts[i][:100],
                    "reason": "api_error",
                    "error": str(e),
                })

    # Return result with successful + failed counts
    return EmbeddingBatchResult(
        embeddings=embeddings,
        failed_items=failed_items,
        success_count=len(embeddings),
        failure_count=len(failed_items),
    )
```

**Usage Pattern**:
```python
# In IngestionService
result = await embedding_service.batch_embed(chunk_texts)

# Process successful embeddings
for i, embedding in enumerate(result.embeddings):
    await vector_service.upsert(chunk_ids[i], embedding)

# Handle failures (log, retry queue, alert)
if result.failure_count > 0:
    logger.warning(f"Failed to embed {result.failure_count} chunks")
    for failed in result.failed_items:
        if failed["reason"] == "quota_exhausted":
            # Alert: OpenAI quota exhausted
            await send_alert("OpenAI quota exhausted")
        else:
            # Add to retry queue
            await retry_queue.add(failed["index"])
```

**When to use**:
- Batch embedding operations (document ingestion)
- Any external API call with quota/rate limits
- Operations where partial success is acceptable

**How to adapt**:
- Already implemented in EmbeddingService.batch_embed()
- Ensure IngestionService uses this method (not single embed in loop)
- Add retry queue for failed items (post-MVP)

**Why this pattern**:
- ✅ Prevents null embedding corruption (Gotcha #1 from feature-analysis.md)
- ✅ Graceful degradation (partial success better than total failure)
- ✅ Clear error tracking (know exactly what failed and why)
- ✅ Enables retry logic (failed items can be reprocessed)
- ❌ Gotcha prevented: **NEVER store null/zero embeddings on quota exhaustion**

---

### Pattern 5: Hybrid Search with Score Normalization

**Source**: `/Users/jon/source/vibes/infra/rag-service/backend/src/services/search/hybrid_search_strategy.py` (lines 1-581)
**Relevance**: 9/10 - **Key for Task 6 (Hybrid Search Enablement)**

**What it does**: Combines vector similarity search (0.7 weight) with PostgreSQL full-text search (0.3 weight) using parallel execution, score normalization, and deduplication.

**Key Techniques**:
```python
import asyncio
import asyncpg

class HybridSearchStrategy:
    """Combine vector + text search with weighted scoring."""

    def __init__(
        self,
        base_strategy: BaseSearchStrategy,
        db_pool: asyncpg.Pool,
        vector_weight: float = 0.7,
        text_weight: float = 0.3,
        candidate_multiplier: int = 5,
    ):
        """Initialize with empirically validated weights."""
        if abs(vector_weight + text_weight - 1.0) > 0.001:
            raise ValueError("Weights must sum to 1.0")

        self.base_strategy = base_strategy
        self.db_pool = db_pool
        self.vector_weight = vector_weight
        self.text_weight = text_weight
        self.candidate_multiplier = candidate_multiplier

    async def search(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Execute hybrid search with parallel execution."""
        # Step 1: Fetch more candidates for reranking
        candidate_limit = limit * self.candidate_multiplier  # 5x multiplier

        # Step 2: Execute both searches in parallel
        vector_results, text_results = await asyncio.gather(
            self._vector_search(query, candidate_limit, filters),
            self._full_text_search(query, candidate_limit, filters),
            return_exceptions=True,
        )

        # Handle exceptions gracefully
        if isinstance(vector_results, Exception):
            logger.error(f"Vector search failed: {vector_results}")
            vector_results = []
        if isinstance(text_results, Exception):
            logger.error(f"Text search failed: {text_results}")
            text_results = []

        if not vector_results and not text_results:
            raise Exception("Both searches failed")

        # Step 3: Normalize scores to 0-1 range
        normalized_vector = self._normalize_scores(vector_results, "score")
        normalized_text = self._normalize_scores(text_results, "rank")

        # Step 4: Combine with weights
        combined_results = self._combine_scores(
            normalized_vector,
            normalized_text
        )

        # Step 5: Sort by combined score, return top-k
        combined_results.sort(key=lambda x: x["score"], reverse=True)
        return combined_results[:limit]

    async def _full_text_search(
        self,
        query: str,
        limit: int,
        filters: Optional[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Execute PostgreSQL full-text search with ts_rank."""
        # Build WHERE clause with filters
        where_clauses = ["ts_vector @@ plainto_tsquery('english', $1)"]
        params: List[Any] = [query]
        param_idx = 2

        if filters:
            if "document_id" in filters:
                where_clauses.append(f"document_id = ${param_idx}")
                params.append(filters["document_id"])
                param_idx += 1

        where_clause = " AND ".join(where_clauses)

        # CRITICAL: Use $1, $2 placeholders (asyncpg style, NOT %s)
        query_sql = f"""
            SELECT
                id as chunk_id,
                text,
                ts_rank(ts_vector, plainto_tsquery('english', $1)) as rank,
                document_id,
                source_id
            FROM chunks
            WHERE {where_clause}
            ORDER BY rank DESC
            LIMIT ${param_idx}
        """
        params.append(limit)

        # CRITICAL: Always use async with for connection management
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(query_sql, *params)

        # Format results
        results = []
        for row in rows:
            results.append({
                "chunk_id": row["chunk_id"],
                "text": row["text"],
                "rank": row["rank"],  # Will be normalized
                "metadata": {
                    "document_id": row["document_id"],
                    "source_id": row["source_id"],
                },
            })

        return results

    def _normalize_scores(
        self,
        results: List[Dict[str, Any]],
        score_field: str,
    ) -> List[Dict[str, Any]]:
        """Min-max normalization to 0-1 range."""
        if not results:
            return []

        scores = [r[score_field] for r in results]
        min_score = min(scores)
        max_score = max(scores)
        score_range = max_score - min_score

        # Handle edge case: all scores equal
        if score_range == 0:
            for result in results:
                result["normalized_score"] = 1.0
            return results

        # Apply min-max normalization
        for result in results:
            original = result[score_field]
            normalized = (original - min_score) / score_range
            result["normalized_score"] = normalized

        return results

    def _combine_scores(
        self,
        vector_results: List[Dict[str, Any]],
        text_results: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Combine normalized scores with weighted average."""
        combined: Dict[str, Dict[str, Any]] = {}

        # Process vector results
        for result in vector_results:
            chunk_id = result["chunk_id"]
            combined[chunk_id] = {
                "chunk_id": chunk_id,
                "text": result["text"],
                "vector_score": result["normalized_score"],
                "text_score": 0.0,
                "score": result["normalized_score"] * self.vector_weight,
                "match_type": "vector",
                "metadata": result["metadata"],
            }

        # Process text results
        for result in text_results:
            chunk_id = result["chunk_id"]
            text_contribution = result["normalized_score"] * self.text_weight

            if chunk_id in combined:
                # Matched both strategies
                combined[chunk_id]["text_score"] = result["normalized_score"]
                combined[chunk_id]["score"] += text_contribution
                combined[chunk_id]["match_type"] = "both"
            else:
                # Matched only text
                combined[chunk_id] = {
                    "chunk_id": chunk_id,
                    "text": result["text"],
                    "vector_score": 0.0,
                    "text_score": result["normalized_score"],
                    "score": text_contribution,
                    "match_type": "text",
                    "metadata": result["metadata"],
                }

        return list(combined.values())
```

**When to use**:
- Semantic search where recall is critical (find all relevant docs)
- Queries mixing conceptual and keyword-based terms
- Production RAG systems (10-15% accuracy improvement over vector-only)

**How to adapt**:
- Already implemented in HybridSearchStrategy class
- Enable via `USE_HYBRID_SEARCH=true` environment variable
- Validate with regression tests (compare vector vs hybrid accuracy)
- Monitor p95 latency (target <100ms)

**Why this pattern**:
- ✅ Empirically validated weights (0.7 vector, 0.3 text from Archon)
- ✅ Parallel execution reduces latency by ~40%
- ✅ Score normalization prevents bias toward one strategy
- ✅ Deduplication ensures no duplicate results
- ✅ Graceful degradation (works if one search fails)
- ❌ Gotcha prevented: **Always normalize scores before combining (different scales)**

---

## Naming Conventions

### File Naming

**Pattern**: `{service_name}_service.py` for service modules
**Examples from codebase**:
- `embedding_service.py` - Handles OpenAI embedding generation
- `vector_service.py` - Qdrant vector operations
- `document_service.py` - Document CRUD operations
- `source_service.py` - Source management
- `ingestion_service.py` - Document ingestion pipeline
- `rag_service.py` - Search coordination (thin coordinator)

**Pattern**: `{strategy_name}_strategy.py` for strategy implementations
**Examples**:
- `base_search_strategy.py` - Vector-only search
- `hybrid_search_strategy.py` - Vector + full-text combined

**Pattern**: `{model_name}.py` for Pydantic models
**Examples**:
- `search_result.py` - SearchResult, EmbeddingBatchResult
- `task.py` - TaskCreate, TaskUpdate

### Class Naming

**Pattern**: `{Feature}Service` for service classes
**Examples**:
- `EmbeddingService` - Embedding generation with caching
- `VectorService` - Vector database operations
- `DocumentService` - Document CRUD
- `IngestionService` - Document processing pipeline
- `RAGService` - Search coordination

**Pattern**: `{Type}Strategy` for strategy pattern implementations
**Examples**:
- `BaseSearchStrategy` - Vector similarity search
- `HybridSearchStrategy` - Combined vector + text search

### Function Naming

**Pattern**: CRUD operations use standard verbs
**Examples**:
```python
async def create_document(pool, data) -> tuple[bool, dict]
async def get_document(pool, doc_id) -> tuple[bool, dict]
async def update_document(pool, doc_id, data) -> tuple[bool, dict]
async def delete_document(pool, doc_id) -> tuple[bool, dict]
async def list_documents(pool, filters) -> tuple[bool, dict]
```

**Pattern**: Private methods use leading underscore
**Examples**:
```python
async def _get_cached_embedding(self, text) -> Optional[list[float]]
async def _cache_embedding(self, text, embedding) -> None
async def _generate_embedding_with_retry(self, text) -> Optional[list[float]]
```

**Pattern**: Validation methods named `validate_*` or just `validate`
**Examples**:
```python
async def validate(self) -> bool  # Strategy validation
def validate_counts(self) -> Self  # Pydantic model validator
```

---

## File Organization

### Directory Structure

```
infra/rag-service/
├── backend/
│   ├── src/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── health.py
│   │   │   │   ├── documents.py  # TODO: Task 4
│   │   │   │   ├── search.py     # TODO: Task 4
│   │   │   │   └── sources.py    # TODO: Task 4
│   │   │   └── dependencies.py
│   │   ├── config/
│   │   │   ├── settings.py       # Pydantic Settings
│   │   │   └── database.py       # Pool utilities
│   │   ├── models/
│   │   │   └── search_result.py  # Pydantic models
│   │   ├── services/
│   │   │   ├── embeddings/
│   │   │   │   └── embedding_service.py
│   │   │   ├── search/
│   │   │   │   ├── base_search_strategy.py
│   │   │   │   ├── hybrid_search_strategy.py
│   │   │   │   └── rag_service.py
│   │   │   ├── vector_service.py
│   │   │   ├── document_service.py
│   │   │   ├── source_service.py
│   │   │   └── ingestion_service.py
│   │   ├── tools/
│   │   │   ├── search_tools.py   # MCP: search_knowledge_base
│   │   │   ├── document_tools.py # MCP: manage_document
│   │   │   └── source_tools.py   # MCP: rag_manage_source
│   │   ├── main.py               # FastAPI app
│   │   └── mcp_server.py         # MCP server (STDIO→HTTP migration)
│   └── tests/
│       ├── unit/
│       │   ├── test_embedding_service.py
│       │   └── test_rag_service.py
│       ├── integration/
│       │   └── test_search_pipeline.py
│       └── mcp/
│           └── test_mcp_tools.py  # TODO: Task 8
├── frontend/                      # TODO: Task 5
│   ├── src/
│   │   ├── components/
│   │   │   ├── DocumentUpload.tsx
│   │   │   ├── SearchInterface.tsx
│   │   │   └── SourceManagement.tsx
│   │   └── api/
│   │       └── client.ts         # REST API client
│   └── package.json
└── docker-compose.yml             # Service orchestration
```

**Justification**:
- Separation of concerns (API routes, services, models, tools)
- Strategy pattern isolated in `services/search/` directory
- MCP tools separate from REST API routes
- Tests mirror source structure (unit/integration/mcp)
- Frontend as separate concern (React app)

---

## Common Utilities to Leverage

### 1. Database Pool Management

**Location**: `backend/src/config/database.py`
**Purpose**: asyncpg pool initialization and lifecycle management
**Usage Example**:
```python
from src.config.database import create_db_pool, close_db_pool

# In lifespan startup
app.state.db_pool = await create_db_pool()

# In lifespan shutdown
await close_db_pool(app.state.db_pool)
```

**Key Functions**:
- `create_db_pool()` - Initialize pool with settings
- `close_db_pool(pool)` - Graceful shutdown
- `check_db_connection(pool)` - Health check

### 2. Service Layer Pattern (tuple[bool, dict] returns)

**Location**: `backend/src/services/*_service.py`
**Purpose**: Consistent error handling across CRUD services
**Usage Example**:
```python
# Service method returns tuple
success, result = await document_service.create_document(data)

if not success:
    # Handle error
    return json.dumps({
        "success": False,
        "error": result.get("error"),
        "suggestion": result.get("suggestion")
    })

# Process successful result
document = result.get("document")
return json.dumps({"success": True, "document": document})
```

**Pattern Benefits**:
- Consistent error handling
- No exception-based flow control
- Clear success/failure distinction
- Suggestion messages for errors

### 3. MCP Tool Response Optimization

**Location**: `infra/task-manager/backend/src/mcp_server.py` (lines 44-79)
**Purpose**: Truncate large text fields to prevent context exhaustion
**Usage Example**:
```python
MAX_DESCRIPTION_LENGTH = 1000

def truncate_text(text: str | None, max_length: int = MAX_DESCRIPTION_LENGTH) -> str | None:
    """Truncate text to max length with ellipsis."""
    if text and len(text) > max_length:
        return text[:max_length - 3] + "..."
    return text

def optimize_for_mcp(item: dict) -> dict:
    """Optimize item for MCP response."""
    item = item.copy()
    if "description" in item:
        item["description"] = truncate_text(item["description"])
    return item
```

**Apply to RAG Service**:
- Truncate document text to 1000 chars for MCP responses
- Limit search results to 20 items max
- Keep full text for REST API endpoints

### 4. Exponential Backoff with Jitter

**Location**: `backend/src/services/embeddings/embedding_service.py` (lines 354-421)
**Purpose**: Rate limit handling for OpenAI API
**Usage Example**:
```python
async def _generate_with_retry(self, text: str, max_retries: int = 3):
    """Generate with exponential backoff on rate limit."""
    for attempt in range(max_retries):
        try:
            return await self.openai_client.embeddings.create(...)

        except openai.RateLimitError as e:
            if attempt < max_retries - 1:
                # Exponential backoff: 2^attempt + jitter
                delay = (2 ** attempt) + random.uniform(0, 1)
                logger.warning(f"Rate limit hit. Retrying in {delay:.2f}s...")
                await asyncio.sleep(delay)
            else:
                logger.error("Rate limit exceeded after retries")
                raise  # Trigger quota exhaustion handling
```

**Apply to**:
- All OpenAI API calls (embeddings)
- Future Crawl4AI rate limiting (Task 3)
- Any external API with rate limits

### 5. Consolidated MCP Tool Pattern

**Location**: `infra/task-manager/backend/src/mcp_server.py` (find_tasks, manage_task)
**Purpose**: Single tool for multiple CRUD operations
**Usage Example**:
```python
@mcp.tool()
async def manage_document(
    action: str,
    document_id: str | None = None,
    title: str | None = None,
    content: str | None = None,
) -> str:
    """Consolidated document management: create/update/delete/get."""
    if action == "create":
        success, result = await document_service.create_document(...)
        return json.dumps({"success": success, **result})

    elif action == "update":
        success, result = await document_service.update_document(...)
        return json.dumps({"success": success, **result})

    elif action == "delete":
        success, result = await document_service.delete_document(...)
        return json.dumps({"success": success, **result})

    elif action == "get":
        success, result = await document_service.get_document(...)
        return json.dumps({"success": success, **result})

    else:
        return json.dumps({
            "success": False,
            "error": f"Unknown action: {action}",
            "suggestion": "Use 'create', 'update', 'delete', or 'get'"
        })
```

**Benefits**:
- Reduces tool count (1 tool instead of 4)
- Consistent interface across operations
- Easier for AI assistants to discover and use

---

## Testing Patterns

### Unit Test Structure

**Pattern**: Mock external dependencies, test service logic in isolation
**Example**: `tests/unit/test_embedding_service.py`

```python
import pytest
from unittest.mock import AsyncMock, MagicMock
import openai

@pytest.fixture
async def mock_db_pool():
    """Mock asyncpg pool."""
    pool = AsyncMock()
    conn = AsyncMock()
    pool.acquire.return_value.__aenter__.return_value = conn
    conn.fetchrow.return_value = None  # Cache miss
    conn.execute.return_value = None
    return pool

@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client."""
    client = AsyncMock()
    client.embeddings.create.return_value = MagicMock(
        data=[MagicMock(embedding=[0.1] * 1536)]
    )
    return client

@pytest.mark.asyncio
async def test_embed_text_success(mock_db_pool, mock_openai_client):
    """Test successful embedding generation."""
    service = EmbeddingService(
        db_pool=mock_db_pool,
        openai_client=mock_openai_client,
    )

    embedding = await service.embed_text("hello world")

    assert embedding is not None
    assert len(embedding) == 1536
    mock_openai_client.embeddings.create.assert_called_once()

@pytest.mark.asyncio
async def test_batch_embed_quota_exhaustion(mock_db_pool, mock_openai_client):
    """Test quota exhaustion handling."""
    # Mock quota exhaustion on second batch
    mock_openai_client.embeddings.create.side_effect = [
        MagicMock(data=[MagicMock(embedding=[0.1] * 1536)] * 100),  # First batch
        openai.RateLimitError("Quota exceeded"),  # Second batch
    ]

    service = EmbeddingService(db_pool=mock_db_pool, openai_client=mock_openai_client)

    # 150 texts - should process 100, fail 50
    texts = [f"text {i}" for i in range(150)]
    result = await service.batch_embed(texts)

    assert result.success_count == 100
    assert result.failure_count == 50
    assert all(f["reason"] == "quota_exhausted" for f in result.failed_items)
```

**Key Techniques**:
- `AsyncMock` for async methods
- `pytest.mark.asyncio` for async tests
- Mock external dependencies (DB, OpenAI, Qdrant)
- Test both success and failure paths
- Verify quota exhaustion stops processing

### Integration Test Structure

**Pattern**: Use real database (test instance), test end-to-end flows
**Example**: `tests/integration/test_search_pipeline.py`

```python
import pytest
import asyncpg
from qdrant_client import AsyncQdrantClient

@pytest.fixture(scope="module")
async def test_db_pool():
    """Create real database pool for integration tests."""
    pool = await asyncpg.create_pool(
        os.getenv("TEST_DATABASE_URL"),
        min_size=1,
        max_size=5,
    )
    yield pool
    await pool.close()

@pytest.fixture(scope="module")
async def test_qdrant_client():
    """Create real Qdrant client."""
    client = AsyncQdrantClient(url=os.getenv("TEST_QDRANT_URL"))
    yield client
    await client.close()

@pytest.mark.asyncio
async def test_hybrid_search_pipeline(test_db_pool, test_qdrant_client):
    """Test full hybrid search pipeline end-to-end."""
    # Initialize services with real dependencies
    vector_service = VectorService(test_qdrant_client, "test_collection")
    embedding_service = EmbeddingService(test_db_pool, real_openai_client)

    base_strategy = BaseSearchStrategy(vector_service, embedding_service, test_db_pool)
    hybrid_strategy = HybridSearchStrategy(base_strategy, test_db_pool)

    # Execute search
    results = await hybrid_strategy.search(
        query="machine learning",
        limit=10,
    )

    # Validate results
    assert len(results) <= 10
    assert all("score" in r for r in results)
    assert all("vector_score" in r for r in results)
    assert all("text_score" in r for r in results)
    assert all(0.0 <= r["score"] <= 1.0 for r in results)

    # Verify results sorted by score descending
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True)
```

**Key Techniques**:
- Use test database (separate from prod)
- Real external services (Qdrant, OpenAI with test key)
- Module-scoped fixtures (reuse connections)
- Validate end-to-end behavior
- Test realistic scenarios

### MCP Test Pattern

**Pattern**: Test JSON string returns and tool behavior
**Example**: `tests/mcp/test_search_tools.py`

```python
import pytest
import json

@pytest.mark.asyncio
async def test_search_knowledge_base_returns_json_string():
    """Test MCP tool returns JSON string (not dict)."""
    from src.tools.search_tools import search_knowledge_base

    result = await search_knowledge_base(
        query="test query",
        limit=5,
    )

    # CRITICAL: Must be JSON string
    assert isinstance(result, str)

    # Parse to validate structure
    data = json.loads(result)
    assert "success" in data
    assert "results" in data
    assert isinstance(data["results"], list)

@pytest.mark.asyncio
async def test_search_knowledge_base_truncates_output():
    """Test MCP tool truncates large results."""
    result = await search_knowledge_base(
        query="test",
        limit=100,  # Request more than max
    )

    data = json.loads(result)

    # Should be limited to MAX_RESULTS_PER_PAGE (20)
    assert len(data["results"]) <= 20

    # Each result should have truncated text
    for r in data["results"]:
        if "text" in r:
            assert len(r["text"]) <= 1000  # MAX_TEXT_LENGTH
```

**Validation Criteria**:
- ✅ Returns JSON string (not dict)
- ✅ Truncates large fields (<1000 chars)
- ✅ Limits result count (≤20 items)
- ✅ Includes error suggestions
- ✅ Handles empty results gracefully

---

## Anti-Patterns to Avoid

### 1. Returning Dicts from MCP Tools

**What it is**: MCP tools return Python dict objects instead of JSON strings

**Why to avoid**: MCP protocol requires JSON strings - returning dicts causes protocol violations and breaks Claude Desktop integration

**Found in**: Common mistake in initial MCP implementations

**Better approach**:
```python
# ❌ WRONG
@mcp.tool()
async def search(query: str) -> dict:
    return {"success": True, "results": []}

# ✅ CORRECT
@mcp.tool()
async def search(query: str) -> str:
    return json.dumps({"success": True, "results": []})
```

### 2. Storing Null Embeddings on Quota Exhaustion

**What it is**: On OpenAI quota exhaustion, code stores null or zero embeddings in vector database

**Why to avoid**: Null embeddings corrupt vector search (match everything with score 0.0) and are nearly impossible to clean up

**Found in**: Early embedding service implementations before EmbeddingBatchResult pattern

**Better approach**: Use EmbeddingBatchResult pattern (Pattern 4 above) - mark items as failed, NEVER store null embeddings

### 3. Returning Connections from Dependencies

**What it is**: FastAPI dependencies return individual database connections instead of pool

**Why to avoid**: Connections not properly released, leading to pool exhaustion and deadlocks under load

**Found in**: Common mistake in async FastAPI apps

**Better approach**:
```python
# ❌ WRONG
async def get_db(request: Request):
    async with request.app.state.db_pool.acquire() as conn:
        yield conn  # Connection held for entire request

# ✅ CORRECT
async def get_db_pool(request: Request) -> asyncpg.Pool:
    return request.app.state.db_pool  # Return pool, services acquire as needed
```

### 4. Using %s Placeholders with asyncpg

**What it is**: SQL queries use `%s` placeholder style (psycopg2) instead of `$1, $2` (asyncpg)

**Why to avoid**: asyncpg uses PostgreSQL native placeholders - `%s` causes syntax errors

**Found in**: Code migrated from psycopg2/psycopg3

**Better approach**:
```python
# ❌ WRONG
await conn.execute("INSERT INTO docs (title) VALUES (%s)", title)

# ✅ CORRECT
await conn.execute("INSERT INTO docs (title) VALUES ($1)", title)
```

### 5. Missing HNSW Disable During Bulk Upload

**What it is**: Qdrant collection created with default HNSW settings during bulk document ingestion

**Why to avoid**: HNSW indexing during bulk upload is 60-90x slower - makes initial data load impractical

**Found in**: Initial Qdrant integrations

**Better approach**:
```python
# For bulk upload (initial load)
await qdrant_client.create_collection(
    collection_name=name,
    vectors_config=VectorParams(
        size=1536,
        distance=Distance.COSINE,
        hnsw_config=HnswConfigDiff(m=0),  # Disable HNSW
    ),
)

# After bulk upload complete, re-enable HNSW
await qdrant_client.update_collection(
    collection_name=name,
    hnsw_config=HnswConfigDiff(m=16),  # Re-enable with default m=16
)
```

### 6. Sequential Search Execution in Hybrid Mode

**What it is**: Execute vector search, wait for completion, then execute text search

**Why to avoid**: Sequential execution wastes time - hybrid search can be 40% slower than necessary

**Found in**: Initial hybrid search implementations

**Better approach**: Use `asyncio.gather()` for parallel execution (Pattern 5 above)

### 7. Not Normalizing Scores Before Combining

**What it is**: Combine raw vector similarity scores (0.0-1.0) with raw ts_rank scores (0.0-infinity)

**Why to avoid**: Different score scales cause bias toward one strategy - typically text search dominates

**Found in**: Naive hybrid search implementations

**Better approach**: Min-max normalize both score types to 0-1 range before weighted combination (Pattern 5)

### 8. CORS allow_origins=["*"] in Production

**What it is**: Configure CORS middleware to allow all origins

**Why to avoid**: Security vulnerability - allows any website to make requests to your API

**Found in**: Development configurations accidentally deployed to production

**Better approach**:
```python
# ✅ Environment-specific CORS
if ENVIRONMENT == "development":
    origins = ["http://localhost:3000", "http://localhost:5173"]
elif ENVIRONMENT == "production":
    origins = os.getenv("CORS_ORIGINS", "").split(",")
else:
    origins = []  # No origins for unknown environments

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Specific origins only
    allow_credentials=True,
)
```

---

## Implementation Hints from Existing Code

### Similar Features Found

#### 1. **Task Management MCP Server** (infra/task-manager)

**Location**: `infra/task-manager/backend/src/mcp_server.py`
**Similarity**: Both provide MCP tools for CRUD operations with consolidated tool pattern
**Lessons**:
- Consolidated tools (find_*/manage_*) reduce tool count
- JSON string returns are critical (json.dumps everywhere)
- Payload truncation prevents context exhaustion
- Structured errors with suggestions improve UX

**Differences**:
- Task manager uses STDIO transport (works for local tools)
- RAG service needs HTTP transport (accessible from containers)
- Task manager has simpler data (no embeddings/vector search)

#### 2. **Embedding Service with Cache** (already exists)

**Location**: `infra/rag-service/backend/src/services/embeddings/embedding_service.py`
**Similarity**: Complete implementation of OpenAI embedding with quota handling
**Lessons**:
- EmbeddingBatchResult pattern works well (prevents null embeddings)
- Cache hit rate of 20-40% provides significant cost savings
- Exponential backoff with jitter handles rate limits gracefully

**Differences**:
- Current implementation uses STDIO MCP server (broken)
- Need to wire AsyncOpenAI client properly in initialization

#### 3. **Hybrid Search Strategy** (already exists)

**Location**: `infra/rag-service/backend/src/services/search/hybrid_search_strategy.py`
**Similarity**: Full hybrid search implementation with score normalization
**Lessons**:
- Parallel execution with asyncio.gather() saves ~40% latency
- Min-max normalization prevents score bias
- 5x candidate multiplier improves reranking quality
- Empirically validated weights (0.7 vector, 0.3 text)

**Differences**:
- Need to validate with regression tests (vector vs hybrid accuracy)
- Need to monitor p95 latency in production (<100ms target)

---

## Recommendations for PRP

Based on pattern analysis:

1. **Follow FastMCP HTTP Transport Pattern** (Pattern 1) for MCP server migration
   - Use `host="0.0.0.0"`, `port=8002` to avoid conflicts
   - Run with `transport="streamable-http"`
   - Update docker-compose.yml to expose port 8002
   - Update Claude Desktop config with HTTP URL

2. **Fix AsyncOpenAI Client Initialization** (Pattern 2) in EmbeddingService
   - Create client in mcp_server.py initialization
   - Pass to EmbeddingService constructor
   - Update EmbeddingService signature to accept `openai_client` parameter
   - Remove any internal client initialization

3. **Reuse Lifespan Pattern** (Pattern 3) for connection pool management
   - Already implemented in main.py (FastAPI)
   - Adapt for mcp_server.py (initialize in main(), cleanup in finally block)
   - Store pool in mcp.app.state for tool access

4. **Validate EmbeddingBatchResult Usage** (Pattern 4) in IngestionService
   - Ensure IngestionService uses batch_embed() (not single embed in loop)
   - Add proper error handling for failed_items
   - Consider retry queue for failed embeddings (post-MVP)

5. **Test Hybrid Search End-to-End** (Pattern 5)
   - Enable via `USE_HYBRID_SEARCH=true` environment variable
   - Run regression tests comparing vector-only vs hybrid accuracy
   - Monitor p95 latency (target <100ms)
   - Validate score normalization prevents bias

6. **Apply MCP Tool Optimization** (Common Utilities #3)
   - Truncate text fields to 1000 chars in MCP responses
   - Limit search results to 20 items max per response
   - Use full data for REST API endpoints (no truncation)

7. **Avoid Anti-Patterns**
   - NEVER return dict from MCP tools (always json.dumps())
   - NEVER store null embeddings on quota exhaustion
   - NEVER return connections from dependencies (return pool)
   - NEVER use %s placeholders with asyncpg (use $1, $2)
   - NEVER enable HNSW during bulk upload (set m=0, re-enable after)
   - NEVER use allow_origins=["*"] in production

8. **Follow Testing Patterns**
   - Unit tests: Mock external dependencies (DB, OpenAI, Qdrant)
   - Integration tests: Use test instances (real DB/Qdrant, test OpenAI key)
   - MCP tests: Validate JSON string returns, truncation, error handling
   - Target 80%+ coverage with focus on critical paths first

---

## Source References

### From Archon

- **c0e629a894699314**: Pydantic AI documentation - AsyncOpenAI client initialization patterns (Relevance: 9/10)
- **d60a71d62eb201d5**: MCP Protocol documentation - Streamable HTTP transport, tool definitions (Relevance: 8/10)

### From Local Codebase

- `/Users/jon/source/vibes/infra/task-manager/backend/src/mcp_server.py:36-569` - FastMCP HTTP pattern, consolidated tools, JSON string returns
- `/Users/jon/source/vibes/infra/vibesbox/src/mcp_server.py:40-314` - Streamable HTTP transport configuration
- `/Users/jon/source/vibes/infra/rag-service/backend/src/main.py:38-133` - FastAPI lifespan connection pool management
- `/Users/jon/source/vibes/infra/rag-service/backend/src/config/database.py:30-180` - asyncpg pool utilities and patterns
- `/Users/jon/source/vibes/infra/rag-service/backend/src/services/embeddings/embedding_service.py:130-278` - EmbeddingBatchResult quota exhaustion handling
- `/Users/jon/source/vibes/infra/rag-service/backend/src/services/search/hybrid_search_strategy.py:1-581` - Hybrid search with score normalization
- `/Users/jon/source/vibes/infra/rag-service/backend/src/services/search/rag_service.py:1-445` - Thin coordinator pattern for search strategies
- `/Users/jon/source/vibes/infra/rag-service/backend/src/mcp_server.py:63-238` - MCP server service initialization pattern

---

## Next Steps for Assembler

When generating the PRP:

1. **Reference these patterns in "Current Codebase Tree" section**:
   - Show existing service structure (embeddings/, search/, tools/)
   - Highlight files that need modification vs creation
   - Note BROKEN files (mcp_server.py OpenAI client issue)

2. **Include key code snippets in "Implementation Blueprint"**:
   - FastMCP HTTP transport setup (Pattern 1)
   - AsyncOpenAI client initialization (Pattern 2)
   - Lifespan connection pool management (Pattern 3)
   - EmbeddingBatchResult usage (Pattern 4)
   - Hybrid search configuration (Pattern 5)

3. **Add anti-patterns to "Known Gotchas" section**:
   - Never return dict from MCP tools
   - Never store null embeddings
   - Never return connections from dependencies
   - Never use %s placeholders with asyncpg
   - Never enable HNSW during bulk upload
   - Never combine raw scores without normalization

4. **Use file organization for "Desired Codebase Tree"**:
   - Show new REST API routes (documents.py, search.py, sources.py)
   - Show new frontend components (DocumentUpload.tsx, SearchInterface.tsx)
   - Show updated mcp_server.py (HTTP transport)
   - Show test structure (unit/, integration/, mcp/)

5. **Include testing patterns in validation steps**:
   - Unit test examples with AsyncMock
   - Integration test setup with test database
   - MCP test JSON string validation
   - Coverage targets (80%+ overall, 85% services, 75% MCP tools)

---

**Document Status**: Complete
**Total Patterns Documented**: 5 major architectural patterns + 5 utilities + 8 anti-patterns
**Lines of Documentation**: ~1100 lines
**Confidence Level**: High (based on proven local codebase implementations)
**Ready For**: Phase 2B (Documentation Hunter), Phase 2C (Example Curator), Phase 2D (Gotcha Detective)
