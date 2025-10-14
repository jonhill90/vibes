# Task Manager - Migrate to Streamable HTTP

**Status**: Not started
**Context**: Task Manager currently uses STDIO transport for MCP server, should use Streamable HTTP like vibesbox
**Related**: `infra/task-manager/`, `infra/vibesbox/` (reference pattern)

---

## Goal

Migrate Task Manager MCP server from STDIO transport to Streamable HTTP transport for:
- Persistent service in Docker container (no restart needed per Claude Desktop restart)
- Better development experience with hot reload
- Easier debugging with curl/httpie
- Pattern consistency with vibesbox

---

## Current State

### ✅ What's Working
- MCP server with STDIO transport (`mcp.run()` with no params)
- Consolidated tools: `find_tasks`, `manage_task`, `find_projects`, `manage_project`
- JSON string responses (Gotcha #3 compliance)
- Docker Compose multi-service setup
- FastAPI backend, React frontend, PostgreSQL database

### ❌ What Needs Changing
- MCP server uses STDIO transport (requires Python script invocation)
- No MCP port exposed in Docker Compose
- Claude Desktop config uses `command`/`args` pattern instead of HTTP URL
- Service requires restart when Claude Desktop restarts

---

## Tasks

### 1. Update MCP Server to Streamable HTTP
**Priority**: High | **Effort**: 30 minutes

**1.1 Update MCP Server Configuration**
File: `infra/task-manager/backend/src/mcp_server.py`

Change from:
```python
# MCP server instance
mcp = FastMCP("Task Manager")

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
```

To:
```python
# MCP server instance with HTTP configuration
# PATTERN FROM: vibesbox/src/mcp_server.py
mcp = FastMCP(
    "Task Manager",
    host="0.0.0.0",
    port=8051  # Internal port (mapped to external via docker-compose)
)

if __name__ == "__main__":
    # Run the MCP server with streamable-http transport
    # PATTERN FROM: vibesbox/src/mcp_server.py
    logger.info("Starting Task Manager MCP server...")
    logger.info(f"   Mode: Streamable HTTP")
    logger.info(f"   URL: http://0.0.0.0:8051/mcp")

    try:
        mcp.run(transport="streamable-http")
    except KeyboardInterrupt:
        logger.info("Task Manager MCP server stopped by user")
    except Exception as e:
        logger.error(f"Fatal error in MCP server: {e}", exc_info=True)
        raise
```

**1.2 Validation**
- Code changes are minimal (3 lines changed)
- Pattern matches vibesbox exactly
- Logging added for debugging

---

### 2. Update Docker Compose Configuration
**Priority**: High | **Effort**: 15 minutes

**2.1 Update Backend Service**
File: `infra/task-manager/docker-compose.yml`

Change backend service from:
```yaml
backend:
  ports:
    - "${API_PORT:-8000}:8000"  # FastAPI server
```

To:
```yaml
backend:
  ports:
    - "${API_PORT:-8000}:8000"  # FastAPI server
    - "${MCP_PORT:-8051}:8051"  # MCP server
  environment:
    - MCP_PORT=${MCP_PORT:-8051}
```

**2.2 Validation**
- MCP port exposed (8051 internal -> 8051 external, avoiding 8052 used by rag-service)
- Environment variable for port configuration
- No conflicts with other services (API: 8000, RAG MCP: 8052, Task MCP: 8051)

---

### 3. Update Claude Desktop Configuration
**Priority**: High | **Effort**: 10 minutes

**3.1 Update Config File**
File: `~/.config/claude/claude_desktop_config.json`

Change from:
```json
{
  "mcpServers": {
    "task-manager": {
      "command": "python",
      "args": ["/path/to/backend/src/mcp_server.py"],
      "env": {
        "DATABASE_URL": "postgresql://...",
        ...
      }
    }
  }
}
```

To:
```json
{
  "mcpServers": {
    "task-manager": {
      "transport": {
        "type": "streamable-http",
        "url": "http://localhost:8051/mcp"
      }
    }
  }
}
```

**3.2 Benefits**
- No environment variables needed in client config (service already running in Docker with env vars)
- No file paths needed (service is containerized)
- Simple URL-based connection
- Works immediately when Docker services are running

---

### 4. Test and Validate
**Priority**: High | **Effort**: 15 minutes

**4.1 Start Services**
```bash
cd infra/task-manager
docker-compose restart backend
docker-compose ps  # Verify backend is healthy
```

**4.2 Test MCP Endpoint**
```bash
# Test MCP server is accessible
curl http://localhost:8051/health || echo "Health endpoint may not exist"

# MCP endpoint should respond (exact format depends on MCP protocol)
curl -X POST http://localhost:8051/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
```

**4.3 Test from Claude Desktop**
- Restart Claude Desktop
- Test `find_tasks()` - should list tasks
- Test `manage_task("create", project_id="...", title="Test")` - should create task
- Test `find_projects()` - should list projects
- Test `manage_project("create", name="Test Project")` - should create project

**4.4 Validation Gates**
- [ ] MCP server starts without errors
- [ ] MCP port 8051 is accessible
- [ ] All 4 tools work from Claude Desktop
- [ ] No environment variables needed in Claude config
- [ ] Service persists across Claude Desktop restarts

---

## Success Criteria

Implementation complete when:
1. ✅ MCP server uses Streamable HTTP transport
2. ✅ Docker Compose exposes MCP port 8051
3. ✅ Claude Desktop connects via HTTP URL
4. ✅ All MCP tools work from Claude Desktop
5. ✅ Service persists across Claude restarts
6. ✅ Pattern matches vibesbox implementation

---

## Estimated Timeline

- **Update MCP server**: 30 minutes
- **Update Docker Compose**: 15 minutes
- **Update Claude config**: 10 minutes
- **Testing**: 15 minutes

**Total**: ~1-1.5 hours

---

## Notes

**Why Streamable HTTP vs STDIO?**
- STDIO requires Python script invocation per Claude Desktop restart
- HTTP allows service to run in Docker container persistently
- Better for development: service stays running with hot reload
- Matches vibesbox pattern for consistency
- Easier debugging: can test MCP endpoints with curl/httpie

**Pattern References:**
- `infra/vibesbox/src/mcp_server.py:39-44` - FastMCP HTTP configuration
- `infra/vibesbox/src/mcp_server.py:296-309` - Main entry point with streamable-http
- `infra/vibesbox/docker-compose.yml:16-17` - Port mapping pattern
- `infra/rag-service/docker-compose.yml:70` - Alternative port mapping (8052)

**Port Allocation:**
- Task Manager API: 8000 (internal) -> 8000 (external)
- Task Manager MCP: 8051 (internal) -> 8051 (external)
- RAG Service API: 8001 (internal) -> 8001 (external)
- RAG Service MCP: 8000 (internal) -> 8052 (external)
- Vibesbox MCP: 8000 (internal) -> 8053 (external)

**Architecture:**
- FastAPI and MCP server run in same container (backend service)
- Both expose different ports
- MCP server shares database pool with FastAPI via shared code
- Clean separation of concerns: API for frontend, MCP for AI assistant

---

**Next Action**: Start with Task 1 (Update MCP Server) - minimal code change, foundational for other tasks
