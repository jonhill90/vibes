# Codebase Patterns: Streamlined Vibesbox

## Overview

Research identified strong existing patterns in the vibes codebase for FastMCP HTTP servers, Docker containerization, async subprocess execution, and MCP tool design. The task-manager backend provides the definitive MCP server pattern to follow, while DesktopCommanderMCP (TypeScript) shows advanced process management techniques that can be adapted to Python. Docker patterns across infra/ demonstrate multi-stage builds, health checks, and the vibes-network integration standard.

**Key Finding**: The vibes codebase has a mature FastMCP implementation pattern that must be followed precisely, especially the critical JSON string return requirement (Gotcha #3).

---

## Architectural Patterns

### Pattern 1: FastMCP HTTP Server with Consolidated Tools

**Source**: `/Users/jon/source/vibes/infra/task-manager/backend/src/mcp_server.py`
**Relevance**: 10/10

**What it does**:
Implements MCP server using FastMCP framework with consolidated tool pattern - single tools that handle multiple operations (find/create/update/delete) rather than separate tools for each operation. This reduces tool count and makes the API cleaner.

**Key Techniques**:

```python
from mcp.server.fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("Task Manager")

# Consolidated tool pattern - one tool, multiple modes
@mcp.tool()
async def find_tasks(
    task_id: str | None = None,  # Get single task
    filter_by: str | None = None,  # Filter mode
    filter_value: str | None = None,
    page: int = 1,
    per_page: int = DEFAULT_PAGE_SIZE,
) -> str:  # CRITICAL: Return JSON string, not dict
    """Find and search tasks (consolidated: list + search + get)."""
    try:
        # Single task mode
        if task_id:
            success, result = await task_service.get_task(task_id)
            return json.dumps({"success": True, "task": result})

        # List mode with filters
        filters = {}
        if filter_by and filter_value:
            filters[filter_by] = filter_value

        success, result = await task_service.list_tasks(filters=filters)
        return json.dumps({"success": True, "tasks": result})
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "suggestion": "Check error message and try again"
        })

# Action-based consolidated tool
@mcp.tool()
async def manage_task(
    action: str,  # "create" | "update" | "delete"
    task_id: str | None = None,
    **kwargs
) -> str:  # CRITICAL: JSON string return
    """Manage tasks (consolidated: create/update/delete)."""
    if action == "create":
        # Create logic
        return json.dumps({"success": True, "task": created_task})
    elif action == "update":
        # Update logic
        return json.dumps({"success": True, "task": updated_task})
    elif action == "delete":
        # Delete logic
        return json.dumps({"success": True, "message": "Deleted"})

# Run server (main entry point)
if __name__ == "__main__":
    mcp.run()
```

**When to use**:
- When building any MCP server in the vibes codebase
- When you need to expose multiple operations on the same resource
- When you want to reduce tool count for Claude's context window

**How to adapt**:
For streamlined vibesbox:
- `execute_command` tool (consolidated: immediate execute + stream mode)
- `manage_process` tool (consolidated: list/kill by action parameter)
- Keep tool count to 2-3 maximum
- All tools return JSON strings with `{"success": bool, "result": ..., "error": ...}` structure

**Why this pattern**:
- **Proven in production**: Already running in task-manager MCP server
- **Cleaner API**: Fewer tools = less cognitive load for AI agents
- **Consistent interface**: All tools follow same response structure
- **Error handling**: Structured errors with suggestions built-in

---

### Pattern 2: MCP Tool JSON Response Format (CRITICAL GOTCHA)

**Source**: `/Users/jon/source/vibes/infra/task-manager/backend/src/mcp_server.py` lines 12-15
**Relevance**: 10/10 (CRITICAL)

**What it does**:
Ensures MCP tools always return JSON strings, never Python dictionaries. This is the #1 gotcha in MCP development - returning a dict will break the tool.

**Key Techniques**:

```python
import json

@mcp.tool()
async def execute_command(command: str, timeout: int = 30) -> str:
    """Execute command and return result.

    CRITICAL: MUST return JSON string, not dict!
    """
    try:
        # Execute command
        result = await run_command(command, timeout)

        # CORRECT: Return json.dumps() of dict
        return json.dumps({
            "success": True,
            "exit_code": result.exit_code,
            "stdout": result.stdout,
            "stderr": result.stderr
        })
    except Exception as e:
        # CORRECT: Even errors as JSON strings
        return json.dumps({
            "success": False,
            "error": str(e),
            "suggestion": "Check command syntax and permissions"
        })

# ❌ WRONG - DO NOT DO THIS:
# return {"success": True, "result": data}  # This breaks MCP!

# ✅ CORRECT - ALWAYS DO THIS:
# return json.dumps({"success": True, "result": data})
```

**When to use**:
- **ALWAYS** - every single MCP tool must return JSON string
- No exceptions to this rule

**How to adapt**:
For vibesbox command execution:
```python
@mcp.tool()
async def execute_command(
    command: str,
    shell: str = "/bin/sh",
    timeout: int = 30,
    stream: bool = True
) -> str:
    """Execute shell command with optional streaming."""
    try:
        if stream:
            # Stream command output line by line
            output_lines = []
            async for line in stream_command(command, shell, timeout):
                output_lines.append(line)

            return json.dumps({
                "success": True,
                "output": "\n".join(output_lines),
                "streaming": True
            })
        else:
            # Execute and wait for completion
            result = await execute_sync(command, shell, timeout)
            return json.dumps({
                "success": True,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            })
    except TimeoutError:
        return json.dumps({
            "success": False,
            "error": f"Command timed out after {timeout}s",
            "suggestion": "Increase timeout or run command in background"
        })
```

**Why this pattern**:
- **MCP protocol requirement**: FastMCP expects string responses
- **Prevents runtime errors**: Returning dicts causes tool failures
- **Documented gotcha**: Feature analysis explicitly calls this out as Gotcha #3
- **Easy to forget**: Python developers naturally return dicts, must be disciplined

**Anti-Pattern to Avoid**:
```python
# ❌ NEVER DO THIS:
@mcp.tool()
async def bad_tool(arg: str) -> dict:  # Wrong return type!
    return {"result": "value"}  # Tool will fail!

# ✅ ALWAYS DO THIS:
@mcp.tool()
async def good_tool(arg: str) -> str:  # Correct return type
    return json.dumps({"result": "value"})  # Tool works!
```

---

### Pattern 3: Response Truncation for Large Payloads

**Source**: `/Users/jon/source/vibes/infra/task-manager/backend/src/mcp_server.py` lines 38-79
**Relevance**: 8/10

**What it does**:
Optimizes MCP responses by truncating large fields (descriptions, output) to prevent payload bloat and context window exhaustion. Critical for command output which can be massive.

**Key Techniques**:

```python
# Constants for payload limits
MAX_DESCRIPTION_LENGTH = 1000
MAX_OUTPUT_LINES = 100

def truncate_text(text: str | None, max_length: int = MAX_DESCRIPTION_LENGTH) -> str | None:
    """Truncate text to maximum length with ellipsis."""
    if text and len(text) > max_length:
        return text[:max_length - 3] + "..."
    return text

def optimize_command_output(output: str, max_lines: int = MAX_OUTPUT_LINES) -> str:
    """Truncate command output to prevent massive payloads."""
    lines = output.split('\n')
    if len(lines) > max_lines:
        truncated_lines = lines[:max_lines]
        truncated_lines.append(f"... [truncated {len(lines) - max_lines} more lines]")
        return '\n'.join(truncated_lines)
    return output

@mcp.tool()
async def execute_command(command: str) -> str:
    """Execute command with output truncation."""
    result = await run_command(command)

    # Truncate stdout/stderr to prevent huge responses
    optimized_stdout = optimize_command_output(result.stdout)
    optimized_stderr = optimize_command_output(result.stderr)

    return json.dumps({
        "success": True,
        "stdout": optimized_stdout,
        "stderr": optimized_stderr,
        "exit_code": result.returncode,
        "truncated": len(result.stdout.split('\n')) > MAX_OUTPUT_LINES
    })
```

**When to use**:
- When returning command output (can be thousands of lines)
- When returning file contents
- When returning any potentially large text field

**How to adapt**:
For vibesbox command execution:
- Truncate stdout/stderr to 100-200 lines by default
- Include truncation indicator in response
- Provide "read more" mechanism via session management
- For streaming: stream chunks but still respect total line limits

**Why this pattern**:
- **Prevents context overflow**: Claude has limited context window
- **Improves performance**: Smaller payloads = faster responses
- **User experience**: Truncated output is usually sufficient, full output on request
- **Proven necessity**: Task-manager learned this the hard way (Gotcha #3 in PRP)

---

### Pattern 4: Docker Multi-Stage Build for Minimal Images

**Source**: `/Users/jon/source/vibes/infra/task-manager/backend/Dockerfile`
**Relevance**: 9/10

**What it does**:
Uses multi-stage Docker builds to separate dependency installation from runtime, resulting in minimal production images. Build stage uses full toolchain, runtime stage has only what's needed to run.

**Key Techniques**:

```dockerfile
# ============================================================================
# BUILD STAGE - Install dependencies with uv
# ============================================================================
FROM python:3.12-slim AS builder

WORKDIR /build

# Install uv package manager (faster than pip)
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml ./

# Create virtual environment and install dependencies
RUN uv venv /venv && \
    . /venv/bin/activate && \
    uv pip install -r pyproject.toml

# ============================================================================
# RUNTIME STAGE - Minimal production image
# ============================================================================
FROM python:3.12-slim

WORKDIR /app

# Copy virtual environment from builder (not rebuild!)
COPY --from=builder /venv /venv

# Copy application source
COPY src/ src/

# Set up Python environment
ENV PYTHONPATH="/app:$PYTHONPATH"
ENV PYTHONUNBUFFERED=1
ENV PATH="/venv/bin:$PATH"

# Expose ports
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Start application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**When to use**:
- Production Docker images (not development)
- When image size matters (Alpine base + multi-stage = <100MB)
- When you want reproducible builds with dependency caching

**How to adapt**:
For streamlined vibesbox (Alpine + Python):

```dockerfile
# BUILD STAGE
FROM python:3.11-alpine AS builder

WORKDIR /build

# Install build dependencies (needed for some Python packages)
RUN apk add --no-cache gcc musl-dev libffi-dev

# Install uv for fast dependency management
RUN pip install --no-cache-dir uv

COPY pyproject.toml ./

# Create venv and install dependencies
RUN uv venv /venv && \
    . /venv/bin/activate && \
    uv pip install -r pyproject.toml

# RUNTIME STAGE
FROM python:3.11-alpine

WORKDIR /app

# Copy venv from builder
COPY --from=builder /venv /venv

# Copy application code
COPY src/ src/

# Environment variables
ENV PATH="/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Expose MCP HTTP port
EXPOSE 8000

# Health check for MCP server
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8000/health || exit 1

# Run MCP server
CMD ["python", "src/mcp_server.py"]
```

**Why this pattern**:
- **Smaller images**: Builder stage discarded after build (saves 100s of MBs)
- **Faster deployments**: Smaller images = faster pulls and starts
- **Security**: Less attack surface with minimal runtime image
- **Layer caching**: Dependencies cached separately from code changes

---

### Pattern 5: Async Subprocess Execution with Streaming

**Source**: `/Users/jon/source/vibes/repos/DesktopCommanderMCP/src/terminal-manager.ts` (TypeScript, adapt to Python)
**Relevance**: 9/10

**What it does**:
Executes commands asynchronously with real-time output streaming, timeout handling, and process state detection. Critical for long-running commands and interactive sessions.

**Key Techniques** (Python adaptation from TypeScript original):

```python
import asyncio
from typing import AsyncIterator
import signal

async def stream_command_output(
    command: str,
    shell: str = "/bin/sh",
    timeout: int = 30,
    env: dict | None = None
) -> AsyncIterator[str]:
    """Stream command output line by line as it's produced.

    Pattern adapted from DesktopCommanderMCP terminal-manager.ts
    """
    # Create subprocess with pipes for stdout/stderr
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        shell=True,
        executable=shell,
        env=env or {},
        stdin=asyncio.subprocess.PIPE  # For interactive commands
    )

    try:
        # Stream stdout line by line as it arrives
        async def read_stream(stream):
            while True:
                line = await stream.readline()
                if not line:
                    break
                yield line.decode('utf-8', errors='replace')

        # Read both stdout and stderr concurrently
        async for line in read_stream(process.stdout):
            yield line

        # Wait for process to complete (with timeout)
        await asyncio.wait_for(process.wait(), timeout=timeout)

    except asyncio.TimeoutError:
        # Graceful termination: SIGTERM -> wait -> SIGKILL
        process.terminate()
        try:
            await asyncio.wait_for(process.wait(), timeout=1.0)
        except asyncio.TimeoutError:
            process.kill()
        yield f"\n[Command timed out after {timeout}s and was terminated]"

    finally:
        # Ensure process is cleaned up
        if process.returncode is None:
            process.kill()
            await process.wait()

# Session-based execution for long-running commands
class CommandSession:
    """Manages long-running command sessions.

    Pattern from DesktopCommanderMCP session management.
    """
    def __init__(self, session_id: str, command: str, process: asyncio.subprocess.Process):
        self.session_id = session_id
        self.command = command
        self.process = process
        self.started_at = asyncio.get_event_loop().time()
        self.output_buffer = []

    async def read_output(self) -> str:
        """Read new output since last read."""
        if self.process.stdout:
            try:
                # Non-blocking read with small timeout
                data = await asyncio.wait_for(
                    self.process.stdout.read(8192),
                    timeout=0.1
                )
                return data.decode('utf-8', errors='replace')
            except asyncio.TimeoutError:
                return ""
        return ""

    async def send_input(self, input_text: str) -> bool:
        """Send input to running process."""
        if self.process.stdin and not self.process.stdin.is_closing():
            try:
                # Ensure newline for shell commands
                if not input_text.endswith('\n'):
                    input_text += '\n'
                self.process.stdin.write(input_text.encode())
                await self.process.stdin.drain()
                return True
            except Exception:
                return False
        return False

    async def terminate(self, force: bool = False) -> bool:
        """Terminate the process gracefully or forcefully."""
        if self.process.returncode is not None:
            return True  # Already terminated

        try:
            if force:
                self.process.kill()
            else:
                # Graceful: SIGTERM -> wait 1s -> SIGKILL
                self.process.terminate()
                try:
                    await asyncio.wait_for(self.process.wait(), timeout=1.0)
                except asyncio.TimeoutError:
                    self.process.kill()

            await self.process.wait()
            return True
        except Exception:
            return False

# Session manager
class SessionManager:
    """Manages multiple command sessions.

    Pattern from DesktopCommanderMCP terminal-manager.ts
    """
    def __init__(self):
        self.sessions: dict[int, CommandSession] = {}

    async def start_session(self, command: str, shell: str = "/bin/sh") -> int:
        """Start a new command session and return PID."""
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.PIPE,
            shell=True,
            executable=shell
        )

        session = CommandSession(
            session_id=str(process.pid),
            command=command,
            process=process
        )
        self.sessions[process.pid] = session
        return process.pid

    def get_session(self, pid: int) -> CommandSession | None:
        """Get session by PID."""
        return self.sessions.get(pid)

    async def cleanup_completed_sessions(self):
        """Remove completed sessions (keep history of last 100)."""
        completed = [
            pid for pid, session in self.sessions.items()
            if session.process.returncode is not None
        ]

        if len(completed) > 100:
            # Keep only most recent 100
            for pid in completed[:-100]:
                del self.sessions[pid]
