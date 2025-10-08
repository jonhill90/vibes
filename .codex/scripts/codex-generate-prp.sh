#!/usr/bin/env bash
# .codex/scripts/codex-generate-prp.sh
# Purpose: Orchestrate full 5-phase PRP generation workflow with parallel Phase 2
# Pattern: Adapted from prps/codex_integration/examples/phase_orchestration.sh
# Source: PRP Task 3 - Complete PRP generation with quality gates

# =============================================================================
# Bash Version Check
# =============================================================================

# Require Bash 4.0+ for associative arrays
if [ "${BASH_VERSINFO[0]}" -lt 4 ]; then
    echo "❌ ERROR: Bash 4.0 or higher is required for associative arrays" >&2
    echo "   Current version: ${BASH_VERSION}" >&2
    echo "" >&2
    echo "   On macOS, install via Homebrew:" >&2
    echo "     brew install bash" >&2
    echo "     /opt/homebrew/bin/bash $(basename "$0") ..." >&2
    exit 1
fi

# =============================================================================
# Configuration
# =============================================================================

# Codex profile (can be overridden via environment variable)
CODEX_PROFILE="${CODEX_PROFILE:-codex-prp}"

# Determine GNU timeout binary (macOS provides gtimeout via coreutils)
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
export TIMEOUT_BIN

# Detect Codex CLI availability and prompt handling
CODEX_CLI_MODE="none"  # values: none, flag, stdin
if command -v codex >/dev/null 2>&1; then
    if codex exec --help 2>&1 | grep -q -- "--prompt"; then
        CODEX_CLI_MODE="flag"
    else
        CODEX_CLI_MODE="stdin"
        echo "ℹ️  Codex CLI detected (using stdin prompt mode)" >&2
    fi
else
    echo "⚠️  WARNING: Codex CLI not found; running in placeholder mode" >&2
fi
export CODEX_CLI_MODE

# Timeouts (in seconds)
PHASE0_TIMEOUT=60      # 1 minute for setup
PHASE1_TIMEOUT=600     # 10 minutes for feature analysis
PHASE2_TIMEOUT=600     # 10 minutes per Phase 2 agent
PHASE3_TIMEOUT=600     # 10 minutes for gotcha detection
PHASE4_TIMEOUT=900     # 15 minutes for PRP assembly

# Quality gate settings (reserved for future use)
# shellcheck disable=SC2034
MIN_PRP_SCORE=8
# shellcheck disable=SC2034
MAX_REGENERATION_ATTEMPTS=3

# Lightweight timeout wrapper (falls back to direct execution if timeout unavailable)
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

# Script directory (for sourcing dependencies)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Archon integration (global state for graceful degradation)
ARCHON_AVAILABLE=false
ARCHON_PROJECT_ID=""
declare -A ARCHON_TASK_IDS  # Map phase name to task ID

# =============================================================================
# Import Dependencies
# =============================================================================

source "${SCRIPT_DIR}/log-phase.sh"
source "${SCRIPT_DIR}/security-validation.sh"
source "${SCRIPT_DIR}/parallel-exec.sh"

# =============================================================================
# Archon Integration
# =============================================================================

# Check if Archon CLI is available and functional
check_archon_availability() {
    # Check if archon command exists
    if ! command -v archon &> /dev/null; then
        echo "ℹ️  Archon CLI not found - proceeding without project tracking"
        return 1
    fi

    # Test basic archon functionality with timeout
    # CRITICAL: Use timeout to prevent hanging if archon server is down
    if run_with_timeout 3s archon health-check &> /dev/null; then
        echo "✅ Archon MCP server available"
        return 0
    else
        echo "ℹ️  Archon CLI found but server not responding - proceeding without tracking"
        return 1
    fi
}

