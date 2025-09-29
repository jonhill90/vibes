[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/jonhill90/vibes)

# Vibes - Conversational Development Environment

Vibes transforms Claude Desktop into a conversational development environment through distributed MCP servers. Instead of learning command-line tools, you describe what you want to build and Claude implements it while teaching you.

## Core Philosophy

**Ask → Build → Understand → Improve → Create**

## Current Architecture

**Production Stack**: Claude Desktop + MCP Servers + Docker Containers + Vector Database

Vibes runs as a distributed system of specialized MCP servers, each handling specific capabilities:

| Server | Purpose | Status | Connection |
|--------|---------|--------|------------|
| `mcp-vibes-server` | Shell access, container management | ✅ Active | Docker exec |
| `mcp-vibesbox-server` | Unified shell + VNC GUI (planned) | 🚧 Development | Docker exec |

## Quick Start

### Prerequisites
- Docker Desktop
- Claude Desktop
- Git

### 1. Clone Repository
```bash
git clone https://github.com/jonhill90/vibes.git
cd vibes
docker network create vibes-network
```

### 2. Start MCP Servers
```bash
cd mcp/mcp-vibes-server
docker-compose up -d
cd ..
```

### 3. Configure Claude Desktop MCP Settings

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "vibes": {
      "command": "docker",
      "args": ["exec", "-i", "mcp-vibes-server", "python3", "/workspace/server.py"]
    }
  }
}
```

### 4. Restart Claude Desktop

After updating the configuration, restart Claude Desktop to load the MCP servers.

## Current Capabilities

- **Execute code** in safe, isolated environments
- **Remember conversations** and build knowledge over time
- **Analyze repositories** from GitHub
- **Manage cloud infrastructure** with Azure and Terraform
- **Persistent knowledge** across sessions
- **Browser automation** and screenshot capture (optional)
- **Learn through conversation** rather than documentation

## Future Vision

**Phase 1: Observable Agent Execution** (In Development)
- Real-time screen sharing of AI work (terminal, browser, Neovim)
- Agent-specific environments with persistent state
- Pause/resume execution controls

**Phase 2: Team Collaboration**
- Discord-like interface for human-AI teams
- Multi-user knowledge spaces
- Agent coordination visualization

**Phase 3: Advanced Intelligence**
- Cross-session agent learning and skill accumulation
- Intelligent task routing between specialized agents
- Predictive workflow assistance

---

*Conversational development environment in production. Observable AI execution in development.*
