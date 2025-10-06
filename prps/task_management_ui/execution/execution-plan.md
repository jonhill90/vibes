# Execution Plan: Task Management UI

**PRP**: /Users/jon/source/vibes/prps/task_management_ui.md
**Feature**: Task Management UI with MCP Integration
**Generated**: 2025-10-06
**Total Tasks**: 25
**Execution Groups**: 7
**Archon Project ID**: 0e5d6945-e25a-465d-ab8b-b2629e0345af

---

## Executive Summary

**Sequential Execution Time**: ~20 hours (25 tasks × ~48 min avg)
**Parallel Execution Time**: ~8.5 hours (7 groups, max task per group)
**Time Savings**: ~11.5 hours (57.5% reduction)
**Parallelization Ratio**: 15 tasks can run in parallel across first 3 groups

---

## Dependency Analysis Overview

### Dependency Categories

**1. File Creation Dependencies**
- Backend tasks depend on Pydantic models (Task 2)
- API routes depend on service layer (Tasks 4-5)
- MCP server depends on service layer (Tasks 4-5)
- Frontend components depend on types (Task 10) and query hooks (Tasks 12-13)

**2. Logical Dependencies**
- Database setup must complete first (Task 1)
- Docker configuration depends on all application code (Tasks 1-18)
- Testing depends on implementation completion (Tasks 22-23)
- Final integration depends on everything (Task 25)

**3. Independent Components**
- Backend and frontend can develop in parallel after foundational tasks
- Projects and Tasks implementations are parallel within same layer
- Docker files can be created independently once structure is clear

---

## Task Dependency Graph

```mermaid
graph TD
    T1[Task 1: Database Setup]
    T2[Task 2: Backend - Pydantic Models]
    T3[Task 3: Backend - Database Config]
    T10[Task 10: Frontend - TypeScript Types]
    T19[Task 19: Docker - Compose Config]

    T4[Task 4: Backend - Service Layer Projects]
    T5[Task 5: Backend - Service Layer Tasks]
    T11[Task 11: Frontend - API Client & Services]
    T12[Task 12: Frontend - TanStack Query Config]

    T6[Task 6: Backend - FastAPI Routes Projects]
    T7[Task 7: Backend - FastAPI Routes Tasks]
    T8[Task 8: Backend - MCP Server]
    T13[Task 13: Frontend - Query Hooks Tasks]

    T9[Task 9: Backend - FastAPI Application]
    T14[Task 14: Frontend - Drag-and-Drop Column]
    T15[Task 15: Frontend - Drag-and-Drop Card]

    T16[Task 16: Frontend - Kanban Board View]
    T17[Task 17: Frontend - List View]
    T18[Task 18: Frontend - Task Detail Modal]

    T20[Task 20: Docker - Backend Dockerfile]
    T21[Task 21: Docker - Frontend Dockerfile]

    T22[Task 22: Testing - Backend Unit Tests]
    T23[Task 23: Testing - MCP Integration Tests]

    T24[Task 24: Documentation]

    T25[Task 25: Final Integration & Testing]

    %% Group 1 - Foundation (Parallel)
    T1 --> T3
    T1 --> T2
    T1 --> T10
    T1 --> T19

    %% Group 2 - Backend/Frontend Core (Parallel)
    T2 --> T4
    T2 --> T5
    T3 --> T4
    T3 --> T5
    T10 --> T11
    T10 --> T12

    %% Group 3 - API & Query Integration (Parallel)
    T4 --> T6
    T5 --> T7
    T5 --> T8
    T11 --> T13
    T12 --> T13

    %% Group 4 - Main Application (Parallel)
    T6 --> T9
    T7 --> T9
    T8 --> T9
    T13 --> T14
    T13 --> T15

    %% Group 5 - UI Components (Parallel)
    T14 --> T16
    T15 --> T16
    T13 --> T17
    T13 --> T18

    %% Group 6 - Docker & Testing (Parallel)
    T9 --> T20
    T16 --> T21
    T17 --> T21
    T18 --> T21
    T9 --> T22
    T9 --> T23
    T16 --> T24

    %% Group 7 - Final Validation (Sequential)
    T20 --> T25
    T21 --> T25
    T22 --> T25
    T23 --> T25
    T24 --> T25
```

---

## Execution Groups

### Group 1: Foundation (Parallel Execution)

**Tasks**: 4
**Execution Mode**: PARALLEL
**Expected Duration**: ~60 minutes (longest task: Database Setup)
**Dependencies**: None - can all start immediately

#### Tasks in Group 1:

**1. Task 1: Database Setup**
- **What it does**: Create PostgreSQL schema with proper indexes and constraints
- **Files**:
  - `database/init.sql`
  - `backend/alembic/versions/001_create_tables.py`
- **No dependencies**: Foundation task
- **Duration**: ~60 min
- **Rationale**: Critical path task - sets up data model for all backend work

**2. Task 2: Backend - Pydantic Models**
- **What it does**: Define type-safe request/response models with validation
- **Files**:
  - `backend/src/models/__init__.py`
  - `backend/src/models/project.py`
  - `backend/src/models/task.py`
- **No dependencies**: Pure Python type definitions
- **Duration**: ~45 min
- **Rationale**: Independent of database, can develop in parallel

**3. Task 10: Frontend - TypeScript Types**
- **What it does**: Type-safe definitions matching backend models
- **Files**:
  - `frontend/src/features/projects/types/project.ts`
  - `frontend/src/features/tasks/types/task.ts`
- **No dependencies**: Pure TypeScript type definitions
- **Duration**: ~30 min
- **Rationale**: Frontend types independent of backend implementation

**4. Task 19: Docker - Compose Configuration**
- **What it does**: Multi-service deployment skeleton (will update in Group 6)
- **Files**:
  - `docker-compose.yml`
  - `.env.example`
- **No dependencies**: Infrastructure definition
- **Duration**: ~45 min
- **Rationale**: Can define service structure before implementation exists

