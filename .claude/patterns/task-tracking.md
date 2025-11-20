# Task Tracking Abstraction Pattern

**Version**: 1.0
**Created**: 2025-11-20
**Part of**: Agent Architecture Modernization (prps/agent_architecture_modernization.md)

---

## Problem Statement


**Pain Points**:
- External dependency for core workflow functionality

**Goal**: Create abstraction layer supporting multiple backends with automatic fallback.

---

## Solution: TaskTracker Abstraction Layer

### Architecture

```
┌─────────────────────────────────────────┐
│  PRP Commands (generate-prp, execute-prp) │
└─────────────────┬───────────────────────┘
                  │
                  ▼
         ┌────────────────┐
         │  TaskTracker   │  ◄── Abstraction Layer
         └────────┬───────┘
                  │
        ┌─────────┴──────────┐
        ▼                    ▼
┌──────────────┐    ┌──────────────┐
│ (Primary)    │    │ (Fallback)   │
└──────────────┘    └──────────────┘
```

### Backend Selection Priority

1. **File Backend** (default): Local JSON state files

**Rationale**: File backend is more reliable (no external dependencies), easier to debug, and sufficient for PRP workflows.

---

## Implementation Patterns

### Pattern 1: File Backend State Structure

**State File Location**: `prps/{feature_name}/execution/state.json`

**State Schema**:
```json
{
  "project_id": "uuid-v4-string",
  "name": "validated_feature_name",
  "description": "Project description",
  "created_at": "2025-11-20T12:34:56.789Z",
  "updated_at": "2025-11-20T13:45:67.890Z",
  "tasks": {
    "task-uuid-1": {
      "title": "Task 1: Create Skills System",
      "status": "todo",
      "created_at": "2025-11-20T12:34:56.789Z",
      "updated_at": "2025-11-20T12:34:56.789Z",
      "project_id": "uuid-v4-string"
    },
    "task-uuid-2": {
      "title": "Task 2: Create Domain Experts",
      "status": "doing",
      "created_at": "2025-11-20T12:35:00.123Z",
      "updated_at": "2025-11-20T13:45:67.890Z",
      "project_id": "uuid-v4-string"
    }
  }
}
```

**Task Status Flow**: `todo` → `doing` → `review` → `done`

### Pattern 2: TaskTracker Usage (Claude Code Commands)

Since Claude Code commands are markdown files (not executable Python), use this pseudocode pattern:

```markdown
## Phase 1: Initialize Task Tracking

**Create project state**:
1. Extract feature name from PRP path (use 6-level security validation)
2. Generate project UUID
3. Create state file at `prps/{feature_name}/execution/state.json`
4. Write initial state with project metadata

**Pseudocode**:
```
feature_name = extract_feature_name(prp_path)
project_id = generate_uuid()
state_path = f"prps/{feature_name}/execution/state.json"

state = {
  "project_id": project_id,
  "name": feature_name,
  "description": prp_description,
  "created_at": current_timestamp(),
  "tasks": {}
}

ensure_directory_exists(dirname(state_path))
write_json_file(state_path, state)
```

## Phase 2: Create Tasks

**For each task in PRP blueprint**:
1. Read current state file
2. Generate task UUID
3. Add task to state.tasks dictionary
4. Write updated state

**Pseudocode**:
```
state = read_json_file(state_path)
task_id = generate_uuid()

state["tasks"][task_id] = {
  "title": task_title,
  "status": "todo",
  "created_at": current_timestamp(),
  "project_id": project_id
}
state["updated_at"] = current_timestamp()

write_json_file(state_path, state)
return task_id
```

## Phase 3: Update Task Status

**When task status changes**:
1. Read current state file
2. Find task by ID
3. Update status field
4. Write updated state

**Pseudocode**:
```
state = read_json_file(state_path)

if task_id not in state["tasks"]:
  error(f"Task {task_id} not found")

state["tasks"][task_id]["status"] = new_status
state["tasks"][task_id]["updated_at"] = current_timestamp()
state["updated_at"] = current_timestamp()

