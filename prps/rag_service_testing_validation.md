# PRP: RAG Service Testing & Validation

**Generated**: 2025-10-16
**Based On**: prps/INITIAL_rag_service_testing_validation.md
**Feature**: Comprehensive testing and validation for RAG service

---

## Goal

Implement comprehensive testing infrastructure for the RAG service, validating recent features (document upload, search filtering, delete operations) using a 4-level quality gate strategy (Syntax → Unit → API Integration → Browser Validation). Create missing DocumentsManagement.tsx component with full CRUD operations and browser-based validation.

**End State**:
- >80% test coverage for backend document/search/delete operations
- Frontend browser validation using Playwright MCP tools for complete user workflows
- DocumentsManagement.tsx component with delete confirmation and source filtering
- Quality gates implemented and running in <210s total (5s + 30s + 60s + 120s)
- Known Crawl4AI truncation issue documented with investigation approach

## Why

**Current Pain Points**:
- Recently implemented features (document upload, source filtering, delete) have no automated tests
- No validation that frontend UI correctly integrates with backend APIs
- Risk of regressions when adding new features or refactoring
- DocumentsManagement page missing from frontend (only CrawlManagement and SourceManagement exist)
- No systematic validation of error handling and edge cases

**Business Value**:
- Prevents production bugs through comprehensive validation
- Enables confident refactoring and feature development
- Reduces manual testing time (automated validation in <4 minutes)
- Provides proof of functionality via browser test screenshots
- Improves developer velocity through fast feedback loops

## What

### Core Features

**Backend Testing**:
- Unit tests for document upload validation (file type, size, MIME checking)
- Integration tests for FastAPI endpoints (POST /upload, GET /documents, DELETE /documents/:id)
- Search filtering tests (with/without source_id parameter)
- Cascade delete tests (document → chunks foreign key validation)
- Error handling tests (400, 404, 413, 422, 500 status codes)

**Frontend Browser Testing**:
- Document upload workflow validation (navigate → fill form → submit → verify)
- Search filtering validation (select source filter → verify results)
- Delete operation validation (click delete → confirm → verify removal)
- New DocumentsManagement.tsx component with CRUD operations

**Quality Gates (4 Levels)**:
1. **Syntax & Style** (~5s): ruff, mypy type checking
2. **Unit Tests** (~30s): pytest with >80% coverage
3. **API Integration** (~60s): FastAPI TestClient tests
4. **Browser Integration** (~120s): Playwright browser automation

### Success Criteria

**Backend Validation**:
- ✅ All unit tests pass with >80% coverage
- ✅ All integration tests pass (API endpoints validated)
- ✅ Type checking passes (mypy zero errors)
- ✅ Linting passes (ruff zero violations)
- ✅ Tests run in <90s total (unit 30s + integration 60s)

**Frontend Validation**:
- ✅ Browser binaries installed (pre-flight check passes)
- ✅ Services running (docker-compose verified)
- ✅ All browser tests pass (upload, filter, delete workflows)
- ✅ Screenshots captured for proof (one per test case)
- ✅ No console errors in browser
- ✅ Tests run in <120s

**End-to-End**:
- ✅ Complete workflow test (create source → upload → search → delete)
- ✅ DocumentsManagement.tsx component deployed and functional
- ✅ Error states handled gracefully
- ✅ CI/CD pipeline includes all quality gates

---

## All Needed Context

### Documentation & References

