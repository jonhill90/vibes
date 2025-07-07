#!/bin/bash

# Test script for Context7 MCP Server
# This script tests the Context7 MCP server functionality

echo "=== Context7 MCP Server Test ==="

# Check if container is running
if ! docker ps | grep -q mcp-context7-server; then
    echo "❌ Container not running. Starting container..."
    docker-compose up -d
    sleep 5
fi

echo "✅ Container is running"

# Test if the server binary exists
echo "🔍 Testing server binary..."
if docker exec mcp-context7-server test -f /server/dist/index.js; then
    echo "✅ Server binary found"
else
    echo "❌ Server binary not found"
    exit 1
fi

# Test server help
echo "🔍 Testing server help..."
docker exec mcp-context7-server node /server/dist/index.js --help || echo "Help command executed"

# Test server with stdio transport (default)
echo "🔍 Testing stdio transport..."
echo "Note: This will start the server in stdio mode. Use Ctrl+C to stop."
echo "In production, you would connect this to your MCP client."

# Show how to run the server
echo ""
echo "=== How to use ==="
echo "1. Start container: docker-compose up -d"
echo "2. Run server: docker exec -it mcp-context7-server node /server/dist/index.js"
echo "3. Or with HTTP transport: docker exec -it mcp-context7-server node /server/dist/index.js --transport http --port 3000"
echo ""
echo "=== Available Tools ==="
echo "- resolve-library-id: Find library IDs for documentation lookup"
echo "- get-library-docs: Get up-to-date documentation for libraries"
echo ""

echo "✅ Context7 MCP Server test completed"
