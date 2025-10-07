# PRP: Execution Reliability - Mandatory Report Generation & Validation Gates

**Generated**: 2025-10-06
**Based On**: prps/INITIAL_prp_execution_reliability.md
**Archon Project**: 001819fc-bfa3-41d5-a7df-c49eab180269

---

## Goal

Make PRP execution 100% reliable for both implementation AND documentation by enforcing mandatory report generation, standardizing templates, and adding validation gates that fail fast when reports are missing.

**End State**:
- 100% of tasks generate completion reports (currently 48%)
- Validation gates block progression if reports missing
- Standardized report naming: `TASK{n}_COMPLETION.md`
- Clear audit trail of all implementation decisions
- Post-execution metrics show report coverage percentage

## Why

**Current Pain Points**:
- 48% report coverage in task_management_ui (13/25 tasks undocumented)
- Silent failures - execution continues despite missing documentation
- 6 different naming patterns for reports (impossible to glob reliably)
- Cannot learn from implementation decisions on 52% of tasks
- No accountability - subagents treat reports as optional

**Business Value**:
- Complete audit trail enables debugging and learning
- Standardized documentation accelerates future development
- Fail-fast validation prevents accumulated technical debt
- Reliable metrics show true completion status
- Knowledge accumulation from every PRP execution

## What

### Core Features

1. **Mandatory Report Generation**
   - Task completion reports for all implementation tasks
   - Test generation reports with coverage metrics
   - Enhanced validation reports with fix iterations
   - All reports follow standardized templates

2. **Validation Gates**
   - File existence checks after each task group
   - Section validation for required content
   - Report coverage calculation (target: 100%)
   - Fail-fast on missing reports (no silent continuation)

3. **Standardized Templates**
   - `task-completion-report.md` - comprehensive task documentation
   - `test-generation-report.md` - test coverage and patterns
   - Enhanced `validation-report.md` - all gates with iterations

4. **Enforcement Mechanisms**
   - Explicit "CRITICAL" language in subagent prompts
   - Validation gates immediately after task execution
   - Actionable error messages with troubleshooting steps
   - Report coverage metrics in final summary

### Success Criteria

- [ ] 100% of tasks generate completion reports (verified programmatically)
- [ ] All reports follow standardized naming: `TASK{n}_COMPLETION.md`
- [ ] Validation gates block progression if report missing
- [ ] Post-execution summary shows: "Reports: X/X (100%)"
- [ ] Easy to audit what each subagent did via standardized reports
- [ ] Test PRP achieves 100% report coverage on first execution

---

## All Needed Context

### Documentation & References

```yaml
# MUST READ - Python & File Operations
- url: https://docs.python.org/3/library/pathlib.html
  sections:
    - "Path.exists() Method" - Core validation for report existence
    - "Path.is_file() Method" - Distinguish files from directories
  why: Foundation for validation gate implementation
  critical_gotchas:
    - TOCTOU race condition - use EAFP (try/except) not check-then-use
    - Symlinks followed by default - broken symlinks return False
    - Always use Path objects, not string concatenation

- url: https://realpython.com/python-f-strings/
  sections:
    - "F-String Formatting" - Variable substitution in templates
    - "Format vs F-Strings" - When to use each approach
  why: Template system uses .format() for runtime substitution
  critical_gotchas:
    - F-strings evaluate at parse time (can't load templates with f-strings)
    - Use .format(**variables) for runtime template substitution
    - Missing variables in .format() raise KeyError - validate first

- url: https://docs.python.org/3/library/string.html#template-strings
  sections:
    - "Template Class" - Safe string substitution
  why: Alternative for security-sensitive template rendering
  critical_gotchas:
    - Prevents arbitrary code execution via format strings
    - Use safe_substitute() for lenient mode (missing vars OK)

# MUST READ - Quality Gates & Validation
- url: https://www.sonarsource.com/learn/quality-gate/
  sections:
    - "What is a Quality Gate" - Validation checkpoint concept
    - "Fail-Fast Principle" - Block progression if criteria not met
  why: Quality gates pattern for report validation
  critical_gotchas:
    - Silent failures accumulate technical debt
    - Warnings without enforcement lead to non-compliance
    - 100% coverage threshold prevents slippage

- url: https://www.nngroup.com/articles/error-message-guidelines/
  sections:
    - "Be Clear and Specific" - State what went wrong
    - "Be Actionable" - Tell user what to do
    - "Reduce Correction Effort" - Provide specific fix instructions
  why: Error message design for validation failures
  critical_gotchas:
    - Generic errors don't help users fix problems
    - Include expected path, troubleshooting, resolution options
    - Use visual separators (===, ⚠️) to highlight critical issues

- url: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
  sections:
    - "Structured Sections" - Organize prompts with clear sections
    - "Output Cues" - Include format hints at end of prompt
    - "Format Specification" - Show exact expected format
  why: Prompt engineering for mandatory report outputs
  critical_gotchas:
    - AI agents skip "optional-sounding" requirements
    - Use "CRITICAL", "MANDATORY", "INCOMPLETE without" language
    - Position critical requirements early and repeat them

# MUST READ - Security
- url: https://lucumr.pocoo.org/2016/12/29/careful-with-str-format/
  sections:
    - "Format String Injection" - Exploiting .format() method
  why: Prevent code execution via template variables
  critical_gotchas:
    - User-controlled format strings can access object attributes
    - Attackers can read globals, secrets, environment variables
    - Use string.Template or validate variables before .format()

# ESSENTIAL LOCAL FILES
- file: /Users/jon/source/vibes/prps/prp_execution_reliability/examples/README.md
  why: Comprehensive "what to mimic" guidance for all 5 examples
  pattern: Study phase → application phase workflow
  critical: All patterns needed for implementation extracted

- file: /Users/jon/source/vibes/prps/prp_execution_reliability/examples/example_task_completion_report.md
  why: GOLD STANDARD structure for task completion reports
  pattern: Files tracking, gotcha verification, dependency checks
  critical: Use this structure for new task-completion-report.md template

- file: /Users/jon/source/vibes/prps/prp_execution_reliability/examples/validation_gate_pattern.py
  why: 5 validation patterns (existence, sections, loop, coverage, security)
  pattern: validate_report_exists() is THE core validation gate
  critical: Copy PATTERN 2 into execute-prp.md Phase 2

- file: /Users/jon/source/vibes/prps/prp_execution_reliability/examples/error_message_pattern.py
  why: Actionable error message design (5 formats)
  pattern: Problem → Impact → Troubleshooting → Resolution structure
  critical: format_missing_report_error() for all validation failures

- file: /Users/jon/source/vibes/.claude/patterns/security-validation.md
  why: 5-level path validation pattern (already in execute-prp.md)
  pattern: extract_feature_name() prevents path traversal
  critical: Use for ALL path operations involving feature names

- file: /Users/jon/source/vibes/.claude/patterns/quality-gates.md
  why: Validation loop with retry (max 5 attempts)
  pattern: Error analysis, fix application, fail-fast after max attempts
  critical: Reference for report validation with retry logic

- file: /Users/jon/source/vibes/.claude/templates/validation-report.md
  why: Reference implementation for validation report structure
  pattern: Iteration tracking table, multi-level validation format
  critical: Enhance with any new validation levels, keep structure

- file: /Users/jon/source/vibes/.claude/templates/completion-report.md
  why: Generic completion report with performance metrics
  pattern: Metrics-driven reporting approach
  critical: Too generic for task reports - needs task-specific enhancement
```

