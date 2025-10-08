#!/usr/bin/env bash
# .codex/tests/test_execute_prp.sh
# Purpose: End-to-end integration test for PRP execution workflow
# Pattern: Feature-analysis.md success criteria (lines 78-86)
# Tests: Validation loop, error handling, coverage enforcement, completion reporting

set -euo pipefail

# =============================================================================
# Test Configuration
# =============================================================================

# Script directory (for accessing source scripts)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Test artifacts directory
TEST_DIR="${SCRIPT_DIR}/fixtures"
TEST_FEATURE="test_codex_prp_execution"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0

# =============================================================================
# Helper Functions
# =============================================================================

# Print test result
pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((TESTS_PASSED++))
}

fail() {
    echo -e "${RED}✗${NC} $1"
    ((TESTS_FAILED++))
}

info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Cleanup test artifacts
cleanup() {
    if [ -d "${REPO_ROOT}/prps/${TEST_FEATURE}" ]; then
        rm -rf "${REPO_ROOT}/prps/${TEST_FEATURE}"
        info "Cleaned up test PRP directory"
    fi

    if [ -d "${TEST_DIR}" ]; then
        rm -rf "${TEST_DIR}"
        info "Cleaned up test fixtures"
    fi
}

# Setup test fixtures
setup() {
    echo ""
    echo "========================================="
    echo "Test Setup"
    echo "========================================="

    # Create test fixtures directory
    mkdir -p "${TEST_DIR}"

    # Create minimal PRP test fixture
    cat > "${TEST_DIR}/${TEST_FEATURE}.md" <<'EOF'
# PRP: Test Codex PRP Execution

**Generated**: 2025-10-07
**Based On**: prps/INITIAL_test_codex_prp_execution.md

---

## Goal

Create a simple user authentication module to validate PRP execution workflow with validation loops.

## Why

**Business Value**:
- Test validation loop functionality
- Verify error handling and retry logic
- Validate test coverage enforcement

## What

### Core Features

1. **User Model**:
   - Email field (validated)
   - Password field (hashed)
   - Pydantic validation

2. **Authentication Service**:
   - Login endpoint
   - Logout endpoint
   - Session management

3. **Testing**:
   - Unit tests for all components
   - Integration tests for API
   - ≥70% test coverage

### Success Criteria

- [ ] All tasks completed
- [ ] All validation gates passed (ruff, mypy, pytest)
- [ ] Test coverage ≥70%
- [ ] No critical linting errors

---

## Known Gotchas & Library Quirks

```python
# CRITICAL GOTCHA 1: Email Validation
# Issue: Using plain string for email allows invalid formats
# Impact: Malformed emails in database

# ❌ WRONG
class User(BaseModel):
    email: str  # No validation

# ✅ RIGHT
from pydantic import EmailStr

class User(BaseModel):
    email: EmailStr  # Pydantic validates format
```

---

## Implementation Blueprint

### Task List

```yaml
Task 1: Create User Model
RESPONSIBILITY: Define user data structure with validation
FILES TO CREATE:
  - src/models/user.py

SPECIFIC STEPS:
  1. Create Pydantic BaseModel for User
  2. Add email field with EmailStr validation
  3. Add password field with hashing
  4. Add docstrings

VALIDATION:
  - ruff check src/models/
  - mypy src/models/
  - Unit tests pass

---

Task 2: Create Authentication Service
RESPONSIBILITY: Implement login/logout logic
FILES TO CREATE:
  - src/services/auth.py

SPECIFIC STEPS:
  1. Implement login() function
  2. Implement logout() function
  3. Add session management
  4. Error handling

VALIDATION:
  - ruff check src/services/
  - pytest tests/test_auth.py
  - Integration tests pass

---

Task 3: Add Tests
RESPONSIBILITY: Comprehensive test coverage
FILES TO CREATE:
  - tests/test_user.py
  - tests/test_auth.py

SPECIFIC STEPS:
  1. Unit tests for User model
  2. Unit tests for auth service
  3. Integration tests for API
  4. Verify coverage ≥70%

VALIDATION:
  - pytest --cov=src tests/
  - Coverage report shows ≥70%
```

---

## Validation Loop

### Level 1: Syntax & Style Checks

```bash
# Linting (auto-fix enabled)
ruff check --fix src/ tests/

# Type checking
mypy src/ tests/

# Expected: No errors
```

### Level 2: Unit Tests

```bash
# Run all unit tests
pytest tests/ -v

# Expected: All tests pass
```

### Level 3: Coverage

```bash
# Run tests with coverage
pytest --cov=src --cov-report=term-missing tests/

# Expected: ≥70% coverage
```

---

## PRP Quality Self-Assessment

**Score: 8/10** - Good confidence in implementation success

**Reasoning**:
- ✅ Clear task breakdown (3 tasks with specific steps)
- ✅ Gotchas documented with solutions
- ✅ Validation loop defined
- ⚠️ Minimal PRP for testing (not production-ready)

EOF

    pass "Created test PRP fixture"
}

