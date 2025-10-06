# Documentation Resources: task_management_ui

## Overview

This document curates official documentation, tutorials, and best practices for building a self-hosted task management system with FastAPI backend, React frontend, MCP integration, and Docker deployment. All technologies were researched through Archon knowledge base first, with web documentation filling gaps. Coverage includes async patterns, drag-and-drop UI, state management, database optimization, containerization, and type safety across Python and TypeScript.

---

## Primary Framework Documentation

### FastAPI (Python Backend)
**Official Docs**: https://fastapi.tiangolo.com/
**Version**: Latest (supports Python 3.12+)
**Archon Source**: c0e629a894699314 (Pydantic AI - includes FastAPI patterns)
**Relevance**: 10/10

**Sections to Read**:

1. **Concurrency and async / await**: https://fastapi.tiangolo.com/async/
   - **Why**: Critical for understanding when to use `async def` vs `def` in endpoints
   - **Key Concepts**:
     - Mix `async def` and `def` freely - FastAPI handles both efficiently
     - Use `async def` when calling libraries that support `await`
     - Use normal `def` for blocking I/O or libraries without async support
     - Dependencies can be async or sync, sub-dependencies can mix both

2. **Path Operation Configuration**: https://fastapi.tiangolo.com/tutorial/path-operation-configuration/
   - **Why**: Metadata for API documentation, tags for organization
   - **Key Concepts**: Response models, status codes, tags, summaries

3. **Dependency Injection**: https://fastapi.tiangolo.com/tutorial/dependencies/
   - **Why**: Service layer pattern, database session management
   - **Key Concepts**: Shared dependencies, sub-dependencies, dependency override for testing

4. **Request Body - Multiple Parameters**: https://fastapi.tiangolo.com/tutorial/body-multiple-params/
   - **Why**: Handling complex task update payloads
   - **Key Concepts**: Combining path, query, and body parameters

5. **Background Tasks**: https://fastapi.tiangolo.com/tutorial/background-tasks/
   - **Why**: Async operations that don't block response (cleanup, notifications)
   - **Key Concepts**: BackgroundTasks dependency, async background functions

6. **CORS (Cross-Origin Resource Sharing)**: https://fastapi.tiangolo.com/tutorial/cors/
   - **Why**: Frontend running on different port needs CORS configured
   - **Key Concepts**: CORSMiddleware, allowed origins, credentials

**Code Examples from Docs**:

```python
# Async endpoint with await
@app.get('/tasks')
async def read_tasks():
    tasks = await get_tasks_from_db()
    return tasks

# Sync endpoint for blocking operations
@app.get('/export')
def export_tasks():
    file_path = generate_csv()  # Blocking I/O
    return FileResponse(file_path)

# Dependency injection
async def get_db():
    db = Database()
    try:
        yield db
    finally:
        await db.disconnect()

@app.get('/tasks')
async def read_tasks(db: Database = Depends(get_db)):
    return await db.fetch_all("SELECT * FROM tasks")
```

**Gotchas from Documentation**:
- `await` can only be used inside `async def` functions
- If unsure about async/sync, use normal `def` - FastAPI runs it in a threadpool
- Dependencies with `def` run in external threadpool automatically
- Background tasks should not modify response after it's sent

---

### Pydantic (Validation & Schemas)
**Official Docs**: https://docs.pydantic.dev/latest/
**Version**: v2 (breaking changes from v1)
**Archon Source**: c0e629a894699314 (Pydantic AI framework docs)
**Relevance**: 10/10

**Sections to Read**:

1. **Models**: https://docs.pydantic.dev/latest/concepts/models/
   - **Why**: Define Task, Project schemas with validation
   - **Key Concepts**: BaseModel, field types, validators, computed fields

2. **Validators**: https://docs.pydantic.dev/latest/concepts/validators/
   - **Why**: Custom validation for task status transitions, priority values
   - **Key Concepts**:
     - `@field_validator` (replaces deprecated `@validator`)
     - Before vs after validation modes
     - Reusable validators

3. **Fields**: https://docs.pydantic.dev/latest/concepts/fields/
   - **Why**: Field metadata, defaults, constraints (min length, max length)
   - **Key Concepts**: Field(...) with description, examples, constraints

4. **JSON Schema**: https://docs.pydantic.dev/latest/concepts/json_schema/
   - **Why**: Auto-generate OpenAPI docs for FastAPI
   - **Key Concepts**: model_json_schema(), customization

5. **Migration Guide (V1 to V2)**: https://docs.pydantic.dev/latest/migration/
   - **Why**: If referencing any V1 examples, know what changed
   - **Key Concepts**: @validator → @field_validator, Config changes

**Code Examples**:

```python
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Literal

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500, description="Task title")
    description: str | None = Field(None, description="Markdown description")
    status: Literal["todo", "doing", "review", "done"] = "todo"
    priority: Literal["low", "medium", "high", "urgent"] = "medium"
    assignee: str = "User"

    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Title cannot be empty or whitespace')
        return v.strip()

class TaskResponse(TaskCreate):
    id: str
    project_id: str | None
    position: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}  # For ORM mode
```

**Gotchas**:
- V2 uses `model_config` dict instead of `Config` class
- `@validator` is deprecated, use `@field_validator`
- Field defaults: `Field(...)` means required, `Field(None)` means optional with None default
- Use `from_attributes=True` (was `orm_mode=True` in V1) for SQLAlchemy models

---

### React 18 + TypeScript
**Official Docs**: https://react.dev/
**Version**: React 18+ with TypeScript 5+
**Archon Source**: Not in Archon (Claude Code docs only)
**Relevance**: 9/10

**Sections to Read**:

