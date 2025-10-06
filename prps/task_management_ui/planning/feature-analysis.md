# Feature Analysis: task_management_ui

## INITIAL.md Summary

Build a containerized, self-hosted task management system with both web UI and MCP server integration for AI assistant interaction. The system features Kanban board and list views with drag-and-drop task management, follows a 4-state workflow (todo → doing → review → done), supports project/workspace organization, and deploys via Docker with all services self-contained (database, backend, frontend, MCP server). The key principle is that the system provides structure while external AI (via MCP) provides intelligence.

## Core Requirements

### Explicit Requirements

1. **Web UI with Dual Views**
   - Kanban board with drag-and-drop task management
   - List view with filters and sorting
   - Both views must support the same CRUD operations

2. **MCP Server Integration**
   - Accessible via `npx mcp-remote http://localhost:PORT/mcp`
   - Consolidated tool pattern: `find_tasks()` and `manage_task(action, ...)`
   - Claude Code/Cursor compatibility
   - Real-time sync between MCP updates and UI

3. **4-State Workflow**
   - Task statuses: `todo` → `doing` → `review` → `done`
   - Status transitions via drag-and-drop (Kanban) or inline updates (list view)
   - Position tracking for manual drag-and-drop ordering

4. **Project/Workspace Organization**
   - Project creation and management
   - Tasks belong to projects
   - Project-scoped task views

5. **Docker Deployment**
   - Single `docker-compose up` to run all services
   - Services: PostgreSQL, Backend (API + MCP), Frontend (React SPA)
   - Data persistence across container restarts
   - Health checks and restart policies
   - Environment variable configuration

6. **Data Model Core Fields**
   - `id` (UUID), `project_id` (FK, nullable)
   - `title` (required), `description` (markdown support)
   - `status` (todo | doing | review | done)
   - `assignee` (string: "User", agent names, etc.)
   - `priority` (low | medium | high | urgent)
   - `position` (for drag-and-drop ordering)
   - `created_at`, `updated_at`

### Implicit Requirements

1. **Type Safety**
   - End-to-end TypeScript (if choosing Node backend) or Python type hints
   - Shared type definitions between frontend/backend (if different languages)
   - Database schema matches API contracts

2. **API Documentation**
   - OpenAPI/Swagger for REST endpoints
   - Clear MCP tool descriptions for AI assistants

3. **Migration Strategy**
   - Database migrations for schema evolution
   - SQL scripts, Alembic (Python), or Prisma (Node)

4. **Error Handling**
   - Validation on both client and server
   - User-friendly error messages
   - MCP error responses that guide AI assistants

5. **Performance Considerations**
   - Pagination for large task lists in MCP responses
   - Optimized queries (exclude large fields when listing)
   - Real-time updates without WebSockets (HTTP polling preferred)

6. **Development Workflow**
   - Hot reload in development
   - Easy local setup with `.env.example`
   - README with setup instructions

## Technical Components

### Backend API Layer
- **Framework**: FastAPI (Python) or Express/Fastify (Node.js)
- **Responsibilities**:
  - RESTful API for UI
  - MCP server endpoint integration
  - Business logic and validation
  - Database operations
- **Key Endpoints**:
  - `/api/projects` - CRUD for projects
  - `/api/projects/{id}/tasks` - Project-scoped tasks
  - `/api/tasks` - Global task operations
  - `/mcp` - MCP protocol endpoint (or separate port)

### MCP Server
- **Integration Pattern**: Consolidated tools (Archon pattern)
  - `find_tasks(query?, task_id?, filter_by?, filter_value?, project_id?)`
  - `manage_task(action, task_id?, project_id?, title?, description?, status?, ...)`
  - `find_projects(project_id?, query?)`
  - `manage_project(action, project_id?, name?, description?)`
- **Response Optimization**:
  - Exclude large fields (sources, code_examples) in list responses
  - Truncate descriptions to 1000 chars
  - Replace arrays with counts
- **Error Handling**: Structured error responses with suggestions

### Frontend UI
- **Framework**: React 18 with TypeScript
- **State Management**: TanStack Query v5 (no Redux/Zustand needed)
- **UI Libraries**:
  - Drag-and-drop: `react-dnd` (proven in Archon)
  - Component library: shadcn/ui or Radix UI
  - Styling: Tailwind CSS
  - Markdown: react-markdown