```yaml
# MUST READ - Testing Frameworks
- url: https://docs.pytest.org/en/stable/how-to/fixtures.html
  sections:
    - "How to use fixtures" - Fixture scopes and autouse
    - "Fixtures reference" - conftest.py patterns
  why: Foundation for test data setup and dependency injection
  critical_gotchas:
    - conftest.py fixtures auto-discovered, no imports needed
    - Fixture scope must match event loop scope for async fixtures

- url: https://pytest-asyncio.readthedocs.io/en/latest/concepts.html
  sections:
    - "Concepts" - Event loop management, test discovery modes
    - "Fixtures" - Async fixture patterns
  why: Essential for testing async FastAPI endpoints and database operations
  critical_gotchas:
    - Module-scoped async fixtures need module-scoped event_loop
    - Tests run sequentially, not concurrently (prevents race conditions)

- url: https://fastapi.tiangolo.com/advanced/testing-dependencies/
  sections:
    - "Testing Dependencies with Overrides"
  why: Mock database pools and external APIs in integration tests
  critical_gotchas:
    - app.dependency_overrides is global, must reset after each test
    - Override key must be exact function object, not different import

- url: https://playwright.dev/python/docs/locators
  sections:
    - "Locators" - Semantic element queries
    - "Auto-waiting" - Actionability checks
  why: Browser automation for frontend validation
  critical_gotchas:
    - Element refs change every render (use semantic queries)
    - Default timeout 30s (set per-operation timeouts: 5s UI, 30s uploads)

# MUST READ - Library APIs
- url: https://docs.python.org/3/library/unittest.mock.html
  sections:
    - "AsyncMock" - Mocking async functions
    - "side_effect" - Sequential mock returns
  why: Mock asyncpg database operations and OpenAI API calls
  critical_gotchas:
    - AsyncMock exceptions not raised until awaited
    - Async context managers need __aenter__/__aexit__ mocks

- url: https://magicstack.github.io/asyncpg/current/usage.html
  sections:
    - "Connection Pools" - Pool management
    - "Transactions" - Transaction handling
  why: Understand connection pooling and transaction patterns
  critical_gotchas:
    - Store pool not connection in service __init__
    - Cannot rollback after failed commit (use context managers)
    - Use $1, $2 placeholders not %s

- url: https://testdriven.io/blog/fastapi-crud/
  sections:
    - "Testing" - Async database testing patterns
  why: Complete working example of FastAPI + asyncpg testing
  critical_gotchas:
    - Use AsyncClient for async endpoint tests
    - Transaction rollback for test isolation

# ESSENTIAL LOCAL FILES
- file: /Users/jon/source/vibes/prps/rag_service_testing_validation/examples/README.md
  why: Comprehensive guide with "What to Mimic/Adapt/Skip" for all 6 examples
  pattern: Study before implementation, reference during coding

- file: /Users/jon/source/vibes/prps/rag_service_testing_validation/examples/example_1_test_fixtures.py
  why: Reusable pytest fixtures (mock_db_pool, mock_openai_client, test data factories)
  pattern: Copy fixture structure, adapt mock behavior for new services
  critical: Async context manager mocking (async generator pattern)

- file: /Users/jon/source/vibes/prps/rag_service_testing_validation/examples/example_2_fastapi_test_pattern.py
  why: FastAPI TestClient with dependency injection and error status testing
  pattern: Test class per endpoint, multiple test methods per status code
  critical: side_effect lists for multi-step database operations

- file: /Users/jon/source/vibes/prps/rag_service_testing_validation/examples/example_3_file_upload_validation.py
  why: Multi-layer file validation (extension, size, MIME type)
  pattern: Defensive validation with user-friendly error messages
  critical: Extension whitelist, magic byte validation for security

- file: /Users/jon/source/vibes/prps/rag_service_testing_validation/examples/example_4_react_component_pattern.py
  why: React CRUD component structure for DocumentsManagement.tsx
  pattern: useState + useEffect + useCallback + react-hook-form
  critical: Delete confirmation modal (two-step pattern)

- file: /Users/jon/source/vibes/prps/rag_service_testing_validation/examples/example_5_browser_validation_workflow.py
  why: Complete browser automation workflow (pre-flight → navigate → interact → validate)
  pattern: Accessibility tree validation, semantic queries, auto-wait
  critical: Pre-flight checks (browser installed, services running)

- file: /Users/jon/source/vibes/infra/rag-service/backend/tests/conftest.py
  why: Existing fixture library - extend, don't recreate
  pattern: Add sample_document, sample_source fixtures to existing file
  critical: Use existing mock patterns (mock_db_pool, mock_openai_client)

- file: /Users/jon/source/vibes/infra/rag-service/backend/tests/integration/test_crawl_api.py
  why: Integration test pattern reference (TestClient with mocked dependencies)
  pattern: Test class organization, error handling tests
  critical: Override get_db_pool dependency in app fixture

- file: /Users/jon/source/vibes/infra/rag-service/frontend/src/components/CrawlManagement.tsx
  why: Template for DocumentsManagement.tsx component
  pattern: Clone structure (list, create, delete, filters, modals)
  critical: Auto-refresh pattern, status badges, confirmation modal

- file: /Users/jon/source/vibes/.claude/patterns/browser-validation.md
  why: Complete browser testing pattern documentation
  pattern: Pre-flight checks, navigation → interaction → validation workflow
  critical: Use browser_snapshot() for validation, screenshots for proof only
```

### Current Codebase Tree

```
infra/rag-service/
├── backend/
│   ├── src/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── documents.py           # Upload endpoint (lines 174-283)
│   │   │   │   ├── crawls.py              # CRUD pattern reference
│   │   │   │   └── sources.py             # Source management
│   │   │   └── dependencies.py            # get_db_pool, get_openai_client
│   │   ├── services/
│   │   │   ├── document_service.py        # list_documents(), create_document()
│   │   │   ├── vector_service.py          # Qdrant operations
│   │   │   ├── ingestion_service.py       # Pipeline orchestration
│   │   │   └── embeddings/
│   │   │       └── embedding_service.py   # OpenAI embeddings
│   │   └── config/
│   │       └── settings.py                # DATABASE_URL, OPENAI_API_KEY
│   └── tests/
│       ├── conftest.py                    # Existing fixtures (EXTEND, don't replace)
│       ├── integration/
│       │   └── test_crawl_api.py          # Pattern reference for API tests
│       └── (NEW: unit/, integration/, browser/ subdirectories)
│
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── CrawlManagement.tsx        # Template for DocumentsManagement
│       │   ├── SourceManagement.tsx       # Table-based management UI
│       │   └── SearchInterface.tsx        # Search with source filtering
│       └── api/
│           └── client.ts                  # API client functions
│
└── docker-compose.yaml                    # Service orchestration
```

### Desired Codebase Tree

```
infra/rag-service/backend/tests/
├── conftest.py                            # EXTEND with new fixtures
├── unit/                                  # NEW: Level 2 tests
│   ├── test_document_service.py           # Service layer unit tests
│   ├── test_file_validation.py            # File upload validation tests
│   └── test_search_filtering.py           # Search with source_id tests
├── integration/                           # EXTEND: Level 3a tests
│   ├── test_crawl_api.py                  # Existing (keep)
│   ├── test_document_api.py               # NEW: Document CRUD endpoints
│   ├── test_delete_cascade.py             # NEW: Foreign key validation
│   └── test_search_api.py                 # NEW: Search filtering endpoint
└── browser/                               # NEW: Level 3b tests
    ├── test_document_upload.py            # Upload workflow validation
    ├── test_search_filtering.py           # Filter UI validation
    └── test_delete_operations.py          # Delete confirmation validation

infra/rag-service/frontend/src/components/
└── DocumentsManagement.tsx                # NEW: Document CRUD component

**New Files to Create**:
1. tests/unit/test_document_service.py
2. tests/unit/test_file_validation.py
3. tests/unit/test_search_filtering.py
4. tests/integration/test_document_api.py
5. tests/integration/test_delete_cascade.py
6. tests/integration/test_search_api.py
7. tests/browser/test_document_upload.py
8. tests/browser/test_search_filtering.py
9. tests/browser/test_delete_operations.py
10. frontend/src/components/DocumentsManagement.tsx

**Files to Modify**:
- tests/conftest.py (add sample_document, sample_source fixtures)
```

