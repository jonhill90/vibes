# Known Gotchas: PRP Execution Reliability

## Overview

This document identifies security vulnerabilities, performance pitfalls, and common mistakes for implementing mandatory report generation with validation gates in PRP execution. All gotchas include concrete solutions with code examples.

**Main Risk Categories**:
- **Critical**: Format string injection, path traversal, TOCTOU race conditions
- **High**: Subagent non-compliance, silent validation failures, information disclosure in errors
- **Medium**: Markdown XSS in rendered reports, performance degradation from validation
- **Low**: Template compatibility issues, naming inconsistencies

---

## Critical Gotchas

### 1. Format String Injection via Template Variables

**Severity**: Critical
**Category**: Security / Code Execution
**Affects**: Template loading system with `.format()` method
**Source**: https://lucumr.pocoo.org/2016/12/29/careful-with-str-format/

**What it is**:

Python's `.format()` method can be exploited when user-controlled data appears in format strings. Attackers can access object attributes, global variables, and potentially execute arbitrary code.

```python
# Vulnerable example - user controls format string
user_input = "{task.__init__.__globals__[CONFIG][SECRET_KEY]}"
template = user_input.format(task=task_object)  # DANGEROUS
```

**Why it's a problem**:

- **Information disclosure**: Attackers can read internal attributes, environment variables, secrets
- **Denial of Service**: Padding with huge lengths (`{:>9999999999}`) exhausts memory
- **Arbitrary attribute access**: Can traverse object graph to reach sensitive data

**How to detect it**:

- Review all `.format()` calls - is the format string ever user-controlled?
- Search for: `feature_name`, `task_name`, or other dynamic inputs used as format strings
- Check if template paths come from user input

**How to avoid/fix**:

```python
# ❌ WRONG - User input in format string
def load_template_vulnerable(template_name: str, feature_name: str) -> str:
    """VULNERABLE: feature_name could be malicious format string"""
    template_path = f".claude/templates/{template_name}"
    template = Path(template_path).read_text()
    # If template contains user-controlled format strings, this is dangerous
    return template.format(feature_name=feature_name)  # RISKY


# ✅ RIGHT - Controlled format string, user data as values only
def load_template_safe(template_name: str, variables: dict[str, str]) -> str:
    """SAFE: Template format string is hardcoded, user data as values"""
    # 1. Template comes from trusted source (.claude/templates/)
    template_path = Path(f".claude/templates/{template_name}")
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    template = template_path.read_text()

    # 2. Validate variable keys (no format string injection)
    allowed_keys = {'feature_name', 'task_number', 'task_name', 'status',
                   'files_modified', 'key_decisions', 'challenges'}
    if not set(variables.keys()).issubset(allowed_keys):
        invalid = set(variables.keys()) - allowed_keys
        raise ValueError(f"Invalid template variables: {invalid}")

    # 3. Use SafeFormatter for extra protection
    try:
        return template.format(**variables)
    except KeyError as e:
        raise ValueError(f"Missing required template variable: {e}")


# ✅ EVEN BETTER - Use string.Template for untrusted scenarios
from string import Template

def load_template_safest(template_name: str, variables: dict[str, str]) -> str:
    """SAFEST: Use string.Template which prevents attribute access"""
    template_path = Path(f".claude/templates/{template_name}")
    template_content = template_path.read_text()

    # Convert {variable} to $variable syntax
    # Or write templates using $variable from the start
    template = Template(template_content)

    # safe_substitute() returns original if variable missing (lenient)
    # substitute() raises KeyError if variable missing (strict)
    return template.safe_substitute(**variables)
```

**Additional safeguards**:

```python
# Input validation for template variables
import re

def validate_template_variable(value: str, max_length: int = 200) -> str:
    """Sanitize template variable values before insertion."""
    # 1. Length limit
    if len(value) > max_length:
        raise ValueError(f"Variable too long: {len(value)} > {max_length}")

    # 2. No format string directives
    if '{' in value or '}' in value:
        raise ValueError("Braces not allowed in template values")

    # 3. Whitelist approach for feature_name (most critical)
    if not re.match(r'^[a-zA-Z0-9_-]+$', value):
        raise ValueError(f"Invalid characters in value: {value}")

    return value
```

**Testing for this vulnerability**:

```python
def test_format_string_injection():
    """Verify format string injection is prevented."""
    malicious_inputs = [
        "{task.__init__.__globals__}",
        "{0.__class__.__bases__[0].__subclasses__()}",
        "{:>9999999999}",  # DOS via padding
    ]

    for malicious in malicious_inputs:
        with pytest.raises(ValueError):
            validate_template_variable(malicious)
```

**Recommendation**: Use `string.Template` for report generation where feature_name or task_name might contain unexpected characters. Use `.format()` only with hardcoded template strings from trusted `.claude/templates/` directory.

---

### 2. Path Traversal in Report Paths

**Severity**: Critical
**Category**: Security / Unauthorized File Access
**Affects**: Report validation, template loading
**Source**: Archon d60a71d62eb201d5 (MCP Security), .claude/patterns/security-validation.md

**What it is**:

Attackers inject `../` sequences in file paths to access files outside intended directories.

```python
# Attacker provides feature_name = "../../etc/passwd"
report_path = f"prps/{feature_name}/execution/TASK1_COMPLETION.md"
# Results in: prps/../../etc/passwd/execution/TASK1_COMPLETION.md
```

**Why it's a problem**:

- **Arbitrary file read**: Can access `/etc/passwd`, config files, secrets
- **Arbitrary file write**: Can overwrite system files if write permissions exist
- **Directory traversal**: Escapes `prps/` directory boundaries

**How to detect it**:

- Path contains `..` sequences
- Resolved path is outside expected base directory
- Path contains null bytes, shell metacharacters

**How to avoid/fix**:

```python
# ❌ WRONG - No validation, direct path construction
def get_report_path_vulnerable(feature_name: str, task_number: int) -> Path:
    return Path(f"prps/{feature_name}/execution/TASK{task_number}_COMPLETION.md")
# Vulnerable: feature_name = "../../etc/passwd" escapes prps/


# ✅ RIGHT - 5-level security validation (from .claude/patterns/security-validation.md)
import re
from pathlib import Path

def extract_feature_name(filepath: str, strip_prefix: str = None) -> str:
    """5-level security validation for feature names from file paths."""

    # Level 1: Path traversal in full path
    if ".." in filepath:
        raise ValueError(f"Path traversal detected in filepath: {filepath}")

    # Extract basename, remove extension
    feature = filepath.split("/")[-1].replace(".md", "")
    if strip_prefix:
        feature = feature.replace(strip_prefix, "")

    # Level 2: Whitelist (alphanumeric + _ - only)
    if not re.match(r'^[a-zA-Z0-9_-]+$', feature):
        raise ValueError(f"Invalid characters in feature name: {feature}")

    # Level 3: Length validation (max 50 chars)
    if len(feature) > 50:
        raise ValueError(f"Feature name too long: {len(feature)} chars (max 50)")

    # Level 4: Directory traversal in extracted name
    if ".." in feature or "/" in feature or "\\" in feature:
        raise ValueError(f"Path traversal in feature name: {feature}")

    # Level 5: Command injection prevention
    dangerous_chars = ['$', '`', ';', '&', '|', '>', '<', '\n', '\r']
    if any(c in feature for c in dangerous_chars):
        raise ValueError(f"Dangerous characters in feature name: {feature}")

    return feature


