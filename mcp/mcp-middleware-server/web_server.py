#!/usr/bin/env python3
"""
MCP Middleware Web Server with SSE

Runs as a persistent web service that provides MCP over HTTP/SSE.
Enables dynamic MCP loading with persistent state.
"""

import json
import logging
import os
import subprocess
import sys
import threading
import time
from typing import Any, Dict, List, Optional
from flask import Flask, Response, jsonify, request
from flask_cors import CORS
import queue

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-middleware-web")

class MCPMiddlewareWeb:
    """Web-based MCP Middleware for persistent dynamic loading."""
    
    def __init__(self):
        self.loaded_mcps = {}
        self.mcp_registry_file = os.environ.get("REGISTRY_FILE", "/app/data/mcp_registry.json")
        self.mcp_discovery_dir = os.environ.get("MCP_DISCOVERY_DIR", "/app/mcps")
        
        # Flask app for SSE
        self.flask_app = Flask(__name__)
        CORS(self.flask_app)
        self.event_queue = queue.Queue()
        self._setup_flask_routes()
        
        # Load existing MCPs (synchronously)
        self._load_registry()
    
    def _setup_flask_routes(self):
        """Set up Flask routes for SSE and MCP endpoints."""
        
        @self.flask_app.route('/mcp/claude/sse/<user_id>')
        def sse_endpoint(user_id):
            """SSE endpoint for MCP communication."""
            def event_stream():
                while True:
                    try:
                        # Send heartbeat
                        yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
                        time.sleep(30)
                    except GeneratorExit:
                        break
            
            return Response(event_stream(), mimetype='text/plain')
        
        @self.flask_app.route('/api/tools', methods=['GET'])
        def list_tools():
            """List available tools."""
            tools = [
                {
                    "name": "load_mcp",
                    "description": "Load a new MCP server dynamically",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Name identifier for the MCP"},
                            "command": {"type": "string", "description": "Command to run the MCP server"},
                            "args": {"type": "array", "items": {"type": "string"}, "default": []},
                            "env": {"type": "object", "default": {}}
                        },
                        "required": ["name", "command"]
                    }
                },
                {
                    "name": "list_loaded_mcps",
                    "description": "List all currently loaded MCP servers",
                    "inputSchema": {"type": "object", "properties": {}}
                },
                {
                    "name": "get_mcp_status", 
                    "description": "Get detailed status of a specific MCP",
                    "inputSchema": {
                        "type": "object",
                        "properties": {"name": {"type": "string"}},
                        "required": ["name"]
                    }
                }
            ]
            return jsonify({"tools": tools})
        
        @self.flask_app.route('/api/call_tool', methods=['POST'])
        def call_tool():
            """Handle tool calls."""
            data = request.json
            name = data.get("name")
            arguments = data.get("arguments", {})
            
            if name == "load_mcp":
                result = self._load_mcp(arguments)
            elif name == "list_loaded_mcps":
                result = self._list_loaded_mcps()
            elif name == "get_mcp_status":
                result = self._get_mcp_status(arguments)
            else:
                result = {"error": f"Unknown tool: {name}"}
            
            return jsonify({"result": result})
        
        @self.flask_app.route('/health', methods=['GET'])
        def health():
            """Health check endpoint."""
            return jsonify({
                "status": "healthy",
                "loaded_mcps": len(self.loaded_mcps),
                "service": "mcp-middleware"
            })
    
    def _load_mcp(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Load a new MCP server dynamically."""
        name = arguments["name"]
        command = arguments["command"]
        args = arguments.get("args", [])
        env = arguments.get("env", {})
        
        if name in self.loaded_mcps:
            return {"error": f"MCP '{name}' is already loaded"}
        
        try:
            # Store MCP info
            self.loaded_mcps[name] = {
                "command": command,
                "args": args,
                "env": env,
                "status": "loaded"
            }
            
            # Save to registry
            self._save_registry()
            
            logger.info(f"Loaded MCP '{name}': {command} {args}")
            return {"success": f"MCP '{name}' loaded successfully"}
            
        except Exception as e:
            logger.error(f"Failed to load MCP '{name}': {e}")
            return {"error": f"Failed to load MCP '{name}': {str(e)}"}
    
    def _list_loaded_mcps(self) -> Dict[str, Any]:
        """List all currently loaded MCP servers."""
        if not self.loaded_mcps:
            return {"mcps": [], "message": "No MCPs are currently loaded"}
        
        mcps = []
        for name, info in self.loaded_mcps.items():
            mcps.append({
                "name": name,
                "command": info["command"],
                "args": info["args"],
                "status": info["status"]
            })
        
        return {"mcps": mcps, "count": len(mcps)}
    
    def _get_mcp_status(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed status of a specific MCP."""
        name = arguments["name"]
        
        if name not in self.loaded_mcps:
            return {"error": f"MCP '{name}' is not loaded"}
        
        info = self.loaded_mcps[name]
        return {
            "name": name,
            "command": info["command"],
            "args": info["args"],
            "env": info["env"],
            "status": info["status"]
        }
    
    def _save_registry(self):
        """Save the current MCP registry to file."""
        try:
            os.makedirs(os.path.dirname(self.mcp_registry_file), exist_ok=True)
            with open(self.mcp_registry_file, "w") as f:
                json.dump(self.loaded_mcps, f, indent=2)
            logger.info(f"Registry saved with {len(self.loaded_mcps)} MCPs")
        except Exception as e:
            logger.error(f"Failed to save registry: {e}")
    
    def _load_registry(self):
        """Load MCP registry from file if it exists."""
        if os.path.exists(self.mcp_registry_file):
            try:
                with open(self.mcp_registry_file, "r") as f:
                    self.loaded_mcps = json.load(f)
                logger.info(f"Loaded {len(self.loaded_mcps)} MCPs from registry")
            except Exception as e:
                logger.error(f"Failed to load registry: {e}")
    
    def run(self):
        """Run the web server."""
        logger.info("Starting MCP Middleware Web Server on port 5000")
        logger.info(f"Health check available at http://localhost:5000/health")
        logger.info(f"SSE endpoint available at http://localhost:5000/mcp/claude/sse/vibes-user")
        self.flask_app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)

if __name__ == "__main__":
    middleware = MCPMiddlewareWeb()
    middleware.run()