- **Key Views**:
  - Project list/switcher
  - Kanban board (4 columns: todo/doing/review/done)
  - List view with filters (status, assignee, priority)
  - Task detail modal/drawer
  - Project settings

### Database
- **Engine**: PostgreSQL
- **Tables**:
  - `projects` (id, name, description, created_at, updated_at)
  - `tasks` (id, project_id, title, description, status, assignee, priority, position, parent_task_id?, created_at, updated_at)
  - `task_dependencies` (id, task_id, depends_on_task_id) - Optional for MVP
- **Considerations**:
  - `position` field for drag-and-drop ordering per status column
  - `parent_task_id` for optional hierarchical tasks (defer to post-MVP)
  - Indexes on `project_id`, `status`, `assignee` for filtering

### Deployment Stack
- **Docker Compose Services**:
  - `db`: PostgreSQL with volume mount
  - `backend`: FastAPI/Express + MCP server
  - `frontend`: React SPA (nginx or serve)
- **Networking**: Internal Docker network + exposed ports
- **Volumes**: Database persistence, config files
- **Health Checks**: Database readiness, API health endpoints

## Tech Stack Recommendations

### Option A: Python/FastAPI Backend (RECOMMENDED)
**Rationale**: Matches vibes ecosystem consistency, Archon reference implementation

**Stack**:
- **Backend**: Python 3.12 + FastAPI + Pydantic
- **Frontend**: React 18 + TypeScript + Vite
- **Database**: PostgreSQL (via asyncpg)
- **MCP**: FastMCP framework (as used in Archon)
- **Validation**: Pydantic models
- **Testing**: pytest (backend), Vitest (frontend)

**Pros**:
- Consistent with existing vibes Python MCP servers
- Can directly reference Archon implementation patterns
- FastMCP provides proven MCP integration
- Strong type safety with Pydantic
- Async/await for performance

**Cons**:
- Type sharing requires duplication (Python models → TS types)
- Two language ecosystems to manage

### Option B: Full-Stack TypeScript (Alternative)
**Rationale**: End-to-end type safety, single language

**Stack**:
- **Backend**: Node.js + TypeScript + Fastify
- **Frontend**: React 18 + TypeScript + Vite
- **Database**: PostgreSQL (via Prisma)
- **MCP**: Custom TypeScript MCP server
- **Validation**: Zod schemas
- **Testing**: Vitest (both backend and frontend)

**Pros**:
- Single language across stack
- Shared types via import
- Prisma provides excellent DX
- Easier for TypeScript-focused developers

**Cons**:
- Less alignment with vibes Python ecosystem
- Need to implement MCP patterns from scratch (no FastMCP)
- Task Master reference is more complex (multi-tenant, auth)

### **RECOMMENDED DECISION: Option A (Python/FastAPI)**
- Leverage Archon's proven patterns
- Reuse vibes MCP infrastructure knowledge
- Better alignment with basic-memory and other Python servers
- Simpler type duplication than building MCP from scratch

## Data Model Design

### Projects Table
```sql
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Tasks Table
```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    parent_task_id UUID REFERENCES tasks(id) ON DELETE SET NULL, -- For future hierarchy
    title VARCHAR(500) NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL CHECK (status IN ('todo', 'doing', 'review', 'done')),
    assignee VARCHAR(255) DEFAULT 'User',
    priority VARCHAR(50) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    position INTEGER DEFAULT 0, -- For drag-and-drop ordering within status column
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- Indexes for performance
    INDEX idx_tasks_project_id (project_id),
    INDEX idx_tasks_status (status),
    INDEX idx_tasks_assignee (assignee),
    INDEX idx_tasks_position (status, position) -- For ordered retrieval per column
);
```

### Task Dependencies Table (Post-MVP)
```sql
CREATE TABLE task_dependencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
    depends_on_task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(task_id, depends_on_task_id)
);
```

### Task Hierarchy Considerations
**MVP Decision**: Flat structure with optional `parent_task_id` (not enforced)

**Rationale**:
- Archon uses flat structure successfully
- Task Master's hierarchical approach (display_id: 1.1.1) adds complexity
- Can add hierarchy post-MVP if needed
- Simpler for Kanban visualization

**Future Enhancement**: If implementing hierarchy
- Add `display_id` generation logic (1, 1.1, 1.1.1)
- UI for expanding/collapsing subtasks
- Cascade status updates (optional)

## MCP Tool Design

### Consolidated Pattern (Archon-style)

**find_tasks Tool**:
```python
@mcp.tool()
async def find_tasks(
    query: str | None = None,           # Keyword search
    task_id: str | None = None,         # Get specific task
    filter_by: str | None = None,       # "status" | "project" | "assignee"
    filter_value: str | None = None,    # Filter value
    project_id: str | None = None,      # Additional project filter
    page: int = 1,
    per_page: int = 10
) -> str:
    """
    Find and search tasks (consolidated: list + search + get).

    Examples:
        find_tasks() # All tasks
        find_tasks(query="auth") # Search
        find_tasks(task_id="uuid") # Get one (full details)
        find_tasks(filter_by="status", filter_value="todo") # Filter

    Returns: JSON array of tasks or single task
    """
