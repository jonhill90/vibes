"""MCP Server for Vibesbox Command Executor.

This module provides FastMCP tools for secure command execution in a containerized environment.

KEY PATTERNS IMPLEMENTED:
1. FastMCP server with tool decorators (@mcp.tool)
2. CRITICAL: Tools return JSON strings (not dicts) - Gotcha #1
3. Consolidated tool pattern: execute_command, manage_process
4. Structured error handling with suggestion messages
5. Output truncation to prevent context exhaustion - Gotcha #5

CRITICAL GOTCHAS ADDRESSED:
- Gotcha #1: MCP tools MUST return json.dumps() strings, NEVER dicts
- Gotcha #5: Output must be truncated to 100 lines max
- All errors return structured JSON with success=false

Pattern Sources:
- prps/streamlined_vibesbox/examples/fastmcp_server_pattern.py
- infra/task-manager/backend/src/mcp_server.py
- PRP Task 6 specification
"""

import json
import logging

from mcp.server.fastmcp import FastMCP

from src.command_executor import execute_command as run_command
from src.session_manager import SessionManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server with HTTP configuration
# PATTERN FROM: archon/python/src/mcp_server/mcp_server.py
mcp = FastMCP(
    "Vibesbox Command Executor",
    host="0.0.0.0",
    port=8000
)

# Initialize session manager for process tracking
# PATTERN FROM: session_manager.py
session_manager = SessionManager(max_completed_sessions=100)


@mcp.tool()
async def execute_command(
    command: str,
    shell: str = "/bin/sh",
    timeout: int = 30,
    stream: bool = True
) -> str:
    """Execute shell command with optional streaming.

    CRITICAL: MUST return JSON string (not dict) - Gotcha #1
    Pattern from: task-manager/mcp_server.py

    This tool executes shell commands in a secure containerized environment
    with validation, timeout enforcement, and output truncation.

    Args:
        command: Shell command to execute (required)
        shell: Shell interpreter to use (default: /bin/sh)
        timeout: Maximum execution time in seconds (1-300, default: 30)
        stream: Whether to stream output line-by-line (default: True)

    Returns:
        JSON string with result (NEVER returns dict - Gotcha #1)
        {
            "success": bool,
            "exit_code": int | null,
            "stdout": str,
            "stderr": str,
            "truncated": bool,
            "error": str | null
        }

    Examples:
        execute_command("echo 'hello world'")
        execute_command("ls -la /tmp", timeout=10)
        execute_command("sleep 100", timeout=1)  # Will timeout
        execute_command("rm -rf /")  # Will be blocked by security
    """
    try:
        logger.info(f"Executing command: {command[:50]}...")

        # Execute command (validates internally with security checks)
        # PATTERN FROM: command_executor.py execute_command()
        result = await run_command(
            command=command,
            shell=shell,
            timeout=timeout,
            stream=stream
        )

        # Convert Pydantic model to JSON string
        # CRITICAL GOTCHA #1: NEVER return result.model_dump() (dict)
        # MUST return JSON string for MCP protocol
        json_result = result.model_dump_json()

        logger.info(
            f"Command completed: success={result.success}, "
            f"exit_code={result.exit_code}, truncated={result.truncated}"
        )

        return json_result

    except Exception as e:
        # Structured error response
        # PATTERN FROM: task-manager error handling
        logger.error(f"Error in execute_command: {e}", exc_info=True)

        return json.dumps({
            "success": False,
            "error": str(e),
            "exit_code": -1,
            "stdout": "",
            "stderr": str(e),
            "truncated": False,
            "suggestion": "Check command syntax and permissions. Review error message for details."
        })


