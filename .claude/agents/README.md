# Claude Code Agents

This directory contains specialized agent configurations for different aspects of development workflow. Each agent is a markdown file with YAML frontmatter defining its capabilities, tools, and behavior.

## Overview

Agents in this directory are invoked by Claude Code to perform specific tasks. They have access to tools (Bash, Read, Edit, etc.) and can work autonomously to complete complex workflows.

**How to use agents**:
```bash
# General invocation
claude --agent {agent-name} "Task description with specific requirements"

# Example: Validation
claude --agent validation-gates "Validate RAG service backend and frontend at localhost:5173"

# Example: PRP execution
claude --agent prp-exec-validator "Run validation gates from prps/user_auth.md"
```

---

## Available Agents

### 1. validation-gates.md

**Purpose**: Testing and validation specialist for backend and frontend code

**Capabilities**:
- Run automated tests (pytest, jest, etc.)
- Execute linting and formatting checks (ruff, eslint)
- Perform type checking (mypy, TypeScript)
- Browser-based UI validation (Playwright)
- Iterative fix loops until all tests pass

**Browser Testing**: ✅ Enabled

**When to use**:
- After implementing features (validate they work correctly)
- Before merging PRs (ensure quality gates met)
- When testing UI workflows end-to-end
- For comprehensive validation (backend + frontend)

**Example invocations**:
```bash
# Backend validation
claude --agent validation-gates "Validate user authentication API - run tests and linting"

# Frontend browser validation
claude --agent validation-gates "Validate document upload feature at localhost:5173 - test full workflow"

# Full-stack validation
claude --agent validation-gates "Validate RAG service: backend tests + frontend UI at localhost:5173"
```

---

### 2. prp-exec-validator.md

**Purpose**: Systematic validation for PRP execution with autonomous fix loops

**Capabilities**:
- Execute validation gates from PRP "Validation Loop" section
- Multi-level validation (syntax → tests → integration → browser)
- Analyze failures and determine root causes
- Apply fixes autonomously (up to 5 attempts per level)
- Browser-based end-to-end testing
- Generate comprehensive validation reports

**Browser Testing**: ✅ Enabled

**When to use**:
- After PRP implementation (systematic validation)
- For full-stack validation (backend + frontend)
- When you need autonomous fixing (not just reporting)
- For comprehensive quality assurance

**Example invocations**:
```bash
# PRP validation with fixes
claude --agent prp-exec-validator "Run validation gates from prps/user_auth.md and fix any issues"

# Full-stack validation
claude --agent prp-exec-validator "Validate prps/task_management.md - include browser tests for frontend at localhost:5174"
```

**Output**: Creates `prps/validation-report.md` with detailed results

---

### 3. Other Agents

**prp-exec-implementer.md**: Task implementation from PRP blueprints
**prp-exec-task-analyzer.md**: PRP analysis and task breakdown
**prp-exec-test-generator.md**: Automated test generation
**documentation-manager.md**: Documentation updates and maintenance
**prp-gen-* agents**: PRP generation workflow specialists

(See individual agent files for details)

---

## Browser Testing Capability

Agents **validation-gates** and **prp-exec-validator** have browser automation tools for frontend UI validation. This enables true end-to-end testing beyond backend APIs.

### Agents with Browser Tools

| Agent | Browser Tools | Use Case |
|-------|---------------|----------|
| **validation-gates** | ✅ Full suite | Frontend UI validation, end-to-end workflows |
| **prp-exec-validator** | ✅ Full suite | Full-stack validation with browser tests |

**Available browser tools**:
- `browser_navigate` - Navigate to URL
- `browser_snapshot` - Capture accessibility tree (structured data)
- `browser_click` - Click elements using semantic queries
- `browser_type` - Type into input fields
- `browser_fill_form` - Fill multiple form fields
- `browser_wait_for` - Wait for text/element to appear
- `browser_take_screenshot` - Capture screenshot (for human review)
- `browser_evaluate` - Execute JavaScript
- `browser_tabs` - Manage browser tabs
- `browser_install` - Install browser binaries

### When to Use Browser Validation

**Use browser validation for**:
- ✅ User-facing UI features (buttons, forms, modals)
- ✅ End-to-end workflows (document upload, task creation)
- ✅ Cross-component integration (frontend + backend)
- ✅ Accessibility validation

