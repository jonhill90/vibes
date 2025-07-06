# Claude Capabilities - Vibes Container Environment

## Core Environment
- **vibes:run_command()** - Execute shell commands in `/workspace/vibes/` container
- **Container paths:** Use `/workspace/vibes/` for all run_command operations
- **Host mounts:** Reference actual user paths (`/Users/[user]/...`) for Docker mounts
- **Working directory:** Commands execute from `/workspace/vibes/` unless specified

## Auto-Setup User Configuration

### Check User Config Directory
```bash
ls /workspace/vibes/.vibes/user-config/ 2>/dev/null || echo "not found"
```

### Create If Missing
```bash
mkdir -p /workspace/vibes/.vibes/user-config/
```

### Initialize Required Files

**/workspace/vibes/.vibes/user-config/mcp-servers.md**
```markdown
# Available MCP Servers - Auto-Discovered
Last updated: [DATE]

## Detected Tools
- vibes:run_command() - Container shell execution

## Discovery Log
[Claude documents MCP function tests here]
```

**/workspace/vibes/.vibes/user-config/behavioral-rules.md**
```markdown
# Behavioral Rules - Auto-Learned
Last updated: [DATE]

## Discovered Patterns
[Claude documents user's folder/naming patterns here]

## Adaptive Behaviors
[Claude documents how it adapts to user's system here]
```

**/workspace/vibes/.vibes/user-config/session-context.md**
```markdown
# Session Context - Persistent Learnings
Last updated: [DATE]

## System State
[Claude maintains ongoing context here]

## Recent Discoveries
[Claude logs new learnings here]
```

## Discovery Process

### 1. Tool Detection
Test available MCP functions by attempting to call them:
- basic-memory tools (search_notes, list_directory, etc.)
- azure tools (if available)
- github tools (if available)
- Document results in mcp-servers.md

### 2. Pattern Recognition
If user has existing structure:
- Use available tools to explore organization
- Document folder patterns, naming conventions
- Record in behavioral-rules.md

### 3. Context Maintenance
- Update session-context.md with ongoing discoveries
- Maintain state between conversations
- Build capability knowledge over time

## Usage Instructions

1. **Always check /workspace/vibes/.vibes/user-config/ first**
2. **Create/update files as you learn new capabilities**
3. **Keep documentation simple and actionable**
4. **Test MCP functions to discover what's available**
5. **Adapt behavior based on discovered user patterns**

---
*This file is version controlled. User-specific discoveries go in /workspace/vibes/.vibes/user-config/*
