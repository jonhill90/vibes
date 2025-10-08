#!/bin/bash
# Source: tests/codex/test_generate_prp.sh
# Lines: 269-303, 104-124, 50-61
# Pattern: Bash script validation and test framework
# Extracted: 2025-10-08
# Relevance: 9/10 - Needed for post-migration validation

set -euo pipefail

# =============================================================================
# PATTERN 1: Bash Syntax Validation
# =============================================================================
# Use Case: Verify all moved scripts have valid bash syntax
# Command: bash -n (parse but don't execute)

validate_script_syntax() {
    local script="$1"

    echo "Validating syntax: ${script}"

    # Check if bash is available
    if ! command -v bash &> /dev/null; then
        echo "❌ ERROR: Bash not found"
        return 1
    fi

    # Syntax check with bash -n
    if bash -n "$script" 2>/dev/null; then
        echo "✅ Valid bash syntax"
        return 0
    else
        echo "❌ Syntax errors found:"
        bash -n "$script" 2>&1 | head -5
        return 1
    fi
}

# =============================================================================
# PATTERN 2: Batch Validation of All Scripts
# =============================================================================
# Use Case: Validate all scripts in .codex/scripts/ directory

validate_all_scripts() {
    local script_dir="$1"

    echo "========================================="
    echo "Validating all scripts in: ${script_dir}"
    echo "========================================="

    local all_valid=true
    local total_scripts=0
    local valid_scripts=0

    # Find all .sh files
    while IFS= read -r script; do
        ((total_scripts++))

        if bash -n "$script" 2>/dev/null; then
            echo "✅ ${script}"
            ((valid_scripts++))
        else
            echo "❌ ${script}"
            bash -n "$script" 2>&1 | head -3
            all_valid=false
        fi
    done < <(find "$script_dir" -name "*.sh" -type f)

    echo ""
    echo "Results: ${valid_scripts}/${total_scripts} scripts valid"

    if [ "$all_valid" = true ]; then
        echo "✅ All scripts passed syntax validation"
        return 0
    else
        echo "❌ Some scripts have syntax errors"
        return 1
    fi
}

# =============================================================================
# PATTERN 3: Test Framework - Pass/Fail Tracking
# =============================================================================
# Use Case: Track test results with counters and colored output

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0

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

# =============================================================================
# PATTERN 4: Cleanup Function
# =============================================================================
# Use Case: Clean up test artifacts after validation

cleanup_test_artifacts() {
    local test_dir="$1"

    if [ -d "${test_dir}" ]; then
        rm -rf "${test_dir}"
        info "Cleaned up test directory: ${test_dir}"
    fi
}

# =============================================================================
# PATTERN 5: File Existence and Permission Checks
# =============================================================================

test_script_exists_and_executable() {
    local script="$1"

    echo "Test: Script existence and permissions"
    echo "---------------------------------------"

    # Check existence
    if [ -f "$script" ]; then
        pass "Script exists: $(basename $script)"
    else
        fail "Script not found: $script"
        return 1
    fi

    # Check executable permission
    if [ -x "$script" ]; then
        pass "Script is executable"
    else
        fail "Script is not executable (run: chmod +x $script)"
        return 1
    fi

    return 0
}

# =============================================================================
# PATTERN 6: Dependency Checking
# =============================================================================
# Use Case: Verify all required dependencies exist after move

test_dependencies_exist() {
    local base_dir="$1"
    shift
    local deps=("$@")

    echo "Test: Required dependencies"
    echo "----------------------------"

    local all_found=true

    for dep in "${deps[@]}"; do
        local dep_path="${base_dir}/${dep}"
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

    return 0
}

# =============================================================================
# PATTERN 7: Test Summary Report
# =============================================================================

print_test_summary() {
    echo ""
    echo "========================================="
    echo "Test Summary"
    echo "========================================="
    echo -e "Passed: ${GREEN}${TESTS_PASSED}${NC}"
    echo -e "Failed: ${RED}${TESTS_FAILED}${NC}"
    echo ""

    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}✓ All tests passed!${NC}"
        return 0
    else
        echo -e "${RED}✗ Some tests failed${NC}"
        return 1
    fi
}

# =============================================================================
# PATTERN 8: Post-Migration Validation Suite
# =============================================================================