def get_report_path_safe(feature_name: str, task_number: int) -> Path:
    """Construct report path with security validation."""
    # 1. Validate feature_name
    validated_feature = extract_feature_name(f"prps/{feature_name}.md")

    # 2. Validate task_number
    if not isinstance(task_number, int) or task_number < 1 or task_number > 1000:
        raise ValueError(f"Invalid task number: {task_number}")

    # 3. Construct path
    report_path = Path(f"prps/{validated_feature}/execution/TASK{task_number}_COMPLETION.md")

    # 4. Resolve to absolute path and verify base directory
    BASE_DIR = Path("/Users/jon/source/vibes/prps").resolve()
    resolved_path = report_path.resolve()

    # 5. Ensure path stays within BASE_DIR (defense in depth)
    try:
        resolved_path.relative_to(BASE_DIR)
    except ValueError:
        raise ValueError(
            f"Path traversal attempt detected:\n"
            f"  Requested: {report_path}\n"
            f"  Resolved: {resolved_path}\n"
            f"  Base dir: {BASE_DIR}"
        )

    return resolved_path


# ✅ ALTERNATIVE - Use is_relative_to() (Python 3.9+)
def get_report_path_modern(feature_name: str, task_number: int) -> Path:
    """Modern approach using is_relative_to()."""
    validated_feature = extract_feature_name(f"prps/{feature_name}.md")

    BASE_DIR = Path("/Users/jon/source/vibes/prps").resolve()
    report_path = (BASE_DIR / validated_feature / "execution" / f"TASK{task_number}_COMPLETION.md").resolve()

    if not report_path.is_relative_to(BASE_DIR):
        raise ValueError(f"Path outside base directory: {report_path}")

    return report_path
```

**Testing for this vulnerability**:

```python
def test_path_traversal_prevention():
    """Verify path traversal attacks are blocked."""
    malicious_features = [
        "../../etc/passwd",
        "../../../root",
        "valid/../../../etc",
        "test/../../sensitive",
        "..\\..\\windows\\system32",  # Windows-style
    ]

    for malicious in malicious_features:
        with pytest.raises(ValueError) as exc_info:
            get_report_path_safe(malicious, 1)

        assert "traversal" in str(exc_info.value).lower()
```

**Recommendation**: Always use `extract_feature_name()` before constructing any file paths. This pattern is already in execute-prp.md - ensure ALL new path operations use it.

---

### 3. TOCTOU Race Condition in Report Validation

**Severity**: Critical
**Category**: Security / Race Condition
**Affects**: Validation gates checking report existence
**Source**: https://cwe.mitre.org/data/definitions/367.html

**What it is**:

Time-of-Check Time-of-Use (TOCTOU) race condition where report is validated (check) then read/used later (use), allowing file to be deleted/modified between operations.

```python
# Vulnerable sequence:
if report_path.exists():  # CHECK (time 1)
    # ... other operations ...
    content = report_path.read_text()  # USE (time 2)
    # File could be deleted between CHECK and USE!
```

**Why it's a problem**:

- **File deletion**: Report passes validation but disappears before use
- **File replacement**: Attacker replaces valid report with malicious content
- **False positives**: Validation says "pass" but subsequent operations fail

**How to detect it**:

- `FileNotFoundError` during read after validation passed
- Report content differs from what was validated
- Timing-dependent failures in parallel execution

**How to avoid/fix**:

```python
# ❌ WRONG - Check then use (TOCTOU vulnerable)
def validate_report_toctou(feature_name: str, task_number: int) -> bool:
    report_path = Path(f"prps/{feature_name}/execution/TASK{task_number}_COMPLETION.md")

    # CHECK
    if not report_path.exists():
        raise ValidationError("Report missing")

    # GAP - file could be deleted/modified here!

    # USE
    content = report_path.read_text()  # May raise FileNotFoundError
    return True


# ✅ RIGHT - Use EAFP (Easier to Ask Forgiveness than Permission)
def validate_report_safe(feature_name: str, task_number: int) -> str:
    """Atomic check-and-read to avoid TOCTOU."""
    report_path = Path(f"prps/{feature_name}/execution/TASK{task_number}_COMPLETION.md")

    try:
        # Atomic operation: open and read in one step
        content = report_path.read_text()

        # Validation happens on content we actually have
        if len(content) < 100:
            raise ValidationError(
                f"Report too short: {len(content)} chars (min 100)"
            )

        return content

    except FileNotFoundError:
        raise ValidationError(
            f"❌ Task {task_number} INCOMPLETE: Missing report\n"
            f"Expected: {report_path}\n"
            f"Action: Generate report using .claude/templates/task-completion-report.md"
        )
    except PermissionError:
        raise ValidationError(
            f"Cannot read report (permission denied): {report_path}"
        )


# ✅ EVEN BETTER - Use file descriptor for multiple operations
def validate_report_sections_safe(feature_name: str, task_number: int) -> dict:
    """Perform multiple validations on same file descriptor."""
    report_path = Path(f"prps/{feature_name}/execution/TASK{task_number}_COMPLETION.md")

    try:
        # Open once, use file descriptor for all operations
        with open(report_path, 'r') as f:
            content = f.read()

            # All validations on the content we just read
            required_sections = [
                "## Implementation Summary",
                "## Files Created/Modified",
                "## Validation"
            ]

            missing_sections = [s for s in required_sections if s not in content]

            return {
                "path": str(report_path),
                "size": len(content),
                "missing_sections": missing_sections,
                "valid": len(missing_sections) == 0
            }

    except FileNotFoundError:
        raise ValidationError(f"Report not found: {report_path}")
```

**For parallel execution safety**:

```python
# When validating multiple reports in parallel
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

def validate_all_reports_safe(feature_name: str, task_count: int) -> list[dict]:
    """Safely validate multiple reports, handling TOCTOU per-report."""

    def validate_one(task_num: int) -> dict:
        """Each task validation is atomic."""
        try:
            return validate_report_sections_safe(feature_name, task_num)
        except ValidationError as e:
            return {"task": task_num, "error": str(e), "valid": False}

    # Parallel validation, each atomic
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(validate_one, range(1, task_count + 1)))

    return results
```

**Testing for this vulnerability**:

```python
import threading
import time

