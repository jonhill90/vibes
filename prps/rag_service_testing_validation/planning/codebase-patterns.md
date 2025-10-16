# Codebase Patterns: rag_service_testing_validation

## Overview
This document extracts architectural patterns, testing strategies, and implementation approaches from the existing RAG service codebase to inform comprehensive testing and validation implementation. Key patterns include FastAPI TestClient with async mocking, pytest fixtures for database/service isolation, React component structure with CRUD operations, and browser validation workflows using Playwright MCP tools.

## Architectural Patterns

### Pattern 1: FastAPI TestClient with AsyncMock for Integration Testing
**Source**: `/Users/jon/source/vibes/infra/rag-service/backend/tests/integration/test_crawl_api.py`
**Relevance**: 10/10
**What it does**: Uses FastAPI's TestClient with mocked async database operations to test API endpoints without requiring a live database.

**Key Techniques**:
```python
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture
def app_with_crawl_routes(mock_db_pool):
    """Create FastAPI app with routes for testing."""
    from fastapi import FastAPI
    from src.api.routes.crawls import router as crawl_router
    from src.api.dependencies import get_db_pool

    app = FastAPI()
    app.include_router(crawl_router)

    # Override dependency with mock
    app.dependency_overrides[get_db_pool] = lambda: mock_db_pool

    return app

@pytest.fixture
def client(app_with_crawl_routes):
    """Create TestClient for API tests."""
    return TestClient(app_with_crawl_routes)

def test_start_crawl_success(client, mock_db_pool):
    # Mock database operations with side_effect for sequential returns
    mock_conn = MagicMock()
    mock_conn.fetchval = AsyncMock(side_effect=[True])  # Source exists
    mock_conn.fetchrow = AsyncMock(side_effect=[
        {"id": job_id, "status": "pending", ...},  # Create job
        {"id": job_id, "status": "completed", ...}  # After crawl
    ])

    async def mock_acquire():
        yield mock_conn

    mock_db_pool.acquire = MagicMock(return_value=mock_acquire())

    # Make request
    response = client.post("/api/crawls", json={...})

    assert response.status_code == 201
```

**When to use**:
- Testing API endpoints without live database
- Validating request/response schemas
- Testing error handling (400, 404, 422, 500)
- Integration tests for route handlers

**How to adapt**:
- Replace `crawl_router` with `documents_router` or `search_router`
- Mock different database operations (fetchval, fetchrow, fetch, execute)
- Use `side_effect` list for multi-step operations
- Override specific dependencies (db_pool, openai_client, qdrant_client)

**Why this pattern**:
- Fast execution (~60s for full integration suite vs 10min with real DB)
- Isolated tests prevent data pollution
- Predictable behavior through controlled mocks
- Easy to test edge cases (network failures, malformed data)

---

### Pattern 2: Comprehensive Pytest Fixtures for Service Isolation
**Source**: `/Users/jon/source/vibes/infra/rag-service/backend/tests/conftest.py`
**Relevance**: 10/10
**What it does**: Provides reusable fixtures for database pools, service mocks, and test data factories to ensure consistent test setup across all test modules.

**Key Techniques**:
```python
import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture
def mock_db_pool():
    """Mock asyncpg connection pool for unit tests."""
    pool = MagicMock()
    conn = MagicMock()

    # Mock connection methods
    conn.fetchrow = AsyncMock()
    conn.fetchval = AsyncMock()
    conn.fetch = AsyncMock()
    conn.execute = AsyncMock()

    # Mock acquire() as async context manager
    async def mock_acquire():
        yield conn

    pool.acquire = MagicMock(return_value=mock_acquire())
    pool.close = AsyncMock()

    return pool

@pytest.fixture
def mock_openai_client():
    """Mock OpenAI AsyncClient for unit tests."""
    client = AsyncMock(spec=AsyncOpenAI)
    client.embeddings = AsyncMock()
    client.embeddings.create = AsyncMock()
    return client

@pytest.fixture
def sample_embedding():
    """Sample embedding vector (1536 dimensions)."""
    return [0.1] * 1536

@pytest.fixture
def sample_chunk():
    """Sample chunk dictionary with all required fields."""
    return {
        "chunk_id": str(uuid4()),
        "document_id": str(uuid4()),
        "text": "This is a test chunk of text for testing purposes.",
        "chunk_index": 0,
        "score": 0.95,
        "metadata": {"title": "Test Document"}
    }

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for pytest-asyncio."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
```

**When to use**:
- Unit tests requiring database operations
- Service layer testing with isolated dependencies
- Test data generation for consistent inputs
- Async test execution with pytest-asyncio

**How to adapt**:
- Add fixtures for new services (DocumentService, SearchService)
- Create test data factories for documents, sources, chunks
- Mock external APIs (OpenAI, Qdrant, file system)
- Extend `mock_mcp_context` for tool testing

