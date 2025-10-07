# Validation Report: {feature_name}

## Validation Summary

**Overall Status**: {✅ PASS / ❌ FAIL}
**Total Levels**: {X}
**Levels Passed**: {Y}
**Issues Found**: {Z}

## Validation Levels

### Level 1: Syntax & Style Checks

**Status**: {✅ PASS / ❌ FAIL}

**Commands Run**:
```bash
ruff check --fix .
mypy .
```

**Results**:
- Ruff: {status} - {details}
- MyPy: {status} - {details}

**Issues**: {list any issues or "None"}

---

### Level 2: Unit Tests

**Status**: {✅ PASS / ❌ FAIL}

**Commands Run**:
```bash
pytest tests/ -v
```

**Results**:
- Tests Run: {count}
- Passed: {count}
- Failed: {count}
- Coverage: {percentage}%

**Failed Tests** (if any):
- {test_name}: {error_message}

---

### Level 3: Integration Tests

**Status**: {✅ PASS / ❌ FAIL}

**Commands Run**:
```bash
{project-specific commands from PRP}
```

**Results**:
{test results}

**Issues**: {list any issues or "None"}

---

## Issue Details

### Issue #1: {Issue Title}
- **Severity**: {Critical/High/Medium/Low}
- **Location**: {file:line}
- **Description**: {what's wrong}
- **Fix Applied**: {what was done}
- **Status**: {Fixed/Pending/Cannot Fix}

### Issue #2: {Issue Title}
...

---

## Validation Iterations

| Attempt | Level | Result | Duration | Issues Fixed |
|---------|-------|--------|----------|--------------|
| 1 | Level 1 | ❌ FAIL | 2min | Syntax errors in file.py |
| 2 | Level 1 | ✅ PASS | 1min | - |
| 3 | Level 2 | ❌ FAIL | 5min | Test assertion error |
| 4 | Level 2 | ✅ PASS | 4min | - |
| 5 | Level 3 | ✅ PASS | 3min | - |

**Total Attempts**: {count}
**Total Time**: {X} minutes

---

## Recommendations

{Optional section with suggestions for improvement or next steps}

---

## Next Steps

- [ ] {action item 1}
- [ ] {action item 2}
- [ ] {action item 3}
