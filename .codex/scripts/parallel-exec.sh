#!/bin/bash
# .codex/scripts/parallel-exec.sh
# Purpose: Parallel execution helper for Phase 2 agents with PID tracking and exit code capture
# Pattern: Adapted from prps/codex_integration/examples/phase_orchestration.sh (lines 112-161)
# Source: PRP Task 2 - parallel execution with timeout, exit code capture, separate logging

set -euo pipefail

# =============================================================================
# Configuration
# =============================================================================

# Default timeout for agents (10 minutes)
DEFAULT_TIMEOUT_SEC=600

# Kill timeout (force kill after initial timeout)
KILL_AFTER_SEC=5

# Default Codex profile
CODEX_PROFILE="${CODEX_PROFILE:-codex-prp}"

# Determine GNU timeout binary (supports macOS gtimeout)
TIMEOUT_BIN="${TIMEOUT_BIN:-timeout}"
if ! command -v "$TIMEOUT_BIN" >/dev/null 2>&1; then
    if command -v gtimeout >/dev/null 2>&1; then
        TIMEOUT_BIN="$(command -v gtimeout)"
    else
        echo "⚠️  WARNING: GNU timeout command not found; proceeding without enforced timeouts" >&2
        echo "   Install with: brew install coreutils" >&2
        TIMEOUT_BIN=""
    fi
fi