```

**manage_task Tool**:
```python
@mcp.tool()
async def manage_task(
    action: str,                        # "create" | "update" | "delete"
    task_id: str | None = None,         # For update/delete
    project_id: str | None = None,      # For create
    title: str | None = None,
    description: str | None = None,
    status: str | None = None,          # "todo" | "doing" | "review" | "done"
    assignee: str | None = None,        # "User", "Archon", agent names
    priority: str | None = None,        # "low" | "medium" | "high" | "urgent"
    position: int | None = None         # For ordering
) -> str:
    """
    Manage tasks (consolidated: create/update/delete).

    Examples:
        manage_task("create", project_id="uuid", title="Implement auth", assignee="User")
        manage_task("update", task_id="uuid", status="doing")
        manage_task("delete", task_id="uuid")

    Returns: {success: bool, task?: object, message: string}
    """
```

**Response Optimization** (from Archon):
```python
def optimize_task_response(task: dict) -> dict:
    """Optimize task for MCP response."""
    # Truncate long descriptions
    if task.get("description") and len(task["description"]) > 1000:
        task["description"] = task["description"][:997] + "..."

    # Replace arrays with counts (if present)
    if "attachments" in task:
        task["attachments_count"] = len(task["attachments"])
        del task["attachments"]

    return task
```

### Project Management Tools

**find_projects Tool**:
```python
@mcp.tool()
async def find_projects(
    project_id: str | None = None,      # Get specific project
    query: str | None = None,           # Keyword search
    page: int = 1,
    per_page: int = 10
) -> str:
    """
    Find and search projects.

    Returns: JSON array of projects or single project
    """
```

**manage_project Tool**:
```python
@mcp.tool()
async def manage_project(
    action: str,                        # "create" | "update" | "delete"
    project_id: str | None = None,      # For update/delete
    name: str | None = None,
    description: str | None = None
) -> str:
    """
    Manage projects (create/update/delete).

    Returns: {success: bool, project?: object, message: string}
    """
