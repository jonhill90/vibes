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
- `tools`: Allowlist of tools (inherits all if omitted)
- `disallowedTools`: Denylist to remove from inherited
- `model`: `sonnet`, `opus`, `haiku`, or `inherit`
- `permissionMode`: Permission handling
- `skills`: Skills to preload into context
- `hooks`: Lifecycle hooks

## System Prompt Guidelines
- Be clear about agent's role and purpose
- Include step-by-step workflow when applicable
- Specify output format expectations
- Keep focused on one specific task

## Tool Restrictions
- Grant only necessary permissions
- Use `disallowedTools` for read-only agents
- Common read-only set: `Read, Grep, Glob, Bash`
