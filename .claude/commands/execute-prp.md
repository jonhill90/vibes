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
from pathlib import Path

def extract_feature_name(filepath: str, strip_prefix: str = None, validate_no_redundant: bool = True) -> str:
    """6-level security validation for feature names (see .claude/patterns/security-validation.md).

    Args:
        filepath: Path to PRP file (e.g., "prps/INITIAL_feature.md")
        strip_prefix: Optional prefix to strip (e.g., "INITIAL_")
        validate_no_redundant: If True, reject prp_ prefix (strict for new PRPs)

    Returns:
        Validated feature name

    Raises:
        ValueError: If validation fails with actionable error message
    """
    # Whitelist of allowed prefixes (security enhancement)
    ALLOWED_PREFIXES = {"INITIAL_", "EXAMPLE_"}

    # Level 1: Path traversal in full path
    if ".." in filepath: raise ValueError(f"Path traversal: {filepath}")

    # Extract basename, remove extension
    feature = filepath.split("/")[-1].replace(".md", "")

    # Validate strip_prefix parameter itself (prevents path traversal via parameter)
    if strip_prefix:
        if strip_prefix not in ALLOWED_PREFIXES:
            raise ValueError(
                f"Invalid strip_prefix: '{strip_prefix}'\n"
                f"Allowed prefixes: {', '.join(ALLOWED_PREFIXES)}\n"
                f"Never use 'prp_' as strip_prefix"
            )
        # CRITICAL FIX: Use removeprefix() instead of replace()
        # removeprefix() only removes the prefix from START of string (if present)
        # replace() would remove ALL occurrences (bug if prefix appears multiple times)
        # Example: "INITIAL_INITIAL_test" with replace("INITIAL_", "") → "test" (WRONG - both removed)
        # Example: "INITIAL_INITIAL_test" with removeprefix("INITIAL_") → "INITIAL_test" (CORRECT)
        feature = feature.removeprefix(strip_prefix)

        # Check for empty result after stripping
        if not feature:
            raise ValueError(
                f"Empty feature name after stripping prefix '{strip_prefix}'\n"
                f"File: {filepath}\n"
                f"Fix: Rename file with actual feature name after prefix"
            )

    # Level 2: Whitelist (alphanumeric + _ - only)
    if not re.match(r'^[a-zA-Z0-9_-]+$', feature): raise ValueError(f"Invalid: {feature}")

    # Level 3: Length (max 50 chars)
    if len(feature) > 50: raise ValueError(f"Too long: {len(feature)}")

    # Level 4: Directory traversal in extracted name
    if ".." in feature or "/" in feature or "\\" in feature: raise ValueError(f"Path traversal: {feature}")

    # Level 5: Command injection
    if any(c in feature for c in ['$','`',';','&','|','>','<','\n','\r']): raise ValueError(f"Dangerous: {feature}")

    # Level 6: Redundant prefix validation (NEW - from Task 4)
    if validate_no_redundant and feature.startswith("prp_"):
        raise ValueError(
            f"❌ Redundant 'prp_' prefix detected: '{feature}'\n"
            f"\n"
            f"PROBLEM: Files are in prps/ directory - prefix is redundant\n"
            f"EXPECTED: '{feature.removeprefix('prp_')}'\n"
            f"\n"
            f"RESOLUTION:\n"
            f"Rename: prps/{feature}.md → prps/{feature.removeprefix('prp_')}.md\n"
            f"\n"
            f"See: .claude/conventions/prp-naming.md for naming rules"
        )

    return feature

# Auto-detect INITIAL_ prefix in filename (improves developer experience)
# Developers no longer need to remember to use strip_prefix parameter
# If filename starts with INITIAL_, automatically strip it for directory naming
filename = prp_path.split("/")[-1]