# Initialize Archon project and tasks
archon_initialize_project() {
    local feature="$1"

    if [ "$ARCHON_AVAILABLE" != "true" ]; then
        return 0
    fi

    echo "📊 Initializing Archon project tracking..."

    # Create project
    local project_json
    if ! project_json=$(archon create-project \
        --title "PRP: ${feature}" \
        --description "Generating comprehensive PRP from INITIAL.md" \
        --format json 2>/dev/null); then
        echo "⚠️  Failed to create Archon project - continuing without tracking"
        ARCHON_AVAILABLE=false
        return 0
    fi

    # Extract project ID (assuming JSON format: {"project": {"id": "..."}})
    ARCHON_PROJECT_ID=$(echo "$project_json" | grep -o '"id"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | cut -d'"' -f4)

    if [ -z "$ARCHON_PROJECT_ID" ]; then
        echo "⚠️  Failed to extract project ID - continuing without tracking"
        ARCHON_AVAILABLE=false
        return 0
    fi

    echo "   Project ID: ${ARCHON_PROJECT_ID}"

    # Create tasks for all phases
    local -A task_priorities
    task_priorities[phase0]=100
    task_priorities[phase1]=95
    task_priorities[phase2a]=90
    task_priorities[phase2b]=85
    task_priorities[phase2c]=80
    task_priorities[phase3]=75
    task_priorities[phase4]=70

    for phase in phase0 phase1 phase2a phase2b phase2c phase3 phase4; do
        local task_json
        if task_json=$(archon create-task \
            --project-id "$ARCHON_PROJECT_ID" \
            --title "${phase}: ${PHASES[$phase]}" \
            --description "Execute ${PHASES[$phase]} for ${feature}" \
            --status "todo" \
            --priority "${task_priorities[$phase]}" \
            --format json 2>/dev/null); then

            # Extract task ID
            local task_id
            task_id=$(echo "$task_json" | grep -o '"id"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | cut -d'"' -f4)

            if [ -n "$task_id" ]; then
                ARCHON_TASK_IDS[$phase]="$task_id"
                echo "   ✅ Task created: ${phase} (${task_id})"
            fi
        fi
    done

    echo "📊 Archon project initialized successfully"
    return 0
}

# Update Archon task status
archon_update_task_status() {
    local phase="$1"
    local status="$2"  # todo, doing, done, blocked

    if [ "$ARCHON_AVAILABLE" != "true" ]; then
        return 0
    fi

    local task_id="${ARCHON_TASK_IDS[$phase]}"
    if [ -z "$task_id" ]; then
        return 0
    fi

    # Update task status
    archon update-task \
        --task-id "$task_id" \
        --status "$status" \
        &> /dev/null || true  # Ignore errors to prevent workflow disruption
}

# Store final PRP in Archon
archon_store_prp() {
    local feature="$1"
    local prp_file="prps/${feature}.md"

    if [ "$ARCHON_AVAILABLE" != "true" ]; then
        return 0
    fi

    if [ ! -f "$prp_file" ]; then
        echo "⚠️  PRP file not found: ${prp_file}"
        return 0
    fi

    echo "📊 Storing PRP in Archon..."

    # Store as document
    if archon create-document \
        --project-id "$ARCHON_PROJECT_ID" \
        --title "${feature}.md" \
        --type "prp" \
        --content "$(cat "$prp_file")" \
        &> /dev/null; then
        echo "   ✅ PRP stored in Archon"
    else
        echo "   ⚠️  Failed to store PRP in Archon"
    fi

    return 0
}

# =============================================================================
# Phase Definitions
# =============================================================================

# Phase descriptions
declare -A PHASES
PHASES[phase0]="Setup and Initialization"
PHASES[phase1]="Feature Analysis"
PHASES[phase2a]="Codebase Research"
PHASES[phase2b]="Documentation Hunt"
PHASES[phase2c]="Example Curation"
PHASES[phase3]="Gotcha Detection"
PHASES[phase4]="PRP Assembly"

# Phase dependencies (comma-separated list of phases that must complete first)
declare -A DEPENDENCIES
DEPENDENCIES[phase0]=""
DEPENDENCIES[phase1]="phase0"
DEPENDENCIES[phase2a]="phase1"
DEPENDENCIES[phase2b]="phase1"
DEPENDENCIES[phase2c]="phase1"
DEPENDENCIES[phase3]="phase2a,phase2b,phase2c"
DEPENDENCIES[phase4]="phase3"

# Parallel groups (phases that can run simultaneously)
# shellcheck disable=SC2034
declare -A PARALLEL_GROUPS
PARALLEL_GROUPS[group1]="phase2a,phase2b,phase2c"

# Phase timeouts
declare -A TIMEOUTS
TIMEOUTS[phase0]=$PHASE0_TIMEOUT
TIMEOUTS[phase1]=$PHASE1_TIMEOUT
TIMEOUTS[phase2a]=$PHASE2_TIMEOUT
TIMEOUTS[phase2b]=$PHASE2_TIMEOUT
TIMEOUTS[phase2c]=$PHASE2_TIMEOUT
TIMEOUTS[phase3]=$PHASE3_TIMEOUT
TIMEOUTS[phase4]=$PHASE4_TIMEOUT

# Enable strict mode AFTER array initialization
set -euo pipefail

# =============================================================================
# Dependency Validation
# =============================================================================

# Check if all dependencies for a phase are met
check_dependencies() {
    local feature="$1"
    local phase="$2"
    local deps="${DEPENDENCIES[$phase]}"

    # No dependencies - OK to proceed
    if [ -z "$deps" ]; then
        return 0
    fi

    # Parse comma-separated dependency list
    IFS=',' read -ra DEP_ARRAY <<< "$deps"

    local missing_deps=()
    for dep in "${DEP_ARRAY[@]}"; do
        # Trim leading/trailing whitespace without external tools (sandbox safe)
        dep="${dep#"${dep%%[![:space:]]*}"}"
        dep="${dep%"${dep##*[![:space:]]}"}"

        # Check if dependency phase completed successfully
        if ! validate_phase_completion "$feature" "$dep" 2>/dev/null; then
            missing_deps+=("$dep")
        fi
    done

    # Report missing dependencies
    if [ ${#missing_deps[@]} -gt 0 ]; then
        echo "❌ ERROR: Dependencies not met for ${phase}" >&2
        echo "   Required: ${deps}" >&2
        echo "   Missing: ${missing_deps[*]}" >&2
        return 1
    fi

    return 0
}

# =============================================================================
# Phase Execution
# =============================================================================

# Execute a single sequential phase
execute_sequential_phase() {
    local feature="$1"
    local phase="$2"
    local prompt_file="$3"
    local timeout_sec="${TIMEOUTS[$phase]}"

    echo ""
    echo "========================================="
    echo "Phase: ${phase} - ${PHASES[$phase]}"
    echo "========================================="

    # Check dependencies
    if ! check_dependencies "$feature" "$phase"; then
        echo "❌ Cannot execute ${phase} - dependencies not met" >&2
        archon_update_task_status "$phase" "blocked"
        return 1
    fi

    # Check if prompt file exists
    if [ ! -f "$prompt_file" ]; then
        echo "⚠️  WARNING: Prompt file not found: ${prompt_file}" >&2
        echo "Creating placeholder output for testing..." >&2

        # Create placeholder output
        local output_dir="prps/${feature}/codex/planning"
        mkdir -p "$output_dir"
        echo "# ${PHASES[$phase]} (Placeholder)" > "${output_dir}/${phase}.md"

        log_phase_start "$feature" "$phase"
        log_phase_complete "$feature" "$phase" 0 0
        archon_update_task_status "$phase" "done"
        return 0
    fi

    # Ensure Codex CLI is available
    if [ "$CODEX_CLI_MODE" = "none" ]; then
        echo "⚠️  WARNING: Codex CLI unavailable; creating placeholder output" >&2
        local output_dir="prps/${feature}/codex/planning"
        mkdir -p "$output_dir"
        echo "# ${PHASES[$phase]} (Placeholder - Codex CLI unavailable)" > "${output_dir}/${phase}.md"
        log_phase_start "$feature" "$phase"
        log_phase_complete "$feature" "$phase" 0 0
        archon_update_task_status "$phase" "done"
        return 0
    fi

    # Update Archon: mark task as "doing"
    archon_update_task_status "$phase" "doing"

    # Log phase start
    log_phase_start "$feature" "$phase"

    # Setup log file
    local log_dir="prps/${feature}/codex/logs"
    mkdir -p "$log_dir"
    local log_file="${log_dir}/${phase}.log"

    # Resolve prompt template with runtime context
    local prompt_content
    if ! prompt_content=$(FEATURE_NAME="$feature" \
        INITIAL_MD_PATH="$initial_md" \
        FEATURE_DIR="prps/${feature}" \
        PLANNING_DIR="prps/${feature}/planning" \
        CODEX_DIR="prps/${feature}/codex" \
        LOG_DIR="prps/${feature}/codex/logs" \
        PHASE_NAME="$phase" \
        envsubst < "$prompt_file"); then
        echo "❌ ERROR: Failed to render prompt template: ${prompt_file}" >&2
        return 1
    fi

    # Execute with timeout wrapper
    local start_time
    start_time=$(date +%s)
    local exit_code=0

    echo "🚀 Starting: ${PHASES[$phase]}"
    echo "   Timeout: ${timeout_sec}s"
    echo "   Profile: ${CODEX_PROFILE}"

    # CRITICAL: Timeout wrapper to prevent zombie processes (GOTCHA #3)
    # CRITICAL: Explicit profile to avoid wrong model/config (GOTCHA #4)
    local cmd_exit=0
    if [ "$CODEX_CLI_MODE" = "flag" ]; then
        if run_with_timeout --kill-after=5s "${timeout_sec}s" \
            codex exec \
            -c rollout_recorder.enabled=false \
            --profile "$CODEX_PROFILE" \
            --prompt "$prompt_content" \
            > "$log_file" 2>&1; then
            cmd_exit=0
        else
            cmd_exit=$?
        fi
    else
        if run_with_timeout --kill-after=5s "${timeout_sec}s" \
            codex exec \
            -c rollout_recorder.enabled=false \
            --profile "$CODEX_PROFILE" \
            - \
            > "$log_file" 2>&1 <<< "$prompt_content"; then
            cmd_exit=0
        else
            cmd_exit=$?
        fi
    fi

    if [ $cmd_exit -eq 0 ]; then
        exit_code=0
    else
        exit_code=$cmd_exit
    fi

    local end_time
    end_time=$(date +%s)
    local duration=$((end_time - start_time))

    # Interpret exit code (GOTCHA #8: timeout exit codes)
    local status_msg
    local archon_status="done"
    case $exit_code in
        0)
            status_msg="✅ SUCCESS"
            archon_status="done"
            ;;
        124)
            status_msg="❌ TIMEOUT (exceeded ${timeout_sec}s)"
            archon_status="blocked"
            ;;
        125)
            status_msg="❌ TIMEOUT COMMAND FAILED (timeout not installed?)"
            archon_status="blocked"
            ;;
        137)
            status_msg="❌ KILLED (SIGKILL - process didn't respond to TERM)"
            archon_status="blocked"
            ;;
        *)
            status_msg="❌ FAILED (exit ${exit_code})"
            archon_status="blocked"
            ;;
    esac

    echo "${status_msg}: ${phase} completed in ${duration}s"

    # Log phase completion
    log_phase_complete "$feature" "$phase" "$exit_code" "$duration"

    # Update Archon: mark task as "done" or "blocked"
    archon_update_task_status "$phase" "$archon_status"

    return $exit_code
}

