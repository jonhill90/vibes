# PRP: Test Codex PRP Execution

**Generated**: 2025-10-07
**Based On**: prps/INITIAL_test_codex_prp_execution.md

---

## Goal

Create a simple user authentication module to validate PRP execution workflow with validation loops.

## Why

**Business Value**:
- Test validation loop functionality
- Verify error handling and retry logic
- Validate test coverage enforcement

## What

### Core Features

1. **User Model**:
   - Email field (validated)
   - Password field (hashed)
   - Pydantic validation

2. **Authentication Service**:
   - Login endpoint
   - Logout endpoint
   - Session management

3. **Testing**:
   - Unit tests for all components
   - Integration tests for API
   - ≥70% test coverage

### Success Criteria

- [ ] All tasks completed
- [ ] All validation gates passed (ruff, mypy, pytest)
- [ ] Test coverage ≥70%
- [ ] No critical linting errors

---

## Known Gotchas & Library Quirks

```python
# CRITICAL GOTCHA 1: Email Validation
# Issue: Using plain string for email allows invalid formats
# Impact: Malformed emails in database

# ❌ WRONG
class User(BaseModel):
    email: str  # No validation

# ✅ RIGHT
from pydantic import EmailStr

class User(BaseModel):
    email: EmailStr  # Pydantic validates format
```

---

## Implementation Blueprint

### Task List

```yaml
Task 1: Create User Model
RESPONSIBILITY: Define user data structure with validation
FILES TO CREATE:
  - src/models/user.py

SPECIFIC STEPS:
  1. Create Pydantic BaseModel for User
  2. Add email field with EmailStr validation
  3. Add password field with hashing
  4. Add docstrings

VALIDATION:
  - ruff check src/models/
  - mypy src/models/
  - Unit tests pass

---

Task 2: Create Authentication Service
RESPONSIBILITY: Implement login/logout logic
FILES TO CREATE:
  - src/services/auth.py

SPECIFIC STEPS:
  1. Implement login() function
  2. Implement logout() function
  3. Add session management
  4. Error handling

VALIDATION:
  - ruff check src/services/
  - pytest tests/test_auth.py
  - Integration tests pass

---

Task 3: Add Tests
RESPONSIBILITY: Comprehensive test coverage
FILES TO CREATE:
  - tests/test_user.py
  - tests/test_auth.py

SPECIFIC STEPS:
  1. Unit tests for User model
  2. Unit tests for auth service
  3. Integration tests for API
  4. Verify coverage ≥70%

VALIDATION:
  - pytest --cov=src tests/
  - Coverage report shows ≥70%
```

---

## Validation Loop

### Level 1: Syntax & Style Checks

```bash
# Linting (auto-fix enabled)
ruff check --fix src/ tests/

# Type checking
mypy src/ tests/

# Expected: No errors
```

### Level 2: Unit Tests

```bash
# Run all unit tests
pytest tests/ -v

# Expected: All tests pass
```

### Level 3: Coverage

```bash
# Run tests with coverage
pytest --cov=src --cov-report=term-missing tests/

# Expected: ≥70% coverage
```

---

## PRP Quality Self-Assessment

**Score: 8/10** - Good confidence in implementation success

**Reasoning**:
- ✅ Clear task breakdown (3 tasks with specific steps)
- ✅ Gotchas documented with solutions
- ✅ Validation loop defined
- ⚠️ Minimal PRP for testing (not production-ready)

