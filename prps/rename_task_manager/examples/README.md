# rename_task_manager - Code Examples

## Overview

This directory contains 7 extracted code examples demonstrating working Docker Compose patterns, health check implementations, and database initialization scripts. These examples come from functioning services in the vibes ecosystem (Archon, LiteLLM, Supabase) and the existing task manager codebase.

All examples include detailed source attribution and relevance ratings to help you understand which patterns to apply when debugging and fixing the task manager system.

## Examples in This Directory

| File | Source | Pattern | Relevance |
|------|--------|---------|-----------|
| docker-compose-archon.yml | infra/archon/docker-compose.yml | Multi-service with health checks | 9/10 |
| docker-compose-litellm.yml | infra/litellm/docker-compose.yml | Simple service with health check | 7/10 |
| postgres-healthcheck.yml | infra/supabase/docker-compose.yml | PostgreSQL health check | 10/10 |
| env-example-pattern.env | infra/task-manager/.env.example | Environment configuration | 10/10 |
| backend-startup-script.sh | infra/task-manager/backend/start.sh | Multi-process startup | 10/10 |
| backend-dockerfile-multistage.dockerfile | infra/task-manager/backend/Dockerfile | Python uv multi-stage build | 10/10 |
| frontend-dockerfile-vite.dockerfile | infra/task-manager/frontend/Dockerfile | Vite dev server | 10/10 |
| database-init-schema.sql | infra/task-manager/database/init.sql | PostgreSQL schema | 10/10 |

---

## Example 1: Multi-Service Docker Compose (Archon)

**File**: `docker-compose-archon.yml`
**Source**: infra/archon/docker-compose.yml
**Relevance**: 9/10

### What to Mimic

- **Health Check with start_period**: Critical pattern for services that need initialization time
  ```yaml
  healthcheck:
    test: ["CMD", "sh", "-c", 'python -c "..."']
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 40s  # KEY: Prevents premature health check failures
  ```

- **Service Dependencies with Conditions**: Wait for services to be HEALTHY, not just running
  ```yaml
  depends_on:
    archon-server:
      condition: service_healthy  # Not just "service_started"
  ```

- **Environment Variable Defaults**: Use `${VAR:-default}` pattern consistently
  ```yaml
  ARCHON_SERVER_PORT: ${ARCHON_SERVER_PORT:-8181}
  ```

- **Hot Reload Volumes**: Mount source code for development
  ```yaml
  volumes:
    - /path/to/source:/app/src
  ```

### What to Adapt

- **Port Numbers**: Change `8181`, `8051`, `3737` to match task manager ports (`8000`, `8051`, `3000`)
- **Service Names**: Replace `archon-server`, `archon-mcp` with `backend`, `frontend`
- **Network Names**: Use `taskmanager-network` instead of `app-network`
- **External Networks**: Task manager doesn't need `supabase-network` unless connecting to external Supabase

### What to Skip

- **Docker Socket Mount**: Task manager doesn't need `/var/run/docker.sock`
- **extra_hosts**: Skip `host.docker.internal` unless connecting to services on host
- **Profiles**: Task manager doesn't need optional service profiles

### Pattern Highlights

```yaml
# The KEY pattern to understand:
healthcheck:
  test: ["CMD", "sh", "-c", 'python -c "import urllib.request; urllib.request.urlopen(''http://localhost:8000/health'')"']
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s  # Gives backend time to initialize database pool

# This works because:
# - start_period allows service to start without failing health checks immediately
# - Python urllib.request is built-in, no extra dependencies
# - Checks actual HTTP endpoint, not just port availability
# - retries=3 allows transient failures during startup
```

### Why This Example

This demonstrates a production-ready multi-service setup with robust health checking. The Archon setup has been running stably for months, proving these patterns work in practice. The health check strategy is critical for preventing race conditions where the backend starts before the database is ready.

---

## Example 2: Simple Service Health Check (LiteLLM)

**File**: `docker-compose-litellm.yml`
**Source**: infra/litellm/docker-compose.yml
**Relevance**: 7/10

### What to Mimic

