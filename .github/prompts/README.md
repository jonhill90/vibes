# Prompt Evaluation

Use this directory to regression-test prompt and context-engineering changes before merging.

## Goal

Ensure prompt changes improve outputs without breaking known good behavior.

## Workflow

1. Add or update fixtures in `fixtures/`
2. Run the prompt/agent with each fixture input
3. Score results with `eval-checklist.md`
4. Record failures and adjust prompt/context
5. Re-run until all required checks pass

## Minimum Gate

- No critical checklist failures
- No regressions on previously passing fixtures
- At least one fixture covering an edge case
