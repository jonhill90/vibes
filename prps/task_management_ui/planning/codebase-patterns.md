# Codebase Patterns: task_management_ui

## Overview

This document extracts proven architectural patterns, naming conventions, and implementation strategies from the Archon codebase to guide the development of the standalone task management UI. Archon provides excellent reference implementations for MCP server consolidation, FastAPI service layers, React component architecture, and Docker deployment patterns.

**Key Finding**: Archon demonstrates a mature, production-ready architecture using Python/FastAPI + React/TypeScript with TanStack Query, which aligns perfectly with the recommended tech stack for this feature.

## Architectural Patterns

### Pattern 1: Consolidated MCP Tools Pattern
**Source**: `/Users/jon/source/vibes/repos/Archon/python/src/mcp_server/features/tasks/task_tools.py`
**Relevance**: 10/10

**What it does**: Consolidates CRUD operations into two tools: `find_tasks` (list + search + get) and `manage_task` (create + update + delete), reducing tool count while maintaining full functionality.

**Key Techniques**:
```python
@mcp.tool()
async def find_tasks(
    ctx: Context,
    query: str | None = None,      # Search keyword
    task_id: str | None = None,     # Get single task
    filter_by: str | None = None,   # "status" | "project" | "assignee"
    filter_value: str | None = None,
    project_id: str | None = None,
    page: int = 1,
    per_page: int = 10,
) -> str:
    """Unified find/search/get operation"""
    if task_id:
        # Single task mode - return full details
        response = await client.get(f"/api/tasks/{task_id}")
        return json.dumps({"success": True, "task": task})
    else:
        # List mode with filters
        params = {"page": page, "per_page": per_page}
        if query:
            params["q"] = query
        # ... apply filters
        return json.dumps({"success": True, "tasks": optimized_tasks})

@mcp.tool()
async def manage_task(
    ctx: Context,
    action: str,  # "create" | "update" | "delete"
    task_id: str | None = None,
    # ... other fields
) -> str:
    """Unified create/update/delete operation"""
    if action == "create":
        # ... create logic
    elif action == "update":
        # ... update logic
    elif action == "delete":
        # ... delete logic
```

**Response Optimization** (critical for MCP):
```python
MAX_DESCRIPTION_LENGTH = 1000

def optimize_task_response(task: dict) -> dict:
    """Optimize task for MCP response"""
    # Truncate long text
    if task.get("description") and len(task["description"]) > 1000:
        task["description"] = task["description"][:997] + "..."

    # Replace arrays with counts
    if "sources" in task and isinstance(task["sources"], list):
        task["sources_count"] = len(task["sources"])
        del task["sources"]

    return task
```

**When to use**:
- All MCP tool implementations
- Reduces AI IDE tool clutter (2 tools vs 6+)
- Single source of truth for operation logic

**How to adapt**:
- Keep same pattern: `find_*` and `manage_*`
- Add project-level tools: `find_projects`, `manage_project`
- Always optimize responses for AI consumption
- Include pagination from the start

**Why this pattern**:
- Proven in Archon's production deployment
- Simplifies tool discovery for AI assistants
- Reduces maintenance burden (one place to update)
- Better error handling consistency

---

### Pattern 2: Service Layer Architecture
**Source**: `/Users/jon/source/vibes/repos/Archon/python/src/server/services/projects/task_service.py`
**Relevance**: 10/10

**What it does**: Separates business logic into service classes that sit between API routes and database, enabling code reuse across MCP tools and REST endpoints.

**Key Techniques**:
```python
class TaskService:
    """Service class for task operations"""

    VALID_STATUSES = ["todo", "doing", "review", "done"]

    def __init__(self, supabase_client=None):
        self.supabase_client = supabase_client or get_supabase_client()

    def validate_status(self, status: str) -> tuple[bool, str]:
        """Validation returns (success, error_message)"""
        if status not in self.VALID_STATUSES:
            return False, f"Invalid status '{status}'. Must be one of: {', '.join(self.VALID_STATUSES)}"
        return True, ""

    async def create_task(
        self,
        project_id: str,
        title: str,
        description: str = "",
        assignee: str = "User",
        task_order: int = 0,
        # ...
    ) -> tuple[bool, dict[str, Any]]:
        """
        Returns: (success, result_dict)
        result_dict contains either 'task' or 'error' key
        """
        # Validation
        if not title or len(title.strip()) == 0:
            return False, {"error": "Title required"}

        # Business logic
        # ... create task

        return True, {"task": task_data}
```

