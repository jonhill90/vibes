# Source: .claude/patterns/browser-validation.md
# Lines: 304-403 (complete example extracted)
# Pattern: Browser validation workflow with pre-flight checks
# Extracted: 2025-10-16
# Relevance: 10/10

"""Browser Validation Workflow Pattern.

This example demonstrates the complete browser validation workflow:
1. Pre-flight checks (browser installed, services running)
2. Navigation and initial state validation
3. UI interaction (clicks, form fills)
4. Wait for operations to complete
5. Final state validation
6. Screenshot for human proof

Key patterns:
- browser_snapshot() for agent validation (structured data)
- browser_take_screenshot() for human proof only
- Semantic queries for element selection
- Auto-wait with appropriate timeouts
- Comprehensive error handling

This is the gold standard pattern for all browser tests.
"""

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


# Pre-flight check helper functions
def check_browser_installed() -> bool:
    """Verify browser binaries are installed."""
    try:
        browser_navigate(url="about:blank")
        print("✅ Browser installed")
        return True
    except Exception:
        print("⚠️ Browser not installed")
        return False


def check_frontend_running(port: int) -> bool:
    """Verify frontend service is running."""
    result = Bash(f"curl -s http://localhost:{port}")
    if "Connection refused" in result.stderr:
        print(f"❌ Frontend not running on port {port}")
        return False
    print(f"✅ Frontend running on port {port}")
    return True


def verify_service_identity(url: str, expected_title: str) -> bool:
    """Ensure correct service is running."""
    browser_navigate(url=url)
    title = browser_evaluate(function="() => document.title")
    if expected_title in title:
        print(f"✅ Correct service: {title}")
        return True
    print(f"❌ Wrong service. Expected '{expected_title}', got '{title}'")
    return False


def run_preflight_checks() -> bool:
    """Run all pre-flight checks before browser validation."""
    print("🔍 Running pre-flight checks...")

    checks = [
        ("Browser installed", check_browser_installed),
        ("Frontend running", lambda: check_frontend_running(5173)),
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


# Error handling with retry pattern
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


# Usage examples
if __name__ == "__main__":
    # Example 1: Simple validation
    validate_document_upload()

    # Example 2: With pre-flight checks
    if run_preflight_checks():
        validate_document_upload()

    # Example 3: With error handling
    success = validate_with_error_handling()
    if not success:
        exit(1)
