---
description: 'Guidelines for writing and editing agent definition files'
applyTo: '.github/agents/**/*.md'
---

# Agent Authoring Rules

When writing or editing subagent markdown files:

## Structure
- YAML frontmatter for configuration
- Markdown body is the system prompt

## Required Frontmatter
- `name`: Unique identifier (lowercase, hyphens)
- `description`: When the agent should be delegated to

## Optional Frontmatter
- `tools`: Allowlist of tools as a **YAML array** (inherits all if omitted)
- `disallowedTools`: Denylist as a **YAML array**
- `model`: `sonnet`, `opus`, `haiku`, or `inherit`
- `permissionMode`: Permission handling
- `skills`: Skills to preload into context
- `hooks`: Lifecycle hooks

## Tools Syntax

The `tools` and `disallowedTools` fields **must be YAML arrays**, not comma-separated strings.

```yaml
# Correct
tools:
  - Read
  - Grep
  - Glob

# Wrong — will error: "The 'tools' attribute must be an array"
tools: Read, Grep, Glob
```

## System Prompt Guidelines
- Be clear about agent's role and purpose
- Include step-by-step workflow when applicable
- Specify output format expectations
- Keep focused on one specific task

## Tool Restrictions
- Grant only necessary permissions
- Use `disallowedTools` for read-only agents
- Common read-only set: `[Read, Grep, Glob, Bash]`
