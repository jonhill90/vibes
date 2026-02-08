# Claude Code Skills Guide

Complete reference for Claude Code skills - reusable knowledge and workflows that extend Claude's capabilities.

## What Are Skills?

Skills are modular packages that teach Claude how to perform specific tasks. Create a `SKILL.md` file with instructions, and Claude adds it to its toolkit. Claude uses skills when relevant, or you can invoke one directly with `/skill-name`.

Skills follow the [Agent Skills](https://agentskills.io) open standard with Claude Code extensions.

## Skill Locations

| Location | Path | Applies to |
|----------|------|------------|
| Enterprise | See managed settings | All users in organization |
| Personal | `~/.claude/skills/<skill-name>/SKILL.md` | All your projects |
| Project | `.claude/skills/<skill-name>/SKILL.md` | This project only |
| Plugin | `<plugin>/skills/<skill-name>/SKILL.md` | Where plugin is enabled |

When skills share the same name, higher-priority locations win: enterprise > personal > project.

### Automatic Discovery

Claude Code automatically discovers skills from nested `.claude/skills/` directories. If you're editing a file in `packages/frontend/`, Claude also looks for skills in `packages/frontend/.claude/skills/`.

## Skill Structure

Each skill is a directory with `SKILL.md` as the entrypoint:

```
my-skill/
├── SKILL.md           # Main instructions (required)
├── reference.md       # Detailed docs (loaded on demand)
├── examples.md        # Example outputs
├── scripts/           # Executable scripts
│   └── helper.py
└── assets/            # Templates, images for output
    └── template.json
```

Keep `SKILL.md` under 500 lines. Move detailed reference material to separate files.

## SKILL.md Format

```yaml
---
name: my-skill
description: What this skill does and when to use it
---

Your skill instructions here...
```

### Frontmatter Fields

All fields are optional except `description` (recommended).

| Field | Description |
|-------|-------------|
| `name` | Display name (defaults to directory name). Lowercase letters, numbers, hyphens only (max 64 chars) |
| `description` | What the skill does and when to use it. Claude uses this to decide when to apply the skill |
| `argument-hint` | Hint shown during autocomplete. Example: `[issue-number]` or `[filename] [format]` |
| `disable-model-invocation` | Set `true` to prevent Claude from auto-loading. Only you can invoke with `/name` |
| `user-invocable` | Set `false` to hide from `/` menu. Only Claude can invoke |
| `allowed-tools` | Tools Claude can use without asking permission when skill is active |
| `model` | Model to use when skill is active |
| `context` | Set to `fork` to run in a forked subagent context |
| `agent` | Which subagent type to use when `context: fork` is set |
| `hooks` | Hooks scoped to this skill's lifecycle |

## String Substitutions

Skills support dynamic values in content:

| Variable | Description |
|----------|-------------|
| `$ARGUMENTS` | All arguments passed when invoking. If not present, appended as `ARGUMENTS: <value>` |
| `$ARGUMENTS[N]` | Specific argument by 0-based index (`$ARGUMENTS[0]` for first) |
| `$N` | Shorthand for `$ARGUMENTS[N]` (`$0` for first, `$1` for second) |
| `${CLAUDE_SESSION_ID}` | Current session ID for logging or session-specific files |

### Example

```yaml
---
name: migrate-component
description: Migrate a component from one framework to another
---

Migrate the $0 component from $1 to $2.
Preserve all existing behavior and tests.
```

Running `/migrate-component SearchBar React Vue` replaces `$0` with `SearchBar`, `$1` with `React`, `$2` with `Vue`.

## Dynamic Context Injection

The `!`command`` syntax runs shell commands before the skill content is sent to Claude:

```yaml
---
name: pr-summary
description: Summarize changes in a pull request
context: fork
agent: Explore
allowed-tools: Bash(gh *)
---

## Pull request context
- PR diff: !`gh pr diff`
- PR comments: !`gh pr view --comments`
- Changed files: !`gh pr diff --name-only`

## Your task
Summarize this pull request...
```

Each `!`command`` executes immediately, and output replaces the placeholder. This is preprocessing - Claude only sees the final result.

## Invocation Control

By default, both you and Claude can invoke any skill.

### disable-model-invocation: true

Only you can invoke the skill. Use for workflows with side effects:

```yaml
---
name: deploy
description: Deploy the application to production
disable-model-invocation: true
---
```

### user-invocable: false

Only Claude can invoke the skill. Use for background knowledge:

```yaml
---
name: legacy-system-context
description: Context about the legacy system
user-invocable: false
---
```

### Invocation Matrix

| Frontmatter | You can invoke | Claude can invoke | Context loading |
|-------------|----------------|-------------------|-----------------|
| (default) | Yes | Yes | Description always, full on invoke |
| `disable-model-invocation: true` | Yes | No | Not in context until you invoke |
| `user-invocable: false` | No | Yes | Description always, full on invoke |

## Restrict Tool Access

Limit which tools Claude can use when a skill is active:

```yaml
---
name: safe-reader
description: Read files without making changes
allowed-tools: Read, Grep, Glob
---
```

## Run Skills in Subagents

Add `context: fork` to run in isolation. The skill content becomes the prompt that drives the subagent:

```yaml
---
name: deep-research
description: Research a topic thoroughly
context: fork
agent: Explore
---

Research $ARGUMENTS thoroughly:

1. Find relevant files using Glob and Grep
2. Read and analyze the code
3. Summarize findings with specific file references
```

The `agent` field specifies which subagent: `Explore`, `Plan`, `general-purpose`, or custom agents from `.claude/agents/`.

**Warning**: `context: fork` only makes sense for skills with explicit instructions. Guidelines without a task will return without meaningful output.

## Supporting Files

Reference supporting files from SKILL.md so Claude knows what each file contains:

```markdown
## Additional resources

- For complete API details, see [reference.md](reference.md)
- For usage examples, see [examples.md](examples.md)
```

Claude reads reference files on demand (progressive disclosure).

## Hooks in Skills

Define hooks that run while a skill is active:

```yaml
---
name: secure-operations
description: Perform operations with security checks
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/security-check.sh"
---
```

## Skill Types

### Reference Skills
Add knowledge Claude applies to current work:

```yaml
---
name: api-conventions
description: API design patterns for this codebase
---

When writing API endpoints:
- Use RESTful naming conventions
- Return consistent error formats
- Include request validation
```

### Task Skills
Step-by-step instructions for specific actions:

```yaml
---
name: deploy
description: Deploy the application to production
context: fork
disable-model-invocation: true
---

Deploy the application:
1. Run the test suite
2. Build the application
3. Push to the deployment target
```

## Extended Thinking

To enable extended thinking in a skill, include the word "ultrathink" anywhere in your skill content.

## Troubleshooting

### Skill not triggering
1. Check description includes keywords users would naturally say
2. Verify skill appears in "What skills are available?"
3. Try invoking directly with `/skill-name`

### Skill triggers too often
1. Make description more specific
2. Add `disable-model-invocation: true` for manual-only

### Claude doesn't see all skills
Skill descriptions may exceed character budget (default 15,000). Run `/context` to check for warnings. Set `SLASH_COMMAND_TOOL_CHAR_BUDGET` to increase.

## Distribution

- **Project skills**: Commit `.claude/skills/` to version control
- **Plugins**: Create a `skills/` directory in your plugin
- **Managed**: Deploy organization-wide through managed settings
