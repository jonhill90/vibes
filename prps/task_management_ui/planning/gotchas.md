# Known Gotchas & Solutions: task_management_ui

## Overview

This document identifies critical pitfalls, common mistakes, security vulnerabilities, and performance issues for the task management UI feature. Based on research from Archon knowledge base, FastAPI/React documentation, and 2024-2025 web resources, this covers gotchas in MCP server implementation, FastAPI + React integration, Docker composition, PostgreSQL patterns, drag-and-drop UI, and type safety.

**Key Finding**: Most issues are preventable with proper async patterns, transaction isolation, query cancellation, and response optimization.

---

## Critical Gotchas

### 1. FastAPI: Blocking the Event Loop with Sync Functions

**Severity**: Critical
**Category**: Performance / System Stability
**Affects**: FastAPI async endpoints
**Source**: https://medium.com/@bhagyarana80/10-async-pitfalls-in-fastapi-and-how-to-avoid-them-60d6c67ea48f

**What it is**:
Calling synchronous blocking functions (like `time.sleep`, synchronous database calls, or file I/O) inside async endpoints blocks the entire event loop, preventing other requests from being processed.

**Why it's a problem**:
- Blocks all concurrent requests during the blocking operation
- Degrades performance to worse than synchronous servers
- Can cause request timeouts under load
- Defeats the entire purpose of using async

**How to detect it**:
- Endpoint latency increases linearly with concurrent requests
- High CPU usage but low throughput
- Requests queue up and timeout
- Profiling shows event loop blocked

**How to avoid/fix**:

```python
# ❌ WRONG - Blocks event loop
@app.get("/tasks")
async def get_tasks():
    import time
    time.sleep(2)  # BLOCKS entire server!

    # Synchronous database call
    session = get_sync_session()
    tasks = session.query(Task).all()  # BLOCKS!
    return tasks

# ✅ RIGHT - Non-blocking async
@app.get("/tasks")
async def get_tasks():
    import asyncio
    await asyncio.sleep(2)  # Non-blocking

    # Async database call
    async with get_async_session() as session:
        result = await session.execute(select(Task))
        tasks = result.scalars().all()
    return tasks

# ✅ ALTERNATIVE - Use def for sync code (FastAPI runs in threadpool)
@app.get("/tasks")
def get_tasks():
    # FastAPI automatically runs this in a separate thread
    session = get_sync_session()
    tasks = session.query(Task).all()
    return tasks
```

**Key Rule**: If you use `async def`, NEVER call blocking functions. Use `await` for I/O or use regular `def` and let FastAPI handle threading.

---

### 2. PostgreSQL: Position Reordering Race Conditions

**Severity**: Critical
**Category**: Data Integrity / Concurrency
**Affects**: Drag-and-drop position updates, concurrent task reordering
**Source**: https://dba.stackexchange.com/questions/303368/atomic-updates-to-ordering-in-a-table-for-a-waiting-list-application

**What it is**:
Concurrent drag-and-drop operations can create position conflicts when multiple users reorder tasks simultaneously. Without proper transaction isolation, positions can become duplicated or gaps can appear.

**Why it's a problem**:
- Lost updates: User A's reorder gets overwritten by User B
- Duplicate positions: Two tasks end up with same position value
- Deadlocks: Two transactions lock rows in different order
- UI shows incorrect task order after refresh

**How to detect it**:
- Position gaps or duplicates in database: `SELECT position, COUNT(*) FROM tasks GROUP BY position HAVING COUNT(*) > 1`
- Deadlock errors in PostgreSQL logs
- Task order differs between users' views
- Tests with concurrent updates fail intermittently

**How to avoid/fix**:

```python
# ❌ WRONG - Race condition prone
async def update_task_position(task_id: str, new_position: int, status: str):
    # Read current tasks
    tasks = await db.fetch_all(
        "SELECT id, position FROM tasks WHERE status = $1 AND position >= $2",
        status, new_position
    )

    # Update positions (NOT ATOMIC!)
    for task in tasks:
        await db.execute(
            "UPDATE tasks SET position = $1 WHERE id = $2",
            task['position'] + 1, task['id']
        )

    # Update target task
    await db.execute(
        "UPDATE tasks SET position = $1, status = $2 WHERE id = $3",
        new_position, status, task_id
    )

# ✅ RIGHT - Atomic transaction with explicit locking
async def update_task_position(task_id: str, new_position: int, status: str):
    async with db.transaction():
        # Acquire locks in consistent order (by id) to prevent deadlocks
        await db.execute(
            """
            SELECT id FROM tasks
            WHERE status = $1 AND position >= $2
            ORDER BY id  -- Consistent lock order prevents deadlocks
            FOR UPDATE
            """,
            status, new_position
        )

        # Atomic batch update
        await db.execute(
            """
            UPDATE tasks
            SET position = position + 1,
                updated_at = NOW()
            WHERE status = $1 AND position >= $2
            """,
            status, new_position
        )

        # Update target task
        await db.execute(
            """
            UPDATE tasks
            SET position = $1,
                status = $2,
                updated_at = NOW()
            WHERE id = $3
            """,
            new_position, status, task_id
        )

# ✅ ALTERNATIVE - Use absolute scoring instead of positions
# Instead of positions 1,2,3,4, use scores like 1000, 2000, 3000, 4000
# When inserting between 2000 and 3000, use 2500
# This makes concurrent writes for distinct users problem-free
async def update_task_score(task_id: str, new_score: float):
    await db.execute(
        "UPDATE tasks SET score = $1 WHERE id = $2",
        new_score, task_id
    )
```

