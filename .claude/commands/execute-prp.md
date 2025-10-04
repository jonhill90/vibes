# Execute PRP

Orchestrates PRP execution: a multi-subagent system that implements features through parallel task execution, automated test generation, and systematic validation.

## PRP File: $ARGUMENTS

Implement a feature using the PRP file with a 5-phase multi-subagent approach. Execute independent tasks in parallel for 30-50% faster implementation.

## The 5-Phase Workflow

### Phase 0: Load & Setup (YOU handle this)

**Immediate Actions**:

1. ✅ Acknowledge the PRP execution request
2. ✅ Read the PRP file to understand all requirements
3. ✅ Extract feature name from PRP
4. ✅ Check Archon availability
5. ✅ Create Archon project and tasks from PRP
6. ✅ Proceed to Phase 1 (task dependency analysis)

**Setup Process**:

```python
# 1. Read PRP
prp_path = "$ARGUMENTS"
prp_content = Read(prp_path)

# 2. Extract feature name
# From file name: prps/user_auth.md → "user_auth"
# Or from PRP Goal section
feature_name = extract_feature_name(prp_path, prp_content)

# 3. Extract all tasks from PRP Implementation Blueprint
# Look for "Task List (Execute in Order)" section
tasks = extract_tasks_from_prp(prp_content)
# Each task has: name, responsibility, files, steps, validation

# 4. Check Archon availability
health = mcp__archon__health_check()
archon_available = health["status"] == "healthy"

# 5. If Archon available, create project and tasks
if archon_available:
    # Create project
    project = mcp__archon__manage_project("create",
        title=f"PRP Execution: {feature_name}",
        description=f"Implementing feature from {prp_path}"
    )
    project_id = project["project"]["id"]

    # Create Archon task for each PRP task
    task_mappings = []  # Maps PRP task to Archon task ID
    for i, prp_task in enumerate(tasks):
        archon_task = mcp__archon__manage_task("create",
            project_id=project_id,
            title=prp_task["name"],
            description=prp_task["responsibility"],
            status="todo",
            task_order=100 - i  # Higher order = higher priority
        )
        task_mappings.append({
            "prp_task": prp_task,
            "archon_task_id": archon_task["task"]["id"]
        })
else:
    project_id = None
    task_mappings = tasks  # Just use PRP tasks without Archon IDs

# 6. Proceed to Phase 1 (dependency analysis)
```

---

### Phase 1: Dependency Analysis

**Subagent**: `prp-exec-task-analyzer`
**Mode**: AUTONOMOUS
**Duration**: 2-3 minutes

**Your Actions**:

```python
# 1. Prepare context for analyzer
context = f'''You are analyzing PRP tasks to create an optimal execution plan with parallel task grouping.

**PRP File**: {prp_path}
**Feature Name**: {feature_name}
**Total Tasks**: {len(tasks)}
**Archon Project ID**: {project_id if archon_available else "Not available"}

**Your Task**:
1. Read the PRP file thoroughly
2. Extract all tasks from "Implementation Blueprint" → "Task List"
3. Analyze dependencies (explicit: "after Task X", implicit: file dependencies)
4. Group tasks into parallel execution groups
5. Create execution plan with:
   - Group 1: Independent tasks (run in parallel)
   - Group 2: Tasks depending on Group 1 (run in parallel)
   - Group 3+: Continue until all tasks grouped
6. Estimate time savings from parallelization
7. Create prps/execution-plan.md

**Output**: prps/execution-plan.md with task grouping strategy
'''

# 2. Invoke analyzer
Task(subagent_type="prp-exec-task-analyzer",
     description="Analyze task dependencies",
     prompt=context)

# 3. Wait for completion - analyzer creates execution-plan.md

# 4. Read execution plan
execution_plan = Read("prps/execution-plan.md")
groups = parse_execution_groups(execution_plan)
```

**Expected Output**: `prps/execution-plan.md` with task groups

---

### Phase 2: Parallel Task Implementation

**Subagents**: Multiple `prp-exec-implementer` instances (one per task)
**Mode**: PARALLEL or SEQUENTIAL based on execution plan
**Duration**: Varies by complexity (30-50% faster than sequential)

**Your Actions**:

