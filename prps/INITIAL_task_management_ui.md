# INITIAL: Task Management System with UI and MCP Integration

## FEATURE

Build a containerized, self-hosted task management system with web UI and MCP server integration for AI assistant interaction.

**Core Capabilities**:
- Web UI with **both Kanban board and list view** (drag-and-drop task management)
- MCP server for Claude Code/Cursor integration
- 4-state workflow: `todo` → `doing` → `review` → `done`
- Project/workspace organization
- Docker deployment (self-contained: database, backend, frontend, MCP server)

**Key Principle**: System provides structure, external AI (via MCP) provides intelligence.

## EXAMPLES

### Reference Implementations

**Task Master** (`~/source/vibes/repos/claude-task-master`):
- Node/TypeScript with Supabase backend
- Hierarchical tasks with display_id (1, 1.1, 1.1.1)
- MCP server integration
- **Study**: `packages/tm-core/src/types/database.types.ts` for data model
- **Study**: Task hierarchy with parent_task_id, dependencies table

**Archon** (`~/source/vibes/repos/Archon`):
- Python/FastAPI + React + Supabase + pgvector
- Clean MCP tool pattern (`find_tasks`, `manage_task` consolidation)
- Full-stack web UI with real-time updates
- **Study**: `python/src/mcp_server/features/tasks/task_tools.py` for MCP implementation
- **Study**: `python/src/server/services/projects/task_service.py` for service layer
- **Study**: `archon-ui-main/src/features/projects/tasks/` for React components
- **Study**: TanStack Query usage for server state management

**What to Extract from References**:
1. Archon's MCP consolidation pattern (find/manage for CRUD)
2. Archon's service layer architecture (API route → Service → Database)
3. Archon's React patterns (feature-based organization, optimistic updates)
4. Task Master's hierarchical structure (if implementing parent/child tasks)
5. Both projects' TypeScript/type safety approaches

## DOCUMENTATION

**MCP Integration**:
- MCP SDK Documentation: https://modelcontextprotocol.io/
- Archon MCP implementation: `repos/Archon/python/src/mcp_server/`

**UI Component Libraries** (Research Required):
- Kanban drag-and-drop: @hello-pangea/dnd, react-beautiful-dnd, or dnd-kit
- UI components: shadcn/ui, Radix UI, or similar
- Markdown editor: react-markdown or similar

**Backend** (Choose One - Research Required):
- **Option A**: Python/FastAPI (matches vibes ecosystem)
- **Option B**: Node/Express or Fastify (full-stack TypeScript)

**Database**:
- PostgreSQL (with or without Supabase)
- Migration strategy: SQL scripts, Alembic (Python), or Prisma (Node)

## OTHER CONSIDERATIONS

### Required MCP Tools

**Task Management**:
```
find_tasks(query?, task_id?, filter_by?, filter_value?, project_id?)
  - List all tasks
  - Search by keyword
  - Get single task by ID
  - Filter by status, project, assignee

manage_task(action, task_id?, project_id?, title?, description?, status?, ...)
  - action: "create" | "update" | "delete"
  - Create new task, update existing, delete task
```

**Project Management**:
```
find_projects(project_id?, query?)
  - List all projects, get single project, search

manage_project(action, project_id?, name?, description?)
  - action: "create" | "update" | "delete"
```

### Data Model Decisions

**Core Task Fields** (Minimum):
- `id` (UUID), `project_id` (FK, nullable)
- `title` (required), `description` (markdown?)
- `status` (todo | doing | review | done)
- `assignee` (string: "User", agent names, etc.)
- `priority` (low | medium | high | urgent?)
- `position` (for manual drag-and-drop ordering)
- `created_at`, `updated_at`

**To Research**:
- Parent/child hierarchy (parent_task_id) vs flat with grouping?
- Display ID (1.1.1 style) vs UUID only?
- Feature/epic labels vs tags?
- Time tracking (estimated_hours, actual_hours)?
- Task dependencies table?

### Tech Stack Research Questions

1. **Backend**: Python/FastAPI (vibes consistency) vs Node/TypeScript (full-stack TS)?
2. **Task Hierarchy**: Strict parent/child vs flat with flexible grouping vs hybrid?
3. **Real-time**: HTTP polling vs WebSockets for UI updates?
4. **Authentication**: Single-user initially vs multi-user from start?
5. **Integration**: Standalone or integrate with basic-memory/Archon knowledge base?

### MVP Success Criteria

**Deployment**:
- [ ] `docker-compose up` runs all services
- [ ] Web UI accessible at `http://localhost:PORT`
- [ ] Data persists across container restarts

**UI Functionality**:
- [ ] Can create projects via UI
- [ ] Can create tasks (title, description, status)
- [ ] Kanban board displays tasks by status column
- [ ] List view shows tasks with filters/sorting
- [ ] Can drag tasks between status columns
- [ ] Can update task details inline

**MCP Integration**:
- [ ] MCP server accessible via `npx mcp-remote http://localhost:PORT/mcp`
- [ ] `find_tasks()` returns task list
- [ ] `manage_task("create", ...)` creates task visible in UI immediately
- [ ] `manage_task("update", ...)` updates task (syncs with UI)
- [ ] Claude Code can manage tasks via MCP tools

**Quality**:
- [ ] Type safety (TypeScript or Python type hints)
- [ ] Clean architecture (service layer, API routes, data models)
- [ ] API documentation (OpenAPI/Swagger)
- [ ] README with setup instructions
- [ ] `.env.example` with configuration template

### Deployment Configuration

**Docker Compose Structure**:
- Database service (PostgreSQL)
- Backend service (API + MCP server)
- Frontend service (React SPA)
- Health checks and restart policies
- Volume mounts for data persistence

**Environment Variables** (`.env.example`):
```
DATABASE_URL=postgresql://user:pass@db:5432/taskmanager
NODE_ENV=development
PORT=3000
MCP_PORT=8051
```

### Known Challenges

1. Kanban drag-and-drop with status transition validation
2. MCP tool responsiveness for large task lists (pagination needed?)
3. Real-time sync between MCP updates and UI
4. Database migrations in containerized environment
5. Type sharing between backend/frontend (if different languages)

### Future Enhancements (Not MVP)

- Time tracking and reporting
- Task dependencies with visual graph
- Advanced search (full-text, complex filters)
- Task templates, bulk operations
- Export/import (JSON, CSV)
- Notifications, webhooks
- Analytics (burndown, velocity charts)
- Mobile app
- Collaboration (comments, mentions)

### Integration with Vibes

**Proposed Location**: `/Users/jon/source/vibes/infra/task-manager/`

**Standalone Nature**:
- Does NOT depend on other vibes MCP servers
- Can run independently or alongside existing servers
- Own database (not shared with Archon)
- Optional: Link tasks to basic-memory notes
- Listed in main vibes README under MCP servers