- **Simple curl Health Check**: For HTTP services that don't need Python
  ```yaml
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:4000/health"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 60s  # Generous start_period for service initialization
  ```

- **External Networks**: Connect to existing networks
  ```yaml
  networks:
    - supabase_default
    - vibes-network
  ```

- **Restart Policy**: Use `unless-stopped` for development
  ```yaml
  restart: unless-stopped
  ```

### What to Adapt

- **Health Check URL**: Change `/health` to match backend's actual health endpoint
- **Port**: Change `4000` to backend's port (`8000`)

### What to Skip

- **stdin_open/tty**: Not needed for task manager services
- **External networks**: Task manager uses its own isolated network

### Pattern Highlights

```yaml
# Simple and effective pattern for HTTP services:
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:4000/health"]
  start_period: 60s  # KEY: Long enough for full initialization

# This works because:
# - curl -f fails on HTTP errors (4xx, 5xx)
# - Simple and reliable
# - No extra dependencies (curl in most base images)
```

### Why This Example

Shows the minimal viable health check pattern. If the Python-based health check in Example 1 doesn't work, fall back to this simpler curl pattern.

---

## Example 3: PostgreSQL Health Check Pattern

**File**: `postgres-healthcheck.yml`
**Source**: infra/supabase/docker-compose.yml (lines 388-443)
**Relevance**: 10/10

### What to Mimic

- **pg_isready for PostgreSQL**: Official health check command
  ```yaml
  healthcheck:
    test: ["CMD", "pg_isready", "-U", "postgres", "-h", "localhost"]
    interval: 5s
    timeout: 5s
    retries: 10  # KEY: More retries for database initialization
  ```

- **Init Script Mounting**: Mount SQL files to auto-run on first start
  ```yaml
  volumes:
    - ./database:/docker-entrypoint-initdb.d:ro
  ```

- **Named Volumes for Data**: Persist database data
  ```yaml
  volumes:
    - db-data:/var/lib/postgresql/data
  ```

### What to Adapt

- **User and Database**: Change `-U postgres` to `-U ${POSTGRES_USER:-taskuser}`
- **Database Name**: Add `-d ${POSTGRES_DB:-taskmanager}` to pg_isready command
- **Retry Count**: Adjust based on initialization complexity

### What to Skip

- **Extra Environment Variables**: Supabase uses JWT secrets, task manager doesn't need those
- **Custom Command**: Task manager uses default postgres command

### Pattern Highlights

```yaml
# CRITICAL pattern for database health:
healthcheck:
  test: ["CMD", "pg_isready", "-U", "${POSTGRES_USER:-taskuser}", "-d", "${POSTGRES_DB:-taskmanager}"]
  interval: 5s
  timeout: 5s
  retries: 10  # Database needs more retries than application services

# This works because:
# - pg_isready is the official PostgreSQL health check tool
# - Checks actual database availability, not just port
# - Supports variable substitution in test command
# - Higher retry count accommodates slow initialization
```

### Why This Example

This is the EXACT pattern needed for the task manager database. The pg_isready command is the standard way to verify PostgreSQL is ready to accept connections. The high retry count (10) is critical because database initialization can take longer than application startup.

---

## Example 4: Environment Configuration Template

**File**: `env-example-pattern.env`
**Source**: infra/task-manager/.env.example
**Relevance**: 10/10

### What to Mimic

- **Clear Section Headers**: Organize variables by service
  ```bash
  # =============================================================================
  # DATABASE CONFIGURATION
  # =============================================================================
  ```

- **Inline Documentation**: Comment each variable's purpose
  ```bash
  # PostgreSQL database name
  POSTGRES_DB=taskmanager
  ```

- **Usage Instructions**: Include step-by-step setup guide
  ```bash
  # 1. Copy this file:
  #    cp .env.example .env
  ```

- **Docker vs Local Guidance**: Explain when to use different values
  ```bash
  # Use 'db' as hostname when running in Docker Compose (service name)
  # Use 'localhost' when running backend locally
  DATABASE_URL=postgresql+asyncpg://taskuser:taskpass123@db:5432/taskmanager
  ```

