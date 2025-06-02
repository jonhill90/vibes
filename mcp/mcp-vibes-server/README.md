# MCP Vibes Server

Persistent containerized MCP server for shell command execution.

## Setup

1. Copy `.env.example` to `.env` and set your `VIBES_PATH`
2. Run: `docker compose up -d`

## Claude Config

```json
"mcp-vibes": {
  "command": "docker",
  "args": [
    "exec", "-i", "mcp-vibes-server",
    "python3", "/workspace/server.py"
  ]
}
```
