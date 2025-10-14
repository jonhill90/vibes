# Source: prps/INITIAL_playwright_agent_integration.md (lines 157-164)
# Pattern: Browser state validation and proof capture
# Extracted: 2025-10-13
# Relevance: 10/10 - How to validate UI state and capture proof

```python
# Take screenshot for visual proof
browser_take_screenshot(filename="validation-proof.png")

# Run JavaScript assertion
browser_evaluate(function="() => document.querySelectorAll('.task-card').length")
```

## What This Demonstrates

**Two validation approaches**:

1. **Visual proof**: Screenshots for human verification
2. **Programmatic validation**: JavaScript execution for agent validation

## Complete Validation Example

```python
# After completing user action (e.g., document upload)

# 1. Capture final state via accessibility tree
final_state = mcp__MCP_DOCKER__browser_snapshot()

# 2. Verify expected elements present
if "Test Document" in final_state and "Upload successful" in final_state:
    print("✅ Document uploaded successfully")
else:
    print("❌ Expected elements not found")
    print(f"State: {final_state[:500]}...")

# 3. Take screenshot for human verification (optional)
mcp__MCP_DOCKER__browser_take_screenshot(filename="document-upload-success.png")
print("📸 Screenshot saved for visual verification")

# 4. Run JavaScript validation (count elements)
document_count = mcp__MCP_DOCKER__browser_evaluate(
    function="() => document.querySelectorAll('.document-card').length"
)
print(f"Found {document_count} documents in UI")

if document_count > 0:
    print("✅ Document rendered in list")
else:
    print("❌ No documents found in UI")
```

## Validation Strategies

### Strategy 1: Accessibility Tree Validation (PREFERRED)

**Why**: Structured data agents can parse directly

```python
# Capture accessibility tree
state = mcp__MCP_DOCKER__browser_snapshot()

# Check for expected elements
validation_checks = {
    "upload_button": "button containing 'Upload'" in state,
    "document_list": "list" in state,
    "first_document": "Document 1.pdf" in state,
}

all_passed = all(validation_checks.values())
if all_passed:
    print("✅ All UI elements present")
else:
    failed = [k for k, v in validation_checks.items() if not v]
    print(f"❌ Missing elements: {failed}")
```

### Strategy 2: JavaScript Evaluation (PROGRAMMATIC)

**Why**: Precise element counting, attribute checking

```python
# Count specific elements
result = mcp__MCP_DOCKER__browser_evaluate(
    function="""() => {
        return {
            documentCount: document.querySelectorAll('.document-card').length,
            uploadButtonEnabled: !document.querySelector('button[name="upload"]')?.disabled,
            searchResultsVisible: document.querySelector('.search-results')?.style.display !== 'none'
        }
    }"""
)

print(f"Validation results: {result}")

# Expected: {"documentCount": 3, "uploadButtonEnabled": true, "searchResultsVisible": true}
```

### Strategy 3: Screenshot Capture (HUMAN VERIFICATION)

**Why**: Visual proof for human review, debugging

```python
# Take screenshot at critical points
mcp__MCP_DOCKER__browser_take_screenshot(filename="before-action.png")

# ... perform action ...

mcp__MCP_DOCKER__browser_take_screenshot(filename="after-action.png")

print("📸 Screenshots saved:")
print("  - before-action.png")
print("  - after-action.png")
print("Review these for visual verification")
```

**IMPORTANT**: Agents cannot parse screenshots directly! Use accessibility tree for validation.

## Common Validation Patterns

### Pattern 1: Element Existence

```python
state = mcp__MCP_DOCKER__browser_snapshot()

# Check element exists
if "button containing 'Submit'" in state:
    print("✅ Submit button present")
else:
    print("❌ Submit button not found")
```

### Pattern 2: Element Count

```python
count = mcp__MCP_DOCKER__browser_evaluate(
    function="() => document.querySelectorAll('.task-card').length"
)

if count == expected_count:
    print(f"✅ Correct number of tasks: {count}")
else:
    print(f"❌ Expected {expected_count} tasks, found {count}")
```

### Pattern 3: Element State

```python
button_state = mcp__MCP_DOCKER__browser_evaluate(
    function="""() => {
        const btn = document.querySelector('button[name="submit"]');
        return {
            disabled: btn?.disabled,
            visible: btn?.offsetParent !== null,
            text: btn?.textContent.trim()
        }
    }"""
)

if not button_state['disabled'] and button_state['visible']:
    print("✅ Submit button ready for interaction")
else:
    print("❌ Submit button not ready")
```

### Pattern 4: Form Validation State

```python
form_errors = mcp__MCP_DOCKER__browser_evaluate(
    function="() => Array.from(document.querySelectorAll('.error-message')).map(el => el.textContent)"
)

if len(form_errors) == 0:
    print("✅ No form validation errors")
else:
    print(f"❌ Form errors: {form_errors}")
```

## Full Example: RAG Service Document Upload Validation

```python
# 1. Upload document (see 03_browser_interaction_pattern.md)
mcp__MCP_DOCKER__browser_navigate(url="http://localhost:5173")
mcp__MCP_DOCKER__browser_click(element="button containing 'Upload'")
mcp__MCP_DOCKER__browser_fill_form(fields=[
    {"name": "file", "type": "file", "value": "/tmp/test-doc.pdf"}
])
mcp__MCP_DOCKER__browser_click(element="button containing 'Submit'")
mcp__MCP_DOCKER__browser_wait_for(text="Upload successful", timeout=30000)

# 2. Validation Phase
print("\n🔍 Validating upload result...")

# 2a. Check accessibility tree
final_state = mcp__MCP_DOCKER__browser_snapshot()
validation_results = {
    "success_message": "Upload successful" in final_state,
    "document_in_list": "test-doc.pdf" in final_state,
    "list_visible": "list" in final_state,
}

# 2b. Count documents via JavaScript
doc_count = mcp__MCP_DOCKER__browser_evaluate(
    function="() => document.querySelectorAll('.document-card').length"
)
validation_results["document_count_positive"] = doc_count > 0

# 2c. Take proof screenshot
mcp__MCP_DOCKER__browser_take_screenshot(filename="upload-validation.png")

# 3. Report results
all_passed = all(validation_results.values())
if all_passed:
    print("✅ Upload validation PASSED")
    print(f"  - Success message displayed")
    print(f"  - Document appears in list")
    print(f"  - {doc_count} total documents")
    print(f"  - Screenshot saved: upload-validation.png")
else:
    print("❌ Upload validation FAILED")
    failed_checks = [k for k, v in validation_results.items() if not v]
    print(f"  - Failed checks: {failed_checks}")
    print(f"  - State: {final_state[:200]}...")
```

## When to Use Each Strategy

| Strategy | Use When | Performance | Agent-Friendly |
|----------|----------|-------------|----------------|
| Accessibility Tree | Checking element presence/text | Fast (~100ms) | ✅ Yes |
| JavaScript Evaluate | Precise counts, attributes | Fast (~50ms) | ✅ Yes |
| Screenshot | Human review, debugging | Slow (~500ms) | ❌ No (visual only) |

## Gotchas

1. **Screenshots for Humans Only**: Agents can't parse images - use accessibility tree
2. **Token Budget**: Screenshots consume ~2000 tokens each - use sparingly
3. **Timing**: Wait for state stabilization before validation
4. **JavaScript Scope**: Runs in browser context - can access DOM but not Node.js globals
5. **Accessibility Tree Updates**: Re-capture after actions (tree is a snapshot, not live)