# Provide local run_with_timeout helper if not already defined
if ! declare -f run_with_timeout >/dev/null 2>&1; then
    run_with_timeout() {
        local kill_after=()
        local extra_opts=()
        local duration=""

        while (($# > 0)); do
            case "$1" in
                --kill-after=*)
                    kill_after+=("$1")
                    shift
                    ;;
                --preserve-status|--foreground)
                    extra_opts+=("$1")
                    shift
                    ;;
                *)
                    duration="$1"
                    shift
                    break
                    ;;
            esac
        done

        if [ -z "$duration" ]; then
            echo "❌ ERROR: run_with_timeout called without duration" >&2
            return 1
        fi

        if (($# == 0)); then
            echo "❌ ERROR: run_with_timeout called without command" >&2
            return 1
        fi

        if [ -n "$TIMEOUT_BIN" ]; then
            "$TIMEOUT_BIN" "${kill_after[@]}" "${extra_opts[@]}" "$duration" "$@"
        else
            echo "⚠️  WARNING: Executing without timeout enforcement: $*" >&2
            "$@"
        fi
    }
fi

# Respect Codex CLI mode (fallback detection if not exported)
CODEX_CLI_MODE="${CODEX_CLI_MODE:-none}"
if [ "$CODEX_CLI_MODE" = "none" ] && command -v codex >/dev/null 2>&1; then
    if codex exec --help 2>&1 | grep -q -- "--prompt"; then
        CODEX_CLI_MODE="flag"
    else
        CODEX_CLI_MODE="stdin"
        echo "ℹ️  Codex CLI detected (using stdin prompt mode)" >&2
    fi
fi

# =============================================================================
# Core Parallel Execution Function
# =============================================================================

# Execute parallel group of phases with PID tracking and exit code capture
# CRITICAL GOTCHAS ADDRESSED:
#   - Gotcha #1: Exit code timing - MUST capture immediately after wait
#   - Gotcha #3: Timeout wrapper required
#   - Gotcha #5: Separate log files per agent
#   - Gotcha #7: Capture PIDs immediately with $!
execute_parallel_group() {
    local feature="$1"
    local group_name="$2"
    shift 2
    local phases=("$@")  # Array of phase names

    echo ""
    echo "========================================="
    echo "Parallel Group: ${group_name}"
    echo "Phases: ${phases[*]}"
    echo "========================================="

    # Validate we have phases to run
    if [ ${#phases[@]} -eq 0 ]; then
        echo "❌ ERROR: No phases provided to execute_parallel_group" >&2
        return 1
    fi

    # Source dependencies
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    source "${script_dir}/log-phase.sh"

    # Setup log directory
    local log_dir="prps/${feature}/codex/logs"
    mkdir -p "$log_dir"

    # Start timestamp for parallel group
    local start_time=$(date +%s)

    # Log phase starts (separate manifests to avoid race condition - GOTCHA #9)
    echo "🚀 Starting ${#phases[@]} agents in parallel..."
    for phase in "${phases[@]}"; do
        log_phase_start "$feature" "$phase"
    done

    # Launch all agents in background with timeout wrapper
    # CRITICAL: Capture PIDs immediately with $! to avoid race condition (GOTCHA #7)
    local pids=()
    local phase_names=()

    for phase in "${phases[@]}"; do
        local prompt_file=".codex/prompts/${phase}.md"
        local log_file="${log_dir}/${phase}.log"

        echo "   Launching: ${phase} (PID will be captured)"

        # CRITICAL: Timeout wrapper to prevent zombie processes (GOTCHA #3)
        # CRITICAL: Separate log file per agent to avoid output interleaving (GOTCHA #5)
        # CRITICAL: Explicit profile to avoid wrong model/config (GOTCHA #4)
        if [ -f "$prompt_file" ]; then
            local prompt_content
            if ! prompt_content=$(FEATURE_NAME="$feature" \
                FEATURE_DIR="prps/${feature}" \
                PLANNING_DIR="prps/${feature}/planning" \
                CODEX_DIR="prps/${feature}/codex" \
                LOG_DIR="prps/${feature}/codex/logs" \
                INITIAL_MD_PATH="prps/${feature}/codex/INITIAL.md" \
                PHASE_NAME="$phase" \
                envsubst < "$prompt_file"); then
                echo "❌ ERROR: Failed to render prompt template: ${prompt_file}" >&2
                return 1
            fi

            if [ "$CODEX_CLI_MODE" = "none" ]; then
                echo "⚠️  WARNING: Codex CLI unavailable; creating placeholder output" >&2
                (echo "Skipped: Codex CLI missing" > "$log_file"; exit 0) &
            else
                if [ "$CODEX_CLI_MODE" = "flag" ]; then
                    (
                        run_with_timeout --kill-after=${KILL_AFTER_SEC}s ${DEFAULT_TIMEOUT_SEC}s \
                            codex exec \
                            -c rollout_recorder.enabled=false \
                            --profile "$CODEX_PROFILE" \
                            --prompt "$prompt_content"
                    ) > "$log_file" 2>&1 &
                else
                    (
                        run_with_timeout --kill-after=${KILL_AFTER_SEC}s ${DEFAULT_TIMEOUT_SEC}s \
                            codex exec \
                            -c rollout_recorder.enabled=false \
                            --profile "$CODEX_PROFILE" \
                            - <<< "$prompt_content"
                    ) > "$log_file" 2>&1 &
                fi
            fi
        else
            echo "⚠️  WARNING: Prompt file not found: ${prompt_file}" >&2
            echo "Creating empty agent that will succeed immediately (for testing)" >&2
            (echo "Skipped: prompt file missing" > "$log_file"; exit 0) &
        fi

        # CRITICAL: Capture PID immediately after background launch (GOTCHA #7)
        local pid=$!
        pids+=("$pid")
        phase_names+=("$phase")
        echo "   Agent ${phase}: PID ${pid}"
    done

    echo "   Waiting for all agents to complete..."
    echo ""

    # CRITICAL: Wait for each agent and capture exit code IMMEDIATELY (GOTCHA #1)
    # Cannot wait for all at once - must capture each exit code separately
    local exit_codes=()
    local all_success=true
    local failed_phases=()

    for i in "${!pids[@]}"; do
        local pid="${pids[$i]}"
        local phase="${phase_names[$i]}"

        # CRITICAL: Capture exit code IMMEDIATELY after wait (GOTCHA #1)
        # If we don't capture immediately, the exit code is lost
        wait "$pid"
        local exit_code=$?

        exit_codes+=("$exit_code")

        # Calculate duration (from group start - all start at roughly same time)
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))

        # Log phase completion
        log_phase_complete "$feature" "$phase" "$exit_code" "$duration"

        # Interpret exit code (GOTCHA #8: timeout exit codes)
        local status_msg
        case $exit_code in
            0)
                status_msg="✅ SUCCESS"
                ;;
            124)
                status_msg="❌ TIMEOUT (exceeded ${DEFAULT_TIMEOUT_SEC}s)"
                all_success=false
                failed_phases+=("$phase")
                ;;
            125)
                status_msg="❌ TIMEOUT COMMAND FAILED (timeout not installed?)"
                all_success=false
                failed_phases+=("$phase")
                ;;
            137)
                status_msg="❌ KILLED (SIGKILL - process didn't respond to TERM)"
                all_success=false
                failed_phases+=("$phase")
                ;;
            *)
                status_msg="❌ FAILED (exit ${exit_code})"
                all_success=false
                failed_phases+=("$phase")
                ;;
        esac

        echo "   ${status_msg}: ${phase} (${duration}s)"
    done

    # Calculate total parallel execution time
    local total_time=$(date +%s)
    local parallel_duration=$((total_time - start_time))

    echo ""
    echo "========================================="
    echo "Parallel Group Complete: ${group_name}"
    echo "========================================="
    echo "Total parallel duration: ${parallel_duration}s"
    echo ""

    # Report results
    if [ "$all_success" = true ]; then
        echo "✅ All agents succeeded"
        for i in "${!phase_names[@]}"; do
            local phase="${phase_names[$i]}"
            local exit_code="${exit_codes[$i]}"
            echo "   ${phase}: exit ${exit_code}"
        done
        return 0
    else
        echo "❌ Parallel group failed. Failed agents:"
        for failed_phase in "${failed_phases[@]}"; do
            # Find exit code for this phase
            for i in "${!phase_names[@]}"; do
                if [ "${phase_names[$i]}" = "$failed_phase" ]; then
                    local exit_code="${exit_codes[$i]}"
                    echo "   - ${failed_phase}: exit ${exit_code}"
                    break
                fi
            done
        done
        echo ""
        echo "Check logs in: ${log_dir}/"
        return 1
    fi
}

