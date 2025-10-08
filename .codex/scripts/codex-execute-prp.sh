#!/bin/bash
# .codex/scripts/codex-execute-prp.sh
# Purpose: Orchestrate PRP execution with validation loop (ruff → mypy → pytest)
# Pattern: .claude/patterns/quality-gates.md (validation loop pattern)
# Source: Task 5 from prps/codex_commands.md (lines 648-684)

set -euo pipefail

# =============================================================================
# Configuration
# =============================================================================

# Maximum validation attempts before requiring manual intervention
MAX_VALIDATION_ATTEMPTS=5

# Minimum test coverage percentage
MIN_COVERAGE=70

# Validation level timeouts (seconds)
TIMEOUT_SYNTAX=300     # 5 minutes for linting/type checking
TIMEOUT_TESTS=600      # 10 minutes for unit tests
TIMEOUT_COVERAGE=900   # 15 minutes for coverage tests

# Get script directory for sourcing dependencies
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# =============================================================================
# Import Dependencies
# =============================================================================

# Source security validation (6-level feature name validation)
if [ -f "${SCRIPT_DIR}/security-validation.sh" ]; then
    source "${SCRIPT_DIR}/security-validation.sh"
else
    echo "❌ ERROR: security-validation.sh not found" >&2
    echo "   Expected: ${SCRIPT_DIR}/security-validation.sh" >&2
    exit 1
fi

# Source manifest logger (JSONL logging)
if [ -f "${SCRIPT_DIR}/log-phase.sh" ]; then
    source "${SCRIPT_DIR}/log-phase.sh"
else
    echo "❌ ERROR: log-phase.sh not found" >&2
    echo "   Expected: ${SCRIPT_DIR}/log-phase.sh" >&2
    exit 1
fi

# =============================================================================
# Helper Functions
# =============================================================================

# Show usage information
show_usage() {
    cat <<'EOF'
Usage: ./.codex/scripts/codex-execute-prp.sh <prp_file>

Orchestrate PRP execution with validation loop (ruff → mypy → pytest).

Arguments:
  prp_file    Path to PRP file (e.g., prps/user_auth.md or prps/INITIAL_feature.md)

Environment Variables:
  MAX_VALIDATION_ATTEMPTS    Maximum validation attempts (default: 5)
  MIN_COVERAGE              Minimum test coverage % (default: 70)
  SKIP_VALIDATION           Skip validation loop (testing only, default: false)

Validation Levels:
  Level 1: Syntax & Style (ruff check --fix, mypy)
  Level 2: Unit Tests (pytest tests/)
  Level 3: Coverage (pytest --cov, verify ≥70%)

On Validation Failure:
  - Extract error messages from logs
  - Check PRP "Known Gotchas" section for solutions
  - Apply fix based on gotcha pattern
  - Retry validation (increment attempt counter)

After Max Attempts:
  - Generate completion report (files changed, quality score, coverage %, blockers)
  - Offer user choices (continue/manual intervention/abort)

Examples:
  # Execute PRP with validation
  ./.codex/scripts/codex-execute-prp.sh prps/user_auth.md

  # Execute INITIAL PRP (auto-strips INITIAL_ prefix)
  ./.codex/scripts/codex-execute-prp.sh prps/INITIAL_user_auth.md

  # Custom max attempts
  MAX_VALIDATION_ATTEMPTS=3 ./.codex/scripts/codex-execute-prp.sh prps/user_auth.md

Manifest Location:
  prps/<feature>/codex/logs/manifest.jsonl

Completion Report:
  prps/<feature>/codex/logs/execution_report.md

EOF
}

# Extract feature name from PRP file path
extract_feature_from_prp() {
    local prp_path="$1"

    # Check if file exists
    if [ ! -f "$prp_path" ]; then
        echo "❌ ERROR: PRP file not found: $prp_path" >&2
        return 1
    fi

    # Extract feature name with security validation
    # Handles both INITIAL_feature.md and feature.md
    local feature
    feature=$(extract_feature_name "$prp_path" "INITIAL_" "true") || return 1

    echo "$feature"
}

# Check if PRP has "Known Gotchas" section
extract_gotchas_from_prp() {
    local prp_path="$1"

    if [ ! -f "$prp_path" ]; then
        echo ""
        return 1
    fi

    # Extract "Known Gotchas" section (between ## Known Gotchas and next ##)
    local gotchas
    gotchas=$(sed -n '/^## Known Gotchas/,/^## /p' "$prp_path" | head -n -1)

    echo "$gotchas"
}

