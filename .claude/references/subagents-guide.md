# Claude Code Subagents Guide

Complete reference for Claude Code subagents - specialized AI assistants that handle specific types of tasks.

## What Are Subagents?

Subagents are specialized AI assistants that handle specific types of tasks. Each subagent runs in its own context window with a custom system prompt, specific tool access, and independent permissions.

### Benefits
- **Preserve context** - Keep exploration out of your main conversation
- **Enforce constraints** - Limit which tools a subagent can use
- **Reuse configurations** - Share subagents across projects
- **Specialize behavior** - Focused system prompts for specific domains
- **Control costs** - Route tasks to faster, cheaper models like Haiku

## Built-in Subagents

### Explore
Fast, read-only agent optimized for searching and analyzing codebases.
- **Model**: Haiku (fast, low-latency)
- **Tools**: Read-only (denied Write and Edit)
- **Purpose**: File discovery, code search, codebase exploration
- **Thoroughness levels**: quick, medium, very thorough

### Plan
Research agent used during plan mode to gather context before presenting a plan.
- **Model**: Inherits from main conversation
- **Tools**: Read-only (denied Write and Edit)
- **Purpose**: Codebase research for planning

### general-purpose
Capable agent for complex, multi-step tasks requiring both exploration and action.
- **Model**: Inherits from main conversation
- **Tools**: All tools
- **Purpose**: Complex research, multi-step operations, code modifications

### Other Built-in Agents
- **Bash** - Running terminal commands in separate context
- **statusline-setup** - Configuring status line
- **Claude Code Guide** - Answering questions about Claude Code features

## Custom Subagents

### Locations

| Location | Scope | Priority |
|----------|-------|----------|
| `--agents` CLI flag | Current session | 1 (highest) |
| `.claude/agents/` | Current project | 2 |
| `~/.claude/agents/` | All your projects | 3 |
| Plugin's `agents/` directory | Where plugin is enabled | 4 (lowest) |

### Creating a Subagent

Use `/agents` command for interactive creation, or create markdown files manually:

```markdown
---
name: code-reviewer
description: Reviews code for quality and best practices
tools:
  - Read
  - Glob
  - Grep
model: sonnet
---

You are a code reviewer. When invoked, analyze the code and provide
specific, actionable feedback on quality, security, and best practices.
```

### Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique identifier using lowercase letters and hyphens |
| `description` | Yes | When Claude should delegate to this subagent |
| `tools` | No | Tools the subagent can use (inherits all if omitted) |
| `disallowedTools` | No | Tools to deny, removed from inherited list |
| `model` | No | `sonnet`, `opus`, `haiku`, or `inherit` (default) |
| `permissionMode` | No | `default`, `acceptEdits`, `dontAsk`, `bypassPermissions`, or `plan` |
| `skills` | No | Skills to preload into the subagent's context |
| `hooks` | No | Lifecycle hooks scoped to this subagent |

### CLI-Defined Subagents

Pass JSON when launching Claude Code:

```bash
claude --agents '{
  "code-reviewer": {
    "description": "Expert code reviewer. Use proactively after code changes.",
    "prompt": "You are a senior code reviewer. Focus on code quality, security, and best practices.",
    "tools": ["Read", "Grep", "Glob", "Bash"],
    "model": "sonnet"
  }
}'
```

## Tool Restrictions

### Allowlist (tools)
```yaml
---
name: safe-researcher
description: Research agent with restricted capabilities
tools:
  - Read
  - Grep
  - Glob
  - Bash
---
```

### Denylist (disallowedTools)
```yaml
---
name: read-only-agent
tools:
  - Read
  - Grep
  - Glob
  - Bash
disallowedTools:
  - Write
  - Edit
---
```

## Permission Modes

| Mode | Behavior |
|------|----------|
| `default` | Standard permission checking with prompts |
| `acceptEdits` | Auto-accept file edits |
| `dontAsk` | Auto-deny permission prompts |
| `bypassPermissions` | Skip all permission checks (use with caution) |
| `plan` | Plan mode (read-only exploration) |

