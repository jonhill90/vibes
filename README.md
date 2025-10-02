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
| `mcp-vibesbox-server` | Unified shell + VNC GUI | ✅ Active | Docker exec |

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

## Context Engineering & PRPs

Vibes uses **Context Engineering** to transform AI coding from generic code generation to production-ready implementation. Instead of prompting in the dark, we engineer comprehensive context that enables first-pass success.

### What are PRPs?

**PRP** (Product Requirements Prompt) = **PRD** + **Curated Codebase Intelligence** + **Agent Runbook**

A PRP is a context engineering artifact that treats Claude like a competent junior developer who needs a comprehensive briefing. It includes:

- **PRD**: Clear goals, business value, success criteria
- **Curated Context**: Documentation URLs, file references, existing patterns, known gotchas
- **Agent Runbook**: Implementation blueprint, pseudocode, task list, validation gates

### PRP Workflow

```
1. Create INITIAL.md      → Describe your feature
2. /generate-prp          → Research and create comprehensive PRP
3. /execute-prp           → Implement with validation loops
4. Validation             → Tests pass, code quality verified
5. Done                   → Production-ready code
```

### Directory Structure

```
vibes/
├── prps/
│   ├── templates/        # PRP templates for different types
│   │   ├── prp_base.md          # Comprehensive base template
│   │   ├── feature_template.md  # Standard features
│   │   ├── tool_template.md     # API integrations
│   │   └── documentation_template.md  # Documentation
│   ├── active/           # In-progress PRPs
│   ├── completed/        # Finished PRPs
│   └── archived/         # Old reference PRPs
└── examples/             # Reference patterns and examples
    ├── prp-workflow/     # Example PRPs
    ├── tools/            # Code patterns (API, files, etc.)
    └── documentation/    # Doc templates
```

### Core Principles

1. **Context is King**: Include ALL necessary documentation, examples, and gotchas
2. **Validation Loops**: Provide executable tests the AI can run and fix iteratively
3. **Information Dense**: Use keywords and patterns from your codebase
4. **Progressive Success**: Start simple, validate, then enhance
5. **One-Pass Implementation**: Comprehensive context enables getting it right the first time

### Available Commands

- `/generate-prp <file>` - Research codebase and create comprehensive PRP
- `/execute-prp <prp>` - Execute PRP with iterative validation
- `/list-prps [status]` - List PRPs by status (active/completed/archived)

### Example Templates

Choose the right template for your task:

- **Feature Template**: Standard feature development
- **Tool Template**: API integrations and external tools
- **Documentation Template**: READMEs, API docs, guides

### Learn More

- [PRP Base Template](prps/templates/prp_base.md) - Comprehensive template with all sections
- [Examples Directory](examples/README.md) - Reference patterns for common tasks
- [Context Engineering Intro](https://github.com/coleam00/context-engineering-intro) - Original philosophy

**Philosophy**: Context engineering is 10x better than prompt engineering and 100x better than vibe coding. Give Claude the context it needs to succeed.

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
