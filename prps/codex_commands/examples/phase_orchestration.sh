#!/bin/bash
# Source: prps/codex_integration/examples/phase_orchestration.sh
# Lines: 64-330 (full orchestration pattern)
# Pattern: Multi-phase workflow with parallel execution (Phase 2)
# Extracted: 2025-10-07
# Relevance: 10/10

# =============================================================================
# PATTERN: Phase Orchestration with Parallel Execution
# =============================================================================
# Use Case: Execute multi-phase workflows with dependency management
#
# What to Mimic:
#   - Sequential phase execution with validation gates
#   - Parallel subagent pattern for independent phases
#   - Error handling with retry/skip/abort options
#   - Progress tracking and status reporting
#   - PID tracking for exit code capture (CRITICAL!)
#
# What to Adapt:
#   - Phase count and dependencies (customize per workflow)
#   - Parallel vs sequential execution strategy
#   - Archon integration (optional)
#   - Timeout values (600s default, adjust per phase)
#
# What to Skip:
#   - Complex DAG orchestration (keep simple for MVP)
#   - Distributed execution (local-only for now)

set -e

# =============================================================================
# Configuration
# =============================================================================
FEATURE_NAME="${1:-}"
CODEX_PROFILE="${2:-codex-prp}"
PHASE_DIR=".codex/commands"
OUTPUT_DIR="prps/${FEATURE_NAME}/codex"

# Phase definitions
declare -A PHASES=(
    [phase0]="Setup and Initialization"
    [phase1]="Feature Analysis"
    [phase2a]="Codebase Research"
    [phase2b]="Documentation Hunt"
    [phase2c]="Example Curation"
    [phase3]="Gotcha Detection"
    [phase4]="PRP Assembly"
)

# Phase dependencies (phases that must complete before this one)
declare -A DEPENDENCIES=(
    [phase0]=""
    [phase1]="phase0"
    [phase2a]="phase1"
    [phase2b]="phase1"
    [phase2c]="phase1"
    [phase3]="phase2a,phase2b,phase2c"
    [phase4]="phase3"
)

# Parallel groups (phases that can run in parallel)
declare -A PARALLEL_GROUPS=(
    [group1]="phase2a,phase2b,phase2c"
)

# =============================================================================
# Phase Execution Functions
# =============================================================================

execute_phase() {
    local phase="$1"
    local phase_name="${PHASES[$phase]}"
    local prompt_file="${PHASE_DIR}/${phase}.md"

    echo ""
    echo "========================================="
    echo "Phase: ${phase} - ${phase_name}"
    echo "========================================="

    if [ ! -f "$prompt_file" ]; then
        echo "⚠️  Prompt file not found: ${prompt_file}"
        echo "Skipping phase: ${phase}"
        return 0
    fi

    local start_time=$(date +%s)
    local log_file="${OUTPUT_DIR}/logs/${phase}.log"

    # Execute Codex
    if codex exec \
        --profile "$CODEX_PROFILE" \
        --prompt "$(cat "$prompt_file")" \
        > "$log_file" 2>&1; then

        local exit_code=0
        local status="✅ SUCCESS"
    else
        local exit_code=$?
        local status="❌ FAILED"
    fi

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    echo "${status}: ${phase} completed in ${duration}s"

    # Log to manifest
    source "${OUTPUT_DIR}/scripts/manifest_logger.sh"
    log_phase_complete "$phase" "$exit_code" "$duration"

    return $exit_code
}

# =============================================================================
# CRITICAL PATTERN: Parallel Group Execution with PID Tracking
# =============================================================================
# This is the KEY pattern for 3x speedup (Phase 2: 15min → 5min)
#
# GOTCHA 1: Exit Code Capture Timing
#   ❌ WRONG: wait $PID1 $PID2 $PID3; EXIT=$?
#              (only captures last PID's exit code!)
#   ✅ RIGHT: wait $PID1; EXIT1=$?
#             wait $PID2; EXIT2=$?
#             wait $PID3; EXIT3=$?
#             (capture IMMEDIATELY after each wait)
#
# GOTCHA 2: Output Interleaving
#   ❌ WRONG: All agents write to stdout (mixed output)
#   ✅ RIGHT: Separate log files per agent (phase2a.log, phase2b.log, phase2c.log)
#
# GOTCHA 3: Zombie Processes
#   ❌ WRONG: codex exec & (can hang forever, blocks wait)
#   ✅ RIGHT: timeout 600 codex exec & (kills after 10min)

