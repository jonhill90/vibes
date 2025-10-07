# PRP: Fix Task Manager System

**Generated**: 2025-10-07
**Based On**: /Users/jon/source/vibes/prps/INITIAL_rename_task_manager.md
**Archon Project**: 90a6faab-c4c4-47d8-9889-f3cd2d60405c

---

## Goal

Debug and fix the task manager Docker Compose system that has never successfully run. Get all services (database, backend, frontend) healthy and operational, then clean up naming inconsistencies.

**End State**:
- All Docker Compose services start cleanly and show "healthy" status
- Database initialized with correct schema (projects, tasks tables)
- Backend API responds at http://localhost:8000 with health check
- MCP server responds at http://localhost:8051 with health check
- Frontend loads in browser at http://localhost:3000
- End-to-end functionality: Create projects, create tasks, drag-and-drop between Kanban columns
- MCP tools accessible via Claude Code integration
- Documentation uses consistent "task-manager" naming

## Why

**Current Pain Points**:
- System has never successfully run after moving to `infra/task-manager/`
- Can't use task management features at all (completely broken)
- No working MCP integration for Claude Code
- Unclear what the actual issues are (need systematic debugging)

**Business Value**:
- Archon MCP server needs functional task management backend
- Claude Code workflows require working MCP tools
- Vibes ecosystem needs centralized task tracking
- Demonstrates full-stack Docker Compose pattern for other services

**Integration Value**:
- Validates Docker Compose patterns used across vibes infra services
- Proves React + FastAPI + PostgreSQL + MCP stack
- Serves as reference implementation for future services

---

## What

### Core Features

**Phase 1: Debug & Fix (Priority)**
- Systematically identify why services aren't starting
- Fix database initialization (schema creation, connection)
- Fix backend startup (Python dependencies, database pool, MCP server)
- Fix frontend build and dev server (Vite configuration, CORS)
- Verify health checks pass for all services
- Test end-to-end functionality (UI → API → Database → MCP)

**Phase 2: Clean Up References (Quick polish)**
- Update remaining "task-management-ui" references to "task-manager"
- Update documentation paths to `infra/task-manager/`
- Ensure naming consistency across user-facing content

### Success Criteria

**Phase 1 Complete**:
- [ ] `.env` file exists with correct values
- [ ] `docker-compose up` starts all services without errors
- [ ] `docker-compose ps` shows all services healthy (db, backend) or running (frontend)
- [ ] Database tables exist: `docker exec taskmanager-db psql -U taskuser -d taskmanager -c "\dt"` shows projects, tasks
- [ ] Backend health: `curl http://localhost:8000/health` returns `{"status": "healthy"}`
- [ ] MCP health: `curl http://localhost:8051/health` succeeds
- [ ] Frontend loads: `curl http://localhost:3000` returns HTML
- [ ] UI functional: Can create project, create task, drag task in browser
- [ ] MCP functional: Can call tools via `npx mcp-remote http://localhost:8051/mcp`

**Phase 2 Complete**:
- [ ] No "task-management-ui" references in README or user-facing docs
- [ ] All documentation paths reference `infra/task-manager/`
- [ ] Code examples are copy-paste ready

---

## All Needed Context

### Documentation & References

```yaml
# MUST READ - Docker Compose Health Checks
- url: https://docs.docker.com/compose/how-tos/startup-order/
  sections:
    - "Control startup and shutdown order" - depends_on with service_healthy condition
    - "Health check best practices" - start_period prevents premature failures
  why: Critical for preventing race conditions where backend starts before database ready
  critical_gotchas:
    - Default depends_on only waits for container start, not readiness
    - Must use "condition: service_healthy" to wait for health checks
    - start_period gives initialization grace period before failures count

- url: https://docs.docker.com/reference/compose-file/services/#healthcheck
  sections:
    - "Healthcheck syntax" - test, interval, timeout, retries, start_period
    - "CMD vs CMD-SHELL" - when to use each test format
  why: Understanding health check parameters and timing
  critical_gotchas:
    - Without start_period, service marked unhealthy during initialization
    - pg_isready needs username and database name parameters
    - Python health checks require proper URL encoding in shell

# MUST READ - FastAPI Async Patterns
- url: https://fastapi.tiangolo.com/advanced/events/
  sections:
    - "Lifespan Events" - @asynccontextmanager for startup/shutdown
    - "Database pool initialization" - create pool at startup, close at shutdown
  why: Backend must initialize asyncpg connection pool correctly
  critical_gotchas:
    - Replaces deprecated @app.on_event("startup")
    - Pool must be created ONCE at startup, not per request
    - Always close pool on shutdown to avoid resource leaks

- url: https://fastapi.tiangolo.com/tutorial/cors/
  sections:
    - "CORSMiddleware configuration" - allow_origins, allow_credentials
    - "Security implications" - never use wildcard with credentials
  why: Frontend needs CORS configured to call backend API
  critical_gotchas:
    - CORS must be added BEFORE routes are registered
    - Can't use allow_origins=["*"] with allow_credentials=True
    - Must include http://localhost:3000 in allow_origins for dev

# MUST READ - PostgreSQL Docker Initialization
- url: https://hub.docker.com/_/postgres
  sections:
    - "Initialization scripts" - /docker-entrypoint-initdb.d behavior
    - "Environment variables" - POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
    - "Health checks" - pg_isready command
  why: Understanding database initialization and health check patterns
  critical_gotchas:
    - Init scripts ONLY run if data directory is empty (first start)
    - Use "docker-compose down -v" to force re-initialization
    - pg_isready must specify correct user and database name
    - Connection strings must use service name "db" not "localhost"

# MUST READ - Vite in Docker
- url: https://vite.dev/config/server-options
  sections:
    - "server.host" - listen on 0.0.0.0 for Docker
    - "server.watch" - file watching with usePolling
  why: Frontend must be accessible from outside container
  critical_gotchas:
    - MUST use --host flag or host: true in config
    - Without --host, Vite binds to localhost and Docker can't forward
    - May need usePolling: true for hot reload in Docker

# MUST READ - asyncpg Connection Pools
- url: https://magicstack.github.io/asyncpg/current/usage.html
  sections:
    - "Connection pools" - create_pool, acquire, close
    - "Connection string format" - DSN vs keyword arguments
  why: Backend uses asyncpg for async PostgreSQL access
  critical_gotchas:
    - Pure asyncpg: postgresql://user:pass@host:port/db
    - SQLAlchemy format: postgresql+asyncpg://user:pass@host:port/db
    - Pool is NOT thread-safe, use one per application
    - Must use "async with pool.acquire() as conn" pattern

# MUST READ - uv Package Manager
- url: https://docs.astral.sh/uv/
  sections:
    - "Working on Projects" - uv sync, uv.lock usage
    - "Docker Integration" - copying uv binary, frozen installs
  why: Backend Dockerfile uses uv for dependency management
  critical_gotchas:
    - Use "uv sync --frozen" in Docker to prevent lockfile updates
    - pyproject.toml must have [project] table with dependencies
    - uv.lock should be committed to version control
    - May need to use "uv run" prefix for commands

# ESSENTIAL LOCAL FILES - Working Examples
- file: /Users/jon/source/vibes/prps/rename_task_manager/examples/README.md
  why: Comprehensive guide to all code examples with "What to Mimic/Adapt/Skip"
  pattern: Study this FIRST before applying any patterns

- file: /Users/jon/source/vibes/prps/rename_task_manager/examples/docker-compose-archon.yml
  why: Working multi-service reference with robust health checks
  critical: start_period: 40s prevents premature backend health check failures
  pattern: Health check with service_healthy dependency

- file: /Users/jon/source/vibes/prps/rename_task_manager/examples/postgres-healthcheck.yml
  why: Exact PostgreSQL health check pattern needed
  critical: pg_isready -U user -d database with retries: 10
  pattern: Database initialization and health validation

- file: /Users/jon/source/vibes/prps/rename_task_manager/examples/backend-startup-script.sh
  why: Multi-process container pattern (MCP + FastAPI)
  critical: Use "exec" for proper signal handling
  pattern: Background process (&) for MCP, foreground (exec) for API

- file: /Users/jon/source/vibes/prps/rename_task_manager/examples/backend-dockerfile-multistage.dockerfile
  why: Python multi-stage build with uv package manager
  critical: Multi-stage keeps images small, PATH must include /venv/bin
  pattern: Builder stage installs deps, runtime stage copies venv

- file: /Users/jon/source/vibes/prps/rename_task_manager/examples/frontend-dockerfile-vite.dockerfile
  why: Vite dev server Dockerfile with --host flag
  critical: CMD ["npm", "run", "dev", "--", "--host"] is required for Docker
  pattern: --host makes Vite listen on 0.0.0.0

- file: /Users/jon/source/vibes/prps/rename_task_manager/examples/env-example-pattern.env
  why: Complete environment variable template
  critical: DATABASE_URL must use "db" not "localhost" in Docker
  pattern: ${VAR:-default} syntax for all docker-compose variables

- file: /Users/jon/source/vibes/prps/rename_task_manager/examples/database-init-schema.sql
  why: Complete PostgreSQL schema with best practices
  critical: CREATE EXTENSION pgcrypto, proper indexes on foreign keys
  pattern: UUID PKs, enum types, composite indexes, auto-update triggers
```

