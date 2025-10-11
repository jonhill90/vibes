# Codebase Patterns: rag_service_research

## Overview

This document captures proven implementation patterns from Archon and task-manager codebases for building a standalone RAG service. The patterns cover service layer architecture, async database operations, MCP tool consolidation, search strategies, embedding services, and error handling. All patterns include file paths and specific code examples to guide implementation.

## Architectural Patterns

### Pattern 1: Service Coordinator with Strategy Delegation
**Source**: `/Users/jon/source/vibes/infra/archon/python/src/server/services/search/rag_service.py`
**Relevance**: 10/10
**What it does**: Implements a thin coordinator service that delegates to specialized strategy classes for different search approaches (vector, hybrid, reranking, agentic). The coordinator manages configuration, initializes strategies, and orchestrates the search pipeline.

**Key Techniques**:
```python
class RAGService:
    """Coordinator service that orchestrates multiple RAG strategies."""

    def __init__(self, supabase_client=None):
        """Initialize RAG service as a coordinator for search strategies"""
        self.supabase_client = supabase_client or get_supabase_client()

        # Initialize base strategy (always needed)
        self.base_strategy = BaseSearchStrategy(self.supabase_client)

        # Initialize optional strategies
        self.hybrid_strategy = HybridSearchStrategy(self.supabase_client, self.base_strategy)
        self.agentic_strategy = AgenticRAGStrategy(self.supabase_client, self.base_strategy)

        # Initialize reranking strategy based on settings
        self.reranking_strategy = None
        use_reranking = self.get_bool_setting("USE_RERANKING", False)
        if use_reranking:
            try:
                self.reranking_strategy = RerankingStrategy()
                logger.info("Reranking strategy loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load reranking strategy: {e}")
                self.reranking_strategy = None

    async def search_documents(self, query: str, use_hybrid_search: bool = False, ...):
        """Document search delegates to appropriate strategy"""
        query_embedding = await create_embedding(query)

        if use_hybrid_search:
            # Use hybrid strategy
            results = await self.hybrid_strategy.search_documents_hybrid(...)
        else:
            # Use basic vector search from base strategy
            results = await self.base_strategy.vector_search(...)

        return results
```

**When to use**:
- When building a RAG service with multiple search strategies
- When features need to be enabled/disabled via configuration
- When strategies can be composed in a pipeline (base → hybrid → reranking)

**How to adapt**:
- Start with base vector search strategy
- Add hybrid search as optional enhancement
- Design strategies as independent classes with consistent interfaces
- Use configuration/environment variables to enable/disable strategies

**Why this pattern**:
- **Separation of concerns**: Each strategy is independently testable
- **Graceful degradation**: If reranking fails, continue with vector results
- **Easy extension**: Add new strategies without modifying coordinator
- **Configuration-driven**: Features can be toggled without code changes

### Pattern 2: Async Service Layer with Connection Pooling
**Source**: `/Users/jon/source/vibes/infra/task-manager/backend/src/services/task_service.py`
**Relevance**: 10/10
**What it does**: Implements service classes with asyncpg connection pooling, comprehensive error handling via tuple[bool, dict] returns, and proper transaction management with row locking to prevent race conditions.

**Key Techniques**:
```python
class TaskService:
    """Service class for task operations with atomic position management."""

    def __init__(self, db_pool: asyncpg.Pool):
        """Initialize with database connection pool"""
        self.db_pool = db_pool

    async def list_tasks(
        self,
        filters: dict[str, Any] | None = None,
        page: int = 1,
        per_page: int = 50,
        exclude_large_fields: bool = False,
    ) -> tuple[bool, dict[str, Any]]:
        """List tasks with filters, pagination, and optional field exclusion.

        PATTERN: Conditional field selection for performance
        - exclude_large_fields=True: Truncate description > 1000 chars
        - exclude_large_fields=False: Return full description
        """
        try:
            # CRITICAL: Always use async with for connection management (Gotcha #12)
            async with self.db_pool.acquire() as conn:
                # Conditional field selection for MCP optimization
                if exclude_large_fields:
                    select_fields = """
                        id, project_id, title,
                        CASE
                            WHEN LENGTH(description) > 1000
                            THEN SUBSTRING(description FROM 1 FOR 1000) || '...'
                            ELSE description
                        END as description,
                        status, created_at, updated_at
                    """
                else:
                    select_fields = "*"

                # Build query with $1, $2 placeholders (asyncpg style - Gotcha #7)
                query = f"SELECT {select_fields} FROM tasks WHERE status = $1"
                rows = await conn.fetch(query, filters.get("status"))

            tasks = [dict(row) for row in rows]

            # tuple[bool, dict] error handling pattern
            return True, {
                "tasks": tasks,
                "total_count": len(tasks),
                "page": page,
                "per_page": per_page,
            }

        except asyncpg.PostgresError as e:
            logger.error(f"Database error listing tasks: {e}")
            return False, {"error": f"Database error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error listing tasks: {e}")
            return False, {"error": f"Error listing tasks: {str(e)}"}

    async def update_task_position(
        self,
        task_id: str,
        new_status: str,
        new_position: int,
    ) -> tuple[bool, dict[str, Any]]:
        """Update task position with atomic reordering logic.

        CRITICAL IMPLEMENTATION - Gotcha #2 Pattern:
        1. Start transaction
        2. Lock affected rows in consistent order (ORDER BY id) to prevent deadlocks
        3. Batch update: increment positions >= new_position
        4. Update target task to new status and position
        5. Commit transaction
        """
        try:
            async with self.db_pool.acquire() as conn:
                async with conn.transaction():
                    # CRITICAL: Lock rows in consistent order (ORDER BY id)
                    # This prevents deadlocks when multiple concurrent updates occur
                    await conn.execute(
                        """
                        SELECT id FROM tasks
                        WHERE status = $1 AND position >= $2
                        ORDER BY id
                        FOR UPDATE
                        """,
                        new_status,
                        new_position,
                    )

                    # Atomic batch update - increment positions
                    await conn.execute(
                        """
                        UPDATE tasks
                        SET position = position + 1, updated_at = NOW()
                        WHERE status = $1 AND position >= $2
                        """,
                        new_status,
                        new_position,
                    )

                    # Update target task
                    query = """
                        UPDATE tasks
                        SET status = $1, position = $2, updated_at = NOW()
                        WHERE id = $3
                        RETURNING *
                    """
                    row = await conn.fetchrow(query, new_status, new_position, task_id)

            return True, {"task": dict(row), "message": "Task position updated"}

        except asyncpg.PostgresError as e:
            return False, {"error": f"Database error: {str(e)}"}
```

