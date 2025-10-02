name: "Feature Template - Streamlined for Standard Features"
description: |

## Purpose
Simplified template for implementing standard features in Vibes. Use this when adding new functionality that doesn't require complex multi-agent systems or extensive tool integrations.

## Core Principles
1. **Context is King**: Include ALL necessary documentation and examples
2. **Validation Loops**: Provide executable tests the AI can run and fix
3. **Progressive Success**: Start simple, validate, then enhance
4. **Follow Global Rules**: Adhere to all rules in CLAUDE.md

---

## Goal
[Clear, specific description of what needs to be built]

Example: "Add user authentication endpoint that supports JWT tokens and session management"

## Why
- **Business Value**: [How does this help users or the business?]
- **Integration**: [How does this fit with existing features?]
- **Problems Solved**: [What specific problems does this address?]

## What
[Detailed description of user-visible behavior and technical requirements]

### Success Criteria
- [ ] [Specific, measurable outcome 1]
- [ ] [Specific, measurable outcome 2]
- [ ] [Specific, measurable outcome 3]

## Context

### Documentation & References
```yaml
# Critical resources to review before implementation
- url: [Official API/library documentation]
  why: [Specific sections or methods needed]

- file: [path/to/similar/implementation.py]
  why: [Pattern to follow, gotchas to avoid]

- doc: [Related documentation URL]
  section: [Specific section about patterns/pitfalls]
```

### Current Structure
```bash
# Relevant current codebase structure
project/
├── existing/
│   └── relevant_file.py
└── config/
    └── settings.py
```

### Desired Structure
```bash
# What will be added/modified
project/
├── existing/
│   └── relevant_file.py     # MODIFIED: Added new functionality
├── new_feature/
│   ├── __init__.py          # NEW: Package init
│   ├── core.py             # NEW: Core feature logic
│   └── utils.py            # NEW: Helper functions
└── config/
    └── settings.py         # MODIFIED: Added config variables
```

### Known Gotchas & Patterns
```python
# CRITICAL: [Library/framework quirks to be aware of]
# Example: FastAPI requires async functions for all endpoints
# Example: This library doesn't support Python 3.11+ yet

# PATTERN: [Existing patterns in codebase to follow]
# Example: All database queries use connection pooling from db/pool.py
# Example: Error responses follow format in utils/responses.py
```

## Implementation

### Task List
```yaml
Task 1: [First step]
ACTION: [What to do]
FILES: [Which files to create/modify]
PATTERN: [Existing code to mirror]

Task 2: [Second step]
ACTION: [What to do]
FILES: [Which files to create/modify]
PATTERN: [Existing code to mirror]

Task 3: [Third step]
ACTION: [What to do]
FILES: [Which files to create/modify]
PATTERN: [Existing code to mirror]
```

### Key Implementation Details
```python
# Pseudocode showing critical logic (not full implementation)

# Task 1: Core functionality
def new_feature(param: str) -> Result:
    # PATTERN: Validate inputs first (see validators.py)
    validated = validate_input(param)

    # CRITICAL: [Important detail about implementation]
    # Example: Must use connection pooling for all DB queries

    # PATTERN: Follow existing error handling
    try:
        result = process(validated)
    except SpecificError as e:
        # Handle gracefully
        return error_response(e)

    return success_response(result)
```

### Integration Points
```yaml
CONFIG:
  - file: config/settings.py
  - add: FEATURE_SETTING = os.getenv('FEATURE_SETTING', 'default')

DEPENDENCIES:
  - Update requirements.txt with: new-library>=1.0.0

ROUTES (if API):
  - file: api/routes.py
  - add: router.include_router(feature_router, prefix='/feature')

DATABASE (if needed):
  - Create migration: migrations/001_add_feature_table.sql
```

## Validation

### Level 1: Syntax & Style
```bash
# Run linting and type checking
ruff check . --fix
mypy .

# Expected: No errors
```

### Level 2: Unit Tests
```python
# Create tests/test_new_feature.py

def test_happy_path():
    """Test basic functionality works"""
    result = new_feature("valid_input")
    assert result.success is True

def test_validation_error():
    """Test invalid input is rejected"""
    with pytest.raises(ValidationError):
        new_feature("invalid")

def test_edge_case():
    """Test edge cases handled"""
    result = new_feature("")
    assert result.success is False
```

```bash
# Run tests
pytest tests/test_new_feature.py -v

# Expected: All tests pass
```

### Level 3: Integration Test
```bash
# Manual test or integration test command
[Specific command to test the feature end-to-end]

# Example:
curl -X POST http://localhost:8000/feature \
  -H "Content-Type: application/json" \
  -d '{"param": "test"}'

# Expected: [Specific expected response]
```

## Final Checklist
- [ ] All tests pass
- [ ] No linting/type errors
- [ ] Integration test successful
- [ ] Error cases handled gracefully
- [ ] Documentation updated (if needed)
- [ ] Follows existing code patterns
- [ ] Performance is acceptable

---

## Anti-Patterns to Avoid
- ❌ Don't create new patterns when existing ones work
- ❌ Don't skip validation - always test your changes
- ❌ Don't hardcode values that should be configuration
- ❌ Don't ignore error cases
- ❌ Don't commit without running tests