```

## Architecture Decisions

### 1. Real-Time Updates: HTTP Polling (No WebSockets)
**Decision**: Use HTTP polling with smart intervals (Archon pattern)

**Rationale**:
- Simpler implementation and debugging
- Works through proxies/firewalls
- Archon's smart polling pauses when tab hidden
- ETag caching reduces bandwidth by ~70%

**Implementation**:
- Frontend: TanStack Query with `refetchInterval`
- Smart polling hook: variable intervals based on tab visibility
- Backend: ETag support for cache validation

**Alternative Considered**: WebSockets
- More complex (connection management, reconnection logic)
- Overkill for task management updates
- Adds deployment complexity (reverse proxy config)

### 2. Authentication: Single-User Initially
**Decision**: Skip auth for MVP, design for future multi-user

**Rationale**:
- Self-hosted implies single user or trusted environment
- Can add auth later (JWT, session-based, or OAuth)
- Reduces initial complexity
- MCP assumes local/trusted context

**Future Path**:
- Add `user_id` to tasks/projects tables
- Implement authentication middleware
- Filter queries by authenticated user

### 3. Task Hierarchy: Flat with Optional Parent (Not Enforced)
**Decision**: Include `parent_task_id` field but don't enforce hierarchy in MVP

**Rationale**:
- Archon's flat approach works well
- Simpler Kanban visualization
- Can add UI for hierarchy post-MVP
- Avoids complexity of Task Master's display_id system

**Implementation**:
- `parent_task_id UUID NULL` in schema
- UI shows as flat list initially
- Future: Add expand/collapse, indentation

### 4. Backend Framework: FastAPI (Python)
**Decision**: Use Python + FastAPI + FastMCP

**Rationale**:
- Matches vibes ecosystem (basic-memory, Archon)
- Proven MCP integration patterns
- Can directly copy Archon's service layer architecture
- Strong typing with Pydantic
- Async support for performance

**Trade-off**: Type duplication between Python and TypeScript
- Mitigated by: Code generation or manual sync of critical types
- Acceptable for standalone system

### 5. Drag-and-Drop: react-dnd (Proven in Archon)
**Decision**: Use react-dnd library

**Rationale**:
- Already proven in Archon's Kanban board
- Mature library with good TypeScript support
- Handles complex scenarios (hover, drop zones, previews)

**Implementation Pattern** (from Archon):
```typescript
// KanbanColumn.tsx
const [{ isOver }, drop] = useDrop({
    accept: ItemTypes.TASK,
    drop: (item: { id: string; status: Task["status"] }) => {
        if (item.status !== status) {
            onTaskMove(item.id, status);
        }
    },
    collect: (monitor) => ({ isOver: !!monitor.isOver() }),
});
```

### 6. State Management: TanStack Query (No Redux)
**Decision**: Use TanStack Query v5 exclusively

**Rationale**:
- Handles all server state (tasks, projects)
- Built-in caching, deduplication, polling
- Optimistic updates for instant UI feedback
- Archon successfully eliminated Redux with this approach

**Implementation**:
- Query key factories per feature
- Shared stale times via constants
- Optimistic updates with rollback on error

### 7. Docker Composition: All-in-One vs. Hybrid
**Decision**: All-in-one Docker Compose for production, hybrid for dev

**Production** (`docker-compose.yml`):
```yaml
services:
  db:
    image: postgres:16
    volumes:
      - task-manager-db:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: taskmanager
      POSTGRES_USER: taskuser
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U taskuser"]
      interval: 5s

  backend:
    build: ./backend
    depends_on:
      db:
        condition: service_healthy
    environment:
      DATABASE_URL: postgresql://taskuser:${DB_PASSWORD}@db:5432/taskmanager
      MCP_PORT: 8051
    ports:
      - "8000:8000"
      - "8051:8051"

  frontend:
    build: ./frontend
    depends_on:
      - backend
    ports:
      - "3000:3000"