```

**When to use**:
- When executing commands that produce output over time
- When you need to support long-running processes
- When users need to interact with running processes (send input)
- When you need to track multiple concurrent command sessions

**How to adapt**:
For vibesbox MCP tools:

```python
@mcp.tool()
async def execute_command(
    command: str,
    shell: str = "/bin/sh",
    timeout: int = 30,
    stream: bool = True
) -> str:
    """Execute command with optional streaming."""
    if stream:
        # Collect streaming output
        output_lines = []
        async for line in stream_command_output(command, shell, timeout):
            output_lines.append(line)
            # Truncate if too many lines
            if len(output_lines) > 100:
                output_lines.append("... [output truncated]")
                break

        return json.dumps({
            "success": True,
            "output": "".join(output_lines),
            "streaming": True
        })
    else:
        # Simple execute and return
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            shell=True,
            executable=shell
        )
        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=timeout
        )
        return json.dumps({
            "success": True,
            "exit_code": process.returncode,
            "stdout": stdout.decode(),
            "stderr": stderr.decode()
        })

@mcp.tool()
async def manage_process(
    action: str,  # "list" | "kill" | "read"
    pid: int | None = None,
    signal: str = "SIGTERM"
) -> str:
    """Manage running processes (consolidated tool)."""
    if action == "list":
        sessions = session_manager.sessions.values()
        process_list = [
            {
                "pid": s.process.pid,
                "command": s.command,
                "running": s.process.returncode is None,
                "uptime": time.time() - s.started_at
            }
            for s in sessions
        ]
        return json.dumps({"success": True, "processes": process_list})

    elif action == "kill" and pid:
        session = session_manager.get_session(pid)
        if session:
            success = await session.terminate(force=(signal == "SIGKILL"))
            return json.dumps({
                "success": success,
                "message": f"Process {pid} terminated"
            })
        return json.dumps({
            "success": False,
            "error": f"Process {pid} not found"
        })

    elif action == "read" and pid:
        session = session_manager.get_session(pid)
        if session:
            output = await session.read_output()
            return json.dumps({
                "success": True,
                "output": output,
                "pid": pid
            })
        return json.dumps({
            "success": False,
            "error": f"Session {pid} not found"
        })
