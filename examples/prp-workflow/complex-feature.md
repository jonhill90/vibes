name: "Example: Complex Feature PRP - MCP Server with Shell and GUI Capabilities"
description: |

## Purpose
This is a complete example of a complex, multi-component feature PRP. Use this as a reference when creating PRPs for features that involve multiple systems, integrations, and require careful coordination.

---

## Goal
Build an MCP server (`mcp-vibesbox-server`) that provides both shell command execution and VNC-based GUI automation capabilities in a single Docker container with systemd support.

## Why
- **Business Value**: Enables Claude Desktop to execute shell commands AND automate GUI applications
- **Integration**: Consolidates two separate servers (vibes-server and vibesbox-server) into one
- **Problems Solved**: Current setup requires managing two containers; unified server simplifies deployment and reduces resource usage

## What
A Python-based MCP server running in Docker that provides:
- Shell command execution tool (`run_command`)
- VNC server for GUI automation (display :1, port 5901)
- Screenshot capture with ImageMagick
- GUI interaction tools (click, type, drag)
- Persistent workspace at `/workspace/vibes`

### Success Criteria
- [ ] MCP server starts successfully in Docker container
- [ ] `run_command` tool executes shell commands correctly
- [ ] VNC server accessible on port 5901
- [ ] GUI automation tools work (click, type, screenshot)
- [ ] Screenshots save to `/workspace/vibes/screenshots/`
- [ ] Claude Desktop can use all tools via MCP protocol
- [ ] Container survives restarts (systemd manages VNC)
- [ ] All unit tests pass
- [ ] Integration test with Claude Desktop succeeds

## Context

### Documentation & References
```yaml
# MUST READ - Critical external documentation
- url: https://spec.modelcontextprotocol.io/specification/server/
  why: MCP server protocol specification

- url: https://modelcontextprotocol.io/quickstart/server
  why: MCP server implementation patterns

- url: https://github.com/TigerVNC/tigervnc/wiki
  why: VNC server configuration and usage

- url: https://imagemagick.org/script/import.php
  why: Screenshot capture with ImageMagick

# MUST READ - Existing codebase patterns
- file: mcp/mcp-vibes-server/server.py
  why: Pattern for shell command execution tool

- file: mcp/mcp-vibesbox-server/Dockerfile
  why: Docker container setup with systemd

- file: mcp/mcp-vibesbox-server/docker-compose.yml
  why: Service configuration and volume mounts
```

### Current Structure
```bash
mcp/
├── mcp-vibes-server/          # Shell-only server
│   ├── server.py
│   ├── Dockerfile
│   └── docker-compose.yml
└── mcp-vibesbox-server/       # GUI server (to be replaced)
    ├── server.py
    ├── Dockerfile
    └── docker-compose.yml
```

### Desired Structure
```bash
mcp/
├── mcp-vibes-server/          # Unchanged (legacy)
└── mcp-vibesbox-server/       # UNIFIED SERVER
    ├── server.py              # MODIFIED: Add all tools
    ├── tools/                 # NEW: Organized tool modules
    │   ├── __init__.py
    │   ├── shell.py          # Shell execution tool
    │   └── gui.py            # GUI automation tools
    ├── Dockerfile             # MODIFIED: Add VNC, ImageMagick
    ├── docker-compose.yml     # MODIFIED: Expose VNC port
    ├── vnc_startup.sh        # NEW: VNC server startup script
    ├── requirements.txt       # MODIFIED: Add dependencies
    └── tests/
        ├── test_shell.py     # NEW: Shell tool tests
        └── test_gui.py       # NEW: GUI tool tests
```

### Known Gotchas
```python
# CRITICAL: Docker container needs privileged mode for systemd
# See docker-compose.yml: privileged: true

# CRITICAL: VNC display must be :1, not :0
# Display :0 conflicts with host system

# CRITICAL: Screenshots must use ImageMagick import, not scrot
# scrot doesn't work in VNC environments

# PATTERN: MCP tools return TextContent or ImageContent
# See mcp.server.types for response types

# GOTCHA: systemd requires /sys/fs/cgroup mounted in container
# See docker-compose.yml volumes section

# PATTERN: All file paths in workspace use /workspace prefix
# Container workspace is mounted from host
```

## Implementation

