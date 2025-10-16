# RAG Service Testing & Validation - Code Examples

## Overview

This directory contains 6 extracted code examples demonstrating testing patterns for the RAG service. These examples provide copy-paste ready patterns for backend testing (pytest), frontend testing (React), and browser validation (Playwright).

**Purpose**: Study these before implementing tests. Each example shows "what to mimic", "what to adapt", and "what to skip".

## Examples in This Directory

| File | Source | Pattern | Relevance |
|------|--------|---------|-----------|
| example_1_test_fixtures.py | tests/conftest.py | Pytest fixtures with async mocks | 10/10 |
| example_2_fastapi_test_pattern.py | tests/integration/test_crawl_api.py | FastAPI TestClient integration tests | 9/10 |
| example_3_file_upload_validation.py | src/api/routes/documents.py | File upload security validation | 9/10 |
| example_4_react_component_pattern.py | frontend/src/components/CrawlManagement.tsx | React CRUD component structure | 10/10 |
| example_5_browser_validation_workflow.py | .claude/patterns/browser-validation.md | Playwright browser automation | 10/10 |
| example_6_api_client_patterns.py | frontend/src/api/client.ts | API client with typed requests | 8/10 |

---

## Example 1: Test Fixtures

**File**: `example_1_test_fixtures.py`
**Source**: `infra/rag-service/backend/tests/conftest.py`
**Relevance**: 10/10

### What to Mimic

- **Fixture Structure**: Organize fixtures by category (Database, Services, Test Data, Async Support)
  ```python
  @pytest.fixture
  def mock_db_pool():
      """Mock asyncpg connection pool for unit tests."""
      pool = MagicMock()
      conn = MagicMock()
      conn.fetchrow = AsyncMock()
      conn.fetchval = AsyncMock()
      conn.fetch = AsyncMock()
      conn.execute = AsyncMock()

      async def mock_acquire():
          yield conn

      pool.acquire = MagicMock(return_value=mock_acquire())
      return pool
  ```

- **Async Context Manager Mocking**: Essential for database pool connections
  ```python
  async def mock_acquire():
      yield conn

  pool.acquire = MagicMock(return_value=mock_acquire())
  ```

- **Service Mocks**: OpenAI, Qdrant clients with AsyncMock
  ```python
  @pytest.fixture
  def mock_openai_client():
      client = AsyncMock(spec=AsyncOpenAI)
      client.embeddings.create = AsyncMock()
      return client
  ```

- **Test Data Factories**: Reusable test data (UUIDs, embeddings, chunks)
  ```python
  @pytest.fixture
  def sample_embedding():
      return [0.1] * 1536  # Valid embedding dimensions
  ```

### What to Adapt

- **New Fixtures for Document Tests**: Add `sample_document`, `sample_uploaded_file`, `mock_file_upload`
- **Database Mocks**: Add `fetchone`, `executemany` if needed for bulk operations
- **Service Mocks**: Add `mock_crawl4ai_client` for crawl testing
- **Test Data**: Add document metadata, chunk count validation data

### What to Skip

- **MCP Context Mock**: Only needed for MCP tool testing, skip for API tests
- **Event Loop Fixture**: Already exists, don't duplicate

### Pattern Highlights

```python
# KEY PATTERN: Mock async context manager for database connections
async def mock_acquire():
    yield conn  # Yield mocked connection

pool.acquire = MagicMock(return_value=mock_acquire())

# Usage in tests:
async with pool.acquire() as conn:
    result = await conn.fetchrow("SELECT 1")
```

**Why This Pattern**: AsyncMock doesn't automatically handle context managers. You must explicitly mock `__aenter__` and `__aexit__` or use an async generator like above.

### Why This Example

Fixtures are the foundation of pytest testing. This example shows how to mock async operations (database, API clients) correctly. The pattern handles the tricky async context manager case that trips up most developers.

---

## Example 2: FastAPI Test Pattern

**File**: `example_2_fastapi_test_pattern.py`
**Source**: `infra/rag-service/backend/tests/integration/test_crawl_api.py`
**Relevance**: 9/10

### What to Mimic