```

**Development**: Hybrid approach
- Backend in Docker (or local with `uv run`)
- Frontend local (`npm run dev`) for hot reload
- Database in Docker always

## Similar Implementations Found in Archon

### 1. Archon Task Management System
**Relevance**: 9/10
**Archon Source ID**: e9eb05e2bf38f125 (Task service), 9a7d4217c64c9a0a (MCP docs)

**Key Patterns to Reuse**:
- **MCP Consolidation Pattern** (`find_tasks`, `manage_task`)
  - Location: `/Users/jon/source/vibes/repos/Archon/python/src/mcp_server/features/tasks/task_tools.py`
  - Single tool for CRUD operations via `action` parameter
  - Optimized responses (truncate, exclude large fields)
  - Structured error handling with suggestions

- **Service Layer Architecture**
  - Location: `/Users/jon/source/vibes/repos/Archon/python/src/server/services/projects/task_service.py`
  - Clean separation: API route → Service → Database
  - Validation in service layer
  - Async/await pattern

- **React + TanStack Query Pattern**
  - Location: `/Users/jon/source/vibes/repos/Archon/archon-ui-main/src/features/projects/tasks/`
  - Query key factories per feature
  - Shared stale times and polling config
  - Optimistic updates with rollback
  - No Redux/Zustand needed

- **Kanban Drag-and-Drop**
  - Location: `/Users/jon/source/vibes/repos/Archon/archon-ui-main/src/features/projects/tasks/components/KanbanColumn.tsx`
  - react-dnd for drag operations
  - Status transition on drop
  - Visual feedback during hover

**Gotchas from Archon**:
- ETag implementation requires browser-native HTTP caching (don't build manual cache)
- Smart polling must pause when tab hidden to save resources
- Always exclude large JSONB fields in list responses for MCP
- Status filter + include_closed can conflict - handle carefully

### 2. Task Master Hierarchical System
**Relevance**: 6/10
**Reference Location**: `/Users/jon/source/vibes/repos/claude-task-master/`

**Key Patterns to Extract**:
- **Hierarchical Task Structure** (defer to post-MVP)
  - `parent_task_id` foreign key to self
  - `display_id` for human-readable IDs (1, 1.1, 1.1.1)
  - Position tracking at each level
  - Dependencies table for complex workflows

- **Task Dependencies**
  - Separate `task_dependencies` table
  - Many-to-many relationships
  - Validation to prevent circular dependencies

**What NOT to Copy**:
- Multi-tenant architecture (accounts, users) - overkill for MVP
- Complex document processing - out of scope
- Brief/plan generation - different domain

**Gotchas from Task Master**:
- Display ID generation adds significant complexity
- Hierarchical position tracking requires careful reordering logic
- Subtask counts need to be kept in sync

### 3. FastMCP Framework Patterns
**Relevance**: 8/10
**Source**: Archon MCP implementation

**Key Patterns**:
- Tool registration via decorators
- JSON string responses (MCP protocol requirement)
- Error formatting utilities
- Timeout configuration
- Service discovery for API URLs

**Example from Archon**:
```python
@mcp.tool()
async def find_tasks(ctx: Context, ...) -> str:
    try:
        # Implementation
        return json.dumps({"success": True, "tasks": ...})
    except httpx.RequestError as e:
        return MCPErrorFormatter.from_exception(e, "list tasks")