**Transaction Isolation Levels**:
- Use `READ COMMITTED` (default) for most cases
- Use `SERIALIZABLE` for absolute consistency (retry on serialization failure)
- Always lock rows in consistent order (e.g., ORDER BY id) to prevent deadlocks

---

### 3. MCP: Response Size Limits and JSON Serialization

**Severity**: Critical
**Category**: API Error / Performance
**Affects**: MCP tool responses with large task lists or descriptions
**Source**: Archon source e9eb05e2bf38f125

**What it is**:
MCP tools that return large responses (many tasks, long descriptions, JSONB arrays) can exceed JSON-RPC message size limits or cause serialization errors, breaking AI assistant integration.

**Why it's a problem**:
- Claude Code/Cursor fails to parse response
- JSON serialization errors with very large strings
- Slow response times for AI assistants
- Exceeded token limits in AI context window

**How to detect it**:
- MCP tool calls timeout or return errors
- AI assistant shows "Failed to parse response"
- Response time > 500ms for list operations
- Browser DevTools shows large JSON payloads

**How to avoid/fix**:

```python
# ❌ WRONG - Returns everything, can be huge
@mcp.tool()
async def find_tasks(
    project_id: str | None = None,
    page: int = 1,
    per_page: int = 100  # TOO LARGE!
) -> str:
    tasks = await task_service.list_tasks(
        project_id=project_id,
        page=page,
        per_page=per_page
    )
    # Returns full tasks with all fields
    return json.dumps({"success": True, "tasks": tasks})

# ✅ RIGHT - Optimized responses for MCP
MAX_DESCRIPTION_LENGTH = 1000
MAX_TASKS_PER_PAGE = 20

@mcp.tool()
async def find_tasks(
    project_id: str | None = None,
    page: int = 1,
    per_page: int = 10  # Reasonable default
) -> str:
    # Limit page size
    per_page = min(per_page, MAX_TASKS_PER_PAGE)

    tasks = await task_service.list_tasks(
        project_id=project_id,
        page=page,
        per_page=per_page,
        exclude_large_fields=True  # Don't return JSONB arrays
    )

    # Optimize each task
    optimized_tasks = [optimize_task_for_mcp(task) for task in tasks]

    return json.dumps({
        "success": True,
        "tasks": optimized_tasks,
        "page": page,
        "total": len(optimized_tasks),
        "has_more": len(optimized_tasks) == per_page
    })

def optimize_task_for_mcp(task: dict) -> dict:
    """Reduce response size for AI consumption."""
    # Truncate long descriptions
    if task.get("description") and len(task["description"]) > MAX_DESCRIPTION_LENGTH:
        task["description"] = task["description"][:997] + "..."

    # Replace arrays with counts (if present)
    if "attachments" in task and isinstance(task["attachments"], list):
        task["attachments_count"] = len(task["attachments"])
        del task["attachments"]

    # Remove large JSONB fields
    for field in ["metadata", "sources", "code_examples"]:
        if field in task:
            del task[field]

    return task

# Get single task mode returns full details
if task_id:
    task = await task_service.get_task(task_id)
    # Single task can include full details (but still truncate description)
    if task.get("description") and len(task["description"]) > 5000:
        task["description"] = task["description"][:4997] + "..."
    return json.dumps({"success": True, "task": task})
```

**Performance Targets**:
- List responses: < 500ms for 100 tasks
- Single task: < 200ms
- Response size: < 100KB for list, < 50KB for single

---

### 4. TanStack Query: Race Conditions in Optimistic Updates

**Severity**: High
**Category**: UI Consistency / Race Conditions
**Affects**: Optimistic updates during drag-and-drop, concurrent mutations
**Source**: https://tkdodo.eu/blog/concurrent-optimistic-updates-in-react-query

**What it is**:
When a mutation starts while there's already a request in-flight (e.g., from refetchOnWindowFocus), the optimistic update gets overwritten by the stale response, causing the UI to flicker or show incorrect state.

**Why it's a problem**:
- User drags task to "doing", UI briefly shows it, then reverts to "todo"
- Lost optimistic updates when user focuses window during mutation
- Confusing UX with state toggling back and forth
- Multiple rapid clicks cause conflicting updates

**How to detect it**:
- UI flickers after drag-and-drop
- Task status reverts unexpectedly after window focus
- React Query DevTools shows queries completing after mutations
- User reports "changes not saving"

**How to avoid/fix**:

```typescript
// ❌ WRONG - No query cancellation
const updateTaskMutation = useMutation({
  mutationFn: (update: TaskUpdate) =>
    taskService.updateTask(update.id, update),

  onMutate: async (update) => {
    // Missing: await queryClient.cancelQueries()

    const previous = queryClient.getQueryData(['tasks', projectId]);

    // Optimistic update
    queryClient.setQueryData(['tasks', projectId], (old: Task[]) =>
      old.map(task =>
        task.id === update.id ? { ...task, ...update } : task
      )
    );

    return { previous };
  },

  onError: (err, variables, context) => {
    queryClient.setQueryData(['tasks', projectId], context.previous);
  },
});

// ✅ RIGHT - Cancel queries to prevent race conditions
const updateTaskMutation = useMutation({
  mutationFn: (update: TaskUpdate) =>
    taskService.updateTask(update.id, update),

  onMutate: async (update) => {
    // CRITICAL: Cancel in-flight queries that could overwrite optimistic update
    await queryClient.cancelQueries({
      queryKey: ['tasks', projectId]
    });

    // Snapshot for rollback
    const previous = queryClient.getQueryData(['tasks', projectId]);

    // Optimistic update with stable local ID
    const optimisticTask = {
      ...update,
      _optimistic: true,
      _localId: nanoid(),
    };

    queryClient.setQueryData(['tasks', projectId], (old: Task[] = []) =>
      old.map(task =>
        task.id === update.id
          ? { ...task, ...optimisticTask }
          : task
      )
    );

    return { previous, optimisticId: optimisticTask._localId };
  },

  onError: (err, variables, context) => {
    // Rollback on error
    if (context?.previous) {
      queryClient.setQueryData(['tasks', projectId], context.previous);
    }
    toast.error('Failed to update task');
  },

  onSuccess: (serverTask, variables, context) => {
    // Replace optimistic with server data
    queryClient.setQueryData(['tasks', projectId], (tasks: Task[]) =>
      tasks.map(task =>
        task._localId === context?.optimisticId ? serverTask : task
      )
    );
  },

  onSettled: () => {
    // Smart invalidation: only if no other mutations in progress
    if (queryClient.isMutating({ mutationKey: ['tasks'] }) === 1) {
      queryClient.invalidateQueries({ queryKey: ['tasks', projectId] });
    }
  },
});

// ✅ Additional: Prevent duplicate mutations during pending state
const handleDragEnd = (taskId: string, newStatus: TaskStatus) => {
  // Check if mutation already in progress
  if (updateTaskMutation.isPending) {
    console.warn('Mutation already in progress, ignoring duplicate');
    return;
  }

  updateTaskMutation.mutate({ id: taskId, status: newStatus });
};
```

**Key Patterns**:
1. **Always** cancel queries in `onMutate` to prevent overwrites
2. Use `queryClient.isMutating()` to avoid over-invalidation
3. Debounce rapid user actions (drag events, clicks)
4. Check `isPending` before triggering mutations

---

### 5. Docker: PostgreSQL Volume Permission Errors

**Severity**: Critical
**Category**: Deployment / Data Persistence
**Affects**: Docker Compose setup with PostgreSQL bind mounts
**Source**: https://stackoverflow.com/questions/60619659/postgres-mounting-volume-in-docker-permission-denied

**What it is**:
PostgreSQL container fails to start with "Permission denied" when using bind mounts for data persistence. The container's postgres user (UID 999) doesn't have permissions on the host directory.

**Why it's a problem**:
- Database fails to start: `docker-compose up` fails
- Data persistence doesn't work
- Deployment blocked in CI/CD
- Different behavior between macOS/Linux/Windows

**How to detect it**:
- Container logs: `initdb: error: could not change permissions of directory "/var/lib/postgresql/data": Operation not permitted`
- Container exits immediately after start
- `docker-compose ps` shows db service as "Exit 1"
- PostgreSQL FATAL: data directory has invalid permissions

**How to avoid/fix**:

```yaml
# ❌ WRONG - Bind mount with permission issues
services:
  db:
    image: postgres:16
    volumes:
      - ./data/postgres:/var/lib/postgresql/data  # Host directory bind mount
    environment:
      POSTGRES_DB: taskmanager
      POSTGRES_USER: taskuser
      POSTGRES_PASSWORD: ${DB_PASSWORD}

# Host directory may have wrong ownership/permissions
# Postgres requires 0700 permissions on data directory

# ✅ RIGHT - Use named Docker volume (recommended)
services:
  db:
    image: postgres:16
    volumes:
      - taskmanager-db-data:/var/lib/postgresql/data  # Named volume
    environment:
      POSTGRES_DB: taskmanager
      POSTGRES_USER: taskuser
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U taskuser -d taskmanager"]
      interval: 5s
      timeout: 3s
      retries: 5
      start_period: 10s

volumes:
  taskmanager-db-data:
    driver: local

# ✅ ALTERNATIVE - Fix bind mount permissions (Linux/macOS)
# Before docker-compose up:
# sudo chown -R 999:999 ./data/postgres
# chmod 0700 ./data/postgres

# ✅ ALTERNATIVE - Use user directive (if you control host UID)
services:
  db:
    image: postgres:16
    user: "${UID}:${GID}"  # Match host user
    volumes:
      - ./data/postgres:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: taskmanager
      POSTGRES_USER: taskuser
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      PGDATA: /var/lib/postgresql/data/pgdata  # Subdirectory to avoid permission issues
```