### Current Codebase Tree

```
.claude/
├── templates/
│   ├── completion-report.md          # EXISTS (generic - needs enhancement)
│   └── validation-report.md          # EXISTS (good structure)
├── commands/
│   ├── execute-prp.md                # MODIFY (add validation gates)
│   └── generate-prp.md               # No changes needed
├── patterns/
│   ├── quality-gates.md              # EXISTS (reference for validation loops)
│   ├── security-validation.md        # EXISTS (path traversal prevention)
│   └── archon-workflow.md            # EXISTS (already integrated in execute-prp)
└── agents/
    └── prp-exec-test-generator.md    # EXISTS (good example of output requirements)

prps/task_management_ui/execution/    # EVIDENCE of current state
├── TASK5_IMPLEMENTATION_NOTES.md     # ❌ Wrong naming (6 different patterns)
├── TASK_17_COMPLETION.md             # ✅ Good content, wrong naming (underscore)
├── TASK_18_COMPLETE.md               # ❌ COMPLETE vs COMPLETION
└── ... (12/25 reports, 48% coverage) # ❌ 13 tasks missing reports
```

### Desired Codebase Tree

```
.claude/templates/
├── task-completion-report.md         # NEW - comprehensive task documentation
├── test-generation-report.md         # NEW - test metrics and patterns
└── validation-report.md              # ENHANCE - add more sections

.claude/commands/
└── execute-prp.md                    # MODIFY
    ├── Phase 2: Add validation gates after task groups
    ├── Phase 3: Add report requirement + validation for tests
    ├── Phase 4: Add report requirement + validation for validation
    └── Phase 5: Add report coverage metrics display

prps/{feature_name}/execution/        # STANDARDIZED output
├── execution-plan.md                 # Created by analyzer (existing)
├── TASK1_COMPLETION.md               # NEW (standardized naming)
├── TASK2_COMPLETION.md               # NEW
├── ... (all tasks)                   # 100% coverage
├── test-generation-report.md         # NEW
└── validation-report.md              # ENHANCED

**New Files**:
- `.claude/templates/task-completion-report.md`
- `.claude/templates/test-generation-report.md`
- Enhanced `.claude/templates/validation-report.md`
- Updated `.claude/commands/execute-prp.md`
```

### Known Gotchas & Library Quirks

```python
# CRITICAL GOTCHA #1: Format String Injection
# Source: https://lucumr.pocoo.org/2016/12/29/careful-with-str-format/
# Risk: User-controlled format strings can execute arbitrary code

# ❌ WRONG:
template = user_input.format(task=task_object)  # Can access __globals__, secrets

# ✅ RIGHT:
from string import Template
template = Template(template_content)
return template.safe_substitute(**variables)  # Prevents attribute access

# OR validate variables before .format():
allowed_keys = {'feature_name', 'task_number', 'task_name', 'status'}
if not set(variables.keys()).issubset(allowed_keys):
    raise ValueError(f"Invalid template variables")


# CRITICAL GOTCHA #2: Path Traversal in Report Paths
# Source: .claude/patterns/security-validation.md
# Risk: Attackers inject "../" to access files outside prps/

# ❌ WRONG:
report_path = f"prps/{feature_name}/execution/TASK{n}_COMPLETION.md"
# Vulnerable: feature_name = "../../etc/passwd" escapes prps/

# ✅ RIGHT:
import re
from pathlib import Path

def extract_feature_name(filepath: str) -> str:
    """5-level security validation for feature names."""
    # 1. Path traversal detection
    if ".." in filepath:
        raise ValueError(f"Path traversal: {filepath}")

    # 2. Whitelist (alphanumeric + _ - only)
    feature = filepath.split("/")[-1].replace(".md", "")
    if not re.match(r'^[a-zA-Z0-9_-]+$', feature):
        raise ValueError(f"Invalid characters: {feature}")

    # 3. Length limit (max 50 chars)
    if len(feature) > 50:
        raise ValueError(f"Too long: {len(feature)}")

    # 4. Directory traversal in extracted name
    if ".." in feature or "/" in feature or "\\" in feature:
        raise ValueError(f"Path traversal: {feature}")

    # 5. Command injection prevention
    dangerous = ['$', '`', ';', '&', '|', '>', '<', '\n', '\r']
    if any(c in feature for c in dangerous):
        raise ValueError(f"Dangerous characters: {feature}")

    return feature