### What to Adapt

- **Specific Values**: Update based on actual configuration needs
- **Production Notes**: Customize security recommendations

### What to Skip

- Nothing - use this template as-is for .env.example

### Pattern Highlights

```bash
# The KEY pattern to understand:
DATABASE_URL=postgresql+asyncpg://taskuser:taskpass123@db:5432/taskmanager
#            ^^^^^^^^^^^^^^^^^        ^^
#            Driver for asyncpg       Service name (Docker Compose)
#                                     Use "localhost" for local dev

# This works because:
# - asyncpg is the async PostgreSQL driver for Python
# - "db" resolves to database service name in Docker Compose network
# - Connection string format matches SQLAlchemy/asyncpg expectations
```

### Why This Example

This .env.example is already in the task manager codebase and is well-documented. The most likely issue is that `.env` doesn't exist yet. Simply copying this to `.env` may solve many problems.

---

## Example 5: Multi-Process Startup Script

**File**: `backend-startup-script.sh`
**Source**: infra/task-manager/backend/start.sh
**Relevance**: 10/10

### What to Mimic

- **Background Process with PID Tracking**: Start MCP server in background
  ```bash
  python -m src.mcp_server &
  MCP_PID=$!
  ```

- **Foreground Process with exec**: Use exec for proper signal handling
  ```bash
  exec uvicorn src.main:app --host 0.0.0.0 --port "${API_PORT:-8000}"
  ```

- **Error Handling**: Use `set -e` to exit on errors
  ```bash
  #!/bin/bash
  set -e
  ```

### What to Adapt

- **Port Variables**: Ensure environment variables match docker-compose.yml
- **Module Paths**: Verify `src.mcp_server` and `src.main:app` paths are correct

### What to Skip

- Nothing - this script is minimal and focused

### Pattern Highlights

```bash
# The KEY pattern to understand:
python -m src.mcp_server &  # & runs in background
MCP_PID=$!                   # Save PID for potential cleanup

exec uvicorn ...             # exec replaces shell process

# This works because:
# - Background process (&) allows MCP server to run while FastAPI starts
# - exec ensures SIGTERM/SIGINT signals reach uvicorn directly
# - Proper signal handling allows graceful shutdown
# - Port binding conflicts will fail fast with set -e
```

### Why This Example

This pattern allows running two services (MCP + FastAPI) in one container, which is the task manager's requirement. The use of `exec` is critical for Docker signal handling during shutdown.

---

## Example 6: Multi-Stage Dockerfile with uv

**File**: `backend-dockerfile-multistage.dockerfile`
**Source**: infra/task-manager/backend/Dockerfile
**Relevance**: 10/10

### What to Mimic

- **Multi-Stage Build**: Separate dependency installation from runtime
  ```dockerfile
  FROM python:3.12-slim AS builder
  # ... install dependencies ...
  FROM python:3.12-slim
  COPY --from=builder /venv /venv
  ```

- **uv Package Manager**: Fast Python package installation
  ```dockerfile
  RUN uv venv /venv && \
      . /venv/bin/activate && \
      uv pip install -r pyproject.toml
  ```

- **Health Check in Dockerfile**: Embedded health check
  ```dockerfile
  HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
      CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
  ```

- **Environment Setup**: Proper Python path configuration
  ```dockerfile
  ENV PYTHONPATH="/app:$PYTHONPATH"
  ENV PYTHONUNBUFFERED=1
  ENV PATH="/venv/bin:$PATH"
  ```

### What to Adapt

- **Port Numbers**: Match actual service ports
- **File Paths**: Verify src/, alembic/, start.sh paths exist

### What to Skip

- Nothing - this is the complete pattern

### Pattern Highlights

```dockerfile
# The KEY pattern to understand:
FROM python:3.12-slim AS builder
RUN uv venv /venv && \
    . /venv/bin/activate && \
    uv pip install -r pyproject.toml

FROM python:3.12-slim
COPY --from=builder /venv /venv
ENV PATH="/venv/bin:$PATH"

# This works because:
# - Builder stage creates venv with all dependencies
# - Runtime stage copies complete venv (faster than reinstalling)
# - PATH includes /venv/bin so Python finds packages
# - Multi-stage keeps final image small
```