**Best Practices**:
- **Production**: Always use named Docker volumes (not bind mounts)
- **Development**: Use named volumes OR fix permissions before mounting
- **CI/CD**: Named volumes work consistently across environments
- **Backup**: Use `docker volume` commands or pg_dump (not direct file copy)

---

### 6. Pydantic V2: Breaking Changes in Validators

**Severity**: High
**Category**: Migration / Type Safety
**Affects**: All Pydantic models if migrating from V1
**Source**: https://docs.pydantic.dev/latest/migration/

**What it is**:
Pydantic V2 changed validator decorators and removed keyword arguments, breaking code that uses `@validator`, `@root_validator`, or accesses `values` parameter.

**Why it's a problem**:
- Code that worked in V1 raises AttributeError in V2
- `@validator` is deprecated and will be removed
- `values` argument no longer exists
- Config class changed to dict-based `model_config`

**How to detect it**:
- Import errors: `ImportError: cannot import name 'validator' from 'pydantic'`
- Runtime errors: `AttributeError: 'ValidationInfo' object has no attribute 'values'`
- Deprecation warnings in logs
- Tests fail after Pydantic upgrade

**How to avoid/fix**:

```python
# ❌ WRONG - Pydantic V1 syntax (deprecated)
from pydantic import BaseModel, validator

class TaskCreate(BaseModel):
    title: str
    status: str
    assignee: str

    class Config:  # V1 style
        orm_mode = True

    @validator('title')  # Deprecated
    def title_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()

    @validator('assignee')
    def assignee_depends_on_status(cls, v, values):  # 'values' removed in V2
        if values.get('status') == 'doing' and not v:
            raise ValueError('Assignee required for doing status')
        return v

# ✅ RIGHT - Pydantic V2 syntax
from pydantic import BaseModel, field_validator, model_validator
from pydantic import ValidationInfo

class TaskCreate(BaseModel):
    title: str
    status: str = 'todo'
    assignee: str = 'User'

    model_config = {  # V2 style - dict instead of class
        'from_attributes': True,  # Replaces orm_mode
        'str_strip_whitespace': True,  # Built-in whitespace stripping
    }

    @field_validator('title')  # Replaces @validator
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()

    @model_validator(mode='after')  # For cross-field validation
    def assignee_depends_on_status(self) -> 'TaskCreate':
        if self.status == 'doing' and not self.assignee:
            raise ValueError('Assignee required for doing status')
        return self

    # Access other field values using ValidationInfo.data
    @field_validator('assignee')
    @classmethod
    def validate_assignee(cls, v: str, info: ValidationInfo) -> str:
        # Access other field values
        status = info.data.get('status')
        if status == 'doing' and not v:
            raise ValueError('Assignee required for doing status')
        return v

# Migration helper tool
# pip install bump-pydantic
# bump-pydantic src/  # Automatically converts V1 to V2
```

**V1 → V2 Migration Checklist**:
- [ ] `@validator` → `@field_validator`
- [ ] `@root_validator` → `@model_validator`
- [ ] `values` parameter → `ValidationInfo.data`
- [ ] `Config` class → `model_config` dict
- [ ] `orm_mode=True` → `from_attributes=True`
- [ ] `pre=True` → `mode='before'`

---

## High Priority Gotchas

### 7. FastAPI: Mixing Async and Sync Database Sessions

**Severity**: High
**Category**: Performance / Deadlock Risk
**Affects**: Database operations in async endpoints
**Source**: Web research - FastAPI common mistakes

**What it is**:
Using synchronous database sessions (SQLAlchemy sync, psycopg2) inside async endpoints blocks the event loop. Using async sessions incorrectly can cause deadlocks.

**Why it's a problem**:
- Sync DB calls block all concurrent requests
- Connection pool exhaustion from blocking
- Deadlocks if mixing sync/async in same transaction

**How to detect it**:
- High latency during database operations
- Connection pool "QueuePool limit exceeded" errors
- Event loop blocked warnings

**How to avoid/fix**:

```python
# ❌ WRONG - Sync session in async endpoint
from sqlalchemy.orm import Session

@app.get("/tasks")
async def get_tasks(db: Session = Depends(get_db)):
    # Blocks event loop!
    tasks = db.query(Task).all()
    return tasks

# ✅ RIGHT - Async session with asyncpg
from sqlalchemy.ext.asyncio import AsyncSession

async def get_async_db():
    async with async_session_maker() as session:
        yield session

@app.get("/tasks")
async def get_tasks(db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(Task))
    tasks = result.scalars().all()
    return tasks

# ✅ ALTERNATIVE - Use def for sync operations
@app.get("/tasks")
def get_tasks(db: Session = Depends(get_sync_db)):
    # FastAPI runs in threadpool automatically
    tasks = db.query(Task).all()
    return tasks
```

---

### 8. React DnD: TypeScript Type Issues with Monitor