execute_parallel_group() {
    local group_name="$1"
    local phases="${PARALLEL_GROUPS[$group_name]}"

    echo ""
    echo "========================================="
    echo "Parallel Group: ${group_name}"
    echo "Phases: ${phases}"
    echo "========================================="

    IFS=',' read -ra PHASE_ARRAY <<< "$phases"

    # Start all phases in background
    local pids=()
    local phase_names=()

    for phase in "${PHASE_ARRAY[@]}"; do
        echo "🚀 Starting: ${phase} (${PHASES[$phase]})"
        execute_phase "$phase" &
        pids+=($!)
        phase_names+=("$phase")
    done

    # CRITICAL: Wait for all phases to complete
    # Capture exit codes IMMEDIATELY after each wait (not later!)
    local all_success=true
    local failed_phases=()

    for i in "${!pids[@]}"; do
        local pid="${pids[$i]}"
        local phase="${phase_names[$i]}"

        if wait "$pid"; then
            echo "✅ Completed: ${phase}"
        else
            echo "❌ Failed: ${phase}"
            all_success=false
            failed_phases+=("$phase")
        fi
    done

    if [ "$all_success" = false ]; then
        echo ""
        echo "❌ Parallel group failed. Failed phases:"
        printf '  - %s\n' "${failed_phases[@]}"
        return 1
    fi

    echo "✅ All parallel phases completed successfully"
    return 0
}

# =============================================================================
# Dependency Management
# =============================================================================

check_dependencies() {
    local phase="$1"
    local deps="${DEPENDENCIES[$phase]}"

    if [ -z "$deps" ]; then
        return 0  # No dependencies
    fi

    IFS=',' read -ra DEP_ARRAY <<< "$deps"

    for dep in "${DEP_ARRAY[@]}"; do
        if ! source "${OUTPUT_DIR}/scripts/manifest_logger.sh" && \
           validate_phase_completion "$dep"; then
            echo "❌ Dependency not met: ${dep} (required by ${phase})"
            return 1
        fi
    done

    return 0
}

# =============================================================================
# Main Orchestration
# =============================================================================

orchestrate_workflow() {
    echo "========================================="
    echo "Codex PRP Generation Workflow"
    echo "========================================="
    echo "Feature: ${FEATURE_NAME}"
    echo "Profile: ${CODEX_PROFILE}"
    echo "Output: ${OUTPUT_DIR}"
    echo ""

    # Setup
    mkdir -p "${OUTPUT_DIR}/logs"
    mkdir -p "${OUTPUT_DIR}/scripts"

    # Copy helper scripts
    cp examples/manifest_logger.sh "${OUTPUT_DIR}/scripts/"

    # Phase 0: Setup (always sequential)
    execute_phase "phase0" || {
        echo "❌ Setup failed. Aborting."
        exit 1
    }

    # Phase 1: Feature Analysis (sequential)
    execute_phase "phase1" || {
        echo "❌ Feature analysis failed. Aborting."
        exit 1
    }

    # Phase 2: Parallel Research (3 subagents)
    echo ""
    echo "========================================="
    echo "Phase 2: Parallel Research (3x speedup)"
    echo "========================================="

    if execute_parallel_group "group1"; then
        echo "✅ Research phase completed"
    else
        echo "❌ Research phase failed"
        handle_phase_failure "phase2_parallel"
    fi

    # Phase 3: Gotcha Detection (sequential, depends on Phase 2)
    check_dependencies "phase3" || {
        echo "❌ Dependencies not met for phase3"
        exit 1
    }

    execute_phase "phase3" || {
        handle_phase_failure "phase3"
    }

    # Phase 4: PRP Assembly (sequential, depends on Phase 3)
    check_dependencies "phase4" || {
        echo "❌ Dependencies not met for phase4"
        exit 1
    }

    execute_phase "phase4" || {
        handle_phase_failure "phase4"
    }

    # Final validation
    echo ""
    echo "========================================="
    echo "Workflow Complete"
    echo "========================================="

    source "${OUTPUT_DIR}/scripts/manifest_logger.sh"
    generate_summary_report
}

# =============================================================================
# Error Handling
# =============================================================================

handle_phase_failure() {
    local phase="$1"

    echo ""
    echo "========================================="
    echo "❌ Phase Failed: ${phase}"
    echo "========================================="
    echo ""
    echo "Options:"
    echo "  1. Retry phase"
    echo "  2. Skip phase (continue with partial results)"
    echo "  3. Abort workflow"
    echo ""

    read -p "Choose (1/2/3): " choice

    case "$choice" in
        1)
            echo "Retrying phase: ${phase}"
            execute_phase "$phase" || handle_phase_failure "$phase"
            ;;
        2)
            echo "⚠️  Skipping phase: ${phase}"
            echo "Continuing with partial results..."
            ;;
        3)
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
# Usage
# =============================================================================

usage() {
    cat <<EOF
Usage: $0 <feature_name> [codex_profile]

Orchestrates multi-phase PRP generation workflow with:
  - Sequential execution for dependent phases
  - Parallel execution for independent phases (3x speedup)
  - Dependency validation
  - Error handling with retry/skip/abort

Example:
  $0 user_authentication codex-prp

Environment Variables:
  CODEX_PROFILE - Override default profile
  AUTO_RETRY    - Automatically retry failed phases (true/false)

EOF
}

# =============================================================================
# Main
# =============================================================================

if [ $# -eq 0 ]; then
    usage
    exit 1
fi

if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    orchestrate_workflow
fi