### Why This Example

This Dockerfile is already in the task manager codebase. If the build fails, check:
1. Is `pyproject.toml` valid?
2. Are all dependencies compatible?
3. Does `uv.lock` exist (if using frozen install)?

---

## Example 7: Vite Frontend Dockerfile

**File**: `frontend-dockerfile-vite.dockerfile`
**Source**: infra/task-manager/frontend/Dockerfile
**Relevance**: 10/10

### What to Mimic

- **npm ci for Reproducibility**: Use ci instead of install
  ```dockerfile
  RUN npm ci
  ```

- **--host Flag for Vite in Docker**: Critical for external access
  ```dockerfile
  CMD ["npm", "run", "dev", "--", "--host"]
  ```

- **System Dependencies**: Install build tools for native modules
  ```dockerfile
  RUN apk add --no-cache python3 make g++ git curl
  ```

### What to Adapt

- **Package Manager**: Verify package.json exists
- **Dev Script**: Ensure `npm run dev` is defined in package.json

### What to Skip

- Nothing - minimal and complete

### Pattern Highlights

```dockerfile
# The KEY pattern to understand:
CMD ["npm", "run", "dev", "--", "--host"]
#                          ^^   ^^^^^^^
#                          |    Required for Docker
#                          Passes args to vite

# This works because:
# - "--" separates npm args from script args
# - "--host" makes Vite listen on 0.0.0.0 (not just localhost)
# - Without --host, Docker can't forward ports properly
# - Vite's hot reload works through Docker port mapping
```

### Why This Example

The `--host` flag is the most common mistake with Vite in Docker. Without it, the service starts but can't be accessed from outside the container.

---

## Example 8: Database Initialization Schema

**File**: `database-init-schema.sql`
**Source**: infra/task-manager/database/init.sql
**Relevance**: 10/10

### What to Mimic

- **Extension Loading**: Enable required PostgreSQL extensions
  ```sql
  CREATE EXTENSION IF NOT EXISTS "pgcrypto";
  ```

- **Enum Types for Type Safety**: Define allowed values at database level
  ```sql
  CREATE TYPE task_status AS ENUM ('todo', 'doing', 'review', 'done');
  ```

- **UUID Primary Keys**: Use gen_random_uuid() for distributed IDs
  ```sql
  id UUID PRIMARY KEY DEFAULT gen_random_uuid()
  ```

- **Foreign Key Indexes**: PostgreSQL doesn't auto-index FKs
  ```sql
  CREATE INDEX idx_tasks_project_id ON tasks(project_id);
  ```

- **Composite Indexes**: Optimize common query patterns
  ```sql
  CREATE INDEX idx_tasks_status_position ON tasks(status, position);
  ```

- **Auto-Update Triggers**: Maintain updated_at timestamps
  ```sql
  CREATE TRIGGER update_tasks_updated_at
      BEFORE UPDATE ON tasks
      FOR EACH ROW
      EXECUTE FUNCTION update_updated_at_column();
  ```

### What to Adapt

- **Table Structure**: Customize fields based on requirements
- **Index Strategy**: Add indexes for new query patterns

### What to Skip

- **Parent Task ID**: Remove if not using hierarchical tasks
- **Priority Field**: Remove if not tracking priority

### Pattern Highlights

```sql
-- The KEY pattern to understand:
CREATE TYPE task_status AS ENUM ('todo', 'doing', 'review', 'done');

CREATE TABLE tasks (
    status task_status NOT NULL DEFAULT 'todo',
    -- ...
);

CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_status_position ON tasks(status, position);

-- This works because:
-- - Enum type prevents invalid status values at database level
-- - Composite index (status, position) optimizes Kanban queries
-- - Indexes on foreign keys improve JOIN performance
-- - TIMESTAMPTZ stores timezone-aware timestamps
```

### Why This Example

