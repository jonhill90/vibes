#!/usr/bin/env python3
"""
MCP Middleware with Real-time Feedback

This version adds SSE (Server-Sent Events) support for real-time feedback
to Claude Desktop about MCP status changes and events.
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import threading
import time
from typing import Any, Dict, List, Optional, Sequence
from flask import Flask, Response, jsonify
from flask_cors import CORS
import queue

from mcp import ClientSession, StdioServerParameters
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-middleware")

class EventBroadcaster:
    """Handles SSE event broadcasting to connected clients."""
    
    def __init__(self):
        self.clients = []
        self.event_queue = queue.Queue()
        
    def add_client(self, client_queue):
        """Add a new SSE client."""
        self.clients.append(client_queue)
        logger.info(f"SSE client connected. Total clients: {len(self.clients)}")
        
    def remove_client(self, client_queue):
        """Remove an SSE client."""
        if client_queue in self.clients:
            self.clients.remove(client_queue)
            logger.info(f"SSE client disconnected. Total clients: {len(self.clients)}")
    
    def broadcast_event(self, event_type: str, data: Dict[str, Any]):
        """Broadcast an event to all connected clients."""
        event = {
            "type": event_type,
            "timestamp": time.time(),
            "data": data
        }
        
        # Remove disconnected clients
        active_clients = []
        for client_queue in self.clients:
            try:
                client_queue.put(event, timeout=1)
                active_clients.append(client_queue)
            except queue.Full:
                logger.warning("Client queue full, removing client")
                continue
        
        self.clients = active_clients
        logger.info(f"Broadcasted {event_type} event to {len(self.clients)} clients")

class MCPClient:
    """Enhanced MCP client with event broadcasting."""
    
    def __init__(self, name: str, command: str, args: List[str], env: Dict[str, str], broadcaster: EventBroadcaster):
        self.name = name
        self.command = command
        self.args = args
        self.env = env
        self.broadcaster = broadcaster
        self.process: Optional[subprocess.Popen] = None
        self.session: Optional[ClientSession] = None
        self.tools: List[types.Tool] = []
        self.resources: List[types.Resource] = []
        self.prompts: List[types.Prompt] = []
        self.last_health_check = time.time()
        
    async def start(self) -> bool:
        """Start the MCP server process and establish client session."""
        try:
            self.broadcaster.broadcast_event("mcp_starting", {
                "name": self.name,
                "command": self.command,
                "args": self.args
            })
            
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
            
            self.broadcaster.broadcast_event("mcp_started", {
                "name": self.name,
                "tools": len(self.tools),
                "resources": len(self.resources),
                "prompts": len(self.prompts)
            })
            
            logger.info(f"Successfully started MCP client: {self.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start MCP client {self.name}: {e}")
            self.broadcaster.broadcast_event("mcp_start_failed", {
                "name": self.name,
                "error": str(e)
            })
            await self.stop()
            return False
    
    async def stop(self):
        """Stop the MCP client session and process."""
        try:
            self.broadcaster.broadcast_event("mcp_stopping", {
                "name": self.name
            })
            
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
            
            self.broadcaster.broadcast_event("mcp_stopped", {
                "name": self.name
            })
                
            logger.info(f"Stopped MCP client: {self.name}")
            
        except Exception as e:
            logger.error(f"Error stopping MCP client {self.name}: {e}")
            self.broadcaster.broadcast_event("mcp_stop_error", {
                "name": self.name,
                "error": str(e)
            })
    
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
                self.resources = []
            
            # Fetch prompts
            try:
                prompts_result = await self.session.list_prompts()
                self.prompts = prompts_result.prompts if prompts_result else []
            except Exception:
                self.prompts = []
                
            self.broadcaster.broadcast_event("mcp_capabilities_updated", {
                "name": self.name,
                "tools": [{"name": t.name, "description": t.description} for t in self.tools],
                "resources": [{"name": r.name, "description": r.description} for r in self.resources],
                "prompts": [{"name": p.name, "description": p.description} for p in self.prompts]
            })
                
            logger.info(f"Fetched capabilities for {self.name}: {len(self.tools)} tools, {len(self.resources)} resources, {len(self.prompts)} prompts")
            
        except Exception as e:
            logger.error(f"Failed to fetch capabilities for {self.name}: {e}")
            self.broadcaster.broadcast_event("mcp_capabilities_error", {
                "name": self.name,
                "error": str(e)
            })
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Call a tool on this MCP server."""
        if not self.session:
            return [types.TextContent(
                type="text",
                text=f"MCP client {self.name} is not connected"
            )]
        
        try:
            self.broadcaster.broadcast_event("tool_call_started", {
                "mcp": self.name,
                "tool": name,
                "arguments": arguments
            })
            
            result = await self.session.call_tool(name, arguments)
            
            self.broadcaster.broadcast_event("tool_call_completed", {
                "mcp": self.name,
                "tool": name,
                "success": True
            })
            
            return result.content if result else []
            
        except Exception as e:
            logger.error(f"Tool call failed for {self.name}.{name}: {e}")
            self.broadcaster.broadcast_event("tool_call_failed", {
                "mcp": self.name,
                "tool": name,
                "error": str(e)
            })
            return [types.TextContent(
                type="text",
                text=f"Tool call failed: {str(e)}"
            )]
    
    def is_running(self) -> bool:
        """Check if the MCP client is running."""
        return (self.process is not None and 
                self.process.poll() is None and 
                self.session is not None)
    
    async def health_check(self):
        """Perform a health check on the MCP client."""
        if not self.is_running():
            self.broadcaster.broadcast_event("mcp_health_check_failed", {
                "name": self.name,
                "reason": "not_running"
            })
            return False
        
        try:
            # Try to list tools as a health check
            await self.session.list_tools()
            self.last_health_check = time.time()
            return True
        except Exception as e:
            logger.warning(f"Health check failed for {self.name}: {e}")
            self.broadcaster.broadcast_event("mcp_health_check_failed", {
                "name": self.name,
                "reason": str(e)
            })
            return False

