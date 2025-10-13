# PRP: Streamlined Vibesbox MCP Server

**Generated**: 2025-10-13
**Based On**: prps/INITIAL_streamlined_vibesbox.md
**Archon Project**: 66393d5a-33c4-4957-b933-c0c3e5ca396e

---

## Goal

Build a lightweight containerized MCP server for secure command execution via HTTP streaming. This is a clean, minimal implementation focused purely on command execution capabilities without VNC/GUI overhead - an agent jumpbox for Claude to execute shell commands safely in an isolated Docker environment.

**End State**:
- Minimal Alpine/Debian-based Docker container (~100-200MB)
- FastMCP HTTP server at port 8000 exposing 2-3 consolidated MCP tools
- Secure command execution with sandboxing, resource limits, and blocklist validation
- Real-time streaming output for long-running commands
- Process session management for background tasks
- Full integration with vibes-network for inter-service communication

---

## Why

**Current Pain Points**:
- Need secure command execution environment for AI agents
- Existing vibesbox implementation has VNC/GUI overhead not needed for pure command execution
- No isolated sandboxed environment for potentially dangerous agent-generated commands
- Agents need ability to run long-running commands with streaming output

**Business Value**:
- Enables Claude to perform system administration tasks safely
- Provides foundation for autonomous agent workflows (file manipulation, data processing, etc.)
- Docker isolation prevents agent mistakes from affecting host system
- Streamlined design (vs full desktop environment) = faster startup, less resource usage
- Reusable pattern for future MCP server implementations in vibes ecosystem

---

## What

### Core Features

1. **FastMCP HTTP Server**
   - Tool 1: `execute_command(command, shell, timeout, stream)` - Execute shell commands with optional streaming
   - Tool 2: `manage_process(action, pid, signal)` - List/kill/read running processes
   - JSON-RPC 2.0 over HTTP at `/mcp` endpoint
   - Health check endpoint at `/health` for Docker monitoring

2. **Secure Command Execution**
   - Command validation with blocklist (rm -rf /, fork bombs, etc.)
   - Async subprocess execution with real-time output streaming
   - Configurable timeout enforcement (default 30s, max 300s)
   - Graceful termination (SIGTERM → SIGKILL) for hung processes
   - Output truncation to prevent context window exhaustion (max 100-200 lines)

3. **Process Session Management**
   - Track running processes by PID
   - Background process support for long-running commands
   - Session cleanup on container shutdown
   - Zombie process prevention via automatic reaping

4. **Docker Security**
   - Non-root user execution (UID 1000)
   - Resource limits: 512MB RAM, 0.5 CPU, 100 PIDs
   - Read-only root filesystem where possible
   - Capability dropping (no privileged operations)
   - Network isolation via vibes-network

### Success Criteria

- [ ] Container builds successfully and starts in <5 seconds
- [ ] Image size <200MB (Alpine) or <400MB (Debian slim)
- [ ] Execute simple commands: `echo`, `ls`, `pwd` return correct output
- [ ] Long-running commands stream output line-by-line
- [ ] Blocked commands (`rm -rf /`) rejected with error
- [ ] Timeout enforcement terminates hung processes after specified duration
- [ ] No zombie processes accumulate after executing 50+ commands
- [ ] Health check passes and container integrates with vibes-network
- [ ] All validation gates pass: ruff, mypy, pytest
- [ ] Integration test suite passes (command execution, streaming, process management)

---

## All Needed Context

### Documentation & References

```yaml
# MUST READ - FastMCP Framework
- url: https://gofastmcp.com/getting-started/welcome
  sections:
    - "Getting Started" - FastMCP 2.0 architecture and HTTP server patterns
    - "Tool Registration" - Decorator-based tool definition with @mcp.tool()
  why: Core framework for Python MCP servers, provides HTTP transport out of the box
  critical_gotchas:
    - Tools MUST return JSON strings (json.dumps()), never Python dicts
    - HTTP streaming is preferred transport (supersedes SSE in latest spec)

- url: https://github.com/jlowin/fastmcp
  sections:
    - "Examples" - Working code samples for server initialization
  why: Source code examples demonstrate actual usage patterns
  critical_gotchas:
    - FastMCP v2.x uses decorator pattern, no manual registration needed

# MUST READ - MCP Protocol Specification
- url: https://modelcontextprotocol.io/specification/2025-06-18
  sections:
    - "Streamable HTTP Transport" - POST/GET endpoints, chunked encoding
    - "Tool Design Patterns" - Tool primitives, discovery, security
    - "Security Best Practices" - User consent, untrusted descriptions, authorization
  why: Defines protocol requirements for HTTP-based MCP servers
  critical_gotchas:
    - Tools represent arbitrary code execution - require explicit validation
    - Tool descriptions should be considered untrusted unless from verified server
    - Explicit user consent required before invoking any tool

# MUST READ - Python Asyncio Subprocess
- url: https://docs.python.org/3/library/asyncio-subprocess.html
  sections:
    - "Creating Subprocesses" - create_subprocess_shell() and create_subprocess_exec()
    - "Process Class" - Process lifecycle (wait, terminate, kill, send_signal)
    - "Asyncio Streams" - StreamReader for reading output line-by-line
  why: Core API for async command execution with streaming
  critical_gotchas:
    - Always await process.wait() to prevent zombie processes
    - Use PIPE for stdout/stderr to enable streaming
    - communicate() reads ALL output - use readline() for streaming
    - Decode output with .decode('utf-8', errors='replace')

# MUST READ - Command Injection Security
- url: https://snyk.io/blog/command-injection-python-prevention-examples/
  sections:
    - "Subprocess Security" - shell=True vulnerabilities (CWE-78)
    - "Safe Approaches" - shlex.split() + create_subprocess_exec()
  why: Critical security knowledge for command execution
  critical_gotchas:
    - NEVER use shell=True with user input - enables command injection
    - Use shlex.split() to parse commands safely into argument lists
    - Shell metacharacters (;, |, &, &&, ||, $, `) are dangerous with shell=True
    - Allowlists better than blocklists for command validation

- url: https://www.cisa.gov/resources-tools/resources/secure-design-alert-eliminating-os-command-injection-vulnerabilities
  sections:
    - "CISA Secure by Design Alert" - Command injection elimination strategies
  why: Government security guidance on preventing OS command injection
  critical_gotchas:
    - Command injection enabled major threat actor campaigns in 2024

# MUST READ - Docker Resource Constraints
- url: https://docs.docker.com/engine/containers/resource_constraints/
  sections:
    - "Memory Limits" - --memory, --memory-swap, OOM behavior
    - "CPU Constraints" - --cpus, --cpu-shares, CFS scheduler
  why: Configure resource limits to prevent resource abuse
  critical_gotchas:
    - Default: containers have NO resource limits
    - PID limits prevent fork bombs (set pids_limit: 100)
    - Memory limits prevent excessive host memory consumption

