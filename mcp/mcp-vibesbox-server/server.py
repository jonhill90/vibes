#!/usr/bin/env python3
"""
MCP Vibesbox Server - Unified Shell + VNC GUI Automation

Gives Claude the ability to run shell commands AND control GUI environments
in containerized desktop environments with visual feedback.
"""

import asyncio
import subprocess
from datetime import datetime
import os
import base64
import tempfile
from pathlib import Path
from typing import Any, Dict, List

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent

# Initialize MCP server
server = Server("mcp-vibesbox")

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
    
    # Create permanent filename
    permanent_filename = f"{screenshots_dir}/{timestamp}_vibesbox_1024x768.png"
    
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
        try:
            # Take screenshot using ImageMagick
            result = run_vnc_command(f"import -window root {tmp_file.name}", display)
            
            if result.returncode != 0:
                raise Exception(f"Screenshot failed: {result.stderr}")
            
            # Copy to permanent location
            import shutil
            shutil.copy2(tmp_file.name, permanent_filename)
            print(f"📸 Screenshot saved to: {permanent_filename}")
            
            # Convert to base64
            with open(tmp_file.name, 'rb') as img_file:
                image_data = img_file.read()
                base64_string = base64.b64encode(image_data).decode('utf-8')
                
            return base64_string
            
        finally:
            # Clean up temp file
            if os.path.exists(tmp_file.name):
                os.unlink(tmp_file.name)

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available tools for Claude to use"""
    return [
        Tool(
            name="run_command",
            description="Execute shell commands in the vibesbox environment",
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
        ),
        Tool(
            name="take_screenshot",
            description="Take a screenshot of the current desktop environment and return as viewable image",
            inputSchema={
                "type": "object",
                "properties": {
                    "display": {
                        "type": "string",
                        "description": "VNC display number",
                        "default": ":1"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="click_desktop",
            description="Click at specific coordinates on the desktop",
            inputSchema={
                "type": "object",
                "properties": {
                    "x": {
                        "type": "integer",
                        "description": "X coordinate to click"
                    },
                    "y": {
                        "type": "integer", 
                        "description": "Y coordinate to click"
                    },
                    "button": {
                        "type": "integer",
                        "description": "Mouse button (1=left, 2=middle, 3=right)",
                        "default": 1
                    },
                    "double_click": {
                        "type": "boolean",
                        "description": "Whether to double-click",
                        "default": False
                    },
                    "display": {
                        "type": "string",
                        "description": "VNC display number",
                        "default": ":1"
                    }
                },
                "required": ["x", "y"]
            }
        ),
        Tool(
            name="type_text",
            description="Type text into the currently focused GUI element",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to type"
                    },
                    "display": {
                        "type": "string",
                        "description": "VNC display number",
                        "default": ":1"
                    }
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
                    "keys": {
                        "type": "string",
                        "description": "Key combination (e.g., 'ctrl+c', 'alt+Tab', 'Return', 'Escape')"
                    },
                    "display": {
                        "type": "string",
                        "description": "VNC display number",
                        "default": ":1"
                    }
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
                    "display": {
                        "type": "string",
                        "description": "Display number (e.g., ':1')",
                        "default": ":1"
                    },
                    "geometry": {
                        "type": "string",
                        "description": "Screen resolution",
                        "default": "1024x768"
                    },
                    "password": {
                        "type": "string",
                        "description": "VNC password",
                        "default": "vibes123"
                    }
                },
                "required": []
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent | ImageContent]:
    """Handle tool calls from Claude"""
    
    if name == "run_command":
        command = arguments["command"]
        working_dir = arguments.get("working_dir", "/workspace")
        
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
    
    elif name == "take_screenshot":
        display = arguments.get("display", ":1")
        
        try:
            base64_image = take_screenshot_base64(display)
            
            return [
                TextContent(type="text", text=f"📸 Screenshot captured from display {display}"),
                ImageContent(
                    type="image",
                    data=base64_image,
                    mimeType="image/png"
                )
            ]
            
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Screenshot failed: {str(e)}")]
    
    elif name == "click_desktop":
        x = arguments["x"]
        y = arguments["y"]
        button = arguments.get("button", 1)
        double_click = arguments.get("double_click", False)
        display = arguments.get("display", ":1")
        
        try:
            # Move mouse to coordinates
            result1 = run_vnc_command(f"xdotool mousemove {x} {y}", display)
            if result1.returncode != 0:
                return [TextContent(type="text", text=f"❌ Mouse move failed: {result1.stderr}")]
            
            # Perform click
            if double_click:
                click_cmd = f"xdotool click --repeat 2 {button}"
            else:
                click_cmd = f"xdotool click {button}"
                
            result2 = run_vnc_command(click_cmd, display)
            if result2.returncode != 0:
                return [TextContent(type="text", text=f"❌ Click failed: {result2.stderr}")]
            
            click_type = "double-clicked" if double_click else "clicked"
            return [TextContent(type="text", text=f"🖱️ {click_type} at ({x}, {y}) with button {button} on display {display}")]
            
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Click operation failed: {str(e)}")]
    
    elif name == "type_text":
        text = arguments["text"]
        display = arguments.get("display", ":1")
        
        try:
            # Escape special characters for shell
            escaped_text = text.replace("'", "'\"'\"'")
            result = run_vnc_command(f"xdotool type '{escaped_text}'", display)
            
            if result.returncode != 0:
                return [TextContent(type="text", text=f"❌ Typing failed: {result.stderr}")]
            
            return [TextContent(type="text", text=f"⌨️ Typed '{text}' on display {display}")]
            
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Typing failed: {str(e)}")]
    
    elif name == "send_keys":
        keys = arguments["keys"]
        display = arguments.get("display", ":1")
        
        try:
            result = run_vnc_command(f"xdotool key {keys}", display)
            
            if result.returncode != 0:
                return [TextContent(type="text", text=f"❌ Key combination failed: {result.stderr}")]
            
            return [TextContent(type="text", text=f"🔤 Sent key combination '{keys}' on display {display}")]
            
        except Exception as e:
            return [TextContent(type="text", text=f"❌ Key combination failed: {str(e)}")]
    
    elif name == "start_vnc_server":
        display = arguments.get("display", ":1")
        geometry = arguments.get("geometry", "1024x768")
        password = arguments.get("password", "vibes123")
        
        try:
            # Create VNC directory
            os.makedirs(os.path.expanduser("~/.vnc"), exist_ok=True)
            
            # Set password
            passwd_result = subprocess.run(
                f"echo '{password}' | vncpasswd -f > ~/.vnc/passwd && chmod 600 ~/.vnc/passwd",
                shell=True,
                capture_output=True,
                text=True
            )
            
            if passwd_result.returncode != 0:
                return [TextContent(type="text", text=f"❌ VNC password setup failed: {passwd_result.stderr}")]
            
            # Start VNC server
            vnc_result = subprocess.run(
                f"vncserver {display} -geometry {geometry} -depth 24",
                shell=True,
                capture_output=True,
                text=True
            )
            
            output = f"🖥️ VNC server started on display {display}\n"
            output += f"Resolution: {geometry}\n"
            output += f"Port: {5900 + int(display[1:])}\n"
            
            if vnc_result.stdout:
                output += f"Output: {vnc_result.stdout}\n"
            if vnc_result.stderr:
                output += f"Messages: {vnc_result.stderr}\n"
            
            return [TextContent(type="text", text=output)]
            
        except Exception as e:
            return [TextContent(type="text", text=f"❌ VNC server start failed: {str(e)}")]
    
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