### Known Gotchas & Library Quirks

```python
# CRITICAL: Browser binaries not installed
# Symptom: playwright._impl._api_types.Error: Executable doesn't exist
# Fix: Pre-flight check with auto-install

def ensure_browser_installed():
    """Verify browser binaries installed, auto-install if missing."""
    try:
        browser_navigate(url="about:blank")
        print("✅ Browser binaries installed")
    except Exception as e:
        if "Executable doesn't exist" in str(e):
            print("⚠️ Browser binaries missing, installing...")
            browser_install()
            time.sleep(30)
        else:
            raise

# CRITICAL: Frontend services not running
# Symptom: net::ERR_CONNECTION_REFUSED in browser tests
# Fix: Pre-flight check with service identity verification

def ensure_frontend_running(port: int, service_name: str):
    """Verify frontend service running and accessible."""
    result = subprocess.run(["docker-compose", "ps", service_name],
                           capture_output=True, text=True)
    if "Up" not in result.stdout:
        print(f"⚠️ {service_name} not running, starting services...")
        subprocess.run(["docker-compose", "up", "-d"], check=True)
        time.sleep(10)

    # Verify service identity (prevent port conflicts)
    result = subprocess.run(["curl", "-s", f"http://localhost:{port}"],
                           capture_output=True, text=True, timeout=5)
    if service_name.lower() not in result.stdout.lower():
        raise ValueError(f"Port conflict: expected {service_name} at {port}")

# CRITICAL: FastAPI dependency overrides not cleaned up
# Symptom: Tests pass alone but fail when run together
# Fix: Fixture with automatic cleanup

@pytest.fixture
def override_db(mock_db_pool):
    """Override database dependency with automatic cleanup."""
    from src.api.dependencies import get_db_pool
    from src.main import app

    app.dependency_overrides[get_db_pool] = lambda: mock_db_pool
    yield
    app.dependency_overrides = {}  # Reset all overrides

# CRITICAL: AsyncMock exceptions not raised until awaited
# Symptom: Test expects exception but gets coroutine object
# Fix: Always await AsyncMock calls

mock_conn.fetchval = AsyncMock(side_effect=ValueError("DB error"))

# ❌ WRONG - Doesn't raise exception
result = mock_conn.fetchval("SELECT 1")  # Returns coroutine

# ✅ RIGHT - Exception raised when awaited
with pytest.raises(ValueError, match="DB error"):
    await mock_conn.fetchval("SELECT 1")

# CRITICAL: Playwright element refs change every render
# Symptom: Error: No element found matching selector
# Fix: Use semantic queries, not refs

# ❌ WRONG - Brittle refs
browser_click(ref="e5")  # This ref is ephemeral!

# ✅ RIGHT - Semantic queries (stable)
browser_click(element="button containing 'Upload'")
browser_fill_form(fields=[
    {"name": "file", "type": "file", "value": "/tmp/test.pdf"},
    {"name": "title", "type": "textbox", "value": "Test Document"}
])
browser_wait_for(text="Upload successful", timeout=30000)

# CRITICAL: Async context manager mocking requires __aenter__/__aexit__
# Symptom: AttributeError: __aenter__
# Fix: Mock async context manager with async generator

mock_pool = MagicMock()
mock_conn = MagicMock()
mock_conn.fetchval = AsyncMock(return_value="result")

# Mock async context manager
async def mock_acquire():
    yield mock_conn

mock_pool.acquire = MagicMock(return_value=mock_acquire())

# Now this works
async with mock_pool.acquire() as conn:
    result = await conn.fetchval("SELECT 1")

# CRITICAL: asyncpg uses $1, $2 placeholders, not %s
# Symptom: syntax error at or near "%"
# Fix: Use asyncpg-style placeholders

# ❌ WRONG - psycopg2 style
query = "SELECT * FROM documents WHERE id = %s"

# ✅ RIGHT - asyncpg style
query = "SELECT * FROM documents WHERE id = $1"
result = await conn.fetchrow(query, doc_id)

# CRITICAL: File upload TestClient requires specific format
# Symptom: 422 Unprocessable Entity - "Field required: file"
# Fix: Use files parameter with tuple (filename, content, content_type)

# ❌ WRONG - Wrong format
response = client.post("/api/upload",
    data={"file": open("/tmp/test.pdf", "rb")})

# ✅ RIGHT - Correct tuple format
from io import BytesIO

file_content = b"test file content"
file = BytesIO(file_content)

response = client.post("/api/upload",
    data={"title": "Test Document", "source_id": "123"},
    files={"file": ("test.pdf", file, "application/pdf")}
)

# CRITICAL: Browser screenshots for validation (anti-pattern)
# Symptom: Agent cannot validate from screenshot
# Fix: Use accessibility tree (browser_snapshot) for validation

# ❌ WRONG - Screenshot for validation
screenshot = browser_take_screenshot("state.png")
# Agent can't parse images!

# ✅ RIGHT - Accessibility tree for validation
snapshot = browser_snapshot()  # ~500 tokens, agent-parseable
validation_checks = {
    "page_loaded": "Document Management" in snapshot,
    "upload_button": "Upload" in snapshot
}
if all(validation_checks.values()):
    browser_take_screenshot("proof.png")  # Human proof only

# LIBRARY QUIRK: Crawl4AI content truncation
# Issue: Returns ~50 chunks instead of expected 300-400 for large documents
# Location: backend/src/services/crawler/crawl_service.py
# Status: Under investigation (see TODO.md lines 103-115)
# Workaround: Document limitation, mark tests as xfail for large documents

# For large documents, Crawl4AI may truncate content
if len(result.markdown) < 100000:
    logger.warning(f"Content may be truncated: {len(result.markdown)} bytes")
```

