# Quality Gates - Quick Reference

**Purpose**: Quality validation, scoring enforcement (8+/10), validation iteration loops (max 5 attempts)
**Use when**: PRP generation quality checks, execution validation, error fix loops
**See also**: `.claude/commands/generate-prp.md` Phase 5, `.claude/agents/prp-gen-assembler.md`

## PRP Quality Scoring (8+/10 Minimum)

```python
# Extract score from assembled PRP
import re
prp_content = Read(f"prps/{feature_name}.md")
score_match = re.search(r'Score:\s*(\d+)/10', prp_content)
quality_score = int(score_match.group(1)) if score_match else 0

# Enforce minimum with interactive choice
if quality_score < 8:
    print(f"⚠️ Quality Gate Failed: {quality_score}/10 (minimum: 8/10)")
    print("Options: 1. Regenerate  2. Improve sections  3. Proceed anyway")
    choice = input("Choose (1/2/3): ")

    if choice == "1":
        # Re-run research phases
    elif choice == "2":
        # Re-run specific subagents
    elif choice == "3":
        print("⚠️ Proceeding below threshold")
    else:
        exit(1)
else:
    print(f"✅ Quality Gate Passed: {quality_score}/10")
```

## Execution Validation (Multi-Level)

```bash
# Level 1: Syntax & Style
ruff check --fix src/ && mypy src/  # Python
eslint --fix src/                   # JavaScript

# Level 2: Unit Tests
pytest tests/ -v

# Level 3: Integration Tests
# Project-specific (from PRP)
docker-compose up -d && ./integration_tests.sh
```

## Validation Loop (Max 5 Attempts)

```python
MAX_ATTEMPTS = 5

for attempt in range(1, MAX_ATTEMPTS + 1):
    result = run_validation(level, commands)

    if result.success:
        print(f"✅ Level {level} passed")
        break

    print(f"❌ Attempt {attempt}/{MAX_ATTEMPTS} failed: {result.error}")

    if attempt < MAX_ATTEMPTS:
        # Analyze error against PRP gotchas, apply fix
        error_analysis = analyze_error(result.error, prp_gotchas)
        fix_attempt = apply_fix(error_analysis)
        print(f"Applied fix: {fix_attempt.description}")
    else:
        print(f"⚠️ Max attempts reached - manual intervention required")
```

## Error Analysis Pattern

```python
def analyze_error(error_message: str, prp_gotchas: str) -> dict:
    """Match error against known gotchas, suggest fix."""

    # Error patterns
    patterns = {
        "import_error": r"ImportError|ModuleNotFoundError",
        "type_error": r"TypeError|AttributeError",
        "assertion_error": r"AssertionError",
        "syntax_error": r"SyntaxError|IndentationError",
        "timeout": r"TimeoutError|timeout",
    }

    # Identify type
    error_type = next((name for name, pat in patterns.items()
                      if re.search(pat, error_message)), None)

    # Find gotcha solution
    relevant_gotcha = search_gotchas_for_error_type(prp_gotchas, error_type, error_message)

    return {
        "error_type": error_type,
        "error_message": error_message,
        "relevant_gotcha": relevant_gotcha,
        "suggested_fix": extract_fix_from_gotcha(relevant_gotcha) if relevant_gotcha else None
    }
```

## Field Reference

**PRP Quality Metrics**:
- `quality_score`: Overall score (0-10, minimum 8)
- `research_docs`: Planning docs count (target: 5)
- `examples_extracted`: Code examples count (target: 2+)
- `documentation_sources`: Official docs count (target: 5+)
- `gotchas_documented`: Gotchas count (target: 5-10)

**Validation Result Fields**:
- `status`: "pass" | "fail"
- `attempts`: Fix attempts (1-5)
- `error`: Error message (if failed)

## Rules (DO/DON'T)

**ALWAYS**:
- Enforce 8+/10 minimum for PRPs
- Iterate on failures (max 5 attempts)
- Check PRP gotchas first when fixing
- Reference `prps/templates/prp_base.md` for comprehensive checklist (single source of truth)

**NEVER**:
- Skip validation levels
- Accept scores <8 without user confirmation
- Give up after first failure
- Duplicate prp_base.md checklist elsewhere
