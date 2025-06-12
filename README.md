# Vibes - Conversational Development Environment

Vibes transforms Claude Desktop into a conversational development environment through distributed MCP servers. Instead of learning command-line tools, you describe what you want to build and Claude implements it while teaching you.

## Current State

**Core Philosophy**: Ask → Build → Understand → Improve → Create

**Working Components**:
- Shell access and code execution in isolated containers
- Persistent memory across conversations via vector database
- Repository analysis and code understanding
- INMPARA knowledge management system
- Azure, Terraform, and GitHub integrations

**Architecture**: Claude Desktop + MCP servers + Docker containers + Vector DB

## MCP Server Ecosystem

| Server | Purpose | Status |
|--------|---------|--------|
| `mcp-vibes-server` | Shell access, container management | ✅ Production |
| `mcp-notebook-server` | INMPARA knowledge management | ✅ Production |
| `mcp-openmemory-server` | Persistent conversation memory | ✅ Production |
| `mcp-github-server` | Repository integration | ✅ Production |
| `mcp-azure-server` | Cloud operations | ✅ Production |
| `mcp-terraform-server` | Infrastructure as code | ✅ Production |
| `deepwiki-server` | Code analysis | ✅ Production |

## Future Vision

Expanding toward observable AI execution and team collaboration:

**Phase 1: Observable Agent Execution**
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

## Quick Start

```bash
git clone https://github.com/jonhill90/vibes.git
cd vibes/mcp
docker-compose up -d
# Configure Claude Desktop MCP settings (see docs/)
```

## Current Capabilities

- Execute code in safe, isolated environments
- Remember conversations and build knowledge over time
- Analyze any GitHub repository
- Build real projects with infrastructure automation
- Learn through hands-on conversation rather than documentation

---

*Conversational development environment in production. Observable AI execution in development.*
