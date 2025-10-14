# Known Gotchas: Playwright Agent Integration

## Overview

This document identifies critical pitfalls, common mistakes, and library quirks when integrating Playwright browser automation tools with validation agents. Based on comprehensive research from Playwright documentation, Archon knowledge base, and real-world implementations, we've documented 12 major gotchas across security, performance, configuration, and testing domains. Every gotcha includes detection strategies and actionable solutions to ensure successful integration.

---

## Critical Gotchas

### 1. Browser Binaries Not Installed

**Severity**: Critical
**Category**: System Configuration / Deployment
**Affects**: All Playwright operations
**Source**: https://playwright.dev/python/docs/intro

**What it is**:
Playwright requires separate browser binaries (Chromium, Firefox, WebKit) that are not installed with `pip install playwright`. The first browser operation will fail with "Browser not found" or "Executable doesn't exist" errors.

**Why it's a problem**:
- All browser validation fails immediately
- Blocks entire validation workflow
- Common in CI/CD, Docker, fresh environments
- Error messages can be cryptic

**How to detect it**:
- Error message: `Browser is not installed`
- Error message: `Executable doesn't exist at /path/to/browser`
- First browser operation fails
- Works on one machine, fails on another

**How to avoid/fix**:

```python
# ❌ WRONG - Only pip install, browser operations fail
# Terminal:
pip install playwright
# Python code:
browser = playwright.chromium.launch()  # FAILS

# ✅ RIGHT - Install both package AND browsers
# Terminal:
pip install playwright
playwright install  # Downloads browser binaries (~300MB)

# For Docker/CI environments with system dependencies:
playwright install --with-deps  # Includes OS dependencies
```

**For MCP_DOCKER tool usage**:
```python
# If browser_navigate fails with "browser not installed"
# Use the browser_install tool first:
result = browser_install()  # MCP tool to install browsers
# Wait for installation (30-60 seconds)
# Then proceed with navigation
browser_navigate(url="http://localhost:5173")
```

**Validation script**:
```bash
# Check if browsers are installed
playwright --version
# Should show: Version 1.x.x

# Verify browser binaries exist
python -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); print('Browsers installed'); p.stop()"
```

**Additional Resources**:
- https://playwright.dev/python/docs/browsers
- https://playwright.dev/python/docs/docker

---

### 2. Frontend Service Not Running

**Severity**: Critical
**Category**: Service Availability / Integration
**Affects**: All browser navigation operations
**Source**: Feature Analysis (lines 560-570), RAG service PRP patterns

**What it is**:
Browser validation attempts to navigate to frontend URLs (localhost:5173, localhost:5174) before docker-compose services are running. Results in "Connection refused" or "ERR_CONNECTION_REFUSED" errors.

**Why it's a problem**:
- Navigation fails immediately
- Wastes validation attempts (max 5)
- Confusing error messages (browser issue vs service issue)
- Port conflicts if wrong service running

**How to detect it**:
- Error message: `net::ERR_CONNECTION_REFUSED`
- Error message: `Connection refused at http://localhost:5173`
- Navigation timeouts
- Port unreachable errors

**How to avoid/fix**:

```python
# ❌ WRONG - Navigate without checking service health
browser_navigate(url="http://localhost:5173")  # FAILS if service down

# ✅ RIGHT - Check service health first
import subprocess
import time

def ensure_frontend_running(port: int, service_name: str) -> bool:
    """Check if frontend service is running, start if needed."""

    # Check if port is listening
    result = subprocess.run(
        ["docker-compose", "ps", service_name],
        capture_output=True,
        text=True
    )

    if "Up" not in result.stdout:
        print(f"⚠️ {service_name} not running, starting services...")
        subprocess.run(["docker-compose", "up", "-d"], check=True)

        # Wait for service to be healthy
        max_wait = 30
        for i in range(max_wait):
            try:
                response = requests.get(f"http://localhost:{port}/health")
                if response.status_code == 200:
                    print(f"✅ {service_name} is healthy")
                    return True
            except requests.ConnectionError:
                time.sleep(1)

        raise RuntimeError(f"{service_name} failed to start after {max_wait}s")

    return True

# Use in validation workflow
ensure_frontend_running(5173, "rag-service")
browser_navigate(url="http://localhost:5173")
```

**Quick health check pattern**:
```bash
# Before browser validation, run:
docker-compose ps | grep "Up" || docker-compose up -d

# Wait for health endpoint
curl --retry 10 --retry-delay 1 --retry-connrefused http://localhost:5173/health
```

**Additional Resources**:
- Feature analysis risk mitigation (lines 560-570)
- Docker-compose health check patterns

---

### 3. Thread Safety Violations

**Severity**: Critical
**Category**: Concurrency / System Stability
**Affects**: Multi-threaded agent execution
**Source**: https://github.com/microsoft/playwright-python/issues/470, Playwright docs

**What it is**:
Playwright's sync API is **not thread-safe**. Sharing Playwright instances, browsers, or contexts across threads causes race conditions, hangs, and crashes. Async API with threading also causes process hangs.

**Why it's a problem**:
- Silent failures or mysterious hangs
- Non-deterministic bugs (works sometimes, fails others)
- Process deadlocks requiring force-kill
- Data corruption in browser state

**How to detect it**:
- Process hangs indefinitely
- Error: `RuntimeError: cannot schedule new futures after interpreter shutdown`
- Random failures in parallel tests
- Browser operations never complete
- Tests work sequentially but fail in parallel

**How to avoid/fix**:

```python
# ❌ WRONG - Sharing Playwright instance across threads
from concurrent.futures import ThreadPoolExecutor
from playwright.sync_api import sync_playwright

playwright = sync_playwright().start()  # GLOBAL INSTANCE
browser = playwright.chromium.launch()

def validate_page(url):
    page = browser.new_page()  # SHARED BROWSER - UNSAFE
    page.goto(url)
    return page.title()

with ThreadPoolExecutor(max_workers=4) as executor:
    results = executor.map(validate_page, urls)  # CRASHES

# ✅ RIGHT - Create separate Playwright instance per process
from multiprocessing import Pool
from playwright.sync_api import sync_playwright

def validate_page(url):
    # Each process gets its own Playwright instance
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        title = page.title()
        browser.close()
        return title

# Use multiprocessing, not threading
with Pool(processes=4) as pool:
    results = pool.map(validate_page, urls)  # SAFE

# ✅ BETTER - Use pytest-xdist for parallel tests
# Terminal:
pip install pytest-xdist
pytest tests/ -n 4  # 4 parallel processes
```

**For async API with concurrency**:
```python
# ✅ RIGHT - Async API with single event loop (no threads)
import asyncio
from playwright.async_api import async_playwright

async def validate_page(url):
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        title = await page.title()
        await browser.close()
        return title

# Run concurrently on single event loop
async def main():
    results = await asyncio.gather(
        validate_page("http://localhost:5173"),
        validate_page("http://localhost:5174"),
    )
    return results

asyncio.run(main())
```

**Why this works**:
- Multiprocessing: Each process has isolated memory and Playwright instance
- Async: Single thread, cooperative concurrency (no race conditions)
- Avoid threading: Python threading + Playwright sync API = deadlocks

**Additional Resources**:
- https://playwright.dev/python/docs/library (threading warning)
- https://playwright.dev/java/docs/multithreading (Java, similar issues)
- pytest-xdist documentation for parallel testing

---

### 4. Element References Change Between Renders

**Severity**: High
**Category**: Test Flakiness / Reliability
**Affects**: Element interaction (click, type, etc.)
**Source**: Feature Analysis (lines 575-588), Playwright locators guide

**What it is**:
Playwright's accessibility tree assigns references like `ref="e5"` to elements, but these references change on every page render or React re-render. Hard-coding refs causes tests to fail intermittently.

**Why it's a problem**:
- Flaky tests that pass sometimes, fail others
- Works in development, fails in CI
- Breaks after any UI change
- False positives in validation

**How to detect it**:
- Error: `Element with ref 'e5' not found`
- Test passes first run, fails second run
- Same test gives different results
- Works on slow machines, fails on fast ones (rendering timing)

**How to avoid/fix**:

```python
# ❌ WRONG - Hard-coded element references (brittle)
browser_snapshot()  # Returns: { "role": "button", "ref": "e5", "name": "Upload" }
browser_click(ref="e5")  # FAILS next render (ref changes to "e7")

# ✅ RIGHT - Semantic queries (resilient)
# Use accessible name/role/text instead of ref
browser_click(element="button", name="Upload")
browser_click(element="Upload button")  # Natural language query
browser_click(element="button containing 'Upload'")

# ✅ RIGHT - Role-based locators
page.get_by_role("button", name="Upload").click()
page.get_by_label("Document Title").fill("Test")
page.get_by_text("Upload successful").wait_for()

# ✅ RIGHT - Test ID attributes (for non-semantic elements)
# In React component:
# <div data-testid="upload-form">...</div>

page.get_by_test_id("upload-form").is_visible()
```

**Validation pattern with semantic queries**:
```python
# Complete workflow without refs
def validate_document_upload():
    # Navigate
    page.goto("http://localhost:5173")

    # Use semantic locators (stable across renders)
    page.get_by_role("button", name="Upload Document").click()
    page.get_by_label("Document Title").fill("Test Document")
    page.get_by_label("File").set_input_files("test.pdf")
    page.get_by_role("button", name="Submit").click()

    # Validate success
    expect(page.get_by_text("Upload successful")).to_be_visible()
    expect(page.get_by_role("listitem").filter(
        has_text="Test Document"
    )).to_be_visible()
```

**Locator priority (most to least resilient)**:
1. `get_by_role()` - ARIA roles (most accessible)
2. `get_by_label()` - Form labels
3. `get_by_placeholder()` - Input placeholders
4. `get_by_text()` - Visible text
5. `get_by_test_id()` - Test ID attributes
6. `locator('css')` - CSS selectors (avoid)
7. `ref="e5"` - Element references (NEVER use)

**Additional Resources**:
- https://playwright.dev/docs/locators (locator best practices)
- https://playwright.dev/docs/best-practices#use-locators

---

## High Priority Gotchas

### 5. Timeout Errors and Configuration

**Severity**: High
**Category**: Performance / Reliability
**Affects**: All browser operations
**Source**: https://playwright.dev/docs/test-timeouts, https://autify.com/blog/playwright-timeout

**What it is**:
Playwright has multiple timeout types (navigation, assertion, action) with different defaults (30s, 5s, etc.). Slow-loading pages or network issues trigger TimeoutErrors. Fixed `sleep()` calls make tests even slower and more flaky.

