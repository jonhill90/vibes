# Documentation Resources: Streamlined Vibesbox MCP Server

## Overview
This document provides comprehensive official documentation for building a lightweight MCP server with secure command execution capabilities. Documentation covers FastMCP HTTP transport, Python asyncio subprocess management, Docker Alpine best practices, MCP protocol specification, and security patterns. All sources have been validated for relevance and include working code examples.

## Primary Framework Documentation

### FastMCP (MCP Server Framework)
**Official Docs**: https://gofastmcp.com/getting-started/welcome
**Version**: 2.0+
**Archon Source**: Not in Archon (should be ingested)
**Relevance**: 10/10

**Sections to Read**:
1. **Getting Started**: https://gofastmcp.com/getting-started/welcome
   - **Why**: Complete overview of FastMCP 2.0 architecture and HTTP server patterns
   - **Key Concepts**: Decorator-based tool registration, async support, Pythonic API design

2. **GitHub Repository**: https://github.com/jlowin/fastmcp
   - **Why**: Source code examples and implementation patterns
   - **Key Concepts**: Server initialization, tool decorators, HTTP transport configuration

**Code Examples from Docs**:
```python
# Example 1: Basic FastMCP server with tool registration
# Source: https://gofastmcp.com/getting-started/welcome
from fastmcp import FastMCP

mcp = FastMCP("Demo 🚀")

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

if __name__ == "__main__":
    mcp.run()
```

```python
# Example 2: Async client interaction with HTTP server
# Source: https://gofastmcp.com/getting-started/welcome
import asyncio
from fastmcp import Client

async def main():
    async with Client("https://gofastmcp.com/mcp") as client:
        result = await client.call_tool(
            name="SearchFastMcp",
            arguments={"query": "deploy a FastMCP server"}
        )
    print(result)

asyncio.run(main())
```

**Gotchas from Documentation**:
- FastMCP handles "complex protocol details" automatically
- Uses decorator-based pattern (`@mcp.tool`) not manual registration
- Supports both sync and async tool functions
- HTTP transport is the recommended production approach (superseding SSE)

---

### Model Context Protocol (MCP) Specification
**Official Docs**: https://modelcontextprotocol.io/specification/2025-06-18
**Version**: 2025-06-18 (latest as of Oct 2025)
**Archon Source**: d60a71d62eb201d5 (Model Context Protocol - LLMs)
**Relevance**: 9/10

**Sections to Read**:
1. **Streamable HTTP Transport**: https://modelcontextprotocol.io/specification/2025-06-18#streamable-http
   - **Why**: Defines HTTP transport requirements for MCP servers (replaces SSE)
   - **Key Concepts**: POST/GET endpoints, chunked transfer encoding, bidirectional communication

2. **Tool Design Patterns**: https://modelcontextprotocol.io/specification/2025-06-18#tools
   - **Why**: Defines how to structure tools, tool responses, and security requirements
   - **Key Concepts**: Tool primitives, discovery methods (`tools/list`), execution (`tools/call`)

3. **Authorization Framework**: https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization
   - **Why**: OAuth-based auth for HTTP-based transports (optional but recommended)
   - **Key Concepts**: User consent, access controls, credential handling

4. **Security Best Practices**: https://modelcontextprotocol.io/specification/2025-06-18#security
   - **Why**: Critical security considerations for tool execution
   - **Key Concepts**: User consent requirements, untrusted descriptions, explicit authorization

**Code Examples from Docs**:
```python
# Example: FastMCP tool pattern (from Archon knowledge base)
# Source: https://modelcontextprotocol.io/llms-full.txt
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather")

@mcp.tool()
async def get_weather(latitude: float, longitude: float) -> str:
    """Get weather forecast for coordinates"""
    # Implementation here
    return json.dumps({"forecast": "sunny"})
```