```python
# For each execution group in the plan
for group_number, group in enumerate(groups):
    print(f"\n🔧 Executing Group {group_number + 1}: {len(group['tasks'])} tasks")
    print(f"Mode: {group['mode']}")  # PARALLEL or SEQUENTIAL

    if group['mode'] == "parallel":
        # ⚠️ CRITICAL: Parallel execution for independent tasks
        # Update all Archon tasks in this group to "doing"
        if archon_available:
            for task in group['tasks']:
                archon_task_id = get_archon_task_id(task, task_mappings)
                mcp__archon__manage_task("update",
                    task_id=archon_task_id,
                    status="doing"
                )

        # Prepare context for each implementer
        implementer_contexts = []
        for task in group['tasks']:
            ctx = f'''You are implementing a single task from the PRP execution plan.

**PRP File**: {prp_path}
**Task Name**: {task['name']}
**Responsibility**: {task['responsibility']}
**Files to Modify**: {task['files']}
**Pattern to Follow**: {task['pattern']}
**Specific Steps**: {task['steps']}
**Validation**: {task['validation']}
**Dependencies Complete**: {task['dependencies_complete']}

**Your Task**:
1. Read the full PRP for context
2. Study the pattern referenced (from PRP examples or codebase)
3. Implement all specific steps
4. Follow PRP codebase patterns
5. Avoid gotchas documented in PRP
6. Run validation for this task
7. Report completion

**CRITICAL**: You may be running in parallel with other implementers. Only modify files in YOUR task's file list.

**Output**: Implemented code + validation results
'''
            implementer_contexts.append((task, ctx))

        # ⚠️ CRITICAL: Invoke ALL implementers in SINGLE message
        print(f"Invoking {len(group['tasks'])} implementers in parallel...")
        '''
        # Invoke all implementers simultaneously
        for task, ctx in implementer_contexts:
            Task(subagent_type="prp-exec-implementer",
                 description=f"Implement {task['name']}",
                 prompt=ctx)

        # Mark all complete (after all finish)
        if archon_available:
            for task in group['tasks']:
                archon_task_id = get_archon_task_id(task, task_mappings)
                mcp__archon__manage_task("update",
                    task_id=archon_task_id,
                    status="done"
                )

    elif group['mode'] == "sequential":
        # Sequential execution for dependent tasks
        for task in group['tasks']:
            print(f"Implementing {task['name']}...")

            if archon_available:
                archon_task_id = get_archon_task_id(task, task_mappings)
                mcp__archon__manage_task("update",
                    task_id=archon_task_id,
                    status="doing"
                )

            ctx = f'''You are implementing a single task from the PRP.

**PRP File**: {prp_path}
**Task Name**: {task['name']}
**Responsibility**: {task['responsibility']}
**Files to Modify**: {task['files']}
**Pattern to Follow**: {task['pattern']}
**Specific Steps**: {task['steps']}
**Validation**: {task['validation']}

**Your Task**: Implement this task following PRP guidance.

**Output**: Implemented code + validation results
'''

            Task(subagent_type="prp-exec-implementer",
                 description=f"Implement {task['name']}",
                 prompt=ctx)

            if archon_available:
                mcp__archon__manage_task("update",
                    task_id=archon_task_id,
                    status="done"
                )

    print(f"✅ Group {group_number + 1} complete")
```

**Expected Output**: All files created/modified per PRP specifications

---

### Phase 3: Test Generation

**Subagent**: `prp-exec-test-generator`
**Mode**: AUTONOMOUS
**Duration**: 30-60 minutes

**Your Actions**:

```python
# 1. Collect all implemented files
implemented_files = get_all_modified_files()  # From git status or tracking

# 2. Prepare context for test generator
context = f'''You are generating comprehensive tests for implemented code.

**PRP File**: {prp_path}
**Implemented Files**: {implemented_files}
**Feature Name**: {feature_name}
**Validation Requirements**: (from PRP Validation Loop section)

**Your Task**:
1. Read all implemented files
2. Search codebase for existing test patterns
3. Generate unit tests for all functions/classes
4. Generate integration tests for workflows
5. Follow codebase test conventions
6. Aim for 70%+ coverage
7. Ensure all tests pass
8. Create test-generation-report.md

**Output**:
- tests/test_{feature}_*.py (multiple test files)
- prps/test-generation-report.md
'''

# 3. Invoke test generator
Task(subagent_type="prp-exec-test-generator",
     description="Generate comprehensive tests",
     prompt=context)

# 4. Wait for completion
```

