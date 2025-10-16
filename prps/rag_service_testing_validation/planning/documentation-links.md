# Documentation Resources: RAG Service Testing & Validation

## Overview
This document provides comprehensive documentation links for implementing backend unit/integration tests and frontend browser testing for the RAG service. Coverage includes pytest, FastAPI TestClient, Playwright browser automation, async testing patterns, mocking strategies, and file upload testing. All sources are official documentation with working code examples.

---

## Primary Framework Documentation

### pytest Testing Framework
**Official Docs**: https://docs.pytest.org/en/stable/contents.html
**Version**: 8.4+ (latest stable)
**Archon Source**: Not in Archon
**Relevance**: 10/10

**Sections to Read**:

1. **Getting Started**: https://docs.pytest.org/en/stable/getting-started.html
   - **Why**: Learn basic test structure, assertion patterns, and pytest discovery rules
   - **Key Concepts**:
     - Test files must follow `test_*.py` or `*_test.py` naming convention
     - Use standard `assert` statements for validation
     - `pytest.raises()` for exception testing
     - Automatic test discovery in current directory and subdirectories

2. **How to use fixtures**: https://docs.pytest.org/en/stable/how-to/fixtures.html
   - **Why**: Fixtures are the foundation for test data setup, dependency injection, and teardown
   - **Key Concepts**:
     - `@pytest.fixture` decorator for reusable test components
     - Fixture scopes: function, class, module, package, session
     - `autouse=True` for automatic fixture application
     - Teardown/cleanup with yield statement
     - Request fixtures in test function parameters

3. **Fixtures reference**: https://docs.pytest.org/en/stable/reference/fixtures.html
   - **Why**: Complete API reference for fixture configuration and built-in fixtures
   - **Key Concepts**:
     - conftest.py for sharing fixtures across test modules
     - Fixture parametrization for data-driven testing
     - Fixtures can search upward but never downward in directory structure

4. **How to parametrize fixtures and test functions**: https://docs.pytest.org/en/stable/how-to/parametrize.html
   - **Why**: Test multiple input scenarios efficiently without duplicating test code
   - **Key Concepts**:
     - `@pytest.mark.parametrize` decorator for multiple test inputs
     - Stack decorators for combinatorial testing
     - Apply marks to individual parameters with `pytest.param`

5. **Parametrizing tests examples**: https://docs.pytest.org/en/stable/example/parametrize.html
   - **Why**: Real-world examples of parametrized test patterns
   - **Key Concepts**:
     - Testing multiple input/output pairs
     - Custom parametrization schemes
     - Indirect parametrization

**Code Examples from Docs**:

```python
# Example 1: Basic test structure
# Source: https://docs.pytest.org/en/stable/getting-started.html
def test_passing():
    assert (1, 2, 3) == (1, 2, 3)

def test_failing():
    assert (1, 2, 3) == (3, 2, 1)

# Example 2: Exception testing
import pytest

def test_zero_division():
    with pytest.raises(ZeroDivisionError):
        1 / 0
```

```python
# Example 3: Fixture with scope
# Source: https://docs.pytest.org/en/stable/how-to/fixtures.html
import pytest

@pytest.fixture(scope="module")
async def async_db_pool():
    pool = await create_pool(DATABASE_URL)
    yield pool
    await pool.close()

def test_database_query(async_db_pool):
    # Use the pool fixture
    pass
```

```python
# Example 4: Parametrized tests
# Source: https://docs.pytest.org/en/stable/how-to/parametrize.html
@pytest.mark.parametrize("test_input,expected", [
    ("3+5", 8),
    ("2+4", 6),
    ("6*9", 42)
])
def test_eval(test_input, expected):
    assert eval(test_input) == expected
```

**Gotchas from Documentation**:
- conftest.py fixtures are automatically discovered; no imports needed
- Fixtures can only search upward, never downward in directory structure
- Default fixture scope is "function" (runs once per test)
- Use `scope="module"` or `scope="session"` for expensive setup operations
- Parametrized tests create separate test items for each parameter set

---

### pytest-asyncio (Async Testing Support)
**Official Docs**: https://pytest-asyncio.readthedocs.io/en/latest/
**Version**: 1.2+ (latest)
**Archon Source**: Not in Archon
**Relevance**: 10/10

**Sections to Read**:

1. **Concepts**: https://pytest-asyncio.readthedocs.io/en/latest/concepts.html
   - **Why**: Understand event loop management, test discovery modes, and async fixture patterns
   - **Key Concepts**:
     - Function-level loop scope by default (maximum isolation)
     - Strict mode (explicit markers) vs Auto mode (automatic detection)
     - Event loop assignment per pytest collector level
     - Tests run sequentially, not concurrently (preserves isolation)

2. **Fixtures**: https://pytest-asyncio.readthedocs.io/en/latest/reference/fixtures/
   - **Why**: Learn how to create async fixtures for database connections, API clients, and services
   - **Key Concepts**:
     - `@pytest_asyncio.fixture` decorator for async fixtures
     - All fixture scopes supported (function, class, module, session)
     - Non-function scopes require matching event_loop fixture scope
     - Async fixtures can yield for teardown logic

**Code Examples from Docs**:

```python
# Example 1: Async fixture with yield
# Source: https://pytest-asyncio.readthedocs.io/en/latest/concepts.html
import pytest_asyncio
import asyncio

@pytest_asyncio.fixture
async def async_gen_fixture():
    await asyncio.sleep(0.1)
    yield "a value"

@pytest_asyncio.fixture(scope="module")
async def async_fixture():
    return await asyncio.sleep(0.1)
```

