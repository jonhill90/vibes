#!/bin/bash
# INMPARA MCP Server - Start Script with Qdrant

set -e

echo "🚀 Starting INMPARA MCP Server with Qdrant..."
echo "=============================================="

# Change to project root
cd "$(dirname "$0")/.."

# Check if Docker is available
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    echo "🐳 Using Docker deployment..."
    cd docker
    
    # Start services
    echo "📥 Starting Qdrant vector database..."
    docker-compose up -d qdrant
    
    echo "⏳ Waiting for Qdrant to be ready..."
    sleep 5
    
    echo "🤖 Starting INMPARA MCP Server..."
    docker-compose up -d inmpara-mcp-server
    
    echo "✅ Full stack started!"
    echo ""
    echo "📊 Status:"
    docker-compose ps
    
    echo ""
    echo "🌐 Services available:"
    echo "   • Qdrant Dashboard: http://localhost:6333/dashboard"
    echo "   • Qdrant API: http://localhost:6333"
    echo "   • MCP Server: http://localhost:8000"
    
    echo ""
    echo "📋 View logs:"
    echo "   docker logs -f inmpara-mcp-server"
    echo "   docker logs -f inmpara-qdrant"
    
    echo ""
    echo "🛑 Stop services:"
    echo "   docker-compose down"
    
else
    echo "🐍 Using direct Python deployment..."
    echo "⚠️  Note: You'll need to start Qdrant separately"
    echo "   Docker: docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant:v1.7.4"
    
    # Install dependencies
    pip install -r requirements.txt
    
    # Start server
    cd bin
    QDRANT_HOST=localhost python3 run_production_server.py --vault-path /workspace/vibes/repos/inmpara
fi
