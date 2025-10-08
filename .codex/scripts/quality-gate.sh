#!/bin/bash
# .codex/scripts/quality-gate.sh
# Purpose: Extract PRP quality score and enforce ≥8/10 minimum
# Pattern: Based on prps/codex_commands/examples/quality_gate.sh
# Source: Task 8 from prps/codex_commands.md (lines 763-791)

set -euo pipefail

# Source security validation for feature name handling
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/security-validation.sh" 2>/dev/null || true

# =============================================================================
# Configuration
# =============================================================================

MIN_QUALITY_SCORE=8
MAX_REGENERATION_ATTEMPTS=3

# =============================================================================
# Score Extraction Function
# =============================================================================

extract_prp_score() {
    local prp_file="$1"

    # Validate file exists
    if [ ! -f "$prp_file" ]; then
        echo "❌ ERROR: PRP file not found: ${prp_file}" >&2
        echo "0"
        return 1
    fi

    # Extract score using grep + sed
    # Pattern matches: "Score: 8/10" or "Score:8/10" or "Score : 8/10" or "**Score: 8/10**"
    local score
    score=$(grep -iE '\*?\*?[Ss]core[[:space:]]*:[[:space:]]*[0-9]+/10' "$prp_file" | \
            sed -E 's/.*[Ss]core[[:space:]]*:[[:space:]]*([0-9]+)\/10.*/\1/' | \
            head -1)

    # Return 0 if no score found (with warning)
    if [ -z "$score" ]; then
        echo "⚠️  WARNING: No quality score found in PRP" >&2
        echo "   Expected pattern: 'Score: X/10' in PRP file" >&2
        echo "   File: ${prp_file}" >&2
        echo "0"
        return 1
    fi

    # Validate score is 0-10
    if [ "$score" -lt 0 ] || [ "$score" -gt 10 ] 2>/dev/null; then
        echo "❌ ERROR: Invalid score: ${score} (must be 0-10)" >&2
        echo "0"
        return 1
    fi

    # Success - output the score
    echo "$score"
    return 0
}

# =============================================================================
# Quality Gate Enforcement Function
# =============================================================================

enforce_quality_gate() {
    local prp_file="$1"
    local min_score="${2:-$MIN_QUALITY_SCORE}"
    local max_attempts="${3:-$MAX_REGENERATION_ATTEMPTS}"
    local current_attempt="${4:-1}"

    echo ""
    echo "=========================================="
    echo "Quality Gate Enforcement"
    echo "=========================================="
    echo "PRP File: ${prp_file}"
    echo "Minimum Score: ${min_score}/10"
    echo "Attempt: ${current_attempt}/${max_attempts}"
    echo ""

    # Extract score
    local score
    score=$(extract_prp_score "$prp_file")
    local extract_exit=$?

    if [ $extract_exit -ne 0 ]; then
        echo "❌ Failed to extract quality score from PRP"
        echo ""
        echo "Fix: Ensure PRP includes 'Score: X/10' in content"
        echo ""

        # Offer to continue without score
        read -r -p "Continue without quality score? (y/N): " choice
        if [[ "$choice" =~ ^[Yy]$ ]]; then
            echo "⚠️  WARNING: Proceeding without quality validation"
            return 0
        else
            return 1
        fi
    fi

    echo "Current Score: ${score}/10"
    echo ""

    # Check against threshold
    if [ "$score" -ge "$min_score" ]; then
        echo "✅ Quality Gate PASSED: ${score}/10 >= ${min_score}/10"
        echo ""
        return 0
    fi

    # Quality gate failed
    echo "❌ Quality Gate FAILED: ${score}/10 < ${min_score}/10"
    echo ""

    # Show scoring guidance
    show_scoring_guidance "$score"

    # Check if max attempts reached
    if [ "$current_attempt" -ge "$max_attempts" ]; then
        echo "⚠️  Maximum regeneration attempts reached (${max_attempts})"
        echo ""
        read -r -p "Accept PRP anyway? (y/N): " choice
        if [[ "$choice" =~ ^[Yy]$ ]]; then
            echo "⚠️  WARNING: Proceeding with lower quality PRP (${score}/10)"
            return 0
        else
            echo "❌ Aborting workflow"
            return 1
        fi
    fi

    # Offer choices
    echo "Options:"
    echo "  1. Regenerate PRP (attempt $((current_attempt + 1))/${max_attempts})"
    echo "  2. Accept anyway (proceed with ${score}/10 quality)"
    echo "  3. Abort workflow"
    echo ""

    read -r -p "Choose (1/2/3): " choice

    case "$choice" in
        1)
            echo ""
            echo "🔄 Regeneration requested (would trigger workflow restart)"
            echo "   This would re-run PRP generation phases"
            echo ""
            echo "Note: Automatic regeneration not implemented yet"
            echo "      Please manually regenerate or accept current PRP"
            echo ""
            # In full implementation, this would call regeneration workflow
            return 1
            ;;
        2)
            echo ""
            echo "⚠️  Proceeding with lower quality PRP (${score}/10)"
            echo "   Warning: Implementation may require additional research"
            return 0
            ;;
        3)
            echo ""
            echo "❌ Aborting workflow"
            return 1
            ;;
        *)
            echo "❌ Invalid choice. Aborting."
            return 1
            ;;
    esac
}