**Why it's a problem**:
- Tests fail on slow networks/machines but pass locally
- Hard to debug (which timeout fired?)
- Premature failures on legitimate slow operations
- Manual sleep() makes tests slower without reliability

**How to detect it**:
- Error: `TimeoutError: Timeout 30000ms exceeded`
- Error: `waiting for locator('.selector') to be visible`
- Tests pass locally, fail in CI
- Tests randomly fail under load

**How to avoid/fix**:

```python
# ❌ WRONG - Fixed sleep() instead of smart waiting
import time
page.goto("http://localhost:5173")
time.sleep(5)  # Arbitrary wait - too short or too long
page.click("#submit")

# ❌ WRONG - Using default timeout for slow operations
page.goto("http://localhost:5173")  # Default 30s
# API call takes 45s -> TimeoutError

# ✅ RIGHT - Configure timeouts appropriately
from playwright.sync_api import sync_playwright, TimeoutError

with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context()

    # Set default timeouts for this context
    context.set_default_timeout(60000)  # 60s for slow operations
    context.set_default_navigation_timeout(30000)  # 30s for navigation

    page = context.new_page()

    # Override per-operation
    page.goto("http://localhost:5173", timeout=10000)  # 10s for fast page

    # Use auto-waiting (preferred over sleep)
    page.wait_for_selector(".upload-complete", timeout=15000)

    browser.close()

# ✅ RIGHT - Error handling with retry
def wait_with_retry(page, selector, max_attempts=3, timeout=5000):
    """Smart retry pattern for flaky elements."""
    for attempt in range(max_attempts):
        try:
            page.wait_for_selector(selector, timeout=timeout)
            return True
        except TimeoutError:
            if attempt == max_attempts - 1:
                raise
            print(f"⚠️ Attempt {attempt + 1} failed, retrying...")
            time.sleep(1)
    return False

# Usage
if wait_with_retry(page, ".success-message"):
    print("✅ Element found")
else:
    raise AssertionError("Element not found after retries")
```

**Timeout hierarchy (from specific to general)**:
```python
# 1. Operation-specific (highest priority)
page.click("#button", timeout=5000)

# 2. Action timeout (for this page)
page.set_default_timeout(10000)

# 3. Context timeout (for all pages in context)
context.set_default_timeout(30000)

# 4. Global default (lowest priority)
# 30s for navigation, 5s for assertions
```

**When to increase timeouts**:
- ✅ Large file uploads
- ✅ Heavy API operations
- ✅ CI/CD environments (slower than local)
- ❌ Element not appearing (fix selector instead)
- ❌ Test taking too long (redesign test)

**Additional Resources**:
- https://playwright.dev/docs/test-timeouts
- https://www.checklyhq.com/docs/learn/playwright/waits-and-timeouts/

---

### 6. Agent Token Budget Exhaustion

**Severity**: High
**Category**: Performance / Cost
**Affects**: Agent validation with screenshots
**Source**: Feature Analysis (lines 589-605), INITIAL.md agent limitations

**What it is**:
Agents cannot visually parse screenshots - they're just images to LLMs. Screenshots consume large token budgets (~2000 tokens) but provide no validation value. Accessibility snapshots (~500 tokens) are structured data that agents can actually use.

**Why it's a problem**:
- Wastes 4x tokens with no benefit
- Agent validation incomplete or fails
- Increased costs for no value
- Misleading - looks like agent is "seeing" UI

**How to detect it**:
- Agent validation reports incomplete
- Token budget exceeded errors
- Validation doesn't detect actual UI issues
- Agent says "I cannot verify visual appearance"

**How to avoid/fix**:

```python
# ❌ WRONG - Screenshots for agent validation (waste)
browser_navigate(url="http://localhost:5173")
screenshot = browser_take_screenshot(filename="validation.png")
# Agent cannot validate UI from screenshot
# Just sees "I captured a screenshot at validation.png"

# ❌ WRONG - Multiple screenshots for debugging
for step in steps:
    execute_step(step)
    browser_take_screenshot(filename=f"step_{step}.png")  # Huge token waste

# ✅ RIGHT - Accessibility snapshot for validation
browser_navigate(url="http://localhost:5173")
snapshot = browser_snapshot()  # Returns structured JSON
# Agent can validate: "DocumentList" in snapshot
# Agent can check: snapshot["role"] == "main"
# Agent can verify: snapshot["children"][0]["name"] == "Upload"

# ✅ RIGHT - Validate with structured data
def validate_ui_state(page):
    """Validate UI using accessibility tree."""
    snapshot = page.accessibility.snapshot()

    # Check structure
    assert find_by_role(snapshot, "button")
    assert find_by_text(snapshot, "Upload successful")

    # Check interactive elements
    buttons = find_all_by_role(snapshot, "button")
    assert any(btn["name"] == "Upload" for btn in buttons)

    return True

def find_by_role(node, role):
    """Helper to search accessibility tree."""
    if node.get("role") == role:
        return node
    for child in node.get("children", []):
        result = find_by_role(child, role)
        if result:
            return result
    return None

# ✅ ACCEPTABLE - Screenshots for human review only
# Take ONE screenshot at end for human verification
browser_navigate(url="http://localhost:5173")
# ... perform validation with snapshots ...
# Validation complete, capture proof for humans:
browser_take_screenshot(filename="validation-proof.png")
print("Screenshot saved for human review (not for agent validation)")
```

