#!/usr/bin/env python3
"""
MCP Vibesbox Server - Enhanced with Monitoring
Unified Shell + VNC GUI Automation with real-time operation logging
"""

import asyncio
import subprocess
from datetime import datetime
import os
import base64
import tempfile
import json
import requests
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
server = Server("mcp-vibesbox")

# Monitoring integration
class VibesboxMonitor:
    def __init__(self, monitor_host="mcp-vibesbox-monitor", monitor_port=8000):
        self.monitor_url = f"http://{monitor_host}:{monitor_port}"
        self.enabled = True
        
    def log_operation(self, 
                     operation: str, 
                     details: Dict[str, Any],
                     screenshot_before: Optional[str] = None,
                     screenshot_after: Optional[str] = None):
        """Log an operation to the monitoring system"""
        if not self.enabled:
            return
            
        try:
            operation_data = {
                "timestamp": datetime.now().isoformat(),
                "operation": operation,
                "details": details,
                "screenshot_before": screenshot_before,
                "screenshot_after": screenshot_after
            }
            
            # Send to monitor API (non-blocking)
            requests.post(
                f"{self.monitor_url}/api/operations",
                json=operation_data,
                timeout=1.0  # Quick timeout to not block operations
            )
            logger.info(f"Logged operation: {operation}")
            
        except Exception as e:
            logger.debug(f"Failed to log operation to monitor: {e}")
            # Don't fail the actual operation if monitoring fails

# Global monitor instance
monitor = VibesboxMonitor()

def run_vnc_command(command: str, display: str = ":1") -> subprocess.CompletedProcess:
    """Execute command in VNC environment with proper DISPLAY setting"""
    env = os.environ.copy()
    env["DISPLAY"] = display
    
    return subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        timeout=30,
        env=env
    )

