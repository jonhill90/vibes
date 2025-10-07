# Codebase Patterns: PRP Execution Reliability

## Overview

This document identifies existing patterns for template systems, validation gates, report generation, and error handling that should be applied to enhance PRP execution reliability. The analysis reveals strong existing patterns for security validation, Archon integration, and quality gates, but gaps in mandatory report generation enforcement.

## Architectural Patterns

### Pattern 1: Security-First File Path Validation
**Source**: `/Users/jon/source/vibes/.claude/patterns/security-validation.md`
**Relevance**: 10/10
**What it does**: 5-level validation for extracting feature names from file paths, preventing path traversal and command injection attacks

**Key Techniques**:
```python
import re

def extract_feature_name(filepath: str, strip_prefix: str = None) -> str:
    """5-level security validation for feature names from file paths."""
    # 1. Path traversal in full path
    if ".." in filepath: raise ValueError(f"Path traversal: {filepath}")

    # Extract basename, remove extension
    feature = filepath.split("/")[-1].replace(".md", "")
    if strip_prefix: feature = feature.replace(strip_prefix, "")

    # 2. Whitelist (alphanumeric + _ - only)
    if not re.match(r'^[a-zA-Z0-9_-]+$', feature): raise ValueError(f"Invalid: {feature}")

    # 3. Length (max 50 chars)
    if len(feature) > 50: raise ValueError(f"Too long: {len(feature)}")

    # 4. Directory traversal
    if ".." in feature or "/" in feature or "\\" in feature: raise ValueError(f"Path traversal: {feature}")

    # 5. Command injection
    if any(c in feature for c in ['$','`',';','&','|','>','<','\n','\r']): raise ValueError(f"Dangerous: {feature}")

    return feature
```

**When to use**:
- When extracting feature names from PRP paths
- Before constructing file paths dynamically
- Any time user input influences file system operations

**How to adapt**:
- Already used in execute-prp.md line 16-23
- Apply same pattern to report path validation
- Use for template loading to prevent path traversal

**Why this pattern**:
- Prevents security vulnerabilities
- Provides clear error messages
- Multiple defense layers
- Battle-tested in production workflows

---

### Pattern 2: Quality Gates with Iteration Loops
**Source**: `/Users/jon/source/vibes/.claude/patterns/quality-gates.md`
**Relevance**: 9/10
**What it does**: Multi-level validation with automatic retry loops (max 5 attempts), error analysis, and fix application

**Key Techniques**:
```python
MAX_ATTEMPTS = 5

for attempt in range(1, MAX_ATTEMPTS + 1):
    result = run_validation(level, commands)

    if result.success:
        print(f"✅ Level {level} passed")
        break

    print(f"❌ Attempt {attempt}/{MAX_ATTEMPTS} failed: {result.error}")

    if attempt < MAX_ATTEMPTS:
        # Analyze error against PRP gotchas, apply fix
        error_analysis = analyze_error(result.error, prp_gotchas)
        fix_attempt = apply_fix(error_analysis)
        print(f"Applied fix: {fix_attempt.description}")
    else:
        print(f"⚠️ Max attempts reached - manual intervention required")
```

**When to use**:
- Report validation gates (check existence, check sections)
- Test execution validation
- Any multi-step validation requiring retry logic

**How to adapt**:
```python
# Report validation with retry
for attempt in range(1, MAX_ATTEMPTS + 1):
    report_path = f"prps/{feature_name}/execution/TASK{task_number}_COMPLETION.md"

    if os.path.exists(report_path):
        print(f"✅ Report exists: {report_path}")
        break

    print(f"❌ Attempt {attempt}: Report missing at {report_path}")

    if attempt < MAX_ATTEMPTS:
        print("Regenerating report from task context...")
        # Retry report generation
    else:
        raise ValidationError(f"Task {task_number} missing report after {MAX_ATTEMPTS} attempts")