**Token usage comparison**:
```
browser_snapshot():          ~500 tokens (structured JSON)
browser_take_screenshot():   ~2000 tokens (base64 image)

For 10 validation steps:
- Snapshots:    5,000 tokens  ✅
- Screenshots:  20,000 tokens ❌ (4x waste)
```

**Best practices**:
- **For agents**: Use `browser_snapshot()` - structured data agents can analyze
- **For humans**: Use `browser_take_screenshot()` - visual proof
- **For validation**: Semantic queries + assertions, not visual checks
- **For debugging**: One screenshot at failure point, not every step

**Additional Resources**:
- Feature Analysis lines 227-233 (agent limitations)
- https://playwright.dev/python/docs/api/class-accessibility

---

### 7. Using Fixed Waits Instead of Auto-Wait

**Severity**: High
**Category**: Test Reliability / Performance
**Affects**: Element interaction timing
**Source**: https://betterstack.com/community/guides/testing/playwright-best-practices/

**What it is**:
Playwright has built-in auto-waiting that ensures elements are stable, visible, and enabled before interaction. Adding manual `time.sleep()` or `waitForTimeout()` makes tests slower and less reliable.

**Why it's a problem**:
- Tests slower than necessary (sleep too long)
- Tests still flaky (sleep too short)
- Wastes validation time
- Masks real timing issues

**How to detect it**:
- Tests have `time.sleep()` calls
- Tests have fixed `wait(5000)` calls
- Tests take unnecessarily long
- Still flaky despite sleep calls

**How to avoid/fix**:

```python
# ❌ WRONG - Fixed sleep() calls
import time

page.goto("http://localhost:5173")
time.sleep(3)  # Wait for page load - arbitrary
page.click("#upload-button")
time.sleep(2)  # Wait for modal - arbitrary
page.fill("#title", "Test")
time.sleep(1)  # Wait for... something?

# ✅ RIGHT - Let Playwright auto-wait
page.goto("http://localhost:5173")
# Auto-waits for page load, DOM content loaded

page.click("#upload-button")
# Auto-waits for element to be:
# - Attached to DOM
# - Visible
# - Stable (not animating)
# - Enabled
# - Not obscured by other elements

page.fill("#title", "Test")
# Auto-waits for input to be editable

# ✅ RIGHT - Explicit waits for specific conditions
# Wait for API response
page.wait_for_response(
    lambda response: "api/documents" in response.url,
    timeout=10000
)

# Wait for element state
page.wait_for_selector(".upload-complete", state="visible")

# Wait for network idle
page.wait_for_load_state("networkidle")

# Wait for specific text
page.wait_for_selector("text=Upload successful")
```

**Smart waiting patterns**:
```python
# Pattern: Wait for dynamic content
def wait_for_data_loaded(page):
    """Wait until data is loaded, not arbitrary time."""
    # Wait for loading indicator to disappear
    page.wait_for_selector(".loading-spinner", state="detached")

    # Or wait for data to appear
    page.wait_for_selector(".data-table tr", state="attached")

# Pattern: Wait for animation to complete
def wait_for_animation(page, selector):
    """Wait until element stops moving."""
    # Playwright auto-waits for stable elements
    # No manual waiting needed
    page.click(selector)  # Already waits for stability

# Pattern: Wait for API call
async def wait_for_api_call(page, api_endpoint):
    """Wait for specific API call to complete."""
    async with page.expect_response(
        lambda response: api_endpoint in response.url
    ) as response_info:
        await page.click("#submit")
    response = await response_info.value
    return response.status
```

**When explicit waits ARE needed**:
- ✅ Waiting for API responses
- ✅ Waiting for animations to complete
- ✅ Waiting for specific network state
- ✅ Waiting for dynamic content updates
- ❌ Waiting "just in case"
- ❌ Waiting arbitrary amounts of time
- ❌ Waiting for elements to be clickable (auto-wait handles this)

**Additional Resources**:
- https://playwright.dev/docs/actionability (auto-waiting details)
- https://playwright.dev/python/docs/api/class-page#page-wait-for-selector

---

### 8. Not Managing Browser Context Lifecycle

**Severity**: High
**Category**: Resource Management / Memory Leaks
**Affects**: Long-running validation sessions
**Source**: https://betterstack.com/community/guides/testing/playwright-best-practices/

**What it is**:
Leaving browsers and contexts open consumes memory and system resources. Not properly closing browsers can lead to resource exhaustion, especially in CI/CD or long validation runs.

**Why it's a problem**:
- Memory leaks in long-running processes
- File descriptor exhaustion
- Zombie browser processes
- CI/CD job failures due to resource limits

**How to detect it**:
- Memory usage increases over time
- Error: `Too many open files`
- Error: `Cannot allocate memory`
- Chromium processes remain after script ends
- CI jobs timeout due to resource exhaustion

**How to avoid/fix**:

```python
# ❌ WRONG - No cleanup, resources leak
from playwright.sync_api import sync_playwright

playwright = sync_playwright().start()
browser = playwright.chromium.launch()
page = browser.new_page()
page.goto("http://localhost:5173")
# Script ends, browser still running

# ❌ WRONG - Cleanup only on success
browser = playwright.chromium.launch()
page = browser.new_page()
page.goto("http://localhost:5173")
validate_page(page)
browser.close()  # Not called if validate_page raises exception

# ✅ RIGHT - Use context managers (automatic cleanup)
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    try:
        page.goto("http://localhost:5173")
        validate_page(page)
    finally:
        browser.close()
# Automatically cleans up even on exception

# ✅ BETTER - Nested context managers
with sync_playwright() as p:
    with p.chromium.launch() as browser:
        with browser.new_page() as page:
            page.goto("http://localhost:5173")
            validate_page(page)
# All resources cleaned up automatically

# ✅ RIGHT - Async with context managers
import asyncio
from playwright.async_api import async_playwright

async def validate_async():
    async with async_playwright() as p:
        async with p.chromium.launch() as browser:
            async with browser.new_page() as page:
                await page.goto("http://localhost:5173")
                await validate_page(page)
    # All cleaned up

asyncio.run(validate_async())
```

