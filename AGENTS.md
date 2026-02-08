# AGENTS.md

## Project

Vibes — a conversational development environment for agent skills, subagents, and documentation.

This file is the single source of truth for all AI coding assistants.
Chain: `AGENTS.md` (source) ← `CLAUDE.md` (symlink) ← `.github/copilot-instructions.md` (symlink to AGENTS.md)

---

## Fresh Information First

**Do not rely on training data for APIs, SDKs, or framework patterns.**

Always check live documentation before writing code:

| MCP Server | Use For |
|------------|---------|
| **context7** | Library and framework documentation (npm, PyPI, crates, etc.) |
| **microsoft-learn** | Microsoft, Azure, .NET, and M365 documentation |
| **deepwiki** | GitHub repository documentation and wikis |

Skills and agent patterns evolve — verify against current docs, not memory.

---

## Core Principles

### 1. Think Before Coding

- Surface assumptions explicitly — don't hide confusion
- Present tradeoffs when multiple approaches exist
- Ask clarifying questions before implementing ambiguous requests
- Plan complex changes before touching code

### 2. Simplicity First

- Write the minimum code that solves the problem
- No speculative features, no "just in case" abstractions
- If you're overcomplicating it, rewrite — don't patch
- Three similar lines beat a premature abstraction

### 3. Surgical Changes

- Touch only what's needed to accomplish the task
- Match existing code style — indentation, naming, patterns
- Don't refactor adjacent code, add docstrings, or "improve" untouched files
- A bug fix doesn't need surrounding cleanup

### 4. Goal-Driven Execution

- Define success criteria before starting
- Verify your work — run tests, check output, validate behavior
- Loop until the task is actually done, not just attempted
- If blocked, try a different approach before asking for help

---

## Repository Structure

```
vibes/
├── AGENTS.md                          # Source of truth (this file)
├── CLAUDE.md → AGENTS.md              # Symlink for Claude Code
├── .mcp.json                          # MCP server configuration
│
├── .github/                           # Source of truth for all content
│   ├── skills/                        # Skill source directories
│   │   ├── context7-py/SKILL.md
│   │   ├── context7-sh/SKILL.md
│   │   ├── context7-ps/SKILL.md
│   │   └── ms-learn/SKILL.md
│   ├── agents/                        # Agent definitions
│   │   ├── code-reviewer.md
│   │   └── researcher.md
│   ├── copilot-instructions.md → ../AGENTS.md   # Symlink for Copilot
│   ├── instructions/                  # Copilot scoped instructions
│   │   ├── skill-authoring.instructions.md
│   │   ├── agent-authoring.instructions.md
│   │   ├── documentation.instructions.md
│   │   ├── testing.instructions.md
│   │   └── reference-freshness.instructions.md
│   ├── docs/                          # Platform-agnostic reference docs
│   │   ├── context-engineering.md
│   │   ├── best-practices.md
│   │   └── tdd-workflow.md
│   ├── plugins/
│   └── prompts/
│
├── .claude/                           # Claude Code platform directory
│   ├── skills → ../.github/skills     # Symlink
│   ├── agents → ../.github/agents     # Symlink
│   ├── references/                    # Knowledge docs (mixed)
│   │   ├── context-engineering.md → ../../.github/docs/context-engineering.md
│   │   ├── best-practices.md → ../../.github/docs/best-practices.md
│   │   ├── tdd-workflow.md → ../../.github/docs/tdd-workflow.md
│   │   ├── skills-guide.md            # Claude-specific
│   │   ├── hooks-guide.md             # Claude-specific
│   │   ├── memory-system.md           # Claude-specific
│   │   └── ...
│   └── rules/                         # Claude Code-specific path rules
│       ├── skill-authoring.md
│       ├── agent-authoring.md
│       ├── documentation.md
│       ├── testing.md
│       └── reference-freshness.md
│
├── .codex/                            # Codex CLI platform directory
│   ├── agents → ../.github/agents     # Symlink
│   ├── skills → ../.github/skills     # Symlink
│   └── config.toml                    # MCP servers, approval policy, sandbox
│
└── skills/                            # Categorized browsing view
    ├── python/
    ├── bash/
    └── powershell/
```

### Architecture