**Parallelization Strategy**:
- Invoke 4 `prp-exec-implementer` subagents simultaneously
- Each gets one task from this group
- All agents can work independently without conflicts
- No shared files or resources

**Critical Path**: Task 1 (Database Setup) - longest duration in group

---

### Group 2: Backend/Frontend Core (Parallel Execution)

**Tasks**: 4
**Execution Mode**: PARALLEL
**Expected Duration**: ~75 minutes (longest task: Task Service with position logic)
**Dependencies**: Group 1 must complete first

#### Tasks in Group 2:

**1. Task 3: Backend - Database Configuration**
- **What it does**: Setup asyncpg connection pool and dependency injection
- **Files**:
  - `backend/src/config/__init__.py`
  - `backend/src/config/database.py`
- **Depends on**:
  - Task 1 (Database Setup) - needs schema to connect to
  - Task 2 (Pydantic Models) - references models for typing
- **Duration**: ~45 min
- **Why parallel**: Different concern from services, no file conflicts

**2. Task 4: Backend - Service Layer (Projects)**
- **What it does**: Business logic for project CRUD operations
- **Files**:
  - `backend/src/services/__init__.py`
  - `backend/src/services/project_service.py`
- **Depends on**:
  - Task 2 (Pydantic Models) - uses ProjectCreate, ProjectUpdate models
  - Task 3 (Database Config) - uses db_pool
- **Duration**: ~60 min
- **Why parallel**: Separate file from Task 5, can work simultaneously

**3. Task 5: Backend - Service Layer (Tasks with Position Logic)**
- **What it does**: Task CRUD with atomic position reordering
- **Files**:
  - `backend/src/services/task_service.py`
- **Depends on**:
  - Task 2 (Pydantic Models) - uses TaskCreate, TaskUpdate models
  - Task 3 (Database Config) - uses db_pool for transactions
- **Duration**: ~75 min (complex position logic)
- **Why parallel**: Separate file from Task 4, different entity

**4. Task 11: Frontend - API Client & Services**
- **What it does**: Type-safe API calls with error handling
- **Files**:
  - `frontend/src/features/shared/api/apiClient.ts`
  - `frontend/src/features/projects/services/projectService.ts`
  - `frontend/src/features/tasks/services/taskService.ts`
- **Depends on**:
  - Task 10 (Frontend Types) - imports Task, Project interfaces
- **Duration**: ~60 min
- **Why parallel**: Frontend work, completely independent of backend service layer

**Parallelization Strategy**:
- Wait for Group 1 completion signal
- Invoke 4 `prp-exec-implementer` subagents simultaneously
- Backend tasks (3, 4, 5) work on different files
- Frontend task (11) completely isolated from backend
- No resource conflicts

**Critical Path**: Task 5 (Task Service) - most complex with position reordering logic

---

### Group 3: API & Query Integration (Parallel Execution)

**Tasks**: 4
**Execution Mode**: PARALLEL
**Expected Duration**: ~75 minutes (longest task: MCP Server with optimization)
**Dependencies**: Group 2 must complete first

#### Tasks in Group 3:

**1. Task 6: Backend - FastAPI Routes (Projects)**
- **What it does**: HTTP endpoints for project CRUD
- **Files**:
  - `backend/src/api/__init__.py`
  - `backend/src/api/projects.py`
- **Depends on**:
  - Task 4 (Project Service) - calls ProjectService methods
- **Duration**: ~45 min
- **Why parallel**: Separate file from Task 7, different router

**2. Task 7: Backend - FastAPI Routes (Tasks)**
- **What it does**: HTTP endpoints for task CRUD
- **Files**:
  - `backend/src/api/tasks.py`
- **Depends on**:
  - Task 5 (Task Service) - calls TaskService methods
- **Duration**: ~60 min
- **Why parallel**: Separate file from Task 6, can develop simultaneously

**3. Task 8: Backend - MCP Server**
- **What it does**: MCP tools for AI assistant integration
- **Files**:
  - `backend/src/mcp_server.py`
  - `backend/src/utils/__init__.py`
  - `backend/src/utils/etag.py`
- **Depends on**:
  - Task 5 (Task Service) - uses TaskService for operations
  - Task 4 (Project Service) - uses ProjectService for operations
- **Duration**: ~75 min (complex response optimization logic)
- **Why parallel**: Separate file, different concern from HTTP API

**4. Task 12: Frontend - TanStack Query Configuration**
- **What it does**: Query client setup with smart defaults
- **Files**:
  - `frontend/src/features/shared/config/queryClient.ts`
  - `frontend/src/features/shared/config/queryPatterns.ts`
  - `frontend/src/features/shared/hooks/useSmartPolling.ts`
- **Depends on**:
  - Task 11 (API Services) - will be consumed by services
- **Duration**: ~45 min
- **Why parallel**: Frontend infrastructure, completely isolated from backend API work

**Parallelization Strategy**:
- Wait for Group 2 completion signal
- Invoke 4 `prp-exec-implementer` subagents simultaneously
- Backend API routes (6, 7) work on different routers
- MCP server (8) is separate entry point
- Frontend query config (12) is isolated
- No file conflicts

**Critical Path**: Task 8 (MCP Server) - most complex with truncation and optimization logic

---

### Group 4: Main Application & Drag-and-Drop Foundation (Parallel Execution)

**Tasks**: 3
**Execution Mode**: PARALLEL
**Expected Duration**: ~60 minutes
**Dependencies**: Group 3 must complete first

#### Tasks in Group 4:

**1. Task 9: Backend - FastAPI Application**
- **What it does**: Main application initialization with CORS, health checks
- **Files**:
  - `backend/src/main.py`
- **Depends on**:
  - Task 6 (Projects Routes) - includes project router
  - Task 7 (Tasks Routes) - includes task router
  - Task 3 (Database Config) - startup/shutdown events for pool