```

**Why this pattern**:
- **Real-time feedback**: Users see output as it's produced, not after completion
- **Timeout handling**: Prevents hung processes from blocking forever
- **Graceful termination**: SIGTERM before SIGKILL prevents resource leaks
- **Session management**: Enables interactive commands and long-running tasks
- **Proven in production**: DesktopCommanderMCP uses this successfully

---

## Naming Conventions

### File Naming

**Pattern**: `{feature}_server.py` for MCP servers, `{feature}_manager.py` for core logic
**Examples from codebase**:
- `mcp_server.py` (task-manager MCP server)
- `terminal-manager.ts` (DesktopCommanderMCP)
- `config-manager.ts` (DesktopCommanderMCP)

**For vibesbox**:
- `mcp_server.py` - Main MCP server entrypoint
- `command_executor.py` - Command execution engine
- `session_manager.py` - Process session management
- `security.py` - Command validation and blocklist

### Class Naming

**Pattern**: `{Feature}Manager`, `{Feature}Service`, `{Feature}Session`
**Examples**:
- `TerminalManager` (DesktopCommanderMCP)
- `TaskService` (task-manager)
- `CommandSession` (suggested for vibesbox)

**For vibesbox**:
- `CommandExecutor` - Main execution engine
- `SessionManager` - Manages active command sessions
- `SecurityValidator` - Command validation logic

### Function Naming

**Pattern**:
- MCP tools: `{verb}_{noun}` (execute_command, list_processes)
- Internal functions: `{verb}_{noun}` (stream_output, validate_command)
- Async functions: Always use `async def`, same naming as sync

**Examples**:
- `execute_command()` - MCP tool
- `stream_command_output()` - Internal async generator
- `validate_command()` - Internal validation function

### Variable Naming

**Pattern**: snake_case for all Python code
**Examples**:
- `session_id` not `sessionId`
- `max_output_lines` not `maxOutputLines`
- `process_timeout` not `processTimeout`

---

## File Organization

### Directory Structure

```
infra/vibesbox/
├── src/
│   ├── mcp_server.py           # Main MCP server entrypoint
│   ├── command_executor.py      # Command execution engine
│   ├── session_manager.py       # Process session management
│   ├── security.py              # Command validation & blocklist
│   └── models.py                # Pydantic models
├── tests/
│   ├── test_mcp_server.py
│   ├── test_command_executor.py
│   └── test_security.py
├── Dockerfile                    # Multi-stage Alpine build
├── docker-compose.yml            # Vibes network integration
├── pyproject.toml                # Dependency management (uv)
├── start.sh                      # Container startup script
└── README.md                     # Setup and usage docs
```

**Justification**:
- Mirrors task-manager structure (proven pattern)
- `src/` for source code (Python convention)
- `tests/` for pytest tests (parallel to src/)
- Root-level Docker files (standard Docker practice)
- `start.sh` for container initialization (like task-manager)

**Compare to task-manager**:
```
infra/task-manager/
├── backend/
│   ├── src/
│   │   ├── mcp_server.py       # ← Pattern to follow
│   │   ├── services/           # ← We use flat structure (simpler)
│   │   └── models/             # ← We use models.py (single file)
│   ├── tests/
│   ├── Dockerfile
│   └── start.sh
└── docker-compose.yml
```

---

## Common Utilities to Leverage

### 1. FastMCP Framework

**Location**: `from mcp.server.fastmcp import FastMCP`
**Purpose**: MCP server implementation with HTTP transport
**Usage Example**:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Vibesbox Command Executor")

@mcp.tool()
async def execute_command(command: str) -> str:
    """Execute shell command."""
    return json.dumps({"result": "..."})

if __name__ == "__main__":
    mcp.run()  # Starts HTTP server
```