# ALWAYS use this before constructing paths:
feature_name = extract_feature_name(prp_path)
report_path = f"prps/{feature_name}/execution/TASK{n}_COMPLETION.md"


# CRITICAL GOTCHA #3: TOCTOU Race Condition
# Source: https://cwe.mitre.org/data/definitions/367.html
# Risk: File deleted/modified between check and use

# ❌ WRONG (TOCTOU vulnerable):
if report_path.exists():  # CHECK
    # ... gap where file could be deleted ...
    content = report_path.read_text()  # USE - may raise FileNotFoundError

# ✅ RIGHT (EAFP - Easier to Ask Forgiveness than Permission):
try:
    # Atomic operation - open and read in one step
    content = report_path.read_text()

    # Validate content we actually have
    if len(content) < 100:
        raise ValidationError("Report too short")

except FileNotFoundError:
    raise ValidationError(f"Report missing: {report_path}")


# CRITICAL GOTCHA #4: Subagents Ignoring Mandatory Requirements
# Source: prps/task_management_ui (48% report coverage)
# Risk: Subagents skip "optional-sounding" tasks

# ❌ WRONG (vague prompt):
prompt = "Implement files. Consider creating a completion report."
# Result: 13/25 tasks produced no reports

# ✅ RIGHT (explicit enforcement):
prompt = f'''
Implement single task from PRP: {task['name']}

═══════════════════════════════════════════════════════════════
⚠️  CRITICAL OUTPUT REQUIREMENTS (NON-NEGOTIABLE) ⚠️
═══════════════════════════════════════════════════════════════

This task has TWO outputs, BOTH are MANDATORY:

1️⃣ **Code Implementation** (all files in FILES section)

2️⃣ **Completion Report** (REQUIRED)
   📄 Path: prps/{feature_name}/execution/TASK{task['number']}_COMPLETION.md
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

Your work will be validated and you will receive an error if the report is missing.
'''


# CRITICAL GOTCHA #5: Silent Validation Failures
# Source: codebase-patterns.md Anti-Pattern #1
# Risk: Execution continues despite missing reports

# ❌ WRONG (warn but continue):
if not report_exists:
    print("⚠️ Warning: Report missing")
    # Execution continues - accumulates technical debt

# ✅ RIGHT (fail fast):
if not report_exists:
    raise ValidationError(
        f"❌ QUALITY GATE FAILED: Missing Task Report\n\n"
        f"Task {task_number} did not generate required report.\n"
        f"Expected: {report_path}\n\n"
        f"DO NOT CONTINUE until this is resolved."
    )
# Halts execution immediately


# HIGH PRIORITY GOTCHA #6: Information Disclosure in Error Messages
# Source: https://www.nngroup.com/articles/error-message-guidelines/
# Risk: Leaking absolute paths, usernames, secrets

# ❌ WRONG (leaks sensitive info):
raise ValueError(f"Cannot access {os.path.expanduser('~/.config/secrets.json')}")

# ✅ RIGHT (safe, actionable):
raise ValueError(
    f"Template '{template_name}' not found\n\n"
    f"Expected location: .claude/templates/{template_name}\n"
    f"Action: Ensure template exists in .claude/templates/"
)
# Uses relative paths only, no system info


# MEDIUM PRIORITY GOTCHA #7: Performance Degradation (Large PRPs)
# Source: Quality gates pattern analysis
# Risk: Sequential validation slow for 50+ tasks

# ❌ SLOW (sequential):
for task_num in range(1, 51):
    validate_report_exists(feature_name, task_num)  # 50 disk reads

# ✅ FAST (parallel):
from concurrent.futures import ThreadPoolExecutor

def validate_one(task_num: int) -> dict:
    try:
        content = report_path.read_text()  # Single read
        return {"task": task_num, "status": "valid"}
    except FileNotFoundError:
        return {"task": task_num, "status": "error"}

with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(validate_one, range(1, 51)))
# 5-10x faster for I/O-bound operations


# LOW PRIORITY GOTCHA #8: Template Variable Missing (KeyError)
# Source: Python format() documentation
# Risk: Template expects variable not provided

# ❌ WRONG (no validation):
template.format(**variables)  # May raise KeyError: 'confidence_level'

# ✅ RIGHT (validate variables):
import re

def extract_template_variables(template: str) -> set[str]:
    return set(re.findall(r'\{(\w+)\}', template))

required_vars = extract_template_variables(template)
provided_vars = set(variables.keys())
missing = required_vars - provided_vars

if missing:
    raise ValueError(f"Missing variables: {missing}")

return template.format(**variables)


# LOW PRIORITY GOTCHA #9: Report Naming Inconsistencies
# Source: codebase-patterns.md Anti-Pattern #2
# Evidence: 6 different naming patterns in task_management_ui

# ❌ WRONG (inconsistent):
# TASK5_IMPLEMENTATION_NOTES.md
# TASK_17_COMPLETION.md (underscore before number)
# TASK_18_COMPLETE.md (COMPLETE vs COMPLETION)
# TASK22_TEST_IMPLEMENTATION_REPORT.md

# ✅ RIGHT (standardized):
# TASK1_COMPLETION.md
# TASK2_COMPLETION.md
# TASK17_COMPLETION.md (no underscore before number)
# TASK25_COMPLETION.md

# Enforce in validation:
report_path = Path(f"prps/{feature_name}/execution/TASK{task_number}_COMPLETION.md")

