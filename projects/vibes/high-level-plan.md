# Vibes Self-Documenting Capability System

## Goal
Create a system where Claude automatically discovers and documents its own capabilities, keeping preferences minimal and capabilities self-maintained.

## Architecture

### 1. Minimal Preferences Prompt
```
CRITICAL: Container operations use /workspace/vibes/, host mounts use actual paths.
Read docs/claude-capabilities.md for core tools.
Check ~/.vibes/user-config/ for additional capabilities (auto-create if missing).
```

### 2. Core Capabilities File (vibes/docs/claude-capabilities.md)
- Documents vibes:run_command() basics
- Instructions for Claude to auto-setup ~/.vibes/user-config/
- Version controlled, users don't modify

### 3. Auto-Maintained User Config (~/.vibes/user-config/)
- Claude creates this folder automatically
- Claude discovers and documents available MCP servers
- Claude learns and documents user behavioral patterns
- .gitignored, user-specific

## Implementation Plan

### Phase 1: Core Setup
- [ ] Create vibes/docs/claude-capabilities.md
- [ ] Test minimal preferences prompt
- [ ] Verify auto-creation of ~/.vibes/user-config/

### Phase 2: Discovery Engine  
- [ ] Claude auto-detects available MCP tools
- [ ] Claude documents discoveries in user-config files
- [ ] Claude maintains simple capability registry

### Phase 3: Pattern Learning
- [ ] Claude learns user's folder patterns
- [ ] Claude documents behavioral adaptations
- [ ] Claude maintains session context between conversations

### Phase 4: Validation
- [ ] Test with fresh container deployment
- [ ] Test with different MCP server combinations
- [ ] Test with different user patterns

## Key Principles

1. **Keep It Simple** - No complex architectures
2. **Self-Maintaining** - Claude builds its own documentation
3. **Auto-Discovery** - Claude figures out what tools are available
4. **User-Agnostic** - Works for any user's setup
5. **Minimal Preferences** - Core rules only, details discovered

## File Structure
```
vibes/
├── docs/
│   └── claude-capabilities.md    ← Core instructions (version controlled)
└── projects/vibes/               ← This planning project

~/.vibes/user-config/             ← Auto-created by Claude
├── mcp-servers.md               ← Available tools
├── behavioral-rules.md          ← Learned user patterns  
└── session-context.md           ← Persistent learnings
```

## Success Criteria
- Fresh Claude session can bootstrap capabilities automatically
- Adding new MCP server is auto-discovered in next session
- User patterns are learned and maintained
- System works without manual configuration
