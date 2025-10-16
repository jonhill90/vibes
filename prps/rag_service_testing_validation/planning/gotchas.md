# Known Gotchas: RAG Service Testing & Validation

## Overview

This document identifies critical pitfalls, common mistakes, security vulnerabilities, and performance issues when implementing comprehensive testing for the RAG service. Coverage includes pytest-asyncio event loop management, FastAPI dependency injection, Playwright browser automation, asyncpg transaction handling, React Testing Library anti-patterns, and the known Crawl4AI content truncation issue. Every gotcha includes detection methods and actionable solutions.

## Critical Gotchas

### 1. Browser Binaries Not Installed
**Severity**: Critical
**Category**: System Dependency / Test Environment
**Affects**: Playwright browser automation (all browser tests)
**Source**: CLAUDE.md Browser Testing section + Playwright docs

**What it is**:
Playwright requires browser binaries (Chromium, Firefox, WebKit) to be installed separately via `playwright install`. Tests fail with "Browser not found" or connection errors if binaries are missing.

**Why it's a problem**:
- All browser tests fail immediately with cryptic errors
- Wastes 10-20 minutes of debugging time
- No clear error message (shows as connection timeout)
- Blocks entire browser validation workflow

**How to detect it**:
- Error: `playwright._impl._api_types.Error: Executable doesn't exist`
- Error: `TimeoutError: Timeout 30000ms exceeded` when navigating
- Browser tests work individually but fail in CI/CD
- `playwright --version` shows version but browsers missing

**How to avoid/fix**:
```python
# ✅ RIGHT - Pre-flight check with auto-install
def ensure_browser_installed():
    """Verify browser binaries installed, auto-install if missing."""
    try:
        # Test navigation to about:blank (minimal check)
        browser_navigate(url="about:blank")
        print("✅ Browser binaries installed")
    except Exception as e:
        if "Executable doesn't exist" in str(e) or "Browser not found" in str(e):
            print("⚠️ Browser binaries missing, installing...")
            browser_install()  # MCP tool auto-installs
            time.sleep(30)  # Wait for installation to complete
            print("✅ Browser binaries installed")
        else:
            raise  # Re-raise if different error

# Add to every browser test fixture or setUp
@pytest.fixture(scope="session", autouse=True)
def setup_browser():
    """Ensure browser installed once per test session."""
    ensure_browser_installed()
```

**Why this works**:
- Detects missing browsers early (before test failures)
- Auto-installs via MCP `browser_install()` tool
- Session-scoped fixture runs once, not per test
- Prevents cryptic timeout errors

**Additional Resources**:
- Playwright Installation: https://playwright.dev/python/docs/intro
- MCP Browser Tools: `.claude/patterns/browser-validation.md`

---

### 2. Frontend Services Not Running
**Severity**: Critical
**Category**: Test Environment / Service Availability
**Affects**: All browser integration tests
**Source**: CLAUDE.md Browser Testing + codebase-patterns.md

**What it is**:
Browser tests navigate to `localhost:5173` (RAG frontend) or `localhost:5174` (task manager), but if services aren't running via `docker-compose up -d`, tests fail with connection refused.

**Why it's a problem**:
- Browser tests timeout waiting for page load (30s default)
- Error message is cryptic: "net::ERR_CONNECTION_REFUSED"
- May connect to wrong service if port conflicts exist
- Wastes CI/CD minutes retrying failed connections

**How to detect it**:
- Error: `net::ERR_CONNECTION_REFUSED` in Playwright logs
- Error: `TimeoutError: page.goto: Timeout 30000ms exceeded`
- Browser opens but shows blank page or browser error page
- `docker-compose ps` shows service as "Exit 1" or missing

**How to avoid/fix**:
```python
# ✅ RIGHT - Pre-flight checks with service identity verification
def ensure_frontend_running(port: int, service_name: str, max_retries: int = 3):
    """Verify frontend service running and accessible."""
    import subprocess
    import time

    # Check if service is up
    result = subprocess.run(
        ["docker-compose", "ps", service_name],
        capture_output=True,
        text=True
    )

    if "Up" not in result.stdout:
        print(f"⚠️ {service_name} not running, starting services...")
        subprocess.run(["docker-compose", "up", "-d"], check=True)
        time.sleep(10)  # Wait for service startup

    # Verify service identity (prevent port conflicts)
    for attempt in range(max_retries):
        try:
            result = subprocess.run(
                ["curl", "-s", f"http://localhost:{port}"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if service_name.lower() in result.stdout.lower():
                print(f"✅ {service_name} running on port {port}")
                return
            else:
                print(f"⚠️ Wrong service at port {port}, expected {service_name}")
                raise ValueError(f"Port conflict: expected {service_name} at {port}")
        except subprocess.TimeoutExpired:
            if attempt < max_retries - 1:
                print(f"⚠️ Connection timeout, retrying ({attempt+1}/{max_retries})...")
                time.sleep(5)
            else:
                raise TimeoutError(f"Cannot connect to {service_name} at port {port}")

# Add to browser test setup
@pytest.fixture(scope="session")
def frontend_services():
    """Ensure all frontend services running."""
    ensure_frontend_running(5173, "rag-service")
    ensure_frontend_running(8002, "rag-backend")  # API backend
    yield
    # Optional: docker-compose down after tests
```

**Why this works**:
- Checks service status before browser tests
- Auto-starts services if missing
- Verifies service identity (prevents port conflicts)
- Retry logic handles slow startup
- Session-scoped fixture prevents repeated checks

**Additional Resources**:
- Browser Validation Pattern: `.claude/patterns/browser-validation.md` (lines 304-320)

---

### 3. Dependency Overrides Not Cleaned Up
**Severity**: Critical
**Category**: Test Isolation / State Pollution
**Affects**: FastAPI integration tests (TestClient)
**Source**: Web search + FastAPI docs

**What it is**:
FastAPI's `app.dependency_overrides` is a global dict that persists across tests. If you override a dependency (e.g., `get_db_pool`) and don't reset it, subsequent tests use the mock instead of real dependency.

**Why it's a problem**:
- Tests pass in isolation but fail when run together
- Flaky test behavior (order-dependent failures)
- Hard to debug (test pollution is non-obvious)
- May accidentally use mocks in production code paths

**How to detect it**:
- Test passes when run alone: `pytest tests/integration/test_document_api.py::test_upload`
- Test fails when run with others: `pytest tests/integration/`
- Error: Accessing mock methods that don't exist on real objects
- Different behavior on CI vs local (depends on test order)

**How to avoid/fix**:
```python
# ❌ WRONG - Override without cleanup
def test_upload_document(client):
    app.dependency_overrides[get_db_pool] = lambda: mock_db_pool
    response = client.post("/api/upload", ...)
    # No cleanup - affects next test!

# ✅ RIGHT - Fixture with automatic cleanup
@pytest.fixture
def override_db(mock_db_pool):
    """Override database dependency with automatic cleanup."""
    from src.api.dependencies import get_db_pool
    from src.main import app

    app.dependency_overrides[get_db_pool] = lambda: mock_db_pool
    yield
    app.dependency_overrides = {}  # Reset all overrides

def test_upload_document(client, override_db):
    # Dependency overridden, will auto-cleanup after test
    response = client.post("/api/upload", ...)
    assert response.status_code == 200

# ✅ ALSO GOOD - Context manager for scoped overrides
from contextlib import contextmanager

@contextmanager
def override_dependency(dep_func, override_func):
    """Context manager for scoped dependency override."""
    app.dependency_overrides[dep_func] = override_func
    try:
        yield
    finally:
        app.dependency_overrides.pop(dep_func, None)

def test_with_context(client):
    with override_dependency(get_db_pool, lambda: mock_db_pool):
        response = client.post("/api/upload", ...)
    # Override automatically removed
```

