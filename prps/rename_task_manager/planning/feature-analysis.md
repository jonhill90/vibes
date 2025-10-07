# Feature Analysis: Fix Task Manager System

## INITIAL.md Summary

The task manager system was moved to `infra/task-manager/` but has never successfully run. The goal is to debug and fix all issues to get Docker Compose services running, then clean up any lingering "task-management-ui" references to achieve a fully functional task manager accessible via UI (localhost:3000), API (localhost:8000), and MCP (localhost:8051).

## Core Requirements

### Explicit Requirements

**Phase 1: Debug & Fix (Priority)**
- Investigate why services aren't starting (containers, logs, errors)
- Fix database initialization and connection
- Fix backend startup (dependencies, migrations, MCP server)
- Fix frontend build and startup
- Get all services running healthy
- Verify core functionality works end-to-end

**Phase 2: Clean Up References (Quick polish)**
- Update remaining "task-management-ui" references to "task-manager"
- Update documentation with correct paths
- Ensure consistency across all user-facing content

**Key Context**
- System already at `infra/task-manager/` - no relocation needed
- No existing data to preserve - fresh slate
- Can safely change any configuration
- Simple success criteria: Get containers running → UI loading → MCP responding

### Implicit Requirements

**Docker Compose Health**
- All three services (db, backend, frontend) must start without errors
- Health checks must pass for database and backend
- Services must communicate properly via docker network
- Port mappings must be correct (no conflicts)

**Database Functionality**
- PostgreSQL must initialize with correct schema
- Database connection string must work from backend
- Connection pool must be properly managed
- Health checks via pg_isready must pass

**Backend Functionality**
- Python dependencies must install correctly via uv
- FastAPI must start on port 8000
- MCP server must start on port 8051
- Database connection must work (asyncpg)
- CORS must allow frontend origin
- Both servers (API + MCP) must run simultaneously

**Frontend Functionality**
- Node dependencies must install correctly
- Vite dev server must start on port 3000
- TypeScript compilation must succeed
- API connection via VITE_API_URL must work
- React components must render without errors

**End-to-End Functionality**
- Create projects via UI
- Create tasks via UI
- Drag-and-drop tasks between Kanban columns
- MCP tools respond correctly
- Tasks created via MCP appear in UI

## Technical Components

### Data Models

**Database Schema** (from `database/init.sql`)
- `projects` table: id (UUID), name, description, created_at, updated_at
- `tasks` table: id (UUID), project_id (FK), title, description, status (enum), order_index, created_at, updated_at
- Task status enum: 'todo', 'doing', 'review', 'done'
- Proper foreign key constraints and indexes

**Python Models** (from `backend/src/models/`)
- `Project` Pydantic model for validation
- `Task` Pydantic model with status enum
- Request/Response DTOs for API endpoints

**TypeScript Types** (from `frontend/src/features/*/types/`)
- Project interface
- Task interface with DatabaseTaskStatus
- Service request/response types

### External Integrations

**Core Dependencies**
- **PostgreSQL 16**: Database with asyncpg driver
- **FastAPI**: REST API framework (>=0.104.0)
- **FastMCP**: MCP server integration (>=0.4.0)
- **React 18**: Frontend framework
- **TanStack Query v5**: Data fetching and caching
- **Vite**: Build tool and dev server
- **Uvicorn**: ASGI server for FastAPI

**Build Tools**
- **uv**: Python package manager (used in Dockerfile)
- **npm**: Node package manager
- **Docker Compose**: Service orchestration

### Core Logic

**Backend API** (`backend/src/`)
- `main.py`: FastAPI app with CORS, health checks, lifespan management
- `api/projects.py`: Project CRUD endpoints
- `api/tasks.py`: Task CRUD endpoints with status updates
- `config/database.py`: Database connection pool management
- `services/`: Business logic layer
- `mcp_server.py`: MCP tool definitions for IDE integration

