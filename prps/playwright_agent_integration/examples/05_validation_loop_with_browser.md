# Source: .claude/agents/prp-exec-validator.md (lines 92-116) + .claude/patterns/quality-gates.md (lines 49-70)
# Pattern: Validation iteration loop with browser testing integrated
# Extracted: 2025-10-13
# Relevance: 10/10 - How to integrate browser tests into validation workflow

```python
for level in validation_levels:
    max_attempts = 5
    attempt = 0

    while attempt < max_attempts:
        result = run_validation(level)

        if result.passed:
            print(f"✅ {level} passed")
            break
        else:
            print(f"❌ {level} failed (attempt {attempt + 1})")
            errors = parse_errors(result)
            fixes = determine_fixes(errors)
            apply_fixes(fixes)
            attempt += 1

    if attempt == max_attempts:
        print(f"⚠️ {level} failed after {max_attempts} attempts")
        # Document the issue
        # Provide detailed report
```

## What This Demonstrates

The **validation iteration pattern** used by prp-exec-validator:

1. Run validation command
2. Parse errors if failed
3. Apply fix
4. Re-run (max 5 attempts)
5. Document if still failing

## Extended Pattern: Multi-Level Validation with Browser Tests

```python
# Multi-level validation (from quality-gates pattern)
MAX_ATTEMPTS = 5

validation_levels = [
    {
        "name": "Level 1: Syntax & Style",
        "type": "bash",
        "commands": ["ruff check --fix src/", "mypy src/"]
    },
    {
        "name": "Level 2: Unit Tests",
        "type": "bash",
        "commands": ["pytest tests/unit/ -v"]
    },
    {
        "name": "Level 3a: API Integration Tests",
        "type": "bash",
        "commands": ["pytest tests/integration/ -v"]
    },
    {
        "name": "Level 3b: Frontend Browser Tests",
        "type": "browser",
        "validation_func": validate_frontend_browser
    }
]

# Run all levels
for level in validation_levels:
    print(f"\n🔍 Running {level['name']}...")

    for attempt in range(1, MAX_ATTEMPTS + 1):
        if level['type'] == 'bash':
            result = run_bash_validation(level['commands'])
        elif level['type'] == 'browser':
            result = level['validation_func']()

        if result['success']:
            print(f"✅ {level['name']} passed")
            break

        print(f"❌ Attempt {attempt}/{MAX_ATTEMPTS} failed: {result['error']}")

        if attempt < MAX_ATTEMPTS:
            # Analyze error, apply fix
            fix = determine_fix(result['error'], prp_gotchas)
            apply_fix(fix)
        else:
            print(f"⚠️ Max attempts reached - manual intervention required")
```

## Browser Validation Function Example

```python
def validate_frontend_browser() -> dict:
    """
    Validate frontend UI via browser automation.
    Returns: {"success": bool, "error": str, "details": dict}
    """
    try:
        # 1. Ensure frontend is running
        response = Bash("curl -s http://localhost:5173")
        if "Connection refused" in response.stderr:
            return {
                "success": False,
                "error": "Frontend not running",
                "details": {"fix": "Run: docker-compose up -d"}
            }

        # 2. Navigate to frontend
        mcp__MCP_DOCKER__browser_navigate(url="http://localhost:5173")

        # 3. Capture initial state
        initial_state = mcp__MCP_DOCKER__browser_snapshot()

        # 4. Validate expected components present
        checks = {
            "app_loaded": "RootWebArea" in initial_state,
            "navigation": "navigation" in initial_state,
            "main_content": "main" in initial_state or "Documents" in initial_state,
        }

        if not all(checks.values()):
            failed_checks = [k for k, v in checks.items() if not v]
            return {
                "success": False,
                "error": f"Missing UI components: {failed_checks}",
                "details": {"state": initial_state[:500]}
            }

        # 5. Test critical user flow (document upload)
        mcp__MCP_DOCKER__browser_click(element="button containing 'Upload'")
        mcp__MCP_DOCKER__browser_wait_for(text="Select a document", timeout=5000)

        upload_dialog = mcp__MCP_DOCKER__browser_snapshot()
        if "Select a document" not in upload_dialog:
            return {
                "success": False,
                "error": "Upload dialog did not appear",
                "details": {"state": upload_dialog[:500]}
            }

        # 6. Fill form
        mcp__MCP_DOCKER__browser_fill_form(fields=[
            {"name": "file", "type": "file", "value": "/tmp/test-validation.pdf"}
        ])
        mcp__MCP_DOCKER__browser_click(element="button containing 'Submit'")

        # 7. Wait for success
        try:
            mcp__MCP_DOCKER__browser_wait_for(text="Upload successful", timeout=30000)
        except TimeoutError:
            final_state = mcp__MCP_DOCKER__browser_snapshot()
            return {
                "success": False,
                "error": "Upload did not complete within 30 seconds",
                "details": {"state": final_state[:500]}
            }

        # 8. Verify document appears in list
        final_state = mcp__MCP_DOCKER__browser_snapshot()
        if "test-validation.pdf" not in final_state:
            return {
                "success": False,
                "error": "Uploaded document not found in list",
                "details": {"state": final_state[:500]}
            }

        # 9. Take proof screenshot
        mcp__MCP_DOCKER__browser_take_screenshot(filename="frontend-validation-pass.png")

        # 10. Success!
        return {
            "success": True,
            "error": None,
            "details": {
                "message": "Frontend validation passed",
                "screenshot": "frontend-validation-pass.png"
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Browser validation exception: {str(e)}",
            "details": {"exception_type": type(e).__name__}
        }
```