**Severity**: High
**Category**: Type Safety / Developer Experience
**Affects**: Drag-and-drop implementation with TypeScript
**Source**: https://github.com/react-dnd/react-dnd/issues/3192

**What it is**:
Generic type parameters don't flow through to `DropTargetMonitor`, causing type errors or forcing type assertions. Collector function return types not properly inferred.

**Why it's a problem**:
- Loss of type safety in drag-and-drop logic
- Runtime errors from incorrect type assumptions
- Poor IDE autocomplete and type hints

**How to detect it**:
- TypeScript errors: `Property 'X' does not exist on type 'unknown'`
- Monitor shows as `DropTargetMonitor<unknown, unknown>`
- Need type assertions everywhere

**How to avoid/fix**:

```typescript
// ❌ WRONG - Generic types not inferred
import { useDrop, DropTargetMonitor } from 'react-dnd';

interface DragItem {
  id: string;
  status: TaskStatus;
}

const [{ isOver }, drop] = useDrop({
  accept: 'TASK',
  drop: (item, monitor) => {
    // monitor is DropTargetMonitor<unknown, unknown>
    // item is unknown - no type safety!
    const draggedItem = item as DragItem; // Type assertion required
    onTaskMove(draggedItem.id, status);
  },
  collect: (monitor) => ({
    isOver: !!monitor.isOver(),
  }),
});

// ✅ RIGHT - Explicit type parameters and interfaces
import { useDrop, DropTargetMonitor } from 'react-dnd';

// Define item type constant
export const ItemTypes = {
  TASK: 'task',
} as const;

// Explicit drag item interface
interface TaskDragItem {
  id: string;
  status: TaskStatus;
}

// Explicit collect result interface
interface TaskDropCollect {
  isOver: boolean;
  canDrop: boolean;
}

const [{ isOver, canDrop }, drop] = useDrop<
  TaskDragItem,      // Drag item type
  void,              // Drop result type
  TaskDropCollect    // Collect result type
>({
  accept: ItemTypes.TASK,

  drop: (item: TaskDragItem, monitor: DropTargetMonitor<TaskDragItem, void>) => {
    // Full type safety - item is TaskDragItem
    if (item.status !== status) {
      onTaskMove(item.id, status);
    }
  },

  canDrop: (item: TaskDragItem, monitor: DropTargetMonitor<TaskDragItem, void>) => {
    // Type-safe access to item properties
    return item.status !== status;
  },

  collect: (monitor: DropTargetMonitor<TaskDragItem, void>): TaskDropCollect => ({
    isOver: !!monitor.isOver(),
    canDrop: !!monitor.canDrop(),
  }),
});

// ✅ Drag source with types
const [{ isDragging }, drag] = useDrag<
  TaskDragItem,     // Drag item type
  void,             // Drop result
  { isDragging: boolean }  // Collect result
>({
  type: ItemTypes.TASK,
  item: { id: task.id, status: task.status },
  collect: (monitor) => ({
    isDragging: !!monitor.isDragging(),
  }),
});
```

**Best Practices**:
- Always provide explicit type parameters to `useDrop` and `useDrag`
- Define item type interfaces separately
- Use constants for item types (not magic strings)
- Create typed wrapper hooks for reusable drag/drop logic

---

### 9. PostgreSQL: Missing Foreign Key Indexes

**Severity**: High
**Category**: Performance / Query Optimization
**Affects**: Foreign key queries (e.g., tasks by project_id)
**Source**: PostgreSQL documentation

**What it is**:
PostgreSQL does NOT automatically create indexes on foreign key columns. Queries filtering by `project_id` or `parent_task_id` will use full table scans.

**Why it's a problem**:
- Slow queries on foreign key filters
- N+1 query patterns become extremely slow
- Performance degrades as table grows
- Cascading deletes are slow without indexes

**How to detect it**:
- `EXPLAIN ANALYZE` shows "Seq Scan" on foreign key queries
- Query time increases linearly with table size
- DELETE operations on parent table are slow

**How to avoid/fix**:

```sql
-- ❌ WRONG - No index on foreign key
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    -- Missing index on project_id!
    title TEXT NOT NULL,
    status TEXT NOT NULL
);

-- Query will be slow:
-- SELECT * FROM tasks WHERE project_id = 'xxx';  -- Seq Scan!

-- ✅ RIGHT - Always index foreign keys
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    parent_task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    status TEXT NOT NULL,
    position INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Critical indexes
CREATE INDEX idx_tasks_project_id ON tasks(project_id);
CREATE INDEX idx_tasks_parent_id ON tasks(parent_task_id) WHERE parent_task_id IS NOT NULL;

-- Composite index for common query patterns
CREATE INDEX idx_tasks_project_status ON tasks(project_id, status);
CREATE INDEX idx_tasks_status_position ON tasks(status, position);

-- Partial index for active tasks only
CREATE INDEX idx_tasks_active ON tasks(project_id, status)
    WHERE status IN ('todo', 'doing', 'review');

-- Verify index usage:
EXPLAIN ANALYZE
SELECT * FROM tasks
WHERE project_id = 'some-uuid' AND status = 'todo'
ORDER BY position;

-- Should show "Index Scan using idx_tasks_project_status"
```