**Why use it**:
- Already in vibes codebase (task-manager, archon)
- Handles HTTP transport automatically
- Tool registration via decorators
- Built-in error handling

### 2. Python asyncio.create_subprocess_shell

**Location**: `import asyncio`
**Purpose**: Async subprocess execution with streaming
**Usage Example**:

```python
import asyncio

async def execute_command(command: str):
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        shell=True
    )

    stdout, stderr = await process.communicate()
    return process.returncode, stdout.decode(), stderr.decode()
```

**Why use it**:
- Standard library (no external dependencies)
- Full async/await support
- Streaming output capability
- Process control (terminate, kill)

### 3. Pydantic for Data Validation

**Location**: `from pydantic import BaseModel`
**Purpose**: Request/response validation and documentation
**Usage Example**:

```python
from pydantic import BaseModel, Field

class CommandRequest(BaseModel):
    command: str = Field(..., description="Shell command to execute")
    shell: str = Field("/bin/sh", description="Shell to use")
    timeout: int = Field(30, ge=1, le=300, description="Timeout in seconds")

class CommandResult(BaseModel):
    exit_code: int
    stdout: str
    stderr: str
    duration: float
```

**Why use it**:
- Already used throughout vibes codebase
- Type validation automatically
- JSON schema generation
- FastMCP integration

