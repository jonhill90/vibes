#!/bin/bash
# Source: scripts/codex/parallel-exec.sh
# Lines: 118-119, 303-304
# Pattern: Directory-relative script sourcing with dirname
# Extracted: 2025-10-08
# Relevance: 9/10 - Critical for scripts that source other scripts

set -euo pipefail

# =============================================================================
# PATTERN 1: Script Directory Resolution
# =============================================================================
# Use Case: Scripts that need to source other scripts in same directory
# Works correctly even after directory moves (directory-relative)

# Get the directory where THIS script is located
# CRITICAL: Use BASH_SOURCE[0], not $0, for correct behavior when sourced
get_script_directory() {
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    echo "$script_dir"
}

# =============================================================================
# PATTERN 2: Sourcing Dependencies from Same Directory
# =============================================================================
# Use Case: parallel-exec.sh sources log-phase.sh
# After move: Both in .codex/scripts/, so pattern works unchanged

source_dependency_example() {
    # Get directory of current script
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

    # Source dependency from same directory
    # BEFORE move: scripts/codex/log-phase.sh
    # AFTER move:  .codex/scripts/log-phase.sh
    # Pattern stays SAME because both scripts move together
    source "${script_dir}/log-phase.sh"

    echo "✅ Sourced log-phase.sh from ${script_dir}"
}

# =============================================================================
# PATTERN 3: Multiple Dependencies
# =============================================================================
# Example from parallel-exec.sh (lines 118-119, 303-304)

source_multiple_dependencies() {
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

    # Source all dependencies from same directory
    source "${script_dir}/log-phase.sh"
    source "${script_dir}/security-validation.sh"
    source "${script_dir}/quality-gate.sh"

    echo "✅ All dependencies sourced from ${script_dir}"
}

# =============================================================================
# PATTERN 4: Why This Pattern Works After Directory Moves
# =============================================================================

demonstrate_move_safety() {
    echo "Directory-relative sourcing pattern explanation:"
    echo ""
    echo "BEFORE MOVE:"
    echo "  Script location: scripts/codex/parallel-exec.sh"
    echo "  Script dir:      scripts/codex/"
    echo "  Source command:  source \"\${script_dir}/log-phase.sh\""
    echo "  Resolves to:     scripts/codex/log-phase.sh ✅"
    echo ""
    echo "AFTER MOVE:"
    echo "  Script location: .codex/scripts/parallel-exec.sh"
    echo "  Script dir:      .codex/scripts/"
    echo "  Source command:  source \"\${script_dir}/log-phase.sh\""
    echo "  Resolves to:     .codex/scripts/log-phase.sh ✅"
    echo ""
    echo "KEY INSIGHT: Pattern uses RELATIVE path within same directory"
    echo "  → Works correctly as long as all scripts move TOGETHER"
    echo "  → NO CODE CHANGES needed in sourcing pattern"
}

# =============================================================================
# PATTERN 5: Repository Root Resolution (Alternative Pattern)
# =============================================================================
# Use Case: When you need to reference files in different directories
# Common in test files that reference scripts

get_repo_root_example() {
    # Get script directory first
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

    # Navigate up to repo root (adjust levels as needed)
    # For .codex/scripts/: go up 2 levels
    local repo_root="$(cd "${script_dir}/../.." && pwd)"

    echo "Script dir: ${script_dir}"
    echo "Repo root:  ${repo_root}"

    # Can now reference any file from root
    local config_file="${repo_root}/.codex/config.toml"
    echo "Config: ${config_file}"
}

# =============================================================================
# PATTERN 6: Environment Variable Pattern (From Tests)
# =============================================================================
# Use Case: Test files that need explicit repo root
# Example from test_generate_prp.sh (lines 14-15)

test_file_pattern() {
    # Test files define REPO_ROOT explicitly
    local SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

    # BEFORE move: tests/codex/ → go up 2 levels → repo root
    # AFTER move:  .codex/tests/ → go up 2 levels → repo root
    # Same relative path, pattern works unchanged

    echo "Test script dir: ${SCRIPT_DIR}"
    echo "Repo root: ${REPO_ROOT}"

    # Reference scripts from root
    # THESE paths WILL need updating after move!
    local script_old="${REPO_ROOT}/scripts/codex/codex-generate-prp.sh"
    local script_new="${REPO_ROOT}/.codex/scripts/codex-generate-prp.sh"

    echo "Old path: ${script_old}"
    echo "New path: ${script_new}"
}

# =============================================================================
# ANTI-PATTERN: What NOT to Do
# =============================================================================

anti_pattern_absolute_path() {
    # ❌ WRONG: Hardcoded absolute path
    # Breaks when script is run from different locations
    # source "/Users/jon/vibes/scripts/codex/log-phase.sh"

    # ❌ WRONG: Relative path from current directory
    # Breaks depending on where script is invoked from
    # source "scripts/codex/log-phase.sh"

    # ✅ RIGHT: Directory-relative with dirname
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    source "${script_dir}/log-phase.sh"
}

# =============================================================================
# SUMMARY: What Changes After Directory Move
# =============================================================================

summarize_impact() {
    echo "========================================="
    echo "Impact of Directory Move on Sourcing"
    echo "========================================="
    echo ""
    echo "Scripts sourcing other scripts in SAME directory:"
    echo "  → NO CHANGES needed"
    echo "  → Pattern: source \"\${script_dir}/dependency.sh\""
    echo "  → Example: parallel-exec.sh sources log-phase.sh"
    echo ""
    echo "Test files referencing scripts in DIFFERENT directory:"
    echo "  → CHANGES NEEDED"
    echo "  → Update: scripts/codex/ → .codex/scripts/"
    echo "  → Update: tests/codex/ → .codex/tests/"
    echo "  → Example: test files calling codex-generate-prp.sh"
    echo ""
    echo "Documentation examples:"
    echo "  → CHANGES NEEDED"
    echo "  → Update all path references"
    echo "  → Example: README.md command examples"
    echo "========================================="
}

# Run demonstration if script executed directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    demonstrate_move_safety
    echo ""
    summarize_impact
fi