**Backend Startup** (`backend/start.sh`)
1. Start MCP server in background on port 8051
2. Start FastAPI with uvicorn on port 8000 in foreground
3. Use exec to ensure proper signal handling

**Frontend Architecture** (`frontend/src/`)
- Feature-based structure (`features/projects/`, `features/tasks/`)
- TanStack Query for data fetching
- Optimistic updates with nanoid
- Drag-and-drop with react-dnd
- Radix UI components

**Database Migrations** (`backend/alembic/`)
- Alembic for schema management
- Initial migration creates tables
- Version history tracking

### UI/CLI Requirements

**Web UI (Port 3000)**
- Project list and creation
- Kanban board with drag-and-drop
- Task cards with status visualization
- Modal forms for create/edit
- Real-time updates via polling

**REST API (Port 8000)**
- `/health` - Health check endpoint
- `/api/projects` - Project CRUD
- `/api/tasks` - Task CRUD
- `/api/projects/{id}/tasks` - Project-scoped tasks
- OpenAPI docs at `/docs`

**MCP Server (Port 8051)**
- `find_projects` - Search/list projects
- `manage_project` - Create/update/delete projects
- `find_tasks` - Search/list tasks
- `manage_task` - Create/update/delete tasks
- Health check endpoint

## Similar Implementations Found in Archon

### 1. Archon MCP Server (infra/archon/)
- **Relevance**: 9/10
- **Archon ID**: Working reference implementation
- **Key Patterns to Reuse**:
  - **Multi-service Docker Compose**: Archon has server, MCP, frontend, agents services
  - **Health checks with conditions**: `depends_on: { condition: service_healthy }`
  - **Named volumes for data persistence**: `taskmanager-db-data` pattern
  - **Network isolation**: Custom bridge networks for service communication
  - **Python 3.12 with uv**: Same package manager and Python version
  - **FastAPI health endpoints**: Standard `/health` pattern
  - **Environment variable management**: `.env.example` copied to `.env`
  - **Hot reload volumes**: Source code mounted for development
- **Gotchas to Watch**:
  - Use `host.docker.internal:host-gateway` for external services
  - Set `start_period` in health checks to allow service initialization
  - Mount `/var/run/docker.sock` only if needed
  - Use specific ports to avoid conflicts with other services

### 2. Task Manager Docker Compose (Current)
- **Relevance**: 10/10
- **Archon ID**: Local codebase
- **Analysis**:
  - **Well-structured compose file**: Proper health checks, dependencies, networks
  - **Environment defaults**: Good use of `${VAR:-default}` pattern
  - **Volume exclusions**: Prevents node_modules permission issues
  - **Frontend health check**: Uses curl to verify Vite server
- **Likely Issues Based on "Never Worked"**:
  1. Missing `.env` file (must copy from `.env.example`)
  2. Backend dependencies not installing (uv.lock missing or outdated)
  3. Port conflicts (3000, 8000, 8051, 5432 already in use)
  4. Database not initializing (init.sql not running)
  5. Frontend build failing (TypeScript errors or missing deps)
  6. Backend health check failing (database connection issue)
  7. Start order issues (backend starting before db ready)
  8. Path issues after move (relative paths broken)

### 3. PostgreSQL Health Check Pattern
- **Relevance**: 8/10
- **Archon ID**: Standard pattern from Archon and other infra
- **Key Pattern**:
  ```yaml
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-taskuser} -d ${POSTGRES_DB:-taskmanager}"]
    interval: 5s
    timeout: 5s
    retries: 5
    start_period: 10s
  ```
- **Critical**: Backend must use `depends_on: db: { condition: service_healthy }`
- **Gotcha**: Without health check dependencies, backend starts before db ready and crashes

## Recommended Technology Stack

Based on current implementation (already chosen):

**Backend Framework**: FastAPI 0.104.0+ with Python 3.12
- **Reasoning**: Already implemented, works well with async, good MCP integration

**Database**: PostgreSQL 16 with asyncpg driver
- **Reasoning**: Already chosen, excellent async support, stable