**Why this pattern**:
- DRY principle: define mocks once, reuse everywhere
- Consistent test environment across modules
- Easy to extend with new fixtures
- Scoped fixtures prevent expensive setup repetition

---

### Pattern 3: React Component CRUD Pattern with Delete Confirmation
**Source**: `/Users/jon/source/vibes/infra/rag-service/frontend/src/components/CrawlManagement.tsx`
**Relevance**: 10/10
**What it does**: Implements full CRUD interface with form validation, list display, status filters, auto-refresh, and modal delete confirmation.

**Key Techniques**:
```typescript
import { useState, useEffect, useCallback } from 'react';
import { useForm } from 'react-hook-form';

export default function CrawlManagement() {
  const [crawlJobs, setCrawlJobs] = useState<CrawlJobResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all');
  const [expandedJobId, setExpandedJobId] = useState<string | null>(null);
  const [deletingJobId, setDeletingJobId] = useState<string | null>(null);

  const { register, handleSubmit, formState: { errors }, reset } = useForm<CrawlFormData>({
    defaultValues: {
      max_pages: 100,
      max_depth: 3,
    },
  });

  // Load data with filters
  const loadCrawlJobs = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = statusFilter === 'all' ? {} : { status: statusFilter };
      const data = await listCrawlJobs(params);
      setCrawlJobs(data.crawl_jobs);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load');
    } finally {
      setLoading(false);
    }
  }, [statusFilter]);

  useEffect(() => {
    loadCrawlJobs();
  }, [loadCrawlJobs]);

  // Auto-refresh for active jobs
  useEffect(() => {
    if (!autoRefresh) return;
    const hasActiveJobs = crawlJobs?.some(
      (job) => job.status === 'pending' || job.status === 'running'
    );
    if (!hasActiveJobs) return;

    const interval = setInterval(() => {
      loadCrawlJobs();
    }, 5000); // Refresh every 5 seconds

    return () => clearInterval(interval);
  }, [crawlJobs, autoRefresh, loadCrawlJobs]);

  // Delete with confirmation modal
  const handleDeleteJob = async (jobId: string) => {
    setError(null);
    try {
      await deleteCrawlJob(jobId);
      setDeletingJobId(null);
      await loadCrawlJobs();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete');
    }
  };

  return (
    <div>
      {/* Create Form */}
      <form onSubmit={handleSubmit(onStartCrawl)}>
        <input {...register('url', { required: 'URL is required' })} />
        {errors.url && <span>{errors.url.message}</span>}
      </form>

      {/* List with Filters */}
      <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value as StatusFilter)}>
        <option value="all">All Statuses</option>
        <option value="running">Running</option>
      </select>

      {/* Delete Confirmation Modal */}
      {deletingJobId && (
        <div style={styles.modalOverlay}>
          <div style={styles.modal}>
            <h3>Confirm Delete</h3>
            <p>Are you sure? This action cannot be undone.</p>
            <button onClick={() => handleDeleteJob(deletingJobId)}>Delete</button>
            <button onClick={() => setDeletingJobId(null)}>Cancel</button>
          </div>
        </div>
      )}
    </div>
  );
}
```

**When to use**:
- Management pages (DocumentsManagement, SourceManagement)
- CRUD operations with user confirmation
- Real-time status updates
- Filter/pagination interfaces

**How to adapt**:
- Replace `CrawlJobResponse` with `DocumentResponse`
- Change filters (status → document_type, source_id)
- Adjust auto-refresh interval based on operation type
- Modify table columns for different data models

**Why this pattern**:
- User-friendly confirmation prevents accidental deletes
- Auto-refresh provides live progress updates
- Form validation prevents invalid submissions
- Consistent UI patterns across management pages

---

### Pattern 4: Browser Validation Workflow (Pre-flight → Interact → Validate)
**Source**: `.claude/patterns/browser-validation.md`
**Relevance**: 10/10
**What it does**: Defines standard workflow for browser automation testing using Playwright MCP tools with pre-flight checks, semantic element queries, and accessibility tree validation.

