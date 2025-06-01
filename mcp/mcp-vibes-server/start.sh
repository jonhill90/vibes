#!/bin/bash

echo "🚀 Starting MCP Vibes Server..."
echo "Your AI Learning Orchestrator is initializing..."
echo ""

# Ensure Docker is accessible
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker not accessible. Make sure Docker socket is mounted."
    exit 1
fi

echo "✅ Docker connection verified"

# Create workspace directories
mkdir -p /workspace/{projects,configs,tools,data}
echo "📁 Workspace directories created"

# Ensure vibes network exists
if ! docker network inspect vibes-network >/dev/null 2>&1; then
    docker network create vibes-network
    echo "🌐 Created vibes-network"
else
    echo "🌐 vibes-network already exists"
fi

# Test Ollama connection
echo "🤖 Testing Ollama connection..."
if curl -s http://host.docker.internal:11434/api/tags >/dev/null; then
    echo "✅ Ollama connection successful"
else
    echo "⚠️  Cannot reach Ollama (this is ok, will try later)"
fi

echo ""
echo "🎯 MCP Vibes Server Ready!"
echo "   Claude can now:"
echo "   • Build & run containers"
echo "   • Call your Ollama models" 
echo "   • Set up learning environments"
echo "   • Create files & configurations"
echo "   • Orchestrate complex stacks"
echo ""

# Start the MCP server
exec python3 /workspace/server.py