**Gotchas from Documentation**:
- **June 2025 Update**: Tool Output Schemas allow defining expected return shapes (reduces context window usage)
- **March 2025 Update**: Streamable HTTP transport is now preferred over SSE
- Tools represent "arbitrary code execution" - treat with caution
- Tool descriptions should be considered untrusted unless from verified server
- Explicit user consent required before invoking any tool
- JSON-RPC 2.0 message format required for all communication

---

### Python Asyncio Subprocess
**Official Docs**: https://docs.python.org/3/library/asyncio-subprocess.html
**Version**: Python 3.11+ (matches vibes infrastructure)
**Archon Source**: Not in Archon
**Relevance**: 10/10

**Sections to Read**:
1. **Creating Subprocesses**: https://docs.python.org/3/library/asyncio-subprocess.html#creating-subprocesses
   - **Why**: How to use `create_subprocess_shell()` and `create_subprocess_exec()`
   - **Key Concepts**: PIPE redirection, stdout/stderr streams, async execution

2. **Process Class**: https://docs.python.org/3/library/asyncio-subprocess.html#asyncio.subprocess.Process
   - **Why**: Process lifecycle management (wait, terminate, kill, send_signal)
   - **Key Concepts**: Process control, signal handling, exit codes

3. **Asyncio Streams**: https://docs.python.org/3/library/asyncio-stream.html
   - **Why**: StreamReader/StreamWriter for reading subprocess output line-by-line
   - **Key Concepts**: readline(), read(), async iteration

**Code Examples from Docs**:
```python
# Example 1: Basic subprocess execution with output capture
# Source: https://docs.python.org/3/library/asyncio-subprocess.html
import asyncio

async def run(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()

    print(f'[{cmd!r} exited with {proc.returncode}]')
    if stdout:
        print(f'[stdout]\n{stdout.decode()}')
```

```python
# Example 2: Streaming subprocess output line-by-line
# Source: https://docs.python.org/3/library/asyncio-subprocess.html
import asyncio
import sys

async def get_date():
    code = 'import datetime; print(datetime.datetime.now())'

    # Create subprocess with stdout redirected to PIPE
    proc = await asyncio.create_subprocess_exec(
        sys.executable, '-c', code,
        stdout=asyncio.subprocess.PIPE)

    # Read one line of output
    data = await proc.stdout.readline()
    line = data.decode('ascii').rstrip()

    # Wait for subprocess to complete
    await proc.wait()
    return line
```

```python
# Example 3: Parallel subprocess execution
# Source: https://docs.python.org/3/library/asyncio-subprocess.html
async def main():
    await asyncio.gather(
        run('ls /zzz'),
        run('sleep 1; echo "hello"'))
```

**Gotchas from Documentation**:
- Use `PIPE` for stdout/stderr to enable streaming
- `communicate()` reads ALL output - use `readline()` for streaming
- `wait()` only waits for process exit - doesn't capture output
- Always `await proc.wait()` to clean up process resources
- Decode output with `.decode('utf-8')` or `.decode('ascii')`
- Use `create_subprocess_exec()` with list args for better security
- Subprocess streams are `StreamReader` objects with async methods

---

## Docker Documentation

### Docker Resource Constraints
**Official Docs**: https://docs.docker.com/engine/containers/resource_constraints/
**Archon Source**: Not in Archon
**Relevance**: 9/10

**Sections to Read**:
1. **Memory Limits**: https://docs.docker.com/engine/containers/resource_constraints/#memory
   - **Why**: How to configure memory limits and swap for container isolation
   - **Key Concepts**: `--memory`, `--memory-swap`, `--memory-reservation`, OOM behavior

2. **CPU Constraints**: https://docs.docker.com/engine/containers/resource_constraints/#cpu
   - **Why**: Limit CPU access to prevent resource abuse
   - **Key Concepts**: `--cpus`, `--cpu-shares`, CFS scheduler

**Code Examples from Docs**:
```bash
# Example 1: Memory limit
# Source: https://docs.docker.com/engine/containers/resource_constraints/
docker run -it --memory=300m ubuntu /bin/bash
```

