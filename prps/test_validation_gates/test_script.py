#!/usr/bin/env python3
"""
Test script for validation gates from PRP execution reliability.

This script tests:
1. validate_report_exists() - Core validation gate
2. calculate_report_coverage() - Coverage metrics
3. format_missing_report_error() - Error message quality
"""

import re
import sys
from pathlib import Path
from glob import glob


class ValidationError(Exception):
    """Raised when validation gates fail."""
    pass


def format_missing_report_error(task_number: int, feature_name: str, report_type: str = "COMPLETION") -> str:
    """
    Generate actionable error message for missing report.

    Pattern: Problem → Expected Path → Impact → Troubleshooting → Resolution
    Source: prps/execution_reliability/examples/error_message_pattern.py
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
  This task is INCOMPLETE without documentation.
  - Cannot audit what was implemented
  - Cannot learn from implementation decisions
  - Cannot debug issues in the future
  - Violates PRP execution reliability requirements

TROUBLESHOOTING:
  1. Check if subagent execution completed successfully
     → Review subagent output logs for errors or exceptions

  2. Verify template exists and is accessible
     → Check: {template_path}
     → Ensure template has correct variable placeholders

  3. Check file system permissions
     → Directory: prps/{feature_name}/execution/
     → Ensure write permissions enabled

  4. Review subagent prompt
     → Confirm report generation is marked as CRITICAL
     → Verify exact path specification in prompt

  5. Check for naming issues
     → Standard format: TASK{{number}}_{{TYPE}}.md
     → Wrong: TASK_{task_number}_COMPLETION.md (extra underscore)
     → Wrong: TASK{task_number}_COMPLETE.md (COMPLETE vs COMPLETION)
     → Correct: TASK{task_number}_COMPLETION.md

RESOLUTION OPTIONS:

  Option 1 (RECOMMENDED): Re-run task with explicit report requirement
    → Update subagent prompt to emphasize report is MANDATORY
    → Add validation check immediately after task completion

  Option 2: Manually create report
    → Use template: {template_path}
    → Save to: {report_path}
    → Fill in all required sections

  Option 3: Debug subagent execution
    → Review full subagent output for Write() tool errors
    → Check template variable substitution
    → Verify file creation in correct directory

DO NOT CONTINUE PRP execution until this is resolved.
Report coverage is MANDATORY for execution reliability.
{'='*80}
"""


def validate_report_exists(feature_name: str, task_number: int, report_type: str = "COMPLETION") -> bool:
    """
    Validation gate: Ensure task completion report exists.

    This is THE core validation gate that prevents silent documentation failures.
    Uses EAFP pattern to avoid TOCTOU race condition.

    Pattern: Try to read file (atomic), catch FileNotFoundError
    Source: prps/execution_reliability/examples/validation_gate_pattern.py PATTERN 2

    Args:
        feature_name: Validated feature name (from extract_feature_name)
        task_number: Task number (e.g., 4, 17, 25)
        report_type: Report type (COMPLETION, VALIDATION, etc.)

    Returns:
        True if report exists and has minimum content

    Raises:
        ValidationError: If report is missing or too short (with actionable message)
    """
    report_path = Path(f"prps/{feature_name}/execution/TASK{task_number}_{report_type}.md")

    try:
        # EAFP: Try to read, handle FileNotFoundError
        # This is atomic - no TOCTOU race condition
        content = report_path.read_text()

        # Validate minimum content (prevent empty files)
        if len(content) < 100:
            raise ValidationError(
                f"Task {task_number} report too short: {len(content)} chars (minimum 100)\n"
                f"Path: {report_path}\n\n"
                f"Report may be incomplete or corrupted. Please verify content."
            )

        return True

    except FileNotFoundError:
        # Use actionable error message format
        error_msg = format_missing_report_error(task_number, feature_name, report_type)
        raise ValidationError(error_msg)


