# Feature Analysis: Streamlined Vibesbox MCP Server

## INITIAL.md Summary
Create a lightweight containerized MCP server for secure command execution via HTTP streaming, positioned as an agent jumpbox without VNC/GUI overhead. This is a clean separation from the existing vibesbox implementation, focusing purely on command execution capabilities in a minimal Docker environment.

## Core Requirements

### Explicit Requirements
- **Minimal Docker container** running lightweight Linux (Alpine or similar)
- **HTTP streaming MCP server** at `/mcp` endpoint (not SSE or stdio)
- **Secure command execution** with sandboxing and resource limits
- **Location**: `infra/vibesbox/` directory
- **No VNC/GUI components** - pure command execution focus
- **Clean separation** from existing vibesbox implementation
- **Research-driven design** based on bytebot, DesktopCommanderMCP, and Archon knowledge base

### Implicit Requirements
- **FastAPI/FastMCP framework** for HTTP MCP server (based on existing codebase patterns)
- **Streaming subprocess output** to handle long-running commands
- **Process management** (start, read output, terminate)
- **Session management** for interactive command sessions
- **Structured error handling** with JSON responses
- **Docker Compose integration** with existing vibes network
- **Authentication/authorization** mechanism (TBD based on research)
- **Logging and audit trail** for command execution
- **Resource limiting** via Docker constraints (memory, CPU)
- **Command allowlist/blocklist** for security
- **Working directory management** within container
- **Environment variable handling** for command execution

## Technical Components

### Data Models
```python
# Command Execution Request
class CommandRequest(BaseModel):
    command: str
    shell: str = "/bin/sh"  # Alpine default
    timeout: int = 30  # seconds
    cwd: str | None = None
    env: dict[str, str] | None = None
    stream: bool = True

# Command Result
class CommandResult(BaseModel):
    exit_code: int
    stdout: str
    stderr: str
    duration: float
    command: str

# Session Management
class SessionInfo(BaseModel):
    session_id: str
    command: str
    pid: int
    started_at: datetime
    status: str  # "running", "completed", "terminated"
```

### External Integrations
- **Docker** - Container runtime and resource management
- **FastMCP** - MCP server framework (already in use at task-manager)
- **asyncio subprocess** - For async command execution with streaming
- **Python standard library** - No heavy external dependencies

### Core Logic

#### 1. Command Execution Engine
```python
# Pattern from DesktopCommanderMCP adapted for Python
async def execute_command(
    command: str,
    shell: str,
    timeout: int,
    env: dict
) -> AsyncIterator[str]:
    """Stream command output line by line"""
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        shell=True,
        executable=shell,
        env=env
    )

    # Stream stdout/stderr as they arrive
    async for line in process.stdout:
        yield line.decode()
```

#### 2. MCP Server Tools
Based on existing `/Users/jon/source/vibes/infra/task-manager/backend/src/mcp_server.py` pattern:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Vibesbox Command Executor")

@mcp.tool()
async def execute_command(
    command: str,
    shell: str = "/bin/sh",
    timeout: int = 30,
    cwd: str | None = None
) -> str:
    """Execute shell command with streaming output"""
    # Returns JSON string (Gotcha #3: MCP tools MUST return JSON strings)

@mcp.tool()
async def list_processes() -> str:
    """List running processes in container"""

@mcp.tool()
async def kill_process(pid: int) -> str:
    """Terminate a process by PID"""
```

#### 3. Security Layer
```python
# Blocklist dangerous commands
BLOCKED_COMMANDS = [
    "rm -rf /",
    "dd if=/dev/zero",
    ":(){ :|:& };:",  # Fork bomb
    "chmod -R 777 /",
]