```python
# Example 2: Event loop scope configuration
# Source: https://pytest-asyncio.readthedocs.io/en/latest/concepts.html
import asyncio
import pytest

@pytest.mark.asyncio(loop_scope="module")
async def test_shared_loop():
    loop = asyncio.get_running_loop()
    # All tests in this module share the same loop
```

```python
# Example 3: Async test function
import pytest

@pytest.mark.asyncio
async def test_async_operation():
    result = await some_async_function()
    assert result == expected_value
```

**Gotchas from Documentation**:
- In strict mode (default), must use `@pytest_asyncio.fixture` explicitly
- In auto mode, all async fixtures are handled automatically
- Keep neighboring tests on the same event loop scope for clarity
- Non-function scopes require event_loop fixture with matching/broader scope
- Tests run sequentially (no concurrent execution) to prevent race conditions

---

### FastAPI Testing Framework
**Official Docs**: https://fastapi.tiangolo.com/
**Version**: Latest (framework maintains backward compatibility)
**Archon Source**: Not in Archon
**Relevance**: 10/10

**Sections to Read**:

1. **TestClient Reference**: https://fastapi.tiangolo.com/reference/testclient/
   - **Why**: Understand how to test FastAPI endpoints without real HTTP connections
   - **Key Concepts**:
     - Import from `fastapi.testclient`
     - Based on Starlette's TestClient (wraps HTTPX)
     - Direct communication with FastAPI code (no socket connection)
     - Constructor parameters: app, base_url, raise_server_exceptions, etc.
     - Default base_url is "http://testserver"

2. **Testing Dependencies with Overrides**: https://fastapi.tiangolo.com/advanced/testing-dependencies/
   - **Why**: Essential for mocking databases, external APIs, and authentication in tests
   - **Key Concepts**:
     - `app.dependency_overrides` is a simple dict
     - Key: original dependency function
     - Value: override/mock function
     - Reset with `app.dependency_overrides = {}`
     - Enables testing without calling external services

3. **Request Forms and Files**: https://fastapi.tiangolo.com/tutorial/request-forms-and-files/
   - **Why**: Learn how to handle file uploads with form data (critical for document upload tests)
   - **Key Concepts**:
     - Requires `python-multipart` installation
     - Combine `File()` and `Form()` parameters
     - Uses `multipart/form-data` encoding
     - Cannot mix with `Body` fields expecting JSON
     - `UploadFile` for streamed files, `bytes` for in-memory

4. **Async Tests**: https://fastapi.tiangolo.com/advanced/async-tests/
   - **Why**: Learn how to test async FastAPI endpoints with async database operations
   - **Key Concepts**:
     - Use `AsyncClient` from HTTPX instead of TestClient
     - Test functions must be `async def`
     - Send requests with `await client.get()`
     - Useful for verifying database writes with async DB libraries
     - Use pytest-asyncio to mark tests as async

**Code Examples from Docs**:

```python
# Example 1: Basic TestClient usage
# Source: https://fastapi.tiangolo.com/reference/testclient/
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}

client = TestClient(app)

def test_read_item():
    response = client.get("/items/42")
    assert response.status_code == 200
    assert response.json() == {"item_id": 42}
```

```python
# Example 2: Dependency override for testing
# Source: https://fastapi.tiangolo.com/advanced/testing-dependencies/
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

app = FastAPI()

async def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}

@app.get("/items/")
async def read_items(commons: dict = Depends(common_parameters)):
    return {"message": "Hello Items!", "params": commons}

# Test with override
async def override_dependency(q: str | None = None):
    return {"q": q, "skip": 5, "limit": 10}

client = TestClient(app)
app.dependency_overrides[common_parameters] = override_dependency

def test_override_dependency():
    response = client.get("/items/")
    assert response.json()["params"]["skip"] == 5
```

```python
# Example 3: File upload endpoint
# Source: https://fastapi.tiangolo.com/tutorial/request-forms-and-files/
from typing import Annotated
from fastapi import FastAPI, File, Form, UploadFile

app = FastAPI()

@app.post("/files/")
async def create_file(
    file: Annotated[bytes, File()],
    fileb: Annotated[UploadFile, File()],
    token: Annotated[str, Form()],
):
    return {
        "file_size": len(file),
        "token": token,
        "fileb_content_type": fileb.content_type,
    }
```

```python
# Example 4: Testing file upload
# Source: Community best practices (Stack Overflow)
from fastapi.testclient import TestClient

def test_file_upload():
    response = client.post(
        "/api/upload",
        data={"user_id": 1},  # Form fields
        files={"csv_file": ("filename.csv", file_content)}  # File upload
    )
    assert response.status_code == 200
```

```python
# Example 5: Async test with AsyncClient
# Source: https://fastapi.tiangolo.com/advanced/async-tests/
from httpx import AsyncClient
import pytest

@pytest.mark.asyncio
async def test_async_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/items/42")
    assert response.status_code == 200
```

**Gotchas from Documentation**:
- Don't set Content-Type manually for multipart; TestClient handles it
- Dependency overrides are global; reset after each test
- `raise_server_exceptions=True` by default (exceptions propagate to tests)
- Cannot mix JSON Body with File/Form (HTTP protocol limitation)
- For async database tests, use AsyncClient instead of TestClient
- TestClient doesn't start a real server (direct FastAPI code invocation)