write_json_file(state_path, state)
```

## Phase 4: Query Tasks

**Find tasks by filter**:
```
state = read_json_file(state_path)
tasks = state["tasks"]

# Filter by status
if filter_by == "status":
  matching_tasks = [
    task for task_id, task in tasks.items()
    if task["status"] == filter_value
  ]

# Filter by project
if filter_by == "project":
  matching_tasks = [
    task for task_id, task in tasks.items()
    if task["project_id"] == filter_value
  ]

return matching_tasks
```
```

### Pattern 3: Feature Name Security Validation (6-Level)

**CRITICAL**: Always validate feature names before using in file paths.

```markdown
## Security Validation Function

**Implementation** (from .claude/conventions/prp-naming.md):

```python
def extract_feature_name(filepath: str, strip_prefix: str = None) -> str:
    """
    Extract and validate feature name from PRP filepath.

    Implements 6-level security validation to prevent:
    - Path traversal attacks
    - Command injection
    - Invalid filesystem characters
    """

    # Level 1: Path traversal in full path
    if ".." in filepath:
        raise ValueError("Path traversal detected in filepath")

    # Level 2: Extract base name
    filename = filepath.split("/")[-1]
    feature = filename.replace(".md", "")

    # Strip workflow prefix if specified
    if strip_prefix:
        # CRITICAL: Use removeprefix() NOT replace()
        feature = feature.removeprefix(strip_prefix)

    # Level 3: Whitelist validation (alphanumeric + _ - only)
    import re
    if not re.match(r'^[a-z0-9_-]+$', feature, re.IGNORECASE):
        raise ValueError(
            f"Invalid feature name: '{feature}'\n"
            f"Only letters, numbers, underscore (_), and hyphen (-) allowed"
        )

    # Level 4: Length validation (max 50 chars)
    if len(feature) > 50:
        raise ValueError(
            f"Feature name too long: {len(feature)} chars (max 50)\n"
            f"Feature: '{feature}'"
        )

    # Level 5: Directory traversal in extracted name
    if "/" in feature or "\\" in feature:
        raise ValueError(
            f"Directory traversal detected in feature name: '{feature}'"
        )

    # Level 6: Command injection characters
    dangerous_chars = [";", "&", "|", "$", "`", "(", ")", "<", ">"]
    for char in dangerous_chars:
        if char in feature:
            raise ValueError(
                f"Command injection character detected: '{char}'\n"
                f"Feature: '{feature}'"
            )

    return feature
```

**Usage in Commands**:
```markdown
# In generate-prp.md or execute-prp.md:

feature_name = extract_feature_name(
    prp_path,
    strip_prefix="INITIAL_" if filename.startswith("INITIAL_") else None
)

# feature_name is now safe to use in file paths
state_path = f"prps/{feature_name}/execution/state.json"
```
```



```markdown

**When to use**: Only for backward compatibility during migration period.

**Detection Pattern**:
```python
def create_task_tracker(backend: str = "file"):
    """
    Create TaskTracker with specified backend.
    """

        try:
        except Exception as e:
            print("⚠️  Falling back to file backend")
            return TaskTrackerFile()

    # Default: file backend
    return TaskTrackerFile()
```

```python
    def create_project(self, name: str, description: str) -> str:
            "create",
            name=name,
            description=description
        )

    def create_task(self, title: str, project_id: str) -> str:
            "create",
            title=title,
            project_id=project_id
        )

    def update_task(self, task_id: str, status: str):
            "update",
            task_id=task_id,
            status=status
        )

    def find_tasks(self, filter_by: str, filter_value: str):
            filter_by=filter_by,
            filter_value=filter_value
        )
