---
name: ms-learn
description: Query official Microsoft documentation for Azure, .NET, Microsoft 365, and all Microsoft technologies. Use for concepts, tutorials, code samples, limits, and best practices from learn.microsoft.com.
---

Fetch current Microsoft docs instead of relying on training data.

## Tools

| Tool | Use For |
|------|---------|
| `mcp__microsoft-learn__microsoft_docs_search` | Find docs—concepts, tutorials, config, limits |
| `mcp__microsoft-learn__microsoft_docs_fetch` | Get full page (when search excerpts insufficient) |
| `mcp__microsoft-learn__microsoft_code_sample_search` | Find official code samples |

## Workflow

### Quick lookup
```
Tool: mcp__microsoft-learn__microsoft_docs_search
Parameters: { "query": "Azure Functions Python v2 programming model" }
```

### Full page content
```
Tool: mcp__microsoft-learn__microsoft_docs_fetch
Parameters: { "url": "https://learn.microsoft.com/..." }
```

### Code samples
```
Tool: mcp__microsoft-learn__microsoft_code_sample_search
Parameters: {
  "query": "Cosmos DB",
  "language": "csharp"
}
```

## Query Tips

Be specific:
```
❌ "Azure Functions"
✅ "Azure Functions Python v2 triggers bindings"
✅ "Cosmos DB partition key design best practices"
✅ "Container Apps scaling rules KEDA"
```

Include context:
- **Version**: `.NET 8`, `EF Core 8`
- **Intent**: `quickstart`, `tutorial`, `limits`
- **Platform**: `Linux`, `Windows`

## Languages (for code search)

`csharp` `typescript` `python` `powershell` `azurecli` `java` `go` `rust`

## Note

MCP tools automatically configured via `.mcp.json` - no dependencies required.
Free to use, no API key needed.
