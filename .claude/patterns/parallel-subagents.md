# Parallel Subagent Execution Pattern

**Purpose**: Execute multiple independent subagents simultaneously for 3x speedup through parallel task invocation.

**Use When**: 3+ independent tasks can run simultaneously without file conflicts or data dependencies.

**Performance Impact**: Sequential execution takes 14 minutes, parallel takes 5 minutes = 64% faster.

---

## The CRITICAL Rule: ALL in SINGLE Response

The key to parallel execution is invoking ALL Task tools in ONE response before waiting for any results.

### WRONG (Sequential - 14 minutes)

```python
# This executes tasks one at a time (SLOW)
Task(subagent_type="prp-gen-codebase-researcher", ...)
# [System waits for completion - 5 minutes]
Task(subagent_type="prp-gen-documentation-hunter", ...)
# [System waits for completion - 4 minutes]
Task(subagent_type="prp-gen-example-curator", ...)
# [System waits for completion - 5 minutes]
# Total: 14 minutes
```

### CORRECT (Parallel - 5 minutes)

```python
# 1. Prepare ALL contexts first (don't invoke yet)
researcher_ctx = f'''
You are searching for codebase patterns.
**Your Task**: Search codebase, extract patterns
**Output**: prps/{feature_name}/planning/codebase-patterns.md
'''

hunter_ctx = f'''
You are finding official documentation.
**Your Task**: Search docs, find examples
**Output**: prps/{feature_name}/planning/documentation-links.md
'''

curator_ctx = f'''
You are extracting code examples.
**Your Task**: Extract code, create README
**Output**: prps/{feature_name}/examples/
'''

# 2. Invoke ALL THREE in THIS SAME RESPONSE (before any wait)
print("Invoking 3 subagents in parallel...")

Task(subagent_type="prp-gen-codebase-researcher",
     description="Search codebase patterns",
     prompt=researcher_ctx)

Task(subagent_type="prp-gen-documentation-hunter",
     description="Find official documentation",
     prompt=hunter_ctx)

Task(subagent_type="prp-gen-example-curator",
     description="Extract code examples",
     prompt=curator_ctx)

# 3. System automatically waits for ALL to complete
# Total: max(5, 4, 5) = 5 minutes
```

**Key Insight**: All three Task calls happen in the SAME message before Claude Code waits. This triggers parallel execution.

---

## Performance Math (INCLUDE THIS!)

**Always calculate and communicate time savings:**

```
Sequential Execution:
- Researcher: 5 minutes
- Hunter: 4 minutes
- Curator: 5 minutes
Total: 5 + 4 + 5 = 14 minutes

Parallel Execution:
- All three run simultaneously
Total: max(5, 4, 5) = 5 minutes

Speedup: (14 - 5) / 14 = 64% faster
```

**General formula:**
- Sequential time = sum of all task times
- Parallel time = max task time in group
- Speedup % = (sequential - parallel) / sequential * 100

---

## Archon Task Updates

When using Archon task tracking with parallel execution:

```python
# BEFORE parallel invocation: Update ALL to "doing"
if archon_available:
    for task_id in [task_2a, task_2b, task_2c]:
        mcp__archon__manage_task("update",
            task_id=task_id,
            status="doing"
        )

# [Invoke all tasks in parallel - see above]

# AFTER ALL complete: Update ALL to "done"
if archon_available:
    for task_id in [task_2a, task_2b, task_2c]:
        mcp__archon__manage_task("update",
            task_id=task_id,
            status="done"
        )
```

**Important**: Don't interleave Archon updates with Task invocations. Do all Archon updates BEFORE parallel invocation, then all after completion.

---

## Timing Validation

Add timing checks to verify parallel execution is working:

```python
import time

# Start timing
phase2_start = time.time()

# [Prepare contexts and invoke parallel tasks]

# End timing
phase2_duration = time.time() - phase2_start
phase2_minutes = phase2_duration / 60

print(f"⏱️ Phase 2 completed in {phase2_minutes:.1f} minutes")

# Validate it was actually parallel
expected_parallel_max = 7 * 60  # 7 minutes (with buffer)
if phase2_duration > expected_parallel_max:
    print(f"⚠️ WARNING: Phase 2 took {phase2_minutes:.1f}min (expected <7min)")
    print("Possible issue: Tasks may have executed sequentially instead of parallel")
    print("Check that all Task calls were in the SAME response")
```

**Why this matters**: If timing validation fails, it indicates the parallel pattern was broken and speedup was lost.

---

## When to Use Parallel Execution

Use parallel execution when tasks are:

✅ **Independent**: No task depends on another's output
✅ **No file conflicts**: Different output files
✅ **Separate contexts**: No shared state

### Examples

**generate-prp Phase 2** - ALWAYS parallel:
- Codebase researcher → `prps/{feature}/planning/codebase-patterns.md`
- Documentation hunter → `prps/{feature}/planning/documentation-links.md`
- Example curator → `prps/{feature}/examples/`
- Result: 3 different outputs, no dependencies = safe to parallelize

**execute-prp Phase 2** - CONDITIONAL (check dependencies):
- Task A → creates `src/models/user.py`
- Task B → creates `src/api/users.py`
- Task C → creates `tests/test_users.py` (depends on A and B)
- Result: A and B can run in parallel (Group 1), C runs after (Group 2)

**Test generation** - NEVER parallel:
- Single comprehensive task generating all tests
- Not parallelizable