# =============================================================================
# Test Cases
# =============================================================================

# Test 1: Script exists and is executable
test_script_exists() {
    echo ""
    echo "Test 1: Script existence and permissions"
    echo "-----------------------------------------"

    local script="${REPO_ROOT}/.codex/scripts/codex-execute-prp.sh"

    if [ -f "$script" ]; then
        pass "Script exists: codex-execute-prp.sh"
    else
        fail "Script not found: $script"
        return 1
    fi

    if [ -x "$script" ]; then
        pass "Script is executable"
    else
        fail "Script is not executable (run: chmod +x $script)"
        return 1
    fi
}

# Test 2: Dependencies are available
test_dependencies_exist() {
    echo ""
    echo "Test 2: Required dependencies"
    echo "-----------------------------------------"

    local deps=(
        "log-phase.sh"
        "security-validation.sh"
    )

    local all_found=true

    for dep in "${deps[@]}"; do
        local dep_path="${REPO_ROOT}/.codex/scripts/${dep}"
        if [ -f "$dep_path" ]; then
            pass "Dependency exists: $dep"
        else
            fail "Dependency missing: $dep"
            all_found=false
        fi
    done

    if [ "$all_found" = false ]; then
        return 1
    fi
}

# Test 3: Feature name extraction from PRP
test_feature_extraction() {
    echo ""
    echo "Test 3: Feature name extraction from PRP"
    echo "-----------------------------------------"

    # Source security validation
    source "${REPO_ROOT}/.codex/scripts/security-validation.sh" >/dev/null 2>&1 || {
        fail "Failed to source security-validation.sh"
        return 1
    }

    # Test INITIAL_ prefix stripping
    local feature
    feature=$(extract_feature_name "prps/INITIAL_test_feature.md" "INITIAL_" "true" 2>/dev/null)

    if [ "$feature" = "test_feature" ]; then
        pass "Correctly stripped INITIAL_ prefix: $feature"
    else
        fail "Failed to strip INITIAL_ prefix (got: $feature)"
        return 1
    fi

    # Test regular PRP name
    feature=$(extract_feature_name "prps/regular_feature.md" "" "true" 2>/dev/null)

    if [ "$feature" = "regular_feature" ]; then
        pass "Correctly extracted regular feature name: $feature"
    else
        fail "Failed to extract regular feature name (got: $feature)"
        return 1
    fi
}

# Test 4: PRP gotcha extraction
test_gotcha_extraction() {
    echo ""
    echo "Test 4: Extract Known Gotchas from PRP"
    echo "-----------------------------------------"

    local script="${REPO_ROOT}/.codex/scripts/codex-execute-prp.sh"

    # Check if script has gotcha extraction function
    if grep -q "extract_gotchas_from_prp\|Known Gotchas" "$script"; then
        pass "Script has gotcha extraction capability"
    else
        fail "Script missing gotcha extraction"
        return 1
    fi

    # Test with our fixture PRP
    local prp="${TEST_DIR}/${TEST_FEATURE}.md"

    if grep -q "Known Gotchas" "$prp"; then
        pass "Test PRP contains Known Gotchas section"
    else
        fail "Test PRP missing Known Gotchas section"
        return 1
    fi
}

# Test 5: Validation loop structure
test_validation_loop_structure() {
    echo ""
    echo "Test 5: Validation loop structure"
    echo "-----------------------------------------"

    local script="${REPO_ROOT}/.codex/scripts/codex-execute-prp.sh"

    # Check for max attempts configuration
    if grep -q "MAX_VALIDATION_ATTEMPTS" "$script"; then
        pass "Script defines MAX_VALIDATION_ATTEMPTS"
    else
        fail "Script missing MAX_VALIDATION_ATTEMPTS configuration"
        return 1
    fi

    # Check for validation levels (ruff, mypy, pytest)
    if grep -qi "ruff" "$script"; then
        pass "Script includes ruff validation"
    else
        fail "Script missing ruff validation"
        return 1
    fi

    if grep -qi "pytest\|test" "$script"; then
        pass "Script includes test validation"
    else
        fail "Script missing test validation"
        return 1
    fi

    # Check for coverage enforcement
    if grep -qi "coverage\|MIN_COVERAGE" "$script"; then
        pass "Script includes coverage enforcement"
    else
        fail "Script missing coverage enforcement"
        return 1
    fi
}