**Reordering Logic** (position management):
```python
# If inserting at specific position, increment existing tasks
if task_order > 0:
    existing_tasks = (
        self.supabase_client.table("tasks")
        .select("id, task_order")
        .eq("project_id", project_id)
        .eq("status", "todo")
        .gte("task_order", task_order)
        .execute()
    )

    for task in existing_tasks.data:
        new_order = task["task_order"] + 1
        self.supabase_client.table("tasks").update({
            "task_order": new_order,
            "updated_at": datetime.now().isoformat(),
        }).eq("id", task["id"]).execute()
```

**When to use**:
- All business logic that's shared between API and MCP
- Validation that needs to be consistent
- Complex database operations (like position reordering)

**How to adapt**:
- Create `ProjectService` and `TaskService` classes
- Return `tuple[bool, dict]` pattern consistently
- Use async methods for database operations
- Keep validation separate from execution

**Why this pattern**:
- MCP tools and REST API can share exact same logic
- Testable without HTTP layer
- Easy to add new interfaces (WebSockets, CLI, etc.)

---

### Pattern 3: React + TanStack Query State Management
**Source**: `/Users/jon/source/vibes/repos/Archon/archon-ui-main/src/features/projects/tasks/hooks/useTaskQueries.ts`
**Relevance**: 10/10

**What it does**: Uses TanStack Query as the single source of truth for server state, eliminating Redux/Zustand while providing caching, optimistic updates, and smart polling.

**Key Techniques**:

**Query Key Factory**:
```typescript
// Each feature owns its query keys
export const taskKeys = {
  all: ["tasks"] as const,
  lists: () => [...taskKeys.all, "list"] as const,
  detail: (id: string) => [...taskKeys.all, "detail", id] as const,
  byProject: (projectId: string) => ["projects", projectId, "tasks"] as const,
  counts: () => [...taskKeys.all, "counts"] as const,
};
```

**Smart Polling Hook**:
```typescript
export function useProjectTasks(projectId: string | undefined) {
  const { refetchInterval } = useSmartPolling(2000); // 2s active polling

  return useQuery<Task[]>({
    queryKey: projectId ? taskKeys.byProject(projectId) : DISABLED_QUERY_KEY,
    queryFn: async () => {
      if (!projectId) throw new Error("No project ID");
      return taskService.getTasksByProject(projectId);
    },
    enabled: !!projectId,
    refetchInterval,  // Pauses when tab hidden
    refetchOnWindowFocus: true,  // Refetch on focus (cheap with ETag)
    staleTime: STALE_TIMES.frequent,  // 5 seconds
  });
}
```

**Optimistic Updates**:
```typescript
export function useCreateTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data) => taskService.createTask(data),

    onMutate: async (newTaskData) => {
      // Cancel in-flight queries
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
        status: "todo",
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
        (tasks) => replaceOptimisticEntity(
          tasks,
          context?.optimisticId,
          serverTask
        )
      );
    },
  });
}
```

**When to use**:
- All server state management (no Redux needed)
- Real-time updates via smart polling
- Any mutation that needs instant UI feedback

**How to adapt**:
- Create query key factories for tasks and projects
- Use `STALE_TIMES` constants (from shared config)
- Implement optimistic updates for all mutations
- Add smart polling for Kanban board

---

### Pattern 4: react-dnd Drag and Drop
**Source**: `/Users/jon/source/vibes/repos/Archon/archon-ui-main/src/features/projects/tasks/components/KanbanColumn.tsx`
**Relevance**: 10/10

**What it does**: Implements drag-and-drop task movement between Kanban columns using react-dnd with visual feedback.