**Why this works**:
- Fixture `yield` ensures cleanup even if test fails
- Context manager uses try/finally for guaranteed cleanup
- Explicit reset prevents state pollution
- Works with pytest's test isolation guarantees

**Testing for this gotcha**:
```python
# Verify overrides are cleaned up
def test_overrides_reset():
    from src.main import app
    from src.api.dependencies import get_db_pool

    # Should have no overrides initially
    assert app.dependency_overrides == {}

    # Override in test
    with override_dependency(get_db_pool, lambda: "mock"):
        assert get_db_pool in app.dependency_overrides

    # Should be cleaned up after context
    assert app.dependency_overrides == {}
```

**Additional Resources**:
- FastAPI Dependency Testing: https://fastapi.tiangolo.com/advanced/testing-dependencies/
- TestDriven.io Tips: https://testdriven.io/tips/b1b6489d-6538-4734-b148-6c03f8100096/

---

### 4. AsyncMock Exceptions Not Raised Until Awaited
**Severity**: Critical
**Category**: Async Testing / Mock Configuration
**Affects**: pytest-asyncio tests with AsyncMock side_effect
**Source**: Web search + Python docs

**What it is**:
When AsyncMock's `side_effect` is set to an exception, it doesn't raise immediately upon call. Instead, it returns a coroutine that raises when awaited. Tests that forget to `await` will get a coroutine object instead of the exception.