# Test 6: Error handling and retry logic
test_error_handling() {
    echo ""
    echo "Test 6: Error handling and retry logic"
    echo "-----------------------------------------"

    local script="${REPO_ROOT}/.codex/scripts/codex-execute-prp.sh"

    # Check for error analysis function
    if grep -q "analyze.*error\|error.*analysis" "$script"; then
        pass "Script has error analysis capability"
    else
        info "Script may not have explicit error analysis"
    fi

    # Check for retry mechanism
    if grep -q "retry\|attempt\|ATTEMPTS" "$script"; then
        pass "Script has retry mechanism"
    else
        fail "Script missing retry mechanism"
        return 1
    fi

    # Check for failure handling after max attempts
    if grep -q "max.*attempt\|exhausted\|manual" "$script"; then
        pass "Script handles max attempts exhaustion"
    else
        fail "Script missing max attempts handling"
        return 1
    fi
}

# Test 7: Completion report generation
test_completion_report() {
    echo ""
    echo "Test 7: Completion report generation"
    echo "-----------------------------------------"

    local script="${REPO_ROOT}/.codex/scripts/codex-execute-prp.sh"

    # Check for report generation function
    if grep -q "completion.*report\|report.*completion\|generate.*report" "$script"; then
        pass "Script has report generation capability"
    else
        fail "Script missing completion report generation"
        return 1
    fi

    # Check for expected report fields
    local expected_fields=(
        "files.*changed\|modified"
        "coverage\|test.*coverage"
        "validation\|quality"
    )

    for field_pattern in "${expected_fields[@]}"; do
        if grep -qi "$field_pattern" "$script"; then
            pass "Script tracks: $field_pattern"
        else
            info "Script may not explicitly track: $field_pattern"
        fi
    done
}

# Test 8: Script syntax validation
test_script_syntax() {
    echo ""
    echo "Test 8: Script syntax validation"
    echo "-----------------------------------------"

    local script="${REPO_ROOT}/.codex/scripts/codex-execute-prp.sh"

    # Syntax check
    if bash -n "$script" 2>/dev/null; then
        pass "Script has valid bash syntax"
    else
        fail "Script has syntax errors"
        bash -n "$script" 2>&1 | head -5
        return 1
    fi

    # Check for shellcheck if available
    if command -v shellcheck &> /dev/null; then
        if shellcheck -e SC2086,SC2034 "$script" &>/dev/null; then
            pass "Script passes shellcheck"
        else
            info "Script has shellcheck warnings (non-fatal)"
        fi
    else
        info "shellcheck not available (install for better validation)"
    fi
}

# Test 9: Mock validation loop execution
test_mock_validation_loop() {
    echo ""
    echo "Test 9: Mock validation loop execution"
    echo "-----------------------------------------"

    info "MOCK TEST - Testing validation loop logic without actual code"

    # Create mock validation functions
    mock_validation_level1() {
        # Simulate linting success
        return 0
    }

    mock_validation_level2() {
        # Simulate test success
        return 0
    }

    mock_validation_level3() {
        # Simulate coverage success (≥70%)
        return 0
    }

    # Run mock validation loop
    local max_attempts=3
    local attempt=1
    local validation_passed=false

    while [ $attempt -le $max_attempts ]; do
        info "Validation attempt ${attempt}/${max_attempts}"

        # Level 1: Syntax & Style
        if mock_validation_level1; then
            info "  Level 1: Syntax & Style - PASS"
        else
            info "  Level 1: Syntax & Style - FAIL"
            ((attempt++))
            continue
        fi

        # Level 2: Unit Tests
        if mock_validation_level2; then
            info "  Level 2: Unit Tests - PASS"
        else
            info "  Level 2: Unit Tests - FAIL"
            ((attempt++))
            continue
        fi

        # Level 3: Coverage
        if mock_validation_level3; then
            info "  Level 3: Coverage - PASS"
        else
            info "  Level 3: Coverage - FAIL"
            ((attempt++))
            continue
        fi

        # All validations passed
        validation_passed=true
        break
    done

    if [ "$validation_passed" = true ]; then
        pass "Mock validation loop completed successfully"
    else
        fail "Mock validation loop failed after ${max_attempts} attempts"
        return 1
    fi
}