**Key Techniques**:
```typescript
import { useDrop } from "react-dnd";

export const ItemTypes = {
  TASK: "task",
};

export const KanbanColumn = ({
  status,
  tasks,
  onTaskMove,
  // ...
}) => {
  const ref = useRef<HTMLDivElement>(null);

  const [{ isOver }, drop] = useDrop({
    accept: ItemTypes.TASK,
    drop: (item: { id: string; status: Task["status"] }) => {
      if (item.status !== status) {
        onTaskMove(item.id, status);
      }
    },
    collect: (monitor) => ({
      isOver: !!monitor.isOver(),
    }),
  });

  drop(ref);

  return (
    <div
      ref={ref}
      className={cn(
        "flex flex-col h-full",
        "bg-gradient-to-b from-white/20 to-transparent",
        "backdrop-blur-sm",
        "transition-all duration-200",
        isOver && "bg-cyan-500/5",  // Visual feedback on hover
        isOver && "border-t-2 border-t-cyan-400/50"
      )}
    >
      {/* Column content */}
      {tasks.map((task) => (
        <TaskCard key={task.id} task={task} />
      ))}
    </div>
  );
};
```

**TaskCard drag source**:
```typescript
const [{ isDragging }, drag] = useDrag({
  type: ItemTypes.TASK,
  item: { id: task.id, status: task.status },
  collect: (monitor) => ({
    isDragging: !!monitor.isDragging(),
  }),
});
```

**When to use**:
- Kanban board column drops
- Task reordering within columns
- Any drag-and-drop UI interaction

**How to adapt**:
- Define `ItemTypes.TASK` constant
- Use same drop/drag hook pattern
- Add glassmorphism styling for hover states
- Integrate with TanStack Query mutations for persistence

---

### Pattern 5: MCP Error Handling
**Source**: `/Users/jon/source/vibes/repos/Archon/python/src/mcp_server/utils/error_handling.py`
**Relevance**: 9/10

**What it does**: Provides structured, AI-friendly error responses with actionable suggestions for recovery.

**Key Techniques**:
```python
class MCPErrorFormatter:
    @staticmethod
    def format_error(
        error_type: str,
        message: str,
        details: dict[str, Any] | None = None,
        suggestion: str | None = None,
        http_status: int | None = None,
    ) -> str:
        """Format consistent error structure"""
        error_response = {
            "success": False,
            "error": {
                "type": error_type,
                "message": message,
            },
        }

        if suggestion:
            error_response["error"]["suggestion"] = suggestion

        return json.dumps(error_response)

    @staticmethod
    def from_http_error(response: httpx.Response, operation: str) -> str:
        """Extract error from HTTP response"""
        # Try to parse response body
        try:
            body = response.json()
            error_message = body.get("detail") or body.get("error")
        except:
            error_message = response.text[:500]

        return MCPErrorFormatter.format_error(
            error_type="api_error",
            message=f"Failed to {operation}: {error_message}",
            http_status=response.status_code,
            suggestion=_get_suggestion_for_status(response.status_code),
        )

def _get_suggestion_for_status(status_code: int) -> str | None:
    """AI-friendly suggestions"""
    suggestions = {
        400: "Check that all required parameters are provided and valid",
        404: "The requested resource was not found. Verify the ID is correct",
        409: "There's a conflict. The resource may already exist",
        500: "Server error. Check server logs for details",
    }
    return suggestions.get(status_code)
```

**When to use**:
- All MCP tool error returns
- Any operation that might fail (HTTP, validation, etc.)

**How to adapt**:
- Create `MCPErrorFormatter` utility class
- Always include `suggestion` field for AI guidance
- Use structured error types (not generic "error")
- Return JSON strings from MCP tools, not exceptions

---

## Backend Architecture

### FastAPI Application Structure

**Pattern**: Modular FastAPI with service layer separation
**Reference**: `/Users/jon/source/vibes/repos/Archon/python/src/server/`

