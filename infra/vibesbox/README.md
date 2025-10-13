# Vibesbox - Secure MCP Command Execution Server

**A lightweight, containerized MCP server for secure shell command execution with real-time streaming output.**

Vibesbox provides a sandboxed environment where AI agents can safely execute shell commands with resource limits, security validation, and process management capabilities. Built with FastMCP and designed for the Model Context Protocol ecosystem.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Usage Examples](#usage-examples)
- [Security Considerations](#security-considerations)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [API Reference](#api-reference)

---

## Overview

### What is Vibesbox?

Vibesbox is an agent-friendly "jumpbox" for executing shell commands in an isolated Docker container. It exposes a FastMCP HTTP server that provides two primary tools:

1. **`execute_command`**: Execute shell commands with optional streaming output
2. **`manage_process`**: List, read output from, or terminate running processes

### Key Features

- **Secure Execution**: Command allowlist, blocklist validation, and secrets redaction
- **Real-time Streaming**: Stream command output line-by-line for long-running tasks
- **Process Management**: Track and manage background processes with session IDs
- **Resource Limited**: CPU, memory, and PID limits prevent resource abuse
- **Docker Isolated**: Runs as non-root user in hardened container environment
- **MCP Protocol**: JSON-RPC 2.0 over HTTP with standardized tool discovery

### Use Cases

- AI agents executing file operations (`ls`, `cat`, `find`, `grep`)
- Automated testing and CI/CD pipeline operations
- Safe command execution for code generation and validation
- System administration tasks in isolated environments
- Development environment provisioning and management

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT (AI Agent)                        │
│                    (Claude, GPT, etc.)                          │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP POST /mcp (JSON-RPC 2.0)
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                      VIBESBOX CONTAINER                         │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                   FastMCP Server (Port 8000)              │ │
│  │                  src/mcp_server.py                        │ │
│  └───────────────────────────┬───────────────────────────────┘ │
│                              │                                   │
│  ┌───────────────────────────▼───────────────────────────────┐ │
│  │              SECURITY LAYER (src/security.py)             │ │
│  │  • Command Validation (Allowlist/Blocklist)               │ │
│  │  • Shell Metacharacter Detection                          │ │
│  │  • Secrets Redaction (API_KEY, PASSWORD, TOKEN)           │ │
│  └───────────────────────────┬───────────────────────────────┘ │
│                              │                                   │
│  ┌───────────────────────────▼───────────────────────────────┐ │
│  │         COMMAND EXECUTOR (src/command_executor.py)        │ │
│  │  • Async Subprocess Execution                             │ │
│  │  • Real-time Streaming Output                             │ │
│  │  • Timeout Enforcement (1-300s)                           │ │
│  │  • Output Truncation (100 lines max)                      │ │
│  └───────────────────────────┬───────────────────────────────┘ │
│                              │                                   │
│  ┌───────────────────────────▼───────────────────────────────┐ │
│  │        SESSION MANAGER (src/session_manager.py)           │ │
│  │  • Process Tracking (PID-based)                           │ │
│  │  • Background Process Support                             │ │
│  │  • Graceful Termination (SIGTERM → SIGKILL)               │ │
│  │  • Zombie Process Prevention                              │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                   │
│  Resource Limits:                                                │
│  • CPU: 0.5 cores                                                │
│  • Memory: 512MB                                                 │
│  • PIDs: 100 (fork bomb protection)                              │
│  • User: non-root (vibesbox)                                     │
└───────────────────────────────────────────────────────────────────┘
```

### Technology Stack

- **FastMCP**: Python MCP server framework with HTTP transport
- **Python 3.11**: Async/await for concurrent command execution
- **Pydantic v2**: Type-safe request/response validation
- **Docker**: Container isolation and resource constraints
- **Alpine Linux**: Minimal base image (~150MB total)

### Security Layers

1. **Command Validation**: Only allowlisted commands can execute
2. **Blocklist Filtering**: Dangerous patterns (`rm -rf /`, fork bombs) blocked
3. **Shell Metacharacter Detection**: Command chaining (`;`, `|`, `&&`) prevented
4. **Secrets Redaction**: API keys, passwords, tokens redacted from output
5. **Resource Limits**: CPU, memory, and process count limits enforced
6. **Non-root User**: All commands execute as `vibesbox` user (UID 1000)
7. **Capability Dropping**: Minimal container capabilities (no privileged operations)

---

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- `vibes-network` Docker network exists (run: `docker network create vibes-network`)

### Installation

1. **Clone or navigate to the repository**:
   ```bash
   cd /Users/jon/source/vibes/infra/vibesbox
   ```

2. **Build and start the container**:
   ```bash
   docker compose up --build -d
   ```

3. **Verify health**:
   ```bash
   curl http://localhost:8053/health
   # Expected: {"status": "healthy", "service": "vibesbox"}
   ```

### Quick Test

Execute a simple command via the MCP server:

```bash
curl -X POST http://localhost:8053/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "execute_command",
      "arguments": {
        "command": "echo Hello from Vibesbox!",
        "timeout": 5
      }
    },
    "id": 1
  }'