```

## Open Questions & Research Areas

### 1. UI Component Library Choice
**Question**: shadcn/ui vs. Radix UI primitives directly?

**Research Needed**:
- Archon uses Radix UI primitives with custom styling
- shadcn/ui provides pre-styled components
- Trade-off: Flexibility vs. speed of development

**Recommendation**: Start with shadcn/ui for speed, can always refactor to raw Radix

### 2. Markdown Editor Selection
**Question**: Full editor (react-markdown-editor-lite) vs. simple viewer (react-markdown)?

**Options**:
- Full editor: WYSIWYG editing, toolbar, preview
- Simple viewer: Render markdown, edit in textarea
- Hybrid: Textarea with live preview

**Recommendation**: Start with simple textarea + react-markdown preview (Archon pattern)

### 3. Real-Time Sync Strategy
**Question**: Polling interval configuration?

**Based on Archon**:
- Active operations: 3-5 seconds
- Normal data: 30 seconds
- Tab hidden: 1.5x slower
- Manual refresh always available

**Recommendation**: Follow Archon's `STALE_TIMES` constants

### 4. Migration Strategy
**Question**: SQL files vs. Alembic vs. Prisma?

**Options**:
- Raw SQL: Simple, full control, manual tracking
- Alembic (Python): Versioning, auto-generation, rollback
- Prisma (if Node): Great DX, type generation, requires Node

**Recommendation**: Alembic for Python backend (matches Archon patterns)

### 5. List View Implementation
**Question**: Virtual scrolling for large lists?

**Research**:
- Standard approach: Pagination (10-50 items per page)
- Advanced: react-window for virtual scrolling
- Archon uses: Standard pagination

**Recommendation**: Start with pagination, add virtual scrolling if needed

### 6. Task Position Reordering Logic
**Question**: How to handle position conflicts on drag-and-drop?

**Archon Pattern** (from task_service.py):
```python
# If inserting at position N:
# 1. Get all tasks with position >= N
# 2. Increment each by 1
# 3. Insert new task at position N
```

**Alternative**: Use fractional positions (1.0, 1.5, 2.0) to avoid mass updates
- Pro: Fewer database writes
- Con: Eventual position normalization needed

**Recommendation**: Follow Archon's increment pattern (simpler, proven)

### 7. Docker Image Optimization
**Question**: Multi-stage builds vs. simple builds?

**Options**:
- Multi-stage: Smaller images, longer build time
- Simple: Faster builds, larger images
- Dev vs. Prod: Different Dockerfiles

**Recommendation**: Multi-stage for production, simple for dev (standard practice)

### 8. Environment Variable Management
**Question**: .env file handling in Docker?

**Best Practice**:
- `.env.example` in repo (template)
- `.env` in `.gitignore`
- Docker Compose reads `.env` automatically
- Validation on startup (fail if missing required vars)

**Critical Variables**:
- `DATABASE_URL` or components (host, port, user, password, db)
- `PORT` (API server)
- `MCP_PORT` (MCP server)
- `NODE_ENV` or `ENVIRONMENT` (dev/prod)

### 9. Test Strategy
**Question**: Unit vs. Integration test coverage?

**Recommendation** (based on vibes patterns):
- Backend: pytest with FastAPI test client (async)
- Frontend: Vitest + React Testing Library
- Integration: Test MCP tools via client
- E2E: Optional Playwright for critical flows

**Priority**:
1. MCP tool tests (AI assistants depend on these)
2. Service layer tests (business logic)
3. API endpoint tests
4. Frontend component tests

### 10. Type Sharing Strategy (Python ↔ TypeScript)
**Question**: Manual duplication vs. code generation?

**Options**:
- Manual: Copy types, keep in sync
- Pydantic → TypeScript generator (e.g., pydantic-to-typescript)
- JSON Schema intermediate (Pydantic → JSON Schema → TS)

**Recommendation**: Manual for MVP (only ~5-10 types), evaluate generators if types grow

## Assumptions Made

### 1. **Deployment Context**: Self-hosted, trusted environment
**Reasoning**: INITIAL.md emphasizes "self-hosted" and "containerized"
- No multi-tenancy in MVP
- Authentication deferred to post-MVP
- Single user or trusted team assumed

### 2. **Performance Scale**: <1000 tasks per project
**Reasoning**: Task management UI for individual/small team use
- Pagination at 10-50 items sufficient
- No need for advanced caching layers
- Standard PostgreSQL indexes adequate

### 3. **MCP Usage**: Primary interface for AI assistants, secondary for humans
**Reasoning**: "System provides structure, external AI provides intelligence"
- MCP tools must be robust and well-documented
- UI is for human oversight and manual management
- MCP responses optimized for AI consumption (truncated, counts)

### 4. **Task Complexity**: Mostly flat, optional hierarchy
**Reasoning**: INITIAL.md doesn't mandate hierarchy; Archon proves flat works
- `parent_task_id` included for future use
- No display_id generation in MVP
- Can add hierarchy UI post-MVP if needed

### 5. **Real-Time Requirements**: 30-second staleness acceptable
**Reasoning**: Task management isn't mission-critical real-time
- Archon's polling pattern sufficient
- Manual refresh always available
- Optimistic updates provide instant feedback

### 6. **Integration with Vibes**: Standalone, no cross-dependencies
**Reasoning**: INITIAL.md specifies "standalone" and "does NOT depend on other vibes MCP servers"
- Own database (not shared with Archon)
- Independent Docker Compose
- Optional future linking to basic-memory

### 7. **UI Styling**: Tron-inspired glassmorphism (vibes aesthetic)
**Reasoning**: Archon reference uses this pattern; vibes project likely expects visual consistency
- Tailwind CSS with custom theme
- Glassmorphism effects (backdrop-blur, gradients)
- Cyan/purple accent colors

### 8. **Database**: PostgreSQL without Supabase
**Reasoning**: INITIAL.md says "with or without Supabase"; simpler without for standalone system
- Direct PostgreSQL connection
- No Supabase auth/storage overhead
- Standard asyncpg driver (Python) or pg (Node)

### 9. **Error Handling**: AI-friendly error messages in MCP
**Reasoning**: AI assistants need actionable error guidance
- Structured error format: `{success: false, error: "message", suggestion: "action"}`
- HTTP status codes mapped to error types
- From Archon: `MCPErrorFormatter` pattern

### 10. **Development Workflow**: Docker for deployment, hybrid for dev
**Reasoning**: Standard practice for containerized apps
- `docker-compose up` for full stack
- Local frontend dev for hot reload
- Database always in Docker

## Success Criteria (from INITIAL.md)

### Deployment Success
- ✅ `docker-compose up` runs all services without errors
- ✅ Web UI accessible at `http://localhost:3000`
- ✅ Data persists across container restarts (volume-mounted PostgreSQL)
- ✅ Health checks pass for all services
- ✅ `.env.example` provided with all required variables

