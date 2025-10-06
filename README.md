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
| `basic-memory` | Persistent memory across Claude sessions | ✅ Active | Docker exec |
| `MCP_DOCKER` | Container orchestration gateway | ✅ Active | docker mcp |
| `archon` | Task/knowledge management, RAG search | ✅ Active | npx mcp-remote |

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
    "vibesbox": {
      "command": "docker",
      "args": ["exec", "-i", "mcp-vibesbox-server", "python3", "/workspace/server.py"]
    },
    "basic-memory": {
      "command": "docker",
      "args": ["exec", "-i", "basic-memory-mcp", "/app/start.sh"]
    },
    "MCP_DOCKER": {
      "command": "docker",
      "args": ["mcp", "gateway", "run"]
    },
    "archon": {
      "command": "npx",
      "args": ["mcp-remote", "http://localhost:8051/mcp"]
    }
  }
}
```

### 4. Restart Claude Desktop

After updating the configuration, restart Claude Desktop to load the MCP servers.

## Current Capabilities

- **Shell execution & container management** via `mcp-vibes-server` MCP
  - Run bash commands in isolated environments
  - Docker container lifecycle management
  - Network access to vibes-network

- **Desktop automation & visual feedback** via `mcp-vibesbox-server` MCP
  - VNC desktop environment (XFCE4, 1920x1080)
  - Screenshot capture for Claude's vision
  - Mouse/keyboard control (click, drag, type)
  - ARM64 Chromium browser automation

- **Task & knowledge management** via `archon` MCP
  - Task tracking (find_tasks, manage_task)
  - RAG search across documentation (2-5 keyword queries)
  - Project management and organization

- **Persistent memory** via `basic-memory` MCP
  - Local Markdown-based knowledge storage
  - Conversation context across sessions
  - Semantic linking and knowledge graphs

- **Container orchestration** via `MCP_DOCKER` gateway
  - Unified MCP server management
  - Security isolation and secrets management
  - Enterprise observability

## Context Optimization

We compressed the context Claude sees by **59-70%** without losing functionality.

**File Sizes Achieved**:
- **CLAUDE.md**: 107 lines (from 143, 25% reduction)
- **Patterns**: 47-150 lines each (target ≤150)
- **Commands**: 202-320 lines each (target ≤350)

**Context Per Command**:
- `/generate-prp`: 427 lines (59% reduction from 1044 baseline)
- `/execute-prp`: 309 lines (70% reduction from 1044 baseline)

**Impact**: ~320,400 tokens saved annually (assuming 10 PRP workflows/month)

**Why this matters**: Claude has an "attention budget"—more tokens doesn't mean better results. By compressing context, we improved both speed and accuracy.

See [validation report](prps/prp_context_refactor/execution/validation-report.md) for detailed methodology.

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
├── .claude/              # Context-engineered components (59-70% reduction)
│   ├── commands/         # Slash commands for Claude Code
│   │   ├── generate-prp.md    # 320 lines (59% reduction)
│   │   ├── execute-prp.md     # 202 lines (70% reduction)
│   │   ├── list-prps.md
│   │   └── prep-parallel.md
│   ├── patterns/         # Reusable implementation patterns
│   │   ├── README.md          # Pattern library index
│   │   ├── archon-workflow.md
│   │   ├── parallel-subagents.md
│   │   ├── quality-gates.md
│   │   └── security-validation.md
│   ├── agents/           # Subagent specifications
│   └── templates/        # Report templates
├── prps/                 # Per-feature PRP artifacts
│   ├── {feature_name}/   # Feature-specific directory
│   │   ├── planning/     # Research outputs
│   │   ├── examples/     # Concrete examples
│   │   └── execution/    # Implementation artifacts
│   └── templates/        # PRP templates
│       ├── prp_base.md          # Comprehensive base
│       ├── feature_template.md  # Standard features
│       ├── tool_template.md     # API integrations
│       └── documentation_template.md
├── CLAUDE.md             # 107 lines (project rules only)
└── mcp/                  # MCP server implementations
    ├── mcp-vibesbox-server/
    └── mcp-vibes-server/
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
- [Pattern Library](.claude/patterns/README.md) - Reusable implementation patterns
- [Context Engineering Intro](https://github.com/coleam00/context-engineering-intro) - Original philosophy

**Philosophy**: Context engineering is 10x better than prompt engineering and 100x better than vibe coding. Give Claude the context it needs to succeed.

## Pattern Library

The `.claude/patterns/` directory contains reusable implementation patterns extracted from the PRP system. These patterns enable consistent, high-quality implementations across all features.

| Pattern | Purpose | Link |
|---------|---------|------|
| archon-workflow | Archon MCP integration, health checks, graceful degradation | [View](.claude/patterns/archon-workflow.md) |
| parallel-subagents | 3x speedup through multi-task parallelization | [View](.claude/patterns/parallel-subagents.md) |
| quality-gates | Validation loops ensuring 8+/10 PRP scores | [View](.claude/patterns/quality-gates.md) |
| security-validation | 5-level security checks for user input | [View](.claude/patterns/security-validation.md) |

See [.claude/patterns/README.md](.claude/patterns/README.md) for complete pattern documentation and usage guidelines.

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