```bash
# Example 2: CPU limit (0.5 cores)
# Source: https://docs.docker.com/engine/containers/resource_constraints/
docker run -it --cpus="0.5" ubuntu /bin/bash
```

**Docker Compose Syntax**:
```yaml
# Docker Compose resource limits (Compose Spec format)
# Source: https://docs.docker.com/reference/compose-file/deploy/
services:
  vibesbox:
    image: vibesbox:latest
    deploy:
      resources:
        limits:
          cpus: '0.50'
          memory: 512M
          pids: 100
        reservations:
          cpus: '0.25'
          memory: 256M
```

```yaml
# Alternative syntax (Compose Spec without version)
# Source: https://stackoverflow.com/questions/42345235/
services:
  vibesbox:
    image: vibesbox:latest
    mem_limit: 512M
    cpu_count: 1
    pids_limit: 100
```

**Gotchas from Documentation**:
- Default: containers have NO resource limits
- Memory limits prevent excessive host memory consumption
- Use CFS scheduler for CPU management (default)
- PID limits prevent fork bombs
- `--memory-swap` is modifier flag - requires `--memory` first
- Kernel must support Linux capabilities for advanced controls

---

### Docker Compose Deploy Specification
**Official Docs**: https://docs.docker.com/reference/compose-file/deploy/
**Archon Source**: Not in Archon
**Relevance**: 8/10

**Key Pages**:
- **Deploy Resources**: https://docs.docker.com/reference/compose-file/deploy/#resources
  - **Use Case**: Configure resource limits in docker-compose.yml
  - **Example**: Memory limits, CPU limits, PID limits syntax

**Gotchas from Documentation**:
- Docker Compose 3.9+ doesn't need `--compatibility` flag for deploy limits
- `deploy` section works in swarm mode AND standalone mode (3.9+)
- Use `cpus` (string) not `cpu_count` (integer) in deploy section
- `pids` limit prevents process explosion attacks

---

### Alpine Linux Docker Best Practices
**Best Practices Guide**: https://docs.docker.com/build/building/best-practices/
**Performance Article**: https://pythonspeed.com/articles/alpine-docker-python/
**Archon Source**: Not in Archon
**Relevance**: 7/10

**Key Considerations**:
1. **Alpine vs Slim Debate**: Multiple sources recommend `python:3.11-slim` over Alpine for Python
   - **Why**: Alpine uses musl libc (not glibc) which can slow builds and cause compatibility issues
   - **Recommendation**: Start with `python:3.11-slim` for development, only use Alpine if size is critical

2. **When to Use Alpine**:
   - Multi-stage builds (Alpine for final image)
   - Minimal dependencies (no C extensions)
   - Size-critical deployments (<100MB requirement)

3. **Security Best Practices**:
   - Use non-root user
   - Pin base image versions
   - Regular security updates
   - Minimize installed packages

**Code Example - Non-Root User in Alpine**:
```dockerfile
# Example: Creating non-root user in Alpine
# Source: https://stackoverflow.com/questions/55185898/
FROM python:3.11-alpine

# Create non-root user (Alpine syntax differs from Debian)
RUN addgroup -S vibesbox && adduser -S vibesbox -G vibesbox

# Set working directory and permissions
WORKDIR /app
RUN chown -R vibesbox:vibesbox /app

# Switch to non-root user
USER vibesbox

# Install dependencies
COPY --chown=vibesbox:vibesbox requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=vibesbox:vibesbox . .

CMD ["python", "server.py"]
```

**Gotchas from Documentation**:
- Alpine uses `addgroup`/`adduser` not Debian's `groupadd`/`useradd`
- Alpine's shell is `/bin/sh` (busybox) not `/bin/bash`
- Some Python packages (with C extensions) compile slowly on Alpine
- Alpine images are smaller but builds can be 50x slower for Python
- Consider `python:3.11-slim` (Debian-based) as alternative for compatibility

---

## Security Documentation