1. **React Hooks Reference**: https://react.dev/reference/react/hooks
   - **Why**: useState, useEffect for component logic
   - **Key Concepts**: Rules of hooks, custom hooks, dependency arrays

2. **TypeScript with React**: https://react.dev/learn/typescript
   - **Why**: Type-safe component props, event handlers
   - **Key Concepts**: FC type, PropsWithChildren, typing events

3. **Managing State**: https://react.dev/learn/managing-state
   - **Why**: When to lift state up vs use external state (TanStack Query)
   - **Key Concepts**: State composition, avoiding prop drilling

**Code Examples**:

```typescript
import { FC, useState } from 'react';

interface TaskCardProps {
  task: Task;
  onUpdate: (id: string, updates: Partial<Task>) => void;
}

const TaskCard: FC<TaskCardProps> = ({ task, onUpdate }) => {
  const [isEditing, setIsEditing] = useState(false);

  const handleStatusChange = (newStatus: Task['status']) => {
    onUpdate(task.id, { status: newStatus });
  };

  return (
    <div className="task-card">
      <h3>{task.title}</h3>
      {/* ... */}
    </div>
  );
};
```

---

## Frontend State Management

### TanStack Query v5
**Official Docs**: https://tanstack.com/query/latest/docs/framework/react/overview
**Version**: v5 (latest)
**Archon Source**: Not in Archon
**Relevance**: 10/10

**Sections to Read**:

1. **Overview**: https://tanstack.com/query/latest/docs/framework/react/overview
   - **Why**: Understand core concepts: queries, mutations, cache
   - **Key Concepts**: Automatic background refetching, cache invalidation, deduplication

2. **Queries**: https://tanstack.com/query/latest/docs/framework/react/guides/queries
   - **Why**: Fetching tasks, projects from API
   - **Key Concepts**: useQuery hook, query keys, staleTime, refetchInterval

3. **Mutations**: https://tanstack.com/query/v5/docs/framework/react/guides/mutations
   - **Why**: Creating, updating, deleting tasks
   - **Key Concepts**: useMutation, onSuccess, onError callbacks

4. **Optimistic Updates**: https://tanstack.com/query/v5/docs/react/guides/optimistic-updates
   - **Why**: Instant UI feedback on drag-and-drop, task updates
   - **Key Concepts**:
     - UI-based optimistic updates (simpler)
     - Cache-based optimistic updates (with rollback)
     - `onMutate`, `onError`, `onSettled` lifecycle

5. **Query Invalidation**: https://tanstack.com/query/latest/docs/framework/react/guides/query-invalidation
   - **Why**: Sync UI after mutations, MCP updates
   - **Key Concepts**: invalidateQueries, queryKey matching

6. **React Query DevTools**: https://tanstack.com/query/latest/docs/framework/react/devtools
   - **Why**: Debug cache state, query lifecycle
   - **Key Concepts**: Installation, usage in development

**Code Examples from Docs**:

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

// Query for tasks
const { data: tasks, isLoading } = useQuery({
  queryKey: ['tasks', { status: 'todo' }],
  queryFn: () => fetch('/api/tasks?status=todo').then(r => r.json()),
  staleTime: 30_000,
  refetchInterval: 30_000,
});

// Mutation with optimistic update (UI-based)
const updateTaskMutation = useMutation({
  mutationFn: (update: { id: string; status: string }) =>
    fetch(`/api/tasks/${update.id}`, {
      method: 'PATCH',
      body: JSON.stringify({ status: update.status }),
    }),
  onSettled: () => {
    queryClient.invalidateQueries({ queryKey: ['tasks'] });
  },
});

// Optimistic update (cache-based) with rollback
const queryClient = useQueryClient();

const addTaskMutation = useMutation({
  mutationFn: (newTask: TaskCreate) =>
    fetch('/api/tasks', { method: 'POST', body: JSON.stringify(newTask) }),
  onMutate: async (newTask) => {
    // Cancel outgoing queries
    await queryClient.cancelQueries({ queryKey: ['tasks'] });

    // Snapshot previous value
    const previousTasks = queryClient.getQueryData(['tasks']);

    // Optimistically update
    queryClient.setQueryData(['tasks'], (old: Task[]) => [
      ...old,
      { ...newTask, id: 'temp-id', created_at: new Date() }
    ]);

    return { previousTasks };
  },
  onError: (err, newTask, context) => {
    // Rollback on error
    queryClient.setQueryData(['tasks'], context.previousTasks);
  },
  onSettled: () => {
    // Refetch to sync with server
    queryClient.invalidateQueries({ queryKey: ['tasks'] });
  },
});
```

**Live Examples**:
- **Optimistic Updates UI**: https://tanstack.com/query/v5/docs/framework/react/examples/optimistic-updates-ui
- **Optimistic Updates Cache**: https://tanstack.com/query/v5/docs/framework/react/examples/optimistic-updates-cache

**Gotchas**:
- Query keys must be serializable arrays
- `staleTime` controls when data is considered stale (default 0)
- `refetchInterval` for polling - pause when tab hidden with `refetchIntervalInBackground: false`
- Always cancel queries in `onMutate` to avoid race conditions
- `onSettled` runs after success OR error, good for invalidation

---

## Drag-and-Drop Library

### react-dnd
**Official Docs**: https://react-dnd.github.io/react-dnd/
**Version**: 16.0.1
**Archon Source**: Not in Archon (but Archon uses react-dnd in codebase)
**Relevance**: 9/10

**Sections to Read**:

1. **Quick Start**: https://react-dnd.github.io/react-dnd/docs/overview
   - **Why**: Setup DndProvider, understand drag sources and drop targets
   - **Key Concepts**: HTML5 backend, item types, monitor

2. **useDrag Hook**: https://react-dnd.github.io/react-dnd/docs/api/use-drag
   - **Why**: Make task cards draggable
   - **Key Concepts**: Collect function, item spec, drag preview

3. **useDrop Hook**: https://react-dnd.github.io/react-dnd/docs/api/use-drop
   - **Why**: Make Kanban columns accept drops
   - **Key Concepts**: Accept item types, drop handler, monitor.isOver()

4. **Examples**: https://react-dnd.github.io/react-dnd/examples
   - **Why**: See drag-and-drop patterns in action
   - **Key Concepts**: Sortable lists, Kanban boards

**Code Example (from Archon pattern)**:

```typescript
import { useDrag, useDrop } from 'react-dnd';

