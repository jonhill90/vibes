# Source: README.md
# Lines: 17-20
# Pattern: MCP server documentation table
# Extracted: 2025-10-05
# Relevance: 10/10 - This is the exact table format to extend from 2 to 4 servers

```markdown
| Server | Purpose | Status | Connection |
|--------|---------|--------|------------|
| `mcp-vibes-server` | Shell access, container management | ✅ Active | Docker exec |
| `mcp-vibesbox-server` | Unified shell + VNC GUI | ✅ Active | Docker exec |
```

## What to Mimic

- **Table Structure**: 4 columns (Server, Purpose, Status, Connection)
- **Server Name Formatting**: Use backticks for server names (e.g., `mcp-vibes-server`)
- **Status Indicators**: Use ✅ Active for operational servers
- **Connection Method**: Brief description (e.g., "Docker exec", "npx remote")
- **Purpose Description**: Short, clear description of what the server does

## What to Adapt

- **Add Two More Rows**:
  - `basic-memory`: Persistent memory across Claude sessions | ✅ Active | Docker exec
  - `MCP_DOCKER`: Docker gateway/orchestration | ✅ Active | Docker mcp gateway
  - `archon`: Task/knowledge management, RAG search | ✅ Active | npx remote

## What to Skip

- Nothing - this entire table structure should be preserved and extended

## Pattern Highlights

```markdown
# The key pattern is consistency:
| `server-name` | Brief purpose (5-10 words) | ✅ Active | Brief method |
```

### Why Use Backticks for Server Names
- Makes them stand out as code/technical identifiers
- Consistent with how they appear in config files
- Helps readers know exact string to use

### Status Indicator Meaning
- ✅ Active = Currently configured and running
- 🚧 Development = Work in progress
- ❌ Disabled = Not currently active

## Why This Example

This is the current README.md table that needs to be extended. The feature analysis requires adding 2 missing servers (archon, basic-memory) and potentially MCP_DOCKER. The format is already established and should be maintained for consistency.
