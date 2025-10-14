# Source: prps/INITIAL_playwright_agent_integration.md (lines 206-244) + feature-analysis.md (lines 376-395)
# Pattern: Browser test error handling and recovery
# Extracted: 2025-10-13
# Relevance: 9/10 - Critical for robust browser validation

```python
# Try navigation
try:
    browser_navigate(url="http://localhost:5173")
except ConnectionError:
    # Check if frontend running
    result = Bash("docker-compose ps | grep rag-service")
    if "Up" not in result.stdout:
        # Start services
        Bash("docker-compose up -d")
        # Wait for health
        browser_wait_for(timeout=10000)
        # Retry navigation
        browser_navigate(url="http://localhost:5173")
```

## What This Demonstrates

The **error handling pattern** for browser tests:

1. Try operation
2. Catch specific error
3. Diagnose root cause
4. Apply fix
5. Retry operation

## Complete Error Handling Examples

### Error 1: Frontend Not Running

```python
def ensure_frontend_running(url: str, service_name: str) -> bool:
    """
    Ensure frontend service is running before browser tests.
    Returns: True if started successfully, False otherwise
    """
    try:
        # Check if accessible
        result = Bash(f"curl -s -o /dev/null -w '%{{http_code}}' {url}")
        if result.stdout.strip() in ["200", "304"]:
            print(f"✅ Frontend already running at {url}")
            return True
    except Exception:
        pass

    # Not accessible - check docker-compose
    print(f"⚠️ Frontend not accessible at {url}")
    ps_result = Bash("docker-compose ps")

    if service_name not in ps_result.stdout:
        print(f"❌ Service {service_name} not defined in docker-compose.yml")
        return False

    if "Up" not in ps_result.stdout:
        print(f"🔄 Starting {service_name} via docker-compose...")
        Bash("docker-compose up -d", timeout=60000)

        # Wait for health check
        print("⏳ Waiting for service to be ready...")
        for attempt in range(30):
            try:
                health_result = Bash(f"curl -s -o /dev/null -w '%{{http_code}}' {url}")
                if health_result.stdout.strip() in ["200", "304"]:
                    print(f"✅ Frontend ready at {url}")
                    return True
            except Exception:
                pass

            time.sleep(1)

        print(f"❌ Frontend did not become ready within 30 seconds")
        return False

    return True

# Usage
if ensure_frontend_running("http://localhost:5173", "rag-service"):
    mcp__MCP_DOCKER__browser_navigate(url="http://localhost:5173")
else:
    print("❌ Cannot proceed with browser tests - frontend not available")
    exit(1)
```

### Error 2: Browser Not Installed

```python
def ensure_browser_installed() -> bool:
    """
    Ensure Playwright browser is installed.
    Returns: True if installed successfully, False otherwise
    """
    try:
        # Try to navigate (will fail if browser not installed)
        mcp__MCP_DOCKER__browser_navigate(url="about:blank")
        print("✅ Browser already installed")
        return True
    except Exception as e:
        if "browser not installed" in str(e).lower() or "executable doesn't exist" in str(e).lower():
            print("⚠️ Browser not installed - installing now...")
            try:
                mcp__MCP_DOCKER__browser_install()
                print("✅ Browser installed successfully")

                # Verify installation
                mcp__MCP_DOCKER__browser_navigate(url="about:blank")
                return True
            except Exception as install_error:
                print(f"❌ Browser installation failed: {install_error}")
                return False
        else:
            print(f"❌ Unexpected error: {e}")
            return False

# Usage
if not ensure_browser_installed():
    print("❌ Cannot proceed with browser tests - browser not available")
    exit(1)
```

### Error 3: Element Not Found

```python
def safe_click(element_query: str, max_retries: int = 3, wait_between: int = 1000) -> bool:
    """
    Click element with retry logic for transient failures.
    Returns: True if clicked successfully, False otherwise
    """
    for attempt in range(1, max_retries + 1):
        try:
            # Capture current state
            state = mcp__MCP_DOCKER__browser_snapshot()

            # Check if element exists
            if element_query not in state:
                print(f"⚠️ Attempt {attempt}: Element '{element_query}' not found")
                print(f"Available elements: {state[:200]}...")

                if attempt < max_retries:
                    print(f"⏳ Waiting {wait_between}ms before retry...")
                    time.sleep(wait_between / 1000)
                    continue
                else:
                    print(f"❌ Element not found after {max_retries} attempts")
                    return False

            # Element found - try to click
            mcp__MCP_DOCKER__browser_click(element=element_query)
            print(f"✅ Clicked '{element_query}' successfully")
            return True

        except Exception as e:
            print(f"⚠️ Attempt {attempt} error: {e}")
            if attempt < max_retries:
                time.sleep(wait_between / 1000)
            else:
                print(f"❌ Failed to click after {max_retries} attempts")
                return False

    return False

# Usage
if not safe_click("button containing 'Upload'"):
    print("❌ Cannot proceed - upload button not clickable")
    # Take screenshot for debugging
    mcp__MCP_DOCKER__browser_take_screenshot(filename="error-element-not-found.png")
    exit(1)
```

### Error 4: Timeout Waiting for Element