**Key Techniques**:
```python
def validate_document_upload():
    """Complete document upload validation workflow."""

    # Step 1: Pre-flight checks
    print("🔍 Pre-flight checks...")

    # Check browser installed
    try:
        browser_navigate(url="about:blank")
    except Exception:
        print("⚠️ Browser not installed, installing...")
        browser_install()
        time.sleep(30)  # Wait for installation

    # Check frontend running
    result = Bash("docker-compose ps | grep rag-service")
    if "Up" not in result.stdout:
        print("⚠️ Starting services...")
        Bash("docker-compose up -d")
        time.sleep(10)

    # Verify service identity
    result = Bash("curl -s http://localhost:5173")
    if "RAG Service" not in result.stdout:
        print("❌ Wrong service at port 5173")
        exit(1)

    print("✅ Pre-flight checks passed")

    # Step 2: Navigate and validate initial state
    browser_navigate(url="http://localhost:5173")
    initial_state = browser_snapshot()  # Accessibility tree, NOT screenshot

    if "DocumentList" not in initial_state:
        print("❌ Document list not found")
        exit(1)

    # Step 3: Interact - Use semantic queries (stable across re-renders)
    browser_click(element="button containing 'Upload'")
    browser_wait_for(text="Select a document", timeout=5000)

    browser_fill_form(fields=[
        {"name": "file", "type": "file", "value": "/tmp/test-document.pdf"},
        {"name": "title", "type": "textbox", "value": "Test Document"}
    ])

    browser_click(element="button containing 'Submit'")
    browser_wait_for(text="Upload successful", timeout=30000)

    # Step 4: Validate final state
    final_state = browser_snapshot()

    validation_checks = {
        "success_message": "Upload successful" in final_state,
        "document_title": "Test Document" in final_state,
        "document_in_list": "test-document.pdf" in final_state
    }

    all_passed = all(validation_checks.values())

    if all_passed:
        print("✅ All validations passed")
        browser_take_screenshot(filename="validation-proof.png")  # Human proof only
    else:
        print("❌ Validation failed")
        browser_take_screenshot(filename="validation-error.png")
        exit(1)
```

**When to use**:
- Frontend UI validation (document upload, search filtering, delete operations)
- End-to-end workflow testing
- Accessibility validation
- User journey testing

**How to adapt**:
- Change service port (5173 for RAG, 5174 for Task Manager)
- Adjust timeouts (5s for UI, 30s for uploads, 60s for processing)
- Replace element queries for different UI components
- Add service-specific validation checks

**Why this pattern**:
- Pre-flight checks prevent wasted attempts
- Accessibility tree provides agent-parseable validation (not screenshots)
- Semantic queries survive re-renders (element refs change)
- Token-efficient (~500 tokens/snapshot vs ~2000 tokens/screenshot)

---

### Pattern 5: Service Layer with Connection Pool Pattern
**Source**: `/Users/jon/source/vibes/infra/rag-service/backend/src/services/document_service.py`
**Relevance**: 9/10
**What it does**: Implements service layer with proper connection pool management, using `async with pool.acquire()` for each operation and returning `tuple[bool, dict]` for error handling.

**Key Techniques**:
```python
import asyncpg
import logging

logger = logging.getLogger(__name__)

class DocumentService:
    """Service class for document operations with asyncpg connection pooling."""

    VALID_DOCUMENT_TYPES = ["pdf", "markdown", "html", "text", "docx"]

    def __init__(self, db_pool: asyncpg.Pool):
        """Initialize with database connection pool.

        CRITICAL PATTERN (Gotcha #2):
        - Store db_pool, NOT connection
        - Connections acquired per-operation via async with pool.acquire()
        """
        self.db_pool = db_pool

    async def list_documents(
        self,
        filters: dict[str, Any] | None = None,
        page: int = 1,
        per_page: int = 50,
        exclude_large_fields: bool = False,
    ) -> tuple[bool, dict[str, Any]]:
        """List documents with filters, pagination, and optional field exclusion."""
        try:
            filters = filters or {}
            offset = (page - 1) * per_page

            # Build WHERE clause
            where_clauses = []
            params = []
            param_idx = 1

            if "source_id" in filters:
                where_clauses.append(f"source_id = ${param_idx}")
                params.append(filters["source_id"])
                param_idx += 1

            where_clause = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

            # CRITICAL PATTERN (Gotcha #8): Always use async with for connection management
            async with self.db_pool.acquire() as conn:
                total_count = await conn.fetchval(
                    f"SELECT COUNT(*) FROM documents {where_clause}",
                    *params
                )

                # CRITICAL (Gotcha #3): Use $1, $2 placeholders (asyncpg), not %s
                query = f"""
                    SELECT *
                    FROM documents
                    {where_clause}
                    ORDER BY created_at DESC
                    LIMIT ${param_idx} OFFSET ${param_idx + 1}
                """
                params.extend([per_page, offset])
                rows = await conn.fetch(query, *params)

            documents = [dict(row) for row in rows]

            return True, {
                "documents": documents,
                "total_count": total_count,
                "page": page,
                "per_page": per_page,
            }

        except asyncpg.PostgresError as e:
            logger.error(f"Database error listing documents: {e}")
            return False, {"error": f"Database error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            return False, {"error": f"Error listing documents: {str(e)}"}
```

**When to use**:
- Service layer implementations (DocumentService, SourceService, SearchService)
- Database operations with connection pooling
- Paginated queries
- Error handling with success/failure tuples

**How to adapt**:
- Change table name and column names for different services
- Adjust filters and validation based on data model
- Add service-specific business logic
- Extend error handling for specific database errors

