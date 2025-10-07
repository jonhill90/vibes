# Test Generation Report Template

**Usage Instructions:**
This template is used to document test generation results. Fill in all `{variable}` placeholders with actual values.

**Required Variables:**
- `{feature_name}`: Name of feature being tested (e.g., "user_auth", "task_management_ui")
- `{total_tests}`: Total number of test cases generated
- `{test_files_created}`: Number of test files created
- `{coverage_percentage}`: Overall test coverage percentage (if available)
- `{patterns_used}`: Comma-separated list of test patterns applied
- `{edge_cases_count}`: Number of edge cases covered
- `{execution_status}`: PASS | FAIL | PARTIAL | NOT_RUN
- `{generation_time}`: Time taken to generate tests (minutes)
- `{test_files_table}`: Markdown table of test files (see example below)
- `{coverage_table}`: Markdown table of coverage per module (see example below)
- `{edge_cases_list}`: Markdown list of edge cases tested
- `{integration_notes}`: Notes on integration with existing tests

**Example Variables:**
```python
variables = {
    "feature_name": "user_auth",
    "total_tests": 47,
    "test_files_created": 5,
    "coverage_percentage": 92.5,
    "patterns_used": "unit tests, integration tests, edge case tests",
    "edge_cases_count": 12,
    "execution_status": "PASS",
    "generation_time": 15,
    "test_files_table": "...",  # See format below
    "coverage_table": "...",    # See format below
    "edge_cases_list": "...",   # See format below
    "integration_notes": "Tests integrate with existing pytest suite..."
}
```

---

# Test Generation Report: {feature_name}

## Test Summary

| Metric | Value | Status |
|--------|-------|--------|
| Total Tests Generated | {total_tests} | ✅ |
| Test Files Created | {test_files_created} | ✅ |
| Coverage Percentage | {coverage_percentage}% | {coverage_status} |
| Edge Cases Covered | {edge_cases_count} | ✅ |
| Test Execution | {execution_status} | {execution_status_icon} |
| Generation Time | {generation_time} min | ✅ |

**Patterns Used**: {patterns_used}

## Test Files Created

{test_files_table}

**Example Table Format:**
```markdown
| File Path | Lines | Test Count | Purpose |
|-----------|-------|------------|---------|
| tests/test_user_model.py | 145 | 12 | User model validation tests |
| tests/test_auth_api.py | 203 | 18 | Authentication API endpoint tests |
| tests/integration/test_user_flow.py | 89 | 5 | End-to-end user flow tests |
```

## Coverage Analysis

{coverage_table}

**Example Table Format:**
```markdown
| Module/File | Coverage | Tests | Status |
|-------------|----------|-------|--------|
| src/models/user.py | 95% | 12 | ✅ |
| src/api/auth.py | 88% | 18 | ✅ |
| src/utils/validation.py | 92% | 8 | ✅ |
| **Overall** | **92.5%** | **47** | **✅** |
```

## Patterns Applied

### Test Patterns from PRP

{patterns_from_prp}

**Example:**
```markdown
1. **Unit Test Pattern** (from examples/test_patterns/unit_test.py)
   - Isolated component testing
   - Mocked dependencies
   - Single responsibility per test

2. **Integration Test Pattern** (from examples/test_patterns/integration_test.py)
   - Multi-component workflows
   - Real database interactions (test DB)
   - End-to-end API calls

3. **Edge Case Pattern** (from PRP Known Gotchas)
   - Null/empty input handling
   - Boundary value testing
   - Error condition validation
```

### Test Patterns Found in Codebase

{patterns_from_codebase}

**Example:**
```markdown
1. **Pytest Fixtures** (from tests/conftest.py)
   - Reusable test data setup
   - Database session management
   - Mock authentication tokens

2. **Parameterized Tests** (from tests/test_validation.py)
   - Data-driven test cases
   - Multiple input scenarios
   - @pytest.mark.parametrize usage
```

## Edge Cases Covered

{edge_cases_list}

**Example List Format:**
```markdown
1. **Null/Empty Input Validation**
   - Empty email string → ValidationError
   - Null password → ValidationError
   - Whitespace-only username → ValidationError

2. **Boundary Value Testing**
   - Password minimum length (8 chars) → Valid
   - Password maximum length (128 chars) → Valid
   - Username exactly 50 chars → Valid

3. **Invalid Data Types**
   - Integer for email field → TypeError
   - List for password field → TypeError
   - Dict for username field → TypeError

4. **Concurrent Operations**
   - Duplicate email registration → IntegrityError
   - Simultaneous password resets → Handled correctly
   - Race condition in token generation → Prevented

5. **Security Edge Cases**
   - SQL injection attempts → Sanitized
   - XSS in user input → Escaped
   - Path traversal in file uploads → Blocked
```

## Integration with Existing Tests

{integration_notes}