**Index Strategy**:
- Index ALL foreign key columns
- Create composite indexes for common query combinations
- Use partial indexes for filtered queries (WHERE status != 'done')
- Monitor with `EXPLAIN ANALYZE` in development

---

### 10. CORS: FastAPI + React Development Configuration

**Severity**: High
**Category**: Security / Development Setup
**Affects**: API requests from React dev server to FastAPI
**Source**: https://fastapi.tiangolo.com/tutorial/cors/

**What it is**:
Frontend running on `localhost:3000` cannot access backend on `localhost:8000` due to CORS policy. Browsers block cross-origin requests by default.

**Why it's a problem**:
- API requests fail with CORS errors
- Development is blocked until CORS configured
- Overly permissive CORS in production is a security risk

**How to detect it**:
- Browser console: `Access to fetch at 'http://localhost:8000/api/tasks' from origin 'http://localhost:3000' has been blocked by CORS policy`
- Network tab shows CORS preflight OPTIONS requests failing
- 403 Forbidden or CORS error messages

**How to avoid/fix**:

```python
# ❌ WRONG - No CORS or overly permissive
from fastapi import FastAPI

app = FastAPI()

# No CORS middleware - requests from frontend will fail!

# OR too permissive:
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # DANGEROUS in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ RIGHT - Environment-specific CORS configuration
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# Configure CORS based on environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "development":
    # Development: Allow localhost origins
    origins = [
        "http://localhost:3000",
        "http://localhost:5173",  # Vite default
        "http://127.0.0.1:3000",
    ]
elif ENVIRONMENT == "production":
    # Production: Only allow specific domains
    origins = [
        "https://yourdomain.com",
        "https://app.yourdomain.com",
    ]
else:
    origins = []

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Specific origins only
    allow_credentials=True,  # Required for cookies/auth
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
)

# ✅ Alternative: Environment variable list
# CORS_ORIGINS=http://localhost:3000,http://localhost:5173
cors_origins = os.getenv("CORS_ORIGINS", "").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in cors_origins if origin],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
)

# Health check endpoint (no CORS needed)
@app.get("/health")
async def health():
    return {"status": "healthy"}
```

**Security Best Practices**:
- NEVER use `allow_origins=["*"]` in production
- Use environment variables for origin configuration
- Only allow specific HTTP methods needed
- Enable `allow_credentials` only if using cookies/auth
- Test CORS in production-like environment before deployment

---

## Medium Priority Gotchas

### 11. TanStack Query: Stale Time Confusion

**Severity**: Medium
**Category**: Performance / UX
**Affects**: Query caching and refetch behavior
**Source**: TanStack Query documentation

**What it is**:
Misunderstanding `staleTime` vs `cacheTime` (now `gcTime`) causes either too many refetches or stale data being displayed.

**Why it's confusing**:
- `staleTime: 0` (default) means data is immediately stale → refetches on every mount
- `gcTime: 5 minutes` (default) means unused data stays in cache for 5 minutes
- Developers often set them incorrectly

**How to handle it**:

```typescript
// ❌ WRONG - Constant refetching or stale data
const { data } = useQuery({
  queryKey: ['tasks'],
  queryFn: fetchTasks,
  // Missing staleTime - defaults to 0 (always stale)
  // Refetches on every component mount!
});

// ✅ RIGHT - Explicit stale times based on data volatility
export const STALE_TIMES = {
  instant: 0,           // Always refetch
  frequent: 5_000,      // 5 seconds - rapidly changing data
  normal: 30_000,       // 30 seconds - normal data
  rare: 300_000,        // 5 minutes - rarely changing
  static: Infinity,     // Never stale - static data
} as const;

const { data: tasks } = useQuery({
  queryKey: ['tasks', projectId],
  queryFn: () => taskService.getTasksByProject(projectId),
  staleTime: STALE_TIMES.normal,     // 30s - tasks change occasionally
  gcTime: 10 * 60 * 1000,            // 10 minutes in cache
  refetchOnWindowFocus: true,         // Refetch when tab focused (if stale)
  refetchInterval: 30_000,           // Poll every 30s
  refetchIntervalInBackground: false, // Pause when tab hidden
});

const { data: projects } = useQuery({
  queryKey: ['projects'],
  queryFn: fetchProjects,
  staleTime: STALE_TIMES.rare,  // 5 minutes - projects rarely change
  gcTime: 30 * 60 * 1000,       // 30 minutes
});
```

**Rule of Thumb**:
- Fast-changing data (task status): 5-30 seconds stale time
- Slow-changing data (projects, users): 5-15 minutes stale time
- Static data (config, enums): Infinity stale time
- Always set `refetchIntervalInBackground: false` to save resources

---

### 12. FastAPI: Dependency Injection Scope Issues

**Severity**: Medium
**Category**: Memory Leaks / Resource Management
**Affects**: Database sessions, connections, file handles
**Source**: FastAPI documentation

**What it is**:
Dependencies that create resources (DB sessions, file handles) not properly scoped can cause memory leaks or resource exhaustion.

**How to handle it**:

