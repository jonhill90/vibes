#!/usr/bin/env python3
"""
AgentBox MCP Server
Lightweight MCP server for agent command execution
Pattern: infra/vibesbox with simplified tools
"""

import json
import logging
import subprocess
import asyncio
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from starlette.responses import JSONResponse
from starlette.routing import Route

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
# Pattern: infra/vibesbox/src/mcp_server.py
mcp = FastMCP(
    "agentbox",
    host="0.0.0.0",
    port=8000
)

# Add custom health endpoint to underlying Starlette app
@mcp.custom_route("/health", methods=["GET"])
async def health_endpoint(request):
    """HTTP health endpoint for Docker healthcheck"""
    return JSONResponse({
        "status": "healthy",
        "service": "agentbox",
        "version": "1.0.0"
    })

# Simple process tracking
active_processes = {}


@mcp.tool()
async def execute_command(
    command: str,
    shell: str = "/bin/sh",
    timeout: int = 30
) -> str:
    """Execute shell command with timeout.

    Pattern from: vibesbox execute_command
    Returns JSON string (not dict)

    Args:
        command: Shell command to execute
        shell: Shell interpreter (/bin/sh or /bin/bash)
        timeout: Max execution time (1-300 seconds, default 30)

    Returns:
        JSON string with result
    """
    try:
        # Cap timeout
        timeout = min(max(timeout, 1), 300)

        logger.info(f"Executing: {command[:50]}...")

        result = subprocess.run(
            [shell, "-c", command],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        return json.dumps({
            "success": result.returncode == 0,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "truncated": False
        })

    except subprocess.TimeoutExpired:
        return json.dumps({
            "success": False,
            "exit_code": -1,
            "stdout": "",
            "stderr": f"Command timed out after {timeout} seconds",
            "truncated": False,
            "error": "timeout"
        })
    except Exception as e:
        return json.dumps({
            "success": False,
            "exit_code": -1,
            "stdout": "",
            "stderr": str(e),
            "truncated": False,
            "error": str(e)
        })


@mcp.tool()
async def manage_process(
    action: str,
    pid: int | None = None
) -> str:
    """Manage background processes.

    Pattern from: vibesbox manage_process

    Args:
        action: "list" | "kill" | "read"
        pid: Process ID (required for kill/read)

    Returns:
        JSON string with result
    """
    if action == "list":
        processes = [
            {
                "pid": pid,
                "command": info["command"],
                "status": "running" if info["proc"].poll() is None else "completed"
            }
            for pid, info in active_processes.items()
        ]

        return json.dumps({
            "success": True,
            "processes": processes,
            "count": len(processes)
        })

    elif action == "kill" and pid:
        if pid not in active_processes:
            return json.dumps({
                "success": False,
                "error": f"Process {pid} not found"
            })

        try:
            active_processes[pid]["proc"].terminate()
            return json.dumps({
                "success": True,
                "message": f"Process {pid} terminated",
                "pid": pid
            })
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e)
            })

    elif action == "read" and pid:
        if pid not in active_processes:
            return json.dumps({
                "success": False,
                "error": f"Process {pid} not found"
            })

        proc = active_processes[pid]["proc"]
        stdout = proc.stdout.read() if proc.stdout else ""

        return json.dumps({
            "success": True,
            "pid": pid,
            "output": stdout,
            "has_new_output": len(stdout) > 0
        })

    else:
        return json.dumps({
            "success": False,
            "error": "Invalid action or missing pid"
        })


@mcp.tool()
async def health() -> str:
    """Health check for Docker monitoring.

    Pattern from: vibesbox health
    """
    return json.dumps({
        "status": "healthy",
        "service": "agentbox",
        "version": "1.0.0"
    })


if __name__ == "__main__":
    logger.info("Starting AgentBox MCP server...")
    logger.info("   Mode: Streamable HTTP")
    logger.info("   URL: http://0.0.0.0:8000/mcp")

    try:
        mcp.run(transport="streamable-http")
    except KeyboardInterrupt:
        logger.info("AgentBox MCP server stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise
