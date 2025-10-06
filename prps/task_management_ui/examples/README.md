# Code Examples for task_management_ui

## Overview

This directory contains **physically extracted code files** from Archon's task management implementation, demonstrating proven patterns for building a containerized task management system with MCP integration, Kanban UI, and FastAPI backend.

**Quality Score**: 9/10 - Comprehensive coverage of all key patterns with working code examples

## Examples in This Directory

| File | Source | Pattern | Relevance |
|------|--------|---------|-----------|
| mcp/task_tools.py | Archon task_tools.py | Consolidated MCP tools | 10/10 |
| backend/task_service.py | Archon task_service.py | Service layer with validation | 9/10 |
| frontend/KanbanColumn.tsx | Archon KanbanColumn.tsx | react-dnd drag-and-drop | 10/10 |
| frontend/useTaskQueries.ts | Archon useTaskQueries.ts | TanStack Query hooks | 10/10 |
| docker/docker-compose.yml | Archon docker-compose.yml | Multi-service deployment | 8/10 |
| database/schema.sql | Archon complete_setup.sql | PostgreSQL schema | 9/10 |

---

## Example 1: MCP Tool Pattern

**File**: `mcp/task_tools.py`
**Source**: /Users/jon/source/vibes/repos/Archon/python/src/mcp_server/features/tasks/task_tools.py
**Relevance**: 10/10

### What to Mimic

- **Consolidated Tool Pattern**: Single `find_tasks` tool handles list/search/get operations
  ```python
  @mcp.tool()
  async def find_tasks(
      query: str | None = None,      # Search capability
      task_id: str | None = None,    # Single item get
      filter_by: str | None = None,  # Filter type
      filter_value: str | None = None # Filter value
  ) -> str:
  ```

- **Response Optimization**: Truncate large fields and replace arrays with counts for MCP responses
  ```python
  def optimize_task_response(task: dict) -> dict:
      # Truncate descriptions
      if task["description"] and len(task["description"]) > 1000:
          task["description"] = task["description"][:997] + "..."

      # Replace arrays with counts
      if "sources" in task:
          task["sources_count"] = len(task["sources"])
          del task["sources"]
  ```

- **Action-Based Mutations**: Single `manage_task` tool with action parameter
  ```python
  @mcp.tool()
  async def manage_task(
      action: str,  # "create" | "update" | "delete"
      task_id: str | None = None,
      # ... other fields
  ) -> str:
      if action == "create":
          # Create logic
      elif action == "update":
          # Update logic
      elif action == "delete":
          # Delete logic
  ```

- **Structured Error Handling**: Use MCPErrorFormatter for consistent error responses
  ```python
  return MCPErrorFormatter.format_error(
      error_type="not_found",
      message=f"Task {task_id} not found",
      suggestion="Verify the task ID is correct",
      http_status=404,
  )
  ```

### What to Adapt

- **Tool Names**: Rename `find_tasks`/`manage_task` to match your domain
- **Field Optimization**: Adjust truncation limits and which fields to exclude
- **Validation Rules**: Modify status values and assignee patterns
- **Error Messages**: Customize suggestions for your user context

### What to Skip

- **Archon-Specific Fields**: `sources`, `code_examples` JSONB arrays
- **Feature Labels**: Optional feature grouping field
- **Complex Query Routing**: Simplify if you only have project-scoped tasks

### Pattern Highlights

```python
# KEY PATTERN: Route selection based on filter type
if filter_by == "project" and filter_value:
    url = urljoin(api_url, f"/api/projects/{filter_value}/tasks")
elif filter_by == "status" and filter_value:
    url = urljoin(api_url, "/api/tasks")
    params["status"] = filter_value

# CRITICAL: Always exclude large fields in MCP list responses
params["exclude_large_fields"] = True

# PATTERN: Normalize different API response shapes
if isinstance(result, list):
    tasks = result
elif "tasks" in result:
    tasks = result["tasks"]
```

### Why This Example

This demonstrates Archon's proven MCP consolidation pattern that:
- Reduces tool count from 6+ to 2 (find + manage)
- Optimizes payload size for AI assistant consumption
- Provides flexible querying with minimal tool complexity
- Handles errors with actionable suggestions

---

## Example 2: Service Layer Pattern

**File**: `backend/task_service.py`
**Source**: /Users/jon/source/vibes/repos/Archon/python/src/server/services/projects/task_service.py
**Relevance**: 9/10

### What to Mimic

