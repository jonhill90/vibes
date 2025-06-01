# Terraform MCP Server

Containerized [Terraform MCP Server](https://github.com/hashicorp/terraform-mcp-server) for seamless integration with Terraform Registry APIs.

## Overview

This server provides MCP (Model Context Protocol) integration with:
- Terraform Registry provider discovery
- Module exploration and analysis
- Provider resource and data source information
- Infrastructure as Code automation capabilities

## Quick Start

1. **Build and start the container:**
   ```bash
   docker-compose up -d --build
   ```

2. **Check container status:**
   ```bash
   docker-compose ps
   docker logs terraform-mcp-server
   ```

3. **Access the MCP server:**
   ```bash
   docker exec -i terraform-mcp-server /server/terraform-mcp-server stdio
   ```

## Configuration

Environment variables can be set in `.env` file:

- `LOG_LEVEL`: Logging level (default: info)
- `TERRAFORM_REGISTRY_URL`: Registry URL (default: https://registry.terraform.io)
- `RATE_LIMIT`: API rate limit (default: 100)
- `CACHE_TTL`: Cache time-to-live in seconds (default: 3600)

## Integration with Claude Desktop

Add to your Claude Desktop MCP configuration:

```json
{
  "mcpServers": {
    "terraform": {
      "command": "docker",
      "args": ["exec", "-i", "terraform-mcp-server", "/server/terraform-mcp-server", "stdio"]
    }
  }
}
```

## Features

- **Provider Discovery**: Find and explore Terraform providers
- **Module Analysis**: Get detailed information about Terraform modules
- **Resource Documentation**: Access provider resource and data source docs
- **Version Management**: Handle provider and module versioning
- **Registry Integration**: Full Terraform Registry API integration

## Management Commands

```bash
# Start the server
docker-compose up -d

# Stop the server
docker-compose down

# Rebuild and restart
docker-compose up -d --build

# View logs
docker logs -f terraform-mcp-server

# Shell access
docker exec -it terraform-mcp-server sh
```

## Health Check

The container includes health checks to ensure the server is running properly.

## Volumes

- `terraform-cache`: Local cache for Terraform data to improve performance

## Network

Uses the shared `mcp-network` for integration with other MCP servers.