## Error Pattern Matching for Browser Tests

```python
def determine_fix(error: str, prp_gotchas: str) -> dict:
    """
    Match browser test errors against known patterns.
    Returns: {"type": str, "fix": str, "file": str}
    """

    # Pattern 1: Frontend not running
    if "Connection refused" in error or "Frontend not running" in error:
        return {
            "type": "environment",
            "fix": "docker-compose up -d",
            "file": None,
            "description": "Start frontend service"
        }

    # Pattern 2: Browser not installed
    if "browser not installed" in error.lower():
        return {
            "type": "environment",
            "fix": "mcp__MCP_DOCKER__browser_install()",
            "file": None,
            "description": "Install Playwright browser"
        }

    # Pattern 3: Element not found
    if "Missing UI components" in error or "not found in list" in error:
        return {
            "type": "frontend_bug",
            "fix": "investigate_component_rendering",
            "file": "frontend/src/components/DocumentList.tsx",
            "description": "Check component rendering logic"
        }

    # Pattern 4: Timeout
    if "did not complete within" in error or "TimeoutError" in error:
        return {
            "type": "performance",
            "fix": "increase_timeout_or_investigate_slowness",
            "file": None,
            "description": "Check backend logs for slow operations"
        }

    # Pattern 5: Upload dialog not appearing
    if "Upload dialog did not appear" in error:
        return {
            "type": "interaction",
            "fix": "check_button_click_handler",
            "file": "frontend/src/components/UploadButton.tsx",
            "description": "Verify onClick handler wired correctly"
        }

    # Default: Unknown error
    return {
        "type": "unknown",
        "fix": "manual_investigation",
        "file": None,
        "description": f"Unknown error: {error[:100]}..."
    }
```

## Complete Validation Report Example

```markdown
# Validation Report: RAG Service Frontend

**Date**: 2025-10-13
**Final Status**: ✅ All Pass

## Validation Summary

| Level | Command | Status | Attempts | Time |
|-------|---------|--------|----------|------|
| 1 - Syntax | ruff check | ✅ Pass | 1 | 5s |
| 2 - Type Check | mypy | ✅ Pass | 1 | 8s |
| 3a - API Tests | pytest integration/ | ✅ Pass | 1 | 45s |
| 3b - Frontend Browser | validate_frontend_browser() | ✅ Pass | 2 | 120s |

**Total Time**: 178s
**Total Attempts**: 5
**Success Rate**: 100%

---

## Level 3b: Frontend Browser Tests

### Command
```python
validate_frontend_browser()
```

### Results

**Attempt 1**: ❌ Failed
- Error: `Frontend not running`
- Fix: Ran `docker-compose up -d`
- Re-run: ✅ Passed

**Attempt 2**: ✅ Passed
- Frontend loaded successfully
- Upload button clicked
- Document uploaded
- Document appeared in list
- Screenshot saved: `frontend-validation-pass.png`

**Final Status**: ✅ Pass (2 attempts)

---

## Browser Test Details

### Checks Performed
1. ✅ Frontend accessible at http://localhost:5173
2. ✅ App loaded with expected components
3. ✅ Navigation present
4. ✅ Main content rendered
5. ✅ Upload button clickable
6. ✅ Upload dialog appeared
7. ✅ Form submission successful
8. ✅ Upload completed within timeout
9. ✅ Document appeared in list

### Visual Proof
Screenshot: `frontend-validation-pass.png`

---

## Issues Resolved

### 1. Frontend Not Running
**Error**: Connection refused on localhost:5173
**Fix**: Ran `docker-compose up -d`
**Category**: Environment

---

## Next Steps

✅ All validations passed - ready for deployment
```

## Integration with PRP Validation Loop

In PRPs, add browser validation to Level 3:

```markdown
### Level 3: Integration Tests

#### API Integration Tests
```bash
pytest tests/integration/ -v
```

#### Frontend Browser Tests
```bash
# Agent-driven browser validation
claude --agent validation-gates "Validate RAG service frontend at localhost:5173"

# Or call validation function directly
python -c "from validation import validate_frontend_browser; validate_frontend_browser()"
```
```

## Gotchas

1. **Browser tests are slow**: 10x slower than API tests - run after API validation
2. **Environment dependencies**: Frontend must be running, browser must be installed
3. **Flaky tests**: Use proper wait strategies, not fixed sleep()
4. **Max attempts**: 5 attempts for browser tests may not be enough - consider 3 for browser
5. **Error messages**: Browser errors less structured than pytest - need custom parsing