---

## Implementation Blueprint

### Phase 0: Planning & Understanding

**BEFORE starting implementation, complete these steps:**

1. **Read Examples Directory** (30 minutes):
   - `prps/rag_service_testing_validation/examples/README.md` cover-to-cover
   - Study Example 1 (test fixtures) - understand async context manager mocking
   - Study Example 2 (FastAPI tests) - understand dependency override pattern
   - Study Example 5 (browser validation) - understand pre-flight checks

2. **Review Existing Patterns** (20 minutes):
   - `infra/rag-service/backend/tests/conftest.py` - fixture patterns to extend
   - `infra/rag-service/backend/tests/integration/test_crawl_api.py` - test organization
   - `infra/rag-service/frontend/src/components/CrawlManagement.tsx` - component structure

3. **Verify Environment** (10 minutes):
   - `docker-compose ps` - all services running
   - `playwright install` - browser binaries available
   - `pytest --version` - pytest-asyncio installed

### Task List (Execute in Order)

```yaml
Task 1: Extend Test Fixtures
RESPONSIBILITY: Add reusable test data factories and mocks
FILES TO MODIFY:
  - infra/rag-service/backend/tests/conftest.py

PATTERN TO FOLLOW: Existing fixtures (mock_db_pool, mock_openai_client)

SPECIFIC STEPS:
  1. Add sample_document fixture (document_id, title, type, source_id, chunks)
  2. Add sample_source fixture (source_id, title, type)
  3. Add sample_chunk fixture (chunk_id, document_id, text, embedding)
  4. Add mock_uploaded_file fixture (BytesIO with PDF header)
  5. Test fixtures work: pytest tests/conftest.py --collect-only

VALIDATION:
  - No import errors when loading conftest.py
  - Fixtures discoverable by pytest (pytest --fixtures shows new ones)

---

Task 2: Unit Tests - File Upload Validation
RESPONSIBILITY: Test document upload validation logic (file type, size, MIME)
FILES TO CREATE:
  - infra/rag-service/backend/tests/unit/test_file_validation.py

PATTERN TO FOLLOW: Example 3 (file upload validation patterns)

SPECIFIC STEPS:
  1. Test extension whitelist validation (.pdf, .docx, .txt, .md, .html)
  2. Test file size limit (10MB max)
  3. Test MIME type validation (security layer)
  4. Test invalid file types (.exe, .zip rejected)
  5. Test error messages are user-friendly
  6. Run: pytest tests/unit/test_file_validation.py -v

VALIDATION:
  - All tests pass
  - Coverage >80% for validation functions

---

Task 3: Unit Tests - Document Service
RESPONSIBILITY: Test document service business logic (list, create, delete)
FILES TO CREATE:
  - infra/rag-service/backend/tests/unit/test_document_service.py

PATTERN TO FOLLOW: Example 1 (async fixtures), Example 2 (mock patterns)

SPECIFIC STEPS:
  1. Test list_documents() with filters (source_id, document_type)
  2. Test list_documents() pagination (page, per_page)
  3. Test create_document() success path
  4. Test create_document() database error handling
  5. Test delete_document() cascade to chunks
  6. Use mock_db_pool fixture with side_effect for sequential returns
  7. Run: pytest tests/unit/test_document_service.py -v

VALIDATION:
  - All tests pass
  - Async mocks configured correctly (side_effect lists work)

---

Task 4: Integration Tests - Document API
RESPONSIBILITY: Test FastAPI document endpoints (POST /upload, GET /documents, DELETE)
FILES TO CREATE:
  - infra/rag-service/backend/tests/integration/test_document_api.py

PATTERN TO FOLLOW: tests/integration/test_crawl_api.py (TestClient pattern)

SPECIFIC STEPS:
  1. Create app_with_document_routes fixture (override get_db_pool)
  2. Test POST /api/documents/upload (multipart/form-data)
  3. Test GET /api/documents (list with filters)
  4. Test DELETE /api/documents/{id} (cascade delete)
  5. Test error cases (400, 404, 413, 422, 500)
  6. Use files parameter for file uploads: files={"file": ("test.pdf", file, "application/pdf")}
  7. Run: pytest tests/integration/test_document_api.py -v

VALIDATION:
  - All status codes tested (200, 201, 400, 404, 413, 422, 500)
  - File upload format correct (multipart/form-data)
  - Dependency overrides reset after tests

---

Task 5: Integration Tests - Search Filtering
RESPONSIBILITY: Test search with source_id filter parameter
FILES TO CREATE:
  - infra/rag-service/backend/tests/integration/test_search_api.py

PATTERN TO FOLLOW: Example 2 (FastAPI TestClient with mocks)

SPECIFIC STEPS:
  1. Test POST /api/search without source_id filter
  2. Test POST /api/search with valid source_id filter
  3. Test POST /api/search with invalid source_id (400 error)
  4. Test POST /api/search with non-existent source_id (empty results)
  5. Mock Qdrant search results with source_id filtering
  6. Run: pytest tests/integration/test_search_api.py -v

VALIDATION:
  - Search returns filtered results
  - Invalid source_id returns 400 with helpful error message

---

Task 6: Integration Tests - Cascade Deletes
RESPONSIBILITY: Test foreign key constraints (document → chunks)
FILES TO CREATE:
  - infra/rag-service/backend/tests/integration/test_delete_cascade.py

PATTERN TO FOLLOW: Example 2 (multi-step database operations with side_effect)

SPECIFIC STEPS:
  1. Test delete document cascades to chunks
  2. Test delete source cascades to documents and chunks
  3. Test delete crawl job removes associated data
  4. Mock database operations with side_effect for sequential queries
  5. Run: pytest tests/integration/test_delete_cascade.py -v

VALIDATION:
  - Mock verifies cascade DELETE queries executed
  - Transaction handling correct (context managers used)

---

Task 7: Browser Tests - Document Upload Workflow
RESPONSIBILITY: Validate end-to-end upload workflow with browser automation
FILES TO CREATE:
  - infra/rag-service/backend/tests/browser/test_document_upload.py

PATTERN TO FOLLOW: Example 5 (browser validation workflow)

SPECIFIC STEPS:
  1. Add pre-flight check fixtures (browser_installed, frontend_running)
  2. Navigate to http://localhost:5173/documents
  3. Click "Upload" button using semantic query
  4. Fill form: browser_fill_form(fields=[{"name": "file", ...}, {"name": "title", ...}])
  5. Submit and wait for success: browser_wait_for(text="Upload successful", timeout=30000)
  6. Validate final state: browser_snapshot() contains document title
  7. Take proof screenshot: browser_take_screenshot("upload-proof.png")
  8. Run: pytest tests/browser/test_document_upload.py -v

VALIDATION:
  - Pre-flight checks pass (browser installed, services running)
  - No element ref usage (only semantic queries)
  - Accessibility tree used for validation, screenshot for proof only

---

Task 8: Browser Tests - Search Filtering Workflow
RESPONSIBILITY: Validate search with source filter UI
FILES TO CREATE:
  - infra/rag-service/backend/tests/browser/test_search_filtering.py

PATTERN TO FOLLOW: Example 5 (navigation → interaction → validation)

SPECIFIC STEPS:
  1. Navigate to search page
  2. Enter query in search box
  3. Select source from dropdown filter
  4. Submit search
  5. Validate filtered results in accessibility tree
  6. Change filter and verify results update
  7. Take proof screenshot
  8. Run: pytest tests/browser/test_search_filtering.py -v

VALIDATION:
  - Filter dropdown functional
  - Results update when filter changes
  - Validation uses browser_snapshot() not screenshots

---

Task 9: Browser Tests - Delete Operations Workflow
RESPONSIBILITY: Validate delete with confirmation modal
FILES TO CREATE:
  - infra/rag-service/backend/tests/browser/test_delete_operations.py

PATTERN TO FOLLOW: Example 5 (browser workflow), Example 4 (delete confirmation modal)

SPECIFIC STEPS:
  1. Navigate to documents management page
  2. Click delete button on first document
  3. Wait for confirmation modal: browser_wait_for(text="Confirm Delete")
  4. Click confirm button in modal
  5. Wait for success message
  6. Verify document removed from list
  7. Take proof screenshot
  8. Run: pytest tests/browser/test_delete_operations.py -v

VALIDATION:
  - Confirmation modal appears (two-step delete)
  - Document removed from accessibility tree after confirmation

---

Task 10: Frontend Component - DocumentsManagement.tsx
RESPONSIBILITY: Create document CRUD component with delete confirmation
FILES TO CREATE:
  - infra/rag-service/frontend/src/components/DocumentsManagement.tsx

PATTERN TO FOLLOW: CrawlManagement.tsx (state management, modals, filters)

SPECIFIC STEPS:
  1. Clone CrawlManagement.tsx structure
  2. Replace CrawlJobResponse with DocumentResponse type
  3. Update API calls: listDocuments(), deleteDocument()
  4. Modify table columns: title, type, chunk_count, source, created_at
  5. Add source filter dropdown
  6. Implement delete confirmation modal (two-step pattern)
  7. Add success/error toast notifications
  8. Test manually: npm run dev, verify CRUD operations

VALIDATION:
  - Component renders without errors
  - Delete confirmation modal appears
  - Source filter dropdown functional
  - Table displays document metadata correctly

---

Task 11: Quality Gates - Syntax & Style
RESPONSIBILITY: Ensure code passes linting and type checking
COMMAND:
  cd infra/rag-service/backend
  ruff check tests/ --fix
  mypy tests/

VALIDATION:
  - Zero ruff violations
  - Zero mypy type errors
  - Execution time: <5 seconds

---

Task 12: Quality Gates - Unit Tests
RESPONSIBILITY: Run unit tests with coverage check
COMMAND:
  cd infra/rag-service/backend
  pytest tests/unit/ -v --cov=src --cov-report=term-missing --cov-fail-under=80

VALIDATION:
  - All unit tests pass
  - Coverage >80%
  - Execution time: <30 seconds

---

Task 13: Quality Gates - Integration Tests
RESPONSIBILITY: Run API integration tests
COMMAND:
  cd infra/rag-service/backend
  pytest tests/integration/ -v

VALIDATION:
  - All integration tests pass
  - Execution time: <60 seconds

---

Task 14: Quality Gates - Browser Tests
RESPONSIBILITY: Run browser automation tests
COMMAND:
  cd infra/rag-service/backend
  pytest tests/browser/ -v

VALIDATION:
  - All browser tests pass
  - Screenshots generated in tests/browser/screenshots/
  - Execution time: <120 seconds

---

Task 15: End-to-End Validation
RESPONSIBILITY: Complete workflow test (create → upload → search → delete)
COMMAND:
  Manual test or integration test combining all operations

STEPS:
  1. Create source via API
  2. Upload document to that source
  3. Search with source_id filter
  4. Verify document in results
  5. Delete document
  6. Verify cascade to chunks

VALIDATION:
  - Complete workflow succeeds
  - Data persists correctly across operations
  - Error states handled gracefully

---

Task 16: Documentation & Cleanup
RESPONSIBILITY: Update documentation and clean up test artifacts
FILES TO MODIFY:
  - infra/rag-service/README.md (add testing section)
  - infra/rag-service/TODO.md (mark completed items)

SPECIFIC STEPS:
  1. Document how to run tests (pytest commands)
  2. Document quality gates (4 levels)
  3. Document known issues (Crawl4AI truncation)
  4. Update TODO.md with completion status
  5. Clean up temporary test files

VALIDATION:
  - README includes testing instructions
  - TODO.md updated with investigation notes
```