# Analyze error message against PRP gotchas
analyze_validation_error() {
    local error_log="$1"
    local prp_gotchas="$2"
    local validation_level="$3"

    echo ""
    echo "========================================="
    echo "Error Analysis (Validation Level ${validation_level})"
    echo "========================================="

    # Extract error type patterns
    local error_type="unknown"

    if grep -qi "ImportError\|ModuleNotFoundError" "$error_log"; then
        error_type="import_error"
    elif grep -qi "TypeError\|AttributeError" "$error_log"; then
        error_type="type_error"
    elif grep -qi "AssertionError" "$error_log"; then
        error_type="assertion_error"
    elif grep -qi "SyntaxError\|IndentationError" "$error_log"; then
        error_type="syntax_error"
    elif grep -qi "TimeoutError\|timeout" "$error_log"; then
        error_type="timeout"
    elif grep -qi "ruff" "$error_log"; then
        error_type="linting_error"
    elif grep -qi "mypy" "$error_log"; then
        error_type="type_checking_error"
    fi

    echo "Error Type: ${error_type}"
    echo ""

    # Show relevant error lines (first 20 lines)
    echo "Error Details (first 20 lines):"
    echo "-----------------------------------------"
    head -20 "$error_log"
    echo ""

    # Search for relevant gotcha
    if [ -n "$prp_gotchas" ] && [ "$prp_gotchas" != "" ]; then
        echo "Searching PRP gotchas for: ${error_type}..."
        # Simple grep for error type in gotchas section
        local relevant_gotcha
        relevant_gotcha=$(echo "$prp_gotchas" | grep -i "$error_type" -A 5 || echo "")

        if [ -n "$relevant_gotcha" ]; then
            echo ""
            echo "Relevant Gotcha Found:"
            echo "-----------------------------------------"
            echo "$relevant_gotcha"
            echo ""
        else
            echo "No specific gotcha found for this error type"
        fi
    else
        echo "No gotchas section found in PRP"
    fi

    echo "========================================="
    echo ""
}

