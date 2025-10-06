# Examples Curated: task_management_ui

## Summary

Extracted **6 working code examples** to the examples directory with comprehensive documentation. All files are **physically extracted** (not just referenced) from Archon's production codebase, demonstrating proven patterns for task management with MCP integration.

## Files Created

### 1. **mcp/task_tools.py** - MCP Tool Pattern
   - **Source**: Archon task_tools.py (374 lines)
   - **Pattern**: Consolidated MCP tools (find_tasks, manage_task)
   - **Key Patterns**:
     - Single tool for list/search/get operations
     - Response optimization (truncate, counts)
     - Action-based mutations (create/update/delete)
     - Structured error handling with MCPErrorFormatter
   - **Relevance**: 10/10

### 2. **backend/task_service.py** - Service Layer
   - **Source**: Archon task_service.py (300+ lines)
   - **Pattern**: Service layer with validation and async operations
   - **Key Patterns**:
     - Validation methods (status, assignee, priority)
     - Position reordering logic for drag-and-drop
     - Conditional field exclusion for performance
     - Keyword search across multiple fields
   - **Relevance**: 9/10

### 3. **frontend/KanbanColumn.tsx** - Drag-and-Drop UI
   - **Source**: Archon KanbanColumn.tsx (104 lines)
   - **Pattern**: react-dnd Kanban column with visual feedback
   - **Key Patterns**:
     - useDrop hook for column-level drop zones
     - Visual feedback during drag (isOver state)
     - Status-based color theming
     - TaskCard integration with reordering
   - **Relevance**: 10/10

### 4. **frontend/useTaskQueries.ts** - Data Fetching
   - **Source**: Archon useTaskQueries.ts (220 lines)
   - **Pattern**: TanStack Query v5 hooks with optimistic updates
   - **Key Patterns**:
     - Query key factories for cache management
     - Smart polling with visibility awareness
     - Optimistic updates with rollback on error
     - Proper invalidation after mutations
   - **Relevance**: 10/10

### 5. **docker/docker-compose.yml** - Deployment
   - **Source**: Archon docker-compose.yml (182 lines)
   - **Pattern**: Multi-service Docker Compose with health checks
   - **Key Patterns**:
     - Health check dependencies
     - Environment variable defaults
     - Hot reload volumes for development
     - Service discovery via container names
   - **Relevance**: 8/10

### 6. **database/schema.sql** - Database Schema
   - **Source**: Archon complete_setup.sql (120+ lines)
   - **Pattern**: PostgreSQL schema with position tracking
   - **Key Patterns**:
     - Position tracking with composite index
     - Custom enum types (task_status, task_priority)
     - JSONB fields for metadata
     - Soft delete with archived flags
     - Automatic timestamp triggers
   - **Relevance**: 9/10

### 7. **README.md** - Comprehensive Guide
   - **Content**: Usage instructions, pattern highlights, integration guidance
   - **Sections**:
     - What to Mimic (specific code patterns)
     - What to Adapt (customization points)
     - What to Skip (optional features)
     - Pattern Highlights (critical code snippets)
     - Why This Example (rationale)
   - **Length**: ~800 lines of detailed documentation

## Key Patterns Extracted

### MCP Layer
- **Consolidated Tools**: `find_tasks` (list/search/get), `manage_task` (create/update/delete)
- **Response Optimization**: Truncate descriptions to 1000 chars, replace arrays with counts
- **Error Handling**: MCPErrorFormatter with structured error types and suggestions

### Backend Layer
- **Service Architecture**: Validation → Business Logic → Database
- **Position Reordering**: Increment existing tasks when inserting at specific position
- **Performance**: Conditional field exclusion, keyword search with OR filters

### Frontend Layer
- **Drag-and-Drop**: react-dnd useDrop for columns, visual feedback on hover
- **Data Fetching**: TanStack Query with optimistic updates and rollback
- **Smart Polling**: Visibility-aware intervals (pause when hidden, slow when unfocused)

### Database Layer
- **Position Tracking**: `task_order` INTEGER with composite index (status, position)
- **Type Safety**: Custom enums at database level
- **Flexibility**: JSONB for sources/code_examples arrays
- **Audit Trail**: Soft delete with archived_at, archived_by

### Infrastructure
- **Docker Deployment**: Multi-service with health checks
- **Hot Reload**: Volume mounts for development
- **Service Discovery**: Container name-based URLs

## Recommendations for PRP Assembly

### 1. Reference Examples in "All Needed Context"

```markdown
## Code Examples

Working code examples extracted from Archon:
- **MCP Tools**: `prps/task_management_ui/examples/mcp/task_tools.py`
- **Service Layer**: `prps/task_management_ui/examples/backend/task_service.py`
- **Kanban UI**: `prps/task_management_ui/examples/frontend/KanbanColumn.tsx`
- **Query Hooks**: `prps/task_management_ui/examples/frontend/useTaskQueries.ts`
- **Docker Setup**: `prps/task_management_ui/examples/docker/docker-compose.yml`
- **Database Schema**: `prps/task_management_ui/examples/database/schema.sql`

Full documentation: `prps/task_management_ui/examples/README.md`
```