**Why it's a problem**:
- Test expects exception but gets coroutine object
- Assertion fails with confusing message: `AssertionError: <coroutine object AsyncMockMixin._execute_mock_call>`
- Tests pass incorrectly (exception never raised)
- Hard to debug (error message doesn't mention the real issue)

**How to detect it**:
- Test fails with: `RuntimeWarning: coroutine was never awaited`
- Assertion error shows coroutine object: `<coroutine object ...>`
- Exception you expected to raise is never raised
- Using `mock.assert_called_once()` works but exception test fails

**How to avoid/fix**:
```python
# ❌ WRONG - Forgetting to await AsyncMock with side_effect
from unittest.mock import AsyncMock
import pytest

mock_conn = AsyncMock()
mock_conn.fetchval = AsyncMock(side_effect=ValueError("DB error"))

# This doesn't raise immediately!
result = mock_conn.fetchval("SELECT 1")  # Returns coroutine
# Test fails: result is <coroutine>, not exception

# ✅ RIGHT - Always await AsyncMock calls
mock_conn = AsyncMock()
mock_conn.fetchval = AsyncMock(side_effect=ValueError("DB error"))

with pytest.raises(ValueError, match="DB error"):
    await mock_conn.fetchval("SELECT 1")  # Exception raised here

# ✅ RIGHT - Testing exception propagation in service
async def test_document_service_db_error(mock_db_pool):
    # Mock database error
    mock_conn = AsyncMock()
    mock_conn.fetchval = AsyncMock(side_effect=asyncpg.PostgresError("Connection lost"))

    # Mock pool.acquire() to return this connection
    async def mock_acquire():
        yield mock_conn

    mock_db_pool.acquire = AsyncMock(return_value=mock_acquire())

    # Test that service handles error properly
    service = DocumentService(mock_db_pool)
    success, result = await service.list_documents()

    assert success is False
    assert "Database error" in result["error"]
```

**Why this works**:
- `await` triggers the side_effect execution
- `pytest.raises()` catches the exception properly
- Service layer handles exceptions gracefully
- Test validates error handling code path

**Common pattern for sequential errors**:
```python
# ✅ Testing error recovery with side_effect list
mock_conn.fetchval = AsyncMock(side_effect=[
    asyncpg.PostgresError("First call fails"),
    "success_value"  # Second call succeeds
])

# First call raises exception
with pytest.raises(asyncpg.PostgresError):
    await mock_conn.fetchval("SELECT 1")

# Second call returns value
result = await mock_conn.fetchval("SELECT 1")
assert result == "success_value"
```

**Additional Resources**:
- unittest.mock AsyncMock: https://docs.python.org/3/library/unittest.mock.html#unittest.mock.AsyncMock
- Stack Overflow Discussion: https://stackoverflow.com/questions/79216021/

---

### 5. Playwright Element Refs Change Every Render
**Severity**: Critical
**Category**: Browser Automation / Element Selection
**Affects**: All browser tests using element refs
**Source**: CLAUDE.md + Playwright docs + codebase-patterns.md

**What it is**:
Playwright's `browser_snapshot()` returns element refs like `ref="e5"` that are only valid for that specific snapshot. After any re-render (state change, navigation, interaction), refs change. Using hard-coded refs breaks tests immediately.

**Why it's a problem**:
- Tests break on every UI update or re-render
- Error: `Element with ref="e5" not found`
- Brittle tests require constant maintenance
- False positives (test fails but UI works)

**How to detect it**:
- Error: `Error: No element found matching selector`
- Test worked once, now fails without code changes
- Different refs in screenshots/snapshots between runs
- Clicking same button requires different ref each time

**How to avoid/fix**:
```python
# ❌ WRONG - Hard-coded element refs (breaks on re-render)
browser_click(ref="e5")  # This ref is ephemeral!
browser_fill_form(fields=[{"ref": "e12", "value": "test"}])

# ✅ RIGHT - Use semantic queries (stable across re-renders)
browser_click(element="button containing 'Upload'")
browser_click(element="button containing 'Submit'")
browser_click(element="link containing 'Documents'")

# ✅ RIGHT - Form fields by semantic names
browser_fill_form(fields=[
    {"name": "file", "type": "file", "value": "/tmp/test.pdf"},
    {"name": "title", "type": "textbox", "value": "Test Document"},
    {"name": "description", "type": "textbox", "value": "Test description"}
])

# ✅ RIGHT - Wait for text content (not refs)
browser_wait_for(text="Upload successful", timeout=30000)
browser_wait_for(text="Document created", timeout=5000)

# ✅ RIGHT - Validate using accessibility tree content
snapshot = browser_snapshot()
if "Test Document" in snapshot and "Upload successful" in snapshot:
    print("✅ Document uploaded and visible")
```

**Why this works**:
- Semantic queries use user-facing text (stable)
- Form field names are HTML attributes (don't change)
- Text content is what users see (resilient to DOM changes)
- Accessibility tree structure is more stable than refs

**Pattern for complex interactions**:
```python
# ✅ Complete workflow without refs
def test_document_upload_workflow():
    # Navigate
    browser_navigate(url="http://localhost:5173")

    # Interact using semantic queries
    browser_click(element="link containing 'Documents'")
    browser_wait_for(text="Document Management", timeout=5000)

    browser_click(element="button containing 'Upload'")
    browser_wait_for(text="Select a document", timeout=5000)

    # Fill form by field names
    browser_fill_form(fields=[
        {"name": "file", "type": "file", "value": "/tmp/test.pdf"},
        {"name": "title", "type": "textbox", "value": "Test Document"}
    ])

    browser_click(element="button containing 'Submit'")
    browser_wait_for(text="Upload successful", timeout=30000)

    # Validate final state
    snapshot = browser_snapshot()
    assert "Test Document" in snapshot
    assert "test.pdf" in snapshot
```

**Additional Resources**:
- Playwright Locators: https://playwright.dev/python/docs/locators
- Browser Validation Pattern: `.claude/patterns/browser-validation.md` (Gotcha #4)

---

## High Priority Gotchas

### 1. pytest-asyncio Event Loop Scope Mismatches
**Severity**: High
**Category**: Test Framework / Event Loop Management
**Affects**: pytest-asyncio tests with module/session-scoped fixtures
**Source**: Web search + pytest-asyncio docs

**What it is**:
When using non-function scoped async fixtures (module/session), they must run on an event loop with matching or broader scope. Mismatched scopes cause "task attached to different loop" errors.

**Why it's a problem**:
- RuntimeError: `Task <Task pending> attached to a different loop`
- Fixtures fail to initialize properly
- Tests fail with cryptic event loop errors
- Hard to debug (error points to wrong line)

**How to detect it**:
- Error: `RuntimeError: Task attached to a different loop`
- Module/session-scoped async fixtures fail during setup
- Tests pass individually but fail when run together
- Error mentions "loop is closed" or "different event loop"

**How to avoid/fix**:
```python
# ❌ WRONG - Module-scoped fixture with function-scoped loop
@pytest.fixture(scope="module")
async def db_pool():
    """This will fail - module scope needs module loop!"""
    pool = await asyncpg.create_pool(DATABASE_URL)
    yield pool
    await pool.close()

# ✅ RIGHT - Match fixture scope with loop scope
@pytest.fixture(scope="module")
def event_loop():
    """Provide module-scoped event loop for module-scoped fixtures."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="module")
async def db_pool(event_loop):
    """Module-scoped fixture with matching event loop."""
    pool = await asyncpg.create_pool(DATABASE_URL)
    yield pool
    await pool.close()

# ✅ BEST - Use function scope unless necessary
@pytest_asyncio.fixture  # Default scope="function"
async def db_pool():
    """Function-scoped - safest option for test isolation."""
    pool = await asyncpg.create_pool(DATABASE_URL)
    yield pool
    await pool.close()
```

**Why this works**:
- Matching scopes ensure fixture runs on correct loop
- Function scope is safest (maximum isolation)
- Explicit event_loop fixture controls loop lifecycle
- Module scope reduces expensive setup repetition

**Testing configuration**:
```python
# pytest.ini or pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"  # or "strict"
asyncio_default_fixture_loop_scope = "function"

# In conftest.py
@pytest.fixture(scope="session")
def event_loop():
    """Session-scoped event loop for expensive fixtures."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()
```

**Additional Resources**:
- pytest-asyncio Concepts: https://pytest-asyncio.readthedocs.io/en/latest/concepts.html
- Medium Article: https://medium.com/@connect.hashblock/async-testing-with-pytest-37c613f1cfa3

---

### 2. FastAPI Dependency Override Requires Exact Function Reference
**Severity**: High
**Category**: Dependency Injection / Import Resolution
**Affects**: FastAPI integration tests with dependency_overrides
**Source**: Web search + FastAPI docs

**What it is**:
`app.dependency_overrides` keys must be the exact function object used in `Depends()`, not a string name or different import of the same function. Using wrong reference means override is ignored.

**Why it's a problem**:
- Override silently ignored (no error message)
- Tests use real dependency instead of mock
- May connect to production database/APIs in tests
- Hard to debug (looks correct but doesn't work)

**How to detect it**:
- Mock not being used (real database calls happen)
- Tests fail with "database not found" or network errors
- `app.dependency_overrides` has entries but not used
- Different import paths for same function

**How to avoid/fix**:
```python
# ❌ WRONG - Different import reference
# In src/api/routes/documents.py:
from src.api.dependencies import get_db_pool

@router.post("/upload")
async def upload(db_pool = Depends(get_db_pool)):
    ...

# In test:
from src.api.dependencies import get_db_pool as get_pool  # Different name!
app.dependency_overrides[get_pool] = lambda: mock_pool  # Doesn't work!

# ✅ RIGHT - Use exact same import path
# In test:
from src.api.dependencies import get_db_pool  # Exact same import
from src.api.routes import documents  # Import module that uses it

app.dependency_overrides[get_db_pool] = lambda: mock_pool  # Works!

# ✅ BEST - Import from where it's defined
# Dependency defined in: src/api/dependencies.py
# Route imports from: src.api.dependencies
# Test imports from: src.api.dependencies (same path)

from fastapi import FastAPI
from src.api.dependencies import get_db_pool
from src.api.routes.documents import router

app = FastAPI()
app.include_router(router)

# This override will work
app.dependency_overrides[get_db_pool] = lambda: mock_pool
```

**Why this works**:
- Python object identity comparison (is, not ==)
- Import path must match router's import path
- Using exact reference ensures override is recognized
- Override dict uses object identity as key

**Pattern for test fixtures**:
```python
# ✅ Centralized override fixture
@pytest.fixture
def app_with_overrides(mock_db_pool, mock_openai_client):
    """FastAPI app with all dependencies overridden."""
    from fastapi import FastAPI
    from src.api.dependencies import get_db_pool, get_openai_client
    from src.api.routes.documents import router as doc_router
    from src.api.routes.crawls import router as crawl_router

    app = FastAPI()
    app.include_router(doc_router)
    app.include_router(crawl_router)

    # Override using exact references
    app.dependency_overrides[get_db_pool] = lambda: mock_db_pool
    app.dependency_overrides[get_openai_client] = lambda: mock_openai_client

    yield app

    # Cleanup
    app.dependency_overrides = {}

@pytest.fixture
def client(app_with_overrides):
    """TestClient with all overrides applied."""
    return TestClient(app_with_overrides)
```

**Additional Resources**:
- FastAPI Testing Dependencies: https://fastapi.tiangolo.com/advanced/testing-dependencies/
- Stack Overflow: https://stackoverflow.com/questions/77473101/

---

### 3. asyncpg Cannot Rollback After Failed Commit
**Severity**: High
**Category**: Database / Transaction Management
**Affects**: asyncpg transaction testing and error handling
**Source**: Web search + asyncpg docs

**What it is**:
After a transaction commit fails, asyncpg enters an "error state" where calling `rollback()` raises `InterfaceError: cannot rollback; the transaction is in error state`. The connection is still usable for new transactions.

**Why it's a problem**:
- Error handling code may try to rollback after commit failure
- Unexpected InterfaceError in except blocks
- Confusing error messages (rollback itself fails)
- May leak transactions if not handled correctly

**How to detect it**:
- Error: `asyncpg.InterfaceError: cannot rollback; the transaction is in error state`
- Occurs in except block after failed commit
- Transaction left in inconsistent state
- Tests fail with "cannot perform operation: another operation is in progress"

**How to avoid/fix**:
```python
# ❌ WRONG - Trying to rollback after failed commit
async with pool.acquire() as conn:
    tr = conn.transaction()
    await tr.start()
    try:
        await conn.execute("INSERT INTO documents ...")
        await tr.commit()  # This might fail
    except Exception as e:
        await tr.rollback()  # InterfaceError if commit failed!
        raise

# ✅ RIGHT - Use async context manager (auto-rollback on exception)
async with pool.acquire() as conn:
    async with conn.transaction():
        # Any exception automatically rolls back
        await conn.execute("INSERT INTO documents ...")
        await conn.execute("INSERT INTO chunks ...")
        # Commit happens automatically if no exception

# ✅ RIGHT - Manual transaction with proper error handling
async with pool.acquire() as conn:
    tr = conn.transaction()
    await tr.start()
    try:
        await conn.execute("INSERT INTO documents ...")
        await tr.commit()
    except Exception as e:
        # Only rollback if commit not attempted
        if tr.is_active():
            await tr.rollback()
        raise

# ✅ BEST - Don't manually rollback, let context manager handle it
async def insert_document(pool, doc_data):
    """Service method with automatic transaction management."""
    try:
        async with pool.acquire() as conn:
            async with conn.transaction():
                doc_id = await conn.fetchval(
                    "INSERT INTO documents (title) VALUES ($1) RETURNING id",
                    doc_data["title"]
                )
                await conn.execute(
                    "INSERT INTO chunks (document_id, content) VALUES ($1, $2)",
                    doc_id, doc_data["content"]
                )
                return True, {"document_id": doc_id}
    except asyncpg.PostgresError as e:
        logger.error(f"Database error: {e}")
        return False, {"error": str(e)}
```

**Why this works**:
- Context manager handles commit/rollback automatically
- No manual rollback in error state
- Transaction state checked before rollback
- Connection remains usable after failed transaction

**Testing transaction failures**:
```python
# ✅ Testing transaction rollback
async def test_transaction_rollback(mock_db_pool):
    """Verify transaction rolls back on error."""
    mock_conn = AsyncMock()

    # Simulate constraint violation on second insert
    mock_conn.fetchval = AsyncMock(return_value="doc_id_123")
    mock_conn.execute = AsyncMock(
        side_effect=asyncpg.UniqueViolationError("Duplicate key")
    )

    # Mock transaction context manager
    mock_tr = AsyncMock()
    mock_conn.transaction = MagicMock(return_value=mock_tr)
    mock_tr.__aenter__ = AsyncMock(return_value=mock_tr)
    mock_tr.__aexit__ = AsyncMock(return_value=False)  # Propagate exception

    async def mock_acquire():
        yield mock_conn

    mock_db_pool.acquire = MagicMock(return_value=mock_acquire())

    # Test service handles error gracefully
    service = DocumentService(mock_db_pool)
    success, result = await service.create_document({...})

    assert success is False
    assert "error" in result
```

**Additional Resources**:
- asyncpg Transaction API: https://magicstack.github.io/asyncpg/current/api/index.html#transactions
- GitHub Issue: https://github.com/sqlalchemy/sqlalchemy/issues/5824

---

### 4. Async Context Manager Mocking Requires __aenter__ and __aexit__
**Severity**: High
**Category**: Mock Configuration / Async Testing
**Affects**: Tests mocking asyncpg pool.acquire() or any async context manager
**Source**: codebase-patterns.md + existing tests

**What it is**:
Async context managers (`async with`) require `__aenter__` and `__aexit__` magic methods. MagicMock doesn't configure these automatically for async operations, causing AttributeError.

**Why it's a problem**:
- Error: `AttributeError: __aenter__`
- Mock looks correct but fails at runtime
- Tests fail when trying to use `async with`
- Confusing error (doesn't mention mocking issue)

**How to detect it**:
- Error: `AttributeError: __aenter__` or `__aexit__`
- Occurs when using `async with mock_pool.acquire()`
- Mock has return_value but context manager fails
- Works with regular mock, fails with async context

**How to avoid/fix**:
```python
# ❌ WRONG - MagicMock without async context manager support
from unittest.mock import MagicMock, AsyncMock

mock_pool = MagicMock()
mock_conn = MagicMock()
mock_pool.acquire = AsyncMock(return_value=mock_conn)

# This fails: AttributeError: __aenter__
async with mock_pool.acquire() as conn:
    await conn.fetchval("SELECT 1")

# ✅ RIGHT - Mock async context manager with __aenter__/__aexit__
mock_pool = MagicMock()
mock_conn = MagicMock()

# Mock connection methods
mock_conn.fetchval = AsyncMock(return_value="result")
mock_conn.fetchrow = AsyncMock(return_value={"id": "123"})
mock_conn.execute = AsyncMock()

# Mock async context manager
async def mock_acquire():
    yield mock_conn

mock_pool.acquire = MagicMock(return_value=mock_acquire())

# Now this works
async with mock_pool.acquire() as conn:
    result = await conn.fetchval("SELECT 1")

# ✅ ALSO GOOD - Using AsyncMock for __aenter__/__aexit__
mock_pool = MagicMock()
mock_conn = MagicMock()
mock_conn.fetchval = AsyncMock(return_value="result")

mock_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
mock_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=None)

async with mock_pool.acquire() as conn:
    result = await conn.fetchval("SELECT 1")
```

**Why this works**:
- Async generator yields connection (proper context manager)
- `__aenter__` returns the connection object
- `__aexit__` handles cleanup (returns None to propagate exceptions)
- Matches real asyncpg pool.acquire() behavior

**Complete fixture pattern**:
```python
# ✅ BEST - Reusable fixture from conftest.py
@pytest.fixture
def mock_db_pool():
    """Mock asyncpg connection pool for unit tests."""
    pool = MagicMock()
    conn = MagicMock()

    # Mock connection query methods
    conn.fetchrow = AsyncMock()
    conn.fetchval = AsyncMock()
    conn.fetch = AsyncMock()
    conn.execute = AsyncMock()

    # Mock async context manager
    async def mock_acquire():
        yield conn

    pool.acquire = MagicMock(return_value=mock_acquire())
    pool.close = AsyncMock()

    return pool

# Use in tests
@pytest.mark.asyncio
async def test_document_service(mock_db_pool):
    # Configure mock behavior
    mock_conn = await mock_db_pool.acquire().__anext__()
    mock_conn.fetchval.return_value = "doc_id_123"

    # Test service
    service = DocumentService(mock_db_pool)
    success, result = await service.create_document({...})

    assert success is True
```

**Additional Resources**:
- Example 1 in examples directory: `example_1_test_fixtures.py`
- unittest.mock Documentation: https://docs.python.org/3/library/unittest.mock.html

---

### 5. File Upload TestClient Requires Specific Format
**Severity**: High
**Category**: API Testing / File Upload
**Affects**: FastAPI TestClient tests for multipart/form-data endpoints
**Source**: Web search + FastAPI docs

**What it is**:
FastAPI TestClient requires file uploads to use `files` parameter with tuple format `(filename, file_content, content_type)`. Using wrong format or `data` parameter for files causes validation errors.

**Why it's a problem**:
- Error: `422 Unprocessable Entity` - "Field required: file"
- File parameter not recognized by FastAPI
- Tests fail but real uploads work (browser sends correct format)
- Confusing error message (doesn't mention format issue)

**How to detect it**:
- Status 422 on upload endpoint that works in browser
- Error: `{"detail": [{"loc": ["body", "file"], "msg": "field required"}]}`
- `print(request.headers)` shows wrong Content-Type
- File content is None in endpoint even though test sends data

**How to avoid/fix**:
```python
# ❌ WRONG - Using data parameter for file
from fastapi.testclient import TestClient

response = client.post(
    "/api/upload",
    data={
        "file": open("/tmp/test.pdf", "rb"),  # Wrong way!
        "title": "Test Document"
    }
)

# ❌ WRONG - Wrong tuple format
response = client.post(
    "/api/upload",
    files={"file": open("/tmp/test.pdf", "rb")},  # Missing filename!
    data={"title": "Test Document"}
)

# ✅ RIGHT - Correct files parameter with tuple
from io import BytesIO

file_content = b"test file content"
file = BytesIO(file_content)

response = client.post(
    "/api/upload",
    data={"title": "Test Document", "source_id": "123"},  # Form fields
    files={"file": ("test.pdf", file, "application/pdf")}  # File upload
)

assert response.status_code == 200

# ✅ RIGHT - Using actual file
with open("/tmp/test.pdf", "rb") as f:
    response = client.post(
        "/api/upload",
        data={"title": "Test Document"},
        files={"file": ("test.pdf", f, "application/pdf")}
    )

# ✅ BEST - Test fixture for file uploads
@pytest.fixture
def sample_pdf():
    """Generate test PDF file content."""
    content = b"%PDF-1.4\n%\xE2\xE3\xCF\xD3\n"  # Minimal PDF header
    content += b"Test document content\n"
    content += b"%%EOF"
    return BytesIO(content)

def test_upload_document(client, sample_pdf):
    response = client.post(
        "/api/upload",
        data={
            "title": "Test Document",
            "source_id": "550e8400-e29b-41d4-a716-446655440000"
        },
        files={
            "file": ("test.pdf", sample_pdf, "application/pdf")
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "document_id" in data
    assert data["filename"] == "test.pdf"
```

**Why this works**:
- `files` parameter sets correct Content-Type (multipart/form-data)
- Tuple format: (filename, file_object, content_type)
- `data` parameter for non-file form fields
- TestClient automatically handles multipart encoding

**Testing file validation**:
```python
# ✅ Test file size limit
def test_upload_file_too_large(client):
    large_file = BytesIO(b"x" * (11 * 1024 * 1024))  # 11MB (over limit)

    response = client.post(
        "/api/upload",
        data={"title": "Large File"},
        files={"file": ("large.pdf", large_file, "application/pdf")}
    )

    assert response.status_code == 413  # Payload Too Large
    assert "exceeds maximum" in response.json()["detail"]

# ✅ Test file type validation
def test_upload_invalid_type(client):
    exe_file = BytesIO(b"MZ\x90\x00")  # EXE header

    response = client.post(
        "/api/upload",
        data={"title": "Invalid File"},
        files={"file": ("virus.exe", exe_file, "application/x-msdownload")}
    )

    assert response.status_code == 400
    assert "not allowed" in response.json()["detail"]
```

**Additional Resources**:
- FastAPI File Upload Testing: https://fastapi.tiangolo.com/tutorial/request-forms-and-files/
- Stack Overflow: https://stackoverflow.com/questions/63614660/

---

## Medium Priority Gotchas

### 1. Browser Auto-Wait Default Timeout Too Long
**Severity**: Medium
**Category**: Performance / Test Duration
**Affects**: Playwright browser tests with slow operations
**Source**: Playwright docs + browser-validation.md

**What it is**:
Playwright's default timeout is 30 seconds for all operations. For fast UI interactions (button clicks, navigation), this means tests wait 30s before failing, making test suites unnecessarily slow.

**Why it's confusing**:
- Tests take 30s to fail even for simple errors
- Test suite runtime bloats (5min becomes 20min)
- CI/CD minutes wasted on timeouts
- Hard to debug (long wait before error appears)

**How to handle it**:
```python
# ❌ SLOW - Using default 30s timeout for fast operations
browser_click(element="button containing 'Submit'")  # Waits 30s if not found!
browser_wait_for(text="Success message")  # 30s timeout

# ✅ RIGHT - Set appropriate timeouts per operation type
# Fast UI operations (5 seconds)
browser_click(element="button containing 'Submit'", timeout=5000)
browser_wait_for(text="Page loaded", timeout=5000)

# File uploads (30 seconds)
browser_wait_for(text="Upload complete", timeout=30000)

# Large document processing (60 seconds)
browser_wait_for(text="Processing complete", timeout=60000)

# ✅ BEST - Set default timeout at page level
def test_document_workflow():
    browser_navigate(url="http://localhost:5173")

    # Set default timeout for all operations on this page
    browser_evaluate(script="page.setDefaultTimeout(5000)")

    # Now all operations use 5s timeout by default
    browser_click(element="button containing 'Upload'")
    browser_wait_for(text="Select a document")
```

**Why this works**:
- Fast failures for UI issues (5s vs 30s)
- Longer timeouts for slow operations (uploads)
- Test suite completes faster
- Clear timeout values document expected behavior

**Timeout guidelines**:
```python
# Recommended timeout values
TIMEOUTS = {
    "ui_interaction": 5000,      # Button clicks, navigation
    "page_load": 10000,           # Page navigation
    "api_call": 15000,            # Backend API calls
    "file_upload": 30000,         # File upload processing
    "document_processing": 60000, # Embedding generation
    "crawl_job": 120000,          # Web crawling
}

def browser_click_with_timeout(element: str, operation_type: str = "ui_interaction"):
    """Click with appropriate timeout for operation type."""
    timeout = TIMEOUTS.get(operation_type, 5000)
    browser_click(element=element, timeout=timeout)
```

**Additional Resources**:
- Playwright Actionability: https://playwright.dev/python/docs/actionability

---

### 2. React Testing Library: Using fireEvent Instead of userEvent
**Severity**: Medium
**Category**: Test Quality / User Simulation
**Affects**: React component tests (if added in future)
**Source**: Web search + React Testing Library docs

**What it is**:
`fireEvent` directly dispatches events, while `userEvent` simulates real user interactions (keyDown, keyPress, keyUp for each character). Using `fireEvent` misses keyboard events that components may listen to.

**Why it's confusing**:
- `fireEvent` works for simple tests but misses edge cases
- Components using keyboard listeners fail with `fireEvent`
- `userEvent` is async (must await), `fireEvent` is sync
- Tests pass with `fireEvent` but real usage fails

**How to handle**:
```javascript
// ❌ WRONG - Using fireEvent for user interactions
import { fireEvent } from '@testing-library/react';

const input = screen.getByLabelText('Title');
fireEvent.change(input, { target: { value: 'Test Document' } });
// Missing keyDown, keyPress, keyUp events!

fireEvent.click(screen.getByText('Submit'));
// Missing hover, focus, mouseDown, mouseUp events!

// ✅ RIGHT - Using userEvent for realistic interactions
import userEvent from '@testing-library/user-event';

const user = userEvent.setup();
const input = screen.getByLabelText('Title');

await user.type(input, 'Test Document');
// Triggers: keyDown → keyPress → input → keyUp for each character

await user.click(screen.getByText('Submit'));
// Triggers: hover → focus → mouseDown → click → mouseUp

// ✅ BEST - Complete form interaction test
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import DocumentUpload from './DocumentUpload';

test('document upload form submission', async () => {
  const user = userEvent.setup();
  const onSubmit = jest.fn();

  render(<DocumentUpload onSubmit={onSubmit} />);

  // Type into inputs
  await user.type(screen.getByLabelText('Title'), 'Test Document');
  await user.type(screen.getByLabelText('Description'), 'Test description');

  // Upload file
  const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
  const fileInput = screen.getByLabelText('File');
  await user.upload(fileInput, file);

  // Submit form
  await user.click(screen.getByText('Submit'));

  // Verify submission
  expect(onSubmit).toHaveBeenCalledWith({
    title: 'Test Document',
    description: 'Test description',
    file: expect.objectContaining({ name: 'test.pdf' })
  });
});
```

**Why userEvent is better**:
- Simulates real user behavior (multiple events)
- Catches keyboard listener bugs
- Better async/await semantics
- Closer to actual browser interactions

**When to use fireEvent**:
```javascript
// ✅ ACCEPTABLE - fireEvent for non-user events
fireEvent.error(img);  // Image load error
fireEvent.load(img);   // Image load success
// These aren't user interactions, so fireEvent is fine
```

**Additional Resources**:
- Kent C. Dodds: https://kentcdodds.com/blog/common-mistakes-with-react-testing-library
- testing-library/user-event: https://testing-library.com/docs/user-event/intro/

---

### 3. Playwright Screenshots for Validation (Anti-Pattern)
**Severity**: Medium
**Category**: Test Efficiency / Token Usage
**Affects**: Browser tests using screenshots for validation
**Source**: CLAUDE.md + browser-validation.md

**What it is**:
Agents cannot parse screenshots to validate UI state. Using `browser_take_screenshot()` for validation wastes tokens (~2000 per screenshot) and provides no validation data. Screenshots are only useful for human review.

**Why it's confusing**:
- Screenshot captured successfully (no error)
- Agent cannot extract validation data from image
- Test appears to validate but doesn't
- Wastes 4x tokens compared to accessibility tree

**How to handle**:
```python
# ❌ WRONG - Screenshot for validation
browser_navigate(url="http://localhost:5173")
screenshot = browser_take_screenshot(filename="state.png")
# How do we validate from the screenshot? Agent can't parse images!
# Test passes but doesn't validate anything

# ✅ RIGHT - Accessibility tree for validation
browser_navigate(url="http://localhost:5173")
snapshot = browser_snapshot()  # ~500 tokens, agent-parseable

validation_checks = {
    "page_loaded": "Document Management" in snapshot,
    "upload_button": "Upload" in snapshot,
    "document_list": "DocumentList" in snapshot
}

if all(validation_checks.values()):
    print("✅ All validations passed")
else:
    print(f"❌ Failed checks: {[k for k, v in validation_checks.items() if not v]}")

# ✅ ACCEPTABLE - Screenshot for human proof (after validation)
if all(validation_checks.values()):
    browser_take_screenshot(filename="validation-proof.png")  # Human proof only
```

**Why accessibility tree is better**:
- Agent can parse text content
- 4x fewer tokens (~500 vs ~2000)
- Structured data (not visual)
- Faster to process

**Complete validation pattern**:
```python
def validate_document_upload_ui():
    """Validate document upload UI state."""

    # Navigate
    browser_navigate(url="http://localhost:5173/documents")

    # Capture accessibility tree (for validation)
    snapshot = browser_snapshot()

    # Validate using tree content
    validation_checks = {
        "page_title": "Document Management" in snapshot,
        "upload_button": "button containing 'Upload'" in snapshot or "Upload" in snapshot,
        "document_list": "DocumentList" in snapshot or "No documents" in snapshot,
        "filter_dropdown": "source" in snapshot.lower() or "filter" in snapshot.lower()
    }

    failed_checks = [k for k, v in validation_checks.items() if not v]

    if failed_checks:
        print(f"❌ Validation failed: {failed_checks}")
        # Screenshot for debugging
        browser_take_screenshot(filename="validation-failure.png")
        raise AssertionError(f"Validation failed: {failed_checks}")

    print("✅ All UI validations passed")
    # Screenshot for human proof
    browser_take_screenshot(filename="validation-success.png")
```

**Additional Resources**:
- Browser Validation Pattern: `.claude/patterns/browser-validation.md` (Gotcha #6)

---

### 4. asyncpg Placeholder Syntax ($1, $2) vs psycopg2 (%s)
**Severity**: Medium
**Category**: Database / SQL Syntax
**Affects**: asyncpg queries (may copy from psycopg2 examples)
**Source**: codebase-patterns.md anti-patterns

**What it is**:
asyncpg uses PostgreSQL-native `$1`, `$2` placeholders, while psycopg2 uses `%s`. Mixing syntaxes causes syntax errors or incorrect parameter binding.

**Why it's confusing**:
- Stack Overflow examples use `%s` (psycopg2)
- Error message is unclear: `syntax error at or near "%"`
- Works in psycopg2 but fails in asyncpg
- Copy-paste from other projects breaks

**How to handle**:
```python
# ❌ WRONG - psycopg2 style placeholders
query = "SELECT * FROM documents WHERE id = %s"
result = await conn.fetchrow(query, doc_id)
# Error: syntax error at or near "%"

query = "INSERT INTO documents (title, type) VALUES (%s, %s)"
await conn.execute(query, title, doc_type)
# Error: syntax error

# ✅ RIGHT - asyncpg style placeholders
query = "SELECT * FROM documents WHERE id = $1"
result = await conn.fetchrow(query, doc_id)

query = "INSERT INTO documents (title, type) VALUES ($1, $2)"
await conn.execute(query, title, doc_type)

# ✅ RIGHT - Dynamic query building with asyncpg
def build_filter_query(filters: dict) -> tuple[str, list]:
    """Build WHERE clause with asyncpg placeholders."""
    where_clauses = []
    params = []
    param_idx = 1

    if "source_id" in filters:
        where_clauses.append(f"source_id = ${param_idx}")
        params.append(filters["source_id"])
        param_idx += 1

    if "document_type" in filters:
        where_clauses.append(f"type = ${param_idx}")
        params.append(filters["document_type"])
        param_idx += 1

    where_clause = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    query = f"SELECT * FROM documents {where_clause}"

    return query, params

# Usage
query, params = build_filter_query({"source_id": "123", "type": "pdf"})
results = await conn.fetch(query, *params)
```

**Why this works**:
- `$1`, `$2` is PostgreSQL native (faster)
- asyncpg validates placeholder count
- param_idx ensures correct numbering
- Works with prepared statements

**Testing query building**:
```python
def test_build_filter_query():
    # Test single filter
    query, params = build_filter_query({"source_id": "123"})
    assert "$1" in query
    assert params == ["123"]

    # Test multiple filters
    query, params = build_filter_query({"source_id": "123", "type": "pdf"})
    assert "$1" in query and "$2" in query
    assert params == ["123", "pdf"]

    # Test no filters
    query, params = build_filter_query({})
    assert "WHERE" not in query
    assert params == []
```

**Additional Resources**:
- asyncpg Usage Guide: https://magicstack.github.io/asyncpg/current/usage.html
- Codebase Patterns: Anti-Pattern #5

---

### 5. Pytest waitFor with Multiple Assertions (Anti-Pattern)
**Severity**: Medium
**Category**: Test Reliability / Async Testing
**Affects**: React Testing Library async tests (if added)
**Source**: Web search + React Testing Library docs

**What it is**:
Having multiple assertions inside a single `waitFor()` callback can cause flaky tests. `waitFor` retries the entire callback, so if the first assertion passes but the second fails, it retries everything, potentially missing the window where both pass.

**Why it's confusing**:
- Tests pass intermittently (timing-dependent)
- Multiple assertions seem logical (check multiple things)
- Error messages are unclear (which assertion failed?)
- Works locally, fails in CI (different timing)

**How to handle**:
```javascript
// ❌ WRONG - Multiple assertions in single waitFor
await waitFor(() => {
  expect(screen.getByText('Upload complete')).toBeInTheDocument();
  expect(screen.getByText('Test Document')).toBeInTheDocument();
  expect(screen.getByText('5 chunks')).toBeInTheDocument();
});
// If first passes but second fails, entire callback retries!

// ✅ RIGHT - Single assertion per waitFor, await between
await waitFor(() => {
  expect(screen.getByText('Upload complete')).toBeInTheDocument();
});

await waitFor(() => {
  expect(screen.getByText('Test Document')).toBeInTheDocument();
});

expect(screen.getByText('5 chunks')).toBeInTheDocument();  // No wait needed if previous passed

// ✅ BEST - Use findBy queries (auto-wait)
expect(await screen.findByText('Upload complete')).toBeInTheDocument();
expect(await screen.findByText('Test Document')).toBeInTheDocument();
expect(screen.getByText('5 chunks')).toBeInTheDocument();

// ✅ ALTERNATIVE - Wait for last element, check others synchronously
await screen.findByText('Upload complete');
// Now that upload is complete, other elements should be visible
expect(screen.getByText('Test Document')).toBeInTheDocument();
expect(screen.getByText('5 chunks')).toBeInTheDocument();
```

**Why single assertions work better**:
- Clear which assertion failed
- More predictable retry behavior
- findBy queries are simpler syntax
- Synchronous checks after async wait

**Anti-pattern with side effects**:
```javascript
// ❌ WRONG - Side effects in waitFor callback
let documentCount = 0;
await waitFor(() => {
  documentCount = screen.getAllByTestId('document-item').length;  // Side effect!
  expect(documentCount).toBe(3);
});
// documentCount changes on every retry!

// ✅ RIGHT - Query once after wait
await waitFor(() => {
  expect(screen.getAllByTestId('document-item')).toHaveLength(3);
});
const documentCount = screen.getAllByTestId('document-item').length;
```

**Additional Resources**:
- React Testing Library Async: https://testing-library.com/docs/guide-disappearance#waiting-for-appearance
- DEV Community Article: https://dev.to/tipsy_dev/testing-library-writing-better-async-tests-c67

---

## Low Priority Gotchas

### 1. Hardcoded Ports in Tests
**Severity**: Low
**Category**: Test Flexibility / Configuration
**Affects**: Browser tests and integration tests
**Source**: feature-analysis.md assumptions

**What it is**:
Tests that hardcode `localhost:5173` or `localhost:8002` fail if services run on different ports (CI/CD, parallel tests, different environments).

**How to handle**:
```python
# ❌ BRITTLE - Hardcoded ports
browser_navigate(url="http://localhost:5173")
response = requests.get("http://localhost:8002/api/documents")

# ✅ RIGHT - Environment variables with defaults
import os

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8002")

browser_navigate(url=FRONTEND_URL)
response = requests.get(f"{BACKEND_URL}/api/documents")

# ✅ BEST - Configuration fixture
@pytest.fixture(scope="session")
def config():
    """Test configuration with environment overrides."""
    return {
        "frontend_url": os.getenv("FRONTEND_URL", "http://localhost:5173"),
        "backend_url": os.getenv("BACKEND_URL", "http://localhost:8002"),
        "frontend_port": int(os.getenv("FRONTEND_PORT", "5173")),
        "backend_port": int(os.getenv("BACKEND_PORT", "8002")),
    }

def test_document_upload(config):
    browser_navigate(url=config["frontend_url"])
```

**Why this works**:
- Tests portable across environments
- CI/CD can override ports
- Parallel test runs possible
- Single source of truth for configuration

---

### 2. Pytest Discovery Ignores Non-Standard Names
**Severity**: Low
**Category**: Test Organization
**Affects**: Custom test file naming
**Source**: Documentation-links.md

**What it is**:
Pytest only discovers files matching `test_*.py` or `*_test.py`. Files like `testing_documents.py` or `doc_tests.py` are ignored.

**How to handle**:
```bash
# ❌ WRONG - Non-standard names (not discovered)
tests/
├── document_testing.py    # Ignored!
├── test_helper.py          # Looks like test, but helper
└── api_test_suite.py       # Ignored!

# ✅ RIGHT - Standard naming convention
tests/
├── test_document_api.py    # Discovered
├── test_document_service.py # Discovered
└── conftest.py             # Special file (fixtures)

# ✅ ACCEPTABLE - Configure pytest to discover custom patterns
# pytest.ini or pyproject.toml
[tool.pytest.ini_options]
python_files = ["test_*.py", "*_test.py", "testing_*.py"]
```

---

## Library-Specific Quirks

### Crawl4AI Content Truncation Issue
**Severity**: HIGH (blocking feature completeness)
**Category**: External Library / Configuration
**Affects**: Web crawling with Crawl4AI
**Source**: TODO.md (lines 103-115)

**Version-Specific Issues**:
- **Current**: Crawl4AI returns truncated markdown (~50 chunks from 2.7MB document)
- **Expected**: Should return 300-400 chunks for large documents
- **Root cause**: `result.markdown` from Crawl4AI library is pre-truncated

**The Problem**:
```python
# Current behavior
result = await crawler.arun(url="https://ai.pydantic.dev/llms-full.txt")
print(len(result.markdown))  # ~150KB instead of 2.7MB
# Content is already truncated before our code sees it

# Our truncation was removed but issue persists
# Location: backend/src/services/crawler/crawl_service.py:155-169
```

**Investigation Needed**:
1. **Check Crawl4AI Configuration Options**:
   ```python
   # Possible configuration to try
   crawler_config = {
       "max_length": None,  # Remove length limit?
       "word_count_threshold": 0,  # Disable word limit?
       "extraction_strategy": "NoExtractionStrategy",  # Full content?
   }
   ```

2. **Alternative Approaches**:
   - Use Crawl4AI's built-in chunking instead of post-processing
   - Try LLM extraction mode for large documents
   - Investigate Crawl4AI GitHub issues for similar reports

**Workaround**:
```python
# ✅ Document the limitation
async def crawl_website(url: str) -> dict:
    """
    Crawl website and extract content.

    Known Issue: Crawl4AI may truncate large documents.
    For documents >1MB, content may be incomplete.
    See: infra/rag-service/TODO.md line 103
    """
    result = await crawler.arun(url)

    # Log warning if content seems truncated
    if len(result.markdown) < 100000:  # Less than 100KB
        logger.warning(f"Content may be truncated: {len(result.markdown)} bytes")

    return result
```

**Testing Approach**:
```python
# ✅ Test with known-size documents
def test_crawl_large_document():
    """Test crawling large document (known truncation issue)."""
    url = "https://ai.pydantic.dev/llms-full.txt"
    result = crawl_website(url)

    # Document known issue
    if len(result.chunks) < 200:
        pytest.xfail("Known issue: Crawl4AI truncates large documents (TODO.md line 103)")

    assert len(result.chunks) > 200
```

**Additional Resources**:
- Crawl4AI Documentation: https://docs.crawl4ai.com/api/parameters/
- TODO.md: Lines 103-115

---

## Performance Gotchas

### 1. Sequential Test Execution vs Parallel
**Impact**: Test suite duration
**Affects**: pytest execution time

**The problem**:
pytest-asyncio runs tests sequentially (not concurrently) by design for test isolation. Test suite with 50 async tests takes 50x longer than single test.

**Benchmarks**:
- Single test: ~2s
- 50 tests sequential: ~100s
- 50 tests parallel (not possible with pytest-asyncio): N/A

**Solution**:
```bash
# ✅ Use pytest-xdist for parallel execution (separate from pytest-asyncio)
pip install pytest-xdist

# Run tests in parallel (4 workers)
pytest tests/ -n 4

# Note: Each worker gets own event loop (test isolation maintained)
```

**Why pytest-asyncio is sequential**:
- Prevents race conditions between tests
- Each test gets clean event loop
- Database transaction isolation guaranteed
- Trade-off: safety > speed

**Additional Resources**:
- pytest-asyncio Concepts: https://pytest-asyncio.readthedocs.io/en/latest/concepts.html

---

## Security Gotchas

### 1. File Upload MIME Type Spoofing
**Severity**: HIGH
**Type**: Security / File Validation
**Affects**: Document upload endpoint
**CVE**: N/A (general vulnerability class)
**Source**: Example 3 (file upload validation)

**Vulnerability**:
Relying only on file extension or client-provided MIME type allows malicious file uploads. Attacker can rename `virus.exe` to `document.pdf` and bypass extension check.

**Secure Implementation**:
```python
# ❌ VULNERABLE - Extension only
def validate_file(filename: str, content_type: str):
    allowed = [".pdf", ".docx", ".txt"]
    ext = os.path.splitext(filename)[1].lower()
    if ext not in allowed:
        raise ValueError("File type not allowed")
    # Attacker renames virus.exe → virus.pdf

# ❌ VULNERABLE - Client MIME type only
def validate_file(filename: str, content_type: str):
    allowed = ["application/pdf", "text/plain"]
    if content_type not in allowed:
        raise ValueError("MIME type not allowed")
    # Attacker can fake Content-Type header

# ✅ SECURE - Multi-layer validation
import magic  # python-magic library

def validate_file(file_path: str, filename: str, content_type: str) -> tuple[bool, str]:
    """
    Validate uploaded file using multiple checks.

    Security Measures:
    1. Extension whitelist (first line of defense)
    2. MIME type check (secondary validation)
    3. Magic byte validation (actual file content)
    """
    allowed_extensions = {".pdf", ".docx", ".txt", ".md", ".html"}
    allowed_mime_types = {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
        "text/markdown",
        "text/html"
    }

    # Layer 1: Extension check
    ext = os.path.splitext(filename)[1].lower()
    if ext not in allowed_extensions:
        return False, f"File extension {ext} not allowed. Allowed: {allowed_extensions}"

    # Layer 2: Client MIME type (log warning if mismatch)
    if content_type not in allowed_mime_types:
        logger.warning(f"Unexpected MIME type: {content_type} for {filename}")

    # Layer 3: Magic byte validation (actual content)
    mime = magic.Magic(mime=True)
    actual_mime = mime.from_file(file_path)

    if actual_mime not in allowed_mime_types:
        logger.error(f"MIME spoofing detected: {filename} claims {content_type} but is {actual_mime}")
        return False, f"File content does not match extension. Detected: {actual_mime}"

    return True, "File validated successfully"

# Security measures applied:
# 1. Extension whitelist prevents obvious attacks
# 2. MIME type logged (detect spoofing attempts)
# 3. Magic bytes verify actual file content
```

**Testing for this vulnerability**:
```python
def test_file_mime_spoofing():
    """Verify magic byte validation prevents MIME spoofing."""
    # Create malicious file (EXE disguised as PDF)
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(b"MZ\x90\x00")  # Windows EXE header
        fake_pdf = f.name

    try:
        valid, message = validate_file(fake_pdf, "virus.pdf", "application/pdf")
        assert valid is False
        assert "does not match" in message
    finally:
        os.unlink(fake_pdf)
```

**Additional Resources**:
- OWASP File Upload: https://owasp.org/www-community/vulnerabilities/Unrestricted_File_Upload
- Example 3: `example_3_file_upload_validation.py`

---

## Testing Gotchas

### Common Test Pitfalls

**1. Not Using spec Parameter on Mocks**:
```python
# ❌ DANGEROUS - Mock accepts any attribute
mock_service = Mock()
mock_service.wrong_method_name()  # No error! (typo not caught)

# ✅ SAFE - spec prevents typos
mock_service = Mock(spec=DocumentService)
mock_service.wrong_method_name()  # AttributeError!
```

**2. Forgetting to Reset Mocks Between Tests**:
```python
# ❌ WRONG - Mock state persists
mock_service = Mock()

def test_one():
    mock_service.create.return_value = "doc1"
    assert create_document() == "doc1"

def test_two():
    # Still has return_value from test_one!
    assert create_document() == "doc2"  # Fails!

# ✅ RIGHT - Reset mock or use fixture
@pytest.fixture
def mock_service():
    return Mock(spec=DocumentService)
```

---

## Gotcha Checklist for Implementation

Before marking PRP complete, verify these gotchas are addressed:

### Critical
- [ ] **Browser binaries**: Pre-flight check with auto-install (Gotcha #1)
- [ ] **Services running**: Verify frontend/backend available (Gotcha #2)
- [ ] **Dependency overrides**: Automatic cleanup with fixtures (Gotcha #3)
- [ ] **AsyncMock exceptions**: Always await mock calls (Gotcha #4)
- [ ] **Element refs**: Use semantic queries, not refs (Gotcha #5)

### High Priority
- [ ] **Event loop scope**: Match fixture scope with loop scope (High #1)
- [ ] **Dependency reference**: Use exact import path for overrides (High #2)
- [ ] **Transaction rollback**: Use context managers for asyncpg (High #3)
- [ ] **Async context mocking**: Mock __aenter__/__aexit__ (High #4)
- [ ] **File upload format**: Use files parameter with tuple (High #5)

### Medium Priority
- [ ] **Browser timeouts**: Set appropriate timeouts per operation (Med #1)
- [ ] **userEvent vs fireEvent**: Use userEvent for React tests (Med #2)
- [ ] **Screenshot validation**: Use accessibility tree, not screenshots (Med #3)
- [ ] **asyncpg placeholders**: Use $1, $2 not %s (Med #4)
- [ ] **waitFor assertions**: Single assertion per waitFor (Med #5)

### Security
- [ ] **File validation**: Multi-layer validation with magic bytes (Security #1)
- [ ] **File size limits**: Enforce MAX_FILE_SIZE (10MB) (Example 3)
- [ ] **Extension whitelist**: Only allow safe file types (Example 3)

### Known Issues
- [ ] **Crawl4AI truncation**: Document limitation, mark tests as xfail (Library Quirk)
- [ ] **Port configuration**: Use environment variables (Low #1)

---

## Sources Referenced

### From Web Search
- **pytest-asyncio pitfalls**: https://stackoverflow.com/questions/61022713/ (Event loop scope issues)
- **FastAPI dependency testing**: https://fastapi.tiangolo.com/advanced/testing-dependencies/ (Override cleanup)
- **Playwright Python**: https://playwright.dev/python/docs/locators (Semantic queries)
- **asyncpg transactions**: https://github.com/sqlalchemy/sqlalchemy/issues/5824 (Rollback after commit failure)
- **React Testing Library**: https://kentcdodds.com/blog/common-mistakes-with-react-testing-library (Common mistakes)
- **unittest.mock AsyncMock**: https://docs.python.org/3/library/unittest.mock.html (Side effect awaiting)
- **Crawl4AI config**: https://docs.crawl4ai.com/api/parameters/ (Max length issue)

### From Codebase
- **TODO.md**: Lines 103-115 (Crawl4AI truncation issue)
- **CLAUDE.md**: Browser Testing section (Pre-flight checks, element refs)
- **browser-validation.md**: `.claude/patterns/browser-validation.md` (Complete workflow pattern)
- **codebase-patterns.md**: Anti-patterns section (asyncpg placeholders, async context managers)
- **feature-analysis.md**: Assumptions section (Port configuration, service startup)
- **examples directory**: All 6 examples (Test fixtures, FastAPI patterns, file validation, React CRUD, browser workflow, API client)

---

## Recommendations for PRP Assembly

When generating the PRP:
1. **Include critical gotchas** in "Known Gotchas & Library Quirks" section with solutions
2. **Reference solutions** in "Implementation Blueprint" (e.g., "Use pre-flight check from Gotcha #1")
3. **Add detection tests** to validation gates (e.g., "Verify dependency overrides reset after test")
4. **Warn about version issues** in documentation references (e.g., "Crawl4AI truncation issue - see TODO.md")
5. **Highlight anti-patterns** to avoid (e.g., "Never use element refs - see Gotcha #5")
6. **Cross-reference examples** (e.g., "See Example 1 for async context manager mocking pattern")

## Confidence Assessment

**Gotcha Coverage**: 9.5/10
- **Security**: High confidence - file validation patterns from existing code + OWASP best practices
- **Performance**: Good coverage - timeout configuration, sequential execution trade-offs documented
- **Common Mistakes**: Comprehensive - pytest-asyncio, FastAPI, Playwright, asyncpg, React Testing Library all covered

**Gaps**:
- Limited Crawl4AI documentation (investigation needed for truncation issue)
- React Testing Library gotchas based on web research (no React tests in current codebase)
- MCP browser tools documentation not available (using Playwright docs as proxy)

**Strengths**:
- Every gotcha has detection method and solution
- Code examples show wrong vs right approach
- Cross-referenced with existing codebase patterns
- Actionable remedies, not just warnings
- Prioritized by severity (Critical → Low)
