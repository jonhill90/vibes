# Memory Design Patterns

Proven patterns for organizing Claude Code memory files.

## Modular Rules Organization

Split large CLAUDE.md into focused rule files:

```
.claude/
├── CLAUDE.md           # Core project info
└── rules/
    ├── code-style.md   # Formatting, naming
    ├── testing.md      # Test conventions
    ├── security.md     # Security requirements
    └── architecture.md # Design patterns
```

## Path-Specific Rules

Apply rules only to matching files:

```yaml
---
paths:
  - "src/api/**/*.ts"
---

# API Rules

- All endpoints must validate input
- Use standard error format
- Include OpenAPI comments
```

```yaml
---
paths:
  - "**/*.test.ts"
  - "**/*.spec.ts"
---

# Testing Rules

- Use describe/it structure
- Mock external dependencies
- Test edge cases
```

## Frontend/Backend Split

Organize by domain:

```
.claude/rules/
├── frontend/
│   ├── react.md
│   ├── styles.md
│   └── state.md
├── backend/
│   ├── api.md
│   ├── database.md
│   └── auth.md
└── shared/
    └── conventions.md
```

## Language-Specific Rules

```yaml
---
paths:
  - "**/*.ts"
  - "**/*.tsx"
---

# TypeScript Rules

- Use strict mode
- Explicit return types for public functions
- Avoid `any`, use `unknown`
- Prefer type over interface
```

```yaml
---
paths:
  - "**/*.py"
---

# Python Rules

- Use type hints
- Follow PEP 8
- Docstrings for public functions
```

## Monorepo Pattern

Nested CLAUDE.md for package-specific context:

```
monorepo/
├── CLAUDE.md           # Root conventions
├── packages/
│   ├── frontend/
│   │   └── CLAUDE.md   # Frontend-specific
│   ├── backend/
│   │   └── CLAUDE.md   # Backend-specific
│   └── shared/
│       └── CLAUDE.md   # Shared library rules
```

Claude discovers nested CLAUDE.md when working in those directories.

## Import Pattern

Keep CLAUDE.md lean with imports:

```markdown
# Project

See @README.md for overview.
See @package.json for commands.

## Architecture
@docs/architecture.md

## API Reference
@docs/api.md
```

## Personal Preferences Pattern

Use CLAUDE.local.md for individual settings:

```markdown
# My Preferences

## Editor
- I use VS Code
- Prefer 2-space indent
- Dark theme examples

## Workflow
- My test data: fixtures/my-data/
- Local API: http://localhost:3001
```

CLAUDE.local.md is auto-gitignored.

## Worktree Sharing

For multiple git worktrees, use home imports:

```markdown
# Individual Preferences
@~/.claude/my-project-instructions.md
```

All worktrees share the same instructions.

## Shared Rules via Symlinks

```bash
# Share security rules across projects
ln -s ~/company-standards/security.md .claude/rules/security.md

# Share entire rules directory
ln -s ~/shared-claude-rules .claude/rules/shared
```

## User-Level Rules

Personal rules for all projects:

```
~/.claude/rules/
├── preferences.md    # Coding style
├── workflows.md      # Common workflows
└── shortcuts.md      # Personal shortcuts
```

## Team vs Personal Split

**Team (committed):**
- `.claude/CLAUDE.md` - Project conventions
- `.claude/rules/` - Shared rules

**Personal (not committed):**
- `CLAUDE.local.md` - Personal preferences
- `~/.claude/CLAUDE.md` - Global preferences
- `~/.claude/rules/` - Personal rules

## Hierarchy Usage

| Need | Use |
|------|-----|
| Org-wide standards | Managed policy |
| Project conventions | .claude/CLAUDE.md |
| Topic-specific rules | .claude/rules/*.md |
| Personal global prefs | ~/.claude/CLAUDE.md |
| Personal project prefs | CLAUDE.local.md |

## Best Practices

1. **Keep focused** - One topic per rule file
2. **Be specific** - "Use 2-space indent" not "Format properly"
3. **Use paths sparingly** - Only when rules truly apply to specific files
4. **Organize by domain** - Group related rules
5. **Review periodically** - Update as project evolves
6. **Don't duplicate** - Reference other files with imports