```

**Expected Response**:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"success\": true, \"exit_code\": 0, \"stdout\": \"Hello from Vibesbox!\\n\", \"stderr\": \"\", \"truncated\": false, \"error\": null}"
      }
    ]
  },
  "id": 1
}
```

---

## Usage Examples

### Example 1: Execute Simple Command

**List files in the current directory**:

```bash
curl -X POST http://localhost:8053/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "execute_command",
      "arguments": {
        "command": "ls -la /app",
        "timeout": 10,
        "stream": false
      }
    },
    "id": 2
  }'
```

**Response**:
```json
{
  "success": true,
  "exit_code": 0,
  "stdout": "total 24\ndrwxr-xr-x    1 vibesbox vibesbox      4096 Oct 13 12:00 .\ndrwxr-xr-x    1 root     root          4096 Oct 13 11:55 ..\ndrwxr-xr-x    6 vibesbox vibesbox      4096 Oct 13 12:00 src\n",
  "stderr": "",
  "truncated": false,
  "error": null
}
```

### Example 2: Stream Long-Running Command

**Execute command with streaming output**:

```bash
curl -X POST http://localhost:8053/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "execute_command",
      "arguments": {
        "command": "for i in 1 2 3 4 5; do echo Line $i; sleep 1; done",
        "timeout": 10,
        "stream": true
      }
    },
    "id": 3
  }'
```

**Response** (output appears line-by-line as command executes):
```json
{
  "success": true,
  "exit_code": 0,
  "stdout": "Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n",
  "stderr": "",
  "truncated": false,
  "error": null
}
```

### Example 3: Manage Background Processes

**List all running processes**:

```bash
curl -X POST http://localhost:8053/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "manage_process",
      "arguments": {
        "action": "list"
      }
    },
    "id": 4
  }'
```

**Response**:
```json
{
  "success": true,
  "processes": [
    {
      "pid": 1234,
      "command": "sleep 100",
      "started_at": "2025-10-13T12:00:00",
      "status": "running"
    },
    {
      "pid": 1235,
      "command": "tail -f /var/log/app.log",
      "started_at": "2025-10-13T12:01:00",
      "status": "running"
    }
  ]
}
```

**Terminate a specific process**:

```bash
curl -X POST http://localhost:8053/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "manage_process",
      "arguments": {
        "action": "kill",
        "pid": 1234,
        "signal": "SIGTERM"
      }
    },
    "id": 5
  }'
```

**Response**:
```json
{
  "success": true,
  "message": "Process 1234 terminated"
}
```

### Example 4: Blocked Command Rejection

**Attempt to execute dangerous command**:

```bash
curl -X POST http://localhost:8053/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "execute_command",
      "arguments": {
        "command": "rm -rf /",
        "timeout": 5
      }
    },
    "id": 6
  }'
```

**Response** (command rejected):
```json
{
  "success": false,
  "exit_code": -1,
  "stdout": "",
  "stderr": "Command blocked: matches dangerous pattern 'rm -rf /'",
  "truncated": false,
  "error": "Command blocked: matches dangerous pattern 'rm -rf /'"
}
```

### Example 5: Timeout Enforcement

**Execute command that exceeds timeout**:

```bash
curl -X POST http://localhost:8053/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "execute_command",
      "arguments": {
        "command": "sleep 100",
        "timeout": 2
      }
    },
    "id": 7
  }'
```

