# LiteLLM Configuration (VPS Production)

This is the **production configuration** from `remote.hill90.space` VPS.

## Key Configuration

### MCP Tool Prefix Fix
```yaml
environment:
  MCP_TOOL_PREFIX_SEPARATOR: ":"
```

This setting is **critical** for Context7 MCP integration. It prevents LiteLLM from incorrectly parsing tool names with hyphens (e.g., `resolve-library-id`).

## Deployment

```bash
docker compose up -d
```

## Notes
- Last synced: 2025-10-12
- Issue fixed: Context7 MCP server prefix mismatch
- See: 01-notes/01r-research/202510121333.md