### 4. Docker Health Checks

**Location**: Dockerfile `HEALTHCHECK` directive
**Purpose**: Container health monitoring
**Usage Example**:

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
```

**Why use it**:
- Docker Compose dependency management
- Automatic restart on failure
- Monitoring integration ready

### 5. uv Package Manager

**Location**: `pip install uv`, then `uv pip install ...`
**Purpose**: Fast Python dependency management
**Usage Example**:

```dockerfile
# In Dockerfile
RUN pip install --no-cache-dir uv
RUN uv venv /venv && \
    . /venv/bin/activate && \
    uv pip install -r pyproject.toml
```

**Why use it**:
- 10-100x faster than pip
- Used in task-manager backend
- Better dependency resolution
- Compatible with pip

---

## Testing Patterns

### Unit Test Structure

**Pattern**: pytest with async support, fixtures for reusable setup
**Example**: Task-manager test structure

```python
import pytest
import pytest_asyncio
from src.mcp_server import execute_command

@pytest_asyncio.fixture
async def command_executor():
    """Fixture providing command executor instance."""
    executor = CommandExecutor()
    yield executor
    await executor.cleanup()

@pytest.mark.asyncio
async def test_execute_simple_command(command_executor):
    """Test executing a simple echo command."""
    result = await command_executor.execute("echo 'test'", timeout=5)

    assert result["exit_code"] == 0
    assert "test" in result["stdout"]
    assert result["stderr"] == ""

@pytest.mark.asyncio
async def test_execute_command_timeout(command_executor):
    """Test command timeout enforcement."""
    with pytest.raises(asyncio.TimeoutError):
        await command_executor.execute("sleep 10", timeout=1)