- **Validation Methods**: Separate validation from business logic
  ```python
  def validate_status(self, status: str) -> tuple[bool, str]:
      if status not in self.VALID_STATUSES:
          return False, f"Invalid status '{status}'. Must be one of: {', '.join(self.VALID_STATUSES)}"
      return True, ""
  ```

- **Position Reordering Logic**: Critical pattern for drag-and-drop
  ```python
  # If inserting at position N:
  # 1. Get all tasks with position >= N
  # 2. Increment each by 1
  # 3. Insert new task at position N

  existing_tasks = (
      self.supabase_client.table("tasks")
      .select("id, task_order")
      .eq("status", task_status)
      .gte("task_order", task_order)
      .execute()
  )

  for task in existing_tasks.data:
      new_order = task["task_order"] + 1
      # Update each task
  ```

- **Conditional Field Exclusion**: Optimize list queries
  ```python
  if exclude_large_fields:
      query = self.supabase_client.table("tasks").select(
          "id, title, description, status, assignee, task_order, "
          "created_at, updated_at, sources, code_examples"  # Fetch for counting
      )
  else:
      query = self.supabase_client.table("tasks").select("*")
  ```

- **Keyword Search Pattern**: Search across multiple fields
  ```python
  if search_query:
      term = search_query.lower()
      query = query.or_(
          f"title.ilike.%{term}%,"
          f"description.ilike.%{term}%,"
          f"feature.ilike.%{term}%"
      )
  ```

### What to Adapt

- **Database Client**: Replace Supabase with your ORM/query builder
- **Validation Rules**: Adjust VALID_STATUSES and VALID_PRIORITIES for your workflow
- **Search Fields**: Change which fields are searchable
- **Response Format**: Customize returned task object structure

### What to Skip

- **Soft Delete Logic**: If using hard delete, skip archived fields
- **JSONB Stats**: If not using JSONB arrays, skip count calculation
- **Parent Task ID**: If not supporting hierarchical tasks

### Pattern Highlights

```python
# CRITICAL: Reordering prevents position conflicts
if task_order > 0:
    # Get tasks at or after new position
    existing = get_tasks_gte_position(project_id, status, task_order)

    # Increment each
    for task in existing:
        update_position(task.id, task.position + 1)

# PATTERN: Partial updates with validation
update_data = {"updated_at": datetime.now().isoformat()}

if "status" in update_fields:
    is_valid, error_msg = self.validate_status(update_fields["status"])
    if not is_valid:
        return False, {"error": error_msg}
    update_data["status"] = update_fields["status"]

# PATTERN: Return tuple for success/error handling
return True, {"task": task_data}  # Success
return False, {"error": "Validation failed"}  # Error
```

### Why This Example

This demonstrates clean service layer architecture that:
- Separates validation from database operations
- Handles complex reordering logic correctly
- Supports flexible querying with performance optimization
- Returns consistent tuple format for error handling

---

## Example 3: Kanban Drag-and-Drop

**File**: `frontend/KanbanColumn.tsx`
**Source**: /Users/jon/source/vibes/repos/Archon/archon-ui-main/src/features/projects/tasks/components/KanbanColumn.tsx
**Relevance**: 10/10

### What to Mimic

- **useDrop Hook for Columns**: Accept task items and handle status transitions
  ```tsx
  const [{ isOver }, drop] = useDrop({
    accept: ItemTypes.TASK,
    drop: (item: { id: string; status: Task["status"] }) => {
      // Only trigger move if status changes
      if (item.status !== status) {
        onTaskMove(item.id, status);
      }
    },
    collect: (monitor) => ({
      isOver: !!monitor.isOver(), // Visual feedback
    }),
  });

  drop(ref); // Attach to column ref
  ```

- **Visual Feedback**: Apply styles based on drag state
  ```tsx
  <div
    className={cn(
      "flex flex-col h-full",
      "bg-gradient-to-b from-white/20 to-transparent",
      "backdrop-blur-sm",
      // Hover state
      isOver && "bg-gradient-to-b from-cyan-500/5 to-purple-500/5",
      isOver && "border-t-2 border-t-cyan-400/50",
      isOver && "shadow-[inset_0_2px_20px_rgba(34,211,238,0.15)]",
    )}
  >
  ```

- **Status-Based Theming**: Use utility functions for column colors
  ```tsx
  <h3 className={cn("font-mono text-sm", getColumnColor(status))}>
    {title}
  </h3>
  <div className={cn("h-[1px]", getColumnGlow(status))} />
  ```

