# Agent-0 Context Management

## 🎯 Project Overview
**Agent-0**: Claude Desktop (me) with enhanced MCP capabilities  
**Purpose**: Build Agent-1 (Vibes - your local Manus alternative)  
**Core Problem**: I need eyes (visual feedback) and hands (process control) to build effectively

## 🏗️ Architecture Context

### Current State
```
Claude Desktop (Agent-1)
    ↓
mcp-vibes-server (Critical - provides run_command)
    ↓
Limited to file operations and basic commands
```

### Target State
```
Claude Desktop (Agent-1) 
    ↓
MCP Middleware (Dynamic Loading)
    ├── Visual MCPs (Screenshot, Browser Control)
    ├── Process MCPs (Server Management, Docker)
    ├── Dev MCPs (Hot Reload, File Watcher)
    └── Future MCPs (Loaded on demand)
```

## 🔑 Key Concepts

### The Gap
1. **Config Hell**: Manual claude_desktop_config.json updates required
2. **No Visual Feedback**: Can't see what I'm building
3. **No Process Control**: Can't manage long-running servers
4. **Slow Iteration**: Restart required for every MCP change

### The Solution
**MCP Middleware**: A single MCP that can dynamically load/test other MCPs without restarts

## 📚 Important Files
- `/workspace/vibes/` - Main project directory
- `mcp-vibes-server` - Critical infrastructure (DO NOT MODIFY)
- `Plan.md` - Overall vision for Vibes (Agent-1)
- `Ideas.md` - Brainstorming and solutions
- `ToDo.md` - Original task list

## 🎨 Vibes (Agent-1) Vision
- Discord-like UI for AI agent interaction
- Multiple specialized agents (Browser, Code, File, Research)
- Local-first with optional cloud LLMs (AWS Bedrock/Azure)
- Observable agent actions (see what they're doing)

## ⚠️ Critical Rules
1. **Never modify mcp-vibes-server** - It's my lifeline
2. **Test in isolation** - New MCPs should be separate
3. **Incremental progress** - Validate each phase before moving on
4. **Document everything** - Future context is crucial