**Response** (terminated after 2 seconds):
```json
{
  "success": false,
  "exit_code": -1,
  "stdout": "",
  "stderr": "Command timed out after 2s",
  "truncated": false,
  "error": "Timeout"
}
```

---

## Security Considerations

### Command Allowlist

Only the following base commands are permitted (see `src/security.py` for full list):

**Read-only**: `ls`, `pwd`, `cat`, `grep`, `echo`, `find`, `head`, `tail`, `wc`, `sort`, `uniq`, `cut`, `awk`, `sed`

**Write operations**: `touch`, `mkdir`, `cp`, `mv`, `ln`

**System info**: `ps`, `top`, `uptime`, `whoami`, `hostname`, `uname`, `date`, `env`

**Development tools**: `python`, `python3`, `node`, `npm`, `git`, `curl`, `wget`, `tar`, `gzip`, `unzip`

### Command Blocklist

The following patterns are explicitly blocked:

- `rm -rf /` - Recursive deletion of root
- `dd if=/dev/zero` - Disk wiping
- `:(){ :|:& };:` - Fork bomb
- `chmod -R 777 /` - Dangerous permission changes
- `mkfs*` - Filesystem formatting commands

### Shell Metacharacters

Commands containing these metacharacters are rejected to prevent command injection:

- `;` - Command separator
- `|` - Pipe
- `&`, `&&`, `||` - Command chaining
- `$`, `` ` ``, `$()` - Variable/command substitution
- `>`, `<` - Redirection (blocked to prevent data exfiltration)

### Secrets Redaction

Output is automatically scanned for secrets and redacted:

- `API_KEY=...` → `API_KEY=[REDACTED]`
- `PASSWORD=...` → `PASSWORD=[REDACTED]`
- `TOKEN=...` → `TOKEN=[REDACTED]`
- `AWS_SECRET_ACCESS_KEY=...` → `AWS_SECRET_ACCESS_KEY=[REDACTED]`
- Private keys in PEM format → `[REDACTED PRIVATE KEY]`

### Resource Limits

**CPU**: Limited to 0.5 cores (50% of one CPU)

**Memory**: Hard limit of 512MB RAM

**PIDs**: Maximum 100 processes (prevents fork bombs)

**User**: All commands run as non-root user `vibesbox` (UID 1000)

**Capabilities**: Minimal container capabilities (CHOWN, SETGID, SETUID only)

### Docker Security Options

- `no-new-privileges:true` - Prevents privilege escalation
- `cap_drop: ALL` - Drops all Linux capabilities
- Non-root user enforcement
- Read-only filesystem for critical paths (future enhancement)

### Security Best Practices

1. **Never expose vibesbox directly to the internet** - Use behind authentication proxy
2. **Regularly update the allowlist** - Add commands as needed, review periodically
3. **Monitor resource usage** - Watch for unusual CPU/memory patterns
4. **Audit command logs** - Track all executed commands for security review
5. **Limit network access** - Only connect to trusted internal networks (vibes-network)
6. **Rotate container regularly** - Recreate container periodically to clear state

---

## Development

### Project Structure

```
infra/vibesbox/
├── src/
│   ├── mcp_server.py          # FastMCP server with tool definitions
│   ├── command_executor.py    # Async subprocess execution
│   ├── session_manager.py     # Process lifecycle management
│   ├── security.py            # Command validation & secrets redaction
│   └── models.py              # Pydantic data models
├── tests/
│   ├── test_mcp_server.py
│   ├── test_command_executor.py
│   ├── test_security.py
│   └── test_session_manager.py
├── Dockerfile                  # Multi-stage build
├── docker-compose.yml          # Service configuration
├── pyproject.toml             # Dependencies
└── README.md                  # This file
```

### Running Tests

**Unit tests** (pytest):
```bash
cd /Users/jon/source/vibes/infra/vibesbox

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_security.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

**Linting** (ruff):
```bash
# Check for issues
ruff check src/

# Auto-fix issues
ruff check src/ --fix
```

**Type checking** (mypy):
```bash
mypy src/
```

### Adding New Commands to Allowlist

