# Agent-0 Project: Detailed Context

## 🎭 The Two Agents Explained

### Agent-0 (Claude Desktop) - The Builder
- **What**: Claude Desktop with MCP (Model Context Protocol) tools
- **Role**: The AI developer building the actual system
- **Current Tools**: run_command via mcp-vibes-server
- **Limitation**: Can't see UI, can't control browsers, manual MCP config updates

### Agent-1 (Vibes) - The Product Being Built
- **What**: A local Manus alternative with Discord-like UI
- **Purpose**: Multi-agent AI system for development tasks
- **Agents Include**: Browser, Code, File, Research, Planner agents
- **Key Feature**: Users can SEE what agents are doing (like screen sharing)

## 🔍 Why This Approach?

The human realized: "I should use the most capable AI I have (Claude Desktop) to build my AI system rather than trying to code it all myself."

But there's a problem: Claude Desktop (Agent-0) is like a master craftsman working blindfolded with limited tools.

## 💡 The Critical Insight: The MCP Config Problem

### Current Painful Workflow:
1. Claude creates new MCP server using run_command ✓
2. Human must manually edit `~/.config/claude/claude_desktop_config.json` ✗
3. Human must restart Claude Desktop ✗
4. Test if it works
5. If not, repeat entire cycle ✗

### Example:
```json
// Human has to manually add this to claude_desktop_config.json:
{
  "mcpServers": {
    "new-mcp": {
      "command": "python",
      "args": ["/path/to/new-mcp/server.py"]
    }
  }
}
```

This manual process kills development velocity!

## 🎯 The Solution: MCP Middleware

### Concept:
```
Claude Desktop 
    ↓ (configured ONCE)
MCP Middleware Server (always running)
    ↓ (loads dynamically)
    ├── Screenshot MCP (loaded when needed)
    ├── Browser MCP (loaded when needed)
    └── Any Future MCP (no config changes!)
```

### How It Works:
1. Human adds MCP Middleware to config ONCE
2. Claude can then load/reload any MCP dynamically
3. No more config edits, no more restarts
4. Instant testing and iteration

## 📂 Project Structure Explained

### Main Project Location:
- `/workspace/vibes/` - The main Vibes project
- `/workspace/vibes/projects/Agent-0/` - This Agent-0 enhancement project

### Critical Directories:
- `/workspace/vibes/mcp/mcp-vibes-server/` - DO NOT MODIFY (provides run_command)
- `/workspace/vibes/concept/` - Discord-like UI mockup
- `/workspace/vibes/repos/` - Reference projects (OpenHands, AgenticSeek, etc.)

### Why These References Matter:
- **lightpanda-browser**: Lightweight browser for agent web automation
- **browserless**: Alternative browser automation approach
- **AgenticSeek**: Example of local-first AI agents
- **OpenHands**: Multi-agent architecture reference

## 🚨 Critical Rules for Next Session

1. **NEVER modify mcp-vibes-server** - It's Claude's only way to run commands
2. **Complete phases in order** - No skipping to "save time"
3. **Test before progressing** - Each phase must work before moving on
4. **Work in vibes directory** - Not in /workspace root
5. **One config entry** - Only MCP Middleware in claude_desktop_config.json

## 🎬 Current State Summary

### What Works:
- Claude can create/modify files
- Claude can run commands via mcp-vibes-server
- Project structure is set up
- Vision is clear

### What's Broken:
- Claude can't see UI (no screenshots)
- Claude can't control browsers (no testing)
- Claude can't run persistent processes
- Manual MCP config updates required

### Next Immediate Step:
Build MCP Middleware to solve the config update problem, enabling rapid development of all other capabilities.

## 💬 Key Conversations & Decisions

1. **"I don't care to use Ollama Models"** - User wants to use cloud LLMs (AWS Bedrock/Azure OpenAI) for Agent-1, not local models

2. **"You are like Agent 0 building Agent 1"** - This framing is crucial: Claude Desktop is the builder creating the actual product

3. **"We need a MCP Server Middle man"** - The middleware insight that unlocks everything

4. **"The Notebook mcp is our attempt at Automatic Documentation"** - Existing MCP for documentation, will enhance later

## 🔧 Technical Context

### MCP (Model Context Protocol):
- Protocol for extending Claude Desktop with tools
- Each MCP server provides specific capabilities
- Currently requires manual config and restart to add new ones

### Current MCP Servers Available:
- mcp-vibes-server (run_command)
- mcp-github-server (GitHub integration)
- mcp-notebook-server (documentation attempts)
- mcp-basic-memory-server (simple storage)
- mcp-terraform-server, mcp-azure-server (cloud tools)

### What Makes MCP Middleware Special:
- It's the ONLY MCP that needs manual configuration
- All other MCPs load through it dynamically
- Provides real-time feedback via SSE/WebSocket
- Enables hot-reload during development

## 🎯 Success Looks Like

### Phase 1 Success (MCP Middleware):
- Create one new MCP without editing config
- Load it dynamically
- Test it immediately
- See results in real-time

### Ultimate Success:
- Claude can see the Discord-like UI
- Claude can modify and test it
- Claude can manage all processes
- Development velocity increases 10x
- Vibes (Agent-1) gets built efficiently