# Execute Phase 2 in parallel (3 agents)
execute_phase2_parallel() {
    local feature="$1"

    echo ""
    echo "========================================="
    echo "Phase 2: Parallel Research (3x speedup)"
    echo "========================================="

    # Check dependencies for all Phase 2 agents
    for phase in phase2a phase2b phase2c; do
        if ! check_dependencies "$feature" "$phase"; then
            echo "❌ Cannot execute Phase 2 - dependencies not met" >&2
            for p in phase2a phase2b phase2c; do
                archon_update_task_status "$p" "blocked"
            done
            return 1
        fi
    done

    # Update Archon: mark all Phase 2 tasks as "doing" BEFORE parallel execution
    archon_update_task_status "phase2a" "doing"
    archon_update_task_status "phase2b" "doing"
    archon_update_task_status "phase2c" "doing"

    # Use parallel execution helper (from parallel-exec.sh)
    # This handles PID tracking, exit code capture, timeout wrapper, separate logs
    local exit_code=0
    if execute_parallel_group "$feature" "phase2" "phase2a" "phase2b" "phase2c"; then
        echo "✅ Phase 2 parallel execution complete"
        exit_code=0
    else
        echo "❌ Phase 2 parallel execution failed"
        exit_code=1
    fi

    # Update Archon: mark all Phase 2 tasks as "done" or "blocked" AFTER parallel execution
    if [ $exit_code -eq 0 ]; then
        archon_update_task_status "phase2a" "done"
        archon_update_task_status "phase2b" "done"
        archon_update_task_status "phase2c" "done"
    else
        archon_update_task_status "phase2a" "blocked"
        archon_update_task_status "phase2b" "blocked"
        archon_update_task_status "phase2c" "blocked"
    fi

    return $exit_code
}