- **Task Card Integration**: Map tasks with index for reordering
  ```tsx
  {tasks.map((task, index) => (
    <TaskCard
      key={task.id}
      task={task}
      index={index}  // Critical for reordering
      onTaskReorder={onTaskReorder}
      onTaskHover={onTaskHover}
    />
  ))}
  ```

### What to Adapt

- **Styling System**: Replace Tailwind glassmorphism with your design system
- **Color Utilities**: Implement getColumnColor/getColumnGlow for your theme
- **Task Card**: Create your own TaskCard component with drag source
- **Empty State**: Customize the "No tasks" message and styling

### What to Skip

- **Tron Aesthetic**: Glassmorphism effects if using different design
- **Archon-Specific Styling**: cn() utility and specific Tailwind patterns
- **Hover State Management**: If not showing hover indicators

### Pattern Highlights

```tsx
// KEY PATTERN: Only trigger status change when crossing columns
drop: (item: { id: string; status: Task["status"] }) => {
  if (item.status !== status) {
    onTaskMove(item.id, status);  // Status transition
  }
}

// PATTERN: Sticky header with glassmorphism
<div className={cn(
  "sticky top-0 z-10",
  "bg-gradient-to-b from-white/80 to-white/60",
  "backdrop-blur-md",
  "border-b border-gray-200/50"
)}>

// CRITICAL: Map with index for position tracking
{tasks.map((task, index) => (
  <TaskCard key={task.id} task={task} index={index} />
))}
```

### Why This Example

This demonstrates production-ready Kanban column implementation that:
- Properly handles status transitions via drag-and-drop
- Provides rich visual feedback during drag operations
- Integrates with position-based reordering
- Uses modern React patterns (hooks, refs)

---

## Example 4: TanStack Query Hooks

**File**: `frontend/useTaskQueries.ts`
**Source**: /Users/jon/source/vibes/repos/Archon/archon-ui-main/src/features/projects/tasks/hooks/useTaskQueries.ts
**Relevance**: 10/10

### What to Mimic

- **Query Key Factory**: Hierarchical, type-safe keys
  ```ts
  export const taskKeys = {
    all: ["tasks"] as const,
    lists: () => [...taskKeys.all, "list"] as const,
    detail: (id: string) => [...taskKeys.all, "detail", id] as const,
    byProject: (projectId: string) => ["projects", projectId, "tasks"] as const,
    counts: () => [...taskKeys.all, "counts"] as const,
  };
  ```

- **Smart Polling**: Visibility-aware refetch intervals
  ```ts
  const { refetchInterval } = useSmartPolling(2000); // 2s when active

  return useQuery<Task[]>({
    queryKey: projectId ? taskKeys.byProject(projectId) : DISABLED_QUERY_KEY,
    queryFn: () => taskService.getTasksByProject(projectId),
    refetchInterval, // Pauses when tab hidden
    refetchOnWindowFocus: true, // Cheap with ETags
    staleTime: STALE_TIMES.frequent,
  });
  ```

- **Optimistic Updates**: Create temporary entities with stable IDs
  ```ts
  onMutate: async (newData) => {
    // 1. Cancel in-flight queries
    await queryClient.cancelQueries({ queryKey: taskKeys.byProject(projectId) });

    // 2. Snapshot for rollback
    const previousTasks = queryClient.getQueryData(taskKeys.byProject(projectId));

    // 3. Create optimistic entity with nanoid
    const optimisticTask = createOptimisticEntity({
      ...newData,
      created_at: new Date().toISOString(),
    });

    // 4. Update cache
    queryClient.setQueryData(taskKeys.byProject(projectId), (old) =>
      [...(old || []), optimisticTask]
    );

    return { previousTasks, optimisticId: optimisticTask._localId };
  }
  ```

- **Error Rollback**: Restore previous state on failure
  ```ts
  onError: (error, variables, context) => {
    // Rollback to snapshot
    if (context?.previousTasks) {
      queryClient.setQueryData(
        taskKeys.byProject(variables.project_id),
        context.previousTasks
      );
    }

    showToast(`Failed: ${error.message}`, "error");
  }
  ```

- **Replace Optimistic**: Swap temp entity with server data
  ```ts
  onSuccess: (serverTask, variables, context) => {
    queryClient.setQueryData(
      taskKeys.byProject(variables.project_id),
      (tasks) => {
        const replaced = replaceOptimisticEntity(
          tasks,
          context?.optimisticId,
          serverTask
        );
        return removeDuplicateEntities(replaced);
      }
    );
  }
  ```