if not report_path.exists():
    # Check for common misspellings
    wrong_patterns = [
        Path(f"...TASK{task_number}_COMPLETE.md"),
        Path(f"...TASK_{task_number}_COMPLETION.md"),  # Extra underscore
    ]

    wrong_exists = [p for p in wrong_patterns if p.exists()]

    if wrong_exists:
        raise ValidationError(
            f"Report has wrong name:\n"
            f"  Found: {wrong_exists[0]}\n"
            f"  Expected: {report_path}\n\n"
            f"Standardized naming: TASK<number>_COMPLETION.md\n"
            f"  - No underscore before number\n"
            f"  - COMPLETION (not COMPLETE, REPORT, or NOTES)"
        )
```

---

## Implementation Blueprint

### Phase 0: Planning & Understanding

**BEFORE starting implementation, complete these steps:**

1. **Study Examples** (~40-45 minutes total)
   - Read `/Users/jon/source/vibes/prps/prp_execution_reliability/examples/README.md`
   - Study `example_task_completion_report.md` (GOLD STANDARD structure)
   - Review `validation_gate_pattern.py` (5 validation patterns)
   - Review `error_message_pattern.py` (actionable error formats)

2. **Review Existing Patterns**
   - `.claude/patterns/security-validation.md` - path validation (already in execute-prp.md)
   - `.claude/patterns/quality-gates.md` - validation loop pattern
   - `.claude/templates/validation-report.md` - reference template structure

3. **Understand Current State**
   - Execute-prp.md Phase 2 structure (where to add validation gates)
   - Subagent prompt patterns (where to add "CRITICAL" language)
   - Report storage location (`prps/{feature_name}/execution/`)

### Task List (Execute in Order)

```yaml
Task 1: Create Task Completion Report Template
RESPONSIBILITY: Standardized template for all task completion reports
FILES TO CREATE:
  - .claude/templates/task-completion-report.md

PATTERN TO FOLLOW:
  - Use example_task_completion_report.md as structure
  - Reference validation-report.md for markdown format

SPECIFIC STEPS:
  1. Copy structure from example_task_completion_report.md
  2. Replace actual values with {variable} placeholders
  3. Add variable list at top (feature_name, task_number, task_name, status, etc.)
  4. Include ALL sections from gold standard:
     - Task Information
     - Files Created/Modified (with line counts and descriptions)
     - Implementation Details (core features)
     - Critical Gotchas Addressed (from PRP)
     - Dependencies Verified
     - Testing Checklist
     - Success Metrics
     - Completion Report summary
  5. Add usage instructions in comment at top
  6. Test template rendering with sample variables

VALIDATION:
  - Template contains all required sections from example
  - All variables use {variable_name} syntax
  - Template can be loaded and formatted successfully
  - Example rendering produces valid markdown

---

Task 2: Create Test Generation Report Template
RESPONSIBILITY: Standardized template for test generation reports
FILES TO CREATE:
  - .claude/templates/test-generation-report.md

PATTERN TO FOLLOW:
  - Adapt from completion-report.md (metrics approach)
  - Add test-specific sections

SPECIFIC STEPS:
  1. Copy structure from completion-report.md
  2. Modify sections for test-specific content:
     - Test Summary (count, coverage %, patterns used)
     - Test Files Created
     - Coverage Analysis (per module/file)
     - Patterns Applied (from PRP or examples)
     - Edge Cases Covered
     - Integration with Existing Tests
  3. Add placeholders: {feature_name}, {total_tests}, {coverage_percentage}, etc.
  4. Include table format for coverage metrics
  5. Test template rendering

VALIDATION:
  - Template covers all test-specific metrics
  - Variables use {variable_name} syntax
  - Can be formatted successfully
  - Output is valid markdown

---

Task 3: Enhance Validation Report Template
RESPONSIBILITY: Add sections to existing validation-report.md
FILES TO MODIFY:
  - .claude/templates/validation-report.md

PATTERN TO FOLLOW:
  - Keep existing structure (already good)
  - Add {feature_name} variable for consistency

SPECIFIC STEPS:
  1. Read existing validation-report.md
  2. Add {feature_name} variable to title and paths
  3. Ensure iteration tracking table is present
  4. Add "Next Steps" section if not present
  5. Verify all sections use consistent variable syntax
  6. Test template rendering

VALIDATION:
  - Existing structure preserved
  - Variables use {variable_name} syntax
  - Can be formatted successfully
  - Backward compatible with current usage

---

Task 4: Add Validation Gate Functions to Execute-PRP
RESPONSIBILITY: Core validation logic to enforce mandatory reports
FILES TO MODIFY:
  - .claude/commands/execute-prp.md

PATTERN TO FOLLOW:
  - Copy validate_report_exists() from validation_gate_pattern.py PATTERN 2
  - Use EAFP pattern (try/except, not check-then-use)

