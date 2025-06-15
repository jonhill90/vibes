#!/usr/bin/env python3
"""
Simple Test MCP Server

A basic MCP server for testing the middleware functionality.
Provides simple tools for demonstration purposes.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List

from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test-mcp")

class TestMCPServer:
    """Simple test MCP server."""
    
    def __init__(self):
        self.server = Server("test-mcp")
        self._setup_handlers()
        
    def _setup_handlers(self):
        """Setup MCP server handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """List available tools."""
            return [
                types.Tool(
                    name="echo",
                    description="Echo back the provided message",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "Message to echo back"
                            }
                        },
                        "required": ["message"]
                    }
                ),
                types.Tool(
                    name="add_numbers",
                    description="Add two numbers together",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "a": {
                                "type": "number",
                                "description": "First number"
                            },
                            "b": {
                                "type": "number",
                                "description": "Second number"
                            }
                        },
                        "required": ["a", "b"]
                    }
                ),
                types.Tool(
                    name="get_timestamp",
                    description="Get the current timestamp",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
            """Handle tool calls."""
            
            if name == "echo":
                message = arguments.get("message", "")
                return [types.TextContent(
                    type="text",
                    text=f"Echo: {message}"
                )]
            
            elif name == "add_numbers":
                a = arguments.get("a", 0)
                b = arguments.get("b", 0)
                result = a + b
                return [types.TextContent(
                    type="text",
                    text=f"{a} + {b} = {result}"
                )]
            
            elif name == "get_timestamp":
                import time
                timestamp = time.time()
                return [types.TextContent(
                    type="text",
                    text=f"Current timestamp: {timestamp}"
                )]
            
            else:
                return [types.TextContent(
                    type="text",
                    text=f"Unknown tool: {name}"
                )]
    
    async def run(self):
        """Run the test MCP server."""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="test-mcp",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )

async def main():
    """Main entry point."""
    server = TestMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())