# Generate completion report
generate_completion_report() {
    local feature="$1"
    local status="$2"  # "success" or "failed"
    local validation_attempts="$3"
    local final_exit_code="$4"

    local report_path="prps/${feature}/codex/logs/execution_report.md"
    # Ensure directory exists
    local report_dir
    report_dir=$(dirname "$report_path")
    mkdir -p "$report_dir"

    # Gather metrics
    local coverage_pct="N/A"
    local quality_score="N/A"
    local files_changed=()

    # Try to extract coverage from pytest output
    if [ -f "prps/${feature}/codex/logs/validation_level3.log" ]; then
        coverage_pct=$(grep -oP 'TOTAL.*\K\d+%' "prps/${feature}/codex/logs/validation_level3.log" | tail -1 || echo "N/A")
    fi

    # Find modified files (last 24 hours)
    if [ -d "prps/${feature}" ]; then
        mapfile -t files_changed < <(find "prps/${feature}" -type f -mtime -1 2>/dev/null || echo "")
    fi

    # Count modified files
    local files_count=${#files_changed[@]}

    # Generate report
    cat > "$report_path" <<EOF
# PRP Execution Completion Report

**Generated**: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
**Feature**: ${feature}
**Status**: ${status}

---

## Summary

- **Final Status**: ${status}
- **Validation Attempts**: ${validation_attempts}/${MAX_VALIDATION_ATTEMPTS}
- **Final Exit Code**: ${final_exit_code}
- **Test Coverage**: ${coverage_pct}
- **Quality Score**: ${quality_score}
- **Files Changed**: ${files_count}

---

## Validation Results

EOF

    # Add validation logs summary
    for level in 1 2 3; do
        local log_file="prps/${feature}/codex/logs/validation_level${level}.log"
        if [ -f "$log_file" ]; then
            local level_status="❌ FAILED"
            if grep -q "SUCCESS" "$log_file" 2>/dev/null; then
                level_status="✅ PASSED"
            fi

            cat >> "$report_path" <<EOF
### Level ${level}: $(get_validation_level_name "$level")
- **Status**: ${level_status}
- **Log**: ${log_file}

EOF
        fi
    done

    # Add blockers if failed
    if [ "$status" = "failed" ]; then
        cat >> "$report_path" <<EOF

---

## Blockers

The following issues prevented successful execution:

EOF
        # Extract last error from validation logs
        for level in 1 2 3; do
            local log_file="prps/${feature}/codex/logs/validation_level${level}.log"
            if [ -f "$log_file" ] && ! grep -q "SUCCESS" "$log_file" 2>/dev/null; then
                cat >> "$report_path" <<EOF
### Validation Level ${level} Failure
\`\`\`
$(tail -30 "$log_file")
\`\`\`

EOF
            fi
        done
    fi

    # Add files changed
    if [ "${files_count}" -gt 0 ]; then
        cat >> "$report_path" <<EOF

---

## Files Changed

EOF
        for file in "${files_changed[@]}"; do
            echo "- \`${file}\`" >> "$report_path"
        done
    fi

    # Add recommendations
    cat >> "$report_path" <<EOF

---

## Recommendations

EOF

    if [ "$status" = "success" ]; then
        cat >> "$report_path" <<EOF
✅ All validations passed! The implementation is ready.

Next Steps:
1. Review generated code
2. Run integration tests
3. Commit changes: \`git add . && git commit -m "Implement ${feature}"\`
EOF
    else
        cat >> "$report_path" <<EOF
❌ Validation failed after ${validation_attempts} attempts.

Options:
1. **Manual intervention**: Review error logs and fix issues manually
2. **Adjust validation thresholds**: Lower MIN_COVERAGE if too strict
3. **Review PRP gotchas**: Check if known issues apply
4. **Regenerate PRP**: If requirements changed, regenerate with updated INITIAL.md

Error logs location: prps/${feature}/codex/logs/validation_level*.log
EOF
    fi

    echo ""
    echo "📊 Completion report generated: ${report_path}"
}

# Get validation level name
get_validation_level_name() {
    local level="$1"
    case "$level" in
        1) echo "Syntax & Style (ruff, mypy)" ;;
        2) echo "Unit Tests (pytest)" ;;
        3) echo "Coverage (pytest --cov)" ;;
        *) echo "Unknown" ;;
    esac
}

# =============================================================================
# Validation Level Functions
# =============================================================================

# Level 1: Syntax & Style (ruff, mypy)
validate_level1_syntax() {
    local feature="$1"
    local log_file="prps/${feature}/codex/logs/validation_level1.log"
    local log_dir
    log_dir=$(dirname "$log_file")

    mkdir -p "$log_dir"

    echo ""
    echo "========================================="
    echo "Validation Level 1: Syntax & Style"
    echo "========================================="
    echo "Running: ruff check --fix && mypy"
    echo "Timeout: ${TIMEOUT_SYNTAX}s"
    echo ""

    # Run ruff (Python linter with auto-fix)
    echo "🔍 Running ruff check --fix..." | tee "$log_file"
    if timeout "${TIMEOUT_SYNTAX}s" ruff check --fix . >> "$log_file" 2>&1; then
        echo "✅ ruff passed" | tee -a "$log_file"
    else
        local exit_code=$?
        echo "❌ ruff failed (exit: ${exit_code})" | tee -a "$log_file"
        return 1
    fi

    # Run mypy (Python type checker)
    echo "" >> "$log_file"
    echo "🔍 Running mypy..." | tee -a "$log_file"
    if timeout "${TIMEOUT_SYNTAX}s" mypy . --config-file pyproject.toml >> "$log_file" 2>&1; then
        echo "✅ mypy passed" | tee -a "$log_file"
    else
        local exit_code=$?
        echo "❌ mypy failed (exit: ${exit_code})" | tee -a "$log_file"
        return 1
    fi

    echo "" >> "$log_file"
    echo "SUCCESS: Level 1 validation passed" >> "$log_file"
    echo "✅ Level 1 PASSED"
    return 0
}

# Level 2: Unit Tests (pytest)
validate_level2_tests() {
    local feature="$1"
    local log_file="prps/${feature}/codex/logs/validation_level2.log"
    local log_dir
    log_dir=$(dirname "$log_file")

    mkdir -p "$log_dir"

    echo ""
    echo "========================================="
    echo "Validation Level 2: Unit Tests"
    echo "========================================="
    echo "Running: pytest tests/"
    echo "Timeout: ${TIMEOUT_TESTS}s"
    echo ""

    echo "🧪 Running pytest..." | tee "$log_file"
    if timeout "${TIMEOUT_TESTS}s" pytest tests/ -v >> "$log_file" 2>&1; then
        echo "✅ pytest passed" | tee -a "$log_file"
        echo "" >> "$log_file"
        echo "SUCCESS: Level 2 validation passed" >> "$log_file"
        echo "✅ Level 2 PASSED"
        return 0
    else
        local exit_code=$?
        echo "❌ pytest failed (exit: ${exit_code})" | tee -a "$log_file"
        return 1
    fi
}

# Level 3: Coverage (pytest --cov)
validate_level3_coverage() {
    local feature="$1"
    local log_file="prps/${feature}/codex/logs/validation_level3.log"
    local log_dir
    log_dir=$(dirname "$log_file")

    mkdir -p "$log_dir"

    echo ""
    echo "========================================="
    echo "Validation Level 3: Test Coverage"
    echo "========================================="
    echo "Running: pytest --cov"
    echo "Minimum Coverage: ${MIN_COVERAGE}%"
    echo "Timeout: ${TIMEOUT_COVERAGE}s"
    echo ""

    echo "📊 Running pytest with coverage..." | tee "$log_file"
    if timeout "${TIMEOUT_COVERAGE}s" pytest tests/ --cov=. --cov-report=term-missing >> "$log_file" 2>&1; then
        echo "✅ pytest --cov passed" | tee -a "$log_file"

        # Extract coverage percentage
        local coverage_pct
        coverage_pct=$(grep -oP 'TOTAL.*\K\d+' "$log_file" | tail -1 || echo "0")

        echo "" | tee -a "$log_file"
        echo "Coverage: ${coverage_pct}%" | tee -a "$log_file"

        # Check against minimum
        if [ "$coverage_pct" -ge "$MIN_COVERAGE" ]; then
            echo "✅ Coverage ${coverage_pct}% >= ${MIN_COVERAGE}% (minimum)" | tee -a "$log_file"
            echo "" >> "$log_file"
            echo "SUCCESS: Level 3 validation passed" >> "$log_file"
            echo "✅ Level 3 PASSED"
            return 0
        else
            echo "❌ Coverage ${coverage_pct}% < ${MIN_COVERAGE}% (minimum)" | tee -a "$log_file"
            return 1
        fi
    else
        local exit_code=$?
        echo "❌ pytest --cov failed (exit: ${exit_code})" | tee -a "$log_file"
        return 1
    fi
}

# =============================================================================
# Validation Loop
# =============================================================================

# Run validation loop with max attempts
run_validation_loop() {
    local feature="$1"
    local prp_path="$2"

    # Extract gotchas from PRP
    local prp_gotchas
    prp_gotchas=$(extract_gotchas_from_prp "$prp_path")

    echo ""
    echo "========================================="
    echo "PRP Execution Validation Loop"
    echo "========================================="
    echo "Feature: ${feature}"
    echo "PRP: ${prp_path}"
    echo "Max Attempts: ${MAX_VALIDATION_ATTEMPTS}"
    echo "Min Coverage: ${MIN_COVERAGE}%"
    echo ""

    # Validation loop
    local attempt=1
    local validation_success=false

    while [ $attempt -le $MAX_VALIDATION_ATTEMPTS ]; do
        echo ""
        echo "========================================="
        echo "Validation Attempt ${attempt}/${MAX_VALIDATION_ATTEMPTS}"
        echo "========================================="

        # Log attempt start
        log_phase_start "$feature" "validation_attempt_${attempt}"

        local attempt_start
        attempt_start=$(date +%s)
        local all_levels_passed=true

        # Level 1: Syntax & Style
        if validate_level1_syntax "$feature"; then
            log_phase_complete "$feature" "validation_level1_attempt${attempt}" 0 0
        else
            log_phase_complete "$feature" "validation_level1_attempt${attempt}" 1 0
            all_levels_passed=false

            # Analyze error
            analyze_validation_error \
                "prps/${feature}/codex/logs/validation_level1.log" \
                "$prp_gotchas" \
                1

            # Don't proceed to level 2 if level 1 fails
            if [ $attempt -lt $MAX_VALIDATION_ATTEMPTS ]; then
                echo "⚠️  Level 1 failed - fix syntax/style errors before retrying"
                echo ""
                read -p "Press Enter to retry after manual fixes (or Ctrl+C to abort)..." -r
                ((attempt++))
                continue
            else
                break
            fi
        fi

        # Level 2: Unit Tests
        if validate_level2_tests "$feature"; then
            log_phase_complete "$feature" "validation_level2_attempt${attempt}" 0 0
        else
            log_phase_complete "$feature" "validation_level2_attempt${attempt}" 1 0
            all_levels_passed=false

            # Analyze error
            analyze_validation_error \
                "prps/${feature}/codex/logs/validation_level2.log" \
                "$prp_gotchas" \
                2

            # Don't proceed to level 3 if level 2 fails
            if [ $attempt -lt $MAX_VALIDATION_ATTEMPTS ]; then
                echo "⚠️  Level 2 failed - fix failing tests before retrying"
                echo ""
                read -p "Press Enter to retry after manual fixes (or Ctrl+C to abort)..." -r
                ((attempt++))
                continue
            else
                break
            fi
        fi

        # Level 3: Coverage
        if validate_level3_coverage "$feature"; then
            log_phase_complete "$feature" "validation_level3_attempt${attempt}" 0 0
        else
            log_phase_complete "$feature" "validation_level3_attempt${attempt}" 1 0
            all_levels_passed=false

            # Analyze error
            analyze_validation_error \
                "prps/${feature}/codex/logs/validation_level3.log" \
                "$prp_gotchas" \
                3

            if [ $attempt -lt $MAX_VALIDATION_ATTEMPTS ]; then
                echo "⚠️  Level 3 failed - increase test coverage"
                echo ""
                read -p "Press Enter to retry after adding tests (or Ctrl+C to abort)..." -r
                ((attempt++))
                continue
            else
                break
            fi
        fi

        # All levels passed!
        if [ "$all_levels_passed" = true ]; then
            validation_success=true
            local attempt_end
            attempt_end=$(date +%s)
            local attempt_duration=$((attempt_end - attempt_start))

            log_phase_complete "$feature" "validation_attempt_${attempt}" 0 "$attempt_duration"

            echo ""
            echo "========================================="
            echo "✅ All Validation Levels PASSED"
            echo "========================================="
            echo "Attempt: ${attempt}/${MAX_VALIDATION_ATTEMPTS}"
            echo "Duration: ${attempt_duration}s"
            break
        fi

        ((attempt++))
    done

    # Check if max attempts reached
    if [ "$validation_success" = false ]; then
        echo ""
        echo "========================================="
        echo "❌ Validation Failed"
        echo "========================================="
        echo "Max attempts reached: ${MAX_VALIDATION_ATTEMPTS}"
        echo ""

        # Offer user choices
        echo "Options:"
        echo "  1. Continue anyway (accept partial implementation)"
        echo "  2. Manual intervention (pause for user fixes)"
        echo "  3. Abort workflow"
        echo ""

        read -r -p "Choose (1/2/3): " choice

        case "$choice" in
            1)
                echo ""
                echo "⚠️  Continuing with partial implementation"
                return 2  # Partial success exit code
                ;;
            2)
                echo ""
                echo "⏸️  Pausing for manual intervention"
                echo "Fix issues and re-run: ./.codex/scripts/codex-execute-prp.sh $prp_path"
                return 3  # Manual intervention exit code
                ;;
            3)
                echo ""
                echo "Aborting workflow"
                return 1  # Failure exit code
                ;;
            *)
                echo "Invalid choice. Aborting."
                return 1
                ;;
        esac
    fi

    return 0
}

# =============================================================================
# Main Execution
# =============================================================================

main() {
    # Check for help flag
    if [ $# -eq 0 ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
        show_usage
        exit 0
    fi

    # Parse arguments
    local prp_path="$1"

    # Extract feature name with security validation
    local feature
    feature=$(extract_feature_from_prp "$prp_path") || {
        echo "❌ Failed to extract valid feature name from: $prp_path"
        exit 1
    }

    echo ""
    echo "=========================================="
    echo "Codex PRP Execution Workflow"
    echo "=========================================="
    echo "PRP: ${prp_path}"
    echo "Feature: ${feature}"
    echo "Output: prps/${feature}/codex/logs/"
    echo ""

    # Setup directories
    mkdir -p "prps/${feature}/codex/logs"

    # Log execution start
    log_phase_start "$feature" "execution_start"

    # Run validation loop (unless skipped)
    local validation_exit=0
    if [ "${SKIP_VALIDATION:-false}" = "true" ]; then
        echo "⚠️  Validation skipped (SKIP_VALIDATION=true)"
        validation_exit=0
    else
        run_validation_loop "$feature" "$prp_path"
        validation_exit=$?
    fi

    # Log execution complete
    log_phase_complete "$feature" "execution_complete" "$validation_exit" 0

    # Generate completion report
    local final_status="failed"
    if [ $validation_exit -eq 0 ]; then
        final_status="success"
    elif [ $validation_exit -eq 2 ]; then
        final_status="partial"
    fi

    generate_completion_report "$feature" "$final_status" "$MAX_VALIDATION_ATTEMPTS" "$validation_exit"

    # Show summary
    echo ""
    echo "=========================================="
    echo "Execution Complete"
    echo "=========================================="
    echo "Status: ${final_status}"
    echo "Report: prps/${feature}/codex/logs/execution_report.md"
    echo "Manifest: prps/${feature}/codex/logs/manifest.jsonl"
    echo ""

    # Exit with validation result
    if [ $validation_exit -eq 0 ] || [ $validation_exit -eq 2 ]; then
        exit 0
    else
        exit 1
    fi
}

# Run main if called directly (not sourced)
if [ "${BASH_SOURCE[0]:-}" = "${0}" ]; then
    main "$@"
fi