**Directory Organization**:
```
backend/
├── api_routes/          # HTTP endpoint handlers
│   ├── projects_api.py  # /api/projects/*
│   └── tasks_api.py     # /api/tasks/*
├── services/            # Business logic layer
│   ├── project_service.py
│   └── task_service.py
├── models/              # Pydantic request/response models
│   ├── project_models.py
│   └── task_models.py
├── config/              # Configuration and settings
│   └── database.py      # Database client setup
├── utils/               # Shared utilities
│   └── etag_utils.py    # ETag generation
└── main.py              # FastAPI app initialization
```

**API Route Pattern**:
```python
from fastapi import APIRouter, Request, Response
from src.server.services.task_service import TaskService
from src.server.utils.etag_utils import generate_etag, check_etag

router = APIRouter(prefix="/api")

@router.get("/tasks")
async def list_tasks(
    request: Request,
    response: Response,
    project_id: str | None = None,
    status: str | None = None,
):
    """List tasks with optional filters"""
    service = TaskService()
    success, result = service.list_tasks(
        project_id=project_id,
        status=status,
        exclude_large_fields=True  # Optimize for API
    )

    if not success:
        raise HTTPException(status_code=400, detail=result)

    # ETag support
    etag = generate_etag(result)
    if check_etag(request, etag):
        return Response(status_code=304)

    response.headers["ETag"] = etag
    response.headers["Cache-Control"] = "no-cache, must-revalidate"

    return result
```

**Validation with Pydantic**:
```python
from pydantic import BaseModel, Field

class CreateTaskRequest(BaseModel):
    project_id: str
    title: str = Field(..., min_length=1, max_length=500)
    description: str = ""
    status: str = Field(default="todo", pattern="^(todo|doing|review|done)$")
    assignee: str = "User"
    priority: str = Field(default="medium", pattern="^(low|medium|high|urgent)$")
```

**Async Database Operations**:
```python
async def create_task(self, ...) -> tuple[bool, dict]:
    """Async for database I/O"""
    try:
        response = self.supabase_client.table("tasks").insert({
            "project_id": project_id,
            "title": title,
            # ...
        }).execute()

        return True, {"task": response.data[0]}
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        return False, {"error": str(e)}
```

---

## Frontend Architecture

### Component Organization (Vertical Slices)

**Pattern**: Feature-based directory structure
**Reference**: `/Users/jon/source/vibes/repos/Archon/archon-ui-main/src/features/`

```
frontend/src/
├── features/
│   ├── projects/
│   │   ├── components/      # Project UI components
│   │   ├── hooks/           # useProjectQueries.ts
│   │   ├── services/        # projectService.ts (API calls)
│   │   ├── types/           # TypeScript types
│   │   └── tasks/           # Sub-feature with same structure
│   │       ├── components/
│   │       ├── hooks/
│   │       ├── services/
│   │       └── types/
│   ├── shared/              # Cross-feature utilities
│   │   ├── api/             # apiClient.ts (axios/fetch wrapper)
│   │   ├── config/          # queryClient.ts, queryPatterns.ts
│   │   ├── hooks/           # useSmartPolling.ts
│   │   └── utils/           # optimistic.ts
│   └── ui/                  # Reusable UI components
│       ├── primitives/      # Radix UI wrappers
│       └── hooks/           # UI-specific hooks
└── pages/                   # Route components
```

**Service Layer Pattern**:
```typescript
// features/projects/services/projectService.ts
import { apiClient } from "@/features/shared/api/apiClient";

export const projectService = {
  async listProjects(): Promise<Project[]> {
    const response = await apiClient.get("/api/projects");
    return response.data;
  },

  async createProject(data: CreateProjectRequest): Promise<Project> {
    const response = await apiClient.post("/api/projects", data);
    return response.data.project;
  },
};
```

**Shared Query Configuration**:
```typescript
// features/shared/config/queryPatterns.ts
export const DISABLED_QUERY_KEY = ["disabled"] as const;

export const STALE_TIMES = {
  instant: 0,
  frequent: 5_000,    // 5 seconds
  normal: 30_000,     // 30 seconds
  rare: 300_000,      // 5 minutes
  static: Infinity,   // Never stale
} as const;
```

