# Claude Code Hooks Guide

Complete reference for Claude Code hooks - deterministic scripts that execute automatically at specific points in Claude Code's lifecycle.

## What Are Hooks?

Hooks are user-defined shell commands or LLM prompts that execute automatically at specific points in Claude Code's lifecycle. Use hooks to:
- Format code after edits
- Validate commands before execution
- Send notifications
- Enforce project rules
- Log session activity

## Hook Events

| Event | When it fires | Can block? |
|-------|---------------|------------|
| `SessionStart` | When session begins or resumes | No |
| `UserPromptSubmit` | When you submit a prompt | Yes |
| `PreToolUse` | Before a tool call executes | Yes |
| `PermissionRequest` | When permission dialog appears | Yes |
| `PostToolUse` | After tool call succeeds | No |
| `PostToolUseFailure` | After tool call fails | No |
| `Notification` | When Claude Code sends notification | No |
| `SubagentStart` | When subagent is spawned | No |
| `SubagentStop` | When subagent finishes | Yes |
| `Stop` | When Claude finishes responding | Yes |
| `PreCompact` | Before context compaction | No |
| `SessionEnd` | When session terminates | No |

## Configuration

Define hooks in JSON settings files:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/lint-check.sh"
          }
        ]
      }
    ]
  }
}
```

### Hook Locations

| Location | Scope |
|----------|-------|
| `~/.claude/settings.json` | All your projects |
| `.claude/settings.json` | Single project (shareable) |
| `.claude/settings.local.json` | Single project (git-ignored) |
| Managed policy settings | Organization-wide |
| Plugin `hooks/hooks.json` | When plugin is enabled |
| Skill/Agent frontmatter | While component is active |

## Matcher Patterns

The `matcher` field is a regex that filters when hooks fire:

| Event | What matcher filters | Example |
|-------|---------------------|---------|
| `PreToolUse`, `PostToolUse`, `PermissionRequest` | Tool name | `Bash`, `Edit\|Write`, `mcp__.*` |
| `SessionStart` | How session started | `startup`, `resume`, `clear`, `compact` |
| `SessionEnd` | Why session ended | `clear`, `logout`, `prompt_input_exit`, `bypass_permissions_disabled`, `other` |
| `Notification` | Notification type | `permission_prompt`, `idle_prompt`, `auth_success`, `elicitation_dialog` |
| `SubagentStart`, `SubagentStop` | Agent type | `Bash`, `Explore`, `Plan` |
| `PreCompact` | What triggered compaction | `manual`, `auto` |

Use `"*"`, `""`, or omit `matcher` to match all occurrences.

### MCP Tools

MCP tools follow naming pattern `mcp__<server>__<tool>`:
- `mcp__memory__.*` matches all memory server tools
- `mcp__.*__write.*` matches any "write" tool from any server

## Hook Types

### Command Hooks
```json
{
  "type": "command",
  "command": "/path/to/script.sh",
  "timeout": 600,
  "async": false
}
```

### Prompt Hooks
Send prompt to LLM for single-turn evaluation:
```json
{
  "type": "prompt",
  "prompt": "Evaluate if Claude should stop: $ARGUMENTS",
  "model": "haiku",
  "timeout": 30
}
```

### Agent Hooks
Spawn subagent that can use tools to verify conditions:
```json
{
  "type": "agent",
  "prompt": "Verify all unit tests pass. $ARGUMENTS",
  "timeout": 60
}
```

### Common Fields

| Field | Required | Description |
|-------|----------|-------------|
| `type` | Yes | `"command"`, `"prompt"`, or `"agent"` |
| `timeout` | No | Seconds before canceling. Defaults: 600 command, 30 prompt, 60 agent |
| `statusMessage` | No | Custom spinner message displayed while hook runs |
| `once` | No | If `true`, runs only once per session then removed (skills only) |

## Hook Input/Output

### Input (stdin)

All hooks receive JSON via stdin:

```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/path/to/project",
  "permission_mode": "default",
  "hook_event_name": "PreToolUse",
  "tool_name": "Bash",
  "tool_input": {
    "command": "npm test"
  }
}
```

### Exit Codes

| Exit Code | Behavior |
|-----------|----------|
| 0 | Success - proceed, parse stdout for JSON |
| 2 | Blocking error - block action, show stderr to Claude |
| Other | Non-blocking error - continue, show stderr in verbose mode |

### JSON Output

Exit 0 and print JSON to stdout for structured control:

```json
{
  "continue": false,
  "stopReason": "Build failed",
  "systemMessage": "Warning message",
  "suppressOutput": false
}
```

## Decision Control

### PreToolUse

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "permissionDecisionReason": "Auto-approved",
    "updatedInput": {
      "command": "modified command"
    },
    "additionalContext": "Context for Claude"
  }
}
```