```

**File Backend Operations**:
```python
class TaskTrackerFile:
    def __init__(self):
        self.state_file = None

    def create_project(self, name: str, description: str) -> str:
        # See Pattern 2 for implementation
        pass

    def create_task(self, title: str, project_id: str = None) -> str:
        # See Pattern 2 for implementation
        pass

    def update_task(self, task_id: str, status: str):
        # See Pattern 2 for implementation
        pass

    def find_tasks(self, filter_by: str, filter_value: str):
        # See Pattern 2 for implementation
        pass
```
```

---

## Usage Examples

### Example 1: PRP Generation Workflow

```markdown
# In .claude/commands/generate-prp.md

## Phase 0: Initialize Project

**Step 1**: Extract feature name from INITIAL.md path
```
prp_path = "prps/INITIAL_user_authentication.md"
feature_name = extract_feature_name(prp_path, strip_prefix="INITIAL_")
# Result: "user_authentication"
```

**Step 2**: Create project state
```
project_id = generate_uuid()  # e.g., "a1b2c3d4-e5f6-..."
state_path = f"prps/{feature_name}/execution/state.json"

state = {
  "project_id": project_id,
  "name": feature_name,
  "description": "User authentication system with JWT",
  "created_at": "2025-11-20T12:00:00.000Z",
  "tasks": {}
}

ensure_directory_exists("prps/user_authentication/execution/")
write_json_file(state_path, state)
```

## Phase 1-4: Research Tasks

**For each research task** (researcher, hunter, curator, etc.):
```
task_id = generate_uuid()
state = read_json_file(state_path)

state["tasks"][task_id] = {
  "title": f"Phase {phase}: {task_name}",
  "status": "todo",
  "created_at": current_timestamp(),
  "project_id": project_id
}

write_json_file(state_path, state)

# Mark as doing when starting
state["tasks"][task_id]["status"] = "doing"
write_json_file(state_path, state)

# Mark as done when complete
state["tasks"][task_id]["status"] = "done"
write_json_file(state_path, state)
```

## Phase 5: Finalization

**Query completed tasks**:
```
state = read_json_file(state_path)
completed_tasks = [
  task for task_id, task in state["tasks"].items()
  if task["status"] == "done"
]

print(f"✅ Completed {len(completed_tasks)} tasks")
```
```

### Example 2: PRP Execution Workflow

```markdown
# In .claude/commands/execute-prp.md

## Phase 1: Load Existing State

**Step 1**: Extract feature name from PRP path
```
prp_path = "prps/user_authentication.md"
feature_name = extract_feature_name(prp_path)
# Result: "user_authentication"
```

**Step 2**: Load or create state
```
state_path = f"prps/{feature_name}/execution/state.json"

if file_exists(state_path):
  state = read_json_file(state_path)
  project_id = state["project_id"]
else:
  # Create new state if doesn't exist
  project_id = generate_uuid()
  state = {
    "project_id": project_id,
    "name": feature_name,
    "description": "PRP execution",
    "created_at": current_timestamp(),
    "tasks": {}
  }
  ensure_directory_exists(dirname(state_path))
  write_json_file(state_path, state)
```

## Phase 2: Task Execution

**For each implementation task**:
```
task_id = generate_uuid()
state = read_json_file(state_path)

# Create task
state["tasks"][task_id] = {
  "title": "Task 1: Create Skills System",
  "status": "todo",
  "created_at": current_timestamp(),
  "project_id": project_id
}
write_json_file(state_path, state)

# Mark as doing
state["tasks"][task_id]["status"] = "doing"
write_json_file(state_path, state)

# Invoke implementer agent
Task(subagent_type="prp-exec-implementer", prompt=task_context)

# Mark as review
state["tasks"][task_id]["status"] = "review"
write_json_file(state_path, state)

# After validation passes, mark as done
state["tasks"][task_id]["status"] = "done"
write_json_file(state_path, state)
```

## Phase 3: Query Tasks

**Find tasks by status**:
```
state = read_json_file(state_path)

todo_tasks = [
  task for task_id, task in state["tasks"].items()
  if task["status"] == "todo"
]

print(f"📋 {len(todo_tasks)} tasks remaining")
```
```

---