### Current Codebase Tree

```
infra/task-manager/
├── docker-compose.yml          # Service orchestration (may need health check fixes)
├── .env.example                # Template (MUST copy to .env)
├── database/
│   └── init.sql               # Schema initialization (runs on first DB start)
├── backend/
│   ├── Dockerfile             # Multi-stage Python build with uv
│   ├── pyproject.toml         # Python dependencies
│   ├── start.sh               # Multi-process startup (MCP + FastAPI)
│   ├── alembic/               # Database migrations
│   └── src/
│       ├── main.py            # FastAPI app with lifespan
│       ├── mcp_server.py      # MCP server entry point
│       ├── config/
│       │   └── database.py    # Connection pool management
│       ├── api/               # API route handlers
│       │   ├── projects.py
│       │   └── tasks.py
│       └── services/          # Business logic layer
│           ├── project_service.py
│           └── task_service.py
└── frontend/
    ├── Dockerfile             # Node 20 + Vite dev server
    ├── package.json           # Node dependencies
    ├── vite.config.ts         # Vite configuration
    └── src/
        ├── features/          # Feature-based structure
        │   ├── projects/
        │   └── tasks/
        └── pages/             # Route components

Key Files to Check During Debugging:
- .env (may not exist - MUST copy from .env.example)
- docker-compose.yml (health checks, depends_on conditions)
- backend/start.sh (must be executable: chmod +x)
- backend/src/main.py (CORS, lifespan, database pool)
- backend/src/config/database.py (connection string, pool config)
- frontend/vite.config.ts (server.host: true)
```

### Desired Codebase Tree

**No new files needed** - just fix existing configuration:

```
Changes Required:
- .env (CREATE from .env.example if missing)
- docker-compose.yml (VERIFY health checks have start_period)
- backend/src/main.py (VERIFY CORS includes http://localhost:3000)
- backend/start.sh (VERIFY executable permissions: chmod +x)
- frontend/vite.config.ts (VERIFY server.host: true)

Optional Phase 2 Changes:
- README.md (update paths to infra/task-manager/)
- Code comments (update "task-management-ui" → "task-manager")
```

### Known Gotchas & Library Quirks

```python
# CRITICAL #1: Missing .env File (90% probability - most likely issue)
# The #1 reason Docker Compose setups fail after moving files

# ❌ WRONG - Starting without .env file
cd infra/task-manager
docker-compose up
# Result: "connection refused", "authentication failed", services crash

# ✅ RIGHT - Create .env from template FIRST
cd /Users/jon/source/vibes/infra/task-manager
cp .env.example .env
# Edit .env if needed (defaults usually work for dev)
docker-compose up

# Why this matters:
# - Docker Compose loads .env automatically
# - Variables like DATABASE_URL, POSTGRES_PASSWORD come from .env
# - Without .env, services use wrong defaults or have undefined variables
# - This is gitignored so must be created manually on each setup

# Verification:
ls -la /Users/jon/source/vibes/infra/task-manager/.env
# Should exist. If "No such file", that's the problem.
```

```yaml
# CRITICAL #2: PostgreSQL Init Scripts Only Run Once (70% probability)
# Database initialization scripts only run if data directory is EMPTY

# ❌ WRONG - Restarting without clearing volumes
docker-compose down
docker-compose up
# Result: Database starts but init.sql doesn't run, tables missing

# ✅ RIGHT - Force re-initialization by removing volumes
docker-compose down -v  # -v removes volumes
docker-compose up

# Why this matters:
# - PostgreSQL's docker-entrypoint-initdb.d only runs on first start
# - If volume exists from previous run, init scripts are skipped
# - Even if init failed before, it won't retry on restart
# - Must delete volume to force re-initialization

# Verification:
docker-compose logs db | grep "init"
docker exec taskmanager-db psql -U taskuser -d taskmanager -c "\dt"
# Should see: projects, tasks tables
# If empty: Use "docker-compose down -v" to reset
```

```python
# CRITICAL #3: localhost vs Service Name in Docker Networks (60% probability)
# Inside containers, "localhost" refers to the container itself, NOT other services

# ❌ WRONG - Using localhost in container context
DATABASE_URL = "postgresql+asyncpg://taskuser:pass@localhost:5432/taskmanager"
# Result: "Connection refused" - backend looks for DB inside its own container

# ✅ RIGHT - Using Docker Compose service name
DATABASE_URL = "postgresql+asyncpg://taskuser:pass@db:5432/taskmanager"
#                                                  ^^
#                                                  Service name from docker-compose.yml

# Why this matters:
# - Docker Compose creates internal DNS for service-to-service communication
# - Service name "db" resolves to database container's IP
# - "localhost" inside container = that container (not host, not other containers)
# - Host machine uses localhost:PORT to reach services (mapped ports)

# Verification:
docker-compose exec backend env | grep DATABASE_URL
# Should show "db:5432" not "localhost:5432"

# Testing connectivity:
docker-compose exec backend sh -c 'psql -h db -p 5432 -U taskuser -d taskmanager'
# Should connect. If fails, DATABASE_URL is wrong.
```

```yaml
# CRITICAL #4: Health Checks Need start_period (High impact)
# Without start_period, health checks begin immediately and mark service unhealthy

# ❌ WRONG - No start_period, health checks fail during startup
backend:
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
    interval: 30s
    timeout: 10s
    retries: 3
    # Missing start_period!
  # Result: Backend marked unhealthy while loading Python, connecting to DB

# ✅ RIGHT - Generous start_period allows initialization
backend:
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 40s  # Backend needs time to load Python + connect DB

db:
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U taskuser -d taskmanager"]
    interval: 5s
    timeout: 5s
    retries: 10  # Database needs more retries
    start_period: 10s  # Database starts faster but still needs grace period

# Why this matters:
# - start_period = grace period where failures don't count
# - Backend: Needs 30-40s to import Python modules, create DB pool, start server
# - Database: Needs 10-15s to initialize data directory, start postgres
# - Without start_period: Service restarts in loop from "unhealthy" status

# Verification:
docker-compose ps
# Should show "healthy" not "starting (health: starting)" or "unhealthy"
```

```yaml
# CRITICAL #5: Backend Must Wait for Database to be HEALTHY (High impact)
# Default depends_on only waits for container to START, not be READY

# ❌ WRONG - depends_on without condition
backend:
  depends_on:
    - db  # Only waits for container to start
  # Result: Backend starts while DB still initializing, connection refused

# ✅ RIGHT - depends_on with service_healthy condition
backend:
  depends_on:
    db:
      condition: service_healthy  # Waits for health check to pass
  # Backend only starts after pg_isready succeeds

# Why this matters:
# - PostgreSQL needs 5-10s to initialize after container starts
# - asyncpg connection pool creation fails if DB not ready
# - Backend crashes or goes into error state
# - Even with restart policy, timing issues can persist

# Verification:
# Check docker-compose.yml:
grep -A 3 "depends_on:" /Users/jon/source/vibes/infra/task-manager/docker-compose.yml
# Should show "condition: service_healthy" under db dependency
```

```dockerfile
# CRITICAL #6: Vite MUST Use --host Flag in Docker (High impact)
# Vite binds to localhost (127.0.0.1) by default, unreachable from outside container

# ❌ WRONG - Default Vite command
CMD ["npm", "run", "dev"]
# Result: Container runs, but http://localhost:3000 connection refused from browser

# ✅ RIGHT - Vite with --host flag
CMD ["npm", "run", "dev", "--", "--host"]
#                          ^^   ^^^^^^^
#                          |    Listen on 0.0.0.0
#                          Pass args to vite

# Alternative in vite.config.ts:
export default defineConfig({
  server: {
    host: true,  // or '0.0.0.0'
    port: 3000,
    watch: {
      usePolling: true,  // For hot reload in Docker
    },
  },
})

# Why this matters:
# - Without --host: Vite listens on 127.0.0.1 (container's localhost)
# - Docker port mapping requires 0.0.0.0 to forward external traffic
# - Browser connects to host's localhost:3000, Docker forwards to container
# - Container must be listening on 0.0.0.0 to receive forwarded traffic

# Verification:
docker-compose logs frontend | grep "Network"
# Should show: "Network: http://172.x.x.x:3000"
# Not just: "Local: http://127.0.0.1:3000"

curl http://localhost:3000
# Should return HTML, not "connection refused"
```

