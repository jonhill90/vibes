#!/bin/bash
set -e

# Start MCP server in background on port 8051
python -m src.mcp_server &
MCP_PID=$!

# Start FastAPI server on port 8000 (foreground)
exec uvicorn src.main:app --host 0.0.0.0 --port "${API_PORT:-8000}"