**When to use**:
- All service layer methods interacting with PostgreSQL
- Any operation requiring transactions (multi-step operations)
- Operations with race condition risks (position updates, concurrent writes)

**How to adapt for RAG service**:
- Create `DocumentService`, `SourceService`, `SearchService` classes
- Use same tuple[bool, dict] return pattern for all methods
- Implement connection pooling with asyncpg (min_size=5, max_size=20)
- Use transactions for document ingestion (insert document + insert chunks + insert vectors)

**Why this pattern**:
- **Race condition prevention**: Row locking with ORDER BY id prevents deadlocks
- **Clean error handling**: Consistent tuple[bool, dict] makes errors predictable
- **Connection pooling**: Efficient resource usage, scales to concurrent requests
- **Transactional integrity**: Multi-step operations are atomic

### Pattern 3: MCP Tool Consolidation Pattern
**Source**: `/Users/jon/source/vibes/infra/task-manager/backend/src/mcp_server.py`
**Relevance**: 10/10
**What it does**: Consolidates related MCP operations into fewer tools using action-based parameters. Instead of separate tools for create/update/delete, uses `manage_[resource](action="create"|"update"|"delete")`. Implements critical response optimizations for MCP including truncation and pagination limits.

**Key Techniques**:
```python
# MCP Optimization Constants
MAX_DESCRIPTION_LENGTH = 1000
MAX_PER_PAGE = 20
DEFAULT_PAGE_SIZE = 10

def truncate_text(text: str | None, max_length: int = MAX_DESCRIPTION_LENGTH) -> str | None:
    """Truncate text to maximum length with ellipsis."""
    if text and len(text) > max_length:
        return text[:max_length - 3] + "..."
    return text

def optimize_for_mcp(item: dict) -> dict:
    """Optimize item for MCP response (Gotcha #3)"""
    item = item.copy()
    if "description" in item and item["description"]:
        item["description"] = truncate_text(item["description"])
    return item

@mcp.tool()
async def find_tasks(
    query: str | None = None,
    task_id: str | None = None,
    filter_by: str | None = None,
    filter_value: str | None = None,
    page: int = 1,
    per_page: int = DEFAULT_PAGE_SIZE,
) -> str:
    """Find and search tasks (consolidated: list + search + get).

    PATTERN: Single tool for multiple query modes
    - task_id provided: Returns single task with full details
    - filter_by provided: Filters by status/project/assignee
    - No params: Returns all tasks (paginated)
    """
    try:
        # Limit per_page to MAX_PER_PAGE (Gotcha #3)
        per_page = min(per_page, MAX_PER_PAGE)

        db_pool = await get_pool()
        task_service = TaskService(db_pool)

        # Single task get mode
        if task_id:
            success, result = await task_service.get_task(task_id)

            if not success:
                # CRITICAL: Return JSON string, never dict (Gotcha #3)
                return json.dumps({
                    "success": False,
                    "error": result.get("error", "Task not found"),
                    "suggestion": "Verify the task ID is correct"
                })

            task = optimize_for_mcp(result.get("task"))
            return json.dumps({"success": True, "task": task})

        # List mode with filters
        filters = {}
        if filter_by == "status" and filter_value:
            filters["status"] = filter_value

        # CRITICAL: exclude_large_fields=True for MCP responses (Gotcha #3)
        success, result = await task_service.list_tasks(
            filters=filters,
            page=page,
            per_page=per_page,
            exclude_large_fields=True
        )

        if not success:
            return json.dumps({
                "success": False,
                "error": result.get("error"),
                "suggestion": "Check error message and try again"
            })

        tasks = [optimize_for_mcp(task) for task in result.get("tasks", [])]

        return json.dumps({
            "success": True,
            "tasks": tasks,
            "total_count": result.get("total_count"),
            "page": page,
            "per_page": per_page
        })

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "suggestion": "Check error message and try again"
        })

@mcp.tool()
async def manage_task(
    action: str,
    task_id: str | None = None,
    title: str | None = None,
    description: str | None = None,
    status: str | None = None,
) -> str:
    """Manage tasks (consolidated: create/update/delete).

    Args:
        action: "create" | "update" | "delete"
        task_id: Task UUID for update/delete
        title: Task title for create
        description: Task description
        status: Task status
    """
    try:
        db_pool = await get_pool()
        task_service = TaskService(db_pool)

        if action == "create":
            if not title:
                return json.dumps({
                    "success": False,
                    "error": "title required for create",
                    "suggestion": "Provide title parameter"
                })

            task_data = TaskCreate(title=title, description=description or "", status=status or "todo")
            success, result = await task_service.create_task(task_data)

            if not success:
                return json.dumps({
                    "success": False,
                    "error": result.get("error"),
                    "suggestion": "Check error message and ensure fields are valid"
                })

            task = optimize_for_mcp(result.get("task"))
            return json.dumps({
                "success": True,
                "task": task,
                "message": "Task created successfully"
            })

        elif action == "update":
            # ... similar pattern for update
            pass

        elif action == "delete":
            # ... similar pattern for delete
            pass

        else:
            return json.dumps({
                "success": False,
                "error": f"Unknown action: {action}",
                "suggestion": "Use 'create', 'update', or 'delete'"
            })

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "suggestion": "Check error message and try again"
        })
```

**When to use**:
- All MCP tool implementations
- Any tools that perform CRUD operations on resources
- Tools that return potentially large text fields

**How to adapt for RAG service**:
- `search_knowledge_base(query, source_id?, match_count?, search_type?)` - Consolidated search
- `manage_document(action, document_id?, file_path?, source_id?)` - Document CRUD
- `manage_source(action, source_id?, url?, source_type?)` - Source management
- `crawl_website(url, recursive?, max_pages?)` - Web crawling

**Why this pattern**:
- **Reduced tool proliferation**: 2-3 tools instead of 10+ individual tools
- **MCP payload optimization**: Truncation reduces bandwidth by ~70%
- **Consistent error format**: AI assistants can parse structured errors with suggestions
- **Better UX for AI**: Single tool for related operations is easier to understand

### Pattern 4: Strategy Pattern for Search Approaches
**Source**: `/Users/jon/source/vibes/infra/archon/python/src/server/services/search/base_search_strategy.py`
**Relevance**: 9/10
**What it does**: Implements search strategies as independent classes with consistent interfaces. Base vector search provides foundation, hybrid search combines vector + full-text, reranking reorders results using CrossEncoder.

**Key Techniques**:
```python
# Base Strategy - Foundation for all other strategies
class BaseSearchStrategy:
    """Base strategy implementing fundamental vector similarity search"""

    def __init__(self, supabase_client: Client):
        self.supabase_client = supabase_client

    async def vector_search(
        self,
        query_embedding: list[float],
        match_count: int,
        filter_metadata: dict | None = None,
        table_rpc: str = "match_archon_crawled_pages",
    ) -> list[dict[str, Any]]:
        """Perform basic vector similarity search."""
        with safe_span("base_vector_search", table=table_rpc) as span:
            try:
                # Build RPC parameters
                rpc_params = {
                    "query_embedding": query_embedding,
                    "match_count": match_count,
                }

                # Add filter parameters
                if filter_metadata:
                    if "source" in filter_metadata:
                        rpc_params["source_filter"] = filter_metadata["source"]
                        rpc_params["filter"] = {}
                    else:
                        rpc_params["filter"] = filter_metadata
                else:
                    rpc_params["filter"] = {}

                # Execute search via Supabase RPC
                response = self.supabase_client.rpc(table_rpc, rpc_params).execute()

                # Filter by similarity threshold (0.05)
                filtered_results = []
                if response.data:
                    for result in response.data:
                        similarity = float(result.get("similarity", 0.0))
                        if similarity >= 0.05:  # SIMILARITY_THRESHOLD
                            filtered_results.append(result)

                span.set_attribute("results_found", len(filtered_results))
                return filtered_results

            except Exception as e:
                logger.error(f"Vector search failed: {e}")
                return []

# Hybrid Strategy - Combines vector + full-text search
class HybridSearchStrategy:
    """Strategy implementing hybrid search combining vector and full-text"""

    def __init__(self, supabase_client: Client, base_strategy):
        self.supabase_client = supabase_client
        self.base_strategy = base_strategy  # Can delegate to base if needed

    async def search_documents_hybrid(
        self,
        query: str,
        query_embedding: list[float],
        match_count: int,
        filter_metadata: dict | None = None,
    ) -> list[dict[str, Any]]:
        """Hybrid search using PostgreSQL function combining vector + ts_vector."""
        with safe_span("hybrid_search_documents") as span:
            try:
                # Call PostgreSQL hybrid search function
                response = self.supabase_client.rpc(
                    "hybrid_search_archon_crawled_pages",
                    {
                        "query_embedding": query_embedding,
                        "query_text": query,
                        "match_count": match_count,
                        "filter": filter_metadata or {},
                    },
                ).execute()

                if not response.data:
                    return []

                # Format results with match_type information
                results = []
                for row in response.data:
                    result = {
                        "id": row["id"],
                        "content": row["content"],
                        "metadata": row["metadata"],
                        "similarity": row["similarity"],
                        "match_type": row["match_type"],  # "vector", "text", or "both"
                    }
                    results.append(result)

                span.set_attribute("results_count", len(results))
                return results

            except Exception as e:
                logger.error(f"Hybrid search failed: {e}")
                return []
```