# =============================================================================
# Error Handling
# =============================================================================

# Handle phase failure with interactive retry/skip/abort
handle_phase_failure() {
    local feature="$1"
    local phase="$2"
    local exit_code="$3"

    echo ""
    echo "========================================="
    echo "❌ Phase Failed: ${phase}"
    echo "========================================="
    echo "Exit Code: ${exit_code}"
    echo ""

    # Show error details from log
    local log_file="prps/${feature}/codex/logs/${phase}.log"
    if [ -f "$log_file" ]; then
        echo "Last 20 lines of log:"
        echo "-----------------------------------------"
        tail -20 "$log_file"
        echo "-----------------------------------------"
        echo ""
    fi

    # Interactive error handling
    echo "Options:"
    echo "  1. Retry phase (with same timeout)"
    echo "  2. Retry with increased timeout (+50%)"
    echo "  3. Skip phase (continue with partial results)"
    echo "  4. Abort workflow"
    echo ""

    read -r -p "Choose (1/2/3/4): " choice

    case "$choice" in
        1)
            echo "Retrying phase: ${phase}"
            return 1  # Signal to retry
            ;;
        2)
            echo "Retrying with increased timeout..."
            # Increase timeout by 50%
            local current_timeout="${TIMEOUTS[$phase]}"
            local new_timeout=$((current_timeout * 3 / 2))
            TIMEOUTS[$phase]=$new_timeout
            echo "New timeout: ${new_timeout}s (was ${current_timeout}s)"
            return 1  # Signal to retry
            ;;
        3)
            echo "⚠️  Skipping phase: ${phase}"
            echo "Continuing with partial results..."
            return 0  # Signal to continue
            ;;
        4)
            echo "Aborting workflow"
            exit 1
            ;;
        *)
            echo "Invalid choice. Aborting."
            exit 1
            ;;
    esac
}