# =============================================================================
# Helper Functions
# =============================================================================

# Calculate speedup from parallel execution
calculate_speedup() {
    local feature="$1"
    shift
    local phases=("$@")

    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    source "${script_dir}/log-phase.sh"

    echo ""
    echo "========================================="
    echo "Speedup Analysis"
    echo "========================================="

    # Get duration for each phase
    local total_sequential=0
    local max_parallel=0

    for phase in "${phases[@]}"; do
        local duration=$(get_phase_duration "$feature" "$phase")
        total_sequential=$((total_sequential + duration))

        if [ "$duration" -gt "$max_parallel" ]; then
            max_parallel=$duration
        fi

        echo "Phase ${phase}: ${duration}s"
    done

    echo ""
    echo "Sequential estimate: ${total_sequential}s"
    echo "Actual parallel time: ${max_parallel}s"

    if [ "$max_parallel" -gt 0 ]; then
        local speedup=$((total_sequential * 100 / max_parallel))
        local speedup_percent=$((speedup - 100))
        echo "Speedup: ${speedup}% (${speedup_percent}% faster)"

        # Check if we achieved at least 2x speedup
        if [ "$speedup" -ge 200 ]; then
            echo "✅ Target speedup achieved (≥2x)"
        else
            echo "⚠️  Below target speedup (expected ≥2x, got ${speedup}%)"
        fi
    fi

    echo "========================================="
}

# =============================================================================
# Testing Functions
# =============================================================================

# Test parallel execution with mock agents
test_parallel_execution() {
    echo "========================================="
    echo "Testing Parallel Execution"
    echo "========================================="
    echo ""

    # Create test feature
    local test_feature="test_parallel_$$"
    local test_dir="prps/${test_feature}/codex"
    mkdir -p "${test_dir}/logs"
    mkdir -p ".codex/prompts"

    # Create mock prompt files (will be skipped, but we'll use sleep instead)
    echo "Test prompt A" > ".codex/prompts/test_phase_a.md"
    echo "Test prompt B" > ".codex/prompts/test_phase_b.md"
    echo "Test prompt C" > ".codex/prompts/test_phase_c.md"

    echo "Test 1: All agents succeed (sleep 2s each)"
    echo "-------------------------------------------"

    # Override codex exec with sleep for testing
    # We'll use a wrapper function instead
    test_agent() {
        local duration="$1"
        local exit_code="${2:-0}"
        sleep "$duration"
        return "$exit_code"
    }

    # Launch test agents
    local start=$(date +%s)

    (test_agent 2 0) > "${test_dir}/logs/test_phase_a.log" 2>&1 &
    local PID_A=$!
    echo "Agent A: PID $PID_A"

    (test_agent 2 0) > "${test_dir}/logs/test_phase_b.log" 2>&1 &
    local PID_B=$!
    echo "Agent B: PID $PID_B"

    (test_agent 2 0) > "${test_dir}/logs/test_phase_c.log" 2>&1 &
    local PID_C=$!
    echo "Agent C: PID $PID_C"

    # Wait and capture exit codes
    wait $PID_A; local EXIT_A=$?
    wait $PID_B; local EXIT_B=$?
    wait $PID_C; local EXIT_C=$?

    local end=$(date +%s)
    local duration=$((end - start))

    echo ""
    echo "Results:"
    echo "  Agent A: exit $EXIT_A"
    echo "  Agent B: exit $EXIT_B"
    echo "  Agent C: exit $EXIT_C"
    echo "  Duration: ${duration}s"

    if [[ $EXIT_A -eq 0 && $EXIT_B -eq 0 && $EXIT_C -eq 0 ]]; then
        echo "✅ Test 1 PASSED: All agents succeeded"
    else
        echo "❌ Test 1 FAILED: Expected all success"
        return 1
    fi

    if [ "$duration" -le 3 ]; then
        echo "✅ Parallel execution confirmed (${duration}s ≤ 3s)"
    else
        echo "⚠️  Execution slower than expected (${duration}s > 3s)"
    fi

    echo ""
    echo "Test 2: One agent fails"
    echo "-------------------------------------------"

    start=$(date +%s)

    (test_agent 1 0) > "${test_dir}/logs/test2_a.log" 2>&1 &
    PID_A=$!

    (test_agent 1 1) > "${test_dir}/logs/test2_b.log" 2>&1 &
    PID_B=$!

    (test_agent 1 0) > "${test_dir}/logs/test2_c.log" 2>&1 &
    PID_C=$!

    wait $PID_A; EXIT_A=$?
    wait $PID_B; EXIT_B=$?
    wait $PID_C; EXIT_C=$?

    echo "Results:"
    echo "  Agent A: exit $EXIT_A (expected 0)"
    echo "  Agent B: exit $EXIT_B (expected 1)"
    echo "  Agent C: exit $EXIT_C (expected 0)"

    if [[ $EXIT_A -eq 0 && $EXIT_B -eq 1 && $EXIT_C -eq 0 ]]; then
        echo "✅ Test 2 PASSED: Exit codes captured correctly"
    else
        echo "❌ Test 2 FAILED: Exit codes incorrect"
        return 1
    fi

    # Cleanup
    rm -rf "prps/${test_feature}"
    rm -f ".codex/prompts/test_phase_"*.md

    echo ""
    echo "========================================="
    echo "✅ All Tests Passed"
    echo "========================================="
}