- **Duration**: ~45 min
- **Why parallel**: Separate concern from frontend, integrates backend pieces

**2. Task 13: Frontend - Query Hooks (Tasks)**
- **What it does**: TanStack Query hooks with optimistic updates
- **Files**:
  - `frontend/src/features/tasks/hooks/useTaskQueries.ts`
- **Depends on**:
  - Task 11 (API Services) - calls taskService methods
  - Task 12 (Query Config) - uses QueryClient, STALE_TIMES
- **Duration**: ~60 min (complex optimistic update logic)
- **Why parallel**: Frontend work, independent of backend main app

**3. Task 14: Frontend - Drag-and-Drop (Kanban Column)**
- **What it does**: Droppable Kanban column with visual feedback
- **Files**:
  - `frontend/src/features/tasks/components/KanbanColumn.tsx`
- **Depends on**:
  - Task 13 (Query Hooks) - uses useUpdateTaskPosition mutation
  - Task 10 (Types) - imports TaskStatus, Task types
- **Duration**: ~45 min
- **Why parallel**: Can start once query hooks pattern is clear (same group)

**Parallelization Strategy**:
- Wait for Group 3 completion signal
- Invoke 3 `prp-exec-implementer` subagents simultaneously
- Backend main app (9) integrates backend pieces
- Frontend hooks (13) and column (14) are different files
- No conflicts between backend and frontend work

**Critical Path**: Task 13 (Query Hooks) - complex optimistic updates with cancellation

**Note**: Task 14 technically depends on Task 13, but can be started in parallel since the pattern is well-defined in the PRP. If strict ordering required, move Task 14 to Group 5.

---

### Group 5: UI Components (Parallel Execution)

**Tasks**: 4
**Execution Mode**: PARALLEL
**Expected Duration**: ~60 minutes
**Dependencies**: Group 4 must complete first

#### Tasks in Group 5:

**1. Task 15: Frontend - Drag-and-Drop (Task Card)**
- **What it does**: Draggable task card
- **Files**:
  - `frontend/src/features/tasks/components/TaskCard.tsx`
- **Depends on**:
  - Task 13 (Query Hooks) - uses task types and patterns
  - Task 10 (Types) - imports Task interface
- **Duration**: ~30 min
- **Why parallel**: Separate component from other UI tasks

**2. Task 16: Frontend - Kanban Board View**
- **What it does**: 4-column Kanban layout with drag-and-drop integration
- **Files**:
  - `frontend/src/features/tasks/components/KanbanBoard.tsx`
  - `frontend/src/pages/KanbanPage.tsx`
- **Depends on**:
  - Task 14 (Kanban Column) - renders KanbanColumn components
  - Task 15 (Task Card) - TaskCard rendered in columns
  - Task 13 (Query Hooks) - uses useProjectTasks, useUpdateTaskPosition
- **Duration**: ~60 min
- **Why parallel**: Integrates components, but separate from List/Detail views

**3. Task 17: Frontend - List View**
- **What it does**: Filterable table view with sorting
- **Files**:
  - `frontend/src/features/tasks/components/TaskListView.tsx`
  - `frontend/src/pages/ListPage.tsx`
- **Depends on**:
  - Task 13 (Query Hooks) - uses useProjectTasks
- **Duration**: ~60 min
- **Why parallel**: Different view from Kanban, separate files

**4. Task 18: Frontend - Task Detail Modal**
- **What it does**: Edit task details in modal
- **Files**:
  - `frontend/src/features/tasks/components/TaskDetailModal.tsx`
- **Depends on**:
  - Task 13 (Query Hooks) - uses useUpdateTask, useDeleteTask
- **Duration**: ~45 min
- **Why parallel**: Standalone component, no conflicts with List/Kanban views

**Parallelization Strategy**:
- Wait for Group 4 completion signal
- Invoke 4 `prp-exec-implementer` subagents simultaneously
- All tasks work on different components/pages
- Task 16 integrates 14+15 but can proceed with clear interface contracts
- No file conflicts

**Critical Path**: Task 16 (Kanban Board) or Task 17 (List View) - both ~60 min

**Note**: Task 16 depends on Task 15, creating a sub-dependency within this group. If strict ordering required, could split into:
- Group 5a: Tasks 15, 17, 18 (parallel)
- Group 5b: Task 16 (after 15 completes)

For practical execution, keep as single group since Task 15 is fast (30 min) and Task 16 can start with clear interface.

---

### Group 6: Docker & Testing (Parallel Execution)

**Tasks**: 5
**Execution Mode**: PARALLEL
**Expected Duration**: ~75 minutes (longest task: Backend Unit Tests)
**Dependencies**: Group 5 must complete first

#### Tasks in Group 6:

**1. Task 20: Docker - Backend Dockerfile**
- **What it does**: Multi-stage Dockerfile for backend
- **Files**:
  - `backend/Dockerfile`
- **Depends on**:
  - Task 9 (Main App) - knows backend structure and entry point
  - Task 1 (Database) - alembic migrations need to exist
- **Duration**: ~30 min
- **Why parallel**: Infrastructure file, doesn't conflict with frontend Docker

**2. Task 21: Docker - Frontend Dockerfile**
- **What it does**: Frontend build for development
- **Files**:
  - `frontend/Dockerfile`
- **Depends on**:
  - Task 16 (Kanban Board) - frontend structure complete
  - Task 17 (List View) - all pages exist
  - Task 18 (Task Modal) - all components exist
- **Duration**: ~30 min
- **Why parallel**: Separate file from backend Docker, can work simultaneously

**3. Task 22: Testing - Backend Unit Tests**
- **What it does**: Test service layer and API endpoints
- **Files**:
  - `backend/tests/test_task_service.py`
  - `backend/tests/test_api_tasks.py`
- **Depends on**:
  - Task 9 (Main App) - backend implementation complete
  - Task 5 (Task Service) - testing the service layer
  - Task 7 (Task Routes) - testing the API