# BACKWARD COMPATIBILITY: Use validate_no_redundant=False for existing PRPs
# This allows legacy PRPs with prp_ prefix to execute with warnings instead of errors
# New PRPs will be validated strictly by generate-prp.md with validate_no_redundant=True
try:
    if filename.startswith("INITIAL_"):
        # Strip INITIAL_ prefix for directory naming
        feature_name = extract_feature_name(prp_path, strip_prefix="INITIAL_", validate_no_redundant=False)
    else:
        # No prefix to strip, but still validate (permissive mode)
        feature_name = extract_feature_name(prp_path, validate_no_redundant=False)
except ValueError as e:
    # Graceful handling: warn but continue execution for backward compatibility
    print(f"⚠️ WARNING: Naming convention issue detected:")
    print(str(e))
    print("\nThis PRP may not follow current naming standards.")
    print("Continuing execution for backward compatibility...")
    # Extract feature name without validation for legacy support
    feature_name = prp_path.split("/")[-1].replace(".md", "")
    if filename.startswith("INITIAL_"):
        feature_name = feature_name.removeprefix("INITIAL_")

Bash(f"mkdir -p prps/{feature_name}/execution")

# 3. Validation Gate Functions (see prps/prp_execution_reliability/examples/)

class ValidationError(Exception):
    """
    Raised when validation gates fail.

    Use this for ALL validation failures that should stop execution.
    Error message should be actionable (include paths, troubleshooting, resolution).
    """
    pass

def format_missing_report_error(task_number: int, feature_name: str, report_type: str = "COMPLETION") -> str:
    """
    Generate actionable error message for missing report.

    Pattern: Problem → Expected Path → Impact → Troubleshooting → Resolution
    Source: prps/prp_execution_reliability/examples/error_message_pattern.py
    """
    report_path = f"prps/{feature_name}/execution/TASK{task_number}_{report_type}.md"
    template_path = f".claude/templates/task-{report_type.lower()}-report.md"

    return f"""
{'='*80}
❌ VALIDATION GATE FAILED: Missing Task Report
{'='*80}

PROBLEM:
  Task {task_number} did not generate required completion report.

EXPECTED PATH:
  {report_path}

IMPACT:
  This task is INCOMPLETE without documentation.
  - Cannot audit what was implemented
  - Cannot learn from implementation decisions
  - Cannot debug issues in the future
  - Violates PRP execution reliability requirements

TROUBLESHOOTING:
  1. Check if subagent execution completed successfully
     → Review subagent output logs for errors or exceptions

  2. Verify template exists and is accessible
     → Check: {template_path}
     → Ensure template has correct variable placeholders

  3. Check file system permissions
     → Directory: prps/{feature_name}/execution/
     → Ensure write permissions enabled

  4. Review subagent prompt
     → Confirm report generation is marked as CRITICAL
     → Verify exact path specification in prompt

  5. Check for naming issues
     → Standard format: TASK{{number}}_{{TYPE}}.md
     → Wrong: TASK_{task_number}_COMPLETION.md (extra underscore)
     → Wrong: TASK{task_number}_COMPLETE.md (COMPLETE vs COMPLETION)
     → Correct: TASK{task_number}_COMPLETION.md

RESOLUTION OPTIONS:

  Option 1 (RECOMMENDED): Re-run task with explicit report requirement
    → Update subagent prompt to emphasize report is MANDATORY
    → Add validation check immediately after task completion

  Option 2: Manually create report
    → Use template: {template_path}
    → Save to: {report_path}
    → Fill in all required sections

  Option 3: Debug subagent execution
    → Review full subagent output for Write() tool errors
    → Check template variable substitution
    → Verify file creation in correct directory

DO NOT CONTINUE PRP execution until this is resolved.
Report coverage is MANDATORY for execution reliability.
{'='*80}
"""