- **`.github/`** is the source of truth for all skills, agents, plugins, and prompts
- **`.claude/`** and **`.codex/`** contain symlinks back to `.github/`
- **`CLAUDE.md`** symlinks to `AGENTS.md` — Claude Code reads the same source
- **`.github/copilot-instructions.md`** symlinks to `AGENTS.md` — GitHub Copilot gets the same guidance
- **`skills/`** at the repo root provides categorized language-based browsing via symlinks
- **`.github/docs/`** holds platform-agnostic reference docs (context engineering, best practices, TDD)
- **`.claude/references/`** holds Claude-specific knowledge + symlinks to agnostic docs from `.github/docs/`
- **`.claude/rules/`** holds path-specific authoring rules for Claude Code (`paths:` frontmatter)
- **`.github/instructions/`** holds scoped instruction files for GitHub Copilot (`applyTo:` frontmatter)
- **`.codex/config.toml`** configures MCP servers, approval policy, and sandbox mode for Codex CLI
- **`AGENTS.md`** is read natively by Codex CLI from the project root (no symlink needed)
- **`AGENTS.override.md`** (git-ignored) provides local Codex overrides, analogous to `CLAUDE.local.md`

---

## Conventions

### Skill Naming

- Source directory: `.github/skills/{name}-{lang}/` (e.g., `context7-py`, `context7-sh`)
- Each directory contains a `SKILL.md` file
- Language variants get separate skill directories — one per language (py, sh, ps)
- Categorized symlinks: `skills/{language}/{short-name}` → `../../.github/skills/{full-name}`

### Agent Naming

- File: `.github/agents/{name}.md` (e.g., `code-reviewer.md`)
- Use kebab-case for filenames
- Agent files combine YAML frontmatter (config) + markdown body (system prompt)

### SKILL.md Authoring

- **Frontmatter**: `name` and `description` are required; description is the PRIMARY trigger
- **Description**: Include "when to use" context — this is how the agent decides to invoke the skill
- **Body**: Imperative form ("Run tests" not "Running tests")
- **Size**: Keep under 500 lines — use progressive disclosure for detail
- **References**: Move detailed content to separate files, link from SKILL.md
- **Examples**: Prefer concise examples over verbose explanations

### SKILL.md Frontmatter Features

| Field | Purpose |
|-------|---------|
| `name` | Skill identifier (required) |
| `description` | Trigger text — when to use (required) |
| `context: fork` | Isolated execution context |
| `allowed-tools` | Restrict available tools |
| `disable-model-invocation: true` | Manual-only activation |
| `$ARGUMENTS`, `$0`, `$1` | Dynamic content injection |
| `` !`command` `` | Dynamic context from shell commands |

---

## MCP Servers

This repository uses three MCP servers for fresh documentation:

### context7

Fetches up-to-date library and framework documentation.

```
Use: /context7 or resolve-library-id + get-library-docs
When: Working with any library, framework, or SDK
```

### microsoft-learn

Queries official Microsoft documentation.

```
Use: /ms-learn or microsoft_learn_search
When: Azure, .NET, M365, Windows, or any Microsoft technology
```

### deepwiki

Fetches GitHub repository documentation and wikis.

```
Use: deepwiki tools
When: Understanding a GitHub project's architecture or API
```

---

## Clean Code Checklist

Before committing any skill, agent, or documentation change:

- [ ] **Does it work?** — Tested, verified, produces expected output
- [ ] **Is it simple?** — No unnecessary abstraction or indirection
- [ ] **Is it focused?** — Does one thing well
- [ ] **Does it match existing patterns?** — Naming, structure, style
- [ ] **Would another agent understand it?** — Clear description, obvious purpose

---

## Do's and Don'ts

### Do

- Use MCP tools for fresh documentation before writing code
- Write focused skills that do one thing well
- Test and verify before committing
- Ask clarifying questions when requirements are ambiguous
- Use progressive disclosure — core workflow in SKILL.md, details in reference files
- Match the naming conventions: `{name}-{lang}` for skills, `kebab-case.md` for agents

### Don't

- Rely on training data for API signatures, SDK methods, or configuration formats
- Create monolithic skills that try to do everything
- Skip validation — always verify skills activate correctly
- Add features that weren't requested
- Modify files outside the scope of the current task
- Commit without reviewing changes

---

## Success Indicators

You're doing it right when:

- **Fewer unnecessary file changes** — only touched files are relevant to the task
- **Clarifying questions come first** — ambiguity is resolved before implementation
- **Skills auto-activate correctly** — descriptions trigger on the right queries
- **Clean, focused commits** — each commit does one thing
- **Fresh docs are used** — MCP tools are invoked before writing integration code

---

## Workflow

Use Claude Code's built-in plan mode for feature planning and implementation.

1. **Explore** — understand the current state before proposing changes
2. **Plan** — surface tradeoffs and get alignment
3. **Implement** — make surgical, focused changes
4. **Verify** — test, validate, review
5. **Commit** — clean, descriptive commit messages
