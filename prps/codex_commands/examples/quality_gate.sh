#!/bin/bash
# Source: .claude/patterns/quality-gates.md + .claude/commands/generate-prp.md (lines 236-276)
# Pattern: PRP quality scoring and enforcement (8+/10 minimum)
# Extracted: 2025-10-07
# Relevance: 10/10

# =============================================================================
# PATTERN: Quality Gate Enforcement with Score Extraction
# =============================================================================
# Use Case: Validate PRP quality after assembly, enforce minimum threshold
#
# What to Mimic:
#   - Regex score extraction from PRP content
#   - 8/10 minimum threshold with interactive choice
#   - Regeneration loop for failed quality checks
#   - Clear user messaging (current score vs minimum)
#
# What to Adapt:
#   - Minimum score threshold (8/10 default, adjust per project)
#   - Regeneration strategy (full workflow vs specific phases)
#   - Interactive vs automated mode (CI/CD might need automation)
#
# What to Skip:
#   - Complex scoring algorithms (keep simple regex)
#   - Multiple quality metrics (focus on single score first)
#
# CRITICAL GOTCHA: Score Extraction Regex
#   - PRP must include "Score: X/10" in standardized format
#   - Case-insensitive matching recommended
#   - Handle missing score gracefully (default to 0)

set -e

# =============================================================================
# Configuration
# =============================================================================
MIN_QUALITY_SCORE=8
MAX_ATTEMPTS=3

# =============================================================================
# Score Extraction Functions
# =============================================================================

extract_quality_score() {
    local prp_file="$1"

    if [ ! -f "$prp_file" ]; then
        echo "❌ PRP file not found: ${prp_file}" >&2
        echo "0"
        return 1
    fi

    # Extract score using grep + sed
    # Pattern matches: "Score: 8/10" or "Score:8/10" or "Score : 8/10"
    local score=$(grep -iE 'Score[[:space:]]*:[[:space:]]*[0-9]+/10' "$prp_file" | \
                  sed -E 's/.*Score[[:space:]]*:[[:space:]]*([0-9]+)\/10.*/\1/' | \
                  head -1)

    if [ -z "$score" ]; then
        echo "⚠️  No quality score found in PRP (expected 'Score: X/10')" >&2
        echo "0"
        return 1
    fi

    # Validate score is 0-10
    if [ "$score" -lt 0 ] || [ "$score" -gt 10 ]; then
        echo "❌ Invalid score: ${score} (must be 0-10)" >&2
        echo "0"
        return 1
    fi

    echo "$score"
    return 0
}

# =============================================================================
# Quality Gate Enforcement
# =============================================================================

enforce_quality_gate() {
    local prp_file="$1"
    local min_score="${2:-$MIN_QUALITY_SCORE}"

    echo ""
    echo "========================================="
    echo "Quality Gate Enforcement"
    echo "========================================="
    echo "PRP File: ${prp_file}"
    echo "Minimum Score: ${min_score}/10"
    echo ""

    # Extract score
    local score=$(extract_quality_score "$prp_file")
    local extract_exit=$?

    if [ $extract_exit -ne 0 ]; then
        echo "❌ Failed to extract quality score"
        echo ""
        echo "Fix: Ensure PRP includes 'Score: X/10' in content"
        return 1
    fi

    echo "Current Score: ${score}/10"
    echo ""

    # Check against threshold
    if [ "$score" -ge "$min_score" ]; then
        echo "✅ Quality Gate PASSED: ${score}/10 >= ${min_score}/10"
        return 0
    fi

    # Quality gate failed
    echo "❌ Quality Gate FAILED: ${score}/10 < ${min_score}/10"
    echo ""

    return 1
}

# Interactive quality gate with regeneration options
interactive_quality_gate() {
    local prp_file="$1"
    local feature_name="$2"
    local attempt="${3:-1}"

    if [ $attempt -gt $MAX_ATTEMPTS ]; then
        echo "⚠️  Max quality attempts reached (${MAX_ATTEMPTS})"
        echo "Proceeding with current PRP quality"
        return 0
    fi

    if enforce_quality_gate "$prp_file"; then
        return 0
    fi

    # Failed - offer options
    echo "Options:"
    echo "  1. Regenerate entire PRP (re-run all phases)"
    echo "  2. Regenerate research only (re-run Phase 2)"
    echo "  3. Manually improve PRP (edit file)"
    echo "  4. Proceed anyway (accept lower quality)"
    echo "  5. Abort workflow"
    echo ""

    read -p "Choose (1/2/3/4/5): " choice

    case "$choice" in
        1)
            echo ""
            echo "🔄 Regenerating entire PRP (attempt ${attempt}/${MAX_ATTEMPTS})..."
            regenerate_full_prp "$feature_name"
            # Recursive call with incremented attempt
            interactive_quality_gate "$prp_file" "$feature_name" $((attempt + 1))
            ;;
        2)
            echo ""
            echo "🔄 Regenerating research phases (attempt ${attempt}/${MAX_ATTEMPTS})..."
            regenerate_research_phases "$feature_name"
            # Re-run assembly and check again
            regenerate_assembly "$feature_name"
            interactive_quality_gate "$prp_file" "$feature_name" $((attempt + 1))
            ;;
        3)
            echo ""
            echo "📝 Opening PRP for manual editing..."
            echo "File: ${prp_file}"
            echo ""
            echo "After editing, press Enter to re-check quality..."
            read -p ""
            interactive_quality_gate "$prp_file" "$feature_name" $attempt
            ;;
        4)
            echo ""
            echo "⚠️  Proceeding with lower quality PRP"
            echo "Warning: Implementation may require additional research"
            return 0
            ;;
        5)
            echo ""
            echo "Aborting workflow"
            exit 1
            ;;
        *)
            echo "Invalid choice. Try again."
            interactive_quality_gate "$prp_file" "$feature_name" $attempt
            ;;
    esac
}