---

### Playwright Browser Automation
**Official Docs**: https://playwright.dev/python/
**Version**: Latest (Python 3.8+)
**Archon Source**: Not in Archon
**Relevance**: 9/10

**Sections to Read**:

1. **Installation**: https://playwright.dev/python/docs/intro
   - **Why**: Setup instructions and system requirements for browser automation
   - **Key Concepts**:
     - Install via pip: `pip install pytest-playwright`
     - Install browser binaries: `playwright install`
     - Python 3.8+ required
     - Supports Chromium, WebKit, Firefox
     - Cross-platform (Windows, macOS, Linux)

2. **Locators (Semantic Queries)**: https://playwright.dev/python/docs/locators
   - **Why**: Critical for stable, user-facing element selection (avoid brittle CSS selectors)
   - **Key Concepts**:
     - `page.get_by_role()` - Primary recommendation (accessibility-based)
     - `page.get_by_text()` - Find by text content
     - `page.get_by_label()` - Form elements by label
     - `page.get_by_placeholder()` - Input placeholders
     - `page.get_by_test_id()` - Explicit test contracts
     - Chain locators to narrow searches
     - Avoid CSS/XPath (break on DOM changes)

3. **Locator API Reference**: https://playwright.dev/python/docs/api/class-locator
   - **Why**: Complete API for interacting with elements (click, fill, wait)
   - **Key Concepts**:
     - `locator.click()` - Click elements with auto-wait
     - `locator.fill()` - Type into inputs
     - `locator.wait_for()` - Explicit waits
     - `locator.is_visible()` - Visibility checks
     - Locators are lazy (re-query on each action)

4. **Auto-waiting**: https://playwright.dev/python/docs/actionability
   - **Why**: Understand Playwright's automatic waiting mechanism (eliminates sleep() calls)
   - **Key Concepts**:
     - Actions auto-wait for actionability checks
     - Default timeout: 30 seconds
     - Checks: visible, stable, enabled, receives events
     - Customize with `timeout` parameter
     - Set default with `page.set_default_timeout()`

5. **Accessibility API**: https://playwright.dev/python/docs/api/class-accessibility
   - **Why**: Capture accessibility tree for validation (agent-readable structure)
   - **Key Concepts**:
     - `accessibility.snapshot()` captures tree
     - `interestingOnly=true` (default) prunes unused nodes
     - Returns root accessible node
     - Note: Method is deprecated; consider newer ARIA snapshots

6. **ARIA Snapshots**: https://playwright.dev/docs/aria-snapshots
   - **Why**: Modern alternative for accessibility tree validation (YAML format)
   - **Key Concepts**:
     - YAML representation of page structure
     - Store and compare snapshots
     - Verify page structure consistency
     - Better than deprecated accessibility.snapshot()

7. **Page API**: https://playwright.dev/python/docs/api/class-page
   - **Why**: Complete reference for page-level operations (navigate, evaluate, screenshot)
   - **Key Concepts**:
     - `page.goto()` - Navigation
     - `page.screenshot()` - Capture screenshots
     - `page.evaluate()` - Run JavaScript
     - `page.wait_for_selector()` - Explicit waits
     - `page.set_default_timeout()` - Configure timeouts

**Code Examples from Docs**:

```python
# Example 1: Basic test with semantic locators
# Source: https://playwright.dev/python/docs/intro
import re
from playwright.sync_api import Page, expect

def test_has_title(page: Page):
    page.goto("https://playwright.dev/")
    expect(page).to_have_title(re.compile("Playwright"))

def test_get_started_link(page: Page):
    page.goto("https://playwright.dev/")
    page.get_by_role("link", name="Get started").click()
    expect(page.get_by_role("heading", name="Installation")).to_be_visible()
```

```python
# Example 2: Semantic locator patterns
# Source: https://playwright.dev/python/docs/locators
from playwright.sync_api import Page

def test_user_facing_locators(page: Page):
    # Fill form using labels (how users see it)
    page.get_by_label("User Name").fill("John")
    page.get_by_label("Password").fill("secret")

    # Click button by role and text
    page.get_by_role("button", name="Sign in").click()

    # Verify success message appears
    expect(page.get_by_text("Welcome, John!")).to_be_visible()
```

```python
# Example 3: Chaining locators for specificity
# Source: https://playwright.dev/python/docs/locators
def test_filtered_locators(page: Page):
    # Find specific product in list
    product = page.get_by_role("listitem").filter(has_text="Product 2")
    product.get_by_role("button", name="Add to cart").click()
```

```python
# Example 4: Setting timeouts
# Source: https://playwright.dev/python/docs/actionability
def test_with_custom_timeout(page: Page):
    # Set default timeout for all operations
    page.set_default_timeout(30000)  # 30 seconds

    # Or set timeout for specific action
    page.locator("[data-test='username']").click(timeout=10000)
```

```python
# Example 5: Accessibility tree snapshot (deprecated but still functional)
# Source: https://playwright.dev/python/docs/api/class-accessibility
def test_accessibility_snapshot(page: Page):
    page.goto("https://example.com")
    snapshot = page.accessibility.snapshot()
    # snapshot contains structured tree data
```

