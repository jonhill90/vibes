# Source: README.md lines 48-57 (current) vs. actual config (needed)
# Pattern: MCP configuration JSON snippet in README
# Extracted: 2025-10-05
# Relevance: 10/10 - Shows exactly what needs to change

## Current README Config (Incomplete - Only 1 Server)

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

## What's Wrong
- Shows only 1 server when 4 are configured
- Uses old "vibes" key instead of "vibesbox"
- Missing: basic-memory, MCP_DOCKER, archon

## Updated Config (Complete - All 4 Servers)

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

## What to Mimic

- **JSON Structure**: Nested object with "mcpServers" parent key
- **Server Keys**: Use exact names from actual config (vibesbox, not vibes)
- **Command Format**: Array of strings for args
- **Formatting**: Proper indentation, trailing commas allowed in JSON5

## What to Adapt

- **Replace lines 48-57** in README.md with the complete 4-server config
- **Keep context**: Maintain the explanation above/below about file paths
- **Preserve formatting**: Keep same indentation style as current README

## What to Skip

- Don't add comments in the JSON (keep it valid JSON)
- Don't explain each server here (table does that)
- Don't duplicate server purposes (already in architecture table)

## Pattern Highlights

### Connection Methods Shown
```json
// Docker exec pattern (vibesbox, basic-memory)
"command": "docker",
"args": ["exec", "-i", "container-name", "script-path"]

// Docker gateway pattern (MCP_DOCKER)
"command": "docker",
"args": ["mcp", "gateway", "run"]

// NPX remote pattern (archon)
"command": "npx",
"args": ["mcp-remote", "http://localhost:8051/mcp"]
```

## Why This Example

The current README shows an incomplete, outdated configuration. Users following the Quick Start guide will only configure 1 server when they should configure all 4. This example shows the exact replacement needed to match production reality.
