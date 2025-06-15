#!/usr/bin/env python3
"""
MCP Middleware Server

This server acts as a middleware between Claude Desktop and other MCP servers,
enabling dynamic loading and management of MCPs without requiring configuration
changes or restarts.
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
from typing import Any, Dict, List, Optional, Sequence

from mcp import ClientSession, StdioServerParameters
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-middleware")

class MCPMiddleware:
    """
    MCP Middleware that manages dynamic loading and routing of other MCP servers.
    """
    
    def __init__(self):
        self.server = Server("mcp-middleware")
        self.loaded_mcps: Dict[str, Dict[str, Any]] = {}
        self.mcp_registry_file = os.path.join(os.path.dirname(__file__), "mcp_registry.json")
        
        # Setup handlers
        self._setup_handlers()
        
    def _setup_handlers(self):
        """Setup MCP server handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """List all available tools from all loaded MCPs."""
            tools = []
            
            # Add middleware management tools
            tools.extend([
                types.Tool(
                    name="load_mcp",
                    description="Load a new MCP server dynamically",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Name identifier for the MCP"
                            },
                            "command": {
                                "type": "string", 
                                "description": "Command to run the MCP server"
                            },
                            "args": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Arguments for the MCP server command"
                            },
                            "env": {
                                "type": "object",
                                "description": "Environment variables for the MCP server"
                            }
                        },
                        "required": ["name", "command"]
                    }
                ),
                types.Tool(
                    name="unload_mcp",
                    description="Unload a dynamically loaded MCP server",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Name identifier of the MCP to unload"
                            }
                        },
                        "required": ["name"]
                    }
                ),
                types.Tool(
                    name="list_loaded_mcps",
                    description="List all currently loaded MCP servers",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                types.Tool(
                    name="reload_mcp",
                    description="Reload a specific MCP server",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Name identifier of the MCP to reload"
                            }
                        },
                        "required": ["name"]
                    }
                )
            ])
            
            # Add tools from loaded MCPs
            for mcp_name, mcp_info in self.loaded_mcps.items():
                if "tools" in mcp_info:
                    for tool in mcp_info["tools"]:
                        # Prefix tool names with MCP name to avoid conflicts
                        prefixed_tool = types.Tool(
                            name=f"{mcp_name}_{tool.name}",
                            description=f"[{mcp_name}] {tool.description}",
                            inputSchema=tool.inputSchema
                        )
                        tools.append(prefixed_tool)
            
            return tools
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
            """Handle tool calls, routing to appropriate MCP or handling middleware tools."""
            
            # Handle middleware management tools
            if name == "load_mcp":
                return await self._load_mcp(arguments)
            elif name == "unload_mcp":
                return await self._unload_mcp(arguments)
            elif name == "list_loaded_mcps":
                return await self._list_loaded_mcps()
            elif name == "reload_mcp":
                return await self._reload_mcp(arguments)
            
            # Route to loaded MCPs
            for mcp_name in self.loaded_mcps:
                if name.startswith(f"{mcp_name}_"):
                    original_tool_name = name[len(f"{mcp_name}_"):]
                    return await self._route_to_mcp(mcp_name, original_tool_name, arguments)
            
            return [types.TextContent(
                type="text",
                text=f"Tool '{name}' not found in any loaded MCP"
            )]
    
    async def _load_mcp(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Load a new MCP server dynamically."""
        name = arguments["name"]
        command = arguments["command"]
        args = arguments.get("args", [])
        env = arguments.get("env", {})
        
        try:
            # Check if MCP is already loaded
            if name in self.loaded_mcps:
                return [types.TextContent(
                    type="text",
                    text=f"MCP '{name}' is already loaded"
                )]
            
            # Start the MCP server process
            full_env = os.environ.copy()
            full_env.update(env)
            
            process = subprocess.Popen(
                [command] + args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=full_env,
                text=True
            )
            
            # Create client session to communicate with the MCP
            server_params = StdioServerParameters(
                command=command,
                args=args,
                env=env
            )
            
            # Store MCP information
            self.loaded_mcps[name] = {
                "process": process,
                "command": command,
                "args": args,
                "env": env,
                "server_params": server_params,
                "tools": []  # Will be populated when we connect
            }
            
            # Save to registry
            await self._save_registry()
            
            logger.info(f"Successfully loaded MCP: {name}")
            return [types.TextContent(
                type="text",
                text=f"Successfully loaded MCP '{name}'"
            )]
            
        except Exception as e:
            logger.error(f"Failed to load MCP {name}: {e}")
            return [types.TextContent(
                type="text",
                text=f"Failed to load MCP '{name}': {str(e)}"
            )]
    
    async def _unload_mcp(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Unload a dynamically loaded MCP server."""
        name = arguments["name"]
        
        if name not in self.loaded_mcps:
            return [types.TextContent(
                type="text",
                text=f"MCP '{name}' is not loaded"
            )]
        
        try:
            # Terminate the process
            mcp_info = self.loaded_mcps[name]
            if "process" in mcp_info:
                mcp_info["process"].terminate()
                mcp_info["process"].wait(timeout=5)
            
            # Remove from loaded MCPs
            del self.loaded_mcps[name]
            
            # Save to registry
            await self._save_registry()
            
            logger.info(f"Successfully unloaded MCP: {name}")
            return [types.TextContent(
                type="text",
                text=f"Successfully unloaded MCP '{name}'"
            )]
            
        except Exception as e:
            logger.error(f"Failed to unload MCP {name}: {e}")
            return [types.TextContent(
                type="text",
                text=f"Failed to unload MCP '{name}': {str(e)}"
            )]
    
    async def _list_loaded_mcps(self) -> List[types.TextContent]:
        """List all currently loaded MCP servers."""
        if not self.loaded_mcps:
            return [types.TextContent(
                type="text",
                text="No MCPs are currently loaded"
            )]
        
        mcp_list = []
        for name, info in self.loaded_mcps.items():
            status = "running" if info.get("process") and info["process"].poll() is None else "stopped"
            tool_count = len(info.get("tools", []))
            mcp_list.append(f"- {name}: {status} ({tool_count} tools)")
        
        return [types.TextContent(
            type="text",
            text=f"Loaded MCPs:\n" + "\n".join(mcp_list)
        )]
    
    async def _reload_mcp(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Reload a specific MCP server."""
        name = arguments["name"]
        
        if name not in self.loaded_mcps:
            return [types.TextContent(
                type="text",
                text=f"MCP '{name}' is not loaded"
            )]
        
        # Store the original configuration
        mcp_info = self.loaded_mcps[name]
        command = mcp_info["command"]
        args = mcp_info["args"]
        env = mcp_info["env"]
        
        # Unload and reload
        await self._unload_mcp({"name": name})
        return await self._load_mcp({
            "name": name,
            "command": command,
            "args": args,
            "env": env
        })
    
    async def _route_to_mcp(self, mcp_name: str, tool_name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Route a tool call to the appropriate MCP server."""
        # For now, return a placeholder response
        # In a full implementation, this would establish a client connection
        # to the MCP server and forward the tool call
        return [types.TextContent(
            type="text",
            text=f"Routed call to {mcp_name}.{tool_name} with args: {arguments}"
        )]
    
    async def _save_registry(self):
        """Save the current MCP registry to file."""
        registry_data = {}
        for name, info in self.loaded_mcps.items():
            registry_data[name] = {
                "command": info["command"],
                "args": info["args"],
                "env": info["env"]
            }
        
        with open(self.mcp_registry_file, "w") as f:
            json.dump(registry_data, f, indent=2)
    
    async def _load_registry(self):
        """Load MCP registry from file if it exists."""
        if os.path.exists(self.mcp_registry_file):
            try:
                with open(self.mcp_registry_file, "r") as f:
                    registry_data = json.load(f)
                
                for name, config in registry_data.items():
                    await self._load_mcp({
                        "name": name,
                        "command": config["command"],
                        "args": config.get("args", []),
                        "env": config.get("env", {})
                    })
            except Exception as e:
                logger.error(f"Failed to load registry: {e}")
    
    async def run(self):
        """Run the MCP middleware server."""
        # Load existing MCPs from registry
        await self._load_registry()
        
        # Run the server
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="mcp-middleware",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )

async def main():
    """Main entry point."""
    middleware = MCPMiddleware()
    await middleware.run()

if __name__ == "__main__":
    asyncio.run(main())