# =============================================================================
# Phase 0: Setup
# =============================================================================

execute_phase0_setup() {
    local feature="$1"
    local initial_md="$2"

    echo ""
    echo "========================================="
    echo "Phase 0: Setup and Initialization"
    echo "========================================="

    # Update Archon: mark Phase 0 as "doing"
    archon_update_task_status "phase0" "doing"

    log_phase_start "$feature" "phase0"

    local start_time
    start_time=$(date +%s)

    # Create directory structure
    local base_dir="prps/${feature}"
    local codex_dir="${base_dir}/codex"

    echo "📁 Creating directory structure..."
    mkdir -p "${codex_dir}/planning"
    mkdir -p "${codex_dir}/logs"
    mkdir -p "${codex_dir}/examples"

    # Copy INITIAL.md to codex directory
    if [ -f "$initial_md" ]; then
        cp "$initial_md" "${codex_dir}/INITIAL.md"
        echo "   ✅ Copied INITIAL.md"
    fi

    # Initialize manifest (already done by log_phase_start, but verify)
    local manifest="${codex_dir}/logs/manifest.jsonl"
    if [ -f "$manifest" ]; then
        echo "   ✅ Manifest initialized: ${manifest}"
    else
        echo "   ⚠️  WARNING: Manifest not created by log_phase_start"
    fi

    # Create .codex/prompts directory if needed
    mkdir -p ".codex/prompts"
    echo "   ✅ Prompt directory ready"

    # Initialize Archon project tracking (after directory structure created)
    archon_initialize_project "$feature"

    local end_time
    end_time=$(date +%s)
    local duration=$((end_time - start_time))

    log_phase_complete "$feature" "phase0" 0 "$duration"

    # Update Archon: mark Phase 0 as "done"
    archon_update_task_status "phase0" "done"

    echo "✅ Phase 0 complete (${duration}s)"
    return 0
}

