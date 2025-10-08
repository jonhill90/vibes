# Phase 1 · Feature Analysis

You are the lead analyst for `${FEATURE_NAME}`.

## Inputs
- Initial requirements: `${INITIAL_MD_PATH}`
- Output location: `${PLANNING_DIR}/feature-analysis.md`

## Responsibilities
1. Read **every section** of the INITIAL file to extract explicit requirements, constraints, success criteria, stakeholders, and pain points.
2. Infer hidden/implicit requirements or assumptions needed to make the feature production ready.
3. Identify the architectural areas of the codebase that will be touched (APIs, CLIs, scripts, configuration, documentation).
4. Note integrations with existing tooling (Archon, Codex CLI, CI/CD, etc.).
5. Produce a crisp blueprint the downstream researchers can act on without rereading INITIAL.md.

## Deliverable
Create `${PLANNING_DIR}/feature-analysis.md` with the following structure (overwrite if it already exists):

````markdown
# Feature Analysis: ${FEATURE_NAME}

## INITIAL.md Summary
- [Key points]

## Explicit Requirements
- [Bulleted list]

## Implicit Requirements & Assumptions
- [Bulleted list]

## Technical Components
- [Subsystems, files, services that will change]

## External Interfaces & Integrations
- [Codex CLI, Archon MCP, CI/CD, etc.]

## Risks & Open Questions
- [What needs clarification]

## Success Criteria
- [Concrete, testable outcomes]
````

## Quality Bar
- No TODO/placeholder text.
- Everything needed for Phases 2A/2B/2C to proceed independently.
- Call out anything that might block research (and why).

## Output Instructions
When ready, overwrite the file using a heredoc so the downstream phases consume it:

```bash
cat <<'EOF' > "${PLANNING_DIR}/feature-analysis.md"
[final markdown content]
EOF
```

Confirm success by showing `ls -l ${PLANNING_DIR}` and `sed -n '1,40p' ${PLANNING_DIR}/feature-analysis.md`.