### UI Functionality Success
- ✅ Can create projects via UI
- ✅ Can create tasks (title, description, status, assignee, priority)
- ✅ Kanban board displays tasks in 4 columns (todo/doing/review/done)
- ✅ List view shows tasks with filters (status, assignee, priority) and sorting
- ✅ Can drag tasks between status columns (Kanban)
- ✅ Can update task details inline (list view) or via modal
- ✅ Task position updates reflect drag-and-drop order

### MCP Integration Success
- ✅ MCP server accessible via `npx mcp-remote http://localhost:8051/mcp` (or configured port)
- ✅ `find_tasks()` returns task list with proper filtering
- ✅ `find_tasks(task_id="uuid")` returns single task with full details
- ✅ `manage_task("create", ...)` creates task visible in UI immediately
- ✅ `manage_task("update", ...)` updates task with UI sync
- ✅ `manage_task("delete", ...)` removes task from UI
- ✅ Claude Code can manage tasks via MCP tools without errors

### Quality Success
- ✅ Type safety: Python type hints or end-to-end TypeScript
- ✅ Clean architecture: Service layer separates business logic from API routes
- ✅ API documentation: OpenAPI/Swagger UI available
- ✅ README with setup instructions (prerequisites, environment setup, run commands)
- ✅ `.env.example` with all configuration options documented

### Performance Success
- ✅ MCP task list responses < 500ms for 100 tasks
- ✅ Drag-and-drop updates < 200ms perceived latency
- ✅ UI polling doesn't exceed 1 req/sec when tab active
- ✅ Database queries use indexes (no full table scans)

## Next Steps for Downstream Agents

### Phase 2: Codebase Researcher
**Focus Areas**:
1. **Search for FastAPI project structures** in vibes codebase
   - Pattern: `Grep "FastAPI" --type=py`
   - Extract: App initialization, middleware setup, CORS config

2. **Locate Archon's MCP server initialization**
   - Pattern: `Grep "FastMCP" path=repos/Archon/python`
   - Extract: Server setup, tool registration, error handling

3. **Find React + TanStack Query examples**
   - Pattern: `Glob **/use*Queries.ts path=repos/Archon`
   - Extract: Query key patterns, mutation hooks, optimistic updates

4. **Identify Docker Compose patterns**
   - Pattern: `Grep "docker-compose" --glob="*.yml"`
   - Extract: Service definitions, health checks, volume mounts

**Expected Artifacts**:
- Service layer file paths and patterns
- MCP tool implementation examples
- Frontend hook patterns with query keys
- Docker configuration references

### Phase 3: Documentation Hunter
**Focus Areas**:
1. **FastAPI + Pydantic documentation**
   - Search Archon knowledge base: `rag_search_knowledge_base("FastAPI async validation")`
   - Look for: Async endpoints, request validation, response models

2. **react-dnd documentation and examples**
   - Search: `rag_search_code_examples("react-dnd useDrop")`
   - Look for: Drag-and-drop setup, type definitions, drop zones

3. **TanStack Query v5 patterns**
   - Search Archon docs: `rag_search_knowledge_base("TanStack Query staleTime")`
   - Look for: Query configuration, polling, optimistic updates

4. **PostgreSQL schema design best practices**
   - Search: `rag_search_knowledge_base("PostgreSQL indexes foreign keys")`
   - Look for: Index strategies, migration patterns

**Expected Artifacts**:
- FastAPI async patterns with code examples
- react-dnd TypeScript integration guide
- TanStack Query polling and cache configuration
- Database schema migration approaches

### Phase 4: Example Curator
**Focus Areas**:
1. **Extract MCP tool implementations from Archon**
   - Files: `/Users/jon/source/vibes/repos/Archon/python/src/mcp_server/features/tasks/task_tools.py`
   - Extract: Consolidated tool pattern, error handling, response optimization

2. **Extract Kanban component from Archon**
   - Files: `/Users/jon/source/vibes/repos/Archon/archon-ui-main/src/features/projects/tasks/components/KanbanColumn.tsx`
   - Extract: useDrop hook, column rendering, task card integration

