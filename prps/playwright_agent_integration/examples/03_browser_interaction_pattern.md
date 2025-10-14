# Source: prps/INITIAL_playwright_agent_integration.md (lines 142-155)
# Pattern: Browser UI interaction (click, type, fill form)
# Extracted: 2025-10-13
# Relevance: 10/10 - Core interaction patterns for validation

```python
# Click element
browser_click(element="Upload button", ref="e5")

# Fill form
browser_fill_form(fields=[
    {"name": "title", "type": "textbox", "ref": "e6", "value": "Test Doc"},
    {"name": "file", "type": "file", "ref": "e7", "value": "/path/to/test.pdf"}
])

# Wait for success
browser_wait_for(text="Upload successful")
```

## What This Demonstrates

**Three core interaction patterns**:

1. **Clicking elements**: Buttons, links, tabs
2. **Filling forms**: Text inputs, file uploads, dropdowns
3. **Waiting for results**: Success messages, state changes

## Complete Example: RAG Service Upload Flow

```python
# 1. Navigate and capture initial state
mcp__MCP_DOCKER__browser_navigate(url="http://localhost:5173")
initial_snapshot = mcp__MCP_DOCKER__browser_snapshot()

# 2. Find and click Upload button
# Use semantic query (text-based, not hard-coded ref)
mcp__MCP_DOCKER__browser_click(element="button containing 'Upload'")

# 3. Wait for upload dialog to appear
mcp__MCP_DOCKER__browser_wait_for(text="Select a document", timeout=5000)

# 4. Fill form fields
mcp__MCP_DOCKER__browser_fill_form(fields=[
    {
        "name": "title",
        "type": "textbox",
        "value": "Test Research Paper"
    },
    {
        "name": "description",
        "type": "textbox",
        "value": "Testing document upload flow"
    },
    {
        "name": "file",
        "type": "file",
        "value": "/tmp/test-document.pdf"
    }
])

# 5. Submit form
mcp__MCP_DOCKER__browser_click(element="button containing 'Submit'")

# 6. Wait for upload to complete
mcp__MCP_DOCKER__browser_wait_for(text="Upload successful", timeout=30000)

# 7. Verify document appears in list
final_snapshot = mcp__MCP_DOCKER__browser_snapshot()
if "Test Research Paper" in final_snapshot:
    print("✅ Document uploaded and displayed correctly")
else:
    print("❌ Document not found in list after upload")
    print(f"Final state: {final_snapshot[:500]}...")
```

## Element Selection Strategies

### ✅ PREFER: Semantic Queries (Stable)

```python
# Use text content (resilient to UI changes)
browser_click(element="button containing 'Upload'")
browser_click(element="link containing 'Documentation'")
browser_type(element="textbox labeled 'Search'", text="test query")
```

### ⚠️ AVOID: Hard-Coded References (Brittle)

```python
# Element refs change between renders
browser_click(element="button", ref="e5")  # May become e6 after re-render
```

### ✅ GOOD: Role-Based Queries

```python
# Use ARIA roles
browser_click(element="button[name='submit']")
browser_type(element="textbox[aria-label='Email']", text="test@example.com")
```

## Form Filling Patterns

### Simple Text Input

```python
mcp__MCP_DOCKER__browser_type(
    element="textbox labeled 'Title'",
    text="My Document Title"
)
```

### Multi-Field Form

```python
mcp__MCP_DOCKER__browser_fill_form(fields=[
    {"name": "title", "type": "textbox", "value": "Document Title"},
    {"name": "author", "type": "textbox", "value": "John Doe"},
    {"name": "category", "type": "combobox", "value": "Research"},
])
```

### File Upload

```python
# File must exist on disk
mcp__MCP_DOCKER__browser_fill_form(fields=[
    {"name": "file", "type": "file", "value": "/absolute/path/to/file.pdf"}
])
```

## Wait Strategies

### Wait for Text to Appear

```python
# Wait for success message (max 10 seconds)
mcp__MCP_DOCKER__browser_wait_for(text="Upload successful", timeout=10000)
```

### Wait for Element to Appear

```python
# Wait for specific element role
mcp__MCP_DOCKER__browser_wait_for(text="Document Title", timeout=5000)
```

### Custom Wait with JavaScript

```python
# Wait for custom condition
mcp__MCP_DOCKER__browser_evaluate(
    function="() => document.querySelectorAll('.document-card').length > 0"
)
```

## Common Interaction Patterns

### Task Manager: Create Task

```python
mcp__MCP_DOCKER__browser_navigate(url="http://localhost:5174")
mcp__MCP_DOCKER__browser_click(element="button containing 'Create Task'")
mcp__MCP_DOCKER__browser_fill_form(fields=[
    {"name": "title", "type": "textbox", "value": "Test Task"},
    {"name": "description", "type": "textbox", "value": "Testing browser validation"},
])
mcp__MCP_DOCKER__browser_click(element="button containing 'Submit'")
mcp__MCP_DOCKER__browser_wait_for(text="Test Task", timeout=5000)
```

### RAG Service: Search Documents

```python
mcp__MCP_DOCKER__browser_navigate(url="http://localhost:5173/search")
mcp__MCP_DOCKER__browser_type(
    element="textbox labeled 'Search'",
    text="machine learning"
)
mcp__MCP_DOCKER__browser_click(element="button containing 'Search'")
mcp__MCP_DOCKER__browser_wait_for(text="Search results", timeout=10000)
```

## Gotchas

1. **Element References Change**: Always use semantic queries (text, role)
2. **Timing Issues**: Always wait after clicks/submits - don't assume instant
3. **File Paths**: Must be absolute paths, file must exist
4. **Timeout Tuning**: 5s for fast ops, 30s for uploads, 60s for processing
5. **React Re-renders**: Accessibility tree refs (`e5`, `e6`) change - DON'T hard-code