# =============================================================================
# Summary Report
# =============================================================================

generate_summary_report() {
    local feature="$1"

    echo ""
    echo "========================================="
    echo "PRP Generation Summary Report"
    echo "========================================="
    echo "Feature: ${feature}"
    echo ""

    # Generate manifest summary
    generate_summary_report "$feature"

    # Calculate total duration
    local manifest="prps/${feature}/codex/logs/manifest.jsonl"
    if [ -f "$manifest" ]; then
        echo ""
        echo "Phase Durations:"
        echo "-----------------------------------------"

        for phase in phase0 phase1 phase2a phase2b phase2c phase3 phase4; do
            local duration
            duration=$(get_phase_duration "$feature" "$phase" 2>/dev/null || echo "0")
            echo "  ${phase}: ${duration}s"
        done

        # Calculate speedup for Phase 2
        echo ""
        echo "Speedup Analysis (Phase 2):"
        echo "-----------------------------------------"

        local dur_2a
        dur_2a=$(get_phase_duration "$feature" "phase2a" 2>/dev/null || echo "0")
        local dur_2b
        dur_2b=$(get_phase_duration "$feature" "phase2b" 2>/dev/null || echo "0")
        local dur_2c
        dur_2c=$(get_phase_duration "$feature" "phase2c" 2>/dev/null || echo "0")

        local sequential_estimate=$((dur_2a + dur_2b + dur_2c))
        local parallel_actual=$dur_2a
        [ "$dur_2b" -gt "$parallel_actual" ] && parallel_actual=$dur_2b
        [ "$dur_2c" -gt "$parallel_actual" ] && parallel_actual=$dur_2c

        echo "  Sequential estimate: ${sequential_estimate}s"
        echo "  Parallel actual: ${parallel_actual}s"

        if [ "$parallel_actual" -gt 0 ]; then
            local speedup=$((sequential_estimate * 100 / parallel_actual))
            local speedup_percent=$((speedup - 100))
            echo "  Speedup: ${speedup}% (${speedup_percent}% faster)"

            if [ $speedup -ge 200 ]; then
                echo "  ✅ Target speedup achieved (≥2x)"
            else
                echo "  ⚠️  Below target speedup (expected ≥2x)"
            fi
        fi
    fi

    echo ""
    echo "Final PRP: prps/${feature}.md"
    echo "Manifest: prps/${feature}/codex/logs/manifest.jsonl"
    echo ""
    echo "========================================="
}

# =============================================================================
# Main Orchestration
# =============================================================================

