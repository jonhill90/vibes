#!/bin/bash
# INMPARA MCP Server - Build Script with Qdrant

set -e

echo "🏗️ Building INMPARA MCP Server with Qdrant..."
echo "=============================================="

# Change to project root
cd "$(dirname "$0")/.."

# Build Docker image
echo "📦 Building Docker image..."
docker build -f docker/Dockerfile -t inmpara-mcp-server:latest .

# Create production config
echo "⚙️ Creating production configuration..."
if [ ! -f docker/.env ]; then
    cp docker/.env.example docker/.env
    echo "✅ Created docker/.env from example"
else
    echo "ℹ️ docker/.env already exists"
fi

# Pull Qdrant image
echo "📥 Pulling Qdrant vector database..."
docker pull qdrant/qdrant:v1.7.4

# Create Docker network
echo "🌐 Setting up Docker network..."
docker network create inmpara-network 2>/dev/null || echo "ℹ️ Network already exists"

# Run tests
echo "🧪 Running tests..."
python3 tests/quick_test.py

echo "✅ Build complete!"
echo ""
echo "🚀 To start the full stack:"
echo "   cd docker && docker-compose up -d"
echo ""
echo "🔍 To check status:"
echo "   docker-compose ps"
echo "   docker logs inmpara-mcp-server"
echo "   docker logs inmpara-qdrant"
echo ""
echo "🕸️ Qdrant UI available at: http://localhost:6333/dashboard"
