# PRP: Test Validation Gates

**Generated**: 2025-10-07
**Purpose**: Test that validation gates enforce mandatory report generation
**Archon Project**: N/A (Test PRP)

---

## Goal

Verify that the PRP execution reliability validation gates work correctly by executing a minimal PRP with 3 simple tasks and confirming that:
1. All tasks generate completion reports
2. Validation gates catch missing reports
3. Error messages are actionable
4. Final summary shows 100% report coverage

**End State**:
- 3 simple tasks executed
- 3 completion reports generated (`TASK1_COMPLETION.md`, `TASK2_COMPLETION.md`, `TASK3_COMPLETION.md`)
- Validation gates verified to work correctly
- Report coverage metrics display correctly

## Why

**Testing Need**:
- Validate that validation gates from execution_reliability work as designed
- Confirm error messages are actionable and helpful
- Verify report coverage calculation is accurate
- Test fail-fast behavior when reports are missing

**Business Value**:
- Confidence in validation gate implementation
- Proof that 100% report coverage is achievable
- Verification of error handling and user experience

## What

### Core Features to Test

1. **Normal Execution** - All reports generated correctly
2. **Validation Gate Triggering** - Missing reports detected
3. **Error Message Quality** - Actionable troubleshooting steps
4. **Coverage Calculation** - Accurate percentage and missing task identification

### Success Criteria

- [ ] All 3 tasks complete successfully
- [ ] All 3 completion reports exist with correct naming
- [ ] Validation gates pass for all tasks
- [ ] Final summary shows "Reports: 3/3 (100%)"
- [ ] Test demonstrates validation gate catches missing reports

---

## All Needed Context

### Documentation & References

```yaml
# Test-Specific Context
- PRP to test: prps/execution_reliability.md (Tasks 1-7 must be complete)
- Templates used:
  - .claude/templates/task-completion-report.md
- Validation functions:
  - validate_report_exists() from execute-prp.md
  - calculate_report_coverage() from execute-prp.md
  - format_missing_report_error() from execute-prp.md
```

### Current Codebase Tree

```
prps/test_validation_gates/
└── execution/                    # Will be created
    ├── TASK1_COMPLETION.md      # To be generated
    ├── TASK2_COMPLETION.md      # To be generated
    └── TASK3_COMPLETION.md      # To be generated

test_files/                       # Test artifacts
├── hello_world.py               # Task 1 output
├── hello_world_enhanced.py      # Task 2 output
└── validation_results.txt       # Task 3 output
```

### Known Gotchas & Library Quirks

```python
# GOTCHA #1: Report Naming Must Be Exact
# Correct: TASK1_COMPLETION.md
# Wrong: TASK_1_COMPLETION.md (extra underscore)
# Wrong: TASK1_COMPLETE.md (COMPLETE vs COMPLETION)

# GOTCHA #2: Minimum Content Length
# Reports must have at least 100 characters
# Empty or very short files will fail validation

# GOTCHA #3: Template Variables
# All required variables must be provided
# Missing variables will cause KeyError
```

---

## Implementation Blueprint

### Task List

```yaml
Task 1: Create Hello World File
RESPONSIBILITY: Create a simple Python file with hello world function
FILES TO CREATE:
  - test_files/hello_world.py

PATTERN TO FOLLOW:
  - Simple Python function with docstring
  - Basic print statement

SPECIFIC STEPS:
  1. Create test_files/ directory
  2. Write hello_world.py with:
     - hello() function
     - Docstring explaining function
     - Main block that calls hello()
  3. Verify file is valid Python
  4. Create completion report using template

VALIDATION:
  - File exists at test_files/hello_world.py
  - File is valid Python (no syntax errors)
  - Completion report exists at prps/test_validation_gates/execution/TASK1_COMPLETION.md
  - Report has minimum 100 characters

---

Task 2: Enhance Hello World
RESPONSIBILITY: Modify hello world to accept name parameter
FILES TO MODIFY:
  - test_files/hello_world.py

PATTERN TO FOLLOW:
  - Function parameter addition
  - Default parameter value

SPECIFIC STEPS:
  1. Read existing hello_world.py
  2. Modify hello() to accept name parameter with default "World"
  3. Update docstring to document parameter
  4. Update main block to demonstrate parameter usage
  5. Verify changes work correctly
  6. Create completion report using template

VALIDATION:
  - Modified file has name parameter
  - Default value works correctly
  - Completion report exists at prps/test_validation_gates/execution/TASK2_COMPLETION.md
  - Report documents the modification

---

Task 3: Validate Implementation
RESPONSIBILITY: Run validation checks and document results
FILES TO CREATE:
  - test_files/validation_results.txt

PATTERN TO FOLLOW:
  - Run syntax check on hello_world.py
  - Document validation results

SPECIFIC STEPS:
  1. Run Python syntax check on hello_world.py
  2. Verify function can be imported
  3. Test function with different parameters
  4. Document results in validation_results.txt
  5. Create completion report using template

VALIDATION:
  - Syntax check passes
  - Function works as expected
  - Results documented in validation_results.txt
  - Completion report exists at prps/test_validation_gates/execution/TASK3_COMPLETION.md
  - Report includes validation status
```

