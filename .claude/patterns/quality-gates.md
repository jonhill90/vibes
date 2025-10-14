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

# Level 3a: API Integration Tests
# Project-specific (from PRP)
docker-compose up -d && ./integration_tests.sh

# Level 3b: Browser Integration Tests (User-Facing Features)
# Agent-driven browser validation (10x slower than API tests)
claude --agent validation-gates "Validate frontend at localhost:5173"
```

### Level 3b: Browser Integration Tests

**When to Use**: User-facing features, frontend UI validation, end-to-end workflows

**Pattern**: Navigation → Interaction → Validation (accessibility tree-based)

```python
def validate_frontend_browser() -> dict:
    """Browser validation for frontend UI."""
    # 1. Pre-flight: Check frontend running
    response = Bash("curl -s http://localhost:5173")
    if "Connection refused" in response.stderr:
        return {"success": False, "error": "Frontend not running"}

    # 2. Navigate and capture state
    browser_navigate(url="http://localhost:5173")
    initial_state = browser_snapshot()  # Accessibility tree (~500 tokens)

    # 3. Validate expected components
    checks = {
        "app_loaded": "RootWebArea" in initial_state,
        "navigation": "navigation" in initial_state,
        "main_content": "main" in initial_state
    }

    if not all(checks.values()):
        return {"success": False, "error": f"Missing components"}

    # 4. Test interaction (semantic locators, not refs)
    browser_click(element="button containing 'Upload'")
    browser_wait_for(text="Select a document", timeout=5000)

    # 5. Validate final state
    final_state = browser_snapshot()
    if "Select a document" not in final_state:
        return {"success": False, "error": "Dialog not shown"}

    # 6. Screenshot for human verification only
    browser_take_screenshot(filename="validation-proof.png")

    return {"success": True, "screenshot": "validation-proof.png"}
```

**Performance Note**: Browser tests are ~10x slower than API tests. Run after API validation passes.

**Key Differences from API Tests**:
- Use accessibility tree for validation (not screenshots - agents can't parse images)
- Use semantic locators ("button containing 'Upload'", not refs like "e5")
- Requires frontend service running + browser binaries installed
- Same 5-attempt retry pattern applies

**See**: `.claude/patterns/browser-validation.md` for complete patterns, gotchas, and error handling

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