```python
# ❌ WRONG - Session not properly closed
def get_db():
    db = SessionLocal()
    return db  # Never closed!

@app.get("/tasks")
async def get_tasks(db: Session = Depends(get_db)):
    return db.query(Task).all()

# ✅ RIGHT - Proper cleanup with yield
async def get_async_db():
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()  # Guaranteed cleanup

@app.get("/tasks")
async def get_tasks(db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(Task))
    return result.scalars().all()
```

---

### 13. Docker Compose: Service Dependency Timing

**Severity**: Medium
**Category**: Deployment Reliability
**Affects**: Service startup order
**Source**: Docker Compose documentation

**What it is**:
`depends_on` only waits for container to start, not for service to be ready. Backend tries to connect to DB before it's accepting connections.

**How to handle it**:

```yaml
# ❌ WRONG - depends_on without health check
services:
  backend:
    depends_on:
      - db  # Only waits for container start, not readiness

# ✅ RIGHT - Health check dependency
services:
  db:
    image: postgres:16
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U taskuser -d taskmanager"]
      interval: 5s
      timeout: 3s
      retries: 5
      start_period: 10s

  backend:
    depends_on:
      db:
        condition: service_healthy  # Waits for health check to pass
```

---

## Anti-Patterns to Avoid

### 1. Manual Cache Invalidation Loops

**What it is**: Using setTimeout or manual intervals to invalidate TanStack Query cache

**Why it's bad**: TanStack Query has built-in polling and smart refetching

**Better pattern**:
```typescript
// ❌ Avoid
useEffect(() => {
  const interval = setInterval(() => {
    queryClient.invalidateQueries(['tasks']);
  }, 5000);
  return () => clearInterval(interval);
}, []);

// ✅ Use built-in refetchInterval
useQuery({
  queryKey: ['tasks'],
  queryFn: fetchTasks,
  refetchInterval: 5000,
  refetchIntervalInBackground: false,
});
```

---

### 2. Endpoint-to-Endpoint Internal API Calls

**What it is**: One FastAPI endpoint calling another endpoint via HTTP

**Why it's bad**:
- Extra serialization/deserialization overhead
- Double authentication/authorization
- Increased latency
- Harder to debug

**Better pattern**:
```python
# ❌ Avoid
@app.get("/tasks")
async def get_tasks():
    return await task_service.list_tasks()

@app.get("/reports")
async def get_report():
    # Calling another endpoint internally - BAD!
    async with httpx.AsyncClient() as client:
        tasks = await client.get("http://localhost:8000/tasks")
    return {"task_count": len(tasks.json())}

# ✅ Share service layer
@app.get("/tasks")
async def get_tasks():
    return await task_service.list_tasks()

@app.get("/reports")
async def get_report():
    # Direct service call - GOOD!
    tasks = await task_service.list_tasks()
    return {"task_count": len(tasks)}
```

---

### 3. Hardcoded Polling Intervals

**What it is**: Using magic numbers for staleTime, refetchInterval

**Why it's bad**: Inconsistent caching behavior across features

**Better pattern**:
```typescript
// ❌ Avoid
useQuery({ staleTime: 30000 })  // Magic number

// ✅ Use constants
import { STALE_TIMES } from '@/config/queryPatterns';
useQuery({ staleTime: STALE_TIMES.normal })
```

---

### 4. Mixing Query Key Patterns

**What it is**: Inconsistent query key structure across features

**Why it's bad**: Hard to invalidate related queries

**Better pattern**:
```typescript
// ❌ Avoid
['tasks', projectId]
['project', projectId, 'tasks']
['getTasks', { projectId }]

// ✅ Consistent query key factory
export const taskKeys = {
  all: ['tasks'] as const,
  lists: () => [...taskKeys.all, 'list'] as const,
  byProject: (projectId: string) => [...taskKeys.all, 'project', projectId] as const,
  detail: (id: string) => [...taskKeys.all, 'detail', id] as const,
};
```

---

## Gotcha Checklist for Implementation

Before marking PRP complete, verify these gotchas are addressed:

### Security & Data Integrity
- [ ] CORS configured with specific origins (not `*`)
- [ ] Position reordering uses transactions with row locking
- [ ] MCP responses truncate sensitive/large data
- [ ] Foreign keys have ON DELETE CASCADE or SET NULL
- [ ] Pydantic validators migrated to V2 syntax

### Performance
- [ ] Async functions don't call blocking I/O (use `await` or `def`)
- [ ] Database queries use async sessions (asyncpg)
- [ ] Foreign key columns have indexes
- [ ] MCP responses limited to 20 items per page
- [ ] TanStack Query uses appropriate staleTime values

### Reliability
- [ ] Optimistic updates cancel in-flight queries
- [ ] Docker health checks configured for dependencies
- [ ] PostgreSQL volume uses named volume (not bind mount)
- [ ] Error boundaries catch React DnD errors
- [ ] Transaction isolation prevents race conditions

### Type Safety
- [ ] React DnD hooks have explicit type parameters
- [ ] Pydantic models use `@field_validator` (not `@validator`)
- [ ] TypeScript types match database schema exactly
- [ ] API responses match Pydantic models