**Gotchas from Documentation**:
- Element refs change every render; always use semantic queries
- Default timeout is 30 seconds (may be too long/short for some operations)
- Screenshots don't include auto-wait; use explicit waits first
- Accessibility API is deprecated; prefer ARIA snapshots
- Playwright uses auto-wait; avoid manual `time.sleep()`
- Tests run in headless mode by default
- Browser binaries must be installed separately (`playwright install`)
- CSS/XPath selectors break easily; prioritize user-facing locators

---

## Library Documentation

### 1. unittest.mock (Python Standard Library)
**Official Docs**: https://docs.python.org/3/library/unittest.mock.html
**Purpose**: Mocking and patching for testing (database pools, API clients, external services)
**Archon Source**: Not in Archon
**Relevance**: 10/10

**Key Pages**:

- **unittest.mock — mock object library**: https://docs.python.org/3/library/unittest.mock.html
  - **Use Case**: Complete reference for Mock, MagicMock, AsyncMock, and patching
  - **Key Sections**:
    - AsyncMock for async functions and context managers
    - MagicMock for magic methods (container operations, context managers)
    - side_effect for functions, exceptions, iterables
    - Patching with `@patch` decorator and context managers

- **unittest.mock — getting started**: https://docs.python.org/3/library/unittest.mock-examples.html
  - **Use Case**: Practical examples and common patterns
  - **Key Sections**:
    - Mocking method calls
    - Mocking classes and objects
    - Patching built-ins
    - Where to patch (test vs source module)

**API Reference**:

- **AsyncMock**: https://docs.python.org/3/library/unittest.mock.html#unittest.mock.AsyncMock
  - **Signature**: `AsyncMock(spec=None, side_effect=None, return_value=None, ...)`
  - **Returns**: Awaitable that returns `return_value` or result of `side_effect`
  - **Example**:
  ```python
  from unittest.mock import AsyncMock
  import asyncio

  # Mock async function
  mock = AsyncMock(return_value="result")
  result = await mock()
  assert result == "result"

  # Mock with side_effect
  mock = AsyncMock(side_effect=[1, 2, 3])
  assert await mock() == 1
  assert await mock() == 2
  ```

- **MagicMock**: https://docs.python.org/3/library/unittest.mock.html#unittest.mock.MagicMock
  - **Signature**: `MagicMock(spec=None, side_effect=None, return_value=None, ...)`
  - **Returns**: Mock with magic methods pre-configured
  - **Example**:
  ```python
  from unittest.mock import MagicMock

  # Mock async context manager
  mock_pool = MagicMock()
  mock_conn = MagicMock()
  mock_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
  mock_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=None)

  async with mock_pool.acquire() as conn:
      result = await conn.fetchval("SELECT 1")
  ```

**Applicable patterns**:

- **Pattern 1: Mocking async database pool**
  ```python
  from unittest.mock import AsyncMock, MagicMock

  @pytest.fixture
  def mock_db_pool():
      pool = MagicMock()
      conn = MagicMock()
      cursor = MagicMock()

      # Mock connection acquisition
      pool.acquire.return_value.__aenter__ = AsyncMock(return_value=conn)
      pool.acquire.return_value.__aexit__ = AsyncMock(return_value=None)

      # Mock query methods
      conn.fetchval = AsyncMock(return_value="mock_result")
      conn.fetchrow = AsyncMock(return_value={"id": "123"})
      conn.execute = AsyncMock(return_value=None)

      return pool
  ```

- **Pattern 2: Side effects for sequential returns**
  ```python
  # Mock multiple database calls with different results
  mock_conn.fetchval.side_effect = [
      "source_id_123",  # First call returns source_id
      5,                # Second call returns chunk count
  ]
  ```

- **Pattern 3: Mock async context manager manually**
  ```python
  mock_pool = MagicMock()
  mock_pool.__aenter__ = AsyncMock(return_value=mock_pool)
  mock_pool.__aexit__ = AsyncMock(return_value=None)
  ```

---

### 2. asyncpg (PostgreSQL Async Driver)
**Official Docs**: https://magicstack.github.io/asyncpg/current/
**Purpose**: Async database operations and connection pool management
**Archon Source**: Not in Archon
**Relevance**: 9/10

**Key Pages**:

- **Usage Guide**: https://magicstack.github.io/asyncpg/current/usage.html
  - **Use Case**: Learn connection pools, transaction management, and resource cleanup
  - **Key Concepts**:
    - Connection pools recommended for server applications
    - Use `asyncpg.create_pool()` to create pool
    - Acquire connections with async context manager
    - Transactions use `connection.transaction()`
    - Auto-commit mode when not in explicit transaction

- **API Reference**: https://magicstack.github.io/asyncpg/current/api/index.html
  - **Use Case**: Complete API for Pool, Connection, Transaction classes
  - **Key Concepts**:
    - Pool methods: acquire(), close(), set_connect_args()
    - Connection methods: fetchval(), fetchrow(), execute()
    - Transaction methods: start(), commit(), rollback()

**Code Examples**:

```python
# Example 1: Creating and using connection pool
# Source: https://magicstack.github.io/asyncpg/current/usage.html
import asyncpg

# Create pool
pool = await asyncpg.create_pool(
    user='user',
    password='password',
    database='database',
    host='127.0.0.1'
)

# Use pool with async context manager
async with pool.acquire() as connection:
    result = await connection.fetchval('SELECT 2 ^ $1', power)

# Close pool when done
await pool.close()
```

