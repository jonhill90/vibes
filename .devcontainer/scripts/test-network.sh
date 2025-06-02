#!/bin/bash

echo "🔍 Testing vibes-network connectivity from devcontainer..."
echo ""

# Test if we can resolve and ping MCP servers
MCP_SERVERS=("azure-mcp-server" "terraform-mcp-server" "mcp-vibes-server" "openmemory-mcp")

echo "📡 Testing network connectivity to MCP servers:"
for server in "${MCP_SERVERS[@]}"; do
    if ping -c 1 -W 2 "$server" &>/dev/null; then
        echo "✅ $server - reachable"
    else
        echo "❌ $server - not reachable"
    fi
done

echo ""
echo "🌐 Testing HTTP connectivity:"

# Test openmemory UI
if curl -s -o /dev/null -w "%{http_code}" http://openmemory-ui:3000 | grep -q "200"; then
    echo "✅ openmemory-ui:3000 - HTTP 200"
else
    echo "❌ openmemory-ui:3000 - not responding"
fi

echo ""
echo "🏷️ Current container network info:"
echo "Container IP: $(hostname -I)"
echo "Container hostname: $(hostname)"

echo ""
echo "🎯 Network test complete!"