def validate_report_exists(feature_name: str, task_number: int, report_type: str = "COMPLETION") -> bool:
    """
    Validation gate: Ensure task completion report exists.

    This is THE core validation gate that prevents silent documentation failures.
    Uses EAFP pattern to avoid TOCTOU race condition.

    Pattern: Try to read file (atomic), catch FileNotFoundError
    Source: prps/prp_execution_reliability/examples/validation_gate_pattern.py PATTERN 2

    Args:
        feature_name: Validated feature name (from extract_feature_name)
        task_number: Task number (e.g., 4, 17, 25)
        report_type: Report type (COMPLETION, VALIDATION, etc.)

    Returns:
        True if report exists and has minimum content

    Raises:
        ValidationError: If report is missing or too short (with actionable message)
    """
    report_path = Path(f"prps/{feature_name}/execution/TASK{task_number}_{report_type}.md")

    try:
        # EAFP: Try to read, handle FileNotFoundError
        # This is atomic - no TOCTOU race condition
        content = report_path.read_text()

        # Validate minimum content (prevent empty files)
        if len(content) < 100:
            raise ValidationError(
                f"Task {task_number} report too short: {len(content)} chars (minimum 100)\n"
                f"Path: {report_path}\n\n"
                f"Report may be incomplete or corrupted. Please verify content."
            )

        return True

    except FileNotFoundError:
        # Use actionable error message format
        error_msg = format_missing_report_error(task_number, feature_name, report_type)
        raise ValidationError(error_msg)

def calculate_report_coverage(feature_name: str, total_tasks: int) -> dict:
    """
    Calculate report coverage percentage for PRP execution.

    This shows how many tasks generated completion reports vs total tasks.
    GOAL: 100% coverage (all tasks documented).

    Pattern: Glob for reports, extract task numbers, calculate coverage
    Source: prps/prp_execution_reliability/examples/validation_gate_pattern.py PATTERN 5

    Args:
        feature_name: Validated feature name
        total_tasks: Total number of tasks in PRP

    Returns:
        dict with keys:
            - total_tasks: Total number of tasks
            - reports_found: Number of reports found
            - coverage_percentage: Coverage as percentage (rounded to 1 decimal)
            - missing_tasks: List of task numbers without reports
            - status: "✅ COMPLETE" or "⚠️ INCOMPLETE"
    """
    from glob import glob

    # Find all TASK*_COMPLETION.md reports
    pattern = f"prps/{feature_name}/execution/TASK*_COMPLETION.md"
    task_reports = glob(pattern)
    reports_found = len(task_reports)

    # Calculate coverage percentage
    coverage_pct = (reports_found / total_tasks) * 100 if total_tasks > 0 else 0

    # Find missing task numbers
    reported_tasks = set()
    for report_path in task_reports:
        # Extract task number from filename (TASK17_COMPLETION.md → 17)
        filename = report_path.split("/")[-1]
        match = re.search(r'TASK(\d+)_', filename)
        if match:
            reported_tasks.add(int(match.group(1)))

    all_tasks = set(range(1, total_tasks + 1))
    missing_tasks = sorted(all_tasks - reported_tasks)

    return {
        "total_tasks": total_tasks,
        "reports_found": reports_found,
        "coverage_percentage": round(coverage_pct, 1),
        "missing_tasks": missing_tasks,
        "status": "✅ COMPLETE" if coverage_pct == 100 else "⚠️ INCOMPLETE"
    }

# 4. Extract tasks
tasks = extract_tasks_from_prp(prp_content)

# 5. Archon setup (see .claude/patterns/archon-workflow.md)
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

**CONTEXT**:
- PRP: {prp_path}
- Task: {task['name']}
- Responsibility: {task['responsibility']}
- Files: {task['files']}
- Pattern: {task['pattern']}
- Steps: {task['steps']}

**CRITICAL**: Parallel execution - only modify YOUR task's files.

═══════════════════════════════════════════════════════════════
⚠️  CRITICAL OUTPUT REQUIREMENTS (NON-NEGOTIABLE) ⚠️
═══════════════════════════════════════════════════════════════

This task has TWO outputs, BOTH are MANDATORY:

1️⃣ **Code Implementation** (all files in FILES section above)