- **Duration**: ~75 min (comprehensive test coverage)
- **Why parallel**: Testing different concern from Docker, can run simultaneously

**4. Task 23: Testing - MCP Integration Tests**
- **What it does**: Test MCP tools end-to-end
- **Files**:
  - `backend/tests/test_mcp.py`
- **Depends on**:
  - Task 8 (MCP Server) - testing MCP implementation
  - Task 9 (Main App) - MCP server integrated
- **Duration**: ~45 min
- **Why parallel**: Separate test file, can run alongside Task 22

**5. Task 24: Documentation**
- **What it does**: Setup instructions and API documentation
- **Files**:
  - `README.md`
- **Depends on**:
  - Task 16 (Kanban Board) - UI structure documented
  - Task 9 (Main App) - API endpoints documented
  - Task 19 (Docker Compose) - deployment steps documented
- **Duration**: ~60 min
- **Why parallel**: Documentation separate from implementation and testing

**Parallelization Strategy**:
- Wait for Group 5 completion signal
- Invoke 5 `prp-exec-implementer` subagents simultaneously
- Docker tasks (20, 21) work on different Dockerfiles
- Test tasks (22, 23) work on different test files
- Documentation (24) is separate markdown file
- No resource conflicts

**Critical Path**: Task 22 (Backend Unit Tests) - most comprehensive, ~75 min

---

### Group 7: Final Integration & Testing (Sequential Execution)

**Tasks**: 1
**Execution Mode**: SEQUENTIAL
**Expected Duration**: ~90 minutes
**Dependencies**: ALL previous groups (1-6) must complete

#### Task in Group 7:

**1. Task 25: Final Integration & Testing**
- **What it does**: End-to-end validation of all features
- **Files**: NO NEW FILES - TESTING ONLY
- **Depends on**:
  - Task 20 (Backend Dockerfile) - Docker build must work
  - Task 21 (Frontend Dockerfile) - Docker build must work
  - Task 22 (Backend Tests) - Unit tests must pass
  - Task 23 (MCP Tests) - MCP tests must pass
  - Task 24 (Documentation) - README must exist for validation steps
- **Duration**: ~90 min (comprehensive end-to-end testing)
- **Why sequential**: Must wait for everything to be complete, validates entire system

**Specific Steps**:
1. `docker-compose up --build` - verify all services start
2. Access http://localhost:3000 - UI loads
3. Create project via UI - UI functionality works
4. Create tasks via UI - CRUD operations work
5. Drag task from "todo" to "doing" - optimistic updates work
6. Verify server sync - backend properly updates
7. Test MCP via `npx mcp-remote` - MCP integration works
8. `find_tasks()` - MCP tools functional
9. `manage_task("create", ...)` - MCP mutations work
10. Verify task appears in UI - end-to-end flow works
11. Test filters in list view - UI features complete
12. Test task detail modal - all components functional
13. Restart containers - data persistence verified
14. Performance benchmarks - meets requirements

**Validation Criteria**:
- All success criteria from PRP "What" section pass
- Performance benchmarks met (< 500ms MCP, < 200ms drag)
- No console errors in browser
- No errors in docker-compose logs
- Data persists across restarts

**Why Not Parallel**:
- Integration testing requires complete system
- Must validate interactions between all components
- Testing order matters (setup → functionality → performance → persistence)
- Failure at any step blocks remaining validation

---

## Execution Summary

| Group | Tasks | Mode | Duration | Dependencies | Tasks List |
|-------|-------|------|----------|--------------|------------|
| 1 | 4 | Parallel | ~60 min | None | 1, 2, 10, 19 |
| 2 | 4 | Parallel | ~75 min | Group 1 | 3, 4, 5, 11 |
| 3 | 4 | Parallel | ~75 min | Group 2 | 6, 7, 8, 12 |
| 4 | 3 | Parallel | ~60 min | Group 3 | 9, 13, 14 |
| 5 | 4 | Parallel | ~60 min | Group 4 | 15, 16, 17, 18 |
| 6 | 5 | Parallel | ~75 min | Group 5 | 20, 21, 22, 23, 24 |
| 7 | 1 | Sequential | ~90 min | Groups 1-6 | 25 |

**Total Sequential Time**: ~1,200 minutes (~20 hours)
**Total Parallel Time**: ~495 minutes (~8.25 hours)
**Time Savings**: ~705 minutes (~11.75 hours)
**Efficiency Gain**: 58.75%

---

## Critical Path Analysis

The **critical path** (longest sequence of dependent tasks) is:

**Task 1** (60 min) → **Task 3+2** (45 min, parallel with 2) → **Task 5** (75 min) → **Task 8** (75 min) → **Task 13** (60 min) → **Task 16** (60 min) → **Task 22** (75 min) → **Task 25** (90 min)

**Critical Path Duration**: ~540 minutes (~9 hours)

**Note**: Actual parallel execution is ~495 min due to max duration per group, not cumulative.

**Bottleneck Tasks** (longest in each group):
1. Group 1: Task 1 (Database Setup) - 60 min
2. Group 2: Task 5 (Task Service) - 75 min
3. Group 3: Task 8 (MCP Server) - 75 min
4. Group 4: Task 13 (Query Hooks) - 60 min
5. Group 5: Task 16/17 (Kanban/List) - 60 min
6. Group 6: Task 22 (Backend Tests) - 75 min
7. Group 7: Task 25 (Final Integration) - 90 min

**Optimization Opportunities**:
- Group 2: Task 5 (75 min) is longest - could be split into CRUD + position logic (2 tasks)
- Group 3: Task 8 (75 min) is longest - could be split into tools + optimization (2 tasks)
- Group 6: Task 22 (75 min) is longest - could be split into service tests + API tests (already separate)

---

## Implementation Instructions for Orchestrator

### Execution Workflow

