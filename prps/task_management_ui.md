# PRP: Task Management UI with MCP Integration

**Generated**: 2025-10-06
**Based On**: prps/INITIAL_task_management_ui.md
**Archon Project**: 4af077fb-9c9c-4bca-bdee-5c54d4b73d29
**Quality Score**: 9/10

---

## Goal

Build a self-hosted, containerized task management system with dual interfaces: a web UI for human oversight and an MCP server for AI assistant integration. The system provides structure (4-state workflow, project organization, drag-and-drop Kanban) while external AI provides intelligence via Claude Code/Cursor.

**End State**:
- Single `docker-compose up` deploys all services (PostgreSQL, FastAPI backend with MCP server, React frontend)
- Web UI at `http://localhost:3000` with Kanban board and list view
- MCP server accessible at `http://localhost:8051/mcp` via `npx mcp-remote`
- Real-time UI updates via smart HTTP polling (no WebSockets)
- Data persists across container restarts
- Tasks flow through `todo → doing → review → done` statuses
- AI assistants manage tasks via consolidated MCP tools (`find_tasks`, `manage_task`)

---

## Why

**Current Pain Points**:
- Task management scattered across text files, memory, and ad-hoc notes
- No structured workflow for AI-assisted development tasks
- Difficulty tracking project progress and task dependencies
- Manual context switching between task lists and code
- No integration between AI coding assistants and task tracking

**Business Value**:
- **Developer Productivity**: AI assistants can autonomously manage their task queue
- **Context Preservation**: Task descriptions and status persist across sessions
- **Visual Oversight**: Kanban board provides at-a-glance project status
- **Extensibility**: Standalone system can integrate with other vibes MCP servers
- **Reference Implementation**: Demonstrates FastAPI + React + MCP patterns for future vibes projects

**Integration with Vibes Ecosystem**:
- Follows Archon's proven MCP consolidation pattern
- Complements basic-memory by providing structured task context
- Uses same Docker deployment patterns as other vibes services
- Can be extended to link tasks with knowledge base documents

---

## What

### Core Features

**1. Web UI (React + TypeScript)**
- **Kanban Board View**: 4 columns (todo, doing, review, done) with drag-and-drop
- **List View**: Filterable table with sorting and inline editing
- **Task Detail Modal**: Full description (markdown), priority, assignee, timestamps
- **Project Management**: Create/switch projects, project-scoped task views
- **Real-time Updates**: Smart polling pauses when tab hidden, ETag caching

**2. MCP Server Integration**
- **Consolidated Tools Pattern** (Archon-style):
  - `find_tasks(query?, task_id?, filter_by?, filter_value?, project_id?, page?, per_page?)` - List, search, or get tasks
  - `manage_task(action, task_id?, project_id?, title?, description?, status?, assignee?, priority?, position?)` - Create, update, delete
  - `find_projects(project_id?, query?)` - List or get projects
  - `manage_project(action, project_id?, name?, description?)` - Create, update, delete
- **Response Optimization**: Truncate descriptions to 1000 chars, exclude large fields, replace arrays with counts
- **AI-Friendly Errors**: Structured responses with suggestions: `{"success": false, "error": "...", "suggestion": "..."}`

**3. 4-State Workflow**
- **Status Transitions**: `todo → doing → review → done`
- **Drag-and-Drop**: Move tasks between columns in Kanban view
- **Position Tracking**: Manual ordering within each status column
- **Atomic Updates**: Transaction isolation prevents race conditions

**4. Project/Workspace Organization**
- **Project Entity**: `id`, `name`, `description`, `created_at`, `updated_at`
- **Task-Project Association**: Tasks belong to projects (nullable for global tasks)
- **Project Switcher**: UI component to filter tasks by project

**5. Docker Deployment**
- **Services**: `db` (PostgreSQL), `backend` (FastAPI + MCP), `frontend` (React SPA)
- **Health Checks**: Backend waits for database readiness before starting
- **Data Persistence**: Named Docker volumes for database
- **Hot Reload**: Volume mounts for development environment
- **Environment Config**: `.env` file for all configuration

### Success Criteria

**Deployment**:
- [ ] `docker-compose up` starts all services without errors
- [ ] Web UI accessible at `http://localhost:3000`
- [ ] MCP server responds to `npx mcp-remote http://localhost:8051/mcp`
- [ ] Data persists after `docker-compose down && docker-compose up`
- [ ] Health checks pass for all services

**UI Functionality**:
- [ ] Create project via UI
- [ ] Create task with title, description (markdown), status, priority, assignee
- [ ] Kanban board displays tasks in 4 columns
- [ ] Drag task from "todo" to "doing" updates status immediately (optimistic update)
- [ ] List view shows tasks with filters (status, assignee, priority) and sorting
- [ ] Task detail modal edits title, description, status, priority, assignee
- [ ] Manual drag-and-drop ordering within columns persists

**MCP Integration**:
- [ ] `find_tasks()` returns task list with pagination
- [ ] `find_tasks(task_id="uuid")` returns single task with full details
- [ ] `find_tasks(filter_by="status", filter_value="todo")` filters correctly
- [ ] `manage_task("create", project_id="uuid", title="Test")` creates task visible in UI
- [ ] `manage_task("update", task_id="uuid", status="doing")` updates task in UI
- [ ] `manage_task("delete", task_id="uuid")` removes task from UI
- [ ] Claude Code can manage tasks via MCP without errors

**Quality**:
- [ ] Python type hints on all backend functions
- [ ] TypeScript strict mode enabled for frontend
- [ ] Pydantic models validate all request/response data
- [ ] OpenAPI docs available at `http://localhost:8000/docs`
- [ ] README with setup instructions and example commands
- [ ] `.env.example` with all required variables documented

**Performance**:
- [ ] MCP `find_tasks()` responds in < 500ms for 100 tasks
- [ ] Drag-and-drop update perceived latency < 200ms
- [ ] UI polling rate ≤ 1 request/second when active
- [ ] Database queries use indexes (verify with `EXPLAIN ANALYZE`)

---

## All Needed Context

### Documentation & References

**CRITICAL**: Read these sections BEFORE implementation. All gotchas and patterns are documented here.

```yaml
# MUST READ - Backend Framework
- url: https://fastapi.tiangolo.com/async/
  sections:
    - "Concurrency and async / await" - When to use async def vs def
  why: Critical for avoiding event loop blocking (Gotcha #1)
  critical_gotchas:
    - Never call blocking I/O in async endpoints
    - Use await for async operations or def for sync operations
    - FastAPI runs def endpoints in threadpool automatically

- url: https://docs.pydantic.dev/latest/concepts/validators/
  sections:
    - "Field Validators" - @field_validator decorator (V2 syntax)
    - "Model Validators" - Cross-field validation
  why: Pydantic V2 has breaking changes from V1
  critical_gotchas:
    - @validator is DEPRECATED, use @field_validator
    - values parameter removed, use ValidationInfo.data
    - Config class replaced with model_config dict

- url: https://fastapi.tiangolo.com/tutorial/cors/
  sections:
    - "CORS Middleware" - Cross-origin configuration
  why: Frontend on localhost:3000 needs to call backend on localhost:8000
  critical_gotchas:
    - NEVER use allow_origins=["*"] in production
    - Configure specific origins via environment variable

# MUST READ - Frontend State Management
- url: https://tanstack.com/query/v5/docs/react/guides/optimistic-updates
  sections:
    - "Optimistic Updates" - Cache-based pattern with rollback
  why: Instant UI feedback on drag-and-drop requires optimistic updates
  critical_gotchas:
    - ALWAYS cancel queries in onMutate to prevent race conditions
    - Use _localId for stable optimistic entity identification
    - Check isPending before triggering mutations

- url: https://tanstack.com/query/latest/docs/framework/react/guides/mutations
  sections:
    - "Mutations" - useMutation lifecycle
    - "Query Invalidation" - Smart cache invalidation
  why: MCP updates need to sync with UI cache
  critical_gotchas:
    - Don't over-invalidate - check queryClient.isMutating()
    - Use queryKey factories for consistent cache keys

# MUST READ - Drag-and-Drop
- url: https://react-dnd.github.io/react-dnd/docs/api/use-drop
  sections:
    - "useDrop Hook" - Drop target implementation
  why: Kanban columns are drop zones
  critical_gotchas:
    - Wrap app in DndProvider with HTML5Backend
    - Item type matching is strict - use constants
    - Provide explicit type parameters for TypeScript

- url: https://react-dnd.github.io/react-dnd/docs/api/use-drag
  sections:
    - "useDrag Hook" - Drag source implementation
  why: Task cards are draggable
  critical_gotchas:
    - TypeScript types require explicit generic parameters
    - Use ItemTypes constant for accept validation

# MUST READ - Database
- url: https://www.postgresql.org/docs/current/indexes.html
  sections:
    - "Index Types" - B-tree indexes for filtering
    - "Multicolumn Indexes" - Composite indexes for common queries
  why: Foreign keys NOT auto-indexed, must create manually
  critical_gotchas:
    - CREATE INDEX on ALL foreign key columns
    - Use composite index (status, position) for Kanban queries
    - Partial indexes for active tasks: WHERE status IN ('todo', 'doing', 'review')

- url: https://magicstack.github.io/asyncpg/current/usage.html
  sections:
    - "Connection Pooling" - Pool creation and management
    - "Transactions" - Async transaction context managers
  why: Async database driver for FastAPI
  critical_gotchas:
    - Use $1, $2 placeholders (not %s)
    - Always use async with pool.acquire()
    - Transactions: async with conn.transaction()

# MUST READ - MCP Integration
- url: https://modelcontextprotocol.io/docs/concepts/tools
  sections:
    - "Tool Schema" - JSON Schema input validation
    - "Tool Execution" - Response format
  why: MCP tools must return JSON strings
  critical_gotchas:
    - Tools return JSON strings, not Python dicts
    - Truncate responses > 100KB (description to 1000 chars)
    - Provide structured errors with suggestions

# MUST READ - Docker
- url: https://docs.docker.com/reference/compose-file/services/
  sections:
    - "healthcheck" - Service health checks
    - "depends_on" - Service dependencies with conditions
  why: Backend must wait for database readiness
  critical_gotchas:
    - depends_on with service_healthy waits for health check
    - Use named volumes (not bind mounts) for PostgreSQL data
    - start_period gives service time to initialize

# ESSENTIAL LOCAL FILES - Archon Reference Implementation
- file: prps/task_management_ui/examples/README.md
  why: Complete guide to all extracted patterns
  pattern: Study before implementation - saves hours of debugging

- file: prps/task_management_ui/examples/mcp/task_tools.py
  why: Proven MCP consolidation pattern from Archon production
  critical:
    - Consolidated find_tasks (list + search + get in one tool)
    - Response optimization (truncate, exclude, counts)
    - MCPErrorFormatter for AI-friendly errors

- file: prps/task_management_ui/examples/backend/task_service.py
  why: Service layer pattern with validation and position reordering
  critical:
    - Position increment logic for drag-and-drop (lines 93-115)
    - Validation returns tuple[bool, str] pattern
    - Async operations with proper error handling

- file: prps/task_management_ui/examples/frontend/KanbanColumn.tsx
  why: react-dnd drag-and-drop implementation with visual feedback
  critical:
    - useDrop hook with ItemTypes constant
    - Visual feedback on isOver state
    - Only trigger mutation if status changed

- file: prps/task_management_ui/examples/frontend/useTaskQueries.ts
  why: TanStack Query v5 patterns with optimistic updates
  critical:
    - Query key factories (taskKeys.byProject, taskKeys.detail)
    - cancelQueries in onMutate to prevent race conditions
    - createOptimisticEntity with _localId for stable references

- file: prps/task_management_ui/examples/docker/docker-compose.yml
  why: Multi-service Docker Compose with health checks
  critical:
    - Health check with pg_isready for PostgreSQL
    - depends_on with service_healthy condition
    - Named volumes for data persistence

- file: prps/task_management_ui/examples/database/schema.sql
  why: PostgreSQL schema with position tracking and indexes
  critical:
    - Composite index (status, position) for Kanban
    - Indexes on ALL foreign keys
    - Auto-update timestamp triggers
```

