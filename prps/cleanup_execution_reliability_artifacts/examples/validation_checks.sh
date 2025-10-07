#!/bin/bash
# Source: Feature analysis + prp_execution_reliability validation patterns
# Pattern: Validation scripts for verifying file operations and documentation updates
# Extracted: 2025-10-07
# Relevance: 10/10 - Essential validation patterns for cleanup verification

set -e  # Exit on error

# =============================================================================
# PATTERN 1: File Existence Validation
# =============================================================================
# Use Case: Verify files/directories exist after move operations

validate_file_exists() {
    local file_path="$1"
    local description="${2:-File}"

    if [ -e "${file_path}" ]; then
        echo "  ✅ ${description} exists: ${file_path}"
        return 0
    else
        echo "  ❌ ${description} missing: ${file_path}"
        return 1
    fi
}

validate_file_not_exists() {
    local file_path="$1"
    local description="${2:-File}"

    if [ ! -e "${file_path}" ]; then
        echo "  ✅ ${description} removed: ${file_path}"
        return 0
    else
        echo "  ❌ ${description} still exists: ${file_path}"
        return 1
    fi
}

# =============================================================================
# PATTERN 2: Directory Structure Validation
# =============================================================================
# Use Case: Verify expected directory structure after consolidation

validate_directory_structure() {
    local feature_name="$1"
    local expected_dirs=("examples" "planning" "execution")

    echo "Validating directory structure for: ${feature_name}"
    echo "Expected structure: prps/${feature_name}/{examples,planning,execution}"

    local all_valid=true

    # Check each expected directory
    for dir in "${expected_dirs[@]}"; do
        if ! validate_file_exists "prps/${feature_name}/${dir}" "Directory"; then
            all_valid=false
        fi
    done

    # Check old directory doesn't exist
    if [ -d "prps/prp_${feature_name}" ]; then
        echo "  ❌ Old directory still exists: prps/prp_${feature_name}"
        all_valid=false
    else
        echo "  ✅ Old directory removed: prps/prp_${feature_name}"
    fi

    if [ "${all_valid}" = true ]; then
        echo "✅ Directory structure validation PASSED"
        return 0
    else
        echo "❌ Directory structure validation FAILED"
        return 1
    fi
}

# =============================================================================
# PATTERN 3: Text Reference Validation (Grep-based)
# =============================================================================
# Use Case: Verify old references have been replaced in documentation

validate_no_old_references() {
    local directory="$1"
    local old_text="$2"
    local file_pattern="${3:-.md}"  # Default to .md files

    echo "Validating no old references: '${old_text}' in ${directory}"

    # Search for old text (case-sensitive)
    # -r = recursive
    # -n = show line numbers
    # --include = file pattern
    local matches=$(grep -rn --include="*${file_pattern}" "${old_text}" "${directory}" 2>/dev/null || true)

    if [ -z "${matches}" ]; then
        echo "  ✅ No instances of '${old_text}' found"
        return 0
    else
        echo "  ❌ Found instances of '${old_text}':"
        echo "${matches}" | head -10  # Show first 10 matches
        local count=$(echo "${matches}" | wc -l | tr -d ' ')
        echo "  Total occurrences: ${count}"
        return 1
    fi
}

# =============================================================================
# PATTERN 4: File Path Validation in Documentation
# =============================================================================
# Use Case: Verify all file paths in documentation are valid

validate_markdown_file_paths() {
    local file_path="$1"

    echo "Validating file paths in: ${file_path}"

    # Extract potential file paths from markdown
    # Pattern: Look for paths starting with prps/, .claude/, etc.
    local paths=$(grep -oE '(prps|\.claude)/[a-zA-Z0-9_/-]+\.(md|py|sh|yml)' "${file_path}" 2>/dev/null || true)

    if [ -z "${paths}" ]; then
        echo "  ℹ️  No file paths found to validate"
        return 0
    fi

    local all_valid=true
    local checked=0
    local valid=0
    local invalid=0

    # Check each path
    while IFS= read -r path; do
        if [ -z "${path}" ]; then
            continue
        fi

        checked=$((checked + 1))

        if [ -e "${path}" ]; then
            valid=$((valid + 1))
        else
            echo "  ❌ Invalid path referenced: ${path}"
            invalid=$((invalid + 1))
            all_valid=false
        fi
    done <<< "${paths}"

    echo "  Checked: ${checked} paths"
    echo "  ✅ Valid: ${valid}"
    if [ ${invalid} -gt 0 ]; then
        echo "  ❌ Invalid: ${invalid}"
    fi

    if [ "${all_valid}" = true ]; then
        echo "✅ All file paths are valid"
        return 0
    else
        echo "❌ Some file paths are invalid"
        return 1
    fi
}

# =============================================================================
# PATTERN 5: Git Status Validation
# =============================================================================
# Use Case: Verify git operations completed successfully

validate_git_status() {
    echo "Validating git status"

    # Check if there are staged changes
    if git diff --cached --quiet; then
        echo "  ℹ️  No staged changes"
    else
        echo "  ⚠️  Staged changes detected:"
        git diff --cached --name-status | head -10
    fi

    # Check if there are unstaged changes
    if git diff --quiet; then
        echo "  ℹ️  No unstaged changes"
    else
        echo "  ⚠️  Unstaged changes detected:"
        git diff --name-status | head -10
    fi

    # Check if there are untracked files
    local untracked=$(git ls-files --others --exclude-standard)
    if [ -z "${untracked}" ]; then
        echo "  ℹ️  No untracked files"
    else
        echo "  ⚠️  Untracked files detected:"
        echo "${untracked}" | head -10
    fi

    echo "✅ Git status check complete"
}

# =============================================================================
# PATTERN 6: File Count Validation
# =============================================================================
# Use Case: Verify expected number of files after operations

count_files_in_directory() {
    local dir_path="$1"
    local pattern="${2:-*}"

    if [ ! -d "${dir_path}" ]; then
        echo "0"
        return
    fi

    find "${dir_path}" -type f -name "${pattern}" | wc -l | tr -d ' '
}

validate_file_count() {
    local dir_path="$1"
    local expected_count="$2"
    local pattern="${3:-*}"
    local description="${4:-files}"

    local actual_count=$(count_files_in_directory "${dir_path}" "${pattern}")

    if [ "${actual_count}" -eq "${expected_count}" ]; then
        echo "  ✅ ${description} count correct: ${actual_count}/${expected_count}"
        return 0
    else
        echo "  ❌ ${description} count mismatch: ${actual_count} found, ${expected_count} expected"
        return 1
    fi
}

# =============================================================================
# PATTERN 7: Comprehensive Validation Suite
# =============================================================================
# Use Case: Run all validations for a cleanup operation

run_comprehensive_validation() {
    local feature_name="$1"

    echo "========================================="
    echo "COMPREHENSIVE VALIDATION"
    echo "Feature: ${feature_name}"
    echo "========================================="

    local total_checks=0
    local passed_checks=0

    # Check 1: Directory structure
    echo ""
    echo "CHECK 1/6: Directory Structure"
    echo "---------------------------------"
    total_checks=$((total_checks + 1))
    if validate_directory_structure "${feature_name}"; then
        passed_checks=$((passed_checks + 1))
    fi

    # Check 2: Old references removed
    echo ""
    echo "CHECK 2/6: Old References Removed"
    echo "---------------------------------"
    total_checks=$((total_checks + 1))
    if validate_no_old_references "prps/${feature_name}" "prp_${feature_name}"; then
        passed_checks=$((passed_checks + 1))
    fi

    # Check 3: PRP file exists with correct name
    echo ""
    echo "CHECK 3/6: PRP File"
    echo "---------------------------------"
    total_checks=$((total_checks + 1))
    if validate_file_exists "prps/${feature_name}.md" "PRP file"; then
        passed_checks=$((passed_checks + 1))
    fi

    # Check 4: Old PRP file removed
    echo ""
    echo "CHECK 4/6: Old PRP File Removed"
    echo "---------------------------------"
    total_checks=$((total_checks + 1))
    if validate_file_not_exists "prps/prp_${feature_name}.md" "Old PRP file"; then
        passed_checks=$((passed_checks + 1))
    fi

    # Check 5: File paths in PRP are valid
    echo ""
    echo "CHECK 5/6: File Paths in PRP"
    echo "---------------------------------"
    total_checks=$((total_checks + 1))
    if validate_markdown_file_paths "prps/${feature_name}.md"; then
        passed_checks=$((passed_checks + 1))
    fi

    # Check 6: Git status
    echo ""
    echo "CHECK 6/6: Git Status"
    echo "---------------------------------"
    total_checks=$((total_checks + 1))
    validate_git_status  # Always passes, just informational
    passed_checks=$((passed_checks + 1))

    # Summary
    echo ""
    echo "========================================="
    echo "VALIDATION SUMMARY"
    echo "========================================="
    echo "Checks passed: ${passed_checks}/${total_checks}"

    local percentage=$(( (passed_checks * 100) / total_checks ))
    echo "Success rate: ${percentage}%"

    if [ ${passed_checks} -eq ${total_checks} ]; then
        echo ""
        echo "✅ ALL VALIDATIONS PASSED"
        echo "Cleanup operation completed successfully!"
        return 0
    else
        echo ""
        echo "❌ SOME VALIDATIONS FAILED"
        echo "Please review failures above and fix issues."
        return 1
    fi
}