class MCPMiddleware:
    """Enhanced MCP Middleware with real-time feedback."""
    
    def __init__(self):
        self.server = Server("mcp-middleware")
        self.mcp_clients: Dict[str, MCPClient] = {}
        self.mcp_registry_file = os.path.join(os.path.dirname(__file__), "mcp_registry.json")
        self.mcp_discovery_dir = os.path.join(os.path.dirname(__file__), "mcps")
        self.broadcaster = EventBroadcaster()
        
        # Ensure discovery directory exists
        os.makedirs(self.mcp_discovery_dir, exist_ok=True)
        
        # Setup Flask app for SSE
        self.flask_app = Flask(__name__)
        CORS(self.flask_app)
        self._setup_flask_routes()
        
        # Setup MCP handlers
        self._setup_handlers()
        
        # Start health check task
        self._start_health_monitor()
        
    def _setup_flask_routes(self):
        """Setup Flask routes for SSE and status endpoints."""
        
        @self.flask_app.route('/events')
        def events():
            """SSE endpoint for real-time events."""
            def event_stream():
                client_queue = queue.Queue()
                self.broadcaster.add_client(client_queue)
                
                try:
                    while True:
                        try:
                            event = client_queue.get(timeout=30)  # 30 second timeout
                            yield f"data: {json.dumps(event)}\n\n"
                        except queue.Empty:
                            # Send heartbeat
                            yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': time.time()})}\n\n"
                except GeneratorExit:
                    self.broadcaster.remove_client(client_queue)
            
            return Response(event_stream(), mimetype='text/event-stream')
        
        @self.flask_app.route('/status')
        def status():
            """Get current status of all MCPs."""
            status_data = {}
            for name, client in self.mcp_clients.items():
                status_data[name] = {
                    "running": client.is_running(),
                    "tools": len(client.tools),
                    "resources": len(client.resources),
                    "prompts": len(client.prompts),
                    "last_health_check": client.last_health_check,
                    "command": client.command,
                    "args": client.args
                }
            
            return jsonify({
                "middleware_status": "running",
                "mcps": status_data,
                "total_mcps": len(self.mcp_clients),
                "active_sse_clients": len(self.broadcaster.clients)
            })
    
    def _start_health_monitor(self):
        """Start the health monitoring task."""
        def health_monitor():
            while True:
                try:
                    asyncio.run(self._perform_health_checks())
                    time.sleep(30)  # Check every 30 seconds
                except Exception as e:
                    logger.error(f"Health monitor error: {e}")
                    time.sleep(60)  # Wait longer on error
        
        health_thread = threading.Thread(target=health_monitor, daemon=True)
        health_thread.start()
    
    async def _perform_health_checks(self):
        """Perform health checks on all loaded MCPs."""
        for name, client in list(self.mcp_clients.items()):
            try:
                is_healthy = await client.health_check()
                if not is_healthy:
                    logger.warning(f"MCP {name} failed health check")
            except Exception as e:
                logger.error(f"Health check error for {name}: {e}")
    
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
                            "name": {"type": "string", "description": "Name identifier for the MCP"},
                            "command": {"type": "string", "description": "Command to run the MCP server"},
                            "args": {"type": "array", "items": {"type": "string"}, "description": "Arguments for the MCP server command", "default": []},
                            "env": {"type": "object", "description": "Environment variables for the MCP server", "default": {}}
                        },
                        "required": ["name", "command"]
                    }
                ),
                types.Tool(
                    name="unload_mcp",
                    description="Unload a dynamically loaded MCP server",
                    inputSchema={
                        "type": "object",
                        "properties": {"name": {"type": "string", "description": "Name identifier of the MCP to unload"}},
                        "required": ["name"]
                    }
                ),
                types.Tool(
                    name="list_loaded_mcps",
                    description="List all currently loaded MCP servers and their capabilities",
                    inputSchema={"type": "object", "properties": {}}
                ),
                types.Tool(
                    name="reload_mcp",
                    description="Reload a specific MCP server",
                    inputSchema={
                        "type": "object",
                        "properties": {"name": {"type": "string", "description": "Name identifier of the MCP to reload"}},
                        "required": ["name"]
                    }
                ),
                types.Tool(
                    name="discover_mcps",
                    description="Discover MCP servers in the discovery directory",
                    inputSchema={
                        "type": "object",
                        "properties": {"auto_load": {"type": "boolean", "description": "Automatically load discovered MCPs", "default": False}}
                    }
                ),
                types.Tool(
                    name="get_mcp_status",
                    description="Get detailed status of a specific MCP",
                    inputSchema={
                        "type": "object",
                        "properties": {"name": {"type": "string", "description": "Name identifier of the MCP"}},
                        "required": ["name"]
                    }
                ),
                types.Tool(
                    name="start_feedback_server",
                    description="Start the SSE feedback server for real-time updates",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "port": {"type": "integer", "description": "Port to run the feedback server on", "default": 5000}
                        }
                    }
                )
            ])
            
            # Add tools from loaded MCPs with prefixes
            for mcp_name, client in self.mcp_clients.items():
                if client.is_running():
                    for tool in client.tools:
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
            elif name == "start_feedback_server":
                return await self._start_feedback_server(arguments)
            
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
    
    async def _start_feedback_server(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Start the SSE feedback server."""
        port = arguments.get("port", 5000)
        
        def run_flask():
            self.flask_app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
        
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        
        self.broadcaster.broadcast_event("feedback_server_started", {
            "port": port,
            "endpoints": {
                "events": f"http://localhost:{port}/events",
                "status": f"http://localhost:{port}/status"
            }
        })
        
        return [types.TextContent(
            type="text",
            text=f"SSE feedback server started on port {port}. Access events at http://localhost:{port}/events and status at http://localhost:{port}/status"
        )]
    
    # Include all the other methods from the previous implementation
    # (load_mcp, unload_mcp, list_loaded_mcps, etc.)
    # ... [Previous methods would be included here]
    

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

