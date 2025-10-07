# Template Locations Guide

This repository has TWO template locations with different purposes:

---

## `.claude/templates/` - PRP Execution Templates

**Purpose**: Templates used DURING PRP execution by subagents

**Files**:
- `task-completion-report.md` - Task completion documentation
- `test-generation-report.md` - Test coverage reports
- `validation-report.md` - Validation gate results
- `completion-report.md` - Legacy completion template

**When to use**:
- Creating completion reports during `/execute-prp`
- Generating test reports in validation phase
- Documenting task implementation
- Tracking PRP execution progress

**Used by**: Subagents (prp-exec-implementer, prp-exec-test-generator, prp-exec-validator)

---

## `prps/templates/` - PRP Generation Templates

**Purpose**: Templates used DURING PRP generation by `/generate-prp`

**Files**:
- `prp_base.md` - Base PRP structure
- `feature_template.md` - Feature implementation PRPs
- `tool_template.md` - Tool integration PRPs
- `documentation_template.md` - Documentation PRPs

**When to use**:
- Generating new PRPs with `/generate-prp`
- Creating consistent PRP structure
- Assembling PRP from research artifacts
- Standardizing PRP format

**Used by**: PRP generation agents (prp-gen-assembler)

---

## Quick Reference

| Need to... | Use Template From |
|---|---|
| Document task completion | `.claude/templates/task-completion-report.md` |
| Generate test report | `.claude/templates/test-generation-report.md` |
| Create validation report | `.claude/templates/validation-report.md` |
| Create new PRP | `prps/templates/prp_base.md` |
| Generate feature PRP | `prps/templates/feature_template.md` |

---

## Why Two Locations?

**Separation of Concerns**:
- Execution templates are reusable across ALL PRPs (not PRP-specific)
- Generation templates define PRP structure itself
- Clear distinction prevents confusion

**Lifecycle Stages**:
1. **PRP Generation** (`/generate-prp`) uses `prps/templates/` to create PRP document
2. **PRP Execution** (`/execute-prp`) uses `.claude/templates/` to document execution

---

**Last Updated**: 2025-10-07
**Related**: cleanup_execution_reliability_artifacts PRP