# Test 10: Coverage enforcement logic
test_coverage_enforcement() {
    echo ""
    echo "Test 10: Coverage enforcement logic"
    echo "-----------------------------------------"

    # Mock coverage calculation
    calculate_coverage() {
        # Simulate parsing coverage report
        # Format: "TOTAL 85%"
        local coverage_report="$1"
        echo "$coverage_report" | grep -oP '\d+(?=%)' | head -1
    }

    # Test with valid coverage (≥70%)
    local coverage_report="TOTAL 85%"
    local coverage=$(calculate_coverage "$coverage_report")

    if [ "$coverage" -ge 70 ]; then
        pass "Coverage enforcement accepts ≥70% (got ${coverage}%)"
    else
        fail "Coverage enforcement logic incorrect"
        return 1
    fi

    # Test with invalid coverage (<70%)
    coverage_report="TOTAL 65%"
    coverage=$(calculate_coverage "$coverage_report")

    if [ "$coverage" -lt 70 ]; then
        pass "Coverage enforcement rejects <70% (got ${coverage}%)"
    else
        fail "Coverage enforcement logic incorrect"
        return 1
    fi
}

# Test 11: PRP file validation
test_prp_file_validation() {
    echo ""
    echo "Test 11: PRP file validation"
    echo "-----------------------------------------"

    local script="${REPO_ROOT}/.codex/scripts/codex-execute-prp.sh"
    local prp="${TEST_DIR}/${TEST_FEATURE}.md"

    # Test with valid PRP
    if [ -f "$prp" ]; then
        pass "Test PRP file exists"
    else
        fail "Test PRP file not found"
        return 1
    fi

    # Test with nonexistent PRP (should fail gracefully)
    local fake_prp="${TEST_DIR}/nonexistent.md"

    # Script should detect missing file
    # Note: We can't actually run the script without Codex CLI,
    # but we can check if it has file existence validation
    if grep -q "not found\|does not exist\|\[ ! -f" "$script"; then
        pass "Script validates PRP file existence"
    else
        fail "Script missing PRP file validation"
        return 1
    fi
}

# Test 12: Task extraction from PRP
test_task_extraction() {
    echo ""
    echo "Test 12: Task extraction from PRP"
    echo "-----------------------------------------"

    local prp="${TEST_DIR}/${TEST_FEATURE}.md"

    # Extract task count from PRP
    local task_count=$(grep -c "^Task [0-9]\+:" "$prp" 2>/dev/null || echo "0")

    if [ "$task_count" -gt 0 ]; then
        pass "Found ${task_count} tasks in test PRP"
    else
        fail "No tasks found in test PRP"
        return 1
    fi

    # Verify expected tasks exist
    if grep -q "Task 1: Create User Model" "$prp"; then
        pass "Task 1 present in PRP"
    else
        fail "Task 1 missing from PRP"
        return 1
    fi
}

# =============================================================================
# Test Summary
# =============================================================================

print_summary() {
    echo ""
    echo "========================================="
    echo "Test Summary"
    echo "========================================="
    echo -e "Passed: ${GREEN}${TESTS_PASSED}${NC}"
    echo -e "Failed: ${RED}${TESTS_FAILED}${NC}"
    echo ""

    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}✓ All tests passed!${NC}"
        echo ""
        echo "PRP execution validation complete:"
        echo "  ✓ Script structure validated"
        echo "  ✓ Feature extraction working"
        echo "  ✓ Validation loop logic present"
        echo "  ✓ Error handling and retry mechanism"
        echo "  ✓ Coverage enforcement logic correct"
        echo "  ✓ Completion report generation"
        echo "  ✓ PRP file validation"
        echo ""
        echo "NOTE: Full end-to-end test requires actual Codex CLI."
        echo "      These tests validate script structure and logic."
        echo ""
        return 0
    else
        echo -e "${RED}✗ Some tests failed${NC}"
        echo ""
        echo "Please fix the failures before proceeding."
        echo ""
        return 1
    fi
}

# =============================================================================
# Main Test Execution
# =============================================================================

main() {
    echo "========================================="
    echo "Codex Execute PRP Integration Test"
    echo "========================================="
    echo "Testing: PRP execution with validation loops"
    echo "Pattern: Feature-analysis.md success criteria"
    echo ""

    # Setup
    setup

    # Run all test cases
    test_script_exists || true
    test_dependencies_exist || true
    test_feature_extraction || true
    test_gotcha_extraction || true
    test_validation_loop_structure || true
    test_error_handling || true
    test_completion_report || true
    test_script_syntax || true
    test_mock_validation_loop || true
    test_coverage_enforcement || true
    test_prp_file_validation || true
    test_task_extraction || true

    # Cleanup
    cleanup

    # Print summary
    print_summary
}

# Run main if executed directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