### Python Subprocess Security
**Security Guide**: https://snyk.io/blog/command-injection-python-prevention-examples/
**Official Docs**: https://docs.python.org/3/library/subprocess.html#security-considerations
**Archon Source**: Not in Archon
**Relevance**: 10/10

**Key Security Practices**:
1. **Avoid `shell=True`**:
   - **Why**: Enables shell injection vulnerabilities
   - **Fix**: Pass commands as list, not string

2. **Use `shlex.split()` for parsing**:
   - **Why**: Safely splits command strings into argument lists
   - **When**: When you must accept command strings from users

3. **Input Validation**:
   - **Why**: Prevent command injection (CWE-78)
   - **How**: Allowlist/blocklist patterns, sanitization

**Code Examples**:
```python
# Example 1: WRONG - vulnerable to injection
# Source: https://snyk.io/blog/command-injection-python-prevention-examples/
import subprocess
subprocess.Popen('nslookup ' + hostname, shell=True)  # VULNERABLE!
```

```python
# Example 2: CORRECT - safe approach
# Source: https://snyk.io/blog/command-injection-python-prevention-examples/
import subprocess
subprocess.Popen(['nslookup', hostname])  # SAFE!
```

```python
# Example 3: Using shlex for safe parsing
# Source: https://www.stackhawk.com/blog/command-injection-python/
import shlex
import subprocess

user_command = "ls -la /tmp"
args = shlex.split(user_command)  # Safely split into ['ls', '-la', '/tmp']
subprocess.run(args)  # No shell=True!
```

```python
# Example 4: Command blocklist pattern
# Source: Security best practices
BLOCKED_COMMANDS = [
    "rm -rf /",
    "dd if=/dev/zero",
    ":(){ :|:& };:",  # Fork bomb
    "chmod -R 777 /",
    "mkfs",
]

def validate_command(command: str) -> bool:
    """Check if command is blocked."""
    command_lower = command.lower().strip()
    for blocked in BLOCKED_COMMANDS:
        if blocked.lower() in command_lower:
            return False
    return True
```

**Gotchas from Documentation**:
- **NEVER use `shell=True` with user input** - major security risk
- Pass commands as lists: `['cmd', 'arg1', 'arg2']` not `"cmd arg1 arg2"`
- Use `shlex.split()` to safely parse command strings
- Shell metacharacters (`|`, `&`, `;`, etc.) are dangerous with `shell=True`
- Input validation must be strict - allowlists better than blocklists
- Static analysis tool: `bandit` catches subprocess security issues

---

## Library Documentation

### 1. Pydantic (Data Validation)
**Official Docs**: https://docs.pydantic.dev/latest/
**Version**: 2.0+
**Archon Source**: c0e629a894699314 (Pydantic AI Agent Framework - includes Pydantic docs)
**Relevance**: 9/10

**Key Pages**:
- **BaseModel**: https://docs.pydantic.dev/latest/api/base_model/
  - **Use Case**: Define data models for CommandRequest, CommandResult, SessionInfo
  - **Example**: Type validation, JSON serialization (`model_dump()`, `model_dump_json()`)

- **Validators**: https://docs.pydantic.dev/latest/concepts/validators/
  - **Use Case**: Custom validation for command sanitization
  - **Example**: Field validators, model validators

**API Reference**:
- **BaseModel.model_dump()**: https://docs.pydantic.dev/latest/api/base_model/#pydantic.BaseModel.model_dump
  - **Signature**: `model_dump(*, mode='python', include=None, exclude=None, ...) -> dict`
  - **Returns**: Dictionary representation of model
  - **Example**:
  ```python
  class CommandResult(BaseModel):
      exit_code: int
      stdout: str
      stderr: str

  result = CommandResult(exit_code=0, stdout="output", stderr="")
  result.model_dump()  # {'exit_code': 0, 'stdout': 'output', 'stderr': ''}
  ```

- **BaseModel.model_dump_json()**: https://docs.pydantic.dev/latest/api/base_model/#pydantic.BaseModel.model_dump_json
  - **Signature**: `model_dump_json(*, indent=None, ...) -> str`
  - **Returns**: JSON string representation
  - **Example**:
  ```python
  result.model_dump_json()  # '{"exit_code":0,"stdout":"output","stderr":""}'
  ```