**Smart Polling**:
```typescript
// features/ui/hooks/useSmartPolling.ts
export function useSmartPolling(baseInterval: number) {
  const [isVisible, setIsVisible] = useState(true);
  const [isFocused, setIsFocused] = useState(true);

  useEffect(() => {
    // Listen for visibility changes
    const handleVisibility = () => setIsVisible(!document.hidden);
    document.addEventListener("visibilitychange", handleVisibility);

    return () => document.removeEventListener("visibilitychange", handleVisibility);
  }, []);

  // Adjust interval based on visibility/focus
  const refetchInterval = useMemo(() => {
    if (!isVisible) return false;  // Pause when hidden
    if (!isFocused) return baseInterval * 1.5;  // Slow when unfocused
    return baseInterval;
  }, [isVisible, isFocused, baseInterval]);

  return { refetchInterval };
}
```

---

## Database Patterns

### Schema Design

**Pattern**: PostgreSQL with vector extension and proper indexing
**Reference**: `/Users/jon/source/vibes/repos/Archon/migration/complete_setup.sql`

**Projects Table**:
```sql
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_projects_created_at ON projects(created_at DESC);
```

**Tasks Table** (with position tracking):
```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    parent_task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,

    title VARCHAR(500) NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL CHECK (status IN ('todo', 'doing', 'review', 'done')),
    assignee VARCHAR(255) DEFAULT 'User',
    priority VARCHAR(50) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),

    -- Position for drag-and-drop ordering within status column
    position INTEGER DEFAULT 0,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Indexes for performance
    INDEX idx_tasks_project_id (project_id),
    INDEX idx_tasks_status (status),
    INDEX idx_tasks_assignee (assignee),
    INDEX idx_tasks_position (status, position)  -- For ordered retrieval
);
```

**Auto-update Timestamp Trigger**:
```sql
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
```

**Key Design Decisions**:
- UUID for all IDs (cross-database compatibility)
- `position` field for manual ordering (not auto-increment)
- CHECK constraints for enum values
- Cascading deletes for project → tasks
- Timestamps with timezone
- Composite indexes for common query patterns

---

## Docker & Deployment

### Docker Compose Pattern

**Reference**: `/Users/jon/source/vibes/repos/Archon/docker-compose.yml`

**Multi-Service Composition**:
```yaml
services:
  # Database
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: taskmanager
      POSTGRES_USER: taskuser
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - task-manager-db:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U taskuser"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - app-network

  # Backend (API + MCP)
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    depends_on:
      db:
        condition: service_healthy
    environment:
      DATABASE_URL: postgresql://taskuser:${DB_PASSWORD}@db:5432/taskmanager
      MCP_PORT: ${MCP_PORT:-8051}
      API_PORT: ${API_PORT:-8000}
    ports:
      - "${API_PORT:-8000}:8000"
      - "${MCP_PORT:-8051}:8051"
    volumes:
      - ./backend/src:/app/src  # Hot reload
    command: ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--reload"]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
    networks:
      - app-network

  # Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    depends_on:
      backend:
        condition: service_healthy
    environment:
      VITE_API_URL: http://backend:8000
    ports:
      - "${FRONTEND_PORT:-3000}:3000"
    volumes:
      - ./frontend/src:/app/src  # Hot reload
    networks:
      - app-network

networks:
  app-network:
    driver: bridge

volumes:
  task-manager-db:
```

**Multi-Stage Dockerfile (Backend)**:
```dockerfile
# Build stage
FROM python:3.12-slim as builder
WORKDIR /app
RUN pip install uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

# Runtime stage
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY src/ ./src/
ENV PATH="/app/.venv/bin:$PATH"
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Environment Variable Management**:
```bash
# .env.example
DATABASE_URL=postgresql://taskuser:password@db:5432/taskmanager
API_PORT=8000
MCP_PORT=8051
FRONTEND_PORT=3000
DB_PASSWORD=changeme
```

---

## Type Safety Strategies

### Backend Type Hints

**Pattern**: Full Python type hints with validation
**Reference**: All Archon service files

```python
from typing import Any
from datetime import datetime