SPECIFIC STEPS:
  1. Read validation_gate_pattern.py PATTERN 2
  2. Add validation functions to execute-prp.md Phase 0 (Setup):
     ```python
     def validate_report_exists(feature_name: str, task_number: int) -> bool:
         """Validation gate: Ensure task completion report exists."""
         report_path = Path(f"prps/{feature_name}/execution/TASK{task_number}_COMPLETION.md")

         try:
             # EAFP: Try to read, handle FileNotFoundError
             content = report_path.read_text()

             if len(content) < 100:
                 raise ValidationError(f"Report too short: {len(content)} chars (min 100)")

             return True

         except FileNotFoundError:
             raise ValidationError(format_missing_report_error(task_number, feature_name))

     def format_missing_report_error(task_number: int, feature_name: str) -> str:
         """Generate actionable error message for missing report."""
         report_path = f"prps/{feature_name}/execution/TASK{task_number}_COMPLETION.md"

         return (
             f"\n{'='*80}\n"
             f"❌ VALIDATION GATE FAILED: Missing Task Report\n"
             f"{'='*80}\n\n"
             f"PROBLEM:\n"
             f"  Task {task_number} did not generate required completion report.\n\n"
             f"EXPECTED PATH:\n"
             f"  {report_path}\n\n"
             f"IMPACT:\n"
             f"  This task is INCOMPLETE without documentation.\n"
             f"  - Cannot audit what was implemented\n"
             f"  - Cannot learn from implementation decisions\n\n"
             f"TROUBLESHOOTING:\n"
             f"  1. Check if subagent execution completed successfully\n"
             f"  2. Verify template exists: .claude/templates/task-completion-report.md\n"
             f"  3. Check write permissions in prps/{feature_name}/\n\n"
             f"RESOLUTION:\n"
             f"  Option 1 (RECOMMENDED): Re-run task with explicit report requirement\n"
             f"  Option 2: Manually create report using template\n\n"
             f"DO NOT CONTINUE PRP execution until this is resolved.\n"
             f"{'='*80}\n"
         )
     ```
  3. Add report coverage calculation function:
     ```python
     def calculate_report_coverage(feature_name: str, total_tasks: int) -> dict:
         """Calculate report coverage percentage."""
         from glob import glob
         import re

         task_reports = glob(f"prps/{feature_name}/execution/TASK*_COMPLETION.md")
         reports_found = len(task_reports)
         coverage_pct = (reports_found / total_tasks) * 100

         # Find missing task numbers
         reported_tasks = set()
         for report_path in task_reports:
             match = re.search(r'TASK(\d+)_', report_path.split("/")[-1])
             if match:
                 reported_tasks.add(int(match.group(1)))

         missing_tasks = sorted(set(range(1, total_tasks + 1)) - reported_tasks)

         return {
             "total_tasks": total_tasks,
             "reports_found": reports_found,
             "coverage_percentage": round(coverage_pct, 1),
             "missing_tasks": missing_tasks,
             "status": "✅ COMPLETE" if coverage_pct == 100 else "⚠️ INCOMPLETE"
         }
     ```

VALIDATION:
  - Functions added to execute-prp.md Phase 0
  - Validation logic matches PATTERN 2 from examples
  - Error messages match format_missing_report_error() pattern
  - Coverage calculation works correctly

---

Task 5: Add Validation Gates to Execute-PRP Phase 2
RESPONSIBILITY: Call validation after each task group completes
FILES TO MODIFY:
  - .claude/commands/execute-prp.md (Phase 2: Implementation)

PATTERN TO FOLLOW:
  - Fail fast - halt execution if validation fails
  - Validate after task groups (not individual tasks in parallel)

SPECIFIC STEPS:
  1. Locate Phase 2 task group execution loop
  2. After each task group completes, add validation:
     ```python
     # After task group completes
     for task in group['tasks']:
         Task(subagent_type="prp-exec-implementer", ...)

     # VALIDATION GATE - Fail fast if any reports missing
     print(f"\n🔍 Validating Group {group['number']} reports...")
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
                     task_id=task_ids[task['number']],
                     status="todo",
                     description=f"VALIDATION FAILED: Report missing"
                 )

             # HALT EXECUTION - don't continue to next group
             raise

     print(f"✅ Group {group['number']}: All {len(group['tasks'])} reports validated\n")
     ```
  3. Test with sample task group

VALIDATION:
  - Validation gate added after each task group
  - Fails fast on first missing report
  - Updates Archon status if available
  - Error message is actionable

---

Task 6: Update Subagent Prompts with Mandatory Language
RESPONSIBILITY: Make report generation explicitly mandatory in prompts
FILES TO MODIFY:
  - .claude/commands/execute-prp.md (Phase 2: prp-exec-implementer prompts)

PATTERN TO FOLLOW:
  - Use "CRITICAL", "MANDATORY", "INCOMPLETE without" language
  - Visual separators (═══, ⚠️) to highlight
  - Exact path specification

SPECIFIC STEPS:
  1. Locate prp-exec-implementer Task() invocations in Phase 2
  2. Enhance prompt with explicit output requirements:
     ```python
     Task(subagent_type="prp-exec-implementer", description=f"Implement {task['name']}", prompt=f'''
     Implement single task from PRP: {task['name']}

     **CONTEXT**:
     - PRP: {prp_path}
     - Responsibility: {task['responsibility']}
     - Pattern: {task['pattern']}
     - Dependencies: {task.get('depends_on', 'None')}

     **FILES TO CREATE/MODIFY**:
     {task['files']}

     **IMPLEMENTATION STEPS**:
     {task['steps']}

     ═══════════════════════════════════════════════════════════════
     ⚠️  CRITICAL OUTPUT REQUIREMENTS (NON-NEGOTIABLE) ⚠️
     ═══════════════════════════════════════════════════════════════

     This task has TWO outputs, BOTH are MANDATORY:

     1️⃣ **Code Implementation** (all files in FILES section above)

     2️⃣ **Completion Report** (REQUIRED)
        📄 Path: prps/{feature_name}/execution/TASK{task['number']}_COMPLETION.md
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
     ''')
     ```
  3. Update prp-exec-test-generator prompt similarly
  4. Update prp-exec-validator prompt similarly

VALIDATION:
  - Prompts use "CRITICAL" and "MANDATORY" language
  - Exact report path specified
  - Visual separators highlight requirements
  - Validation consequences explained

---

Task 7: Add Report Coverage Metrics to Phase 5
RESPONSIBILITY: Display final report coverage in completion summary
FILES TO MODIFY:
  - .claude/commands/execute-prp.md (Phase 5: Completion)

PATTERN TO FOLLOW:
  - Call calculate_report_coverage()
  - Display: "Reports: X/X (100%)"
  - Show missing tasks if <100%