2️⃣ **Completion Report** (REQUIRED)
   📄 Path: prps/{feature_name}/execution/TASK{{task['number']}}_COMPLETION.md
   📋 Template: .claude/templates/task-completion-report.md

   Required sections:
   - Implementation Summary
   - Files Created/Modified (with line counts)
   - Key Decisions Made
   - Challenges Encountered
   - Validation Status

⚠️ YOUR TASK IS INCOMPLETE WITHOUT THE COMPLETION REPORT ⚠️

The report is NOT optional. It is MANDATORY for:
✓ Auditing implementation decisions
✓ Learning from challenges encountered
✓ Debugging issues in the future
✓ Passing validation gates

═══════════════════════════════════════════════════════════════

**VALIDATION**:
Your work will be validated immediately after completion:
1. ✅ All files created/modified
2. ✅ Report exists at exact path above
3. ✅ Report contains all required sections
4. ✅ Code passes linting (if applicable)

❌ If report is missing, you will receive a VALIDATION ERROR and must regenerate it.

**WORKFLOW**: 1. Read PRP, 2. Study pattern, 3. Implement, 4. Validate, 5. Create completion report
''')

        # VALIDATION GATE - Fail fast if any reports missing
        print(f"\n🔍 Validating Group {group_number + 1} reports...")
        for task in group['tasks']:
            try:
                validate_report_exists(feature_name, task['number'])
                print(f"  ✅ Task {task['number']}: Report validated")
            except ValidationError as e:
                print(str(e))

                # Update Archon task status to "todo" (failed, needs retry)
                if archon_available:
                    mcp__archon__manage_task(
                        "update",
                        task_id=get_archon_task_id(task, task_mappings),
                        status="todo",
                        description=f"VALIDATION FAILED: Report missing"
                    )

                # HALT EXECUTION - don't continue to next group
                raise

        print(f"✅ Group {group_number + 1}: All {len(group['tasks'])} reports validated\n")

        if archon_available:
            for task in group['tasks']:
                mcp__archon__manage_task("update", task_id=get_archon_task_id(task, task_mappings), status="done")

    elif group['mode'] == "sequential":
        for task in group['tasks']:
            if archon_available:
                mcp__archon__manage_task("update", task_id=get_archon_task_id(task, task_mappings), status="doing")

            Task(subagent_type="prp-exec-implementer", description=f"Implement {task['name']}", prompt=f'''
Implement single task from PRP.

**CONTEXT**:
- PRP: {prp_path}
- Task: {task['name']}
- Responsibility: {task['responsibility']}
- Files: {task['files']}
- Pattern: {task['pattern']}
- Steps: {task['steps']}

═══════════════════════════════════════════════════════════════
⚠️  CRITICAL OUTPUT REQUIREMENTS (NON-NEGOTIABLE) ⚠️
═══════════════════════════════════════════════════════════════

This task has TWO outputs, BOTH are MANDATORY:

1️⃣ **Code Implementation** (all files in FILES section above)

2️⃣ **Completion Report** (REQUIRED)
   📄 Path: prps/{feature_name}/execution/TASK{{task['number']}}_COMPLETION.md
   📋 Template: .claude/templates/task-completion-report.md

   Required sections:
   - Implementation Summary
   - Files Created/Modified (with line counts)
   - Key Decisions Made
   - Challenges Encountered
   - Validation Status

⚠️ YOUR TASK IS INCOMPLETE WITHOUT THE COMPLETION REPORT ⚠️

The report is NOT optional. It is MANDATORY for:
✓ Auditing implementation decisions
✓ Learning from challenges encountered
✓ Debugging issues in the future
✓ Passing validation gates

═══════════════════════════════════════════════════════════════

**VALIDATION**:
Your work will be validated immediately after completion:
1. ✅ All files created/modified
2. ✅ Report exists at exact path above
3. ✅ Report contains all required sections
4. ✅ Code passes linting (if applicable)

❌ If report is missing, you will receive a VALIDATION ERROR and must regenerate it.