@pytest.mark.asyncio
async def test_blocked_command_rejected(command_executor):
    """Test security blocklist prevents dangerous commands."""
    result = await command_executor.execute("rm -rf /", timeout=5)

    assert result["success"] is False
    assert "blocked" in result["error"].lower()
```

**Key techniques**:
- **Fixtures**: Reusable setup/teardown via `@pytest.fixture`
- **Async tests**: `@pytest.mark.asyncio` for async test functions
- **Mocking**: Use `pytest-mock` for external dependencies
- **Parametrization**: `@pytest.mark.parametrize` for multiple test cases

### Integration Test Structure

**Pattern**: Docker-based integration tests with real containers
**Example**: Test against running Docker container

```python
import pytest
import httpx
import subprocess

@pytest.fixture(scope="module")
def vibesbox_container():
    """Start vibesbox container for integration tests."""
    # Start container
    subprocess.run([
        "docker", "compose", "up", "-d", "vibesbox"
    ], check=True)

    # Wait for health check
    subprocess.run([
        "docker", "compose", "exec", "-T", "vibesbox",
        "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
    ], check=True, timeout=30)

    yield

    # Cleanup
    subprocess.run([
        "docker", "compose", "down", "-v"
    ], check=True)

@pytest.mark.integration
def test_mcp_execute_command_integration(vibesbox_container):
    """Test MCP execute_command tool via HTTP."""
    response = httpx.post(
        "http://localhost:8000/mcp",
        json={
            "tool": "execute_command",
            "arguments": {
                "command": "echo 'integration test'",
                "timeout": 5
            }
        }
    )

    assert response.status_code == 200
    result = response.json()
    assert result["success"] is True
    assert "integration test" in result["stdout"]
```

**Key techniques**:
- **Module-scoped fixtures**: Container starts once for all tests
- **Health checks**: Wait for service readiness before testing
- **Cleanup**: Always tear down containers after tests
- **Mark integration tests**: `@pytest.mark.integration` for separation

---

## Anti-Patterns to Avoid

### 1. Returning Dicts from MCP Tools

**What it is**: Returning Python dictionaries instead of JSON strings from MCP tools
**Why to avoid**: MCP protocol expects JSON strings, dicts cause runtime errors
**Found in**: Common mistake when first implementing MCP servers
**Better approach**: Always `return json.dumps({...})`

```python
# ❌ ANTI-PATTERN
@mcp.tool()
async def bad_tool() -> dict:
    return {"result": "value"}  # BREAKS!

# ✅ CORRECT PATTERN
@mcp.tool()
async def good_tool() -> str:
    return json.dumps({"result": "value"})
```

### 2. Not Truncating Command Output

**What it is**: Returning full command output without truncation
**Why to avoid**: Commands can produce thousands of lines, exhausting context window
**Found in**: Early versions of command execution tools
**Better approach**: Truncate to 100-200 lines, indicate truncation, provide "read more"

```python
# ❌ ANTI-PATTERN
@mcp.tool()
async def execute_command(command: str) -> str:
    result = await run_command(command)
    return json.dumps({"stdout": result.stdout})  # Could be 100k lines!

# ✅ CORRECT PATTERN
@mcp.tool()
async def execute_command(command: str) -> str:
    result = await run_command(command)
    truncated = truncate_output(result.stdout, max_lines=100)
    return json.dumps({
        "stdout": truncated,
        "truncated": len(result.stdout.split('\n')) > 100
    })
```

### 3. Blocking on process.communicate()

**What it is**: Using `process.communicate()` without timeout, blocking forever on hung processes
**Why to avoid**: Hung processes block the entire MCP server
**Found in**: Naive subprocess implementations
**Better approach**: Always use `asyncio.wait_for()` with timeout

```python
# ❌ ANTI-PATTERN
async def bad_execute(command: str):
    process = await asyncio.create_subprocess_shell(command, ...)
    stdout, stderr = await process.communicate()  # Hangs forever if process hangs!

# ✅ CORRECT PATTERN
async def good_execute(command: str, timeout: int):
    process = await asyncio.create_subprocess_shell(command, ...)
    try:
        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=timeout
        )
    except asyncio.TimeoutError:
        process.kill()
        raise
```

### 4. Not Cleaning Up Orphaned Processes

**What it is**: Starting subprocesses without tracking them or cleaning up on exit
**Why to avoid**: Resource leaks, orphaned processes consume memory/CPU
**Found in**: Simple command execution implementations
**Better approach**: Track processes in session manager, cleanup on container stop

```python
# ❌ ANTI-PATTERN
async def bad_start_command(command: str):
    process = await asyncio.create_subprocess_shell(command, ...)
    return process.pid  # Process leaked, no way to clean up!