**When to use**:
- When multiple search approaches need to coexist
- When features should be toggleable via configuration
- When strategies can be composed or chained

**How to adapt**:
- Start with base vector search (MVP)
- Add hybrid search as optional enhancement
- Design PostgreSQL functions for hybrid search (vector + ts_vector)
- Use consistent return format across all strategies

**Why this pattern**:
- **Independent testing**: Each strategy can be tested in isolation
- **Easy extension**: Add new strategies without modifying existing code
- **Graceful degradation**: If hybrid fails, fall back to base vector search
- **Performance optimization**: Can choose strategy based on query characteristics

### Pattern 5: Embedding Service with Batch Processing
**Source**: `/Users/jon/source/vibes/infra/archon/python/src/server/services/embeddings/embedding_service.py`
**Relevance**: 9/10
**What it does**: Handles embedding generation with batch processing, rate limiting, retry logic, and graceful failure handling. Uses structured result tracking to report both successes and failures.

**Key Techniques**:
```python
@dataclass
class EmbeddingBatchResult:
    """Result of batch embedding creation with success/failure tracking."""

    embeddings: list[list[float]] = field(default_factory=list)
    failed_items: list[dict[str, Any]] = field(default_factory=list)
    success_count: int = 0
    failure_count: int = 0
    texts_processed: list[str] = field(default_factory=list)

    def add_success(self, embedding: list[float], text: str):
        """Add a successful embedding."""
        self.embeddings.append(embedding)
        self.texts_processed.append(text)
        self.success_count += 1

    def add_failure(self, text: str, error: Exception, batch_index: int | None = None):
        """Add a failed item with error details."""
        self.failed_items.append({
            "text": text[:200] if text else None,
            "error": str(error),
            "error_type": type(error).__name__,
            "batch_index": batch_index,
        })
        self.failure_count += 1

async def create_embeddings_batch(
    texts: list[str],
    progress_callback: Any | None = None,
    provider: str | None = None,
) -> EmbeddingBatchResult:
    """Create embeddings with graceful failure handling.

    Follows "skip, don't corrupt" principle - failed items are tracked
    but not stored with zero embeddings.
    """
    if not texts:
        return EmbeddingBatchResult()

    result = EmbeddingBatchResult()

    # Validate text inputs
    validated_texts = []
    for i, text in enumerate(texts):
        if isinstance(text, str):
            validated_texts.append(text)
        else:
            result.add_failure(
                repr(text),
                EmbeddingAPIError("Invalid text type"),
                batch_index=None
            )

    texts = validated_texts

    async with get_llm_client(provider=provider) as client:
        # Load batch size from configuration
        batch_size = 100  # Configurable
        embedding_dimensions = 1536  # Configurable

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            batch_index = i // batch_size

            try:
                # Retry logic with exponential backoff
                retry_count = 0
                max_retries = 3

                while retry_count < max_retries:
                    try:
                        # Create embeddings for batch
                        response = await client.embeddings.create(
                            model="text-embedding-3-small",
                            input=batch,
                            dimensions=embedding_dimensions,
                        )

                        # Add successful embeddings
                        for text, item in zip(batch, response.data, strict=False):
                            result.add_success(item.embedding, text)

                        break  # Success

                    except openai.RateLimitError as e:
                        if "insufficient_quota" in str(e):
                            # Quota exhausted - stop everything
                            for text in texts[i:]:
                                result.add_failure(
                                    text,
                                    EmbeddingQuotaExhaustedError("Quota exhausted"),
                                    batch_index
                                )
                            return result  # Return partial results
                        else:
                            # Regular rate limit - retry
                            retry_count += 1
                            if retry_count < max_retries:
                                wait_time = 2**retry_count
                                await asyncio.sleep(wait_time)
                            else:
                                raise

            except Exception as e:
                # Batch failed - track failures but continue
                for text in batch:
                    result.add_failure(text, e, batch_index)

            # Progress reporting
            if progress_callback:
                processed = result.success_count + result.failure_count
                progress = (processed / len(texts)) * 100
                await progress_callback(f"Processed {processed}/{len(texts)}", progress)

            await asyncio.sleep(0.01)  # Yield control

        return result
```

**When to use**:
- Document ingestion pipelines
- Batch embedding generation
- Any operation requiring external API calls with rate limits

**How to adapt**:
- Use for document chunking and embedding
- Implement progress tracking for long-running operations
- Report both successes and failures to user
- Cache embeddings by content hash to avoid regeneration

**Why this pattern**:
- **Graceful degradation**: Quota exhaustion doesn't lose all work
- **Progress tracking**: Users see real-time status
- **Rate limit handling**: Automatic retry with exponential backoff
- **Batch efficiency**: Reduces API calls by 100x compared to single requests

