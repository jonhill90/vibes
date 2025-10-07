# Source: .claude/commands/execute-prp.md + .claude/patterns/quality-gates.md
# Pattern: Actionable error messages with troubleshooting guidance
# Extracted: 2025-10-06
# Relevance: 9/10 - Critical for developer experience and debugging

"""
Error Message Design Pattern: Actionable, Contextual, Helpful

PRINCIPLE: Error messages should enable self-service resolution.

STRUCTURE:
1. Clear problem statement (what failed)
2. Contextual information (relevant paths, values)
3. Why this matters (impact)
4. Troubleshooting steps (how to investigate)
5. Resolution options (how to fix)
"""

from typing import Optional, List


# =============================================================================
# PATTERN 1: Missing Report Error (BEST PRACTICE)
# =============================================================================
# This is the PRIMARY error message for validation gate failures

def format_missing_report_error(
    task_number: int,
    feature_name: str,
    report_type: str = "COMPLETION"
) -> str:
    """
    Format actionable error for missing task report.

    Example:
        >>> error = format_missing_report_error(17, "user_auth")
        >>> raise ValidationError(error)
    """
    report_path = f"prps/{feature_name}/execution/TASK{task_number}_{report_type}.md"
    template_path = f".claude/templates/task-{report_type.lower()}-report.md"

    return f"""
{'='*80}
❌ VALIDATION GATE FAILED: Missing Task Report
{'='*80}

PROBLEM:
Task {task_number} did not generate required completion report.

EXPECTED PATH:
{report_path}

IMPACT:
This task is INCOMPLETE without documentation. Report generation is MANDATORY.
- Cannot audit what was implemented
- Cannot learn from implementation decisions
- Violates PRP execution reliability requirements

TROUBLESHOOTING:
1. Check if task subagent finished execution successfully
   → Review subagent output logs
   → Look for error messages or exceptions

2. Verify template exists and is accessible
   → Check: {template_path}
   → Ensure template has correct variable placeholders

3. Check file system permissions
   → Directory: prps/{feature_name}/execution/
   → Ensure write permissions enabled

4. Review subagent prompt
   → Confirm report generation is marked as CRITICAL
   → Verify path is correct (uses feature_name variable)

5. Check for file naming issues
   → Standard format: TASK{{number}}_{{TYPE}}.md
   → Examples: TASK17_COMPLETION.md, TASK5_VALIDATION.md

RESOLUTION OPTIONS:

Option 1: Re-run task with explicit report requirement
   → Update subagent prompt to emphasize report is mandatory
   → Add validation check in task completion logic

Option 2: Manually create report (not recommended)
   → Use template: {template_path}
   → Save to: {report_path}
   → Fill in all required sections

Option 3: Debug subagent execution
   → Review full subagent output
   → Check for Write() tool errors
   → Verify template variable substitution

DO NOT CONTINUE without resolving this issue.
Report coverage is MANDATORY for PRP execution reliability.

Report this issue to improve subagent reliability.
{'='*80}
"""


# =============================================================================
# PATTERN 2: Incomplete Report Sections Error
# =============================================================================

def format_incomplete_report_error(
    report_path: str,
    missing_sections: List[str]
) -> str:
    """
    Format actionable error for reports missing required sections.

    Example:
        >>> error = format_incomplete_report_error(
        ...     "prps/user_auth/execution/TASK17_COMPLETION.md",
        ...     ["Files Created/Modified", "Validation"]
        ... )
        >>> print(f"⚠️ {error}")
    """
    return f"""
⚠️ REPORT QUALITY WARNING: Missing Required Sections

REPORT PATH:
{report_path}

MISSING SECTIONS:
{chr(10).join(f'  - {section}' for section in missing_sections)}

IMPACT:
Report lacks critical information for auditability and learning.

REQUIRED SECTIONS (Minimum):
  - Implementation Summary (what was done)
  - Files Created/Modified (where changes are)
  - Validation (how success was verified)

RESOLUTION:
1. Open report file: {report_path}
2. Add missing sections using markdown headers (## or ###)
3. Fill in relevant information for each section
4. Save and re-run validation

TEMPLATE REFERENCE:
See .claude/templates/task-completion-report.md for section structure.
"""


# =============================================================================
# PATTERN 3: Validation Level Failure Error
# =============================================================================
# Source: .claude/patterns/quality-gates.md

def format_validation_failure_error(
    level_name: str,
    command: str,
    error_output: str,
    attempt: int,
    max_attempts: int,
    suggested_fix: Optional[str] = None
) -> str:
    """
    Format actionable error for validation level failures.

    Example:
        >>> error = format_validation_failure_error(
        ...     "Level 1: Syntax Check",
        ...     "ruff check --fix src/",
        ...     "src/auth.py:45: F401 'os' imported but unused",
        ...     2,
        ...     5,
        ...     "Remove unused import: os"
        ... )
    """
    header = f"❌ VALIDATION FAILED: {level_name} (Attempt {attempt}/{max_attempts})"

    fix_section = ""
    if suggested_fix:
        fix_section = f"""
SUGGESTED FIX:
{suggested_fix}

Applying fix automatically...
"""
    else:
        fix_section = """
⚠️ No automatic fix available for this error.
Manual intervention may be required.
"""

    return f"""
{header}

COMMAND:
{command}

ERROR OUTPUT:
{error_output}

{fix_section}

NEXT STEPS:
{'- Fix will be applied and validation re-run' if suggested_fix else '- Review error output and fix manually'}
- Attempts remaining: {max_attempts - attempt}
- See PRP "Common Gotchas" section for known issues
"""