### Implementation Pseudocode

```python
# Task 1: Extend conftest.py fixtures
# Location: infra/rag-service/backend/tests/conftest.py

@pytest.fixture
def sample_document():
    """Sample document record for testing."""
    return {
        "id": str(uuid4()),
        "title": "Test Document",
        "type": "pdf",
        "source_id": str(uuid4()),
        "created_at": datetime.now(),
        "chunk_count": 5
    }

@pytest.fixture
def mock_uploaded_file():
    """Mock PDF file for upload testing."""
    from io import BytesIO
    content = b"%PDF-1.4\n%\xE2\xE3\xCF\xD3\nTest content\n%%EOF"
    return BytesIO(content)

# Task 2: File upload validation tests
# Location: tests/unit/test_file_validation.py

def test_valid_file_extension():
    """Test extension whitelist accepts valid types."""
    valid_extensions = [".pdf", ".docx", ".txt", ".md", ".html"]
    for ext in valid_extensions:
        filename = f"document{ext}"
        # Call validation function from routes/documents.py
        is_valid, message = validate_file_extension(filename)
        assert is_valid is True

def test_file_size_limit():
    """Test file size limit enforcement (10MB)."""
    large_file = BytesIO(b"x" * (11 * 1024 * 1024))  # 11MB
    is_valid, message = validate_file_size(large_file)
    assert is_valid is False
    assert "exceeds maximum" in message

# Task 4: FastAPI integration tests
# Location: tests/integration/test_document_api.py

@pytest.fixture
def app_with_document_routes(mock_db_pool):
    """Create FastAPI app with document routes and overrides."""
    from fastapi import FastAPI
    from src.api.routes.documents import router
    from src.api.dependencies import get_db_pool

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_db_pool] = lambda: mock_db_pool

    yield app

    # CRITICAL: Reset overrides after test
    app.dependency_overrides = {}

def test_upload_document_success(client, sample_document, mock_uploaded_file):
    """Test successful document upload."""
    # PATTERN: Use files parameter for multipart/form-data
    response = client.post(
        "/api/documents/upload",
        data={
            "title": "Test Document",
            "source_id": str(uuid4())
        },
        files={
            "file": ("test.pdf", mock_uploaded_file, "application/pdf")
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "document_id" in data
    assert data["filename"] == "test.pdf"

# Task 7: Browser upload validation
# Location: tests/browser/test_document_upload.py

@pytest.fixture(scope="session", autouse=True)
def setup_browser():
    """Ensure browser installed and services running."""
    # CRITICAL: Pre-flight check from Gotcha #1
    ensure_browser_installed()
    ensure_frontend_running(5173, "rag-service")

def test_document_upload_workflow():
    """Test complete document upload workflow."""
    # Navigate
    browser_navigate(url="http://localhost:5173/documents")

    # CRITICAL: Use semantic queries, not refs (Gotcha #5)
    browser_click(element="button containing 'Upload'")
    browser_wait_for(text="Select a document", timeout=5000)

    # Fill form
    browser_fill_form(fields=[
        {"name": "file", "type": "file", "value": "/tmp/test-document.pdf"},
        {"name": "title", "type": "textbox", "value": "Test Document"}
    ])

    browser_click(element="button containing 'Submit'")
    browser_wait_for(text="Upload successful", timeout=30000)

    # CRITICAL: Validate with accessibility tree, not screenshot (Gotcha #8)
    snapshot = browser_snapshot()
    validation_checks = {
        "success_message": "Upload successful" in snapshot,
        "document_title": "Test Document" in snapshot,
        "document_in_list": "test-document.pdf" in snapshot
    }

    if all(validation_checks.values()):
        print("✅ All validations passed")
        browser_take_screenshot(filename="upload-proof.png")  # Human proof only
    else:
        print(f"❌ Failed checks: {[k for k, v in validation_checks.items() if not v]}")
        browser_take_screenshot(filename="upload-failure.png")
        raise AssertionError("Validation failed")

# Task 10: DocumentsManagement.tsx component
# Location: frontend/src/components/DocumentsManagement.tsx

export default function DocumentsManagement() {
    // PATTERN: State management from CrawlManagement.tsx
    const [documents, setDocuments] = useState<DocumentResponse[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [sourceFilter, setSourceFilter] = useState<string>('all');
    const [deletingDocId, setDeletingDocId] = useState<string | null>(null);

    // PATTERN: Data loading with useCallback
    const loadDocuments = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const filters = sourceFilter === 'all' ? {} : { source_id: sourceFilter };
            const data = await listDocuments(filters);
            setDocuments(data.documents);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load');
        } finally {
            setLoading(false);
        }
    }, [sourceFilter]);

    useEffect(() => {
        loadDocuments();
    }, [loadDocuments]);

    // CRITICAL: Delete confirmation modal (two-step pattern from Example 4)
    const handleDeleteDocument = async (docId: string) => {
        setError(null);
        try {
            await deleteDocument(docId);
            setDeletingDocId(null);
            await loadDocuments();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to delete');
        }
    };

    return (
        <div>
            {/* Filter dropdown */}
            <select value={sourceFilter} onChange={(e) => setSourceFilter(e.target.value)}>
                <option value="all">All Sources</option>
                {/* Dynamic source options */}
            </select>

            {/* Document list */}
            {documents.map(doc => (
                <div key={doc.id}>
                    <span>{doc.title}</span>
                    <span>{doc.type}</span>
                    <span>{doc.chunk_count} chunks</span>
                    <button onClick={() => setDeletingDocId(doc.id)}>Delete</button>
                </div>
            ))}

            {/* CRITICAL: Confirmation modal */}
            {deletingDocId && (
                <div style={styles.modalOverlay}>
                    <div style={styles.modal}>
                        <h3>Confirm Delete</h3>
                        <p>Are you sure? This action cannot be undone.</p>
                        <button onClick={() => handleDeleteDocument(deletingDocId)}>
                            Delete
                        </button>
                        <button onClick={() => setDeletingDocId(null)}>
                            Cancel
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
```

