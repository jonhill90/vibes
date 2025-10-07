# Execute PRP

Multi-subagent system: parallel task execution, automated tests, systematic validation. **PRP File**: $ARGUMENTS

## 5-Phase Workflow

### Phase 0: Setup (YOU)

```python
# 1. Read PRP
prp_path = "$ARGUMENTS"
prp_content = Read(prp_path)

# 2. Security validation (see .claude/patterns/security-validation.md)
import re
def extract_feature_name(filepath: str, strip_prefix: str = None) -> str:
    if ".." in filepath: raise ValueError(f"Path traversal: {filepath}")
    feature = filepath.split("/")[-1].replace(".md", "")
    if strip_prefix: feature = feature.replace(strip_prefix, "")
    if not re.match(r'^[a-zA-Z0-9_-]+$', feature): raise ValueError(f"Invalid: {feature}")
    if len(feature) > 50: raise ValueError(f"Too long: {len(feature)}")
    if any(c in feature for c in ['$','`',';','&','|','>','<','\n','\r']): raise ValueError(f"Dangerous: {feature}")
    return feature

feature_name = extract_feature_name(prp_path)
Bash(f"mkdir -p prps/{feature_name}/execution")

# 3. Extract tasks
tasks = extract_tasks_from_prp(prp_content)

# 4. Archon setup (see .claude/patterns/archon-workflow.md)
health = mcp__archon__health_check()
if health["status"] == "healthy":
    project = mcp__archon__manage_project("create", title=f"PRP: {feature_name}", description=f"From {prp_path}")
    project_id = project["project"]["id"]
    task_mappings = []
    for i, t in enumerate(tasks):
        at = mcp__archon__manage_task("create", project_id=project_id, title=t["name"],
                                       description=t["responsibility"], status="todo", task_order=100-i)
        task_mappings.append({"prp_task": t, "archon_task_id": at["task"]["id"]})
else:
    project_id = None
    task_mappings = tasks
```

### Phase 1: Dependency Analysis

**Subagent**: `prp-exec-task-analyzer` | **Duration**: 2-3 min

```python
Task(subagent_type="prp-exec-task-analyzer", description="Analyze dependencies", prompt=f'''
Analyze PRP tasks for parallel execution.

PRP: {prp_path}, Feature: {feature_name}, Tasks: {len(tasks)}, Archon: {project_id}

Steps:
1. Read PRP "Implementation Blueprint" → "Task List"
2. Analyze dependencies (explicit + file-based)
3. Group into parallel groups (Group 1: independent, Group 2: depends on G1, etc.)
4. Estimate time savings
5. Create prps/{feature_name}/execution/execution-plan.md
''')

execution_plan = Read(f"prps/{feature_name}/execution/execution-plan.md")
groups = parse_execution_groups(execution_plan)
```

### Phase 2: Parallel Implementation

**Subagents**: Multiple `prp-exec-implementer` | **Duration**: 30-50% faster (see `.claude/patterns/parallel-subagents.md`)

```python
for group_number, group in enumerate(groups):
    if group['mode'] == "parallel":
        if archon_available:
            for task in group['tasks']:
                mcp__archon__manage_task("update", task_id=get_archon_task_id(task, task_mappings), status="doing")

        for task in group['tasks']:
            Task(subagent_type="prp-exec-implementer", description=f"Implement {task['name']}", prompt=f'''
Implement single task from PRP.

PRP: {prp_path}, Task: {task['name']}, Responsibility: {task['responsibility']}
Files: {task['files']}, Pattern: {task['pattern']}, Steps: {task['steps']}

Steps: 1. Read PRP, 2. Study pattern, 3. Implement, 4. Validate, 5. Report
CRITICAL: Parallel execution - only modify YOUR task's files.
''')

        if archon_available:
            for task in group['tasks']:
                mcp__archon__manage_task("update", task_id=get_archon_task_id(task, task_mappings), status="done")

    elif group['mode'] == "sequential":
        for task in group['tasks']:
            if archon_available:
                mcp__archon__manage_task("update", task_id=get_archon_task_id(task, task_mappings), status="doing")

            Task(subagent_type="prp-exec-implementer", description=f"Implement {task['name']}", prompt=f'''
Implement task: {task['name']}
PRP: {prp_path}, Files: {task['files']}, Steps: {task['steps']}
''')

            if archon_available:
                mcp__archon__manage_task("update", task_id=get_archon_task_id(task, task_mappings), status="done")