### Current Codebase Tree (Relevant Archon Reference)

```
repos/Archon/
├── python/
│   ├── src/
│   │   ├── mcp_server/
│   │   │   ├── features/
│   │   │   │   └── tasks/
│   │   │   │       └── task_tools.py          # MCP consolidation pattern
│   │   │   └── utils/
│   │   │       └── error_handling.py          # MCPErrorFormatter
│   │   └── server/
│   │       ├── services/
│   │       │   └── projects/
│   │       │       └── task_service.py        # Service layer pattern
│   │       └── utils/
│   │           └── etag_utils.py              # HTTP caching
│   └── pyproject.toml
├── archon-ui-main/
│   └── src/
│       ├── features/
│       │   ├── projects/
│       │   │   └── tasks/
│       │   │       ├── components/
│       │   │       │   └── KanbanColumn.tsx   # Drag-and-drop
│       │   │       ├── hooks/
│       │   │       │   └── useTaskQueries.ts  # TanStack Query
│       │   │       ├── services/
│       │   │       │   └── taskService.ts     # API client
│       │   │       └── types/
│       │   │           └── task.ts            # TypeScript types
│       │   └── shared/
│       │       ├── config/
│       │       │   └── queryPatterns.ts       # STALE_TIMES constants
│       │       └── utils/
│       │           └── optimistic.ts          # Optimistic update helpers
│       └── pages/
├── migration/
│   └── complete_setup.sql                     # Database schema
└── docker-compose.yml                          # Multi-service deployment
```

### Desired Codebase Tree (New Implementation)

```
task-management-ui/
├── backend/
│   ├── src/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── projects.py                    # Project CRUD endpoints
│   │   │   └── tasks.py                       # Task CRUD endpoints
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── project_service.py             # Project business logic
│   │   │   └── task_service.py                # Task business logic + position logic
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── project.py                     # Pydantic models for projects
│   │   │   └── task.py                        # Pydantic models for tasks
│   │   ├── config/
│   │   │   ├── __init__.py
│   │   │   └── database.py                    # asyncpg pool setup
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   └── etag.py                        # ETag generation (from Archon)
│   │   ├── mcp_server.py                      # MCP tools (find_tasks, manage_task)
│   │   └── main.py                            # FastAPI app initialization
│   ├── tests/
│   │   ├── test_tasks.py                      # Task service tests
│   │   └── test_mcp.py                        # MCP tool tests
│   ├── alembic/
│   │   ├── versions/
│   │   │   └── 001_create_tables.py           # Initial schema migration
│   │   └── env.py
│   ├── Dockerfile
│   ├── pyproject.toml                         # uv dependencies
│   └── uv.lock
│
├── frontend/
│   ├── src/
│   │   ├── features/
│   │   │   ├── projects/
│   │   │   │   ├── components/
│   │   │   │   │   ├── ProjectList.tsx
│   │   │   │   │   └── ProjectSwitcher.tsx
│   │   │   │   ├── hooks/
│   │   │   │   │   └── useProjectQueries.ts
│   │   │   │   ├── services/
│   │   │   │   │   └── projectService.ts
│   │   │   │   └── types/
│   │   │   │       └── project.ts
│   │   │   ├── tasks/
│   │   │   │   ├── components/
│   │   │   │   │   ├── KanbanBoard.tsx       # 4-column layout
│   │   │   │   │   ├── KanbanColumn.tsx      # useDrop for column
│   │   │   │   │   ├── TaskCard.tsx          # useDrag for card
│   │   │   │   │   ├── TaskListView.tsx      # Table with filters
│   │   │   │   │   └── TaskDetailModal.tsx   # Edit modal
│   │   │   │   ├── hooks/
│   │   │   │   │   └── useTaskQueries.ts     # Query + mutation hooks
│   │   │   │   ├── services/
│   │   │   │   │   └── taskService.ts        # API calls
│   │   │   │   └── types/
│   │   │   │       └── task.ts               # TypeScript types
│   │   │   ├── shared/
│   │   │   │   ├── api/
│   │   │   │   │   └── apiClient.ts          # Axios/fetch wrapper
│   │   │   │   ├── config/
│   │   │   │   │   ├── queryClient.ts        # TanStack Query setup
│   │   │   │   │   └── queryPatterns.ts      # STALE_TIMES constants
│   │   │   │   ├── hooks/
│   │   │   │   │   └── useSmartPolling.ts    # Visibility-aware polling
│   │   │   │   └── utils/
│   │   │   │       └── optimistic.ts         # Optimistic entity helpers
│   │   │   └── ui/
│   │   │       └── components/               # shadcn/ui components
│   │   ├── pages/
│   │   │   ├── KanbanPage.tsx
│   │   │   └── ListPage.tsx
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── tests/
│   │   └── TaskCard.test.tsx
│   ├── Dockerfile
│   ├── package.json
│   └── vite.config.ts
│
├── database/
│   └── init.sql                               # Schema creation
│
├── docker-compose.yml                          # All services
├── .env.example                                # Environment template
└── README.md                                   # Setup instructions

**New Files** (25 total):
Backend (11): main.py, mcp_server.py, 2 API routes, 2 services, 2 model files, database.py, etag.py, migration
Frontend (12): 3 pages, 6 components, 3 hooks, 3 services, 3 types/utils
Infrastructure (2): docker-compose.yml, init.sql
```

### Known Gotchas & Library Quirks

**CRITICAL**: All implementation tasks MUST address these gotchas. Refer to prps/task_management_ui/planning/gotchas.md for full details.

