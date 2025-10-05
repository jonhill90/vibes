# Archon Workflow Pattern - Complete Reference

This pattern consolidates Archon MCP integration from 6+ locations into a single source of truth. Use this when implementing commands that need project/task tracking.

## Health Check (ALWAYS FIRST)

Every Archon workflow must start with a health check:

```python
health = mcp__archon__health_check()
archon_available = health["status"] == "healthy"
# Returns: {"status": "healthy"} or raises exception
```

**Why first?** Determines if Archon is available and enables graceful fallback if not.

---

## Graceful Fallback Pattern

Always provide graceful degradation when Archon is unavailable:

```python
if archon_available:
    # Use Archon features (project/task tracking)
    project = mcp__archon__manage_project("create", ...)
    project_id = project["project"]["id"]
else:
    # Graceful fallback - workflow continues
    project_id = None
    task_ids = []
    print("ℹ️ Archon MCP not available - proceeding without project tracking")
```

**Critical:** Never fail the entire workflow just because Archon is unavailable. Users should be able to work offline or without Archon server.

---

## Project Creation

Create an Archon project to organize all related tasks:

```python
project = mcp__archon__manage_project("create",
    title=f"PRP Generation: {feature_name}",
    description=f"Creating comprehensive PRP from {initial_md_path}"
)
project_id = project["project"]["id"]
```

**Fields:**
- `title`: Human-readable project name (use display-friendly format)
- `description`: Brief summary of what the project accomplishes

**Returns:** `{"project": {"id": "uuid-string", ...}}`

---

## Task Creation with Priority

Create tasks for each major phase or component:

```python
task = mcp__archon__manage_task("create",
    project_id=project_id,
    title="Phase 1: Feature Analysis",
    description="Extract requirements from INITIAL.md",
    status="todo",
    assignee="prp-gen-feature-analyzer",
    task_order=100  # Higher = higher priority (0-100)
)
task_id = task["task"]["id"]
```

**Fields:**
- `project_id`: Links task to project
- `title`: Brief task name
- `description`: What the task accomplishes
- `status`: Initial status (always `"todo"`)
- `assignee`: Who/what executes the task (subagent name or "user")
- `task_order`: Priority (higher number = higher priority, use 0-100 range)

**Priority pattern:** Start at 100 and count down (100, 90, 85, 80, 75, 70...)

**Returns:** `{"task": {"id": "uuid-string", ...}}`

---

## Task Status Flow: todo → doing → done

Tasks follow a strict lifecycle:

```python
# 1. Before starting work
mcp__archon__manage_task("update", task_id=task_id, status="doing")

# 2. After successful completion
mcp__archon__manage_task("update", task_id=task_id, status="done")

# 3. On error (reset for retry)
mcp__archon__manage_task("update",
    task_id=task_id,
    status="todo",
    description=f"ERROR: {error_message}"
)
```

**Status values:**
- `"todo"`: Not started, ready to begin
- `"doing"`: Currently in progress
- `"done"`: Successfully completed
- `"review"`: Completed but needs validation (optional)

**Never skip "doing" status** - it's important for tracking active work.

---

## Parallel Task Updates

When running multiple tasks in parallel, update ALL statuses BEFORE invoking subagents:

```python
# BEFORE parallel invocation: Update ALL to "doing"
if archon_available:
    for task_id in parallel_task_ids:
        mcp__archon__manage_task("update", task_id=task_id, status="doing")

# Invoke all parallel subagents (in single response)
Task(subagent_type="researcher", ...)
Task(subagent_type="hunter", ...)
Task(subagent_type="curator", ...)

# AFTER ALL complete: Update ALL to "done"
if archon_available:
    for task_id in parallel_task_ids:
        mcp__archon__manage_task("update", task_id=task_id, status="done")
```

**Critical:** Don't interleave status updates with subagent invocations. Update all to "doing" first, then invoke all subagents, then update all to "done".

---

## Error Handling and Recovery

When a subagent or task fails:

```python
try:
    # Invoke subagent
    Task(subagent_type="prp-gen-feature-analyzer", ...)
except Exception as e:
    # Log error
    print(f"⚠️ Phase failed: {e}")

    # Update Archon if available
    if archon_available:
        mcp__archon__manage_task("update",
            task_id=task_id,
            description=f"ERROR: {e}",
            status="todo"  # Reset to allow retry
        )

    # Give user choice to recover
    print("\nWould you like me to:")
    print("1. Retry this phase")
    print("2. Continue with partial results")
    print("3. Abort workflow")
    # Wait for user decision
```

**Recovery strategy:**
1. Reset task status to `"todo"` (not back to `"doing"`)
2. Update description with error message for debugging
3. Give user options (retry/continue/abort)

---

## Project Completion

Update project with final summary and store completion documents:

```python
# 1. Update project with final notes
mcp__archon__manage_project("update",
    project_id=project_id,
    description=f"COMPLETED: {completion_summary}"
)

# 2. Store final document in Archon
mcp__archon__manage_document("create",
    project_id=project_id,
    title=f"{feature_name}.md",
    content=document_content,
    document_type="prp"  # or "initial" or "report"
)
```

**Document types:**
- `"prp"`: Product Requirements Prompt
- `"initial"`: INITIAL.md user request
- `"report"`: Completion or validation report

---

## Complete Working Example

Here's a full workflow showing all patterns together:

```python
def example_archon_workflow(feature_name: str, initial_md_path: str):
    """
    Complete example: PRP generation with Archon tracking.
    Shows all patterns in realistic context.
    """

    # Phase 0: Health Check & Setup
    health = mcp__archon__health_check()
    archon_available = health["status"] == "healthy"

    if not archon_available:
        print("ℹ️ Archon MCP not available - proceeding without project tracking")
        project_id = None
        task_ids = []
    else:
        # Create project
        project = mcp__archon__manage_project("create",
            title=f"PRP Generation: {feature_name}",
            description=f"Creating comprehensive PRP from {initial_md_path}"
        )
        project_id = project["project"]["id"]

        # Create 6 tasks for the 6 phases
        task_definitions = [
            {"title": "Phase 1: Feature Analysis", "assignee": "prp-gen-feature-analyzer", "order": 100},
            {"title": "Phase 2A: Codebase Research", "assignee": "prp-gen-codebase-researcher", "order": 90},
            {"title": "Phase 2B: Documentation Hunt", "assignee": "prp-gen-documentation-hunter", "order": 85},
            {"title": "Phase 2C: Example Curation", "assignee": "prp-gen-example-curator", "order": 80},
            {"title": "Phase 3: Gotcha Detection", "assignee": "prp-gen-gotcha-detective", "order": 75},
            {"title": "Phase 4: PRP Assembly", "assignee": "prp-gen-assembler", "order": 70}
        ]

        task_ids = []
        for task_def in task_definitions:
            task = mcp__archon__manage_task("create",
                project_id=project_id,
                title=task_def["title"],
                description=f"{task_def['assignee']} - Autonomous execution",
                status="todo",
                assignee=task_def["assignee"],
                task_order=task_def["order"]
            )
            task_ids.append(task["task"]["id"])

    # Phase 1: Single task (sequential)
    if archon_available:
        mcp__archon__manage_task("update", task_id=task_ids[0], status="doing")

    try:
        # Invoke analyzer subagent
        Task(subagent_type="prp-gen-feature-analyzer", ...)
    except Exception as e:
        if archon_available:
            mcp__archon__manage_task("update",
                task_id=task_ids[0],
                status="todo",
                description=f"ERROR: {e}"
            )
        # Handle error...
        return

    if archon_available:
        mcp__archon__manage_task("update", task_id=task_ids[0], status="done")

    # Phase 2: Parallel tasks (3 simultaneous)
    parallel_task_ids = task_ids[1:4]  # Tasks 2A, 2B, 2C

    if archon_available:
        for task_id in parallel_task_ids:
            mcp__archon__manage_task("update", task_id=task_id, status="doing")

    # Invoke all three in parallel (single message with 3 Task calls)
    Task(subagent_type="prp-gen-codebase-researcher", ...)
    Task(subagent_type="prp-gen-documentation-hunter", ...)
    Task(subagent_type="prp-gen-example-curator", ...)

    if archon_available:
        for task_id in parallel_task_ids:
            mcp__archon__manage_task("update", task_id=task_id, status="done")

    # Phase 3: Gotcha detection
    if archon_available:
        mcp__archon__manage_task("update", task_id=task_ids[4], status="doing")

    Task(subagent_type="prp-gen-gotcha-detective", ...)

    if archon_available:
        mcp__archon__manage_task("update", task_id=task_ids[4], status="done")

    # Phase 4: Assembly
    if archon_available:
        mcp__archon__manage_task("update", task_id=task_ids[5], status="doing")

    Task(subagent_type="prp-gen-assembler", ...)

    if archon_available:
        mcp__archon__manage_task("update", task_id=task_ids[5], status="done")

    # Phase 5: Completion
    if archon_available:
        mcp__archon__manage_project("update",
            project_id=project_id,
            description="COMPLETED: Generated PRP with 8/10 quality score"
        )

        # Store final PRP
        prp_content = Read(f"prps/{feature_name}.md")
        mcp__archon__manage_document("create",
            project_id=project_id,
            title=f"{feature_name}.md",
            content=prp_content,
            document_type="prp"
        )

    print("✅ PRP Generation Complete!")
```

---

## Key Patterns Summary

**ALWAYS:**
1. Health check FIRST
2. Graceful fallback if Archon unavailable
3. Update to "doing" BEFORE starting work
4. Update to "done" AFTER completion
5. Reset to "todo" on errors (for retry)
6. Parallel updates: ALL to "doing", invoke all, ALL to "done"

**NEVER:**
1. Skip health check
2. Fail workflow if Archon unavailable
3. Skip "doing" status
4. Update tasks while subagents running (batch before/after)
5. Use other status values besides todo/doing/done

**CONTEXT PASSING:**
- Include `project_id` in subagent contexts
- Include `archon_available` flag
- Subagents can update their own tasks if needed

---

## When to Use This Pattern

Use Archon workflow pattern when:
- Implementing multi-phase workflows
- Coordinating multiple subagents
- Need progress tracking and visibility
- Want to enable retry/recovery
- Building long-running operations

Don't use when:
- Simple single-step operations
- No subagent coordination needed
- Workflow is < 30 seconds

---

## References

- **Source code example**: `examples/prp_context_cleanup/archon_workflow_example.py`
- **Used by**: `.claude/commands/generate-prp.md`, `.claude/commands/execute-prp.md`
- **Archon MCP docs**: Search Archon knowledge base for latest API details