### What to Adapt

- **Query Keys**: Match your API structure (global vs scoped)
- **Polling Intervals**: Tune for your real-time requirements
- **Service Methods**: Point to your API client
- **Toast Library**: Replace useToast with your notification system
- **Optimistic Utils**: Adapt createOptimisticEntity to your entity shape

### What to Skip

- **Dual Nature Keys**: If tasks are only project-scoped
- **Counts Query**: If not showing aggregate counts
- **Complex Invalidation**: Simplify if not tracking related data

### Pattern Highlights

```ts
// CRITICAL: Cancel queries before optimistic update
await queryClient.cancelQueries({ queryKey: taskKeys.byProject(projectId) });

// PATTERN: Stable optimistic IDs with nanoid
const optimisticTask = createOptimisticEntity<Task>({
  ...newData,
  _localId: nanoid(), // Stable ID for replacement
  _optimistic: true,   // Flag for UI indicators
});

// PATTERN: Conditional invalidation
if (updates.status) {
  // Status changed - invalidate counts
  queryClient.invalidateQueries({ queryKey: taskKeys.counts() });
}

// PATTERN: Always refetch in onSettled for consistency
onSettled: () => {
  queryClient.invalidateQueries({ queryKey: taskKeys.byProject(projectId) });
}
```

### Why This Example

This demonstrates production-grade TanStack Query patterns that:
- Provides instant UI feedback with optimistic updates
- Handles errors gracefully with rollback
- Prevents race conditions with query cancellation
- Optimizes network usage with smart polling
- Maintains cache consistency across mutations

---

## Example 5: Docker Deployment

**File**: `docker/docker-compose.yml`
**Source**: /Users/jon/source/vibes/repos/Archon/docker-compose.yml
**Relevance**: 8/10

### What to Mimic

- **Health Check Dependencies**: Services wait for dependencies
  ```yaml
  archon-mcp:
    depends_on:
      archon-server:
        condition: service_healthy  # Wait for server health check
  ```

- **Health Check Patterns**: Different checks for different services
  ```yaml
  # HTTP health check
  healthcheck:
    test: ["CMD", "sh", "-c", 'python -c "import urllib.request; urllib.request.urlopen(''http://localhost:8181/health'')"']
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 40s

  # Socket health check
  healthcheck:
    test: ["CMD", "sh", "-c", 'python -c "import socket; s=socket.socket(); s.connect((''localhost'', 8051)); s.close()"']
  ```

- **Environment Variable Defaults**: Fallback values
  ```yaml
  ports:
    - "${ARCHON_SERVER_PORT:-8181}:${ARCHON_SERVER_PORT:-8181}"

  environment:
    - LOG_LEVEL=${LOG_LEVEL:-INFO}
    - AGENTS_ENABLED=${AGENTS_ENABLED:-false}
  ```

- **Hot Reload Volumes**: Mount source for development
  ```yaml
  volumes:
    - ./python/src:/app/src  # Source code
    - ./python/tests:/app/tests  # Tests
    - ./migration:/app/migration  # Migrations
  ```

- **Service Discovery**: Inter-service communication
  ```yaml
  environment:
    - API_SERVICE_URL=http://archon-server:${ARCHON_SERVER_PORT:-8181}
    - SERVICE_DISCOVERY_MODE=docker_compose

  networks:
    - app-network  # Custom bridge network
  ```

### What to Adapt

- **Service Names**: Replace archon-* with your project name
- **Port Numbers**: Choose your preferred ports
- **Build Contexts**: Update Dockerfile paths
- **Environment Variables**: Add your specific configuration
- **Volume Mounts**: Adjust to your directory structure

### What to Skip

- **Profile System**: If not using optional services
- **Service Discovery**: If using simple networking
- **host.docker.internal**: If not accessing host services

### Pattern Highlights

```yaml
# CRITICAL: Use health checks for startup ordering
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:3737"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s  # Important: give time to start

# PATTERN: Volume mounts for hot reload
volumes:
  - ./src:/app/src  # Code changes reload automatically

# PATTERN: Inter-service URLs using container names
environment:
  - API_SERVICE_URL=http://backend:8000
  - MCP_SERVICE_URL=http://mcp-server:8051

# PATTERN: Custom network for isolation
networks:
  app-network:
    driver: bridge
```