```python
# CRITICAL GOTCHA #1: FastAPI - Blocking the Event Loop
# Source: https://medium.com/@bhagyarana80/10-async-pitfalls-in-fastapi-and-how-to-avoid-them-60d6c67ea48f

# ❌ WRONG - Blocks event loop for ALL requests
@app.get("/tasks")
async def get_tasks():
    import time
    time.sleep(2)  # BLOCKS entire server!
    return tasks

# ✅ RIGHT - Non-blocking async
@app.get("/tasks")
async def get_tasks():
    await asyncio.sleep(2)  # Non-blocking
    return tasks

# ✅ ALTERNATIVE - Use def for sync code (FastAPI runs in threadpool)
@app.get("/tasks")
def get_tasks():
    # FastAPI automatically runs this in a separate thread
    session = get_sync_session()
    tasks = session.query(Task).all()
    return tasks

# RULE: If you use async def, NEVER call blocking functions

# CRITICAL GOTCHA #2: PostgreSQL - Position Reordering Race Conditions
# Source: Archon task_service.py + PostgreSQL concurrency docs

# ❌ WRONG - Race condition prone
async def update_task_position(task_id: str, new_position: int, status: str):
    # Read tasks (NOT ATOMIC!)
    tasks = await db.fetch_all(...)
    # Update positions (RACE CONDITION!)
    for task in tasks:
        await db.execute(...)

# ✅ RIGHT - Atomic transaction with row locking
async def update_task_position(task_id: str, new_position: int, status: str):
    async with db.transaction():
        # Acquire locks in consistent order (prevents deadlocks)
        await db.execute(
            """
            SELECT id FROM tasks
            WHERE status = $1 AND position >= $2
            ORDER BY id  -- Consistent lock order
            FOR UPDATE
            """,
            status, new_position
        )

        # Atomic batch update
        await db.execute(
            "UPDATE tasks SET position = position + 1 WHERE status = $1 AND position >= $2",
            status, new_position
        )

        # Update target task
        await db.execute(
            "UPDATE tasks SET position = $1, status = $2 WHERE id = $3",
            new_position, status, task_id
        )

# RULE: ALWAYS use transactions for position updates, lock rows in consistent order

# CRITICAL GOTCHA #3: MCP - Response Size Limits
# Source: Archon e9eb05e2bf38f125

MAX_DESCRIPTION_LENGTH = 1000
MAX_TASKS_PER_PAGE = 20

# ❌ WRONG - Returns everything, can be huge
@mcp.tool()
async def find_tasks(per_page: int = 100) -> str:  # TOO LARGE!
    tasks = await task_service.list_tasks(per_page=per_page)
    return json.dumps({"tasks": tasks})  # Can exceed JSON-RPC limits

# ✅ RIGHT - Optimized responses
@mcp.tool()
async def find_tasks(per_page: int = 10) -> str:
    per_page = min(per_page, MAX_TASKS_PER_PAGE)  # Limit page size
    tasks = await task_service.list_tasks(
        per_page=per_page,
        exclude_large_fields=True  # Don't return JSONB arrays
    )

    # Optimize each task
    optimized_tasks = [optimize_task_for_mcp(task) for task in tasks]
    return json.dumps({"success": True, "tasks": optimized_tasks})

def optimize_task_for_mcp(task: dict) -> dict:
    # Truncate long descriptions
    if task.get("description") and len(task["description"]) > 1000:
        task["description"] = task["description"][:997] + "..."

    # Remove large fields
    for field in ["metadata", "attachments"]:
        if field in task:
            del task[field]

    return task

# RULE: ALWAYS limit MCP responses to < 100KB, truncate descriptions, exclude large fields

# CRITICAL GOTCHA #4: TanStack Query - Race Conditions in Optimistic Updates
# Source: https://tkdodo.eu/blog/concurrent-optimistic-updates-in-react-query

// ❌ WRONG - No query cancellation
const updateTaskMutation = useMutation({
  mutationFn: (update) => taskService.updateTask(update.id, update),
  onMutate: async (update) => {
    // Missing: await queryClient.cancelQueries()
    const previous = queryClient.getQueryData(['tasks', projectId]);
    queryClient.setQueryData(['tasks', projectId], ...);
    return { previous };
  },
});

// ✅ RIGHT - Cancel queries to prevent race conditions
const updateTaskMutation = useMutation({
  mutationFn: (update) => taskService.updateTask(update.id, update),
  onMutate: async (update) => {
    // CRITICAL: Cancel in-flight queries
    await queryClient.cancelQueries({
      queryKey: ['tasks', projectId]
    });

    const previous = queryClient.getQueryData(['tasks', projectId]);

    const optimisticTask = {
      ...update,
      _optimistic: true,
      _localId: nanoid(),
    };

    queryClient.setQueryData(['tasks', projectId], (old) =>
      old.map(task =>
        task.id === update.id ? { ...task, ...optimisticTask } : task
      )
    );

    return { previous, optimisticId: optimisticTask._localId };
  },

  onError: (err, variables, context) => {
    if (context?.previous) {
      queryClient.setQueryData(['tasks', projectId], context.previous);
    }
  },

  onSuccess: (serverTask, variables, context) => {
    queryClient.setQueryData(['tasks', projectId], (tasks) =>
      tasks.map(task =>
        task._localId === context?.optimisticId ? serverTask : task
      )
    );
  },
});

// RULE: ALWAYS cancel queries in onMutate, use _localId for stable references

# CRITICAL GOTCHA #5: Docker - PostgreSQL Volume Permission Errors
# Source: https://stackoverflow.com/questions/60619659/postgres-mounting-volume-in-docker-permission-denied

# ❌ WRONG - Bind mount with permission issues
services:
  db:
    volumes:
      - ./data/postgres:/var/lib/postgresql/data  # Permission denied!

# ✅ RIGHT - Use named Docker volume
services:
  db:
    volumes:
      - taskmanager-db-data:/var/lib/postgresql/data  # Works consistently
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U taskuser -d taskmanager"]
      interval: 5s

volumes:
  taskmanager-db-data:
    driver: local

# RULE: ALWAYS use named volumes for PostgreSQL data (not bind mounts)

# CRITICAL GOTCHA #6: Pydantic V2 - Breaking Changes
# Source: https://docs.pydantic.dev/latest/migration/

# ❌ WRONG - Pydantic V1 syntax (deprecated)
from pydantic import BaseModel, validator

class TaskCreate(BaseModel):
    title: str

    class Config:  # V1 style
        orm_mode = True

    @validator('title')  # Deprecated!
    def title_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v

# ✅ RIGHT - Pydantic V2 syntax
from pydantic import BaseModel, field_validator

class TaskCreate(BaseModel):
    title: str

    model_config = {  # V2 style - dict instead of class
        'from_attributes': True,  # Replaces orm_mode
    }

    @field_validator('title')  # Replaces @validator
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()

# RULE: Use @field_validator (not @validator), model_config dict (not Config class)

# HIGH PRIORITY GOTCHA #7: PostgreSQL - Missing Foreign Key Indexes
# Source: PostgreSQL documentation

# ❌ WRONG - No index on foreign key
CREATE TABLE tasks (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id),  -- No auto-index!
    -- Query will be SLOW: SELECT * FROM tasks WHERE project_id = 'xxx'
);

# ✅ RIGHT - Always index foreign keys
CREATE TABLE tasks (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    status TEXT NOT NULL,
    position INTEGER DEFAULT 0
);

-- Critical indexes
CREATE INDEX idx_tasks_project_id ON tasks(project_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_status_position ON tasks(status, position);  -- For Kanban

# RULE: CREATE INDEX on ALL foreign key columns + composite indexes for common queries

# HIGH PRIORITY GOTCHA #8: CORS Configuration
# Source: https://fastapi.tiangolo.com/tutorial/cors/

# ❌ WRONG - Overly permissive
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # DANGEROUS in production!
)

# ✅ RIGHT - Environment-specific
import os

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "development":
    origins = ["http://localhost:3000", "http://localhost:5173"]
elif ENVIRONMENT == "production":
    origins = ["https://yourdomain.com"]
else:
    origins = []

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Specific origins only
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
)

# RULE: NEVER use allow_origins=["*"] in production, use environment variables

# MEDIUM PRIORITY GOTCHA #9: react-dnd TypeScript Types
# Source: https://github.com/react-dnd/react-dnd/issues/3192

// ❌ WRONG - Generic types not inferred
const [{ isOver }, drop] = useDrop({
  accept: 'TASK',
  drop: (item, monitor) => {
    // item is unknown - no type safety!
  },
});

// ✅ RIGHT - Explicit type parameters
export const ItemTypes = {
  TASK: 'task',
} as const;

interface TaskDragItem {
  id: string;
  status: TaskStatus;
}

const [{ isOver }, drop] = useDrop<
  TaskDragItem,      // Drag item type
  void,              // Drop result type
  { isOver: boolean } // Collect result type
>({
  accept: ItemTypes.TASK,
  drop: (item: TaskDragItem) => {
    // Full type safety - item is TaskDragItem
    onTaskMove(item.id, status);
  },
  collect: (monitor) => ({
    isOver: !!monitor.isOver(),
  }),
});

// RULE: Always provide explicit type parameters to useDrop and useDrag

# MEDIUM PRIORITY GOTCHA #10: TanStack Query - Stale Time Confusion
# Source: TanStack Query documentation

// ❌ WRONG - Constant refetching or stale data
const { data } = useQuery({
  queryKey: ['tasks'],
  queryFn: fetchTasks,
  // Missing staleTime - defaults to 0 (always stale)
  // Refetches on EVERY component mount!
});

// ✅ RIGHT - Explicit stale times
export const STALE_TIMES = {
  instant: 0,
  frequent: 5_000,      // 5 seconds
  normal: 30_000,       // 30 seconds
  rare: 300_000,        // 5 minutes
  static: Infinity,
} as const;

const { data: tasks } = useQuery({
  queryKey: ['tasks', projectId],
  queryFn: () => taskService.getTasksByProject(projectId),
  staleTime: STALE_TIMES.normal,     // 30s
  gcTime: 10 * 60 * 1000,            // 10 minutes
  refetchOnWindowFocus: true,
  refetchInterval: 30_000,
  refetchIntervalInBackground: false, // Pause when hidden
});

// RULE: Always use STALE_TIMES constants, set refetchIntervalInBackground: false
```

**Comprehensive Gotcha Documentation**: See `prps/task_management_ui/planning/gotchas.md` for all 13 documented gotchas with detection strategies and solutions.

---

## Tech Stack & Architecture Decisions

### Backend: Python + FastAPI + FastMCP

**Rationale**: Matches vibes ecosystem (Archon, basic-memory), proven MCP patterns, strong async support

**Stack**:
- **Framework**: FastAPI (Python 3.12+)
- **Validation**: Pydantic V2
- **Database Driver**: asyncpg (async PostgreSQL)
- **Migrations**: Alembic
- **MCP Framework**: FastMCP (as used in Archon)
- **Testing**: pytest with pytest-asyncio

**Pros**:
- Consistent with existing vibes Python MCP servers
- Can directly reference Archon implementation patterns
- FastMCP provides proven MCP integration
- Strong type safety with Pydantic
- Async/await for performance

**Cons**:
- Type sharing requires duplication (Python models → TS types)
- Two language ecosystems to manage

### Frontend: React 18 + TypeScript + Vite

**Rationale**: Modern stack with excellent developer experience, proven in Archon UI

**Stack**:
- **Framework**: React 18 with TypeScript (strict mode)
- **Build Tool**: Vite
- **State Management**: TanStack Query v5 (no Redux/Zustand)
- **Drag-and-Drop**: react-dnd (proven in Archon)
- **UI Components**: shadcn/ui (Radix UI + Tailwind CSS)
- **Markdown**: react-markdown
- **Testing**: Vitest + React Testing Library

**Pros**:
- Single source of truth for server state (TanStack Query)
- Built-in caching, deduplication, polling
- Optimistic updates for instant UI feedback
- Type-safe component props and API contracts

**Cons**:
- Type duplication from backend (acceptable for standalone system)

### Database: PostgreSQL 16

**Rationale**: Robust relational database with excellent indexing and transaction support

**Stack**:
- **Engine**: PostgreSQL 16
- **Connection**: asyncpg connection pool
- **Schema Management**: Alembic migrations

**Design Decisions**:
- UUID for all IDs (cross-database compatibility)
- `position` INTEGER for manual ordering (not auto-increment)
- CHECK constraints for enum values (status, priority)
- Cascading deletes for project → tasks
- Timestamps with timezone
- Composite indexes for common query patterns

