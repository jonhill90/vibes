#!/bin/bash
# Source: Adapted from validation_checks.sh + Codex exec JSONL output docs
# Pattern: Manifest logging for phase tracking (JSONL format)
# Extracted: 2025-10-07
# Relevance: 9/10 - Essential for audit trail and phase validation

# =============================================================================
# PATTERN: JSONL Manifest Logging
# =============================================================================
# Use Case: Track phase completion, duration, and exit codes
# Format: JSON Lines (one JSON object per line, append-only)
#
# What to Mimic:
#   - JSONL format (newline-delimited JSON)
#   - Append-only logging (use >> not >)
#   - Timestamp in ISO 8601 format (UTC)
#   - Exit code tracking for validation
#
# What to Adapt:
#   - Additional metadata fields (model, tokens, etc.)
#   - Log file location based on your directory structure
#
# What to Skip:
#   - Pretty-printing (JSONL must be one-line-per-entry)
#   - Complex nested structures (keep flat for grep/jq parsing)

set -e

# =============================================================================
# Configuration
# =============================================================================
DEFAULT_MANIFEST_PATH="prps/${FEATURE_NAME}/codex/logs/manifest.jsonl"

# =============================================================================
# Helper Functions
# =============================================================================

# Get current UTC timestamp in ISO 8601 format
get_timestamp() {
    date -u +"%Y-%m-%dT%H:%M:%SZ"
}

# Log phase start
log_phase_start() {
    local phase="$1"
    local manifest="${2:-$DEFAULT_MANIFEST_PATH}"

    local entry=$(cat <<EOF
{"phase":"${phase}","status":"started","timestamp":"$(get_timestamp)"}
EOF
)

    echo "$entry" >> "$manifest"
    echo "📝 Logged phase start: ${phase}" >&2
}

# Log phase completion
log_phase_complete() {
    local phase="$1"
    local exit_code="$2"
    local duration_sec="$3"
    local manifest="${4:-$DEFAULT_MANIFEST_PATH}"

    local status="success"
    if [ "$exit_code" -ne 0 ]; then
        status="failed"
    fi

    local entry=$(cat <<EOF
{"phase":"${phase}","status":"${status}","exit_code":${exit_code},"duration_sec":${duration_sec},"timestamp":"$(get_timestamp)"}
EOF
)

    echo "$entry" >> "$manifest"

    if [ "$exit_code" -eq 0 ]; then
        echo "✅ Logged phase complete: ${phase} (${duration_sec}s)" >&2
    else
        echo "❌ Logged phase failure: ${phase} (exit: ${exit_code})" >&2
    fi
}

# Log approval request (capture for audit trail)
log_approval_request() {
    local request_type="$1"
    local file_path="$2"
    local operation="$3"
    local response="$4"
    local manifest="${5:-$DEFAULT_MANIFEST_PATH}"

    local entry=$(cat <<EOF
{"type":"approval","request_type":"${request_type}","file":"${file_path}","operation":"${operation}","response":"${response}","timestamp":"$(get_timestamp)"}
EOF
)

    echo "$entry" >> "$manifest"
    echo "🔐 Logged approval: ${request_type} - ${response}" >&2
}

# Log Codex exec event (from --json output)
log_codex_event() {
    local event_type="$1"
    local event_data="$2"  # Already JSON formatted
    local manifest="${3:-$DEFAULT_MANIFEST_PATH}"

    local entry=$(cat <<EOF
{"type":"codex_event","event_type":"${event_type}","data":${event_data},"timestamp":"$(get_timestamp)"}
EOF
)

    echo "$entry" >> "$manifest"
}

# =============================================================================
# Validation Functions
# =============================================================================

# Check if phase completed successfully
validate_phase_completion() {
    local phase="$1"
    local manifest="${2:-$DEFAULT_MANIFEST_PATH}"

    if [ ! -f "$manifest" ]; then
        echo "❌ Manifest not found: ${manifest}" >&2
        return 1
    fi

    # Extract phase entry (last occurrence)
    local entry=$(grep "\"phase\":\"${phase}\"" "$manifest" | tail -1)

    if [ -z "$entry" ]; then
        echo "❌ Phase not logged: ${phase}" >&2
        return 1
    fi

    # Check exit code using jq (or grep if jq unavailable)
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
    local phase="$1"
    local manifest="${2:-$DEFAULT_MANIFEST_PATH}"

    local entry=$(grep "\"phase\":\"${phase}\"" "$manifest" | tail -1)

    if command -v jq &> /dev/null; then
        echo "$entry" | jq -r '.duration_sec // 0'
    else
        echo "$entry" | grep -oP '"duration_sec":\K\d+' || echo "0"
    fi
}

# Generate summary report from manifest
generate_summary_report() {
    local manifest="${1:-$DEFAULT_MANIFEST_PATH}"

    if [ ! -f "$manifest" ]; then
        echo "❌ Manifest not found: ${manifest}"
        return 1
    fi

    echo "========================================="
    echo "Manifest Summary Report"
    echo "========================================="
    echo "Manifest: ${manifest}"
    echo ""

    # Count phases
    local total_phases=$(grep -c '"phase":' "$manifest" || echo "0")
    local successful=$(grep -c '"status":"success"' "$manifest" || echo "0")
    local failed=$(grep -c '"status":"failed"' "$manifest" || echo "0")

    echo "Total Phases: ${total_phases}"
    echo "Successful: ${successful}"
    echo "Failed: ${failed}"
    echo ""

    # Show each phase
    echo "Phase Details:"
    echo "-----------------------------------------"

    if command -v jq &> /dev/null; then
        jq -r 'select(.phase != null) | "\(.phase): \(.status) (\(.duration_sec // 0)s, exit: \(.exit_code // 0))"' "$manifest"
    else
        # Fallback: show raw entries
        grep '"phase":' "$manifest" | while IFS= read -r line; do
            echo "$line"
        done
    fi

    echo ""
    echo "========================================="
}

# =============================================================================
# Usage Example
# =============================================================================

example_usage() {
    echo "========================================="
    echo "Example: Phase Execution with Logging"
    echo "========================================="

    FEATURE_NAME="test_feature"
    MANIFEST="prps/${FEATURE_NAME}/codex/logs/manifest.jsonl"
    mkdir -p "$(dirname "$MANIFEST")"

    # Phase 1
    log_phase_start "phase1" "$MANIFEST"
    START=$(date +%s)

    # Simulate work
    sleep 2
    EXIT_CODE=0

    END=$(date +%s)
    DURATION=$((END - START))
    log_phase_complete "phase1" "$EXIT_CODE" "$DURATION" "$MANIFEST"

    # Validation
    if validate_phase_completion "phase1" "$MANIFEST"; then
        echo "Phase 1 validated successfully"
    fi

    # Summary
    generate_summary_report "$MANIFEST"
}

# =============================================================================
# Main
# =============================================================================

if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    echo "Manifest logger script loaded"
    echo ""
    echo "Available functions:"
    echo "  - log_phase_start <phase> [manifest_path]"
    echo "  - log_phase_complete <phase> <exit_code> <duration_sec> [manifest_path]"
    echo "  - log_approval_request <type> <file> <operation> <response> [manifest_path]"
    echo "  - log_codex_event <event_type> <event_json> [manifest_path]"
    echo "  - validate_phase_completion <phase> [manifest_path]"
    echo "  - get_phase_duration <phase> [manifest_path]"
    echo "  - generate_summary_report [manifest_path]"
    echo ""
    echo "Run example: source manifest_logger.sh && example_usage"
fi