---

## Validation Loop

### Level 1: File Creation Validation
```bash
# Verify all task files created
ls test_files/hello_world.py
ls test_files/validation_results.txt

# Expected: Both files exist
```

### Level 2: Report Validation
```bash
# Verify all completion reports exist
ls prps/test_validation_gates/execution/TASK1_COMPLETION.md
ls prps/test_validation_gates/execution/TASK2_COMPLETION.md
ls prps/test_validation_gates/execution/TASK3_COMPLETION.md

# Expected: All 3 reports exist with correct naming
```

### Level 3: Report Content Validation
```bash
# Verify reports have minimum content
for i in 1 2 3; do
  size=$(wc -c < prps/test_validation_gates/execution/TASK${i}_COMPLETION.md)
  if [ $size -lt 100 ]; then
    echo "ERROR: TASK${i} report too short ($size chars)"
  else
    echo "OK: TASK${i} report ($size chars)"
  fi
done

# Expected: All reports ≥100 characters
```

### Level 4: Coverage Calculation Validation
```python
# Test coverage calculation
from pathlib import Path
import re

def calculate_report_coverage(feature_name: str, total_tasks: int) -> dict:
    from glob import glob

    pattern = f"prps/{feature_name}/execution/TASK*_COMPLETION.md"
    task_reports = glob(pattern)
    reports_found = len(task_reports)

    coverage_pct = (reports_found / total_tasks) * 100 if total_tasks > 0 else 0

    reported_tasks = set()
    for report_path in task_reports:
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

# Test with 3 tasks
metrics = calculate_report_coverage("test_validation_gates", 3)
print(f"Coverage: {metrics['coverage_percentage']}%")
print(f"Status: {metrics['status']}")
print(f"Missing: {metrics['missing_tasks']}")

# Expected: 100%, COMPLETE, []
```

---

## Final Validation Checklist

### Test Execution
- [ ] All 3 tasks completed successfully
- [ ] All 3 files created in test_files/
- [ ] All 3 completion reports generated

### Validation Gate Testing
- [ ] Normal execution: All reports validated
- [ ] Missing report test: Validation gate catches issue
- [ ] Error message test: Actionable troubleshooting provided
- [ ] Coverage calculation: Accurate percentage computed

### Report Quality
- [ ] Reports follow TASK{n}_COMPLETION.md naming
- [ ] Reports have ≥100 characters
- [ ] Reports contain all required sections
- [ ] Reports document implementation accurately

### Metrics Display
- [ ] Final summary shows "Reports: 3/3 (100%)"
- [ ] Coverage percentage calculated correctly
- [ ] Status shows "✅ COMPLETE" for 100% coverage

---

## Success Metrics

### Quantitative
- 3/3 tasks completed (100%)
- 3/3 reports generated (100% coverage)
- 0 validation errors in final execution
- All reports follow standardized naming

### Qualitative
- Validation gates work as designed
- Error messages are actionable
- Coverage calculation is accurate
- Test PRP demonstrates reliability improvements

---

## PRP Quality Self-Assessment

**Score: 10/10** - Simple test PRP with clear success criteria

**Reasoning**:
- ✅ Minimal complexity - 3 simple tasks focused on testing validation
- ✅ Clear validation criteria at each level
- ✅ Tests all critical validation gate features
- ✅ No external dependencies (just Python standard library)
- ✅ Easy to verify success/failure

**Test Coverage**:
- Normal execution path (all reports generated)
- Error detection path (missing reports caught)
- Error message quality (actionable guidance)
- Metrics calculation (coverage percentage)

**Implementation readiness**: Ready for execution immediately.