@mcp.tool()
async def manage_process(
    action: str,
    pid: int | None = None,
    signal: str = "SIGTERM"
) -> str:
    """Manage running processes (consolidated tool).

    CRITICAL: MUST return JSON string (not dict) - Gotcha #1
    Pattern from: task-manager consolidated tools

    This tool provides process management capabilities:
    - List all active and recently completed sessions
    - Kill (terminate) a specific process by PID
    - Read incremental output from a running process

    Args:
        action: "list" | "kill" | "read" (required)
        pid: Process ID for "kill" and "read" actions (optional for "list")
        signal: Signal to send for "kill" action: "SIGTERM" (graceful) | "SIGKILL" (force)
               Default: "SIGTERM"

    Returns:
        JSON string with result (NEVER returns dict - Gotcha #1)

        For "list" action:
        {
            "success": bool,
            "processes": [
                {
                    "pid": int,
                    "command": str,
                    "started_at": str,
                    "status": "running" | "completed"
                }
            ],
            "count": int
        }

        For "kill" action:
        {
            "success": bool,
            "message": str,
            "pid": int
        }

        For "read" action:
        {
            "success": bool,
            "pid": int,
            "output": str,
            "has_new_output": bool
        }

    Examples:
        manage_process("list")  # List all processes
        manage_process("kill", pid=1234)  # Graceful termination (SIGTERM)
        manage_process("kill", pid=1234, signal="SIGKILL")  # Force kill
        manage_process("read", pid=1234)  # Read new output
    """
    try:
        logger.info(f"Process action: {action}, pid={pid}, signal={signal}")

        if action == "list":
            # List all sessions (active and completed)
            # PATTERN FROM: session_manager.py list_sessions()
            sessions = session_manager.list_sessions()

            # Convert SessionInfo Pydantic models to dicts
            # Then wrap in JSON string (Gotcha #1)
            processes_list = [
                {
                    "pid": s.pid,
                    "command": s.command,
                    "started_at": s.started_at.isoformat(),
                    "status": s.status
                }
                for s in sessions
            ]

            return json.dumps({
                "success": True,
                "processes": processes_list,
                "count": len(processes_list)
            })

        elif action == "kill" and pid:
            # Terminate specific process
            # PATTERN FROM: process_cleanup_pattern.py
            # Gotcha: Graceful termination (SIGTERM -> SIGKILL)
            force = (signal == "SIGKILL")

            success = await session_manager.terminate_session(pid, force=force)

            if not success:
                return json.dumps({
                    "success": False,
                    "error": f"Process {pid} not found in active sessions",
                    "suggestion": "Use manage_process('list') to see active processes"
                })

            return json.dumps({
                "success": True,
                "message": f"Process {pid} terminated with signal {signal}",
                "pid": pid
            })

        elif action == "read" and pid:
            # Read incremental output from process
            # PATTERN FROM: session_manager.py read_output()
            try:
                output = await session_manager.read_output(pid)

                return json.dumps({
                    "success": True,
                    "pid": pid,
                    "output": output,
                    "has_new_output": len(output) > 0
                })

            except ValueError as e:
                # Session not found
                return json.dumps({
                    "success": False,
                    "error": str(e),
                    "pid": pid,
                    "suggestion": "Verify PID exists using manage_process('list')"
                })

        else:
            # Invalid action or missing PID
            return json.dumps({
                "success": False,
                "error": f"Invalid action '{action}' or missing PID for '{action}' action",
                "suggestion": "Valid actions: 'list' (no PID), 'kill' (requires PID), 'read' (requires PID)"
            })

    except Exception as e:
        # Unexpected error
        logger.error(f"Error in manage_process ({action}): {e}", exc_info=True)

        return json.dumps({
            "success": False,
            "error": str(e),
            "action": action,
            "pid": pid,
            "suggestion": "Check error message and try again"
        })


# Health check tool for Docker
# PATTERN FROM: MCP tool pattern (since FastMCP doesn't expose app directly)
@mcp.tool()
async def health() -> str:
    """Health check for Docker container monitoring.

    Returns:
        JSON string with health status
    """
    return json.dumps({
        "status": "healthy",
        "service": "vibesbox",
        "version": "1.0.0"
    })


# Main entry point
if __name__ == "__main__":
    # PATTERN FROM: archon/python/src/mcp_server/mcp_server.py
    # Run the MCP server with streamable-http transport
    logger.info("Starting Vibesbox MCP server...")
    logger.info(f"   Mode: Streamable HTTP")
    logger.info(f"   URL: http://0.0.0.0:8000/mcp")

    try:
        mcp.run(transport="streamable-http")
    except KeyboardInterrupt:
        logger.info("Vibesbox MCP server stopped by user")
    except Exception as e:
        logger.error(f"Fatal error in MCP server: {e}", exc_info=True)
        raise
    finally:
        # Cleanup on shutdown
        import asyncio
        asyncio.run(session_manager.cleanup_all())
        logger.info("Vibesbox MCP server shutdown complete")