### Task List
```yaml
Task 1: Update Dockerfile with VNC and dependencies
ACTION: Add VNC server, ImageMagick, systemd support
FILES: mcp/mcp-vibesbox-server/Dockerfile
PATTERN: Follow existing vibesbox-server Dockerfile structure
PACKAGES:
  - tigervnc-standalone-server
  - tigervnc-common
  - imagemagick
  - systemd
  - dbus

Task 2: Create VNC startup script
ACTION: Build systemd service for VNC server
FILES: mcp/mcp-vibesbox-server/vnc_startup.sh
PATTERN: Standard VNC startup with password and display config

Task 3: Create shell execution tool module
ACTION: Extract shell command logic into tools/shell.py
FILES: mcp/mcp-vibesbox-server/tools/shell.py
PATTERN: Mirror mcp-vibes-server/server.py run_command tool

Task 4: Create GUI automation tool module
ACTION: Build GUI tools (screenshot, click, type, drag)
FILES: mcp/mcp-vibesbox-server/tools/gui.py
DEPENDENCIES: python-xlib, pynput for GUI interaction

Task 5: Update main server.py
ACTION: Register all tools using MCP protocol
FILES: mcp/mcp-vibesbox-server/server.py
PATTERN: Use @server.list_tools() and @server.call_tool()

Task 6: Update docker-compose.yml
ACTION: Configure container with VNC port and volumes
FILES: mcp/mcp-vibesbox-server/docker-compose.yml
PORTS: 5901 (VNC)
VOLUMES: ./screenshots, /workspace

Task 7: Create screenshot directory
ACTION: Ensure screenshots directory exists
FILES: mcp/mcp-vibesbox-server/screenshots/
PATTERN: .gitkeep file to preserve directory

Task 8: Write comprehensive tests
ACTION: Unit tests for shell and GUI tools
FILES: mcp/mcp-vibesbox-server/tests/
PATTERN: pytest with mocked subprocess and X11 calls

Task 9: Update requirements.txt
ACTION: Add all Python dependencies
FILES: mcp/mcp-vibesbox-server/requirements.txt
PACKAGES: mcp, python-xlib, pynput, Pillow

Task 10: Integration test with Claude Desktop
ACTION: Test all tools via Claude Desktop MCP connection
TEST: Execute command, take screenshot, click, type
```

### Detailed Pseudocode for Key Components

```python
# tools/shell.py - Shell command execution

import subprocess
import asyncio
from typing import Dict, Any
from mcp.server.types import TextContent

async def run_command(
    command: str,
    working_dir: str = "/workspace",
    timeout: int = 120
) -> Dict[str, Any]:
    """
    Execute shell command in container.

    Args:
        command: Shell command to execute
        working_dir: Working directory
        timeout: Command timeout in seconds

    Returns:
        Dict with stdout, stderr, exit_code
    """
    try:
        # PATTERN: Use asyncio.create_subprocess_shell for async
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=working_dir
        )

        # CRITICAL: Implement timeout to prevent hanging
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            process.kill()
            return {
                "error": f"Command timed out after {timeout}s",
                "exit_code": -1
            }

        return {
            "stdout": stdout.decode("utf-8"),
            "stderr": stderr.decode("utf-8"),
            "exit_code": process.returncode
        }

    except Exception as e:
        return {"error": str(e), "exit_code": -1}

# tools/gui.py - GUI automation

import subprocess
from datetime import datetime
from pathlib import Path

async def take_screenshot(
    display: str = ":1",
    output_dir: str = "/workspace/vibes/screenshots"
) -> str:
    """
    Capture screenshot using ImageMagick.

    Args:
        display: VNC display number
        output_dir: Directory to save screenshot

    Returns:
        Path to screenshot file
    """
    # CRITICAL: Use ImageMagick import, not scrot
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_vibesbox_1920x1080.png"
    filepath = Path(output_dir) / filename

    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # PATTERN: Set DISPLAY environment variable
    env = {"DISPLAY": display}

    # Capture screenshot
    process = await asyncio.create_subprocess_exec(
        "import",
        "-window", "root",
        str(filepath),
        env=env
    )

    await process.communicate()

    if process.returncode == 0:
        return str(filepath)
    else:
        raise RuntimeError(f"Screenshot capture failed")

async def click_desktop(
    x: int,
    y: int,
    button: int = 1,
    double_click: bool = False,
    display: str = ":1"
) -> bool:
    """
    Click at coordinates on desktop.

    Args:
        x: X coordinate
        y: Y coordinate
        button: Mouse button (1=left, 2=middle, 3=right)
        double_click: Whether to double-click
        display: VNC display

    Returns:
        True if successful
    """
    # PATTERN: Use xdotool for mouse automation
    env = {"DISPLAY": display}

    # Move mouse to coordinates
    await asyncio.create_subprocess_exec(
        "xdotool", "mousemove", str(x), str(y),
        env=env
    )

    # Click
    click_count = 2 if double_click else 1
    process = await asyncio.create_subprocess_exec(
        "xdotool", "click", "--repeat", str(click_count), str(button),
        env=env
    )

    await process.communicate()
    return process.returncode == 0

# server.py - Main MCP server

from mcp.server import Server
from mcp.server.stdio import stdio_server
from tools.shell import run_command
from tools.gui import take_screenshot, click_desktop

server = Server("mcp-vibesbox-server")

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools"""
    return [
        Tool(
            name="run_command",
            description="Execute shell command in container",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {"type": "string"},
                    "working_dir": {"type": "string"},
                    "timeout": {"type": "integer"}
                },
                "required": ["command"]
            }
        ),
        Tool(
            name="take_screenshot",
            description="Capture screenshot of VNC desktop",
            inputSchema={
                "type": "object",
                "properties": {
                    "display": {"type": "string"}
                }
            }
        ),
        Tool(
            name="click_desktop",
            description="Click at coordinates on desktop",
            inputSchema={
                "type": "object",
                "properties": {
                    "x": {"type": "integer"},
                    "y": {"type": "integer"},
                    "button": {"type": "integer"}
                },
                "required": ["x", "y"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute tool based on name"""
    if name == "run_command":
        result = await run_command(**arguments)
        return [TextContent(type="text", text=str(result))]

    elif name == "take_screenshot":
        path = await take_screenshot(**arguments)
        return [TextContent(type="text", text=f"Screenshot saved: {path}")]

    elif name == "click_desktop":
        success = await click_desktop(**arguments)
        return [TextContent(type="text", text=f"Click: {success}")]

    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)
```