```python
# Example 2: Transaction management
# Source: https://magicstack.github.io/asyncpg/current/usage.html
async with connection.transaction():
    await connection.execute("INSERT INTO mytable VALUES(1, 2, 3)")
    # Automatically commits on exit or rolls back on exception
```

```python
# Example 3: Multiple operations in transaction
async with pool.acquire() as connection:
    async with connection.transaction():
        # Insert document
        doc_id = await connection.fetchval(
            "INSERT INTO documents (title) VALUES ($1) RETURNING id",
            "My Document"
        )
        # Insert chunks
        await connection.execute(
            "INSERT INTO chunks (document_id, content) VALUES ($1, $2)",
            doc_id, "chunk content"
        )
```

**Testing Considerations**:
- Mock pool with `MagicMock` + `AsyncMock` for `__aenter__`/`__aexit__`
- Mock connection methods: `fetchval`, `fetchrow`, `execute`, `executemany`
- Use `side_effect` list for multi-step operations (insert then select)
- Connection reset happens on release (cursors/listeners removed)
- Prepared statements invalid after connection release

---

### 3. pytest-cov (Code Coverage)
**Official Docs**: https://pytest-cov.readthedocs.io/
**Purpose**: Measure code coverage during pytest execution
**Archon Source**: Not in Archon
**Relevance**: 8/10

**Key Pages**:

- **Overview**: https://pytest-cov.readthedocs.io/en/latest/readme.html
  - **Use Case**: Setup and basic usage for coverage reporting
  - **Key Concepts**:
    - Install: `pip install pytest-cov`
    - Run: `pytest --cov=src --cov-report=term-missing`
    - Coverage contexts with `--cov-context=test`
    - Xdist support for parallel testing
    - Automatic .coverage file management

**Usage Examples**:

```bash
# Example 1: Basic coverage with terminal report
pytest tests/ --cov=src --cov-report=term-missing

# Example 2: HTML coverage report
pytest tests/ --cov=src --cov-report=html

# Example 3: Branch coverage
pytest tests/ --cov=src --cov-branch --cov-report=term-missing

# Example 4: Coverage with minimum threshold (80%)
pytest tests/ --cov=src --cov-fail-under=80
```

**Integration with Quality Gates**:
```bash
# Level 2: Unit tests with coverage check
pytest tests/unit/ -v --cov=src --cov-report=term-missing --cov-fail-under=80
```

---

### 4. HTTPX (Async HTTP Client)
**Official Docs**: https://www.python-httpx.org/
**Purpose**: AsyncClient for testing FastAPI async endpoints
**Archon Source**: Not in Archon
**Relevance**: 8/10

**Key Pages**:

- **AsyncClient**: https://www.python-httpx.org/async/
  - **Use Case**: Testing async FastAPI endpoints with async database operations
  - **Key Concepts**:
    - Use `AsyncClient` instead of TestClient for async tests
    - Supports HTTP/1.1 and HTTP/2
    - Context manager for resource cleanup
    - Full async/await support

**Code Example**:

```python
# Testing async FastAPI endpoint
# Source: FastAPI docs + HTTPX docs
from httpx import AsyncClient
from fastapi import FastAPI
import pytest

app = FastAPI()

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    # Async database query here
    return {"item_id": item_id}

@pytest.mark.asyncio
async def test_read_item():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/items/42")
    assert response.status_code == 200
    assert response.json() == {"item_id": 42}
```

---

## Integration Guides

### FastAPI + asyncpg Testing Pattern
**Guide URL**: https://testdriven.io/blog/fastapi-crud/
**Source Type**: Tutorial (High-quality third-party)
**Quality**: 9/10
**Archon Source**: Not in Archon

**What it covers**:
- Setting up async database fixtures
- FastAPI dependency override for database connections
- Testing CRUD operations with TestClient
- Transaction rollback for test isolation
- Async test patterns with pytest-asyncio

**Code examples**:

```python
# Async database fixture with transaction rollback
@pytest_asyncio.fixture
async def test_db():
    # Create test database
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Yield session
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        yield session

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
```

**Applicable patterns**:
- Use transaction rollback for test isolation (avoid test data pollution)
- Override FastAPI dependencies with `app.dependency_overrides`
- Create module-scoped fixtures for expensive database setup
- Use AsyncClient for testing async endpoints with database operations

---

### Playwright + pytest Integration
**Guide URL**: https://playwright.dev/python/docs/intro
**Source Type**: Official
**Quality**: 10/10
**Archon Source**: Not in Archon

**What it covers**:
- Installing pytest-playwright plugin
- Using page fixture in tests
- Browser configuration and selection
- Headless vs headed mode
- Screenshot and video recording

**Code examples**:

```python
# pytest-playwright integration
# Source: https://playwright.dev/python/docs/intro
import re
from playwright.sync_api import Page, expect

def test_homepage_has_title(page: Page):
    page.goto("https://playwright.dev/")
    expect(page).to_have_title(re.compile("Playwright"))

def test_get_started_link(page: Page):
    page.goto("https://playwright.dev/")
    page.get_by_role("link", name="Get started").click()
    expect(page.get_by_role("heading", name="Installation")).to_be_visible()
```

**Applicable patterns**:
- Use page fixture from pytest-playwright (automatic browser lifecycle)
- Semantic locators for stable element selection
- expect() assertions for auto-waiting validation
- No manual browser setup/teardown needed

