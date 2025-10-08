#!/bin/bash
# Source: Conceptual from feature-analysis.md + stdin approval patterns
# Pattern: Approval request handling for Codex CLI
# Extracted: 2025-10-07
# Relevance: 8/10 - Important for interactive approval workflows

# =============================================================================
# PATTERN: Approval Request Handling
# =============================================================================
# Use Case: Capture and log approval requests from Codex CLI
# Context: Codex prompts on stdin when approval_policy = "on-request"
#
# What to Mimic:
#   - Stdin-based approval flow (read from Codex, respond yes/no)
#   - Approval logging for audit trail
#   - Auto-approval policies based on operation type
#
# What to Adapt:
#   - Auto-approval rules (which operations to auto-approve)
#   - Logging format (JSONL, CSV, etc.)
#   - Integration with manifest logging
#
# What to Skip:
#   - GUI/TUI for approvals (this is CLI-only)
#   - Complex approval workflows (keep simple for MVP)

set -e

# =============================================================================
# Configuration
# =============================================================================
FEATURE_NAME="${FEATURE_NAME:-default}"
APPROVAL_LOG="${APPROVAL_LOG:-prps/${FEATURE_NAME}/codex/logs/approvals.jsonl}"
AUTO_APPROVE_READS="${AUTO_APPROVE_READS:-false}"
AUTO_APPROVE_WRITES="${AUTO_APPROVE_WRITES:-false}"

# =============================================================================
# Helper Functions
# =============================================================================

get_timestamp() {
    date -u +"%Y-%m-%dT%H:%M:%SZ"
}

# Log approval decision
log_approval() {
    local request_type="$1"
    local file_path="$2"
    local operation="$3"
    local response="$4"
    local reason="${5:-manual}"

    mkdir -p "$(dirname "$APPROVAL_LOG")"

    local entry=$(cat <<EOF
{"type":"approval","request_type":"${request_type}","file":"${file_path}","operation":"${operation}","response":"${response}","reason":"${reason}","timestamp":"$(get_timestamp)"}
EOF
)

    echo "$entry" >> "$APPROVAL_LOG"
}

# Determine if operation should be auto-approved
should_auto_approve() {
    local operation="$1"
    local file_path="$2"

    # Auto-approve reads if enabled
    if [ "$AUTO_APPROVE_READS" = "true" ] && [[ "$operation" =~ ^(read|list|search)$ ]]; then
        echo "true"
        return
    fi

    # Auto-approve writes if enabled (DANGEROUS - use with caution)
    if [ "$AUTO_APPROVE_WRITES" = "true" ] && [[ "$operation" =~ ^(write|create|modify)$ ]]; then
        # Additional safety: never auto-approve sensitive paths
        if [[ "$file_path" =~ \.env|credentials|secrets|\.ssh ]]; then
            echo "false"
            return
        fi
        echo "true"
        return
    fi

    # Check whitelist paths (example: auto-approve writes to workspace)
    if [[ "$file_path" =~ ^prps/.*/(planning|examples|execution)/ ]]; then
        echo "true"
        return
    fi

    # Default: require manual approval
    echo "false"
}

# Handle approval request from Codex
handle_approval_request() {
    local request_line="$1"

    # Parse request (example format: "Approve read of file.txt? (yes/no)")
    # Extract operation and file path
    local operation="unknown"
    local file_path="unknown"

    if [[ "$request_line" =~ Approve\ ([a-z]+)\ of\ ([^?]+) ]]; then
        operation="${BASH_REMATCH[1]}"
        file_path="${BASH_REMATCH[2]}"
    fi

    # Check auto-approval
    if [ "$(should_auto_approve "$operation" "$file_path")" = "true" ]; then
        echo "yes"
        log_approval "auto" "$file_path" "$operation" "approved" "auto-approval policy"
        echo "🤖 Auto-approved: ${operation} ${file_path}" >&2
    else
        # Manual approval
        echo "📋 Approval request: ${operation} ${file_path}" >&2
        read -p "Approve? (yes/no): " response

        if [[ "$response" =~ ^(yes|y|Y|YES)$ ]]; then
            echo "yes"
            log_approval "manual" "$file_path" "$operation" "approved" "user approved"
            echo "✅ Approved: ${operation} ${file_path}" >&2
        else
            echo "no"
            log_approval "manual" "$file_path" "$operation" "denied" "user denied"
            echo "❌ Denied: ${operation} ${file_path}" >&2
        fi
    fi
}

# =============================================================================
# Interactive Approval Loop
# =============================================================================
# Use Case: Pipe Codex stderr through this script to handle approvals