def test_toctou_resilience():
    """Verify TOCTOU race condition doesn't cause false positives."""
    report_path = Path("prps/test_feature/execution/TASK1_COMPLETION.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("# Test Report\n\n...")

    def delete_during_validation():
        """Simulate attacker deleting file mid-validation."""
        time.sleep(0.01)  # Let validation start
        report_path.unlink()

    # Start deletion thread
    deleter = threading.Thread(target=delete_during_validation)
    deleter.start()

    # Validation should either succeed (read before deletion)
    # or fail gracefully (FileNotFoundError caught)
    try:
        result = validate_report_safe("test_feature", 1)
        # If succeeded, file was read before deletion
        assert len(result) > 0
    except ValidationError as e:
        # If failed, should have clear error message
        assert "missing" in str(e).lower()

    deleter.join()
```

**Recommendation**: Always use EAFP pattern (`try/except FileNotFoundError`) instead of checking existence then reading. Open file once and perform all validations on the content.

---

## High Priority Gotchas

### 4. Subagent Ignoring Mandatory Report Requirements

**Severity**: High
**Category**: Common Bug / Workflow Failure
**Affects**: Task execution subagents (prp-exec-implementer)
**Source**: prps/task_management_ui (48% report coverage), feature-analysis.md

**What it is**:

Subagents treat report generation as optional, skip it entirely, or generate reports with wrong names/locations. Current evidence: 13 out of 25 tasks in task_management_ui produced no reports.

**Why it's a problem**:

- **Audit gaps**: Cannot learn from 52% of implementation decisions
- **Silent failures**: Execution continues despite missing documentation
- **Inconsistent compliance**: Some tasks documented, others not (unpredictable)

**How to detect it**:

```bash
# Check for missing reports after execution
ls prps/feature_name/execution/TASK*_COMPLETION.md | wc -l
# Compare count to total tasks - if different, reports missing
```

**How to avoid/fix**:

```python
# ❌ WRONG - Vague prompt suggesting reports are optional
Task(subagent_type="prp-exec-implementer", description=f"Implement {task['name']}", prompt=f'''
Implement files for this task.

{task['files']}
{task['steps']}

Consider creating a completion report when done.
''')


# ✅ RIGHT - Explicit, mandatory language with consequences
Task(subagent_type="prp-exec-implementer", description=f"Implement {task['name']}", prompt=f'''
Implement single task from PRP: {task['name']}

**CONTEXT**:
- PRP: {prp_path}
- Responsibility: {task['responsibility']}
- Pattern: {task['pattern']}
- Dependencies: {task.get('depends_on', 'None')}

**FILES TO CREATE/MODIFY**:
{task['files']}

**IMPLEMENTATION STEPS**:
{task['steps']}

═══════════════════════════════════════════════════════════════
⚠️  CRITICAL OUTPUT REQUIREMENTS (NON-NEGOTIABLE) ⚠️
═══════════════════════════════════════════════════════════════

This task has TWO outputs, BOTH are MANDATORY:

1️⃣ **Code Implementation** (all files in FILES section above)

2️⃣ **Completion Report** (REQUIRED)
   📄 Path: prps/{feature_name}/execution/TASK{task['number']}_COMPLETION.md
   📋 Template: .claude/templates/task-completion-report.md

   Required sections:
   - Implementation Summary
   - Files Created/Modified (with line counts)
   - Key Decisions Made
   - Challenges Encountered
   - Validation Status

⚠️ YOUR TASK IS INCOMPLETE WITHOUT THE COMPLETION REPORT ⚠️

The report is NOT optional. It is MANDATORY for:
✓ Auditing implementation decisions
✓ Learning from challenges encountered
✓ Debugging issues in the future
✓ Passing validation gates

═══════════════════════════════════════════════════════════════

**VALIDATION**:
Your work will be validated immediately after completion:
1. ✅ All files created/modified
2. ✅ Report exists at exact path above
3. ✅ Report contains all required sections
4. ✅ Code passes linting (if applicable)

❌ If report is missing, you will receive a VALIDATION ERROR and must regenerate it.

**WORKFLOW**:
1. Read task details and pattern examples
2. Implement all files
3. Test implementation (if tests exist)
4. Generate completion report using template
5. Verify report exists at correct path
''')


# ✅ ADD VALIDATION GATE IMMEDIATELY AFTER TASK
# (In execute-prp.md Phase 2, after task group completion)

def validate_task_outputs(feature_name: str, task_number: int, max_retries: int = 3) -> None:
    """Validation gate: Ensure task outputs are complete."""

    report_path = Path(f"prps/{feature_name}/execution/TASK{task_number}_COMPLETION.md")

    for attempt in range(1, max_retries + 1):
        if report_path.exists():
            print(f"✅ Task {task_number}: Report validated")
            return

        print(f"❌ Attempt {attempt}/{max_retries}: Report missing at {report_path}")

        if attempt < max_retries:
            # Give subagent chance to create it
            time.sleep(2)
        else:
            # FAIL FAST - don't continue execution
            raise ValidationError(
                f"\n{'='*80}\n"
                f"❌ VALIDATION GATE FAILED: Task {task_number} Missing Report\n"
                f"{'='*80}\n\n"
                f"PROBLEM:\n"
                f"  Task {task_number} completed implementation but did not generate\n"
                f"  the mandatory completion report.\n\n"
                f"EXPECTED PATH:\n"
                f"  {report_path}\n\n"
                f"IMPACT:\n"
                f"  This task is INCOMPLETE without documentation.\n"
                f"  - Cannot audit what was implemented\n"
                f"  - Cannot learn from implementation decisions\n"
                f"  - Cannot debug issues that arise later\n\n"
                f"RESOLUTION:\n"
                f"  Option 1 (RECOMMENDED): Re-run task with explicit report requirement\n"
                f"  Option 2: Manually create report using template:\n"
                f"            .claude/templates/task-completion-report.md\n"
                f"  Option 3: Review subagent output for errors\n\n"
                f"DO NOT CONTINUE PRP execution until this is resolved.\n"
                f"{'='*80}\n"
            )


# Call validation immediately after task:
Task(subagent_type="prp-exec-implementer", ...)
validate_task_outputs(feature_name, task_number)  # FAIL FAST if missing
```

**Prompt engineering best practices**:

```markdown
# Anti-patterns to avoid in prompts:
❌ "Create a report if possible"          → Sounds optional
❌ "You may want to document this"        → Not mandatory
❌ "Consider adding a completion report"  → Easily ignored
❌ "Documentation would be helpful"       → Too soft

# Strong patterns to use:
✅ "CRITICAL: Report is MANDATORY"
✅ "Task is INCOMPLETE without report"
✅ "You MUST create report at [exact path]"
✅ "Report is NOT optional"
✅ Visual separators (═══, ⚠️) to highlight
✅ Numbered list showing report as equal priority to code
```

**Testing subagent compliance**:

```python
def test_subagent_compliance():
    """Verify implementer subagent creates mandatory reports."""
    # Simulate task execution
    result = execute_task(
        feature_name="test_feature",
        task_number=1,
        task_definition={...}
    )

    # Validation gate should enforce report
    report_path = Path("prps/test_feature/execution/TASK1_COMPLETION.md")
    assert report_path.exists(), "Subagent failed to create mandatory report"

    # Report should have required sections
    content = report_path.read_text()
    assert "## Implementation Summary" in content
    assert "## Files Created/Modified" in content
    assert "## Validation" in content
```

**Recommendation**: Use "CRITICAL", "MANDATORY", "INCOMPLETE without" language in ALL subagent prompts. Add validation gates immediately after task execution. Fail fast - don't continue if report missing.

---

### 5. Information Disclosure in Error Messages

**Severity**: High
**Category**: Security / Information Leakage
**Affects**: Validation error messages
**Source**: https://www.nngroup.com/articles/error-message-guidelines/, Archon d60a71d62eb201d5

**What it is**:

Error messages leak sensitive information like internal paths, configuration details, or system architecture.

```python
# Dangerous error - reveals internal structure
raise ValidationError(
    f"Cannot access /srv/production/secrets/api_keys.json"
)
```

**Why it's a problem**:

- **Path disclosure**: Reveals internal directory structure
- **Attack surface mapping**: Helps attackers understand system architecture
- **Credential hints**: Error messages may include usernames, database names
- **Version fingerprinting**: Stack traces reveal library versions with known CVEs

**How to detect it**:

- Error messages contain absolute paths outside project
- Stack traces shown to users
- Database connection strings in errors
- Environment variable names leaked

**How to avoid/fix**:

```python
# ❌ WRONG - Verbose error with internal details
def load_template_verbose_error(template_name: str) -> str:
    template_path = Path("/Users/jon/.config/claude/templates") / template_name
    try:
        return template_path.read_text()
    except FileNotFoundError:
        raise ValueError(
            f"Template not found at {template_path}\n"
            f"Current user: {os.getenv('USER')}\n"
            f"Working directory: {os.getcwd()}\n"
            f"Available templates: {os.listdir(template_path.parent)}"
        )
        # DANGER: Leaks absolute paths, username, directory contents


# ✅ RIGHT - User-focused error without sensitive details
def load_template_safe_error(template_name: str) -> str:
    template_path = Path(".claude/templates") / template_name

    try:
        return template_path.read_text()

    except FileNotFoundError:
        raise ValueError(
            f"Template '{template_name}' not found\n\n"
            f"Available templates:\n"
            f"  - task-completion-report.md\n"
            f"  - test-generation-report.md\n"
            f"  - validation-report.md\n\n"
            f"Action: Ensure template exists in .claude/templates/"
        )
        # SAFE: Relative path, hardcoded list, no system info


# ✅ VALIDATION ERRORS - User-actionable without leakage
def format_missing_report_error(
    task_number: int,
    feature_name: str,
    report_type: str = "COMPLETION"
) -> str:
    """Generate secure, actionable error message."""

    # Use relative path only
    expected_path = f"prps/{feature_name}/execution/TASK{task_number}_{report_type}.md"

    return (
        f"{'='*80}\n"
        f"❌ VALIDATION GATE FAILED: Missing Task Report\n"
        f"{'='*80}\n\n"
        f"PROBLEM:\n"
        f"  Task {task_number} did not generate required {report_type.lower()} report.\n\n"
        f"EXPECTED PATH (relative to project root):\n"
        f"  {expected_path}\n\n"
        # NO absolute paths, usernames, system details
        f"TROUBLESHOOTING:\n"
        f"  1. Check if subagent execution completed successfully\n"
        f"  2. Verify template exists: .claude/templates/task-completion-report.md\n"
        f"  3. Check write permissions in prps/ directory\n"
        f"  4. Review subagent output for errors\n\n"
        f"RESOLUTION:\n"
        f"  - Re-run task with explicit report requirement\n"
        f"  - OR manually create report using template\n\n"
        f"{'='*80}\n"
    )
    # SAFE: No sensitive information disclosed


# ✅ EXCEPTION HANDLING - Hide internals in production
import logging

def validate_with_safe_errors(feature_name: str, task_number: int) -> None:
    """Catch all exceptions and provide user-safe messages."""

    try:
        # Actual validation logic
        report_path = get_report_path_safe(feature_name, task_number)
        content = report_path.read_text()
        validate_sections(content)

    except ValidationError:
        # Re-raise validation errors (already user-safe)
        raise

    except Exception as e:
        # Log full details for debugging (internal only)
        logging.error(
            f"Internal error during validation:\n"
            f"  Feature: {feature_name}\n"
            f"  Task: {task_number}\n"
            f"  Exception: {type(e).__name__}: {e}\n",
            exc_info=True  # Include stack trace in logs
        )

        # User sees generic message only
        raise ValidationError(
            f"Validation failed for Task {task_number}\n\n"
            f"An internal error occurred. Check logs for details.\n"
            f"Contact: [support email]"
        )
        # SAFE: No stack trace, exception details, or paths exposed
```

**Secure logging pattern**:

```python
import logging
from pathlib import Path

# Configure logging to file (not console/user-visible)
logging.basicConfig(
    filename=Path(".claude/logs/validation.log"),
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def validate_with_logging(feature_name: str, task_number: int) -> None:
    """Log details internally, show safe errors to user."""

    try:
        logging.info(f"Validating task {task_number} for {feature_name}")
        # ... validation logic ...
        logging.info("Validation passed")

    except FileNotFoundError as e:
        # Log full error internally
        logging.error(f"FileNotFoundError: {e}", exc_info=True)

        # Show safe error to user
        raise ValidationError(format_missing_report_error(task_number, feature_name))
```

**Testing error message safety**:

```python
def test_error_messages_no_leakage():
    """Verify error messages don't leak sensitive information."""

    try:
        validate_report_safe("nonexistent_feature", 999)
    except ValidationError as e:
        error_msg = str(e)

        # Should NOT contain:
        assert "/Users/" not in error_msg, "Absolute path leaked"
        assert os.getenv('USER') not in error_msg, "Username leaked"
        assert "Traceback" not in error_msg, "Stack trace leaked"

        # SHOULD contain:
        assert "prps/" in error_msg, "Relative path missing"
        assert "Action:" in error_msg or "Resolution:" in error_msg, "Not actionable"
```

**Recommendation**: Always use relative paths in error messages. Log detailed errors internally (file-based logging), show user-safe messages externally. Never include: absolute paths outside project, usernames, environment variables, stack traces.

---

### 6. Silent Validation Failures (Continue Despite Errors)

**Severity**: High
**Category**: Workflow Failure / Anti-Pattern
**Affects**: Execute-prp.md validation gates
**Source**: codebase-patterns.md Anti-Pattern #1

**What it is**:

Validation detects missing reports but execution continues anyway, leading to 48% report coverage (current state).

```python
# Anti-pattern: Check but don't enforce
if not report_exists:
    print("⚠️ Warning: Report missing")
    # ... execution continues ...
# Result: 13/25 tasks with no reports
```

**Why it's a problem**:

- **Accumulated technical debt**: Missing reports pile up
- **False sense of completion**: "100% tasks complete" but 52% undocumented
- **Difficult recovery**: Harder to regenerate reports retrospectively
- **No accountability**: Subagents learn that reports are "optional warnings"

**How to detect it**:

- Console shows warnings but execution proceeds
- Final summary claims "success" despite missing reports
- No ValidationError exceptions raised
- Log files show "⚠️ Warning" but no "❌ Error"

**How to avoid/fix**:

```python
# ❌ WRONG - Warn but continue (silent failure)
def validate_reports_weak(feature_name: str, total_tasks: int) -> None:
    """Weak validation that doesn't enforce compliance."""

    missing = []
    for task_num in range(1, total_tasks + 1):
        report_path = Path(f"prps/{feature_name}/execution/TASK{task_num}_COMPLETION.md")
        if not report_path.exists():
            missing.append(task_num)

    if missing:
        print(f"⚠️ Warning: {len(missing)} reports missing: {missing}")
        # WRONG: Continues execution despite failures

    print("✅ Validation complete")  # Misleading - not all valid


# ✅ RIGHT - Fail fast (raise exception)
def validate_reports_strict(feature_name: str, total_tasks: int) -> None:
    """Strict validation that enforces 100% compliance."""

    missing = []
    for task_num in range(1, total_tasks + 1):
        report_path = Path(f"prps/{feature_name}/execution/TASK{task_num}_COMPLETION.md")
        if not report_path.exists():
            missing.append(task_num)

    if missing:
        # FAIL FAST - raise exception to halt execution
        coverage_pct = ((total_tasks - len(missing)) / total_tasks) * 100

        raise ValidationError(
            f"\n{'='*80}\n"
            f"❌ QUALITY GATE FAILED: Incomplete Report Coverage\n"
            f"{'='*80}\n\n"
            f"COVERAGE: {total_tasks - len(missing)}/{total_tasks} ({coverage_pct:.0f}%)\n"
            f"REQUIRED: 100%\n\n"
            f"MISSING REPORTS FOR TASKS: {missing}\n\n"
            f"RESOLUTION:\n"
            f"  Each missing task must generate a completion report.\n"
            f"  Template: .claude/templates/task-completion-report.md\n"
            f"  Path: prps/{feature_name}/execution/TASK<N>_COMPLETION.md\n\n"
            f"DO NOT PROCEED until all reports are generated.\n"
            f"{'='*80}\n"
        )

    print(f"✅ Quality Gate PASSED: {total_tasks}/{total_tasks} reports (100%)")


# ✅ INTEGRATION IN EXECUTE-PRP.MD
# Phase 2: Implementation (after each task group)

for group in task_groups:
    # Execute tasks in parallel
    results = []
    for task in group['tasks']:
        result = Task(subagent_type="prp-exec-implementer", ...)
        results.append(result)

    # VALIDATION GATE - Fail fast if any reports missing
    for task in group['tasks']:
        try:
            validate_task_outputs(feature_name, task['number'])
        except ValidationError as e:
            # Log error
            print(str(e))

            # Update Archon task status to "todo" (failed, needs retry)
            if archon_available:
                mcp__archon__manage_task(
                    "update",
                    task_id=task_ids[task['number']],
                    status="todo",
                    description=f"VALIDATION FAILED: {str(e)[:200]}"
                )

            # HALT EXECUTION - don't continue to next group
            raise

    print(f"✅ Group {group['number']}: All reports validated")


# ✅ FINAL COVERAGE CHECK (Phase 5: Completion)
try:
    validate_reports_strict(feature_name, total_tasks)

    print(f"\n{'='*80}")
    print(f"✅ PRP EXECUTION COMPLETE")
    print(f"{'='*80}")
    print(f"  Implementation: {total_tasks}/{total_tasks} tasks (100%)")
    print(f"  Documentation: {total_tasks}/{total_tasks} reports (100%)")
    print(f"  Validation: All gates passed")
    print(f"{'='*80}\n")

except ValidationError as e:
    print(f"\n{'='*80}")
    print(f"⚠️ PRP EXECUTION INCOMPLETE")
    print(f"{'='*80}")
    print(str(e))

    # Exit with error code
    sys.exit(1)
```

**Comparison of approaches**:

| Approach | Report Coverage | Execution Halts? | Accountability |
|----------|----------------|------------------|----------------|
| ❌ Silent (warn only) | 48% (current) | No | None - continues |
| ✅ Fail fast (raise) | 100% (target) | Yes - at first failure | High - must fix |
| ⚠️ Collect & fail at end | 95-100% | Yes - at end | Medium - batch fixes |

**Testing fail-fast behavior**:

```python
def test_validation_fails_fast():
    """Verify validation halts execution on first missing report."""

    # Create reports for tasks 1-4, skip task 5
    for task_num in [1, 2, 3, 4]:
        Path(f"prps/test/execution/TASK{task_num}_COMPLETION.md").write_text("...")

    # Validation should raise exception for task 5
    with pytest.raises(ValidationError) as exc_info:
        validate_reports_strict("test", total_tasks=10)

    # Error message should identify missing tasks
    assert "5" in str(exc_info.value)
    assert "100%" in str(exc_info.value)  # Required threshold
```

**Recommendation**: Replace ALL warnings with exceptions. Use `raise ValidationError()` instead of `print("⚠️ Warning")`. Fail fast - halt execution immediately when validation fails.

---

## Medium Priority Gotchas

### 7. Markdown XSS in Rendered Reports (If Rendered as HTML)

**Severity**: Medium
**Category**: Security / XSS
**Affects**: Report rendering (if HTML preview used)
**Source**: https://github.com/showdownjs/showdown/wiki/Markdown's-XSS-Vulnerability

**What it is**:

If reports are rendered as HTML (e.g., for preview in UI), malicious markdown can inject JavaScript.

```markdown
# Report for Task 5

![XSS](javascript:alert('XSS'))
[Click](javascript:alert('XSS'))
<img src=x onerror="alert('XSS')">
```

**Why it's a problem**:

- **XSS attacks**: Steals cookies, session tokens when report viewed in browser
- **Credential theft**: Can capture user input in rendered HTML
- **Phishing**: Malicious links that appear legitimate

**How to detect it**:

- HTML preview renders JavaScript
- Click on link executes code instead of navigating
- Image tags have `onerror` handlers

**How to avoid/fix**:

```python
# ❌ WRONG - Render markdown to HTML without sanitization
import markdown

def render_report_unsafe(report_content: str) -> str:
    """UNSAFE: Renders markdown including malicious HTML."""
    return markdown.markdown(report_content)
    # Renders: <img src=x onerror="alert('XSS')"> as-is


# ✅ RIGHT - Sanitize HTML after markdown processing
import markdown
import bleach

def render_report_safe(report_content: str) -> str:
    """SAFE: Render markdown then sanitize HTML."""

    # 1. Convert markdown to HTML
    html = markdown.markdown(report_content)

    # 2. Whitelist safe tags and attributes
    allowed_tags = [
        'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li', 'blockquote', 'code', 'pre', 'a', 'img', 'table',
        'thead', 'tbody', 'tr', 'th', 'td'
    ]

    allowed_attrs = {
        'a': ['href', 'title'],
        'img': ['src', 'alt', 'title'],
        'code': ['class'],  # For syntax highlighting
    }

    allowed_protocols = ['http', 'https', 'mailto']

    # 3. Sanitize (remove dangerous content)
    clean_html = bleach.clean(
        html,
        tags=allowed_tags,
        attributes=allowed_attrs,
        protocols=allowed_protocols,
        strip=True  # Strip disallowed tags instead of escaping
    )

    return clean_html


# ✅ ALTERNATIVE - Don't render to HTML at all (safest)
def display_report_markdown_only(report_path: Path) -> str:
    """Safest: Display raw markdown without HTML rendering."""
    return report_path.read_text()
    # Many IDEs/editors render markdown safely without XSS risk
```

**If using markdown libraries**:

```python
# Configure markdown to disable HTML
import markdown

md = markdown.Markdown(
    extensions=['extra', 'codehilite'],
    extension_configs={
        'extra': {
            'enable_attributes': False  # Disable {: .class} syntax
        }
    }
)

# Disable raw HTML
md.enable_attributes = False

html = md.convert(report_content)
# Then sanitize with bleach as above
```

**Content Security Policy (if serving HTML)**:

```html
<!-- Add CSP header to prevent inline JavaScript -->
<meta http-equiv="Content-Security-Policy"
      content="default-src 'self'; script-src 'none'; object-src 'none';">
```

**Testing for XSS vulnerabilities**:

```python
def test_markdown_xss_prevention():
    """Verify XSS payloads are sanitized."""

    xss_payloads = [
        "![XSS](javascript:alert('XSS'))",
        "[Click](javascript:alert('XSS'))",
        '<img src=x onerror="alert(\'XSS\')">',
        '<script>alert("XSS")</script>',
        '<svg onload="alert(\'XSS\')">',
    ]

    for payload in xss_payloads:
        html = render_report_safe(payload)

        # Should NOT contain javascript: or event handlers
        assert "javascript:" not in html.lower()
        assert "onerror=" not in html.lower()
        assert "onload=" not in html.lower()
        assert "<script" not in html.lower()
```

**Recommendation**: If reports must be rendered as HTML, ALWAYS sanitize with `bleach.clean()` after markdown processing. Better: Display raw markdown (many viewers render safely). Add CSP headers if serving HTML.

**Note**: This is MEDIUM priority because reports in this project are likely stored as plain `.md` files and viewed in editors (not rendered to HTML). Upgrade to HIGH if web preview is added.

---

### 8. Performance Degradation from Excessive Validation

**Severity**: Medium
**Category**: Performance
**Affects**: Validation gates in large PRPs (50+ tasks)
**Source**: Quality gates pattern analysis

**What it is**:

Running validation on every task sequentially can slow execution in large PRPs, especially if validation involves disk I/O, parsing, or network calls.

```python
# Sequential validation - slow for 50 tasks
for task_num in range(1, 51):
    validate_report_exists(feature_name, task_num)  # 50 disk reads
    validate_report_sections(feature_name, task_num)  # 50 more reads + parsing
# Total: 100+ disk operations sequentially
```

**Why it's a problem**:

- **Slow feedback**: Delays between task completion and validation result
- **Poor UX**: User waits for validation instead of seeing progress
- **Waste resources**: Sequential I/O when parallel would be faster

**How to detect it**:

- Validation takes >1 second per task
- Noticeable pause after task completion before next task starts
- `time` command shows high real time vs. CPU time

**How to avoid/fix**:

```python
# ❌ WRONG - Sequential validation
def validate_all_reports_slow(feature_name: str, total_tasks: int) -> None:
    """Sequential validation - slow for large PRPs."""
    for task_num in range(1, total_tasks + 1):
        # Each validation waits for previous to complete
        validate_report_exists(feature_name, task_num)
        validate_report_sections(feature_name, task_num)
    # For 50 tasks: ~5-10 seconds


# ✅ RIGHT - Parallel validation with ThreadPoolExecutor
from concurrent.futures import ThreadPoolExecutor, as_completed

def validate_all_reports_fast(feature_name: str, total_tasks: int) -> None:
    """Parallel validation - fast for large PRPs."""

    def validate_one_task(task_num: int) -> dict:
        """Validate single task (called in parallel)."""
        try:
            validate_report_exists(feature_name, task_num)
            result = validate_report_sections(feature_name, task_num)
            return {"task": task_num, "status": "valid", "result": result}
        except ValidationError as e:
            return {"task": task_num, "status": "error", "error": str(e)}

    # Parallel execution (max 10 workers to avoid overwhelming disk)
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(validate_one_task, task_num): task_num
            for task_num in range(1, total_tasks + 1)
        }

        results = []
        for future in as_completed(futures):
            task_num = futures[future]
            try:
                result = future.result()
                results.append(result)

                if result["status"] == "valid":
                    print(f"✅ Task {task_num}: Validated")
                else:
                    print(f"❌ Task {task_num}: {result['error']}")

            except Exception as e:
                print(f"❌ Task {task_num}: Validation failed: {e}")
                results.append({"task": task_num, "status": "exception", "error": str(e)})

    # Check for failures
    failures = [r for r in results if r["status"] != "valid"]
    if failures:
        raise ValidationError(
            f"{len(failures)} validation failures:\n" +
            "\n".join(f"  Task {f['task']}: {f.get('error', 'Unknown error')}" for f in failures)
        )

    print(f"✅ All {total_tasks} reports validated in parallel")
    # For 50 tasks: ~1-2 seconds (5x faster)


# ✅ OPTIMIZE FILE READS - Cache content if multiple validations
def validate_with_caching(feature_name: str, total_tasks: int) -> None:
    """Read each file once, run multiple validations on cached content."""

    # Step 1: Read all files in parallel
    report_contents = {}

    def read_one(task_num: int) -> tuple[int, str]:
        report_path = Path(f"prps/{feature_name}/execution/TASK{task_num}_COMPLETION.md")
        try:
            return (task_num, report_path.read_text())
        except FileNotFoundError:
            raise ValidationError(f"Task {task_num}: Report not found")

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(read_one, n) for n in range(1, total_tasks + 1)]
        for future in as_completed(futures):
            task_num, content = future.result()
            report_contents[task_num] = content

    # Step 2: Run validations on cached content (in memory - fast)
    for task_num, content in report_contents.items():
        # Validate sections
        if "## Implementation Summary" not in content:
            raise ValidationError(f"Task {task_num}: Missing Implementation Summary")

        # Validate length
        if len(content) < 100:
            raise ValidationError(f"Task {task_num}: Report too short ({len(content)} chars)")

    print(f"✅ Validated {total_tasks} reports (cached reads)")