### Real-Time Updates: HTTP Polling (No WebSockets)

**Rationale**: Simpler implementation, works through proxies, proven in Archon

**Pattern**: Smart polling with variable intervals
- Active tab: 30 seconds
- Tab hidden: pause polling
- Manual refresh always available
- ETag caching reduces bandwidth by ~70%

**Alternative Considered**: WebSockets
- More complex (connection management, reconnection)
- Overkill for task management updates
- Adds deployment complexity

### Authentication: Single-User Initially (No Auth in MVP)

**Rationale**: Self-hosted implies single user or trusted environment

**Future Path**:
- Add `user_id` to tasks/projects tables
- Implement JWT or session-based auth
- Filter queries by authenticated user

### Task Hierarchy: Flat with Optional Parent (Not Enforced)

**Rationale**: Archon's flat approach works well, simpler Kanban visualization

**Design**:
- `parent_task_id UUID NULL` in schema
- UI shows as flat list initially
- Future: Add expand/collapse, indentation

---

## Data Model & Schema

### Projects Table

```sql
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_projects_created_at ON projects(created_at DESC);
```

### Tasks Table

```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    parent_task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,

    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL CHECK (status IN ('todo', 'doing', 'review', 'done')),
    assignee TEXT DEFAULT 'User',
    priority TEXT DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),

    -- Position for drag-and-drop ordering within status column
    position INTEGER DEFAULT 0,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- CRITICAL: Indexes on ALL foreign keys + composite for common queries
CREATE INDEX idx_tasks_project_id ON tasks(project_id);
CREATE INDEX idx_tasks_parent_id ON tasks(parent_task_id) WHERE parent_task_id IS NOT NULL;
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_assignee ON tasks(assignee);
CREATE INDEX idx_tasks_status_position ON tasks(status, position);  -- For Kanban ordering

-- Partial index for active tasks only
CREATE INDEX idx_tasks_active ON tasks(project_id, status)
    WHERE status IN ('todo', 'doing', 'review');

-- Auto-update timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_tasks_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at
    BEFORE UPDATE ON projects
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### Pydantic Models (Backend)

```python
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Literal

# Enums
TaskStatus = Literal["todo", "doing", "review", "done"]
TaskPriority = Literal["low", "medium", "high", "urgent"]

# Request Models
class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None

class TaskCreate(BaseModel):
    project_id: str | None = None
    title: str = Field(..., min_length=1, max_length=500)
    description: str | None = None
    status: TaskStatus = "todo"
    assignee: str = "User"
    priority: TaskPriority = "medium"
    position: int = 0

    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Title cannot be empty or whitespace')
        return v.strip()

class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    assignee: str | None = None
    priority: TaskPriority | None = None
    position: int | None = None

# Response Models
class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class TaskResponse(BaseModel):
    id: str
    project_id: str | None
    parent_task_id: str | None
    title: str
    description: str | None
    status: TaskStatus
    assignee: str
    priority: TaskPriority
    position: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
```

### TypeScript Types (Frontend)

```typescript
// types/task.ts
export type TaskStatus = "todo" | "doing" | "review" | "done";
export type TaskPriority = "low" | "medium" | "high" | "urgent";

export interface Task {
  id: string;
  project_id: string | null;
  parent_task_id: string | null;
  title: string;
  description: string | null;
  status: TaskStatus;
  assignee: string;
  priority: TaskPriority;
  position: number;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  project_id?: string;
  title: string;
  description?: string;
  status?: TaskStatus;
  assignee?: string;
  priority?: TaskPriority;
  position?: number;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  status?: TaskStatus;
  assignee?: string;
  priority?: TaskPriority;
  position?: number;
}