// Define item types
const ItemTypes = {
  TASK: 'task',
};

// Draggable task card
interface DraggableTaskProps {
  task: Task;
}

const DraggableTask: FC<DraggableTaskProps> = ({ task }) => {
  const [{ isDragging }, drag] = useDrag({
    type: ItemTypes.TASK,
    item: { id: task.id, status: task.status },
    collect: (monitor) => ({
      isDragging: !!monitor.isDragging(),
    }),
  });

  return (
    <div ref={drag} style={{ opacity: isDragging ? 0.5 : 1 }}>
      {task.title}
    </div>
  );
};

// Droppable Kanban column
interface KanbanColumnProps {
  status: Task['status'];
  onTaskMove: (taskId: string, newStatus: Task['status']) => void;
}

const KanbanColumn: FC<KanbanColumnProps> = ({ status, onTaskMove }) => {
  const [{ isOver }, drop] = useDrop({
    accept: ItemTypes.TASK,
    drop: (item: { id: string; status: Task['status'] }) => {
      if (item.status !== status) {
        onTaskMove(item.id, status);
      }
    },
    collect: (monitor) => ({
      isOver: !!monitor.isOver(),
    }),
  });

  return (
    <div ref={drop} className={isOver ? 'highlight' : ''}>
      <h2>{status}</h2>
      {/* Render tasks */}
    </div>
  );
};

// App root wraps in DndProvider
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';

<DndProvider backend={HTML5Backend}>
  <App />
</DndProvider>
```

**GitHub Repository**: https://github.com/react-dnd/react-dnd

**Gotchas**:
- Must wrap app in `<DndProvider>` with backend (HTML5Backend for web)
- Item type matching is strict - use constants
- TypeScript: Define item type interface for type safety
- `collect` function returns props based on monitor state
- Multiple drop zones: Use `canDrop` to validate

---

## UI Component Library

### shadcn/ui
**Official Docs**: https://ui.shadcn.com/docs
**Version**: Latest
**Archon Source**: Not in Archon
**Relevance**: 8/10

**Sections to Read**:

1. **Introduction**: https://ui.shadcn.com/docs
   - **Why**: Understand component ownership model (copy code, not npm package)
   - **Key Concepts**: Built on Radix UI + Tailwind, TypeScript support

2. **Installation (Vite)**: https://ui.shadcn.com/docs/installation/vite
   - **Why**: Setup for React + Vite project
   - **Key Concepts**: tailwind.config, components.json, CLI usage

3. **Components**: https://ui.shadcn.com/docs/components
   - **Why**: Browse available components for task UI
   - **Recommended for project**:
     - **Button**: https://ui.shadcn.com/docs/components/button
     - **Card**: https://ui.shadcn.com/docs/components/card
     - **Dialog**: https://ui.shadcn.com/docs/components/dialog (for task modals)
     - **Select**: https://ui.shadcn.com/docs/components/select (for status, priority)
     - **Textarea**: https://ui.shadcn.com/docs/components/textarea (for description)
     - **Badge**: https://ui.shadcn.com/docs/components/badge (for status chips)

4. **Theming**: https://ui.shadcn.com/docs/theming
   - **Why**: Customize colors to match Tron-inspired glassmorphism
   - **Key Concepts**: CSS variables, dark mode

**Installation**:
```bash
npx shadcn@latest init
npx shadcn@latest add button card dialog select textarea badge
```

**Code Example**:

```typescript
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

<Card>
  <CardHeader>
    <CardTitle>{task.title}</CardTitle>
  </CardHeader>
  <CardContent>
    <p>{task.description}</p>
    <Button onClick={() => updateTask(task.id, { status: 'doing' })}>
      Start Task
    </Button>
  </CardContent>
</Card>
```

**Gotchas**:
- Not an npm package - CLI copies component code into your project
- Full control but requires managing component updates manually
- TypeScript-first - use JS version via CLI flag if needed
- Depends on Tailwind CSS configuration

---

## Database Documentation

### PostgreSQL
**Official Docs**: https://www.postgresql.org/docs/current/
**Version**: 16+ (latest LTS)
**Archon Source**: Not in Archon
**Relevance**: 8/10

**Sections to Read**:

1. **Chapter 11: Indexes**: https://www.postgresql.org/docs/current/indexes.html
   - **Why**: Optimize task queries by status, project, assignee
   - **Key Concepts**:
     - B-tree indexes (default, good for equality and range)
     - Multi-column indexes (project_id + status)
     - Partial indexes (WHERE status != 'done')

2. **CREATE INDEX**: https://www.postgresql.org/docs/current/sql-createindex.html
   - **Why**: Syntax for creating indexes, CONCURRENTLY option
   - **Key Concepts**: Index types, expressions, CONCURRENTLY for production

3. **Foreign Keys**: https://www.postgresql.org/docs/current/ddl-constraints.html#DDL-CONSTRAINTS-FK
   - **Why**: task.project_id references projects.id with CASCADE
   - **Key Concepts**: ON DELETE CASCADE, ON UPDATE CASCADE

4. **Data Types**: https://www.postgresql.org/docs/current/datatype.html
   - **Why**: UUID, TIMESTAMP, VARCHAR, TEXT, ENUM alternatives
   - **Key Concepts**:
     - UUID for IDs (gen_random_uuid())
     - TIMESTAMP vs TIMESTAMPTZ
     - TEXT vs VARCHAR (prefer TEXT in PostgreSQL)

**Index Strategy for Task Management**:

```sql
-- Primary keys (automatic indexes)
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL CHECK (status IN ('todo', 'doing', 'review', 'done')),
    assignee TEXT DEFAULT 'User',
    priority TEXT DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    position INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for filtering
