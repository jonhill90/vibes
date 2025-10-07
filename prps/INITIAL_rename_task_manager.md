# INITIAL: Fix Task Manager

## FEATURE

Get the task manager system working. The directory has already been moved to `infra/task-manager/` but the application has never successfully run. Need to debug and fix all issues to get a working system, then clean up any lingering "task-management-ui" references.

**Current State**:
- ✅ Location: Already at `infra/task-manager/`
- ❌ Status: Never worked, services not starting
- ⚠️ References: Mix of "task-management-ui" and "task-manager" in code/docs
- ℹ️ Data: None (fresh install, no existing data to preserve)

**Core Requirements**:

**Phase 1 - Debug & Fix** (Priority):
- Investigate why services aren't starting (containers, logs, errors)
- Fix database initialization and connection
- Fix backend startup (dependencies, migrations, MCP server)
- Fix frontend build and startup
- Get all services running healthy
- Verify core functionality works end-to-end

**Phase 2 - Clean Up References** (Quick polish):
- Update remaining "task-management-ui" references to "task-manager"
- Update documentation with correct paths
- Ensure consistency across all user-facing content

**Why This Matters**:
- **It doesn't work**: Can't use a broken system
- **Clean slate**: No data to preserve means we can fix freely
- **Already moved**: Don't need to worry about relocation - just fix in place
- **Simple goal**: Get containers running → Get UI loading → Get MCP responding

## EXAMPLES

### Working Docker Compose Services in Vibes

**Reference patterns from working infra projects**:

1. **infra/archon/** - Full-stack MCP server
   - ✅ Services start cleanly with `docker-compose up`
   - ✅ Health checks work
   - ✅ All dependencies properly installed

2. **infra/litellm/** - LiteLLM proxy service
   - ✅ Clean startup
   - ✅ Port configuration works
   - ✅ Environment variables properly set

**What a working task-manager should look like**:
```bash
cd infra/task-manager
docker-compose up

# Expected output:
# ✅ taskmanager-db ... healthy
# ✅ taskmanager-backend ... healthy
# ✅ taskmanager-frontend ... running

# Should be accessible:
# http://localhost:3000 - Frontend UI
# http://localhost:8000 - Backend API
# http://localhost:8051 - MCP Server
```

## DOCUMENTATION

### Phase 1: Debugging the Broken System

**Common Issues to Investigate**:

1. **Docker Services Not Starting**:
   - Check if containers are running: `docker-compose ps`
   - Check logs for errors: `docker-compose logs`
   - Check if ports are already in use: `lsof -i :3000 :8000 :8051 :5432`
   - Verify docker-compose.yml syntax

2. **Database Issues**:
   - Check if database initialized: `docker-compose logs db`
   - Verify connection string in .env matches docker-compose
   - Check if init.sql ran successfully
   - Test connection: `docker exec -it taskmanager-db psql -U taskuser -d taskmanager`

3. **Backend Issues**:
   - Python dependency errors: Check pyproject.toml, verify uv.lock
   - Import errors: Check if src/ structure is correct
   - Database connection: Verify DATABASE_URL format
   - MCP server: Check if FastMCP installed and configured
   - Migrations: Check if Alembic migrations ran
   - Port conflicts: Verify 8000 and 8051 are free

4. **Frontend Issues**:
   - Node/npm errors: Check package.json, package-lock.json
   - Build errors: Check TypeScript compilation errors
   - Vite config: Verify vite.config.ts settings
   - API connection: Verify VITE_API_URL points to backend
   - CORS errors: Check backend CORS_ORIGINS includes frontend URL

5. **Configuration Issues**:
   - Missing .env file: Check if .env.example was copied
   - Wrong environment variables: Verify all required vars set
   - Path issues: Check if relative paths work after move

**Debugging Checklist**:
- [ ] Copy .env.example to .env if missing
- [ ] Verify all environment variables are set
- [ ] Check if ports are available (3000, 8000, 8051, 5432)
- [ ] Run `docker-compose down -v` to clean slate
- [ ] Run `docker-compose build --no-cache` to rebuild images
- [ ] Run `docker-compose up` and check logs for errors
- [ ] Fix errors one service at a time (db → backend → frontend)
- [ ] Verify database health: `docker-compose ps` shows healthy
- [ ] Verify backend health: `curl http://localhost:8000/health`
- [ ] Verify frontend loads: `curl http://localhost:3000`
- [ ] Verify MCP server: `curl http://localhost:8051/health`

**Expected Working State**:
```bash
# All services should show healthy/running
docker-compose ps

# Should return {"status": "healthy"}
curl http://localhost:8000/health

# Should return HTML
curl http://localhost:3000

# Should be accessible in browser
open http://localhost:3000
```

### Phase 2: Files to Update After Fix and Move
1. **docker-compose.yml**:
   - Container names: `taskmanager-*` → `task-manager-*` (optional, but more consistent)
   - Volume names: `taskmanager-db-data` → `task-manager-db-data`
   - Network names: `taskmanager-network` → `task-manager-network`

2. **README.md**:
   - Update directory paths in all code examples
   - Update quick start navigation instructions
   - Update references from "Task Management UI" to "Task Manager"

3. **Backend files**:
   - Search for "task-management-ui" or "taskmanager" in:
     - `backend/src/main.py` (app title, description)
     - `backend/src/mcp_server.py` (MCP server name)
     - Any log messages or comments

4. **Frontend files**:
   - `frontend/package.json` (name field)
   - `frontend/index.html` (title tag)
   - Any references in component comments

5. **Documentation**:
   - `prps/task_management_ui.md` → update internal paths
   - `prps/INITIAL_task_management_ui.md` → update for historical reference
   - Main vibes `README.md` if task manager is listed

6. **Environment files**:
   - `.env` and `.env.example` - check for hardcoded paths

## OTHER CONSIDERATIONS

### Fresh Start Advantage

**No existing data** means:
- ✅ Can freely rename volumes/networks if desired
- ✅ Can change any configuration without migration
- ✅ Can nuke everything with `docker-compose down -v` and start fresh
- ✅ No backup/restore needed
- ✅ Faster iteration on fixes

### Naming Decisions (Can change freely)

Since there's no data to preserve, we can choose any naming we want:

**Option A - Keep Current Names** (Less work):
- Container names: `taskmanager-db`, `taskmanager-backend`, `taskmanager-frontend`
- Volume: `taskmanager-db-data`
- Network: `taskmanager-network`
- Pro: No file changes needed
- Con: Inconsistent with directory name `task-manager`

**Option B - Rename Everything** (Cleaner):
- Container names: `task-manager-db`, `task-manager-backend`, `task-manager-frontend`
- Volume: `task-manager-db-data`
- Network: `task-manager-network`
- Pro: Consistent naming throughout
- Con: Requires updating docker-compose.yml

**Recommendation**: Do Option A for Phase 1 (get it working first), optionally do Option B in Phase 2 (polish).

### Debugging Strategy

**Step-by-step approach**:
1. Start from scratch: `docker-compose down -v` (nuke everything)
2. Check .env file exists with correct values
3. Build fresh: `docker-compose build --no-cache`
4. Start services: `docker-compose up`
5. Watch logs carefully for first error
6. Fix that error
7. Repeat steps 1-6 until all services healthy

### Testing Checklist

**Phase 1 - Basic functionality**:
- [ ] `.env` file exists with correct values
- [ ] `docker-compose up` starts all services without errors
- [ ] Database container healthy: `docker-compose ps` shows healthy
- [ ] Backend container healthy and logs show "Started MCP server"
- [ ] Frontend container running and logs show "ready in X ms"
- [ ] Database accessible: `curl http://localhost:8000/health/db`
- [ ] Backend accessible: `curl http://localhost:8000/health`
- [ ] Frontend accessible: `curl http://localhost:3000` returns HTML
- [ ] MCP server accessible: `curl http://localhost:8051/health`

**Phase 2 - End-to-end functionality**:
- [ ] Web UI loads in browser at http://localhost:3000
- [ ] No console errors in browser devtools
- [ ] Can create a project via UI
- [ ] Can create a task via UI
- [ ] Can drag task between Kanban columns
- [ ] MCP tools respond: `npx mcp-remote http://localhost:8051/mcp`
- [ ] Can create task via MCP and see it appear in UI

**Phase 3 - Documentation cleanup**:
- [ ] No references to "task-management-ui" in user-facing docs
- [ ] README paths point to `infra/task-manager/`
- [ ] All code examples work as written

## VALIDATION CRITERIA

**Phase 1 Success Criteria (Get It Working)**:
- [ ] All Docker services start without errors
- [ ] Database is healthy and accessible
- [ ] Backend API responds to health check
- [ ] Frontend loads in browser (http://localhost:3000)
- [ ] MCP server responds to health check
- [ ] Can create a project via UI
- [ ] Can create a task via UI
- [ ] Can drag task between Kanban columns
- [ ] MCP tools respond (via `npx mcp-remote`)
- [ ] Can create task via MCP and see it appear in UI

**Phase 2 Success Criteria (Clean Up References)**:
- [ ] No "task-management-ui" references in user-facing documentation
- [ ] All README paths point to `infra/task-manager/`
- [ ] All code examples work as written
- [ ] Container names consistent (decide on `taskmanager-*` vs `task-manager-*`)
- [ ] System still works identically after documentation updates

**Overall Success**:
- Task manager is fully functional for first time
- Can be used by Claude Code via MCP
- Can be managed by humans via web UI
- Documentation is clear and accurate
- Ready for actual use in vibes ecosystem

## ESTIMATED EFFORT

**Phase 1 - Get It Working**:
- **Investigation**: 10-20 minutes (check logs, identify issues)
- **Fixing**: 30-90 minutes (depends on issue complexity)
- **Testing**: 15-20 minutes (verify all features work)
- **Subtotal**: ~1-2 hours

**Phase 2 - Clean Up References**:
- **Search & replace**: 15-20 minutes (find "task-management-ui" references)
- **Documentation updates**: 10-15 minutes (README paths)
- **Testing**: 5 minutes (verify links work)
- **Subtotal**: ~30 minutes

**Total**: ~1.5-2.5 hours

**Likely fastest path**: 1 hour if issues are simple (e.g., missing .env or port conflict)

## RISKS & MITIGATION

**Risk 1**: Issue is complex and takes hours to debug
- **Mitigation**: Start with common issues first (ports, .env, dependencies)
- **Fallback**: Can rebuild from scratch using original PRP if needed

**Risk 2**: Fix one issue, break another
- **Mitigation**: Test after each fix with `docker-compose up`
- **Mitigation**: Use `docker-compose down -v` to start fresh if things get messy

**Risk 3**: Documentation updates break working system
- **Mitigation**: Do Phase 2 in separate commit after Phase 1 works
- **Mitigation**: Only update docs/comments, not functional code

**Risk 4**: Miss references to old name in code
- **Mitigation**: Use grep to find all instances:
  ```bash
  grep -r "task-management-ui" infra/task-manager/
  ```

**Risk 5**: Port conflicts with other services
- **Mitigation**: Check `lsof -i :3000 :8000 :8051 :5432` before starting
- **Mitigation**: Can change ports in .env if needed

## NEXT STEPS

**Recommended Approach**:
1. **Generate Full PRP**: Run `/generate-prp prps/INITIAL_rename_task_manager.md`
   - This will create detailed debugging steps
   - Will include specific commands to run
   - Will have validation checks at each step

2. **Execute PRP Phase 1**: Debug and fix the system
   - Follow systematic troubleshooting steps
   - Test after each fix
   - Get to working state

3. **Execute PRP Phase 2**: Clean up references
   - Quick search-and-replace
   - Update documentation
   - Final testing

4. **Commit**: Two commits (Phase 1 fixes, Phase 2 cleanup) or one combined

**Alternative - Just Start Debugging**:
If you want to start immediately:
```bash
cd infra/task-manager
docker-compose down -v      # Nuke everything
docker-compose build --no-cache
docker-compose up           # Watch for errors
```

Then generate PRP only if you get stuck or want systematic approach.

## LIKELY ISSUES (Based on Initial Move)

Since the system was already moved from `task-management-ui/` to `infra/task-manager/`, possible issues:

1. **Stale Containers**: Old containers still running with wrong paths
   - Solution: `docker-compose down -v && docker-compose up --build`

2. **Missing .env**: Environment file not present after move
   - Solution: Copy `.env.example` to `.env`

3. **Build Cache Issues**: Docker using old cached layers
   - Solution: `docker-compose build --no-cache`

4. **Port Conflicts**: Services from old location still running
   - Solution: Check `lsof -i :3000 :8000 :8051 :5432` and kill processes

5. **Database Not Initialized**: Volume exists but schema not created
   - Solution: Verify init.sql ran or run migrations manually

6. **Path References**: Code still referencing old paths
   - Solution: Grep for "task-management-ui" and update

7. **Dependency Issues**: Backend/frontend dependencies not installed
   - Backend: Missing FastMCP, asyncpg, or other Python deps
   - Frontend: Missing react-dnd, @tanstack/react-query, or other npm deps
   - Solution: Check Dockerfiles install all deps from package files

## OPEN QUESTIONS

1. What specific error is preventing the app from working? (Need logs to diagnose)
2. Are containers starting at all? (Need `docker-compose ps` output)
3. Did the move break any relative paths in code? (Need to check imports)
4. Should we rename docker volumes for consistency? (Recommendation: No, keep existing)
5. Should we rename container names? (Recommendation: No, keep `taskmanager-*`)
6. Should we update PRP filenames for consistency? (Recommendation: No, keep as historical record)
7. Should we update Python package names? (Recommendation: No, out of scope)
8. Is task-management-ui referenced in main vibes documentation? (Need to check)

## SUCCESS METRICS

**Current State** (Starting point):
- Location: `~/source/vibes/infra/task-manager/` ✅ (already moved)
- Status: ❌ **Never worked** - services not starting
- References: ⚠️ Mix of "task-management-ui" and "task-manager"
- Data: None (fresh system)

**Goal State** (What success looks like):
- Location: `~/source/vibes/infra/task-manager/` ✅ (same)
- Status: ✅ **Fully functional** - all services healthy
- UI: ✅ Loads at http://localhost:3000
- API: ✅ Responds at http://localhost:8000
- MCP: ✅ Responds at http://localhost:8051
- Features: ✅ Create projects, create tasks, drag-and-drop
- References: ✅ Consistent "task-manager" in all docs
- Ready: ✅ Can be used in production for vibes ecosystem