# Resource limits via Docker
CONTAINER_LIMITS = {
    "memory": "512m",
    "cpu_shares": 512,
    "pids_limit": 100,
}
```

### UI/CLI Requirements
- **HTTP endpoint** at `/mcp` for MCP protocol
- **Docker CLI** for container management
- **Health check endpoint** for monitoring
- **No web UI required** - pure API server

## Similar Implementations Found in Archon

### 1. Task Manager MCP Server (Vibes Codebase)
- **Relevance**: 9/10
- **Location**: `/Users/jon/source/vibes/infra/task-manager/backend/src/mcp_server.py`
- **Key Patterns**:
  - FastMCP server setup with `@mcp.tool()` decorators
  - **CRITICAL Gotcha #3**: MCP tools MUST return JSON strings (not dicts)
  - Consolidated tool pattern: single tool for multiple operations (find/create/update/delete)
  - Structured error responses with success/error/suggestion fields
  - Async/await throughout
- **Gotchas**:
  - Always return JSON strings from tools
  - Truncate large responses to avoid payload bloat
  - Use `json.dumps()` explicitly in all tool returns
- **Reuse**: Server structure, tool patterns, error handling

### 2. DesktopCommanderMCP (Reference Repo)
- **Relevance**: 8/10
- **Location**: `/Users/jon/source/vibes/repos/DesktopCommanderMCP/`
- **Key Patterns**:
  - Process management tools (start_process, interact_with_process, read_process_output)
  - Command blocking/allowlisting for security
  - Session management for long-running commands
  - Configuration management (get_config, set_config_value)
  - Comprehensive audit logging
  - Docker support with persistent volumes
- **Gotchas**:
  - `allowedDirectories` only restricts filesystem ops, NOT terminal commands
  - Docker provides real isolation vs. configuration-based sandboxing
  - Fuzzy search fallback when exact matches fail
- **Reuse**: Process execution patterns, security model, session management

### 3. Bytebot (Reference Repo)
- **Relevance**: 6/10
- **Location**: `/Users/jon/source/vibes/repos/bytebot/`
- **Key Patterns**:
  - Full desktop environment in container (Ubuntu + XFCE)
  - REST API for task creation
  - File upload handling for tasks
  - Persistent environment across restarts
  - Password manager integration
- **Gotchas**:
  - VNC/GUI adds significant overhead (200+ MB)
  - Complex multi-component architecture
  - Requires database for task storage
- **Reuse**: Docker containerization approach, REST API patterns
- **Avoid**: VNC/GUI components, complex UI layer

## Recommended Technology Stack

### Core Framework
- **Language**: Python 3.11+ (matches existing vibes infrastructure)
- **MCP Server**: FastMCP (already used in task-manager)
- **Web Framework**: FastAPI (FastMCP is built on it)
- **Async Runtime**: asyncio (standard library)

### Container
- **Base Image**: `python:3.11-alpine` (minimal, secure, ~50MB)
- **Shell**: `/bin/sh` (Alpine default, lightweight)
- **Process Manager**: None needed (single MCP server process)

### Dependencies
```python
# Minimal dependency set
fastmcp>=1.0.0  # MCP server framework
pydantic>=2.0.0  # Data validation (included with FastMCP)
uvicorn>=0.30.0  # ASGI server (included with FastMCP)
```

### Testing
- **pytest** - Unit and integration tests
- **pytest-asyncio** - Async test support
- **httpx** - HTTP client for testing MCP endpoints
- **docker-py** - Docker integration tests

### Security
- **Docker resource limits** - CPU, memory, PID constraints
- **Command validation** - Blocklist/allowlist patterns
- **No network access** by default - unless explicitly needed
- **Read-only filesystem** where possible
- **Non-root user** execution

## Assumptions Made

### 1. **HTTP Transport Pattern**: Use FastMCP with HTTP streaming (not SSE)
   - **Reasoning**: INITIAL.md explicitly requires "HTTP streaming MCP server (not SSE/stdio)"
   - **Source**: FastMCP supports HTTP transport via FastAPI
   - **Confidence**: High - direct requirement match

### 2. **Authentication**: Start with no auth, add later if needed
   - **Reasoning**: Not mentioned in INITIAL.md, can add token-based auth in v2
   - **Source**: DesktopCommanderMCP also starts without auth in basic mode
   - **Confidence**: Medium - should validate with user in Phase 2

### 3. **File Operations**: NOT included in initial scope
   - **Reasoning**: INITIAL.md says "command execution" focus, "Out of Scope" lists GUI interactions
   - **Source**: DesktopCommanderMCP has filesystem tools, but we're going minimal
   - **Confidence**: High - aligns with "streamlined" goal
   - **Future**: Can add read/write file tools in Phase 2 if needed

### 4. **Resource Limits**: 512MB RAM, 0.5 CPU, 100 processes
   - **Reasoning**: Enough for command execution, prevents resource abuse
   - **Source**: Standard container limits for development tools
   - **Confidence**: Medium - should tune based on actual usage

### 5. **Timeout Defaults**: 30 seconds for commands, configurable
   - **Reasoning**: Prevents hanging processes, long-running can stream
   - **Source**: DesktopCommanderMCP uses similar timeout patterns
   - **Confidence**: High - industry standard

### 6. **Logging**: JSON structured logs to stdout/stderr
   - **Reasoning**: Container-native logging, easy Docker Compose integration
   - **Source**: 12-factor app methodology
   - **Confidence**: High - matches vibes infrastructure

### 7. **Network**: Isolated by default, connect to vibes network if needed
   - **Reasoning**: Security first, explicit network connectivity
   - **Source**: Docker best practices
   - **Confidence**: High - can relax if agent needs external access

### 8. **Storage**: Ephemeral by default, optional volume mounts
   - **Reasoning**: Stateless command execution, persist only if needed
   - **Source**: Bytebot uses persistent volumes for workspace
   - **Confidence**: Medium - may need workspace volume for multi-command workflows

### 9. **Tool Design**: 3-5 consolidated tools (execute, list_processes, kill_process)
   - **Reasoning**: Follows task-manager pattern of consolidated tools
   - **Source**: Task manager uses find_tasks/manage_task pattern
   - **Confidence**: High - proven pattern in this codebase

### 10. **Shell**: Alpine's `/bin/sh` by default, configurable per command
   - **Reasoning**: Lightweight, sufficient for most commands
   - **Source**: DesktopCommanderMCP allows shell configuration
   - **Confidence**: High - can override with bash if specific commands need it

## Success Criteria

Based on INITIAL.md checklist and inferred quality standards:

1. ✅ **Clean Docker container** in `infra/vibesbox/`
   - Dockerfile builds successfully
   - Image size < 100MB
   - Starts in < 3 seconds
   - Alpine-based, no unnecessary packages

2. ✅ **HTTP MCP server** responding at `/mcp`
   - FastMCP server runs successfully
   - Responds to MCP protocol requests
   - Health check endpoint returns 200
   - Logs startup without errors

3. ✅ **Secure command execution** tool(s)
   - `execute_command` tool works for basic commands
   - Blocked commands are rejected
   - Resource limits enforced by Docker
   - Command output streams correctly

4. ✅ **Proper streaming** output handling
   - Long-running commands stream line-by-line
   - No buffering issues
   - Client receives output in real-time
   - Timeout handling works correctly

5. ✅ **No conflicts** with existing vibesbox
   - Different directory (`infra/vibesbox/` not `mcp-servers/vibesbox/`)
   - Different container name
   - Different port (if any)
   - No shared resources

6. ✅ **Integration tests** pass
   - Execute simple command (echo, ls)
   - Execute long-running command with streaming
   - Kill running process
   - List processes
   - Timeout enforcement
   - Blocked command rejection

7. ✅ **Documentation** complete
   - README with setup instructions
   - API documentation for MCP tools
   - Security considerations
   - Example usage

## Gotchas and Challenges

### Known Gotchas (From Research)

1. **MCP Response Format** (from task-manager)
   - ❌ **WRONG**: Return Python dict from tool
   - ✅ **CORRECT**: Return `json.dumps(dict)` string
   - **Impact**: Tools break if returning dicts directly
   - **Source**: `/Users/jon/source/vibes/infra/task-manager/backend/src/mcp_server.py` line 12

2. **Subprocess Streaming** (from DesktopCommanderMCP)
   - ❌ **WRONG**: Wait for process.communicate() to complete
   - ✅ **CORRECT**: Read stdout/stderr incrementally with async iterators
   - **Impact**: Long commands appear frozen
   - **Source**: Node.js streams in DesktopCommanderMCP

3. **Command Security** (from DesktopCommanderMCP)
   - ❌ **WRONG**: Trust `allowedDirectories` for full sandboxing
   - ✅ **CORRECT**: Use Docker isolation + command validation
   - **Impact**: Directory restrictions can be bypassed via shell
   - **Source**: DesktopCommanderMCP README security warnings

4. **Alpine Shell Compatibility** (general knowledge)
   - ❌ **WRONG**: Assume bash is available
   - ✅ **CORRECT**: Use `/bin/sh` or install bash explicitly
   - **Impact**: Bashisms fail in Alpine
   - **Source**: Alpine Linux uses busybox sh by default

5. **Process Cleanup** (subprocess best practices)
   - ❌ **WRONG**: Leave orphaned processes
   - ✅ **CORRECT**: Track PIDs and cleanup on container stop
   - **Impact**: Resource leaks, container restart issues
   - **Source**: Python asyncio subprocess docs

### Anticipated Challenges

1. **WebSocket vs HTTP Streaming**
   - Challenge: MCP over HTTP requires proper streaming setup
   - Mitigation: FastMCP handles this, verify with examples
   - Risk: Medium

2. **Container Restart Persistence**
   - Challenge: Session state lost on restart
   - Mitigation: Accept ephemeral sessions or add optional persistence
   - Risk: Low (acceptable for MVP)

3. **Error Propagation**
   - Challenge: Capturing both stdout and stderr while streaming
   - Mitigation: Use asyncio.gather for parallel reading
   - Risk: Low

4. **Timeout Handling**
   - Challenge: Graceful vs forceful process termination
   - Mitigation: SIGTERM → wait → SIGKILL pattern
   - Risk: Medium

## Next Steps for Downstream Agents

### Codebase Researcher
**Focus Areas**:
1. **Existing MCP patterns** in `/Users/jon/source/vibes/infra/task-manager/backend/src/mcp_server.py`
   - How FastMCP is configured and run
   - JSON response patterns
   - Error handling structure

2. **Docker Compose patterns** in existing infra/
   - Network configuration
   - Volume mounting patterns
   - Environment variable handling

3. **Python subprocess patterns** for async execution
   - Streaming output examples
   - Error handling
   - Process management

4. **Security patterns** in existing containers
   - Non-root user setup
   - Resource limits
   - Network isolation

**Output**: Concrete code snippets showing existing patterns to reuse

### Documentation Hunter
**Find Documentation For**:
1. **FastMCP HTTP transport**
   - How to configure HTTP streaming (not SSE)
   - Tool registration patterns
   - Client connection examples

2. **Python asyncio subprocess**
   - create_subprocess_shell documentation
   - Streaming stdout/stderr
   - Process lifecycle management
   - Timeout handling

3. **Docker Alpine Python**
   - Best practices for python:alpine images
   - Package installation (apk vs pip)
   - Shell differences from Ubuntu

4. **MCP Protocol Spec**
   - HTTP transport requirements
   - Tool response formats
   - Error handling standards

**Output**: Links to official docs, gotchas from docs, key API references

### Example Curator
**Extract Examples Showing**:
1. **FastMCP HTTP server setup**
   - Minimal working example
   - Tool registration
   - Running the server

2. **Streaming subprocess output**
   - Python asyncio examples
   - Line-by-line reading
   - Error stream handling

3. **Docker multi-stage builds** for minimal Python images
   - Alpine base examples
   - Dependency installation
   - Non-root user setup

4. **Command execution security**
   - Input validation examples
   - Blocklist/allowlist patterns
   - Safe subprocess invocation

**Output**: Working code examples with explanations

### Gotcha Detective
**Investigate Problem Areas**:
1. **FastMCP HTTP streaming gotchas**
   - Does it support chunked responses?
   - How to stream command output?
   - Known issues with long-running tools?

2. **Alpine package compatibility**
   - Any Python packages that fail on Alpine?
   - Shell script compatibility issues?
   - Missing common utilities?

3. **Subprocess zombie processes**
   - Cleanup patterns
   - Signal handling
   - Container stop behavior

4. **MCP tool response size limits**
   - Is there a max response size?
   - How to handle large command output?
   - Should we paginate results?

**Output**: List of gotchas with mitigation strategies

## Research Questions for Phase 2

1. **Authentication**: Should we add API key auth? OAuth? Or trust network isolation?
2. **File Operations**: Do agents need read/write file tools? Or just command execution?
3. **Persistent Storage**: Should we mount a workspace volume? Or keep ephemeral?
4. **Network Access**: Does container need internet access? Or fully isolated?
5. **Shell Choice**: Stick with `/bin/sh` or install bash for compatibility?
6. **Session State**: Should sessions persist across container restarts?
7. **Monitoring**: What metrics should we expose? Prometheus endpoint?
8. **Rate Limiting**: Should we limit command execution frequency?

## Architecture Diagram

```
┌─────────────────────────────────────────────────┐
│  Claude / AI Agent (Client)                     │
└────────────────┬────────────────────────────────┘
                 │ HTTP MCP Protocol
                 │ POST /mcp