**For pytest fixtures**:
```python
# ✅ RIGHT - pytest fixture with proper cleanup
import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="function")
def browser_page():
    """Provide fresh browser page for each test."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        yield page
        # Cleanup happens after yield
        browser.close()

def test_upload(browser_page):
    browser_page.goto("http://localhost:5173")
    # Test code
    # No manual cleanup needed
```

**For validation agents**:
```python
# ✅ RIGHT - Agent validation with cleanup
class BrowserValidator:
    def __init__(self):
        self.playwright = None
        self.browser = None

    def __enter__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def validate(self, url):
        page = self.browser.new_page()
        try:
            page.goto(url)
            # Validation logic
        finally:
            page.close()

# Usage
with BrowserValidator() as validator:
    validator.validate("http://localhost:5173")
# All cleaned up automatically
```

**Additional Resources**:
- https://playwright.dev/python/docs/library#browser-management
- Python context manager protocol

---

### 9. Testing Implementation Details Instead of User Behavior

**Severity**: High
**Category**: Test Quality / Maintainability
**Affects**: Test resilience to refactoring
**Source**: https://playwright.dev/docs/best-practices, React testing anti-patterns

**What it is**:
Tests that verify internal component state, CSS class names, or DOM structure instead of user-visible behavior. These tests break when implementation changes, even if user experience is identical.