### 2. Include Pattern Highlights in "Implementation Blueprint"

**MCP Tools Pattern**:
```python
# Consolidated tool: find_tasks handles list/search/get
@mcp.tool()
async def find_tasks(
    task_id: str | None = None,  # Get specific
    query: str | None = None,     # Search
    filter_by: str | None = None  # Filter
) -> str:
    if task_id:
        # Return full details for single task
    else:
        # Return optimized list (truncated, counts)
```

**Position Reordering Pattern**:
```python
# When inserting at position N:
# 1. Get tasks with position >= N
# 2. Increment each by 1
# 3. Insert new task at N
existing_tasks = get_tasks_gte_position(project_id, status, position)
for task in existing_tasks:
    update_position(task.id, task.position + 1)
```

**Optimistic Update Pattern**:
```ts
// 1. Cancel in-flight queries
await queryClient.cancelQueries({ queryKey: taskKeys.byProject(projectId) });

// 2. Snapshot for rollback
const previous = queryClient.getQueryData(taskKeys.byProject(projectId));

// 3. Create optimistic entity with stable ID
const optimistic = createOptimisticEntity({ ...data });

// 4. Update cache
queryClient.setQueryData(taskKeys.byProject(projectId), [...old, optimistic]);

// 5. Rollback on error, replace on success
```

### 3. Direct Implementer to Study Examples

**Pre-Implementation Checklist**:
- [ ] Read `examples/README.md` for all patterns
- [ ] Study MCP consolidation pattern (task_tools.py)
- [ ] Review position reordering logic (task_service.py)
- [ ] Understand optimistic updates (useTaskQueries.ts)
- [ ] Review drag-and-drop setup (KanbanColumn.tsx)
- [ ] Check database schema (schema.sql)

### 4. Validation: Can Code Be Adapted from Examples?

**Yes, with these adaptations**:

| Component | Example File | Adaptation Needed |
|-----------|--------------|-------------------|
| MCP Tools | task_tools.py | Rename tools, adjust status values |
| Service Layer | task_service.py | Replace Supabase with chosen DB client |
| Kanban UI | KanbanColumn.tsx | Adjust styling, customize TaskCard |
| Query Hooks | useTaskQueries.ts | Update query keys, service imports |
| Docker Setup | docker-compose.yml | Rename services, adjust ports |
| Database | schema.sql | Modify enums, adjust fields |

**Key Decisions**:
- Keep: Consolidated MCP pattern, position reordering, optimistic updates
- Adapt: Status values (todo/doing/review/done), priority levels, JSONB fields
- Skip: Archon-specific features (sources, code_examples), soft delete if not needed

## Quality Assessment

### Coverage
**9/10** - All major patterns covered with working code

Areas covered:
- ✅ MCP tool consolidation with response optimization
- ✅ Service layer with validation and reordering
- ✅ Drag-and-drop Kanban UI with visual feedback
- ✅ TanStack Query with optimistic updates
- ✅ Docker deployment with health checks
- ✅ PostgreSQL schema with position tracking

Missing (acceptable):
- Frontend routing (feature-specific)
- Authentication (deferred to post-MVP)
- Test examples (can reference Archon tests directly)

### Relevance
**9/10** - Examples directly applicable to task management UI

All patterns match requirements:
- ✅ 4-state workflow (todo → doing → review → done)
- ✅ MCP integration for AI assistants
- ✅ Kanban board with drag-and-drop
- ✅ FastAPI backend + React frontend
- ✅ Docker Compose deployment
- ✅ PostgreSQL database

Minor gaps:
- List view examples (can adapt from Archon list components)
- Markdown editor (simple textarea + react-markdown shown in Archon)

### Completeness
**9/10** - Examples are self-contained and near-runnable

Each example includes:
- ✅ Full source code with comments
- ✅ Source attribution headers
- ✅ Pattern explanation in README
- ✅ "What to Mimic/Adapt/Skip" guidance
- ✅ Critical code snippet highlights

To make fully runnable:
- Add imports/dependencies (shown in source)
- Configure environment variables (.env.example in Archon)
- Connect to database (schema provided)

### Overall Quality: 9/10

**Strengths**:
- Working production code from Archon beta
- Comprehensive documentation with usage guidance
- Clear pattern highlights and adaptation points
- All 6 layers covered (MCP, backend, frontend, database, docker)

**Minor Gaps**:
- No test examples (reference Archon test suite)
- No .env.example (copy from Archon)
- No list view component (adapt from Archon TaskList)

**Recommendation**: Examples are ready for PRP integration. Implementer should:
1. Study all 6 example files
2. Read pattern highlights in README
3. Copy and adapt code for task management UI
4. Reference Archon codebase for gaps (tests, config)

---

**Generated**: 2025-10-06
**Feature**: task_management_ui
**Total Examples**: 6 code files + 1 comprehensive README
**Source Quality**: Production code from Archon
**Extraction Method**: Physical file extraction with source attribution
**Ready for PRP**: ✅ Yes