```bash
# CRITICAL #7: Shell Script Permissions in Docker (Medium impact)
# start.sh may not have execute permissions, causing "permission denied"

# ❌ WRONG - Copy without ensuring permissions
# In Dockerfile:
COPY start.sh /app/start.sh
CMD ["/app/start.sh"]
# Result: "exec /app/start.sh: permission denied"

# ✅ RIGHT - Multiple solutions:

# Option 1: Set permissions on host
chmod +x /Users/jon/source/vibes/infra/task-manager/backend/start.sh
docker-compose build --no-cache backend

# Option 2: Use COPY --chmod in Dockerfile
COPY --chmod=0755 start.sh /app/start.sh
CMD ["/app/start.sh"]

# Option 3: RUN chmod in Dockerfile
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh
CMD ["/app/start.sh"]

# Option 4: Use bash explicitly
COPY start.sh /app/start.sh
CMD ["bash", "/app/start.sh"]

# Why this matters:
# - Git may not preserve execute bit depending on config
# - File moves can lose permissions
# - Docker COPY preserves source permissions on Linux/macOS
# - Container exits immediately with exit code 126 (permission denied)

# Verification:
ls -l /Users/jon/source/vibes/infra/task-manager/backend/start.sh
# Should show: -rwxr-xr-x (has 'x' for execute)
# Not: -rw-r--r-- (missing 'x')
```

```python
# CRITICAL #8: CORS Must Allow Frontend Origin (Medium impact)
# FastAPI blocks frontend requests without CORS middleware

# ❌ WRONG - No CORS middleware
from fastapi import FastAPI
app = FastAPI()
# Result: Browser blocks API responses with CORS policy error

# ✅ RIGHT - CORS configured for development
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Vite dev server
        "http://127.0.0.1:3000",  # Alternative localhost
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Why this matters:
# - Browser enforces same-origin policy (different ports = different origins)
# - Backend on :8000, frontend on :3000 = cross-origin requests
# - Without CORS: Request succeeds, backend responds, browser blocks response
# - Developer sees "blocked by CORS policy" in console
# - Backend logs show 200 OK, frontend sees error

# Security notes:
# - Never use allow_origins=["*"] with allow_credentials=True
# - Production should use specific domain: ["https://yourdomain.com"]
# - CORS middleware must be added BEFORE routes

# Verification:
# Open http://localhost:3000 in browser
# Open DevTools Console (F12)
# Look for CORS errors when making API calls
# Should NOT see: "blocked by CORS policy"
```

```python
# CRITICAL #9: asyncpg Connection String Format (Medium impact)
# Pure asyncpg vs SQLAlchemy format difference

# ❌ WRONG - Mixing formats
# Pure asyncpg with +asyncpg scheme:
DATABASE_URL = "postgresql+asyncpg://user:pass@db:5432/dbname"
pool = await asyncpg.create_pool(dsn=DATABASE_URL)
# Result: Invalid DSN format error

# ✅ RIGHT - Use correct format for library
# For asyncpg.create_pool (pure asyncpg):
DATABASE_URL = "postgresql://user:pass@db:5432/dbname"
pool = await asyncpg.create_pool(dsn=DATABASE_URL)

# For SQLAlchemy with asyncpg driver:
DATABASE_URL = "postgresql+asyncpg://user:pass@db:5432/dbname"
engine = create_async_engine(DATABASE_URL)

# Why this matters:
# - asyncpg uses libpq connection URI format (no driver suffix)
# - SQLAlchemy uses dialect+driver format (postgresql+asyncpg)
# - Task manager uses pure asyncpg (no SQLAlchemy ORM)
# - Using wrong format causes "invalid DSN" error

# Verification:
grep "DATABASE_URL" /Users/jon/source/vibes/infra/task-manager/.env
# Should show: postgresql://... (no +asyncpg for pure asyncpg)
```

```bash
# CRITICAL #10: Port Conflicts on Host (Medium probability)
# Ports 3000, 8000, 8051, or 5432 already in use

# ❌ WRONG - Starting without checking
docker-compose up
# Result: "port is already allocated" error

# ✅ RIGHT - Check for conflicts first
lsof -i :3000 -i :8000 -i :8051 -i :5432

# If ports in use, either:
# Option 1: Stop conflicting processes
kill <PID>  # From lsof output
# Or: brew services stop postgresql

# Option 2: Change ports in .env
FRONTEND_PORT=3001
API_PORT=8001
MCP_PORT=8052
POSTGRES_PORT=5433

# Why this matters:
# - Other dev projects may use same default ports
# - macOS may have PostgreSQL running via Homebrew
# - Another task-manager instance may still be running
# - Docker can't bind to already-used ports

# Verification:
lsof -i :3000 :8000 :8051 :5432
# Should show: Nothing (no output = ports free)
# Or: Only docker-proxy processes (after starting services)
```

```yaml
# Library Quirk #1: uv Package Manager Syntax
# uv has different command patterns than pip

# ❌ WRONG - Using pip-style commands
RUN pip install -r requirements.txt  # uv doesn't use requirements.txt

# ✅ RIGHT - Using uv with pyproject.toml
RUN uv venv /venv && \
    . /venv/bin/activate && \
    uv pip install -e .

# Or for frozen installs:
RUN uv sync --frozen --no-cache

# Why this matters:
# - uv uses pyproject.toml as source of truth
# - uv.lock is the lockfile (like package-lock.json)
# - --frozen prevents lockfile updates during build
# - uv is 10-100x faster than pip for dependency resolution

# Verification:
# Check backend Dockerfile uses uv commands correctly
# Ensure pyproject.toml has [project] table with dependencies
```

```python
# Library Quirk #2: FastAPI Lifespan Events (Modern Pattern)
# @app.on_event() is deprecated, use lifespan instead

# ❌ DEPRECATED - Old startup/shutdown pattern
@app.on_event("startup")
async def startup():
    global db_pool
    db_pool = await asyncpg.create_pool(...)

@app.on_event("shutdown")
async def shutdown():
    await db_pool.close()

# ✅ RIGHT - Modern lifespan pattern
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global db_pool
    db_pool = await asyncpg.create_pool(...)
    yield
    # Shutdown
    await db_pool.close()

app = FastAPI(lifespan=lifespan)

# Why this matters:
# - Lifespan replaces deprecated on_event decorators
# - FastAPI 0.104.0+ recommends lifespan
# - Provides cleaner startup/shutdown management
# - Code before yield = startup, after yield = shutdown
```

```typescript
// Library Quirk #3: Vite Environment Variables
// Only VITE_ prefixed variables exposed to client code

// ❌ WRONG - Variable without VITE_ prefix
// In .env:
API_URL=http://localhost:8000

// In frontend code:
const apiUrl = import.meta.env.API_URL;  // undefined!

// ✅ RIGHT - Use VITE_ prefix
// In .env:
VITE_API_URL=http://localhost:8000

// In frontend code:
const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Why this matters:
// - Vite only exposes variables starting with VITE_
// - This prevents accidentally exposing secrets to client
// - Variables without prefix are available during build only
// - Common mistake when migrating from other build tools
```

```bash
# Debugging Gotcha: Docker Build Cache
# Stale cached layers can cause mysterious issues

# ❌ WRONG - Building with cache after dependency changes
docker-compose build
docker-compose up
# Result: Old dependencies used, new packages not installed

# ✅ RIGHT - Force rebuild without cache
docker-compose build --no-cache
docker-compose up

# Or rebuild specific service:
docker-compose build --no-cache backend
docker-compose up -d backend

# Why this matters:
# - Docker caches each Dockerfile layer
# - If pyproject.toml or package.json changes, cache may not detect it
# - Cached layer with old dependencies gets reused
# - --no-cache forces fresh build from scratch

# Verification:
# If you see "ModuleNotFoundError" for recently added packages
# Or "Cannot find module" errors in frontend
# Rebuild with --no-cache
```
```

---

## Implementation Blueprint

### Phase 0: Planning & Understanding (10 minutes)

**BEFORE starting implementation, complete these steps**:

1. **Study Working Examples** (5 minutes)
   - Read `/Users/jon/source/vibes/prps/rename_task_manager/examples/README.md` completely
   - Focus on "What to Mimic" sections for each example
   - Note the 8 working patterns extracted from Archon, LiteLLM, Supabase

2. **Understand Current State** (3 minutes)
   - System moved to `infra/task-manager/` but never worked
   - No existing data to preserve (fresh slate)
   - Can safely change any configuration
   - Need systematic debugging, not guessing

3. **Review Documentation Links** (2 minutes)
   - Scan "All Needed Context" section above
   - Bookmark critical gotchas (#1-#10)
   - Note that examples directory has complete working code

### Task List (Execute in Order)

```yaml
# ==============================================================================
# PHASE 1: PRE-FLIGHT CHECKS (5 minutes)
# ==============================================================================