### Why This Example

This demonstrates production-ready Docker Compose setup that:
- Ensures services start in correct order
- Supports hot reload for development
- Handles inter-service communication
- Uses health checks for reliability
- Provides fallback defaults for configuration

---

## Example 6: Database Schema

**File**: `database/schema.sql`
**Source**: /Users/jon/source/vibes/repos/Archon/migration/complete_setup.sql
**Relevance**: 9/10

### What to Mimic

- **Position Tracking**: Integer field with composite index
  ```sql
  task_order INTEGER DEFAULT 0,

  -- Composite index for ordered queries
  CREATE INDEX idx_tasks_status_position
    ON archon_tasks(status, task_order);
  ```

- **Custom Enum Types**: Database-level validation
  ```sql
  CREATE TYPE task_status AS ENUM ('todo', 'doing', 'review', 'done');
  CREATE TYPE task_priority AS ENUM ('low', 'medium', 'high', 'critical');

  status task_status DEFAULT 'todo',
  priority task_priority DEFAULT 'medium' NOT NULL,
  ```

- **JSONB Fields**: Flexible metadata storage
  ```sql
  sources JSONB DEFAULT '[]'::jsonb,
  code_examples JSONB DEFAULT '[]'::jsonb,

  -- Optional GIN index for searching
  CREATE INDEX idx_tasks_sources_gin
    ON archon_tasks USING GIN (sources);
  ```

- **Soft Delete Pattern**: Archived fields
  ```sql
  archived BOOLEAN DEFAULT false,
  archived_at TIMESTAMPTZ NULL,
  archived_by TEXT NULL,

  -- Index with WHERE clause for performance
  CREATE INDEX idx_tasks_archived
    ON archon_tasks(archived)
    WHERE archived IS NOT NULL;
  ```

- **Automatic Timestamps**: Trigger for updated_at
  ```sql
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),

  CREATE OR REPLACE FUNCTION update_updated_at_column()
  RETURNS TRIGGER AS $$
  BEGIN
      NEW.updated_at = NOW();
      RETURN NEW;
  END;
  $$ LANGUAGE plpgsql;

  CREATE TRIGGER update_tasks_updated_at
      BEFORE UPDATE ON tasks
      FOR EACH ROW
      EXECUTE FUNCTION update_updated_at_column();
  ```

### What to Adapt

- **Enum Values**: Change status/priority for your workflow
- **JSONB Fields**: Adjust metadata structure
- **Indexes**: Add based on your query patterns
- **Foreign Keys**: Update table references

### What to Skip

- **parent_task_id**: If not supporting hierarchy
- **Soft delete**: If using hard delete
- **JSONB fields**: If storing metadata in separate tables

### Pattern Highlights

```sql
-- CRITICAL: Position reordering requires composite index
CREATE INDEX idx_tasks_status_position
  ON tasks(status, task_order);

-- Query pattern:
-- WHERE status = 'todo' ORDER BY task_order

-- PATTERN: Default values prevent NULL issues
status task_status DEFAULT 'todo',
assignee TEXT DEFAULT 'User' CHECK (assignee != ''),
task_order INTEGER DEFAULT 0,

-- PATTERN: CASCADE for data integrity
project_id UUID REFERENCES projects(id) ON DELETE CASCADE,

-- PATTERN: Efficient soft delete queries
WHERE archived IS NULL OR archived = false

-- With index:
CREATE INDEX ON tasks(archived) WHERE archived IS NOT NULL;
```

### Why This Example

This demonstrates robust database schema that:
- Supports drag-and-drop with position tracking
- Uses enums for type safety
- Provides flexible JSONB storage
- Implements soft delete pattern
- Auto-updates timestamps with triggers

---

## Usage Instructions

### Study Phase

1. **Read Each Example File**
   - Review the source attribution headers
   - Understand the context and relevance score
   - Note the specific patterns highlighted

2. **Focus on "What to Mimic" Sections**
   - These are the proven patterns to copy
   - Code snippets show exact implementations
   - Comments explain why each pattern works

3. **Review "What to Adapt" Guidance**
   - These are customization points
   - Adjust for your specific requirements
   - Maintain the core pattern while adapting details

4. **Note "What to Skip" Items**
   - Features specific to Archon
   - Optional complexity you may not need
   - Alternative approaches to consider

### Application Phase