3. **Extract service layer examples**
   - Files: `/Users/jon/source/vibes/repos/Archon/python/src/server/services/projects/task_service.py`
   - Extract: CRUD operations, validation, async patterns

4. **Extract Docker Compose from existing vibes projects**
   - Search: `Glob **/docker-compose.yml`
   - Extract: PostgreSQL service, health checks, volume configurations

**Expected Artifacts**:
- Annotated MCP tool code with key patterns highlighted
- React drag-and-drop component example with explanations
- Service layer template with validation patterns
- Docker Compose template with comments

### Phase 5: Gotcha Detective
**Investigation Areas**:
1. **Drag-and-drop position conflicts**
   - Research: How does Archon handle concurrent position updates?
   - Files: `/Users/jon/source/vibes/repos/Archon/python/src/server/services/projects/task_service.py` (lines 94-115)
   - Expected gotcha: Race conditions when multiple users drag simultaneously
   - Mitigation: Transaction isolation, position increment logic

2. **MCP response size limits**
   - Research: What breaks when task descriptions are very long?
   - Known from Archon: 1000 char truncation, array → count conversion
   - Expected gotcha: JSON serialization errors with large responses
   - Mitigation: Always truncate, paginate, exclude large fields

3. **TanStack Query cache invalidation**
   - Research: When does optimistic update fail to sync?
   - Files: Archon's query hooks (useTaskQueries.ts)
   - Expected gotcha: Stale data after MCP updates if cache not invalidated
   - Mitigation: Use ETag, smart polling, manual invalidation on MCP writes

4. **Docker volume permissions**
   - Research: PostgreSQL data directory ownership issues
   - Common gotcha: Container user UID mismatch with host
   - Mitigation: Named volumes (not bind mounts), proper user in Dockerfile

5. **FastAPI async database connections**
   - Research: Connection pool exhaustion
   - Expected gotcha: Forgetting `await` on async database calls
   - Mitigation: Use async context managers, connection pooling with asyncpg

6. **React-dnd TypeScript types**
   - Research: Type errors with item types in drag-and-drop
   - Known from Archon: Custom `ItemTypes` enum, strict item interface
   - Expected gotcha: Runtime errors if item types don't match
   - Mitigation: Shared TypeScript types for drag items, strict accept validation

**Expected Artifacts**:
- List of 10+ gotchas with mitigation strategies
- Code examples of safe patterns vs. dangerous patterns
- Checklist for validation gates (preventing common errors)
- Performance pitfall warnings (N+1 queries, polling too fast)

---

## Summary for Assembler Agent

**Feature Scope**: Self-hosted task management with dual UI (Kanban + list), MCP integration for AI assistants, 4-state workflow, Docker deployment.

**Tech Stack Decision**: Python/FastAPI backend + React/TypeScript frontend (Option A)
- Matches vibes ecosystem
- Proven patterns in Archon
- FastMCP for MCP integration

**Critical Patterns to Reuse**:
1. Archon's consolidated MCP tools (`find_tasks`, `manage_task`)
2. Service layer architecture (API → Service → DB)
3. react-dnd for Kanban drag-and-drop
4. TanStack Query for state management (no Redux)
5. Smart HTTP polling (no WebSockets)

**Key Architectural Decisions**:
- Flat task structure (optional parent_task_id for future)
- HTTP polling for real-time updates
- Single-user initially (no auth in MVP)
- PostgreSQL without Supabase
- All-in-one Docker Compose deployment

**Reference Implementations**:
- **Primary**: Archon (`/Users/jon/source/vibes/repos/Archon/`)
- **Secondary**: Task Master (for hierarchy ideas, post-MVP)

**Open Questions for Implementation**:
- Markdown editor: Full vs. simple (lean toward simple)
- Migration tool: Alembic (recommended)
- List view: Pagination (start here) vs. virtual scrolling
- Type sharing: Manual (MVP) vs. code generation (future)

**Success Metrics**:
- `docker-compose up` runs all services ✅
- MCP tools work with Claude Code ✅
- Drag-and-drop Kanban functional ✅
- Data persists across restarts ✅
- < 500ms MCP response times ✅

**Confidence Level**: 9/10
- Strong reference implementations available
- Proven tech stack in vibes ecosystem
- Clear requirements with well-defined scope
- Known gotchas documented from Archon experience