**Why this pattern**:
- Connection pooling prevents resource exhaustion
- Tuple return pattern enables clear error handling
- Proper async context managers prevent connection leaks
- Logging aids debugging and monitoring

---

## Naming Conventions

### File Naming
**Pattern**: `{feature}_{type}.py` or `{Feature}{Type}.tsx`
**Examples**:
- Backend tests: `test_crawl_api.py`, `test_ingestion_service.py`, `test_document_service.py`
- Backend services: `document_service.py`, `vector_service.py`, `embedding_service.py`
- Backend routes: `documents.py`, `crawls.py`, `sources.py`
- Frontend components: `CrawlManagement.tsx`, `SourceManagement.tsx`, `DocumentUpload.tsx`
- Test fixtures: `conftest.py` (pytest convention)

### Class Naming
**Pattern**: `{Feature}{Type}` (PascalCase)
**Examples**:
- Services: `DocumentService`, `VectorService`, `EmbeddingService`, `IngestionService`
- Test classes: `TestStartCrawlEndpoint`, `TestListCrawlJobsEndpoint`, `TestCrawlAPIErrorHandling`
- Response models: `DocumentResponse`, `CrawlJobResponse`, `ErrorResponse`, `MessageResponse`
- Request models: `CrawlStartRequest`, `SourceRequest`, `DocumentRequest`

### Function Naming
**Pattern**: `{verb}_{noun}` (snake_case for Python, camelCase for TypeScript)
**Examples**:
- Python service methods: `list_documents()`, `create_document()`, `delete_document()`, `get_document()`
- Python test methods: `test_start_crawl_success()`, `test_start_crawl_invalid_source_id_format()`
- TypeScript handlers: `handleDeleteJob()`, `loadCrawlJobs()`, `onStartCrawl()`
- TypeScript API calls: `listDocuments()`, `createSource()`, `deleteCrawlJob()`

### Variable Naming
**Pattern**: Descriptive names matching purpose
**Examples**:
- Mock objects: `mock_db_pool`, `mock_openai_client`, `mock_qdrant_client`, `mock_conn`
- Test data: `sample_embedding`, `sample_chunk`, `sample_document_id`, `sample_source_id`
- State variables: `crawlJobs`, `loading`, `error`, `statusFilter`, `deletingJobId`
- API responses: `response`, `data`, `result`, `success`

---

## File Organization

### Directory Structure
```
infra/rag-service/
├── backend/
│   ├── src/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── documents.py           # Document CRUD endpoints
│   │   │   │   ├── crawls.py              # Crawl job endpoints
│   │   │   │   └── sources.py             # Source management endpoints
│   │   │   └── dependencies.py            # Dependency injection
│   │   ├── services/
│   │   │   ├── document_service.py        # Document business logic
│   │   │   ├── vector_service.py          # Vector DB operations
│   │   │   ├── ingestion_service.py       # Pipeline orchestration
│   │   │   ├── embeddings/
│   │   │   │   └── embedding_service.py   # Embedding generation
│   │   │   └── search/
│   │   │       ├── rag_service.py         # Search orchestration
│   │   │       └── base_search_strategy.py
│   │   ├── models/
│   │   │   └── responses.py               # Pydantic response models
│   │   └── config/
│   │       └── settings.py                # Configuration
│   └── tests/
│       ├── conftest.py                    # Shared fixtures
│       ├── unit/
│       │   ├── test_document_service.py   # Service layer tests
│       │   ├── test_embedding_service.py
│       │   └── test_routes.py             # Route handler tests
│       ├── integration/
│       │   ├── test_crawl_api.py          # API integration tests
│       │   ├── test_document_api.py
│       │   └── test_hybrid_search.py
│       └── browser/
│           ├── test_document_upload.py    # Browser validation
│           ├── test_search_filtering.py
│           └── test_delete_operations.py
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── CrawlManagement.tsx        # Crawl job management UI
│       │   ├── SourceManagement.tsx       # Source CRUD UI
│       │   ├── DocumentUpload.tsx         # Upload interface
│       │   ├── SearchInterface.tsx        # Search UI
│       │   └── DocumentsManagement.tsx    # NEW: Document management UI
│       └── api/
│           └── client.ts                  # API client functions
└── docker-compose.yaml                    # Service orchestration
```

**Justification**:
- **Tests organized by level**: `unit/`, `integration/`, `browser/` matches quality-gates pattern (Level 2, 3a, 3b)
- **Services by domain**: Separate concerns (ingestion, search, embeddings, vector storage)
- **Routes by resource**: RESTful organization (documents, crawls, sources)
- **Shared fixtures in conftest.py**: Pytest convention for fixture discovery
- **Frontend components by feature**: Each management component is self-contained

---

## Common Utilities to Leverage