---

### FastAPI File Upload Testing
**Guide URL**: Stack Overflow discussions + FastAPI docs
**Source Type**: Community + Official
**Quality**: 8/10
**Archon Source**: Not in Archon

**What it covers**:
- Testing multipart/form-data endpoints
- Sending files with TestClient
- Combining form fields and file uploads
- Handling UploadFile in tests

**Code examples**:

```python
# Testing file upload endpoint
# Source: Stack Overflow + FastAPI docs
from fastapi.testclient import TestClient
from io import BytesIO

def test_file_upload():
    # Create test file
    file_content = b"test file content"
    file = BytesIO(file_content)

    # Send multipart request
    response = client.post(
        "/api/upload",
        data={"title": "Test Document", "source_id": "123"},  # Form fields
        files={"file": ("test.txt", file, "text/plain")}  # File upload
    )

    assert response.status_code == 200
    assert response.json()["filename"] == "test.txt"
```

**Applicable patterns**:
- Use `data={}` for form fields, `files={}` for file uploads
- Don't set Content-Type manually (TestClient handles it)
- Use BytesIO for in-memory test files
- Specify filename and content type in files tuple

---

## Best Practices Documentation

### Async Testing with pytest-asyncio
**Resource**: https://pytest-asyncio.readthedocs.io/en/latest/concepts.html
**Type**: Official Guide
**Relevance**: 10/10

**Key Practices**:

1. **Use consistent event loop scopes**: Keep all tests in a class/module on the same loop scope
   - **Why**: Maintains clarity and prevents subtle bugs
   - **Example**:
   ```python
   # All tests in this module share module-scoped loop
   @pytest.mark.asyncio(loop_scope="module")
   async def test_1():
       pass

   @pytest.mark.asyncio(loop_scope="module")
   async def test_2():
       pass
   ```

2. **Match fixture scope with event loop scope**: Non-function scoped fixtures need matching event_loop scope
   - **Why**: Prevents event loop mismatch errors
   - **Example**:
   ```python
   @pytest_asyncio.fixture(scope="module")
   async def db_pool():
       pool = await create_pool()
       yield pool
       await pool.close()
   ```

3. **Tests run sequentially, not concurrently**: Embrace sequential execution for test isolation
   - **Why**: Prevents race conditions and maintains test independence
   - **Example**: Don't use asyncio.gather() in test suite

4. **Use strict mode for mixed async libraries**: Explicit markers prevent conflicts
   - **Why**: Allows coexistence with other async frameworks
   - **Example**: Only `@pytest.mark.asyncio` tests are treated as asyncio tests

---

### Playwright Auto-Waiting Best Practices
**Resource**: https://playwright.dev/python/docs/actionability
**Type**: Official Guide
**Relevance**: 10/10

**Key Practices**:

1. **Trust auto-wait, avoid sleep()**: Playwright waits automatically for actionability
   - **Why**: Eliminates flaky tests from arbitrary timeouts
   - **Example**:
   ```python
   # ❌ WRONG - Manual sleep
   page.click("#button")
   time.sleep(3)

   # ✅ RIGHT - Auto-wait
   page.locator("#button").click()  # Waits for actionability
   ```

2. **Set appropriate timeouts per operation**: Different operations need different timeouts
   - **Why**: UI actions (5s) vs file uploads (30s) vs API calls (60s)
   - **Example**:
   ```python
   page.locator("#upload-button").click(timeout=5000)
   page.wait_for_selector(".success-message", timeout=30000)  # Upload processing
   ```

3. **Use semantic locators, not CSS**: Role-based locators are resilient to changes
   - **Why**: CSS selectors break when DOM structure changes
   - **Example**:
   ```python
   # ❌ WRONG - Brittle CSS selector
   page.locator("div.container > button.primary").click()

   # ✅ RIGHT - Semantic locator
   page.get_by_role("button", name="Submit").click()
   ```

4. **Verify state with expect(), not assertions**: Auto-waiting assertions
   - **Why**: expect() retries until condition passes or timeout
   - **Example**:
   ```python
   # ❌ WRONG - No auto-wait
   assert page.locator(".success").is_visible()

   # ✅ RIGHT - Auto-wait with expect
   expect(page.locator(".success")).to_be_visible()
   ```

---

### FastAPI Dependency Override Testing Pattern
**Resource**: https://fastapi.tiangolo.com/advanced/testing-dependencies/
**Type**: Official Guide
**Relevance**: 10/10

**Key Practices**:

1. **Always reset overrides after tests**: Prevent test pollution
   - **Why**: Global state affects subsequent tests
   - **Example**:
   ```python
   def test_with_override():
       app.dependency_overrides[get_db] = lambda: mock_db
       # Run test
       response = client.get("/items")
       # Reset
       app.dependency_overrides = {}
   ```

2. **Use fixtures for scoped overrides**: Automatic cleanup
   - **Why**: Ensures overrides are removed even if test fails
   - **Example**:
   ```python
   @pytest.fixture
   def override_db():
       app.dependency_overrides[get_db] = lambda: mock_db
       yield
       app.dependency_overrides = {}
   ```

3. **Mock external services, not business logic**: Test real code, fake I/O
   - **Why**: Maintain confidence in application behavior
   - **Example**: Override database connection, not validation functions