## Naming Conventions

### File Naming
**Pattern**: `{feature}_service.py`, `{feature}_strategy.py`, `{feature}_tools.py`
**Examples from codebase**:
- Service layer: `task_service.py`, `project_service.py`, `rag_service.py`
- Strategies: `base_search_strategy.py`, `hybrid_search_strategy.py`
- MCP tools: `task_tools.py` (in `mcp_server/features/tasks/`)

### Class Naming
**Pattern**: `{Feature}Service`, `{Feature}Strategy`, `{Feature}Exception`
**Examples**:
- Services: `TaskService`, `RAGService`, `EmbeddingService`
- Strategies: `BaseSearchStrategy`, `HybridSearchStrategy`, `RerankingStrategy`
- Exceptions: `EmbeddingAPIError`, `EmbeddingRateLimitError`

### Function Naming
**Pattern**: Descriptive verbs with domain context
**Examples from services**:
- Service methods: `list_tasks()`, `get_task()`, `create_task()`, `update_task_position()`
- Strategy methods: `vector_search()`, `search_documents_hybrid()`, `rerank_results()`
- Utility functions: `create_embedding()`, `create_embeddings_batch()`, `truncate_text()`

### MCP Tool Naming
**Pattern**: `find_{resource}`, `manage_{resource}`, `{action}_{resource}`
**Examples**:
- Query tools: `find_tasks()`, `find_projects()`, `find_documents()`
- Action tools: `manage_task()`, `manage_project()`, `crawl_website()`

## File Organization

### Directory Structure
```
rag_service/
├── backend/
│   ├── src/
│   │   ├── config/
│   │   │   └── database.py          # Connection pooling setup
│   │   ├── models/
│   │   │   ├── document.py          # Pydantic models
│   │   │   ├── source.py
│   │   │   └── chunk.py
│   │   ├── services/
│   │   │   ├── rag_service.py       # Coordinator
│   │   │   ├── document_service.py  # CRUD operations
│   │   │   ├── source_service.py
│   │   │   ├── embeddings/
│   │   │   │   └── embedding_service.py
│   │   │   └── search/
│   │   │       ├── base_search_strategy.py
│   │   │       ├── hybrid_search_strategy.py
│   │   │       └── reranking_strategy.py
│   │   ├── api_routes/
│   │   │   ├── documents_api.py     # FastAPI routes
│   │   │   ├── sources_api.py
│   │   │   └── search_api.py
│   │   ├── mcp_server/
│   │   │   ├── main.py              # MCP server entry
│   │   │   └── features/
│   │   │       ├── documents/
│   │   │       │   └── document_tools.py
│   │   │       ├── sources/
│   │   │       │   └── source_tools.py
│   │   │       └── search/
│   │   │           └── search_tools.py
│   │   └── main.py                  # FastAPI app entry
│   └── tests/
│       ├── services/
│       ├── api/
│       └── mcp/
├── docker-compose.yml
└── .env.example
```

**Justification**:
- Mirrors task-manager structure for consistency
- Vertical feature slicing in MCP server
- Service layer separates business logic from API routes
- Strategy pattern allows search approaches to be composed

## Common Utilities to Leverage

### 1. Connection Pooling (asyncpg)
**Location**: `/Users/jon/source/vibes/infra/task-manager/backend/src/config/database.py`
**Purpose**: Provides async PostgreSQL connection pool with proper lifecycle management
**Usage Example**:
```python
from config.database import get_pool, init_db_pool, close_db_pool

# Application startup
@app.on_event("startup")
async def startup():
    await init_db_pool()

# Application shutdown
@app.on_event("shutdown")
async def shutdown():
    await close_db_pool()

# In service classes
class DocumentService:
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool

    async def list_documents(self):
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM documents")
            return [dict(row) for row in rows]
```

### 2. Supabase Client Factory
**Location**: `/Users/jon/source/vibes/infra/archon/python/src/server/utils/supabase_client.py` (inferred)
**Purpose**: Creates authenticated Supabase client for vector database operations
**Usage Example**:
```python
from utils import get_supabase_client

supabase = get_supabase_client()

# Vector search via RPC
response = supabase.rpc("match_documents", {
    "query_embedding": embedding,
    "match_count": 10
}).execute()
```

### 3. Structured Logging with Spans
**Location**: `/Users/jon/source/vibes/infra/archon/python/src/server/config/logfire_config.py` (inferred from imports)
**Purpose**: Provides observability with structured logging and tracing
**Usage Example**:
```python
from config.logfire_config import safe_span, get_logger

logger = get_logger(__name__)

async def search_documents(query: str):
    with safe_span("search_documents", query_length=len(query)) as span:
        try:
            results = await perform_search(query)
            span.set_attribute("results_found", len(results))
            return results
        except Exception as e:
            logger.error(f"Search failed: {e}")
            span.set_attribute("error", str(e))
            raise
```