### 1. FastAPI Dependency Injection System
**Location**: `infra/rag-service/backend/src/api/dependencies.py`
**Purpose**: Provides dependency injection for database pools and services
**Usage Example**:
```python
from src.api.dependencies import get_db_pool
from fastapi import Depends
import asyncpg

@router.post("/api/documents")
async def upload_document(
    db_pool: asyncpg.Pool = Depends(get_db_pool),
):
    document_service = DocumentService(db_pool)
    # Use service...
```

**Why use it**:
- Enables dependency overriding in tests
- Centralizes service initialization
- Simplifies route handler signatures

### 2. Pytest-asyncio for Async Test Execution
**Location**: `infra/rag-service/backend/tests/conftest.py` (event_loop fixture)
**Purpose**: Enables async/await in pytest test functions
**Usage Example**:
```python
import pytest

@pytest.mark.asyncio
async def test_list_documents(mock_db_pool):
    service = DocumentService(mock_db_pool)
    success, result = await service.list_documents()
    assert success is True
```

**Why use it**:
- Tests async code naturally with async/await
- Proper event loop management
- Compatible with FastAPI async routes

### 3. React Hook Form for Form Validation
**Location**: `infra/rag-service/frontend/src/components/CrawlManagement.tsx`
**Purpose**: Declarative form validation with error handling
**Usage Example**:
```typescript
import { useForm } from 'react-hook-form';

const { register, handleSubmit, formState: { errors }, reset } = useForm<FormData>({
  defaultValues: { max_pages: 100 }
});

<input {...register('url', { required: 'URL is required' })} />
{errors.url && <span>{errors.url.message}</span>}
```

**Why use it**:
- Automatic validation on submit
- Error message display
- Form reset after successful submission

### 4. asyncpg Connection Pooling
**Location**: Used throughout services (`document_service.py`, `crawls.py`)
**Purpose**: Efficient database connection management
**Usage Example**:
```python
async with db_pool.acquire() as conn:
    result = await conn.fetchrow("SELECT * FROM documents WHERE id = $1", doc_id)
```

**Why use it**:
- Prevents connection leaks
- Connection reuse for performance
- Automatic cleanup via context manager

### 5. unittest.mock AsyncMock and MagicMock
**Location**: `infra/rag-service/backend/tests/conftest.py`, `test_crawl_api.py`
**Purpose**: Mock async operations and services
**Usage Example**:
```python
from unittest.mock import AsyncMock, MagicMock

mock_conn = MagicMock()
mock_conn.fetchval = AsyncMock(return_value=True)
mock_conn.fetchrow = AsyncMock(side_effect=[
    {"id": 1, "status": "pending"},
    {"id": 1, "status": "completed"}
])
```

**Why use it**:
- Sequential mock returns with side_effect
- Async method mocking
- Service isolation in tests

---

## Testing Patterns

### Unit Test Structure
**Pattern**: Test class per endpoint/method, multiple test methods per class
**Example**: `/Users/jon/source/vibes/infra/rag-service/backend/tests/integration/test_crawl_api.py`

**Key techniques**:
```python
class TestStartCrawlEndpoint:
    """Tests for POST /api/crawls endpoint."""

    def test_start_crawl_success(self, client, mock_db_pool):
        """Test successful crawl job creation.

        Expected:
        - Returns 201 Created
        - Response includes job_id, status, pages_crawled
        - Database INSERT called
        """
        # Arrange
        mock_conn = MagicMock()
        mock_conn.fetchval = AsyncMock(side_effect=[True])  # Source exists

        # Act
        response = client.post("/api/crawls", json={...})

        # Assert
        assert response.status_code == 201
        assert "id" in response.json()

    def test_start_crawl_invalid_source_id_format(self, client, mock_db_pool):
        """Test start crawl with invalid UUID format.

        Expected:
        - Returns 400 Bad Request
        - Error message indicates invalid UUID
        """
        response = client.post("/api/crawls", json={"source_id": "not-a-uuid", ...})
        assert response.status_code == 400

    def test_start_crawl_source_not_found(self, client, mock_db_pool):
        """Test start crawl with non-existent source.

        Expected:
        - Returns 400 Bad Request
        - Error message indicates source not found
        """
        mock_conn = MagicMock()
        mock_conn.fetchval = AsyncMock(return_value=False)  # Source doesn't exist

        response = client.post("/api/crawls", json={...})
        assert response.status_code == 400
```

**Fixture usage**:
- `client`: FastAPI TestClient with mocked dependencies
- `mock_db_pool`: AsyncMock connection pool
- `mock_openai_client`: AsyncMock for OpenAI API
- `sample_embedding`, `sample_chunk`: Test data factories

**Mocking patterns**:
- Use `side_effect` list for sequential mock returns
- Mock `fetchval()` for EXISTS queries
- Mock `fetchrow()` for single row returns
- Mock `fetch()` for multiple row returns
- Mock `execute()` for INSERT/UPDATE/DELETE

