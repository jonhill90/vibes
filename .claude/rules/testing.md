---
paths:
  - "tests/**"
---

# Testing Guidelines

## Workflow: Red-Green-Refactor

Follow test-driven development when writing new features or fixing bugs:

1. **Red** — Write a failing test that defines the expected behavior
2. **Green** — Write the minimum code to make the test pass
3. **Refactor** — Clean up while keeping tests green

Do not skip steps. Do not write implementation before the test exists.

## Test Conventions

- Write clear, focused tests that verify one behavior at a time
- Use descriptive test names that explain what is being tested and the expected outcome
- Follow Arrange-Act-Assert (AAA) pattern: set up test data, execute the code under test, verify results
- Keep tests independent — each test should run in isolation without depending on other tests
- Start with the simplest test case, then add edge cases and error conditions
- Tests should fail for the right reason — verify they catch the bugs they're meant to catch
- Mock external dependencies to keep tests fast and reliable

## Triangulation

Don't trust a single test case. Use multiple examples to prevent false positives from hardcoded or overly specific implementations. If one test could pass by accident, add another that forces a real implementation.

## Test Doubles

- Use stubs to replace external dependencies with controlled return values
- Use spies to verify interactions without changing behavior
- Be explicit about what kind of double you need — don't use vague terms
- Keep test doubles minimal — only fake what's necessary for isolation

## Quality Checks

- Every test should fail before it passes (verify the Red step)
- Run the full suite after each change, not just the new test
- Match existing test style — naming, structure, assertion patterns
- If refactoring, tests must stay green throughout

## Do Not

- Generate tests without running them
- Write tests that pass trivially (testing nothing)
- Couple tests to implementation details — test behavior, not internals
- Skip edge cases: null, empty, boundary values, error paths