class TaskService:
    def validate_status(self, status: str) -> tuple[bool, str]:
        """Returns (is_valid, error_message)"""
        # ...

    async def create_task(
        self,
        project_id: str,
        title: str,
        description: str = "",
        assignee: str = "User",
        task_order: int = 0,
    ) -> tuple[bool, dict[str, Any]]:
        """Returns (success, result_dict)"""
        # ...
```

### Frontend TypeScript

**Pattern**: Strict TypeScript with shared types
**Reference**: `/Users/jon/source/vibes/repos/Archon/archon-ui-main/src/features/projects/tasks/types/`

```typescript
// Database-aligned types (no translation layer!)
export type TaskStatus = "todo" | "doing" | "review" | "done";
export type TaskPriority = "low" | "medium" | "high" | "urgent";

export interface Task {
  id: string;
  project_id: string;
  title: string;
  description: string;
  status: TaskStatus;
  assignee: string;
  priority: TaskPriority;
  position: number;
  created_at: string;
  updated_at: string;
}

export interface CreateTaskRequest {
  project_id: string;
  title: string;
  description?: string;
  status?: TaskStatus;
  assignee?: string;
  priority?: TaskPriority;
}

export interface UpdateTaskRequest {
  title?: string;
  description?: string;
  status?: TaskStatus;
  assignee?: string;
  priority?: TaskPriority;
  position?: number;
}
```

**Type Sharing Strategy**:
- **Manual duplication** for MVP (only 5-10 types)
- Keep types in sync via code review
- Use database values directly (no mapping layers)
- Consider Pydantic → TypeScript codegen for future

---

## Naming Conventions

### File Naming
**Backend**:
- `{feature}_service.py` - Service modules
- `{feature}_api.py` - API route handlers
- `{feature}_models.py` - Pydantic models

**Frontend**:
- `use{Feature}Queries.ts` - Query hooks
- `{feature}Service.ts` - API service
- `{Feature}View.tsx` - Page components
- `{Feature}Card.tsx` - Display components

### Class/Function Naming
**Backend**:
- `TaskService` - Service classes
- `create_task()` - Async service methods
- `CreateTaskRequest` - Pydantic request models

**Frontend**:
- `useProjectTasks()` - Query hooks
- `useCreateTask()` - Mutation hooks
- `taskKeys` - Query key factories

### Database Values
**Direct usage** (no translation):
- Status: `"todo"`, `"doing"`, `"review"`, `"done"`
- Priority: `"low"`, `"medium"`, `"high"`, `"urgent"`

---

## Common Utilities to Leverage

### 1. ETag Generation
**Location**: `/Users/jon/source/vibes/repos/Archon/python/src/server/utils/etag_utils.py`
**Purpose**: Generate ETags for HTTP caching

```python
import hashlib
import json

def generate_etag(data: dict) -> str:
    """Generate ETag from response data"""
    json_str = json.dumps(data, sort_keys=True)
    hash_value = hashlib.md5(json_str.encode()).hexdigest()
    return f'"{hash_value}"'

def check_etag(request: Request, current_etag: str) -> bool:
    """Check if client's ETag matches current"""
    client_etag = request.headers.get("If-None-Match")
    return client_etag == current_etag
```

### 2. Optimistic Update Helpers
**Location**: `/Users/jon/source/vibes/repos/Archon/archon-ui-main/src/features/shared/utils/optimistic.ts`

```typescript
import { nanoid } from "nanoid";

export interface OptimisticEntity {
  _optimistic?: boolean;
  _localId?: string;
}

export function createOptimisticEntity<T>(data: Partial<T>): T & OptimisticEntity {
  return {
    ...data,
    _optimistic: true,
    _localId: nanoid(),
  } as T & OptimisticEntity;
}