**Gotchas from Documentation**:
- Pydantic v2 uses `model_dump()` not `dict()` (v1 method)
- Pydantic v2 uses `model_dump_json()` not `json()` (v1 method)
- BaseModel validators are synchronous - use `validate_call()` decorator for async
- No native async validation in BaseModel - consider `pydantic-async-validation` library if needed

---

### 2. FastAPI (Web Framework)
**Official Docs**: https://fastapi.tiangolo.com/
**Production Guide**: https://fastapi.tiangolo.com/deployment/manually/
**Archon Source**: Not in Archon
**Relevance**: 8/10

**Key Pages**:
- **Running a Server Manually**: https://fastapi.tiangolo.com/deployment/manually/
  - **Use Case**: Production deployment with Uvicorn
  - **Example**: Uvicorn configuration, async server management

**Code Example**:
```python
# Example: FastAPI server with Uvicorn
# Source: https://fastapi.tiangolo.com/deployment/manually/
import uvicorn
from fastapi import FastAPI

app = FastAPI()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Gotchas from Documentation**:
- FastMCP is built on FastAPI - inherits its async patterns
- Use Gunicorn + Uvicorn workers for production (not standalone Uvicorn)
- Production command: `gunicorn -k uvicorn.workers.UvicornWorker app:app`
- Uvicorn handles async (concurrency), Gunicorn handles processes (parallelism)

---

### 3. Uvicorn (ASGI Server)
**Official Docs**: https://www.uvicorn.org/
**Deployment Guide**: https://www.uvicorn.org/deployment/
**Archon Source**: Not in Archon
**Relevance**: 7/10

**Key Pages**:
- **Deployment**: https://www.uvicorn.org/deployment/
  - **Use Case**: Running MCP server in production
  - **Pattern**: Gunicorn + Uvicorn workers

**Production Pattern**:
```bash
# Production deployment with Gunicorn + Uvicorn workers
# Source: https://www.uvicorn.org/deployment/
gunicorn -k uvicorn.workers.UvicornWorker \
  --workers 4 \
  --bind 0.0.0.0:8000 \
  mcp_server:mcp
```

---

## Testing Documentation

### pytest-asyncio (Async Testing)
**Official Docs**: https://pytest-asyncio.readthedocs.io/en/latest/
**PyPI**: https://pypi.org/project/pytest-asyncio/
**Archon Source**: Not in Archon
**Relevance**: 9/10

**Relevant Sections**:
- **Concepts**: https://pytest-asyncio.readthedocs.io/en/latest/concepts.html
  - **How to use**: Mark async tests with `@pytest.mark.asyncio`
- **Testing Async Code**: https://tonybaloney.github.io/posts/async-test-patterns-for-pytest-and-unittest.html
  - **Patterns**: Fixtures, mocking async functions, async context managers

**Test Examples**:
```python
# Example: Basic async test
# Source: https://pytest-asyncio.readthedocs.io/en/latest/
import pytest

@pytest.mark.asyncio
async def test_execute_command():
    result = await execute_command("echo hello")
    assert result.exit_code == 0
    assert "hello" in result.stdout
```

---

### pytest-subprocess (Subprocess Mocking)
**Official Docs**: https://pytest-subprocess.readthedocs.io/en/latest/
**PyPI**: https://pypi.org/project/pytest-subprocess/
**Archon Source**: Not in Archon
**Relevance**: 8/10

**Relevant Sections**:
- **Usage**: https://pytest-subprocess.readthedocs.io/en/latest/usage.html
  - **How to use**: Mock subprocess calls with `fp.register()`
  - **Asyncio Support**: Works with `asyncio.create_subprocess_shell`

**Test Examples**:
```python
# Example: Mocking asyncio subprocess
# Source: https://pytest-subprocess.readthedocs.io/en/latest/usage.html
import pytest
import asyncio

