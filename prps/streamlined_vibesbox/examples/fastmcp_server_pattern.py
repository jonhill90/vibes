# Source: /Users/jon/source/vibes/infra/task-manager/backend/src/mcp_server.py
# Lines: 1-82, 200-240
# Pattern: FastMCP server initialization with tool decorators and JSON return pattern
# Extracted: 2025-10-13
# Relevance: 10/10 - Perfect match for MCP server setup in this codebase

"""FastMCP Server Pattern - Streamlined Example

This demonstrates the EXACT pattern used in task-manager for creating
an MCP server with tools. Key aspects:
1. FastMCP initialization
2. @mcp.tool() decorator pattern
3. CRITICAL: Always return JSON strings (not dicts)
4. Structured error handling
5. Async/await throughout
"""

import json
import logging
from typing import Any

from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

# PATTERN 1: Initialize FastMCP with descriptive name
mcp = FastMCP("Vibesbox Command Executor")

# PATTERN 2: Constants for optimization
MAX_OUTPUT_LENGTH = 10000  # Truncate large command output
DEFAULT_TIMEOUT = 30


def truncate_text(text: str | None, max_length: int = MAX_OUTPUT_LENGTH) -> str | None:
    """Truncate text to maximum length with ellipsis.

    CRITICAL: Always truncate large outputs to reduce payload size.
    This is Gotcha #3 from task-manager - MCP responses should be manageable.
    """
    if text and len(text) > max_length:
        return text[:max_length - 3] + "..."
    return text


# PATTERN 3: Tool decorator with async function
@mcp.tool()
async def execute_command(
    command: str,
    shell: str = "/bin/sh",
    timeout: int = DEFAULT_TIMEOUT,
    cwd: str | None = None
) -> str:
    """Execute shell command with streaming output.

    CRITICAL PATTERN: MCP tools MUST return JSON strings (not dicts).
    This is the #1 gotcha from task-manager implementation.

    Args:
        command: Shell command to execute
        shell: Shell interpreter to use
        timeout: Maximum execution time in seconds
        cwd: Working directory (optional)

    Returns:
        JSON string with result (NEVER returns dict - Gotcha #3)

    Example:
        execute_command("ls -la", shell="/bin/sh", timeout=10)
    """
    try:
        # TODO: Actual subprocess execution goes here
        # This is just the pattern structure

        # CRITICAL: Return json.dumps() NOT a dict
        return json.dumps({
            "success": True,
            "output": "Command executed successfully",
            "exit_code": 0,
            "command": command
        })

    except Exception as e:
        logger.error(f"Error in execute_command: {e}", exc_info=True)
        # PATTERN 4: Structured error responses with suggestion
        return json.dumps({
            "success": False,
            "error": str(e),
            "suggestion": "Check command syntax and try again"
        })


@mcp.tool()
async def list_processes() -> str:
    """List running processes in container.

    Returns:
        JSON string with process list (NEVER returns dict)
    """
    try:
        # TODO: Actual process listing goes here

        return json.dumps({
            "success": True,
            "processes": [],
            "count": 0
        })

    except Exception as e:
        logger.error(f"Error in list_processes: {e}", exc_info=True)
        return json.dumps({
            "success": False,
            "error": str(e),
            "suggestion": "Check error message and try again"
        })


@mcp.tool()
async def kill_process(pid: int) -> str:
    """Terminate a process by PID.

    Args:
        pid: Process ID to terminate

    Returns:
        JSON string with result (NEVER returns dict)
    """
    try:
        # TODO: Actual process termination goes here

        return json.dumps({
            "success": True,
            "message": f"Process {pid} terminated successfully"
        })

    except Exception as e:
        logger.error(f"Error in kill_process: {e}", exc_info=True)
        return json.dumps({
            "success": False,
            "error": str(e),
            "suggestion": "Check PID is valid and process exists"
        })


# PATTERN 5: Server execution
if __name__ == "__main__":
    # Run the MCP server
    # FastMCP handles all the HTTP/SSE/stdio transport details
    mcp.run()