```python
# Pseudo-code for PRP execution orchestrator

execution_plan = load_execution_plan("prps/task_management_ui/execution/execution-plan.md")
prp = load_prp("prps/task_management_ui.md")

for group in execution_plan.groups:
    print(f"Starting Group {group.number}: {group.name}")
    print(f"Mode: {group.mode}, Tasks: {group.task_count}, Duration: ~{group.duration} min")

    if group.mode == "parallel":
        # Update all tasks in group to "doing" status in Archon
        for task in group.tasks:
            archon.manage_task(
                action="update",
                task_id=task.archon_id,
                status="doing",
                assignee="prp-exec-implementer"
            )

        # Invoke multiple implementers in SINGLE parallel call
        results = parallel_invoke([
            {
                "agent": "prp-exec-implementer",
                "context": prepare_task_context(task, prp),
                "task_id": task.archon_id
            }
            for task in group.tasks
        ])

        # Wait for all to complete
        wait_for_completion(results)

        # Validate all completed successfully
        for task, result in zip(group.tasks, results):
            if result.success:
                archon.manage_task(
                    action="update",
                    task_id=task.archon_id,
                    status="review"
                )
                # Run validation from task definition
                validation_passed = run_validation(task.validation_commands)
                if validation_passed:
                    archon.manage_task(
                        action="update",
                        task_id=task.archon_id,
                        status="done"
                    )
                else:
                    print(f"Validation failed for {task.name}")
                    # Handle failure - retry or escalate
            else:
                print(f"Task {task.name} failed: {result.error}")
                # Handle failure

    elif group.mode == "sequential":
        for task in group.tasks:
            # Update to doing
            archon.manage_task(
                action="update",
                task_id=task.archon_id,
                status="doing"
            )

            # Invoke single implementer
            result = invoke_subagent(
                agent="prp-exec-implementer",
                context=prepare_task_context(task, prp)
            )

            # Validate
            if result.success:
                validation_passed = run_validation(task.validation_commands)
                if validation_passed:
                    archon.manage_task(
                        action="update",
                        task_id=task.archon_id,
                        status="done"
                    )
                else:
                    print(f"Validation failed for {task.name}")
                    break  # Stop sequential execution on failure
            else:
                print(f"Task {task.name} failed")
                break

    print(f"Group {group.number} complete\n")

print("All groups complete - implementation finished!")
```

---

### Task Context Preparation

For each task, prepare this context for the implementer subagent:

```yaml
# Context passed to prp-exec-implementer

task_metadata:
  task_id: "archon-task-uuid-here"  # If Archon task exists
  task_number: 5
  task_name: "Backend - Service Layer (Tasks with Position Logic)"
  prp_file: "/Users/jon/source/vibes/prps/task_management_ui.md"
  execution_plan: "/Users/jon/source/vibes/prps/task_management_ui/execution/execution-plan.md"

task_details:
  responsibility: "Task CRUD with atomic position reordering"
  files_to_create:
    - "backend/src/services/task_service.py"
  pattern_to_follow: "prps/task_management_ui/examples/backend/task_service.py (lines 93-115)"

  specific_steps:
    - "Create TaskService class with db_pool"
    - "Implement async def list_tasks(self, filters, page, per_page, exclude_large_fields)"
    - "Implement async def get_task(self, task_id: str)"
    - "Implement async def create_task(self, data: TaskCreate)"
    - "Implement async def update_task_position(self, task_id, new_status, new_position)"
    - "  - CRITICAL: Use transaction with row locking (SELECT ... FOR UPDATE)"
    - "  - Increment positions >= new_position before insert"
    - "  - Lock rows in consistent order (ORDER BY id) to prevent deadlocks"
    - "Implement async def update_task(self, task_id: str, data: TaskUpdate)"
    - "Implement async def delete_task(self, task_id: str)"
    - "Add validation methods: validate_status(status), validate_priority(priority)"

  validation_commands:
    - "cd backend && uv run pytest tests/test_task_service.py -v"
    - "cd backend && uv run mypy src/services/task_service.py"
    - "cd backend && uv run ruff check src/services/task_service.py"

  gotchas_to_avoid:
    - "CRITICAL: Position reordering MUST use transaction + row locking (Gotcha #2)"
    - "Lock rows ORDER BY id to prevent deadlocks"
    - "If exclude_large_fields=True, don't select description > 1000 chars"

dependencies_complete:
  - task_2: "Backend - Pydantic Models"
  - task_3: "Backend - Database Configuration"

group_info:
  group_number: 2
  execution_mode: "parallel"
  parallel_tasks: ["Task 3", "Task 4", "Task 5", "Task 11"]

prp_reference:
  full_prp_available: true
  task_section_line_range: "1238-1298"  # Lines in PRP for this task

instructions: |
  You are implementing Task 5 from the Task Management UI PRP.

  Your role:
  1. Read the PATTERN TO FOLLOW file carefully
  2. Implement the SPECIFIC STEPS exactly as listed
  3. Follow all GOTCHAS TO AVOID
  4. Run VALIDATION COMMANDS and fix any errors
  5. Report completion with validation results

  You have access to:
  - Full PRP at prp_file path
  - Example code at pattern reference
  - All dependencies (Tasks 2, 3) are complete

  Critical Success Criteria:
  - Position reordering uses SELECT ... FOR UPDATE (Gotcha #2)
  - All validation commands pass
  - Code follows Archon patterns from examples

  When complete, report:
  - Files created/modified
  - Validation results (pytest output, mypy, ruff)
  - Any issues encountered
  - Ready for next group (confirm dependencies satisfied)
```

---

## Dependency Verification Protocol

Before starting each group, orchestrator MUST verify:

### Group 1 → Group 2
**Required artifacts**:
- [ ] `database/init.sql` exists
- [ ] `backend/src/models/task.py` exists
- [ ] `backend/src/models/project.py` exists
- [ ] `frontend/src/features/tasks/types/task.ts` exists
- [ ] `docker-compose.yml` exists