validate_codex_reorganization() {
    echo "========================================="
    echo "Codex Reorganization: Post-Migration Validation"
    echo "========================================="

    # Reset counters
    TESTS_PASSED=0
    TESTS_FAILED=0

    # Test 1: Scripts exist
    echo ""
    echo "Test 1: Script existence"
    echo "------------------------"
    local scripts=(
        ".codex/scripts/parallel-exec.sh"
        ".codex/scripts/codex-generate-prp.sh"
        ".codex/scripts/codex-execute-prp.sh"
        ".codex/scripts/log-phase.sh"
        ".codex/scripts/quality-gate.sh"
    )

    for script in "${scripts[@]}"; do
        if [ -f "$script" ]; then
            pass "Exists: $script"
        else
            fail "Missing: $script"
        fi
    done

    # Test 2: Tests exist
    echo ""
    echo "Test 2: Test file existence"
    echo "----------------------------"
    local tests=(
        ".codex/tests/test_generate_prp.sh"
        ".codex/tests/test_execute_prp.sh"
        ".codex/tests/test_parallel_timing.sh"
    )

    for test in "${tests[@]}"; do
        if [ -f "$test" ]; then
            pass "Exists: $test"
        else
            fail "Missing: $test"
        fi
    done

    # Test 3: Fixtures directory
    echo ""
    echo "Test 3: Fixtures directory"
    echo "--------------------------"
    if [ -d ".codex/tests/fixtures" ]; then
        pass "Fixtures directory exists"
    else
        fail "Fixtures directory missing"
    fi

    # Test 4: Old directories removed
    echo ""
    echo "Test 4: Old directories cleanup"
    echo "-------------------------------"
    if [ ! -d "scripts/codex" ]; then
        pass "Old directory removed: scripts/codex"
    else
        fail "Old directory still exists: scripts/codex"
    fi

    if [ ! -d "tests/codex" ]; then
        pass "Old directory removed: tests/codex"
    else
        fail "Old directory still exists: tests/codex"
    fi

    # Test 5: Syntax validation
    echo ""
    echo "Test 5: Script syntax validation"
    echo "---------------------------------"
    local syntax_errors=false
    for script in "${scripts[@]}"; do
        if [ -f "$script" ]; then
            if bash -n "$script" 2>/dev/null; then
                pass "Valid syntax: $(basename $script)"
            else
                fail "Syntax error: $(basename $script)"
                syntax_errors=true
            fi
        fi
    done

    # Test 6: Path references
    echo ""
    echo "Test 6: Path reference verification"
    echo "------------------------------------"
    local old_refs=$(grep -r "scripts/codex/" .codex/ 2>/dev/null | wc -l | tr -d ' ')
    if [ "$old_refs" -eq 0 ]; then
        pass "No old path references found (scripts/codex/)"
    else
        fail "Found $old_refs old path references"
        grep -rn "scripts/codex/" .codex/ 2>/dev/null | head -3
    fi

    local old_test_refs=$(grep -r "tests/codex/" .codex/ 2>/dev/null | wc -l | tr -d ' ')
    if [ "$old_test_refs" -eq 0 ]; then
        pass "No old test path references found (tests/codex/)"
    else
        fail "Found $old_test_refs old test path references"
        grep -rn "tests/codex/" .codex/ 2>/dev/null | head -3
    fi

    # Print summary
    print_test_summary
}

# =============================================================================
# PATTERN 9: Git History Verification
# =============================================================================

verify_git_history_preserved() {
    local file="$1"
    local original_name="$2"

    echo "Verifying git history for: ${file}"

    # Check that file shows "renamed from" in git log
    local rename_entry=$(git log --follow --format="%H" --name-status "$file" | grep "^R")

    if [ -n "$rename_entry" ]; then
        echo "✅ Git history preserved (file shows rename)"
        echo "   ${rename_entry}"
    else
        echo "⚠️  No rename entry found in git log"
        echo "   May indicate history loss or file wasn't renamed with git mv"
    fi

    # Check full history is accessible
    local commit_count=$(git log --follow --format="%H" "$file" | wc -l | tr -d ' ')
    echo "   Commit history: ${commit_count} commits"

    if [ "$commit_count" -gt 0 ]; then
        echo "✅ History accessible with --follow"
    else
        echo "❌ No history found"
        return 1
    fi
}

# =============================================================================
# PATTERN 10: Executable Permission Verification
# =============================================================================

verify_executable_permissions() {
    local script_dir="$1"

    echo "Verifying executable permissions..."

    local missing_exec=()

    while IFS= read -r script; do
        if [ ! -x "$script" ]; then
            missing_exec+=("$script")
        fi
    done < <(find "$script_dir" -name "*.sh" -type f)

    if [ ${#missing_exec[@]} -eq 0 ]; then
        echo "✅ All scripts are executable"
        return 0
    else
        echo "❌ Some scripts missing executable permission:"
        for script in "${missing_exec[@]}"; do
            echo "   - $script"
        done
        echo ""
        echo "Fix with: chmod +x ${missing_exec[@]}"
        return 1
    fi
}

# =============================================================================
# USAGE EXAMPLE
# =============================================================================

if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    echo "Bash Validation Pattern Examples"
    echo "================================="
    echo ""
    echo "Available functions:"
    echo "  - validate_script_syntax <script>"
    echo "  - validate_all_scripts <directory>"
    echo "  - validate_codex_reorganization"
    echo "  - verify_git_history_preserved <file> <original_name>"
    echo "  - verify_executable_permissions <directory>"
    echo ""
    echo "Example usage:"
    echo "  source bash_validation_pattern.sh"
    echo "  validate_codex_reorganization"
fi