- **TestClient Setup**: Create FastAPI app with routes and override dependencies
  ```python
  @pytest.fixture
  def app_with_routes(mock_db_pool):
      app = FastAPI()
      app.include_router(router)
      app.dependency_overrides[get_db_pool] = lambda: mock_db_pool
      return app

  @pytest.fixture
  def client(app_with_routes):
      return TestClient(app_with_routes)
  ```

- **Side Effect Lists**: For multi-step operations (check source exists → create job → update status)
  ```python
  mock_conn.fetchval = AsyncMock(side_effect=[
      True,  # Source exists
  ])

  mock_conn.fetchrow = AsyncMock(side_effect=[
      {"id": job_id, "status": "pending"},  # Initial job
      {"id": job_id, "status": "completed"},  # After processing
  ])
  ```

- **Test Class Organization**: Group related endpoint tests
  ```python
  class TestUploadEndpoint:
      def test_upload_success(self, client, mock_db_pool):
          pass

      def test_upload_invalid_file(self, client, mock_db_pool):
          pass

      def test_upload_file_too_large(self, client, mock_db_pool):
          pass
  ```

- **Error Status Testing**: Validate error responses (400, 404, 422, 500)
  ```python
  assert response.status_code == 400
  assert "source not found" in str(response.json()["detail"]).lower()
  ```

### What to Adapt

- **Document Routes**: Change `/api/crawls` to `/api/documents`
- **Test Data**: Use document-specific data (files, titles, types)
- **Validation Tests**: Test file extensions, size limits, MIME types
- **Cascade Delete Tests**: Verify documents cascade delete chunks

### What to Skip

- **Crawler/Ingestion Mocks**: Already tested in crawl_api tests, don't duplicate
- **Complex side_effect chains**: Simplify for document CRUD (less multi-step logic)

### Pattern Highlights

```python
# KEY PATTERN: side_effect for sequential mock returns
mock_conn.fetchrow = AsyncMock(side_effect=[
    {"id": uuid4(), "status": "pending"},  # First call
    {"id": uuid4(), "status": "completed"},  # Second call
])

# Each await conn.fetchrow() returns next item in list
```

**Why This Pattern**: Many operations involve multiple database queries. `side_effect` with a list allows you to control each sequential return value.

### Why This Example

Shows the FastAPI integration test pattern: create test app, override dependencies, use TestClient. The side_effect pattern is critical for testing multi-step operations without complex mocking logic.

---

## Example 3: File Upload Validation

**File**: `example_3_file_upload_validation.py`
**Source**: `infra/rag-service/backend/src/api/routes/documents.py`
**Relevance**: 9/10

### What to Mimic

- **Extension Whitelist**: Validate file extensions before processing
  ```python
  ALLOWED_EXTENSIONS = [".pdf", ".docx", ".txt", ".md", ".html"]

  file_extension = "." + filename.split(".")[-1].lower()
  if file_extension not in ALLOWED_EXTENSIONS:
      raise HTTPException(status_code=400, detail={
          "error": "Invalid file type",
          "suggestion": f"Upload one of: {', '.join(ALLOWED_EXTENSIONS)}"
      })
  ```

- **Size Limits**: Read file and check size before processing
  ```python
  MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

  file_content = await file.read()
  if len(file_content) > MAX_FILE_SIZE:
      raise HTTPException(status_code=413, detail={
          "error": "File too large",
          "detail": f"Size {len(file_content)} exceeds max {MAX_FILE_SIZE}"
      })
  ```

- **User-Friendly Errors**: Include error, detail, and suggestion fields
  ```python
  {
      "success": False,
      "error": "Invalid file type",
      "detail": "File extension '.exe' not allowed",
      "suggestion": "Upload one of: .pdf, .docx, .txt, .md, .html"
  }
  ```

- **MIME Type Validation**: Check Content-Type header (secondary check)
  ```python
  content_type = file.content_type or ""
  if content_type and content_type not in ALLOWED_MIME_TYPES:
      logger.warning(f"Unexpected MIME type: {content_type}")
      # Don't reject - extension check is primary
  ```

### What to Adapt