# =============================================================================
# PATTERN 4: Report Coverage Summary (Success/Warning)
# =============================================================================

def format_report_coverage_summary(
    total_tasks: int,
    reports_found: int,
    coverage_percentage: float,
    missing_tasks: List[int]
) -> str:
    """
    Format report coverage summary with clear status.

    Example:
        >>> summary = format_report_coverage_summary(25, 12, 48.0, [1,2,3,5,7,8,9,10,12,16,19,23,25])
        >>> print(summary)
    """
    status_emoji = "✅" if coverage_percentage == 100 else "⚠️"
    status_text = "COMPLETE" if coverage_percentage == 100 else "INCOMPLETE"

    missing_section = ""
    if missing_tasks:
        missing_section = f"""
MISSING REPORTS:
Tasks without completion reports: {', '.join(map(str, missing_tasks))}

IMPACT:
- Cannot audit {len(missing_tasks)} tasks ({100 - coverage_percentage:.1f}% of work)
- Incomplete implementation trail
- Violates PRP execution reliability requirements

ACTION REQUIRED:
1. Review which tasks are missing reports (see list above)
2. Re-run missing tasks with report requirement emphasized
3. OR manually create reports using template
4. Target: 100% coverage for full auditability
"""

    return f"""
{'='*80}
{status_emoji} REPORT COVERAGE: {status_text}
{'='*80}

METRICS:
- Total Tasks: {total_tasks}
- Reports Found: {reports_found}
- Coverage: {coverage_percentage:.1f}%
- Status: {status_text}

{missing_section if missing_section else 'All tasks documented! ✅'}
{'='*80}
"""


# =============================================================================
# PATTERN 5: Error Analysis Output
# =============================================================================
# Source: .claude/patterns/quality-gates.md error analysis pattern

def format_error_analysis(
    error_message: str,
    error_type: Optional[str],
    relevant_gotcha: Optional[str],
    suggested_fix: Optional[dict]
) -> str:
    """
    Format error analysis with gotcha matching and fix suggestions.

    Example:
        >>> analysis = format_error_analysis(
        ...     "ImportError: No module named 'pydantic'",
        ...     "import_error",
        ...     "Missing dependency: Add to requirements.txt",
        ...     {"action": "add_dependency", "package": "pydantic"}
        ... )
    """
    gotcha_section = ""
    if relevant_gotcha:
        gotcha_section = f"""
MATCHED GOTCHA:
{relevant_gotcha}

This is a KNOWN issue documented in the PRP.
"""

    fix_section = ""
    if suggested_fix:
        fix_section = f"""
SUGGESTED FIX:
Action: {suggested_fix.get('action', 'Unknown')}
Details: {suggested_fix.get('description', 'See fix dict for details')}

This fix will be applied automatically.
"""

    return f"""
ERROR ANALYSIS:

ERROR TYPE: {error_type or 'Unknown'}

ERROR MESSAGE:
{error_message}

{gotcha_section}

{fix_section if fix_section else 'No automatic fix available. Manual intervention required.'}
"""


# =============================================================================
# USAGE EXAMPLES
# =============================================================================

if __name__ == "__main__":
    # Example 1: Missing report error (validation gate failure)
    print("EXAMPLE 1: Missing Report Error")
    print(format_missing_report_error(17, "user_auth", "COMPLETION"))
    print("\n" + "="*80 + "\n")

    # Example 2: Incomplete report warning
    print("EXAMPLE 2: Incomplete Report Warning")
    print(format_incomplete_report_error(
        "prps/user_auth/execution/TASK17_COMPLETION.md",
        ["Files Created/Modified", "Validation"]
    ))
    print("\n" + "="*80 + "\n")

    # Example 3: Validation failure with suggested fix
    print("EXAMPLE 3: Validation Failure")
    print(format_validation_failure_error(
        "Level 1: Syntax Check",
        "ruff check --fix src/",
        "src/auth.py:45: F401 'os' imported but unused",
        2,
        5,
        "Remove unused import: os"
    ))
    print("\n" + "="*80 + "\n")

    # Example 4: Report coverage - incomplete
    print("EXAMPLE 4: Report Coverage (Incomplete)")
    print(format_report_coverage_summary(
        total_tasks=25,
        reports_found=12,
        coverage_percentage=48.0,
        missing_tasks=[1, 2, 3, 5, 7, 8, 9, 10, 12, 16, 19, 23, 25]
    ))
    print("\n" + "="*80 + "\n")

    # Example 5: Report coverage - complete
    print("EXAMPLE 5: Report Coverage (Complete)")
    print(format_report_coverage_summary(
        total_tasks=25,
        reports_found=25,
        coverage_percentage=100.0,
        missing_tasks=[]
    ))