1. **Edit `src/security.py`**:
   ```python
   ALLOWED_COMMANDS = {
       # ... existing commands ...
       "your_new_command",  # Add here
   }
   ```

2. **Add test case** in `tests/test_security.py`:
   ```python
   def test_new_command_allowed():
       is_valid, _ = validate_command("your_new_command --option")
       assert is_valid
   ```

3. **Rebuild and test**:
   ```bash
   docker compose build
   docker compose up -d
   # Test the new command via MCP
   ```

### Local Development (without Docker)

1. **Install dependencies**:
   ```bash
   pip install -e .
   ```

2. **Run MCP server**:
   ```bash
   python src/mcp_server.py
   ```

3. **Test locally**:
   ```bash
   curl http://localhost:8000/health
   ```

### Environment Variables

Configure via `.env` file or environment variables:

- `MCP_PORT` - MCP server port (default: 8000)
- `LOG_LEVEL` - Logging level: DEBUG, INFO, WARNING, ERROR (default: INFO)
- `MAX_TIMEOUT` - Maximum command timeout in seconds (default: 300)
- `MAX_OUTPUT_LINES` - Maximum output lines before truncation (default: 100)

---

## Troubleshooting

### Issue: Container won't start

**Symptoms**: `docker compose up` fails or container exits immediately

**Solutions**:

1. **Check logs**:
   ```bash
   docker logs vibesbox
   ```

2. **Verify vibes-network exists**:
   ```bash
   docker network ls | grep vibes-network
   # If missing, create it:
   docker network create vibes-network
   ```

3. **Check port conflicts**:
   ```bash
   lsof -i :8053
   # If port in use, change in docker-compose.yml
   ```

4. **Rebuild from scratch**:
   ```bash
   docker compose down -v
   docker compose build --no-cache
   docker compose up -d
   ```

### Issue: Commands not executing

**Symptoms**: Commands return errors or no output

**Solutions**:

1. **Check if command is allowlisted**:
   ```bash
   # Inside container:
   docker exec -it vibesbox python -c "from src.security import ALLOWED_COMMANDS; print(sorted(ALLOWED_COMMANDS))"
   ```

2. **Verify command isn't blocked**:
   - Check `src/security.py` `BLOCKED_COMMANDS` list
   - Remove shell metacharacters (`;`, `|`, `&`)

3. **Check timeout settings**:
   - Increase timeout in request: `"timeout": 60`
   - Long-running commands need higher timeouts

### Issue: Output not streaming

**Symptoms**: Streaming output doesn't appear line-by-line

**Solutions**:

1. **Verify `PYTHONUNBUFFERED=1` is set**:
   ```bash
   docker exec vibesbox env | grep PYTHONUNBUFFERED
   # Should output: PYTHONUNBUFFERED=1
   ```

2. **Check Dockerfile**:
   ```dockerfile
   ENV PYTHONUNBUFFERED=1  # This line MUST be present
   ```

3. **Rebuild container**:
   ```bash
   docker compose build --no-cache
   docker compose up -d
   ```

### Issue: Zombie processes accumulating

**Symptoms**: Container becomes unresponsive, PID limit reached

**Solutions**:

1. **Check for zombies**:
   ```bash
   docker exec vibesbox ps aux | grep Z
   ```

2. **Verify session cleanup**:
   - Ensure `SessionManager.cleanup_all()` is called on shutdown
   - Check `src/session_manager.py` for proper `process.wait()` calls

3. **Restart container** (temporary fix):
   ```bash
   docker compose restart vibesbox
   ```

4. **Long-term fix**: Review code for missing `await process.wait()` calls

### Issue: High resource usage

**Symptoms**: Container using excessive CPU/memory

**Solutions**:

1. **Check resource stats**:
   ```bash
   docker stats vibesbox
   ```

2. **Verify limits are applied**:
   ```bash
   docker inspect vibesbox | grep -A 10 "Memory\|Cpu"
   ```

3. **List running processes**:
   ```bash
   curl -X POST http://localhost:8053/mcp \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"manage_process","arguments":{"action":"list"}},"id":1}'
   ```

4. **Terminate resource-intensive processes**:
   ```bash
   # Use manage_process tool with action="kill"
   ```

### Issue: Secrets not being redacted

**Symptoms**: API keys or passwords visible in output