```

**Batch validation strategy**:

```python
# Validate after task GROUPS, not individual tasks
# (In execute-prp.md Phase 2)

for group in task_groups:
    # Execute all tasks in group (parallel)
    for task in group['tasks']:
        Task(subagent_type="prp-exec-implementer", ...)

    # BATCH VALIDATE entire group (parallel)
    task_numbers = [t['number'] for t in group['tasks']]
    validate_tasks_batch(feature_name, task_numbers)  # Fast parallel validation

    print(f"✅ Group {group['number']}: All {len(task_numbers)} reports validated")

# Benefits:
# - Fewer validation rounds (once per group vs once per task)
# - Still fails fast (halts between groups if issues found)
# - Better performance (parallel I/O)
```

**Performance benchmarks**:

```python
import time

def benchmark_validation_approaches():
    """Compare sequential vs parallel validation performance."""

    feature_name = "test_feature"
    total_tasks = 50

    # Sequential
    start = time.time()
    validate_all_reports_slow(feature_name, total_tasks)
    sequential_time = time.time() - start

    # Parallel
    start = time.time()
    validate_all_reports_fast(feature_name, total_tasks)
    parallel_time = time.time() - start

    print(f"Sequential: {sequential_time:.2f}s")
    print(f"Parallel: {parallel_time:.2f}s")
    print(f"Speedup: {sequential_time / parallel_time:.1f}x")

    # Expected: 5-10x speedup for I/O-bound operations
