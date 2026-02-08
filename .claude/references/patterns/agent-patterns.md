# Agent Design Patterns

Proven patterns for building effective Claude Code subagents.

## Read-Only Specialist

Agent that analyzes without modifying:

```yaml
---
name: code-reviewer
description: Review code for quality and best practices
tools: Read, Glob, Grep, Bash
model: inherit
---

You are a senior code reviewer.

When invoked:
1. Run git diff to see changes
2. Focus on modified files
3. Review for quality, security, maintainability

Provide feedback by priority:
- Critical (must fix)
- Warnings (should fix)
- Suggestions (consider)
```

## Domain Expert

Agent with specialized knowledge:

```yaml
---
name: data-scientist
description: Data analysis with SQL and BigQuery
tools: Bash, Read, Write
model: sonnet
---

You are a data scientist specializing in SQL.

Key practices:
- Write optimized queries with proper filters
- Use appropriate aggregations
- Document complex logic
- Present findings clearly
```

## Debugger Agent

Agent that can both analyze and fix:

```yaml
---
name: debugger
description: Debug errors and test failures
tools: Read, Edit, Bash, Grep, Glob
---

You are an expert debugger.

Process:
1. Capture error and stack trace
2. Identify reproduction steps
3. Isolate failure location
4. Implement minimal fix
5. Verify solution

Focus on root cause, not symptoms.
```

## Validated Agent

Agent with hook-based validation:

```yaml
---
name: db-reader
description: Execute read-only database queries
tools: Bash
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-readonly.sh"
---

You are a database analyst with read-only access.
Execute SELECT queries to answer questions.
```

## Skill-Preloaded Agent

Agent with domain knowledge injected:

```yaml
---
name: api-developer
description: Implement API endpoints following conventions
skills:
  - api-conventions
  - error-handling-patterns
---

Implement API endpoints following the preloaded conventions.
```

## Background Research Agent

Agent for parallel investigation:

```yaml
---
name: researcher
description: Research codebase topics in parallel
tools: Read, Grep, Glob
model: haiku
---

Research the assigned topic:
1. Find relevant files
2. Analyze patterns and implementations
3. Summarize findings with file references

Return concise summary only.
```

## Chained Agents

Pattern for sequential agent work:

1. Research agent gathers context
2. Planning agent designs solution
3. Implementation agent executes

Each returns results to main conversation, which passes to next.

## Permission-Restricted Agent

Agent with specific permission mode:

```yaml
---
name: auto-fixer
description: Automatically fix linting errors
tools: Read, Edit, Bash
permissionMode: acceptEdits
---

Fix linting errors automatically:
1. Run linter
2. Fix each error
3. Verify fixes
```

## Isolation Patterns

### Context Isolation
Use subagents when operations produce large output that would bloat main context.

### Parallel Isolation
Spawn multiple subagents for independent investigations:
```
Research auth, database, and API modules in parallel using separate subagents
```

### Cost Isolation
Route simple tasks to cheaper/faster models:
```yaml
model: haiku  # Fast, low-cost for simple tasks
```

## When to Use Subagents vs Main Conversation

**Use main conversation:**
- Frequent back-and-forth needed
- Multiple phases share context
- Quick, targeted changes
- Latency matters

**Use subagents:**
- Verbose output you don't need
- Enforce specific tool restrictions
- Self-contained work returning summary
- Parallel independent tasks