---

## Validation Loop

### Level 1: Syntax & Style Checks (~5s)

```bash
cd infra/rag-service/backend

# Run linting with auto-fix
ruff check src/ tests/ --fix

# Run type checking
mypy src/

# Expected: No errors
# If errors: READ error message, understand issue, fix code, re-run
```

### Level 2: Unit Tests (~30s)

```bash
cd infra/rag-service/backend

# Run unit tests with coverage
pytest tests/unit/ -v --cov=src --cov-report=term-missing --cov-fail-under=80

# Expected: All tests pass, coverage >80%
# If failing: Read error, check mock configuration, fix test or code
# NEVER mock to pass - understand root cause first
```

### Level 3a: API Integration Tests (~60s)

```bash
cd infra/rag-service/backend

# Run integration tests
pytest tests/integration/ -v

# Expected: All tests pass
# If failing: Check dependency overrides, mock side_effect configuration
# Verify async context manager mocking (__aenter__/__aexit__)
```

### Level 3b: Browser Integration Tests (~120s)

```bash
cd infra/rag-service/backend

# Ensure services running
docker-compose up -d

# Run browser tests
pytest tests/browser/ -v

# Expected: All tests pass, screenshots in tests/browser/screenshots/
# If failing: Check pre-flight checks (browser installed, services running)
# Verify semantic queries used (not element refs)
# Check timeouts appropriate for operation (5s UI, 30s uploads)
```