// types/project.ts
export interface Project {
  id: string;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProjectCreate {
  name: string;
  description?: string;
}
```

---

## Implementation Blueprint

### Phase 0: Planning & Understanding

**BEFORE starting implementation, complete these steps:**

1. **Read ALL research documents**:
   - [ ] `prps/task_management_ui/planning/feature-analysis.md` - Requirements and decisions
   - [ ] `prps/task_management_ui/planning/codebase-patterns.md` - Archon patterns to follow
   - [ ] `prps/task_management_ui/planning/documentation-links.md` - External docs with gotchas
   - [ ] `prps/task_management_ui/planning/examples-to-include.md` - Example code to adapt
   - [ ] `prps/task_management_ui/planning/gotchas.md` - All 13 gotchas with solutions

2. **Study example implementations**:
   - [ ] `prps/task_management_ui/examples/README.md` - Pattern highlights and adaptation guide
   - [ ] `prps/task_management_ui/examples/mcp/task_tools.py` - MCP consolidation pattern
   - [ ] `prps/task_management_ui/examples/backend/task_service.py` - Service layer with validation
   - [ ] `prps/task_management_ui/examples/frontend/KanbanColumn.tsx` - Drag-and-drop UI
   - [ ] `prps/task_management_ui/examples/frontend/useTaskQueries.ts` - TanStack Query patterns
   - [ ] `prps/task_management_ui/examples/docker/docker-compose.yml` - Multi-service deployment
   - [ ] `prps/task_management_ui/examples/database/schema.sql` - PostgreSQL schema

3. **Read critical documentation sections**:
   - [ ] FastAPI async guide: https://fastapi.tiangolo.com/async/
   - [ ] Pydantic V2 validators: https://docs.pydantic.dev/latest/concepts/validators/
   - [ ] TanStack Query optimistic updates: https://tanstack.com/query/v5/docs/react/guides/optimistic-updates
   - [ ] react-dnd useDrop: https://react-dnd.github.io/react-dnd/docs/api/use-drop
   - [ ] PostgreSQL indexes: https://www.postgresql.org/docs/current/indexes.html

### Task List (Execute in Order)

**Estimated Total Time**: 16-20 hours for experienced developer

```yaml
Task 1: Database Setup
RESPONSIBILITY: Create PostgreSQL schema with proper indexes and constraints
FILES TO CREATE:
  - database/init.sql
  - backend/alembic/versions/001_create_tables.py

PATTERN TO FOLLOW: prps/task_management_ui/examples/database/schema.sql

SPECIFIC STEPS:
  1. Create projects table with UUID primary key, timestamps
  2. Create tasks table with foreign keys to projects and self (parent_task_id)
  3. Add CHECK constraints for status and priority enums
  4. Create indexes on ALL foreign keys (idx_tasks_project_id, idx_tasks_parent_id)
  5. Create composite index (status, position) for Kanban ordering
  6. Create partial index for active tasks WHERE status IN ('todo', 'doing', 'review')
  7. Add auto-update timestamp triggers for updated_at

VALIDATION:
  - psql -d taskmanager -f database/init.sql runs without errors
  - \d tasks shows all indexes created
  - EXPLAIN ANALYZE SELECT * FROM tasks WHERE project_id = 'uuid' uses index

GOTCHAS TO AVOID:
  - PostgreSQL does NOT auto-index foreign keys - create manually (Gotcha #7)
  - Use TEXT not VARCHAR for flexibility
  - Use TIMESTAMPTZ (with timezone) not TIMESTAMP
  - Lock rows in consistent order (ORDER BY id) to prevent deadlocks (Gotcha #2)

---

Task 2: Backend - Pydantic Models
RESPONSIBILITY: Define type-safe request/response models with validation
FILES TO CREATE:
  - backend/src/models/__init__.py
  - backend/src/models/project.py
  - backend/src/models/task.py

PATTERN TO FOLLOW: Archon models + Pydantic V2 docs

SPECIFIC STEPS:
  1. Create ProjectCreate, ProjectUpdate, ProjectResponse models
  2. Create TaskCreate, TaskUpdate, TaskResponse models
  3. Use Literal types for status and priority enums
  4. Add @field_validator for title (check not empty/whitespace)
  5. Set model_config = {"from_attributes": True} for ORM compatibility
  6. Use Field(..., min_length=1, max_length=500) for constraints

VALIDATION:
  - from models.task import TaskCreate validates correctly
  - TaskCreate(title="") raises ValidationError
  - TaskCreate(status="invalid") raises ValidationError
  - pytest tests/test_models.py passes

GOTCHAS TO AVOID:
  - Use @field_validator (NOT @validator) - Pydantic V2 (Gotcha #6)
  - model_config dict (NOT Config class) - Pydantic V2
  - from_attributes=True (NOT orm_mode=True) - Pydantic V2

---

Task 3: Backend - Database Configuration
RESPONSIBILITY: Setup asyncpg connection pool and dependency injection
FILES TO CREATE:
  - backend/src/config/__init__.py
  - backend/src/config/database.py

PATTERN TO FOLLOW: Archon database setup + asyncpg docs

SPECIFIC STEPS:
  1. Create async connection pool with asyncpg.create_pool()
  2. Configure pool size (min=5, max=20)
  3. Create get_db() dependency with async context manager
  4. Use async with pool.acquire() for connection management
  5. Add startup event to create pool, shutdown event to close

VALIDATION:
  - Pool creates successfully with DATABASE_URL from .env
  - Dependency injection works in test endpoint
  - Connections released after use (check pg_stat_activity)

GOTCHAS TO AVOID:
  - Use async def for get_db() dependency (Gotcha #1)
  - Always use async with pool.acquire() - never forget cleanup (Gotcha #12)
  - Use $1, $2 placeholders (NOT %s) for queries (Gotcha #7)

---

Task 4: Backend - Service Layer (Projects)
RESPONSIBILITY: Business logic for project CRUD operations
FILES TO CREATE:
  - backend/src/services/__init__.py
  - backend/src/services/project_service.py

PATTERN TO FOLLOW: prps/task_management_ui/examples/backend/task_service.py

SPECIFIC STEPS:
  1. Create ProjectService class with __init__(self, db_pool)
  2. Implement async def list_projects(self, page=1, per_page=10)
  3. Implement async def get_project(self, project_id: str)
  4. Implement async def create_project(self, data: ProjectCreate)
  5. Implement async def update_project(self, project_id: str, data: ProjectUpdate)
  6. Implement async def delete_project(self, project_id: str)
  7. Use tuple[bool, dict] return pattern for errors: (success, result)
  8. Validate inputs before database operations

VALIDATION:
  - service.create_project(ProjectCreate(name="Test")) returns (True, project)
  - service.get_project("nonexistent") returns (False, {"error": "Not found"})
  - pytest tests/test_project_service.py passes

GOTCHAS TO AVOID:
  - Use async with db.transaction() for multi-step operations (Gotcha #2)
  - Return tuple[bool, dict] not exceptions - handle errors gracefully
  - Validate inputs (check name not empty) before database calls

---

Task 5: Backend - Service Layer (Tasks with Position Logic)
RESPONSIBILITY: Task CRUD with atomic position reordering
FILES TO CREATE:
  - backend/src/services/task_service.py

PATTERN TO FOLLOW: prps/task_management_ui/examples/backend/task_service.py (lines 93-115)

SPECIFIC STEPS:
  1. Create TaskService class with db_pool
  2. Implement async def list_tasks(self, filters, page, per_page, exclude_large_fields)
  3. Implement async def get_task(self, task_id: str)
  4. Implement async def create_task(self, data: TaskCreate)
  5. Implement async def update_task_position(self, task_id, new_status, new_position)
     - CRITICAL: Use transaction with row locking (SELECT ... FOR UPDATE)
     - Increment positions >= new_position before insert
     - Lock rows in consistent order (ORDER BY id) to prevent deadlocks
  6. Implement async def update_task(self, task_id: str, data: TaskUpdate)
  7. Implement async def delete_task(self, task_id: str)
  8. Add validation methods: validate_status(status), validate_priority(priority)

VALIDATION:
  - service.update_task_position("task1", "doing", 2) increments existing positions
  - Concurrent position updates don't create duplicates (test with asyncio.gather)
  - pytest tests/test_task_service.py passes

GOTCHAS TO AVOID:
  - CRITICAL: Position reordering MUST use transaction + row locking (Gotcha #2)
  - Lock rows ORDER BY id to prevent deadlocks
  - If exclude_large_fields=True, don't select description > 1000 chars

PSEUDOCODE:
async def update_task_position(self, task_id: str, new_status: str, new_position: int):
    async with self.db_pool.acquire() as conn:
        async with conn.transaction():
            # Lock rows in consistent order to prevent deadlocks
            await conn.execute(
                """
                SELECT id FROM tasks
                WHERE status = $1 AND position >= $2
                ORDER BY id  -- Consistent lock order
                FOR UPDATE
                """,
                new_status, new_position
            )

            # Atomic batch update - increment positions
            await conn.execute(
                """
                UPDATE tasks
                SET position = position + 1, updated_at = NOW()
                WHERE status = $1 AND position >= $2
                """,
                new_status, new_position
            )

            # Update target task
            await conn.execute(
                """
                UPDATE tasks
                SET status = $1, position = $2, updated_at = NOW()
                WHERE id = $3
                """,
                new_status, new_position, task_id
            )

---

Task 6: Backend - FastAPI Routes (Projects)
RESPONSIBILITY: HTTP endpoints for project CRUD
FILES TO CREATE:
  - backend/src/api/__init__.py
  - backend/src/api/projects.py

PATTERN TO FOLLOW: Archon API routes + FastAPI docs

SPECIFIC STEPS:
  1. Create APIRouter with prefix="/api/projects"
  2. Add GET /api/projects (list with pagination)
  3. Add GET /api/projects/{project_id} (single project)
  4. Add POST /api/projects (create with ProjectCreate model)
  5. Add PATCH /api/projects/{project_id} (update with ProjectUpdate model)
  6. Add DELETE /api/projects/{project_id}
  7. Inject ProjectService via Depends(get_project_service)
  8. Use Pydantic response_model for type safety
  9. Add OpenAPI tags and descriptions

VALIDATION:
  - GET /api/projects returns 200 with project list
  - POST /api/projects with invalid data returns 422
  - pytest tests/test_api_projects.py passes

GOTCHAS TO AVOID:
  - Use async def for endpoints calling async services (Gotcha #1)
  - Raise HTTPException(status_code=..., detail=...) for errors
  - Add response_model to all endpoints for OpenAPI docs

---

Task 7: Backend - FastAPI Routes (Tasks)
RESPONSIBILITY: HTTP endpoints for task CRUD
FILES TO CREATE:
  - backend/src/api/tasks.py

PATTERN TO FOLLOW: Archon task API routes

SPECIFIC STEPS:
  1. Create APIRouter with prefix="/api/tasks"
  2. Add GET /api/tasks (list with filters: project_id, status, assignee, page, per_page)
  3. Add GET /api/tasks/{task_id} (single task)
  4. Add POST /api/tasks (create with TaskCreate model)
  5. Add PATCH /api/tasks/{task_id} (update with TaskUpdate model)
  6. Add PATCH /api/tasks/{task_id}/position (position update)
  7. Add DELETE /api/tasks/{task_id}
  8. Add ETag support for list endpoint (from prps/.../examples/backend/task_service.py)
  9. Inject TaskService via Depends(get_task_service)

VALIDATION:
  - GET /api/tasks?status=todo returns filtered tasks
  - PATCH /api/tasks/{id}/position updates position atomically
  - ETag caching returns 304 Not Modified when data unchanged
  - pytest tests/test_api_tasks.py passes

GOTCHAS TO AVOID:
  - Use async def for all endpoints (Gotcha #1)
  - Add ETag header to list responses for caching
  - Handle position updates via separate endpoint (not generic PATCH)

---

Task 8: Backend - MCP Server
RESPONSIBILITY: MCP tools for AI assistant integration
FILES TO CREATE:
  - backend/src/mcp_server.py
  - backend/src/utils/__init__.py
  - backend/src/utils/etag.py (optional, for ETag generation)

PATTERN TO FOLLOW: prps/task_management_ui/examples/mcp/task_tools.py

SPECIFIC STEPS:
  1. Create FastMCP instance: mcp = FastMCP("Task Manager")
  2. Implement @mcp.tool() async def find_tasks(...) -> str:
     - Parameters: query, task_id, filter_by, filter_value, project_id, page, per_page
     - If task_id: return single task with full details
     - Else: return optimized list (truncate, exclude large fields)
     - Limit per_page to MAX_TASKS_PER_PAGE (20)
  3. Implement @mcp.tool() async def manage_task(action, ...) -> str:
     - Actions: "create", "update", "delete"
     - Return structured JSON: {"success": bool, "task"?: object, "message"?: string}
  4. Implement @mcp.tool() async def find_projects(...) -> str
  5. Implement @mcp.tool() async def manage_project(action, ...) -> str
  6. Create optimize_task_for_mcp(task) helper:
     - Truncate description to 1000 chars
     - Remove large fields
  7. Wrap tool logic in try/except, return structured errors
  8. Add if __name__ == "__main__": mcp.run()

VALIDATION:
  - mcp.run() starts server without errors
  - find_tasks() returns JSON string (not dict)
  - manage_task("create", title="Test") creates task
  - Response size < 100KB for list of 20 tasks
  - pytest tests/test_mcp.py passes

GOTCHAS TO AVOID:
  - CRITICAL: MCP tools MUST return JSON strings (not dicts) (Gotcha #3)
  - ALWAYS truncate description to 1000 chars (Gotcha #3)
  - Limit per_page to MAX_TASKS_PER_PAGE (20) (Gotcha #3)
  - Return structured errors: {"success": false, "error": "...", "suggestion": "..."}

PSEUDOCODE:
@mcp.tool()
async def find_tasks(
    query: str | None = None,
    task_id: str | None = None,
    filter_by: str | None = None,
    filter_value: str | None = None,
    project_id: str | None = None,
    page: int = 1,
    per_page: int = 10
) -> str:
    try:
        per_page = min(per_page, MAX_TASKS_PER_PAGE)  # Limit to 20

        if task_id:
            # Get single task with full details
            task = await task_service.get_task(task_id)
            if not task:
                return json.dumps({
                    "success": False,
                    "error": "Task not found",
                    "suggestion": "Use find_tasks() without task_id to list all tasks"
                })
            # Still truncate description
            if task.get("description") and len(task["description"]) > 1000:
                task["description"] = task["description"][:997] + "..."
            return json.dumps({"success": True, "task": task})

        # List/search mode
        tasks = await task_service.list_tasks(
            query=query,
            filters={filter_by: filter_value} if filter_by else {},
            page=page,
            per_page=per_page,
            exclude_large_fields=True
        )

        # Optimize each task
        optimized_tasks = [optimize_task_for_mcp(t) for t in tasks]

        return json.dumps({
            "success": True,
            "tasks": optimized_tasks,
            "page": page,
            "total": len(optimized_tasks)
        })
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "suggestion": "Check error message and try again"
        })

---

Task 9: Backend - FastAPI Application
RESPONSIBILITY: Main application initialization with CORS, health checks
FILES TO CREATE:
  - backend/src/main.py

PATTERN TO FOLLOW: Archon main.py + FastAPI docs

SPECIFIC STEPS:
  1. Create FastAPI app with title, description, version
  2. Configure CORS middleware with environment-specific origins
     - Development: ["http://localhost:3000", "http://localhost:5173"]
     - Production: from CORS_ORIGINS environment variable
  3. Add startup event to create database pool
  4. Add shutdown event to close database pool
  5. Include project and task routers with /api prefix
  6. Add health check endpoint: GET /health
  7. Add OpenAPI customization (tags, metadata)

VALIDATION:
  - uvicorn src.main:app --reload starts without errors
  - http://localhost:8000/docs shows OpenAPI documentation
  - http://localhost:8000/health returns {"status": "healthy"}
  - CORS allows requests from http://localhost:3000

GOTCHAS TO AVOID:
  - CRITICAL: Configure CORS with specific origins (Gotcha #8)
  - NEVER use allow_origins=["*"] in production
  - Use environment variable for CORS_ORIGINS

---

Task 10: Frontend - TypeScript Types
RESPONSIBILITY: Type-safe definitions matching backend models
FILES TO CREATE:
  - frontend/src/features/projects/types/project.ts
  - frontend/src/features/tasks/types/task.ts

PATTERN TO FOLLOW: Archon types + backend Pydantic models

SPECIFIC STEPS:
  1. Create Project interface matching ProjectResponse
  2. Create ProjectCreate interface matching backend
  3. Create Task interface matching TaskResponse
  4. Create TaskCreate, TaskUpdate interfaces
  5. Create TaskStatus, TaskPriority literal types
  6. Ensure field names match backend EXACTLY (snake_case)

VALIDATION:
  - TypeScript compiles without errors
  - Types match API responses (test with actual data)

GOTCHAS TO AVOID:
  - Use snake_case (project_id, created_at) to match backend
  - Use string for dates (ISO 8601 from JSON)
  - Make nullable fields optional or explicitly null

---

Task 11: Frontend - API Client & Services
RESPONSIBILITY: Type-safe API calls with error handling
FILES TO CREATE:
  - frontend/src/features/shared/api/apiClient.ts
  - frontend/src/features/projects/services/projectService.ts
  - frontend/src/features/tasks/services/taskService.ts

PATTERN TO FOLLOW: Archon service layer

SPECIFIC STEPS:
  1. Create axios instance in apiClient.ts with baseURL from env (VITE_API_URL)
  2. Add request interceptor for headers
  3. Add response interceptor for error handling
  4. Create projectService with methods:
     - listProjects(), getProject(id), createProject(data), updateProject(id, data), deleteProject(id)
  5. Create taskService with methods:
     - listTasks(filters), getTask(id), createTask(data), updateTask(id, data), updateTaskPosition(id, status, position), deleteTask(id)
  6. Return typed responses (Promise<Task[]>, Promise<Project>, etc.)

VALIDATION:
  - taskService.listTasks() returns Task[]
  - Network errors throw with message
  - TypeScript infers correct return types

GOTCHAS TO AVOID:
  - Use VITE_API_URL environment variable (not hardcoded)
  - Handle 422 validation errors from backend
  - Return typed data (not axios response directly)

---

Task 12: Frontend - TanStack Query Configuration
RESPONSIBILITY: Query client setup with smart defaults
FILES TO CREATE:
  - frontend/src/features/shared/config/queryClient.ts
  - frontend/src/features/shared/config/queryPatterns.ts
  - frontend/src/features/shared/hooks/useSmartPolling.ts

PATTERN TO FOLLOW: prps/.../examples/frontend/useTaskQueries.ts + Archon config

SPECIFIC STEPS:
  1. Create QueryClient with default options:
     - staleTime: 30_000 (30 seconds)
     - gcTime: 10 * 60 * 1000 (10 minutes)
     - refetchOnWindowFocus: true
     - retry logic (don't retry 4xx errors)
  2. Create STALE_TIMES constants: instant, frequent, normal, rare, static
  3. Create DISABLED_QUERY_KEY constant: ["disabled"]
  4. Create useSmartPolling hook:
     - Listen to visibilitychange event
     - Return refetchInterval: false when hidden, baseInterval when visible
  5. Wrap App in QueryClientProvider

VALIDATION:
  - QueryClient created without errors
  - useSmartPolling pauses when tab hidden
  - TanStack Query DevTools available in dev

GOTCHAS TO AVOID:
  - CRITICAL: Set refetchIntervalInBackground: false to pause polling (Gotcha #10)
  - Use STALE_TIMES constants (not magic numbers)
  - Don't retry 4xx errors (client errors shouldn't retry)

---

Task 13: Frontend - Query Hooks (Tasks)
RESPONSIBILITY: TanStack Query hooks with optimistic updates
FILES TO CREATE:
  - frontend/src/features/tasks/hooks/useTaskQueries.ts

PATTERN TO FOLLOW: prps/task_management_ui/examples/frontend/useTaskQueries.ts

SPECIFIC STEPS:
  1. Create query key factory:
     - taskKeys.all, taskKeys.lists(), taskKeys.byProject(projectId), taskKeys.detail(id)
  2. Create useProjectTasks(projectId) query hook:
     - Use useSmartPolling for refetchInterval
     - staleTime: STALE_TIMES.normal
     - refetchOnWindowFocus: true
  3. Create useTask(taskId) query hook
  4. Create useCreateTask() mutation hook:
     - onMutate: cancel queries, snapshot previous, optimistic update with _localId
     - onError: rollback to previous
     - onSuccess: replace optimistic with server data
  5. Create useUpdateTask() mutation hook (same pattern)
  6. Create useUpdateTaskPosition() mutation hook
  7. Create useDeleteTask() mutation hook

VALIDATION:
  - useProjectTasks returns tasks with isLoading, error states
  - useCreateTask mutation adds task to cache optimistically
  - Optimistic update rolls back on error
  - Polling pauses when tab hidden

GOTCHAS TO AVOID:
  - CRITICAL: await queryClient.cancelQueries() in onMutate (Gotcha #4)
  - Use _localId for stable optimistic entity references
  - Check isPending before triggering mutations
  - Use queryClient.isMutating() to avoid over-invalidation

PSEUDOCODE:
export function useCreateTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: TaskCreate) => taskService.createTask(data),

    onMutate: async (newTaskData) => {
      // CRITICAL: Cancel in-flight queries
      await queryClient.cancelQueries({
        queryKey: taskKeys.byProject(newTaskData.project_id)
      });

      // Snapshot for rollback
      const previous = queryClient.getQueryData(
        taskKeys.byProject(newTaskData.project_id)
      );

      // Optimistic update with stable ID
      const optimisticTask = createOptimisticEntity<Task>({
        ...newTaskData,
        id: 'temp-' + nanoid(),
        status: newTaskData.status || 'todo',
        created_at: new Date().toISOString(),
      });

      queryClient.setQueryData(
        taskKeys.byProject(newTaskData.project_id),
        (old: Task[] = []) => [...old, optimisticTask]
      );

      return { previous, optimisticId: optimisticTask._localId };
    },

    onError: (err, vars, context) => {
      // Rollback on error
      if (context?.previous) {
        queryClient.setQueryData(
          taskKeys.byProject(vars.project_id),
          context.previous
        );
      }
    },

    onSuccess: (serverTask, vars, context) => {
      // Replace optimistic with real data
      queryClient.setQueryData(
        taskKeys.byProject(vars.project_id),
        (tasks: Task[]) => replaceOptimisticEntity(
          tasks,
          context?.optimisticId,
          serverTask
        )
      );
    },
  });
}

---

Task 14: Frontend - Drag-and-Drop (Kanban Column)
RESPONSIBILITY: Droppable Kanban column with visual feedback
FILES TO CREATE:
  - frontend/src/features/tasks/components/KanbanColumn.tsx

PATTERN TO FOLLOW: prps/task_management_ui/examples/frontend/KanbanColumn.tsx

SPECIFIC STEPS:
  1. Define ItemTypes constant: { TASK: 'task' }
  2. Define TaskDragItem interface: { id: string, status: TaskStatus }
  3. Create KanbanColumn component with props: status, tasks, onTaskMove
  4. Use useDrop<TaskDragItem, void, { isOver: boolean }>():
     - accept: ItemTypes.TASK
     - drop: (item) => { if (item.status !== status) onTaskMove(item.id, status) }
     - collect: (monitor) => ({ isOver: !!monitor.isOver() })
  5. Attach drop ref to column container
  6. Add visual feedback classes when isOver
  7. Render TaskCard components for each task

VALIDATION:
  - Column highlights when dragging task over it
  - Dropping task triggers onTaskMove callback
  - TypeScript types are correct

GOTCHAS TO AVOID:
  - CRITICAL: Provide explicit type parameters to useDrop (Gotcha #9)
  - Use ItemTypes constant (not magic string "task")
  - Only call onTaskMove if status changed

---

Task 15: Frontend - Drag-and-Drop (Task Card)
RESPONSIBILITY: Draggable task card
FILES TO CREATE:
  - frontend/src/features/tasks/components/TaskCard.tsx

PATTERN TO FOLLOW: Archon TaskCard + react-dnd docs

SPECIFIC STEPS:
  1. Create TaskCard component with props: task, onUpdate
  2. Use useDrag<TaskDragItem, void, { isDragging: boolean }>():
     - type: ItemTypes.TASK
     - item: { id: task.id, status: task.status }
     - collect: (monitor) => ({ isDragging: !!monitor.isDragging() })
  3. Attach drag ref to card container
  4. Add opacity: isDragging ? 0.5 : 1 for visual feedback
  5. Render task title, priority badge, assignee

VALIDATION:
  - Card becomes draggable
  - Card opacity reduces while dragging
  - TypeScript types are correct

GOTCHAS TO AVOID:
  - Provide explicit type parameters to useDrag (Gotcha #9)
  - Don't prevent default drag behavior

---

Task 16: Frontend - Kanban Board View
RESPONSIBILITY: 4-column Kanban layout with drag-and-drop integration
FILES TO CREATE:
  - frontend/src/features/tasks/components/KanbanBoard.tsx
  - frontend/src/pages/KanbanPage.tsx

PATTERN TO FOLLOW: Archon Kanban board

SPECIFIC STEPS:
  1. Create KanbanBoard component
  2. Use useProjectTasks(projectId) to fetch tasks
  3. Use useUpdateTaskPosition() mutation for drag-and-drop
  4. Group tasks by status: const tasksByStatus = groupBy(tasks, 'status')
  5. Render 4 KanbanColumn components (todo, doing, review, done)
  6. Pass onTaskMove handler that calls updateTaskPosition.mutate()
  7. Add loading and error states
  8. Wrap app in DndProvider with HTML5Backend

VALIDATION:
  - 4 columns render correctly
  - Dragging task between columns updates status
  - Optimistic update shows immediate feedback
  - Mutation rolls back on error

GOTCHAS TO AVOID:
  - Wrap App in <DndProvider backend={HTML5Backend}> (Gotcha #9)
  - Check updateTaskPosition.isPending before triggering mutation
  - Don't call mutation if source and destination are same

---

Task 17: Frontend - List View
RESPONSIBILITY: Filterable table view with sorting
FILES TO CREATE:
  - frontend/src/features/tasks/components/TaskListView.tsx
  - frontend/src/pages/ListPage.tsx

PATTERN TO FOLLOW: Standard table component patterns

SPECIFIC STEPS:
  1. Create TaskListView component
  2. Use useProjectTasks(projectId) to fetch tasks
  3. Add filter controls: status, assignee, priority dropdowns
  4. Add sort controls: created_at, updated_at, title
  5. Use shadcn/ui Table component
  6. Add inline edit for status (select dropdown)
  7. Click row to open TaskDetailModal
  8. Add pagination controls

VALIDATION:
  - Filters update query parameters
  - Sorting works correctly
  - Inline status edit triggers mutation
  - Pagination navigates correctly

GOTCHAS TO AVOID:
  - Use URL query params for filters (not local state)
  - Debounce filter changes to reduce API calls

---

Task 18: Frontend - Task Detail Modal
RESPONSIBILITY: Edit task details in modal
FILES TO CREATE:
  - frontend/src/features/tasks/components/TaskDetailModal.tsx

PATTERN TO FOLLOW: shadcn/ui Dialog component

SPECIFIC STEPS:
  1. Use shadcn/ui Dialog component
  2. Add form fields: title (input), description (textarea), status (select), priority (select), assignee (input)
  3. Use react-markdown for description preview
  4. Use useUpdateTask() mutation for save
  5. Add delete button with confirmation
  6. Close modal on successful save

VALIDATION:
  - Modal opens when clicking task
  - Form edits task fields
  - Save button triggers mutation
  - Modal closes on save

GOTCHAS TO AVOID:
  - Validate form before submitting
  - Show loading state during mutation

---

Task 19: Docker - Compose Configuration
RESPONSIBILITY: Multi-service deployment with health checks
FILES TO CREATE:
  - docker-compose.yml
  - .env.example

PATTERN TO FOLLOW: prps/task_management_ui/examples/docker/docker-compose.yml

SPECIFIC STEPS:
  1. Create db service:
     - image: postgres:16
     - Named volume: taskmanager-db-data
     - Health check: pg_isready -U taskuser -d taskmanager
     - Environment: POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
  2. Create backend service:
     - build: ./backend
     - depends_on: db (condition: service_healthy)
     - ports: 8000:8000, 8051:8051
     - volumes: ./backend:/app (hot reload)
     - environment: DATABASE_URL, MCP_PORT, CORS_ORIGINS
  3. Create frontend service:
     - build: ./frontend
     - depends_on: backend
     - ports: 3000:3000
     - volumes: ./frontend:/app (exclude node_modules)
     - environment: VITE_API_URL
  4. Create named volume: taskmanager-db-data
  5. Create .env.example with all variables documented

VALIDATION:
  - docker-compose up starts all services
  - Backend waits for database health check
  - Data persists after docker-compose down && docker-compose up
  - Hot reload works for backend and frontend

GOTCHAS TO AVOID:
  - CRITICAL: Use named volume (not bind mount) for PostgreSQL data (Gotcha #5)
  - depends_on with service_healthy waits for health check (Gotcha #13)
  - start_period: 10s gives database time to initialize
  - Exclude node_modules from frontend volume mount

---

Task 20: Docker - Backend Dockerfile
RESPONSIBILITY: Multi-stage Dockerfile for backend
FILES TO CREATE:
  - backend/Dockerfile

PATTERN TO FOLLOW: Archon Dockerfile + uv patterns

SPECIFIC STEPS:
  1. Build stage: python:3.12-slim
     - Install uv
     - Copy pyproject.toml, uv.lock
     - Run uv sync --frozen
  2. Runtime stage: python:3.12-slim
     - Copy .venv from builder
     - Copy src/
     - Set PATH to .venv/bin
     - Expose 8000 and 8051
     - CMD: uvicorn src.main:app --host 0.0.0.0 --port 8000

VALIDATION:
  - docker build -t taskmanager-backend ./backend builds successfully
  - docker run taskmanager-backend starts without errors
  - Image size reasonable (< 500MB)

GOTCHAS TO AVOID:
  - Use multi-stage to reduce image size
  - Copy .venv (not reinstall) in runtime stage
  - Expose both API port (8000) and MCP port (8051)

---

Task 21: Docker - Frontend Dockerfile
RESPONSIBILITY: Frontend build for development
FILES TO CREATE:
  - frontend/Dockerfile

PATTERN TO FOLLOW: Standard Vite Dockerfile

SPECIFIC STEPS:
  1. FROM node:20-alpine
  2. WORKDIR /app
  3. Copy package.json, package-lock.json
  4. Run npm ci
  5. Copy src/, public/, vite.config.ts, etc.
  6. Expose 3000
  7. CMD: npm run dev -- --host

VALIDATION:
  - docker build -t taskmanager-frontend ./frontend builds successfully
  - docker run taskmanager-frontend starts dev server
  - Hot reload works when volumes mounted

GOTCHAS TO AVOID:
  - Use npm ci (not npm install) for reproducible builds
  - Include --host flag for Vite to accept external connections

---

Task 22: Testing - Backend Unit Tests
RESPONSIBILITY: Test service layer and API endpoints
FILES TO CREATE:
  - backend/tests/test_task_service.py
  - backend/tests/test_api_tasks.py

PATTERN TO FOLLOW: pytest patterns

SPECIFIC STEPS:
  1. Create test_task_service.py:
     - Test create_task with valid data
     - Test update_task_position with concurrent updates
     - Test validation errors
  2. Create test_api_tasks.py:
     - Test GET /api/tasks with filters
     - Test POST /api/tasks with invalid data (422)
     - Test PATCH /api/tasks/{id}/position
  3. Use pytest-asyncio for async tests
  4. Use fixtures for database setup

VALIDATION:
  - pytest backend/tests/ -v passes all tests
  - Coverage > 80% for service layer

GOTCHAS TO AVOID:
  - Use @pytest.mark.asyncio for async tests
  - Clean up test data after each test

---

Task 23: Testing - MCP Integration Tests
RESPONSIBILITY: Test MCP tools end-to-end
FILES TO CREATE:
  - backend/tests/test_mcp.py

PATTERN TO FOLLOW: MCP testing patterns

SPECIFIC STEPS:
  1. Test find_tasks() returns JSON string
  2. Test find_tasks(task_id="uuid") returns single task
  3. Test manage_task("create", ...) creates task
  4. Test manage_task("update", ...) updates task
  5. Test error responses have structured format
  6. Verify response sizes < 100KB

VALIDATION:
  - pytest backend/tests/test_mcp.py -v passes
  - All tools return JSON strings (not dicts)

GOTCHAS TO AVOID:
  - Parse JSON response to verify structure
  - Test that description truncation works

---

Task 24: Documentation
RESPONSIBILITY: Setup instructions and API documentation
FILES TO CREATE:
  - README.md

SPECIFIC STEPS:
  1. Add project overview
  2. Add prerequisites (Docker, Docker Compose)
  3. Add setup instructions:
     - Copy .env.example to .env
     - docker-compose up --build
     - Access UI at http://localhost:3000
     - Access MCP at http://localhost:8051/mcp
  4. Add example MCP commands
  5. Add development workflow (hot reload, testing)
  6. Add troubleshooting section

VALIDATION:
  - Following README from scratch works
  - All environment variables documented

GOTCHAS TO AVOID:
  - Document all environment variables in .env.example
  - Include MCP access example: npx mcp-remote http://localhost:8051/mcp

---

Task 25: Final Integration & Testing
RESPONSIBILITY: End-to-end validation of all features
NO NEW FILES - TESTING ONLY

SPECIFIC STEPS:
  1. docker-compose up --build
  2. Access http://localhost:3000
  3. Create project via UI
  4. Create tasks via UI
  5. Drag task from "todo" to "doing" in Kanban view
  6. Verify optimistic update + server sync
  7. Test MCP via npx mcp-remote http://localhost:8051/mcp:
     - find_tasks()
     - manage_task("create", title="Test from MCP")
     - Verify task appears in UI
  8. Test filters in list view
  9. Test task detail modal
  10. Restart containers, verify data persists

VALIDATION:
  - All success criteria from "What" section pass
  - Performance benchmarks met (< 500ms MCP, < 200ms drag)
  - No console errors in browser
  - No errors in docker-compose logs

GOTCHAS TO AVOID:
  - Test with fresh database (docker-compose down -v)
  - Verify ETag caching (Network tab shows 304 responses)
  - Test concurrent drag-and-drop (open two browser windows)
```

### Integration Points

```yaml
ENVIRONMENT VARIABLES:
  - .env file with:
    - DATABASE_URL: postgresql://taskuser:password@db:5432/taskmanager
    - DB_PASSWORD: (secure password)
    - MCP_PORT: 8051
    - API_PORT: 8000
    - FRONTEND_PORT: 3000
    - CORS_ORIGINS: http://localhost:3000,http://localhost:5173
    - VITE_API_URL: http://localhost:8000
    - ENVIRONMENT: development (or production)

API ROUTES:
  - Backend includes routers in main.py:
    - app.include_router(projects_router, prefix="/api", tags=["projects"])
    - app.include_router(tasks_router, prefix="/api", tags=["tasks"])

MCP SERVER:
  - Run separately or as part of backend process
  - Accessible via HTTP transport: http://localhost:8051/mcp
  - Tools auto-discovered by Claude Code/Cursor

FRONTEND BUILD:
  - Vite environment variables prefixed with VITE_
  - API calls use VITE_API_URL from .env
  - Production build: npm run build → dist/ served by nginx
```

---

## Validation Loop

### Level 1: Syntax & Style Checks

**Backend**:
```bash
# Run FIRST - fix any errors before proceeding
cd backend
uv run ruff check src/ --fix  # Auto-fix what's possible
uv run mypy src/             # Type checking

# Expected: No errors. If errors, READ the error and fix.
```

**Frontend**:
```bash
cd frontend
npm run lint                 # ESLint
npm run type-check           # TypeScript compiler

# Expected: No errors
```

### Level 2: Unit Tests

**Backend**:
```bash
cd backend
uv run pytest tests/ -v      # All tests
uv run pytest tests/test_task_service.py -v  # Specific test

# Expected: All tests pass
# If failing: Read error, understand root cause, fix code, re-run
```

**Frontend**:
```bash
cd frontend
npm run test                 # Vitest

# Expected: All tests pass
```

### Level 3: Integration Tests

**Start Services**:
```bash
docker-compose up --build

# Expected:
# - db: Health check passes
# - backend: Starts after db healthy, no errors in logs
# - frontend: Dev server starts, accessible at http://localhost:3000
```

**Test Web UI**:
```bash
# 1. Create project
# Browser: http://localhost:3000 → "New Project" → Name: "Test Project" → Create

# 2. Create task
# Click project → "New Task" → Title: "Test Task" → Description: "Test" → Create

# 3. Drag task
# Kanban view → Drag "Test Task" from "todo" to "doing"

# Expected: Task moves immediately (optimistic), then syncs with server
```

**Test MCP Server**:
```bash
# Connect to MCP server
npx mcp-remote http://localhost:8051/mcp

# In MCP client:
# find_tasks()
# Expected: {"success": true, "tasks": [...]}

# manage_task("create", title="MCP Task", status="todo")
# Expected: {"success": true, "task": {...}}

# Verify in UI: Refresh browser, task should appear
```

**Test API Endpoints**:
```bash
# List tasks
curl http://localhost:8000/api/tasks | jq

# Create task
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "API Task", "status": "todo"}' | jq

# Update task position
curl -X PATCH http://localhost:8000/api/tasks/{task_id}/position \
  -H "Content-Type: application/json" \
  -d '{"status": "doing", "position": 0}' | jq

# Expected: All return 200/201 with JSON data
```

### Level 4: Performance Tests

```bash
# MCP response time
time npx mcp-remote http://localhost:8051/mcp -c 'find_tasks()'
# Expected: < 500ms

# Drag-and-drop latency
# Browser DevTools → Network → Drag task → Check PATCH request
# Expected: < 200ms

# Database query performance
docker exec -it taskmanager-db psql -U taskuser -d taskmanager
# In psql:
EXPLAIN ANALYZE SELECT * FROM tasks WHERE project_id = 'some-uuid' AND status = 'todo' ORDER BY position;
# Expected: Index Scan (not Seq Scan)
```

---

## Final Validation Checklist

**Deployment**:
- [ ] docker-compose up starts all services without errors
- [ ] Health checks pass: docker-compose ps shows all services healthy
- [ ] Web UI accessible at http://localhost:3000
- [ ] MCP server responds to npx mcp-remote http://localhost:8051/mcp
- [ ] Data persists after docker-compose down && docker-compose up

**Functionality**:
- [ ] Can create project via UI
- [ ] Can create task with all fields (title, description, status, priority, assignee)
- [ ] Kanban board displays tasks in 4 columns
- [ ] Drag task between columns updates status immediately (optimistic update)
- [ ] List view shows tasks with working filters (status, assignee, priority)
- [ ] Task detail modal edits task fields
- [ ] Manual drag-and-drop ordering within columns persists
- [ ] MCP find_tasks() returns task list
- [ ] MCP manage_task("create", ...) creates task visible in UI
- [ ] MCP manage_task("update", ...) updates task in UI

**Quality**:
- [ ] All backend tests pass: pytest backend/tests/ -v
- [ ] All frontend tests pass: npm run test
- [ ] No linting errors: ruff check, npm run lint
- [ ] No type errors: mypy, npm run type-check
- [ ] OpenAPI docs at http://localhost:8000/docs
- [ ] README with setup instructions
- [ ] .env.example with all variables documented

**Performance**:
- [ ] MCP find_tasks() < 500ms for 100 tasks
- [ ] Drag-and-drop perceived latency < 200ms
- [ ] Database queries use indexes (verify with EXPLAIN ANALYZE)
- [ ] UI polling rate ≤ 1 req/sec when active

**Gotcha Verification**:
- [ ] No blocking I/O in async endpoints (Gotcha #1)
- [ ] Position reordering uses transactions + row locking (Gotcha #2)
- [ ] MCP responses truncated to < 100KB (Gotcha #3)
- [ ] Optimistic updates cancel queries in onMutate (Gotcha #4)
- [ ] PostgreSQL uses named volume (not bind mount) (Gotcha #5)
- [ ] Pydantic uses @field_validator (not @validator) (Gotcha #6)
- [ ] All foreign keys have indexes (Gotcha #7)
- [ ] CORS configured with specific origins (Gotcha #8)
- [ ] react-dnd hooks have explicit type parameters (Gotcha #9)
- [ ] TanStack Query uses STALE_TIMES constants (Gotcha #10)

---

## Anti-Patterns to Avoid

```yaml
Backend:
  - ❌ Don't call blocking functions in async def endpoints (Gotcha #1)
  - ❌ Don't skip transactions for position updates (Gotcha #2)
  - ❌ Don't return large MCP responses without truncation (Gotcha #3)
  - ❌ Don't use Pydantic V1 syntax (@validator) (Gotcha #6)
  - ❌ Don't skip indexes on foreign keys (Gotcha #7)
  - ❌ Don't use allow_origins=["*"] in CORS (Gotcha #8)

Frontend:
  - ❌ Don't skip query cancellation in onMutate (Gotcha #4)
  - ❌ Don't use magic numbers for staleTime (Gotcha #10)
  - ❌ Don't omit type parameters for react-dnd hooks (Gotcha #9)
  - ❌ Don't manually invalidate cache in useEffect (use refetchInterval)
  - ❌ Don't hardcode API URLs (use VITE_API_URL)

Docker:
  - ❌ Don't use bind mounts for PostgreSQL data (Gotcha #5)
  - ❌ Don't skip health checks in depends_on (Gotcha #13)
  - ❌ Don't forget start_period for database initialization

General:
  - ❌ Don't create new patterns when proven ones exist
  - ❌ Don't skip validation because "it should work"
  - ❌ Don't ignore failing tests - fix them
  - ❌ Don't hardcode values that should be environment variables
```

---

## Success Metrics

**Deployment Success**:
- Single command (`docker-compose up`) runs entire stack
- Zero manual configuration steps beyond `.env` file
- Data persists across container restarts

**Developer Experience**:
- Hot reload works for both backend and frontend
- Clear error messages guide debugging
- OpenAPI docs provide interactive API testing
- TypeScript provides compile-time safety

**AI Integration**:
- Claude Code can autonomously manage task queue via MCP
- AI-friendly error messages guide recovery from failures
- MCP response times enable real-time AI interaction

**Code Quality**:
- 80%+ test coverage on service layer
- Zero linting/type errors
- Clean architecture (API → Service → Database)
- Proven patterns from Archon production codebase

---

## PRP Quality Self-Assessment

**Score: 9/10** - High confidence in one-pass implementation success

**Reasoning**:

**Strengths** (what earns the 9/10):
- ✅ **Comprehensive Context**: All 5 research docs synthesized (1,400+ lines total research)
- ✅ **Clear Task Breakdown**: 25 ordered tasks with specific steps, validation, and gotchas
- ✅ **Proven Patterns**: 6 working code examples extracted from Archon production
- ✅ **Validation Strategy**: 4-level validation (syntax, unit, integration, performance)
- ✅ **Error Handling**: 13 documented gotchas with detection and solutions
- ✅ **Complete Tech Stack**: All decisions justified with Archon reference
- ✅ **Executable Checks**: All validation commands are runnable
- ✅ **Documentation Links**: Direct URLs to critical sections with gotcha warnings
- ✅ **Data Model**: Fully specified with indexes, constraints, and triggers
- ✅ **Type Safety**: End-to-end types (Pydantic → PostgreSQL → TypeScript)

**Confidence Factors**:
1. **Archon Reference**: 95% pattern match to proven production codebase
2. **Working Examples**: All 6 code examples are executable, not pseudocode
3. **Gotcha Coverage**: 13 critical issues pre-documented with solutions
4. **Clear Dependencies**: Task order explicitly handles dependencies
5. **Validation Gates**: Each task has specific pass/fail criteria

**Minor Deductions** (why not 10/10):
- ⚠️ **Manual Type Sharing**: Python → TypeScript types require manual sync (acceptable for MVP, but could use codegen)
- ⚠️ **Example File Paths**: Assumes examples directory structure exists (created by Example Curator, should be verified)
- ⚠️ **Environment Complexity**: Two-language stack requires managing Python + Node ecosystems
- ⚠️ **No E2E Tests**: Playwright integration tests not included (manual testing sufficient for MVP)

**Gaps Addressed**:
- All critical gotchas from research phase documented (Gotchas #1-13)
- All example files referenced and explained
- All documentation URLs link to specific sections
- All validation commands are executable

**Risk Mitigation**:
- If Archon examples directory missing: Document paths are provided, can recreate from codebase
- If type sync fails: Manual review process documented
- If Docker issues: Comprehensive troubleshooting in gotchas.md
- If performance issues: Benchmarks and optimization strategies documented

**First-Pass Implementation Probability**: 85%+

Based on:
- Archon patterns proven in production (beta testing)
- All gotchas pre-documented from real-world experience
- Validation loops enable iterative fixes
- Clear task order prevents dependency errors
- Executable validation commands catch issues early

**What Makes This PRP Ready**:
1. Implementer can start coding with ZERO additional research ✅
2. All decisions justified with rationale ✅
3. Gotchas integrated into task list ✅
4. Task order logical with clear dependencies ✅
5. Validation gates specific and executable ✅
6. Code examples demonstrate all critical patterns ✅
7. Documentation links target exact sections needed ✅
8. Data model fully specified with constraints ✅
9. Performance benchmarks defined ✅
10. Anti-patterns explicitly called out ✅

**Recommendation**: Proceed with implementation. This PRP provides sufficient context for a first-pass implementation with high success probability. Use validation loops to iterate on any issues discovered during implementation.

---

**PRP Generated**: 2025-10-06
**Research Quality**: 9/10 across all 5 phases
**Total Lines**: 2,100+ (PRP) + 1,400+ (research docs) = 3,500+ lines of implementation guidance
**Estimated Implementation Time**: 16-20 hours for experienced developer
**Ready for Implementation**: ✅ Yes