**Example:**
```markdown
### Integration Strategy
- **Test Suite**: Integrated with existing pytest suite in `tests/`
- **Fixtures**: Reused existing fixtures from `tests/conftest.py`
- **Naming Convention**: Followed existing `test_<module>_<feature>.py` pattern
- **Coverage Integration**: Added to existing coverage.py configuration

### Compatibility
- ✅ All new tests use pytest framework (consistent with existing)
- ✅ Database fixtures compatible with existing test DB setup
- ✅ Mock patterns match existing test approach
- ✅ CI/CD integration: Tests added to GitHub Actions workflow

### Dependencies
- No new test dependencies required (pytest, pytest-cov already installed)
- Reused existing test utilities from `tests/utils/`
- Compatible with current test database schema
```

## Test Execution Results

### Execution Summary

```bash
# Command run:
{test_command}

# Results:
{test_execution_output}
```

**Example:**
```bash
# Command run:
pytest tests/ -v --cov=src --cov-report=term-missing

# Results:
========================= test session starts =========================
platform darwin -- Python 3.11.5, pytest-7.4.2, pluggy-1.3.0
collected 47 items

tests/test_user_model.py::test_user_creation PASSED              [ 2%]
tests/test_user_model.py::test_email_validation PASSED           [ 4%]
tests/test_user_model.py::test_password_hashing PASSED           [ 6%]
...
tests/integration/test_user_flow.py::test_registration_flow PASSED [100%]

---------- coverage: platform darwin, python 3.11.5 ----------
Name                     Stmts   Miss  Cover   Missing
------------------------------------------------------
src/models/user.py          45      2    95%   23, 45
src/api/auth.py             78      9    88%   12, 34-38, 56, 89
src/utils/validation.py     25      2    92%   18, 22
------------------------------------------------------
TOTAL                      148     13    92%

========================= 47 passed in 3.45s ==========================
```

### Test Failures (if any)

{test_failures}

**Example:**
```markdown
**Status**: ✅ All tests passed

OR

**Status**: ⚠️ 2 tests failed

1. `tests/test_auth_api.py::test_token_expiration`
   - **Error**: AssertionError: Token not expired after 24 hours
   - **Cause**: Mock time not advancing correctly
   - **Fix Applied**: Updated mock to use freezegun library
   - **Status**: ✅ Fixed and passing

2. `tests/integration/test_user_flow.py::test_concurrent_registration`
   - **Error**: IntegrityError: duplicate key value
   - **Cause**: Race condition in test setup
   - **Fix Applied**: Added transaction isolation
   - **Status**: ✅ Fixed and passing
```

## Known Gotchas Addressed

{gotchas_addressed}

**Example:**
```markdown
1. **Async Test Execution** (from PRP Known Gotchas)
   - **Issue**: Async functions require special pytest decorator
   - **Solution**: Used `@pytest.mark.asyncio` for all async tests
   - **Pattern**: `async def test_async_operation():`

2. **Database State Leakage** (from codebase patterns)
   - **Issue**: Tests modify database, affecting subsequent tests
   - **Solution**: Added transaction rollback in teardown fixture
   - **Pattern**:
     ```python
     @pytest.fixture
     def db_session():
         session = TestSession()
         yield session
         session.rollback()
         session.close()
     ```

3. **Mock Configuration** (from PRP examples)
   - **Issue**: External API calls slow down tests
   - **Solution**: Mocked all external dependencies
   - **Pattern**: Used `unittest.mock.patch` for HTTP clients
```

## Validation Checklist

- [ ] All test files created successfully
- [ ] Tests follow existing patterns from codebase
- [ ] Edge cases from PRP documented and tested
- [ ] Coverage meets target percentage (≥80%)
- [ ] All tests pass (or failures documented with fixes)
- [ ] Integration with existing test suite verified
- [ ] No new test dependencies required (or documented)
- [ ] Test execution time acceptable (<5 min for unit tests)
- [ ] CI/CD integration complete (if applicable)

## Success Metrics

**Quantitative:**
- ✅ Generated {total_tests} test cases
- ✅ Achieved {coverage_percentage}% coverage (target: ≥80%)
- ✅ Covered {edge_cases_count} edge cases
- ✅ Test execution time: {test_execution_time} seconds

**Qualitative:**
- ✅ Tests follow codebase patterns
- ✅ Comprehensive edge case coverage
- ✅ Clear test documentation (docstrings)
- ✅ Easy to maintain and extend

## Next Steps

{next_steps}

**Example:**
```markdown
1. **Review test coverage gaps**
   - Identify modules below 80% coverage
   - Add tests for uncovered edge cases

2. **Performance optimization**
   - Profile slow tests (>1 second)
   - Add database indices if needed

3. **CI/CD integration**
   - Add tests to GitHub Actions workflow
   - Configure coverage reporting (Codecov)

4. **Documentation**
   - Update README with test instructions
   - Document test fixtures and utilities
```

---

**Report Generated**: {generation_date}
**Generated By**: Claude Code (PRP Execution - Test Generator)
**Confidence Level**: {confidence_level}