- url: https://docs.docker.com/reference/compose-file/deploy/
  sections:
    - "Deploy Resources" - Compose syntax for limits/reservations
  why: Docker Compose resource limit configuration
  critical_gotchas:
    - Use cpus as string ('0.50') not cpu_count (integer)
    - deploy section works in swarm AND standalone mode (3.9+)

# MUST READ - Docker Security
- url: https://docs.docker.com/build/building/best-practices/
  sections:
    - "Security Best Practices" - Non-root users, minimal packages, specific tags
  why: Container security hardening strategies
  critical_gotchas:
    - Always run as non-root user
    - Pin base image versions (python:3.11-slim not python:slim)
    - Minimize installed packages to reduce attack surface

# ESSENTIAL LOCAL FILES
- file: prps/streamlined_vibesbox/examples/README.md
  why: Comprehensive guide to 5 production-tested patterns from vibes codebase
  pattern: STUDY THIS FIRST before writing any code

- file: prps/streamlined_vibesbox/examples/fastmcp_server_pattern.py
  why: Exact MCP server pattern from task-manager (production code)
  critical: Tools MUST return json.dumps(), never dicts - this is non-negotiable
  pattern: Consolidated tool design, structured error responses, output truncation

- file: prps/streamlined_vibesbox/examples/subprocess_streaming_pattern.py
  why: Async subprocess execution with streaming output and session management
  critical: Stream output as it arrives (don't wait for communicate())
  pattern: asyncio.create_subprocess_shell with PIPE, async iteration, timeout handling

- file: prps/streamlined_vibesbox/examples/docker_alpine_python_pattern.dockerfile
  why: Multi-stage Docker build for minimal Python images
  critical: PYTHONUNBUFFERED=1 required for streaming output
  pattern: Builder + runtime stages, uv package manager, health checks

- file: prps/streamlined_vibesbox/examples/docker_compose_pattern.yml
  why: Docker Compose with health checks and resource limits
  critical: PID limit (100) prevents fork bombs, external vibes-network integration
  pattern: Resource limits (CPU, memory, PIDs), health checks, network configuration

- file: prps/streamlined_vibesbox/examples/process_cleanup_pattern.py
  why: Graceful process cleanup and session management
  critical: Two-stage termination (SIGTERM → SIGKILL) prevents resource leaks
  pattern: SessionManager class, limited history (max 100), cleanup on shutdown

- file: /Users/jon/source/vibes/infra/task-manager/backend/src/mcp_server.py
  why: Definitive MCP server implementation pattern for vibes codebase
  critical: JSON string returns, response truncation, consolidated tools
  pattern: Lines 12-15 (JSON strings), 38-79 (truncation), 82-357 (tools)

- file: /Users/jon/source/vibes/infra/task-manager/backend/Dockerfile
  why: Production Docker multi-stage build pattern
  critical: Virtual environment copying, health checks, PYTHONUNBUFFERED=1
  pattern: Lines 1-23 (builder), 24-58 (runtime), 52-53 (health check)

- file: /Users/jon/source/vibes/infra/task-manager/docker-compose.yml
  why: vibes-network integration pattern
  critical: External network usage, health check dependencies
  pattern: Lines 59-62 (depends_on with health check), 101-103 (network)
```

### Current Codebase Tree

```
vibes/
├── infra/
│   ├── task-manager/              # Reference MCP server (FastMCP)
│   │   ├── backend/
│   │   │   ├── src/
│   │   │   │   ├── mcp_server.py  # DEFINITIVE pattern for MCP tools
│   │   │   │   └── services/      # Service layer pattern
│   │   │   ├── Dockerfile         # Multi-stage build pattern
│   │   │   └── start.sh           # Container startup script
│   │   └── docker-compose.yml     # vibes-network integration
│   └── archon/                    # Another MCP server reference
│       └── mcp_server.py          # Similar patterns
├── repos/
│   └── DesktopCommanderMCP/       # Reference for process management
│       └── src/
│           └── terminal-manager.ts # Session management patterns
├── prps/
│   └── streamlined_vibesbox/
│       ├── examples/              # 5 extracted code patterns
│       │   ├── README.md          # MUST READ comprehensive guide
│       │   ├── fastmcp_server_pattern.py
│       │   ├── subprocess_streaming_pattern.py
│       │   ├── docker_alpine_python_pattern.dockerfile
│       │   ├── docker_compose_pattern.yml
│       │   └── process_cleanup_pattern.py
│       └── planning/              # Research documents
│           ├── feature-analysis.md
│           ├── codebase-patterns.md
│           ├── documentation-links.md
│           ├── examples-to-include.md
│           └── gotchas.md
└── docker-compose.yml             # Root compose file
```

### Desired Codebase Tree

```
infra/vibesbox/
├── src/
│   ├── mcp_server.py              # Main MCP server entrypoint (FastMCP)
│   │                              # Tools: execute_command, manage_process
│   ├── command_executor.py        # Command execution engine
│   │                              # Functions: execute_command, stream_output
│   ├── session_manager.py         # Process session management
│   │                              # Classes: SessionManager, CommandSession
│   ├── security.py                # Command validation & blocklist
│   │                              # Functions: validate_command, is_blocked
│   └── models.py                  # Pydantic models
│                                  # Models: CommandRequest, CommandResult, SessionInfo
├── tests/
│   ├── test_mcp_server.py         # MCP tool tests
│   ├── test_command_executor.py   # Command execution tests
│   ├── test_security.py           # Security validation tests
│   └── test_session_manager.py    # Session management tests
├── Dockerfile                      # Multi-stage Alpine/Debian build
├── docker-compose.yml              # vibes-network integration
├── pyproject.toml                  # Dependency management (uv)
├── start.sh                        # Container startup script
└── README.md                       # Setup and usage docs

**New Files**:
- src/mcp_server.py (150 lines) - FastMCP server with tool definitions
- src/command_executor.py (200 lines) - Async subprocess execution logic
- src/session_manager.py (150 lines) - Process tracking and cleanup
- src/security.py (100 lines) - Command validation and blocklist
- src/models.py (80 lines) - Pydantic data models
- Dockerfile (60 lines) - Multi-stage Docker build
- docker-compose.yml (40 lines) - Compose configuration
- start.sh (20 lines) - Startup script
- pyproject.toml (30 lines) - Dependencies
- tests/*.py (400 lines total) - Test suite
```

### Known Gotchas & Library Quirks

```python
# CRITICAL GOTCHA #1: MCP Tools MUST Return JSON Strings
# Source: /Users/jon/source/vibes/infra/task-manager/backend/src/mcp_server.py (lines 12-15)
# Impact: Tools break completely if returning dicts

# ❌ WRONG - Returns dict (BREAKS MCP!)
@mcp.tool()
async def execute_command(command: str) -> dict:
    return {"result": "value"}  # FAILS!

# ✅ RIGHT - Returns JSON string (WORKS!)
@mcp.tool()
async def execute_command(command: str) -> str:
    return json.dumps({"result": "value"})  # SUCCESS!

# CRITICAL GOTCHA #2: Command Injection via shell=True
# Source: https://snyk.io/blog/command-injection-python-prevention-examples/
# Impact: Arbitrary code execution, data exfiltration, system compromise

# ❌ WRONG - Vulnerable to injection
process = await asyncio.create_subprocess_shell(
    user_command,  # Can contain: "; rm -rf /"
    shell=True  # DANGEROUS!
)

# ✅ RIGHT - Safe approach
import shlex
args = shlex.split(user_command)
process = await asyncio.create_subprocess_exec(
    *args,  # Argument list - no shell injection possible
    # shell=True omitted (defaults to False)
)

# CRITICAL GOTCHA #3: Zombie Process Accumulation
# Source: https://stackoverflow.com/questions/60542596/
# Impact: PID exhaustion, resource leaks, container restart required

# ❌ WRONG - Creates zombies
process = await asyncio.create_subprocess_shell(command, ...)
stdout, stderr = await process.communicate()
# Missing: await process.wait() - process becomes zombie!

# ✅ RIGHT - Proper cleanup
process = await asyncio.create_subprocess_shell(command, ...)
try:
    stdout, stderr = await process.communicate()
    await process.wait()  # Reap the process
finally:
    if process.returncode is None:
        process.kill()
        await process.wait()  # Reap killed process

# CRITICAL GOTCHA #4: Docker Container Escape (CVE-2024-21626)
# Source: https://thehackernews.com/2025/08/docker-fixes-cve-2025-9074-critical.html
# Impact: Container escape to host system, privilege escalation

# ❌ WRONG - Running as root
FROM python:3.11-alpine
CMD ["python", "server.py"]  # Runs as root!

# ✅ RIGHT - Non-root user
FROM python:3.11-alpine
RUN addgroup -S vibesbox && adduser -S vibesbox -G vibesbox
USER vibesbox  # Run as non-root
CMD ["python", "server.py"]

# HIGH PRIORITY GOTCHA #5: Output Truncation Required
# Source: /Users/jon/source/vibes/infra/task-manager/backend/src/mcp_server.py (lines 38-79)
# Impact: Context window exhaustion, poor performance, unusable responses

# ❌ WRONG - Returns full output (can be 100k lines)
return json.dumps({"stdout": result.stdout})

# ✅ RIGHT - Truncate output
lines = result.stdout.split('\n')
if len(lines) > 100:
    truncated = lines[:100]
    truncated.append(f"... [truncated {len(lines) - 100} more lines]")
    stdout = '\n'.join(truncated)
else:
    stdout = result.stdout
return json.dumps({"stdout": stdout, "truncated": len(lines) > 100})

# HIGH PRIORITY GOTCHA #6: Timeout Enforcement
# Source: Python asyncio subprocess documentation
# Impact: Hung processes, server unresponsiveness, resource exhaustion

# ❌ WRONG - No timeout (hangs forever)
stdout, stderr = await process.communicate()

# ✅ RIGHT - Timeout with graceful termination
try:
    stdout, stderr = await asyncio.wait_for(
        process.communicate(),
        timeout=30
    )
except asyncio.TimeoutError:
    process.terminate()  # SIGTERM (graceful)
    try:
        await asyncio.wait_for(process.wait(), timeout=1.0)
    except asyncio.TimeoutError:
        process.kill()  # SIGKILL (force)
    await process.wait()

# MEDIUM PRIORITY GOTCHA #7: Alpine Python Compatibility
# Source: https://pythonspeed.com/articles/alpine-docker-python/
# Impact: 50x slower builds, larger images, runtime incompatibilities

# ❌ PROBLEMATIC - Alpine can be slower for Python
FROM python:3.11-alpine
RUN pip install -r requirements.txt  # Can take 30+ minutes!
# Result: 851MB image, 1,557s build (real benchmark)

# ✅ RECOMMENDED - Debian slim for Python
FROM python:3.11-slim
RUN pip install --no-cache-dir -r requirements.txt  # Uses wheels, fast!
# Result: 363MB image, 30s build (50x faster!)

# MEDIUM PRIORITY GOTCHA #8: FastMCP Confused Deputy
# Source: https://towardsdatascience.com/the-mcp-security-survival-guide/
# Impact: Users can execute privileged commands via MCP server

# ❌ WRONG - No authorization checking
@mcp.tool()
async def execute_command(command: str) -> str:
    return await run_command(command)  # Executes as server's user!

# ✅ RIGHT - Authorization checks
@mcp.tool()
async def execute_command(command: str, user_id: str) -> str:
    # Validate user has permission to execute this command
    user_permission = get_user_permission(user_id)
    if not authorizer.can_execute(command, user_permission):
        return json.dumps({"success": False, "error": "Unauthorized"})
    return await run_command(command)

# MEDIUM PRIORITY GOTCHA #9: Pydantic v2 API Changes
# Source: https://docs.pydantic.dev/latest/api/base_model/
# Impact: Breaking change from v1 to v2

# ❌ WRONG - Pydantic v1 API (deprecated)
result_dict = result.dict()  # AttributeError in v2!
result_json = result.json()  # AttributeError in v2!

# ✅ RIGHT - Pydantic v2 API
result_dict = result.model_dump()
result_json = result.model_dump_json()

# LOW PRIORITY GOTCHA #10: PYTHONUNBUFFERED Required
# Source: Docker Python best practices
# Impact: Streaming output doesn't appear in logs

# ❌ WRONG - Missing environment variable
FROM python:3.11-alpine
CMD ["python", "server.py"]  # Output buffered!

# ✅ RIGHT - Unbuffered output
FROM python:3.11-alpine
ENV PYTHONUNBUFFERED=1  # Critical for streaming!
CMD ["python", "server.py"]

# Vibes Codebase Patterns
# - FastMCP used for all MCP servers (task-manager, archon)
# - Consolidated tool pattern: single tool for multiple operations
# - External vibes-network for all infra services
# - Multi-stage Docker builds with uv package manager
# - Health checks with 30s interval, 10s timeout, 3 retries
# - Non-root user in all containers (security standard)
```

---

## Implementation Blueprint

### Phase 0: Planning & Understanding

**BEFORE starting implementation, complete these steps:**

1. **Read Examples Directory** (30 minutes):
   - `prps/streamlined_vibesbox/examples/README.md` - Comprehensive guide
   - All 5 example files - Study "What to Mimic" sections
   - Note pattern highlights for quick reference

2. **Study Reference Implementations** (20 minutes):
   - `/Users/jon/source/vibes/infra/task-manager/backend/src/mcp_server.py` - MCP server pattern
   - Focus on: JSON string returns, consolidated tools, error handling
   - Note truncation pattern (lines 38-79)

3. **Review Security Requirements** (15 minutes):
   - Command injection prevention: shlex.split() + create_subprocess_exec()
   - Allowlist approach: define ALLOWED_COMMANDS explicitly
   - Docker security: non-root user, resource limits, capability dropping

4. **Understand Integration Points** (10 minutes):
   - vibes-network external network requirement
   - Health check pattern for Docker Compose dependencies
   - Port 8000 for MCP HTTP server

### Task List (Execute in Order)

```yaml
Task 1: Project Setup and Dependencies
RESPONSIBILITY: Create project structure and install dependencies

FILES TO CREATE:
  - infra/vibesbox/pyproject.toml
  - infra/vibesbox/.gitignore

PATTERN TO FOLLOW: task-manager/backend/pyproject.toml

SPECIFIC STEPS:
  1. Create infra/vibesbox/ directory
  2. Initialize pyproject.toml with dependencies:
     - fastmcp>=2.0.0 (MCP server framework)
     - pydantic>=2.0.0 (data validation)
     - uvicorn>=0.30.0 (ASGI server)
  3. Add dev dependencies:
     - pytest>=8.0.0
     - pytest-asyncio>=0.23.0
     - pytest-subprocess>=1.5.0 (for mocking)
     - ruff>=0.3.0 (linting)
     - mypy>=1.9.0 (type checking)
  4. Create .gitignore (Python patterns)

VALIDATION:
  - pyproject.toml has all required dependencies
  - Directory structure matches desired tree

---

Task 2: Data Models (Pydantic Schemas)
RESPONSIBILITY: Define type-safe data models for requests/responses

FILES TO CREATE:
  - infra/vibesbox/src/models.py

PATTERN TO FOLLOW: Pydantic BaseModel with validators

SPECIFIC STEPS:
  1. Create CommandRequest model:
     - command: str (required)
     - shell: str = "/bin/sh" (default)
     - timeout: int = 30 (default, range 1-300)
     - stream: bool = True (default)
  2. Create CommandResult model:
     - success: bool
     - exit_code: int | None
     - stdout: str
     - stderr: str
     - truncated: bool
     - error: str | None
  3. Create SessionInfo model:
     - pid: int
     - command: str
     - started_at: datetime
     - status: str ("running" | "completed" | "terminated")
  4. Add field validators for command length, timeout range

VALIDATION:
  - Models instantiate successfully
  - Validators catch invalid input (empty command, timeout out of range)
  - model_dump_json() returns valid JSON strings

---

Task 3: Security Layer (Command Validation)
RESPONSIBILITY: Implement command validation and blocklist

FILES TO CREATE:
  - infra/vibesbox/src/security.py

PATTERN TO FOLLOW: Allowlist validation with shlex parsing

SPECIFIC STEPS:
  1. Define BLOCKED_COMMANDS list:
     - "rm -rf /"
     - "dd if=/dev/zero"
     - ":(){ :|:& };:" (fork bomb)
     - "chmod -R 777 /"
     - "mkfs"
  2. Define ALLOWED_COMMANDS set:
     - Read-only: ls, pwd, cat, grep, echo, find
     - Write: touch, mkdir, cp, mv
     - System: ps, top, df, du
  3. Implement validate_command(command: str) -> tuple[bool, str]:
     - Parse with shlex.split()
     - Check if command in ALLOWED_COMMANDS
     - Check for blocked patterns
     - Check for shell metacharacters (;, |, &, $, `)
     - Return (is_valid, error_message)
  4. Implement sanitize_output(output: str) -> str:
     - Redact secrets (API_KEY=, PASSWORD=, TOKEN=)
     - Use regex patterns to replace with [REDACTED]

VALIDATION:
  - Allowed commands pass validation
  - Blocked commands rejected with clear error
  - Shell metacharacters caught (e.g., "ls; rm -rf /")
  - Secrets redacted from output

---

Task 4: Command Executor (Async Subprocess)
RESPONSIBILITY: Execute commands with streaming output and timeout handling

FILES TO CREATE:
  - infra/vibesbox/src/command_executor.py

PATTERN TO FOLLOW: examples/subprocess_streaming_pattern.py

SPECIFIC STEPS:
  1. Implement stream_command_output(command, shell, timeout) -> AsyncIterator[str]:
     - Use asyncio.create_subprocess_shell with PIPE
     - Async iterate over stdout.readline()
     - Yield lines as they arrive
     - Handle timeout with asyncio.wait_for()
     - Graceful termination: SIGTERM → wait 1s → SIGKILL
  2. Implement execute_command(command, shell, timeout, stream) -> CommandResult:
     - Validate command with security.validate_command()
     - If stream=True: collect from stream_command_output()
     - If stream=False: use communicate() with timeout
     - Truncate output to max 100 lines
     - Sanitize output to redact secrets
     - Return CommandResult model
  3. Add helper: truncate_output(output, max_lines=100) -> tuple[str, bool]:
     - Split into lines, truncate if > max_lines
     - Append "... [truncated N more lines]"
     - Return (truncated_output, was_truncated)

VALIDATION:
  - Simple commands execute: echo "test" returns "test"
  - Long commands stream line-by-line
  - Timeout enforced: sleep 100 with timeout=1 terminates in ~1s
  - Output truncated: 500-line output returns only 100 + truncation message
  - Secrets redacted: env | grep API_KEY shows [REDACTED]

---

Task 5: Session Manager (Process Tracking)
RESPONSIBILITY: Track long-running processes and prevent zombies

FILES TO CREATE:
  - infra/vibesbox/src/session_manager.py

PATTERN TO FOLLOW: examples/process_cleanup_pattern.py

SPECIFIC STEPS:
  1. Define CommandSession dataclass:
     - session_id: str
     - command: str
     - process: asyncio.subprocess.Process
     - started_at: float (time.time())
     - output_buffer: list[str]
  2. Implement SessionManager class:
     - sessions: dict[int, CommandSession]
     - completed: dict[int, CommandSession] (max 100)
  3. Implement methods:
     - start_session(command, shell) -> int (returns PID)
     - get_session(pid) -> CommandSession | None
     - read_output(pid) -> str (new output since last read)
     - terminate_session(pid, force=False) -> bool
     - cleanup_all() -> None (called on shutdown)
  4. Add background reaping:
     - When process completes, move to completed dict
     - Limit completed dict to 100 most recent
     - Cleanup zombie processes automatically

VALIDATION:
  - Start session returns valid PID
  - read_output() returns incremental output
  - terminate_session() terminates process gracefully
  - cleanup_all() terminates all running processes
  - No zombies accumulate after 50 sessions

---

Task 6: MCP Server (FastMCP Tools)
RESPONSIBILITY: Expose command execution via MCP protocol

FILES TO CREATE:
  - infra/vibesbox/src/mcp_server.py

PATTERN TO FOLLOW: examples/fastmcp_server_pattern.py + task-manager/mcp_server.py

SPECIFIC STEPS:
  1. Initialize FastMCP:
     - mcp = FastMCP("Vibesbox Command Executor")
  2. Create execute_command tool:
     - @mcp.tool() decorator
     - Parameters: command, shell="/bin/sh", timeout=30, stream=True
     - Call command_executor.execute_command()
     - Return json.dumps(CommandResult.model_dump())
     - Handle errors with try/except
  3. Create manage_process tool:
     - @mcp.tool() decorator
     - Parameters: action ("list" | "kill" | "read"), pid, signal="SIGTERM"
     - Action "list": return all sessions from session_manager
     - Action "kill": terminate_session(pid, force=(signal=="SIGKILL"))
     - Action "read": read_output(pid)
     - Return json.dumps() of result
  4. Add health check endpoint:
     - GET /health returns {"status": "healthy"}
  5. Add main entry point:
     - if __name__ == "__main__": mcp.run()

VALIDATION:
  - Server starts without errors
  - Health check returns 200 OK
  - execute_command tool works via HTTP POST
  - manage_process tool lists/kills/reads sessions
  - All responses are JSON strings (not dicts)

---

Task 7: Docker Configuration
RESPONSIBILITY: Containerize MCP server with security hardening

FILES TO CREATE:
  - infra/vibesbox/Dockerfile
  - infra/vibesbox/.dockerignore

PATTERN TO FOLLOW: examples/docker_alpine_python_pattern.dockerfile

SPECIFIC STEPS:
  1. Multi-stage build:
     - Builder stage: python:3.11-slim, install uv, create venv, install deps
     - Runtime stage: python:3.11-slim, copy venv, copy src/
  2. Create non-root user:
     - RUN groupadd -r vibesbox && useradd -r -g vibesbox vibesbox
     - RUN chown -R vibesbox:vibesbox /app
     - USER vibesbox
  3. Set environment variables:
     - ENV PYTHONUNBUFFERED=1 (critical for streaming!)
     - ENV PATH="/venv/bin:$PATH"
  4. Add health check:
     - HEALTHCHECK --interval=30s --timeout=10s --retries=3
     - CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
  5. Expose port 8000
  6. CMD ["python", "src/mcp_server.py"]

VALIDATION:
  - Image builds successfully
  - Image size <400MB (Debian slim)
  - Container starts in <5 seconds
  - Health check passes after startup
  - Runs as non-root user (docker exec vibesbox whoami != root)

---

Task 8: Docker Compose Integration
RESPONSIBILITY: Integrate with vibes-network and configure resource limits

FILES TO CREATE:
  - infra/vibesbox/docker-compose.yml

PATTERN TO FOLLOW: examples/docker_compose_pattern.yml

SPECIFIC STEPS:
  1. Define vibesbox service:
     - build: . (use local Dockerfile)
     - container_name: vibesbox
     - ports: "8000:8000"
  2. Add resource limits:
     - deploy.resources.limits.cpus: '0.50'
     - deploy.resources.limits.memory: 512M
     - pids_limit: 100
  3. Add security options:
     - security_opt: ["no-new-privileges:true"]
     - cap_drop: ["ALL"]
     - cap_add: ["CHOWN", "SETGID", "SETUID"]
  4. Configure health check:
     - healthcheck with 30s interval, 10s timeout, 3 retries
  5. Connect to vibes-network:
     - networks: [vibes-network]
     - networks.vibes-network.external: true

VALIDATION:
  - docker compose up builds and starts successfully
  - Container joins vibes-network
  - Health check passes
  - Resource limits enforced (check docker stats)
  - PID limit enforced (attempt to create 101 processes fails)

---

Task 9: Startup Script
RESPONSIBILITY: Container initialization script

FILES TO CREATE:
  - infra/vibesbox/start.sh

PATTERN TO FOLLOW: task-manager/backend/start.sh

SPECIFIC STEPS:
  1. Add shebang: #!/bin/sh
  2. Set -e (exit on error)
  3. Echo startup message
  4. Run MCP server: python src/mcp_server.py
  5. Make executable: chmod +x start.sh

VALIDATION:
  - Script runs without errors
  - MCP server starts successfully

---

Task 10: Unit Tests
RESPONSIBILITY: Test individual components in isolation

FILES TO CREATE:
  - infra/vibesbox/tests/test_security.py
  - infra/vibesbox/tests/test_command_executor.py
  - infra/vibesbox/tests/test_session_manager.py
  - infra/vibesbox/tests/test_mcp_server.py

PATTERN TO FOLLOW: pytest-asyncio with mocking

SPECIFIC STEPS:
  1. test_security.py:
     - test_allowed_commands_pass()
     - test_blocked_commands_rejected()
     - test_shell_metacharacters_caught()
     - test_secrets_redacted()
  2. test_command_executor.py:
     - test_execute_simple_command()
     - test_execute_with_timeout()
     - test_output_truncation()
     - test_streaming_output()
  3. test_session_manager.py:
     - test_start_session()
     - test_terminate_session()
     - test_no_zombie_accumulation()
     - test_cleanup_all()
  4. test_mcp_server.py:
     - test_execute_command_tool()
     - test_manage_process_tool()
     - test_json_string_responses()
     - test_error_handling()

VALIDATION:
  - All unit tests pass: pytest tests/ -v
  - No linting errors: ruff check src/
  - No type errors: mypy src/

---

Task 11: Integration Tests
RESPONSIBILITY: Test against running Docker container

FILES TO CREATE:
  - infra/vibesbox/tests/test_integration.py

PATTERN TO FOLLOW: Docker-based integration tests

SPECIFIC STEPS:
  1. Add fixture to start container:
     - docker compose up -d
     - Wait for health check
     - Yield
     - docker compose down -v
  2. Test command execution:
     - POST /mcp with execute_command tool
     - Verify response structure
     - Verify stdout contains expected output
  3. Test process management:
     - Start background process
     - List processes
     - Read output
     - Kill process
  4. Test timeout enforcement:
     - Execute sleep 100 with timeout=1
     - Verify terminates in ~1s
  5. Test blocked commands:
     - Execute rm -rf /
     - Verify rejected with error

VALIDATION:
  - Integration tests pass
  - Container starts/stops cleanly
  - No processes left running

---

Task 12: Documentation
RESPONSIBILITY: Usage documentation and examples

FILES TO CREATE:
  - infra/vibesbox/README.md

SPECIFIC STEPS:
  1. Overview section:
     - What vibesbox does
     - Architecture diagram (ASCII)
  2. Quick Start:
     - docker compose up
     - Health check verification
  3. Usage Examples:
     - Execute command via HTTP
     - Stream long-running command
     - Manage processes
  4. Security Considerations:
     - Command validation
     - Resource limits
     - Non-root user
  5. Development:
     - Running tests
     - Adding new commands to allowlist
  6. Troubleshooting:
     - Common errors and solutions

VALIDATION:
  - README is comprehensive
  - Examples are copy-pasteable
  - Architecture diagram is clear
```

### Implementation Pseudocode

```python
# Task 6: MCP Server Tool Implementation
from mcp.server.fastmcp import FastMCP
import json
from src.command_executor import execute_command as run_command
from src.session_manager import SessionManager

mcp = FastMCP("Vibesbox Command Executor")
session_manager = SessionManager()

@mcp.tool()
async def execute_command(
    command: str,
    shell: str = "/bin/sh",
    timeout: int = 30,
    stream: bool = True
) -> str:
    """Execute shell command with optional streaming.

    CRITICAL: MUST return JSON string (not dict)
    Pattern from: task-manager/mcp_server.py
    """
    try:
        # Execute command (validates internally)
        result = await run_command(
            command=command,
            shell=shell,
            timeout=timeout,
            stream=stream
        )

        # Convert Pydantic model to JSON string
        # Gotcha: NEVER return result.model_dump() (dict)
        return result.model_dump_json()

    except Exception as e:
        # Structured error response
        # Pattern from: task-manager error handling
        return json.dumps({
            "success": False,
            "error": str(e),
            "exit_code": -1,
            "stdout": "",
            "stderr": str(e),
            "suggestion": "Check command syntax and permissions"
        })

@mcp.tool()
async def manage_process(
    action: str,  # "list" | "kill" | "read"
    pid: int | None = None,
    signal: str = "SIGTERM"
) -> str:
    """Manage running processes (consolidated tool).

    Pattern from: task-manager consolidated tools
    """
    try:
        if action == "list":
            # List all sessions
            sessions = session_manager.list_sessions()
            return json.dumps({
                "success": True,
                "processes": [s.to_dict() for s in sessions]
            })

        elif action == "kill" and pid:
            # Terminate specific process
            # Gotcha: Graceful termination (SIGTERM -> SIGKILL)
            force = (signal == "SIGKILL")
            success = await session_manager.terminate_session(pid, force)
            return json.dumps({
                "success": success,
                "message": f"Process {pid} terminated"
            })

        elif action == "read" and pid:
            # Read incremental output
            output = await session_manager.read_output(pid)
            return json.dumps({
                "success": True,
                "pid": pid,
                "output": output
            })

        else:
            return json.dumps({
                "success": False,
                "error": "Invalid action or missing PID"
            })

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })

# Health check endpoint
@mcp.app.get("/health")
async def health_check():
    """Health check for Docker."""
    return {"status": "healthy", "service": "vibesbox"}

# Main entry point
if __name__ == "__main__":
    # Pattern from: task-manager/mcp_server.py
    mcp.run()  # Starts HTTP server on port 8000

# Task 4: Command Executor Implementation
import asyncio
import shlex
from typing import AsyncIterator
from src.security import validate_command, sanitize_output
from src.models import CommandResult

async def stream_command_output(
    command: str,
    shell: str,
    timeout: int
) -> AsyncIterator[str]:
    """Stream command output line by line.

    Pattern from: examples/subprocess_streaming_pattern.py
    """
    process = None
    try:
        # Create subprocess with pipes
        # Gotcha: Use PIPE for streaming, not communicate()
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            shell=True,
            executable=shell
        )

        # Stream stdout line by line
        # Gotcha: Don't wait for communicate() - read as it arrives
        if process.stdout:
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                yield line.decode('utf-8', errors='replace')

        # Wait for process completion
        await asyncio.wait_for(process.wait(), timeout=timeout)

    except asyncio.TimeoutError:
        # Graceful termination pattern
        # From: examples/process_cleanup_pattern.py
        if process:
            process.terminate()  # SIGTERM (graceful)
            try:
                await asyncio.wait_for(process.wait(), timeout=1.0)
            except asyncio.TimeoutError:
                process.kill()  # SIGKILL (force)
            await process.wait()  # Reap the process

        yield f"\n[Command timed out after {timeout}s and was terminated]"

    finally:
        # Ensure cleanup
        # Gotcha: MUST wait() to prevent zombies
        if process and process.returncode is None:
            process.kill()
            await process.wait()

async def execute_command(
    command: str,
    shell: str = "/bin/sh",
    timeout: int = 30,
    stream: bool = True
) -> CommandResult:
    """Execute command with validation and output handling.

    Pattern from: examples/subprocess_streaming_pattern.py
    """
    # Security validation BEFORE execution
    # Pattern from: security.py
    is_valid, error_msg = validate_command(command)
    if not is_valid:
        return CommandResult(
            success=False,
            exit_code=-1,
            stdout="",
            stderr=error_msg,
            truncated=False,
            error=error_msg
        )

    if stream:
        # Streaming mode: collect output line by line
        output_lines = []
        async for line in stream_command_output(command, shell, timeout):
            output_lines.append(line)
            # Gotcha: Truncate to prevent context window exhaustion
            if len(output_lines) > 100:
                output_lines.append("... [truncated]")
                break

        # Sanitize output to redact secrets
        # Pattern from: security.sanitize_output()
        safe_output = sanitize_output("".join(output_lines))

        return CommandResult(
            success=True,
            exit_code=0,
            stdout=safe_output,
            stderr="",
            truncated=len(output_lines) > 100,
            error=None
        )

    else:
        # Non-streaming mode: wait for completion
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            shell=True,
            executable=shell
        )

        try:
            # Gotcha: Use wait_for() to enforce timeout
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )

            # Truncate output
            stdout_text = stdout.decode('utf-8', errors='replace')
            stderr_text = stderr.decode('utf-8', errors='replace')

            stdout_truncated, was_truncated = truncate_output(stdout_text)
            stderr_truncated, _ = truncate_output(stderr_text)

            # Sanitize
            safe_stdout = sanitize_output(stdout_truncated)
            safe_stderr = sanitize_output(stderr_truncated)

            return CommandResult(
                success=True,
                exit_code=process.returncode,
                stdout=safe_stdout,
                stderr=safe_stderr,
                truncated=was_truncated,
                error=None
            )

        except asyncio.TimeoutError:
            # Timeout handling with graceful termination
            process.terminate()
            try:
                await asyncio.wait_for(process.wait(), timeout=1.0)
            except asyncio.TimeoutError:
                process.kill()
            await process.wait()

            return CommandResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=f"Command timed out after {timeout}s",
                truncated=False,
                error="Timeout"
            )

def truncate_output(output: str, max_lines: int = 100) -> tuple[str, bool]:
    """Truncate output to prevent massive payloads.

    Pattern from: task-manager/mcp_server.py (lines 38-79)
    """
    lines = output.split('\n')
    was_truncated = len(lines) > max_lines

    if was_truncated:
        truncated_lines = lines[:max_lines]
        truncated_lines.append(f"\n... [truncated {len(lines) - max_lines} more lines]")
        return '\n'.join(truncated_lines), True

    return output, False
```

---

## Validation Loop

### Level 1: Syntax & Style Checks

```bash
# Run these FIRST - fix any errors before proceeding
cd infra/vibesbox

# Linting (auto-fix what's possible)
ruff check src/ --fix

# Type checking (static analysis)
mypy src/

# Expected: No errors. If errors, READ the error message and fix.
```

**Common Issues**:
- Missing type hints → Add return types to all functions
- Unused imports → Remove or use them
- Line too long → Break into multiple lines
- Missing docstrings → Add docstrings to public functions

### Level 2: Unit Tests

```python
# Test each component in isolation
# Pattern from: pytest-asyncio best practices

# Security validation tests
# File: tests/test_security.py
import pytest
from src.security import validate_command, sanitize_output

def test_allowed_commands_pass():
    """Allowed commands should pass validation."""
    is_valid, _ = validate_command("ls -la /tmp")
    assert is_valid

def test_blocked_commands_rejected():
    """Blocked commands should be rejected."""
    is_valid, error = validate_command("rm -rf /")
    assert not is_valid
    assert "blocked" in error.lower()

def test_shell_metacharacters_caught():
    """Shell metacharacters should be caught."""
    is_valid, error = validate_command("ls; rm -rf /")
    assert not is_valid
    assert "metacharacter" in error.lower() or ";" in error

def test_secrets_redacted():
    """Secrets should be redacted from output."""
    output = "API_KEY=sk-secret123\nother output"
    safe = sanitize_output(output)
    assert "sk-secret123" not in safe
    assert "[REDACTED]" in safe

# Command executor tests
# File: tests/test_command_executor.py
import pytest
from src.command_executor import execute_command, truncate_output

@pytest.mark.asyncio
async def test_execute_simple_command():
    """Basic command execution works."""
    result = await execute_command("echo 'test'", timeout=5)
    assert result.success
    assert "test" in result.stdout
    assert result.exit_code == 0

@pytest.mark.asyncio
async def test_execute_with_timeout():
    """Timeout enforcement works."""
    result = await execute_command("sleep 100", timeout=1)
    assert not result.success
    assert "timed out" in result.stderr.lower()

def test_output_truncation():
    """Output truncation works."""
    long_output = "\n".join([f"line {i}" for i in range(200)])
    truncated, was_truncated = truncate_output(long_output, max_lines=100)
    assert was_truncated
    assert "truncated" in truncated.lower()
    assert truncated.count('\n') <= 101  # 100 lines + truncation message

# Session manager tests
# File: tests/test_session_manager.py
import pytest
from src.session_manager import SessionManager

@pytest.mark.asyncio
async def test_start_session():
    """Session creation returns valid PID."""
    manager = SessionManager()
    pid = await manager.start_session("sleep 10")
    assert pid > 0
    session = manager.get_session(pid)
    assert session is not None
    await manager.cleanup_all()

@pytest.mark.asyncio
async def test_terminate_session():
    """Session termination works."""
    manager = SessionManager()
    pid = await manager.start_session("sleep 100")
    success = await manager.terminate_session(pid, force=False)
    assert success
    # Process should be terminated
    session = manager.get_session(pid)
    assert session.process.returncode is not None

@pytest.mark.asyncio
async def test_no_zombie_accumulation():
    """No zombies accumulate after many sessions."""
    import subprocess

    # Get initial zombie count
    initial_zombies = subprocess.run(
        ["ps", "aux"],
        capture_output=True,
        text=True
    )
    initial_count = initial_zombies.stdout.count(" Z ")

    # Run 50 commands
    manager = SessionManager()
    for i in range(50):
        await manager.start_session(f"echo test{i}")

    await manager.cleanup_all()

    # Check zombie count hasn't increased
    final_zombies = subprocess.run(
        ["ps", "aux"],
        capture_output=True,
        text=True
    )
    final_count = final_zombies.stdout.count(" Z ")

    assert final_count == initial_count, f"Zombie leak: {final_count - initial_count} zombies"

# MCP server tests
# File: tests/test_mcp_server.py
import pytest
import json
from src.mcp_server import execute_command as execute_command_tool

@pytest.mark.asyncio
async def test_execute_command_tool():
    """MCP execute_command tool works."""
    result_json = await execute_command_tool("echo 'test'", timeout=5)

    # Critical: Must be JSON string, not dict
    assert isinstance(result_json, str)

    result = json.loads(result_json)
    assert result["success"]
    assert "test" in result["stdout"]

@pytest.mark.asyncio
async def test_json_string_responses():
    """All tool responses are JSON strings."""
    result = await execute_command_tool("echo 'test'")

    # Gotcha #2: Must be string, not dict
    assert isinstance(result, str), "Tool must return JSON string, not dict!"

    # Should parse as valid JSON
    parsed = json.loads(result)
    assert "success" in parsed

@pytest.mark.asyncio
async def test_error_handling():
    """Errors return structured JSON."""
    result_json = await execute_command_tool("invalid_command_xyz123", timeout=1)
    result = json.loads(result_json)

    assert not result["success"]
    assert "error" in result
```

```bash
# Run tests and iterate until passing
cd infra/vibesbox
pytest tests/ -v

# If failing:
# 1. Read error message carefully
# 2. Understand root cause
# 3. Fix code (never mock just to pass tests)
# 4. Re-run tests
```

### Level 3: Integration Tests

```bash
# Start the service
cd infra/vibesbox
docker compose up --build -d

# Wait for health check
sleep 5

# Test 1: Health check
curl http://localhost:8000/health
# Expected: {"status": "healthy", "service": "vibesbox"}

# Test 2: Execute simple command
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "execute_command",
      "arguments": {
        "command": "echo hello world",
        "timeout": 5
      }
    },
    "id": 1
  }'
# Expected: JSON response with "hello world" in stdout

# Test 3: List processes
curl -X POST http://localhost:8000/mcp \
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
    "id": 2
  }'
# Expected: JSON response with processes array

# Test 4: Blocked command rejected
curl -X POST http://localhost:8000/mcp \
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
    "id": 3
  }'
# Expected: success: false, error contains "blocked"

# Check logs for errors
docker logs vibesbox

# Cleanup
docker compose down -v
```

**If errors**:
- Check logs: `docker logs vibesbox`
- Check health: `docker exec vibesbox ps aux`
- Verify user: `docker exec vibesbox whoami` (should NOT be root)
- Check resource limits: `docker stats vibesbox`

---

## Final Validation Checklist

Before marking PRP complete:

### Functionality
- [ ] Container builds successfully: `docker compose build`
- [ ] Container starts in <5 seconds: `time docker compose up -d`
- [ ] Health check passes: `curl http://localhost:8000/health`
- [ ] Execute command works: `echo "test"` returns "test"
- [ ] Streaming works: Long commands stream line-by-line
- [ ] Timeout works: `sleep 100` with timeout=1 terminates in ~1s
- [ ] Process management: List/kill/read processes work
- [ ] Blocked commands rejected: `rm -rf /` returns error

### Security
- [ ] Runs as non-root: `docker exec vibesbox whoami` != root
- [ ] Command validation: Blocked commands rejected
- [ ] Shell metacharacters caught: `ls; rm -rf /` rejected
- [ ] Secrets redacted: `env | grep API_KEY` shows [REDACTED]
- [ ] Resource limits enforced: `docker stats vibesbox`
- [ ] PID limit enforced: Cannot create >100 processes

### Quality
- [ ] All unit tests pass: `pytest tests/ -v`
- [ ] No linting errors: `ruff check src/`
- [ ] No type errors: `mypy src/`
- [ ] Integration tests pass
- [ ] No zombie processes: `ps aux | grep Z | wc -l` == 0 after 50 commands
- [ ] Image size <400MB: `docker images | grep vibesbox`

### Integration
- [ ] Connects to vibes-network: `docker network inspect vibes-network`
- [ ] Health check dependency works in compose
- [ ] Logs are readable: `docker logs vibesbox`
- [ ] No errors in startup logs

### Documentation
- [ ] README.md has usage examples
- [ ] Code has docstrings for public functions
- [ ] Example curl commands work
- [ ] Architecture diagram is clear

---

## Anti-Patterns to Avoid

### Security Anti-Patterns

❌ **Never use shell=True with user input**
```python
# WRONG - Enables command injection
process = await asyncio.create_subprocess_shell(user_command, shell=True)

# RIGHT - Safe argument list
args = shlex.split(user_command)
process = await asyncio.create_subprocess_exec(*args)
```

❌ **Never run container as root**
```dockerfile
# WRONG - Runs as root
FROM python:3.11-alpine
CMD ["python", "server.py"]

# RIGHT - Non-root user
FROM python:3.11-alpine
RUN addgroup -S vibesbox && adduser -S vibesbox -G vibesbox
USER vibesbox
CMD ["python", "server.py"]
```

❌ **Never trust AI-generated commands blindly**
```python
# WRONG - No validation
@mcp.tool()
async def execute(command: str) -> str:
    return await run_command(command)  # Dangerous!

# RIGHT - Validate first
@mcp.tool()
async def execute(command: str) -> str:
    is_valid, error = validate_command(command)
    if not is_valid:
        return json.dumps({"success": False, "error": error})
    return await run_command(command)
```

### MCP Protocol Anti-Patterns

❌ **Never return dicts from MCP tools**
```python
# WRONG - Returns dict (BREAKS MCP!)
@mcp.tool()
async def execute(command: str) -> dict:
    return {"result": "value"}  # Tool fails!

# RIGHT - Returns JSON string
@mcp.tool()
async def execute(command: str) -> str:
    return json.dumps({"result": "value"})  # Works!
```

❌ **Never return full command output without truncation**
```python
# WRONG - Can return 100k lines
return json.dumps({"stdout": result.stdout})

# RIGHT - Truncate to 100 lines
stdout, truncated = truncate_output(result.stdout, max_lines=100)
return json.dumps({"stdout": stdout, "truncated": truncated})
```

### Process Management Anti-Patterns

❌ **Never forget to wait() for process cleanup**
```python
# WRONG - Creates zombie processes
process = await asyncio.create_subprocess_shell(command, ...)
stdout, stderr = await process.communicate()
# Missing: await process.wait()

# RIGHT - Always wait()
process = await asyncio.create_subprocess_shell(command, ...)
try:
    stdout, stderr = await process.communicate()
    await process.wait()  # Reap process
finally:
    if process.returncode is None:
        process.kill()
        await process.wait()
```

❌ **Never use communicate() without timeout**
```python
# WRONG - Hangs forever
stdout, stderr = await process.communicate()

# RIGHT - Enforce timeout
stdout, stderr = await asyncio.wait_for(
    process.communicate(),
    timeout=30
)
```

### Docker Anti-Patterns

❌ **Never omit resource limits**
```yaml
# WRONG - No limits
services:
  vibesbox:
    image: vibesbox

# RIGHT - Resource limits
services:
  vibesbox:
    image: vibesbox
    deploy:
      resources:
        limits:
          cpus: '0.50'
          memory: 512M
    pids_limit: 100
```

❌ **Never use isolated Docker networks**
```yaml
# WRONG - Isolated network
networks:
  vibesbox-network:
    driver: bridge

# RIGHT - External vibes-network
networks:
  vibes-network:
    external: true
```

---

## Success Metrics

**Implementation Quality**:
- Zero security vulnerabilities (bandit, semgrep pass)
- 95%+ test coverage
- <5s container startup
- <400MB image size (Debian) or <200MB (Alpine)

**Performance**:
- Command execution latency <100ms for simple commands
- Streaming output appears in real-time (<500ms delay)
- Timeout enforcement accurate to ±100ms
- No memory leaks (constant memory usage over 1000 commands)

**Security**:
- All command injection attempts blocked
- No privilege escalation possible
- Container escape mitigated (CVE-2024-21626)
- Secrets redacted from output

**Reliability**:
- Health check passes consistently
- No zombie process accumulation
- Graceful shutdown (all processes cleaned up)
- Recovers from errors without restart

---

## PRP Quality Self-Assessment

**Score: 9/10** - High confidence in one-pass implementation success

**Reasoning**:
- ✅ **Comprehensive context**: All 5 research documents synthesized, 1600+ lines of detailed gotchas, patterns, and examples
- ✅ **Clear task breakdown**: 12 sequential tasks with specific steps, validation criteria, and pseudocode
- ✅ **Proven patterns**: 5 production code examples extracted, task-manager MCP server as reference, DesktopCommanderMCP for process management
- ✅ **Validation strategy**: 3-level validation (syntax/unit/integration), executable tests, specific curl commands
- ✅ **Error handling**: 35+ gotchas documented with wrong/right examples, anti-patterns called out explicitly
- ✅ **Security-first**: Command injection prevention, container hardening, secrets redaction, resource limits
- ✅ **Codebase-specific**: Follows vibes patterns (vibes-network, multi-stage Docker, FastMCP, consolidated tools)

**Deduction reasoning (-1 point)**:
- ⚠️ FastMCP HTTP streaming documentation is sparse - implementer may need to experiment with chunked responses
- ⚠️ MCP response size limits not officially specified - following task-manager pattern (100 lines, 1000 chars) but may need tuning
- ⚠️ Alpine vs Debian slim decision not made definitively - research shows Debian slim is 50x faster for builds but Alpine is smaller

**Mitigations**:
1. **Streaming**: Examples show asyncio subprocess streaming patterns, FastAPI StreamingResponse documented, can adapt
2. **Size limits**: Task-manager truncation pattern is proven, can adjust based on testing
3. **Base image**: Start with Debian slim (python:3.11-slim) for development, switch to Alpine only if <200MB requirement strict

**Confidence areas**:
- **10/10**: Security (command injection, container escape, secrets redaction) - comprehensive coverage
- **9/10**: MCP protocol compliance (JSON strings, consolidated tools, error handling) - exact patterns from task-manager
- **9/10**: Process management (zombie prevention, graceful termination, session tracking) - adapted from DesktopCommanderMCP
- **8/10**: Docker configuration (multi-stage builds, resource limits, health checks) - proven patterns, minor Alpine gotchas
- **8/10**: HTTP streaming (chunked encoding, timeout handling) - some edge cases may exist

**Implementation risk**: LOW
- All critical patterns documented with working code
- Validation gates will catch 95% of issues
- Task breakdown enables incremental progress with validation
- Reference implementations available in vibes codebase

**Expected outcome**: Working MCP server in 1 implementation pass, minor tweaks needed for:
- Output truncation thresholds (may need 150 lines instead of 100)
- Timeout defaults (may need 60s instead of 30s for some commands)
- Allowed commands list (will grow based on agent needs)

---

**Generated by**: Phase 4 - PRP Assembler
**Research Quality**: 5/5 comprehensive research documents
**Implementation Readiness**: 9/10 - ready for autonomous implementation
**Estimated Implementation Time**: 6-8 hours for MVP, 12-16 hours for production-ready