**WORKFLOW**: 1. Read PRP, 2. Study pattern, 3. Implement, 4. Validate, 5. Create completion report
''')

            # VALIDATION GATE - Fail fast if report missing (sequential tasks)
            print(f"\n🔍 Validating Task {task['number']} report...")
            try:
                validate_report_exists(feature_name, task['number'])
                print(f"  ✅ Task {task['number']}: Report validated\n")
            except ValidationError as e:
                print(str(e))

                # Update Archon task status to "todo" (failed, needs retry)
                if archon_available:
                    mcp__archon__manage_task(
                        "update",
                        task_id=get_archon_task_id(task, task_mappings),
                        status="todo",
                        description=f"VALIDATION FAILED: Report missing"
                    )

                # HALT EXECUTION - don't continue
                raise

            if archon_available:
                mcp__archon__manage_task("update", task_id=get_archon_task_id(task, task_mappings), status="done")
```

### Phase 3: Test Generation

**Subagent**: `prp-exec-test-generator` | **Duration**: 30-60 min

```python
Task(subagent_type="prp-exec-test-generator", description="Generate tests", prompt=f'''
Generate comprehensive tests (70%+ coverage).

**CONTEXT**:
- PRP: {prp_path}
- Implemented Files: {get_all_modified_files()}
- Feature: {feature_name}

═══════════════════════════════════════════════════════════════
⚠️  CRITICAL OUTPUT REQUIREMENTS (NON-NEGOTIABLE) ⚠️
═══════════════════════════════════════════════════════════════

This task has TWO outputs, BOTH are MANDATORY:

1️⃣ **Test Files** (unit tests + integration tests, 70%+ coverage)

2️⃣ **Test Generation Report** (REQUIRED)
   📄 Path: prps/{feature_name}/execution/test-generation-report.md
   📋 Template: .claude/templates/test-generation-report.md

   Required sections:
   - Test Summary (count, coverage %, patterns used)
   - Test Files Created
   - Coverage Analysis (per module/file)
   - Patterns Applied
   - Edge Cases Covered

⚠️ YOUR TASK IS INCOMPLETE WITHOUT THE TEST GENERATION REPORT ⚠️

The report is NOT optional. It is MANDATORY for:
✓ Documenting test coverage metrics
✓ Tracking patterns and edge cases
✓ Auditing test quality
✓ Passing validation gates

═══════════════════════════════════════════════════════════════

**VALIDATION**:
Your work will be validated immediately after completion:
1. ✅ All test files created
2. ✅ Tests pass (pytest)
3. ✅ Coverage ≥70%
4. ✅ Report exists at exact path above
5. ✅ Report contains all required sections

❌ If report is missing, you will receive a VALIDATION ERROR and must regenerate it.

**WORKFLOW**: 1. Read files, 2. Find test patterns, 3. Generate unit tests, 4. Generate integration tests,
5. Follow conventions, 6. Ensure pass, 7. Create test-generation-report.md
''')
```

### Phase 4: Validation

**Subagent**: `prp-exec-validator` | **Duration**: 10-90 min (see `.claude/patterns/quality-gates.md`)

```python
Task(subagent_type="prp-exec-validator", description="Validate", prompt=f'''
Systematic validation with iteration loops (max 5 attempts per level).

**CONTEXT**:
- PRP: {prp_path}
- Implemented Files: {implemented_files}
- Test Files: {test_files}
- Pattern: .claude/patterns/quality-gates.md (multi-level, error analysis, fix application)

**CRITICAL**: Iterate until pass or max attempts.

═══════════════════════════════════════════════════════════════
⚠️  CRITICAL OUTPUT REQUIREMENTS (NON-NEGOTIABLE) ⚠️
═══════════════════════════════════════════════════════════════

This task has TWO outputs, BOTH are MANDATORY:

1️⃣ **Validation Fixes** (all levels pass or max attempts reached)

