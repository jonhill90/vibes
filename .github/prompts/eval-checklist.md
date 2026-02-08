# Prompt Eval Checklist

Use this checklist for every fixture run.

## Required

- [ ] Output follows requested format exactly
- [ ] Output is factually grounded in provided context
- [ ] Output includes no hallucinated files, commands, or APIs
- [ ] Output respects explicit constraints and scope limits
- [ ] Output stays concise and avoids irrelevant details

## Context Quality

- [ ] Prompt included only needed context (no kitchen-sink dump)
- [ ] Missing context was identified explicitly
- [ ] Retrieval order was logical and progressive

## Task Quality

- [ ] Result solves the user request end-to-end
- [ ] Verification steps or evidence are included when needed
- [ ] Error handling/edge case behavior is acceptable

## TDD Compliance (for code changes)

- [ ] Tests were written before implementation
- [ ] Test failed first (Red), then passed (Green)
- [ ] Implementation is minimum required to pass tests
- [ ] Refactoring kept tests green

## Regression Decision

- [ ] Pass
- [ ] Fail (capture failing checklist items and update prompt/context)
