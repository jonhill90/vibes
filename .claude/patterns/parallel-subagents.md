# Parallel Subagents - Quick Reference

Execute 3+ independent subagents simultaneously for 3x speedup (14min → 5min).

## CRITICAL: ALL Task() Calls in SINGLE Response

```python
# WRONG - Sequential (sum of task times)
Task(subagent_type="researcher", ...)  # [waits]
Task(subagent_type="hunter", ...)      # Total: 14 min

# RIGHT - Parallel (max of task times)
Task(subagent_type="researcher", ...)
Task(subagent_type="hunter", ...)
Task(subagent_type="curator", ...)
# ALL in SAME response = parallel, Total: 5 min
```

## Core Pattern

```python
# 1. Prepare contexts
researcher_ctx = f'''
You are searching for codebase patterns.
**Task**: Search codebase, extract patterns
**Output**: prps/{feature_name}/planning/codebase-patterns.md
'''
hunter_ctx = f'''[similar]'''
curator_ctx = f'''[similar]'''

# 2. Invoke ALL in SAME response
Task(subagent_type="prp-gen-codebase-researcher",
     description="Search codebase patterns",
     prompt=researcher_ctx)
Task(subagent_type="prp-gen-documentation-hunter",
     description="Find documentation",
     prompt=hunter_ctx)
Task(subagent_type="prp-gen-example-curator",
     description="Extract examples",
     prompt=curator_ctx)
```

## With Task Tracking

```python
# Update ALL to "doing" BEFORE (file-based state)
state = read_json_file(state_path)
for task_id in parallel_task_ids:
    state["tasks"][task_id]["status"] = "doing"
    state["tasks"][task_id]["updated_at"] = current_timestamp()
write_json_file(state_path, state)

# Invoke ALL in SAME response
Task(subagent_type="researcher", prompt=researcher_ctx)
Task(subagent_type="hunter", prompt=hunter_ctx)
Task(subagent_type="curator", prompt=curator_ctx)

# Update ALL to "done" AFTER
state = read_json_file(state_path)
for task_id in parallel_task_ids:
    state["tasks"][task_id]["status"] = "done"
    state["tasks"][task_id]["updated_at"] = current_timestamp()
write_json_file(state_path, state)
```


## Timing & Performance

```python
import time
start = time.time()
# [Invoke parallel tasks]
duration = (time.time() - start) / 60
if duration > 7: print("WARNING: Sequential execution")

# Performance calculation
sequential = sum([5,4,5])  # 14min
parallel = max([5,4,5])    # 5min
speedup = (14-5)/14*100    # 64%
```

## When to Use

**Parallel when**:
- Independent (no dependencies)
- No file conflicts
- No shared state

**Examples**:
```python
# generate-prp Phase 2 - ALWAYS parallel
Task(...) # → planning/codebase-patterns.md
Task(...) # → planning/documentation-links.md
Task(...) # → examples/

# execute-prp - CONDITIONAL
# Group 1 (parallel)
Task(...) # → src/models/user.py
Task(...) # → src/api/users.py
# Group 2 (sequential after)
Task(...) # → tests/ (needs both)
```

## Error Handling & Conflict Check

```python
# Reset failed tasks (file-based state)
failed = [t for t in results if t.status == "failed"]
if failed:
    state = read_json_file(state_path)
    for task in failed:
        state["tasks"][task.id]["status"] = "todo"
        state["tasks"][task.id]["description"] = f"ERROR: {task.error}"
        state["tasks"][task.id]["updated_at"] = current_timestamp()
    write_json_file(state_path, state)

# Check file conflicts before parallelizing
def can_run_in_parallel(tasks):
    all_files = set()
    for task in tasks:
        if all_files & set(task.get('files',[])): return False
        all_files.update(task.get('files',[]))
    return True
```

## Rules

**ALWAYS**:
- Prepare contexts BEFORE invoking
- Invoke ALL in SINGLE response
- Update task state in batches (before/after)
- Validate timing (~max, not sum)
- Limit to 3-6 tasks per group

**NEVER**:
- Invoke in separate responses
- Interleave task state updates
- Parallelize dependent tasks
- Parallelize same file writes
- Exceed 6 parallel tasks

## Anti-Pattern

```python
# WRONG - Loop = sequential
for subagent in ["researcher", "hunter", "curator"]:
    Task(subagent_type=f"prp-gen-{subagent}", ...)
# 14 minutes

# RIGHT - All together = parallel
Task(subagent_type="prp-gen-researcher", ...)
Task(subagent_type="prp-gen-hunter", ...)
Task(subagent_type="prp-gen-curator", ...)
# 5 minutes
```

Working example: `.claude/commands/generate-prp.md` Phase 2