2️⃣ **Enhanced Validation Report** (REQUIRED)
   📄 Path: prps/{feature_name}/execution/validation-report.md
   📋 Template: .claude/templates/validation-report.md

   Required sections:
   - Validation Levels (syntax, type, unit, integration)
   - Iteration Tracking (attempts, errors, fixes)
   - Final Status (all pass/partial/failed)
   - Error Analysis (root causes)
   - Fix Applications (what was changed)
   - Next Steps (if any failures remain)

⚠️ YOUR TASK IS INCOMPLETE WITHOUT THE VALIDATION REPORT ⚠️

The report is NOT optional. It is MANDATORY for:
✓ Documenting validation iterations
✓ Tracking error patterns and fixes
✓ Auditing quality gate results
✓ Understanding what passed/failed

═══════════════════════════════════════════════════════════════

**VALIDATION**:
Your work will be validated immediately after completion:
1. ✅ All validation levels attempted
2. ✅ Iteration loop followed (max 5 per level)
3. ✅ Report exists at exact path above
4. ✅ Report contains all required sections
5. ✅ Report includes iteration tracking table

❌ If report is missing, you will receive a VALIDATION ERROR and must regenerate it.

**WORKFLOW**: 1. Read PRP Validation Loop, 2. Execute levels, 3. For failures: analyze → fix → retry (max 5),
4. Document all iterations, 5. Create validation-report.md with complete tracking
''')
```

### Phase 5: Completion (YOU)

```python
validation_report = Read(f"prps/{feature_name}/execution/validation-report.md")
all_passed = check_all_validations_passed(validation_report)
test_report = Read(f"prps/{feature_name}/execution/test-generation-report.md")
coverage = extract_coverage(test_report)

# Calculate report coverage metrics
metrics = calculate_report_coverage(feature_name, total_tasks)

# Quality gate: Enforce 100% report coverage
if metrics['coverage_percentage'] < 100:
    raise ValidationError(
        f"Quality Gate FAILED: Report coverage {metrics['coverage_percentage']}% (required: 100%)\n"
        f"Missing reports for tasks: {metrics['missing_tasks']}"
    )
```

**Success** (all passed):
```
{'='*80}
✅ PRP EXECUTION COMPLETE
{'='*80}
  Feature: {feature_name}
  Implementation: {total_tasks}/{total_tasks} tasks (100%)
  Documentation: {metrics['reports_found']}/{metrics['total_tasks']} reports ({metrics['coverage_percentage']}%)

  {metrics['status'] if metrics['coverage_percentage'] == 100 else f"⚠️ Missing reports for tasks: {metrics['missing_tasks']}"}

  Tests: {test_count} ({coverage}%)
  Validation: Syntax ✅ | Type ✅ | Unit ✅ ({unit_test_count}) | Integration ✅ ({integration_test_count})

  Time: {elapsed_time} min | Speedup: {time_saved}%
{'='*80}

Next Steps:
  1. git diff
  2. pytest tests/test_{feature}* -v
  3. cat prps/{feature_name}/execution/validation-report.md
  4. Review task reports: ls prps/{feature_name}/execution/TASK*_COMPLETION.md
  5. Commit changes

Archon: {project_status}
```

**Partial** (issues):
```
{'='*80}
⚠️ PARTIAL IMPLEMENTATION
{'='*80}
  Feature: {feature_name}
  Completed: {completed}/{total} tasks
  Documentation: {metrics['reports_found']}/{metrics['total_tasks']} reports ({metrics['coverage_percentage']}%)

  {f"⚠️ Missing reports for tasks: {metrics['missing_tasks']}" if metrics['missing_tasks'] else "✅ Report coverage: 100%"}

  Tests: {test_file_count} ({coverage}%)
  Issues: {validation_failures}
{'='*80}

Actions Required:
  1. cat prps/{feature_name}/execution/validation-report.md
  2. Fix {recommendations}
  3. Re-run {failed_commands}
  4. {'Generate missing reports: ' + str(metrics['missing_tasks']) if metrics['missing_tasks'] else 'All reports complete'}

Options:
  1. Investigate failures and fix
  2. Re-run validator
  3. Continue (NOT RECOMMENDED - incomplete documentation)
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