# =============================================================================
# PATTERN 8: File Content Spot Check
# =============================================================================
# Use Case: Manually verify file content for correctness

spot_check_file_content() {
    local file_path="$1"
    local search_term="${2:-}"

    echo "Spot checking: ${file_path}"

    if [ ! -f "${file_path}" ]; then
        echo "  ❌ File does not exist"
        return 1
    fi

    # Show file size
    local size=$(wc -c < "${file_path}" | tr -d ' ')
    echo "  File size: ${size} bytes"

    # Show line count
    local lines=$(wc -l < "${file_path}" | tr -d ' ')
    echo "  Line count: ${lines}"

    # Show first 10 lines
    echo "  First 10 lines:"
    head -10 "${file_path}" | sed 's/^/    /'

    # If search term provided, check for it
    if [ -n "${search_term}" ]; then
        echo "  Searching for: '${search_term}'"
        local matches=$(grep -n "${search_term}" "${file_path}" 2>/dev/null || true)
        if [ -n "${matches}" ]; then
            echo "  ✅ Found ${search_term}:"
            echo "${matches}" | head -5 | sed 's/^/    /'
        else
            echo "  ℹ️  Not found: ${search_term}"
        fi
    fi

    echo "  ✅ Spot check complete"
}

# =============================================================================
# USAGE EXAMPLE: Validate execution_reliability cleanup
# =============================================================================

validate_execution_reliability_cleanup() {
    echo "========================================="
    echo "EXAMPLE: Validate execution_reliability Cleanup"
    echo "========================================="

    run_comprehensive_validation "execution_reliability"

    # Additional specific checks
    echo ""
    echo "Additional Validation Checks"
    echo "========================================="

    # Check TASK8_TEST_RESULTS.md moved correctly
    echo ""
    echo "Checking TASK8_TEST_RESULTS.md location"
    validate_file_exists "prps/execution_reliability/execution/TASK8_TEST_RESULTS.md" \
        "TASK8_TEST_RESULTS.md"

    # Check all 8 completion reports exist
    echo ""
    echo "Checking completion reports count"
    validate_file_count "prps/execution_reliability/execution" 8 "TASK*_COMPLETION.md" \
        "completion reports"

    # Spot check a few files
    echo ""
    echo "Spot checking PRP file content"
    spot_check_file_content "prps/execution_reliability.md" "execution_reliability"

    echo ""
    echo "========================================="
    echo "✅ Validation complete!"
    echo "========================================="
}

# =============================================================================
# Main execution
# =============================================================================

if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    echo "Validation checks script loaded"
    echo ""
    echo "Available functions:"
    echo "  - validate_file_exists <path> [description]"
    echo "  - validate_file_not_exists <path> [description]"
    echo "  - validate_directory_structure <feature_name>"
    echo "  - validate_no_old_references <directory> <old_text> [file_pattern]"
    echo "  - validate_markdown_file_paths <file_path>"
    echo "  - validate_git_status"
    echo "  - validate_file_count <dir> <expected> [pattern] [description]"
    echo "  - run_comprehensive_validation <feature_name>"
    echo "  - spot_check_file_content <file_path> [search_term]"
    echo "  - validate_execution_reliability_cleanup"
    echo ""
    echo "Example usage:"
    echo "  source validation_checks.sh"
    echo "  validate_execution_reliability_cleanup"
fi
