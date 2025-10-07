#!/bin/bash
# Source: infra/task-manager/backend/start.sh
# Pattern: Multi-process startup script for Docker container
# Extracted: 2025-10-07
# Relevance: 10/10 - Shows how to run both MCP server and FastAPI in one container

set -e

# Start MCP server in background on port 8051
python -m src.mcp_server &
MCP_PID=$!

# Start FastAPI server on port 8000 (foreground)
# Using exec ensures signals (SIGTERM) are properly forwarded
exec uvicorn src.main:app --host 0.0.0.0 --port "${API_PORT:-8000}"