SPECIFIC STEPS:
  1. Locate Phase 5 completion summary
  2. Add report coverage calculation and display:
     ```python
     # Calculate report coverage
     metrics = calculate_report_coverage(feature_name, total_tasks)

     # Display summary
     print(f"\n{'='*80}")
     print(f"✅ PRP EXECUTION COMPLETE")
     print(f"{'='*80}")
     print(f"  Feature: {feature_name}")
     print(f"  Implementation: {total_tasks}/{total_tasks} tasks (100%)")
     print(f"  Documentation: {metrics['reports_found']}/{metrics['total_tasks']} reports ({metrics['coverage_percentage']}%)")

     if metrics['missing_tasks']:
         print(f"  ⚠️ Missing reports for tasks: {metrics['missing_tasks']}")
         print(f"\n  WARNING: Report coverage below 100%. Generate missing reports.")
     else:
         print(f"  ✅ Report coverage: 100% - Complete audit trail")

     print(f"  Validation: All gates passed")
     print(f"{'='*80}\n")
     ```
  3. Add validation to fail if coverage <100%:
     ```python
     if metrics['coverage_percentage'] < 100:
         raise ValidationError(
             f"Quality Gate FAILED: Report coverage {metrics['coverage_percentage']}% (required: 100%)\n"
             f"Missing reports for tasks: {metrics['missing_tasks']}"
         )
     ```

VALIDATION:
  - Coverage metrics displayed in final summary
  - Missing tasks shown if <100%
  - Quality gate enforces 100% coverage
  - Summary is clear and actionable

---

Task 8: Test PRP Execution with Validation Gates
RESPONSIBILITY: Verify all validation gates work correctly
FILES TO TEST:
  - .claude/commands/execute-prp.md (end-to-end test)

PATTERN TO FOLLOW:
  - Create test PRP with 3-5 tasks
  - Execute with validation gates enabled
  - Verify 100% report coverage achieved

SPECIFIC STEPS:
  1. Create test PRP: `prps/test_validation_gates.md`
     - 3 simple tasks (create file, modify file, test)
     - Each task clearly specifies report requirement
  2. Execute: `/execute-prp prps/test_validation_gates.md`
  3. Verify validation gates trigger:
     - Remove one report mid-execution
     - Verify execution halts with actionable error
     - Verify error message matches format_missing_report_error()
  4. Fix missing report, resume execution
  5. Verify final summary shows:
     - "Reports: 3/3 (100%)"
     - "✅ Report coverage: 100%"
  6. Verify all reports follow standardized naming: `TASK{n}_COMPLETION.md`

VALIDATION:
  - Test PRP completes successfully
  - All 3 reports generated
  - Validation gate catches missing reports
  - Error messages are actionable
  - Final summary shows 100% coverage
  - Reports follow naming convention
```

### Implementation Pseudocode

```python
# Task 1: Template Creation
# Load gold standard example
example = Read("/Users/jon/source/vibes/prps/prp_execution_reliability/examples/example_task_completion_report.md")

# Extract structure, replace values with {variables}
template_content = convert_to_template(example)

# Add variable documentation
header = """
# Task Completion Report Template

Variables required:
- {feature_name}: Name of feature being implemented
- {task_number}: Task number (1-based)
- {task_name}: Human-readable task name
- {status}: COMPLETE | PARTIAL | FAILED
- {files_modified}: Newline-separated list of files
- {implementation_summary}: Brief summary of what was done
- {key_decisions}: Newline-separated list of decisions
- {challenges}: Challenges encountered (or "None")
- {validation_status}: ✅ PASS | ❌ FAIL

Usage:
  template = Path(".claude/templates/task-completion-report.md").read_text()
  report = template.format(
      feature_name="user_auth",
      task_number=3,
      ...
  )
"""

template_with_header = header + "\n" + template_content
Write(".claude/templates/task-completion-report.md", template_with_header)


# Task 4-5: Validation Gate Integration
# Pattern from: validation_gate_pattern.py PATTERN 2

def validate_report_exists(feature_name: str, task_number: int) -> bool:
    """
    Validation gate: Ensure task completion report exists.

    This is THE function that prevents 48% → 100% coverage.
    Uses EAFP pattern to avoid TOCTOU race condition.
    """
    report_path = Path(f"prps/{feature_name}/execution/TASK{task_number}_COMPLETION.md")

    try:
        # EAFP: Try to read, handle FileNotFoundError
        # This is atomic - no TOCTOU race condition
        content = report_path.read_text()

        # Validate minimum content (prevent empty files)
        if len(content) < 100:
            raise ValidationError(
                f"Task {task_number} report too short: {len(content)} chars (minimum 100)"
            )

        return True

    except FileNotFoundError:
        # Use actionable error message format
        error_msg = format_missing_report_error(task_number, feature_name)
        raise ValidationError(error_msg)


# Task 6: Subagent Prompt Enhancement
# Pattern from: Anthropic context engineering + prp-exec-test-generator.md

implementer_prompt = f'''
Implement single task from PRP: {task['name']}

[...existing context...]

═══════════════════════════════════════════════════════════════
⚠️  CRITICAL OUTPUT REQUIREMENTS (NON-NEGOTIABLE) ⚠️
═══════════════════════════════════════════════════════════════

This task has TWO outputs, BOTH are MANDATORY:

1️⃣ **Code Implementation**
2️⃣ **Completion Report** (REQUIRED)
   📄 Path: prps/{feature_name}/execution/TASK{task['number']}_COMPLETION.md
   📋 Template: .claude/templates/task-completion-report.md

⚠️ YOUR TASK IS INCOMPLETE WITHOUT THE COMPLETION REPORT ⚠️

═══════════════════════════════════════════════════════════════
'''

# Use "CRITICAL", "MANDATORY", "INCOMPLETE without" language
# Visual separators (═══, ⚠️) highlight non-negotiable requirements
# Exact path specification prevents naming inconsistencies


# Task 7: Coverage Metrics
# Pattern from: validation_gate_pattern.py PATTERN 5

metrics = calculate_report_coverage(feature_name, total_tasks)