# ✅ CORRECT PATTERN
class SessionManager:
    def __init__(self):
        self.sessions: dict[int, CommandSession] = {}

    async def start_command(self, command: str):
        process = await asyncio.create_subprocess_shell(command, ...)
        session = CommandSession(process)
        self.sessions[process.pid] = session
        return process.pid

    async def cleanup_all(self):
        """Called on shutdown to clean up all processes."""
        for session in self.sessions.values():
            await session.terminate()
```

### 5. Using Bare Alpine Without Build Dependencies

**What it is**: Using `FROM python:3.11-alpine` without installing build dependencies for packages
**Why to avoid**: Many Python packages (like cryptography, numpy) need gcc/musl-dev to build
**Found in**: Naive Alpine Dockerfiles
**Better approach**: Use multi-stage build with build dependencies in builder stage

```dockerfile
# ❌ ANTI-PATTERN
FROM python:3.11-alpine
RUN pip install fastmcp  # May fail if fastmcp has C dependencies!

# ✅ CORRECT PATTERN
FROM python:3.11-alpine AS builder
RUN apk add --no-cache gcc musl-dev libffi-dev  # Build dependencies
RUN pip install fastmcp
# ... build complete ...

FROM python:3.11-alpine
COPY --from=builder /venv /venv  # Only runtime needed
```

### 6. Not Using vibes-network for Docker Services

**What it is**: Creating isolated Docker networks instead of using shared `vibes-network`
**Why to avoid**: Services can't communicate with each other (e.g., Archon, task-manager)
**Found in**: Services built outside vibes ecosystem
**Better approach**: Always use `vibes-network` external network

```yaml
# ❌ ANTI-PATTERN
networks:
  vibesbox-network:  # Isolated network!
    driver: bridge

# ✅ CORRECT PATTERN
networks:
  vibes-network:
    external: true  # Use existing vibes-network