### Developer Experience
- [ ] `.env.example` includes all required variables
- [ ] Validation errors provide actionable messages
- [ ] Query key factories prevent inconsistent cache
- [ ] Service layer shared between API and MCP

---

## Testing Gotchas

### 1. Async Test Fixtures Scope

**Pitfall**: Using function-scoped fixtures for async database connections causes connection pool exhaustion

**Solution**:
```python
# ❌ Wrong
@pytest.fixture
async def db_session():
    async with async_session_maker() as session:
        yield session

# ✅ Right - session scope for connection pool
@pytest.fixture(scope="session")
async def db_pool():
    return await asyncpg.create_pool(DATABASE_URL)

@pytest.fixture
async def db_session(db_pool):
    async with db_pool.acquire() as conn:
        yield conn
```

### 2. TanStack Query Test Isolation

**Pitfall**: Query cache persists between tests causing flaky tests

**Solution**:
```typescript
// ✅ Clear cache before each test
beforeEach(() => {
  queryClient.clear();
});
```

---

## Deployment Gotchas

### 1. Environment Variable Validation

**Issue**: Missing env vars cause runtime errors in production

**Solution**:
```python
# ✅ Validate on startup
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    mcp_port: int = 8051
    cors_origins: str

    class Config:
        env_file = ".env"

settings = Settings()  # Raises error if missing required vars
```

### 2. Health Check False Positives

**Issue**: Health check passes but service not ready

**Solution**:
```python
# ✅ Comprehensive health check
@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        # Verify database connection
        await db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Unhealthy: {e}")
```

---

## Performance Benchmarks

Track these metrics to detect gotchas:

- **MCP Tools**:
  - `find_tasks()` list: < 500ms for 100 tasks
  - `manage_task()`: < 200ms for create/update
  - Response size: < 100KB

- **API Endpoints**:
  - GET /tasks: < 300ms
  - POST /tasks: < 200ms
  - PATCH /tasks/{id}: < 150ms

- **Database**:
  - Position reorder transaction: < 100ms
  - Task query by project_id: < 50ms (with index)

- **Frontend**:
  - Optimistic update perceived latency: < 50ms
  - Drag-and-drop to mutation: < 200ms

---

## Sources Referenced

### From Archon Knowledge Base
- `e9eb05e2bf38f125` - MCP response optimization patterns
- `c0e629a894699314` - Pydantic AI framework patterns
- `d60a71d62eb201d5` - MCP documentation and best practices

### From Web Research
- FastAPI async pitfalls: https://medium.com/@bhagyarana80/10-async-pitfalls-in-fastapi-and-how-to-avoid-them-60d6c67ea48f
- Pydantic V2 migration: https://docs.pydantic.dev/latest/migration/
- TanStack Query race conditions: https://tkdodo.eu/blog/concurrent-optimistic-updates-in-react-query
- PostgreSQL concurrency: https://dba.stackexchange.com/questions/303368/atomic-updates-to-ordering-in-a-table-for-a-waiting-list-application
- Docker volume permissions: https://stackoverflow.com/questions/60619659/postgres-mounting-volume-in-docker-permission-denied
- React DnD TypeScript: https://github.com/react-dnd/react-dnd/issues/3192

---

## Recommendations for PRP Assembly

When generating the PRP:

1. **Include in "Known Gotchas & Library Quirks" section**:
   - FastAPI async/sync mixing (Critical #1, #7)
   - PostgreSQL position conflicts (Critical #2)
   - MCP response limits (Critical #3)
   - TanStack Query race conditions (Critical #4)
   - Pydantic V2 breaking changes (Critical #6)

2. **Add to "Validation Gates"**:
   - Test position reordering with concurrent updates
   - Verify MCP response sizes < 100KB
   - Check foreign key indexes exist
   - Validate CORS configuration per environment

3. **Reference in "Implementation Blueprint"**:
   - Transaction pattern for position updates
   - Query cancellation in optimistic updates
   - Async session dependency injection
   - Named volume configuration

4. **Highlight in Documentation**:
   - Environment variable requirements
   - Database migration considerations
   - Type parameter patterns for react-dnd

---

## Confidence Assessment

**Gotcha Coverage**: 9/10
- **Security**: High confidence - CORS, transactions, data validation covered
- **Performance**: High confidence - async patterns, indexes, response optimization covered
- **Common Mistakes**: High confidence - 13 gotchas documented with solutions
- **Library-Specific**: High confidence - Pydantic V2, react-dnd types, TanStack Query

**Gaps**:
- WebSocket alternatives (polling covered)
- Multi-tenant concerns (out of scope for MVP)
- Advanced caching strategies (basic patterns sufficient)

**Overall Quality**: 9/10 - Comprehensive coverage with actionable solutions for all critical areas.

---

**Generated**: 2025-10-06
**Feature**: task_management_ui
**Total Gotchas**: 13 documented (6 Critical, 4 High, 3 Medium)
**All gotchas include**: Problem description, impact, detection, and solutions with code examples
**Ready for PRP Integration**: ✅ Yes