@pytest.mark.asyncio
async def test_subprocess_mock(fp):
    # Register fake process
    fp.register(
        ["echo", "hello"],
        stdout="hello\n",
        returncode=0
    )

    # Test code that creates subprocess
    process = await asyncio.create_subprocess_exec(
        "echo", "hello",
        stdout=asyncio.subprocess.PIPE
    )
    stdout, _ = await process.communicate()
    assert stdout.decode() == "hello\n"
```

**Alternative: Manual Mocking**:
```python
# Example: Manual async subprocess mocking
# Source: https://joshmustill.medium.com/mocking-asyncio-subprocess-in-python-with-pytest-ad508d3e6b53
from unittest.mock import AsyncMock, patch
import pytest

@pytest.mark.asyncio
async def test_subprocess_with_mock():
    mock_process = AsyncMock()
    mock_process.communicate.return_value = (b"output", b"")
    mock_process.returncode = 0

    with patch('asyncio.create_subprocess_shell', return_value=mock_process):
        # Test code here
        pass
```

---

## Integration Guides

### FastMCP + Docker Integration
**Tutorial**: https://www.firecrawl.dev/blog/fastmcp-tutorial-building-mcp-servers-python
**Example Guide**: https://www.pondhouse-data.com/blog/create-mcp-server-with-fastmcp
**Archon Source**: Not in Archon
**Relevance**: 8/10

**What it covers**:
- Building MCP servers with FastMCP
- HTTP and SSE transport patterns
- Deployment considerations

**Code examples**:
```python
# Example: Complete FastMCP server structure
# Source: https://www.firecrawl.dev/blog/fastmcp-tutorial-building-mcp-servers-python
from fastmcp import FastMCP
import asyncio

mcp = FastMCP("command-executor")

@mcp.tool()
async def execute_command(command: str, timeout: int = 30) -> str:
    """Execute a shell command with timeout."""
    try:
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=timeout
        )

        return json.dumps({
            "exit_code": process.returncode,
            "stdout": stdout.decode(),
            "stderr": stderr.decode()
        })
    except asyncio.TimeoutError:
        process.kill()
        return json.dumps({"error": "Command timed out"})

if __name__ == "__main__":
    mcp.run()