def calculate_report_coverage(feature_name: str, total_tasks: int) -> dict:
    """
    Calculate report coverage percentage for PRP execution.

    This shows how many tasks generated completion reports vs total tasks.
    GOAL: 100% coverage (all tasks documented).

    Pattern: Glob for reports, extract task numbers, calculate coverage
    Source: prps/execution_reliability/examples/validation_gate_pattern.py PATTERN 5

    Args:
        feature_name: Validated feature name
        total_tasks: Total number of tasks in PRP

    Returns:
        dict with keys:
            - total_tasks: Total number of tasks
            - reports_found: Number of reports found
            - coverage_percentage: Coverage as percentage (rounded to 1 decimal)
            - missing_tasks: List of task numbers without reports
            - status: "✅ COMPLETE" or "⚠️ INCOMPLETE"
    """
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


def test_validation_gate_missing_report():
    """Test A: Verify validation gate catches missing reports."""
    print("\n" + "="*80)
    print("TEST A: Missing Report Detection")
    print("="*80)

    feature_name = "test_validation_gates"
    task_number = 999  # Non-existent task

    try:
        validate_report_exists(feature_name, task_number)
        print("❌ FAILED: Should have raised ValidationError")
        return False
    except ValidationError as e:
        # Verify error message is actionable
        error_msg = str(e)

        checks = {
            "Has 'VALIDATION GATE FAILED' header": "VALIDATION GATE FAILED" in error_msg,
            "Includes expected path": "TASK999_COMPLETION.md" in error_msg,
            "Has troubleshooting section": "TROUBLESHOOTING:" in error_msg,
            "Has resolution options": "RESOLUTION" in error_msg,
            "Mentions path format": "Standard format:" in error_msg,
        }

        all_passed = all(checks.values())

        for check, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"  {status} {check}")

        if all_passed:
            print("\n✅ TEST A PASSED: Validation gate works correctly")
            return True
        else:
            print("\n❌ TEST A FAILED: Error message missing required elements")
            return False