Values for `permissionDecision`: `"allow"`, `"deny"`, `"ask"`

### PermissionRequest

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PermissionRequest",
    "decision": {
      "behavior": "allow",
      "updatedInput": { "command": "npm run lint" }
    }
  }
}
```

### Stop / SubagentStop

```json
{
  "decision": "block",
  "reason": "Tests must pass before stopping"
}
```

## Common Patterns

### Auto-Format on Edit

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "npx prettier --write \"$CLAUDE_PROJECT_DIR\"/**/*.{js,ts,tsx}"
          }
        ]
      }
    ]
  }
}
```

### Block Dangerous Commands

```bash
#!/bin/bash
# block-rm.sh
COMMAND=$(jq -r '.tool_input.command' < /dev/stdin)

if echo "$COMMAND" | grep -q 'rm -rf'; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: "Destructive command blocked"
    }
  }'
else
  exit 0
fi
```

### Session Context Loading

```bash
#!/bin/bash
# session-start.sh

# Load recent issues
ISSUES=$(gh issue list --limit 5 --json number,title)

jq -n --arg issues "$ISSUES" '{
  hookSpecificOutput: {
    hookEventName: "SessionStart",
    additionalContext: "Recent issues: \($issues)"
  }
}'
```

### Persist Environment Variables

SessionStart hooks can persist environment variables:

```bash
#!/bin/bash
if [ -n "$CLAUDE_ENV_FILE" ]; then
  echo 'export NODE_ENV=production' >> "$CLAUDE_ENV_FILE"
  echo 'export DEBUG_LOG=true' >> "$CLAUDE_ENV_FILE"
fi
exit 0
```

## Async Hooks

Run hooks in background without blocking:

```json
{
  "type": "command",
  "command": "/path/to/run-tests.sh",
  "async": true,
  "timeout": 120
}
```

Async hooks cannot block or control Claude's behavior.

## Hooks in Skills/Agents

Define hooks in frontmatter:

```yaml
---
name: secure-operations
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/security-check.sh"
---
```

`Stop` hooks in skill/agent frontmatter are converted to `SubagentStop`.

## Project-Level Subagent Hooks

In settings.json:

```json
{
  "hooks": {
    "SubagentStart": [
      {
        "matcher": "db-agent",
        "hooks": [
          { "type": "command", "command": "./scripts/setup-db.sh" }
        ]
      }
    ],
    "SubagentStop": [
      {
        "hooks": [
          { "type": "command", "command": "./scripts/cleanup-db.sh" }
        ]
      }
    ]
  }
}
```

## Reference Variables

- `$CLAUDE_PROJECT_DIR` - Project root
- `${CLAUDE_PLUGIN_ROOT}` - Plugin's root directory
- `$CLAUDE_ENV_FILE` - File path for persisting environment variables (SessionStart only)
- `$CLAUDE_CODE_REMOTE` - Set to `"true"` in remote web environments

## Management Commands

- `/hooks` - Interactive hooks manager (view, add, delete)
- Toggle `"disableAllHooks": true` in settings to disable all hooks

## Debugging

Run `claude --debug` to see hook execution details. Toggle verbose mode with `Ctrl+O`.

## Security Notes

Hooks run with your system user's full permissions. Always:
- Validate and sanitize inputs
- Quote shell variables (`"$VAR"` not `$VAR`)
- Block path traversal (check for `..`)
- Use absolute paths
- Skip sensitive files (.env, .git/, keys)
