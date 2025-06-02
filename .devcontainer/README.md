# Vibes DevContainer Configuration

This devcontainer provides a complete development environment for the Vibes project with full Docker integration and MCP server capabilities.

## Features

### Core Tools
- **Docker CLI & Compose** - Full container management capabilities
- **Node.js 20.x** - Modern JavaScript runtime with npm
- **Python 3** - With MCP package for server development
- **Azure CLI** - Cloud operations and management
- **Claude CLI** - AI assistance integration
- **Codex CLI** - OpenAI code assistance

### Development Environment
- **VS Code Extensions** - Docker, Azure, Python, Go, .NET, Terraform
- **Network Integration** - Connects to vibes-network for MCP communication
- **Volume Mounts** - Docker socket access for container management
- **Shell Aliases** - Quick navigation commands (`cdv`, `vibes`)

## Quick Start

1. Open the project in VS Code
2. Click "Reopen in Container" when prompted
3. Wait for the container to build and start
4. Run diagnostic tests:
   ```bash
   bash /usr/local/share/test-docker.sh
   bash /usr/local/share/test-network.sh
   ```

## Available Commands

- `cdv` or `vibes` - Navigate to vibes directory
- `docker ps` - Check running containers
- `claude --help` - Claude CLI help
- `az --help` - Azure CLI help

## Network Integration

The devcontainer automatically connects to the `vibes-network` allowing communication with MCP servers:
- azure-mcp-server
- terraform-mcp-server
- mcp-vibes-server
- openmemory-mcp

## Environment Variables

Set these in your VS Code settings or `.env` file:
- `ANTHROPIC_API_KEY` - For Claude CLI
- `OPENAI_API_KEY` - For Codex CLI
- `AZURE_*` - For Azure operations

## Troubleshooting

See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for common issues and solutions.