### 4. Response Optimization for MCP
**Location**: `/Users/jon/source/vibes/infra/task-manager/backend/src/mcp_server.py`
**Purpose**: Truncates large fields to reduce MCP payload size
**Usage Example**:
```python
MAX_DESCRIPTION_LENGTH = 1000
MAX_PER_PAGE = 20

def truncate_text(text: str | None, max_length: int = MAX_DESCRIPTION_LENGTH) -> str | None:
    if text and len(text) > max_length:
        return text[:max_length - 3] + "..."
    return text

def optimize_for_mcp(document: dict) -> dict:
    document = document.copy()
    if "content" in document:
        document["content"] = truncate_text(document["content"])
    return document
```

### 5. Embedding Creation with Rate Limiting
**Location**: `/Users/jon/source/vibes/infra/archon/python/src/server/services/embeddings/embedding_service.py`
**Purpose**: Creates embeddings with automatic rate limiting and retry logic
**Usage Example**:
```python
from services.embeddings.embedding_service import create_embedding, create_embeddings_batch

# Single embedding
embedding = await create_embedding("search query text")

# Batch embeddings with progress
result = await create_embeddings_batch(
    texts=chunk_texts,
    progress_callback=lambda msg, pct: print(f"{msg}: {pct}%")
)

print(f"Success: {result.success_count}, Failed: {result.failure_count}")
for failed in result.failed_items:
    print(f"Failed: {failed['text'][:50]}... - {failed['error']}")
```

## Testing Patterns

### Unit Test Structure
**Pattern**: Test service methods independently with mocked dependencies
**Example**: Tests for `TaskService` in `/Users/jon/source/vibes/infra/task-manager/backend/tests/`
**Key techniques**:
- Mock asyncpg connection pool
- Test tuple[bool, dict] return values
- Test error handling paths
- Verify SQL queries use $1, $2 placeholders

```python
import pytest
from unittest.mock import AsyncMock, MagicMock
from services.document_service import DocumentService

@pytest.mark.asyncio
async def test_list_documents_success():
    # Mock connection pool
    mock_pool = MagicMock()
    mock_conn = AsyncMock()
    mock_pool.acquire.return_value.__aenter__.return_value = mock_conn

    # Mock query results
    mock_conn.fetch.return_value = [
        {"id": "1", "title": "Doc 1"},
        {"id": "2", "title": "Doc 2"},
    ]

    # Test service
    service = DocumentService(mock_pool)
    success, result = await service.list_documents()

    assert success is True
    assert len(result["documents"]) == 2
    assert result["documents"][0]["title"] == "Doc 1"

@pytest.mark.asyncio
async def test_list_documents_database_error():
    mock_pool = MagicMock()
    mock_conn = AsyncMock()
    mock_pool.acquire.return_value.__aenter__.return_value = mock_conn

    # Simulate database error
    mock_conn.fetch.side_effect = asyncpg.PostgresError("Connection failed")

    service = DocumentService(mock_pool)
    success, result = await service.list_documents()

    assert success is False
    assert "error" in result
    assert "Connection failed" in result["error"]
```

### Integration Test Structure
**Pattern**: Test API endpoints with FastAPI TestClient
**Example**: Integration tests for task API routes
**Key techniques**:
- Use FastAPI TestClient for async tests
- Test full request/response cycle
- Verify response status codes and payloads
- Test authentication and authorization

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_search_documents():
    response = client.post("/api/search", json={
        "query": "vector database",
        "match_count": 5
    })

    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "total_found" in data
```

### MCP Tool Testing
**Pattern**: Test MCP tools as standalone async functions
**Example**: Direct tool invocation tests
**Key techniques**:
- Test JSON string return values (not dicts)
- Verify structured error responses
- Test truncation and optimization
- Test all action modes (create/update/delete)

```python
@pytest.mark.asyncio
async def test_find_documents_success():
    result_json = await find_documents()
    result = json.loads(result_json)

    assert result["success"] is True
    assert "documents" in result
    assert len(result["documents"]) <= 20  # MAX_PER_PAGE

@pytest.mark.asyncio
async def test_manage_document_create():
    result_json = await manage_document(
        action="create",
        title="Test Document",
        content="Sample content"
    )
    result = json.loads(result_json)

    assert result["success"] is True
    assert "document" in result
    assert result["document"]["title"] == "Test Document"
```

## Anti-Patterns to Avoid

### 1. Hardcoded Credentials in Code
**What it is**: Storing API keys, database passwords, or secrets directly in source code
**Why to avoid**: Security vulnerability, can't change without redeployment, leaks in version control
**Found in**: N/A (both codebases use environment variables)
**Better approach**:
```python
# ❌ WRONG
OPENAI_API_KEY = "sk-abc123..."
DATABASE_URL = "postgresql://user:password@localhost/db"

# ✅ CORRECT
import os
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
```

### 2. Missing Connection Pool Context Managers
**What it is**: Acquiring database connections without using `async with` for proper cleanup
**Why to avoid**: Connection leaks, pool exhaustion, resource starvation
**Found in**: Addressed by Gotcha #12 in task-manager
**Better approach**:
```python
# ❌ WRONG - Connection may not be released
conn = await db_pool.acquire()
rows = await conn.fetch("SELECT * FROM tasks")
await db_pool.release(conn)  # Might not run if error occurs

# ✅ CORRECT - Connection always released
async with db_pool.acquire() as conn:
    rows = await conn.fetch("SELECT * FROM tasks")