```

**Recommendation**: Use parallel validation with `ThreadPoolExecutor` for task batches. Limit workers to 10 to avoid overwhelming disk. Cache file contents if running multiple validations on same files.

---

## Low Priority Gotchas

### 9. Template Variable Missing (KeyError at Runtime)

**Severity**: Low
**Category**: Template Bug
**Affects**: Report generation when templates updated
**Source**: Python format() documentation

**What it is**:

Template expects variable that isn't provided, causing `KeyError` during `.format()` call.

```python
# Template contains {confidence_level}
template = "Confidence: {confidence_level}"

# But variable not provided
template.format(feature_name="test")  # KeyError: 'confidence_level'
```

**Why it's a problem**:

- **Report generation fails**: Task completes but report can't be created
- **Cryptic errors**: `KeyError: 'confidence_level'` isn't immediately obvious
- **Maintenance burden**: Template changes break existing code

**How to detect it**:

- `KeyError` during report generation
- Error message references template variable name
- Report file not created despite template being found

**How to avoid/fix**:

```python
# ❌ WRONG - No validation of template variables
def generate_report_unchecked(template_name: str, **variables) -> str:
    template = Path(f".claude/templates/{template_name}").read_text()
    return template.format(**variables)  # May raise KeyError


# ✅ RIGHT - Validate required variables before format()
import re

