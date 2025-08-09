#!/bin/bash

# Enhanced startup script with VNC debugging
echo "🚀 Starting MCP Vibesbox Monitor with VNC debugging..."

# Start nginx
echo "📡 Starting nginx..."
nginx

# Start websockify with verbose logging and connection timeout settings
echo "🌐 Starting websockify with debug logging..."
websockify --verbose --timeout=300 --idle-timeout=300 6080 mcp-vibesbox-server:5901 &

# Wait a moment for websockify to initialize
sleep 3

# Start FastAPI on port 8001 (internal)
echo "🔧 Starting FastAPI backend..."
exec python -c "
import uvicorn
from app import app

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8001)
"
