#!/usr/bin/env python3
"""
MCP Middleware Remote Server - With Real Tool Aggregation

This implementation adds real MCP client connections and tool aggregation
to replace the simulation layer.
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
from typing import Any, Dict, List, Optional, Set
import uuid

import uvicorn
from fastapi import FastAPI, Request, Response
from starlette.routing import Mount

# MCP SDK imports
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent, CallToolResult
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters
import mcp.server.stdio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-middleware-remote")

class MCPClientWrapper:
    """Wrapper for MCP client connections with lifecycle management."""
    
    def __init__(self, name: str, command: str, args: List[str]):
        self.name = name
        self.command = command
        self.args = args
        self.process: Optional[subprocess.Popen] = None
        self.session: Optional[ClientSession] = None
        self.tools: List[Tool] = []
        self.connected = False
        
    async def connect(self) -> bool:
        """Establish connection to the MCP server."""
        try:
            logger.info(f"Connecting to MCP {self.name} with command: {self.command} {' '.join(self.args)}")
            
            # Handle Docker exec connections
            if self.command == "docker" and "exec" in self.args:
                # For docker exec, we need to modify the approach
                container_name = None
                for i, arg in enumerate(self.args):
                    if arg == "-i" and i + 1 < len(self.args):
                        container_name = self.args[i + 1]
                        break
                
                if not container_name:
                    logger.error(f"Could not find container name in args: {self.args}")
                    return False
                
                # Check if container exists and is running
                check_cmd = ["docker", "ps", "--filter", f"name={container_name}", "--format", "{{.Names}}"]
                result = subprocess.run(check_cmd, capture_output=True, text=True)
                
                if container_name not in result.stdout:
                    logger.error(f"Container {container_name} is not running")
                    return False
                
                # Start the process
                self.process = subprocess.Popen(
                    [self.command] + self.args,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
            else:
                # For regular commands
                self.process = subprocess.Popen(
                    [self.command] + self.args,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            
            # Create client session
            server_params = StdioServerParameters(
                command=self.command,
                args=self.args
            )
            
            self.session = ClientSession(server_params)
            await self.session.initialize()
            
            # Fetch tools
            await self._fetch_tools()
            
            self.connected = True
            logger.info(f"Successfully connected to MCP {self.name}, found {len(self.tools)} tools")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to MCP {self.name}: {e}")
            await self.disconnect()
            return False
    
    async def disconnect(self):
        """Disconnect from the MCP server."""
        try:
            if self.session:
                await self.session.close()
                self.session = None
            
            if self.process:
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait()
                self.process = None
            
            self.connected = False
            self.tools = []
            logger.info(f"Disconnected from MCP {self.name}")
            
        except Exception as e:
            logger.error(f"Error disconnecting from MCP {self.name}: {e}")
    
    async def _fetch_tools(self):
        """Fetch tools from the connected MCP."""
        if not self.session:
            return
        
        try:
            result = await self.session.list_tools()
            self.tools = result.tools if result else []
            logger.info(f"Fetched {len(self.tools)} tools from MCP {self.name}")
            
        except Exception as e:
            logger.error(f"Failed to fetch tools from MCP {self.name}: {e}")
            self.tools = []
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Call a tool on this MCP."""
        if not self.session or not self.connected:
            return [TextContent(
                type="text",
                text=f"MCP {self.name} is not connected"
            )]
        
        try:
            result = await self.session.call_tool(tool_name, arguments)
            return result.content if result else []
            
        except Exception as e:
            logger.error(f"Tool call failed for {self.name}.{tool_name}: {e}")
            return [TextContent(
                type="text",
                text=f"Tool call failed: {str(e)}"
            )]

