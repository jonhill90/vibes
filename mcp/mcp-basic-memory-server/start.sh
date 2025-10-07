#!/bin/bash

# Set data directory to Obsidian vault
export BASIC_MEMORY_DIR=/obsidian-vault

cd /app
source .venv/bin/activate

# Create basic memory config pointing to obsidian vault (silently)
mkdir -p /root/.basic-memory
cat > /root/.basic-memory/config.json << 'CONFIG'
{
  "projects": {
    "obsidian": "/obsidian-vault"
  },
  "default_project": "obsidian",
  "default_project_mode": true
}
CONFIG

# Start MCP server using the default project (no --project flag needed since we set default_project)
exec basic-memory mcp 2>/dev/null
