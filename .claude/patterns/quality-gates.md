# Quality Gates Pattern

Document quality validation, scoring enforcement, and validation iteration loops for PRP generation and execution.

## PRP Quality Scoring (8+/10 Minimum)

### Scoring Criteria

```python
quality_checks = [
    "PRP score >= 8/10",
    "All 5 research documents created",
    "Examples extracted to examples/ (not just references)",
    "Examples have README with 'what to mimic' guidance",
    "Documentation includes URLs with specific sections",
    "Gotchas documented with solutions (not just warnings)",
    "Task list is logical and ordered",
    "Validation gates are executable commands",
    "Codebase patterns referenced appropriately"
]
```

### Score Extraction

```python
import re

prp_content = Read(f"prps/{feature_name}/{feature_name}.md")

# Extract score from PRP (look for "Score: X/10" pattern)
score_match = re.search(r'Score:\s*(\d+)/10', prp_content)
quality_score = int(score_match.group(1)) if score_match else 0
```

### Score Enforcement with Interactive Choice

```python
if quality_score < 8:
    print(f"⚠️ Quality Gate Failed: PRP scored {quality_score}/10 (minimum: 8/10)")
    print("\nOptions:")
    print("1. Regenerate with additional research")
    print("2. Review and improve specific sections")
    print("3. Proceed anyway (not recommended)")

    choice = input("Choose (1/2/3): ")

    if choice == "1":
        # Re-run phases with more research
        print("Re-running research phases with enhanced criteria...")
        # Trigger Phase 2 again with additional context
    elif choice == "2":
        # Identify gaps
        gaps = identify_missing_sections(prp_content)
        print("\nIdentified gaps:")
        for gap in gaps:
            print(f"  - {gap}")
        print("\nEnhancing specific sections...")
        # Re-run specific subagents for weak sections
    elif choice == "3":
        print("⚠️ Proceeding with quality score below threshold")
    else:
        print("❌ Invalid choice - aborting")
        exit(1)
else:
    print(f"✅ Quality Gate Passed: {quality_score}/10")
```

### Comprehensive Validation Checklist

For the full validation checklist, see the single source of truth:

**Reference**: `prps/templates/prp_base.md` - Final validation Checklist section

**DO NOT duplicate the checklist here** - always reference the template to ensure consistency.

## Execution Quality Gates (Multi-Level)

### Level 1: Syntax & Style

```bash
# Python validation
ruff check --fix src/
mypy src/

# Expected: No errors
```

### Level 2: Unit Tests

```bash
# Run all unit tests
pytest tests/ -v

# Expected: All tests pass
```

### Level 3: Integration Tests

```bash
# Project-specific integration tests
# Commands specified in PRP Validation Loop section

# Example:
# curl -X POST http://localhost:8000/api/endpoint
# docker-compose up -d && ./integration_tests.sh
```

### Validation Loop (Max 5 Attempts)

```python
MAX_ATTEMPTS = 5

for attempt in range(1, MAX_ATTEMPTS + 1):
    print(f"\nValidation attempt {attempt}/{MAX_ATTEMPTS}")

    # Run validation level
    result = run_validation(level, commands)

    if result.success:
        print(f"✅ Level {level} passed")
        break
    else:
        print(f"❌ Level {level} failed")
        print(f"Error: {result.error}")

        if attempt < MAX_ATTEMPTS:
            print("\nAnalyzing error and attempting fix...")

            # Analyze error message
            error_analysis = analyze_error(result.error, prp_gotchas)

            # Apply fix
            fix_attempt = apply_fix(error_analysis)
            print(f"Applied fix: {fix_attempt.description}")

            # Re-run validation in next iteration
        else:
            print(f"\n⚠️ Max attempts ({MAX_ATTEMPTS}) reached")
            print(f"Level {level} still failing after {MAX_ATTEMPTS} attempts")

            # Offer options
            print("\nOptions:")
            print("1. Continue to next level (not recommended)")
            print("2. Manual intervention required")
            print("3. Abort validation")
```

### Validation Result Tracking

```python
validation_results = {
    "level_1_syntax": {"status": "pass", "attempts": 1},
    "level_2_unit_tests": {"status": "pass", "attempts": 3},
    "level_3_integration": {"status": "fail", "attempts": 5, "error": "..."},
}

# Calculate pass rate
total_levels = len(validation_results)
passed_levels = sum(1 for r in validation_results.values() if r["status"] == "pass")
pass_rate = (passed_levels / total_levels) * 100

print(f"\nValidation Pass Rate: {pass_rate}% ({passed_levels}/{total_levels} levels)")
```

## Error Analysis and Fix Application

### Analyze Error Messages

```python
def analyze_error(error_message: str, prp_gotchas: str) -> dict:
    """Analyze validation error and match against known gotchas."""

    # Common error patterns
    patterns = {
        "import_error": r"ImportError|ModuleNotFoundError",
        "type_error": r"TypeError|AttributeError",
        "assertion_error": r"AssertionError",
        "syntax_error": r"SyntaxError|IndentationError",
        "timeout": r"TimeoutError|timeout",
    }

    # Identify error type
    error_type = None
    for name, pattern in patterns.items():
        if re.search(pattern, error_message):
            error_type = name
            break

    # Check if gotchas address this
    relevant_gotcha = None
    if prp_gotchas and error_type:
        # Search gotchas for relevant solution
        gotcha_sections = extract_gotcha_sections(prp_gotchas)
        for section in gotcha_sections:
            if error_type in section.lower() or \
               any(keyword in section for keyword in extract_keywords(error_message)):
                relevant_gotcha = section
                break

    return {
        "error_type": error_type,
        "error_message": error_message,
        "relevant_gotcha": relevant_gotcha,
        "suggested_fix": extract_fix_from_gotcha(relevant_gotcha) if relevant_gotcha else None
    }
```