def test_validation_gate_valid_report():
    """Test B: Verify validation gate passes for valid reports."""
    print("\n" + "="*80)
    print("TEST B: Valid Report Acceptance")
    print("="*80)

    feature_name = "test_validation_gates"
    task_number = 1

    # Create test report
    report_path = Path(f"prps/{feature_name}/execution/TASK{task_number}_COMPLETION.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)

    # Create report with sufficient content (>100 chars)
    report_content = """# Task 1 Implementation Complete

## Task Information
- Task: Create Hello World
- Status: COMPLETE

## Implementation Summary
Created hello_world.py with basic function that prints greeting.

## Files Created
- test_files/hello_world.py

## Validation
All requirements met.
"""
    report_path.write_text(report_content)

    try:
        result = validate_report_exists(feature_name, task_number)
        if result is True:
            print(f"  ✅ Report validated successfully")
            print(f"  ✅ Report size: {len(report_content)} chars (minimum: 100)")
            print("\n✅ TEST B PASSED: Validation gate accepts valid report")
            return True
        else:
            print("❌ TEST B FAILED: Unexpected return value")
            return False
    except ValidationError as e:
        print(f"❌ TEST B FAILED: Unexpected validation error: {e}")
        return False


def test_validation_gate_short_report():
    """Test C: Verify validation gate rejects reports that are too short."""
    print("\n" + "="*80)
    print("TEST C: Short Report Rejection")
    print("="*80)

    feature_name = "test_validation_gates"
    task_number = 2

    # Create report that's too short (<100 chars)
    report_path = Path(f"prps/{feature_name}/execution/TASK{task_number}_COMPLETION.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    short_content = "# Task 2\n\nDone."  # Only ~20 chars
    report_path.write_text(short_content)

    try:
        validate_report_exists(feature_name, task_number)
        print("❌ TEST C FAILED: Should have raised ValidationError for short report")
        return False
    except ValidationError as e:
        error_msg = str(e)
        if "too short" in error_msg and str(len(short_content)) in error_msg:
            print(f"  ✅ Detected short report ({len(short_content)} chars)")
            print(f"  ✅ Error message includes character count")
            print("\n✅ TEST C PASSED: Validation gate rejects short reports")
            return True
        else:
            print(f"❌ TEST C FAILED: Error message doesn't mention short length")
            return False
    finally:
        # Clean up
        report_path.unlink()


def test_coverage_calculation():
    """Test D: Verify coverage calculation is accurate."""
    print("\n" + "="*80)
    print("TEST D: Coverage Calculation Accuracy")
    print("="*80)

    feature_name = "test_validation_gates"
    total_tasks = 3

    # Create reports for tasks 1 and 3 (skip 2)
    for task_num in [1, 3]:
        report_path = Path(f"prps/{feature_name}/execution/TASK{task_num}_COMPLETION.md")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(f"# Task {task_num} Report\n\n" + "x" * 100)

    try:
        metrics = calculate_report_coverage(feature_name, total_tasks)

        checks = {
            "Total tasks correct": metrics['total_tasks'] == 3,
            "Reports found correct": metrics['reports_found'] == 2,
            "Coverage percentage correct": metrics['coverage_percentage'] == 66.7,
            "Missing tasks identified": metrics['missing_tasks'] == [2],
            "Status is INCOMPLETE": metrics['status'] == "⚠️ INCOMPLETE",
        }

        for check, passed in checks.items():
            status = "✅" if passed else "❌"
            value = metrics.get(check.split()[0].lower(), "N/A")
            print(f"  {status} {check}")

        all_passed = all(checks.values())

        if all_passed:
            print(f"\n  Coverage: {metrics['coverage_percentage']}%")
            print(f"  Status: {metrics['status']}")
            print(f"  Missing: {metrics['missing_tasks']}")
            print("\n✅ TEST D PASSED: Coverage calculation is accurate")
            return True
        else:
            print("\n❌ TEST D FAILED: Coverage calculation has errors")
            print(f"  Actual metrics: {metrics}")
            return False
    finally:
        # Clean up
        for task_num in [1, 3]:
            Path(f"prps/{feature_name}/execution/TASK{task_num}_COMPLETION.md").unlink()


def test_coverage_100_percent():
    """Test E: Verify 100% coverage shows COMPLETE status."""
    print("\n" + "="*80)
    print("TEST E: 100% Coverage Detection")
    print("="*80)

    feature_name = "test_validation_gates"
    total_tasks = 3

    # Create reports for all 3 tasks
    for task_num in [1, 2, 3]:
        report_path = Path(f"prps/{feature_name}/execution/TASK{task_num}_COMPLETION.md")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(f"# Task {task_num} Report\n\n" + "x" * 100)

    try:
        metrics = calculate_report_coverage(feature_name, total_tasks)

        checks = {
            "Total tasks correct": metrics['total_tasks'] == 3,
            "Reports found correct": metrics['reports_found'] == 3,
            "Coverage percentage is 100": metrics['coverage_percentage'] == 100.0,
            "No missing tasks": metrics['missing_tasks'] == [],
            "Status is COMPLETE": metrics['status'] == "✅ COMPLETE",
        }

        for check, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"  {status} {check}")

        all_passed = all(checks.values())

        if all_passed:
            print(f"\n  Coverage: {metrics['coverage_percentage']}%")
            print(f"  Status: {metrics['status']}")
            print("\n✅ TEST E PASSED: 100% coverage detected correctly")
            return True
        else:
            print("\n❌ TEST E FAILED: 100% coverage not detected")
            print(f"  Actual metrics: {metrics}")
            return False
    except Exception as e:
        print(f"❌ TEST E FAILED: Exception: {e}")
        return False


def main():
    """Run all validation gate tests."""
    print("\n" + "="*80)
    print("VALIDATION GATE TEST SUITE")
    print("Testing PRP Execution Reliability - Task 8")
    print("="*80)

    tests = [
        ("Missing Report Detection", test_validation_gate_missing_report),
        ("Valid Report Acceptance", test_validation_gate_valid_report),
        ("Short Report Rejection", test_validation_gate_short_report),
        ("Coverage Calculation", test_coverage_calculation),
        ("100% Coverage Detection", test_coverage_100_percent),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n❌ TEST FAILED WITH EXCEPTION: {test_name}")
            print(f"   Error: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {test_name}")

    print(f"\nResults: {passed_count}/{total_count} tests passed ({(passed_count/total_count)*100:.1f}%)")

    if passed_count == total_count:
        print("\n✅ ALL TESTS PASSED - Validation gates are working correctly!")
        return 0
    else:
        print(f"\n⚠️ {total_count - passed_count} TEST(S) FAILED - Review failures above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