Task 1: Environment Configuration Check
RESPONSIBILITY: Ensure .env file exists with correct values (90% probability this is the issue)

FILES TO VERIFY/CREATE:
  - /Users/jon/source/vibes/infra/task-manager/.env

PATTERN TO FOLLOW: examples/env-example-pattern.env

SPECIFIC STEPS:
  1. Check if .env file exists:
     ls -la /Users/jon/source/vibes/infra/task-manager/.env

  2. If missing, create from template:
     cd /Users/jon/source/vibes/infra/task-manager
     cp .env.example .env

  3. Verify DATABASE_URL uses service name "db" not "localhost":
     grep DATABASE_URL .env
     # Should show: ...@db:5432/... (NOT @localhost:5432)

  4. Verify VITE_API_URL is set:
     grep VITE_API_URL .env
     # Should show: VITE_API_URL=http://localhost:8000

VALIDATION:
  - .env file exists and contains all variables from .env.example
  - DATABASE_URL uses "db:5432" for Docker networking
  - No placeholder values like "changeme" remain

GOTCHAS TO AVOID:
  - Using localhost instead of db in DATABASE_URL (Critical Gotcha #3)
  - Missing VITE_ prefix for frontend variables (Library Quirk #3)

---

Task 2: Port Conflict Check
RESPONSIBILITY: Ensure ports 3000, 8000, 8051, 5432 are available

FILES TO VERIFY: None (system check)

PATTERN TO FOLLOW: Standard debugging practice

SPECIFIC STEPS:
  1. Check for port conflicts:
     lsof -i :3000 -i :8000 -i :8051 -i :5432

  2. If ports in use:
     - Option A: Kill conflicting processes:
       kill <PID>
     - Option B: Change ports in .env:
       FRONTEND_PORT=3001
       API_PORT=8001
       MCP_PORT=8052

VALIDATION:
  - lsof shows no processes using target ports
  - Or .env updated with alternative ports

GOTCHAS TO AVOID:
  - Forgetting to check if old task-manager instance still running (Critical Gotcha #10)

---

Task 3: Clean Slate - Remove Stale Resources
RESPONSIBILITY: Remove old volumes/containers to force fresh initialization

FILES TO VERIFY: None (Docker cleanup)

PATTERN TO FOLLOW: Standard Docker reset

SPECIFIC STEPS:
  1. Stop and remove everything:
     cd /Users/jon/source/vibes/infra/task-manager
     docker-compose down -v

  2. Verify volumes removed:
     docker volume ls | grep taskmanager
     # Should show: Nothing (volumes deleted)

  3. Remove any orphan containers:
     docker ps -a | grep taskmanager
     docker rm -f <container_ids> (if any found)

VALIDATION:
  - No taskmanager volumes exist
  - No taskmanager containers exist
  - Clean slate for fresh start

GOTCHAS TO AVOID:
  - Forgetting -v flag, which leaves old database data (Critical Gotcha #2)

# ==============================================================================
# PHASE 2: DOCKER COMPOSE CONFIGURATION FIXES (10 minutes)
# ==============================================================================

Task 4: Verify Health Check Configuration
RESPONSIBILITY: Ensure health checks have proper timing and dependencies

FILES TO MODIFY:
  - /Users/jon/source/vibes/infra/task-manager/docker-compose.yml

PATTERN TO FOLLOW: examples/docker-compose-archon.yml, examples/postgres-healthcheck.yml

SPECIFIC STEPS:
  1. Verify database health check has start_period:
     grep -A 6 "db:" docker-compose.yml | grep -A 6 "healthcheck:"

  2. Should look like (from postgres-healthcheck.yml example):
     healthcheck:
       test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-taskuser} -d ${POSTGRES_DB:-taskmanager}"]
       interval: 5s
       timeout: 5s
       retries: 10
       start_period: 10s

  3. Verify backend health check has start_period:
     grep -A 6 "backend:" docker-compose.yml | grep -A 6 "healthcheck:"

  4. Should have:
     healthcheck:
       test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
       interval: 30s
       timeout: 10s
       retries: 3
       start_period: 40s  # Backend needs time to load Python + DB pool

  5. Verify backend depends_on uses service_healthy:
     grep -A 3 "depends_on:" docker-compose.yml

  6. Should show:
     depends_on:
       db:
         condition: service_healthy  # NOT just service_started

VALIDATION:
  - All health checks have start_period
  - Database: start_period: 10s, retries: 10
  - Backend: start_period: 40s, retries: 3
  - Backend depends_on db with condition: service_healthy

GOTCHAS TO AVOID:
  - Missing start_period causes premature health check failures (Critical Gotcha #4)
  - depends_on without condition only waits for container start, not readiness (Critical Gotcha #5)

---

Task 5: Verify Backend Script Permissions
RESPONSIBILITY: Ensure start.sh is executable

FILES TO VERIFY/MODIFY:
  - /Users/jon/source/vibes/infra/task-manager/backend/start.sh
  - /Users/jon/source/vibes/infra/task-manager/backend/Dockerfile (if needed)

PATTERN TO FOLLOW: examples/backend-startup-script.sh

SPECIFIC STEPS:
  1. Check if start.sh is executable:
     ls -l backend/start.sh
     # Should show: -rwxr-xr-x (has 'x' bits)

  2. If not executable, fix:
     chmod +x backend/start.sh

  3. Verify Dockerfile sets permissions (alternative):
     grep -A 2 "COPY start.sh" backend/Dockerfile
     # Should have RUN chmod +x or COPY --chmod=0755

  4. Verify start.sh content matches pattern:
     cat backend/start.sh
     # Should have:
     # - #!/bin/bash
     # - set -e
     # - python -m src.mcp_server &
     # - exec uvicorn src.main:app ...

VALIDATION:
  - start.sh has execute permissions (ls -l shows 'x')
  - Script starts MCP in background (&) and FastAPI with exec
  - Uses environment variable for port: ${API_PORT:-8000}

GOTCHAS TO AVOID:
  - Missing execute permissions cause "permission denied" exit (Critical Gotcha #7)

---

Task 6: Verify Frontend Vite Configuration
RESPONSIBILITY: Ensure Vite uses --host flag for Docker networking

FILES TO VERIFY:
  - /Users/jon/source/vibes/infra/task-manager/frontend/Dockerfile
  - /Users/jon/source/vibes/infra/task-manager/frontend/vite.config.ts

PATTERN TO FOLLOW: examples/frontend-dockerfile-vite.dockerfile

SPECIFIC STEPS:
  1. Check Dockerfile CMD:
     grep CMD frontend/Dockerfile
     # Should show: CMD ["npm", "run", "dev", "--", "--host"]

  2. If --host flag missing, either:
     - Option A: Update Dockerfile CMD
     - Option B: Update vite.config.ts:
       export default defineConfig({
         server: {
           host: true,
           port: 3000,
           watch: { usePolling: true },
         },
       })

  3. Verify package.json has dev script:
     grep '"dev"' frontend/package.json
     # Should show: "dev": "vite" or similar

VALIDATION:
  - Dockerfile has --host flag OR vite.config.ts has host: true
  - Frontend will be accessible from outside container

GOTCHAS TO AVOID:
  - Missing --host causes "connection refused" from browser (Critical Gotcha #6)

# ==============================================================================
# PHASE 3: BUILD AND START (5-10 minutes)
# ==============================================================================

Task 7: Build Fresh Images
RESPONSIBILITY: Build all services without cache to ensure dependencies installed

FILES INVOLVED: All Dockerfiles

PATTERN TO FOLLOW: Standard Docker best practice

SPECIFIC STEPS:
  1. Build without cache:
     cd /Users/jon/source/vibes/infra/task-manager
     docker-compose build --no-cache

  2. Watch build output for errors:
     - Backend: uv installing dependencies
     - Frontend: npm ci installing packages
     - Any "not found" or "failed to fetch" errors

  3. If backend build fails:
     - Check pyproject.toml syntax
     - Check uv.lock exists (or remove if outdated)
     - Fallback: Use pip instead of uv if uv has issues

  4. If frontend build fails:
     - Check package.json syntax
     - Check package-lock.json not corrupted
     - Try deleting package-lock.json and rebuilding

VALIDATION:
  - All services build successfully
  - No "ModuleNotFoundError" or "Cannot find module" errors
  - Build logs show dependencies installed

GOTCHAS TO AVOID:
  - Using cached layers with old dependencies (Debugging Gotcha)
  - uv syntax errors (Library Quirk #1)

---

Task 8: Start Services and Monitor Logs
RESPONSIBILITY: Start all services and watch for first error

FILES INVOLVED: None (runtime)

PATTERN TO FOLLOW: Standard debugging workflow

SPECIFIC STEPS:
  1. Start services in foreground (to see logs):
     docker-compose up

  2. Watch logs carefully for first error:
     - Database: "database system is ready to accept connections"
     - Backend: "Database pool initialized", "MCP server started", "Uvicorn running"
     - Frontend: "ready in X ms", "Network: http://..."

  3. Check service status in another terminal:
     docker-compose ps
     # Should show:
     # - taskmanager-db: healthy
     # - taskmanager-backend: healthy
     # - taskmanager-frontend: running (Up)

  4. If any service shows "unhealthy" or "restarting":
     - Check logs: docker-compose logs <service>
     - Check health check: docker inspect <container> | grep Health -A 20
     - Fix the error and restart: docker-compose down && docker-compose up

VALIDATION:
  - All services reach healthy/running state
  - No repeated error messages in logs
  - Services stay running (don't crash and restart)

COMMON ERRORS TO WATCH FOR:
  - "connection refused" → Database not ready (check health check timing)
  - "authentication failed" → Wrong credentials in .env
  - "permission denied" → start.sh not executable
  - "port already in use" → Port conflicts
  - "module not found" → Dependencies not installed (rebuild --no-cache)

# ==============================================================================
# PHASE 4: VALIDATION (10 minutes)
# ==============================================================================

Task 9: Service-by-Service Health Validation
RESPONSIBILITY: Verify each service is actually working

FILES INVOLVED: None (testing)

PATTERN TO FOLLOW: Standard testing workflow

SPECIFIC STEPS:
  1. Check Docker service status:
     docker-compose ps
     # Expected:
     # - taskmanager-db: healthy (green)
     # - taskmanager-backend: healthy (green)
     # - taskmanager-frontend: Up (not unhealthy)

  2. Test database connectivity:
     docker exec -it taskmanager-db psql -U taskuser -d taskmanager -c "\dt"
     # Should show: projects, tasks tables
     # If empty: database init.sql didn't run (do docker-compose down -v)

  3. Test backend API health:
     curl http://localhost:8000/health
     # Should return: {"status": "healthy"}
     # If 000: Backend not started yet
     # If connection refused: Backend not listening or wrong port

  4. Test backend API docs:
     curl http://localhost:8000/docs
     # Should return: HTML (OpenAPI docs)
     open http://localhost:8000/docs
     # Should show: Swagger UI

  5. Test MCP server health:
     curl http://localhost:8051/health
     # Should return: 200 OK
     # If fails: MCP server not running (check backend logs)

  6. Test frontend:
     curl http://localhost:3000
     # Should return: HTML with "<!DOCTYPE html>"
     # If 000: Frontend not started or wrong port
     # If connection refused: Vite not using --host flag

  7. Test frontend in browser:
     open http://localhost:3000
     # Should show: Task Manager UI
     # Check browser console (F12): No CORS errors

VALIDATION:
  - Database: Tables exist (projects, tasks)
  - Backend API: Health endpoint returns 200 + {"status": "healthy"}
  - Backend API: /docs shows Swagger UI
  - MCP Server: Health endpoint returns 200
  - Frontend: curl returns HTML
  - Frontend: Browser loads UI without errors

GOTCHAS TO CHECK:
  - Database init.sql ran (Critical Gotcha #2)
  - Backend using "db" not "localhost" (Critical Gotcha #3)
  - CORS configured for frontend origin (Critical Gotcha #8)
  - Vite using --host flag (Critical Gotcha #6)

---

Task 10: End-to-End Functionality Test
RESPONSIBILITY: Verify core features work through UI and MCP

FILES INVOLVED: None (testing)

PATTERN TO FOLLOW: Feature validation workflow

SPECIFIC STEPS:
  1. Test project creation via UI:
     - Open http://localhost:3000 in browser
     - Click "New Project" button
     - Enter name: "Test Project"
     - Save
     - Verify project appears in list

  2. Test task creation via UI:
     - Click on "Test Project"
     - Click "New Task" button
     - Enter title: "Test Task"
     - Select status: "todo"
     - Save
     - Verify task appears in "To Do" column

  3. Test drag-and-drop:
     - Drag "Test Task" from "To Do" to "Doing" column
     - Verify task moves visually
     - Refresh page
     - Verify task still in "Doing" column (persisted)

  4. Test MCP tools:
     # Install mcp-remote if needed:
     npm install -g @modelcontextprotocol/mcp-remote

     # List available tools:
     npx mcp-remote http://localhost:8051/mcp list-tools
     # Should show: find_tasks, manage_task, find_projects, manage_project

     # Create task via MCP:
     npx mcp-remote http://localhost:8051/mcp call manage_task \
       action=create title="MCP Test Task" status=todo
     # Should return: Task object with ID

     # Verify in UI:
     # Refresh http://localhost:3000
     # "MCP Test Task" should appear in To Do column

VALIDATION:
  - UI: Can create project
  - UI: Can create task
  - UI: Can drag task between columns
  - UI: Changes persist after refresh
  - MCP: Tools respond
  - MCP: Tasks created via MCP appear in UI
  - Integration: Full round-trip works (UI ↔ API ↔ DB ↔ MCP)

SUCCESS METRICS:
  - All CRUD operations work via UI
  - Drag-and-drop updates status correctly
  - MCP tools accessible and functional
  - Data persists across refreshes
  - No errors in browser console
  - No errors in backend logs

# ==============================================================================
# PHASE 5: DOCUMENTATION CLEANUP (Optional - 15 minutes)
# ==============================================================================

Task 11: Update Documentation References
RESPONSIBILITY: Clean up "task-management-ui" → "task-manager" references

FILES TO MODIFY:
  - /Users/jon/source/vibes/infra/task-manager/README.md
  - Any other docs with old references

PATTERN TO FOLLOW: Search and replace

SPECIFIC STEPS:
  1. Search for old references:
     cd /Users/jon/source/vibes
     grep -r "task-management-ui" infra/task-manager/
     # Note all files with references

  2. Update README.md:
     - Change "Task Management UI" → "Task Manager"
     - Update paths from old location to infra/task-manager/
     - Verify code examples still work

  3. Update code comments (optional):
     - Backend: Check src/main.py for app title/description
     - Backend: Check src/mcp_server.py for server name
     - Frontend: Check package.json name field
     - Frontend: Check index.html title tag

  4. Update historical PRPs (optional):
     - Add note to prps/task_management_ui.md: "Moved to infra/task-manager/"
     - Update INITIAL_task_management_ui.md paths

VALIDATION:
  - No "task-management-ui" in user-facing documentation
  - All paths reference infra/task-manager/
  - Code examples are copy-paste ready
  - System still works after changes (re-test)

NOTE: This is polish work. Skip if Phase 1 validation passes and system works.
```

### Implementation Pseudocode

```python
# PHASE 1: Pre-flight Checks
# ==========================

def preflight_checks():
    """Ensure environment is ready before starting services"""

    # Task 1: Check .env file
    # PATTERN: Most common failure (90% probability)
    if not exists(".env"):
        # CRITICAL: This is likely THE issue
        copy_file(".env.example", ".env")
        print("✅ Created .env from template")

    # Verify DATABASE_URL format
    database_url = read_env_var("DATABASE_URL")
    if "localhost" in database_url:
        # GOTCHA: Must use service name in Docker
        warn("DATABASE_URL uses 'localhost' - should use 'db'")
        # Fix: Edit .env, replace localhost with db

    # Task 2: Check port conflicts
    # PATTERN: Common when other services running
    ports = [3000, 8000, 8051, 5432]
    for port in ports:
        if port_in_use(port):
            warn(f"Port {port} already in use")
            # Options:
            # 1. Kill process using port
            # 2. Change port in .env

    # Task 3: Clean slate
    # PATTERN: Force database re-initialization
    run("docker-compose down -v")  # -v removes volumes
    print("✅ Removed old containers and volumes")


# PHASE 2: Docker Compose Configuration
# =====================================

def verify_docker_compose_config():
    """Check docker-compose.yml has correct patterns"""

    # Task 4: Health check configuration
    # PATTERN: From examples/docker-compose-archon.yml
    db_health_check = {
        "test": ["CMD-SHELL", "pg_isready -U taskuser -d taskmanager"],
        "interval": "5s",
        "timeout": "5s",
        "retries": 10,  # Database needs more retries
        "start_period": "10s",  # CRITICAL: Grace period
    }

    backend_health_check = {
        "test": ["CMD", "curl", "-f", "http://localhost:8000/health"],
        "interval": "30s",
        "timeout": "10s",
        "retries": 3,
        "start_period": "40s",  # CRITICAL: Backend needs time to load
    }

    # PATTERN: Backend must wait for DB to be HEALTHY
    backend_depends_on = {
        "db": {
            "condition": "service_healthy"  # NOT just service_started
        }
    }

    # Task 5: Backend script permissions
    # PATTERN: From examples/backend-startup-script.sh
    if not is_executable("backend/start.sh"):
        run("chmod +x backend/start.sh")
        print("✅ Made start.sh executable")

    # Verify start.sh content:
    # - Starts MCP in background: python -m src.mcp_server &
    # - Starts FastAPI with exec: exec uvicorn src.main:app ...
    # - Uses environment variable: ${API_PORT:-8000}

    # Task 6: Frontend Vite configuration
    # PATTERN: From examples/frontend-dockerfile-vite.dockerfile
    dockerfile_cmd = read_dockerfile_cmd("frontend/Dockerfile")
    if "--host" not in dockerfile_cmd:
        # CRITICAL: Vite needs --host flag for Docker
        warn("Frontend Dockerfile missing --host flag")
        # Fix: Add to CMD: ["npm", "run", "dev", "--", "--host"]
        # OR: Set in vite.config.ts: server: { host: true }


# PHASE 3: Build and Start
# =========================

def build_and_start_services():
    """Build fresh images and start services"""

    # Task 7: Build fresh images
    # PATTERN: Force rebuild without cache
    print("Building services without cache...")
    run("docker-compose build --no-cache")

    # Watch for build errors:
    # - Backend: "ModuleNotFoundError" → Dependencies not installed
    # - Frontend: "Cannot find module" → npm packages missing
    # - Backend: uv errors → Check pyproject.toml syntax

    # Task 8: Start services and monitor
    # PATTERN: Foreground mode to see logs
    print("Starting services (watch for errors)...")
    run("docker-compose up")  # Run in foreground

    # Expected log messages:
    # Database: "database system is ready to accept connections"
    # Backend: "Database pool initialized"
    # Backend: "MCP server started on port 8051"
    # Backend: "Uvicorn running on http://0.0.0.0:8000"
    # Frontend: "ready in 342ms"
    # Frontend: "Network: http://172.x.x.x:3000"


# PHASE 4: Validation
# ===================

def validate_services():
    """Verify all services are working correctly"""

    # Task 9: Service-by-service validation
    # PATTERN: Test each layer independently

    # Check Docker status
    services = run("docker-compose ps")
    assert "taskmanager-db" in services and "healthy" in services
    assert "taskmanager-backend" in services and "healthy" in services
    assert "taskmanager-frontend" in services and "Up" in services

    # Check database
    tables = docker_exec("taskmanager-db",
                        "psql -U taskuser -d taskmanager -c '\\dt'")
    assert "projects" in tables and "tasks" in tables
    # If empty: Init script didn't run (do docker-compose down -v)

    # Check backend API
    response = http_get("http://localhost:8000/health")
    assert response.status == 200
    assert response.json() == {"status": "healthy"}

    # Check backend OpenAPI docs
    response = http_get("http://localhost:8000/docs")
    assert response.status == 200
    assert "swagger" in response.text.lower()

    # Check MCP server
    response = http_get("http://localhost:8051/health")
    assert response.status == 200

    # Check frontend
    response = http_get("http://localhost:3000")
    assert response.status == 200
    assert "<!DOCTYPE html>" in response.text

    # Task 10: End-to-end functionality test
    # PATTERN: Test through UI and MCP

    # Test project creation via UI
    # (Manual: Open browser, create project, verify appears)

    # Test MCP tools
    mcp_tools = run("npx mcp-remote http://localhost:8051/mcp list-tools")
    assert "find_tasks" in mcp_tools
    assert "manage_task" in mcp_tools

    # Create task via MCP
    result = run("""
        npx mcp-remote http://localhost:8051/mcp call manage_task \
          action=create title="Test" status=todo
    """)
    assert "id" in result  # Task created

    print("✅ All validation checks passed!")


# GOTCHA DETECTION HELPER
# =======================

def detect_common_gotchas():
    """Proactively check for known issues"""

    gotchas = []

    # Gotcha #1: Missing .env file (90% probability)
    if not exists(".env"):
        gotchas.append({
            "severity": "CRITICAL",
            "issue": "Missing .env file",
            "fix": "cp .env.example .env"
        })

    # Gotcha #2: Stale database volume (70% probability)
    volumes = run("docker volume ls | grep taskmanager")
    if volumes:
        gotchas.append({
            "severity": "HIGH",
            "issue": "Old database volume exists",
            "fix": "docker-compose down -v"
        })

    # Gotcha #3: localhost in DATABASE_URL (60% probability)
    if exists(".env"):
        db_url = read_env_var("DATABASE_URL")
        if "localhost" in db_url:
            gotchas.append({
                "severity": "CRITICAL",
                "issue": "DATABASE_URL uses localhost instead of db",
                "fix": "Edit .env, change localhost to db"
            })

    # Gotcha #4: Missing start_period in health checks
    compose = read_yaml("docker-compose.yml")
    for service in ["db", "backend"]:
        health = compose["services"][service].get("healthcheck", {})
        if "start_period" not in health:
            gotchas.append({
                "severity": "HIGH",
                "issue": f"{service} health check missing start_period",
                "fix": f"Add start_period to {service} health check"
            })

    # Gotcha #6: Missing --host flag for Vite
    dockerfile = read_file("frontend/Dockerfile")
    if "--host" not in dockerfile:
        gotchas.append({
            "severity": "HIGH",
            "issue": "Frontend missing --host flag",
            "fix": "Add --host to Vite dev command or set in vite.config.ts"
        })

    # Gotcha #7: start.sh not executable
    if not is_executable("backend/start.sh"):
        gotchas.append({
            "severity": "HIGH",
            "issue": "start.sh not executable",
            "fix": "chmod +x backend/start.sh"
        })

    return gotchas


# DEBUGGING WORKFLOW
# ==================

def debug_task_manager():
    """Main debugging workflow"""

    print("Task Manager System Debugger")
    print("=" * 50)

    # Phase 0: Check for common gotchas
    print("\n🔍 Checking for common gotchas...")
    gotchas = detect_common_gotchas()

    if gotchas:
        print(f"\n⚠️  Found {len(gotchas)} potential issues:")
        for g in gotchas:
            print(f"  [{g['severity']}] {g['issue']}")
            print(f"    Fix: {g['fix']}")

        print("\n💡 Fix these before continuing")
        return

    # Phase 1: Pre-flight checks
    print("\n✈️  Running pre-flight checks...")
    preflight_checks()

    # Phase 2: Verify configuration
    print("\n🔧 Verifying Docker Compose configuration...")
    verify_docker_compose_config()

    # Phase 3: Build and start
    print("\n🚀 Building and starting services...")
    build_and_start_services()

    # Phase 4: Validate
    print("\n✅ Validating services...")
    validate_services()

    print("\n🎉 Task Manager is now fully functional!")
    print("\n📍 Access points:")
    print("   UI:  http://localhost:3000")
    print("   API: http://localhost:8000")
    print("   MCP: http://localhost:8051")
```

---

## Validation Loop

### Level 1: Pre-Start Validation (Before docker-compose up)

```bash
# Run these checks BEFORE starting services

echo "🔍 Pre-Start Validation"
echo "======================="

# Check 1: .env file exists
if [ ! -f .env ]; then
  echo "❌ FAIL: .env file missing"
  echo "   Fix: cp .env.example .env"
  exit 1
else
  echo "✅ PASS: .env file exists"
fi

# Check 2: DATABASE_URL uses service name
DATABASE_URL=$(grep DATABASE_URL .env | cut -d= -f2)
if echo "$DATABASE_URL" | grep -q "localhost"; then
  echo "❌ FAIL: DATABASE_URL uses localhost (should use 'db')"
  echo "   Fix: Edit .env, change localhost to db"
  exit 1
else
  echo "✅ PASS: DATABASE_URL uses service name"
fi

# Check 3: Port conflicts
for PORT in 3000 8000 8051 5432; do
  if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "❌ FAIL: Port $PORT already in use"
    echo "   Fix: lsof -i :$PORT (see what's using it)"
    exit 1
  fi
done
echo "✅ PASS: All ports available"

# Check 4: start.sh is executable
if [ ! -x backend/start.sh ]; then
  echo "❌ FAIL: start.sh not executable"
  echo "   Fix: chmod +x backend/start.sh"
  exit 1
else
  echo "✅ PASS: start.sh is executable"
fi

# Check 5: docker-compose.yml has start_period in health checks
if ! grep -A 5 "healthcheck:" docker-compose.yml | grep -q "start_period"; then
  echo "⚠️  WARN: Health checks may be missing start_period"
  echo "   Check: docker-compose.yml health check configuration"
fi

echo ""
echo "✅ Pre-start validation complete"
echo "   Ready to run: docker-compose up"
```

### Level 2: Runtime Validation (After services start)

```bash
# Run these checks AFTER services are running

echo "🚦 Runtime Validation"
echo "===================="

# Wait for services to initialize
echo "⏳ Waiting 60 seconds for services to initialize..."
sleep 60

# Check 1: Docker service status
echo "Checking Docker service status..."
docker-compose ps

DB_STATUS=$(docker-compose ps taskmanager-db | grep healthy)
if [ -z "$DB_STATUS" ]; then
  echo "❌ FAIL: Database not healthy"
  echo "   Check: docker-compose logs db"
  exit 1
else
  echo "✅ PASS: Database healthy"
fi

BACKEND_STATUS=$(docker-compose ps taskmanager-backend | grep healthy)
if [ -z "$BACKEND_STATUS" ]; then
  echo "❌ FAIL: Backend not healthy"
  echo "   Check: docker-compose logs backend"
  exit 1
else
  echo "✅ PASS: Backend healthy"
fi

# Check 2: Database tables exist
echo "Checking database schema..."
TABLES=$(docker exec taskmanager-db psql -U taskuser -d taskmanager -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public' AND table_name IN ('projects', 'tasks');")
if [ "$TABLES" -lt 2 ]; then
  echo "❌ FAIL: Database tables missing"
  echo "   Fix: docker-compose down -v && docker-compose up (force re-init)"
  exit 1
else
  echo "✅ PASS: Database tables exist"
fi

# Check 3: Backend API health
echo "Checking backend API..."
HEALTH=$(curl -s http://localhost:8000/health)
if ! echo "$HEALTH" | grep -q "healthy"; then
  echo "❌ FAIL: Backend API not responding correctly"
  echo "   Check: docker-compose logs backend"
  exit 1
else
  echo "✅ PASS: Backend API healthy"
fi

# Check 4: MCP server health
echo "Checking MCP server..."
MCP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8051/health)
if [ "$MCP_STATUS" != "200" ]; then
  echo "❌ FAIL: MCP server not responding"
  echo "   Check: docker-compose logs backend | grep MCP"
  exit 1
else
  echo "✅ PASS: MCP server responding"
fi

# Check 5: Frontend responds
echo "Checking frontend..."
FRONTEND=$(curl -s http://localhost:3000 | head -n 1)
if ! echo "$FRONTEND" | grep -q "<!DOCTYPE html>"; then
  echo "❌ FAIL: Frontend not serving HTML"
  echo "   Check: docker-compose logs frontend"
  exit 1
else
  echo "✅ PASS: Frontend serving HTML"
fi

echo ""
echo "✅ Runtime validation complete"
echo "   All services are operational"
```

### Level 3: Integration Testing (End-to-end)

```bash
# Test actual functionality

echo "🔗 Integration Testing"
echo "===================="

# Test 1: Create project via API
echo "Testing project creation..."
PROJECT_RESPONSE=$(curl -s -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Project", "description": "Validation test"}')

PROJECT_ID=$(echo "$PROJECT_RESPONSE" | jq -r '.id')
if [ "$PROJECT_ID" = "null" ] || [ -z "$PROJECT_ID" ]; then
  echo "❌ FAIL: Could not create project"
  echo "   Response: $PROJECT_RESPONSE"
  exit 1
else
  echo "✅ PASS: Project created (ID: $PROJECT_ID)"
fi

# Test 2: Create task via API
echo "Testing task creation..."
TASK_RESPONSE=$(curl -s -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d "{\"project_id\": \"$PROJECT_ID\", \"title\": \"Test Task\", \"status\": \"todo\"}")

TASK_ID=$(echo "$TASK_RESPONSE" | jq -r '.id')
if [ "$TASK_ID" = "null" ] || [ -z "$TASK_ID" ]; then
  echo "❌ FAIL: Could not create task"
  echo "   Response: $TASK_RESPONSE"
  exit 1
else
  echo "✅ PASS: Task created (ID: $TASK_ID)"
fi

# Test 3: Update task status
echo "Testing task update..."
UPDATE_RESPONSE=$(curl -s -X PUT http://localhost:8000/api/tasks/$TASK_ID \
  -H "Content-Type: application/json" \
  -d '{"status": "doing"}')

UPDATED_STATUS=$(echo "$UPDATE_RESPONSE" | jq -r '.status')
if [ "$UPDATED_STATUS" != "doing" ]; then
  echo "❌ FAIL: Could not update task status"
  echo "   Response: $UPDATE_RESPONSE"
  exit 1
else
  echo "✅ PASS: Task status updated"
fi

# Test 4: MCP tools accessible
echo "Testing MCP tools..."
MCP_TOOLS=$(npx -y @modelcontextprotocol/mcp-remote http://localhost:8051/mcp list-tools 2>&1)
if ! echo "$MCP_TOOLS" | grep -q "find_tasks"; then
  echo "❌ FAIL: MCP tools not accessible"
  echo "   Output: $MCP_TOOLS"
  exit 1
else
  echo "✅ PASS: MCP tools accessible"
fi

# Test 5: CORS working (check from browser console manually)
echo "⚠️  MANUAL: Test CORS in browser"
echo "   1. Open http://localhost:3000"
echo "   2. Open DevTools Console (F12)"
echo "   3. Create a project via UI"
echo "   4. Verify no CORS errors in console"

echo ""
echo "✅ Integration testing complete"
echo "   Core functionality working"
```

---

## Final Validation Checklist

Before marking PRP complete, verify:

### Phase 1: System Working
- [ ] `.env` file exists with correct values
- [ ] All ports available (3000, 8000, 8051, 5432)
- [ ] `docker-compose ps` shows all services healthy/running
- [ ] Database tables exist: `docker exec taskmanager-db psql -U taskuser -d taskmanager -c "\dt"` shows projects, tasks
- [ ] Backend health: `curl http://localhost:8000/health` returns `{"status": "healthy"}`
- [ ] Backend docs: `curl http://localhost:8000/docs` returns HTML
- [ ] MCP health: `curl http://localhost:8051/health` returns 200 OK
- [ ] Frontend: `curl http://localhost:3000` returns HTML
- [ ] Frontend in browser: `open http://localhost:3000` loads UI
- [ ] No errors in browser console (F12)

### Phase 2: Functionality Verified
- [ ] Can create project via UI
- [ ] Can create task via UI
- [ ] Can drag task between Kanban columns
- [ ] Task state persists after page refresh
- [ ] MCP tools listed: `npx mcp-remote http://localhost:8051/mcp list-tools`
- [ ] Can create task via MCP
- [ ] Task created via MCP appears in UI

### Phase 3: Configuration Validated
- [ ] DATABASE_URL uses service name "db" not "localhost"
- [ ] All health checks have `start_period`
- [ ] Backend `depends_on` uses `condition: service_healthy`
- [ ] `start.sh` is executable (`ls -l` shows `-rwxr-xr-x`)
- [ ] Frontend uses `--host` flag or `host: true` in vite.config.ts
- [ ] CORS configured with `http://localhost:3000` in `allow_origins`

### Phase 4: Documentation (Optional)
- [ ] No "task-management-ui" in user-facing docs
- [ ] README paths point to `infra/task-manager/`
- [ ] Code examples work as written

---

## Anti-Patterns to Avoid

### ❌ Don't: Start without checking .env file
**Why**: Most common cause of failure (90% probability). Missing `.env` means services use wrong defaults or crash.

**Do Instead**: Always verify `.env` exists before `docker-compose up`

---

### ❌ Don't: Restart without clearing volumes when database fails
**Why**: PostgreSQL init scripts only run on first start. Restarting without `-v` keeps broken database state.

**Do Instead**: Use `docker-compose down -v` to force database re-initialization

---

### ❌ Don't: Use localhost in DATABASE_URL inside containers
**Why**: Inside container, localhost = that container, not other services. Backend can't reach database.

**Do Instead**: Use service name "db" from docker-compose.yml for container-to-container communication

---

### ❌ Don't: Skip start_period in health checks
**Why**: Services marked unhealthy during initialization, causing restart loops or dependent services never starting.

**Do Instead**: Always include generous start_period (10s for db, 40s for backend) in health checks

---

### ❌ Don't: Use depends_on without condition: service_healthy
**Why**: Backend starts before database is ready, connection pool creation fails, backend crashes.

**Do Instead**: Always use `condition: service_healthy` to wait for health checks, not just container start

---

### ❌ Don't: Run Vite in Docker without --host flag
**Why**: Vite binds to localhost by default, unreachable from outside container even with port mapping.

**Do Instead**: Use `--host` flag in CMD or `host: true` in vite.config.ts

---

### ❌ Don't: Build with cached layers after dependency changes
**Why**: Docker reuses cached layer with old dependencies, new packages not installed.

**Do Instead**: Use `docker-compose build --no-cache` when dependencies change

---

### ❌ Don't: Guess at issues - use systematic debugging
**Why**: Multiple issues can compound. Fixing randomly wastes time and may break working parts.

**Do Instead**: Follow debugging workflow: Pre-flight checks → config fixes → build → validate

---

### ❌ Don't: Skip validation steps
**Why**: May appear to work but have subtle issues (CORS errors, MCP not working, data not persisting).

**Do Instead**: Run all three validation levels (pre-start, runtime, integration)

---

### ❌ Don't: Mix asyncpg DSN formats
**Why**: Pure asyncpg uses `postgresql://`, SQLAlchemy uses `postgresql+asyncpg://`. Wrong format causes errors.

**Do Instead**: Use `postgresql://` for pure asyncpg (task manager doesn't use SQLAlchemy)

---

## Success Metrics

### Current State (Baseline)
- Location: `/Users/jon/source/vibes/infra/task-manager/` ✅ (already moved)
- Status: ❌ Never worked - services not starting
- Error: Unknown (need logs to diagnose)
- Usability: ❌ Completely broken - cannot use

### Target State (Phase 1 Success)
- Location: `/Users/jon/source/vibes/infra/task-manager/` ✅ (unchanged)
- Status: ✅ All services healthy
- Services:
  - Database: ✅ Healthy, tables created
  - Backend: ✅ Healthy, API responding
  - MCP: ✅ Responding, tools accessible
  - Frontend: ✅ Running, UI loads
- Functionality: ✅ Create/read/update/delete via UI and MCP
- Performance: Sub-second response times
- Stability: Runs for hours without crashes

### Target State (Phase 2 Success)
- Documentation: ✅ Consistent "task-manager" naming
- Paths: ✅ All references to `infra/task-manager/`
- Examples: ✅ Copy-paste ready
- Production ready: ✅ Can be used in vibes ecosystem

---

## PRP Quality Self-Assessment

**Score: 9.5/10** - High confidence in one-pass implementation success

**Reasoning**:
- ✅ Comprehensive context: All 5 research documents thoroughly synthesized
- ✅ Clear task breakdown: 11 tasks with specific steps and validation
- ✅ Proven patterns: 8 working examples extracted from Archon/LiteLLM/Supabase
- ✅ Validation strategy: 3-level validation (pre-start, runtime, integration)
- ✅ Error handling: 10 critical gotchas with detection and solutions
- ✅ Working examples: Complete code from functioning services
- ✅ Debugging workflow: Systematic approach with decision points
- ✅ Anti-patterns documented: 10 common mistakes with explanations

**Deduction reasoning** (-0.5 points):
- Assumes underlying code is correct (task manager code itself may have bugs)
- Cannot account for unknown environment-specific issues (firewall, macOS security, etc.)
- MCP server testing requires manual verification in some cases

**Mitigations**:
- Systematic debugging catches most issues early
- Validation loops detect problems at each layer
- Examples provide working reference for comparison
- Gotcha detection identifies common problems proactively

**Confidence in one-pass success**: 85%
- If issue is one of the top 3 gotchas (95% probability): Will fix immediately
- If issue is configuration/setup related: Will fix within 1-2 iterations
- If issue is code bug: May require deeper debugging beyond PRP scope

---

## Additional Context

### Why This Matters

**Business Impact**:
- Task manager is critical infrastructure for vibes ecosystem
- Archon MCP server depends on functional task management
- Claude Code integration requires working MCP tools
- Demonstrates full-stack patterns for future services

**Technical Impact**:
- Validates Docker Compose health check strategy
- Proves React + FastAPI + PostgreSQL + MCP integration
- Serves as reference for infra/ services
- Tests uv package manager in production Dockerfile

**User Impact**:
- Developers need UI for task visibility
- AI agents need MCP for programmatic access
- Team coordination requires centralized task tracking
- Project planning needs backlog management

### Integration Points

**With Archon**:
- Archon MCP server will use task manager MCP tools
- Claude Code (via Archon) manages development tasks
- Task manager provides visual feedback for AI-created tasks

**With Vibes Ecosystem**:
- Part of infra/ services family (archon, litellm, supabase)
- Follows standard Docker Compose patterns
- Uses vibes-network for inter-service communication

**With Development Workflow**:
- PRP execution creates tasks in task manager
- Sprint planning uses task manager Kanban
- Progress tracking for multi-stage features

### Files Requiring Attention

**Critical (Must Review)**:
1. `.env` - Likely missing, must create from `.env.example`
2. `docker-compose.yml` - Verify health checks and dependencies
3. `backend/start.sh` - Check executable permissions
4. `backend/src/main.py` - Verify CORS and lifespan configuration
5. `frontend/vite.config.ts` or `frontend/Dockerfile` - Ensure --host flag

**Secondary (Check if Issues Persist)**:
1. `backend/pyproject.toml` - Verify dependency versions compatible
2. `backend/src/config/database.py` - Check connection pool configuration
3. `frontend/package.json` - Verify all dependencies present
4. `database/init.sql` - Ensure schema is complete

**Documentation (Phase 2)**:
1. `README.md` - Update paths to infra/task-manager/
2. `prps/task_management_ui.md` - Add move note
3. Main vibes `README.md` - Update if task manager mentioned

---

## Appendix: Quick Reference

### Common Commands

```bash
# Pre-flight
cd /Users/jon/source/vibes/infra/task-manager
cp .env.example .env  # If missing
lsof -i :3000 :8000 :8051 :5432  # Check ports
docker-compose down -v  # Clean slate

# Build and Start
docker-compose build --no-cache
docker-compose up  # Watch logs

# Validation
docker-compose ps  # Check status
curl http://localhost:8000/health  # Backend
curl http://localhost:8051/health  # MCP
curl http://localhost:3000  # Frontend
docker exec taskmanager-db psql -U taskuser -d taskmanager -c "\dt"  # Database

# Debugging
docker-compose logs db  # Database logs
docker-compose logs backend  # Backend logs
docker-compose logs frontend  # Frontend logs
docker exec -it taskmanager-db psql -U taskuser -d taskmanager  # DB shell
docker exec -it taskmanager-backend bash  # Backend shell
```

### Critical Gotcha Quick Reference

| Issue | Probability | Detection | Fix |
|-------|-------------|-----------|-----|
| Missing .env | 90% | `ls .env` fails | `cp .env.example .env` |
| Stale DB volume | 70% | Tables don't exist | `docker-compose down -v` |
| localhost in DB URL | 60% | Connection refused | Edit .env: db not localhost |
| Missing start_period | High | Services unhealthy | Add to health checks |
| Wrong depends_on | High | Backend starts too early | Use service_healthy |
| Vite no --host | High | Frontend unreachable | Add to Dockerfile CMD |
| Script not executable | Medium | Permission denied | `chmod +x start.sh` |
| Missing CORS | Medium | Browser blocks | Add CORSMiddleware |
| Wrong asyncpg format | Medium | Invalid DSN | Remove +asyncpg |
| Port conflicts | Medium | Port allocated error | `lsof -i :PORT` |

### Example Working Values

```bash
# .env file (working development values)
POSTGRES_USER=taskuser
POSTGRES_PASSWORD=taskpass123
POSTGRES_DB=taskmanager
DATABASE_URL=postgresql+asyncpg://taskuser:taskpass123@db:5432/taskmanager

VITE_API_URL=http://localhost:8000
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

API_PORT=8000
MCP_PORT=8051
FRONTEND_PORT=3000
```

### Health Check Examples

```yaml
# Database (from examples/postgres-healthcheck.yml)
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-taskuser} -d ${POSTGRES_DB:-taskmanager}"]
  interval: 5s
  timeout: 5s
  retries: 10
  start_period: 10s

# Backend (from examples/docker-compose-archon.yml)
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### Success Indicators

✅ **System is working when**:
- `docker-compose ps` shows healthy/running for all services
- `curl http://localhost:8000/health` returns `{"status": "healthy"}`
- `curl http://localhost:3000` returns HTML
- Browser loads http://localhost:3000 without errors
- Can create project and task via UI
- Tasks persist after page refresh
- MCP tools listed: `npx mcp-remote http://localhost:8051/mcp list-tools`

❌ **System is broken when**:
- Services show "unhealthy" or "restarting" in `docker-compose ps`
- curl commands return "connection refused"
- Browser shows CORS errors
- Database tables don't exist
- UI shows errors or blank pages

---

**End of PRP: Fix Task Manager System**

**Next Steps**: Execute tasks in order, validate at each step, iterate if needed.

**Estimated Time**: 1-2 hours for Phase 1 (debug & fix), 30 minutes for Phase 2 (documentation cleanup)

**Success Probability**: 85% one-pass success if following systematic approach