print(f"Reports: {metrics['reports_found']}/{metrics['total_tasks']} ({metrics['coverage_percentage']}%)")

if metrics['coverage_percentage'] < 100:
    print(f"⚠️ Missing: Tasks {metrics['missing_tasks']}")
    raise ValidationError("Quality Gate FAILED: Report coverage below 100%")

# Target: 100% coverage, fail if not achieved
```

---

## Validation Loop

### Level 1: Template Validation

```bash
# Verify templates can be loaded and formatted
python -c "
from pathlib import Path

templates = [
    '.claude/templates/task-completion-report.md',
    '.claude/templates/test-generation-report.md',
    '.claude/templates/validation-report.md'
]

for template_path in templates:
    template = Path(template_path).read_text()

    # Test formatting with sample variables
    try:
        result = template.format(
            feature_name='test_feature',
            task_number=1,
            task_name='Test Task',
            status='COMPLETE',
            files_modified='test.py',
            implementation_summary='Test implementation',
            key_decisions='None',
            challenges='None',
            validation_status='✅ PASS'
        )
        print(f'✅ {template_path}: Valid')
    except KeyError as e:
        print(f'❌ {template_path}: Missing variable {e}')
"
```

### Level 2: Validation Gate Testing

```python
# Test validation gate with missing report
def test_validation_gate_missing_report():
    """Verify validation gate catches missing reports."""
    feature_name = "test_feature"
    task_number = 999  # Non-existent task

    try:
        validate_report_exists(feature_name, task_number)
        assert False, "Should have raised ValidationError"
    except ValidationError as e:
        # Verify error message is actionable
        error_msg = str(e)
        assert "VALIDATION GATE FAILED" in error_msg
        assert "TASK999_COMPLETION.md" in error_msg
        assert "TROUBLESHOOTING:" in error_msg
        assert "RESOLUTION:" in error_msg
        print("✅ Validation gate works correctly")


