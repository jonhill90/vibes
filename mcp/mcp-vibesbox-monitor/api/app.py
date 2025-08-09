#!/usr/bin/env python3

import os
import json
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import socket

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

# API Routes
@app.get("/api/status")
async def get_status():
    """Get system status"""
    return system_status

@app.get("/api/operations")
async def get_operations(limit: int = 50):
    """Get recent operations"""
    return operation_logs[-limit:]

@app.get("/api/operations/{operation_id}")
async def get_operation(operation_id: int):
    """Get specific operation details"""
    if operation_id >= len(operation_logs):
        raise HTTPException(status_code=404, detail="Operation not found")
    return operation_logs[operation_id]

@app.post("/api/operations")
async def add_operation(operation: OperationLog):
    """Add new operation log (called by vibesbox server)"""
    operation_logs.append(operation)
    system_status.total_operations += 1
    system_status.last_operation = operation.timestamp
    
    # Broadcast to connected websockets
    await broadcast_to_websockets({
        "type": "new_operation",
        "operation": operation.dict()
    })
    
    return {"status": "logged"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates"""
    await websocket.accept()
    connected_websockets.append(websocket)
    
    try:
        # Send initial status
        await websocket.send_json({
            "type": "status",
            "data": system_status.dict()
        })
        
        # Keep connection alive
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connected_websockets.remove(websocket)

async def broadcast_to_websockets(message: Dict[str, Any]):
    """Broadcast message to all connected websockets"""
    for websocket in connected_websockets.copy():
        try:
            await websocket.send_json(message)
        except:
            connected_websockets.remove(websocket)

# Health check for vibesbox server
async def check_vibesbox_connection():
    """Periodically check connection to vibesbox server"""
    vibesbox_host = os.getenv("VIBESBOX_SERVER_HOST", "mcp-vibesbox-server")
    vibesbox_port = int(os.getenv("VIBESBOX_SERVER_PORT", "5901"))
    
    while True:
        try:
            # Test socket connection to VNC server
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((vibesbox_host, vibesbox_port))
            sock.close()
            
            if result == 0:
                system_status.vibesbox_connected = True
            else:
                system_status.vibesbox_connected = False
                logger.warning(f"Cannot connect to vibesbox server at {vibesbox_host}:{vibesbox_port}")
        except Exception as e:
            system_status.vibesbox_connected = False
            logger.warning(f"Cannot connect to vibesbox server at {vibesbox_host}: {e}")
        
        await asyncio.sleep(10)  # Check every 10 seconds

@app.on_event("startup")
async def startup_event():
    """Start background tasks"""
    asyncio.create_task(check_vibesbox_connection())
    logger.info("MCP Vibesbox Monitor started")

# Serve static frontend files
static_dir = Path("/app/static")
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def serve_frontend():
    """Serve the frontend application"""
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    else:
        # Return simple HTML if frontend not built yet
        return HTMLResponse("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>MCP Vibesbox Monitor</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    max-width: 1200px; 
                    margin: 0 auto; 
                    padding: 20px;
                    background: #f5f5f5;
                }
                .header { 
                    background: #2c3e50; 
                    color: white; 
                    padding: 20px; 
                    border-radius: 8px;
                    margin-bottom: 20px;
                }
                .status-card { 
                    background: white; 
                    padding: 20px; 
                    border-radius: 8px; 
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    margin-bottom: 20px;
                }
                .operations-list { 
                    background: white; 
                    border-radius: 8px; 
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .operation-item { 
                    padding: 15px; 
                    border-bottom: 1px solid #eee; 
                }
                .timestamp { 
                    color: #666; 
                    font-size: 0.9em; 
                }
                .online { color: #27ae60; }
                .offline { color: #e74c3c; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔍 MCP Vibesbox Monitor</h1>
                <p>Real-time monitoring for Claude's vibesbox operations</p>
            </div>
            
            <div class="status-card">
                <h2>System Status</h2>
                <p id="connection-status">⏳ Checking connection...</p>
                <p id="operation-count">Operations logged: <span id="op-count">0</span></p>
                <p id="last-operation">Last operation: <span id="last-op">None</span></p>
            </div>
            
            <div class="operations-list">
                <h2 style="padding: 20px 20px 0;">Recent Operations</h2>
                <div id="operations-container">
                    <div class="operation-item">
                        <em>Operations will appear here when Claude interacts with the vibesbox...</em>
                    </div>
                </div>
            </div>

            <script>
                // WebSocket connection for real-time updates
                const ws = new WebSocket(`ws://${window.location.host}/ws`);
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    
                    if (data.type === 'status') {
                        updateStatus(data.data);
                    } else if (data.type === 'new_operation') {
                        addOperation(data.operation);
                    }
                };
                
                function updateStatus(status) {
                    const connectionEl = document.getElementById('connection-status');
                    const countEl = document.getElementById('op-count');
                    const lastOpEl = document.getElementById('last-op');
                    
                    connectionEl.innerHTML = status.vibesbox_connected 
                        ? '<span class="online">🟢 Connected to Vibesbox</span>'
                        : '<span class="offline">🔴 Vibesbox Offline</span>';
                    
                    countEl.textContent = status.total_operations;
                    lastOpEl.textContent = status.last_operation || 'None';
                }
                
                function addOperation(operation) {
                    const container = document.getElementById('operations-container');
                    const opDiv = document.createElement('div');
                    opDiv.className = 'operation-item';
                    opDiv.innerHTML = `
                        <strong>${operation.operation}</strong>
                        <span class="timestamp">${new Date(operation.timestamp).toLocaleString()}</span>
                        <br>
                        <small>${JSON.stringify(operation.details)}</small>
                    `;
                    container.insertBefore(opDiv, container.firstChild);
                    
                    // Keep only last 20 operations visible
                    while (container.children.length > 20) {
                        container.removeChild(container.lastChild);
                    }
                }
                
                // Fetch initial data
                fetch('/api/status')
                    .then(r => r.json())
                    .then(updateStatus);
                
                fetch('/api/operations?limit=10')
                    .then(r => r.json())
                    .then(operations => {
                        operations.reverse().forEach(addOperation);
                    });
            </script>
        </body>
        </html>
        """)

if __name__ == "__main__":
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    uvicorn.run(app, host=host, port=port)

@app.post("/api/screenshot")
async def take_screenshot():
    """Take a screenshot of the vibesbox"""
    try:
        # This would call the vibesbox server to take a screenshot
        # For now, return a placeholder response
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "screenshot": None,  # Base64 encoded screenshot would go here
            "message": "Screenshot functionality needs vibesbox integration"
        }
    except Exception as e:
        logger.error(f"Error taking screenshot: {e}")
        raise HTTPException(status_code=500, detail=str(e))
