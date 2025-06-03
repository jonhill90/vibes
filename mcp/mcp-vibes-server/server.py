#!/usr/bin/env python3
"""
MCP Vibes Server - Simple Jumpbox

Gives Claude the ability to run shell commands in a container environment.
"""

import asyncio
import subprocess
import os
from pathlib import Path
from typing import Any, Dict, List

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Initialize MCP server
server = Server("mcp-vibes")

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available tools for Claude to use"""
    return [
        Tool(
            name="run_command",
            description="Execute shell commands in the jumpbox environment",
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
                        "default": "/workspace/vibes"
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
        working_dir = arguments.get("working_dir", "/workspace/vibes")
        
        try:
            # Change to working directory if specified
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
            
            # Format the response
            output = ""
            if result.stdout:
                output += f"STDOUT:\n{result.stdout}\n"
            if result.stderr:
                output += f"STDERR:\n{result.stderr}\n"
            output += f"EXIT CODE: {result.returncode}"
            
            return [TextContent(type="text", text=output)]
            
        except subprocess.TimeoutExpired:
            return [TextContent(type="text", text="❌ Command timed out after 60 seconds")]
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Error executing command: {str(e)}")]
    
    else:
        return [TextContent(type="text", text=f"❌ Unknown tool: {name}")]

async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
