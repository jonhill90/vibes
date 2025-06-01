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

## Architecture

```
mcp/
├── README.md                    # This file
├── mcp-vibes-server/           # Custom shell access server
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── server.py
│   └── ...
└── mcp-openmemory-server/      # Memory server setup
    ├── docker-compose.yml
    └── ...
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

## Configuration

Each server is configured in Claude Desktop's `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mcp-vibes": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "..."]
    },
    "openmemory": {
      "command": "npx",
      "args": ["mcp-remote", "http://localhost:8765/..."]
    }
  }
}
```

## Development

- Servers are built and managed through Docker Compose
- Use the `vibes-network` for inter-service communication
- Mount `/workspace/vibes` for file system access
- Follow MCP protocol specifications

---

*The backbone that gives Claude Desktop its superpowers*