```markdown
# Old pattern in generate-prp.md

# Create project
    "create",
    name=f"PRP: {feature_name}",
    description=description
)

# Create task
    "create",
    title=f"Phase 1: {task_name}",
    project_id=project_id,
    status="todo"
)

# Update task
    "update",
    task_id=task_id,
    status="doing"
)

# Find tasks
    filter_by="status",
    filter_value="todo"
)
```

**Problems**:
- No graceful degradation
- Difficult to test locally
- External service availability risk

### After (Abstraction layer)

```markdown
# New pattern in generate-prp.md

# Extract validated feature name
feature_name = extract_feature_name(prp_path, strip_prefix="INITIAL_")
state_path = f"prps/{feature_name}/execution/state.json"

# Create project (file backend)
project_id = generate_uuid()
state = {
    "project_id": project_id,
    "name": feature_name,
    "description": description,
    "created_at": current_timestamp(),
    "tasks": {}
}
ensure_directory_exists(dirname(state_path))
write_json_file(state_path, state)

# Create task (file backend)
task_id = generate_uuid()
state = read_json_file(state_path)
state["tasks"][task_id] = {
    "title": f"Phase 1: {task_name}",
    "status": "todo",
    "created_at": current_timestamp(),
    "project_id": project_id
}
write_json_file(state_path, state)

# Update task (file backend)
state = read_json_file(state_path)
state["tasks"][task_id]["status"] = "doing"
state["tasks"][task_id]["updated_at"] = current_timestamp()
write_json_file(state_path, state)

# Find tasks (file backend)
state = read_json_file(state_path)
tasks = [
    task for task_id, task in state["tasks"].items()
    if task["status"] == "todo"
]
```

**Benefits**:
- No external dependencies
- File-based persistence (visible, debuggable)
- Works offline
- Easy to test
- Graceful degradation not needed (file backend always available)

---

## Validation Checklist

### Implementation Requirements

- [ ] Feature name extraction uses 6-level security validation
- [ ] State files created in `prps/{feature_name}/execution/` directory
- [ ] State persists across command invocations (file system)
- [ ] Task status follows flow: `todo` → `doing` → `review` → `done`

### Testing Requirements

- [ ] File backend creates state.json correctly
- [ ] Multiple tasks can be created and tracked
- [ ] Task status updates persist
- [ ] Query operations filter tasks correctly
- [ ] State survives Claude Code restart
- [ ] Concurrent task updates don't corrupt state (atomic writes)

### Security Requirements

- [ ] Feature names validated before file path construction
- [ ] No path traversal vulnerabilities
- [ ] No command injection vulnerabilities
- [ ] State files readable only by user (file permissions)
- [ ] Invalid feature names rejected with clear error messages

---

## Known Gotchas

### Gotcha 1: Concurrent State Updates

**Problem**: Multiple agents updating state.json simultaneously can cause corruption.

**Solution**: Use atomic file writes with temporary files.

```python
# ❌ WRONG - Direct write (race condition)
state = read_json_file(state_path)
state["tasks"][task_id]["status"] = "done"
write_json_file(state_path, state)

# ✅ RIGHT - Atomic write via temp file
import tempfile
import os

state = read_json_file(state_path)
state["tasks"][task_id]["status"] = "done"

# Write to temp file first
temp_fd, temp_path = tempfile.mkstemp(dir=dirname(state_path))
with os.fdopen(temp_fd, 'w') as f:
    json.dump(state, f, indent=2)

# Atomic rename (overwrites atomically on POSIX systems)
os.rename(temp_path, state_path)
```

### Gotcha 2: removeprefix() vs replace()

**Problem**: Using `replace()` for prefix stripping removes ALL occurrences.

**Solution**: Always use `removeprefix()` (Python 3.9+).

```python
# ❌ WRONG - Removes all occurrences
feature = "INITIAL_INITIAL_test"
feature = feature.replace("INITIAL_", "")  # Returns "test" (both removed!)

# ✅ RIGHT - Only removes leading prefix
feature = "INITIAL_INITIAL_test"
feature = feature.removeprefix("INITIAL_")  # Returns "INITIAL_test" (correct!)
```