4. **Match signature of original dependency**: Prevent type errors
   - **Why**: FastAPI uses type hints for validation
   - **Example**:
   ```python
   # Original dependency
   async def get_db() -> AsyncSession:
       ...

   # Override with matching signature
   async def override_get_db() -> AsyncSession:
       return mock_session
   ```

---

## Testing Documentation

### pytest Test Discovery
**Official Docs**: https://docs.pytest.org/en/stable/getting-started.html
**Archon Source**: Not in Archon

**Relevant Sections**:

- **Test Discovery Rules**: Automatic test collection
  - **Files**: `test_*.py` or `*_test.py`
  - **Functions**: `test_*` functions or methods
  - **Classes**: `Test*` classes with `test_*` methods
  - **Location**: Current directory and subdirectories

**Test Organization**:
```
tests/
├── unit/
│   ├── test_document_upload.py
│   ├── test_search_filtering.py
│   └── test_delete_operations.py
├── integration/
│   ├── test_crawl_api.py
│   ├── test_document_api.py
│   └── test_source_api.py
└── browser/
    ├── test_upload_flow.py
    ├── test_search_flow.py
    └── test_delete_flow.py
```

---

### pytest-cov Coverage Reports
**Official Docs**: https://pytest-cov.readthedocs.io/en/latest/readme.html
**Archon Source**: Not in Archon

**Coverage Commands**:

```bash
# Terminal report with missing lines
pytest --cov=src --cov-report=term-missing

# HTML report (opens in browser)
pytest --cov=src --cov-report=html
open htmlcov/index.html

# XML report (for CI/CD)
pytest --cov=src --cov-report=xml

# Multiple report types
pytest --cov=src --cov-report=term-missing --cov-report=html --cov-report=xml

# Fail if coverage below threshold
pytest --cov=src --cov-fail-under=80
```

**Test Coverage Goals**:
- Unit tests: >80% code coverage
- Integration tests: API endpoint coverage
- Browser tests: Critical user flows

---

## Additional Resources

### Tutorials with Code

1. **A Practical Guide To Async Testing With Pytest-Asyncio**: https://pytest-with-eric.com/pytest-advanced/pytest-asyncio/
   - **Format**: Blog with code examples
   - **Quality**: 9/10
   - **What makes it useful**: Comprehensive examples of async fixtures, event loop configuration, and common pitfalls

2. **Developing and Testing an Asynchronous API with FastAPI and Pytest**: https://testdriven.io/blog/fastapi-crud/
   - **Format**: Blog with working code
   - **Quality**: 9/10
   - **What makes it useful**: Complete CRUD app with async database testing, dependency injection, and transaction management

3. **React Testing Library Tutorial**: https://www.robinwieruch.de/react-testing-library/
   - **Format**: Blog tutorial
   - **Quality**: 9/10
   - **What makes it useful**: User-centric testing approach, query patterns, and best practices for component testing

4. **The ultimate Playwright Python tutorial**: https://www.browserstack.com/guide/playwright-python-tutorial
   - **Format**: Comprehensive guide
   - **Quality**: 8/10
   - **What makes it useful**: Installation, browser configuration, locator strategies, and practical examples

5. **Testing FastAPI FormData Upload**: https://stackoverflow.com/questions/63614660/testing-fastapi-formdata-upload
   - **Format**: Stack Overflow Q&A
   - **Quality**: 8/10
   - **What makes it useful**: Specific solution for multipart file upload testing with TestClient

### API References

1. **pytest API Reference**: https://docs.pytest.org/en/stable/reference/reference.html
   - **Coverage**: All pytest decorators, fixtures, and commands
   - **Examples**: Yes, comprehensive

2. **Playwright Python API Reference**: https://playwright.dev/python/docs/api/class-playwright
   - **Coverage**: Page, Locator, Browser, BrowserContext classes
   - **Examples**: Yes, with code snippets

3. **FastAPI API Reference**: https://fastapi.tiangolo.com/reference/
   - **Coverage**: FastAPI class, dependency injection, TestClient, responses
   - **Examples**: Yes, detailed

4. **asyncpg API Reference**: https://magicstack.github.io/asyncpg/current/api/index.html
   - **Coverage**: Pool, Connection, Transaction, Record classes
   - **Examples**: Some, with usage patterns

### Community Resources

1. **pytest-asyncio GitHub**: https://github.com/pytest-dev/pytest-asyncio
   - **Type**: GitHub repository
   - **Why included**: Issue tracker, examples, and changelog for async testing

2. **FastAPI GitHub Discussions**: https://github.com/fastapi/fastapi/discussions
   - **Type**: GitHub discussions
   - **Why included**: Community solutions for testing patterns and edge cases

3. **Playwright Community Forum**: https://playwright.tech/
   - **Type**: Community blog and forum
   - **Why included**: Real-world examples and troubleshooting guides

4. **Python asyncio Documentation**: https://docs.python.org/3/library/asyncio.html
   - **Type**: Official Python docs
   - **Why included**: Foundation for understanding async patterns in tests

---

## Documentation Gaps

**Not found in Archon or Web**:
- **MCP Browser Tools Official Documentation**: No comprehensive docs for `browser_navigate`, `browser_snapshot`, `browser_click`, etc. from MCP_DOCKER server
  - **Recommendation**: Reference CLAUDE.md Browser Testing section and existing patterns in `.claude/patterns/browser-validation.md`
  - **Alternative**: Use Playwright documentation as foundation; MCP tools are wrappers around Playwright