# =============================================================================
# Regeneration Functions (placeholders - implement based on workflow)
# =============================================================================

regenerate_full_prp() {
    local feature_name="$1"
    echo "TODO: Re-run full PRP generation workflow for ${feature_name}"
    # Implementation: Call main workflow script with feature_name
}

regenerate_research_phases() {
    local feature_name="$1"
    echo "TODO: Re-run Phase 2 (research) for ${feature_name}"
    # Implementation: Call Phase 2 parallel execution
}

regenerate_assembly() {
    local feature_name="$1"
    echo "TODO: Re-run Phase 4 (assembly) for ${feature_name}"
    # Implementation: Call Phase 4 assembler
}

# =============================================================================
# Validation Report Generation
# =============================================================================

generate_quality_report() {
    local prp_file="$1"
    local feature_name="$2"

    echo ""
    echo "========================================="
    echo "PRP Quality Report"
    echo "========================================="
    echo "Feature: ${feature_name}"
    echo "PRP File: ${prp_file}"
    echo ""

    # Extract score
    local score=$(extract_quality_score "$prp_file")

    # Count research artifacts
    local planning_dir="prps/${feature_name}/planning"
    local examples_dir="prps/${feature_name}/examples"

    local research_docs=0
    local example_files=0

    if [ -d "$planning_dir" ]; then
        research_docs=$(find "$planning_dir" -name "*.md" -type f 2>/dev/null | wc -l)
    fi

    if [ -d "$examples_dir" ]; then
        example_files=$(find "$examples_dir" -type f ! -name "README.md" 2>/dev/null | wc -l)
    fi

    # Display metrics
    echo "Quality Metrics:"
    echo "-----------------------------------------"
    echo "PRP Quality Score:    ${score}/10"
    echo "Research Documents:   ${research_docs}"
    echo "Example Files:        ${example_files}"
    echo ""

    # Overall assessment
    if [ "$score" -ge 8 ]; then
        echo "Overall: ✅ READY FOR EXECUTION"
    elif [ "$score" -ge 6 ]; then
        echo "Overall: ⚠️  MARGINAL (consider regeneration)"
    else
        echo "Overall: ❌ NOT READY (regeneration recommended)"
    fi

    echo "========================================="
    echo ""
}

# =============================================================================
# Usage
# =============================================================================

usage() {
    cat <<EOF
Usage: $0 <prp_file> <feature_name> [min_score]

Enforce quality gate for generated PRP.

Arguments:
  prp_file       Path to PRP file (e.g., prps/feature.md)
  feature_name   Feature name (for regeneration if needed)
  min_score      Minimum quality score (default: 8/10)

Examples:
  # Check quality (default 8/10 minimum)
  $0 prps/user_auth.md user_auth

  # Check quality (custom 9/10 minimum)
  $0 prps/user_auth.md user_auth 9

  # Non-interactive mode (exit code 0 = pass, 1 = fail)
  $0 prps/user_auth.md user_auth 8 && echo "Quality passed"

Functions available when sourced:
  - extract_quality_score <prp_file>
  - enforce_quality_gate <prp_file> [min_score]
  - interactive_quality_gate <prp_file> <feature_name> [attempt]
  - generate_quality_report <prp_file> <feature_name>

EOF
}

# =============================================================================
# Main
# =============================================================================

if [ "${BASH_SOURCE[0]:-}" = "${0}" ]; then
    # Check for help flag
    if [ $# -eq 0 ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
        usage
        exit 0
    fi

    # Parse arguments
    PRP_FILE="$1"
    FEATURE_NAME="$2"
    MIN_SCORE="${3:-$MIN_QUALITY_SCORE}"

    # Run quality gate
    if [ -z "$FEATURE_NAME" ]; then
        # Non-interactive mode (just check)
        enforce_quality_gate "$PRP_FILE" "$MIN_SCORE"
    else
        # Interactive mode (with regeneration options)
        interactive_quality_gate "$PRP_FILE" "$FEATURE_NAME" 1
        generate_quality_report "$PRP_FILE" "$FEATURE_NAME"
    fi
fi