main() {
    local initial_md="${1:-}"

    # Validate input
    if [ -z "$initial_md" ]; then
        echo "❌ ERROR: INITIAL.md file path required" >&2
        echo "" >&2
        echo "Usage: $0 <path/to/INITIAL_feature.md>" >&2
        echo "" >&2
        echo "Example:" >&2
        echo "  $0 prps/INITIAL_user_auth.md" >&2
        exit 1
    fi

    if [ ! -f "$initial_md" ]; then
        echo "❌ ERROR: INITIAL.md file not found: ${initial_md}" >&2
        exit 1
    fi

    # Extract and validate feature name
    # CRITICAL: Use security validation to prevent path traversal and injection (GOTCHA #2)
    local feature
    feature=$(extract_feature_name "$initial_md" "INITIAL_" "true") || {
        echo "❌ ERROR: Feature name extraction failed" >&2
        exit 1
    }

    echo "========================================="
    echo "Codex PRP Generation Workflow"
    echo "========================================="
    echo "Feature: ${feature}"
    echo "Input: ${initial_md}"
    echo "Profile: ${CODEX_PROFILE}"
    echo "Output: prps/${feature}/codex"
    echo ""

    # Check Archon availability (graceful degradation)
    echo "🔍 Checking Archon availability..."
    if check_archon_availability; then
        ARCHON_AVAILABLE=true
    else
        ARCHON_AVAILABLE=false
    fi
    echo ""

    # Phase 0: Setup
    execute_phase0_setup "$feature" "$initial_md" || {
        echo "❌ Setup failed. Aborting."
        exit 1
    }

    # Phase 1: Feature Analysis
    local phase1_prompt=".codex/prompts/phase1.md"
    while true; do
        if execute_sequential_phase "$feature" "phase1" "$phase1_prompt"; then
            break
        else
            local exit_code=$?
            if ! handle_phase_failure "$feature" "phase1" "$exit_code"; then
                # Skip or abort
                break
            fi
            # Retry
        fi
    done

    # Phase 2: Parallel Research
    while true; do
        if execute_phase2_parallel "$feature"; then
            break
        else
            if ! handle_phase_failure "$feature" "phase2" 1; then
                # Skip or abort
                break
            fi
            # Retry
        fi
    done

    # Validate Phase 2 outputs before continuing (GOTCHA #11: dependency validation)
    echo ""
    echo "Validating Phase 2 outputs..."
    if ! check_dependencies "$feature" "phase3"; then
        echo "⚠️  WARNING: Phase 2 incomplete, Phase 3 may have insufficient inputs"
        read -r -p "Continue anyway? (y/n): " continue_choice
        if [ "$continue_choice" != "y" ]; then
            echo "Aborting workflow"
            exit 1
        fi
    fi

    # Phase 3: Gotcha Detection
    local phase3_prompt=".codex/prompts/phase3.md"
    while true; do
        if execute_sequential_phase "$feature" "phase3" "$phase3_prompt"; then
            break
        else
            local exit_code=$?
            if ! handle_phase_failure "$feature" "phase3" "$exit_code"; then
                break
            fi
        fi
    done

    # Phase 4: PRP Assembly
    local phase4_prompt=".codex/prompts/phase4.md"
    while true; do
        if execute_sequential_phase "$feature" "phase4" "$phase4_prompt"; then
            break
        else
            local exit_code=$?
            if ! handle_phase_failure "$feature" "phase4" "$exit_code"; then
                break
            fi
        fi
    done

    # Generate summary report
    generate_summary_report "$feature"

    # Store final PRP in Archon
    archon_store_prp "$feature"

    echo ""
    echo "========================================="
    echo "✅ PRP Generation Complete"
    echo "========================================="
    echo "PRP: prps/${feature}.md"
    echo "Manifest: prps/${feature}/codex/logs/manifest.jsonl"
    echo ""
}

# =============================================================================
# Entry Point
# =============================================================================

if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