```

**Why this pattern**:
- Handles transient failures gracefully
- Provides multiple chances for subagents
- Clear feedback on progress
- Matches existing validation loop pattern

---

### Pattern 3: Archon Integration with Graceful Degradation
**Source**: `/Users/jon/source/vibes/.claude/patterns/archon-workflow.md`
**Relevance**: 8/10
**What it does**: Health check first, graceful fallback if unavailable, status tracking (todo → doing → done), error reset

**Key Techniques**:
```python
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
        title=f"PRP: {feature_name}",
        description=f"Execution of {prp_path}"
    )
    project_id = project["project"]["id"]

    # 4. Update status: todo → doing → done
    mcp__archon__manage_task("update", task_id=task_id, status="doing")
    # ... do work ...
    mcp__archon__manage_task("update", task_id=task_id, status="done")

# 5. Error handling - reset to "todo" for retry
try:
    Task(subagent_type="prp-exec-implementer", ...)
except Exception as e:
    if archon_available:
        mcp__archon__manage_task("update", task_id=task_id,
            status="todo", description=f"ERROR: {e}")
    print(f"⚠️ Phase failed: {e}")
```

**When to use**:
- All multi-phase workflows
- Tracking task completion status
- Providing audit trail of execution

**How to adapt**:
- Already integrated in execute-prp.md Phase 0
- Add status updates before/after validation gates
- Track report generation as separate tasks

**Why this pattern**:
- Never blocks workflow if Archon unavailable
- Provides rich execution history
- Enables post-execution analysis
- Consistent across all PRP workflows

---

### Pattern 4: Template-Based Markdown Generation
**Source**: `/Users/jon/source/vibes/.claude/templates/validation-report.md`, `completion-report.md`
**Relevance**: 10/10
**What it does**: Standardized markdown templates with placeholder variables, consistent structure, clear sections

**Key Techniques**:
```python
# Template loading
def load_template(template_name: str) -> str:
    template_path = f".claude/templates/{template_name}"
    template_content = Read(template_path)
    return template_content

# Variable substitution using f-strings
template = load_template("task-completion-report.md")
report_content = template.format(
    task_number=task_number,
    task_name=task["name"],
    feature_name=feature_name,
    files_modified="\n".join(modified_files),
    key_decisions="\n".join(decisions),
    validation_status="✅ PASS" if all_passed else "❌ FAIL"
)

# Write report
report_path = f"prps/{feature_name}/execution/TASK{task_number}_COMPLETION.md"
Write(report_path, report_content)
```

**Template Structure** (validation-report.md):
```markdown
# Validation Report: {Feature Name}

## Validation Summary
**Overall Status**: {✅ PASS / ❌ FAIL}
**Total Levels**: {X}
**Levels Passed**: {Y}
**Issues Found**: {Z}

## Validation Levels
### Level 1: Syntax & Style Checks
**Status**: {✅ PASS / ❌ FAIL}
**Commands Run**: ...
**Results**: ...

## Issue Details
### Issue #1: {Issue Title}
- **Severity**: {Critical/High/Medium/Low}
- **Location**: {file:line}
- **Fix Applied**: {what was done}