```

**Applicable patterns**:
- Decorator-based tool registration
- Async subprocess execution
- JSON response formatting
- Error handling with try/except

---

## Best Practices Documentation

### Docker Security Best Practices
**Official Guide**: https://docs.docker.com/build/building/best-practices/
**Security Checklist**: https://www.sysdig.com/learn-cloud-native/dockerfile-best-practices
**Archon Source**: Not in Archon
**Relevance**: 9/10

**Key Practices**:
1. **Run as non-root user**:
   - **Why**: Reduces attack surface, limits privilege escalation
   - **Example**:
   ```dockerfile
   RUN addgroup -S appgroup && adduser -S appuser -G appgroup
   USER appuser
   ```

2. **Minimize image layers**:
   - **Why**: Smaller images, faster builds
   - **Example**: Combine RUN commands with `&&`

3. **Use specific base image tags**:
   - **Why**: Reproducible builds, avoid "latest" drift
   - **Example**: `python:3.11-alpine` not `python:alpine`

4. **Avoid installing unnecessary packages**:
   - **Why**: Reduces attack surface, smaller images
   - **Example**: Use `--no-cache-dir` with pip

5. **Set appropriate file permissions**:
   - **Why**: Prevent modification by non-root user
   - **Example**: `COPY --chown=root:root --chmod=755`

---

### Async Error Handling Best Practices
**Article**: https://tonybaloney.github.io/posts/async-test-patterns-for-pytest-and-unittest.html
**Official Docs**: https://docs.python.org/3/library/asyncio-task.html#asyncio.Task
**Archon Source**: Not in Archon
**Relevance**: 7/10

**Key Practices**:
1. **Always await coroutines**: Unawaited coroutines generate warnings
2. **Use `asyncio.gather()` for parallel execution**: Handles multiple errors gracefully
3. **Wrap async operations in try/except**: Catch exceptions in async context
4. **Use `asyncio.wait_for()` for timeouts**: Prevent hanging operations

**Example**:
```python
# Error handling pattern for async subprocess
async def execute_with_timeout(command: str, timeout: int) -> dict:
    try:
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=timeout
        )

        return {
            "success": True,
            "exit_code": process.returncode,
            "stdout": stdout.decode(),
            "stderr": stderr.decode()
        }
    except asyncio.TimeoutError:
        process.kill()
        await process.wait()
        return {"success": False, "error": "Command timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

---

## Additional Resources

### Tutorials with Code
1. **Building MCP Servers with FastMCP**: https://medium.com/@anil.goyal0057/building-and-exposing-mcp-servers-with-fastmcp-stdio-http-and-sse-ace0f1d996dd
   - **Format**: Blog with code examples
   - **Quality**: 8/10
   - **What makes it useful**: Covers STDIO, HTTP, and SSE transports with working examples

2. **DataCamp MCP Tutorial**: https://www.datacamp.com/tutorial/building-mcp-server-client-fastmcp
   - **Format**: Interactive tutorial
   - **Quality**: 9/10
   - **What makes it useful**: Step-by-step guide with complete server/client examples

3. **Docker Best Practices 2025**: https://blog.bytescrum.com/dockerfile-best-practices-2025-secure-fast-and-modern
   - **Format**: Blog with security focus
   - **Quality**: 8/10
   - **What makes it useful**: Modern Dockerfile patterns with security emphasis

### API References
1. **Python asyncio API**: https://docs.python.org/3/library/asyncio-api-index.html
   - **Coverage**: Complete asyncio module reference
   - **Examples**: Yes, with detailed explanations

2. **Pydantic API**: https://docs.pydantic.dev/latest/api/
   - **Coverage**: Complete Pydantic v2 API
   - **Examples**: Yes, comprehensive examples

3. **Docker Compose File Spec**: https://docs.docker.com/reference/compose-file/
   - **Coverage**: Complete compose file reference
   - **Examples**: Yes, with syntax examples

### Community Resources
1. **FastMCP GitHub Issues**: https://github.com/jlowin/fastmcp/issues
   - **Type**: GitHub repository issue tracker
   - **Why included**: Real-world problems and solutions from users

2. **MCP Specification Discussions**: https://github.com/modelcontextprotocol/specification/discussions
   - **Type**: GitHub discussions
   - **Why included**: Protocol evolution, best practices, community input

3. **Stack Overflow - asyncio subprocess**: https://stackoverflow.com/questions/tagged/asyncio+subprocess
   - **Type**: Q&A forum
   - **Why included**: Common problems and solutions for async subprocess patterns

---

## Documentation Gaps

**Not found in Archon or Web**:
- **FastMCP HTTP streaming examples**: Official docs show basic examples but lack streaming output patterns
  - **Recommendation**: Reference Python asyncio subprocess streaming docs and adapt to FastMCP tools

- **MCP tool response size limits**: No clear guidance on maximum response size
  - **Recommendation**: Follow task-manager pattern (truncate descriptions to 1000 chars, limit list results to 20 items)

**Outdated or Incomplete**:
- **Alpine Python recommendations**: Some older guides recommend Alpine without caveats about build performance
  - **Suggested alternative**: Use `python:3.11-slim` (Debian) unless size is critical (<100MB requirement)

- **Docker Compose version 2 vs 3 syntax**: Many tutorials mix old syntax with new
  - **Suggested alternative**: Use Compose Spec (no version field) with modern syntax

---

## Quick Reference URLs

For easy copy-paste into PRP:

```yaml
Framework Docs:
  - FastMCP: https://gofastmcp.com/getting-started/welcome
  - FastMCP GitHub: https://github.com/jlowin/fastmcp
  - MCP Specification: https://modelcontextprotocol.io/specification/2025-06-18
  - FastAPI: https://fastapi.tiangolo.com/

Library Docs:
  - Python asyncio subprocess: https://docs.python.org/3/library/asyncio-subprocess.html
  - Pydantic BaseModel: https://docs.pydantic.dev/latest/api/base_model/
  - Pydantic Validators: https://docs.pydantic.dev/latest/concepts/validators/
  - Uvicorn: https://www.uvicorn.org/

Docker Docs:
  - Resource Constraints: https://docs.docker.com/engine/containers/resource_constraints/
  - Compose Deploy Spec: https://docs.docker.com/reference/compose-file/deploy/
  - Best Practices: https://docs.docker.com/build/building/best-practices/

Security Docs:
  - Python Subprocess Security: https://snyk.io/blog/command-injection-python-prevention-examples/
  - Command Injection Prevention: https://www.stackhawk.com/blog/command-injection-python/
  - Docker Security: https://www.sysdig.com/learn-cloud-native/dockerfile-best-practices

Testing Docs:
  - pytest-asyncio: https://pytest-asyncio.readthedocs.io/en/latest/
  - pytest-subprocess: https://pytest-subprocess.readthedocs.io/en/latest/

Tutorials:
  - FastMCP Tutorial: https://www.firecrawl.dev/blog/fastmcp-tutorial-building-mcp-servers-python
  - MCP Server Creation: https://www.pondhouse-data.com/blog/create-mcp-server-with-fastmcp
  - DataCamp MCP Guide: https://www.datacamp.com/tutorial/building-mcp-server-client-fastmcp
```

---

## Recommendations for PRP Assembly

When generating the PRP:
1. **Include these URLs** in "Documentation & References" section
2. **Extract code examples** shown above into PRP context (especially subprocess streaming, FastMCP tool patterns, security validation)
3. **Highlight gotchas** from documentation in "Known Gotchas" section:
   - MCP tools MUST return JSON strings (not dicts) - see task-manager example
   - Alpine vs Slim debate - recommend `python:3.11-slim` for development
   - NEVER use `shell=True` with user input - command injection risk
   - Streamable HTTP is now preferred over SSE transport
4. **Reference specific sections** in implementation tasks:
   - "See Python asyncio subprocess docs: https://docs.python.org/3/library/asyncio-subprocess.html#asyncio.create_subprocess_shell"
   - "See MCP security practices: https://modelcontextprotocol.io/specification/2025-06-18#security"
   - "See Docker resource limits: https://docs.docker.com/engine/containers/resource_constraints/"
5. **Note gaps** so implementation can compensate:
   - FastMCP streaming patterns not well-documented - adapt from asyncio examples
   - Response size limits not specified - follow task-manager optimization patterns

---

## Archon Ingestion Candidates

**Documentation not in Archon but should be**:
- **FastMCP Official Documentation** (https://gofastmcp.com/) - Why: Core framework for Python MCP servers, actively maintained by Prefect
- **Python asyncio subprocess module** (https://docs.python.org/3/library/asyncio-subprocess.html) - Why: Essential for async process management in Python
- **Docker Resource Constraints** (https://docs.docker.com/engine/containers/resource_constraints/) - Why: Critical for container security and resource management
- **Python subprocess security guide** (https://snyk.io/blog/command-injection-python-prevention-examples/) - Why: Essential security knowledge for command execution

[This helps improve Archon knowledge base over time]

---

## Codebase Examples (Already Available)

**Task Manager MCP Server** (`/Users/jon/source/vibes/infra/task-manager/backend/src/mcp_server.py`):
- **Relevance**: 10/10 - Direct pattern for FastMCP tool implementation
- **Key Patterns**:
  - `@mcp.tool()` decorator usage
  - JSON response formatting with `json.dumps()` (NEVER return dict)
  - Consolidated tool pattern (single tool for multiple operations)
  - Response optimization (truncate large fields)
  - Structured error handling with success/error/suggestion

**Reuse these patterns directly for vibesbox MCP server implementation.**