┌────────────────▼────────────────────────────────┐
│  FastMCP HTTP Server                            │
│  ┌──────────────────────────────────────────┐   │
│  │  MCP Tools:                              │   │
│  │  - execute_command(cmd, shell, timeout)  │   │
│  │  - list_processes()                      │   │
│  │  - kill_process(pid)                     │   │
│  └──────────────────────────────────────────┘   │
│                                                  │
│  ┌──────────────────────────────────────────┐   │
│  │  Security Layer:                         │   │
│  │  - Command validation (blocklist)        │   │
│  │  - Input sanitization                    │   │
│  │  - Resource limit checks                 │   │
│  └──────────────────────────────────────────┘   │
│                                                  │
│  ┌──────────────────────────────────────────┐   │
│  │  Execution Engine:                       │   │
│  │  - asyncio.create_subprocess_shell       │   │
│  │  - Streaming stdout/stderr               │   │
│  │  - Process tracking                      │   │
│  │  - Timeout enforcement                   │   │
│  └──────────────────────────────────────────┘   │
│                                                  │
│  Alpine Linux Container                         │
│  - 512MB RAM limit                              │
│  - 0.5 CPU shares                               │
│  - 100 process limit                            │
│  - Isolated network (optional)                  │
└─────────────────────────────────────────────────┘
```

## Implementation Phases

### Phase 1: Core Infrastructure (MVP)
- Dockerfile with Alpine Python
- FastMCP server setup
- `execute_command` tool with basic execution
- Docker Compose integration
- Basic integration tests

### Phase 2: Process Management
- `list_processes` tool
- `kill_process` tool
- Session tracking
- Timeout enforcement

### Phase 3: Security Hardening
- Command blocklist
- Resource limits enforcement
- Non-root user
- Audit logging

### Phase 4: Production Readiness
- Health checks
- Monitoring/metrics
- Comprehensive error handling
- Documentation
- Performance tuning

## Estimated Complexity

**Overall Complexity**: Medium

**Component Breakdown**:
- Docker setup: Easy (existing patterns in codebase)
- FastMCP server: Easy (copy from task-manager)
- Command execution: Medium (streaming requires care)
- Security layer: Medium (validation logic)
- Testing: Medium (async tests, Docker integration)

**Time Estimate**: 6-8 hours for MVP, 12-16 hours for production-ready

**Risk Areas**:
- HTTP streaming configuration (Medium risk)
- Subprocess cleanup on errors (Medium risk)
- Security validation completeness (Low risk - Docker isolation helps)
- Alpine compatibility issues (Low risk - minimal dependencies)