## Validation Iterations
| Attempt | Level | Result | Duration | Issues Fixed |
|---------|-------|--------|----------|--------------|
| 1 | Level 1 | ❌ FAIL | 2min | Syntax errors |
| 2 | Level 1 | ✅ PASS | 1min | - |
```

**When to use**:
- All standardized report generation
- Ensuring consistent documentation structure
- Providing clear templates for subagents

**How to adapt**:
- Create `task-completion-report.md` template (NEW)
- Create `test-generation-report.md` template (NEW)
- Enhance existing `validation-report.md` with more sections
- Use Python f-strings for variable substitution (simplest approach)

**Why this pattern**:
- Ensures consistency across all reports
- Easy for subagents to follow
- Human-readable templates
- Simple variable substitution (no complex templating engine)

---

### Pattern 5: Explicit Subagent Output Requirements
**Source**: Analysis of feature-analysis.md, INITIAL_execution_reliability.md
**Relevance**: 10/10
**What it does**: Uses "CRITICAL OUTPUT REQUIREMENTS" and "INCOMPLETE without" language to enforce mandatory outputs from subagents

**Key Techniques**:
```python
# Enhanced subagent prompt pattern
Task(subagent_type="prp-exec-implementer", description=f"Implement {task['name']}", prompt=f'''
Implement single task from PRP.

PRP: {prp_path}
Task: {task['name']}
Responsibility: {task['responsibility']}
Files: {task['files']}
Pattern: {task['pattern']}
Steps: {task['steps']}

CRITICAL OUTPUT REQUIREMENTS:
1. Implement all files listed in task
2. Create completion report: prps/{feature_name}/execution/TASK{task['number']}_COMPLETION.md
3. Use template: .claude/templates/task-completion-report.md
4. Report MUST exist before you finish

Your task is INCOMPLETE without the completion report.

Steps:
1. Read PRP task details
2. Study pattern examples
3. Implement files
4. Validate implementation
5. Generate completion report (MANDATORY)
''')
```

**When to use**:
- All subagent invocations requiring specific outputs
- When subagents historically skip optional requirements
- Emphasizing non-negotiable deliverables

**How to adapt**:
- Add "CRITICAL OUTPUT REQUIREMENTS" section to all implementer prompts
- Add "Your task is INCOMPLETE without X" statement
- List exact file paths expected
- Reference templates explicitly

**Why this pattern**:
- Makes requirements crystal clear
- "INCOMPLETE" language creates accountability
- Proven effective in prp-exec-validator agent
- Addresses root cause of missing reports (subagents thinking it's optional)

---

## Naming Conventions

### File Naming

**Pattern**: `TASK{n}_COMPLETION.md` (standardized, no underscores before number)

**Current Reality** (from task_management_ui):
- ❌ `TASK5_IMPLEMENTATION_NOTES.md`
- ❌ `TASK9_IMPLEMENTATION_REPORT.md`
- ❌ `TASK_17_COMPLETION.md` (underscore before number)
- ❌ `TASK_18_COMPLETE.md` (COMPLETE vs COMPLETION)
- ❌ `TASK20_IMPLEMENTATION_REPORT.md`
- ❌ `TASK22_TEST_IMPLEMENTATION_REPORT.md`
- ✅ `TASK_21_COMPLETION.md` (correct but inconsistent)

**Standardized Pattern** (going forward):
```
TASK1_COMPLETION.md
TASK2_COMPLETION.md
...
TASK25_COMPLETION.md
```

**Why this convention**:
- Easy to glob: `glob(f"prps/{feature_name}/execution/TASK*_COMPLETION.md")`
- Alphabetically sorted (TASK1, TASK2, ... TASK10, ... TASK25)
- "COMPLETION" is most descriptive (vs COMPLETE, NOTES, REPORT)
- Consistent with validation-report.md naming

### Class Naming
Not applicable - this is a documentation/workflow enhancement, no new classes

### Function Naming

**Pattern**: `validate_{what}`, `calculate_{metric}`, `extract_{data}`

**Examples from codebase**:
```python
# Validation functions
def validate_report_exists(feature_name: str, task_number: int) -> bool
def validate_report_sections(report_path: str, required_sections: list[str]) -> list[str]

# Metric calculation
def calculate_report_coverage(feature_name: str, total_tasks: int) -> dict