---

## Final Validation Checklist

### Functional Requirements
- [ ] All unit tests pass with >80% coverage
- [ ] All integration tests pass (API endpoints validated)
- [ ] All browser tests pass (frontend workflows validated)
- [ ] DocumentsManagement.tsx component functional
- [ ] Delete confirmation modal works (two-step pattern)
- [ ] Source filter dropdown works
- [ ] Error states handled gracefully (400, 404, 413, 422, 500)

### Quality Gates
- [ ] Level 1: Syntax & Style passes (<5s) - ruff, mypy zero errors
- [ ] Level 2: Unit tests pass (<30s) - >80% coverage
- [ ] Level 3a: Integration tests pass (<60s) - all endpoints validated
- [ ] Level 3b: Browser tests pass (<120s) - all workflows validated
- [ ] Total execution time <210s for all quality gates

### Code Quality
- [ ] All critical gotchas addressed (see checklist below)
- [ ] Follows existing codebase patterns (Example 1-6)
- [ ] Error messages user-friendly with suggestions
- [ ] Logging informative but not verbose
- [ ] No hardcoded values that should be config

### Documentation
- [ ] Test results documented (pass/fail status)
- [ ] Screenshots prove functionality (in tests/browser/screenshots/)
- [ ] Known issues documented (Crawl4AI truncation in TODO.md)
- [ ] Test coverage report generated
- [ ] README.md updated with testing instructions