### Integration Points
```yaml
DOCKER:
  - Network: vibes-network (external)
  - Ports: 5901 (VNC), optional 6080 (noVNC)
  - Volumes:
      - /workspace (persistent workspace)
      - ./screenshots (screenshot storage)
  - Privileged: true (for systemd)

CONFIGURATION:
  - VNC Password: Set in vnc_startup.sh
  - Display: :1
  - Resolution: 1920x1080
  - Screenshot format: PNG

DEPENDENCIES:
  - Python: mcp, python-xlib, pynput, Pillow
  - System: tigervnc, imagemagick, xdotool, systemd

CLAUDE_DESKTOP:
  - Config: claude_desktop_config.json
  - Command: docker exec -i mcp-vibesbox-server python /workspace/server.py
```

## Validation

### Level 1: Container Build
```bash
# Build Docker container
cd mcp/mcp-vibesbox-server
docker-compose build

# Expected: Build succeeds without errors
```

### Level 2: Container Startup
```bash
# Start container
docker-compose up -d

# Verify container running
docker ps | grep mcp-vibesbox-server

# Check VNC server running
docker exec mcp-vibesbox-server ps aux | grep vnc

# Expected: Container running, VNC server active
```

### Level 3: Unit Tests
```bash
# Run unit tests in container
docker exec mcp-vibesbox-server pytest tests/ -v

# Expected: All tests pass
```

### Level 4: Tool Integration Tests
```bash
# Test shell command
echo '{"command": "ls /workspace"}' | docker exec -i mcp-vibesbox-server python server.py

# Test screenshot
echo '{"display": ":1"}' | docker exec -i mcp-vibesbox-server python server.py

# Verify screenshot created
ls screenshots/

# Expected: Commands execute, screenshot file created
```

### Level 5: VNC Connection Test
```bash
# Connect to VNC server
# Use VNC client (TigerVNC, RealVNC, etc.)
# Connect to: localhost:5901
# Password: (from vnc_startup.sh)

# Expected: Desktop visible in VNC client
```

### Level 6: Claude Desktop Integration
```bash
# Update Claude Desktop config
# Add mcp-vibesbox-server to mcpServers

# Restart Claude Desktop

# In Claude: Ask to run a shell command
# In Claude: Ask to take a screenshot

# Expected: All tools accessible and functional
```

## Final Checklist
- [ ] Docker container builds successfully
- [ ] Container starts without errors
- [ ] VNC server accessible on port 5901
- [ ] All tools registered in MCP server
- [ ] Shell commands execute correctly
- [ ] Screenshots capture and save
- [ ] GUI automation tools work
- [ ] All unit tests pass (20+ tests)
- [ ] Integration tests pass
- [ ] Claude Desktop can use all tools
- [ ] Screenshots save to correct directory
- [ ] Container survives restarts
- [ ] No resource leaks or hanging processes

---

## Anti-Patterns to Avoid
- ❌ Don't use display :0 - conflicts with host
- ❌ Don't skip systemd setup - VNC won't persist
- ❌ Don't use scrot for screenshots - use ImageMagick
- ❌ Don't forget privileged mode in docker-compose
- ❌ Don't hardcode paths - use configuration
- ❌ Don't skip timeout handling in commands
- ❌ Don't commit VNC password to repo
- ❌ Don't test only happy path - test errors too

## Progressive Implementation Strategy

This complex feature uses **progressive success**:

1. **Phase 1**: Basic container with shell execution only
2. **Phase 2**: Add VNC server (verify VNC connection works)
3. **Phase 3**: Add screenshot capability
4. **Phase 4**: Add GUI automation (click, type, drag)
5. **Phase 5**: Optimize and polish

**Validation at each phase before proceeding!**

## Notes

This example demonstrates:
- Breaking down complex features into manageable tasks
- Multiple integration points (Docker, VNC, MCP)
- Progressive validation strategy
- Comprehensive testing approach
- Security considerations (privileged containers)
- Resource management (screenshots, processes)

**Key Takeaway**: Complex features require detailed planning, progressive implementation, and validation at multiple levels. The PRP ensures nothing is forgotten.
