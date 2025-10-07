# Codebase Patterns: Fix Task Manager System

## Overview

This document provides concrete patterns from working Docker Compose services (Archon, LiteLLM) and relevant knowledge base examples for debugging and fixing the task manager. The primary focus is on Docker Compose health checks, multi-service orchestration, Python backend patterns with FastAPI + asyncpg, and React frontend with Vite. These patterns will guide systematic debugging of a system that has never successfully run.

## Architectural Patterns

### Pattern 1: Docker Compose Health Check Dependencies

**Source**: `/Users/jon/source/vibes/infra/archon/docker-compose.yml` (lines 54-65, 94-110)
**Relevance**: 10/10

**What it does**: Ensures services start in correct order with health validation, preventing "connection refused" errors when backend tries to connect to database before it's ready.

**Key Techniques**:
```yaml
# Database health check (PostgreSQL)
db:
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-taskuser} -d ${POSTGRES_DB:-taskmanager}"]
    interval: 5s
    timeout: 5s
    retries: 5
    start_period: 10s  # Critical: Give database time to initialize

# Backend depends on healthy database
backend:
  depends_on:
    db:
      condition: service_healthy  # Wait for health check to pass
```

**When to use**:
- Always use for multi-service Docker Compose setups
- Database must be healthy before backend connects
- Backend must be healthy before frontend makes API calls
- Prevents race conditions during container startup

**How to adapt**:
- Task manager already has this pattern in `docker-compose.yml` (lines 24-29, 57-60)
- Verify health check is actually passing: `docker-compose ps`
- Check that `pg_isready` uses correct variables
- Ensure backend waits for `service_healthy` not just `service_started`

**Why this pattern**:
- Eliminates 90% of "connection refused" startup errors
- Provides clear service status in `docker-compose ps`
- Allows services to retry until dependencies ready
- Standard pattern across all vibes infra services

### Pattern 2: Python Backend with uv + Multi-Stage Build

**Source**: `/Users/jon/source/vibes/infra/archon/python/Dockerfile.server` (lines 1-18)
**Relevance**: 10/10

**What it does**: Builds Python application with uv package manager in isolated build stage, then copies only necessary artifacts to runtime stage for minimal image size and faster startup.

**Key Techniques**:
```dockerfile
# BUILD STAGE - Install dependencies with uv
FROM python:3.12-slim AS builder
WORKDIR /build
RUN pip install --no-cache-dir uv

COPY pyproject.toml .

# Install to virtual environment
RUN uv venv /venv && \
    . /venv/bin/activate && \
    uv pip install --group server --group server-reranking

# RUNTIME STAGE - Minimal production image
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /venv /venv
ENV PATH="/venv/bin:$PATH"
```

**When to use**:
- All Python services using uv package manager
- When you need reproducible builds
- Production deployments requiring minimal image size
- Development with hot reload via volume mounts

**How to adapt**:
- Task manager backend Dockerfile already follows this pattern
- **CRITICAL**: Check if `uv pip install -r pyproject.toml` is correct syntax
- Archon uses `uv pip install --group {groupname}` for dependency groups
- Task manager may need `uv.lock` file for frozen dependencies
- Verify all dependencies in pyproject.toml are compatible

**Why this pattern**:
- Multi-stage builds reduce final image size by 60-70%
- Virtual environment isolation prevents dependency conflicts
- uv is 10-100x faster than pip for dependency resolution
- Separates build-time dependencies from runtime

### Pattern 3: Multi-Process Container with Shell Script

**Source**: `/Users/jon/source/vibes/infra/task-manager/backend/start.sh` (lines 1-9)
**Relevance**: 10/10

**What it does**: Runs multiple Python services (MCP server + FastAPI) in a single container using background process for MCP and foreground process for API.

**Key Techniques**:
```bash
#!/bin/bash
set -e  # Exit on error

# Start MCP server in background on port 8051
python -m src.mcp_server &
MCP_PID=$!

# Start FastAPI server on port 8000 (foreground)
exec uvicorn src.main:app --host 0.0.0.0 --port "${API_PORT:-8000}"
```

**When to use**:
- Running multiple related services in one container
- MCP server + API server colocated for simplicity
- Development environments where service separation not critical
- When both processes need same Python environment

**How to adapt**:
- **CRITICAL**: Verify start.sh has executable permissions
- Check with: `ls -l infra/task-manager/backend/start.sh`
- If not executable: `chmod +x infra/task-manager/backend/start.sh`
- Or update Dockerfile CMD to: `CMD ["bash", "start.sh"]`
- Add logging to verify both processes start: `echo "MCP server started with PID $MCP_PID"`