**Expected Output**:
- Test files in `tests/`
- `prps/test-generation-report.md`

---

### Phase 4: Systematic Validation

**Subagent**: `prp-exec-validator`
**Mode**: AUTONOMOUS with iteration loops
**Duration**: 10-90 minutes (depending on issues found)

**Your Actions**:

```python
# 1. Extract validation commands from PRP
validation_commands = extract_validation_commands(prp_content)
# From PRP "Validation Loop" section:
# Level 1: Syntax checks
# Level 2: Unit tests
# Level 3: Integration tests
# etc.

# 2. Prepare context for validator
context = f'''You are running systematic validation for implemented code.

**PRP File**: {prp_path}
**Implemented Files**: {implemented_files}
**Test Files**: {test_files}
**Validation Gates**: (from PRP Validation Loop section)

**Your Task**:
1. Read the PRP Validation Loop section
2. Execute each validation level in order
3. For each failure:
   - Analyze error messages
   - Check PRP gotchas for guidance
   - Apply fixes
   - Re-run validation
   - Iterate until pass (max 5 attempts per level)
4. Document all issues found and fixed
5. Create comprehensive validation-report.md

**CRITICAL**: Iterate on failures. Don't give up until all tests pass or max attempts reached.

**Output**: prps/validation-report.md with all results
'''

# 3. Invoke validator
Task(subagent_type="prp-exec-validator",
     description="Validate implementation",
     prompt=context)

# 4. Wait for completion - validator will iterate on failures
```

**Expected Output**: `prps/validation-report.md`

---

### Phase 5: Completion & Reporting (YOU handle this)

**Final Validation Check**:

```python
# 1. Read validation report
validation_report = Read("prps/validation-report.md")

# 2. Check if all validations passed
all_passed = check_all_validations_passed(validation_report)

# 3. Read test generation report
test_report = Read("prps/test-generation-report.md")
coverage = extract_coverage(test_report)
```

**Success Message** (if all passed):

```markdown
✅ **PRP Execution Complete!**

**Feature**: {feature_name}
**PRP**: {prp_path}

**Implementation Summary**:
- Tasks Completed: {task_count}
- Parallel Execution Groups: {group_count}
- Time Saved by Parallelization: ~{time_saved}%
- Files Created/Modified: {file_count}

**Test Results**:
- Test Files Generated: {test_file_count}
- Total Tests: {test_count}
- Test Coverage: {coverage}%
- All Tests Passing: ✅

**Validation Results**:
- Syntax Checks: ✅ Pass
- Type Checks: ✅ Pass
- Unit Tests: ✅ Pass ({unit_test_count} tests)
- Integration Tests: ✅ Pass ({integration_test_count} tests)

**Total Implementation Time**: {elapsed_time} minutes

**Files Modified**:
{list_of_modified_files}

**Next Steps**:

1. **Review the implementation** (recommended):
   ```bash
   git diff
   ```

2. **Run tests yourself** (optional verification):
   ```bash
   pytest tests/test_{feature}* -v
   ```

3. **Review validation report** (see what was fixed):
   ```bash
   cat prps/validation-report.md
   ```

4. **Commit changes** (when ready):
   ```bash
   git add .
   git commit -m "Implement {feature_name}

   - {task_1_summary}
   - {task_2_summary}
   ...

   🤖 Generated with Claude Code
   Co-Authored-By: Claude <noreply@anthropic.com>"
   ```

**Archon Project**: {if available, show project status or URL}

Great work! The feature is fully implemented, tested, and validated. Ready for code review or deployment.
```

**Partial Success Message** (if some validations failed):

```markdown
⚠️ **PRP Execution Complete with Issues**

**Feature**: {feature_name}
**Status**: Partial implementation

**What Was Completed**:
- Tasks Implemented: {completed_task_count}/{total_task_count}
- Tests Generated: {test_file_count} files
- Test Coverage: {coverage}%

**Validation Issues**:
{list_validation_failures}

**Recommended Actions**:

1. **Review validation report for details**:
   ```bash
   cat prps/validation-report.md
   ```

2. **Address remaining issues**:
   {specific_recommendations_from_validator}

3. **Re-run validation manually**:
   ```bash
   {validation_commands_that_failed}
   ```

Would you like me to:
1. Investigate specific failures
2. Re-run the validator
3. Continue despite failures (not recommended)
```

