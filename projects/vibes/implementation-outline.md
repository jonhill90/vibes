# Implementation Outline

## Files to Create

### 1. vibes/docs/claude-capabilities.md
**Purpose:** Core instructions for Claude (version controlled)
**Content:**
- How vibes:run_command() works
- Instructions to check/create ~/.vibes/user-config/
- Template for auto-discovery process

### 2. ~/.vibes/user-config/ Templates  
**Purpose:** Auto-created files Claude maintains
**Files:**
- mcp-servers.md (available tools)
- behavioral-rules.md (learned patterns)
- session-context.md (persistent state)

### 3. Updated Preferences Prompt
**Purpose:** Minimal entry point
**Content:**
- Container/host path rules
- Pointer to docs/claude-capabilities.md
- Instruction to check ~/.vibes/user-config/

## Bootstrap Flow

1. **Claude Session Starts**
   - Reads minimal preferences prompt
   - Goes to docs/claude-capabilities.md
   
2. **Auto-Setup Check**
   - run_command("ls ~/.vibes/user-config/") 
   - If missing: Create folder + template files
   - If exists: Read existing capabilities
   
3. **Tool Discovery**
   - Test available functions (basic-memory, azure, etc.)
   - Document findings in mcp-servers.md
   - Update capabilities registry

4. **Pattern Learning**
   - If user has notebook: Discover folder patterns
   - Document behavioral adaptations
   - Maintain session context

## Key Commands Claude Will Use

- Check config: ls ~/.vibes/user-config/
- Create folder: mkdir -p ~/.vibes/user-config/
- Initialize template files with basic structure
- Test available MCP functions
- Document discoveries automatically

## Testing Strategy

1. **Clean Environment Test**
   - Fresh container, no ~/.vibes/
   - Claude should auto-create everything
   
2. **MCP Server Addition Test**  
   - Add new MCP server
   - Next Claude session should auto-discover
   
3. **Multi-User Test**
   - Different ~/.vibes/user-config/ per user
   - Same vibes repo, different capabilities

## Next Steps

1. Create docs/claude-capabilities.md
2. Test auto-discovery with current setup
3. Refine templates based on testing
4. Document final preferences prompt
