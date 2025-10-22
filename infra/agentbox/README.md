# AgentBox

Alpine-based MCP server for agent command execution with HTTP/SSE streaming.

**Pattern**: Based on `infra/vibesbox` with Alpine Linux and extended tools.

## Features

- **Streamable HTTP**: Native HTTP support matching vibesbox (port 8054)
- **Alpine Base**: Minimal footprint (~50MB vs ~200MB Ubuntu)
- **Easy Package Extension**: Simple array-based package list in Dockerfile
- **3 MCP Tools**: execute_command, manage_process, health (matches vibesbox)
- **Docker CLI**: Read-only socket access for container management
- **Security**: Non-root user, minimal capabilities, resource limits

## Quick Start

```bash
# Configure
cp .env.example .env
# Edit VIBES_PATH in .env

# Start
docker-compose up -d

# Test
curl http://localhost:8054/health
```

## Adding Packages

Edit `Dockerfile` package arrays:

```dockerfile
# Core packages (always installed)
ARG CORE_PACKAGES="\
    bash \
    git \
    curl \
    "

# Add tools as needed - just add to the array!
ARG EXTRA_PACKAGES="\
    tree \
    htop \
    ncdu \
    yourpackage \
    "
```

Rebuild:
```bash
docker-compose up -d --build
```

## MCP Tools (3 total)

### execute_command
```python
execute_command(
    command="ls -la",
    shell="/bin/sh",  # optional: /bin/sh or /bin/bash
    timeout=30  # optional, 1-300 seconds
)
# Returns JSON with success, exit_code, stdout, stderr
```

### manage_process
```python
# List processes
manage_process(action="list")

# Kill process
manage_process(action="kill", pid=1234)

# Read process output
manage_process(action="read", pid=1234)
# Returns JSON with process info
```

### health
```python
health()
# Returns JSON: {"status": "healthy", "service": "agentbox", "version": "1.0.0"}
```

## Configuration

`.env` options:
- `VIBES_PATH` - Host path to vibes directory
- `AGENTBOX_PORT` - External port (default: 8054)
- `LOG_LEVEL` - Logging level (info, debug, warning, error)

## Integration

**Connection**: `http://localhost:8054/mcp`

**Transport**: `streamable-http` (matches vibesbox pattern)

Note: As Claude Code, I can use these tools directly without additional configuration.

## Architecture

```
Alpine Linux (python:3.11-alpine)
├── Core packages (bash, git, curl, wget, jq, vim)
├── Extra tools (tree, htop, ncdu)
├── Docker CLI (container management)
├── Python deps (fastmcp, pydantic, uvicorn)
└── MCP server (HTTP/SSE on :8000 → :8054)
```

**Security**:
- User: agentbox (non-root)
- Capabilities: CHOWN, SETGID, SETUID only
- Resources: 1 CPU core, 1GB RAM, 200 PIDs
- Docker: Read-only socket access

## vs Vibesbox

| Feature | Vibesbox | AgentBox |
|---------|----------|----------|
| Base | Debian slim | **Alpine** |
| Size | ~150MB | **~50MB** |
| Tools | 3 | **3 (same)** |
| Docker CLI | ❌ | **✅** |
| Package mgmt | apt | **apk (faster)** |
| Transport | streamable-http | **streamable-http** |

## Troubleshooting

```bash
# Logs
docker-compose logs -f

# Health
curl http://localhost:8054/health

# Shell access
docker-compose exec agentbox sh

# Restart
docker-compose restart
```

## Files

```
agentbox/
├── Dockerfile          # Alpine base with package arrays
├── docker-compose.yml  # Service definition
├── pyproject.toml      # Python dependencies
└── src/
    └── mcp_server.py   # FastMCP server with 5 tools
```