**Solutions**:

1. **Check redaction patterns** in `src/security.py`:
   ```python
   SECRET_PATTERNS = [
       # Verify your secret format matches these patterns
   ]
   ```

2. **Add new pattern** if needed:
   ```python
   (re.compile(r'(YOUR_SECRET_PATTERN\s*=\s*)[^\s]+'), r'\1[REDACTED]'),
   ```

3. **Test redaction**:
   ```python
   from src.security import sanitize_output
   output = "API_KEY=secret123"
   print(sanitize_output(output))  # Should show: API_KEY=[REDACTED]
   ```

### Issue: Health check failing

**Symptoms**: Container marked as unhealthy in `docker ps`

**Solutions**:

1. **Check health check endpoint**:
   ```bash
   docker exec vibesbox curl http://localhost:8000/health
   ```

2. **View health check logs**:
   ```bash
   docker inspect vibesbox | grep -A 20 Health
   ```

3. **Adjust health check timing** in `docker-compose.yml`:
   ```yaml
   healthcheck:
     interval: 30s
     timeout: 10s
     retries: 3
     start_period: 40s  # Increase if startup is slow
   ```

---

## API Reference

### Tool: `execute_command`

**Description**: Execute a shell command with optional streaming output.

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `command` | string | Yes | - | Shell command to execute |
| `shell` | string | No | `/bin/sh` | Shell interpreter path |
| `timeout` | integer | No | 30 | Command timeout in seconds (1-300) |
| `stream` | boolean | No | true | Stream output line-by-line |

**Returns**: JSON object with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether command completed successfully |
| `exit_code` | integer | Process exit code (null if error/timeout) |
| `stdout` | string | Standard output from command |
| `stderr` | string | Standard error from command |
| `truncated` | boolean | Whether output was truncated (>100 lines) |
| `error` | string | Error message if command failed (null on success) |

**Example**:
```json
{
  "command": "ls -la /app",
  "timeout": 10,
  "stream": false
}
```

**Response**:
```json
{
  "success": true,
  "exit_code": 0,
  "stdout": "total 24\ndrwxr-xr-x ...",
  "stderr": "",
  "truncated": false,
  "error": null
}
```

---

### Tool: `manage_process`

**Description**: Manage running processes (list, read output, or terminate).

**Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `action` | string | Yes | - | Action: "list", "kill", or "read" |
| `pid` | integer | Conditional | null | Process ID (required for "kill" and "read") |
| `signal` | string | No | "SIGTERM" | Signal to send ("SIGTERM" or "SIGKILL") |

**Actions**:

**`list`**: List all active and completed processes

**Returns**:
```json
{
  "success": true,
  "processes": [
    {
      "pid": 1234,
      "command": "sleep 100",
      "started_at": "2025-10-13T12:00:00",
      "status": "running"
    }
  ]
}
```

**`kill`**: Terminate a specific process

**Parameters**: `pid` (required), `signal` (optional, default: "SIGTERM")

**Returns**:
```json
{
  "success": true,
  "message": "Process 1234 terminated"
}
```

**`read`**: Read incremental output from a process

**Parameters**: `pid` (required)

**Returns**:
```json
{
  "success": true,
  "pid": 1234,
  "output": "New output since last read...\n"
}
```

---

## Contributing

### Code Style

- Follow PEP 8 style guide
- Use type hints for all function parameters and return values
- Add docstrings for all public functions and classes
- Maximum line length: 100 characters

### Testing Requirements

- All new features must have unit tests
- Test coverage must be >80%
- All tests must pass before merging
- Add integration tests for new MCP tools

### Pull Request Process

1. Create feature branch: `git checkout -b feature/your-feature`
2. Implement changes with tests
3. Run linting: `ruff check src/ --fix`
4. Run type checking: `mypy src/`
5. Run tests: `pytest tests/ -v`
6. Update documentation (this README)
7. Submit PR with clear description

---

## License

This project is part of the Vibes ecosystem. See the main repository for license information.

---

## Support

For issues, questions, or feature requests:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review existing issues in the repository
3. Open a new issue with:
   - Clear description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Logs from `docker logs vibesbox`

---

**Built with FastMCP** | **Docker Isolated** | **Security First**
