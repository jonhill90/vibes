#!/bin/bash

# INMPARA Notebook Server Startup Script

echo "🚀 Starting INMPARA Notebook MCP Server..."

# Check if Qdrant is running
if ! curl -f http://localhost:6334/health > /dev/null 2>&1; then
    echo "🔍 Starting Qdrant vector database..."
    docker-compose up -d qdrant
    
    echo "⏳ Waiting for Qdrant to be ready..."
    until curl -f http://localhost:6334/health > /dev/null 2>&1; do
        sleep 2
    done
    echo "✅ Qdrant is ready"
fi

# Set environment
export INMPARA_VAULT_PATH="/workspace/vibes/repos/inmpara"
export SQLITE_DB_PATH="./data/inmpara_vault.db"
export QDRANT_HOST="localhost"
export QDRANT_PORT="6334"

# Create data directory
mkdir -p ./data

echo "📚 INMPARA Notebook Server Configuration:"
echo "   - Vault Path: $INMPARA_VAULT_PATH"
echo "   - Database: $SQLITE_DB_PATH"
echo "   - Vector DB: $QDRANT_HOST:$QDRANT_PORT"
echo ""

echo "🎯 Available MCP Tools (Phase 1):"
echo "   - capture_conversation_insight: Intelligent insight detection"
echo "   - auto_create_note: Perfect INMPARA note creation"
echo "   - search_semantic: Vector similarity search"
echo "   - suggest_connections: Real-time connection discovery"
echo "   - get_inbox_items: Preview inbox with analysis"
echo "   - get_recent_insights: Show detected insights"
echo "   - search_exact: Traditional text search"
echo "   - validate_inmpara_format: Format validation"
echo "   - get_vault_analytics: Knowledge base statistics"
echo "   - start_conversation_session: Begin insight tracking"
echo ""

echo "🔗 Starting MCP Server..."
python3 main.py
