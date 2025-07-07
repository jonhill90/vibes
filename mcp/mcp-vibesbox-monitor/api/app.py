#!/usr/bin/env python3

import os
import json
import asyncio
import logging
import subprocess
import base64
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import requests

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="MCP Vibesbox Monitor", version="1.0.0")

# Data models
class OperationLog(BaseModel):
    timestamp: datetime
    operation: str
    details: Dict[str, Any]
    screenshot_before: str = None
    screenshot_after: str = None

class SystemStatus(BaseModel):
    vibesbox_connected: bool
    last_operation: datetime = None
    total_operations: int = 0

# In-memory storage (could be replaced with database)
operation_logs: List[OperationLog] = []
system_status = SystemStatus(vibesbox_connected=False, total_operations=0)
connected_websockets: List[WebSocket] = []

# Data directory
DATA_DIR = Path("/app/data")
DATA_DIR.mkdir(exist_ok=True)

async def broadcast_to_websockets(data: dict):
    """Broadcast data to all connected WebSocket clients"""
    if connected_websockets:
        disconnected = []
        for websocket in connected_websockets:
            try:
                await websocket.send_json(data)
            except Exception as e:
                logger.error(f"Error sending to websocket: {e}")
                disconnected.append(websocket)
        
        # Remove disconnected websockets
        for ws in disconnected:
            connected_websockets.remove(ws)

def check_vibesbox_connection():
    """Check if vibesbox server is accessible"""
    try:
        # Try to execute a simple command in the vibesbox container
        result = subprocess.run(
            ["docker", "exec", "mcp-vibesbox-server", "echo", "connection_test"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except Exception as e:
        logger.error(f"Vibesbox connection check failed: {e}")
        return False

def take_vibesbox_screenshot():
    """Take a screenshot from the vibesbox server"""
    try:
        # Execute the screenshot command in the vibesbox container
        # This calls the same function that the MCP server uses
        cmd = [
            "docker", "exec", "mcp-vibesbox-server", 
            "python3", "-c", 
            """
import subprocess
import tempfile
import base64
import os
from datetime import datetime

def run_vnc_command(command, display=':1'):
    env = os.environ.copy()
    env['DISPLAY'] = display
    return subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        timeout=30,
        env=env
    )

# Generate timestamp for filename
timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
screenshots_dir = '/workspace/vibes/screenshots'

# Ensure screenshots directory exists
os.makedirs(screenshots_dir, exist_ok=True)

# Create permanent filename
permanent_filename = f'{screenshots_dir}/{timestamp}_vibesbox_monitor_1920x1080.png'

with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
    # Take screenshot using ImageMagick
    result = run_vnc_command(f'import -window root {tmp_file.name}', ':1')
    
    if result.returncode != 0:
        raise Exception(f'Screenshot failed: {result.stderr}')
    
    # Copy to permanent location
    import shutil
    shutil.copy2(tmp_file.name, permanent_filename)
    print(f'📸 Screenshot saved to: {permanent_filename}')
    
    # Convert to base64
    with open(tmp_file.name, 'rb') as img_file:
        image_data = img_file.read()
        base64_string = base64.b64encode(image_data).decode('utf-8')
        
    print(base64_string)
"""
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            raise Exception(f"Screenshot command failed: {result.stderr}")
        
        # Extract base64 from stdout (last line should be the base64 string)
        lines = result.stdout.strip().split('\n')
        base64_image = lines[-1]  # Last line should be the base64 encoded image
        
        # Validate it's actually base64
        try:
            base64.b64decode(base64_image)
            return base64_image
        except Exception:
            # If the last line isn't valid base64, look for it in the output
            for line in reversed(lines):
                try:
                    base64.b64decode(line)
                    return line
                except:
                    continue
            raise Exception("No valid base64 image found in output")
            
    except Exception as e:
        logger.error(f"Error taking vibesbox screenshot: {e}")
        raise e

# API Routes
@app.get("/api/status")
async def get_status():
    """Get system status"""
    # Update vibesbox connection status
    system_status.vibesbox_connected = check_vibesbox_connection()
    return system_status

@app.get("/api/operations")
async def get_operations():
    """Get operation log history"""
    return {"operations": operation_logs}

@app.post("/api/screenshot")
async def take_screenshot():
    """Take a screenshot of the vibesbox"""
    try:
        # Check if vibesbox is connected first
        if not check_vibesbox_connection():
            raise HTTPException(status_code=503, detail="Vibesbox server not accessible")
        
        # Take the actual screenshot
        base64_image = take_vibesbox_screenshot()
        
        # Create operation log entry
        operation = OperationLog(
            timestamp=datetime.now(),
            operation="screenshot",
            details={"source": "monitor_manual", "resolution": "1920x1080"},
            screenshot_after=base64_image
        )
        
        operation_logs.append(operation)
        system_status.last_operation = operation.timestamp
        system_status.total_operations += 1
        
        # Broadcast to WebSocket clients
        await broadcast_to_websockets({
            "type": "operation",
            "data": {
                "timestamp": operation.timestamp.isoformat(),
                "operation": "screenshot",
                "details": operation.details,
                "screenshot": base64_image
            }
        })
        
        return {
            "status": "success",
            "timestamp": operation.timestamp.isoformat(),
            "screenshot": base64_image,
            "message": "Screenshot captured from vibesbox desktop"
        }
        
    except Exception as e:
        logger.error(f"Error taking screenshot: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    connected_websockets.append(websocket)
    
    try:
        # Send initial status
        await websocket.send_json({
            "type": "status",
            "data": {
                "vibesbox_connected": check_vibesbox_connection(),
                "total_operations": system_status.total_operations
            }
        })
        
        # Keep