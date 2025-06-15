#!/bin/bash

# Create network if it doesn't exist
docker network create mcp-network 2>/dev/null || true

# Create data directory
mkdir -p ./data

# Build and start the middleware server
docker compose up --build -d

echo "MCP Middleware Server started"
echo "Check status with: docker compose ps"
echo "View logs with: docker compose logs -f"