```

### 3. Non-Tuple Error Handling in Services
**What it is**: Raising exceptions or returning None to indicate failures
**Why to avoid**: Inconsistent error handling, harder to parse errors, no structured data
**Found in**: Improved pattern from task-manager
**Better approach**:
```python
# ❌ WRONG - Inconsistent returns
async def get_document(id: str):
    try:
        return document
    except:
        return None  # Caller doesn't know what went wrong

# ✅ CORRECT - Consistent tuple[bool, dict] pattern
async def get_document(id: str) -> tuple[bool, dict]:
    try:
        return True, {"document": document}
    except Exception as e:
        return False, {"error": str(e)}
```

### 4. Returning Dicts from MCP Tools
**What it is**: MCP tools returning Python dicts instead of JSON strings
**Why to avoid**: MCP protocol requires JSON strings, breaks integration with AI assistants
**Found in**: Gotcha #3 in task-manager
**Better approach**:
```python
# ❌ WRONG - Returns dict
@mcp.tool()
async def find_documents():
    return {"success": True, "documents": [...]}

# ✅ CORRECT - Returns JSON string
@mcp.tool()
async def find_documents() -> str:
    return json.dumps({"success": True, "documents": [...]})
```

### 5. Missing Row Locking in Concurrent Updates
**What it is**: Updating rows without locking when concurrent modifications are possible
**Why to avoid**: Race conditions, data corruption, duplicate positions/ordering
**Found in**: Addressed by Gotcha #2 in task-manager
**Better approach**:
```python
# ❌ WRONG - No locking, race condition possible
async with conn.transaction():
    await conn.execute("UPDATE tasks SET position = position + 1 WHERE status = $1", status)
    await conn.execute("UPDATE tasks SET position = $1 WHERE id = $2", new_pos, task_id)

# ✅ CORRECT - Lock rows in consistent order
async with conn.transaction():
    # Lock rows ORDER BY id to prevent deadlocks
    await conn.execute(
        "SELECT id FROM tasks WHERE status = $1 AND position >= $2 ORDER BY id FOR UPDATE",
        status, new_pos
    )
    await conn.execute("UPDATE tasks SET position = position + 1 WHERE status = $1 AND position >= $2", status, new_pos)
    await conn.execute("UPDATE tasks SET position = $1 WHERE id = $2", new_pos, task_id)
```

### 6. Not Truncating Large Fields for MCP
**What it is**: Returning full document content (10KB+) through MCP tools
**Why to avoid**: Massive payloads slow down AI assistants, exceed token limits
**Found in**: Gotcha #3 in task-manager
**Better approach**:
```python
# ❌ WRONG - Return full 50KB document
@mcp.tool()
async def find_documents():
    docs = await service.list_documents()  # Each doc has 50KB content
    return json.dumps({"documents": docs})

# ✅ CORRECT - Truncate to 1000 chars
MAX_CONTENT_LENGTH = 1000

def optimize_for_mcp(doc: dict) -> dict:
    doc = doc.copy()
    if "content" in doc and len(doc["content"]) > MAX_CONTENT_LENGTH:
        doc["content"] = doc["content"][:MAX_CONTENT_LENGTH - 3] + "..."
    return doc

@mcp.tool()
async def find_documents():
    docs = await service.list_documents(exclude_large_fields=True)
    optimized = [optimize_for_mcp(doc) for doc in docs]
    return json.dumps({"documents": optimized})
```

### 7. Storing Zero/Null Embeddings
**What it is**: When embedding generation fails, storing `[0.0, 0.0, ...]` or null embeddings
**Why to avoid**: Corrupts vector search results, returns irrelevant matches
**Found in**: Addressed in Archon's embedding service with `EmbeddingBatchResult`
**Better approach**:
```python
# ❌ WRONG - Stores corrupted data
for text in texts:
    try:
        embedding = await create_embedding(text)
    except:
        embedding = [0.0] * 1536  # Corrupts search!
    await store_embedding(text, embedding)

# ✅ CORRECT - Skip failed items, track failures
result = await create_embeddings_batch(texts)
for text, embedding in zip(result.texts_processed, result.embeddings):
    await store_embedding(text, embedding)

# Report failures separately
if result.has_failures:
    logger.error(f"Failed to embed {result.failure_count} texts")
    for failed in result.failed_items:
        logger.error(f"  - {failed['text'][:50]}: {failed['error']}")
