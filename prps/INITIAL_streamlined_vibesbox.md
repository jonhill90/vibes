# INITIAL: Streamlined Vibesbox MCP Server

## Overview
Create a lightweight containerized MCP server for command execution via HTTP streaming, positioned as an agent jumpbox without VNC/GUI overhead.

## Goals
- Minimal Docker container for secure command execution
- HTTP streaming MCP server (not SSE/stdio)
- Improved tool design based on Archon knowledge base research
- Clean separation from existing vibesbox implementation

## Key Requirements

### 1. Container Setup
- **Location**: `infra/vibesbox/`
- **Base**: Lightweight Linux (Alpine or similar)
- **Purpose**: Agent command execution environment
- **No VNC**: Remove all GUI/desktop components from original

### 2. MCP Server
- **Protocol**: Streamable HTTP at `/mcp` endpoint
- **Tools**: Command execution with proper streaming support
- **Security**: Sandboxed execution, resource limits

### 3. Reference Implementations
Research these for design patterns:
- `repos/bytebot/` - Command execution patterns
- `repos/DesktopCommanderMCP/` - MCP HTTP streaming implementation
- Archon knowledge base - MCP server best practices

## Research Areas
1. MCP HTTP streaming protocol (vs SSE/stdio)
2. Docker container security for agent execution
3. Command execution streaming patterns
4. Resource limiting and sandboxing

## Out of Scope
- VNC/desktop functionality
- Screenshot/GUI interaction tools
- Browser automation
- Complex UI interactions

## Success Criteria
- [ ] Clean Docker container in `infra/vibesbox/`
- [ ] HTTP MCP server responding at `/mcp`
- [ ] Secure command execution tool(s)
- [ ] Proper streaming output handling
- [ ] No conflicts with existing vibesbox implementation

## Technical Constraints
- Must use HTTP streaming (not SSE or stdio)
- Must be containerized (Docker)
- Must maintain security boundaries
- Should be resource-efficient

## Open Questions
1. What specific commands/tools should be exposed?
2. Should we support file operations alongside commands?
3. What resource limits are appropriate?
4. Authentication/authorization approach?

## References
- Existing: `mcp-servers/vibesbox/` (what to improve upon)
- Examples: `repos/bytebot/`, `repos/DesktopCommanderMCP/`
- Knowledge: Archon MCP documentation and examples
