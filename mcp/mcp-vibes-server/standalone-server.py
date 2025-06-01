#!/usr/bin/env python3
"""
MCP Vibes Server - Standalone Version for Claude Desktop

This version runs directly without Docker for easier Claude Desktop integration.
"""

import asyncio
import subprocess
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

# Add the path to find mcp modules if needed
sys.path.insert(0, '/usr/local/lib/python3.10/dist-packages')

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError as e:
    print(f"Error importing MCP: {e}", file=sys.stderr)
    print("Make sure the 'mcp' package is installed: pip install mcp", file=sys.stderr)
    sys.exit(1)

# Initialize MCP server
server = Server("mcp-vibes-standalone")

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available tools for Claude to use"""
    return [
        Tool(
            name="run_command",
            description="Execute shell commands in the container environment",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Shell command to execute"
                    },
                    "working_dir": {
                        "type": "string",
                        "description": "Working directory (optional)",
                        "default": "/workspace"
                    }
                },
                "required": ["command"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls from Claude"""
    
    if name == "run_command":
        command = arguments["command"]
        working_dir = arguments.get("working_dir", "/workspace")
        
        try:
            # Change to working directory if specified and exists
            original_dir = os.getcwd()
            if working_dir and os.path.exists(working_dir):
                os.chdir(working_dir)
            
            # Execute the command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Restore original directory
            os.chdir(original_dir)
            
            # Format the response
            output = ""
            if result.stdout:
                output += f"STDOUT:\n{result.stdout}\n"
            if result.stderr:
                output += f"STDERR:\n{result.stderr}\n"
            output += f"EXIT CODE: {result.returncode}"
            
            return [TextContent(type="text", text=output)]
            
        except subprocess.TimeoutExpired:
            os.chdir(original_dir)
            return [TextContent(type="text", text="❌ Command timed out after 60 seconds")]
        except Exception as e:
            os.chdir(original_dir)
            return [TextContent(type="text", text=f"❌ Error executing command: {str(e)}")]
    
    else:
        return [TextContent(type="text", text=f"❌ Unknown tool: {name}")]

async def main():
    """Run the MCP server"""
    try:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
