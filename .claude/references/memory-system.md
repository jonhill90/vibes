# Claude Code Memory System

Complete reference for Claude Code's memory system - persistent context that Claude sees across sessions.

## Memory Hierarchy

Claude Code offers five memory locations in a hierarchical structure. Files higher in the hierarchy take precedence and are loaded first.

| Memory Type | Location | Purpose | Shared With |
|-------------|----------|---------|-------------|
| **Managed policy** | macOS: `/Library/Application Support/ClaudeCode/CLAUDE.md`<br>Linux: `/etc/claude-code/CLAUDE.md`<br>Windows: `C:\Program Files\ClaudeCode\CLAUDE.md` | Organization-wide instructions managed by IT/DevOps | All users in organization |
| **Project memory** | `./CLAUDE.md` or `./.claude/CLAUDE.md` | Team-shared instructions for the project | Team members via source control |
| **Project rules** | `./.claude/rules/*.md` | Modular, topic-specific project instructions | Team members via source control |
| **User memory** | `~/.claude/CLAUDE.md` | Personal preferences for all projects | Just you (all projects) |
| **Project memory (local)** | `./CLAUDE.local.md` | Personal project-specific preferences | Just you (current project) |

All memory files are automatically loaded into Claude Code's context when launched.

## CLAUDE.md Locations

### Project Memory
Store project memory in either:
- `./CLAUDE.md` (project root)
- `./.claude/CLAUDE.md` (in .claude directory)

Both work the same way. Use `/init` to bootstrap a CLAUDE.md for your codebase.

### User Memory
Personal preferences that apply to all projects:
```
~/.claude/CLAUDE.md
```

### Local Memory (Git-Ignored)
Personal project-specific preferences that shouldn't be committed:
```
./CLAUDE.local.md
```

CLAUDE.local.md files are automatically added to .gitignore.

## Import Syntax

CLAUDE.md files can import additional files using `@path/to/import` syntax:

```markdown
See @README for project overview and @package.json for available npm commands.

# Additional Instructions
- git workflow @docs/git-instructions.md
```

### Import Rules
- Both relative and absolute paths are allowed
- Relative paths resolve relative to the file containing the import (not the working directory)
- Imported files can recursively import additional files (max-depth: 5 hops)
- Imports are not evaluated inside markdown code spans and code blocks
- First-time imports show an approval dialog

### Worktree Support
For multiple git worktrees, use home-directory imports so all worktrees share the same personal instructions:

```markdown
# Individual Preferences
- @~/.claude/my-project-instructions.md
```

## Modular Rules with .claude/rules/

For larger projects, organize instructions into multiple files using the `.claude/rules/` directory:

```
your-project/
├── .claude/
│   ├── CLAUDE.md           # Main project instructions
│   └── rules/
│       ├── code-style.md   # Code style guidelines
│       ├── testing.md      # Testing conventions
│       └── security.md     # Security requirements
```

All `.md` files in `.claude/rules/` are automatically loaded as project memory.

### Path-Specific Rules

Rules can be scoped to specific files using YAML frontmatter with the `paths` field:

```markdown
---
paths:
  - "src/api/**/*.ts"
---

# API Development Rules

- All API endpoints must include input validation
- Use the standard error response format
- Include OpenAPI documentation comments
```

Rules without a `paths` field are loaded unconditionally.

### Glob Patterns

The `paths` field supports standard glob patterns:

| Pattern | Matches |
|---------|---------|
| `**/*.ts` | All TypeScript files in any directory |
| `src/**/*` | All files under `src/` directory |
| `*.md` | Markdown files in the project root |
| `src/components/*.tsx` | React components in a specific directory |

Multiple patterns are supported:

```markdown
---
paths:
  - "src/**/*.ts"
  - "lib/**/*.ts"
  - "tests/**/*.test.ts"
---
```

Brace expansion works for matching multiple extensions:

```markdown
---
paths:
  - "src/**/*.{ts,tsx}"
  - "{src,lib}/**/*.ts"
---
```

### Rules Subdirectories

Rules can be organized into subdirectories:

```
.claude/rules/
├── frontend/
│   ├── react.md
│   └── styles.md
├── backend/
│   ├── api.md
│   └── database.md
└── general.md
```

All `.md` files are discovered recursively.

### Symlinks

The `.claude/rules/` directory supports symlinks for sharing rules across projects:

```bash
# Symlink a shared rules directory
ln -s ~/shared-claude-rules .claude/rules/shared

# Symlink individual rule files
ln -s ~/company-standards/security.md .claude/rules/security.md
```

### User-Level Rules

Personal rules that apply to all your projects:

```
~/.claude/rules/
├── preferences.md    # Your personal coding preferences
└── workflows.md      # Your preferred workflows
```

User-level rules are loaded before project rules, giving project rules higher priority.

## How Claude Looks Up Memories

Claude Code reads memories recursively:
1. Starting in the current working directory
2. Recurses up to (but not including) the root directory `/`
3. Reads any CLAUDE.md or CLAUDE.local.md files it finds

This is convenient for monorepos where you run Claude Code in `foo/bar/` and have memories in both `foo/CLAUDE.md` and `foo/bar/CLAUDE.md`.

### Nested Discovery

Claude also discovers CLAUDE.md files nested in subtrees under your current working directory. Instead of loading them at launch, they are only included when Claude reads files in those subtrees.

### Additional Directories

The `--add-dir` flag gives Claude access to additional directories. To also load memory files from these directories, set:

```bash
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1 claude --add-dir ../shared-config
```

## Organization-Level Memory

Organizations can deploy centrally managed CLAUDE.md files that apply to all users:

1. Create the managed memory file at the **Managed policy** location
2. Deploy via configuration management system (MDM, Group Policy, Ansible, etc.)

## Commands

- `/memory` - Open any memory file in your system editor
- `/init` - Bootstrap a CLAUDE.md for your codebase

## Best Practices

1. **Be specific**: "Use 2-space indentation" is better than "Format code properly"
2. **Use structure**: Format memories as bullet points under descriptive markdown headings
3. **Review periodically**: Update memories as your project evolves
4. **Keep it focused**: Each rule file should cover one topic
5. **Use descriptive filenames**: The filename should indicate what the rules cover
6. **Use conditional rules sparingly**: Only add `paths` frontmatter when rules truly apply to specific file types
7. **Organize with subdirectories**: Group related rules (e.g., `frontend/`, `backend/`)
