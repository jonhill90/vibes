# Source: .claude/commands/execute-prp.md (Phase 0) + .claude/patterns/quality-gates.md
# Pattern: File validation and error handling with security checks
# Extracted: 2025-10-06
# Relevance: 10/10 - Core validation pattern for file existence and security

import re
from pathlib import Path
from typing import List, Optional


# =============================================================================
# PATTERN 1: Security Validation (Path Traversal Protection)
# =============================================================================
# Source: .claude/commands/execute-prp.md lines 15-23
# Use this for ALL user-provided file paths

def extract_feature_name(filepath: str, strip_prefix: Optional[str] = None) -> str:
    """
    Extract and validate feature name from filepath with security checks.

    CRITICAL: This prevents path traversal attacks and shell injection.
    Use before ANY file operations with user-provided paths.

    Args:
        filepath: User-provided file path (e.g., "prps/INITIAL_feature_name.md")
        strip_prefix: Optional prefix to remove (e.g., "INITIAL_")

    Returns:
        Validated feature name (e.g., "feature_name")

    Raises:
        ValueError: If path fails security validation

    Example:
        >>> feature = extract_feature_name("prps/INITIAL_user_auth.md", "INITIAL_")
        >>> # Returns: "user_auth"

        >>> feature = extract_feature_name("prps/../etc/passwd.md")
        >>> # Raises: ValueError("Path traversal: prps/../etc/passwd.md")
    """
    # Check 1: Path traversal detection
    if ".." in filepath:
        raise ValueError(f"Path traversal detected: {filepath}")

    # Extract filename from path
    feature = filepath.split("/")[-1].replace(".md", "")

    # Remove optional prefix
    if strip_prefix:
        feature = feature.replace(strip_prefix, "")

    # Check 2: Valid characters only (alphanumeric, underscore, hyphen)
    if not re.match(r'^[a-zA-Z0-9_-]+$', feature):
        raise ValueError(f"Invalid characters in feature name: {feature}")

    # Check 3: Length validation (prevent DoS)
    if len(feature) > 50:
        raise ValueError(f"Feature name too long ({len(feature)} chars): {feature}")

    # Check 4: Shell injection prevention
    dangerous_chars = ['$', '`', ';', '&', '|', '>', '<', '\n', '\r']
    if any(c in feature for c in dangerous_chars):
        raise ValueError(f"Dangerous characters detected in: {feature}")

    return feature


# =============================================================================
# PATTERN 2: Report Existence Validation
# =============================================================================
# Source: Feature analysis + quality-gates.md
# Use this to check if required reports exist after task completion

def validate_report_exists(feature_name: str, task_number: int, report_type: str = "COMPLETION") -> bool:
    """
    Validate that a task completion report exists.

    This is the VALIDATION GATE that prevents silent documentation failures.
    Call this after each task or task group completes.

    Args:
        feature_name: Validated feature name (from extract_feature_name)
        task_number: Task number (e.g., 17)
        report_type: Report type (COMPLETION, VALIDATION, etc.)

    Returns:
        True if report exists

    Raises:
        ValidationError: If report is missing (with actionable error message)

    Example:
        >>> validate_report_exists("user_auth", 17, "COMPLETION")
        >>> # Raises if prps/user_auth/execution/TASK17_COMPLETION.md missing
    """
    report_path = f"prps/{feature_name}/execution/TASK{task_number}_{report_type}.md"

    if not Path(report_path).exists():
        # CRITICAL: Actionable error message with path and troubleshooting
        error_msg = f"""
❌ VALIDATION GATE FAILED: Missing Task Report

Task {task_number} did not generate required completion report.

Expected Path: {report_path}

This task is INCOMPLETE without documentation.

Troubleshooting:
1. Check if task subagent finished execution
2. Verify template was loaded: .claude/templates/task-completion-report.md
3. Check write permissions in prps/{feature_name}/execution/
4. Review task subagent logs for errors

Resolution:
- Re-run task {task_number} with explicit report requirement
- OR manually create report at expected path
- OR debug subagent execution

DO NOT CONTINUE without resolving this issue.
Report coverage is MANDATORY for PRP execution reliability.
"""
        raise ValidationError(error_msg)

    return True


# =============================================================================
# PATTERN 3: Report Section Validation
# =============================================================================
# Source: Feature analysis (required sections detection)
# Use this to ensure reports have minimum required content

def validate_report_sections(report_path: str, required_sections: List[str]) -> List[str]:
    """
    Validate that report contains all required sections.

    Args:
        report_path: Path to report file
        required_sections: List of section headers to check for

    Returns:
        List of missing sections (empty if all present)

    Example:
        >>> missing = validate_report_sections(
        ...     "prps/user_auth/execution/TASK17_COMPLETION.md",
        ...     ["Implementation Summary", "Files Created/Modified", "Validation"]
        ... )
        >>> if missing:
        ...     print(f"⚠️ Report missing sections: {missing}")
    """
    # Read report content
    with open(report_path, 'r') as f:
        report_content = f.read()

    # Check for each required section
    missing_sections = []
    for section in required_sections:
        # Check for markdown headers (## or ###)
        if f"## {section}" not in report_content and f"### {section}" not in report_content:
            missing_sections.append(section)

    return missing_sections


# =============================================================================
# PATTERN 4: Validation Loop (Max Attempts with Error Analysis)
# =============================================================================
# Source: .claude/patterns/quality-gates.md lines 49-70
# Use this for iterative validation with automatic fix attempts

MAX_ATTEMPTS = 5