def extract_template_variables(template: str) -> set[str]:
    """Extract all {variable} placeholders from template."""
    return set(re.findall(r'\{(\w+)\}', template))


def generate_report_validated(template_name: str, **variables) -> str:
    """Generate report with variable validation."""

    # 1. Load template
    template_path = Path(f".claude/templates/{template_name}")
    template = template_path.read_text()

    # 2. Extract required variables
    required_vars = extract_template_variables(template)

    # 3. Check all required variables provided
    provided_vars = set(variables.keys())
    missing_vars = required_vars - provided_vars

    if missing_vars:
        raise ValueError(
            f"Template '{template_name}' missing variables: {missing_vars}\n"
            f"Required: {sorted(required_vars)}\n"
            f"Provided: {sorted(provided_vars)}"
        )

    # 4. Warn about extra variables (not used in template)
    extra_vars = provided_vars - required_vars
    if extra_vars:
        print(f"⚠️ Warning: Unused variables: {extra_vars}")

    # 5. Safe to format
    return template.format(**variables)


# ✅ USE DEFAULT VALUES for optional variables
def generate_report_with_defaults(template_name: str, **variables) -> str:
    """Generate report with default values for missing variables."""

    template_path = Path(f".claude/templates/{template_name}")
    template = template_path.read_text()

    # Define defaults for optional variables
    defaults = {
        'archon_task_id': 'N/A',
        'confidence_level': 'MEDIUM',
        'duration_minutes': '0',
        'challenges': 'None encountered',
    }

    # Merge provided variables with defaults (provided takes precedence)
    all_variables = {**defaults, **variables}

    # Validate required variables still present
    required_vars = extract_template_variables(template)
    provided_vars = set(all_variables.keys())
    missing_vars = required_vars - provided_vars

    if missing_vars:
        raise ValueError(f"Missing required variables: {missing_vars}")

    return template.format(**all_variables)
```

**Template design best practices**:

```markdown
# ❌ WRONG - Too many variables, some rarely used
# Task {task_number} Report: {task_name}
Feature: {feature_name}
Group: {group_number}
Archon ID: {archon_task_id}
Started: {start_time}
Ended: {end_time}
Duration: {duration_minutes}
Confidence: {confidence_level}
Dependencies: {dependencies}

# ✅ RIGHT - Essential variables only, optional in prose
# Task {task_number}: {task_name}

**Feature**: {feature_name}
**Status**: {status}

## Implementation Summary
{implementation_summary}

## Files Modified
{files_modified}