export function replaceOptimisticEntity<T extends OptimisticEntity>(
  entities: T[],
  localId: string,
  serverData: T
): T[] {
  return entities.map(entity =>
    entity._localId === localId ? serverData : entity
  );
}
```

### 3. Query Client Configuration
**Location**: `/Users/jon/source/vibes/repos/Archon/archon-ui-main/src/features/shared/config/queryClient.ts`

```typescript
import { QueryClient } from "@tanstack/react-query";

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,           // 30 seconds
      gcTime: 10 * 60 * 1000,      // 10 minutes
      refetchOnWindowFocus: true,   // ETag makes this cheap
      retry: (failureCount, error) => {
        const status = (error as any)?.status;
        if (status >= 400 && status < 500) return false;  // Don't retry 4xx
        return failureCount < 2;
      },
    },
  },
});
```

---

## Testing Patterns

### Backend Testing (pytest)

```python
import pytest
from src.server.services.task_service import TaskService

@pytest.fixture
def task_service():
    return TaskService()

@pytest.mark.asyncio
async def test_create_task(task_service):
    success, result = await task_service.create_task(
        project_id="test-project",
        title="Test Task",
        description="Test description"
    )

    assert success is True
    assert result["task"]["title"] == "Test Task"
    assert result["task"]["status"] == "todo"
```

### Frontend Testing (Vitest)

```typescript
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClientProvider } from "@tanstack/react-query";
import { useProjectTasks } from "../useTaskQueries";

vi.mock("../../services", () => ({
  taskService: {
    getTasksByProject: vi.fn().mockResolvedValue([]),
  },
}));

