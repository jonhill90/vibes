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
  "default_project": "obsidian"
}
CONFIG

# Start MCP server without any extra output - only JSON should go to stdout
export BASIC_MEMORY_PROJECT=obsidian
exec basic-memory --project obsidian mcp 2>/dev/null