**Why it's a problem**:
- Tests break on every refactor
- False positives (implementation changed, behavior didn't)
- Doesn't catch actual user-facing bugs
- High maintenance burden

**How to detect it**:
- Tests check CSS class names
- Tests verify internal state variables
- Tests depend on specific DOM structure
- Tests break when styling changes
- Tests pass but users report bugs

**How to avoid/fix**:

```python
# ❌ WRONG - Testing implementation details
# Check internal CSS classes
assert page.locator(".modal-open").is_visible()

# Check specific DOM structure
assert page.locator("div > div > span").count() == 3

# Check inline styles
assert page.locator("#button").get_attribute("style") == "color: red"

# ✅ RIGHT - Test user-visible behavior
# What does the user see?
expect(page.get_by_role("dialog")).to_be_visible()

# What can the user do?
expect(page.get_by_role("button", name="Submit")).to_be_enabled()

# What does the user read?
expect(page.get_by_text("Upload successful")).to_be_visible()

# ❌ WRONG - Testing React component internals
# (Can't do this in E2E tests anyway, but conceptually wrong)
assert component.state["isOpen"] == true

# ✅ RIGHT - Test the result, not the mechanism
expect(page.get_by_role("dialog")).to_be_visible()
# Who cares HOW it's open, just that user sees it

# ❌ WRONG - Testing Redux/Zustand store state
# (Implementation detail)
assert store.getState().documents.length == 5

# ✅ RIGHT - Test what user sees in UI
expect(page.get_by_role("listitem")).to_have_count(5)
```

**User behavior validation pattern**:
```python
def test_document_upload_workflow(page):
    """Test from user perspective: what they see and do."""

    # 1. User navigates to app
    page.goto("http://localhost:5173")

    # 2. User sees upload button
    expect(page.get_by_role("button", name="Upload")).to_be_visible()

    # 3. User clicks upload button
    page.get_by_role("button", name="Upload").click()

    # 4. User sees upload form
    expect(page.get_by_role("dialog")).to_be_visible()
    expect(page.get_by_label("Document Title")).to_be_visible()

    # 5. User fills form
    page.get_by_label("Document Title").fill("Test Document")
    page.get_by_label("File").set_input_files("test.pdf")

    # 6. User submits
    page.get_by_role("button", name="Submit").click()

    # 7. User sees success message
    expect(page.get_by_text("Upload successful")).to_be_visible()

    # 8. User sees document in list
    expect(page.get_by_role("listitem").filter(
        has_text="Test Document"
    )).to_be_visible()

    # Note: No CSS selectors, no internal state, no DOM structure
    # Pure user behavior
```

**Questions to ask**:
- ✅ "Can a user see this?"
- ✅ "Can a user click this?"
- ✅ "Does this change what the user sees?"
- ❌ "Is this CSS class applied?"
- ❌ "Is this state variable set?"
- ❌ "Is the DOM structure correct?"

**Additional Resources**:
- https://kentcdodds.com/blog/testing-implementation-details
- https://testing-library.com/docs/guiding-principles

---

## Medium Priority Gotchas

### 10. MCP Tool Naming Confusion

**Severity**: Medium
**Category**: Configuration / Tool Access
**Affects**: Agent tool invocation
**Source**: Feature Analysis (lines 367-376), MCP documentation

**What it is**:
MCP tools have full names like `mcp__MCP_DOCKER__browser_navigate` but agent YAML tool lists use short names `browser_navigate`. Mixing these causes tool not found errors.

**Why it's a problem**:
- Tools declared but not accessible
- Confusing error messages
- Works in one agent, fails in another
- Documentation inconsistency

**How to detect it**:
- Error: `Tool 'mcp__MCP_DOCKER__browser_navigate' not found`
- Agent can't access declared tools
- Tools work when invoked directly but not in agent
- YAML validation passes but runtime fails

**How to handle**:

```yaml
# ❌ WRONG - Full MCP names in agent YAML
---
name: validation-gates
tools: Bash, Read, Edit, mcp__MCP_DOCKER__browser_navigate, mcp__MCP_DOCKER__browser_snapshot
---

# ✅ RIGHT - Short names in YAML (system adds prefix)
---
name: validation-gates
tools: Bash, Read, Edit, browser_navigate, browser_snapshot, browser_click
---
```

**When invoking tools**:
```python
# In agent code, use short names (agent system resolves)
browser_navigate(url="http://localhost:5173")
snapshot = browser_snapshot()

# NOT:
mcp__MCP_DOCKER__browser_navigate(url="http://localhost:5173")  # Won't work
```

**Complete browser tool list for YAML**:
```yaml
tools: Bash, Read, Edit, Grep, Glob, browser_navigate, browser_snapshot, browser_click, browser_type, browser_take_screenshot, browser_evaluate, browser_wait_for, browser_fill_form, browser_tabs, browser_install
```

**Tool name resolution pattern**:
```
YAML Declaration:        browser_navigate
↓
Agent System Resolves:   mcp__MCP_DOCKER__browser_navigate
↓
MCP Server Receives:     browser_navigate (via MCP protocol)
↓
Tool Executes:           Playwright navigation
```

**Additional Resources**:
- Codebase patterns lines 367-376
- Feature analysis lines 118-131

---

### 11. Port Conflicts in Multi-Service Validation

**Severity**: Medium
**Category**: Service Configuration
**Affects**: Parallel frontend testing
**Source**: Feature Analysis (lines 606-621)

**What it is**:
RAG service (5173) and Task Manager (5174) may not be running, or ports may be occupied by other services. Navigation fails silently or connects to wrong service.

**Why it's confusing**:
- Wrong service responds (port occupied by different app)
- Port forwarding issues in Docker
- Multiple docker-compose projects conflict
- Hard to debug (connection succeeds but wrong app)

**How to detect**:
- Page loads but wrong content appears
- API endpoints return 404
- Expected elements missing
- Title/heading doesn't match

**How to handle**:

```python
# ✅ RIGHT - Verify service identity before testing
def verify_service_identity(page, expected_title_substring):
    """Ensure we're connected to the right service."""
    page.goto(f"http://localhost:{port}")

    title = page.title()
    if expected_title_substring not in title:
        raise AssertionError(
            f"Wrong service at port {port}. "
            f"Expected title containing '{expected_title_substring}', "
            f"got '{title}'"
        )

# Usage
verify_service_identity(page, "RAG Service")  # For port 5173
verify_service_identity(page, "Task Manager")  # For port 5174

# ✅ RIGHT - Check specific API endpoints
def verify_rag_service(page):
    page.goto("http://localhost:5173/health")
    response = page.content()
    assert "rag-service" in response.lower()
```

**Port verification script**:
```bash
# Check what's running on ports
lsof -i :5173
lsof -i :5174

# Verify docker-compose services
docker-compose ps

# Check service health
curl http://localhost:5173/health
curl http://localhost:5174/health
```

**Additional Resources**:
- Feature analysis risk mitigation section

---

### 12. Mixing Sync and Async APIs

**Severity**: Medium
**Category**: API Misuse
**Affects**: Code maintainability and correctness
**Source**: https://discuss.python.org/t/two-sync-apis-playwright-and-procrastinate-cannot-use-asynctosync-in-the-same-thread-as-an-async-event-loop/81521

**What it is**:
Playwright offers both sync and async APIs. Mixing them or using sync API in async context (or vice versa) causes errors and confusion.

**Why it's confusing**:
- Error: `Cannot use AsyncToSync in the same thread as an async event loop`
- Unclear which API to use when
- Framework expectations (pytest vs pytest-asyncio)
- Performance implications

**How to handle**:

```python
# ❌ WRONG - Mixing sync and async
import asyncio
from playwright.sync_api import sync_playwright

async def test_page():
    with sync_playwright() as p:  # Sync API in async function
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("http://localhost:5173")  # Blocking call in async context

# ✅ RIGHT - Use async API in async context
import asyncio
from playwright.async_api import async_playwright

async def test_page():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("http://localhost:5173")

asyncio.run(test_page())

# ✅ RIGHT - Use sync API in sync context
from playwright.sync_api import sync_playwright

def test_page():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("http://localhost:5173")

test_page()
```

**Decision guide**:
- **Use Sync API when**: Simple scripts, pytest tests, synchronous codebase
- **Use Async API when**: High concurrency needed, async framework (FastAPI, etc.), event-driven architecture

**Additional Resources**:
- https://playwright.dev/python/docs/library

---

## Library-Specific Quirks

### Playwright Python

**Version-Specific Issues**:
- **v1.40+**: Accessibility snapshot deprecated, use Axe integration
- **v1.30+**: Auto-waiting improved, may need to adjust explicit waits
- **Pre-v1.20**: Browser install command different

**Common Mistakes**:
1. **Not awaiting async calls**: Missing `await` in async API causes promise errors
2. **Using sleep() instead of auto-wait**: Defeats Playwright's smart waiting
3. **Sharing instances across threads**: Not thread-safe, causes crashes
4. **Hard-coding selectors**: Use semantic locators for resilience

**Best Practices**:
- **Use semantic locators**: `get_by_role()`, `get_by_label()`, `get_by_text()`
- **Let Playwright auto-wait**: Don't add manual waits unless necessary
- **Create new contexts for isolation**: Each test should have fresh context
- **Use context managers**: Ensures proper cleanup

---

## Performance Gotchas

### 1. Browser Operations Are 10x Slower Than API Tests

**Impact**: Validation time
**Affects**: CI/CD pipeline duration

**The problem**:
```python
# API test: 50ms
response = requests.get("http://localhost:5000/api/documents")
assert response.status_code == 200

# Browser test: 500ms
page.goto("http://localhost:5173/documents")
expect(page.get_by_text("Documents")).to_be_visible()
```

**The solution**:
```python
# ✅ BEST - Hybrid approach
# 1. Use API for data setup (fast)
requests.post("http://localhost:5000/api/documents", json=test_data)

# 2. Use browser for UI validation (slow but necessary)
page.goto("http://localhost:5173/documents")
expect(page.get_by_text("Test Document")).to_be_visible()

# 3. Use API for teardown (fast)
requests.delete("http://localhost:5000/api/documents/123")
```

**When to use each**:
- **API tests**: Business logic, data validation, performance testing
- **Browser tests**: User workflows, visual validation, accessibility
- **Hybrid**: Setup via API, validate via browser

**Benchmarks**:
- API test: 10-100ms
- Browser test: 100-1000ms
- Improvement: 10x faster with hybrid approach

---

### 2. Headless vs Headed Mode

**Impact**: Performance and debugging
**Affects**: Test speed and CI compatibility

**Configuration**:
```python
# ❌ SLOW - Headed mode (for local debugging only)
browser = playwright.chromium.launch(headless=False)
# ~20% slower, requires display server

# ✅ FAST - Headless mode (for CI/CD)
browser = playwright.chromium.launch(headless=True)
# Faster, works in CI environments

# ✅ SMART - Environment-aware
import os
headless = os.getenv("CI", "false") == "true"
browser = playwright.chromium.launch(headless=headless)
```

---

## Security Gotchas

### 1. Credentials in Screenshots

**Severity**: High
**Type**: Data Leakage
**Affects**: Security compliance

**Vulnerability**:
```python
# ❌ VULNERABLE - Screenshot captures password
page.get_by_label("Password").fill("secret123")
page.screenshot(path="login-test.png")  # Password visible in screenshot
```

**Secure Implementation**:
```python
# ✅ SECURE - Mask sensitive fields before screenshot
page.get_by_label("Password").fill("secret123")
# Add CSS to mask password field
page.add_style_tag(content="""
    input[type="password"] { -webkit-text-security: disc; }
""")
page.screenshot(path="login-test.png")  # Password hidden

# ✅ BETTER - Don't screenshot pages with sensitive data
# Use accessibility snapshot instead (no visual data)
snapshot = page.accessibility.snapshot()
```

---

### 2. Untrusted URL Navigation

**Severity**: Critical
**Type**: SSRF / Open Redirect
**Affects**: Security testing agents

**Vulnerability**:
```python
# ❌ VULNERABLE - Navigate to user-provided URL
user_url = request.get("url")
page.goto(user_url)  # Could be file://, javascript:, data: schemes
```

**Secure Implementation**:
```python
# ✅ SECURE - Validate URL scheme and host
from urllib.parse import urlparse

def safe_navigate(page, url):
    parsed = urlparse(url)

    # Only allow http/https
    if parsed.scheme not in ["http", "https"]:
        raise ValueError(f"Invalid URL scheme: {parsed.scheme}")

    # Only allow localhost for validation
    if parsed.hostname not in ["localhost", "127.0.0.1"]:
        raise ValueError(f"Only localhost URLs allowed: {parsed.hostname}")

    # Only allow expected ports
    if parsed.port not in [5173, 5174, None]:
        raise ValueError(f"Invalid port: {parsed.port}")

    page.goto(url)

# Usage
safe_navigate(page, "http://localhost:5173")  # ✅ Allowed
safe_navigate(page, "file:///etc/passwd")     # ❌ Rejected
```

---

## Integration Gotchas

### Docker + Playwright

**Known Issues**:
1. **Browser binaries missing in Docker**: Use `playwright install --with-deps` in Dockerfile
2. **Display server required for headed mode**: Use headless or Xvfb
3. **Shared memory issues**: Add `--shm-size=2g` to docker run

**Configuration**:
```dockerfile
# ✅ RIGHT - Dockerfile for Playwright
FROM python:3.11
RUN pip install playwright pytest
RUN playwright install --with-deps chromium
# Increase shared memory for browser
CMD ["pytest", "tests/"]
```

```bash
# ✅ RIGHT - Docker run with shared memory
docker run --shm-size=2g -it playwright-tests
```

---

## Testing Gotchas

**Common Test Pitfalls**:
1. **Tests depend on each other**: Each test should be isolated and independent
2. **Not resetting state**: Use `beforeEach` or fixtures to reset between tests
3. **Hard-coded wait times**: Use auto-wait or smart wait strategies
4. **Testing third-party APIs directly**: Mock external services

**Mocking pattern**:
```python
# ✅ RIGHT - Mock external API calls
await page.route("**/api/external/**", lambda route: route.fulfill(
    status=200,
    body=json.dumps({"data": "mocked"})
))
```

---

## Deployment Gotchas

**Environment-Specific Issues**:
- **Development**: Browser binaries may not be installed
- **Staging**: Port conflicts with other services
- **Production**: MCP_DOCKER server may not be available

**Configuration management**:
```python
# ✅ RIGHT - Environment-aware configuration
import os

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
BROWSER_HEADLESS = os.getenv("CI") == "true"
TIMEOUT = int(os.getenv("BROWSER_TIMEOUT", "30000"))
```

---

## Anti-Patterns to Avoid

### 1. The "Sleep-Driven Development" Anti-Pattern

**What it is**: Adding arbitrary `time.sleep()` calls to fix timing issues

**Why it's bad**: Tests slower, still flaky, masks real issues

**Better pattern**: Use Playwright's auto-wait and explicit conditions

### 2. The "Screenshot Everything" Anti-Pattern

**What it is**: Taking screenshots at every step for debugging

**Why it's bad**: Huge token consumption, doesn't help agents, slows tests

**Better pattern**: Use accessibility snapshots, one screenshot at failure only

### 3. The "CSS Selector Hell" Anti-Pattern

**What it is**: Using complex CSS selectors like `.container > div:nth-child(3) > span`

**Why it's bad**: Breaks on any UI change, not accessible

**Better pattern**: Use semantic locators based on ARIA roles and labels

---

## Gotcha Checklist for Implementation

Before marking PRP complete, verify these gotchas are addressed:

- [ ] **Browser installation**: Document `playwright install` requirement
- [ ] **Service health checks**: Verify frontend running before navigation
- [ ] **Thread safety**: Use multiprocessing or async, never threading
- [ ] **Semantic locators**: Use `get_by_role()`, not refs or CSS
- [ ] **Timeout configuration**: Set appropriate timeouts, use auto-wait
- [ ] **Token efficiency**: Use snapshots for agents, screenshots for humans
- [ ] **Resource cleanup**: Use context managers for browser lifecycle
- [ ] **User behavior**: Test what users see, not implementation
- [ ] **Tool naming**: Use short names in YAML, full names resolved by system
- [ ] **Error handling**: Retry patterns for flaky operations

---

## Sources Referenced

### From Archon
- `e9eb05e2bf38f125`: 12-factor-agents patterns (agent loop, tool configuration)
- `d60a71d62eb201d5`: MCP protocol specification (tool invocation patterns)
- `8ea7b5016269d351`: AI agents for beginners (common issues, production challenges)

### From Web
- https://playwright.dev/docs/best-practices - Official best practices
- https://playwright.dev/python/docs/library - Thread safety warning
- https://betterstack.com/community/guides/testing/playwright-best-practices/ - Common pitfalls
- https://github.com/microsoft/playwright-python/issues/470 - Thread safety issue
- https://playwright.dev/docs/test-timeouts - Timeout configuration
- https://autify.com/blog/playwright-timeout - Timeout error handling
- https://playwright.dev/docs/locators - Semantic locator patterns
- https://kentcdodds.com/blog/testing-implementation-details - Testing anti-patterns

### From Local Codebase
- `prps/playwright_agent_integration/planning/feature-analysis.md` - Risk mitigation strategies
- `prps/playwright_agent_integration/planning/codebase-patterns.md` - Agent configuration patterns
- `prps/playwright_agent_integration/planning/documentation-links.md` - Comprehensive documentation resources

---

## Recommendations for PRP Assembly

When generating the PRP:

1. **Include critical gotchas** in "Known Gotchas & Library Quirks" section
   - Browser installation (Gotcha #1)
   - Service availability (Gotcha #2)
   - Thread safety (Gotcha #3)
   - Element references (Gotcha #4)

2. **Reference solutions** in "Implementation Blueprint"
   - Health check pattern before browser navigation
   - Semantic locator examples
   - Context manager pattern for cleanup
   - Accessibility snapshot over screenshots

3. **Add detection tests** to validation gates
   - Verify browser binaries installed
   - Check frontend services running
   - Validate tool naming in agent YAML
   - Test semantic locator resilience

4. **Warn about version issues** in documentation references
   - Playwright 1.40+ accessibility snapshot deprecated
   - Python 3.8+ required
   - Browser auto-update mechanism

5. **Highlight anti-patterns** to avoid
   - No `time.sleep()` in tests
   - No hard-coded element refs
   - No screenshots for agent validation
   - No threading with Playwright sync API

---

## Confidence Assessment

**Gotcha Coverage**: 9/10

**Breakdown**:
- **Security**: 8/10 - Covered credential leakage, SSRF; may need more auth patterns
- **Performance**: 9/10 - Comprehensive coverage of timeout, token budget, API vs browser
- **Common Mistakes**: 10/10 - Extensive Playwright pitfalls documented with solutions
- **Configuration**: 8/10 - MCP tool naming, port conflicts covered; may need more Docker gotchas

**Gaps**:
- Playwright Python Windows-specific issues (ProactorEventLoop) - low priority
- Complex authentication flows (OAuth, SSO) - out of scope for MVP
- Browser extension testing - not applicable
- Mobile device emulation gotchas - out of scope

**Recommendation**: Coverage sufficient for MVP implementation. Address gaps in future iterations based on real-world usage feedback.
