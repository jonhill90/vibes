# Azure MCP Server

Containerized Azure MCP server for Claude Desktop integration.

## Setup

1. Copy your Azure credentials to `.env`:
   ```bash
   cp .env.example .env
   # Edit .env with your Azure Service Principal details
   ```

2. Start the server:
   ```bash
   docker compose up -d
   ```

3. Add to Claude Desktop MCP configuration:
   ```json
   "azure": {
     "command": "docker",
     "args": [
       "exec",
       "-i", 
       "azure-mcp-server",
       "dotnet",
       "azmcp.dll",
       "server",
       "start"
     ]
   }
   ```

## Usage

Once configured, Claude can natively explore your Azure environment through the MCP protocol.
