# MCP Servers 🔌

This directory contains the Docker configurations and implementations for all MCP (Model Context Protocol) servers that power Vibes.

## What are MCP Servers?

MCP servers provide Claude Desktop with specific capabilities by implementing the Model Context Protocol. Each server offers tools that Claude can use during conversations.

## Current Servers

### 🖥️ mcp-vibes-server
**Purpose:** Shell access and container management  
**Capabilities:**
- Execute shell commands in a containerized environment
- File system operations
- Docker container management
- Workspace persistence

**Location:** [`mcp-vibes-server/`](mcp-vibes-server/)

### 🧠 mcp-openmemory-server  
**Purpose:** Persistent memory and semantic search  
**Capabilities:**
- Store and retrieve conversation memories
- Semantic search across stored context
- User-specific memory contexts
- Vector database integration

**Location:** [`mcp-openmemory-server/`](mcp-openmemory-server/)

### 📝 mcp-basic-memory-server
**Purpose:** Local-first knowledge management through Markdown files
**Capabilities:**
- Create and edit structured Markdown notes
- Semantic search across knowledge base
- Bidirectional read/write for LLMs
- Cross-referencing and knowledge graphs
- Human-readable file storage

**Location:** [`mcp-basic-memory-server/`](mcp-basic-memory-server/)

### ☁️ mcp-azure-server
**Purpose:** Azure cloud infrastructure management
**Capabilities:**
- Complete Azure CLI access
- Resource group and subscription management
- Azure services integration
- Infrastructure monitoring and querying

**Location:** [`mcp-azure-server/`](mcp-azure-server/)

### 🏗️ mcp-terraform-server
**Purpose:** Infrastructure as Code management
**Capabilities:**
- Terraform module search and documentation
- Provider documentation access
- Terraform Registry integration
- Infrastructure planning and validation

**Location:** [`mcp-terraform-server/`](mcp-terraform-server/)

### 🐙 mcp-github-server
**Purpose:** GitHub repository and project management
**Capabilities:**
- Repository operations (create, clone, manage)
- Issue and pull request management
- Code search and file operations
- GitHub API integration

**Location:** [`mcp-github-server/`](mcp-github-server/)

### 🌐 mcp-browserless-server
**Purpose:** Browser automation and screenshot capabilities
**Capabilities:**
- Headless Chrome browser functionality
- Screenshot capture via HTTP API
- Browser automation through REST endpoints
- Provides "eyes" for Agent-0 project
- Accessible on port 9333 externally

**Location:** [`mcp-browserless-server/`](mcp-browserless-server/)

### ⏰ mcp-time-server
**Purpose:** Time and timezone functionality
**Capabilities:**
- Current time retrieval in any timezone
- Timezone abbreviation support (EST, PST, GMT, UTC, etc.)
- Environment configuration via .env file
- Timestamp formatting and conversion
- Comprehensive IANA timezone support

**Location:** [`mcp-time-server/`](mcp-time-server/)

### 🖥️ mcp-vibesbox-server
**Purpose:** Unified shell access + VNC GUI automation (in development)
**Capabilities:**
- Execute shell commands (currently implemented)
- Desktop screenshot capture (planned)
- GUI automation (click, type, keys) (planned)
- Multi-vibesbox environment management (planned)
- Template system for different environment types (planned)

**Location:** [`mcp-vibesbox-server/`](mcp-vibesbox-server/)

## Architecture

```
mcp/
├── README.md                        # This file
├── mcp-vibes-server/               # Custom shell access server
├── mcp-openmemory-server/          # Vector-based memory system
├── mcp-basic-memory-server/        # Markdown-based knowledge system
├── mcp-azure-server/               # Azure infrastructure server
├── mcp-terraform-server/           # Terraform IaC server
├── mcp-github-server/              # GitHub integration server
├── mcp-browserless-server/         # Browser automation server
├── mcp-time-server/                # Time and timezone server
└── mcp-vibesbox-server/            # VNC GUI automation server (dev)
```

## How They Work

1. **Docker Containers:** Each MCP server runs in its own container
2. **Network Communication:** Servers communicate over the `vibes-network`
3. **Volume Mounting:** Shared workspace and Docker socket access
4. **Environment Variables:** Configuration through env vars

## Adding New Servers

To add a new MCP server:

1. Create a new directory under `/mcp/`
2. Implement the MCP protocol (Python recommended)
3. Create Docker configuration
4. Update Claude Desktop configuration
5. Document the server's capabilities

## Claude Desktop Configuration

Each server is configured in Claude Desktop's `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "deepwiki": {
      "command": "npx",
      "args": ["mcp-remote", "https://mcp.deepwiki.com/sse"]
    },
    "vibes": {
      "command": "docker",
      "args": ["exec", "-i", "mcp-vibes-server", "python3", "/workspace/server.py"]
    },
    "openmemory": {
      "command": "npx",
      "args": ["mcp-remote", "http://localhost:8765/mcp/claude/sse/vibes-user"]
    },
    "basic-memory": {
      "command": "docker",
      "args": ["exec", "-i", "basic-memory-mcp", "/app/start.sh"]
    },
    "azure": {
      "command": "docker",
      "args": ["exec", "-i", "azure-mcp-server", "dotnet", "azmcp.dll", "server", "start"]
    },
    "terraform": {
      "command": "docker",
      "args": ["exec", "-i", "terraform-mcp-server", "/server/terraform-mcp-server", "stdio"]
    },
    "github": {
      "command": "docker",
      "args": ["exec", "-i", "github-mcp-server", "/server/github-mcp-server", "stdio"]
    }
  }
}
```

## Development

- Servers are built and managed through Docker Compose
- Use the `vibes-network` for inter-service communication
- Mount `/workspace/vibes` for file system access
- Follow MCP protocol specifications

## Memory Systems Comparison

### OpenMemory (Vector-based)
- **Best for:** Semantic search and conversation context
- **Storage:** Qdrant vector database
- **Strengths:** AI-optimized search, automatic clustering
- **Use case:** Remembering conversation patterns and project context

### Basic Memory (File-based)
- **Best for:** Structured knowledge and documentation
- **Storage:** Human-readable Markdown files
- **Strengths:** Editability, version control, tool compatibility
- **Use case:** Building knowledge bases and project documentation

Both memory systems can run simultaneously and serve different purposes in your development workflow.

---

*The backbone that gives Claude Desktop its superpowers*
