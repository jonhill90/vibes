#!/usr/bin/env python3
"""
Enhanced MCP Middleware Server with Dynamic Loading

This enhanced version implements proper MCP client sessions for communicating
with dynamically loaded MCP servers.
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

class MCPClient:
    """Wrapper for MCP client session with process management."""
    
    def __init__(self, name: str, command: str, args: List[str], env: Dict[str, str]):
        self.name = name
        self.command = command
        self.args = args
        self.env = env
        self.process: Optional[subprocess.Popen] = None
        self.session: Optional[ClientSession] = None
        self.tools: List[types.Tool] = []
        self.resources: List[types.Resource] = []
        self.prompts: List[types.Prompt] = []
        
    async def start(self) -> bool:
        """Start the MCP server process and establish client session."""
        try:
            # Set up environment
            full_env = os.environ.copy()
            full_env.update(self.env)
            
            # Start the process
            self.process = subprocess.Popen(
                [self.command] + self.args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=full_env,
                text=True
            )
            
            # Create server parameters
            server_params = StdioServerParameters(
                command=self.command,
                args=self.args,
                env=self.env
            )
            
            # Create and initialize client session
            self.session = ClientSession(server_params)
            await self.session.initialize()
            
            # Fetch available capabilities
            await self._fetch_capabilities()
            
            logger.info(f"Successfully started MCP client: {self.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start MCP client {self.name}: {e}")
            await self.stop()
            return False
    
    async def stop(self):
        """Stop the MCP client session and process."""
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
                
            logger.info(f"Stopped MCP client: {self.name}")
            
        except Exception as e:
            logger.error(f"Error stopping MCP client {self.name}: {e}")
    
    async def _fetch_capabilities(self):
        """Fetch tools, resources, and prompts from the MCP server."""
        if not self.session:
            return
            
        try:
            # Fetch tools
            tools_result = await self.session.list_tools()
            self.tools = tools_result.tools if tools_result else []
            
            # Fetch resources
            try:
                resources_result = await self.session.list_resources()
                self.resources = resources_result.resources if resources_result else []
            except Exception:
                self.resources = []  # Not all MCPs support resources
            
            # Fetch prompts
            try:
                prompts_result = await self.session.list_prompts()
                self.prompts = prompts_result.prompts if prompts_result else []
            except Exception:
                self.prompts = []  # Not all MCPs support prompts
                
            logger.info(f"Fetched capabilities for {self.name}: {len(self.tools)} tools, {len(self.resources)} resources, {len(self.prompts)} prompts")
            
        except Exception as e:
            logger.error(f"Failed to fetch capabilities for {self.name}: {e}")
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Call a tool on this MCP server."""
        if not self.session:
            return [types.TextContent(
                type="text",
                text=f"MCP client {self.name} is not connected"
            )]
        
        try:
            result = await self.session.call_tool(name, arguments)
            return result.content if result else []
            
        except Exception as e:
            logger.error(f"Tool call failed for {self.name}.{name}: {e}")
            return [types.TextContent(
                type="text",
                text=f"Tool call failed: {str(e)}"
            )]
    
    def is_running(self) -> bool:
        """Check if the MCP client is running."""
        return (self.process is not None and 
                self.process.poll() is None and 
                self.session is not None)

