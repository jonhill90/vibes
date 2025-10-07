# Examples Curated: rename_task_manager

## Summary

Extracted 8 code examples to the examples directory. All examples come from working services in the vibes ecosystem, providing proven patterns for Docker Compose orchestration, health checks, and database initialization.

## Files Created

1. **docker-compose-archon.yml**: Multi-service Docker Compose with robust health checks (9/10 relevance)
2. **docker-compose-litellm.yml**: Simple service health check pattern (7/10 relevance)
3. **postgres-healthcheck.yml**: PostgreSQL health check with pg_isready (10/10 relevance)
4. **env-example-pattern.env**: Comprehensive environment configuration template (10/10 relevance)
5. **backend-startup-script.sh**: Multi-process startup script for Docker (10/10 relevance)
6. **backend-dockerfile-multistage.dockerfile**: Python multi-stage build with uv (10/10 relevance)
7. **frontend-dockerfile-vite.dockerfile**: Vite dev server Dockerfile (10/10 relevance)
8. **database-init-schema.sql**: Complete PostgreSQL schema with best practices (10/10 relevance)
9. **README.md**: Comprehensive guide with usage instructions and pattern explanations

## Key Patterns Extracted

### Pattern 1: Health Checks with start_period
**From**: Archon, LiteLLM, Supabase
**Relevance**: Critical for preventing premature health check failures

All working services use generous `start_period` values (30-60 seconds) to allow services time to initialize before health checks begin failing. This prevents race conditions and cascading failures.

Example:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s  # KEY: Prevents premature failures
```

### Pattern 2: Service Dependencies with Conditions
**From**: Archon, Supabase
**Relevance**: Essential for proper service startup order

Services must wait for dependencies to be HEALTHY, not just started. This prevents backends from attempting to connect to databases that aren't ready yet.

Example:
```yaml
depends_on:
  db:
    condition: service_healthy  # Not service_started
```

### Pattern 3: PostgreSQL Health Check
**From**: Supabase
**Relevance**: Exact pattern needed for task manager

The `pg_isready` command is the official PostgreSQL health check tool. It verifies the database is ready to accept connections, not just that the port is open.

Example:
```yaml
healthcheck:
  test: ["CMD", "pg_isready", "-U", "${POSTGRES_USER}", "-d", "${POSTGRES_DB}"]
  interval: 5s
  timeout: 5s
  retries: 10  # Database needs more retries
```

### Pattern 4: Multi-Process Docker Startup
**From**: Task Manager backend
**Relevance**: Required for running both MCP and FastAPI

The startup script runs MCP server in background and FastAPI in foreground, using `exec` for proper signal handling during Docker shutdown.

Example:
```bash
python -m src.mcp_server &
MCP_PID=$!
exec uvicorn src.main:app --host 0.0.0.0 --port "${API_PORT:-8000}"
```

### Pattern 5: Vite --host Flag
**From**: Task Manager frontend
**Relevance**: Critical for Vite to work in Docker

Vite must use the `--host` flag to listen on 0.0.0.0 instead of localhost, otherwise Docker port forwarding won't work.

Example:
```dockerfile
CMD ["npm", "run", "dev", "--", "--host"]
```

### Pattern 6: Environment Variable Defaults
**From**: All Docker Compose examples
**Relevance**: Prevents missing variable errors

Using `${VAR:-default}` pattern throughout provides fallback values and makes the configuration self-documenting.

Example:
```yaml
POSTGRES_DB: ${POSTGRES_DB:-taskmanager}
POSTGRES_USER: ${POSTGRES_USER:-taskuser}
```

### Pattern 7: Database Init Scripts
**From**: Task Manager, Supabase
**Relevance**: Ensures schema is created on first run

Mounting SQL files to `/docker-entrypoint-initdb.d` causes PostgreSQL to auto-run them on first container start.

Example:
```yaml
volumes:
  - ./database:/docker-entrypoint-initdb.d:ro
```

### Pattern 8: Multi-Stage Dockerfile
**From**: Task Manager backend
**Relevance**: Faster builds and smaller images

Separating dependency installation (builder stage) from runtime reduces final image size and improves build caching.

Example:
```dockerfile
FROM python:3.12-slim AS builder
RUN uv pip install -r pyproject.toml