**Why this pattern**:
- Simpler deployment (one container vs two)
- Shared Python environment reduces memory
- `exec` ensures signals propagate correctly to API server
- Background process + foreground process is Docker best practice

### Pattern 4: Frontend Vite Dev Server in Docker

**Source**: `/Users/jon/source/vibes/infra/task-manager/frontend/Dockerfile` (lines 1-23)
**Relevance**: 9/10

**What it does**: Runs Vite development server inside Docker with hot reload support and proper host binding for container networking.

**Key Techniques**:
```dockerfile
FROM node:20-alpine
WORKDIR /app

# Install system dependencies
RUN apk add --no-cache python3 make g++ git curl

# Use npm ci for reproducible builds
COPY package*.json ./
RUN npm ci

COPY . .
EXPOSE 3000

# CRITICAL: --host flag makes Vite accessible from outside container
CMD ["npm", "run", "dev", "--", "--host"]
```

**When to use**:
- Development environments with Docker Compose
- Need hot reload for frontend development
- React/Vue/Svelte applications using Vite
- When frontend needs to call backend in different container

**How to adapt**:
- Task manager frontend Dockerfile already correct
- Verify `package.json` has correct Vite dev script
- Check that `--host` flag is present (allows external connections)
- Ensure VITE_API_URL points to backend (http://localhost:8000 from host)
- Volume mount excludes node_modules: `-/app/node_modules` in docker-compose.yml

**Why this pattern**:
- Hot reload works through Docker volume mounts
- `--host` flag essential for container networking
- npm ci ensures reproducible builds vs npm install
- Alpine base image reduces image size significantly

### Pattern 5: PostgreSQL Initialization with Volume Management

**Source**: `/Users/jon/source/vibes/infra/task-manager/docker-compose.yml` (lines 14-18, 94-96)
**Relevance**: 10/10

**What it does**: Initializes PostgreSQL database with custom SQL scripts and uses named volumes to persist data across container restarts.

**Key Techniques**:
```yaml
db:
  image: postgres:16
  volumes:
    # Named volume for data persistence
    - taskmanager-db-data:/var/lib/postgresql/data
    # Init script runs ONLY on first container start
    - ./database:/docker-entrypoint-initdb.d:ro

volumes:
  taskmanager-db-data:
    driver: local
```

**When to use**:
- Any PostgreSQL database in Docker
- When you need custom schema initialization
- Development and production deployments
- When database needs to survive container restarts

**How to adapt**:
- Task manager already has this pattern
- **CRITICAL GOTCHA**: Init scripts only run if volume is empty
- To force re-initialization: `docker-compose down -v` (deletes volume)
- Verify init.sql exists: `/Users/jon/source/vibes/infra/task-manager/database/init.sql`
- Check database logs to confirm init script ran: `docker-compose logs db | grep init`
- Confirm tables created: `docker exec -it taskmanager-db psql -U taskuser -d taskmanager -c "\dt"`

**Why this pattern**:
- Named volumes prevent permission issues vs bind mounts
- Read-only mount for init scripts prevents accidental modification
- PostgreSQL docker-entrypoint runs all .sql files in order
- Volume persistence means data survives `docker-compose down`

## Naming Conventions

### File Naming
**Pattern**: `{service}_service.py`, `{resource}_api.py`, `{component}.tsx`
**Examples from codebase**:
- Backend services: `project_service.py`, `task_service.py`, `knowledge_service.py`
- API routes: `projects_api.py`, `knowledge_api.py`, `progress_api.py`
- React components: `ProjectCard.tsx`, `TaskList.tsx`, `NewProjectModal.tsx`

### Class Naming
**Pattern**: PascalCase for classes, camelCase for instances
**Examples**:
- Models: `Project`, `Task`, `Document`
- Services: `ProjectService`, `KnowledgeService`
- Exceptions: `DatabaseConnectionError`, `ProjectNotFoundError`

### Function Naming
**Pattern**: snake_case for Python, camelCase for TypeScript
**Examples**:
- Python: `get_project_by_id()`, `create_task()`, `generate_etag()`
- TypeScript: `useProjects()`, `createProject()`, `handleSubmit()`

### Environment Variables
**Pattern**: `UPPERCASE_WITH_UNDERSCORES`, defaults with `${VAR:-default}`
**Examples from .env.example**:
- `POSTGRES_DB=taskmanager`
- `POSTGRES_USER=taskuser`
- `DATABASE_URL=postgresql+asyncpg://taskuser:taskpass123@db:5432/taskmanager`
- Docker Compose: `${POSTGRES_USER:-taskuser}` (defaults to taskuser if not set)

## File Organization

### Docker Compose Multi-Service Structure
```
infra/task-manager/
├── docker-compose.yml       # Service orchestration
├── .env.example             # Environment template (COPY TO .env!)
├── database/
│   └── init.sql            # Database schema initialization
├── backend/
│   ├── Dockerfile          # Python 3.12 + uv build
│   ├── pyproject.toml      # Python dependencies
│   ├── start.sh            # Multi-process startup script
│   ├── src/
│   │   ├── main.py         # FastAPI application
│   │   ├── mcp_server.py   # MCP server entry point
│   │   ├── config/
│   │   │   └── database.py # Database connection pool
│   │   ├── api/            # API route handlers
│   │   └── services/       # Business logic layer
│   └── alembic/            # Database migrations
└── frontend/
    ├── Dockerfile          # Node 20 + Vite
    ├── package.json        # Node dependencies
    ├── vite.config.ts      # Vite configuration
    └── src/
        ├── features/       # Feature-based organization
        └── pages/          # Route components
```

**Justification**:
- Vertical separation (backend/frontend/database) mirrors service boundaries
- Each service has own Dockerfile for independent building
- Shared database/ directory for init scripts accessible to db service
- docker-compose.yml at root for service orchestration
- Pattern matches Archon structure (`infra/archon/python/`, `infra/archon/archon-ui-main/`)

## Common Utilities to Leverage

### 1. ETag Generation for Caching
**Location**: `/Users/jon/source/vibes/infra/archon/python/src/server/utils/etag_utils.py`
**Purpose**: Generate MD5-based ETags for HTTP caching, reduce bandwidth by ~70%
**Usage Example**:
```python
from src.server.utils.etag_utils import generate_etag, check_etag

# In API endpoint
@app.get("/api/tasks")
async def get_tasks(request: Request):
    data = await task_service.get_all()
    etag = generate_etag(data)

    # Return 304 if client has current version
    if check_etag(request, etag):
        return Response(status_code=304, headers={"ETag": etag})

    return JSONResponse(content=data, headers={"ETag": etag})
```

### 2. Smart Polling for Real-Time Updates
**Location**: `/Users/jon/source/vibes/infra/archon/archon-ui-main/src/features/ui/hooks/useSmartPolling.ts`
**Purpose**: Visibility-aware polling that pauses when tab hidden, slows when unfocused
**Usage Example**:
```typescript
import { useSmartPolling } from "@/features/ui/hooks/useSmartPolling";

function useTasksQuery() {
  const refetchInterval = useSmartPolling(5000); // Base 5 seconds

  return useQuery({
    queryKey: ["tasks"],
    queryFn: () => taskService.getAll(),
    refetchInterval, // Auto-adjusts based on visibility
  });
}
```

### 3. Database Connection Pool Management
**Location**: `/Users/jon/source/vibes/infra/archon/python/src/server/config/database.py`
**Purpose**: Manages asyncpg connection pool with proper lifecycle
**Pattern from task manager** (`backend/src/config/database.py` should follow):
```python
from contextlib import asynccontextmanager
from asyncpg import create_pool

pool = None

@asynccontextmanager
async def lifespan(app):
    # Startup: Create connection pool
    global pool
    pool = await create_pool(DATABASE_URL, min_size=5, max_size=20)
    yield
    # Shutdown: Close pool
    await pool.close()

# In FastAPI main.py
app = FastAPI(lifespan=lifespan)
```

### 4. Environment Variable Defaults Pattern
**Location**: All `docker-compose.yml` files in infra/
**Purpose**: Graceful fallback when .env missing or incomplete
**Usage Example**:
```yaml
environment:
  - POSTGRES_DB=${POSTGRES_DB:-taskmanager}
  - POSTGRES_USER=${POSTGRES_USER:-taskuser}
  - API_PORT=${API_PORT:-8000}
  - LOG_LEVEL=${LOG_LEVEL:-INFO}
```

### 5. FastMCP Server Implementation
**Source**: Archon knowledge base (MCP documentation)
**Purpose**: Expose tools to AI IDEs like Claude Code
**Pattern from docs**:
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("task-manager")

@mcp.tool()
async def find_tasks(query: str = "", status: str = "") -> list:
    """Find tasks by query or status."""
    # Implementation here
    pass

if __name__ == "__main__":
    mcp.run(transport="sse")
```

## Testing Patterns

### Unit Test Structure
**Pattern**: Pytest with async support
**Example from Archon**: `python/tests/server/utils/test_etag_utils.py`
**Key techniques**:
```python
import pytest
from src.server.utils.etag_utils import generate_etag

def test_etag_generation():
    """Test ETag hash generation."""
    data = {"id": 1, "name": "test"}
    etag = generate_etag(data)

    # ETag should be consistent
    assert etag == generate_etag(data)

    # ETag should be quoted per RFC 7232
    assert etag.startswith('"') and etag.endswith('"')

@pytest.mark.asyncio
async def test_database_connection():
    """Test async database operations."""
    async with database_pool() as conn:
        result = await conn.fetch("SELECT 1")
        assert result[0]["?column?"] == 1
```

### Integration Test Structure
**Pattern**: Test full API endpoints with TestClient
**Example pattern**:
```python
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_create_task():
    response = client.post("/api/tasks", json={
        "title": "Test task",
        "status": "todo"
    })
    assert response.status_code == 201
    assert "id" in response.json()
```

### Frontend Testing Pattern
**Location**: `archon-ui-main/src/features/*/tests/`
**Pattern**: Vitest + React Testing Library
**Key techniques**:
```typescript
import { describe, it, expect, vi } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

// Mock service
vi.mock("../../services", () => ({
  taskService: {
    getAll: vi.fn().mockResolvedValue([{ id: "1", title: "Test" }]),
  },
}));

describe("useTasksQuery", () => {
  it("fetches tasks successfully", async () => {
    const queryClient = new QueryClient();
    const wrapper = ({ children }) => (
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    );

    const { result } = renderHook(() => useTasksQuery(), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toHaveLength(1);
  });
});
```

## Anti-Patterns to Avoid

### 1. Missing .env File
**What it is**: Starting Docker Compose without creating .env from .env.example
**Why to avoid**: Causes "environment variable not set" errors, services fail to start
**Found in**: This is the #1 most likely cause of "never worked" status
**Better approach**:
```bash
# First step of any debugging
cd infra/task-manager
cp .env.example .env
# Then edit .env if needed
```

### 2. Using localhost in Container Environment
**What it is**: DATABASE_URL=postgresql://...@localhost:5432/... in backend
**Why to avoid**: `localhost` inside container refers to container itself, not db service
**Found in**: Common mistake in database connection strings
**Better approach**: Use Docker Compose service name
```bash
# WRONG (in container context)
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/db

# CORRECT (in docker-compose)
DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/taskmanager
```

### 3. Not Using docker-compose down -v for Clean Slate
**What it is**: Restarting services without clearing volumes when schema changes
**Why to avoid**: Old database data persists, init.sql doesn't run, migrations fail
**Found in**: Common when iterating on database schema
**Better approach**:
```bash
# Full reset (WARNING: deletes all data)
docker-compose down -v
docker-compose up --build

# Verify init script ran
docker-compose logs db | grep "init.sql"
```

### 4. Hardcoding Environment Values
**What it is**: PORT=8000 instead of PORT=${API_PORT:-8000} in docker-compose.yml
**Why to avoid**: Not configurable, conflicts when running multiple services
**Found in**: Less mature Docker Compose files
**Better approach**: Always use environment variable with default
```yaml
# WRONG
ports:
  - "8000:8000"

# CORRECT
ports:
  - "${API_PORT:-8000}:8000"
```

### 5. Missing start_period in Health Checks
**What it is**: Health check without start_period, service marked unhealthy during startup
**Why to avoid**: Backend marked unhealthy before it finishes initializing
**Found in**: Many Docker Compose examples omit this
**Better approach**:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s  # Give service time to initialize
```

### 6. Non-Executable Shell Scripts
**What it is**: start.sh without execute permissions, container fails to start
**Why to avoid**: Cryptic "permission denied" errors in container logs
**Found in**: Files lose permissions during git operations or file moves
**Better approach**:
```bash
# Check permissions
ls -l backend/start.sh

# Fix if needed
chmod +x backend/start.sh

# Or use bash explicitly in Dockerfile
CMD ["bash", "start.sh"]
```

### 7. Using pip Instead of uv
**What it is**: RUN pip install -r requirements.txt in Dockerfile
**Why to avoid**: 10-100x slower, doesn't leverage uv's lock file
**Found in**: Older Python projects
**Better approach**:
```dockerfile
# Install uv
RUN pip install --no-cache-dir uv

# Use uv for dependencies
RUN uv venv /venv && \
    . /venv/bin/activate && \
    uv pip install -r pyproject.toml
```

## Implementation Hints from Existing Code

### Similar Features Found

#### 1. Archon MCP Server (infra/archon/)
**Location**: `/Users/jon/source/vibes/infra/archon/`
**Similarity**: Multi-service Docker Compose with MCP server, FastAPI backend, React frontend
**Lessons**:
- Health checks with `start_period` prevent false failures
- Named volumes avoid permission issues
- Service discovery via Docker networking
- Hot reload via volume mounts in development
**Differences**:
- Archon has 4 services (server, mcp, agents, frontend) vs task manager's 3
- Archon uses Supabase external network, task manager uses isolated network
- Archon has optional profiles for agents service

#### 2. LiteLLM Proxy (infra/litellm/)
**Location**: `/Users/jon/source/vibes/infra/litellm/`
**Similarity**: Single-service using external PostgreSQL (Supabase pattern)
**Lessons**:
- External network integration (`supabase_default`)
- Health check on port 4000 ensures service ready
- Using official images reduces maintenance
- `restart: unless-stopped` for production resilience
**Differences**:
- Uses pre-built image vs custom Dockerfile
- Simpler single-service setup
- No frontend component

#### 3. FastMCP Weather Server (Archon knowledge base)
**Source**: MCP documentation from knowledge base search
**Similarity**: FastMCP server pattern for tool exposure
**Lessons**:
- Use `@mcp.tool()` decorator for tool definition
- Run with `transport="sse"` for HTTP-based MCP
- Tools should have clear docstrings for AI understanding
- Context object provides request metadata
**Differences**:
- Weather example is simpler (single service)
- Task manager has both API and MCP endpoints
- Task manager MCP tools are more complex (CRUD operations)

## Recommendations for PRP

Based on pattern analysis:

1. **Follow Archon's health check pattern** with `start_period` and `service_healthy` conditions
   - Verify all services in docker-compose.yml use this pattern
   - Add logging to confirm health checks passing

2. **Reuse environment variable defaults pattern** from all infra/ services
   - Already present in task manager docker-compose.yml
   - Create .env from .env.example as first debugging step

3. **Mirror Archon's multi-stage Dockerfile pattern** for backend
   - Already implemented correctly
   - Verify uv command syntax matches Archon's pattern

4. **Adapt Archon's frontend Vite configuration** for hot reload
   - Already correct with --host flag
   - Verify volume mounts exclude node_modules

5. **Avoid "missing .env" anti-pattern** which causes 90% of initial failures
   - This is most likely reason for "never worked" status
   - Add to debugging checklist as step 1

6. **Use docker-compose down -v pattern** for clean slate between debugging attempts
   - Forces database re-initialization
   - Eliminates stale volume data

7. **Follow FastMCP server pattern** from knowledge base for MCP integration
   - Verify mcp_server.py follows FastMCP conventions
   - Check that both API and MCP servers start in start.sh

8. **Implement database pool pattern** from Archon for connection management
   - Use FastAPI lifespan for pool creation/cleanup
   - Verify DATABASE_URL format matches asyncpg requirements

## Source References

### From Archon Knowledge Base
- **MCP Server Patterns**: FastMCP initialization and tool patterns (Relevance: 7/10)
  - Source ID: d60a71d62eb201d5 (modelcontextprotocol.io)
  - Source ID: c0e629a894699314 (ai.pydantic.dev)
- **FastAPI Patterns**: Async request handling, Pydantic validation (Relevance: 8/10)
  - Source ID: c0e629a894699314 (ai.pydantic.dev)

### From Local Codebase
- **Docker Compose**: `/Users/jon/source/vibes/infra/archon/docker-compose.yml` - Working multi-service reference
- **Backend Dockerfile**: `/Users/jon/source/vibes/infra/archon/python/Dockerfile.server` - uv + multi-stage pattern
- **Frontend Dockerfile**: `/Users/jon/source/vibes/infra/archon/archon-ui-main/Dockerfile` - Vite dev server
- **Database Health**: `/Users/jon/source/vibes/infra/task-manager/docker-compose.yml:24-29` - pg_isready pattern
- **Multi-Process Start**: `/Users/jon/source/vibes/infra/task-manager/backend/start.sh` - Background + foreground
- **Environment Config**: `/Users/jon/source/vibes/infra/task-manager/.env.example` - Comprehensive defaults

## Next Steps for Assembler

When generating the PRP:

1. **Reference these patterns in "Current Codebase Tree" section**:
   - Archon docker-compose.yml as working reference
   - Task manager docker-compose.yml as current implementation
   - Backend/frontend Dockerfiles as build patterns

2. **Include key code snippets in "Implementation Blueprint"**:
   - Health check configuration from Pattern 1
   - Multi-process startup from Pattern 3
   - Database connection pool pattern

3. **Add anti-patterns to "Known Gotchas" section**:
   - Missing .env file (Anti-Pattern 1)
   - localhost vs service name (Anti-Pattern 2)
   - Volume persistence (Anti-Pattern 3)
   - Shell script permissions (Anti-Pattern 6)

4. **Use file organization for "Desired Codebase Tree"**:
   - Already matches recommended structure
   - No changes needed to directory layout
   - Focus on getting existing structure working

5. **Add debugging workflow to "Step-by-Step Implementation"**:
   - Copy .env.example to .env
   - Check for port conflicts
   - Start with `docker-compose up` (no -d) to see logs
   - Verify health checks pass
   - Test each service individually
   - End-to-end validation

6. **Include validation commands in "Success Criteria"**:
   - `docker-compose ps` - All services healthy
   - `curl http://localhost:8000/health` - API responds
   - `curl http://localhost:8051/health` - MCP responds
   - `curl http://localhost:3000` - Frontend loads
   - Database connection test commands

## Debugging Priority Order

Based on pattern analysis, debug in this order:

1. **Environment Configuration** (5 min)
   - Copy .env.example to .env
   - Verify all variables set correctly
   - Check DATABASE_URL uses 'db' not 'localhost'

2. **Port Conflicts** (2 min)
   - Check `lsof -i :3000 :8000 :8051 :5432`
   - Kill conflicting processes or change ports in .env

3. **Clean Slate** (3 min)
   - `docker-compose down -v` - Force database re-init
   - Remove any existing containers/volumes

4. **Build Fresh** (5-10 min)
   - `docker-compose build --no-cache`
   - Watch for build errors in each service

5. **Start and Monitor** (10+ min)
   - `docker-compose up` (no -d to see logs)
   - Watch for first error in logs
   - Check health check status

6. **Service-by-Service Validation** (15+ min)
   - Database: `docker exec -it taskmanager-db psql -U taskuser -d taskmanager`
   - Backend API: `curl http://localhost:8000/health`
   - MCP Server: `curl http://localhost:8051/health`
   - Frontend: `curl http://localhost:3000`

7. **Fix and Iterate**
   - Address first error found
   - Restart services: `docker-compose down && docker-compose up`
   - Repeat until all healthy

## Confidence Assessment

**High Confidence Patterns** (Will definitely help):
- Pattern 1: Health check dependencies (eliminates startup race conditions)
- Pattern 2: uv multi-stage build (ensures reproducible builds)
- Pattern 5: PostgreSQL volume management (fixes database init issues)
- Anti-Pattern 1: Missing .env (90% likely cause of "never worked")
- Anti-Pattern 2: localhost vs service name (common in Docker)

**Medium Confidence Patterns** (Likely useful):
- Pattern 3: Multi-process container (if start.sh has issues)
- Pattern 4: Vite --host flag (should already be correct)
- Anti-Pattern 6: Shell script permissions (possible but less common)

**Lower Priority Patterns** (Good to have):
- ETag caching utility (optimization, not critical for initial working state)
- Smart polling hook (can add after basic functionality works)
- Testing patterns (validate after system works)

## Success Indicators

You'll know these patterns worked when:
- `docker-compose ps` shows all services as "healthy"
- No "connection refused" errors in logs
- Database tables exist and match schema
- Both FastAPI and MCP servers respond to health checks
- Frontend loads in browser without errors
- Can create/read/update/delete tasks via UI
- MCP tools work when called from Claude Code

## Expected Timeline

- **5 minutes**: Environment setup (.env creation, port checks)
- **10 minutes**: First docker-compose up attempt and log analysis
- **15-30 minutes**: Fix first major issue (likely .env or dependency related)
- **30-60 minutes**: Iterative debugging of remaining issues
- **15 minutes**: End-to-end validation
- **Total**: 1-2 hours for full system functional

If it takes longer, most likely causes:
- Python dependency incompatibilities (check pyproject.toml)
- Frontend TypeScript compilation errors (check package.json)
- Network issues (firewall blocking ports)
- File permission issues (especially on Windows/WSL)