1. **Start with Database Schema** (Example 6)
   - Set up PostgreSQL with task table
   - Create indexes for position tracking
   - Add triggers for timestamps

2. **Build Service Layer** (Example 2)
   - Implement validation methods
   - Add position reordering logic
   - Create list/get/update methods

3. **Create MCP Tools** (Example 1)
   - Implement find_tasks consolidated tool
   - Add manage_task for mutations
   - Include response optimization

4. **Build Frontend Queries** (Example 4)
   - Set up query key factories
   - Implement optimistic updates
   - Add smart polling

5. **Create Kanban UI** (Example 3)
   - Build KanbanColumn with useDrop
   - Add visual feedback for drag
   - Integrate TaskCard components

6. **Configure Docker** (Example 5)
   - Set up multi-service compose
   - Add health checks
   - Configure hot reload

### Testing Patterns

From extracted examples:

**Backend Tests** (task_service.py):
- Test validation methods separately
- Mock Supabase client
- Verify reordering logic with edge cases

**Frontend Tests** (useTaskQueries.ts):
- Mock service methods
- Test optimistic update rollback
- Verify query key generation

**Integration Tests**:
- Test MCP tools via HTTP
- Verify drag-and-drop updates database
- Check real-time polling behavior

---

## Pattern Summary

### Common Patterns Across Examples

1. **Consolidated Tools**: Reduce API surface with action-based operations
   - `find_tasks`: list/search/get in one tool
   - `manage_task`: create/update/delete with action param

2. **Optimistic Updates**: Instant UI feedback with rollback
   - Cancel in-flight queries
   - Create temp entities with stable IDs
   - Replace on success, rollback on error

3. **Position Tracking**: Support drag-and-drop reordering
   - `task_order` integer field
   - Composite index (status, position)
   - Increment logic to prevent conflicts

4. **Smart Polling**: Visibility-aware data freshness
   - Pause when tab hidden
   - Slow down when unfocused
   - ETag caching for bandwidth

5. **Type Safety**: End-to-end validation
   - Database enums (task_status, priority)
   - TypeScript types matching database
   - Service layer validation

### Anti-Patterns Observed

1. **❌ Hardcoded Stale Times**: Always use STALE_TIMES constants
2. **❌ Manual ETag Tracking**: Let browser handle HTTP caching
3. **❌ Prop Drilling**: Use TanStack Query cache, not props
4. **❌ N+1 Queries**: Use composite indexes and exclude_large_fields
5. **❌ Skipping Query Cancellation**: Always cancel before optimistic updates

---

## Integration with PRP

These examples should be:

1. **Referenced** in PRP "All Needed Context" section
   - Link to specific example files
   - Note relevance scores
   - Highlight key patterns to follow

2. **Studied** before implementation
   - Read all examples first
   - Understand pattern relationships
   - Note adaptation points

3. **Adapted** for the specific feature needs
   - Adjust enum values for workflow
   - Customize UI styling
   - Modify query patterns for API structure

4. **Extended** if additional patterns emerge
   - Add new examples as discovered
   - Document gotchas encountered
   - Update README with learnings

---

## Source Attribution

### From Archon

Primary source: `/Users/jon/source/vibes/repos/Archon/`

**MCP Layer**:
- task_tools.py: Consolidated MCP tools pattern
- Response optimization for AI consumption
- Structured error handling

**Backend Layer**:
- task_service.py: Service layer architecture
- Position reordering logic
- Validation patterns

**Frontend Layer**:
- KanbanColumn.tsx: react-dnd drag-and-drop
- useTaskQueries.ts: TanStack Query hooks
- Optimistic updates with rollback

**Infrastructure**:
- docker-compose.yml: Multi-service deployment
- complete_setup.sql: PostgreSQL schema

### From Feature Analysis

Secondary guidance: `prps/task_management_ui/planning/feature-analysis.md`

- 4-state workflow (todo → doing → review → done)
- Consolidated MCP pattern rationale
- HTTP polling vs WebSockets decision
- FastAPI + React tech stack choice

---

## Quality Assessment

- **Coverage**: 9/10 - All major patterns represented with working code
- **Relevance**: 9/10 - Examples directly applicable to task management UI
- **Completeness**: 9/10 - Examples are self-contained and runnable
- **Documentation**: 9/10 - Each example has clear guidance on usage

**Overall**: 9/10

---

**Generated**: 2025-10-06
**Feature**: task_management_ui
**Total Examples**: 6
**Source Quality**: Production code from Archon beta
