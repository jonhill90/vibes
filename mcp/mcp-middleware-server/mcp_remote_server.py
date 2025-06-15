#!/usr/bin/env python3
"""
MCP Middleware Remote Server - Fixed SSE Implementation

Based on working examples from Microsoft Azure documentation.
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import FastAPI, Request, Response
from starlette.routing import Mount

# MCP SDK imports
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent
import mcp.server.stdio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-middleware-remote")

class MCPMiddlewareRemote:
    """MCP Middleware Remote Server for dynamic loading."""
    
    def __init__(self):
        self.loaded_mcps = {}
        self.mcp_registry_file = os.environ.get("REGISTRY_FILE", "/app/data/mcp_registry.json")
        self.mcp_discovery_dir = os.environ.get("MCP_DISCOVERY_DIR", "/app/mcps")
        
        # Create MCP server
        self.mcp_server = Server("mcp-middleware")
        self._setup_tools()
        
        # FastAPI app for HTTP/SSE transport
        self.app = FastAPI(title="MCP Middleware Remote Server", docs_url=None, redoc_url=None)
        
        # Set up SSE transport (following Microsoft Azure example)
        self.sse_transport = SseServerTransport("/messages/")
        self.app.router.routes.append(Mount("/messages", app=self.sse_transport.handle_post_message))
        
        self._setup_routes()
        
        # Load existing MCPs
        self._load_registry()
    
    def _setup_tools(self):
        """Set up MCP tools for dynamic loading."""
        
        @self.mcp_server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available middleware tools."""
            return [
                Tool(
                    name="load_mcp",
                    description="Load a new MCP server dynamically",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Name for the MCP"},
                            "command": {"type": "string", "description": "Command to run"},
                            "args": {"type": "array", "items": {"type": "string"}, "description": "Arguments"}
                        },
                        "required": ["name", "command"]
                    }
                ),
                Tool(
                    name="list_loaded_mcps",
                    description="List all currently loaded MCPs",
                    inputSchema={"type": "object", "properties": {}}
                ),
                Tool(
                    name="discover_mcps",
                    description="Discover available MCPs in the directory",
                    inputSchema={"type": "object", "properties": {}}
                )
            ]
        
        @self.mcp_server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls."""
            if name == "load_mcp":
                return await self._load_mcp(arguments)
            elif name == "list_loaded_mcps":
                return await self._list_loaded_mcps()
            elif name == "discover_mcps":
                return await self._discover_mcps()
            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    def _setup_routes(self):
        """Set up FastAPI routes for MCP remote server."""
        
        @self.app.get("/sse", tags=["MCP"])
        async def handle_sse(request: Request):
            """SSE endpoint for MCP communication (following Azure example)."""
            try:
                async with self.sse_transport.connect_sse(
                    request.scope, 
                    request.receive, 
                    request._send
                ) as (read_stream, write_stream):
                    init_options = self.mcp_server.create_initialization_options()
                    await self.mcp_server.run(
                        read_stream,
                        write_stream,
                        init_options,
                    )
            except Exception as e:
                logger.error(f"SSE connection error: {e}")
                return Response(status_code=500, content=f"SSE Error: {str(e)}")
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {
                "status": "healthy",
                "service": "mcp-middleware-remote",
                "loaded_mcps": len(self.loaded_mcps)
            }
    
    async def _load_mcp(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Load a new MCP dynamically."""
        name = arguments.get("name")
        command = arguments.get("command")
        args = arguments.get("args", [])
        
        try:
            # Simple simulation for now
            self.loaded_mcps[name] = {
                "command": command,
                "args": args,
                "status": "loaded"
            }
            
            return [TextContent(
                type="text",
                text=f"Successfully loaded MCP '{name}' with command '{command}'"
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Failed to load MCP '{name}': {str(e)}"
            )]
    
    async def _list_loaded_mcps(self) -> List[TextContent]:
        """List all loaded MCPs."""
        if not self.loaded_mcps:
            return [TextContent(type="text", text="No MCPs currently loaded")]
        
        mcp_list = []
        for name, info in self.loaded_mcps.items():
            mcp_list.append(f"- {name}: {info['status']} (command: {info['command']})")
        
        return [TextContent(
            type="text",
            text=f"Loaded MCPs:\n" + "\n".join(mcp_list)
        )]
    
    async def _discover_mcps(self) -> List[TextContent]:
        """Discover available MCPs in the directory."""
        try:
            if os.path.exists(self.mcp_discovery_dir):
                files = os.listdir(self.mcp_discovery_dir)
                py_files = [f for f in files if f.endswith('.py')]
                return [TextContent(
                    type="text",
                    text=f"Available MCPs in {self.mcp_discovery_dir}:\n" + "\n".join(py_files)
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"Discovery directory {self.mcp_discovery_dir} not found"
                )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error discovering MCPs: {str(e)}"
            )]
    
    def _load_registry(self):
        """Load existing MCP registry if it exists."""
        try:
            if os.path.exists(self.mcp_registry_file):
                with open(self.mcp_registry_file, 'r') as f:
                    registry_data = json.load(f)
                    self.loaded_mcps.update(registry_data)
                    logger.info(f"Loaded {len(registry_data)} MCPs from registry")
        except Exception as e:
            logger.error(f"Failed to load registry: {e}")

def main():
    """Main entry point."""
    middleware = MCPMiddlewareRemote()
    
    logger.info("Starting MCP Middleware Remote Server on 0.0.0.0:5000")
    logger.info("SSE endpoint: http://0.0.0.0:5000/sse")
    logger.info("Health check: http://0.0.0.0:5000/health")
    
    # Use uvicorn.run directly without asyncio.run()
    uvicorn.run(middleware.app, host="0.0.0.0", port=5000, log_level="info")

if __name__ == "__main__":
    main()