FROM python:3.12-slim
COPY --from=builder /venv /venv
```

## Recommendations for PRP Assembly

### 1. Reference the Examples Directory in PRP

Include in "All Needed Context" section:
```markdown
**Code Examples**: See prps/rename_task_manager/examples/ for:
- Working Docker Compose patterns (Archon, LiteLLM)
- PostgreSQL health check implementation (Supabase)
- Multi-process startup script (task manager backend)
- Complete database schema (task manager)
```

### 2. Include Key Patterns in Implementation Blueprint

Reference specific examples when describing implementation steps:

**Step 1: Verify Environment Configuration**
- Pattern: env-example-pattern.env
- Action: Copy .env.example to .env if missing

**Step 2: Fix Health Checks**
- Pattern: postgres-healthcheck.yml
- Action: Update db service to use pg_isready with correct credentials

**Step 3: Fix Service Dependencies**
- Pattern: docker-compose-archon.yml (lines 94-96)
- Action: Change depends_on to use condition: service_healthy

**Step 4: Verify Backend Startup**
- Pattern: backend-startup-script.sh
- Action: Check start.sh has execute permissions

**Step 5: Fix Frontend Dev Server**
- Pattern: frontend-dockerfile-vite.dockerfile (line 23)
- Action: Ensure Vite uses --host flag

### 3. Direct Implementer to Study README Before Coding

The README contains comprehensive "What to Mimic/Adapt/Skip" sections for each example. Implementer should:
1. Read all 8 example files
2. Study the README sections for relevant patterns
3. Note which patterns apply to which debugging steps
4. Apply patterns systematically

### 4. Use Examples for Validation

After implementing fixes, validate against examples:
- Does health check match postgres-healthcheck.yml pattern?
- Do service dependencies use condition: service_healthy?
- Does start.sh match the multi-process pattern?
- Is .env file present with correct structure?

## Quality Assessment

### Coverage: 10/10
Examples cover all critical aspects identified in feature-analysis.md:
- Docker Compose configuration (3 examples)
- Health check patterns (3 examples)
- Database initialization (1 example)
- Multi-stage builds (2 examples)
- Environment configuration (1 example)
- Startup scripts (1 example)

### Relevance: 9/10
7 out of 8 examples have 10/10 relevance ratings. The single 7/10 (LiteLLM) provides a fallback health check pattern if the preferred Python-based check doesn't work.

All examples come from working services in the vibes ecosystem or the task manager's own codebase, ensuring patterns are proven and applicable.

### Completeness: 10/10
All examples are self-contained with:
- Source attribution headers
- Pattern descriptions
- Relevance ratings
- Complete, runnable code

The README provides:
- "What to Mimic/Adapt/Skip" for each example
- Pattern highlights with explanations
- Usage instructions
- Integration guidance for PRP

### Overall: 9.7/10

**Strengths**:
- All examples from working code
- Comprehensive coverage of requirements
- Detailed documentation in README
- Clear attribution and relevance ratings
- Practical "What to Mimic/Adapt/Skip" guidance

**Areas for Improvement**:
- Could include debugging examples (logs, common errors)
- Could add validation script example
- Could show before/after comparisons

## Common Issues Addressed by Examples

### Issue 1: Missing .env File
**Example**: env-example-pattern.env
**Solution**: Copy .env.example to .env
**Why This Works**: Docker Compose needs environment variables defined

### Issue 2: Backend Starts Before Database Ready
**Example**: docker-compose-archon.yml (depends_on with condition)
**Solution**: Use `condition: service_healthy` in depends_on
**Why This Works**: Backend waits for database health check to pass

### Issue 3: Database Health Check Fails
**Example**: postgres-healthcheck.yml
**Solution**: Use pg_isready with correct user and database name
**Why This Works**: pg_isready is official PostgreSQL readiness check

### Issue 4: MCP Server Not Starting
**Example**: backend-startup-script.sh
**Solution**: Verify start.sh runs MCP in background before FastAPI
**Why This Works**: Both processes need to run simultaneously

### Issue 5: Frontend Can't Connect from Browser
**Example**: frontend-dockerfile-vite.dockerfile
**Solution**: Add --host flag to Vite dev command
**Why This Works**: Vite needs to listen on 0.0.0.0 for Docker port forwarding

### Issue 6: Database Schema Not Created
**Example**: database-init-schema.sql + docker-compose pattern
**Solution**: Mount init.sql to /docker-entrypoint-initdb.d
**Why This Works**: PostgreSQL auto-runs scripts in this directory on first start

### Issue 7: Service Health Checks Failing Too Soon
**Example**: All health check examples (start_period)
**Solution**: Add generous start_period (40-60s) to health checks
**Why This Works**: Gives services time to initialize before checks begin

## Next Steps for Implementer

### Phase 1: Study Examples (10 minutes)
1. Read examples/README.md completely
2. Review each example file
3. Note patterns that apply to debugging steps
4. Understand "What to Mimic/Adapt/Skip" for each

### Phase 2: Apply Patterns (1-2 hours)
1. **Environment Setup**: Copy .env.example to .env
2. **Database Health Check**: Update docker-compose.yml db service
3. **Service Dependencies**: Add condition: service_healthy
4. **Backend Startup**: Verify start.sh permissions and content
5. **Frontend Server**: Check Vite --host flag
6. **Health Check Timing**: Add start_period to all services

### Phase 3: Validate (15 minutes)
1. Run `docker-compose down -v` for clean slate
2. Run `docker-compose up` and watch logs
3. Verify all services reach "healthy" status
4. Test health endpoints manually
5. Verify end-to-end functionality

### Phase 4: Document Changes (15 minutes)
1. Note which examples solved which issues
2. Update task manager README with working setup
3. Document any deviations from example patterns
4. Create validation script based on patterns

## Files Reference for PRP

**Examples Directory**: /Users/jon/source/vibes/prps/rename_task_manager/examples/

**Key Files**:
- README.md: Comprehensive guide (start here)
- docker-compose-archon.yml: Multi-service reference
- postgres-healthcheck.yml: Database health check
- backend-startup-script.sh: Multi-process startup
- env-example-pattern.env: Environment template
- database-init-schema.sql: Complete schema

**Output Document**: /Users/jon/source/vibes/prps/rename_task_manager/planning/examples-to-include.md (this file)

---

Generated: 2025-10-07
Feature: rename_task_manager
Archon Project ID: 90a6faab-c4c4-47d8-9889-f3cd2d60405c
Total Examples: 8 code files + 1 README
Total Patterns Documented: 8 major patterns
Quality Score: 9.7/10