**Assertions**:
- Status codes (200, 201, 400, 404, 422, 500)
- Response structure (JSON keys, types)
- Error messages (detail field)
- Database call counts (if needed)

### Integration Test Structure
**Pattern**: Full request/response cycle with mocked external services
**Example**: Same as unit tests but with more complex scenarios

**Key differences from unit tests**:
- Mock external APIs (OpenAI, Qdrant) but use real service classes
- Test multi-step workflows (create → update → delete)
- Validate side effects (database state changes)
- Test error propagation through layers

### Browser Test Structure (NEW - to be implemented)
**Pattern**: Navigate → Interact → Validate using MCP browser tools
**Template**:
```python
def test_document_upload_workflow():
    """Test document upload end-to-end workflow."""

    # Pre-flight checks
    ensure_browser_installed()
    ensure_frontend_running(5173, "rag-service")

    # Navigate
    browser_navigate(url="http://localhost:5173")
    initial_state = browser_snapshot()
    assert "DocumentList" in initial_state

    # Interact
    browser_click(element="button containing 'Upload'")
    browser_wait_for(text="Select a document", timeout=5000)
    browser_fill_form(fields=[
        {"name": "file", "type": "file", "value": "/tmp/test.pdf"},
        {"name": "title", "type": "textbox", "value": "Test Document"}
    ])
    browser_click(element="button containing 'Submit'")
    browser_wait_for(text="Upload successful", timeout=30000)

    # Validate
    final_state = browser_snapshot()
    assert "Test Document" in final_state
    assert "test.pdf" in final_state

    # Proof screenshot
    browser_take_screenshot(filename="upload-validation-proof.png")
```

---

## Anti-Patterns to Avoid

### 1. Hard-Coding Element Refs in Browser Tests
**What it is**: Using element refs like `ref="e5"` that change on every render
**Why to avoid**: Element refs are ephemeral and break on re-renders
**Found in**: None (existing code uses semantic queries correctly)
**Better approach**:
```python
# ❌ WRONG - Hard-coded refs
browser_click(ref="e5")

# ✅ RIGHT - Semantic queries
browser_click(element="button containing 'Upload'")
```

### 2. Manual sleep() Instead of Auto-Wait
**What it is**: Using `time.sleep(3)` for arbitrary waits
**Why to avoid**: Makes tests slow and unreliable (race conditions)
**Found in**: None (existing code uses proper waits)
**Better approach**:
```python
# ❌ WRONG - Manual sleep
browser_navigate(url="http://localhost:5173")
time.sleep(3)
browser_click(...)

# ✅ RIGHT - Auto-wait with conditions
browser_navigate(url="http://localhost:5173")
browser_wait_for(text="DocumentList", timeout=5000)
browser_click(element="button containing 'Upload'")
```

### 3. Using Screenshots for Agent Validation
**What it is**: Validating UI state by analyzing screenshots
**Why to avoid**: Agents can't parse images; wastes 4x tokens
**Found in**: None (pattern explicitly warns against this)
**Better approach**:
```python
# ❌ WRONG - Screenshot for validation
screenshot = browser_take_screenshot("state.png")
# Agent cannot validate from screenshot

# ✅ RIGHT - Accessibility tree for validation
snapshot = browser_snapshot()
if "ExpectedElement" in snapshot:
    print("✅ Validation passed")

# ✅ ACCEPTABLE - Screenshot for human proof only
browser_take_screenshot(filename="proof.png")
```

### 4. Storing Connections Instead of Pool
**What it is**: Storing `asyncpg.Connection` in service `__init__` instead of pool
**Why to avoid**: Connections can't be reused, causes resource leaks
**Found in**: None (services correctly store pool)
**Better approach**:
```python
# ❌ WRONG - Store connection
class DocumentService:
    def __init__(self, conn: asyncpg.Connection):
        self.conn = conn  # Leaks resources

# ✅ RIGHT - Store pool
class DocumentService:
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool  # Acquire per-operation
```

### 5. Using %s Placeholders Instead of $1, $2
**What it is**: Using psycopg2-style `%s` placeholders with asyncpg
**Why to avoid**: asyncpg uses `$1`, `$2` placeholders (different from psycopg2)
**Found in**: None (services correctly use $1, $2)
**Better approach**:
```python
# ❌ WRONG - psycopg2 style
query = "SELECT * FROM documents WHERE id = %s"
result = await conn.fetchrow(query, doc_id)

# ✅ RIGHT - asyncpg style
query = "SELECT * FROM documents WHERE id = $1"
result = await conn.fetchrow(query, doc_id)
```