```python
def wait_for_element_or_timeout(text: str, timeout_ms: int = 10000, check_interval_ms: int = 500) -> bool:
    """
    Wait for element with custom check interval.
    Returns: True if element appeared, False if timeout
    """
    elapsed = 0

    while elapsed < timeout_ms:
        state = mcp__MCP_DOCKER__browser_snapshot()

        if text in state:
            print(f"✅ Element with text '{text}' found after {elapsed}ms")
            return True

        time.sleep(check_interval_ms / 1000)
        elapsed += check_interval_ms

        if elapsed % 2000 == 0:  # Progress update every 2 seconds
            print(f"⏳ Still waiting for '{text}'... ({elapsed}/{timeout_ms}ms)")

    print(f"❌ Timeout: Element with text '{text}' not found after {timeout_ms}ms")

    # Debug: show current state
    final_state = mcp__MCP_DOCKER__browser_snapshot()
    print(f"Final state: {final_state[:500]}...")

    # Take screenshot for debugging
    mcp__MCP_DOCKER__browser_take_screenshot(filename="error-timeout.png")

    return False

# Usage
if not wait_for_element_or_timeout("Upload successful", timeout_ms=30000):
    print("❌ Upload did not complete - investigating...")

    # Check for error messages
    state = mcp__MCP_DOCKER__browser_snapshot()
    if "error" in state.lower():
        print(f"⚠️ Error message found in UI: {state}")

    # Check backend logs
    logs = Bash("docker-compose logs --tail=50 rag-service")
    if "error" in logs.stdout.lower():
        print(f"⚠️ Backend errors found: {logs.stdout[-500:]}")

    exit(1)
```

### Error 5: Port Conflict

```python
def check_port_available(port: int) -> tuple[bool, str]:
    """
    Check if port is available or already in use.
    Returns: (is_available, message)
    """
    result = Bash(f"lsof -i :{port} || echo 'PORT_FREE'")

    if "PORT_FREE" in result.stdout:
        return (True, f"Port {port} is available")
    else:
        # Port in use - find process
        lines = result.stdout.strip().split('\n')
        if len(lines) > 1:
            process_info = lines[1]
            return (False, f"Port {port} in use by: {process_info}")
        else:
            return (False, f"Port {port} in use")

# Usage
available, message = check_port_available(5173)
if not available:
    print(f"❌ {message}")
    print("💡 Options:")
    print("  1. Stop the conflicting process")
    print("  2. Change frontend port in docker-compose.yml")
    print("  3. Update test to use different port")
    exit(1)
else:
    print(f"✅ {message}")
```

## Complete Error Handling Workflow

```python
def validate_frontend_with_error_handling(url: str, service_name: str):
    """
    Complete browser validation with comprehensive error handling.
    """
    # Phase 1: Pre-flight checks
    print("\n🔍 Phase 1: Pre-flight Checks")

    # Check 1: Browser installed
    if not ensure_browser_installed():
        return {"success": False, "error": "Browser not available"}

    # Check 2: Port available
    port = int(url.split(':')[-1])
    available, message = check_port_available(port)
    if not available:
        return {"success": False, "error": message}

    # Check 3: Frontend running
    if not ensure_frontend_running(url, service_name):
        return {"success": False, "error": "Frontend not running"}

    print("✅ Pre-flight checks passed\n")

    # Phase 2: Browser Navigation
    print("🔍 Phase 2: Browser Navigation")

    try:
        mcp__MCP_DOCKER__browser_navigate(url=url)
        print(f"✅ Navigated to {url}")
    except Exception as e:
        print(f"❌ Navigation failed: {e}")
        return {"success": False, "error": f"Navigation error: {e}"}

    # Phase 3: UI Validation
    print("\n🔍 Phase 3: UI Validation")

    state = mcp__MCP_DOCKER__browser_snapshot()
    if "RootWebArea" not in state:
        print("❌ Page did not load correctly")
        mcp__MCP_DOCKER__browser_take_screenshot(filename="error-page-load.png")
        return {"success": False, "error": "Page load failed"}

    print("✅ Page loaded successfully")

    # Phase 4: Interaction Test
    print("\n🔍 Phase 4: Interaction Test")

    if not safe_click("button containing 'Upload'", max_retries=3):
        return {"success": False, "error": "Upload button not clickable"}

    if not wait_for_element_or_timeout("Select a document", timeout_ms=5000):
        return {"success": False, "error": "Upload dialog did not appear"}

    print("✅ Interaction test passed")

    # Phase 5: Final Validation
    print("\n🔍 Phase 5: Final Validation")

    mcp__MCP_DOCKER__browser_take_screenshot(filename="validation-success.png")
    print("✅ All checks passed")

    return {
        "success": True,
        "error": None,
        "details": {
            "url": url,
            "screenshot": "validation-success.png",
            "phases_completed": 5
        }
    }

# Usage
result = validate_frontend_with_error_handling(
    url="http://localhost:5173",
    service_name="rag-service"
)

if result['success']:
    print("\n✅ Frontend validation PASSED")
else:
    print(f"\n❌ Frontend validation FAILED: {result['error']}")
    exit(1)
```

## Common Error Patterns & Fixes

| Error Pattern | Root Cause | Fix | Detection |
|--------------|------------|-----|-----------|
| Connection refused | Frontend not running | `docker-compose up -d` | `curl` returns error |
| Browser not installed | First run | `browser_install()` | Exception on navigate |
| Element not found | Wrong query or timing | Use semantic query + wait | Check accessibility tree |
| Timeout | Slow operation | Increase timeout or investigate | Operation exceeds limit |
| Port conflict | Another process | Stop process or change port | `lsof -i :PORT` |
| Element reference changed | React re-render | Use text/role, not ref | Hard-coded ref fails |

## Gotchas

1. **Always check environment first**: Browser, frontend, ports
2. **Use retries for transient failures**: Network, timing, rendering
3. **Capture state on failure**: Screenshot + accessibility tree + logs
4. **Don't hard-code element refs**: Use semantic queries (text, role)
5. **Progressive timeout**: Start small (1s), increase if needed
6. **Max retries = 3 for browser**: Browser tests are slow - don't over-retry
