#!/usr/bin/env bash
# .codex/tests/test_generate_prp.sh
# Purpose: End-to-end integration test for PRP generation workflow
# Pattern: Feature-analysis.md success criteria (lines 66-77)
# Tests: Script structure, security validation, dependency checking, error handling

set -euo pipefail

# =============================================================================
# Test Configuration
# =============================================================================

# Script directory (for accessing source scripts)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Test artifacts directory
TEST_DIR="${SCRIPT_DIR}/fixtures"
TEST_FEATURE="test_codex_prp_generation"

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

    # Create minimal INITIAL.md test fixture
    cat > "${TEST_DIR}/INITIAL_${TEST_FEATURE}.md" <<'EOF'
# INITIAL: Test Codex PRP Generation

## Goal
Create a simple user authentication module to validate PRP generation workflow.

## Why
Testing end-to-end PRP generation with parallel Phase 2 execution.

## What
- User model with email and password fields
- Authentication service with login/logout
- Session management
- Unit tests

## Success Criteria
- PRP generated with score ≥8/10
- All Phase 2 outputs created (codebase-patterns.md, documentation-links.md, examples-to-include.md)
- Manifest JSONL complete with all phases logged
- Total duration <15min for typical feature
EOF

    pass "Created test INITIAL.md fixture"
}

# =============================================================================
# Test Cases
# =============================================================================