### Gotcha Checklist (Critical)
- [ ] Browser binaries: Pre-flight check with auto-install (Gotcha #1)
- [ ] Services running: Verify frontend/backend available (Gotcha #2)
- [ ] Dependency overrides: Automatic cleanup with fixtures (Gotcha #3)
- [ ] AsyncMock exceptions: Always await mock calls (Gotcha #4)
- [ ] Element refs: Use semantic queries, not refs (Gotcha #5)
- [ ] Event loop scope: Match fixture scope with loop scope
- [ ] Dependency reference: Use exact import path for overrides
- [ ] Transaction rollback: Use context managers for asyncpg
- [ ] Async context mocking: Mock __aenter__/__aexit__
- [ ] File upload format: Use files parameter with tuple
- [ ] File validation: Multi-layer validation with magic bytes
- [ ] File size limits: Enforce MAX_FILE_SIZE (10MB)

---

## Anti-Patterns to Avoid

```python
# ❌ DON'T: Hard-code element refs in browser tests
browser_click(ref="e5")  # Breaks on re-render!

# ✅ DO: Use semantic queries
browser_click(element="button containing 'Upload'")

# ❌ DON'T: Forget to reset dependency overrides
app.dependency_overrides[get_db_pool] = lambda: mock_pool
# No cleanup - affects next test!

# ✅ DO: Use fixture with automatic cleanup
@pytest.fixture
def override_db(mock_db_pool):
    app.dependency_overrides[get_db_pool] = lambda: mock_db_pool
    yield
    app.dependency_overrides = {}

# ❌ DON'T: Use screenshots for validation
screenshot = browser_take_screenshot("validation.png")
# Agent can't parse images!

# ✅ DO: Use accessibility tree for validation
snapshot = browser_snapshot()
if "ExpectedElement" in snapshot:
    browser_take_screenshot("proof.png")  # Human proof only

# ❌ DON'T: Forget to await AsyncMock calls
result = mock_conn.fetchval("SELECT 1")  # Returns coroutine!

# ✅ DO: Always await AsyncMock calls
result = await mock_conn.fetchval("SELECT 1")

# ❌ DON'T: Use %s placeholders with asyncpg
query = "SELECT * FROM documents WHERE id = %s"

# ✅ DO: Use $1, $2 placeholders
query = "SELECT * FROM documents WHERE id = $1"
result = await conn.fetchrow(query, doc_id)

# ❌ DON'T: Store connections in service __init__
def __init__(self, conn: asyncpg.Connection):
    self.conn = conn  # Leaks resources!

# ✅ DO: Store pool, acquire connections per-operation
def __init__(self, db_pool: asyncpg.Pool):
    self.db_pool = db_pool

async def method(self):
    async with self.db_pool.acquire() as conn:
        result = await conn.fetchval(...)

# ❌ DON'T: Skip pre-flight checks in browser tests
browser_navigate(url="http://localhost:5173")
# Error: Connection refused if services not running!

# ✅ DO: Pre-flight checks first
ensure_browser_installed()
ensure_frontend_running(5173, "rag-service")
browser_navigate(url="http://localhost:5173")

# ❌ DON'T: Use manual sleep() instead of auto-wait
browser_navigate(url="http://localhost:5173")
time.sleep(3)
browser_click(...)

# ✅ DO: Use auto-wait with conditions
browser_navigate(url="http://localhost:5173")
browser_wait_for(text="Page loaded", timeout=5000)
browser_click(element="button containing 'Upload'")
```

---

## Success Metrics

**Test Coverage**: >80% code coverage for document/search/delete operations
**Test Speed**: Quality gates complete in <210s total (5s + 30s + 60s + 120s)
**Browser Validation**: All critical user workflows validated with screenshots as proof
**Component Completeness**: DocumentsManagement.tsx matches CrawlManagement.tsx feature parity
**Error Handling**: All HTTP status codes tested (400, 404, 413, 422, 500)
**Known Issues**: Crawl4AI truncation documented with investigation plan

---

## PRP Quality Self-Assessment

**Score: 9.0/10** - High confidence in one-pass implementation success

**Reasoning**:
- ✅ **Comprehensive context**: All 5 research docs thorough (1200+ lines each)
  - feature-analysis.md: Complete requirements breakdown
  - codebase-patterns.md: 5 patterns extracted with examples
  - documentation-links.md: 15+ official docs with specific sections
  - examples-to-include.md: 6 working code examples with "What to Mimic/Adapt/Skip"
  - gotchas.md: 20+ gotchas with detection and solutions

- ✅ **Clear task breakdown**: 16 tasks with specific steps and validation
  - Tasks ordered logically (fixtures → unit → integration → browser)
  - Each task has pattern reference and validation criteria
  - Pseudocode shows critical implementation details

- ✅ **Proven patterns**: All patterns from working codebase
  - Test fixtures pattern from conftest.py
  - FastAPI TestClient pattern from test_crawl_api.py
  - React CRUD pattern from CrawlManagement.tsx
  - Browser validation pattern from .claude/patterns/browser-validation.md

- ✅ **Validation strategy**: 4-level quality gates with clear pass/fail criteria
  - Level 1: Syntax & Style (<5s) - ruff, mypy
  - Level 2: Unit Tests (<30s) - >80% coverage requirement
  - Level 3a: Integration Tests (<60s) - API endpoints
  - Level 3b: Browser Tests (<120s) - Frontend workflows

- ✅ **Error handling**: 20+ gotchas documented with detection and solutions
  - Browser binaries not installed (pre-flight check pattern)
  - Services not running (service identity verification)
  - Dependency overrides not cleaned (fixture cleanup pattern)
  - AsyncMock exceptions (await requirement)
  - Element refs changing (semantic queries pattern)

**Deduction reasoning (-1.0 points)**:
- ⚠️ **Crawl4AI truncation issue**: Investigation needed, not immediate fix
  - Known limitation documented in TODO.md
  - Workaround provided (mark tests as xfail)
  - Root cause unknown (Crawl4AI library configuration)
  - May require empirical testing or upstream issue review

- ⚠️ **MCP browser tools documentation**: Limited official docs
  - Using Playwright documentation as foundation
  - MCP tools are wrappers around Playwright
  - CLAUDE.md provides usage examples
  - Pattern in .claude/patterns/browser-validation.md comprehensive

**Mitigations**:
1. **Crawl4AI investigation**: Add Task 17 for empirical testing
   - Test with different chunking parameters
   - Review Crawl4AI GitHub issues for similar reports
   - Document findings in TODO.md
   - Mark affected tests as xfail until resolved

2. **MCP tools documentation gap**: Use Playwright docs + CLAUDE.md
   - browser_navigate → page.goto()
   - browser_click → page.locator().click()
   - browser_snapshot → accessibility tree capture
   - browser_take_screenshot → page.screenshot()
   - Pattern documented in browser-validation.md (lines 304-403)

3. **Validation checkpoints**: Add intermediate validation steps
   - After each task, run appropriate quality gate
   - Don't proceed if validation fails
   - Document failures and fixes for future reference

**Overall Assessment**: PRP provides sufficient context, proven patterns, clear validation gates, and comprehensive gotcha coverage for successful first-pass implementation. The Crawl4AI investigation is a separate task that doesn't block main testing work. MCP tools documentation gap mitigated by Playwright docs and existing patterns.

**Recommendation**: Proceed with implementation. Address Crawl4AI investigation as separate follow-up task if time permits.