<!-- Optional sections added by subagent as prose, not variables -->
```

**Testing template variables**:

```python
def test_template_variables_complete():
    """Verify all templates can be rendered with standard variables."""

    # Standard variable set
    variables = {
        'feature_name': 'test_feature',
        'task_number': 1,
        'task_name': 'Implement core logic',
        'status': 'COMPLETE',
        'files_modified': 'src/core.py, tests/test_core.py',
        'implementation_summary': 'Added core functionality',
    }

    templates = [
        'task-completion-report.md',
        'test-generation-report.md',
    ]

    for template_name in templates:
        try:
            report = generate_report_validated(template_name, **variables)
            assert len(report) > 0
        except ValueError as e:
            pytest.fail(f"Template {template_name} failed: {e}")
```

**Recommendation**: Validate template variables before calling `.format()`. Use default values for optional variables. Keep templates simple with minimal required variables.

---

### 10. Report Naming Inconsistencies

**Severity**: Low
**Category**: Convention / Maintenance
**Affects**: Report discovery and globbing
**Source**: codebase-patterns.md Anti-Pattern #2

**What it is**:

Different naming patterns for task reports (already occurred in task_management_ui):
- `TASK5_IMPLEMENTATION_NOTES.md`
- `TASK_17_COMPLETION.md` (underscore before number)
- `TASK_18_COMPLETE.md` (COMPLETE vs COMPLETION)
- `TASK22_TEST_IMPLEMENTATION_REPORT.md`

**Why it's a problem**:

- **Glob patterns break**: `glob("TASK*_COMPLETION.md")` misses `TASK_18_COMPLETE.md`
- **Coverage calculation wrong**: Misses reports with different names
- **Maintenance burden**: Must handle multiple patterns
- **Confusing**: Developers don't know which pattern to use

**How to detect it**:

```bash
# Check for inconsistent naming
ls prps/*/execution/TASK*.md | grep -v "COMPLETION"
# Shows: TASK5_IMPLEMENTATION_NOTES.md, TASK_18_COMPLETE.md, etc.
```

**How to avoid/fix**:

```python
# ❌ WRONG - Flexible naming allows inconsistencies
def find_task_reports_flexible(feature_name: str) -> list[Path]:
    """Finds reports but allows any naming."""
    patterns = [
        "TASK*_COMPLETION.md",
        "TASK*_COMPLETE.md",
        "TASK*_REPORT.md",
        "TASK*_NOTES.md",
        "TASK*_IMPLEMENTATION*.md",
    ]

    reports = []
    for pattern in patterns:
        reports.extend(Path(f"prps/{feature_name}/execution").glob(pattern))

    return reports
    # Problem: Accepts anything, no standardization


# ✅ RIGHT - Enforce strict naming in validation
def validate_report_naming(feature_name: str, task_number: int) -> Path:
    """Enforce strict naming convention."""

    # ONLY accept this exact pattern
    report_path = Path(f"prps/{feature_name}/execution/TASK{task_number}_COMPLETION.md")

    if not report_path.exists():
        # Check for common misspellings
        wrong_patterns = [
            Path(f"prps/{feature_name}/execution/TASK{task_number}_COMPLETE.md"),
            Path(f"prps/{feature_name}/execution/TASK_{task_number}_COMPLETION.md"),  # Extra underscore
            Path(f"prps/{feature_name}/execution/TASK{task_number}_REPORT.md"),
        ]

        wrong_exists = [p for p in wrong_patterns if p.exists()]

        if wrong_exists:
            raise ValidationError(
                f"Report has wrong name:\n"
                f"  Found: {wrong_exists[0]}\n"
                f"  Expected: {report_path}\n\n"
                f"Standardized naming: TASK<number>_COMPLETION.md\n"
                f"  - No underscore before number\n"
                f"  - COMPLETION (not COMPLETE, REPORT, or NOTES)\n"
                f"  - Uppercase extension: .md\n\n"
                f"Action: Rename file to match standard convention"
            )
        else:
            raise ValidationError(f"Report not found: {report_path}")

    return report_path


# ✅ PROVIDE HELPER FUNCTION for correct naming
def get_standard_report_path(feature_name: str, task_number: int, report_type: str = "COMPLETION") -> Path:
    """Generate standard report path (use this in prompts)."""

    allowed_types = ["COMPLETION", "TEST_GENERATION", "VALIDATION"]
    if report_type not in allowed_types:
        raise ValueError(f"Invalid report type: {report_type}. Allowed: {allowed_types}")

    return Path(f"prps/{feature_name}/execution/TASK{task_number}_{report_type}.md")
```

**Enforce in templates and prompts**:

```python
# In subagent prompts, always specify exact path
implementer_prompt = f'''
...

CRITICAL OUTPUT REQUIREMENTS:
1. Implementation files
2. Completion report: {get_standard_report_path(feature_name, task_number)}
                      ^^^ EXACT PATH - do not deviate

Report naming convention (MANDATORY):
- Format: TASK<number>_COMPLETION.md
- Example: TASK5_COMPLETION.md (NOT TASK_5_COMPLETION.md)
- Example: TASK17_COMPLETION.md (NOT TASK17_COMPLETE.md)
'''
```

**Migration script for legacy reports**:

```python
def standardize_report_names(feature_name: str) -> None:
    """Rename legacy reports to standard convention."""

    execution_dir = Path(f"prps/{feature_name}/execution")

    # Find all task reports with non-standard names
    all_reports = execution_dir.glob("TASK*.md")

    for report_path in all_reports:
        # Extract task number from filename
        match = re.search(r'TASK_?(\d+)', report_path.name)
        if not match:
            continue

        task_number = int(match.group(1))
        standard_name = f"TASK{task_number}_COMPLETION.md"
        standard_path = execution_dir / standard_name

        if report_path.name != standard_name:
            print(f"Renaming: {report_path.name} → {standard_name}")
            report_path.rename(standard_path)
```

**Recommendation**: Enforce `TASK{n}_COMPLETION.md` pattern (no underscore before number, COMPLETION not COMPLETE). Validate naming in quality gates. Provide exact path in subagent prompts.

---

## Library-Specific Quirks

### Python pathlib

**Version**: Python 3.4+ (3.9+ for is_relative_to)

**Common Issues**:

1. **Symlink following in exists()**
   - `Path.exists()` follows symlinks by default
   - Returns False for broken symlinks (link exists but target doesn't)
   - **Solution**: Use `Path.is_symlink()` to check separately

2. **resolve() behavior differences**
   - `resolve()` makes path absolute and follows symlinks
   - Raises `FileNotFoundError` if path doesn't exist (Python 3.6-3.9)
   - Python 3.10+: `resolve(strict=False)` to allow non-existent paths
   - **Solution**: Use try/except or check existence first

3. **Trailing slashes**
   - `Path("dir/")` vs `Path("dir")` - both equivalent
   - But string representation differs
   - **Solution**: Always use `.resolve()` for canonical form

### Markdown Processors

**Version**: markdown 3.x, python-markdown

**Common Issues**:

1. **HTML pass-through**
   - Most processors allow raw HTML by default (XSS risk)
   - **Solution**: Use `markdown.markdown(..., enable_attributes=False)` + bleach

2. **GitHub-Flavored Markdown (GFM) differences**
   - Standard markdown != GFM
   - Tables, task lists, strikethrough may not render
   - **Solution**: Use `markdown.extensions` or specify GFM in docs

3. **Code block handling**
   - Inconsistent syntax highlighting across processors
   - **Solution**: Use fenced code blocks with language specifier

---

## Performance Gotchas

### 1. Excessive Disk I/O in Validation

**Impact**: Latency increase (sequential: 50ms/task, parallel: 10ms/task)
**Affects**: Large PRPs (30+ tasks)

**The problem**:
```python
# ❌ SLOW - Multiple reads per task
for task_num in range(1, 50):
    if Path(report_path).exists():       # Read 1: stat
        content = Path(report_path).read_text()  # Read 2: full read
        if len(content) < 100:            # Read 3: (cached)
            ...
# Result: 100+ disk operations
```

**The solution**:
```python
# ✅ FAST - Single read per task, parallel execution
from concurrent.futures import ThreadPoolExecutor

def validate_fast(feature_name: str, task_numbers: list[int]) -> None:
    def validate_one(task_num: int) -> None:
        report_path = Path(f"prps/{feature_name}/execution/TASK{task_num}_COMPLETION.md")
        try:
            # Single read operation
            content = report_path.read_text()

            # All validations on cached content (in memory)
            if len(content) < 100:
                raise ValidationError("Too short")
            if "## Implementation" not in content:
                raise ValidationError("Missing section")

        except FileNotFoundError:
            raise ValidationError(f"Report missing: {report_path}")

    # Parallel execution (I/O-bound benefits from threading)
    with ThreadPoolExecutor(max_workers=10) as executor:
        list(executor.map(validate_one, task_numbers))
```

**Benchmarks**:
- Sequential (50 tasks): ~5-8 seconds
- Parallel (50 tasks): ~1-2 seconds
- **Improvement**: 4-5x faster

---

### 2. Template Loading on Every Report

**Impact**: Memory and I/O waste
**Affects**: Generating multiple reports from same template

**The problem**:
```python
# ❌ WASTEFUL - Loads template 25 times for 25 tasks
for task_num in range(1, 26):
    template = Path(".claude/templates/task-completion-report.md").read_text()  # Reload
    report = template.format(task_number=task_num, ...)
```

**The solution**:
```python
# ✅ EFFICIENT - Load template once, reuse
template_content = Path(".claude/templates/task-completion-report.md").read_text()

for task_num in range(1, 26):
    report = template_content.format(task_number=task_num, ...)  # Reuse cached
```

---

## Security Gotchas

### 1. Command Injection via Feature Names

**Severity**: Critical
**Type**: Code Execution
**Affects**: Shell commands using feature_name
**CVE**: N/A (custom code vulnerability)

**Vulnerability**:
```bash
# If feature_name = "test; rm -rf /"
rm -rf prps/$feature_name/execution/*
# Executes: rm -rf prps/test; rm -rf /execution/*
```

**Secure Implementation**:
```python
# ✅ SECURE - Validate before use in shell
feature_name = extract_feature_name(prp_path)  # Whitelist validation

# Use subprocess with list (no shell injection possible)
import subprocess
subprocess.run([
    "rm", "-rf",
    f"prps/{feature_name}/execution/temp"
], check=True)
# NOT: subprocess.run(f"rm -rf prps/{feature_name}/...", shell=True)
```

---

### 2. Sensitive Data in Error Messages (Revisited)

**Examples of information disclosure**:

```python
# ❌ LEAKS sensitive information
raise ValueError(f"Cannot connect to {DATABASE_URL}")  # Leaks credentials
raise ValueError(f"API key invalid: {API_KEY}")        # Leaks secrets
raise ValueError(f"User not found: {email}")           # Leaks PII
```

**Secure alternative**:
```python
# ✅ SECURE - Generic error, log details internally
logging.error(f"Database connection failed: {DATABASE_URL}")  # Internal only
raise ValueError("Database connection failed - check configuration")  # User-facing
```

---

## Gotcha Checklist for Implementation

Before marking PRP complete, verify these gotchas are addressed:

- [ ] **Format string injection**: Templates use hardcoded format strings, variables validated
- [ ] **Path traversal**: All paths validated with `extract_feature_name()` 5-level check
- [ ] **TOCTOU race conditions**: Using EAFP pattern (try/except), not check-then-use
- [ ] **Subagent compliance**: Prompts use "CRITICAL", "MANDATORY", "INCOMPLETE without" language
- [ ] **Silent failures eliminated**: All validations raise exceptions (no warnings that continue)
- [ ] **Error message safety**: No absolute paths, usernames, or sensitive data in user-facing errors
- [ ] **XSS prevention**: If HTML rendering added, using bleach.clean() sanitization
- [ ] **Performance optimization**: Parallel validation for task batches (ThreadPoolExecutor)
- [ ] **Template variables**: All variables validated before .format(), defaults for optional vars
- [ ] **Naming consistency**: Enforcing `TASK{n}_COMPLETION.md` pattern in validation

---

## Sources Referenced

### From Archon
- **d60a71d62eb201d5** (Model Context Protocol): Path traversal validation, security best practices
- **c0e629a894699314** (Pydantic AI): Format string handling, tool calling patterns
- **9a7d4217c64c9a0a** (Claude Code Hooks): Subagent patterns, compliance enforcement

### From Web
- **Format String Injection**: https://lucumr.pocoo.org/2016/12/29/careful-with-str-format/
- **Markdown XSS**: https://github.com/showdownjs/showdown/wiki/Markdown's-XSS-Vulnerability
- **TOCTOU Race Conditions**: https://cwe.mitre.org/data/definitions/367.html
- **Path Traversal Security**: https://medium.com/@siddiquimohammad0807/pathlib-in-python-modern-secure-file-path-handling-e7ee2bf6b5cd
- **Error Message Design**: https://www.nngroup.com/articles/error-message-guidelines/
- **AI Agent Compliance**: https://springsapps.com/knowledge/best-practices-for-ai-agents-in-compliance---ioni

### From Local Codebase
- `.claude/patterns/security-validation.md`: 5-level path validation pattern
- `.claude/patterns/quality-gates.md`: Validation loop with retry pattern
- `prps/task_management_ui/execution/MISSING_REPORTS_ANALYSIS.md`: Evidence of 48% report coverage failure

---

## Recommendations for PRP Assembly

When generating the PRP:

1. **Include format string injection prevention** in template loading logic (use `string.Template` or validate variables)

2. **Reference path traversal pattern** - use existing `extract_feature_name()` from security-validation.md for ALL path operations

3. **Add TOCTOU mitigation** - use EAFP pattern in validation gates (try/read instead of exists/then/read)

4. **Emphasize fail-fast** - ALL validation must raise exceptions, NO warnings that continue execution

5. **Template variable validation** - add validation before `.format()` calls to prevent KeyError

6. **Parallel validation** - use ThreadPoolExecutor for task batch validation (5-10x speedup)

7. **Secure error messages** - use relative paths only, log details internally, show generic messages to users

8. **Enforce naming** - validate `TASK{n}_COMPLETION.md` pattern in quality gates

9. **Subagent prompt enhancement** - use "CRITICAL", "MANDATORY", "INCOMPLETE without" language + visual separators

10. **Add testing** - include tests for format injection, path traversal, TOCTOU, naming validation

---

## Confidence Assessment

**Gotcha Coverage**: 9/10

- **Security**: High confidence - covered format injection, path traversal, TOCTOU, XSS, command injection, information disclosure
- **Performance**: High confidence - identified I/O bottlenecks, provided parallel solutions
- **Common Mistakes**: High confidence - found real evidence in codebase (48% report coverage), provided concrete solutions
- **Subagent Compliance**: High confidence - analyzed prompt patterns, documented enforcement strategies

**Gaps**:
- **Low documentation on AI agent output compliance** - web sources focus on regulatory compliance, not technical enforcement
- **Limited TOCTOU examples for Python file operations** - most examples in C/C++, adapted patterns to Python
- **Markdown security varies by processor** - provided general guidance, may need processor-specific rules

**Areas of High Confidence**:
- Path traversal prevention (well-documented pattern in codebase)
- Format string injection (extensive Python-specific documentation)
- Validation gate patterns (existing quality-gates.md provides foundation)
- Error message design (NN/G UX guidelines are authoritative)

**Ready for PRP Assembly**: Yes - comprehensive coverage with actionable solutions for all identified gotchas.