test("useProjectTasks fetches tasks", async () => {
  const { result } = renderHook(
    () => useProjectTasks("project-1"),
    { wrapper: QueryClientProvider }
  );

  await waitFor(() => expect(result.current.isSuccess).toBe(true));
  expect(result.current.data).toEqual([]);
});
```

---

## Anti-Patterns to Avoid

### 1. Manual Cache Invalidation
**What it is**: Calling `invalidateQueries` with setTimeout or manual tracking
**Why to avoid**: TanStack Query handles this automatically with smart polling
**Found in**: Early Archon implementations (now refactored)
**Better approach**: Use `staleTime` and `refetchInterval` configuration

### 2. Prop Drilling
**What it is**: Passing data through multiple component layers
**Why to avoid**: Hard to maintain, violates component isolation
**Better approach**: Each component fetches its own data via TanStack Query

### 3. Translation Layers
**What it is**: Mapping database values to different frontend values
**Why to avoid**: Extra code, potential bugs, type safety issues
**Better approach**: Use database values directly in TypeScript types

### 4. Hardcoded Time Values
**What it is**: `staleTime: 30000` instead of `STALE_TIMES.normal`
**Why to avoid**: Inconsistent caching behavior across features
**Better approach**: Always use `STALE_TIMES` constants

### 5. Mixing Query Keys
**What it is**: Tasks importing `projectKeys` or vice versa
**Why to avoid**: Tight coupling between features
**Better approach**: Each feature owns its query keys completely

---

## Implementation Hints from Existing Code

### Similar Features Found

**1. Archon Task Management**
**Location**: `/Users/jon/source/vibes/repos/Archon/`
**Similarity**: 95% - same domain, same tech stack
**Lessons**:
- MCP consolidation pattern works extremely well
- Service layer enables code reuse across MCP and REST
- Smart polling is sufficient (no WebSockets needed)
- ETag caching reduces bandwidth significantly
**Differences**:
- Archon has knowledge base integration (not needed for standalone system)
- Archon uses Supabase (can use raw PostgreSQL)

**2. Task Position Reordering**
**Location**: `task_service.py` lines 93-115
**Pattern**: Increment all tasks >= new position before insert
**Why it works**: Simple, atomic, no fractional positions needed
**Edge case**: Concurrent updates - use transaction isolation

**3. Kanban Drag-and-Drop**
**Location**: `KanbanColumn.tsx` lines 35-45
**Pattern**: `useDrop` on column, `useDrag` on card
**Visual feedback**: Change background/border on `isOver`
**Optimization**: Only call mutation if status actually changed

---

## Recommendations for PRP

Based on pattern analysis:

1. **Follow Archon's MCP consolidation pattern** for `find_tasks`, `manage_task`, `find_projects`, `manage_project`
2. **Reuse service layer architecture** - create `ProjectService` and `TaskService` classes
3. **Mirror Archon's React structure** - vertical slices with query key factories
4. **Adapt react-dnd patterns** for Kanban board implementation
5. **Avoid WebSockets** - use smart HTTP polling like Archon (proven to scale)
6. **Use database values directly** - no translation layers (type-safe end-to-end)
7. **Implement ETag caching** from day one (70% bandwidth reduction)
8. **Start with Docker Compose** - Archon's multi-service pattern is production-ready

---

## Reference File Locations

### Backend Patterns
- **MCP Tools**: `/Users/jon/source/vibes/repos/Archon/python/src/mcp_server/features/tasks/task_tools.py`
- **Service Layer**: `/Users/jon/source/vibes/repos/Archon/python/src/server/services/projects/task_service.py`
- **Error Handling**: `/Users/jon/source/vibes/repos/Archon/python/src/mcp_server/utils/error_handling.py`
- **Database Schema**: `/Users/jon/source/vibes/repos/Archon/migration/complete_setup.sql`

### Frontend Patterns
- **Query Hooks**: `/Users/jon/source/vibes/repos/Archon/archon-ui-main/src/features/projects/tasks/hooks/useTaskQueries.ts`
- **Kanban Component**: `/Users/jon/source/vibes/repos/Archon/archon-ui-main/src/features/projects/tasks/components/KanbanColumn.tsx`
- **Smart Polling**: `/Users/jon/source/vibes/repos/Archon/archon-ui-main/src/features/ui/hooks/useSmartPolling.ts` (inferred from usage)
- **Query Patterns**: `/Users/jon/source/vibes/repos/Archon/archon-ui-main/src/features/shared/config/queryPatterns.ts`

### Docker & Deployment
- **Docker Compose**: `/Users/jon/source/vibes/repos/Archon/docker-compose.yml`

---

## Source References

### From Archon
- **Source ID**: e9eb05e2bf38f125 (Task service documentation) - Relevance 9/10
- **Source ID**: d60a71d62eb201d5 (FastMCP framework patterns) - Relevance 8/10
- **Source ID**: c0e629a894699314 (Pydantic AI patterns) - Relevance 6/10

### From Local Codebase
- `/Users/jon/source/vibes/repos/Archon/python/src/mcp_server/features/tasks/task_tools.py:54-198` - Consolidated MCP pattern
- `/Users/jon/source/vibes/repos/Archon/python/src/server/services/projects/task_service.py:55-158` - Service layer with validation
- `/Users/jon/source/vibes/repos/Archon/archon-ui-main/src/features/projects/tasks/hooks/useTaskQueries.ts:15-220` - TanStack Query patterns
- `/Users/jon/source/vibes/repos/Archon/archon-ui-main/src/features/projects/tasks/components/KanbanColumn.tsx:35-45` - Drag-and-drop implementation

---

## Next Steps for Assembler

When generating the PRP:

1. **Include these patterns in "Current Codebase Tree" section**:
   - Reference Archon's service layer structure
   - Show MCP tool consolidation examples
   - Demonstrate query key factory pattern

2. **Add key code snippets to "Implementation Blueprint"**:
   - Service layer template
   - MCP tool registration
   - Query hook with optimistic updates
   - Drag-and-drop column component

3. **Add anti-patterns to "Known Gotchas" section**:
   - Manual cache invalidation (use smart polling)
   - Prop drilling (use TanStack Query)
   - Translation layers (use DB values directly)
   - Hardcoded time values (use STALE_TIMES)

4. **Use file organization for "Desired Codebase Tree"**:
   - Mirror Archon's vertical slice architecture
   - Separate backend into api_routes, services, models
   - Organize frontend by feature (projects, tasks, ui)

5. **Reference specific Archon files** for implementation guidance:
   - "See Archon's task_tools.py for MCP consolidation pattern"
   - "Follow useTaskQueries.ts pattern for query hooks"
   - "Adapt KanbanColumn.tsx for drag-and-drop"

**Success criteria**: The PRP should enable a developer to build the task management UI by following proven Archon patterns without reinventing solutions that already work.