- **File Size Limits**: Adjust MAX_FILE_SIZE based on requirements (10MB for docs, maybe larger for PDFs)
- **Extension List**: Add/remove based on supported parsers
- **MIME Types**: Keep in sync with extension list
- **Magic Byte Validation**: Add if security is critical (prevents .exe → .pdf rename attacks)

### What to Skip

- **Document Creation Logic**: Focus on validation, not ingestion pipeline
- **Temporary File Handling**: This is ingestion concern, not validation

### Pattern Highlights

```python
# KEY PATTERN: Multi-level validation with helpful errors
# Level 1: Extension
if file_extension not in ALLOWED_EXTENSIONS:
    raise HTTPException(400, detail={"suggestion": "Upload .pdf, .docx..."})

# Level 2: Size
if len(file_content) > MAX_FILE_SIZE:
    raise HTTPException(413, detail={"suggestion": "Compress file..."})

# Level 3: MIME (warning, not error)
if content_type not in ALLOWED_MIME_TYPES:
    logger.warning(f"Unexpected MIME: {content_type}")
    # Don't reject - extension is primary check
```

**Why This Pattern**: Defense in depth. Extension check catches most issues, size limit prevents DoS, MIME type is informational. Each level has clear error message.

### Why This Example

File uploads are a security risk. This example shows proper validation layers: extension whitelist, size limits, MIME type checking. The error messages guide users to fix issues.

---

## Example 4: React Component Pattern

**File**: `example_4_react_component_pattern.py`
**Source**: `frontend/src/components/CrawlManagement.tsx`
**Relevance**: 10/10

### What to Mimic

- **State Management**: Use useState for component state
  ```typescript
  const [items, setItems] = useState<Item[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deletingItemId, setDeletingItemId] = useState<string | null>(null);
  ```

- **Data Loading with useCallback**: Memoize fetch functions
  ```typescript
  const loadItems = useCallback(async () => {
      setLoading(true);
      setError(null);
      try {
          const data = await listItems(filters);
          setItems(data);
      } catch (err) {
          setError(err.message);
      } finally {
          setLoading(false);
      }
  }, [filters]);

  useEffect(() => { loadItems(); }, [loadItems]);
  ```

- **Form Handling**: Use react-hook-form for validation
  ```typescript
  const { register, handleSubmit, formState: { errors }, reset } = useForm({
      defaultValues: { field1: 'default' }
  });

  const onSubmit = async (data) => {
      await createItem(data);
      reset();
      await loadItems();
  };
  ```

- **Delete Confirmation Modal**: Two-step delete (click → confirm)
  ```typescript
  <button onClick={() => setDeletingItemId(item.id)}>Delete</button>

  {deletingItemId && (
      <Modal>
          <button onClick={() => handleDelete(deletingItemId)}>Confirm</button>
          <button onClick={() => setDeletingItemId(null)}>Cancel</button>
      </Modal>
  )}
  ```

- **Status Badges**: Visual status indicators
  ```typescript
  const getStatusStyle = (status) => {
      switch (status) {
          case 'completed': return styles.statusCompleted;  // Green
          case 'failed': return styles.statusFailed;        // Red
          default: return styles.statusDefault;              // Gray
      }
  };
  ```

- **Auto-Refresh**: Poll for active jobs/processes
  ```typescript
  useEffect(() => {
      const hasActive = items.some(i => i.status === 'running');
      if (!hasActive) return;

      const interval = setInterval(loadItems, 5000);
      return () => clearInterval(interval);
  }, [items, loadItems]);
  ```

### What to Adapt

