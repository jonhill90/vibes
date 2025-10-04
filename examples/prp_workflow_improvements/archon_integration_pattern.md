# Source: .claude/commands/create-initial.md (lines 38-87)
# Pattern: Archon MCP integration for project and task tracking
# Purpose: Shows how to create projects, tasks, and track progress with Archon

## Archon Health Check and Project Setup

```python
# 1. Determine feature name (snake_case)
feature_name = user_input_to_snake_case()  # e.g., "web_scraper", "auth_system"

# 2. Create directories
Bash("mkdir -p prps/research")
Bash(f"mkdir -p examples/{feature_name}")

# 3. Check Archon availability
health = mcp__archon__health_check()
archon_available = health["status"] == "healthy"

# 4. If Archon available, create project and tasks
if archon_available:
    # Create project
    project = mcp__archon__manage_project("create",
        title=f"INITIAL.md: {feature_display_name}",
        description=f"Creating comprehensive INITIAL.md for {feature_description}"
    )
    project_id = project["project"]["id"]

    # Create 6 tasks
    tasks = [
        {"title": "Phase 1: Requirements Analysis", "assignee": "prp-initial-feature-clarifier", "order": 100},
        {"title": "Phase 2A: Codebase Research", "assignee": "prp-initial-codebase-researcher", "order": 90},
        {"title": "Phase 2B: Documentation Hunt", "assignee": "prp-initial-documentation-hunter", "order": 85},
        {"title": "Phase 2C: Example Curation", "assignee": "prp-initial-example-curator", "order": 80},
        {"title": "Phase 3: Gotcha Analysis", "assignee": "prp-initial-gotcha-detective", "order": 75},
        {"title": "Phase 4: Assembly", "assignee": "prp-initial-assembler", "order": 70}
    ]

    task_ids = []
    for task_def in tasks:
        task = mcp__archon__manage_task("create",
            project_id=project_id,
            title=task_def["title"],
            description=f"{task_def['assignee']} - Autonomous execution",
            status="todo",
            assignee=task_def["assignee"],
            task_order=task_def["order"]
        )
        task_ids.append(task["task"]["id"])
else:
    project_id = None
    task_ids = []

# 5. Proceed to Phase 1
```

## Task Status Updates

```python
# Before starting a phase
if archon_available:
    mcp__archon__manage_task("update", task_id=task_ids[0], status="doing")

# After completing a phase
if archon_available:
    mcp__archon__manage_task("update", task_id=task_ids[0], status="done")
```

## Parallel Task Updates

```python
# Update multiple tasks to "doing" before parallel execution
if archon_available:
    for i in [1, 2, 3]:  # Tasks 2A, 2B, 2C
        mcp__archon__manage_task("update", task_id=task_ids[i], status="doing")

# After all parallel tasks complete
if archon_available:
    for i in [1, 2, 3]:
        mcp__archon__manage_task("update", task_id=task_ids[i], status="done")
```

## Error Handling

```python
try:
    invoke_subagent("agent-name", context)
except SubagentError as e:
    # Log error
    logger.error(f"Phase X failed: {e}")

    # Update Archon if available
    if archon_available:
        mcp__archon__manage_task("update", task_id=task_id,
            description=f"ERROR: {e}",
            status="todo"  # Reset to allow retry
        )

    # Inform user
    print(f"⚠️ Phase X encountered an issue: {e}")
    print("Would you like me to:")
    print("1. Retry this phase")
    print("2. Continue with partial results")
    print("3. Abort workflow")

    # Wait for user decision
```

## Fallback Pattern

```python
# Proceed without tracking if Archon unavailable
# Workflow continues normally, just no Archon project/task updates
if not archon_available:
    print("ℹ️ Archon MCP not available - proceeding without project tracking")
```

## Project Completion

```python
# Update project with final notes
mcp__archon__manage_project("update",
    project_id=project_id,
    description=f"COMPLETED: Generated INITIAL.md with {example_count} examples, quality score: {score}/10"
)

# Store final document in Archon
mcp__archon__manage_document("create",
    project_id=project_id,
    title=f"INITIAL_{feature_name}.md",
    content=initial_md_content,
    document_type="initial"
)
```

## Key Patterns to Mimic

1. **Health Check First**: Always check Archon availability before attempting operations
2. **Graceful Fallback**: Continue workflow even if Archon unavailable
3. **Task Status Flow**: todo → doing → done (or back to todo on error)
4. **Task Order**: Higher number = higher priority (0-100)
5. **Context Passing**: Include project_id in subagent context
6. **Error Handling**: Reset task status on failure to allow retry
7. **Progress Visibility**: Update task status throughout workflow
8. **Document Storage**: Store final outputs as Archon documents

This pattern should be used in both improved generate-prp and execute-prp commands.