```

### Phase 3: Test Generation

**Subagent**: `prp-exec-test-generator` | **Duration**: 30-60 min

```python
Task(subagent_type="prp-exec-test-generator", description="Generate tests", prompt=f'''
Generate comprehensive tests (70%+ coverage).

PRP: {prp_path}, Implemented: {get_all_modified_files()}, Feature: {feature_name}

Steps: 1. Read files, 2. Find test patterns, 3. Generate unit tests, 4. Generate integration tests,
5. Follow conventions, 6. Ensure pass, 7. Create prps/{feature_name}/execution/test-generation-report.md
''')
```

### Phase 4: Validation

**Subagent**: `prp-exec-validator` | **Duration**: 10-90 min (see `.claude/patterns/quality-gates.md`)

```python
Task(subagent_type="prp-exec-validator", description="Validate", prompt=f'''
Systematic validation with iteration loops (max 5 attempts per level).

PRP: {prp_path}, Implemented: {implemented_files}, Tests: {test_files}

Pattern: .claude/patterns/quality-gates.md (multi-level, error analysis, fix application)

Steps: 1. Read PRP Validation Loop, 2. Execute levels, 3. For failures: analyze → fix → retry (max 5),
4. Document, 5. Create prps/{feature_name}/execution/validation-report.md

CRITICAL: Iterate until pass or max attempts.
''')
```

### Phase 5: Completion (YOU)

```python
validation_report = Read(f"prps/{feature_name}/execution/validation-report.md")
all_passed = check_all_validations_passed(validation_report)
test_report = Read(f"prps/{feature_name}/execution/test-generation-report.md")
coverage = extract_coverage(test_report)
```

**Success** (all passed):
```
✅ PRP Execution Complete!
Feature: {feature_name} | Tasks: {task_count} | Files: {file_count}
Tests: {test_count} ({coverage}%) | Time: {elapsed_time} min | Speedup: {time_saved}%

Validation: Syntax ✅ | Type ✅ | Unit ✅ ({unit_test_count}) | Integration ✅ ({integration_test_count})

Next: 1. git diff, 2. pytest tests/test_{feature}* -v, 3. cat prps/{feature_name}/execution/validation-report.md, 4. Commit
Archon: {project_status}
```

**Partial** (issues):
```
⚠️ Partial Implementation
Feature: {feature_name} | Completed: {completed}/{total} | Tests: {test_file_count} ({coverage}%)
Issues: {validation_failures}

Actions: 1. cat prps/{feature_name}/execution/validation-report.md, 2. Fix {recommendations}, 3. Re-run {failed_commands}
Options: 1. Investigate, 2. Re-run validator, 3. Continue (not recommended)
```

## Error Handling

```python
# Subagent failure
try: Task(...)
except Exception as e:
    if archon_available:
        mcp__archon__manage_task("update", task_id=task_id, status="todo", description=f"ERROR: {e}")
    print("Options: 1. Retry 2. Partial 3. Abort")

# Circular dependency
if circular_dependency_detected:
    print("⚠️ Circular dependency:", dependency_cycle)
    print("Options: 1. Manual order 2. Break dependency 3. Abort")
```

## Quality Gates

```python
["Tasks implemented", "Files created", "Tests generated", "Coverage ≥70%", "Syntax pass",
 "Unit pass", "Integration pass", "Validation pass", "Gotchas addressed"]
```

## Metrics

Tasks: {X}/{total} | Speedup: {X}% | Tests: {X} | Coverage: {X}% | Pass rate: {X}% | Time: {X} min

## Parallel Example

6 tasks: G1(A,B,C parallel→20min) + G2(D,E parallel→20min) + G3(F→20min) = 60min vs 120min sequential = **50% faster**