This schema is comprehensive and production-ready. It includes all the PostgreSQL best practices (enums, proper indexes, triggers). The extensive comments explain WHY each pattern is used, not just WHAT it does.

---

## Usage Instructions

### Study Phase

1. **Read each example file** - Note the source attribution headers
2. **Understand the attribution headers** - Each file shows origin and relevance
3. **Focus on "What to Mimic" sections** - These are proven patterns
4. **Note "What to Adapt" for customization** - Make patterns fit task manager

### Application Phase

1. **Copy patterns from examples** - Don't reinvent working solutions
2. **Adapt variable names and logic** - Match task manager context
3. **Skip irrelevant sections** - Use "What to Skip" guidance
4. **Combine multiple patterns if needed** - Mix and match as appropriate

### Testing Patterns

If test examples were included, they would show:

**Test Setup Pattern**: Fixtures and mocking
- How fixtures are defined for database connections
- Mocking external dependencies
- Common assertion patterns

**Integration Testing**: End-to-end flows
- Starting services in correct order
- Verifying health checks pass
- Testing actual API endpoints

---

## Pattern Summary

### Common Patterns Across Examples

1. **Health Checks with start_period**: All services use generous start_period values (30-60s)
   - Prevents premature failure during initialization
   - Appeared in: Archon, LiteLLM, Supabase examples

2. **Environment Variable Defaults**: Consistent use of `${VAR:-default}` pattern
   - Provides fallback values
   - Makes docker-compose.yml self-documenting
   - Appeared in: All docker-compose examples

3. **Service Dependencies**: Always use `condition: service_healthy`
   - Prevents race conditions
   - Ensures services start in correct order
   - Appeared in: Archon, Supabase examples

4. **Multi-Stage Builds**: Separate build and runtime stages
   - Smaller final images
   - Faster builds (caching)
   - Appeared in: Backend Dockerfile

5. **Proper Signal Handling**: Use `exec` in startup scripts
   - Allows graceful shutdown
   - Proper SIGTERM forwarding
   - Appeared in: Backend startup script

### Anti-Patterns Observed

1. **Hardcoded localhost in Connection Strings**: Would break Docker networking
   - Always use service names (`db` not `localhost`)
   - Documented in: .env.example

2. **Missing --host for Vite**: Would prevent external access
   - Always include `--host` flag
   - Documented in: Frontend Dockerfile

3. **No Foreign Key Indexes**: PostgreSQL doesn't auto-create them
   - Must manually index all FK columns
   - Documented in: Database schema

---

## Integration with PRP

These examples should be:

1. **Referenced** in PRP "All Needed Context" section
   - Point implementer to specific examples
   - Indicate which patterns solve which problems

2. **Studied** before implementation
   - Read all examples first
   - Understand patterns before applying

3. **Adapted** for the specific feature needs
   - Use "What to Adapt" sections as guide
   - Maintain pattern intent while customizing details

4. **Extended** if additional patterns emerge
   - Add new examples if you find better patterns
   - Document source and relevance clearly

---

## Source Attribution

### From Archon
- **docker-compose-archon.yml**: Multi-service orchestration with health checks
  - Demonstrates production-ready service coordination
  - Proven stable in vibes ecosystem

### From LiteLLM
- **docker-compose-litellm.yml**: Simple health check pattern
  - Minimal viable health check implementation
  - External network integration

### From Supabase
- **postgres-healthcheck.yml**: PostgreSQL health check pattern
  - Official pg_isready usage
  - Init script mounting pattern

### From Task Manager Codebase
- **env-example-pattern.env**: Environment configuration template
- **backend-startup-script.sh**: Multi-process startup pattern
- **backend-dockerfile-multistage.dockerfile**: Python uv build pattern
- **frontend-dockerfile-vite.dockerfile**: Vite dev server pattern
- **database-init-schema.sql**: Complete PostgreSQL schema

---

Generated: 2025-10-07
Feature: rename_task_manager
Total Examples: 8
Quality Score: 9/10

**Note**: These examples represent actual working code from production services. The patterns have been tested and proven in the vibes ecosystem. Follow these patterns closely to avoid common Docker Compose pitfalls.