- **Data Model**: Change from CrawlJob to Document (different fields)
- **Filters**: Add document type, source_id filters
- **Display Fields**: Show title, type, chunk count, created date (not pages crawled)
- **Actions**: Remove "Abort" (documents don't have running state), keep "Delete"
- **Auto-Refresh**: Not needed for documents (no background processing)

### What to Skip

- **Progress Bars**: Documents don't have progress (upload is instant)
- **Status Filters**: Documents don't have status (always "completed")
- **Expandable Details**: Simpler for documents (less metadata)

### Pattern Highlights

```typescript
// KEY PATTERN: Delete confirmation modal
const [deletingItemId, setDeletingItemId] = useState<string | null>(null);

// Step 1: Click delete button
<button onClick={(e) => {
    e.stopPropagation();  // Prevent row click
    setDeletingItemId(item.id);
}}>
    Delete
</button>

// Step 2: Show modal and confirm
{deletingItemId && (
    <Modal>
        <p>Are you sure? This action cannot be undone.</p>
        <button onClick={() => {
            await deleteItem(deletingItemId);
            setDeletingItemId(null);
            await loadItems();
        }}>
            Confirm Delete
        </button>
        <button onClick={() => setDeletingItemId(null)}>
            Cancel
        </button>
    </Modal>
)}
```

**Why This Pattern**: Two-step delete prevents accidental deletions. Modal provides clear confirmation UI. `e.stopPropagation()` prevents triggering row click when clicking delete.

### Why This Example

CrawlManagement is the perfect template for DocumentsManagement. Both are CRUD UIs with lists, forms, filters, and delete operations. The patterns (state management, loading states, modals) are directly applicable.

---

## Example 5: Browser Validation Workflow

**File**: `example_5_browser_validation_workflow.py`
**Source**: `.claude/patterns/browser-validation.md`
**Relevance**: 10/10

### What to Mimic

- **Pre-Flight Checks**: Verify browser installed and services running
  ```python
  # Check browser
  try:
      browser_navigate(url="about:blank")
  except Exception:
      browser_install()
      time.sleep(30)

  # Check service
  result = Bash("docker-compose ps | grep rag-service")
  if "Up" not in result.stdout:
      Bash("docker-compose up -d")
      time.sleep(10)
  ```

- **Accessibility Tree Validation**: Use `browser_snapshot()` not screenshots
  ```python
  initial_state = browser_snapshot()
  if "DocumentList" not in initial_state:
      print("❌ Page not loaded correctly")
      exit(1)
  ```

- **Semantic Queries**: Stable element selection
  ```python
  browser_click(element="button containing 'Upload'")
  browser_type(element="textbox", name="title", text="Test Doc")
  ```

- **Auto-Wait**: Use `browser_wait_for()` with conditions
  ```python
  browser_wait_for(text="Upload successful", timeout=30000)
  ```

- **Validation Checklist**: Multiple checks with clear status
  ```python
  validation_checks = {
      "success_message": "Upload successful" in final_state,
      "document_in_list": "Test Document" in final_state,
      "list_visible": "DocumentList" in final_state,
  }

  if all(validation_checks.values()):
      print("✅ All validations passed")
  else:
      for check, passed in validation_checks.items():
          print(f"{'✅' if passed else '❌'} {check}")
  ```

- **Screenshot for Proof**: One at end for human review
  ```python
  # After validation
  browser_take_screenshot(filename="validation-proof.png")
  ```

### What to Adapt

- **Service Port**: Change 5173 to match frontend port
- **Expected Text**: Change "DocumentList" to actual page elements
- **Form Fields**: Adapt to document upload form structure
- **Timeouts**: 5s for UI, 30s for uploads, adjust as needed

### What to Skip

- **Complex Retry Logic**: Start simple, add retries if needed
- **Service Identity Check**: Only needed if port conflicts are common
- **Multiple Screenshots**: One at end is sufficient

### Pattern Highlights

```python
# KEY PATTERN: Navigation → Interaction → Validation
# Step 1: Navigate and verify initial state
browser_navigate(url="http://localhost:5173")
state = browser_snapshot()
assert "DocumentList" in state

# Step 2: Interact with UI
browser_click(element="button containing 'Upload'")
browser_wait_for(text="Select a document", timeout=5000)
browser_fill_form(fields=[
    {"name": "file", "type": "file", "value": "/tmp/test.pdf"}
])
browser_click(element="button containing 'Submit'")
browser_wait_for(text="Upload successful", timeout=30000)

# Step 3: Validate final state
final_state = browser_snapshot()
assert "test.pdf" in final_state
browser_take_screenshot(filename="proof.png")
```

**Why This Pattern**: Separates concerns. Navigation verifies page loaded. Interaction simulates user actions. Validation checks expected outcome. Screenshot provides human-readable proof.

### Why This Example

This is the gold standard browser validation workflow. Pre-flight checks prevent common failures. Accessibility tree validation is agent-parseable. Semantic queries are stable. Auto-wait prevents flaky tests. This pattern should be used for ALL browser tests.

---

## Example 6: API Client Patterns

**File**: `example_6_api_client_patterns.py`
**Source**: `frontend/src/api/client.ts`
**Relevance**: 8/10

### What to Mimic

- **Client Configuration**: BaseURL, timeout, headers
  ```typescript
  const apiClient = axios.create({
      baseURL: 'http://localhost:8003',
      timeout: 30000,
      headers: { 'Content-Type': 'application/json' }
  });
  ```

- **Error Interceptor**: Global error handling
  ```typescript
  apiClient.interceptors.response.use(
      (response) => response,
      (error) => {
          const message = error.response?.data?.error || error.message;
          throw new Error(message);
      }
  );
  ```

- **FormData for File Uploads**: Multipart/form-data
  ```typescript
  const formData = new FormData();
  formData.append('file', file);
  formData.append('title', title);

  await apiClient.post('/api/documents', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
  });
  ```

- **Query Parameters**: Use `params` option
  ```typescript
  await apiClient.get('/api/documents', {
      params: { page: 1, per_page: 10, source_id: 'uuid' }
  });
  ```

### What to Adapt

- **Python HTTP Client**: Use httpx or requests instead of axios
  ```python
  import httpx

  async with httpx.AsyncClient(base_url="http://localhost:8003", timeout=30.0) as client:
      response = await client.get("/api/documents")
  ```

- **Type Definitions**: Convert TypeScript interfaces to Pydantic models
  ```python
  from pydantic import BaseModel

  class DocumentResponse(BaseModel):
      id: str
      title: str
      created_at: datetime
  ```

- **FormData in Python**: Use `files` parameter
  ```python
  files = {'file': ('test.pdf', open('test.pdf', 'rb'), 'application/pdf')}
  data = {'title': 'Test', 'source_id': 'uuid'}
  response = await client.post('/api/documents', files=files, data=data)
  ```

### What to Skip

- **Runtime URL Detection**: Not needed for backend tests (use fixed localhost)
- **Browser-Specific Logic**: window.location checks not applicable

### Pattern Highlights

```python
# KEY PATTERN: Testing API calls in Python
@pytest.mark.asyncio
async def test_upload_document(async_client):
    # Prepare file
    files = {'file': ('test.pdf', b'content', 'application/pdf')}
    data = {'title': 'Test', 'source_id': 'uuid'}

    # Make request
    response = await async_client.post('/api/documents', files=files, data=data)

    # Assert response
    assert response.status_code == 201
    json_data = response.json()
    assert json_data['title'] == 'Test'
    assert 'id' in json_data
```

**Why This Pattern**: Integration tests should match real API usage. Using FormData for files, query params for filters, JSON bodies for search - these match frontend API client patterns.

### Why This Example

Shows how frontend calls backend APIs. Integration tests should match these patterns. Helps understand request/response structure, error handling, and FormData usage for file uploads.

---

## Usage Instructions

### Study Phase

1. **Read each example file** in order (1 → 6)
2. **Understand the attribution headers** (source file, lines, pattern, relevance)
3. **Focus on "What to Mimic" sections** - these are the core patterns to copy
4. **Note "What to Adapt" sections** - these need customization for your feature
5. **Review "Pattern Highlights"** - these show the KEY code patterns with explanations

### Application Phase

1. **Copy patterns from examples** - Don't reinvent, adapt proven patterns
2. **Adapt variable names and logic** - Change crawl → document, job → upload, etc.
3. **Skip irrelevant sections** - Don't copy progress bars if not needed
4. **Combine multiple patterns** - Use fixtures (Ex1) + TestClient (Ex2) together
5. **Test your implementations** - Run pytest and verify tests pass

### Testing Patterns

**Backend Testing Workflow**:
```python
# 1. Import fixtures from Example 1
from tests.conftest import mock_db_pool, sample_document_id

# 2. Create test app with dependencies (Example 2)
@pytest.fixture
def app_with_routes(mock_db_pool):
    app = FastAPI()
    app.include_router(documents_router)
    app.dependency_overrides[get_db_pool] = lambda: mock_db_pool
    return app

# 3. Write tests using TestClient
def test_upload_document(client, mock_db_pool):
    # Use patterns from Example 3 for validation logic
    pass
```

**Frontend Testing Workflow**:
```python
# 1. Use browser validation pattern (Example 5)
def validate_document_upload():
    # Pre-flight checks
    if not check_browser_installed():
        browser_install()

    # Navigate and interact
    browser_navigate(url="http://localhost:5173")
    browser_click(element="button containing 'Upload'")

    # Validate
    state = browser_snapshot()
    assert "Upload successful" in state
```

**Component Development Workflow**:
```typescript
// Use React patterns from Example 4
import { useState, useEffect, useCallback } from 'react';
import { listDocuments, deleteDocument } from '../api/client';

export default function DocumentsManagement() {
    const [documents, setDocuments] = useState([]);
    const [deletingId, setDeletingId] = useState(null);

    const loadDocuments = useCallback(async () => {
        const data = await listDocuments();
        setDocuments(data);
    }, []);

    // Delete confirmation modal pattern
    // Auto-refresh pattern (if needed)
    // Form handling pattern
}
```

---

## Pattern Summary

### Common Patterns Across Examples

1. **Async Context Managers**: Mock with async generators (Ex1)
2. **Side Effect Lists**: Sequential mock returns for multi-step ops (Ex2)
3. **Validation Layers**: Extension → Size → MIME type (Ex3)
4. **State Management**: useState + useEffect + useCallback (Ex4)
5. **Browser Pre-Flight**: Check browser + services before tests (Ex5)
6. **Error Handling**: Extract error, detail, suggestion from responses (Ex6)

### Anti-Patterns Observed

1. **❌ Using sleep() instead of browser_wait_for()** - Flaky tests
2. **❌ Hard-coding element refs** - Breaks on re-render
3. **❌ Using screenshots for validation** - Agents can't parse images
4. **❌ Skipping pre-flight checks** - Wastes time on known failures
5. **❌ Not using side_effect for multi-step** - Complex mocking logic
6. **❌ Mixing sync and async APIs** - Thread safety issues

---

## Integration with PRP

These examples should be:

1. **Referenced** in PRP "All Needed Context" section
   ```markdown
   ## Examples
   Study these before implementation:
   - Example 1: Test fixtures pattern
   - Example 2: FastAPI integration tests
   - Example 5: Browser validation workflow
   ```

2. **Studied** before implementation
   - Read all examples first
   - Understand patterns before coding
   - Identify which patterns apply to your task

3. **Adapted** for the specific feature needs
   - Copy patterns, not entire files
   - Customize for document vs crawl jobs
   - Combine multiple patterns as needed

4. **Extended** if additional patterns emerge
   - Add new examples if novel patterns discovered
   - Document gotchas encountered
   - Update README with lessons learned

---

## Source Attribution

### From Local Codebase

- **tests/conftest.py**: Test fixtures with async mocking
- **tests/integration/test_crawl_api.py**: FastAPI integration test patterns
- **src/api/routes/documents.py**: File upload validation logic
- **frontend/src/components/CrawlManagement.tsx**: React CRUD component
- **frontend/src/api/client.ts**: API client patterns

### From Documentation

- **.claude/patterns/browser-validation.md**: Browser automation workflow

---

## Quality Assessment

- **Coverage**: 10/10 - Examples cover all major patterns needed (fixtures, API tests, file uploads, React, browser, API client)
- **Relevance**: 9.2/10 - All examples directly applicable to RAG service testing
- **Completeness**: 9/10 - Examples are self-contained with clear attribution
- **Clarity**: 9/10 - Each example has "What to Mimic/Adapt/Skip" guidance
- **Overall**: 9.3/10

---

Generated: 2025-10-16
Feature: rag_service_testing_validation
Total Examples: 6
Pattern Coverage: Comprehensive (backend, frontend, browser, fixtures, validation)