```

---

## Implementation Hints from Existing Code

### Similar Features Found

#### 1. Task-Manager MCP Server

**Location**: `/Users/jon/source/vibes/infra/task-manager/backend/src/mcp_server.py`
**Similarity**: Exact same MCP server pattern - FastMCP with consolidated tools
**Lessons**:
- Consolidated tools work great (find/manage pattern)
- JSON string returns are non-negotiable
- Truncation is essential for large responses
- Structured error responses with suggestions improve UX

**Differences**:
- Task-manager uses database, vibesbox uses subprocess
- Task-manager is stateful, vibesbox can be ephemeral

**Key takeaway**: Copy the mcp_server.py structure verbatim, replace service layer with command executor

#### 2. DesktopCommanderMCP Process Management

**Location**: `/Users/jon/source/vibes/repos/DesktopCommanderMCP/src/terminal-manager.ts`
**Similarity**: Advanced process management with sessions, interactive input, output streaming
**Lessons**:
- Session-based approach enables long-running commands
- Graceful termination (SIGTERM -> wait -> SIGKILL) prevents leaks
- Process state detection (waiting for input) improves UX
- Output buffering per session enables "read more" pattern

**Differences**:
- TypeScript vs Python (syntax differences)
- DesktopCommanderMCP uses filesystem sandboxing (we use Docker isolation)
- DesktopCommanderMCP has more complex terminal emulation (we keep simple)

**Key takeaway**: Adapt the session management pattern to Python with asyncio

#### 3. Task-Manager Dockerfile Multi-Stage Build

**Location**: `/Users/jon/source/vibes/infra/task-manager/backend/Dockerfile`
**Similarity**: Multi-stage Python build with uv package manager
**Lessons**:
- Builder stage + runtime stage = minimal images
- uv is fast and reliable for dependency management
- Health checks are essential for Docker Compose
- Virtual environment copying is efficient

**Differences**:
- Task-manager uses `python:3.12-slim`, we'll use `python:3.11-alpine` (smaller)
- Task-manager exposes two ports (API + MCP), we only need MCP port

**Key takeaway**: Copy Dockerfile structure but use Alpine base for even smaller image

---

## Recommendations for PRP

Based on pattern analysis, the PRP should:

1. **Follow task-manager MCP pattern exactly**
   - Use FastMCP with consolidated tools
   - Return JSON strings from all tools (never dicts!)
   - Implement structured error responses with suggestions
   - Truncate large outputs (max 100-200 lines)

2. **Reuse session management pattern from DesktopCommanderMCP**
   - Implement SessionManager class for process tracking
   - Support long-running commands with read_output()
   - Enable send_input() for interactive commands
   - Implement graceful termination (SIGTERM -> SIGKILL)

3. **Mirror task-manager file structure**
   - `src/mcp_server.py` - main MCP server
   - `src/command_executor.py` - execution engine
   - `src/session_manager.py` - process sessions
   - `src/security.py` - validation and blocklist
   - `tests/` - parallel test structure

4. **Adapt task-manager Dockerfile for Alpine**
   - Multi-stage build (builder + runtime)
   - Use `python:3.11-alpine` base
   - Install build dependencies in builder stage only
   - Copy venv from builder to runtime
   - Health check on port 8000

5. **Integrate with vibes-network**
   - Use `vibes-network` external network in docker-compose.yml
   - Follow naming convention: `vibesbox` service name
   - No port exposure needed (MCP server accessed via network)
   - Add health check for dependency management

6. **Implement 2-3 consolidated tools maximum**
   - `execute_command(command, shell, timeout, stream)` - main execution tool
   - `manage_process(action, pid, signal)` - list/kill/read processes
   - Optional: `get_config()` / `set_config()` for runtime configuration

7. **Add comprehensive security layer**
   - Blocklist for dangerous commands (rm -rf /, fork bombs, etc.)
   - Command validation before execution
   - Resource limits via Docker (512MB RAM, 0.5 CPU, 100 PIDs)
   - Non-root user in container

8. **Test at multiple levels**
   - Unit tests for command_executor, security, session_manager
   - Integration tests against running Docker container
   - Test command timeout enforcement
   - Test process cleanup on shutdown

---

## Source References

### From Archon Knowledge Base

- **MCP Protocol Spec** (source: d60a71d62eb201d5) - Relevance 7/10
  - Tool discovery via `*/list` methods
  - Tool execution via `tools/call`
  - Return format expectations (JSON strings)

- **MCP Tools Best Practices** (source: c0e629a894699314) - Relevance 6/10
  - Tool naming conventions
  - Error handling patterns
  - Timeout management

**Note**: Archon searches returned mostly high-level documentation. Local codebase patterns are more directly applicable.

### From Local Codebase

- **`/Users/jon/source/vibes/infra/task-manager/backend/src/mcp_server.py`** - DEFINITIVE pattern
  - Lines 12-15: JSON string return requirement
  - Lines 38-79: Response truncation pattern
  - Lines 82-199: Consolidated tool pattern (find_tasks)
  - Lines 201-357: Action-based tool pattern (manage_task)

- **`/Users/jon/source/vibes/repos/DesktopCommanderMCP/src/terminal-manager.ts`** - Process management
  - Lines 46-188: Async subprocess execution with streaming
  - Lines 225-244: Graceful termination (SIGTERM -> SIGKILL)
  - Lines 247-258: Session tracking and cleanup

- **`/Users/jon/source/vibes/repos/DesktopCommanderMCP/src/tools/process.ts`** - Process tools
  - Lines 9-40: list_processes implementation
  - Lines 42-62: kill_process with error handling

- **`/Users/jon/source/vibes/infra/task-manager/backend/Dockerfile`** - Docker pattern
  - Lines 1-23: Builder stage with uv
  - Lines 24-58: Runtime stage with venv copy
  - Lines 52-53: Health check pattern

- **`/Users/jon/source/vibes/infra/task-manager/docker-compose.yml`** - Docker Compose
  - Lines 24-29: Health check configuration
  - Lines 59-62: depends_on with health check condition
  - Lines 101-103: Custom bridge network

- **`/Users/jon/source/vibes/mcp/mcp-vibes-server/docker-compose.yml`** - vibes-network
  - Lines 13-16: External vibes-network usage (correct pattern)

- **`/Users/jon/source/vibes/mcp/mcp-vibesbox-server/docker-compose.yml`** - Existing vibesbox
  - Lines 29-32: vibes-network integration
  - Shows this is standard pattern for all vibes services

---

## Next Steps for Assembler

When generating the PRP:

1. **Reference these patterns in "Current Codebase Tree" section**:
   - Task-manager mcp_server.py as MCP server template
   - DesktopCommanderMCP terminal-manager.ts for process management concepts
   - Task-manager Dockerfile for Docker build pattern

2. **Include key code snippets in "Implementation Blueprint"**:
   - FastMCP tool decorator pattern
   - JSON string return example
   - Async subprocess streaming example
   - Session manager class structure
   - Docker multi-stage build template

3. **Add anti-patterns to "Known Gotchas" section**:
   - MCP tools MUST return JSON strings (Gotcha #3)
   - Always truncate command output (100-200 lines max)
   - Use asyncio.wait_for() for timeouts
   - Clean up orphaned processes on shutdown
   - Install build deps in Alpine builder stage

4. **Use file organization for "Desired Codebase Tree"**:
   ```
   infra/vibesbox/
   ├── src/
   │   ├── mcp_server.py
   │   ├── command_executor.py
   │   ├── session_manager.py
   │   └── security.py
   ├── tests/
   ├── Dockerfile
   └── docker-compose.yml
   ```

5. **Reference vibes-network pattern**:
   - All vibes services use external `vibes-network`
   - No isolated networks for infra services
   - Health checks enable proper startup ordering

6. **Emphasize proven patterns**:
   - Task-manager MCP server is production-ready reference
   - Multi-stage Docker builds proven across infra/
   - Consolidated tool pattern reduces complexity
   - Session management enables advanced use cases

**Success metric**: The PRP should enable implementation without needing to reference external docs - all patterns are documented here with working code examples from the codebase.
