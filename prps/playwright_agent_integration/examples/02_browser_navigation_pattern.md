# Source: prps/INITIAL_playwright_agent_integration.md (lines 133-140)
# Pattern: Browser navigation and initial state capture
# Extracted: 2025-10-13
# Relevance: 9/10 - Foundation for all browser testing

```python
# Navigate to frontend
browser_navigate(url="http://localhost:5173")

# Capture page state
browser_snapshot()
```

## What This Demonstrates

The **basic browser navigation pattern** that all UI tests start with:

1. Navigate to the frontend URL
2. Capture the page's accessibility tree
3. Verify page loaded correctly

## Complete Example with Error Handling

```python
# 1. Navigate to frontend
try:
    mcp__MCP_DOCKER__browser_navigate(url="http://localhost:5173")
except ConnectionError as e:
    print(f"❌ Frontend not accessible: {e}")
    print("💡 Ensure docker-compose is running: docker-compose up -d")
    exit(1)

# 2. Capture initial state
initial_state = mcp__MCP_DOCKER__browser_snapshot()

# 3. Verify page loaded
if "DocumentList" in initial_state:
    print("✅ Page loaded - DocumentList component found")
elif "error" in initial_state.lower():
    print(f"❌ Page error: {initial_state}")
    exit(1)
else:
    print("⚠️ Page loaded but expected components not found")
    print(f"Accessibility tree: {initial_state[:500]}...")
```

## What the Accessibility Tree Provides

`browser_snapshot()` returns the **accessibility tree** (not visual screenshot):

- **Structured data** agents can parse
- Element roles (button, textbox, heading, etc.)
- Element labels and text content
- Element references (e.g., `ref="e5"`) for interaction
- Focus order and semantic structure

Example tree snippet:
```
RootWebArea "RAG Service"
  heading "Documents"
  button "Upload Document" ref="e5"
  list
    listitem "Document 1.pdf" ref="e12"
    listitem "Document 2.pdf" ref="e13"
```

## When to Use This Pattern

- **Start of every UI test**: Navigate → Snapshot → Verify
- **After user actions**: Capture state changes
- **Before assertions**: Verify expected elements present

## Common URLs

| Service | URL | Port |
|---------|-----|------|
| RAG Service Frontend | http://localhost:5173 | 5173 |
| Task Manager Frontend | http://localhost:5174 | 5174 |
| API Backend | http://localhost:8000 | 8000 |
| Qdrant | http://localhost:6333 | 6333 |

## Gotchas

1. **Frontend Must Be Running**: `docker-compose up -d` before navigation
2. **Wait for Ready**: Some apps need time to hydrate - wait for key element
3. **Browser Not Installed**: First run may need `mcp__MCP_DOCKER__browser_install()`
4. **Accessibility Tree vs Screenshot**: Snapshot is structured data, not visual