CREATE INDEX idx_tasks_project_id ON tasks(project_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_assignee ON tasks(assignee);

-- Composite index for ordered retrieval within status column (Kanban)
CREATE INDEX idx_tasks_status_position ON tasks(status, position);

-- Partial index for active tasks only (performance optimization)
CREATE INDEX idx_tasks_active ON tasks(project_id, status)
    WHERE status IN ('todo', 'doing', 'review');
```

**Best Practices from Community**:
- Primary keys auto-indexed
- Foreign keys NOT auto-indexed - create manually
- Use EXPLAIN ANALYZE to verify index usage
- VACUUM and ANALYZE regularly for statistics
- B-tree for equality and range, GIN for JSONB/arrays (not needed for MVP)

**Gotchas**:
- VARCHAR(n) and TEXT have same performance in PostgreSQL - prefer TEXT
- Indexes add overhead to writes - don't over-index
- CREATE INDEX CONCURRENTLY to avoid locking table (production)
- ENUM types are rigid - use CHECK constraints with TEXT for flexibility

---

### asyncpg (PostgreSQL Driver for Python)
**Official Docs**: https://magicstack.github.io/asyncpg/current/
**GitHub**: https://github.com/MagicStack/asyncpg
**Archon Source**: Not in Archon
**Relevance**: 9/10

**Sections to Read**:

1. **Usage**: https://magicstack.github.io/asyncpg/current/usage.html
   - **Why**: Connection pool, async queries
   - **Key Concepts**: Pool creation, acquire/release, transactions

2. **API Reference**: https://magicstack.github.io/asyncpg/current/api/index.html
   - **Why**: fetch(), fetchrow(), execute(), executemany()
   - **Key Concepts**: Query methods, prepared statements

**Code Example**:

```python
import asyncpg

# Create connection pool (app startup)
pool = await asyncpg.create_pool(
    host='localhost',
    port=5432,
    user='taskuser',
    password='password',
    database='taskmanager',
    min_size=5,
    max_size=20
)

# Query tasks
async def get_tasks(status: str | None = None):
    async with pool.acquire() as conn:
        if status:
            rows = await conn.fetch(
                "SELECT * FROM tasks WHERE status = $1 ORDER BY position",
                status
            )
        else:
            rows = await conn.fetch("SELECT * FROM tasks ORDER BY created_at DESC")
        return [dict(row) for row in rows]

# Insert task
async def create_task(task_data: dict):
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO tasks (title, description, status, priority, assignee, project_id)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING *
            """,
            task_data['title'],
            task_data.get('description'),
            task_data.get('status', 'todo'),
            task_data.get('priority', 'medium'),
            task_data.get('assignee', 'User'),
            task_data.get('project_id')
        )
        return dict(row)

# Transaction for position updates
async def update_task_position(task_id: str, new_status: str, new_position: int):
    async with pool.acquire() as conn:
        async with conn.transaction():
            # Increment positions >= new_position in new status
            await conn.execute(
                "UPDATE tasks SET position = position + 1 WHERE status = $1 AND position >= $2",
                new_status, new_position
            )
            # Update task
            await conn.execute(
                "UPDATE tasks SET status = $1, position = $2 WHERE id = $3",
                new_status, new_position, task_id
            )
```

**Gotchas**:
- Use `$1, $2` placeholders (not `%s` or `?`)
- Always use connection pool in production
- Use `async with pool.acquire()` for automatic connection release
- Transactions: `async with conn.transaction()`
- fetchrow() for single row, fetch() for multiple

---

### Alembic (Database Migrations)
**Official Docs**: https://alembic.sqlalchemy.org/
**Version**: Latest (1.16+)
**Archon Source**: Not in Archon
**Relevance**: 9/10

**Sections to Read**:

1. **Tutorial**: https://alembic.sqlalchemy.org/en/latest/tutorial.html
   - **Why**: Setup migration environment, create first migration
   - **Key Concepts**: alembic init, alembic revision, upgrade/downgrade

2. **Auto Generating Migrations**: https://alembic.sqlalchemy.org/en/latest/autogenerate.html
   - **Why**: Generate migrations from SQLAlchemy models (if using ORM)
   - **Key Concepts**: --autogenerate flag, review generated code

3. **Operation Reference**: https://alembic.sqlalchemy.org/en/latest/ops.html
   - **Why**: Available operations in migration scripts
   - **Key Concepts**: create_table, add_column, create_index, execute (raw SQL)

**Setup**:
```bash
pip install alembic
alembic init alembic
```

**Migration Example**:

```python
# alembic/versions/001_create_tasks_table.py
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = '001'
down_revision = None

def upgrade():
    op.create_table(
        'projects',
        sa.Column('id', UUID, primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.Text, nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        'tasks',
        sa.Column('id', UUID, primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('project_id', UUID, sa.ForeignKey('projects.id', ondelete='CASCADE')),
        sa.Column('title', sa.Text, nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('status', sa.Text, nullable=False, server_default='todo'),
        sa.Column('assignee', sa.Text, server_default='User'),
        sa.Column('priority', sa.Text, server_default='medium'),
        sa.Column('position', sa.Integer, server_default='0'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )

    # Indexes
    op.create_index('idx_tasks_project_id', 'tasks', ['project_id'])
    op.create_index('idx_tasks_status', 'tasks', ['status'])
    op.create_index('idx_tasks_status_position', 'tasks', ['status', 'position'])

def downgrade():
    op.drop_table('tasks')
    op.drop_table('projects')
```

**Commands**:
```bash
# Create migration
alembic revision -m "create tasks table"

# Run migrations
alembic upgrade head

# Rollback one version
alembic downgrade -1

# View current version
alembic current

# View migration history
alembic history
```

**Gotchas**:
- Always review auto-generated migrations before running
- Test both upgrade() and downgrade()
- Use `sa.text()` for raw SQL expressions
- Migrations run in order by revision ID
- Can't autogenerate everything (e.g., data migrations, raw SQL)

---

## Docker & Deployment

### Docker Compose
**Official Docs**: https://docs.docker.com/compose/
**Version**: Compose file format v3.8+
**Archon Source**: Not in Archon
**Relevance**: 10/10

**Sections to Read**:

1. **Services**: https://docs.docker.com/reference/compose-file/services/
   - **Why**: Define backend, frontend, database services
   - **Key Concepts**:
     - `healthcheck` attribute for service health
     - `depends_on` with `service_healthy` condition
     - `environment` for config
     - `volumes` for persistence

2. **Networking**: https://docs.docker.com/compose/networking/
   - **Why**: Internal service communication
   - **Key Concepts**: Default network, service discovery by name

3. **Volumes**: https://docs.docker.com/compose/compose-file/07-volumes/
   - **Why**: PostgreSQL data persistence
   - **Key Concepts**: Named volumes vs bind mounts

**docker-compose.yml Example**:

```yaml
version: '3.8'

services:
  db:
    image: postgres:16
    container_name: taskmanager-db
    environment:
      POSTGRES_DB: taskmanager
      POSTGRES_USER: taskuser
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - taskmanager-db-data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U taskuser -d taskmanager"]
      interval: 5s
      timeout: 3s
      retries: 5
      start_period: 10s
    restart: unless-stopped

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: taskmanager-backend
    depends_on:
      db:
        condition: service_healthy
    environment:
      DATABASE_URL: postgresql://taskuser:${DB_PASSWORD}@db:5432/taskmanager
      MCP_PORT: 8051
      CORS_ORIGINS: http://localhost:3000
    ports:
      - "8000:8000"  # API
      - "8051:8051"  # MCP server
    volumes:
      - ./backend:/app  # Dev: hot reload
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: taskmanager-frontend
    depends_on:
      - backend
    environment:
      VITE_API_URL: http://localhost:8000
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app  # Dev: hot reload
      - /app/node_modules  # Exclude node_modules
    command: npm run dev -- --host
    restart: unless-stopped

volumes:
  taskmanager-db-data:
    driver: local
```

**Backend Dockerfile (multi-stage)**:

```dockerfile
# Build stage
FROM python:3.12-slim AS builder
WORKDIR /app
RUN pip install uv
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev

# Production stage
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY . .
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000 8051
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Frontend Dockerfile**:

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev", "--", "--host"]
```

**.env.example**:

```bash
# Database
DB_PASSWORD=your_secure_password_here

# Backend
DATABASE_URL=postgresql://taskuser:${DB_PASSWORD}@db:5432/taskmanager
MCP_PORT=8051
CORS_ORIGINS=http://localhost:3000

# Frontend
VITE_API_URL=http://localhost:8000
```

**Commands**:
```bash
# Start all services
docker-compose up

# Build and start
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop all services
docker-compose down

# Stop and remove volumes (data loss!)
docker-compose down -v
```

**Gotchas from Documentation**:
- `depends_on` with `service_healthy` waits for healthcheck to pass
- Volume mounts: Named volumes persist, bind mounts for dev hot reload
- Service names become DNS hostnames (backend calls `db:5432`)
- Environment variables: Use `${VAR}` from .env file
- `restart: unless-stopped` for production resilience
- Healthcheck `start_period` gives service time to initialize

---

## MCP Integration

### Model Context Protocol (MCP)
**Official Docs**: https://modelcontextprotocol.io/
**Version**: Latest
**Archon Source**: d60a71d62eb201d5 (MCP documentation)
**Relevance**: 10/10

**Sections to Read**:

1. **Introduction**: https://modelcontextprotocol.io/introduction
   - **Why**: Understand MCP architecture, client-server model
   - **Key Concepts**: Resources, prompts, tools, transports

2. **Core Concepts - Tools**: https://modelcontextprotocol.io/docs/concepts/tools
   - **Why**: Define task management tools for AI assistants
   - **Key Concepts**:
     - Tool schema with JSON Schema input validation
     - Tool execution and response format
     - Error handling

3. **Servers**: https://modelcontextprotocol.io/docs/concepts/servers
   - **Why**: Implement MCP server in backend
   - **Key Concepts**: Server capabilities, transport (stdio, HTTP)

4. **Example Servers**: https://modelcontextprotocol.io/examples
   - **Why**: Reference implementations
   - **Key Examples**:
     - Filesystem server (read/write patterns)
     - Everything server (comprehensive example)

**Tool Schema Example**:

```typescript
// MCP tool definition (conceptual - actual implementation in Python)
{
  "name": "find_tasks",
  "description": "Find and search tasks with optional filtering",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "Keyword search across title and description"
      },
      "task_id": {
        "type": "string",
        "description": "Get specific task by ID"
      },
      "filter_by": {
        "type": "string",
        "enum": ["status", "project", "assignee"],
        "description": "Field to filter by"
      },
      "filter_value": {
        "type": "string",
        "description": "Value to filter for"
      },
      "project_id": {
        "type": "string",
        "description": "Filter tasks by project"
      }
    }
  }
}

{
  "name": "manage_task",
  "description": "Create, update, or delete tasks",
  "inputSchema": {
    "type": "object",
    "properties": {
      "action": {
        "type": "string",
        "enum": ["create", "update", "delete"],
        "description": "Action to perform"
      },
      "task_id": {
        "type": "string",
        "description": "Task ID (required for update/delete)"
      },
      "title": { "type": "string" },
      "description": { "type": "string" },
      "status": {
        "type": "string",
        "enum": ["todo", "doing", "review", "done"]
      },
      "priority": {
        "type": "string",
        "enum": ["low", "medium", "high", "urgent"]
      },
      "assignee": { "type": "string" }
    },
    "required": ["action"]
  }
}
```

**MCP Response Format**:

```json
// Success response
{
  "content": [
    {
      "type": "text",
      "text": "{\"success\": true, \"tasks\": [{\"id\": \"...\", \"title\": \"...\"}]}"
    }
  ]
}

// Error response
{
  "content": [
    {
      "type": "text",
      "text": "{\"success\": false, \"error\": \"Task not found\", \"suggestion\": \"Use find_tasks() to list available tasks\"}"
    }
  ],
  "isError": true
}
```

**Gotchas from Archon MCP Implementation**:
- MCP tools must return JSON string (not Python dict)
- Truncate large fields in list responses (description > 1000 chars)
- Exclude JSONB arrays in list responses, replace with counts
- Provide structured errors with suggestions for AI assistants
- Use consolidated tools (`find_tasks`, `manage_task`) vs many small tools
- HTTP transport for remote access: `npx mcp-remote http://localhost:8051/mcp`

---

### FastMCP (Python MCP Framework)
**GitHub**: https://github.com/jlowin/fastmcp
**Archon Source**: Referenced in e9eb05e2bf38f125 (12-factor-agents)
**Relevance**: 10/10

**Sections to Read (GitHub README)**:

1. **Quick Start**: Tool registration with decorators
2. **Server Setup**: Creating MCP server instance
3. **Tool Patterns**: Examples of tool implementations

**Code Example (from Archon pattern)**:

```python
from fastmcp import FastMCP

mcp = FastMCP("Task Manager")

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
    """
    Find and search tasks (consolidated: list + search + get).

    Args:
        query: Keyword search across title and description
        task_id: Get specific task by ID (returns full details)
        filter_by: Field to filter by (status, project, assignee)
        filter_value: Value to filter for
        project_id: Filter tasks by project
        page: Page number for pagination
        per_page: Items per page

    Returns:
        JSON string with tasks array or single task
    """
    try:
        # Get specific task
        if task_id:
            task = await task_service.get_task(task_id)
            if not task:
                return json.dumps({
                    "success": False,
                    "error": "Task not found",
                    "suggestion": "Use find_tasks() without task_id to list all tasks"
                })
            return json.dumps({"success": True, "task": task})

        # List/search tasks
        filters = {}
        if filter_by and filter_value:
            filters[filter_by] = filter_value
        if project_id:
            filters['project_id'] = project_id

        tasks = await task_service.list_tasks(
            query=query,
            filters=filters,
            page=page,
            per_page=per_page
        )

        # Optimize responses for MCP
        optimized_tasks = [optimize_task_for_mcp(t) for t in tasks]

        return json.dumps({
            "success": True,
            "tasks": optimized_tasks,
            "page": page,
            "per_page": per_page,
            "total": len(tasks)
        })

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "suggestion": "Check the error message and try again"
        })

def optimize_task_for_mcp(task: dict) -> dict:
    """Optimize task for MCP response (reduce size)."""
    # Truncate long descriptions
    if task.get("description") and len(task["description"]) > 1000:
        task["description"] = task["description"][:997] + "..."
    return task

@mcp.tool()
async def manage_task(
    action: str,  # "create" | "update" | "delete"
    task_id: str | None = None,
    project_id: str | None = None,
    title: str | None = None,
    description: str | None = None,
    status: str | None = None,
    assignee: str | None = None,
    priority: str | None = None,
    position: int | None = None
) -> str:
    """
    Manage tasks (consolidated: create/update/delete).

    Args:
        action: Action to perform (create, update, delete)
        task_id: Task ID (required for update/delete)
        project_id: Project ID (for create)
        title: Task title
        description: Markdown description
        status: Task status (todo, doing, review, done)
        assignee: Assigned to (User, agent name, etc.)
        priority: Priority level (low, medium, high, urgent)
        position: Position for ordering

    Returns:
        JSON string with success status and task data
    """
    try:
        if action == "create":
            task_data = {
                "title": title,
                "description": description,
                "status": status or "todo",
                "priority": priority or "medium",
                "assignee": assignee or "User",
                "project_id": project_id,
                "position": position or 0
            }
            task = await task_service.create_task(task_data)
            return json.dumps({"success": True, "task": task})

        elif action == "update":
            if not task_id:
                return json.dumps({
                    "success": False,
                    "error": "task_id required for update action"
                })

            updates = {}
            for field in ["title", "description", "status", "assignee", "priority", "position"]:
                value = locals()[field]
                if value is not None:
                    updates[field] = value

            task = await task_service.update_task(task_id, updates)
            return json.dumps({"success": True, "task": task})

        elif action == "delete":
            if not task_id:
                return json.dumps({
                    "success": False,
                    "error": "task_id required for delete action"
                })
            await task_service.delete_task(task_id)
            return json.dumps({"success": True, "message": "Task deleted"})

        else:
            return json.dumps({
                "success": False,
                "error": f"Invalid action: {action}",
                "suggestion": "Use 'create', 'update', or 'delete'"
            })

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })

# Run MCP server
if __name__ == "__main__":
    mcp.run()
```

**MCP Server Integration in FastAPI**:

```python
# main.py
from fastapi import FastAPI
from mcp_server import mcp

app = FastAPI()

# Regular API routes
@app.get("/api/tasks")
async def list_tasks():
    # ...
    pass

# Mount MCP server (if using HTTP transport)
# Or run separately on different port
```

**Gotchas**:
- Tools must return JSON strings, not Python dicts
- Type hints in tool functions become JSON Schema
- Use descriptive docstrings - shown to AI assistants
- Error handling: Return structured errors, not exceptions
- Long-running operations: MCP expects quick responses

---

## Testing Documentation

### pytest (Python Testing)
**Official Docs**: https://docs.pytest.org/
**Version**: Latest
**Archon Source**: Not in Archon
**Relevance**: 8/10

**Sections to Read**:

1. **Getting Started**: https://docs.pytest.org/en/latest/getting-started.html
   - **Why**: Setup, first tests
   - **Key Concepts**: Test discovery, assert statements

2. **Fixtures**: https://docs.pytest.org/en/latest/how-to/fixtures.html
   - **Why**: Reusable test setup (database, client)
   - **Key Concepts**: @pytest.fixture, scope, autouse

3. **Async Tests**: https://docs.pytest.org/en/latest/how-to/async.html
   - **Why**: Test async endpoints and database operations
   - **Key Concepts**: pytest-asyncio, async fixtures

**Test Example**:

```python
import pytest
from httpx import AsyncClient
from main import app

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def sample_task():
    # Create test task
    task = await task_service.create_task({
        "title": "Test Task",
        "status": "todo"
    })
    yield task
    # Cleanup
    await task_service.delete_task(task['id'])

@pytest.mark.asyncio
async def test_create_task(client):
    response = await client.post("/api/tasks", json={
        "title": "New Task",
        "description": "Test description"
    })
    assert response.status_code == 201
    data = response.json()
    assert data['title'] == "New Task"
    assert data['status'] == "todo"

@pytest.mark.asyncio
async def test_update_task_status(client, sample_task):
    response = await client.patch(
        f"/api/tasks/{sample_task['id']}",
        json={"status": "doing"}
    )
    assert response.status_code == 200
    assert response.json()['status'] == "doing"

@pytest.mark.asyncio
async def test_mcp_find_tasks():
    result = await find_tasks(filter_by="status", filter_value="todo")
    data = json.loads(result)
    assert data['success'] is True
    assert isinstance(data['tasks'], list)
```

---

### Vitest (Frontend Testing)
**Official Docs**: https://vitest.dev/
**Version**: Latest
**Archon Source**: Not in Archon
**Relevance**: 7/10

**Sections to Read**:

1. **Getting Started**: https://vitest.dev/guide/
   - **Why**: Setup for Vite projects
   - **Key Concepts**: Configuration, test syntax

2. **Mocking**: https://vitest.dev/guide/mocking.html
   - **Why**: Mock API calls, TanStack Query
   - **Key Concepts**: vi.fn(), vi.mock()

**Test Example**:

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import TaskCard from './TaskCard';

describe('TaskCard', () => {
  it('renders task title and description', () => {
    const task = {
      id: '123',
      title: 'Test Task',
      description: 'Test description',
      status: 'todo',
      priority: 'medium',
    };

    const queryClient = new QueryClient();
    render(
      <QueryClientProvider client={queryClient}>
        <TaskCard task={task} onUpdate={vi.fn()} />
      </QueryClientProvider>
    );

    expect(screen.getByText('Test Task')).toBeInTheDocument();
    expect(screen.getByText('Test description')).toBeInTheDocument();
  });
});
```

---

## Additional Resources

### TypeScript Official Docs
**URL**: https://www.typescriptlang.org/docs/
**Relevance**: 9/10

**Key Sections**:
- **Handbook**: https://www.typescriptlang.org/docs/handbook/intro.html
- **React TypeScript Cheatsheet**: https://react-typescript-cheatsheet.netlify.app/

**Example**: Type-safe task types

```typescript
// types/task.ts
export type TaskStatus = 'todo' | 'doing' | 'review' | 'done';
export type TaskPriority = 'low' | 'medium' | 'high' | 'urgent';

export interface Task {
  id: string;
  project_id: string | null;
  title: string;
  description: string | null;
  status: TaskStatus;
  priority: TaskPriority;
  assignee: string;
  position: number;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  assignee?: string;
  project_id?: string;
}

export interface TaskUpdate extends Partial<TaskCreate> {
  position?: number;
}
```

---

### Tailwind CSS Documentation
**URL**: https://tailwindcss.com/docs
**Relevance**: 8/10 (if using shadcn/ui)

**Key Sections**:
- **Installation**: https://tailwindcss.com/docs/installation/using-vite
- **Flexbox & Grid**: https://tailwindcss.com/docs/flex
- **Dark Mode**: https://tailwindcss.com/docs/dark-mode

---

### Vite Documentation
**URL**: https://vitejs.dev/guide/
**Relevance**: 8/10

**Key Sections**:
- **Getting Started**: https://vitejs.dev/guide/
- **Env Variables**: https://vitejs.dev/guide/env-and-mode.html (VITE_ prefix)
- **Backend Integration**: https://vitejs.dev/guide/backend-integration.html

---

## Community Resources

### Stack Overflow Tags
- **FastAPI**: https://stackoverflow.com/questions/tagged/fastapi
- **React DnD**: https://stackoverflow.com/questions/tagged/react-dnd
- **TanStack Query**: https://stackoverflow.com/questions/tagged/react-query
- **PostgreSQL**: https://stackoverflow.com/questions/tagged/postgresql

### GitHub Discussions
- **FastAPI**: https://github.com/fastapi/fastapi/discussions
- **TanStack Query**: https://github.com/TanStack/query/discussions
- **MCP**: https://github.com/modelcontextprotocol/mcp/discussions

---

## Documentation Gaps

**Not found in Archon or Web**:
- **@hello-pangea/dnd**: Fork of react-beautiful-dnd (deprecated). Alternative found: react-dnd (actively maintained, better TypeScript support)

**Outdated or Incomplete**:
- **react-beautiful-dnd**: Archived/unmaintained. **Recommendation**: Use react-dnd instead (proven in Archon)

---

## Quick Reference URLs

For easy copy-paste into PRP:

```yaml
Backend Framework:
  - FastAPI Async: https://fastapi.tiangolo.com/async/
  - FastAPI Dependencies: https://fastapi.tiangolo.com/tutorial/dependencies/
  - Pydantic Models: https://docs.pydantic.dev/latest/concepts/models/
  - Pydantic Validators: https://docs.pydantic.dev/latest/concepts/validators/

Frontend Framework:
  - React TypeScript: https://react.dev/learn/typescript
  - TanStack Query Mutations: https://tanstack.com/query/v5/docs/framework/react/guides/mutations
  - TanStack Query Optimistic Updates: https://tanstack.com/query/v5/docs/react/guides/optimistic-updates
  - react-dnd Overview: https://react-dnd.github.io/react-dnd/docs/overview

UI Components:
  - shadcn/ui Docs: https://ui.shadcn.com/docs
  - shadcn/ui Components: https://ui.shadcn.com/docs/components

Database:
  - PostgreSQL Indexes: https://www.postgresql.org/docs/current/indexes.html
  - asyncpg Usage: https://magicstack.github.io/asyncpg/current/usage.html
  - Alembic Tutorial: https://alembic.sqlalchemy.org/en/latest/tutorial.html

Docker:
  - Docker Compose Services: https://docs.docker.com/reference/compose-file/services/
  - Docker Compose Networking: https://docs.docker.com/compose/networking/

MCP:
  - MCP Introduction: https://modelcontextprotocol.io/introduction
  - MCP Tools Concept: https://modelcontextprotocol.io/docs/concepts/tools
  - MCP Examples: https://modelcontextprotocol.io/examples

Testing:
  - pytest Fixtures: https://docs.pytest.org/en/latest/how-to/fixtures.html
  - pytest Async: https://docs.pytest.org/en/latest/how-to/async.html
  - Vitest Guide: https://vitest.dev/guide/
```

---

## Recommendations for PRP Assembly

When generating the PRP:

1. **Include these URLs** in "Documentation & References" section
   - Group by category (Backend, Frontend, Database, Docker, MCP)
   - Link to specific sections, not just homepages

2. **Extract code examples** shown above into PRP context
   - FastAPI async endpoint patterns
   - Pydantic validation models
   - TanStack Query optimistic updates
   - react-dnd drag-and-drop hooks
   - Docker Compose healthcheck configuration
   - MCP tool implementations

3. **Highlight gotchas** from documentation in "Known Gotchas" section
   - Pydantic V2 breaking changes (@validator → @field_validator)
   - TanStack Query cache invalidation timing
   - Docker Compose depends_on with service_healthy
   - MCP tool response format (JSON strings)
   - PostgreSQL foreign key indexes (not automatic)

4. **Reference specific sections** in implementation tasks
   - Example: "See FastAPI async docs for when to use async def: https://fastapi.tiangolo.com/async/"
   - Example: "Follow TanStack Query optimistic update pattern: https://tanstack.com/query/v5/docs/react/guides/optimistic-updates"

5. **Note gaps** so implementation can compensate
   - react-beautiful-dnd is deprecated → use react-dnd
   - No specific FastMCP docs → reference Archon implementation patterns

---

## Archon Ingestion Candidates

**Documentation not in Archon but should be**:
- **FastAPI Official Docs** (https://fastapi.tiangolo.com/) - Comprehensive async web framework for Python, critical for vibes ecosystem
- **TanStack Query v5 Docs** (https://tanstack.com/query/latest/docs) - Modern React state management, eliminates Redux complexity
- **react-dnd Documentation** (https://react-dnd.github.io/react-dnd/) - Proven drag-and-drop library used in Archon
- **PostgreSQL Official Docs** (https://www.postgresql.org/docs/current/) - Database best practices, indexing strategies
- **Docker Compose Reference** (https://docs.docker.com/compose/) - Multi-service orchestration patterns
- **shadcn/ui Components** (https://ui.shadcn.com/) - Modern React component library with TypeScript support
- **Alembic Documentation** (https://alembic.sqlalchemy.org/) - Database migration patterns for Python projects

These resources would significantly enhance Archon's ability to guide future full-stack development tasks in the vibes ecosystem.

---

## Summary

**Most Critical Docs to Read First**:
1. **FastAPI Async Guide** (15 min) - Foundation for backend architecture
2. **TanStack Query Optimistic Updates** (20 min) - Critical for UX patterns
3. **MCP Tools Concept** (10 min) - Core integration requirement
4. **Docker Compose Services** (15 min) - Deployment foundation
5. **react-dnd Overview** (10 min) - Drag-and-drop implementation

**Estimated Total Reading Time**: 6-8 hours for comprehensive coverage

**Confidence Level**: 9/10
- Strong coverage from Archon knowledge base (MCP, Pydantic patterns)
- Comprehensive web documentation for frontend technologies
- Working code examples extracted from official sources
- Known gotchas documented from both Archon experience and official docs
- Clear recommendations for library choices (react-dnd over react-beautiful-dnd)