# Data extraction
def extract_feature_name(filepath: str, strip_prefix: str = None) -> str
```

**Pattern Rules**:
- Verb_noun structure
- Clear action words (validate, calculate, extract, check, verify)
- Return type in docstring
- Raise specific exceptions (ValueError, ValidationError)

---

## File Organization

### Directory Structure

**Current Structure**:
```
.claude/
├── templates/
│   ├── completion-report.md          # EXISTS (generic)
│   └── validation-report.md          # EXISTS
├── commands/
│   ├── execute-prp.md                # MODIFY (add validation gates)
│   └── generate-prp.md               # No changes needed
├── patterns/
│   ├── quality-gates.md              # EXISTS (reference this)
│   ├── security-validation.md        # EXISTS (use this)
│   └── archon-workflow.md            # EXISTS (already integrated)
└── agents/
    └── prp-exec-test-generator.md    # EXISTS (good example)

prps/{feature_name}/
├── execution/
│   ├── execution-plan.md             # Created by analyzer
│   ├── TASK1_COMPLETION.md           # NEW (per task)
│   ├── TASK2_COMPLETION.md           # NEW
│   ├── ...
│   ├── test-generation-report.md     # NEW
│   └── validation-report.md          # ENHANCED
└── {feature_name}.md                 # Main PRP
```

**New Files to Create**:
```
.claude/templates/
├── task-completion-report.md         # NEW
└── test-generation-report.md         # NEW
```

**Files to Modify**:
```
.claude/commands/execute-prp.md       # Add validation gates
.claude/templates/validation-report.md # Enhance with more sections
```

**Justification**:
- Templates directory already established pattern
- execution/ directory for all task outputs
- Consistent naming across all reports
- Easy to find and audit

---

## Common Utilities to Leverage

### 1. Security Validation - extract_feature_name()
**Location**: `.claude/patterns/security-validation.md` (pattern), used in execute-prp.md
**Purpose**: Extract and validate feature names from file paths
**Usage Example**:
```python
from .claude.patterns.security_validation import extract_feature_name

feature_name = extract_feature_name(prp_path)  # prps/my_feature.md → my_feature
# Raises ValueError if invalid
```

### 2. Quality Gate Validation Loop
**Location**: `.claude/patterns/quality-gates.md`
**Purpose**: Iterate validation with max attempts, error analysis, fix application
**Usage Example**:
```python
MAX_ATTEMPTS = 5

for attempt in range(1, MAX_ATTEMPTS + 1):
    result = run_validation(level, commands)
    if result.success:
        break
    if attempt < MAX_ATTEMPTS:
        apply_fix(analyze_error(result.error))
    else:
        raise ValidationError("Max attempts reached")
```

### 3. Archon Health Check and Task Tracking
**Location**: `.claude/patterns/archon-workflow.md`
**Purpose**: Track task status, provide audit trail, graceful degradation
**Usage Example**:
```python
health = mcp__archon__health_check()
if health["status"] == "healthy":
    task = mcp__archon__manage_task("create",
        project_id=project_id,
        title="Task 1",
        status="todo")
    mcp__archon__manage_task("update", task_id=task["task"]["id"], status="doing")
    # ... do work ...
    mcp__archon__manage_task("update", task_id=task["task"]["id"], status="done")
```

### 4. File Existence Validation
**Location**: Standard Python (os.path.exists, Path.exists)
**Purpose**: Check if files exist before processing
**Usage Example**:
```python
import os

report_path = f"prps/{feature_name}/execution/TASK{task_number}_COMPLETION.md"

if not os.path.exists(report_path):
    raise ValidationError(f"Task {task_number} missing completion report at {report_path}")
```

### 5. Glob Pattern for Report Discovery
**Location**: Used in INITIAL_execution_reliability.md
**Purpose**: Find all task reports matching pattern
**Usage Example**:
```python
from glob import glob

# Find all task completion reports
task_reports = glob(f"prps/{feature_name}/execution/TASK*_COMPLETION.md")
reports_found = len(task_reports)
total_tasks = 25

