# Source: .claude/agents/validation-gates.md (lines 1-7)
# Pattern: Agent YAML frontmatter with tool list configuration
# Extracted: 2025-10-13
# Relevance: 10/10 - Exact pattern needed for adding browser tools

```markdown
---
name: validation-gates
description: "Testing and validation specialist. Proactively runs tests, validates code changes, ensures quality gates are met, and iterates on fixes until all tests pass. Call this agent after you implement features and need to validate that they were implemented correctly. Be very specific with the features that were implemented and a general idea of what needs to be tested."
tools: Bash, Read, Edit, MultiEdit, Grep, Glob, TodoWrite
---
```

## What This Demonstrates

This is the **YAML frontmatter format** used by all agent markdown files in `.claude/agents/`. It defines:

1. **name**: Agent identifier (kebab-case)
2. **description**: What the agent does and when to use it
3. **tools**: Comma-separated list of available tools

## How to Add Browser Tools

To add Playwright browser tools, simply extend the `tools:` line:

```markdown
---
name: validation-gates
description: "Testing and validation specialist. Proactively runs tests, validates code changes (backend + frontend UI), ensures quality gates are met, and iterates on fixes until all tests pass. Can perform browser automation for end-to-end testing."
tools: Bash, Read, Edit, MultiEdit, Grep, Glob, TodoWrite, mcp__MCP_DOCKER__browser_navigate, mcp__MCP_DOCKER__browser_snapshot, mcp__MCP_DOCKER__browser_click, mcp__MCP_DOCKER__browser_type, mcp__MCP_DOCKER__browser_take_screenshot, mcp__MCP_DOCKER__browser_evaluate, mcp__MCP_DOCKER__browser_wait_for, mcp__MCP_DOCKER__browser_fill_form, mcp__MCP_DOCKER__browser_tabs, mcp__MCP_DOCKER__browser_install
---
```

## Critical Details

1. **Tool Names**: Must match EXACT MCP server export names
   - MCP_DOCKER browser tools: `mcp__MCP_DOCKER__browser_*`
   - Case-sensitive - must be exact

2. **Comma-Separated**: Tools separated by `, ` (comma + space)

3. **No Line Breaks**: All tools on single line (YAML limitation)

4. **Description Update**: Mention new capabilities ("backend + frontend UI")

5. **Declarative Access**: Just listing tools grants access - no code changes needed