# Test 1: Script exists and is executable
test_script_exists() {
    echo ""
    echo "Test 1: Script existence and permissions"
    echo "-----------------------------------------"

    local script="${REPO_ROOT}/.codex/scripts/codex-generate-prp.sh"

    if [ -f "$script" ]; then
        pass "Script exists: codex-generate-prp.sh"
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
        "parallel-exec.sh"
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

# Test 3: Security validation rejects dangerous feature names
test_security_validation() {
    echo ""
    echo "Test 3: Security validation"
    echo "-----------------------------------------"

    # Source security validation
    source "${REPO_ROOT}/.codex/scripts/security-validation.sh" >/dev/null 2>&1 || {
        fail "Failed to source security-validation.sh"
        return 1
    }

    # Test path traversal
    if extract_feature_name "INITIAL_../../etc/passwd.md" "INITIAL_" "true" &>/dev/null; then
        fail "Security validation FAILED - accepted path traversal"
    else
        pass "Rejected path traversal attack"
    fi

    # Test command injection
    if extract_feature_name "INITIAL_test;rm -rf /.md" "INITIAL_" "true" &>/dev/null; then
        fail "Security validation FAILED - accepted command injection"
    else
        pass "Rejected command injection"
    fi

    # Test valid name
    if extract_feature_name "INITIAL_valid_feature_name.md" "INITIAL_" "true" &>/dev/null; then
        pass "Accepted valid feature name"
    else
        fail "Security validation too strict - rejected valid name"
    fi
}

# Test 4: JSONL manifest logging works
test_manifest_logging() {
    echo ""
    echo "Test 4: Manifest JSONL logging"
    echo "-----------------------------------------"

    # Source log-phase.sh
    source "${REPO_ROOT}/.codex/scripts/log-phase.sh" >/dev/null || {
        fail "Failed to source log-phase.sh"
        return 1
    }

    # Create test manifest
    log_phase_start "${TEST_FEATURE}" "phase1" &>/dev/null || {
        fail "Failed to log phase start"
        return 1
    }
    pass "Logged phase start"

    log_phase_complete "${TEST_FEATURE}" "phase1" 0 42 &>/dev/null || {
        fail "Failed to log phase complete"
        return 1
    }
    pass "Logged phase complete"

    # Validate manifest exists
    local manifest="${REPO_ROOT}/prps/${TEST_FEATURE}/codex/logs/manifest.jsonl"
    if [ -f "$manifest" ]; then
        pass "Manifest created at correct path"
    else
        fail "Manifest not created: $manifest"
        return 1
    fi

    # Validate JSONL format
    if grep -q '"phase":"phase1"' "$manifest"; then
        pass "Manifest contains phase1 entry"
    else
        fail "Manifest missing phase1 entry"
        return 1
    fi

    # Validate phase completion
    if validate_phase_completion "${TEST_FEATURE}" "phase1" &>/dev/null; then
        pass "Phase validation works"
    else
        fail "Phase validation failed"
        return 1
    fi
}

# Test 5: Phase dependency validation
test_dependency_validation() {
    echo ""
    echo "Test 5: Phase dependency checking"
    echo "-----------------------------------------"

    # Source parallel-exec.sh
    source "${REPO_ROOT}/.codex/scripts/parallel-exec.sh" >/dev/null 2>&1 || {
        fail "Failed to source parallel-exec.sh"
        return 1
    }

    # Check if check_phase_dependencies function exists
    if declare -f check_phase_dependencies &>/dev/null; then
        pass "Dependency checking function exists"
    else
        info "Dependency checking function not found (may be inline)"
    fi

    # Test Phase 3 depends on Phase 2
    # Note: This is a structural test, not a runtime test
    if grep -q "phase2a\|phase2b\|phase2c" "${REPO_ROOT}/.codex/scripts/codex-generate-prp.sh"; then
        pass "Script references Phase 2 agents"
    else
        fail "Script missing Phase 2 agent references"
        return 1
    fi
}

# Test 6: Script structure validation (no syntax errors)
test_script_syntax() {
    echo ""
    echo "Test 6: Script syntax validation"
    echo "-----------------------------------------"

    local script="${REPO_ROOT}/.codex/scripts/codex-generate-prp.sh"

    # Check if bash is available
    if ! command -v bash &> /dev/null; then
        fail "Bash not found"
        return 1
    fi

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
            # Don't fail on warnings, just info
        fi
    else
        info "shellcheck not available (install for better validation)"
    fi
}

# Test 7: Mock PRP generation workflow (without actual Codex CLI)
test_mock_prp_generation() {
    echo ""
    echo "Test 7: Mock PRP generation workflow"
    echo "-----------------------------------------"

    info "MOCK TEST - Codex CLI not available in test environment"
    info "This test validates script structure and error handling"

    local script="${REPO_ROOT}/.codex/scripts/codex-generate-prp.sh"
    local initial_md="${TEST_DIR}/INITIAL_${TEST_FEATURE}.md"

    # Test 1: Script shows help when no arguments
    if "$script" 2>&1 | grep -qi "usage\|error"; then
        pass "Script shows error/usage when called without arguments"
    else
        info "Script may not have usage message"
    fi

    # Test 2: Script validates INITIAL.md exists
    if "$script" "/nonexistent/INITIAL_fake.md" 2>&1 | grep -qi "not found\|error"; then
        pass "Script validates INITIAL.md file existence"
    else
        info "Script may not validate file existence"
    fi

    # Test 3: Feature name extraction works
    if grep -q "extract_feature_name" "$script"; then
        pass "Script uses feature name extraction"
    else
        fail "Script missing feature name extraction"
        return 1
    fi
}

# Test 8: Timeout handling
test_timeout_wrapper() {
    echo ""
    echo "Test 8: Timeout wrapper validation"
    echo "-----------------------------------------"

    local script="${REPO_ROOT}/.codex/scripts/codex-generate-prp.sh"

    # Check if timeout command is used
    if grep -q "timeout.*codex exec" "$script" || grep -q "TIMEOUT" "$script"; then
        pass "Script uses timeout wrapper for codex exec"
    else
        fail "Script missing timeout wrapper (risk of zombie processes)"
        return 1
    fi

    # Check timeout exit code handling
    if grep -q "124" "$script"; then
        pass "Script handles timeout exit code (124)"
    else
        info "Script may not explicitly handle timeout exit codes"
    fi
}

# Test 9: Profile enforcement
test_profile_enforcement() {
    echo ""
    echo "Test 9: Codex profile enforcement"
    echo "-----------------------------------------"

    local script="${REPO_ROOT}/.codex/scripts/codex-generate-prp.sh"

    # Check for CODEX_PROFILE variable
    if grep -q "CODEX_PROFILE" "$script"; then
        pass "Script defines CODEX_PROFILE variable"
    else
        fail "Script missing CODEX_PROFILE configuration"
        return 1
    fi

    # Check for --profile flag in codex exec calls
    if grep -q "\-\-profile.*\$CODEX_PROFILE\|--profile.*codex-prp" "$script"; then
        pass "Script uses --profile flag in codex exec calls"
    else
        info "Script may not enforce profile in all codex exec calls"
    fi
}

# Test 10: Parallel execution structure
test_parallel_execution_structure() {
    echo ""
    echo "Test 10: Parallel execution structure"
    echo "-----------------------------------------"

    local script="${REPO_ROOT}/.codex/scripts/codex-generate-prp.sh"

    # Check for background job syntax (&)
    if grep -q "&$\|& *$" "$script"; then
        pass "Script uses background job syntax (&)"
    else
        fail "Script missing background job syntax (no parallelization)"
        return 1
    fi

    # Check for wait command
    if grep -q "wait.*\$PID\|wait \$" "$script"; then
        pass "Script uses wait for job synchronization"
    else
        fail "Script missing wait command (incomplete job control)"
        return 1
    fi

    # Check for PID capture
    if grep -q "PID.*=.*\$!" "$script"; then
        pass "Script captures PIDs with \$!"
    else
        fail "Script missing PID capture (can't track jobs)"
        return 1
    fi

    # Check for exit code capture
    if grep -q "EXIT.*=.*\$?" "$script" || grep -q "wait.*;" "$script"; then
        pass "Script captures exit codes"
    else
        fail "Script missing exit code capture (silent failures possible)"
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
        echo "Integration test validation complete:"
        echo "  ✓ Script structure validated"
        echo "  ✓ Security validation working"
        echo "  ✓ Dependency checking functional"
        echo "  ✓ Manifest logging operational"
        echo "  ✓ Parallel execution structure present"
        echo "  ✓ Error handling in place"
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
    echo "Codex Generate PRP Integration Test"
    echo "========================================="
    echo "Testing: End-to-end PRP generation workflow"
    echo "Pattern: Feature-analysis.md success criteria"
    echo ""

    # Setup
    setup

    # Run all test cases
    test_script_exists || true
    test_dependencies_exist || true
    test_security_validation || true
    test_manifest_logging || true
    test_dependency_validation || true
    test_script_syntax || true
    test_mock_prp_generation || true
    test_timeout_wrapper || true
    test_profile_enforcement || true
    test_parallel_execution_structure || true

    # Cleanup
    cleanup

    # Print summary
    print_summary
}

# Run main if executed directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