**MCP Integration**: FastMCP 0.4.0+
- **Reasoning**: Purpose-built for MCP server implementation in Python

**Frontend Framework**: React 18 with TypeScript 5
- **Reasoning**: Already implemented, modern patterns

**Data Fetching**: TanStack Query v5
- **Reasoning**: Already implemented, excellent caching and polling

**Build Tools**:
- **Backend**: uv (Python package manager)
- **Frontend**: Vite 5.x (fast dev server, excellent TypeScript support)

**Testing**:
- **Backend**: pytest with pytest-asyncio
- **Frontend**: Vitest with React Testing Library

**Containerization**: Docker Compose with multi-stage builds
- **Reasoning**: Already configured, works well for development

## Assumptions Made

### 1. Environment Configuration
**Assumption**: `.env` file is missing and needs to be created from `.env.example`
- **Reasoning**: This is the most common cause of "never worked" after a move
- **Source**: Standard practice in all vibes infra projects (archon, litellm, supabase)
- **Action Required**: Copy `.env.example` to `.env` as first debugging step

### 2. Port Conflicts
**Assumption**: Ports 3000, 8000, 8051, or 5432 may already be in use
- **Reasoning**: Common issue when running multiple development services
- **Source**: INITIAL.md mentions system was moved but never worked
- **Action Required**: Check `lsof -i :3000 :8000 :8051 :5432` before starting

### 3. Dependency Installation Issues
**Assumption**: Backend dependencies may not be properly installed via uv
- **Reasoning**: Dockerfile uses `uv pip install -r pyproject.toml` which may fail if deps changed
- **Source**: Python dependency hell is common with async libraries
- **Action Required**: Verify all dependencies in pyproject.toml are compatible, check for uv.lock

### 4. Database Schema Initialization
**Assumption**: `database/init.sql` needs to run but may not be executing
- **Reasoning**: Docker Compose mounts `./database:/docker-entrypoint-initdb.d:ro`
- **Source**: This only runs on first container start, not on restarts
- **Action Required**: May need `docker-compose down -v` to force re-initialization

### 5. Frontend TypeScript Compilation
**Assumption**: TypeScript may have compilation errors preventing Vite from starting
- **Reasoning**: Package name is "task-management-ui" but directory is "task-manager"
- **Source**: Naming inconsistencies can cause import path issues
- **Action Required**: Check for any hardcoded path references in imports

### 6. Backend Start Script Permissions
**Assumption**: `start.sh` may not be executable
- **Reasoning**: File permissions can be lost during moves or in Docker builds
- **Source**: Common Docker issue with shell scripts
- **Action Required**: Verify `chmod +x start.sh` or use `CMD ["bash", "start.sh"]`

### 7. Network Communication Issues
**Assumption**: Services can't communicate via docker-compose network
- **Reasoning**: Docker Compose creates custom bridge network `taskmanager-network`
- **Source**: Services must use service names (db, backend) not localhost
- **Action Required**: Verify DATABASE_URL uses `db:5432` not `localhost:5432`

### 8. Health Check Failures
**Assumption**: Backend health check may fail if database connection pool doesn't initialize
- **Reasoning**: main.py has database pool initialization in lifespan
- **Source**: If asyncpg can't connect, health check will fail
- **Action Required**: Check DATABASE_URL format: `postgresql+asyncpg://user:pass@db:5432/dbname`

### 9. CORS Configuration
**Assumption**: CORS may block frontend requests if not configured correctly
- **Reasoning**: main.py configures CORS based on ENVIRONMENT variable
- **Source**: If ENVIRONMENT not set correctly, wrong origins allowed
- **Action Required**: Verify ENVIRONMENT=development and CORS_ORIGINS includes http://localhost:3000

### 10. MCP Server Port Binding
**Assumption**: MCP server may fail to bind to port 8051 if already in use
- **Reasoning**: start.sh runs MCP server in background before FastAPI
- **Source**: If MCP crashes, FastAPI continues but MCP tools don't work
- **Action Required**: Check logs for both processes, ensure both start successfully

