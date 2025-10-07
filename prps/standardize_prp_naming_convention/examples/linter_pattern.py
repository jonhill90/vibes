# Source: Feature analysis + best practices for linter scripts
# Pattern: PRP naming convention linter
# Extracted: 2025-10-07
# Relevance: 8/10 - Optional but valuable for proactive validation

"""
PRP Naming Convention Linter

PURPOSE: Proactively detect naming convention violations in prps/ directory.
WHEN TO USE: As pre-commit hook or manual check before committing PRPs.
GOAL: Prevent new PRPs with redundant 'prp_' prefix.
"""

import sys
from pathlib import Path
from typing import List, Dict


# =============================================================================
# PATTERN 1: Linter Main Logic
# =============================================================================

def lint_prp_names(prps_directory: str = "prps") -> Dict[str, List[str]]:
    """
    Check all PRP files for naming convention violations.

    Violations:
    - PRP files with redundant 'prp_' prefix (e.g., prp_context_refactor.md)

    Allowed:
    - Clean names (e.g., user_auth.md, context_refactor.md)
    - INITIAL_ prefix (workflow prefix, temporary)
    - EXAMPLE_ prefix (example PRPs, not for execution)

    Returns:
        dict with keys:
            - violations: List of files with violations
            - warnings: List of files with warnings (legacy files)
            - passed: List of files that passed checks

    Example:
        >>> results = lint_prp_names("prps")
        >>> if results['violations']:
        ...     print(f"❌ Found {len(results['violations'])} violations")
    """
    prps_path = Path(prps_directory)

    # Find all .md files in prps/ directory (not recursive, top-level only)
    prp_files = list(prps_path.glob("*.md"))

    violations = []
    warnings = []
    passed = []

    for prp_file in prp_files:
        filename = prp_file.stem  # Filename without .md extension

        # SKIP: Workflow prefixes (temporary, valid)
        if filename.startswith("INITIAL_"):
            passed.append(str(prp_file))
            continue

        # SKIP: Example files (not real PRPs)
        if filename.startswith("EXAMPLE_"):
            passed.append(str(prp_file))
            continue

        # CHECK: Redundant 'prp_' prefix
        if filename.startswith("prp_"):
            # Legacy files get warning, new files would get error
            # For now, all get violations (can be adjusted based on file timestamp)
            violations.append(str(prp_file))
        else:
            passed.append(str(prp_file))

    return {
        "violations": violations,
        "warnings": warnings,
        "passed": passed,
    }


# =============================================================================
# PATTERN 2: Formatted Output
# =============================================================================

def format_lint_results(results: Dict[str, List[str]]) -> str:
    """
    Format linter results for display.

    Returns:
        Formatted string with color-coded results
    """
    total_files = len(results['violations']) + len(results['warnings']) + len(results['passed'])

    output = []
    output.append("=" * 80)
    output.append("PRP NAMING CONVENTION LINTER")
    output.append("=" * 80)
    output.append("")

    # Violations section
    if results['violations']:
        output.append(f"❌ VIOLATIONS ({len(results['violations'])} files):")
        output.append("")
        for filepath in results['violations']:
            filename = Path(filepath).stem
            output.append(f"  {filepath}")
            output.append(f"    → Remove redundant 'prp_' prefix")
            output.append(f"    → Suggested rename: prps/{filename.replace('prp_', '')}.md")
            output.append("")

    # Warnings section
    if results['warnings']:
        output.append(f"⚠️  WARNINGS ({len(results['warnings'])} files):")
        output.append("")
        for filepath in results['warnings']:
            output.append(f"  {filepath}")
        output.append("")

    # Summary
    output.append("=" * 80)
    output.append("SUMMARY:")
    output.append(f"  Total files checked: {total_files}")
    output.append(f"  ✅ Passed: {len(results['passed'])}")
    output.append(f"  ⚠️  Warnings: {len(results['warnings'])}")
    output.append(f"  ❌ Violations: {len(results['violations'])}")

    if results['violations']:
        output.append("")
        output.append("RESOLUTION:")
        output.append("  1. Rename files to remove 'prp_' prefix")
        output.append("  2. Update references in documentation")
        output.append("  3. Re-run linter to verify fixes")
    else:
        output.append("")
        output.append("✅ All PRP files follow naming conventions!")

    output.append("=" * 80)

    return "\n".join(output)


# =============================================================================
# PATTERN 3: Exit Code Logic
# =============================================================================

def get_exit_code(results: Dict[str, List[str]]) -> int:
    """
    Determine exit code based on linter results.

    Exit codes:
        0: All checks passed (no violations)
        1: Violations found (should fail CI/pre-commit)
        2: Warnings only (should pass but notify)

    Example:
        >>> results = lint_prp_names()
        >>> sys.exit(get_exit_code(results))
    """
    if results['violations']:
        return 1  # Fail
    elif results['warnings']:
        return 2  # Warning (pass but notify)
    else:
        return 0  # Success


# =============================================================================
# PATTERN 4: CLI Interface
# =============================================================================

def main():
    """
    Main CLI entry point for linter.

    Usage:
        python scripts/lint_prp_names.py
        python scripts/lint_prp_names.py prps/

    Exit codes:
        0: Success (no violations)
        1: Violations found
        2: Warnings only
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Lint PRP filenames for naming convention violations"
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default="prps",
        help="Directory to check (default: prps)"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Automatically rename files (NOT IMPLEMENTED - manual rename recommended)"
    )

    args = parser.parse_args()

    # Run linter
    results = lint_prp_names(args.directory)

    # Display results
    print(format_lint_results(results))

    # Exit with appropriate code
    exit_code = get_exit_code(results)
    sys.exit(exit_code)


# =============================================================================
# PATTERN 5: Integration with Pre-Commit Hook
# =============================================================================

def pre_commit_hook() -> int:
    """
    Pre-commit hook integration.

    Usage in .git/hooks/pre-commit:
        #!/bin/bash
        python scripts/lint_prp_names.py
        if [ $? -eq 1 ]; then
            echo "❌ PRP naming violations found. Fix before committing."
            exit 1
        fi

    Returns:
        Exit code (0 = pass, 1 = fail)
    """
    results = lint_prp_names("prps")

    # Only fail on violations (not warnings)
    if results['violations']:
        print(format_lint_results(results))
        print("\n❌ Pre-commit check failed: Fix PRP naming violations")
        return 1

    return 0


# =============================================================================
# TEST EXAMPLES
# =============================================================================

if __name__ == "__main__":
    # If run directly, execute CLI
    main()


# =============================================================================
# EXAMPLE OUTPUT
# =============================================================================

"""
Example output when violations are found:

================================================================================
PRP NAMING CONVENTION LINTER
================================================================================

❌ VIOLATIONS (1 files):

  prps/prp_context_refactor.md
    → Remove redundant 'prp_' prefix
    → Suggested rename: prps/context_refactor.md

================================================================================
SUMMARY:
  Total files checked: 6
  ✅ Passed: 5
  ⚠️  Warnings: 0
  ❌ Violations: 1

RESOLUTION:
  1. Rename files to remove 'prp_' prefix
  2. Update references in documentation
  3. Re-run linter to verify fixes
================================================================================

Exit code: 1 (FAIL)
"""
