# CLAUDE.md

## Project

Vibes — a conversational development environment.

## Structure

`.github/` is the source of truth for all skills, agents, plugins, and prompts.

Platform directories symlink to `.github/`:
- `.claude/skills` → `.github/skills`
- `.claude/agents` → `.github/agents`
- `AGENTS.md` → `CLAUDE.md`

GitHub Copilot discovers `.github/` natively.

## Workflow

Use Claude Code's built-in plan mode for feature planning and implementation.