**Update Archon** (if available):

```python
# Add final notes to project
mcp__archon__manage_project("update",
    project_id=project_id,
    description=f"COMPLETED: {task_count} tasks, {test_count} tests, {coverage}% coverage, all validations {'passed' if all_passed else 'partial'}"
)
```

---

## Error Handling

### If Subagent Fails

```python
try:
    Task(subagent_type="agent-name", description="task", prompt=context)
except Exception as e:
    print(f"⚠️ Phase failed: {e}")

    # Update Archon
    if archon_available:
        # Reset relevant tasks to "todo"
        for task_id in affected_tasks:
            mcp__archon__manage_task("update",
                task_id=task_id,
                status="todo",
                description=f"ERROR: {e}"
            )

    # Offer recovery
    print("Would you like me to:")
    print("1. Retry this phase")
    print("2. Continue with partial results")
    print("3. Abort execution")
```

### If Task Dependencies Wrong

```python
# Task analyzer found circular dependency
if circular_dependency_detected:
    print("⚠️ Circular dependency detected in tasks:")
    print(dependency_cycle)
    print("\nOptions:")
    print("1. Manually specify execution order")
    print("2. Break the dependency (requires PRP modification)")
    print("3. Abort execution")
```

### If Tests Don't Pass

```python
# After test generation, if tests fail
if test_failures:
    print(f"⚠️ {len(test_failures)} tests failing after generation")
    print("This is normal - the validator will fix them.")
    print("Proceeding to validation phase...")
    # Validator will iterate on these failures
```

---

## Quality Gates

Before reporting completion:

```python
quality_checks = [
    "All PRP tasks implemented",
    "All files created/modified as specified",
    "Tests generated for all components",
    "Test coverage >= 70%",
    "All syntax checks pass",
    "All unit tests pass",
    "All integration tests pass",
    "All validation gates from PRP pass",
    "Known gotchas from PRP addressed"
]

issues = []
for check in quality_checks:
    if not verify_check(check):
        issues.append(check)

# Report issues if any
```

---

## Success Metrics

Track and report:

- ✅ Tasks completed: {X}/{total}
- ✅ Parallel execution speedup: {X}%
- ✅ Tests generated: {X} test files
- ✅ Test coverage: {X}% (target: 70%+)
- ✅ Validation pass rate: {X}% (target: 100%)
- ✅ Implementation time: {X} minutes
- ✅ Archon tasks: {X} completed

---

## Key Differences from Old execute-prp

**OLD Approach** ❌:
- Sequential task execution (slow)
- Uses TodoWrite (violates ARCHON-FIRST RULE)
- Manual test writing
- No automated validation iteration
- No time tracking

**NEW Approach** ✅:
- Parallel task execution (30-50% faster)
- Archon task management (ARCHON-FIRST compliant)
- Automated test generation (70%+ coverage)
- Systematic validation with fix iteration
- Time tracking and success metrics

---

## Parallel Execution Details

**Phase 2 Parallelization**:

For a PRP with 6 tasks:
- Group 1: Tasks A, B, C (independent) → 3 parallel implementers → 20 min (not 60 min)
- Group 2: Tasks D, E (depend on Group 1) → 2 parallel implementers → 20 min (not 40 min)
- Group 3: Task F (depends on D, E) → 1 implementer → 20 min

**Total**: 60 minutes parallel vs. 120 minutes sequential = **50% faster**

**Implementation**: Use Task tool multiple times in SINGLE message per group.

---

## ULTRATHINK Reminder

**Before starting Phase 2 implementation**, perform ULTRATHINK:

```
*** CRITICAL: ULTRATHINK ABOUT EXECUTION PLAN ***

Review execution plan:
1. Are task dependencies correct?
2. Is parallelization safe (no file conflicts)?
3. Do we have all context from PRP?
4. Are gotchas from PRP understood?
5. Is validation strategy clear?

If any concerns, address before proceeding.
```

---

Remember: The goal is reliable, tested implementation following PRP specifications with 30-50% time savings through intelligent parallelization.