def validation_loop_with_fixes(
    level_name: str,
    validation_command: str,
    error_analyzer: callable,
    max_attempts: int = MAX_ATTEMPTS
) -> dict:
    """
    Run validation with automatic fix attempts on failure.

    This implements the quality gates pattern: validate → fail → analyze → fix → retry.

    Args:
        level_name: Validation level (e.g., "Level 1: Syntax")
        validation_command: Command to run (e.g., "ruff check --fix .")
        error_analyzer: Function to analyze errors and suggest fixes
        max_attempts: Maximum retry attempts (default: 5)

    Returns:
        dict with keys: success (bool), attempts (int), error (str|None)

    Example:
        >>> result = validation_loop_with_fixes(
        ...     "Level 1: Syntax",
        ...     "ruff check --fix src/",
        ...     lambda err: analyze_syntax_error(err, prp_gotchas)
        ... )
        >>> if not result['success']:
        ...     print(f"⚠️ Failed after {result['attempts']} attempts: {result['error']}")
    """
    for attempt in range(1, max_attempts + 1):
        # Run validation
        result = run_validation_command(validation_command)

        if result['success']:
            print(f"✅ {level_name} passed (attempt {attempt})")
            return {'success': True, 'attempts': attempt, 'error': None}

        print(f"❌ {level_name} failed (attempt {attempt}/{max_attempts}): {result['error']}")

        if attempt < max_attempts:
            # Analyze error and attempt fix
            error_analysis = error_analyzer(result['error'])
            if error_analysis['suggested_fix']:
                print(f"Applying fix: {error_analysis['suggested_fix']['description']}")
                apply_fix(error_analysis['suggested_fix'])
            else:
                print("⚠️ No automatic fix available for this error")
        else:
            print(f"⚠️ Max attempts ({max_attempts}) reached - manual intervention required")
            return {'success': False, 'attempts': attempt, 'error': result['error']}

    return {'success': False, 'attempts': max_attempts, 'error': result['error']}


# =============================================================================
# PATTERN 5: Report Coverage Calculation
# =============================================================================
# Source: Feature analysis lines 158-170
# Use this to calculate and display report coverage metrics

def calculate_report_coverage(feature_name: str, total_tasks: int) -> dict:
    """
    Calculate report coverage percentage for a PRP execution.

    This shows how many tasks generated completion reports vs total tasks.
    GOAL: 100% coverage (all tasks documented).

    Args:
        feature_name: Validated feature name
        total_tasks: Total number of tasks in PRP

    Returns:
        dict with coverage metrics

    Example:
        >>> metrics = calculate_report_coverage("user_auth", 25)
        >>> print(f"Reports: {metrics['reports_found']}/{metrics['total_tasks']} ({metrics['coverage_percentage']}%)")
        >>> # Output: "Reports: 25/25 (100%)"

        >>> if metrics['coverage_percentage'] < 100:
        ...     print(f"⚠️ Missing reports for tasks: {metrics['missing_tasks']}")
    """
    from glob import glob

    # Find all TASK*_COMPLETION.md reports
    pattern = f"prps/{feature_name}/execution/TASK*_COMPLETION.md"
    task_reports = glob(pattern)
    reports_found = len(task_reports)

    # Calculate coverage percentage
    coverage_pct = (reports_found / total_tasks) * 100 if total_tasks > 0 else 0

    # Find missing task numbers
    reported_tasks = set()
    for report_path in task_reports:
        # Extract task number from filename (TASK17_COMPLETION.md → 17)
        filename = report_path.split("/")[-1]
        match = re.search(r'TASK(\d+)_', filename)
        if match:
            reported_tasks.add(int(match.group(1)))

    all_tasks = set(range(1, total_tasks + 1))
    missing_tasks = sorted(all_tasks - reported_tasks)

    return {
        "total_tasks": total_tasks,
        "reports_found": reports_found,
        "coverage_percentage": round(coverage_pct, 1),
        "missing_tasks": missing_tasks,
        "status": "✅ COMPLETE" if coverage_pct == 100 else "⚠️ INCOMPLETE"
    }


# =============================================================================
# HELPER CLASSES AND EXCEPTIONS
# =============================================================================

class ValidationError(Exception):
    """
    Raised when validation gates fail.

    Use this for ALL validation failures that should stop execution.
    Error message should be actionable (include paths, troubleshooting, resolution).
    """
    pass


def run_validation_command(command: str) -> dict:
    """Stub: Run a validation command and return result."""
    # Implementation would use subprocess or Bash tool
    import subprocess
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=300)
        return {
            'success': result.returncode == 0,
            'error': result.stderr if result.returncode != 0 else None,
            'output': result.stdout
        }
    except Exception as e:
        return {'success': False, 'error': str(e), 'output': None}


def apply_fix(fix: dict) -> None:
    """Stub: Apply a suggested fix."""
    # Implementation would modify files based on fix suggestion
    pass


# =============================================================================
# USAGE EXAMPLES
# =============================================================================

if __name__ == "__main__":
    # Example 1: Security validation
    try:
        feature = extract_feature_name("prps/INITIAL_user_auth.md", "INITIAL_")
        print(f"✅ Valid feature name: {feature}")
    except ValueError as e:
        print(f"❌ Security check failed: {e}")

    # Example 2: Report existence validation
    try:
        validate_report_exists("user_auth", 17, "COMPLETION")
        print("✅ Task 17 report exists")
    except ValidationError as e:
        print(f"❌ Report validation failed:\n{e}")

    # Example 3: Report coverage calculation
    metrics = calculate_report_coverage("task_management_ui", 25)
    print(f"\n{metrics['status']} Report Coverage:")
    print(f"  Reports: {metrics['reports_found']}/{metrics['total_tasks']} ({metrics['coverage_percentage']}%)")
    if metrics['missing_tasks']:
        print(f"  Missing: Tasks {metrics['missing_tasks']}")