coverage_pct = (reports_found / total_tasks) * 100
print(f"Report Coverage: {reports_found}/{total_tasks} ({coverage_pct:.1f}%)")
```

---

## Testing Patterns

### Unit Test Structure
**Pattern**: Not applicable - this is workflow/documentation enhancement, no code to unit test

### Integration Test Structure
**Pattern**: Manual validation of execute-prp workflow

**Example Validation**:
```bash
# Test 1: Execute PRP with validation gates
/execute-prp prps/test_feature.md

# Expected outputs:
# - All tasks complete
# - All reports generated (100% coverage)
# - Validation gate catches missing reports
# - Error messages are actionable

# Test 2: Simulate missing report
# (Remove a report mid-execution to verify validation gate catches it)
rm prps/test_feature/execution/TASK5_COMPLETION.md
# Execute next phase → should fail with clear error

# Test 3: Verify report coverage calculation
# Check final summary shows: "Reports: 25/25 (100%)"
```

---

## Anti-Patterns to Avoid

### 1. Silent Failures (Continue Despite Missing Outputs)
**What it is**: Workflow continues even when critical outputs (reports) are missing
**Why to avoid**: Leads to 48% report coverage, no audit trail, can't learn from execution
**Found in**: Current execute-prp.md (no validation gates)
**Better approach**:
```python
# WRONG (current)
Task(subagent_type="prp-exec-implementer", ...)
# Continues even if report missing

# RIGHT (new)
Task(subagent_type="prp-exec-implementer", ...)

# Validation gate
report_path = f"prps/{feature_name}/execution/TASK{task_number}_COMPLETION.md"
if not os.path.exists(report_path):
    raise ValidationError(f"CRITICAL: Task {task_number} missing completion report\n"
                        f"Expected: {report_path}\n"
                        f"Action: Check subagent output, regenerate report")
```

### 2. Inconsistent Naming (Multiple Patterns for Same Thing)
**What it is**: 6 different naming patterns found in task_management_ui reports
**Why to avoid**: Impossible to glob reliably, confusing, breaks automation
**Found in**: task_management_ui execution reports (IMPLEMENTATION_NOTES, IMPLEMENTATION_REPORT, COMPLETION, COMPLETE, VALIDATION, TEST_IMPLEMENTATION_REPORT)
**Better approach**:
```python
# WRONG (inconsistent)
TASK5_IMPLEMENTATION_NOTES.md
TASK9_IMPLEMENTATION_REPORT.md
TASK_17_COMPLETION.md
TASK_18_COMPLETE.md

# RIGHT (standardized)
TASK5_COMPLETION.md
TASK9_COMPLETION.md
TASK17_COMPLETION.md
TASK18_COMPLETION.md
```

### 3. Vague Subagent Instructions (Optional-Sounding Requirements)
**What it is**: Prompts that don't emphasize mandatory nature of outputs
**Why to avoid**: Subagents skip "optional" steps, leading to missing reports
**Found in**: Original execute-prp.md prompts (no "CRITICAL" or "INCOMPLETE" language)
**Better approach**:
```python
# WRONG (vague)
prompt = f'''
Implement task. Consider creating a completion report.
'''

# RIGHT (explicit)
prompt = f'''
CRITICAL OUTPUT REQUIREMENTS:
1. Implement files
2. Create completion report: {report_path}
3. Use template: .claude/templates/task-completion-report.md

Your task is INCOMPLETE without the completion report.
'''
```

### 4. Hardcoded Paths Without Variables
**What it is**: Paths like `prps/execution/report.md` instead of `prps/{feature_name}/execution/report.md`
**Why to avoid**: Only works for single feature, not reusable
**Found in**: INITIAL_execution_reliability.md analysis identified this issue (already fixed)
**Better approach**:
```python
# WRONG (hardcoded)
report_path = "prps/execution/TASK1_COMPLETION.md"

# RIGHT (parameterized)
report_path = f"prps/{feature_name}/execution/TASK{task_number}_COMPLETION.md"
```

### 5. No Error Context (Generic Error Messages)
**What it is**: Errors like "Validation failed" without details
**Why to avoid**: User can't debug, doesn't know what to fix
**Found in**: Generic error handling patterns
**Better approach**:
```python
# WRONG (generic)
raise ValidationError("Validation failed")

