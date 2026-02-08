# TDD Workflow for Agents

> Distilled from authoritative sources. Verify against these URLs before relying on local content.

## Sources

- [VS Code: Test-Driven Development Guide](https://code.visualstudio.com/docs/copilot/guides/test-driven-development-guide)
- [GitHub/Automattic: Copilot for TDD](https://github.com/readme/guides/github-copilot-automattic)

---

## Why TDD Works for Agents

Tests are the best verification loop an agent can have. Writing tests first gives the agent a concrete, runnable definition of "done" — eliminating guesswork about whether the implementation is correct.

## Red-Green-Refactor

1. **Red** — Write a failing test that defines the expected behavior
2. **Green** — Write the minimum code to make it pass
3. **Refactor** — Clean up while keeping tests green

Do not skip steps. The failing test proves the test actually tests something.

## Triangulation

A single test case can pass by accident (hardcoded return values, overly specific logic). Add multiple examples that force a real implementation.

- First test: `isPrime(2)` → `true`
- Second test: `isPrime(4)` → `false` (prevents `return true`)
- Third test: `isPrime(7)` → `true` (prevents `return n == 2`)

## Test Doubles

Be explicit about what you need:

- **Stubs** — replace dependencies with controlled return values
- **Spies** — verify interactions without changing behavior
- Only fake what's necessary for isolation

## Working with Agent Suggestions

Agent-generated code often requires adjustment. The workflow is:

1. Accept the suggestion if it's close enough
2. Adjust to match your style and conventions
3. Re-run tests to verify nothing broke

The time to adjust is less than writing from scratch. Don't expect perfection — expect a useful starting point.

## Complements

This doc explains the *why*. For concise test conventions (AAA pattern, naming, independence), see the testing rules in `.claude/rules/testing.md` and `.github/instructions/testing.instructions.md`.
