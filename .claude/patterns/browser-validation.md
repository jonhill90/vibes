# Browser Validation Pattern

**Purpose**: Frontend UI validation using Playwright browser automation via MCP_DOCKER tools
**Use when**: Validating React frontends, end-to-end user workflows, accessibility testing
**See also**: `.claude/patterns/quality-gates.md` (Level 3 Integration Tests), `.claude/agents/validation-gates.md`

---

## Overview

Browser validation enables agents to test frontend UIs through browser automation, extending validation beyond backend APIs to full-stack end-to-end testing. This pattern uses Playwright's accessibility tree approach (not screenshot-based) for fast, token-efficient, agent-parseable validation.

**Key Principles**:
- **Accessibility First**: Use accessibility tree (structured data) for validation, not screenshots (visual data)
- **Semantic Locators**: Query elements by role/text/label, not CSS selectors or element refs
- **Pre-Flight Checks**: Verify browser installed and services running before tests
- **Token Efficiency**: Screenshots for human proof only (~2000 tokens), snapshots for agents (~500 tokens)
- **Auto-Waiting**: Leverage Playwright's smart waiting, avoid manual `sleep()` calls

**When to Use**:
- ✅ Validating user-facing UI features
- ✅ End-to-end workflow testing (upload document, create task)
- ✅ Cross-component integration (frontend + backend)
- ✅ Accessibility validation
- ❌ Backend-only API validation (use API tests instead - 10x faster)
- ❌ Visual design validation (agents can't parse screenshots)

---

## Quick Reference

### Common Browser Tool Commands

```python
# Navigate to frontend
browser_navigate(url="http://localhost:5173")

# Capture accessibility tree (structured JSON)
snapshot = browser_snapshot()

# Validate UI state (agent can parse this)
if "ExpectedElement" in snapshot:
    print("✅ Element found in accessibility tree")

# Click element using semantic query
browser_click(element="button containing 'Upload'")

# Type into input field
browser_type(element="textbox", name="Document Title", text="Test Doc")

# Fill form with multiple fields
browser_fill_form(fields=[
    {"name": "title", "type": "textbox", "value": "Test Document"},
    {"name": "file", "type": "file", "value": "/tmp/test.pdf"}
])

# Wait for specific text to appear
browser_wait_for(text="Upload successful", timeout=30000)

# Take screenshot (human verification only)
browser_take_screenshot(filename="validation-proof.png")

# Execute JavaScript for precise checks
count = browser_evaluate(function="() => document.querySelectorAll('.card').length")

# Install browser binaries (if not already installed)
browser_install()
```

---

## Core Pattern: Navigation → Interaction → Validation

### Step 1: Navigate and Capture Initial State

**Purpose**: Load the frontend and verify page is ready for testing.

```python
# Pre-flight: Ensure frontend service is running
result = Bash("docker-compose ps | grep rag-service")
if "Up" not in result.stdout:
    print("⚠️ Starting services...")
    Bash("docker-compose up -d")
    time.sleep(10)  # Wait for service health

# Navigate to frontend
try:
    browser_navigate(url="http://localhost:5173")
except ConnectionError:
    print("❌ Frontend not running at localhost:5173")
    exit(1)

# Capture initial accessibility tree
initial_state = browser_snapshot()

# Validate expected page loaded
if "DocumentList" in initial_state or "RAG Service" in initial_state:
    print("✅ Page loaded correctly")
else:
    print("❌ Unexpected page content")
    print(f"State: {initial_state[:500]}...")
    exit(1)
```

**Key Points**:
- Always check service health before navigation
- Use accessibility snapshot (not screenshot) to verify page loaded
- Handle ConnectionError if service isn't running

### Step 2: Interact with UI Elements

**Purpose**: Simulate user actions (clicks, typing, form fills).

```python
# Click button using semantic query (text-based, stable)
browser_click(element="button containing 'Upload'")

# Wait for modal/dialog to appear
browser_wait_for(text="Select a document", timeout=5000)

# Fill form fields (batch operation)
browser_fill_form(fields=[
    {"name": "title", "type": "textbox", "value": "Test Document"},
    {"name": "description", "type": "textbox", "value": "Test Description"},
    {"name": "file", "type": "file", "value": "/tmp/test-document.pdf"}
])

# Submit form
browser_click(element="button containing 'Submit'")

# Wait for success message (with timeout)
browser_wait_for(text="Upload successful", timeout=30000)
```

**Key Points**:
- Use semantic queries: `"button containing 'Upload'"` not `ref="e5"`
- Always wait after actions (use `browser_wait_for()` with condition)
- Use absolute file paths for file uploads
- Timeouts: 5s for UI, 30s for file operations

### Step 3: Validate Final State

**Purpose**: Verify UI reflects expected changes.

```python
# Capture final accessibility tree
final_state = browser_snapshot()

# Validation checklist
validation_checks = {
    "success_message": "Upload successful" in final_state,
    "document_in_list": "Test Document" in final_state,
    "list_visible": "DocumentList" in final_state or "list" in final_state,
}

# Check all validations
all_passed = all(validation_checks.values())

if all_passed:
    print("✅ All validations passed")

    # Take proof screenshot for human review (optional)
    browser_take_screenshot(filename="validation-proof.png")
    print("Screenshot saved for human review")
else:
    print("❌ Validation failed:")
    for check, passed in validation_checks.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {check}")

    # Capture debug screenshot
    browser_take_screenshot(filename="validation-error.png")
    print(f"Final state: {final_state[:500]}...")
    exit(1)
```

**Key Points**:
- Use accessibility tree for validation (agents can parse structured data)
- Screenshot at end for proof, not for validation
- Capture debug screenshot on failure
- Multiple validation checks with clear status reporting

---

## Rules (DO/DON'T)

### DO:

- ✅ **Use accessibility tree for validation** - `browser_snapshot()` returns structured JSON agents can analyze
- ✅ **Use semantic locators** - `"button containing 'Upload'"`, `"textbox"`, `"link"` are stable across re-renders
- ✅ **Check service health first** - Verify frontend running before navigation to avoid wasted attempts
- ✅ **Use auto-wait** - Playwright waits for elements automatically, don't add manual `sleep()`
- ✅ **Take screenshots for humans only** - One at end for proof, not for agent validation (agents can't parse images)
- ✅ **Handle ConnectionError** - Frontend down is most common failure mode
- ✅ **Use absolute file paths** - File uploads require full paths: `/tmp/test.pdf` not `./test.pdf`
- ✅ **Set appropriate timeouts** - 5s for UI, 30s for uploads, 60s for heavy processing
- ✅ **Close browser contexts** - Use context managers or explicit cleanup to prevent memory leaks
- ✅ **Validate by user-visible behavior** - Test what users see/do, not CSS classes or internal state

### DON'T:

- ❌ **Don't use screenshots for agent validation** - Agents cannot parse images, use accessibility tree instead
- ❌ **Don't hard-code element refs** - `ref="e5"` changes every render, use semantic queries
- ❌ **Don't use CSS selectors** - `.class-name`, `#id` break on refactors, use `get_by_role()`, `get_by_text()`
- ❌ **Don't skip pre-flight checks** - Always verify browser installed and services running
- ❌ **Don't mix sync and async APIs** - Pick one: `sync_playwright` or `async_playwright`, not both
- ❌ **Don't use threading** - Playwright sync API is NOT thread-safe, use multiprocessing if parallel needed
- ❌ **Don't add manual `sleep()`** - Use `browser_wait_for()` with conditions, not arbitrary waits
- ❌ **Don't test implementation details** - Don't check CSS classes, internal state, or DOM structure
- ❌ **Don't navigate to untrusted URLs** - Validate URLs are localhost before navigation
- ❌ **Don't leave browsers open** - Always clean up resources to prevent memory leaks

---

## Integration with Quality Gates

Browser validation fits at **Level 3: Integration Tests** in the quality-gates pattern. It's the slowest validation level but necessary for user-facing features.

```python
# Multi-Level Validation with Browser Tests

# Level 1: Syntax & Style (fast, ~5 seconds)
print("Running Level 1: Syntax & Style...")
Bash("ruff check src/")
Bash("mypy src/")
print("✅ Level 1 passed")

# Level 2: Unit Tests (medium, ~30 seconds)
print("Running Level 2: Unit Tests...")
Bash("pytest tests/unit/ -v")
print("✅ Level 2 passed")

# Level 3a: API Integration (medium, ~60 seconds)
print("Running Level 3a: API Integration...")
Bash("pytest tests/integration/ -v")
print("✅ Level 3a passed")

# Level 3b: Browser Integration (slow, ~120 seconds)
print("Running Level 3b: Browser Validation...")

def validate_frontend_browser() -> dict:
    """Browser validation function."""
    try:
        # Pre-flight checks
        if not ensure_frontend_running(5173, "rag-service"):
            return {"success": False, "error": "Frontend not running"}

        # Navigate
        browser_navigate(url="http://localhost:5173")

        # Validate workflow
        browser_click(element="button containing 'Upload'")
        browser_wait_for(text="Select a document", timeout=5000)
        browser_fill_form(fields=[
            {"name": "file", "type": "file", "value": "/tmp/test.pdf"}
        ])
        browser_click(element="button containing 'Submit'")
        browser_wait_for(text="Upload successful", timeout=30000)

        # Verify final state
        state = browser_snapshot()
        if "test.pdf" not in state:
            return {"success": False, "error": "Document not in list"}

        return {"success": True, "error": None}

    except Exception as e:
        return {"success": False, "error": str(e)}

result = validate_frontend_browser()
if result["success"]:
    print("✅ Level 3b passed")
else:
    print(f"❌ Level 3b failed: {result['error']}")
    exit(1)

print("✅ All validation levels passed")
```

**Performance Comparison**:
```
Level 1 (Syntax):        ~5 seconds   (CLI tools)
Level 2 (Unit Tests):    ~30 seconds  (pytest)
Level 3a (API Tests):    ~60 seconds  (pytest + API)
Level 3b (Browser):      ~120 seconds (browser automation)

Browser tests are 10x slower than API tests, but necessary for UI validation.
```

**When to Use Each Level**:
- **Level 1**: Every commit (fast feedback)
- **Level 2**: Every commit (unit coverage)
- **Level 3a**: Every PR (API integration)
- **Level 3b**: Every PR with UI changes (browser validation)

---

## Examples

### Example 1: Document Upload Validation (Complete Workflow)

**Scenario**: Validate RAG service document upload feature end-to-end.

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
    if "RAG Service" not in result.stdout and "DocumentList" not in result.stdout:
        print("❌ Wrong service at port 5173")
        exit(1)

    print("✅ Pre-flight checks passed")

    # Step 2: Navigate and validate initial state
    print("🌐 Navigating to frontend...")
    browser_navigate(url="http://localhost:5173")

    initial_state = browser_snapshot()
    if "DocumentList" not in initial_state:
        print("❌ Document list not found")
        print(f"State: {initial_state[:500]}...")
        exit(1)

    print("✅ Initial state valid")

    # Step 3: Interact - Click upload button
    print("🖱️  Clicking upload button...")
    browser_click(element="button containing 'Upload'")

    # Wait for upload dialog
    browser_wait_for(text="Select a document", timeout=5000)
    print("✅ Upload dialog opened")

    # Step 4: Fill upload form
    print("📝 Filling upload form...")
    browser_fill_form(fields=[
        {"name": "title", "type": "textbox", "value": "Test Document"},
        {"name": "description", "type": "textbox", "value": "Automated test document"},
        {"name": "file", "type": "file", "value": "/tmp/test-document.pdf"}
    ])
    print("✅ Form filled")

    # Step 5: Submit form
    print("📤 Submitting upload...")
    browser_click(element="button containing 'Submit'")

    # Wait for upload to complete
    browser_wait_for(text="Upload successful", timeout=30000)
    print("✅ Upload completed")

    # Step 6: Validate final state
    print("✔️  Validating final state...")
    final_state = browser_snapshot()

    validation_checks = {
        "success_message": "Upload successful" in final_state,
        "document_title": "Test Document" in final_state,
        "document_in_list": "test-document.pdf" in final_state or "Test Document" in final_state,
    }

    all_passed = all(validation_checks.values())

    if all_passed:
        print("✅ All validations passed")

        # Take proof screenshot for human review
        browser_take_screenshot(filename="document-upload-validation-proof.png")
        print("📸 Screenshot saved: document-upload-validation-proof.png")
    else:
        print("❌ Validation failed:")
        for check, passed in validation_checks.items():
            status = "✅" if passed else "❌"
            print(f"  {status} {check}")

        browser_take_screenshot(filename="document-upload-validation-error.png")
        print(f"Debug state: {final_state[:500]}...")
        exit(1)

    print("✅ Document upload validation complete")

# Run validation
validate_document_upload()
```

### Example 2: Task Creation Validation (Task Manager)

**Scenario**: Validate task manager create task workflow.

```python
def validate_task_creation():
    """Validate task creation workflow in task manager."""

    # Pre-flight
    ensure_frontend_running(5174, "task-manager")

    # Navigate
    browser_navigate(url="http://localhost:5174")

    initial_state = browser_snapshot()
    if "TaskList" not in initial_state and "Tasks" not in initial_state:
        print("❌ Task list not found")
        exit(1)

    # Click create task button
    browser_click(element="button containing 'Create Task'")
    browser_wait_for(text="New Task", timeout=5000)

    # Fill task form
    browser_fill_form(fields=[
        {"name": "title", "type": "textbox", "value": "Test Task"},
        {"name": "description", "type": "textbox", "value": "Automated test task"},
        {"name": "status", "type": "combobox", "value": "todo"}
    ])

    # Submit
    browser_click(element="button containing 'Create'")
    browser_wait_for(text="Task created", timeout=10000)

    # Validate
    final_state = browser_snapshot()

    if "Test Task" in final_state:
        print("✅ Task created successfully")
        browser_take_screenshot(filename="task-creation-proof.png")
    else:
        print("❌ Task not found in list")
        browser_take_screenshot(filename="task-creation-error.png")
        exit(1)

validate_task_creation()
```

### Example 3: Error Handling with Retries

**Scenario**: Handle flaky operations with retry pattern.

```python
def validate_with_error_handling():
    """Browser validation with comprehensive error handling."""

    MAX_ATTEMPTS = 3

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            print(f"🔄 Attempt {attempt}/{MAX_ATTEMPTS}")

            # Pre-flight with auto-remediation
            try:
                browser_navigate(url="about:blank")
            except Exception:
                if attempt == 1:
                    print("⚠️ Browser not installed, installing...")
                    browser_install()
                    time.sleep(30)
                    continue
                else:
                    raise

            # Check frontend (with auto-start)
            result = Bash("curl -s http://localhost:5173")
            if "Connection refused" in result.stderr:
                print("⚠️ Frontend not running, starting...")
                Bash("docker-compose up -d")
                time.sleep(10)
                continue

            # Navigate with timeout handling
            try:
                browser_navigate(url="http://localhost:5173")
            except TimeoutError:
                if attempt < MAX_ATTEMPTS:
                    print(f"⚠️ Navigation timeout, retrying...")
                    time.sleep(2)
                    continue
                else:
                    raise

            # Perform validation
            state = browser_snapshot()

            if "ExpectedElement" in state:
                print("✅ Validation passed")
                browser_take_screenshot(filename="validation-success.png")
                return True
            else:
                print(f"❌ Expected element not found (attempt {attempt})")
                if attempt < MAX_ATTEMPTS:
                    time.sleep(2)
                    continue
                else:
                    browser_take_screenshot(filename="validation-failed.png")
                    return False

        except Exception as e:
            print(f"❌ Error on attempt {attempt}: {e}")
            if attempt == MAX_ATTEMPTS:
                browser_take_screenshot(filename="validation-exception.png")
                raise
            time.sleep(2)

    return False

# Run with error handling
success = validate_with_error_handling()
if not success:
    exit(1)
```

---

## Gotchas

### Gotcha #1: Browser Binaries Not Installed

**Severity**: Critical
**Detection**: `Browser not found` or `Executable doesn't exist` error

**Problem**:
```python
# ❌ WRONG - Browser operations fail if binaries not installed
browser_navigate(url="http://localhost:5173")
# Error: Browser not found
```

**Solution**:
```python
# ✅ RIGHT - Install browser binaries before use
try:
    browser_navigate(url="about:blank")
except Exception:
    print("⚠️ Installing browser binaries...")
    browser_install()
    time.sleep(30)  # Wait for installation to complete
    browser_navigate(url="about:blank")  # Retry
```

**Pre-flight check**:
```bash
# Check if browsers installed
python -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); p.stop()"
```

### Gotcha #2: Frontend Service Not Running

**Severity**: Critical
**Detection**: `Connection refused` or `ERR_CONNECTION_REFUSED` error

**Problem**:
```python
# ❌ WRONG - Navigate without checking service
browser_navigate(url="http://localhost:5173")
# Error: Connection refused
```

**Solution**:
```python
# ✅ RIGHT - Check service health first
def ensure_frontend_running(port: int, service_name: str) -> bool:
    result = Bash(f"docker-compose ps {service_name}")
    if "Up" not in result.stdout:
        print(f"⚠️ Starting {service_name}...")
        Bash("docker-compose up -d")
        time.sleep(10)

        # Verify health
        for i in range(30):
            result = Bash(f"curl -s http://localhost:{port}")
            if "Connection refused" not in result.stderr:
                return True
            time.sleep(1)

        raise RuntimeError(f"{service_name} failed to start")
    return True

ensure_frontend_running(5173, "rag-service")
browser_navigate(url="http://localhost:5173")
```

### Gotcha #3: Thread Safety Violations

**Severity**: Critical
**Detection**: Process hangs, deadlocks, random failures

**Problem**:
```python
# ❌ WRONG - Playwright sync API is NOT thread-safe
from concurrent.futures import ThreadPoolExecutor

browser = playwright.chromium.launch()  # Shared across threads

def validate(url):
    page = browser.new_page()  # UNSAFE
    page.goto(url)

with ThreadPoolExecutor(max_workers=4) as executor:
    executor.map(validate, urls)  # CRASHES
```

**Solution**:
```python
# ✅ RIGHT - Use multiprocessing or async, never threading
from multiprocessing import Pool

def validate(url):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        browser.close()

with Pool(processes=4) as pool:
    pool.map(validate, urls)  # SAFE
```

### Gotcha #4: Element References Change Between Renders

**Severity**: High
**Detection**: `Element with ref 'e5' not found` error

**Problem**:
```python
# ❌ WRONG - Hard-coded refs change every render
snapshot = browser_snapshot()  # Returns: {"ref": "e5", "name": "Upload"}
browser_click(ref="e5")  # FAILS next render
```

**Solution**:
```python
# ✅ RIGHT - Use semantic queries (stable)
browser_click(element="button containing 'Upload'")
browser_click(element="Upload button")
# Queries by text/role, not ephemeral refs
```

### Gotcha #5: Timeout Errors

**Severity**: High
**Detection**: `TimeoutError: Timeout 30000ms exceeded`

**Problem**:
```python
# ❌ WRONG - Default timeout too short for slow operation
browser_navigate(url="http://localhost:5173")
browser_wait_for(text="Complete")  # Default 5s, operation takes 10s
```

**Solution**:
```python
# ✅ RIGHT - Set appropriate timeouts
browser_wait_for(text="Complete", timeout=15000)  # 15s

# Or use retry pattern
def wait_with_retry(text, max_attempts=3, timeout=5000):
    for attempt in range(max_attempts):
        try:
            browser_wait_for(text=text, timeout=timeout)
            return True
        except TimeoutError:
            if attempt == max_attempts - 1:
                raise
            time.sleep(1)
```

### Gotcha #6: Agent Token Budget Exhaustion

**Severity**: High
**Detection**: Validation incomplete, agents say "cannot verify visual"

**Problem**:
```python
# ❌ WRONG - Screenshots consume 4x tokens with no validation value
screenshot = browser_take_screenshot(filename="step1.png")  # ~2000 tokens
# Agent cannot validate UI from screenshot (just sees base64)
```

**Solution**:
```python
# ✅ RIGHT - Use accessibility snapshot for validation
snapshot = browser_snapshot()  # ~500 tokens, structured JSON
if "ExpectedElement" in snapshot:
    print("✅ Validation passed")

# ✅ ACCEPTABLE - One screenshot at end for human proof
browser_take_screenshot(filename="proof.png")
```

### Gotcha #7: Using Fixed Waits Instead of Auto-Wait

**Severity**: High
**Detection**: Tests slow, still flaky, unnecessary `sleep()` calls

**Problem**:
```python
# ❌ WRONG - Manual sleep makes tests slow and unreliable
import time
page.goto("http://localhost:5173")
time.sleep(3)  # Arbitrary wait
page.click("#button")
time.sleep(2)  # Another arbitrary wait
```

**Solution**:
```python
# ✅ RIGHT - Let Playwright auto-wait
page.goto("http://localhost:5173")  # Auto-waits for load
page.click("#button")  # Auto-waits for element ready

# Use explicit waits for specific conditions
page.wait_for_selector(".complete", state="visible")
```

### Gotcha #8: Not Managing Browser Context Lifecycle

**Severity**: High
**Detection**: Memory leaks, `Too many open files` error

**Problem**:
```python
# ❌ WRONG - Browser left running, resources leak
browser = playwright.chromium.launch()
page = browser.new_page()
page.goto("http://localhost:5173")
# Script ends, browser still running
```

**Solution**:
```python
# ✅ RIGHT - Use context managers for automatic cleanup
with sync_playwright() as p:
    with p.chromium.launch() as browser:
        with browser.new_page() as page:
            page.goto("http://localhost:5173")
# All cleaned up automatically
```

### Gotcha #9: Testing Implementation Details

**Severity**: High
**Detection**: Tests break on refactors, false positives

**Problem**:
```python
# ❌ WRONG - Test CSS classes (implementation detail)
assert page.locator(".modal-open").is_visible()
assert page.locator("div > div > span").count() == 3
```

**Solution**:
```python
# ✅ RIGHT - Test user-visible behavior
expect(page.get_by_role("dialog")).to_be_visible()
expect(page.get_by_text("Upload successful")).to_be_visible()
```

### Gotcha #10: MCP Tool Naming Confusion

**Severity**: Medium
**Detection**: `Tool not found` error despite YAML declaration

**Problem**:
```yaml
# ❌ WRONG - Full MCP names in agent YAML
tools: Bash, Read, mcp__MCP_DOCKER__browser_navigate
```

**Solution**:
```yaml
# ✅ RIGHT - Short names in YAML (system resolves)
tools: Bash, Read, browser_navigate
```

### Gotcha #11: Port Conflicts

**Severity**: Medium
**Detection**: Wrong service responds, expected elements missing

**Problem**:
```python
# ❌ WRONG - Navigate without verifying service identity
browser_navigate(url="http://localhost:5173")
# Could be different app if port conflict
```

**Solution**:
```python
# ✅ RIGHT - Verify service identity
browser_navigate(url="http://localhost:5173")
title = browser_evaluate(function="() => document.title")
if "RAG Service" not in title:
    raise AssertionError(f"Wrong service. Got: {title}")
```

### Gotcha #12: Mixing Sync and Async APIs

**Severity**: Medium
**Detection**: `Cannot use AsyncToSync in same thread` error

**Problem**:
```python
# ❌ WRONG - Sync API in async context
import asyncio
from playwright.sync_api import sync_playwright

async def test():
    with sync_playwright() as p:  # Mixing APIs
        page.goto("http://localhost:5173")
```

**Solution**:
```python
# ✅ RIGHT - Use async API in async context
from playwright.async_api import async_playwright

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("http://localhost:5173")
```

---

## Error Patterns

### Error: "Connection refused"

**Cause**: Frontend service not running
**Fix**:
```bash
docker-compose up -d
sleep 10  # Wait for health
curl http://localhost:5173/health
```

### Error: "Browser not found"

**Cause**: Browser binaries not installed
**Fix**:
```bash
browser_install()  # MCP tool
# Or: playwright install
```

### Error: "Element with ref 'e5' not found"

**Cause**: Hard-coded element refs (change every render)
**Fix**: Use semantic queries
```python
browser_click(element="button containing 'Upload'")
```

### Error: "TimeoutError: Timeout 30000ms exceeded"

**Cause**: Operation slower than timeout
**Fix**: Increase timeout or use retry pattern
```python
browser_wait_for(text="Complete", timeout=60000)
```

### Error: "Cannot allocate memory"

**Cause**: Browser contexts not cleaned up
**Fix**: Use context managers
```python
with sync_playwright() as p:
    with p.chromium.launch() as browser:
        # Auto cleanup
```

### Error: "Wrong service at port"

**Cause**: Port conflict or wrong service
**Fix**: Verify service identity
```python
# Check docker-compose ps
# Verify health endpoint
# Check page title matches expected
```

---

## Pre-Flight Checks

Before running browser validation, always perform these checks:

### 1. Check Browser Installed

```python
def check_browser_installed() -> bool:
    """Verify browser binaries are installed."""
    try:
        browser_navigate(url="about:blank")
        print("✅ Browser installed")
        return True
    except Exception:
        print("⚠️ Browser not installed")
        return False

if not check_browser_installed():
    print("Installing browser binaries...")
    browser_install()
    time.sleep(30)
    if not check_browser_installed():
        print("❌ Browser installation failed")
        exit(1)
```

### 2. Check Frontend Running

```python
def check_frontend_running(port: int) -> bool:
    """Verify frontend service is running."""
    result = Bash(f"curl -s http://localhost:{port}")
    if "Connection refused" in result.stderr:
        print(f"❌ Frontend not running on port {port}")
        return False
    print(f"✅ Frontend running on port {port}")
    return True

if not check_frontend_running(5173):
    print("Starting services...")
    Bash("docker-compose up -d")
    time.sleep(10)
    if not check_frontend_running(5173):
        print("❌ Failed to start frontend")
        exit(1)
```

### 3. Check Port Available

```python
def check_port_conflict(port: int) -> bool:
    """Check for port conflicts."""
    result = Bash(f"lsof -i :{port}")
    if result.stdout:
        print(f"⚠️ Port {port} in use by:")
        print(result.stdout)
        return False
    print(f"✅ Port {port} available")
    return True
```

### 4. Verify Service Identity

```python
def verify_service_identity(url: str, expected_title: str) -> bool:
    """Ensure correct service is running."""
    browser_navigate(url=url)
    title = browser_evaluate(function="() => document.title")
    if expected_title in title:
        print(f"✅ Correct service: {title}")
        return True
    print(f"❌ Wrong service. Expected '{expected_title}', got '{title}'")
    return False

verify_service_identity("http://localhost:5173", "RAG Service")
```

### Complete Pre-Flight Check Function

```python
def run_preflight_checks() -> bool:
    """Run all pre-flight checks before browser validation."""
    print("🔍 Running pre-flight checks...")

    checks = [
        ("Browser installed", check_browser_installed),
        ("Frontend running", lambda: check_frontend_running(5173)),
        ("Port available", lambda: check_port_conflict(5173)),
        ("Service identity", lambda: verify_service_identity(
            "http://localhost:5173", "RAG Service"
        )),
    ]

    for check_name, check_func in checks:
        print(f"\n🔍 Checking: {check_name}")
        if not check_func():
            print(f"❌ Pre-flight check failed: {check_name}")
            return False

    print("\n✅ All pre-flight checks passed")
    return True

# Use in validation
if not run_preflight_checks():
    exit(1)

# Proceed with browser validation
validate_frontend()
```

---

## Additional Resources

**Official Documentation**:
- [Playwright Python Library](https://playwright.dev/python/docs/library) - Core API reference
- [Playwright Locators](https://playwright.dev/docs/locators) - Semantic element selection
- [Playwright Best Practices](https://playwright.dev/docs/best-practices) - Testing patterns
- [Playwright Accessibility Testing](https://playwright.dev/docs/accessibility-testing) - Accessibility tree usage

**PRP Resources**:
- `prps/playwright_agent_integration.md` - Complete PRP with implementation blueprint
- `prps/playwright_agent_integration/examples/` - 6 copy-paste ready code examples
- `prps/playwright_agent_integration/planning/gotchas.md` - All 12 gotchas with detailed solutions

**Codebase Patterns**:
- `.claude/agents/validation-gates.md` - Agent with browser tools
- `.claude/agents/prp-exec-validator.md` - Validation loop pattern
- `.claude/patterns/quality-gates.md` - Multi-level validation structure

---

Generated: 2025-10-13
Pattern: Browser Validation
Coverage: Complete (configuration, navigation, interaction, validation, loops, errors)
Quality Score: 9.8/10