### Apply Fix

```python
def apply_fix(error_analysis: dict) -> dict:
    """Apply fix based on error analysis."""

    if error_analysis["suggested_fix"]:
        # Use fix from PRP gotchas
        print(f"Applying fix from PRP gotchas: {error_analysis['suggested_fix']}")
        # Apply the fix
        result = execute_fix(error_analysis["suggested_fix"])
    else:
        # Generic fix attempt
        print("No specific gotcha found - applying generic fix...")
        result = apply_generic_fix(error_analysis["error_type"], error_analysis["error_message"])

    return result
```

## Quality Metrics and Reporting

### PRP Generation Quality Report

```python
quality_report = {
    "score": quality_score,
    "research_docs": 5,  # feature-analysis, codebase-patterns, docs, examples, gotchas
    "examples_extracted": example_count,
    "documentation_sources": doc_count,
    "gotchas_documented": gotcha_count,
    "task_count": task_count,
    "validation_gates": validation_gate_count,
}

print(f"""
PRP Quality Report:
- Overall Score: {quality_report['score']}/10 {'✅' if quality_report['score'] >= 8 else '⚠️'}
- Research Documents: {quality_report['research_docs']}/5
- Examples Extracted: {quality_report['examples_extracted']} files
- Documentation Sources: {quality_report['documentation_sources']}
- Gotchas Documented: {quality_report['gotchas_documented']}
- Tasks Defined: {quality_report['task_count']}
- Validation Gates: {quality_report['validation_gates']}
""")
```

### Execution Validation Report

```python
execution_report = {
    "tasks_completed": completed_tasks,
    "total_tasks": total_tasks,
    "test_coverage": coverage_percentage,
    "validation_levels": {
        "syntax": "pass",
        "unit_tests": "pass",
        "integration": "pass",
    },
    "total_attempts": sum(attempts_per_level.values()),
    "max_attempts_per_level": max(attempts_per_level.values()),
}

print(f"""
Execution Validation Report:
- Tasks Completed: {execution_report['tasks_completed']}/{execution_report['total_tasks']}
- Test Coverage: {execution_report['test_coverage']}% (target: 70%+)
- Validation Levels:
  - Syntax: {execution_report['validation_levels']['syntax']}
  - Unit Tests: {execution_report['validation_levels']['unit_tests']}
  - Integration: {execution_report['validation_levels']['integration']}
- Total Fix Attempts: {execution_report['total_attempts']}
- Max Attempts per Level: {execution_report['max_attempts_per_level']}/5
""")
```

## Best Practices

### DO:
- ✅ Always enforce 8+/10 minimum score for PRPs
- ✅ Iterate on validation failures (max 5 attempts)
- ✅ Reference prp_base.md template for checklist (single source of truth)
- ✅ Check PRP gotchas first when fixing errors
- ✅ Track attempts per validation level
- ✅ Provide interactive choices for quality failures
- ✅ Document all fixes applied during validation

### DON'T:
- ❌ Don't duplicate prp_base.md checklist in other locations
- ❌ Don't skip validation levels to save time
- ❌ Don't accept quality scores below 8/10 without user confirmation
- ❌ Don't give up after first validation failure
- ❌ Don't ignore error messages - analyze them
- ❌ Don't proceed with broken tests

## Usage Examples

### Example 1: PRP Generation Quality Gate

```python
# After PRP assembly (Phase 4)
prp_content = Read(f"prps/{feature_name}/{feature_name}.md")

# Extract score
score_match = re.search(r'Score:\s*(\d+)/10', prp_content)
quality_score = int(score_match.group(1)) if score_match else 0

# Enforce minimum
if quality_score < 8:
    print(f"⚠️ Quality Gate Failed: {quality_score}/10 (minimum: 8/10)")
    # Interactive choice (see pattern above)
else:
    print(f"✅ Quality Gate Passed: {quality_score}/10")
    # Proceed to delivery
```

### Example 2: Execution Validation Loop

```python
# For each validation level
levels = ["syntax", "unit_tests", "integration"]

for level in levels:
    print(f"\n{'='*60}")
    print(f"Validation Level: {level}")
    print(f"{'='*60}")

    # Get commands from PRP
    commands = get_validation_commands(prp_content, level)

    # Run validation loop (max 5 attempts)
    for attempt in range(1, 6):
        print(f"\nAttempt {attempt}/5")
        result = run_validation_commands(commands)

        if result.success:
            print(f"✅ {level} validation passed")
            break
        else:
            if attempt < 5:
                error_analysis = analyze_error(result.error, prp_gotchas)
                apply_fix(error_analysis)
            else:
                print(f"❌ {level} failed after 5 attempts")
```

## Integration with PRP System

### Generate-PRP Integration (Phase 5)

See `.claude/commands/generate-prp.md` Phase 5 for orchestration logic.

**What to keep in command**:
- Score extraction logic
- Quality gate check (if score < 8)
- Interactive choice prompt

**What to reference from this pattern**:
- Scoring criteria list
- Error analysis approach
- Validation checklist reference

### Execute-PRP Integration (Phase 4)

See `.claude/commands/execute-prp.md` Phase 4 for orchestration logic.

**What to keep in command**:
- Validation level sequencing
- Loop iteration count

**What to reference from this pattern**:
- Multi-level validation structure
- Max attempts per level
- Error analysis and fix application
- Validation result tracking

---

**Remember**: This pattern is self-contained. Don't create sub-patterns or cross-reference other patterns. For the comprehensive validation checklist, always reference `prps/templates/prp_base.md`.