class MCPMiddlewareRemote:
    """MCP Middleware Remote Server with real tool aggregation."""
    
    def __init__(self):
        self.mcp_clients: Dict[str, MCPClientWrapper] = {}
        self.tool_registry: Dict[str, str] = {}  # tool_name -> mcp_name
        self.mcp_registry_file = os.environ.get("REGISTRY_FILE", "/app/data/mcp_registry.json")
        self.mcp_discovery_dir = os.environ.get("MCP_DISCOVERY_DIR", "/app/mcps")
        
        # Create MCP server
        self.mcp_server = Server("mcp-middleware")
        self._setup_tools()
        
        # FastAPI app for HTTP/SSE transport
        self.app = FastAPI(title="MCP Middleware Remote Server", docs_url=None, redoc_url=None)
        
        # Set up SSE transport
        self.sse_transport = SseServerTransport("/messages/")
        self.app.router.routes.append(Mount("/messages", app=self.sse_transport.handle_post_message))
        
        self._setup_routes()
        
        # Load existing MCPs
        self._load_registry()
    
    def _setup_tools(self):
        """Set up MCP tools for dynamic loading."""
        
        @self.mcp_server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available middleware tools plus aggregated tools from loaded MCPs."""
            tools = []
            
            # Add middleware management tools
            tools.extend([
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
                    name="unload_mcp",
                    description="Unload a dynamically loaded MCP server",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Name of the MCP to unload"}
                        },
                        "required": ["name"]
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
                ),
                Tool(
                    name="reload_mcp",
                    description="Reload a specific MCP server",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Name of the MCP to reload"}
                        },
                        "required": ["name"]
                    }
                )
            ])
            
            # Add tools from connected MCPs with prefixes to avoid conflicts
            for mcp_name, client in self.mcp_clients.items():
                if client.connected:
                    for tool in client.tools:
                        # Prefix tool names with MCP name
                        prefixed_name = f"{mcp_name}_{tool.name}"
                        prefixed_tool = Tool(
                            name=prefixed_name,
                            description=f"[{mcp_name}] {tool.description}",
                            inputSchema=tool.inputSchema
                        )
                        tools.append(prefixed_tool)
            
            logger.info(f"Returning {len(tools)} total tools ({len(tools) - 5} from loaded MCPs)")
            return tools
        
        @self.mcp_server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls, routing to appropriate MCP or handling middleware tools."""
            
            # Handle middleware management tools
            if name == "load_mcp":
                return await self._load_mcp(arguments)
            elif name == "unload_mcp":
                return await self._unload_mcp(arguments)
            elif name == "list_loaded_mcps":
                return await self._list_loaded_mcps()
            elif name == "discover_mcps":
                return await self._discover_mcps()
            elif name == "reload_mcp":
                return await self._reload_mcp(arguments)
            
            # Route to loaded MCPs
            for mcp_name, client in self.mcp_clients.items():
                if name.startswith(f"{mcp_name}_"):
                    original_tool_name = name[len(f"{mcp_name}_"):]
                    if client.connected:
                        return await client.call_tool(original_tool_name, arguments)
                    else:
                        return [TextContent(
                            type="text",
                            text=f"MCP '{mcp_name}' is not connected"
                        )]
            
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    def _setup_routes(self):
        """Set up FastAPI routes for MCP remote server."""
        
        @self.app.get("/sse", tags=["MCP"])
        async def handle_sse(request: Request):
            """SSE endpoint for MCP communication."""
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
            connected_mcps = sum(1 for client in self.mcp_clients.values() if client.connected)
            total_tools = sum(len(client.tools) for client in self.mcp_clients.values() if client.connected)
            
            return {
                "status": "healthy",
                "service": "mcp-middleware-remote",
                "loaded_mcps": len(self.mcp_clients),
                "connected_mcps": connected_mcps,
                "total_tools": total_tools
            }
    
    async def _load_mcp(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Load a new MCP dynamically with real connection."""
        name = arguments.get("name")
        command = arguments.get("command")
        args = arguments.get("args", [])
        
        if not name or not command:
            return [TextContent(
                type="text",
                text="Missing required parameters: name and command"
            )]
        
        if name in self.mcp_clients:
            return [TextContent(
                type="text",
                text=f"MCP '{name}' is already loaded"
            )]
        
        try:
            # Create and connect to MCP
            client = MCPClientWrapper(name, command, args)
            success = await client.connect()
            
            if success:
                self.mcp_clients[name] = client
                self._save_registry()
                
                return [TextContent(
                    type="text",
                    text=f"Successfully loaded MCP '{name}' with {len(client.tools)} tools: {[t.name for t in client.tools]}"
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"Failed to connect to MCP '{name}'"
                )]
                
        except Exception as e:
            logger.error(f"Error loading MCP {name}: {e}")
            return [TextContent(
                type="text",
                text=f"Failed to load MCP '{name}': {str(e)}"
            )]
    
    async def _unload_mcp(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Unload a dynamically loaded MCP."""
        name = arguments.get("name")
        
        if not name:
            return [TextContent(
                type="text",
                text="Missing required parameter: name"
            )]
        
        if name not in self.mcp_clients:
            return [TextContent(
                type="text",
                text=f"MCP '{name}' is not loaded"
            )]
        
        try:
            client = self.mcp_clients[name]
            await client.disconnect()
            del self.mcp_clients[name]
            self._save_registry()
            
            return [TextContent(
                type="text",
                text=f"Successfully unloaded MCP '{name}'"
            )]
            
        except Exception as e:
            logger.error(f"Error unloading MCP {name}: {e}")
            return [TextContent(
                type="text",
                text=f"Failed to unload MCP '{name}': {str(e)}"
            )]
    
    async def _reload_mcp(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Reload a specific MCP server."""
        name = arguments.get("name")
        
        if not name:
            return [TextContent(
                type="text",
                text="Missing required parameter: name"
            )]
        
        if name not in self.mcp_clients:
            return [TextContent(
                type="text",
                text=f"MCP '{name}' is not loaded"
            )]
        
        try:
            client = self.mcp_clients[name]
            command = client.command
            args = client.args
            
            # Unload first
            await self._unload_mcp({"name": name})
            
            # Then reload
            return await self._load_mcp({
                "name": name,
                "command": command,
                "args": args
            })
            
        except Exception as e:
            logger.error(f"Error reloading MCP {name}: {e}")
            return [TextContent(
                type="text",
                text=f"Failed to reload MCP '{name}': {str(e)}"
            )]
    
    async def _list_loaded_mcps(self) -> List[TextContent]:
        """List all currently loaded MCPs with their status."""
        if not self.mcp_clients:
            return [TextContent(
                type="text",
                text="No MCPs are currently loaded"
            )]
        
        mcp_info = []
        for name, client in self.mcp_clients.items():
            status = "connected" if client.connected else "disconnected"
            tool_count = len(client.tools)
            tool_names = [t.name for t in client.tools]
            
            info = f"**{name}**: {status} ({tool_count} tools)\n"
            info += f"  Command: {client.command} {' '.join(client.args)}\n"
            if tool_names:
                info += f"  Tools: {', '.join(tool_names)}\n"
            
            mcp_info.append(info)
        
        return [TextContent(
            type="text",
            text="Loaded MCPs:\n\n" + "\n".join(mcp_info)
        )]
    
    async def _discover_mcps(self) -> List[TextContent]:
        """Discover available MCPs in the discovery directory."""
        try:
            if not os.path.exists(self.mcp_discovery_dir):
                return [TextContent(
                    type="text",
                    text=f"Discovery directory does not exist: {self.mcp_discovery_dir}"
                )]
            
            discovered = []
            for file in os.listdir(self.mcp_discovery_dir):
                if file.endswith(".py") and file != "__init__.py":
                    discovered.append(f"Python MCP: {file}")
                elif os.access(os.path.join(self.mcp_discovery_dir, file), os.X_OK):
                    discovered.append(f"Executable MCP: {file}")
            
            if not discovered:
                return [TextContent(
                    type="text",
                    text=f"No MCPs discovered in {self.mcp_discovery_dir}"
                )]
            
            return [TextContent(
                type="text",
                text=f"Discovered MCPs:\n" + "\n".join(discovered)
            )]
            
        except Exception as e:
            logger.error(f"Error discovering MCPs: {e}")
            return [TextContent(
                type="text",
                text=f"Failed to discover MCPs: {str(e)}"
            )]
    
    def _save_registry(self):
        """Save the current MCP registry to file."""
        try:
            os.makedirs(os.path.dirname(self.mcp_registry_file), exist_ok=True)
            
            registry_data = {}
            for name, client in self.mcp_clients.items():
                registry_data[name] = {
                    "command": client.command,
                    "args": client.args
                }
            
            with open(self.mcp_registry_file, "w") as f:
                json.dump(registry_data, f, indent=2)
                
            logger.info(f"Saved registry with {len(registry_data)} MCPs")
            
        except Exception as e:
            logger.error(f"Failed to save registry: {e}")
    
    def _load_registry(self):
        """Load MCP registry from file if it exists."""
        try:
            if os.path.exists(self.mcp_registry_file):
                with open(self.mcp_registry_file, "r") as f:
                    registry_data = json.load(f)
                
                logger.info(f"Loading {len(registry_data)} MCPs from registry")
                
                # Note: We don't auto-connect on startup to avoid issues
                # MCPs can be manually loaded after startup
                
        except Exception as e:
            logger.error(f"Failed to load registry: {e}")

async def main():
    """Main entry point."""
    middleware = MCPMiddlewareRemote()
    
    # Run the FastAPI server
    config = uvicorn.Config(
        app=middleware.app,
        host="0.0.0.0",
        port=5001,
        log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())