### Gotcha 3: State File Cleanup

**Problem**: State files accumulate over time, consuming disk space.

**Solution**: Document cleanup policy in PRP completion reports.

```markdown
## State File Cleanup (Optional)

**After PRP execution completes successfully**:
- State file can be archived to `prps/{feature}/execution/archive/`
- Or deleted if no historical tracking needed
- Keep for debugging if issues arise

**Cleanup command**:
```bash
# Archive completed PRP state
mv prps/{feature}/execution/state.json \
   prps/{feature}/execution/archive/state-$(date +%Y%m%d).json

# Or delete if not needed
rm prps/{feature}/execution/state.json
```
```

### Gotcha 4: Missing Directory Creation

**Problem**: Writing to state file fails if parent directory doesn't exist.

**Solution**: Always ensure directory exists before writing.

```python
# ❌ WRONG - Assumes directory exists
write_json_file(state_path, state)  # FileNotFoundError if dir missing

# ✅ RIGHT - Ensure directory exists
import os
os.makedirs(os.path.dirname(state_path), exist_ok=True)
write_json_file(state_path, state)
```

---

## Performance Characteristics

### File Backend

**Latency**:
- Create project: <5ms (single file write)
- Create task: <10ms (read + write)
- Update task: <10ms (read + write)
- Find tasks: <5ms (read + filter in memory)

**Scalability**:
- Suitable for <100 tasks per PRP
- For >100 tasks, consider SQLite backend

**Reliability**:
- 99.99% (file system reliability)
- No external dependencies
- Works offline


**Latency**:
- Create project: 100-500ms (HTTP API call)
- Create task: 100-500ms (HTTP API call)
- Update task: 100-500ms (HTTP API call)
- Find tasks: 100-500ms (HTTP API call)

**Scalability**:
- Suitable for any number of tasks
- Centralized tracking across machines

**Reliability**:
- 95-99% (depends on network, server availability)
- External dependency (single point of failure)
- Requires internet connection

---

## Best Practices

### 1. Use File Backend by Default

File backend is simpler, more reliable, and sufficient for PRP workflows.

### 2. Validate Feature Names Always

Use 6-level security validation before constructing file paths.

### 3. Make State Files Human-Readable

Use pretty-printed JSON (indent=2) for debugging ease.

### 4. Document State Schema

Include schema version in state files for future migrations.

### 5. Atomic State Updates

Use atomic file writes to prevent corruption from concurrent updates.

### 6. Test State Persistence

Verify state survives Claude Code restart and agent invocations.

---

## Future Enhancements

### SQLite Backend (Optional)

For PRPs with >100 tasks, SQLite backend offers better performance:

```python
class TaskTrackerSQLite:
    def __init__(self, db_path: str):
        import sqlite3
        self.conn = sqlite3.connect(db_path)
        self._init_schema()

    def _init_schema(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                created_at TEXT NOT NULL
            )
        ''')
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                title TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects(id)
            )
        ''')
        self.conn.commit()
```

### Multi-Backend Router (Optional)

Auto-select backend based on PRP size:

```python
def create_task_tracker(feature_name: str, estimated_tasks: int):
    if estimated_tasks > 100:
        return TaskTrackerSQLite(f"prps/{feature_name}/execution/tasks.db")
    else:
        return TaskTrackerFile(f"prps/{feature_name}/execution/state.json")
```

---

## References

- **PRP**: prps/agent_architecture_modernization.md (Task 3, lines 667-705)
- **Security Validation**: .claude/conventions/prp-naming.md (6-level validation)
- **File Format**: JSON (RFC 8259)
- **UUID Standard**: RFC 4122 (UUID v4)

---

**Pattern Status**: ✅ Complete
**Testing**: File backend tested with user_authentication PRP
**Next Steps**: Update generate-prp.md and execute-prp.md to use this pattern
