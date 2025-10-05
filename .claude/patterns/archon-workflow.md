# Archon Workflow

```python
# Archon MCP: Project/task tracking (health check, graceful degradation, parallel execution)
# Use for: Multi-phase workflows, subagent coordination
# See: .claude/commands/generate-prp.md, .claude/commands/execute-prp.md

# === CORE PATTERN ===

# 1. Health check (ALWAYS FIRST)
health = mcp__archon__health_check()
archon_available = health["status"] == "healthy"

# 2. Graceful fallback - never fail workflow if Archon unavailable
if not archon_available:
    project_id = None
    task_ids = []
    print("ℹ️ Archon MCP not available - proceeding without project tracking")
else:
    # 3. Create project
    project = mcp__archon__manage_project("create",
        title=f"PRP Generation: {feature_name}",
        description="Creating comprehensive PRP from INITIAL.md"
    )
    project_id = project["project"]["id"]

    # 4. Create tasks (priority: higher = more important)
    task = mcp__archon__manage_task("create",
        project_id=project_id,
        title="Phase 1: Feature Analysis",
        description="Extract requirements from INITIAL.md",
        status="todo",
        assignee="prp-gen-feature-analyzer",
        task_order=100  # 0-100, higher = higher priority
    )
    task_id = task["task"]["id"]

    # 5. Update status: todo → doing → done
    mcp__archon__manage_task("update", task_id=task_id, status="doing")
    # ... do work ...
    mcp__archon__manage_task("update", task_id=task_id, status="done")

# 6. Parallel execution (CRITICAL: batch updates before/after)
if archon_available:
    for task_id in parallel_task_ids:
        mcp__archon__manage_task("update", task_id=task_id, status="doing")

# Invoke ALL in SAME response (parallel)
Task(subagent_type="prp-gen-codebase-researcher", ...)
Task(subagent_type="prp-gen-documentation-hunter", ...)
Task(subagent_type="prp-gen-example-curator", ...)

if archon_available:
    for task_id in parallel_task_ids:
        mcp__archon__manage_task("update", task_id=task_id, status="done")

# 7. Error handling - reset to "todo" for retry
try:
    Task(subagent_type="prp-gen-feature-analyzer", ...)
except Exception as e:
    if archon_available:
        mcp__archon__manage_task("update", task_id=task_id,
            status="todo", description=f"ERROR: {e}")
    print(f"⚠️ Phase failed: {e}")

# 8. Store final document
if archon_available:
    mcp__archon__manage_document("create",
        project_id=project_id,
        title=f"{feature_name}.md",
        content=Read(f"prps/{feature_name}.md"),
        document_type="prp"
    )

# 9. Project completion
if archon_available:
    mcp__archon__manage_project("update", project_id=project_id,
        description="COMPLETED: Generated PRP with 8/10 quality")


# === API REFERENCE ===

# manage_project(action, **fields)
mcp__archon__manage_project("create",
    title="PRP Generation: user_auth", description="Brief summary")
mcp__archon__manage_project("update",
    project_id="abc-123", description="COMPLETED: 8/10 quality")

# manage_task(action, **fields)
mcp__archon__manage_task("create",
    project_id="abc-123", title="Phase 1: Analysis",
    description="Extract requirements", status="todo",
    assignee="prp-gen-feature-analyzer", task_order=100)
mcp__archon__manage_task("update", task_id="task-456", status="doing")
mcp__archon__manage_task("update", task_id="task-456", status="done")

# manage_document(action, **fields)
mcp__archon__manage_document("create",
    project_id="abc-123", title="feature.md",
    content=Read("prps/feature.md"), document_type="prp")

# Field types: project_id/task_id (UUID), status (todo|doing|done|review),
# task_order (0-100, higher=higher priority), document_type (prp|initial|report)


# === RULES (DO/DON'T) ===

# ALWAYS DO:
health = mcp__archon__health_check()                    # 1. Health check FIRST
if not archon_available: project_id = None              # 2. Graceful fallback
mcp__archon__manage_task("update", status="doing")      # 3. Update BEFORE work
Task(subagent_type="worker", ...)                       #    ... do work ...
mcp__archon__manage_task("update", status="done")       # 4. Update AFTER work
except Exception as e: update(status="todo", desc=e)    # 5. Reset on errors
for tid in tids: update("doing")                        # 6. Batch parallel:
Task(...); Task(...); Task(...)                         #    invoke all at once
for tid in tids: update("done")                         #    then update all

# NEVER DO:
if Archon unavailable: raise Exception()                # ❌ Fail workflow
Task(...); update("doing"); Task(...)                   # ❌ Interleave updates
update("in_progress")                                   # ❌ Invalid status

# Example: Complete single-task workflow
health = mcp__archon__health_check()
if health["status"] == "healthy":
    proj = mcp__archon__manage_project("create", title="My Project")
    task = mcp__archon__manage_task("create", project_id=proj["project"]["id"],
        title="Task 1", status="todo", task_order=100)
    mcp__archon__manage_task("update", task_id=task["task"]["id"], status="doing")
    # ... work ...
    mcp__archon__manage_task("update", task_id=task["task"]["id"], status="done")
```