## Success Criteria

### Phase 1: System Fully Functional

**Docker Compose Health**
- [ ] `docker-compose up` starts all three services without errors
- [ ] `docker-compose ps` shows all services as "healthy" or "running"
- [ ] No error messages in logs from any service
- [ ] All containers stay running (don't crash and restart)

**Database Validation**
- [ ] Database container shows "healthy" status
- [ ] Can connect via: `docker exec -it taskmanager-db psql -U taskuser -d taskmanager`
- [ ] Tables exist: `\dt` shows projects and tasks tables
- [ ] Schema matches init.sql (proper columns, constraints, indexes)

**Backend Validation**
- [ ] Backend container shows "healthy" status
- [ ] FastAPI responds: `curl http://localhost:8000/health` returns `{"status": "healthy"}`
- [ ] OpenAPI docs load: `curl http://localhost:8000/docs` returns HTML
- [ ] Logs show "Database pool initialized" message
- [ ] Logs show both FastAPI and MCP server started

**MCP Server Validation**
- [ ] MCP server responds: `curl http://localhost:8051/health` succeeds
- [ ] Can execute MCP tools via `npx mcp-remote http://localhost:8051/mcp`
- [ ] MCP logs show no errors
- [ ] MCP server running on correct port (8051)

**Frontend Validation**
- [ ] Frontend container running (not necessarily "healthy" - dev server)
- [ ] Vite server responds: `curl http://localhost:3000` returns HTML
- [ ] Browser loads UI: `open http://localhost:3000` shows interface
- [ ] No console errors in browser DevTools
- [ ] No React rendering errors

**End-to-End Functionality**
- [ ] Can create a project via UI
- [ ] Project appears in list immediately (optimistic update)
- [ ] Can create a task via UI
- [ ] Task appears on Kanban board
- [ ] Can drag task to different column
- [ ] Task status updates persist (shows in correct column after refresh)
- [ ] Can create task via MCP tool
- [ ] Task created via MCP appears in UI after polling interval
- [ ] Can update task via both UI and MCP
- [ ] Can delete task and it disappears from UI

### Phase 2: Documentation and Consistency

**Naming Consistency**
- [ ] No "task-management-ui" references in user-facing documentation
- [ ] README.md uses "task-manager" consistently
- [ ] Code comments reference correct directory paths
- [ ] Environment variables use consistent naming
- [ ] Docker container names are acceptable (taskmanager-* is fine, no need to change)

**Documentation Accuracy**
- [ ] All paths in README point to `infra/task-manager/`
- [ ] Quick start instructions work as written
- [ ] Code examples are copy-paste ready
- [ ] Environment variable documentation matches `.env.example`
- [ ] MCP integration instructions are correct

**System Stability**
- [ ] Services stay running for 10+ minutes without crashes
- [ ] Can stop and restart with `docker-compose down && docker-compose up`
- [ ] Can fully reset with `docker-compose down -v && docker-compose up`
- [ ] Logs are clean (no repeated errors or warnings)

## Next Steps for Downstream Agents

### Codebase Researcher
**Focus on**:
1. Find actual Docker Compose logs to identify specific errors
2. Check if `.env` file exists in `infra/task-manager/`
3. Verify `start.sh` has executable permissions
4. Look for any hardcoded path references that reference old location
5. Check for port conflicts on host machine
6. Examine database connection string format in all locations
7. Verify Python package versions are compatible (especially asyncpg + FastAPI)
8. Check if frontend has any import errors or TypeScript compilation issues

**Specific Files to Examine**:
- `infra/task-manager/.env` (may not exist)
- `infra/task-manager/backend/start.sh` (permissions)
- `infra/task-manager/backend/pyproject.toml` (dependency versions)
- `infra/task-manager/frontend/package.json` (dependency versions)
- Any files with absolute paths or old directory references

### Documentation Hunter
**Find documentation for**:
1. **uv package manager**: Installation and dependency resolution
2. **FastMCP**: Server setup and debugging common issues
3. **asyncpg**: Connection string format and common connection errors
4. **PostgreSQL docker**: Initialization scripts and health checks
5. **Vite dev server**: Docker configuration and host flag
6. **Docker Compose**: Health check best practices
7. **FastAPI**: Lifespan events and startup debugging
8. **TanStack Query**: Polling configuration and error handling

**Priority Documentation**:
- FastMCP official docs (may have changed since 0.4.0)
- asyncpg connection string requirements
- Docker Compose depends_on with health checks
- PostgreSQL docker entrypoint initialization

### Example Curator
**Extract examples showing**:
1. **Working Docker Compose with health checks**: Multi-service setups with proper dependencies
2. **FastAPI with database pool**: Lifespan management and connection initialization
3. **Python multi-process startup**: Running multiple servers in one container
4. **Vite in Docker**: Development server configuration with hot reload
5. **MCP server debugging**: Common errors and solutions
6. **PostgreSQL initialization**: Running init scripts in docker-entrypoint-initdb.d
7. **Environment variable defaults**: Proper use of `${VAR:-default}` syntax
8. **Shell script in Docker**: Making scripts executable and running them

**Specific Patterns Needed**:
- Health check that actually waits for service ready (not just port open)
- Background process management in Docker containers
- Database pool error handling and retry logic
- CORS configuration for development vs production

### Gotcha Detective
**Investigate known problem areas**:

1. **uv Package Manager**
   - Does it need uv.lock file?
   - Can it install from pyproject.toml alone?
   - Are all dependencies in pyproject.toml available?
   - Does it handle optional dependencies correctly?

2. **FastMCP Integration**
   - Common startup errors
   - Port binding issues
   - How to verify it's actually running
   - Logging configuration

3. **Database Connection**
   - asyncpg vs psycopg2 connection string differences
   - Connection pool initialization timing
   - Health check vs actual readiness
   - PostgreSQL initialization script execution

4. **Docker Networking**
   - Service name resolution (db vs localhost)
   - Port mapping vs internal ports
   - Health check accessibility from other containers
   - Bridge network configuration

5. **File Permissions in Docker**
   - start.sh execution permissions
   - Volume mount permission issues
   - node_modules ownership problems
   - Database volume initialization

6. **Frontend Build Issues**
   - TypeScript path resolution after directory rename
   - Vite proxy configuration
   - Environment variable passing (VITE_ prefix)
   - Host flag requirement for Docker

7. **Service Startup Order**
   - Health check timing (start_period)
   - Database initialization vs backend startup
   - Frontend waiting for backend
   - Background process in start.sh

8. **Environment Variables**
   - Missing .env file (most likely issue)
   - Wrong variable names
   - Quote handling in docker-compose
   - Variable expansion in health checks

## Debugging Strategy

### Systematic Approach

**Step 1: Pre-flight Checks (5 minutes)**
```bash
cd /Users/jon/source/vibes/infra/task-manager

# Check if .env exists
ls -la .env

# If not, create it
cp .env.example .env

# Check for port conflicts
lsof -i :3000 :8000 :8051 :5432

# Clean slate
docker-compose down -v
```

**Step 2: Build Fresh (5 minutes)**
```bash
# Build without cache
docker-compose build --no-cache

# Check for build errors in each service
```

**Step 3: Start Services and Watch Logs (10 minutes)**
```bash
# Start in foreground to see all logs
docker-compose up

# Watch for first error in logs
# Common patterns to look for:
# - "Connection refused"
# - "Port already in use"
# - "No module named"
# - "Permission denied"
# - "Database does not exist"
# - "Health check failed"
```

**Step 4: Service-by-Service Validation (15 minutes)**
```bash
# Check database
docker-compose ps
docker-compose logs db
docker exec -it taskmanager-db psql -U taskuser -d taskmanager -c "\dt"

# Check backend
docker-compose logs backend
curl http://localhost:8000/health
curl http://localhost:8000/docs

# Check MCP server
curl http://localhost:8051/health

# Check frontend
docker-compose logs frontend
curl http://localhost:3000
```

**Step 5: Fix First Error (Variable)**
- Address the first error found in logs
- Restart with `docker-compose down && docker-compose up`
- Repeat until all services healthy

**Step 6: End-to-End Test (10 minutes)**
```bash
# Open browser
open http://localhost:3000

# Create project
# Create task
# Drag task
# Verify persistence

# Test MCP
npx mcp-remote http://localhost:8051/mcp
```

### Common Issues Quick Reference

| Symptom | Likely Cause | Quick Fix |
|---------|--------------|-----------|
| "No such file: .env" | Missing environment file | `cp .env.example .env` |
| "Address already in use" | Port conflict | `lsof -i :PORT` then kill process |
| "Connection refused" to db | Database not ready | Add health check dependency |
| "Module not found" in backend | Dependencies not installed | Check Dockerfile RUN commands |
| "Permission denied: start.sh" | Not executable | `chmod +x backend/start.sh` |
| Database init.sql not running | Volume persists old data | `docker-compose down -v` |
| Frontend can't reach backend | CORS or wrong API URL | Check VITE_API_URL and CORS_ORIGINS |
| "pg_isready" fails | Wrong connection string | Verify DATABASE_URL matches docker-compose |
| MCP server not responding | Failed to start in background | Check start.sh logs for MCP process |
| Frontend 404 errors | Vite not serving | Check --host flag in Dockerfile CMD |

## Estimated Effort

**Phase 1: Debug and Fix**
- **Pre-flight checks and setup**: 10 minutes
- **First docker-compose up attempt**: 5 minutes
- **Debugging first error**: 15-45 minutes (depends on complexity)
- **Iterative fixes**: 20-60 minutes (2-4 rounds)
- **End-to-end validation**: 15 minutes
- **Subtotal**: 1-2.5 hours

**Phase 2: Clean Up References**
- **Search for old references**: 10 minutes
- **Update documentation**: 15 minutes
- **Update code comments**: 10 minutes
- **Final testing**: 10 minutes
- **Subtotal**: 45 minutes

**Total Estimated Effort**: 2-3.5 hours

**Likely Fastest Path**: 1 hour if the issue is just missing `.env` or simple port conflict

**Likely Slowest Path**: 4 hours if there are multiple compounding issues (dependency conflicts + database schema + TypeScript errors)

## Risk Mitigation

### Risk 1: Complex Dependency Issues
**Likelihood**: Medium
**Impact**: High (could take hours to debug)
**Mitigation**:
- Check pyproject.toml for compatible versions first
- Compare to working Archon dependencies
- Use `uv pip list` in container to verify installs
**Fallback**: Can update dependency versions if needed (no data to lose)

### Risk 2: Unknown Breaking Changes After Move
**Likelihood**: Medium
**Impact**: Medium
**Mitigation**:
- Systematic grep for old paths
- Check git history for what changed in move
- Verify all relative imports still work
**Fallback**: Can reference original PRP or git history to restore

### Risk 3: Docker Networking Issues
**Likelihood**: Low
**Impact**: Medium
**Mitigation**:
- Use standard docker-compose patterns
- Reference working Archon setup
- Verify service name resolution with `docker exec ... ping db`
**Fallback**: Can simplify network config or use host networking temporarily

### Risk 4: Database Schema Mismatch
**Likelihood**: Low
**Impact**: Medium
**Mitigation**:
- Always start with `docker-compose down -v` to ensure clean slate
- Verify init.sql runs by checking logs
- Can manually run SQL if needed
**Fallback**: Can recreate database from scratch (no data loss concern)

### Risk 5: Frontend Build Complexity
**Likelihood**: Medium
**Impact**: Low (can be fixed without affecting backend)
**Mitigation**:
- Check for TypeScript errors first: `npx tsc --noEmit`
- Verify all imports are correct
- Test Vite locally before Docker
**Fallback**: Can fix TypeScript errors incrementally, run with errors temporarily

## Validation Approach

### Automated Validation Script

Create a validation script at `infra/task-manager/validate.sh`:

```bash
#!/bin/bash
set -e

echo "🔍 Task Manager Validation Script"
echo "=================================="

# Check services running
echo "1. Checking Docker services..."
docker-compose ps | grep -q "taskmanager-db.*healthy" && echo "✅ Database healthy" || echo "❌ Database not healthy"
docker-compose ps | grep -q "taskmanager-backend.*healthy" && echo "✅ Backend healthy" || echo "❌ Backend not healthy"
docker-compose ps | grep -q "taskmanager-frontend.*Up" && echo "✅ Frontend running" || echo "❌ Frontend not running"

# Check health endpoints
echo "2. Checking health endpoints..."
curl -sf http://localhost:8000/health > /dev/null && echo "✅ Backend API responding" || echo "❌ Backend API not responding"
curl -sf http://localhost:8051/health > /dev/null && echo "✅ MCP server responding" || echo "❌ MCP server not responding"
curl -sf http://localhost:3000 > /dev/null && echo "✅ Frontend responding" || echo "❌ Frontend not responding"

# Check database connectivity
echo "3. Checking database..."
docker exec taskmanager-db psql -U taskuser -d taskmanager -c "\dt" > /dev/null 2>&1 && echo "✅ Database accessible" || echo "❌ Database not accessible"

echo "=================================="
echo "Validation complete!"
```

### Manual Validation Checklist

Use the Success Criteria section above as the manual checklist.

## Open Questions for PRP Execution

1. **What specific error is preventing the app from working?**
   - Answer: Need to check logs with `docker-compose up` to see first error

2. **Are there any port conflicts on the host machine?**
   - Answer: Check with `lsof -i :3000 :8000 :8051 :5432` before starting

3. **Does the .env file exist?**
   - Answer: Most likely NO - needs to be created from .env.example

4. **Did the move break any relative paths in code?**
   - Answer: Need to grep for "task-management-ui" to find hardcoded references

5. **Are backend dependencies compatible?**
   - Answer: Need to verify asyncpg + FastAPI + FastMCP versions work together

6. **Is the database schema properly initialized?**
   - Answer: Check with `docker exec` into db and run `\dt` in psql

7. **Is start.sh executable?**
   - Answer: Check with `ls -l backend/start.sh` or try running container

8. **Should we rename docker volumes/containers for consistency?**
   - Decision: NO - keep current names, they work fine (taskmanager-* is consistent enough)

9. **Should we update package.json name field?**
   - Decision: OPTIONAL for Phase 2 - not user-facing, low priority

10. **Do we need to update any vibes main documentation?**
    - Answer: Check main vibes README.md for task manager references

## Success Metrics

**Current State** (Baseline):
- Location: ✅ `infra/task-manager/` (already moved)
- Status: ❌ Never worked, services not starting
- Error state: Unknown (no logs captured yet)
- Usability: ❌ Cannot use at all

**Target State** (Phase 1 Complete):
- Location: ✅ `infra/task-manager/` (unchanged)
- Status: ✅ All services healthy and running
- Error state: Clean logs, no errors
- Usability: ✅ Fully functional UI + API + MCP
- Performance: Sub-second response times
- Stability: Runs for hours without crashes

**Target State** (Phase 2 Complete):
- Documentation: ✅ All references to "task-manager"
- Consistency: ✅ Naming aligned across codebase
- User experience: ✅ Clear, accurate documentation
- Production ready: ✅ Can be used confidently in vibes ecosystem

## Additional Context

### Why This Feature Matters

**Business Value**
- Archon MCP server needs working task management
- Claude Code integration requires functional MCP tools
- Vibes ecosystem needs centralized task tracking
- Developers need UI for task visibility

**Technical Value**
- Validates Docker Compose patterns for other services
- Demonstrates full-stack MCP integration
- Proves React + FastAPI + PostgreSQL stack
- Serves as reference for future infra services

**User Experience**
- Cannot currently use task manager at all (broken)
- Once fixed, provides both UI and programmatic access
- Enables seamless task creation from Claude Code
- Allows visual task management in browser

### Key Insights from Archon Research

**Working Patterns to Replicate**:
1. Archon's health check strategy is robust - use same pattern
2. Environment variable defaults in docker-compose prevent errors
3. Named volumes prevent permission issues
4. Proper dependency chains (service_healthy) prevent race conditions
5. Hot reload volumes speed up development iteration

**Common Pitfalls to Avoid**:
1. Starting backend before database is truly ready (not just "up")
2. Hardcoding localhost instead of using service names
3. Missing .env file (catches everyone at least once)
4. Port conflicts from other development services
5. Not using `docker-compose down -v` to ensure clean slate

**Best Practices Observed**:
1. Always provide .env.example with sane defaults
2. Use `${VAR:-default}` pattern for all environment variables
3. Include detailed comments in docker-compose.yml
4. Provide health check endpoints for all services
5. Use multi-stage builds to minimize image size
6. Mount source code for hot reload in development
7. Exclude node_modules and __pycache__ from volumes

### Integration Points

**With Archon**:
- Task manager is designed to be used via Archon MCP server
- Archon will use task manager MCP tools to create/update tasks
- Claude Code (via Archon) will manage development tasks
- UI provides visibility into AI-managed tasks

**With Vibes Ecosystem**:
- Part of the infra/ services family
- Follows same patterns as archon, litellm, supabase
- Uses standard Docker Compose setup
- Integrates with Claude Code workflow

**With Development Workflow**:
- Tasks created during PRP execution
- Progress tracking for multi-stage PRPs
- Sprint planning and backlog management
- Team coordination and work distribution

## Files Requiring Attention

### Critical Files (Must Review)
1. `infra/task-manager/.env` - **Likely missing, needs creation**
2. `infra/task-manager/docker-compose.yml` - Verify health checks
3. `infra/task-manager/backend/Dockerfile` - Check uv install process
4. `infra/task-manager/backend/start.sh` - Verify executable and correct
5. `infra/task-manager/frontend/Dockerfile` - Check npm ci process
6. `infra/task-manager/backend/pyproject.toml` - Verify dependency versions
7. `infra/task-manager/frontend/package.json` - Verify dependency versions

### Secondary Files (Check During Phase 2)
1. `infra/task-manager/README.md` - Update path references
2. `infra/task-manager/backend/src/main.py` - Check for old names
3. `infra/task-manager/backend/src/mcp_server.py` - Check server name
4. `infra/task-manager/frontend/index.html` - Check title tag
5. `prps/task_management_ui.md` - Update for historical reference
6. Main vibes `README.md` - Check for task manager mentions

### Configuration Files (Verify Correctness)
1. `.env.example` - Template is correct, need to copy to `.env`
2. `backend/alembic.ini` - Database URL configuration
3. `frontend/vite.config.ts` - Proxy and server settings
4. `frontend/tsconfig.json` - Path resolution
5. `backend/src/config/database.py` - Connection pool settings

## Conclusion

This feature analysis provides a comprehensive foundation for debugging and fixing the task manager system. The primary focus should be on Phase 1: getting all services running healthy with proper connectivity. Phase 2 (cleanup) is straightforward once the system works.

**Key Success Factors**:
1. Systematic debugging approach (don't try to fix everything at once)
2. Reference working Archon patterns extensively
3. Start with most likely issues (missing .env, port conflicts)
4. Use clean slate approach (docker-compose down -v) between attempts
5. Validate at each layer (db → backend → frontend → end-to-end)

**Expected Outcome**:
A fully functional task manager system that serves as a reliable component of the vibes ecosystem, providing both UI-based task management and MCP-based programmatic access for AI-assisted development workflows.
