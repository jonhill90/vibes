#!/bin/bash
# .codex/scripts/log-phase.sh
# Purpose: JSONL manifest logging for Codex phase tracking and audit trail
# Pattern: Append-only JSONL with ISO 8601 timestamps (UTC)
# Source: Adapted from prps/codex_integration/examples/manifest_logger.sh

set -euo pipefail

# =============================================================================
# Configuration
# =============================================================================

# Default manifest path (can be overridden)
DEFAULT_MANIFEST_DIR="prps"

# =============================================================================
# Helper Functions
# =============================================================================

# Get current UTC timestamp in ISO 8601 format
get_timestamp() {
    date -u +"%Y-%m-%dT%H:%M:%SZ"
}

# Validate feature name (security check)
validate_feature_name() {
    local feature="$1"

    # Level 1: Whitelist (alphanumeric + _ - only)
    if [[ ! "$feature" =~ ^[a-zA-Z0-9_-]+$ ]]; then
        echo "❌ Invalid feature name: $feature" >&2
        echo "Only alphanumeric, underscore, and hyphen allowed" >&2
        return 1
    fi

    # Level 2: Path traversal check
    if [[ "$feature" == *".."* || "$feature" == *"/"* || "$feature" == *"\\"* ]]; then
        echo "❌ Path traversal detected in feature name: $feature" >&2
        return 1
    fi

    # Level 3: Length check (max 50 chars)
    if [ ${#feature} -gt 50 ]; then
        echo "❌ Feature name too long: ${#feature} chars (max 50)" >&2
        return 1
    fi

    return 0
}

# Get manifest path for feature
get_manifest_path() {
    local feature="$1"
    echo "${DEFAULT_MANIFEST_DIR}/${feature}/codex/logs/manifest.jsonl"
}

# Ensure manifest directory exists
ensure_manifest_dir() {
    local manifest_path="$1"
    local manifest_dir=$(dirname "$manifest_path")

    if [ ! -d "$manifest_dir" ]; then
        mkdir -p "$manifest_dir"
        echo "📁 Created manifest directory: $manifest_dir" >&2
    fi
}

# =============================================================================
# Core Logging Functions
# =============================================================================

# Log phase start
log_phase_start() {
    local feature="$1"
    local phase="$2"

    # Validate inputs
    validate_feature_name "$feature" || return 1

    # Get manifest path
    local manifest=$(get_manifest_path "$feature")
    ensure_manifest_dir "$manifest"

    # Create JSONL entry
    local entry=$(cat <<EOF
{"phase":"${phase}","status":"started","timestamp":"$(get_timestamp)"}
EOF
)

    # Append to manifest (atomic write)
    echo "$entry" >> "$manifest"

    echo "📝 Logged phase start: ${phase}" >&2
}

# Log phase completion
log_phase_complete() {
    local feature="$1"
    local phase="$2"
    local exit_code="$3"
    local duration_sec="${4:-0}"

    # Validate inputs
    validate_feature_name "$feature" || return 1

    # Get manifest path
    local manifest=$(get_manifest_path "$feature")
    ensure_manifest_dir "$manifest"

    # Determine status from exit code
    local status="success"
    if [ "$exit_code" -ne 0 ]; then
        status="failed"
    fi

    # Create JSONL entry
    local entry=$(cat <<EOF
{"phase":"${phase}","status":"${status}","exit_code":${exit_code},"duration_sec":${duration_sec},"timestamp":"$(get_timestamp)"}
EOF
)

    # Append to manifest (atomic write)
    echo "$entry" >> "$manifest"

    if [ "$exit_code" -eq 0 ]; then
        echo "✅ Logged phase complete: ${phase} (${duration_sec}s)" >&2
    else
        echo "❌ Logged phase failure: ${phase} (exit: ${exit_code})" >&2
    fi
}

# =============================================================================
# Validation Functions
# =============================================================================

# Check if phase completed successfully
validate_phase_completion() {
    local feature="$1"
    local phase="$2"

    # Validate inputs
    validate_feature_name "$feature" || return 1

    # Get manifest path
    local manifest=$(get_manifest_path "$feature")

    if [ ! -f "$manifest" ]; then
        echo "❌ Manifest not found: ${manifest}" >&2
        return 1
    fi

    # Extract phase entry (last occurrence)
    local entry=$(grep "\"phase\":\"${phase}\"" "$manifest" 2>/dev/null | tail -1)

    if [ -z "$entry" ]; then
        echo "❌ Phase not logged: ${phase}" >&2
        return 1
    fi

    # Check exit code using jq (or grep fallback)
    if command -v jq &> /dev/null; then
        local exit_code=$(echo "$entry" | jq -r '.exit_code // 999')
        local status=$(echo "$entry" | jq -r '.status // "unknown"')
    else
        # Fallback: grep-based extraction
        local exit_code=$(echo "$entry" | grep -oP '"exit_code":\K\d+' || echo "999")
        local status=$(echo "$entry" | grep -oP '"status":"\K[^"]+' || echo "unknown")
    fi

    if [ "$exit_code" -eq 0 ] || [ "$status" = "success" ]; then
        echo "✅ Phase validated: ${phase}" >&2
        return 0
    else
        echo "❌ Phase failed: ${phase} (exit: ${exit_code}, status: ${status})" >&2
        return 1
    fi
}

# Get phase duration
get_phase_duration() {
    local feature="$1"
    local phase="$2"

    # Validate inputs
    validate_feature_name "$feature" || return 1

    # Get manifest path
    local manifest=$(get_manifest_path "$feature")

    if [ ! -f "$manifest" ]; then
        echo "0"
        return 1
    fi

    local entry=$(grep "\"phase\":\"${phase}\"" "$manifest" 2>/dev/null | tail -1)

    if [ -z "$entry" ]; then
        echo "0"
        return 1
    fi

    if command -v jq &> /dev/null; then
        echo "$entry" | jq -r '.duration_sec // 0'
    else
        echo "$entry" | grep -oP '"duration_sec":\K\d+' || echo "0"
    fi
}

# Validate manifest coverage (all expected phases logged)
validate_manifest_coverage() {
    local feature="$1"
    shift
    local expected_phases=("$@")

    # Validate inputs
    validate_feature_name "$feature" || return 1

    # Get manifest path
    local manifest=$(get_manifest_path "$feature")

    if [ ! -f "$manifest" ]; then
        echo "❌ Manifest not found: ${manifest}" >&2
        return 1
    fi

    echo "Checking manifest coverage for ${feature}..." >&2
    echo "" >&2

    local missing_count=0
    local failed_count=0

    for phase in "${expected_phases[@]}"; do
        if grep -q "\"phase\":\"${phase}\"" "$manifest" 2>/dev/null; then
            # Check if phase succeeded
            local entry=$(grep "\"phase\":\"${phase}\"" "$manifest" | tail -1)
            local phase_status="unknown"

            if command -v jq &> /dev/null; then
                phase_status=$(echo "$entry" | jq -r '.status // "unknown"')
            else
                phase_status=$(echo "$entry" | grep -oP '"status":"\K[^"]+' || echo "unknown")
            fi

            if [ "$phase_status" = "success" ]; then
                echo "✅ ${phase} logged (success)" >&2
            elif [ "$phase_status" = "failed" ]; then
                echo "❌ ${phase} logged (FAILED)" >&2
                ((failed_count++))
            else
                echo "⚠️  ${phase} logged (status: ${phase_status})" >&2
            fi
        else
            echo "❌ ${phase} MISSING" >&2
            ((missing_count++))
        fi
    done

    echo "" >&2

    if [ $missing_count -gt 0 ]; then
        echo "⚠️  ${missing_count} phase(s) missing from manifest" >&2
    fi

    if [ $failed_count -gt 0 ]; then
        echo "⚠️  ${failed_count} phase(s) failed" >&2
    fi

    if [ $missing_count -eq 0 ] && [ $failed_count -eq 0 ]; then
        echo "✅ All phases logged successfully" >&2
        return 0
    else
        return 1
    fi
}

# Generate summary report from manifest
generate_summary_report() {
    local feature="$1"

    # Validate inputs
    validate_feature_name "$feature" || return 1

    # Get manifest path
    local manifest=$(get_manifest_path "$feature")

    if [ ! -f "$manifest" ]; then
        echo "❌ Manifest not found: ${manifest}"
        return 1
    fi

    echo "========================================="
    echo "Manifest Summary Report"
    echo "========================================="
    echo "Feature: ${feature}"
    echo "Manifest: ${manifest}"
    echo ""

    # Count phases
    local total_phases=$(grep -c '"phase":' "$manifest" 2>/dev/null || echo "0")
    local successful=$(grep -c '"status":"success"' "$manifest" 2>/dev/null || echo "0")
    local failed=$(grep -c '"status":"failed"' "$manifest" 2>/dev/null || echo "0")
    local started=$(grep -c '"status":"started"' "$manifest" 2>/dev/null || echo "0")

    echo "Total Phase Entries: ${total_phases}"
    echo "Started: ${started}"
    echo "Successful: ${successful}"
    echo "Failed: ${failed}"
    echo ""

    # Show each phase
    echo "Phase Details:"
    echo "-----------------------------------------"

    if command -v jq &> /dev/null; then
        jq -r 'select(.phase != null) | "\(.phase): \(.status) (\(.duration_sec // 0)s, exit: \(.exit_code // 0))"' "$manifest" 2>/dev/null || {
            echo "⚠️  Error parsing manifest with jq"
            grep '"phase":' "$manifest" | head -20
        }
    else
        # Fallback: show raw entries
        grep '"phase":' "$manifest" | head -20
    fi

    echo ""
    echo "========================================="
}

# =============================================================================
# Main Script Logic
# =============================================================================

# Show usage if called directly
show_usage() {
    cat <<EOF
Usage: $0 <feature_name> <phase> <exit_code> [duration_sec]

Log phase execution to JSONL manifest.

Arguments:
  feature_name    Feature name (alphanumeric, underscore, hyphen only)
  phase           Phase identifier (e.g., "phase1", "phase2a")
  exit_code       Exit code (0 = success, non-zero = failure)
  duration_sec    Duration in seconds (optional, default: 0)

Examples:
  # Log phase start
  $0 codex_integration phase1 start

  # Log phase completion
  $0 codex_integration phase1 0 42

  # Log phase failure
  $0 codex_integration phase2 1 15

Functions available when sourced:
  - log_phase_start <feature> <phase>
  - log_phase_complete <feature> <phase> <exit_code> [duration_sec]
  - validate_phase_completion <feature> <phase>
  - get_phase_duration <feature> <phase>
  - validate_manifest_coverage <feature> <phase1> <phase2> ...
  - generate_summary_report <feature>

Manifest Schema:
  {"phase":"phase1","status":"started","timestamp":"2025-10-07T10:30:00Z"}
  {"phase":"phase1","status":"success","exit_code":0,"duration_sec":42,"timestamp":"2025-10-07T10:31:42Z"}

Manifest Location:
  prps/<feature>/codex/logs/manifest.jsonl

EOF
}

# Main execution when called directly (not sourced)
if [ "${BASH_SOURCE[0]:-}" = "${0}" ]; then
    # Check for help flag
    if [ $# -eq 0 ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
        show_usage
        exit 0
    fi

    # Parse arguments
    FEATURE="$1"
    PHASE="$2"
    EXIT_CODE_OR_STATUS="${3:-}"

    # Check if this is a "start" log
    if [ "$EXIT_CODE_OR_STATUS" = "start" ]; then
        log_phase_start "$FEATURE" "$PHASE"
        exit $?
    fi

    # Otherwise, it's a completion log
    EXIT_CODE="$EXIT_CODE_OR_STATUS"
    DURATION_SEC="${4:-0}"

    # Validate exit code is a number
    if ! [[ "$EXIT_CODE" =~ ^[0-9]+$ ]]; then
        echo "❌ Invalid exit code: $EXIT_CODE (must be a number)" >&2
        show_usage
        exit 1
    fi

    # Log phase completion
    log_phase_complete "$FEATURE" "$PHASE" "$EXIT_CODE" "$DURATION_SEC"
    exit $?
fi

# If sourced, just export functions
echo "📦 Manifest logger script loaded" >&2
echo "   Available functions: log_phase_start, log_phase_complete, validate_phase_completion," >&2
echo "                        get_phase_duration, validate_manifest_coverage, generate_summary_report" >&2