# =============================================================================
# Scoring Guidance Function
# =============================================================================

show_scoring_guidance() {
    local current_score="${1:-0}"

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "PRP Quality Scoring Guidance"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # What makes a 10/10 PRP
    echo "What makes a 10/10 PRP:"
    echo "  ✅ Comprehensive context from all 5 phases"
    echo "  ✅ Clear task breakdown with specific steps"
    echo "  ✅ Proven patterns with file references"
    echo "  ✅ All gotchas documented with solutions"
    echo "  ✅ Complete validation strategy"
    echo "  ✅ Example code from codebase"
    echo "  ✅ Documentation links with sections"
    echo "  ✅ Error handling patterns included"
    echo ""

    # Common reasons for <8/10
    echo "Common reasons for <${MIN_QUALITY_SCORE}/10:"
    if [ "$current_score" -le 5 ]; then
        echo "  ❌ Missing research documents (Phase 2 incomplete)"
        echo "  ❌ No codebase patterns identified"
        echo "  ❌ No example code included"
    fi
    if [ "$current_score" -le 7 ]; then
        echo "  ⚠️  Vague task descriptions (not actionable)"
        echo "  ⚠️  Missing gotcha documentation"
        echo "  ⚠️  No validation commands specified"
    fi
    echo "  ⚠️  Generic patterns (not project-specific)"
    echo "  ⚠️  Incomplete documentation references"
    echo "  ⚠️  Missing error handling guidance"
    echo ""

    # How to improve score
    echo "How to improve your PRP score:"
    echo ""
    echo "1. Phase 2 Research (Critical):"
    echo "   • Codebase patterns: Find 3+ similar implementations"
    echo "   • Documentation: Link to specific sections (not just URLs)"
    echo "   • Examples: Extract actual code from codebase"
    echo ""
    echo "2. Gotcha Detection (Important):"
    echo "   • Search for error patterns in git history"
    echo "   • Check for library-specific pitfalls"
    echo "   • Document workarounds with code examples"
    echo ""
    echo "3. Task Clarity (Essential):"
    echo "   • Break into <15 min chunks"
    echo "   • Provide exact file paths to modify"
    echo "   • Include validation commands for each task"
    echo ""
    echo "4. Pattern References (Required):"
    echo "   • Link to existing code: 'Follow pattern from file.py lines X-Y'"
    echo "   • Specify what to mimic vs adapt vs skip"
    echo "   • Include anti-patterns to avoid"
    echo ""

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

# =============================================================================
# Quick Score Check (Non-Interactive)
# =============================================================================

check_prp_score() {
    local prp_file="$1"
    local min_score="${2:-$MIN_QUALITY_SCORE}"

    local score
    score=$(extract_prp_score "$prp_file" 2>/dev/null)
    local extract_exit=$?

    if [ $extract_exit -ne 0 ]; then
        echo "NO_SCORE"
        return 1
    fi

    if [ "$score" -ge "$min_score" ]; then
        echo "PASS:${score}"
        return 0
    else
        echo "FAIL:${score}"
        return 1
    fi
}

# =============================================================================
# Quality Report Generation
# =============================================================================

generate_quality_report() {
    local prp_file="$1"

    # Extract feature name from path
    local feature_name
    feature_name=$(basename "$(dirname "$prp_file")" 2>/dev/null || basename "$prp_file" .md)

    echo ""
    echo "=========================================="
    echo "PRP Quality Report"
    echo "=========================================="
    echo "Feature: ${feature_name}"
    echo "PRP File: ${prp_file}"
    echo ""

    # Extract score
    local score
    score=$(extract_prp_score "$prp_file" 2>/dev/null)
    local extract_exit=$?

    if [ $extract_exit -ne 0 ]; then
        score="N/A"
    fi

    # Count research artifacts
    local prp_dir
    prp_dir=$(dirname "$prp_file")
    local planning_dir="${prp_dir}/planning"
    local examples_dir="${prp_dir}/examples"

    local research_docs=0
    local example_files=0

    if [ -d "$planning_dir" ]; then
        research_docs=$(find "$planning_dir" -name "*.md" -type f 2>/dev/null | wc -l | tr -d ' ')
    fi

    if [ -d "$examples_dir" ]; then
        example_files=$(find "$examples_dir" -type f ! -name "README.md" 2>/dev/null | wc -l | tr -d ' ')
    fi

    # Count gotchas in PRP
    local gotcha_count=0
    if [ -f "$prp_file" ]; then
        gotcha_count=$(grep -ic "gotcha" "$prp_file" 2>/dev/null || echo "0")
    fi

    # Display metrics
    echo "Quality Metrics:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "PRP Quality Score:    ${score}/10"
    echo "Research Documents:   ${research_docs}"
    echo "Example Files:        ${example_files}"
    echo "Gotchas Documented:   ${gotcha_count}"
    echo ""

    # Overall assessment
    if [ "$score" = "N/A" ]; then
        echo "Overall: ⚠️  NO SCORE (cannot validate quality)"
    elif [ "$score" -ge 9 ]; then
        echo "Overall: ✅ EXCELLENT (ready for execution)"
    elif [ "$score" -ge 8 ]; then
        echo "Overall: ✅ READY FOR EXECUTION"
    elif [ "$score" -ge 6 ]; then
        echo "Overall: ⚠️  MARGINAL (consider regeneration)"
    else
        echo "Overall: ❌ NOT READY (regeneration recommended)"
    fi

    echo "=========================================="
    echo ""
}

# =============================================================================
# Usage Information
# =============================================================================

show_usage() {
    cat <<'EOF'
Usage: .codex/scripts/quality-gate.sh <prp_file> [min_score] [max_attempts]

Extract PRP quality score and enforce minimum threshold.

Arguments:
  prp_file       Path to PRP file (e.g., prps/feature.md)
  min_score      Minimum quality score (default: 8/10)
  max_attempts   Max regeneration attempts (default: 3)

Examples:
  # Interactive mode (with regeneration options)
  .codex/scripts/quality-gate.sh prps/user_auth.md

  # Custom minimum score (9/10)
  .codex/scripts/quality-gate.sh prps/user_auth.md 9

  # Custom max attempts
  .codex/scripts/quality-gate.sh prps/user_auth.md 8 5

  # Non-interactive check (CI/CD)
  if .codex/scripts/quality-gate.sh prps/user_auth.md 8 1; then
      echo "Quality passed"
  fi

Functions available when sourced:
  - extract_prp_score <prp_file>
      Extract numeric score from PRP (returns 0 if not found)

  - enforce_quality_gate <prp_file> [min_score] [max_attempts] [current_attempt]
      Interactive quality gate with regeneration options

  - check_prp_score <prp_file> [min_score]
      Non-interactive check (returns PASS:X, FAIL:X, or NO_SCORE)

  - generate_quality_report <prp_file>
      Generate comprehensive quality report

  - show_scoring_guidance [current_score]
      Display scoring guidance and improvement tips

Quality Scoring:
  10/10 = Perfect (comprehensive, proven patterns, all gotchas)
   9/10 = Excellent (minor gaps, ready for execution)
   8/10 = Good (minimum acceptable, may need iteration)
   6-7  = Marginal (missing key sections, regeneration recommended)
   <6   = Poor (incomplete research, not ready)

Exit Codes:
  0 = Quality gate passed
  1 = Quality gate failed or error

See Also:
  - prps/codex_commands.md (Task 8, lines 763-791)
  - .claude/patterns/quality-gates.md
  - prps/codex_commands/examples/quality_gate.sh (pattern source)

EOF
}

# =============================================================================
# Main Script Logic
# =============================================================================

# Main execution (when called directly)
if [ "${BASH_SOURCE[0]:-}" = "${0}" ]; then
    # Check for help flag
    if [ $# -eq 0 ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
        show_usage
        exit 0
    fi

    # Parse arguments
    PRP_FILE="$1"
    MIN_SCORE="${2:-$MIN_QUALITY_SCORE}"
    MAX_ATTEMPTS="${3:-$MAX_REGENERATION_ATTEMPTS}"

    # Validate PRP file exists
    if [ ! -f "$PRP_FILE" ]; then
        echo "❌ ERROR: PRP file not found: ${PRP_FILE}" >&2
        exit 1
    fi

    # Run quality gate (interactive mode)
    enforce_quality_gate "$PRP_FILE" "$MIN_SCORE" "$MAX_ATTEMPTS" 1
    exit_code=$?

    # Generate report
    if [ $exit_code -eq 0 ]; then
        generate_quality_report "$PRP_FILE"
    fi

    exit $exit_code
fi

# If sourced, confirm loading (only if not in non-interactive shell)
if [ -n "${BASH_SOURCE[0]:-}" ] && [ "${BASH_SOURCE[0]:-}" != "${0:-}" ]; then
    echo "📦 Quality gate script loaded" >&2
    echo "   Available functions: extract_prp_score, enforce_quality_gate, check_prp_score, generate_quality_report" >&2
    echo "   Quality threshold: ≥${MIN_QUALITY_SCORE}/10 (max ${MAX_REGENERATION_ATTEMPTS} regeneration attempts)" >&2
fi