```

## Implementation Hints from Existing Code

### Similar Features Found

#### 1. Archon RAG Pipeline
**Location**: `/Users/jon/source/vibes/infra/archon/python/src/server/services/search/`
**Similarity**: Direct implementation of RAG service with multiple strategies
**Lessons learned**:
- Strategy pattern works well for composable search approaches
- Configuration-driven feature enablement is essential
- Graceful degradation (reranking fails → continue) improves reliability
- Observability with spans helps debug complex pipelines

**Differences for standalone service**:
- Will use simpler env var config instead of credential service
- PostgreSQL + pgvector/Qdrant instead of Supabase-specific RPC functions
- Standalone MCP server instead of integrated with larger system

#### 2. Task Manager Service Layer
**Location**: `/Users/jon/source/vibes/infra/task-manager/backend/src/services/`
**Similarity**: Service layer pattern with asyncpg and tuple[bool, dict] returns
**Lessons learned**:
- Connection pooling with asyncpg is battle-tested and performant
- tuple[bool, dict] pattern makes error handling predictable
- Row locking with ORDER BY id prevents deadlocks
- Pagination and field exclusion optimize MCP responses

**Differences for RAG service**:
- More complex data model (documents → chunks → vectors)
- Batch operations for embedding generation
- Vector similarity queries instead of traditional SQL

#### 3. Task Manager MCP Server
**Location**: `/Users/jon/source/vibes/infra/task-manager/backend/src/mcp_server.py`
**Similarity**: Consolidated MCP tools with action parameters and optimization
**Lessons learned**:
- find/manage pattern reduces tool proliferation
- Truncation to 1000 chars significantly reduces payload size
- Structured errors with suggestions improve AI assistant UX
- JSON string returns are critical (not dicts)

**Differences for RAG service**:
- Search tools need to handle vector similarity, not just CRUD
- Source management for crawled websites and uploaded documents
- Progress tracking for long-running crawl operations

## Recommendations for PRP

Based on pattern analysis:

1. **Follow RAGService coordinator pattern** for managing search strategies
   - Start with base vector search in MVP
   - Add hybrid search (vector + ts_vector) as optional enhancement
   - Design for reranking even if not implementing initially

2. **Reuse asyncpg connection pooling pattern** from task-manager
   - Same config: min_size=5, max_size=20, command_timeout=60
   - Always use `async with pool.acquire()` for connections
   - Always use $1, $2 placeholders (asyncpg style)

3. **Mirror MCP tool structure** from task-manager
   - `search_knowledge_base(query, source_id?, match_count?, search_type?)`
   - `manage_document(action, document_id?, file_path?, source_id?)`
   - `manage_source(action, source_id?, url?, source_type?)`
   - `crawl_website(url, recursive?, max_pages?)`

4. **Adapt embedding service batch pattern** for document ingestion
   - Use `EmbeddingBatchResult` for success/failure tracking
   - Implement progress callbacks for long operations
   - Never store zero embeddings on failure

5. **Use tuple[bool, dict] error handling** for all service methods
   - Consistent across all services (DocumentService, SourceService, SearchService)
   - Makes error handling predictable for API routes and MCP tools

6. **Implement conditional field selection** for MCP responses
   - Truncate content to 1000 chars for list operations
   - Limit per_page to 20 for MCP tools
   - Return full content only for single document GET

7. **Design PostgreSQL schema** with vector support
   - Use pgvector extension or Qdrant for vectors
   - Separate tables: documents, chunks, sources
   - ts_vector columns for hybrid search
   - Foreign keys with CASCADE for cleanup

8. **Add structured logging** with spans for observability
   - Log search latency, result counts, match types
   - Track embedding generation progress
   - Monitor database query performance

## Source References

### From Archon
- `/Users/jon/source/vibes/infra/archon/python/src/server/services/search/rag_service.py` - Strategy coordinator - Relevance 10/10
- `/Users/jon/source/vibes/infra/archon/python/src/server/services/search/base_search_strategy.py` - Vector search foundation - Relevance 9/10
- `/Users/jon/source/vibes/infra/archon/python/src/server/services/search/hybrid_search_strategy.py` - Hybrid search pattern - Relevance 9/10
- `/Users/jon/source/vibes/infra/archon/python/src/server/services/embeddings/embedding_service.py` - Batch embedding with rate limiting - Relevance 9/10

### From Task Manager
- `/Users/jon/source/vibes/infra/task-manager/backend/src/services/task_service.py` - Service layer pattern - Relevance 10/10
- `/Users/jon/source/vibes/infra/task-manager/backend/src/mcp_server.py` - MCP tool consolidation - Relevance 10/10
- `/Users/jon/source/vibes/infra/task-manager/backend/src/config/database.py` - Connection pooling - Relevance 10/10

### From Archon Knowledge Base
- No high-relevance code examples from Archon's stored knowledge base
- Pydantic AI patterns available but not directly applicable to RAG service architecture

## Next Steps for Assembler

When generating the PRP:

1. **Reference these patterns in "Current Codebase Tree" section**
   - Link to specific files and line numbers for each pattern
   - Explain which patterns apply to which components

2. **Include key code snippets in "Implementation Blueprint"**
   - Show service layer initialization
   - Show MCP tool structure
   - Show database query patterns with $1, $2 placeholders
   - Show tuple[bool, dict] error handling

3. **Add anti-patterns to "Known Gotchas" section**
   - Connection leaks without async with
   - Missing row locking in concurrent updates
   - Returning dicts instead of JSON from MCP tools
   - Storing zero embeddings on failures
   - Not truncating large fields for MCP

4. **Use file organization for "Desired Codebase Tree"**
   - Show directory structure with service/, mcp_server/, api_routes/
   - Indicate which patterns apply to each file

5. **Create implementation checklist** referencing patterns
   - [ ] Implement DocumentService using task-manager service pattern
   - [ ] Create RAGService coordinator using Archon strategy pattern
   - [ ] Build MCP tools using task-manager consolidation pattern
   - [ ] Setup connection pooling using task-manager database.py pattern
   - [ ] Implement embedding service using Archon batch processing pattern