**Validation** - NEVER parallel:
- Sequential by nature (Level 1 → Level 2 → Level 3)
- Not parallelizable

---

## Common Patterns

### Pattern 1: Research Phase (generate-prp)

```python
# 3 independent research tasks
print("🚀 Phase 2: Parallel Research (3 subagents simultaneously)")

# Prepare all contexts
contexts = {
    "researcher": create_researcher_context(feature_name),
    "hunter": create_hunter_context(feature_name),
    "curator": create_curator_context(feature_name)
}

# Update Archon tasks (before invocation)
if archon_available:
    for task_id in research_task_ids:
        mcp__archon__manage_task("update", task_id=task_id, status="doing")

# Invoke ALL in SINGLE response
Task(subagent_type="prp-gen-codebase-researcher",
     description="Search codebase patterns",
     prompt=contexts["researcher"])

Task(subagent_type="prp-gen-documentation-hunter",
     description="Find documentation",
     prompt=contexts["hunter"])

Task(subagent_type="prp-gen-example-curator",
     description="Extract code examples",
     prompt=contexts["curator"])

# Mark complete (after all finish)
if archon_available:
    for task_id in research_task_ids:
        mcp__archon__manage_task("update", task_id=task_id, status="done")
```

### Pattern 2: Implementation Groups (execute-prp)

```python
# Execute tasks in groups based on dependencies
for group_number, group in enumerate(execution_groups):
    print(f"\n🔧 Group {group_number + 1}: {len(group['tasks'])} tasks ({group['mode']})")

    if group['mode'] == "parallel":
        # Update Archon
        if archon_available:
            for task in group['tasks']:
                mcp__archon__manage_task("update",
                    task_id=get_task_id(task),
                    status="doing")

        # Prepare contexts for all tasks in group
        for task in group['tasks']:
            ctx = create_implementer_context(task)

            # Invoke implementer (all in same response)
            Task(subagent_type="prp-exec-implementer",
                 description=f"Implement {task['name']}",
                 prompt=ctx)

        # Mark complete
        if archon_available:
            for task in group['tasks']:
                mcp__archon__manage_task("update",
                    task_id=get_task_id(task),
                    status="done")

    elif group['mode'] == "sequential":
        # Execute one at a time
        for task in group['tasks']:
            # [Single task invocation]
```

---

## Error Handling

### If One Parallel Task Fails

```python
# After parallel execution completes
results = check_task_results()

failed_tasks = [t for t in results if t.status == "failed"]

if failed_tasks:
    print(f"⚠️ {len(failed_tasks)} parallel tasks failed:")
    for task in failed_tasks:
        print(f"  - {task.name}: {task.error}")

    # Reset failed tasks in Archon
    if archon_available:
        for task in failed_tasks:
            mcp__archon__manage_task("update",
                task_id=task.archon_id,
                status="todo",
                description=f"ERROR: {task.error}"
            )

    print("\nOptions:")
    print("1. Retry just the failed tasks")
    print("2. Continue with partial results")
    print("3. Abort workflow")
```

### File Conflict Detection

```python
# Before parallelizing, check for conflicts
def can_run_in_parallel(tasks):
    all_files = set()
    for task in tasks:
        task_files = set(task.get('files', []))
        if all_files & task_files:  # Intersection exists
            return False  # File conflict!
        all_files.update(task_files)
    return True

if can_run_in_parallel(group_tasks):
    # Safe to parallelize
else:
    print("⚠️ File conflicts detected - executing sequentially")
    group['mode'] = "sequential"
```

---

## Validation Checklist

Before using parallel execution, verify:

- [ ] All tasks are truly independent (no hidden dependencies)
- [ ] No file conflicts (each task modifies different files)
- [ ] All Task calls are in SINGLE response (not in loop with waits)
- [ ] Archon updates happen BEFORE and AFTER (not interleaved)
- [ ] Timing validation added (check duration < expected parallel max)
- [ ] Error handling accounts for partial failures

---

## Maximum Parallelization

**Practical limits:**
- generate-prp Phase 2: 3 parallel tasks (optimal)
- execute-prp Phase 2: Up to 5-6 parallel tasks per group
- More than 6 parallel tasks may be overwhelming

**Why limit?**: Too many parallel tasks can:
- Overwhelm system resources
- Make error tracking difficult
- Reduce individual task quality
- Complicate debugging

**Recommendation**: Group tasks into batches of 3-6 for best results.

---

## Success Metrics

After parallel execution, report:

```python
print(f"""
✅ Parallel Execution Complete

Group {group_num}: {len(tasks)} tasks
- Mode: PARALLEL
- Sequential time estimate: {sequential_time:.1f} min
- Actual parallel time: {parallel_time:.1f} min
- Speedup achieved: {speedup_percent:.0f}%
- All tasks completed: {success_rate}%
""")
```

---

## Related Patterns

- **archon-workflow.md**: Task management and status updates
- **error-handling.md**: Subagent failure recovery
- **quality-gates.md**: Validation after parallel execution

---

## Quick Reference

**Need to parallelize?**

1. Check tasks are independent (no dependencies, no file conflicts)
2. Prepare ALL contexts first
3. Update ALL Archon tasks to "doing"
4. Invoke ALL Task tools in SINGLE response
5. Wait for completion (automatic)
6. Update ALL Archon tasks to "done"
7. Validate timing (should be ~max task time, not sum)

**Key insight**: The SINGLE response is what triggers parallelism. If you invoke tasks in separate responses, they execute sequentially.
