# RAG Service Test Suite

Comprehensive testing infrastructure for the RAG service, implementing a 4-level quality gate strategy from syntax validation to browser-based end-to-end testing.

---

## Table of Contents

- [Overview](#overview)
- [Test Structure](#test-structure)
- [Quality Gate Levels](#quality-gate-levels)
- [Running Tests](#running-tests)
- [Test Fixtures](#test-fixtures)
- [Writing Tests](#writing-tests)
- [Coverage Requirements](#coverage-requirements)
- [Troubleshooting](#troubleshooting)

---

## Overview

The test suite validates:
- **Backend**: Document upload, search filtering, cascade deletes, error handling
- **Frontend**: User workflows (upload, search, delete) via browser automation
- **API**: FastAPI endpoints with comprehensive HTTP status code coverage
- **Services**: Business logic in document service, file validation, search operations

**Test Count**: 80+ test cases across 9 test files
**Coverage Target**: 80%+ code coverage
**Execution Time**: <210 seconds for full suite

---

## Test Structure

```
tests/
├── conftest.py                      # Shared fixtures and test data factories
├── unit/                            # Level 2: Business logic tests (~30s)
│   ├── test_file_validation.py      # File extension, size, MIME type validation
│   └── test_document_service.py     # Document service business logic
├── integration/                     # Level 3a: API endpoint tests (~60s)
│   ├── test_crawl_api.py            # Crawl job API (existing)
│   ├── test_document_api.py         # Document CRUD endpoints
│   ├── test_search_api.py           # Search with source filtering
│   └── test_delete_cascade.py       # Foreign key cascade validation
└── browser/                         # Level 3b: End-to-end workflows (~120s)
    ├── test_document_upload.py      # Upload workflow validation
    ├── test_search_filtering.py     # Search filter UI validation
    └── test_delete_operations.py    # Delete confirmation workflow
```

### Test Categories

**Unit Tests** (`tests/unit/`):
- Test business logic in isolation
- Use mocked dependencies (database, OpenAI API, Qdrant)
- Fast execution (~30s total)
- No external services required

**Integration Tests** (`tests/integration/`):
- Test FastAPI endpoints with FastAPI TestClient
- Use dependency overrides to mock database/external services
- Validate request/response formats
- Test error handling (400, 404, 413, 422, 500)

**Browser Tests** (`tests/browser/`):
- Test complete user workflows using Playwright
- Require frontend and backend services running
- Validate UI integration with backend
- Generate screenshots for proof

---

## Quality Gate Levels

### Level 1: Syntax & Style (~5s)

**Purpose**: Catch syntax errors, type issues, style violations before running tests.

**Commands**:
```bash
# Linting (auto-fix enabled)
ruff check tests/ --fix

# Type checking
mypy tests/
```

**What it validates**:
- Python syntax correctness
- Import order and organization
- Type annotation correctness
- Code style (PEP 8 compliance)
- Unused imports and variables

### Level 2: Unit Tests (~30s)

**Purpose**: Test business logic in isolation with mocked dependencies.

**Command**:
```bash
pytest tests/unit/ -v --cov=src --cov-report=term-missing --cov-fail-under=80
```

**What it validates**:
- File validation logic (extensions, size limits, MIME types)
- Document service operations (list, create, delete)
- Search filtering logic
- Error message quality
- Edge cases and boundary conditions

### Level 3a: API Integration Tests (~60s)

**Purpose**: Test FastAPI endpoints with realistic request/response cycles.

**Command**:
```bash
pytest tests/integration/ -v
```

**What it validates**:
- HTTP endpoint behavior
- Request validation (422 for missing fields)
- Error responses (400, 404, 413, 500)
- Success responses (200, 201)
- Foreign key constraints
- Cascade delete operations

### Level 3b: Browser Integration Tests (~120s)

**Purpose**: Test complete user workflows from UI to database.

**Commands**:
```bash
# Ensure services running
docker-compose up -d

# Run browser tests
pytest tests/browser/ -v
```

**What it validates**:
- Frontend UI elements exist and are interactive
- Form submissions work end-to-end
- Delete confirmation modals appear
- Search filters update results
- Success/error messages display correctly
- Screenshots captured as proof

---

## Running Tests

### Quick Start

```bash
# Run all tests
pytest

# Run specific test level
pytest tests/unit/ -v          # Unit tests only
pytest tests/integration/ -v   # Integration tests only
pytest tests/browser/ -v       # Browser tests only

# Run specific test file
pytest tests/unit/test_file_validation.py -v

# Run specific test function
pytest tests/unit/test_file_validation.py::TestFileExtensionValidation::test_valid_pdf_extension -v
```

### With Coverage

```bash
# Unit tests with coverage
pytest tests/unit/ -v --cov=src --cov-report=term-missing

# HTML coverage report (detailed line-by-line)
pytest tests/unit/ --cov=src --cov-report=html
# Open htmlcov/index.html in browser

# Coverage for specific module
pytest tests/unit/ --cov=src.services.document_service --cov-report=term-missing
```

### Docker Execution

```bash
# Run tests inside Docker container
docker exec -it ragservice-backend pytest

# With coverage
docker exec -it ragservice-backend pytest tests/unit/ --cov=src --cov-report=term-missing

# Interactive shell for debugging
docker exec -it ragservice-backend bash
pytest tests/unit/test_file_validation.py -v -s  # -s shows print statements
```

### Debugging Tests

```bash
# Show print statements and logs
pytest tests/unit/ -v -s

# Stop at first failure
pytest tests/unit/ -x

# Run last failed tests only
pytest tests/unit/ --lf

# Show local variables on failure
pytest tests/unit/ -l

# Run with pdb debugger on failure
pytest tests/unit/ --pdb
```

---

## Test Fixtures

Fixtures are defined in `conftest.py` and auto-discovered by pytest. No explicit imports needed.

### Database Fixtures

**`mock_db_pool`** - Mock asyncpg connection pool
```python
def test_example(mock_db_pool):
    # mock_db_pool.acquire() returns mock connection
    # Configure with side_effect for multi-step operations
    pass
```

**`mock_db_connection`** - Mock database connection
```python
def test_example(mock_db_connection):
    # Pre-configured with fetchval, fetchrow, execute methods
    pass
```

### Service Fixtures

**`mock_openai_client`** - Mock OpenAI API client
```python
def test_example(mock_openai_client):
    # Mock embeddings.create() responses
    pass
```

**`mock_qdrant_client`** - Mock Qdrant vector database client
```python
def test_example(mock_qdrant_client):
    # Mock search() and upsert() operations
    pass
```

**`embedding_service`** - Embedding service with mocked OpenAI
```python
async def test_example(embedding_service):
    embeddings = await embedding_service.generate_embeddings(["text"])
    assert len(embeddings) == 1
```

**`vector_service`** - Vector service with mocked Qdrant
```python
async def test_example(vector_service):
    results = await vector_service.search_vectors(embedding=[0.1, 0.2])
    assert len(results) > 0
```

### Test Data Fixtures

**`sample_document`** - Sample document record
```python
def test_example(sample_document):
    assert sample_document["title"] == "Test Document"
    assert sample_document["type"] == "pdf"
```

**`sample_source`** - Sample source record
```python
def test_example(sample_source):
    assert sample_source["title"] == "Test Source"
    assert sample_source["type"] == "documentation"
```

**`sample_chunk`** - Sample document chunk with embedding
```python
def test_example(sample_chunk):
    assert sample_chunk["text"] == "Sample chunk text"
    assert len(sample_chunk["embedding"]) == 1536
```

**`mock_uploaded_file`** - Mock file upload (BytesIO with PDF header)
```python
def test_example(mock_uploaded_file):
    # Use with FastAPI TestClient file uploads
    response = client.post("/upload", files={"file": ("test.pdf", mock_uploaded_file, "application/pdf")})
```

### FastAPI Fixtures

**`app`** - FastAPI application instance with dependency overrides
```python
def test_example(app, mock_db_pool):
    from src.api.dependencies import get_db_pool
    app.dependency_overrides[get_db_pool] = lambda: mock_db_pool
    # Overrides automatically cleaned up after test
```

---

## Writing Tests

### Unit Test Pattern

```python
import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_document_service_list(mock_db_pool):
    """Test listing documents with filters."""
    # Arrange: Configure mock
    mock_conn = MagicMock()
    mock_conn.fetch = AsyncMock(return_value=[
        {"id": "123", "title": "Doc 1"}
    ])

    async def mock_acquire():
        yield mock_conn

    mock_db_pool.acquire = MagicMock(return_value=mock_acquire())

    # Act: Call service
    from src.services.document_service import DocumentService
    service = DocumentService(mock_db_pool)
    documents = await service.list_documents(source_id="456")

    # Assert: Verify results
    assert len(documents) == 1
    assert documents[0]["title"] == "Doc 1"

    # Verify mock called with correct query
    mock_conn.fetch.assert_called_once()
    query = mock_conn.fetch.call_args[0][0]
    assert "WHERE source_id = $1" in query
```

### Integration Test Pattern

```python
from fastapi.testclient import TestClient

def test_upload_document_success(app, mock_db_pool, mock_uploaded_file):
    """Test successful document upload."""
    client = TestClient(app)

    # Override dependencies
    from src.api.dependencies import get_db_pool
    app.dependency_overrides[get_db_pool] = lambda: mock_db_pool

    # Make request
    response = client.post(
        "/api/documents/upload",
        data={"title": "Test Doc", "source_id": "123"},
        files={"file": ("test.pdf", mock_uploaded_file, "application/pdf")}
    )

    # Assert response
    assert response.status_code == 200
    data = response.json()
    assert "document_id" in data
    assert data["filename"] == "test.pdf"
```

### Browser Test Pattern

```python
from playwright_mcp import browser_navigate, browser_click, browser_wait_for, browser_snapshot

def test_document_upload_workflow():
    """Test complete document upload workflow."""
    # Navigate to page
    browser_navigate(url="http://localhost:5173/documents")

    # Interact with UI (use semantic queries, not refs)
    browser_click(element="button containing 'Upload'")
    browser_wait_for(text="Select a document", timeout=5000)

    # Fill form
    browser_fill_form(fields=[
        {"name": "file", "type": "file", "value": "/tmp/test.pdf"},
        {"name": "title", "type": "textbox", "value": "Test Document"}
    ])

    # Submit and wait
    browser_click(element="button containing 'Submit'")
    browser_wait_for(text="Upload successful", timeout=30000)

    # Validate using accessibility tree (not screenshots)
    snapshot = browser_snapshot()
    assert "Test Document" in snapshot
    assert "Upload successful" in snapshot

    # Screenshot for human proof only
    browser_take_screenshot("upload-proof.png")
```

### Critical Patterns

**Async Context Manager Mocking**:
```python
mock_pool = MagicMock()
mock_conn = MagicMock()
mock_conn.fetchval = AsyncMock(return_value="result")

async def mock_acquire():
    yield mock_conn

mock_pool.acquire = MagicMock(return_value=mock_acquire())
```

**Sequential Mock Returns (side_effect)**:
```python
mock_conn.fetch = AsyncMock(side_effect=[
    [{"id": "1"}],  # First call returns 1 document
    [{"id": "2"}],  # Second call returns different document
])
```

**File Upload Format**:
```python
# Correct format: tuple (filename, file_content, content_type)
files = {"file": ("test.pdf", BytesIO(b"content"), "application/pdf")}
response = client.post("/upload", data={...}, files=files)
```

---

## Coverage Requirements

**Target**: 80% code coverage minimum

**What counts toward coverage**:
- All business logic in `src/services/`
- API endpoints in `src/api/routes/`
- Validation functions
- Error handling paths

**What doesn't require coverage**:
- `__init__.py` files
- Configuration files (`src/config/settings.py`)
- Main entry points (`src/main.py`)
- Database migration scripts

**Viewing coverage**:
```bash
# Terminal output
pytest tests/unit/ --cov=src --cov-report=term-missing

# HTML report (detailed)
pytest tests/unit/ --cov=src --cov-report=html
open htmlcov/index.html
```

**Coverage by module**:
```bash
# Document service coverage
pytest tests/unit/ --cov=src.services.document_service --cov-report=term-missing

# API routes coverage
pytest tests/integration/ --cov=src.api.routes --cov-report=term-missing
```

---

## Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'pytest'`
```bash
# Solution: Install test dependencies
pip install pytest pytest-asyncio pytest-cov httpx
```

**Issue**: Browser tests fail with "Executable doesn't exist"
```bash
# Solution: Install Playwright browser binaries
playwright install
```

**Issue**: "Connection refused" in browser tests
```bash
# Solution: Ensure services running
docker-compose ps  # Verify all services "Up"
docker-compose up -d  # Start services if needed
curl http://localhost:5173  # Verify frontend accessible
curl http://localhost:8000/health  # Verify backend accessible
```

**Issue**: Tests pass individually but fail when run together
```bash
# Solution: Dependency overrides not cleaned up
# Fix: Add cleanup in fixture:
@pytest.fixture
def app_with_overrides():
    # ... setup ...
    yield app
    app.dependency_overrides = {}  # Reset all overrides
```

**Issue**: `RuntimeError: Event loop is closed`
```bash
# Solution: Fixture scope mismatch
# Fix: Match fixture scope with event_loop scope
@pytest.fixture(scope="function")  # Not "module" or "session"
async def async_fixture():
    pass
```

**Issue**: Mock not being called or called with wrong arguments
```bash
# Solution: Check mock configuration
# Debug with:
print(mock_conn.fetchval.call_args_list)  # See all calls
mock_conn.fetchval.assert_called_once_with("SELECT 1", "arg")
```

**Issue**: Coverage below 80%
```bash
# Solution: Identify missing coverage
pytest tests/unit/ --cov=src --cov-report=html
# Open htmlcov/index.html and look for red lines
# Add tests for uncovered code paths
```

### Debugging Tips

1. **Run single test with verbose output**:
   ```bash
   pytest tests/unit/test_file_validation.py::test_valid_extension -v -s
   ```

2. **Show local variables on failure**:
   ```bash
   pytest tests/unit/ -v -l
   ```

3. **Drop into debugger on failure**:
   ```bash
   pytest tests/unit/ --pdb
   ```

4. **Show test execution order**:
   ```bash
   pytest tests/unit/ -v --collect-only
   ```

5. **Re-run only failed tests**:
   ```bash
   pytest tests/unit/ --lf
   ```

---

## Best Practices

### DO:
- ✅ Use fixtures from `conftest.py` (no explicit imports needed)
- ✅ Mock external services (database, OpenAI, Qdrant)
- ✅ Test error paths (400, 404, 500 responses)
- ✅ Use semantic queries in browser tests (`"button containing 'Upload'"`)
- ✅ Validate with accessibility tree (`browser_snapshot()`), not screenshots
- ✅ Clean up dependency overrides after tests
- ✅ Use `AsyncMock` for async functions

### DON'T:
- ❌ Don't use element refs in browser tests (they change every render)
- ❌ Don't forget to `await` AsyncMock calls
- ❌ Don't use `%s` placeholders with asyncpg (use `$1`, `$2`)
- ❌ Don't store database connections in `__init__` (use connection pool)
- ❌ Don't skip pre-flight checks in browser tests (verify services running)
- ❌ Don't rely on test execution order (tests should be independent)

---

## Related Documentation

- **PRP**: `/Users/jon/source/vibes/prps/rag_service_testing_validation.md` - Complete testing specification
- **Validation Report**: `/Users/jon/source/vibes/prps/rag_service_testing_validation/execution/validation-report.md`
- **Browser Validation Pattern**: `/Users/jon/source/vibes/.claude/patterns/browser-validation.md`
- **Quality Gates Pattern**: `/Users/jon/source/vibes/.claude/patterns/quality-gates.md`
- **Main README**: `/Users/jon/source/vibes/infra/rag-service/README.md` - Service overview and setup

---

**Last Updated**: 2025-10-16
**Test Suite Version**: 1.0
**Coverage Target**: 80%+
**Total Tests**: 80+ test cases across 9 test files