def take_screenshot_base64(display: str = ":1") -> str:
    """Take screenshot and return as base64 encoded image, also save to screenshots folder"""
    # Generate timestamp for filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    screenshots_dir = "/workspace/vibes/screenshots"
    
    # Ensure screenshots directory exists
    os.makedirs(screenshots_dir, exist_ok=True)
    
    # Create permanent filename - UPDATED FOR 1920x1080
    permanent_filename = f"{screenshots_dir}/{timestamp}_vibesbox_1920x1080.png"
    
    # Take screenshot using ImageMagick
    env = os.environ.copy()
    env["DISPLAY"] = display
    
    try:
        # Capture screenshot to file
        result = subprocess.run([
            "import", "-window", "root", permanent_filename
        ], env=env, capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            raise Exception(f"Screenshot failed: {result.stderr}")
        
        # Read and encode as base64
        with open(permanent_filename, "rb") as f:
            screenshot_data = f.read()
            screenshot_b64 = base64.b64encode(screenshot_data).decode('utf-8')
        
        return screenshot_b64
        
    except Exception as e:
        logger.error(f"Screenshot error: {e}")
        raise Exception(f"Failed to take screenshot: {e}")

# Tool definitions with monitoring integration

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools"""
    return [
        Tool(
            name="run_command",
            description="Execute shell commands in the vibesbox environment with full container access",
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
        ),
        Tool(
            name="take_screenshot",
            description="Take a screenshot of the VNC desktop environment and return as viewable image",
            inputSchema={
                "type": "object", 
                "properties": {
                    "display": {
                        "type": "string",
                        "description": "VNC display number",
                        "default": ":1"
                    }
                }
            }
        ),
        Tool(
            name="click_desktop",
            description="Click at specific coordinates on the desktop",
            inputSchema={
                "type": "object",
                "properties": {
                    "x": {"type": "integer", "description": "X coordinate to click"},
                    "y": {"type": "integer", "description": "Y coordinate to click"},
                    "button": {"type": "integer", "description": "Mouse button (1=left, 2=middle, 3=right)", "default": 1},
                    "double_click": {"type": "boolean", "description": "Whether to double-click", "default": False},
                    "display": {"type": "string", "description": "VNC display number", "default": ":1"}
                },
                "required": ["x", "y"]
            }
        ),
        Tool(
            name="drag_mouse", 
            description="Drag from one coordinate to another (mouse down, move, mouse up)",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_x": {"type": "integer", "description": "Starting X coordinate"},
                    "start_y": {"type": "integer", "description": "Starting Y coordinate"},
                    "end_x": {"type": "integer", "description": "Ending X coordinate"},
                    "end_y": {"type": "integer", "description": "Ending Y coordinate"},
                    "button": {"type": "integer", "description": "Mouse button to drag with (1=left, 2=middle, 3=right)", "default": 1},
                    "display": {"type": "string", "description": "VNC display number", "default": ":1"}
                },
                "required": ["start_x", "start_y", "end_x", "end_y"]
            }
        ),
        Tool(
            name="type_text",
            description="Type text into the currently focused GUI element",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to type"},
                    "display": {"type": "string", "description": "VNC display number", "default": ":1"}
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="send_keys",
            description="Send keyboard combinations (Ctrl+C, Alt+Tab, Enter, etc.)",
            inputSchema={
                "type": "object", 
                "properties": {
                    "keys": {"type": "string", "description": "Key combination (e.g., 'ctrl+c', 'alt+Tab', 'Return', 'Escape')"},
                    "display": {"type": "string", "description": "VNC display number", "default": ":1"}
                },
                "required": ["keys"]
            }
        ),
        Tool(
            name="start_vnc_server",
            description="Start VNC server on specified display",
            inputSchema={
                "type": "object",
                "properties": {
                    "display": {"type": "string", "description": "Display number (e.g., ':1')", "default": ":1"},
                    "geometry": {"type": "string", "description": "Screen resolution", "default": "1920x1080"},
                    "password": {"type": "string", "description": "VNC password", "default": "vibes123"}
                }
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[Any]:
    """Handle tool calls with monitoring integration"""
    
    # Capture screenshot before operation for monitoring
    screenshot_before = None
    try:
        if name != "take_screenshot":  # Avoid infinite recursion
            screenshot_before = take_screenshot_base64(arguments.get("display", ":1"))
    except:
        pass  # Don't fail operation if screenshot fails
    
    try:
        if name == "run_command":
            return await handle_run_command(arguments, screenshot_before)
        elif name == "take_screenshot":
            return await handle_take_screenshot(arguments, screenshot_before)
        elif name == "click_desktop":
            return await handle_click_desktop(arguments, screenshot_before)
        elif name == "drag_mouse":
            return await handle_drag_mouse(arguments, screenshot_before)
        elif name == "type_text":
            return await handle_type_text(arguments, screenshot_before)
        elif name == "send_keys":
            return await handle_send_keys(arguments, screenshot_before)
        elif name == "start_vnc_server":
            return await handle_start_vnc_server(arguments, screenshot_before)
        else:
            raise ValueError(f"Unknown tool: {name}")
            
    except Exception as e:
        # Log error to monitor
        monitor.log_operation(
            operation=f"{name}_error",
            details={"error": str(e), "arguments": arguments},
            screenshot_before=screenshot_before
        )
        raise

async def handle_run_command(arguments: Dict[str, Any], screenshot_before: Optional[str]) -> List[Any]:
    """Handle run_command with monitoring"""
    command = arguments["command"]
    working_dir = arguments.get("working_dir", "/workspace/vibes")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=working_dir,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        output = f"STDOUT:\n{result.stdout}" if result.stdout else ""
        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}"
        
        output += f"\nEXIT CODE: {result.returncode}"
        
        # Log to monitor
        monitor.log_operation(
            operation="run_command",
            details={
                "command": command,
                "working_dir": working_dir,
                "exit_code": result.returncode,
                "stdout_length": len(result.stdout) if result.stdout else 0,
                "stderr_length": len(result.stderr) if result.stderr else 0
            },
            screenshot_before=screenshot_before
        )
        
        return [TextContent(type="text", text=output)]
        
    except subprocess.TimeoutExpired:
        error_msg = f"Command timed out after 30 seconds: {command}"
        monitor.log_operation(
            operation="run_command_timeout",
            details={"command": command, "working_dir": working_dir},
            screenshot_before=screenshot_before
        )
        return [TextContent(type="text", text=error_msg)]

async def handle_take_screenshot(arguments: Dict[str, Any], screenshot_before: Optional[str]) -> List[Any]:
    """Handle take_screenshot with monitoring"""
    display = arguments.get("display", ":1")
    
    try:
        screenshot_b64 = take_screenshot_base64(display)
        
        # Log to monitor (but don't include the screenshot to avoid recursion)
        monitor.log_operation(
            operation="take_screenshot",
            details={"display": display, "resolution": "1920x1080"},
            # Don't include screenshots to avoid circular logging
        )
        
        return [
            TextContent(type="text", text=f"📸 Screenshot captured from display {display}"),
            ImageContent(type="image", data=screenshot_b64, mimeType="image/png")
        ]
        
    except Exception as e:
        error_msg = f"Failed to take screenshot: {e}"
        monitor.log_operation(
            operation="take_screenshot_error",
            details={"display": display, "error": str(e)}
        )
        return [TextContent(type="text", text=error_msg)]

async def handle_click_desktop(arguments: Dict[str, Any], screenshot_before: Optional[str]) -> List[Any]:
    """Handle click_desktop with monitoring"""
    x = arguments["x"]
    y = arguments["y"]
    button = arguments.get("button", 1)
    double_click = arguments.get("double_click", False)
    display = arguments.get("display", ":1")
    
    try:
        click_type = "double" if double_click else "single"
        click_command = f"xdotool mousemove {x} {y} click{'click' if double_click else ''} {button}"
        
        result = run_vnc_command(click_command, display)
        
        # Capture screenshot after click
        screenshot_after = None
        try:
            screenshot_after = take_screenshot_base64(display)
        except:
            pass
        
        # Log to monitor
        monitor.log_operation(
            operation="click_desktop",
            details={
                "x": x, "y": y, "button": button, 
                "double_click": double_click, "display": display
            },
            screenshot_before=screenshot_before,
            screenshot_after=screenshot_after
        )
        
        if result.returncode == 0:
            return [TextContent(type="text", text=f"🖱️ {click_type.title()} clicked at ({x}, {y}) with button {button}")]
        else:
            error_msg = f"Click failed: {result.stderr}"
            return [TextContent(type="text", text=error_msg)]
            
    except Exception as e:
        error_msg = f"Failed to click: {e}"
        monitor.log_operation(
            operation="click_desktop_error",
            details={"x": x, "y": y, "error": str(e)},
            screenshot_before=screenshot_before
        )
        return [TextContent(type="text", text=error_msg)]

async def handle_drag_mouse(arguments: Dict[str, Any], screenshot_before: Optional[str]) -> List[Any]:
    """Handle drag_mouse with monitoring - enhanced timing"""
    start_x = arguments["start_x"]
    start_y = arguments["start_y"] 
    end_x = arguments["end_x"]
    end_y = arguments["end_y"]
    button = arguments.get("button", 1)
    display = arguments.get("display", ":1")
    
    try:
        # Enhanced drag sequence with optimized timing
        commands = [
            f"xdotool mousemove {start_x} {start_y}",
            "sleep 0.1",  # Brief pause at start position
            f"xdotool mousedown {button}",
            "sleep 0.15", # Longer pause after mousedown
            f"xdotool mousemove {end_x} {end_y}",
            "sleep 0.05", # Brief pause at end position  
            f"xdotool mouseup {button}"
        ]
        
        drag_command = " && ".join(commands)
        result = run_vnc_command(drag_command, display)
        
        # Capture screenshot after drag
        screenshot_after = None
        try:
            screenshot_after = take_screenshot_base64(display)
        except:
            pass
        
        # Log to monitor
        monitor.log_operation(
            operation="drag_mouse",
            details={
                "start_x": start_x, "start_y": start_y,
                "end_x": end_x, "end_y": end_y,
                "button": button, "display": display
            },
            screenshot_before=screenshot_before,
            screenshot_after=screenshot_after
        )
        
        if result.returncode == 0:
            return [TextContent(type="text", text=f"🖱️ Dragged from ({start_x}, {start_y}) to ({end_x}, {end_y}) with button {button}")]
        else:
            error_msg = f"Drag failed: {result.stderr}"
            return [TextContent(type="text", text=error_msg)]
            
    except Exception as e:
        error_msg = f"Failed to drag: {e}"
        monitor.log_operation(
            operation="drag_mouse_error", 
            details={
                "start_x": start_x, "start_y": start_y,
                "end_x": end_x, "end_y": end_y, 
                "error": str(e)
            },
            screenshot_before=screenshot_before
        )
        return [TextContent(type="text", text=error_msg)]

async def handle_type_text(arguments: Dict[str, Any], screenshot_before: Optional[str]) -> List[Any]:
    """Handle type_text with monitoring"""
    text = arguments["text"]
    display = arguments.get("display", ":1")
    
    try:
        # Escape special characters for xdotool
        escaped_text = text.replace("'", "\\'").replace('"', '\\"')
        type_command = f"xdotool type '{escaped_text}'"
        
        result = run_vnc_command(type_command, display)
        
        # Capture screenshot after typing
        screenshot_after = None
        try:
            screenshot_after = take_screenshot_base64(display)
        except:
            pass
        
        # Log to monitor (truncate long text for readability)
        display_text = text[:100] + "..." if len(text) > 100 else text
        monitor.log_operation(
            operation="type_text",
            details={
                "text": display_text, "text_length": len(text), 
                "display": display
            },
            screenshot_before=screenshot_before,
            screenshot_after=screenshot_after
        )
        
        if result.returncode == 0:
            return [TextContent(type="text", text=f"⌨️ Typed text: {display_text}")]
        else:
            error_msg = f"Type failed: {result.stderr}"
            return [TextContent(type="text", text=error_msg)]
            
    except Exception as e:
        error_msg = f"Failed to type: {e}"
        monitor.log_operation(
            operation="type_text_error",
            details={"text": text[:100], "error": str(e)},
            screenshot_before=screenshot_before
        )
        return [TextContent(type="text", text=error_msg)]

async def handle_send_keys(arguments: Dict[str, Any], screenshot_before: Optional[str]) -> List[Any]:
    """Handle send_keys with monitoring"""
    keys = arguments["keys"]
    display = arguments.get("display", ":1")
    
    try:
        key_command = f"xdotool key {keys}"
        result = run_vnc_command(key_command, display)
        
        # Capture screenshot after keys
        screenshot_after = None
        try:
            screenshot_after = take_screenshot_base64(display)
        except:
            pass
        
        # Log to monitor
        monitor.log_operation(
            operation="send_keys",
            details={"keys": keys, "display": display},
            screenshot_before=screenshot_before,
            screenshot_after=screenshot_after
        )
        
        if result.returncode == 0:
            return [TextContent(type="text", text=f"⌨️ Sent keys: {keys}")]
        else:
            error_msg = f"Send keys failed: {result.stderr}"
            return [TextContent(type="text", text=error_msg)]
            
    except Exception as e:
        error_msg = f"Failed to send keys: {e}"
        monitor.log_operation(
            operation="send_keys_error",
            details={"keys": keys, "error": str(e)},
            screenshot_before=screenshot_before
        )
        return [TextContent(type="text", text=error_msg)]

async def handle_start_vnc_server(arguments: Dict[str, Any], screenshot_before: Optional[str]) -> List[Any]:
    """Handle start_vnc_server with monitoring"""
    display = arguments.get("display", ":1")
    geometry = arguments.get("geometry", "1920x1080")
    password = arguments.get("password", "vibes123")
    
    try:
        # Kill existing server
        kill_result = subprocess.run(
            f"vncserver -kill {display}",
            shell=True, capture_output=True, text=True
        )
        
        # Start new server
        start_command = f"vncserver {display} -geometry {geometry} -depth 24"
        start_result = subprocess.run(
            start_command,
            shell=True, capture_output=True, text=True
        )
        
        # Log to monitor
        monitor.log_operation(
            operation="start_vnc_server",
            details={
                "display": display, "geometry": geometry,
                "success": start_result.returncode == 0
            },
            screenshot_before=screenshot_before
        )
        
        if start_result.returncode == 0:
            return [TextContent(type="text", text=f"🖥️ VNC server started on {display} with resolution {geometry}")]
        else:
            error_msg = f"VNC server start failed: {start_result.stderr}"
            return [TextContent(type="text", text=error_msg)]
            
    except Exception as e:
        error_msg = f"Failed to start VNC server: {e}"
        monitor.log_operation(
            operation="start_vnc_server_error",
            details={"display": display, "error": str(e)},
            screenshot_before=screenshot_before
        )
        return [TextContent(type="text", text=error_msg)]

async def main():
    """Run the MCP server"""
    logger.info("Starting Enhanced MCP Vibesbox Server with monitoring...")
    async with stdio_server() as streams:
        await server.run(streams[0], streams[1], server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