## Preloading Skills

Inject skill content into subagent's context at startup:

```yaml
---
name: api-developer
description: Implement API endpoints following team conventions
skills:
  - api-conventions
  - error-handling-patterns
---

Implement API endpoints. Follow the conventions and patterns from the preloaded skills.
```

Full skill content is injected, not just made available. Subagents don't inherit skills from parent conversation.

## Hooks in Subagents

Define hooks that run while a subagent is active:

```yaml
---
name: code-reviewer
description: Review code changes with automatic linting
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-command.sh"
  PostToolUse:
    - matcher: "Edit|Write"
      hooks:
        - type: command
          command: "./scripts/run-linter.sh"
---
```

## Foreground vs Background

- **Foreground**: Block main conversation until complete. Permission prompts passed through.
- **Background**: Run concurrently while you continue working. Permissions pre-approved upfront.

Press **Ctrl+B** to background a running task.

## Resuming Subagents

Subagents retain full conversation history. To continue previous work:

```
Continue that code review and now analyze the authorization logic
```

## Disabling Subagents

Add to deny rules in permissions:

```json
{
  "permissions": {
    "deny": ["Task(Explore)", "Task(my-custom-agent)"]
  }
}
```

Or via CLI:
```bash
claude --disallowedTools "Task(Explore)"
```

## Example Subagents

### Code Reviewer (Read-Only)
```markdown
---
name: code-reviewer
description: Expert code review specialist. Proactively reviews code for quality, security, and maintainability.
tools:
  - Read
  - Grep
  - Glob
  - Bash
model: inherit
---

You are a senior code reviewer ensuring high standards of code quality and security.

When invoked:
1. Run git diff to see recent changes
2. Focus on modified files
3. Begin review immediately

Review checklist:
- Code is clear and readable
- Functions and variables are well-named
- No duplicated code
- Proper error handling
- No exposed secrets or API keys
- Input validation implemented
- Good test coverage

Provide feedback organized by priority:
- Critical issues (must fix)
- Warnings (should fix)
- Suggestions (consider improving)
```

### Debugger
```markdown
---
name: debugger
description: Debugging specialist for errors, test failures, and unexpected behavior.
tools:
  - Read
  - Edit
  - Bash
  - Grep
  - Glob
---

You are an expert debugger specializing in root cause analysis.

When invoked:
1. Capture error message and stack trace
2. Identify reproduction steps
3. Isolate the failure location
4. Implement minimal fix
5. Verify solution works

For each issue, provide:
- Root cause explanation
- Evidence supporting the diagnosis
- Specific code fix
- Testing approach
- Prevention recommendations
```

### Data Scientist
```markdown
---
name: data-scientist
description: Data analysis expert for SQL queries, BigQuery operations, and data insights.
tools:
  - Bash
  - Read
  - Write
model: sonnet
---

You are a data scientist specializing in SQL and BigQuery analysis.

When invoked:
1. Understand the data analysis requirement
2. Write efficient SQL queries
3. Use BigQuery command line tools (bq) when appropriate
4. Analyze and summarize results
5. Present findings clearly

Always ensure queries are efficient and cost-effective.
```

## Auto-Compaction

Subagents support automatic compaction using the same logic as the main conversation. By default, auto-compaction triggers at approximately 95% capacity.

To trigger compaction earlier, set the environment variable:

```bash
CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=50 claude
```

### Transcript Storage

Subagent transcripts are stored separately from the main conversation:

```
~/.claude/projects/{project}/{sessionId}/subagents/agent-{agentId}.jsonl
```

Transcripts persist independently:
- **Main conversation compaction**: Subagent transcripts are unaffected
- **Session persistence**: Can resume subagents after restarting Claude Code
- **Automatic cleanup**: Based on `cleanupPeriodDays` setting (default: 30 days)

## Best Practices

1. **Design focused subagents** - Each should excel at one specific task
2. **Write detailed descriptions** - Claude uses description to decide when to delegate
3. **Limit tool access** - Grant only necessary permissions
4. **Check into version control** - Share project subagents with your team
