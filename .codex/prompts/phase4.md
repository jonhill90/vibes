# Phase 4 · PRP Assembly

You are the final assembler for `${FEATURE_NAME}`.

## Inputs
- Feature analysis: `${PLANNING_DIR}/feature-analysis.md`
- Codebase patterns: `${PLANNING_DIR}/codebase-patterns.md`
- Documentation links: `${PLANNING_DIR}/documentation-links.md`
- Examples index: `${PLANNING_DIR}/examples-to-include.md`
- Gotchas: `${PLANNING_DIR}/gotchas.md`
- Template: `prps/templates/prp_base.md`
- Output: `prps/${FEATURE_NAME}.md`

## Responsibilities
1. Read every research artifact to ensure coverage and consistency.
2. Follow the PRP template exactly, filling each section with synthesized content tailored to `${FEATURE_NAME}`.
3. Reference documentation URLs and example files inline (do not duplicate full code bodies in the PRP).
4. Translate gotchas into the PRP "Gotchas" section with mitigations.
5. Define a verification plan (linting, type checking, tests, manual QA) that aligns with project standards.
6. Self-assess the PRP quality (≥8/10) with clear justification and confidence level.

## Deliverable
Overwrite `prps/${FEATURE_NAME}.md` using this scaffold:

````markdown
# ${FEATURE_NAME}

## Goal
- [...]

## Why Now
- [...]

## What We Are Building
- [...]

## Context & References
- Documentation: [link](...)
- Codebase Patterns: [...]
- Examples Directory: `prps/${FEATURE_NAME}/examples`

## Implementation Plan
1. [...]

## Gotchas & Mitigations
- [...]

## Validation Strategy
- Ruff / mypy / pytest commands, manual checks, CI hooks.

## Rollout & Monitoring
- [...]

## PRP Quality Self-Assessment
**Score: X/10**
- ✅ [...]
- ⚠️ [...]
**Overall Confidence**: HIGH/MEDIUM/LOW — [...]
````

Feel free to expand sections with tables or bullet lists when helpful, but do not remove required headings.

## Quality Bar
- Minimum quality score **≥ 8/10** with explicit deduction reasoning.
- All references resolve to files/URLs produced in earlier phases.
- No TODOs, placeholders, or missing sections.

## Output Instructions
Use a heredoc to write the final PRP:

```bash
cat <<'EOF' > "prps/${FEATURE_NAME}.md"
[final PRP markdown]
EOF
```

Show the first 40 lines to confirm:

```bash
sed -n '1,40p' "prps/${FEATURE_NAME}.md"
```