- **Crawl4AI Documentation**: Limited docs on configuration options for content truncation issue
  - **Recommendation**: Review Crawl4AI GitHub issues and source code for chunking configuration
  - **Alternative**: Test with different chunking parameters empirically

**Outdated or Incomplete**:
- **Playwright Accessibility API**: `accessibility.snapshot()` is deprecated
  - **Issue**: Official docs still reference it
  - **Suggested alternative**: Use ARIA snapshots (https://playwright.dev/docs/aria-snapshots) or accessibility tree from `browser_snapshot()` MCP tool

- **pytest-asyncio Event Loop Fixture**: Documentation scattered across versions
  - **Issue**: Different approaches in v0.20 vs v1.0+
  - **Suggested alternative**: Use latest docs (v1.2+) and auto mode for simplicity

---

## Quick Reference URLs

For easy copy-paste into PRP:

```yaml
Framework Docs:
  - pytest: https://docs.pytest.org/en/stable/contents.html
  - pytest-asyncio: https://pytest-asyncio.readthedocs.io/en/latest/
  - FastAPI: https://fastapi.tiangolo.com/
  - Playwright Python: https://playwright.dev/python/

Library Docs:
  - unittest.mock: https://docs.python.org/3/library/unittest.mock.html
  - asyncpg: https://magicstack.github.io/asyncpg/current/
  - pytest-cov: https://pytest-cov.readthedocs.io/
  - HTTPX: https://www.python-httpx.org/

Integration Guides:
  - FastAPI Testing: https://fastapi.tiangolo.com/advanced/testing-dependencies/
  - FastAPI Async Tests: https://fastapi.tiangolo.com/advanced/async-tests/
  - Playwright pytest: https://playwright.dev/python/docs/intro
  - FastAPI File Upload: https://fastapi.tiangolo.com/tutorial/request-forms-and-files/

Testing Docs:
  - pytest Fixtures: https://docs.pytest.org/en/stable/how-to/fixtures.html
  - pytest Parametrize: https://docs.pytest.org/en/stable/how-to/parametrize.html
  - Playwright Locators: https://playwright.dev/python/docs/locators
  - Playwright Auto-wait: https://playwright.dev/python/docs/actionability

API References:
  - pytest API: https://docs.pytest.org/en/stable/reference/reference.html
  - FastAPI TestClient: https://fastapi.tiangolo.com/reference/testclient/
  - Playwright Page: https://playwright.dev/python/docs/api/class-page
  - Playwright Locator: https://playwright.dev/python/docs/api/class-locator
  - asyncpg API: https://magicstack.github.io/asyncpg/current/api/index.html

Tutorials:
  - Async Testing Guide: https://pytest-with-eric.com/pytest-advanced/pytest-asyncio/
  - FastAPI CRUD Testing: https://testdriven.io/blog/fastapi-crud/
  - Playwright Tutorial: https://www.browserstack.com/guide/playwright-python-tutorial
```

---

## Recommendations for PRP Assembly

When generating the PRP:

1. **Include these URLs** in "Documentation & References" section
   - Organize by category (Framework, Library, Integration)
   - Link directly to specific sections for implementation tasks

2. **Extract code examples** shown above into PRP context
   - AsyncMock patterns for database mocking
   - Playwright semantic locator examples
   - FastAPI dependency override patterns
   - File upload testing examples

3. **Highlight gotchas** from documentation in "Known Gotchas" section
   - Dependency overrides are global (must reset)
   - Playwright element refs change on render
   - pytest-asyncio event loop scope matching
   - TestClient vs AsyncClient usage
   - File upload multipart encoding

4. **Reference specific sections** in implementation tasks
   - Task: "Create document upload test" → Link: FastAPI File Upload docs
   - Task: "Implement browser validation" → Link: Playwright Locators guide
   - Task: "Mock database pool" → Link: unittest.mock AsyncMock examples

5. **Note gaps** so implementation can compensate
   - No MCP browser tools docs → Use Playwright docs + CLAUDE.md patterns
   - Crawl4AI truncation issue → Empirical testing needed
   - Deprecated accessibility API → Use ARIA snapshots or MCP browser_snapshot()

---

## Archon Ingestion Candidates

**Documentation not in Archon but should be**:

- **pytest Official Docs** (https://docs.pytest.org/en/stable/) - Why: Core testing framework, referenced in every PRP
- **pytest-asyncio Docs** (https://pytest-asyncio.readthedocs.io/) - Why: Essential for async testing patterns
- **FastAPI Testing Docs** (https://fastapi.tiangolo.com/advanced/testing-dependencies/) - Why: Frequently used for API testing
- **Playwright Python Docs** (https://playwright.dev/python/) - Why: Browser automation for frontend validation
- **unittest.mock Docs** (https://docs.python.org/3/library/unittest.mock.html) - Why: Standard mocking patterns for all tests
- **asyncpg Usage Guide** (https://magicstack.github.io/asyncpg/current/usage.html) - Why: Async database patterns
- **FastAPI CRUD Testing Tutorial** (https://testdriven.io/blog/fastapi-crud/) - Why: Complete working example of async testing

**Why these are valuable for future PRPs**:
- Testing is required for every feature implementation
- Async patterns are used throughout the codebase
- Browser testing will be standard for UI features
- These docs contain working code examples that can be referenced directly
- Reduces web search time and ensures consistent patterns

[This helps improve Archon knowledge base over time]