# RIGHT (actionable)
raise ValidationError(f"""
CRITICAL: Task {task_number} missing completion report

Expected location: {report_path}
Current directory: {os.getcwd()}

Troubleshooting:
1. Check if subagent completed successfully
2. Search for report in: prps/{feature_name}/
3. Manually create report using: .claude/templates/task-completion-report.md
4. Re-run validation gate

Found reports: {existing_reports}
""")
```

---

## Implementation Hints from Existing Code

### Similar Features Found

1. **Validation Report Template**: `.claude/templates/validation-report.md`
   - **Similarity**: Standardized markdown template with placeholders
   - **Lessons**:
     - Clear sections (Summary, Levels, Issues, Iterations)
     - Table format for iteration tracking
     - Status indicators (✅/❌)
     - "Next Steps" section
   - **Differences**: Task completion reports need different sections (files modified, decisions, challenges vs validation levels)

2. **Quality Gates Pattern**: `.claude/patterns/quality-gates.md`
   - **Similarity**: Multi-level validation with retry loops
   - **Lessons**:
     - MAX_ATTEMPTS = 5 is standard
     - Break on success, retry on failure
     - Error analysis against known gotchas
     - Clear user feedback on each attempt
   - **Differences**: Report validation is simpler (file exists + section check vs running tests)

3. **Security Validation Pattern**: `.claude/patterns/security-validation.md`
   - **Similarity**: Input validation with multiple checks
   - **Lessons**:
     - 5 levels of validation (comprehensive)
     - Specific error messages
     - Raise ValueError with clear descriptions
     - Whitelist approach (only allow safe characters)
   - **Differences**: Apply same rigor to report path validation

4. **Archon Workflow Integration**: execute-prp.md Phase 0
   - **Similarity**: Already integrated health check and task tracking
   - **Lessons**:
     - Health check FIRST
     - Graceful degradation if unavailable
     - Update status before/after work
     - Error handling resets to "todo"
   - **Differences**: Need to track report generation as separate tasks

5. **Test Generator Agent**: `.claude/agents/prp-exec-test-generator.md`
   - **Similarity**: Autonomous agent with clear output requirements
   - **Lessons**:
     - "CRITICAL" section in output requirements
     - Explicit file paths specified
     - Quality standards checklist
     - Success metrics defined
   - **Differences**: Task completion reports are simpler than test generation

---

## Recommendations for PRP

Based on pattern analysis, the PRP should:

1. **Follow Template-Based Report Pattern** for standardized documentation
   - Create task-completion-report.md template
   - Create test-generation-report.md template
   - Use Python f-strings for variable substitution (simplest approach)

2. **Reuse Security Validation Pattern** for path validation
   - Apply extract_feature_name() to all dynamic paths
   - Validate report paths before reading/writing
   - Prevent path traversal attacks

3. **Mirror Quality Gates Pattern** for validation loops
   - Implement report existence checks with retry (max 5 attempts)
   - Check required sections in reports
   - Provide actionable error messages

4. **Adapt Explicit Output Requirements Pattern** for subagent prompts
   - Add "CRITICAL OUTPUT REQUIREMENTS" to all implementer prompts
   - Use "Your task is INCOMPLETE without X" language
   - Specify exact file paths expected

5. **Avoid Silent Failure Anti-Pattern** from current execute-prp.md
   - Add validation gates after each task group
   - Fail fast when reports missing
   - Don't continue execution with incomplete documentation

6. **Follow Archon Integration Pattern** for task tracking
   - Already well-integrated in execute-prp.md
   - Track report generation as separate tasks
   - Update status before/after validation gates

---

## Source References

### From Archon
- **b8565aff9938938b** (Context Engineering Intro): Validation gates, PRP strategies - Relevance 7/10
- **9a7d4217c64c9a0a** (Claude Code Hooks): Subagent patterns, tool usage - Relevance 5/10
- **c0e629a894699314** (Pydantic AI): Validation error handling, retry patterns - Relevance 6/10

### From Local Codebase
- `.claude/patterns/security-validation.md:11-32`: extract_feature_name() pattern
- `.claude/patterns/quality-gates.md:49-70`: Validation loop with max attempts
- `.claude/templates/validation-report.md:1-106`: Template structure example
- `.claude/templates/completion-report.md:1-33`: Generic completion template
- `.claude/commands/execute-prp.md:16-26`: Security validation in action
- `.claude/patterns/archon-workflow.md:10-74`: Archon integration pattern
- `.claude/agents/prp-exec-test-generator.md:1-511`: Autonomous agent with output requirements
- `prps/task_management_ui/execution/TASK_17_COMPLETION.md`: Good task report example
- `prps/task_management_ui/execution/TASK_18_COMPLETE.md`: Alternate naming (shows inconsistency)
- `prps/task_management_ui/execution/MISSING_REPORTS_ANALYSIS.md:74-100`: Root cause of report failures

---

## Next Steps for Assembler

When generating the PRP:

1. **Reference these patterns in "Current Codebase Tree" section**:
   - List `.claude/templates/` directory
   - List `.claude/patterns/quality-gates.md`
   - List `.claude/patterns/security-validation.md`
   - Show execute-prp.md structure

2. **Include key code snippets in "Implementation Blueprint"**:
   - Security validation function (Pattern 1)
   - Validation loop with max attempts (Pattern 2)
   - Template loading and variable substitution (Pattern 4)
   - Report coverage calculation (Utility 5)

3. **Add anti-patterns to "Known Gotchas" section**:
   - Silent failures (Anti-Pattern 1)
   - Inconsistent naming (Anti-Pattern 2)
   - Vague instructions (Anti-Pattern 3)
   - Generic error messages (Anti-Pattern 5)

4. **Use file organization for "Desired Codebase Tree"**:
   ```
   .claude/templates/
   ├── task-completion-report.md     # NEW
   ├── test-generation-report.md     # NEW
   └── validation-report.md          # ENHANCE

   .claude/commands/
   └── execute-prp.md                # MODIFY (add validation gates)
   ```

5. **Include implementation hints in task descriptions**:
   - Task 1 (Templates): Reference validation-report.md structure
   - Task 2 (Validation Gates): Reference quality-gates.md pattern
   - Task 3 (Subagent Prompts): Reference prp-exec-test-generator.md
   - Task 4 (Coverage Calculation): Reference glob pattern from INITIAL.md

6. **Add pattern compliance to validation checklist**:
   - ✅ Uses security validation for paths
   - ✅ Implements quality gate retry loops
   - ✅ Templates follow existing structure
   - ✅ Subagent prompts use "CRITICAL" language
   - ✅ Error messages are actionable

---

## Pattern Maturity Assessment

**Highly Mature Patterns** (Ready to use as-is):
- ✅ Security validation (extract_feature_name)
- ✅ Quality gates (validation loops)
- ✅ Archon integration (health check, graceful degradation)
- ✅ Template structure (validation-report.md)

**Emerging Patterns** (Adapt for this use case):
- 🔶 Explicit output requirements (proven in test-generator, extend to all subagents)
- 🔶 Report coverage metrics (concept exists, needs implementation)
- 🔶 Fail-fast validation (philosophy exists, needs enforcement)

**Missing Patterns** (Create new):
- ❌ Task completion report template (no standard exists)
- ❌ Report section validation (file exists check exists, section check is new)
- ❌ Mandatory report enforcement (no validation gate exists yet)

**Verdict**: Strong foundation exists. This PRP enhances existing patterns rather than reinventing. Focus on standardizing what's proven (templates, validation loops) and adding missing enforcement layer (validation gates).