**Don't use browser validation for**:
- ❌ Backend-only API validation (use API tests - 10x faster)
- ❌ Visual design validation (agents can't parse screenshots)
- ❌ Performance testing (use dedicated tools)

### Example Browser Validation Workflows

#### 1. Document Upload Validation (RAG Service)

```bash
claude --agent validation-gates "Validate document upload feature:
1. Navigate to localhost:5173
2. Click 'Upload' button
3. Fill upload form with test document
4. Submit and verify success message
5. Confirm document appears in list"
```

**What the agent does**:
1. Pre-flight checks (browser installed, services running)
2. Navigate to frontend
3. Capture initial accessibility tree
4. Interact with UI (click, type, fill form)
5. Validate final state using accessibility tree
6. Take screenshot for proof
7. Report results

#### 2. Task Creation Validation (Task Manager)

```bash
claude --agent validation-gates "Validate task creation at localhost:5174:
1. Navigate to task manager
2. Click 'Create Task' button
3. Fill task form (title, description, status)
4. Submit and verify task appears in list"
```

#### 3. Full-Stack Validation

```bash
claude --agent prp-exec-validator "Run validation gates from prps/rag_service.md:
- Level 1: Syntax and linting
- Level 2: Unit tests
- Level 3a: API integration tests
- Level 3b: Browser UI validation at localhost:5173"
```

### Browser Validation Best Practices

**DO**:
- ✅ Use accessibility tree for validation (`browser_snapshot()`)
- ✅ Use semantic locators ("button containing 'Upload'")
- ✅ Check services running before navigation
- ✅ Use auto-wait, not manual `sleep()`
- ✅ Take screenshots for human verification only (at end)

**DON'T**:
- ❌ Use screenshots for agent validation (agents can't parse images)
- ❌ Hard-code element refs (`ref="e5"` changes every render)
- ❌ Use CSS selectors (`.class` breaks on refactors)
- ❌ Skip pre-flight checks (browser installed, services running)
- ❌ Mix sync and async APIs

**See also**: [.claude/patterns/browser-validation.md](../patterns/browser-validation.md) for detailed patterns, examples, and gotchas.

---

## Common Workflows

### 1. After Implementation

```bash
# Validate implementation
claude --agent validation-gates "Validate user authentication feature: run tests, linting, and type checking"
```

### 2. Before PR Merge

```bash
# Comprehensive validation
claude --agent prp-exec-validator "Run all validation gates from prps/feature_name.md"
```

### 3. Frontend UI Testing

```bash
# End-to-end browser validation
claude --agent validation-gates "Validate RAG service UI at localhost:5173: test document upload and search workflows"
```

### 4. Full-Stack Testing

```bash
# Backend + frontend
claude --agent validation-gates "Validate task management:
- Backend: pytest tests/
- Frontend: localhost:5174 task creation workflow"
```

---

## How Agents Work

### Agent Structure

Each agent is a markdown file with YAML frontmatter:

```yaml
---
name: agent-name
description: "Agent purpose and capabilities"
tools: Bash, Read, Edit, Grep, browser_navigate, browser_snapshot
color: cyan  # Optional: for UI display
---

# Agent instructions
[Detailed instructions for agent behavior]
```

### Tool Access

Agents only have access to tools listed in their `tools:` field. Tools are comma-separated on a single line.

**Common tools**:
- `Bash` - Execute shell commands
- `Read` - Read files
- `Edit` - Edit files
- `Write` - Write new files
- `Grep` - Search files
- `Glob` - Find files by pattern
- `browser_*` - Browser automation tools (see above)

### Autonomous Operation

Agents work autonomously to complete tasks:
1. Parse task requirements
2. Execute operations (run tests, fix errors, validate)
3. Iterate until success or max attempts
4. Report results

**Key principle**: Agents are persistent. They don't give up after first failure - they analyze, fix, and retry.

---

## Browser Testing Integration

Browser validation fits at **Level 3: Integration Tests** in the quality-gates pattern:

```
Level 1: Syntax & Style (fast, ~5s)    - ruff, mypy
Level 2: Unit Tests (medium, ~30s)     - pytest unit tests
Level 3a: API Integration (medium, ~60s) - pytest integration tests
Level 3b: Browser Integration (slow, ~120s) - browser validation
```

**Performance**: Browser tests are 10x slower than API tests, but necessary for UI validation.

---

## Validation Reports

Agents create validation reports documenting results:

**Location**: `prps/validation-report.md` (prp-exec-validator)

**Contents**:
- Validation summary (all levels)
- Issues found and fixed
- Remaining issues (if any)
- Recommendations
- Final checklist

---

## Additional Resources

**Patterns**:
- [.claude/patterns/browser-validation.md](../patterns/browser-validation.md) - Complete browser testing pattern with examples and gotchas
- [.claude/patterns/quality-gates.md](../patterns/quality-gates.md) - Multi-level validation structure
- [.claude/patterns/README.md](../patterns/README.md) - Pattern library index

**PRP Examples**:
- `prps/playwright_agent_integration/` - Browser validation implementation
- `prps/playwright_agent_integration/examples/` - Copy-paste ready browser validation examples

**Documentation**:
- [Playwright Python Library](https://playwright.dev/python/docs/library) - Core API reference
- [Playwright Locators](https://playwright.dev/docs/locators) - Semantic element selection
- [Playwright Accessibility Testing](https://playwright.dev/docs/accessibility-testing) - Accessibility tree usage

---

**Last Updated**: 2025-10-14
**Browser Testing**: Added 2025-10-13 (Playwright integration)
