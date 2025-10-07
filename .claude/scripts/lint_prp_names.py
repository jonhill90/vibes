#!/usr/bin/env python3
"""
PRP Naming Convention Linter

PURPOSE: Proactively detect naming convention violations in prps/ directory.
WHEN TO USE: As pre-commit hook or manual check before committing PRPs.
GOAL: Prevent new PRPs with redundant 'prp_' prefix.

Convention Rules:
- PRP files: prps/{feature_name}.md (no prp_ prefix)
- Initial PRPs: prps/INITIAL_{feature_name}.md (workflow prefix, temporary)
- Example PRPs: prps/EXAMPLE_{feature_name}.md (examples, not for execution)
- NEVER use: prps/prp_{feature_name}.md (redundant prefix)

Exit Codes:
- 0: All checks passed (no violations)
- 1: Violations found (should fail CI/pre-commit)
- 2: Warnings only (should pass but notify)
"""

import sys
from pathlib import Path
from typing import List, Dict


def lint_prp_names(prps_directory: str = "prps") -> Dict[str, List[str]]:
    """
    Check all PRP files for naming convention violations.

    Violations:
    - PRP files with redundant 'prp_' prefix (e.g., prp_context_refactor.md)
    - INITIAL_ files with prp_ prefix (e.g., INITIAL_prp_feature.md)

    Allowed:
    - Clean names (e.g., user_auth.md, context_refactor.md)
    - INITIAL_ prefix without prp_ (e.g., INITIAL_feature.md)
    - EXAMPLE_ prefix (example PRPs, not for execution)

    Args:
        prps_directory: Path to prps directory to check

    Returns:
        dict with keys:
            - violations: List of files with violations
            - warnings: List of files with warnings (legacy files)
            - passed: List of files that passed checks
    """
    prps_path = Path(prps_directory)

    if not prps_path.exists():
        return {
            "violations": [f"Directory not found: {prps_directory}"],
            "warnings": [],
            "passed": [],
        }

    # Find all .md files in prps/ directory (not recursive, top-level only)
    prp_files = list(prps_path.glob("*.md"))

    violations = []
    warnings = []
    passed = []

    for prp_file in prp_files:
        filename = prp_file.stem  # Filename without .md extension

        # CHECK 1: INITIAL_ files with prp_ prefix (double violation)
        if filename.startswith("INITIAL_"):
            # Extract feature name after INITIAL_
            feature_name = filename.removeprefix("INITIAL_")

            if feature_name.startswith("prp_"):
                violations.append(str(prp_file))
                continue
            else:
                # Clean INITIAL_ file
                passed.append(str(prp_file))
                continue

        # CHECK 2: EXAMPLE_ files (always allowed)
        if filename.startswith("EXAMPLE_"):
            passed.append(str(prp_file))
            continue

        # CHECK 3: Redundant 'prp_' prefix
        if filename.startswith("prp_"):
            violations.append(str(prp_file))
        else:
            passed.append(str(prp_file))

    return {
        "violations": violations,
        "warnings": warnings,
        "passed": passed,
    }


def format_lint_results(results: Dict[str, List[str]]) -> str:
    """
    Format linter results for display.

    Args:
        results: Dictionary from lint_prp_names()

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
        output.append(f"VIOLATIONS ({len(results['violations'])} files):")
        output.append("")
        for filepath in results['violations']:
            filename = Path(filepath).stem
            output.append(f"  {filepath}")

            # Provide specific fix instructions based on violation type
            if filename.startswith("INITIAL_prp_"):
                # INITIAL_ file with prp_ prefix
                clean_name = filename.removeprefix("INITIAL_").removeprefix("prp_")
                output.append(f"    -> Remove redundant 'prp_' prefix from INITIAL_ file")
                output.append(f"    -> Suggested rename: prps/INITIAL_{clean_name}.md")
            elif filename.startswith("prp_"):
                # Regular file with prp_ prefix
                clean_name = filename.removeprefix("prp_")
                output.append(f"    -> Remove redundant 'prp_' prefix")
                output.append(f"    -> Suggested rename: prps/{clean_name}.md")

            output.append("")

    # Warnings section
    if results['warnings']:
        output.append(f"WARNINGS ({len(results['warnings'])} files):")
        output.append("")
        for filepath in results['warnings']:
            output.append(f"  {filepath}")
        output.append("")

    # Passed section (summary only)
    if results['passed']:
        output.append(f"PASSED ({len(results['passed'])} files):")
        # Show first 5, then summarize
        for filepath in results['passed'][:5]:
            filename = Path(filepath).name
            output.append(f"  {filename}")
        if len(results['passed']) > 5:
            output.append(f"  ... and {len(results['passed']) - 5} more")
        output.append("")

    # Summary
    output.append("=" * 80)
    output.append("SUMMARY:")
    output.append(f"  Total files checked: {total_files}")
    output.append(f"  Passed: {len(results['passed'])}")
    output.append(f"  Warnings: {len(results['warnings'])}")
    output.append(f"  Violations: {len(results['violations'])}")

    if results['violations']:
        output.append("")
        output.append("RESOLUTION:")
        output.append("  1. Rename files to remove 'prp_' prefix")
        output.append("  2. Update references in documentation")
        output.append("  3. Re-run linter to verify fixes")
        output.append("")
        output.append("CONVENTION REFERENCE:")
        output.append("  See: .claude/conventions/prp-naming.md")
    else:
        output.append("")
        output.append("All PRP files follow naming conventions!")

    output.append("=" * 80)

    return "\n".join(output)


def get_exit_code(results: Dict[str, List[str]]) -> int:
    """
    Determine exit code based on linter results.

    Exit codes:
        0: All checks passed (no violations)
        1: Violations found (should fail CI/pre-commit)
        2: Warnings only (should pass but notify)

    Args:
        results: Dictionary from lint_prp_names()

    Returns:
        Exit code (0, 1, or 2)
    """
    if results['violations']:
        return 1  # Fail
    elif results['warnings']:
        return 2  # Warning (pass but notify)
    else:
        return 0  # Success


def main():
    """
    Main CLI entry point for linter.

    Usage:
        python scripts/lint_prp_names.py
        python scripts/lint_prp_names.py prps/
        python scripts/lint_prp_names.py --help

    Exit codes:
        0: Success (no violations)
        1: Violations found
        2: Warnings only
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Lint PRP filenames for naming convention violations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/lint_prp_names.py              # Check prps/ directory
  python scripts/lint_prp_names.py prps/        # Same as above
  python scripts/lint_prp_names.py --help       # Show this help

Exit Codes:
  0 - No violations found
  1 - Violations found (fails CI)
  2 - Warnings only (passes but notifies)

Naming Convention:
  - PRP files: prps/{feature_name}.md (no prp_ prefix)
  - Initial PRPs: prps/INITIAL_{feature_name}.md
  - Example PRPs: prps/EXAMPLE_{feature_name}.md
  - NEVER: prps/prp_{feature_name}.md (redundant prefix)

Reference: .claude/conventions/prp-naming.md
        """
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
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only show violations and errors (suppress passed files)"
    )

    args = parser.parse_args()

    # Handle --fix flag
    if args.fix:
        print("ERROR: --fix flag is not implemented")
        print("Automatic renaming is risky and could break references")
        print("Please rename files manually using git mv to preserve history")
        sys.exit(1)

    # Run linter
    results = lint_prp_names(args.directory)

    # Display results
    output = format_lint_results(results)
    print(output)

    # Exit with appropriate code
    exit_code = get_exit_code(results)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
