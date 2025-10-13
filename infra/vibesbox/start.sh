#!/bin/sh
set -e

# Vibesbox MCP Server Startup Script
# Starts the FastMCP HTTP server for secure command execution

echo "=========================================="
echo "Starting Vibesbox MCP Server..."
echo "=========================================="

# Run MCP server (includes FastMCP HTTP server on port 8000)
# Pattern from: infra/task-manager/backend/start.sh
# Note: FastMCP handles HTTP server internally, no separate uvicorn needed
exec python src/mcp_server.py