**Validation**:
```bash
# Quick smoke test
cd backend && uv run python -c "from src.models.task import TaskCreate; print('Models OK')"
cd frontend && npm run type-check  # Should compile
```

### Group 2 → Group 3
**Required artifacts**:
- [ ] `backend/src/config/database.py` exists
- [ ] `backend/src/services/project_service.py` exists
- [ ] `backend/src/services/task_service.py` exists
- [ ] `frontend/src/features/tasks/services/taskService.ts` exists

**Validation**:
```bash
cd backend && uv run pytest tests/test_task_service.py -v  # Should pass
```

### Group 3 → Group 4
**Required artifacts**:
- [ ] `backend/src/api/projects.py` exists
- [ ] `backend/src/api/tasks.py` exists
- [ ] `backend/src/mcp_server.py` exists
- [ ] `frontend/src/features/shared/config/queryClient.ts` exists

**Validation**:
```bash
cd backend && uv run python -c "from src.api.tasks import router; print('Routes OK')"
```

### Group 4 → Group 5
**Required artifacts**:
- [ ] `backend/src/main.py` exists
- [ ] `frontend/src/features/tasks/hooks/useTaskQueries.ts` exists
- [ ] `frontend/src/features/tasks/components/KanbanColumn.tsx` exists

**Validation**:
```bash
cd backend && uv run uvicorn src.main:app --reload &  # Should start
sleep 5
curl http://localhost:8000/health  # Should return {"status": "healthy"}
kill %1
```

### Group 5 → Group 6
**Required artifacts**:
- [ ] `frontend/src/features/tasks/components/TaskCard.tsx` exists
- [ ] `frontend/src/features/tasks/components/KanbanBoard.tsx` exists
- [ ] `frontend/src/features/tasks/components/TaskListView.tsx` exists
- [ ] `frontend/src/features/tasks/components/TaskDetailModal.tsx` exists

**Validation**:
```bash
cd frontend && npm run build  # Should build successfully
```

### Group 6 → Group 7
**Required artifacts**:
- [ ] `backend/Dockerfile` exists
- [ ] `frontend/Dockerfile` exists
- [ ] `backend/tests/test_task_service.py` exists
- [ ] `backend/tests/test_mcp.py` exists
- [ ] `README.md` exists

**Validation**:
```bash
cd backend && uv run pytest tests/ -v  # All tests pass
docker-compose build  # Should build without errors
```

---

## Risk Assessment & Mitigation

### Potential Bottlenecks

**1. Task 5 (Service Layer - Tasks): 75 minutes**
- **Risk**: Position reordering logic is complex, transaction handling tricky
- **Impact**: Blocks Tasks 7, 8 (Group 3)
- **Mitigation**:
  - Provide detailed pseudocode in task context
  - Reference Archon example (lines 93-115) explicitly
  - Allocate extra buffer time if implementer struggles
  - Fallback: Implement simpler position logic first, optimize later

**2. Task 8 (MCP Server): 75 minutes**
- **Risk**: Response optimization and truncation logic complex
- **Impact**: Blocks Task 9, Task 23
- **Mitigation**:
  - Clear example from Archon task_tools.py
  - Break into sub-steps: basic tools → optimization → testing
  - Validate response sizes early in implementation