class MCPMiddleware:
    """
    Enhanced MCP Middleware that manages dynamic loading and routing of other MCP servers.
    """
    
    def __init__(self):
        self.server = Server("mcp-middleware")
        self.mcp_clients: Dict[str, MCPClient] = {}
        self.mcp_registry_file = os.path.join(os.path.dirname(__file__), "mcp_registry.json")
        self.mcp_discovery_dir = os.path.join(os.path.dirname(__file__), "mcps")
        
        # Ensure discovery directory exists
        os.makedirs(self.mcp_discovery_dir, exist_ok=True)
        
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
                                "description": "Arguments for the MCP server command",
                                "default": []
                            },
                            "env": {
                                "type": "object",
                                "description": "Environment variables for the MCP server",
                                "default": {}
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
                    description="List all currently loaded MCP servers and their capabilities",
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
                ),
                types.Tool(
                    name="discover_mcps",
                    description="Discover MCP servers in the discovery directory",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "auto_load": {
                                "type": "boolean",
                                "description": "Automatically load discovered MCPs",
                                "default": False
                            }
                        }
                    }
                ),
                types.Tool(
                    name="get_mcp_status",
                    description="Get detailed status of a specific MCP",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Name identifier of the MCP"
                            }
                        },
                        "required": ["name"]
                    }
                )
            ])
            
            # Add tools from loaded MCPs with prefixes
            for mcp_name, client in self.mcp_clients.items():
                if client.is_running():
                    for tool in client.tools:
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
            elif name == "discover_mcps":
                return await self._discover_mcps(arguments)
            elif name == "get_mcp_status":
                return await self._get_mcp_status(arguments)
            
            # Route to loaded MCPs
            for mcp_name, client in self.mcp_clients.items():
                if name.startswith(f"{mcp_name}_"):
                    original_tool_name = name[len(f"{mcp_name}_"):]
                    if client.is_running():
                        return await client.call_tool(original_tool_name, arguments)
                    else:
                        return [types.TextContent(
                            type="text",
                            text=f"MCP '{mcp_name}' is not running"
                        )]
            
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
            if name in self.mcp_clients:
                return [types.TextContent(
                    type="text",
                    text=f"MCP '{name}' is already loaded"
                )]
            
            # Create and start MCP client
            client = MCPClient(name, command, args, env)
            success = await client.start()
            
            if success:
                self.mcp_clients[name] = client
                await self._save_registry()
                
                tool_count = len(client.tools)
                return [types.TextContent(
                    type="text",
                    text=f"Successfully loaded MCP '{name}' with {tool_count} tools"
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"Failed to load MCP '{name}'"
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
        
        if name not in self.mcp_clients:
            return [types.TextContent(
                type="text",
                text=f"MCP '{name}' is not loaded"
            )]
        
        try:
            # Stop the client
            client = self.mcp_clients[name]
            await client.stop()
            
            # Remove from loaded MCPs
            del self.mcp_clients[name]
            
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
        """List all currently loaded MCP servers and their capabilities."""
        if not self.mcp_clients:
            return [types.TextContent(
                type="text",
                text="No MCPs are currently loaded"
            )]
        
        mcp_details = []
        for name, client in self.mcp_clients.items():
            status = "running" if client.is_running() else "stopped"
            tool_count = len(client.tools)
            resource_count = len(client.resources)
            prompt_count = len(client.prompts)
            
            details = f"**{name}**: {status}\n"
            details += f"  - Tools: {tool_count}\n"
            details += f"  - Resources: {resource_count}\n"
            details += f"  - Prompts: {prompt_count}\n"
            details += f"  - Command: {client.command} {' '.join(client.args)}"
            
            mcp_details.append(details)
        
        return [types.TextContent(
            type="text",
            text="Loaded MCPs:\n\n" + "\n\n".join(mcp_details)
        )]
    
    async def _reload_mcp(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Reload a specific MCP server."""
        name = arguments["name"]
        
        if name not in self.mcp_clients:
            return [types.TextContent(
                type="text",
                text=f"MCP '{name}' is not loaded"
            )]
        
        # Store the original configuration
        client = self.mcp_clients[name]
        command = client.command
        args = client.args
        env = client.env
        
        # Unload and reload
        await self._unload_mcp({"name": name})
        return await self._load_mcp({
            "name": name,
            "command": command,
            "args": args,
            "env": env
        })
    
    async def _discover_mcps(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Discover MCP servers in the discovery directory."""
        auto_load = arguments.get("auto_load", False)
        
        try:
            discovered = []
            
            # Look for Python MCP servers
            for file in os.listdir(self.mcp_discovery_dir):
                if file.endswith(".py") and file != "__init__.py":
                    mcp_path = os.path.join(self.mcp_discovery_dir, file)
                    mcp_name = file[:-3]  # Remove .py extension
                    
                    discovered.append({
                        "name": mcp_name,
                        "command": "python",
                        "args": [mcp_path],
                        "type": "python"
                    })
            
            # Look for executable scripts
            for file in os.listdir(self.mcp_discovery_dir):
                file_path = os.path.join(self.mcp_discovery_dir, file)
                if os.access(file_path, os.X_OK) and not file.endswith(".py"):
                    discovered.append({
                        "name": file,
                        "command": file_path,
                        "args": [],
                        "type": "executable"
                    })
            
            if not discovered:
                return [types.TextContent(
                    type="text",
                    text=f"No MCPs discovered in {self.mcp_discovery_dir}"
                )]
            
            result_text = f"Discovered {len(discovered)} MCPs:\n\n"
            
            for mcp in discovered:
                result_text += f"- **{mcp['name']}** ({mcp['type']})\n"
                result_text += f"  Command: {mcp['command']} {' '.join(mcp['args'])}\n\n"
                
                if auto_load and mcp['name'] not in self.mcp_clients:
                    load_result = await self._load_mcp({
                        "name": mcp['name'],
                        "command": mcp['command'],
                        "args": mcp['args'],
                        "env": {}
                    })
                    result_text += f"  Auto-load result: {load_result[0].text}\n\n"
            
            return [types.TextContent(type="text", text=result_text)]
            
        except Exception as e:
            logger.error(f"Failed to discover MCPs: {e}")
            return [types.TextContent(
                type="text",
                text=f"Failed to discover MCPs: {str(e)}"
            )]
    
    async def _get_mcp_status(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Get detailed status of a specific MCP."""
        name = arguments["name"]
        
        if name not in self.mcp_clients:
            return [types.TextContent(
                type="text",
                text=f"MCP '{name}' is not loaded"
            )]
        
        client = self.mcp_clients[name]
        
        status_text = f"**MCP Status: {name}**\n\n"
        status_text += f"- **Status**: {'Running' if client.is_running() else 'Stopped'}\n"
        status_text += f"- **Command**: {client.command}\n"
        status_text += f"- **Arguments**: {client.args}\n"
        status_text += f"- **Environment**: {client.env}\n\n"
        
        status_text += f"**Capabilities:**\n"
        status_text += f"- **Tools** ({len(client.tools)}):\n"
        for tool in client.tools:
            status_text += f"  - {tool.name}: {tool.description}\n"
        
        if client.resources:
            status_text += f"- **Resources** ({len(client.resources)}):\n"
            for resource in client.resources:
                status_text += f"  - {resource.name}: {resource.description}\n"
        
        if client.prompts:
            status_text += f"- **Prompts** ({len(client.prompts)}):\n"
            for prompt in client.prompts:
                status_text += f"  - {prompt.name}: {prompt.description}\n"
        
        return [types.TextContent(type="text", text=status_text)]
    
    async def _save_registry(self):
        """Save the current MCP registry to file."""
        registry_data = {}
        for name, client in self.mcp_clients.items():
            registry_data[name] = {
                "command": client.command,
                "args": client.args,
                "env": client.env
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
                    
                logger.info(f"Loaded {len(registry_data)} MCPs from registry")
                    
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