# Test validation gate with valid report
def test_validation_gate_valid_report():
    """Verify validation gate passes for valid reports."""
    feature_name = "test_feature"
    task_number = 1

    # Create test report
    report_path = Path(f"prps/{feature_name}/execution/TASK{task_number}_COMPLETION.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("# Task 1 Completion Report\n\n" + "x" * 100)

    try:
        result = validate_report_exists(feature_name, task_number)
        assert result is True
        print("✅ Validation gate passes for valid report")
    finally:
        report_path.unlink()


# Run tests
test_validation_gate_missing_report()
test_validation_gate_valid_report()
```

### Level 3: Coverage Calculation Testing

```python
# Test report coverage calculation
def test_coverage_calculation():
    """Verify coverage calculation is accurate."""
    feature_name = "test_feature"
    total_tasks = 5

    # Create reports for tasks 1, 2, 4 (skip 3, 5)
    for task_num in [1, 2, 4]:
        report_path = Path(f"prps/{feature_name}/execution/TASK{task_num}_COMPLETION.md")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(f"# Task {task_num} Report\n\n" + "x" * 100)

    try:
        metrics = calculate_report_coverage(feature_name, total_tasks)

        assert metrics['total_tasks'] == 5
        assert metrics['reports_found'] == 3
        assert metrics['coverage_percentage'] == 60.0
        assert metrics['missing_tasks'] == [3, 5]
        assert metrics['status'] == "⚠️ INCOMPLETE"

        print("✅ Coverage calculation accurate")
    finally:
        # Cleanup
        for task_num in [1, 2, 4]:
            Path(f"prps/{feature_name}/execution/TASK{task_num}_COMPLETION.md").unlink()


test_coverage_calculation()
```

### Level 4: Integration Test (End-to-End)

```bash
# Create minimal test PRP
cat > prps/test_validation_gates.md << 'EOF'
# PRP: Test Validation Gates

## Goal
Test that validation gates enforce mandatory report generation.

## Implementation Blueprint

### Task List

```yaml
Task 1: Create Hello World
FILES TO CREATE:
  - test_hello.py

Task 2: Add Tests
FILES TO CREATE:
  - test_hello_test.py

Task 3: Validate
RESPONSIBILITY: Verify everything works
```
EOF

# Execute test PRP
/execute-prp prps/test_validation_gates.md

# Expected output:
# ✅ Task 1: Report validated
# ✅ Task 2: Report validated
# ✅ Task 3: Report validated
# ✅ PRP EXECUTION COMPLETE
# Documentation: 3/3 reports (100%)

# Verify reports created
ls prps/test_validation_gates/execution/TASK*_COMPLETION.md
# Expected: TASK1_COMPLETION.md, TASK2_COMPLETION.md, TASK3_COMPLETION.md

# Test validation gate catches missing reports
rm prps/test_validation_gates/execution/TASK2_COMPLETION.md

# Re-run validation (should fail)
python -c "
from pathlib import Path
from execute_prp import calculate_report_coverage

metrics = calculate_report_coverage('test_validation_gates', 3)
assert metrics['coverage_percentage'] < 100
assert 2 in metrics['missing_tasks']
print('✅ Coverage calculation detects missing report')
"
```

---

## Final Validation Checklist

### Template Quality
- [ ] task-completion-report.md created with all sections from gold standard
- [ ] test-generation-report.md created with test-specific metrics
- [ ] validation-report.md enhanced with {feature_name} variable
- [ ] All templates use {variable_name} syntax consistently
- [ ] Templates can be formatted without KeyError
- [ ] Sample rendering produces valid markdown

### Validation Gate Implementation
- [ ] validate_report_exists() added to execute-prp.md Phase 0
- [ ] Uses EAFP pattern (try/except, not check-then-use)
- [ ] Error message matches format_missing_report_error() pattern
- [ ] Validation gates added after each task group in Phase 2
- [ ] calculate_report_coverage() added to Phase 0
- [ ] Coverage metrics displayed in Phase 5 summary

### Subagent Prompt Enhancement
- [ ] prp-exec-implementer prompts use "CRITICAL" language
- [ ] Exact report path specified: prps/{feature_name}/execution/TASK{n}_COMPLETION.md
- [ ] Visual separators (═══, ⚠️) highlight requirements
- [ ] "INCOMPLETE without" language used
- [ ] Validation consequences explained
- [ ] prp-exec-test-generator prompts similarly enhanced
- [ ] prp-exec-validator prompts similarly enhanced

### End-to-End Testing
- [ ] Test PRP created with 3-5 tasks
- [ ] Test PRP achieves 100% report coverage
- [ ] Validation gate catches missing reports (tested)
- [ ] Error messages are actionable (verified)
- [ ] Final summary shows: "Reports: X/X (100%)"
- [ ] All reports follow naming: TASK{n}_COMPLETION.md

### Security & Gotchas
- [ ] Path validation uses extract_feature_name() for all paths
- [ ] Template variable validation prevents KeyError
- [ ] Error messages use relative paths only (no /Users/...)
- [ ] No sensitive information in error messages
- [ ] TOCTOU prevention: using EAFP pattern
- [ ] Format string injection prevented (string.Template or validation)

### Performance
- [ ] Validation uses parallel execution for large PRPs (optional)
- [ ] Templates loaded once, reused (not reloaded per task)
- [ ] Validation gates don't block parallel task execution

---

## Anti-Patterns to Avoid

### Silent Failures (Continue Despite Errors)
```python
# ❌ WRONG - Warn but continue
if not report_exists:
    print("⚠️ Warning: Report missing")
    # Execution continues - accumulates technical debt

# ✅ RIGHT - Fail fast
if not report_exists:
    raise ValidationError("Quality Gate FAILED: Missing report")
    # Halts execution immediately
```

### Vague Subagent Instructions
```python
# ❌ WRONG - Optional-sounding
prompt = "Consider creating a completion report."

# ✅ RIGHT - Explicit enforcement
prompt = """
⚠️ CRITICAL: Report is MANDATORY
Your task is INCOMPLETE without report at:
prps/{feature_name}/execution/TASK{n}_COMPLETION.md
"""
```

### Check-Then-Use (TOCTOU Vulnerable)
```python
# ❌ WRONG - Race condition
if report_path.exists():  # CHECK
    content = report_path.read_text()  # USE (file could be deleted here)

# ✅ RIGHT - EAFP (atomic)
try:
    content = report_path.read_text()  # Single atomic operation
except FileNotFoundError:
    raise ValidationError("Report missing")
```

### Generic Error Messages
```python
# ❌ WRONG - Not actionable
raise ValueError("Validation failed")

# ✅ RIGHT - Actionable with structure
raise ValidationError(
    f"❌ VALIDATION GATE FAILED: Missing Report\n\n"
    f"PROBLEM: Task {n} incomplete\n"
    f"EXPECTED PATH: {path}\n"
    f"TROUBLESHOOTING:\n  1. Check subagent output\n"
    f"RESOLUTION:\n  - Re-run task\n  - OR create manually"
)
```

### Hardcoded Paths
```python
# ❌ WRONG - No validation
report_path = f"prps/{feature_name}/execution/report.md"
# Vulnerable to path traversal

# ✅ RIGHT - Security validation
feature_name = extract_feature_name(prp_path)  # 5-level validation
report_path = f"prps/{feature_name}/execution/TASK{n}_COMPLETION.md"
```

### Inconsistent Naming
```python
# ❌ WRONG - Multiple patterns
# TASK5_IMPLEMENTATION_NOTES.md
# TASK_17_COMPLETION.md
# TASK_18_COMPLETE.md

# ✅ RIGHT - Standardized
# TASK5_COMPLETION.md
# TASK17_COMPLETION.md (no underscore before number)
# TASK25_COMPLETION.md
```

---

## Success Metrics

### Quantitative
- 100% report coverage (all tasks documented)
- 0 validation gate failures in production PRPs
- 0 reports with non-standard naming
- <2 seconds validation time for 25 tasks (parallel)

### Qualitative
- Clear audit trail of all implementation decisions
- Easy to find and review task reports
- Actionable error messages (no "contact support")
- Subagents understand reports are mandatory

---

## PRP Quality Self-Assessment

**Score: 9/10** - High confidence in one-pass implementation success

**Reasoning**:
- ✅ Comprehensive context: All 5 research docs thorough (feature-analysis, codebase-patterns, documentation-links, examples, gotchas)
- ✅ Clear task breakdown: 8 tasks with specific steps, patterns, and validation criteria
- ✅ Proven patterns: Gold standard example (example_task_completion_report.md), 5 validation patterns extracted
- ✅ Validation strategy: 4-level validation (templates, gates, coverage, integration)
- ✅ Error handling: 9+ gotchas documented with solutions, security patterns applied

**Deduction reasoning** (-1 point):
- **Template variable exhaustiveness**: task-completion-report.md may need iteration to discover all useful variables
- **Mitigation**: Task 1 includes testing template rendering, can add variables as needed

**Strengths**:
- Real evidence of problem (48% report coverage in task_management_ui)
- Gold standard example to copy (example_task_completion_report.md)
- Security patterns already in codebase (extract_feature_name)
- Clear fail-fast enforcement strategy
- Comprehensive gotchas (9 documented with code examples)

**Risks mitigated**:
- Format string injection: Use string.Template or validate variables
- Path traversal: Use existing extract_feature_name() pattern
- TOCTOU race: Use EAFP pattern (try/except)
- Subagent non-compliance: Use "CRITICAL", "MANDATORY" language + validation gates
- Silent failures: Fail fast, raise exceptions (no warnings)

**Implementation readiness**: Can start coding immediately after studying examples (~40 min study time). All patterns proven and extracted.