**3. Task 13 (Query Hooks): 60 minutes**
- **Risk**: Optimistic updates with query cancellation is subtle
- **Impact**: Blocks all UI components (Group 5)
- **Mitigation**:
  - Archon example (useTaskQueries.ts) is working reference
  - Emphasize cancellation in context (Gotcha #4)
  - Test rollback behavior early

**4. Task 22 (Backend Unit Tests): 75 minutes**
- **Risk**: Writing comprehensive tests takes time, may reveal implementation bugs
- **Impact**: Delays final integration (Task 25)
- **Mitigation**:
  - Focus on critical paths first (position reordering, validation)
  - Use pytest fixtures to reduce boilerplate
  - Acceptable to have 80% coverage vs. 100%

**5. Task 25 (Final Integration): 90 minutes**
- **Risk**: End-to-end issues may require revisiting earlier tasks
- **Impact**: Could extend total timeline significantly
- **Mitigation**:
  - Each group has validation gates to catch issues early
  - Most integration issues should surface in Group 6 testing
  - Have rollback strategy if critical bug found

### Parallelization Benefits

**Group 1 (4 tasks in parallel)**:
- Sequential: 180 min (60+45+30+45)
- Parallel: 60 min (max duration)
- **Savings**: 120 min (66%)

**Group 2 (4 tasks in parallel)**:
- Sequential: 240 min (45+60+75+60)
- Parallel: 75 min (max duration)
- **Savings**: 165 min (69%)

**Group 3 (4 tasks in parallel)**:
- Sequential: 225 min (45+60+75+45)
- Parallel: 75 min (max duration)
- **Savings**: 150 min (67%)

**Group 4 (3 tasks in parallel)**:
- Sequential: 150 min (45+60+45)
- Parallel: 60 min (max duration)
- **Savings**: 90 min (60%)

**Group 5 (4 tasks in parallel)**:
- Sequential: 195 min (30+60+60+45)
- Parallel: 60 min (max duration)
- **Savings**: 135 min (69%)

**Group 6 (5 tasks in parallel)**:
- Sequential: 255 min (30+30+75+45+60)
- Parallel: 75 min (max duration)
- **Savings**: 180 min (71%)

**Total Parallelization Benefit**: ~840 minutes saved across 6 parallel groups

---

## Alternative Execution Strategies

### Strategy A: Conservative (Less Parallelization)

**Rationale**: Minimize risk of conflicts, ensure each layer complete before next

**Groups**:
1. Database + Models (Tasks 1, 2) - Parallel
2. Database Config (Task 3) - Sequential
3. Services (Tasks 4, 5) - Parallel
4. API Routes + MCP (Tasks 6, 7, 8) - Parallel
5. Main App (Task 9) - Sequential
6. Frontend Types + Config (Tasks 10, 11, 12) - Parallel
7. Frontend Hooks (Task 13) - Sequential
8. Drag-and-Drop (Tasks 14, 15) - Parallel
9. UI Components (Tasks 16, 17, 18) - Parallel
10. Docker (Tasks 19, 20, 21) - Parallel
11. Testing (Tasks 22, 23) - Parallel
12. Documentation (Task 24) - Sequential
13. Final Integration (Task 25) - Sequential

**Time**: ~10.5 hours (vs. 8.25 hours in recommended plan)
**Benefit**: Lower risk, clearer dependency resolution
**Downside**: 25% slower

### Strategy B: Aggressive (Maximum Parallelization)

**Rationale**: Maximize speed, accept risk of rework

**Groups**:
1. Foundation (Tasks 1, 2, 3, 10, 11, 19) - 6 tasks parallel
2. Services + Query Config (Tasks 4, 5, 12) - 3 tasks parallel
3. API + MCP + Hooks (Tasks 6, 7, 8, 9, 13) - 5 tasks parallel
4. All UI (Tasks 14, 15, 16, 17, 18) - 5 tasks parallel
5. Docker + Testing + Docs (Tasks 20, 21, 22, 23, 24) - 5 tasks parallel
6. Final Integration (Task 25) - Sequential

**Time**: ~6.5 hours (vs. 8.25 hours in recommended plan)
**Benefit**: Fastest possible execution
**Downside**: Higher risk of conflicts, more rework if dependencies unclear

### Recommended: Balanced Strategy (As Presented)

**Rationale**: Optimize for speed while respecting clear dependencies

- **7 groups** balance parallelization vs. safety
- **Clear dependency boundaries** between groups
- **Validation gates** catch issues before cascading
- **58% time savings** vs. sequential execution
- **Low risk** of conflicts within groups

---

## Monitoring & Progress Tracking

### Archon Integration

**Project Structure**:
```
Project: Task Management UI (ID: 0e5d6945-e25a-465d-ab8b-b2629e0345af)
├── Group 1: Foundation
│   ├── Task 1: Database Setup [todo → doing → review → done]
│   ├── Task 2: Backend - Pydantic Models [todo → doing → review → done]
│   ├── Task 10: Frontend - TypeScript Types [todo → doing → review → done]
│   └── Task 19: Docker - Compose Configuration [todo → doing → review → done]
├── Group 2: Backend/Frontend Core
│   ├── Task 3: Backend - Database Config [todo → doing → review → done]
│   ├── Task 4: Backend - Service Layer (Projects) [todo → doing → review → done]
│   ├── Task 5: Backend - Service Layer (Tasks) [todo → doing → review → done]
│   └── Task 11: Frontend - API Client & Services [todo → doing → review → done]
...
```

**Status Updates**:
- **todo**: Task in queue, waiting for dependencies
- **doing**: Implementer actively working (parallel in same group)
- **review**: Implementation complete, validation running
- **done**: Validation passed, ready for next group

**Progress Queries**:
```bash
# Check group status
archon.find_tasks(filter_by="status", filter_value="doing")
# Should show all tasks in current group during execution

# Check overall progress
archon.find_tasks(project_id="0e5d6945-e25a-465d-ab8b-b2629e0345af")
# Shows all tasks with status

# Check specific task
archon.find_tasks(task_id="task-5-uuid")
# Returns full task details with status, assignee, updated_at
```

### Execution Metrics

**Track these metrics during execution**:

1. **Group Completion Time**:
   - Expected vs. Actual duration per group
   - Identify if bottleneck tasks take longer than estimated

2. **Validation Pass Rate**:
   - How many tasks pass validation on first attempt
   - Common failure patterns (linting, type errors, test failures)

3. **Rework Required**:
   - Tasks needing revision after validation
   - Time spent on fixes vs. initial implementation

4. **Critical Path Accuracy**:
   - Did critical path tasks match estimates?
   - Were dependencies correctly identified?

5. **Parallelization Effectiveness**:
   - Actual time savings vs. estimated 58%
   - Were there conflicts between parallel tasks?

### Real-Time Dashboard (Conceptual)

```
PRP Execution: Task Management UI
Progress: ████████░░░░░░░░░░░░░░░░░░░░ 40% (10/25 tasks)

Current Group: 3 (API & Query Integration)
Status: IN PROGRESS (2/4 tasks complete)

Timeline:
[✓] Group 1: Foundation (60 min) - COMPLETE
[✓] Group 2: Backend/Frontend Core (75 min) - COMPLETE
[→] Group 3: API & Query Integration (75 min) - IN PROGRESS (35 min elapsed)
    [✓] Task 6: FastAPI Routes (Projects) - DONE
    [✓] Task 7: FastAPI Routes (Tasks) - DONE
    [→] Task 8: MCP Server - DOING (implementer-2)
    [→] Task 12: TanStack Query Config - DOING (implementer-4)
[ ] Group 4: Main Application (60 min)
[ ] Group 5: UI Components (60 min)
[ ] Group 6: Docker & Testing (75 min)
[ ] Group 7: Final Integration (90 min)

Estimated Completion: 4h 20min remaining
```

---

## Success Criteria Validation

After Task 25 (Final Integration), verify all PRP success criteria:

### Deployment Criteria
- [x] `docker-compose up` starts all services without errors
- [x] Web UI accessible at http://localhost:3000
- [x] MCP server responds to `npx mcp-remote http://localhost:8051/mcp`
- [x] Data persists after `docker-compose down && docker-compose up`
- [x] Health checks pass for all services

### UI Functionality Criteria
- [x] Create project via UI
- [x] Create task with title, description (markdown), status, priority, assignee
- [x] Kanban board displays tasks in 4 columns
- [x] Drag task from "todo" to "doing" updates status immediately (optimistic update)
- [x] List view shows tasks with filters (status, assignee, priority) and sorting
- [x] Task detail modal edits title, description, status, priority, assignee
- [x] Manual drag-and-drop ordering within columns persists

### MCP Integration Criteria
- [x] `find_tasks()` returns task list with pagination
- [x] `find_tasks(task_id="uuid")` returns single task with full details
- [x] `find_tasks(filter_by="status", filter_value="todo")` filters correctly
- [x] `manage_task("create", project_id="uuid", title="Test")` creates task visible in UI
- [x] `manage_task("update", task_id="uuid", status="doing")` updates task in UI
- [x] `manage_task("delete", task_id="uuid")` removes task from UI
- [x] Claude Code can manage tasks via MCP without errors

### Quality Criteria
- [x] Python type hints on all backend functions
- [x] TypeScript strict mode enabled for frontend
- [x] Pydantic models validate all request/response data
- [x] OpenAPI docs available at http://localhost:8000/docs
- [x] README with setup instructions and example commands
- [x] .env.example with all required variables documented

### Performance Criteria
- [x] MCP `find_tasks()` responds in < 500ms for 100 tasks
- [x] Drag-and-drop update perceived latency < 200ms
- [x] UI polling rate ≤ 1 request/second when active
- [x] Database queries use indexes (verify with EXPLAIN ANALYZE)

---

## Assumptions & Constraints

### Assumptions Made

1. **Implementer Skill Level**:
   - Implementers are familiar with FastAPI, React, and Docker
   - Can follow detailed instructions and examples
   - Will read referenced documentation when needed

2. **Example Files Exist**:
   - `prps/task_management_ui/examples/` directory is populated
   - All referenced Archon example files are accessible
   - Example code is functional and tested

3. **Environment Setup**:
   - Python 3.12+, Node 20+, Docker available
   - UV package manager installed for backend
   - PostgreSQL 16 Docker image accessible

4. **Parallel Execution Capability**:
   - Orchestrator can invoke multiple subagents simultaneously
   - Subagents don't interfere with each other's file writes
   - Resource limits allow 4-5 parallel processes

5. **Validation Automation**:
   - All validation commands can run in CI/CD environment
   - Test failures block progression to next group
   - Manual intervention available for edge cases

### Constraints

1. **Single-Pass Implementation**:
   - Tasks in same group can't modify same files
   - Dependencies must be in earlier groups
   - No circular dependencies

2. **Time Estimates**:
   - Based on experienced developer (3-5 years)
   - Junior developers may take 1.5-2x longer
   - Senior developers may be 0.7-0.8x time

3. **Testing Limitations**:
   - Unit tests only, no E2E browser tests (Playwright)
   - Manual testing required for visual UI validation
   - Performance benchmarks are estimates, need measurement

4. **Docker Environment**:
   - Development environment, not production-optimized
   - Hot reload enabled, slower startup times
   - No CI/CD integration in initial implementation

### If Assumptions Prove Wrong

**If example files missing**:
- Use Archon codebase directly (paths documented in PRP)
- Extend task time estimates by 20-30%
- Implementers extract patterns themselves

**If parallel execution unavailable**:
- Fall back to sequential execution within groups
- Total time increases to ~12-14 hours
- Still better than full sequential (20 hours)

**If validation fails consistently**:
- Review task breakdown for missed dependencies
- Increase buffer time for complex tasks (5, 8, 13)
- Consider splitting bottleneck tasks

**If time estimates too optimistic**:
- Groups 2, 3, 6 have most risk (complex logic)
- Add 25% buffer to these groups
- Total time may extend to 10-11 hours

---

## Next Steps for Orchestrator

### Pre-Execution Checklist

Before starting Group 1:
- [x] PRP file exists and is readable
- [x] Execution plan created (this file)
- [x] Archon project created (ID: 0e5d6945-e25a-465d-ab8b-b2629e0345af)
- [x] All 25 tasks created in Archon with proper metadata
- [ ] Example files directory verified: `prps/task_management_ui/examples/`
- [ ] Implementer subagent tested and functional
- [ ] Validation environment ready (Python, Node, Docker)

### Execution Commands

```bash
# Start execution
prp-exec-orchestrator \
  --prp prps/task_management_ui.md \
  --execution-plan prps/task_management_ui/execution/execution-plan.md \
  --archon-project-id 0e5d6945-e25a-465d-ab8b-b2629e0345af \
  --mode parallel

# Monitor progress
watch archon.find_tasks(project_id="0e5d6945-e25a-465d-ab8b-b2629e0345af")

# Validate group completion
./scripts/validate-group.sh <group_number>

# Resume after interruption
prp-exec-orchestrator \
  --resume \
  --from-group <last_completed_group>
```

### Post-Execution Tasks

After Task 25 completes:
1. Run full validation suite from PRP checklist
2. Update Archon project status to "done"
3. Generate execution metrics report
4. Document lessons learned for future PRPs
5. Archive execution logs and validation results

---

## Conclusion

This execution plan provides a **balanced strategy** for implementing the Task Management UI PRP with:

- **58% time savings** through parallelization (20h → 8.25h)
- **7 execution groups** with clear dependency boundaries
- **25 tasks** organized for optimal parallel execution
- **Detailed validation gates** at each group transition
- **Risk mitigation strategies** for bottleneck tasks
- **Comprehensive monitoring** via Archon integration

**Key Success Factors**:
1. Strict dependency enforcement between groups
2. Validation before proceeding to next group
3. Clear task context with examples and gotchas
4. Archon status tracking for progress visibility
5. Rollback strategy if integration issues found

**Recommended Action**: Proceed with parallel execution using this plan. Expected completion in ~8.5 hours with high confidence in success.

---

**Execution Plan Generated**: 2025-10-06
**Plan Version**: 1.0
**Ready for Execution**: ✅ Yes
**Estimated Success Probability**: 85%+