### 6. Skipping Pre-Flight Checks in Browser Tests
**What it is**: Navigating to frontend without verifying service running
**Why to avoid**: Causes cryptic "Connection refused" errors
**Found in**: None (pattern emphasizes pre-flight checks)
**Better approach**:
```python
# ❌ WRONG - Navigate without checks
browser_navigate(url="http://localhost:5173")
# Error: Connection refused

# ✅ RIGHT - Pre-flight checks first
ensure_frontend_running(5173, "rag-service")
browser_navigate(url="http://localhost:5173")
```

---

## Implementation Hints from Existing Code

### Similar Features Found

#### 1. Crawl Job Management
**Location**: `/Users/jon/source/vibes/infra/rag-service/backend/src/api/routes/crawls.py`
**Similarity**: CRUD operations with status tracking, very similar to document management
**Lessons**:
- Use Pydantic models for request/response validation
- Status enum validation in routes (prevent invalid values)
- Pagination with `limit` and `offset` query parameters
- Soft validation (log warnings for unexpected MIME types, don't reject)
- Comprehensive error responses with `detail`, `suggestion` fields

**Differences**: Documents don't have status progression (no "running" status)

#### 2. Document Upload Pipeline
**Location**: `/Users/jon/source/vibes/infra/rag-service/backend/src/api/routes/documents.py:174-283`
**Similarity**: File validation, temporary storage, ingestion pipeline integration
**Lessons**:
- Validate file extension AND MIME type (defense in depth)
- Use `tempfile.NamedTemporaryFile` for upload handling
- Clean up temp files in `finally` block
- Separate validation errors (400) from processing errors (500)
- Log extensively for debugging (file size, chunk count, timing)

**Differences**: Testing should mock file operations, not use real files

#### 3. List with Filters and Pagination
**Location**: `/Users/jon/source/vibes/infra/rag-service/backend/src/services/document_service.py:60-150`
**Similarity**: Dynamic WHERE clause building, pagination logic
**Lessons**:
- Build WHERE clauses dynamically based on filters
- Use `param_idx` counter for asyncpg placeholders
- Get total count before paginated query
- Return metadata (page, per_page, total_count) with results
- Validate filters early (before database query)

**Differences**: Search filtering adds `source_id` filter to vector search

#### 4. React Management Components
**Location**: `CrawlManagement.tsx`, `SourceManagement.tsx`
**Similarity**: List → Create → Edit → Delete workflow with modals
**Lessons**:
- Use `react-hook-form` for validation
- Separate state for editing (`editingSource`, `deletingJobId`)
- Confirmation modal prevents accidental deletes
- Auto-refresh for long-running operations
- Status badges with color coding
- Empty states guide users to first action

**Differences**: DocumentsManagement needs source filter dropdown

---

## Recommendations for PRP

Based on pattern analysis:

1. **Follow test_crawl_api.py pattern** for backend API testing
   - Use FastAPI TestClient with dependency overrides
   - Mock db_pool with AsyncMock for unit tests
   - Use `side_effect` lists for sequential mock returns
   - Test error cases (400, 404, 422, 500) exhaustively

2. **Reuse conftest.py fixtures** instead of reimplementing
   - Extend with `sample_document`, `sample_source` fixtures
   - Add `mock_uploaded_file` fixture for file upload tests
   - Use `mock_mcp_context` for tool testing
   - Add `test_db_pool` fixture for integration tests (if needed)

3. **Mirror CrawlManagement.tsx structure** for DocumentsManagement.tsx
   - Use `react-hook-form` for validation
   - Implement delete confirmation modal
   - Add source filter dropdown
   - Display chunk count in table
   - Use consistent styling (inline styles object)

4. **Adapt browser-validation.md pattern** for frontend tests
   - Create `tests/browser/test_document_upload.py`
   - Implement pre-flight checks (browser installed, services running)
   - Use `browser_snapshot()` for validation (not screenshots)
   - One screenshot at end for human proof
   - Set appropriate timeouts (5s UI, 30s uploads)

5. **Avoid creating new test infrastructure** if possible
   - Use existing fixtures from conftest.py
   - Follow existing test class organization
   - Reuse API client patterns from test_crawl_api.py
   - Don't create separate test database (use transaction rollback)

6. **Follow service layer pattern** for test helpers
   - Store db_pool in `__init__`, acquire connections per-operation
   - Return `tuple[bool, dict]` for error handling
   - Use $1, $2 placeholders for asyncpg
   - Log errors with context

7. **Implement quality gates** in execution order
   - Level 1: `ruff check && mypy src/` (~5s)
   - Level 2: `pytest tests/unit/` (~30s)
   - Level 3a: `pytest tests/integration/` (~60s)
   - Level 3b: Browser validation (~120s)

8. **Use semantic queries** in browser tests
   - `"button containing 'Upload'"` not `ref="e5"`
   - `"textbox"` with `name="title"` for form fields
   - `"link"` for navigation elements
   - Avoid CSS selectors and XPath

---

## Source References

### From Local Codebase
- `/Users/jon/source/vibes/infra/rag-service/backend/tests/integration/test_crawl_api.py`: FastAPI TestClient pattern, AsyncMock usage - Relevance 10/10
- `/Users/jon/source/vibes/infra/rag-service/backend/tests/conftest.py`: Pytest fixtures, test data factories - Relevance 10/10
- `/Users/jon/source/vibes/infra/rag-service/backend/src/api/routes/documents.py`: Document upload pipeline, file validation - Relevance 10/10
- `/Users/jon/source/vibes/infra/rag-service/backend/src/api/routes/crawls.py`: CRUD pattern, status validation - Relevance 9/10
- `/Users/jon/source/vibes/infra/rag-service/backend/src/services/document_service.py`: Service layer pattern, connection pooling - Relevance 9/10
- `/Users/jon/source/vibes/infra/rag-service/frontend/src/components/CrawlManagement.tsx`: React CRUD component, delete confirmation - Relevance 10/10
- `/Users/jon/source/vibes/infra/rag-service/frontend/src/components/SourceManagement.tsx`: Table-based management UI - Relevance 9/10
- `.claude/patterns/browser-validation.md`: Browser testing workflow, pre-flight checks, accessibility tree usage - Relevance 10/10

### Testing Infrastructure Already Present
- `pytest` with `pytest-asyncio` for async test execution
- `unittest.mock` for AsyncMock and MagicMock
- FastAPI TestClient for API integration tests
- Comprehensive fixture library in `conftest.py`
- Docker Compose for service orchestration
- React Hook Form for frontend validation

### Known Test Gaps (To Be Filled)
- ❌ Document upload API tests (validation, multipart/form-data handling)
- ❌ Document CRUD operation tests (list, get, delete)
- ❌ Search source filtering tests (with/without source_id parameter)
- ❌ Cascade delete tests (document → chunks foreign key)
- ❌ Browser validation for document upload workflow
- ❌ Browser validation for search filtering
- ❌ Browser validation for delete operations
- ❌ DocumentsManagement.tsx component (doesn't exist yet)
- ❌ Error handling tests (network failures, invalid inputs)
- ❌ Performance tests (upload time, search latency)

---

## Next Steps for Assembler

When generating the PRP:

1. **Reference these patterns in "Current Codebase Tree" section**:
   - Link to test_crawl_api.py as template for API tests
   - Reference conftest.py for fixture patterns
   - Point to CrawlManagement.tsx for React component structure
   - Include browser-validation.md pattern reference

2. **Include key code snippets in "Implementation Blueprint"**:
   - FastAPI TestClient setup with dependency override
   - AsyncMock side_effect pattern for sequential returns
   - React component structure with delete confirmation
   - Browser validation pre-flight checks

3. **Add anti-patterns to "Known Gotchas" section**:
   - Hard-coded element refs (use semantic queries)
   - Manual sleep() instead of auto-wait
   - Screenshots for validation (use accessibility tree)
   - Storing connections instead of pool
   - %s placeholders instead of $1, $2

4. **Use file organization for "Desired Codebase Tree"**:
   ```
   tests/
   ├── conftest.py (extend with document fixtures)
   ├── unit/
   │   ├── test_document_api.py (NEW)
   │   └── test_search_filtering.py (NEW)
   ├── integration/
   │   ├── test_document_crud.py (NEW)
   │   └── test_cascade_deletes.py (NEW)
   └── browser/
       ├── test_document_upload.py (NEW)
       ├── test_search_filtering.py (NEW)
       └── test_delete_operations.py (NEW)

   frontend/src/components/
   └── DocumentsManagement.tsx (NEW - clone CrawlManagement.tsx)
   ```

5. **Emphasize reuse over creation**:
   - Extend conftest.py fixtures, don't create new fixture files
   - Follow test_crawl_api.py structure exactly
   - Clone CrawlManagement.tsx for DocumentsManagement.tsx
   - Use existing API client patterns

6. **Include quality gates in execution plan**:
   - Level 1: Syntax & Style (~5s)
   - Level 2: Unit Tests (~30s)
   - Level 3a: API Integration (~60s)
   - Level 3b: Browser Integration (~120s)

7. **Provide concrete validation criteria**:
   - >80% code coverage (from feature-analysis.md)
   - All error status codes tested (400, 404, 422, 500)
   - Pre-flight checks pass for browser tests
   - Screenshots generated for proof
   - All tests run in <210s total

---

**Generated**: 2025-10-16
**Source**: Codebase Researcher (Phase 2A)
**Coverage**: Backend testing (FastAPI, pytest, AsyncMock), Frontend patterns (React, CRUD), Browser validation (Playwright MCP)
**Quality Score**: 9.5/10
**Lines**: 1200+
