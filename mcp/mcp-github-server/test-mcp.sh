#!/bin/bash

echo "🧪 Testing GitHub MCP Server..."
echo "================================"

# Check if container is running
if ! docker ps | grep -q github-mcp-server; then
    echo "❌ GitHub MCP server container is not running!"
    exit 1
fi

echo "✅ Container is running"

# Check health status
HEALTH=$(docker inspect github-mcp-server --format='{{.State.Health.Status}}' 2>/dev/null || echo "no-health-check")
echo "🏥 Health status: $HEALTH"

# Test if binary exists and works (distroless container)
if docker exec github-mcp-server /server/github-mcp-server --help >/dev/null 2>&1; then
    echo "✅ GitHub MCP server binary is ready"
    
    # Show available commands
    echo "📋 Available server options:"
    docker exec github-mcp-server /server/github-mcp-server --help | grep -A 20 "Available Commands:"
    
else
    echo "❌ GitHub MCP server binary not working"
    exit 1
fi

# Test basic MCP functionality (if token is configured)
if [ -f .env ] && grep -q "GITHUB_PERSONAL_ACCESS_TOKEN=ghp_" .env; then
    echo ""
    echo "🔑 GitHub token detected, testing MCP initialization..."
    
    # Test MCP initialize call with timeout
    INIT_TEST=$(echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0.0"}}}' | \
    timeout 5s docker exec -i github-mcp-server /server/github-mcp-server stdio 2>/dev/null || echo "timeout")
    
    if echo "$INIT_TEST" | grep -q "result"; then
        echo "✅ MCP protocol initialization successful"
        echo "🛠️  Server has tools available for GitHub operations"
    else
        echo "⚠️  MCP protocol test inconclusive (server may need valid token or method)"
    fi
else
    echo ""
    echo "⚠️  No GitHub token configured in .env file"
    echo "   Add GITHUB_PERSONAL_ACCESS_TOKEN=ghp_... to .env for full functionality"
fi

echo ""
echo "📊 Container Status:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep github-mcp-server

echo ""
echo "📝 Recent logs:"
docker logs github-mcp-server --tail 3

echo ""
echo "🎯 MCP Integration Examples:"
echo ""
echo "   VS Code Agent Mode:"
echo '   {
     "mcp": {
       "servers": {
         "github": {
           "command": "docker",
           "args": ["exec", "-i", "github-mcp-server", "/server/github-mcp-server", "stdio"],
           "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": "your-token"}
         }
       }
     }
   }'
echo ""
echo "   Direct CLI Test:"
echo "   docker exec -i github-mcp-server /server/github-mcp-server stdio"
echo "   (Then send MCP JSON-RPC messages)"