approval_loop() {
    echo "🔐 Approval handler started" >&2
    echo "Auto-approve reads: ${AUTO_APPROVE_READS}" >&2
    echo "Auto-approve writes: ${AUTO_APPROVE_WRITES}" >&2
    echo "Approval log: ${APPROVAL_LOG}" >&2
    echo "" >&2

    while IFS= read -r line; do
        # Check if line is an approval request
        if [[ "$line" =~ Approve.*(yes/no) ]]; then
            handle_approval_request "$line"
        else
            # Pass through non-approval lines
            echo "$line"
        fi
    done
}

# =============================================================================
# Approval Report
# =============================================================================

generate_approval_report() {
    local log_file="${1:-$APPROVAL_LOG}"

    if [ ! -f "$log_file" ]; then
        echo "No approvals logged"
        return
    fi

    echo "========================================="
    echo "Approval Report"
    echo "========================================="
    echo "Log: ${log_file}"
    echo ""

    local total=$(wc -l < "$log_file" | tr -d ' ')
    local approved=$(grep -c '"response":"approved"' "$log_file" || echo "0")
    local denied=$(grep -c '"response":"denied"' "$log_file" || echo "0")
    local auto=$(grep -c '"reason":"auto-approval policy"' "$log_file" || echo "0")

    echo "Total Requests: ${total}"
    echo "Approved: ${approved}"
    echo "Denied: ${denied}"
    echo "Auto-approved: ${auto}"
    echo ""

    echo "Details:"
    echo "-----------------------------------------"

    if command -v jq &> /dev/null; then
        jq -r '"\(.timestamp) | \(.operation) | \(.file) | \(.response) | \(.reason)"' "$log_file"
    else
        cat "$log_file"
    fi

    echo ""
    echo "========================================="
}

# =============================================================================
# Usage Examples
# =============================================================================

example_codex_with_approval_handler() {
    echo "========================================="
    echo "Example: Codex exec with approval handler"
    echo "========================================="

    # Method 1: Pipe stderr through approval handler
    # codex exec --profile codex-prp --prompt "task" 2>&1 | approval_loop

    # Method 2: Set environment variables for auto-approval
    # AUTO_APPROVE_READS=true codex exec --profile codex-prp --prompt "task"

    # Method 3: Interactive mode (default)
    # codex exec --profile codex-prp --prompt "task"
    # (Codex will prompt on stdin, user responds manually)

    echo "To use approval handler:"
    echo "  1. Source this script: source approval_handler.sh"
    echo "  2. Run: codex exec ... 2>&1 | approval_loop"
    echo "  3. Or set: export AUTO_APPROVE_READS=true"
    echo ""
    echo "Generate report:"
    echo "  generate_approval_report"
}

# =============================================================================
# Approval Policy Helper
# =============================================================================

explain_approval_policies() {
    cat <<EOF
========================================
Codex Approval Policies
========================================

Config Setting: approval_policy in config.toml

1. "untrusted"
   - Prompts for ALL commands and file operations
   - Safest, but slowest (many interruptions)
   - Use for: Untrusted code, production systems

2. "on-request" (RECOMMENDED for generation)
   - Prompts before tool use
   - Allows review of file writes before execution
   - Use for: PRP generation, research phases

3. "on-failure" (RECOMMENDED for execution)
   - Only prompts when operations fail
   - Fast, but less control
   - Use for: PRP execution, automated workflows

4. "never"
   - Full automation, no prompts
   - Fastest, but dangerous
   - Use for: Trusted code, sandbox environments only

========================================
Sandbox Modes (pairs with approval policy)
========================================

1. "read-only"
   - No writes, no network
   - Default for codex exec
   - Override: --full-auto or --sandbox workspace-write

2. "workspace-write"
   - Allow writes to workspace roots only
   - Prevents writing outside project
   - Use for: Most PRP workflows

3. "danger-full-access"
   - Full system access (requires explicit flag)
   - Use for: System administration tasks only
   - ⚠️  WARNING: Can modify any file, run any command

========================================
EOF
}

# =============================================================================
# Main
# =============================================================================

if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    echo "Approval handler script loaded"
    echo ""
    echo "Available functions:"
    echo "  - approval_loop"
    echo "  - handle_approval_request <request_line>"
    echo "  - generate_approval_report [log_file]"
    echo "  - explain_approval_policies"
    echo ""
    echo "Usage:"
    echo "  codex exec ... 2>&1 | source approval_handler.sh && approval_loop"
    echo "  AUTO_APPROVE_READS=true codex exec ..."
fi