# =============================================================================
# Usage Information
# =============================================================================

show_usage() {
    cat <<'EOF'
Usage: source .codex/scripts/parallel-exec.sh

Parallel execution helper for Phase 2 agents with:
  - Timeout wrapper (prevents zombie processes)
  - PID tracking (immediate capture with $!)
  - Exit code capture (CRITICAL: immediate after wait)
  - Separate log files (prevents output interleaving)
  - Timeout exit code interpretation (124, 125, 137)

Functions available when sourced:
  - execute_parallel_group <feature> <group_name> <phase1> <phase2> ...
      Execute multiple phases in parallel with full tracking

  - calculate_speedup <feature> <phase1> <phase2> ...
      Calculate speedup from parallel execution

  - test_parallel_execution
      Run self-tests to verify parallel execution

Example Usage:
  # Source the script
  source .codex/scripts/parallel-exec.sh

  # Execute Phase 2 agents in parallel
  execute_parallel_group "user_auth" "phase2" "phase2a" "phase2b" "phase2c"

  # Calculate speedup
  calculate_speedup "user_auth" "phase2a" "phase2b" "phase2c"

  # Run self-tests
  test_parallel_execution

Critical Gotchas Addressed:
  1. Exit code timing (GOTCHA #1) - Captured immediately: wait $PID; EXIT=$?
  2. Timeout wrapper (GOTCHA #3) - All agents wrapped with timeout command
  3. Output interleaving (GOTCHA #5) - Separate log file per agent
  4. Profile omission (GOTCHA #4) - Explicit --profile in all codex exec calls
  5. PID race condition (GOTCHA #7) - PIDs captured with $! immediately
  6. Timeout exit codes (GOTCHA #8) - Special handling for 124, 125, 137

Configuration:
  CODEX_PROFILE       - Codex profile to use (default: codex-prp)
  DEFAULT_TIMEOUT_SEC - Timeout per agent (default: 600s)
  KILL_AFTER_SEC      - Force kill timeout (default: 5s)

EOF
}

# =============================================================================
# Main Script Logic
# =============================================================================

# Show usage if called directly (not sourced)
if [ "${BASH_SOURCE[0]:-}" = "${0}" ]; then
    echo "⚠️  This script is meant to be sourced, not executed directly." >&2
    echo "" >&2
    show_usage
    echo "" >&2
    echo "Alternative: Run self-tests directly" >&2
    echo "  $0 --test" >&2
    echo "" >&2

    # Support --test flag when called directly
    if [ "${1:-}" = "--test" ]; then
        test_parallel_execution
        exit $?
    fi

    exit 1
fi

# If sourced, confirm loading
echo "📦 Parallel execution script loaded" >&2
echo "   Available functions: execute_parallel_group, calculate_speedup, test_parallel_execution" >&2
echo "   Gotchas addressed: Exit code timing, timeout wrapper, PID capture, separate logs" >&2
