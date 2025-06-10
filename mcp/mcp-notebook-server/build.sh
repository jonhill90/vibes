#!/bin/bash

# INMPARA Notebook Server - Build and Setup Script

set -e

echo "🚀 Building INMPARA Notebook MCP Server..."

# Create necessary directories
mkdir -p data/qdrant_storage
mkdir -p logs

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo "📋 Created .env file from template - please configure your settings"
fi

# Start Qdrant vector database
echo "🔍 Starting Qdrant vector database..."
docker-compose up -d qdrant

# Wait for Qdrant to be ready
echo "⏳ Waiting for Qdrant to be ready..."
until curl -f http://localhost:6334/health > /dev/null 2>&1; do
    sleep 2
done
echo "✅ Qdrant is ready"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Initialize database
echo "🗄️ Initializing database..."
python -c "
from src.database.database import INMPARADatabase
import os
db_path = os.getenv('SQLITE_DB_PATH', './data/inmpara_vault.db')
db = INMPARADatabase(db_path)
print('Database initialized successfully')
"

# Test vector database connection
echo "🔗 Testing vector database connection..."
python -c "
from src.database.vector_search import VectorSearchEngine
import os
host = os.getenv('QDRANT_HOST', 'localhost')
port = int(os.getenv('QDRANT_PORT', '6334'))
vs = VectorSearchEngine(host=host, port=port)
info = vs.get_collection_info()
print(f'Vector database connected: {info}')
"

echo "✅ INMPARA Notebook Server setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Configure your .env file with API keys and paths"
echo "2. Start the server: python -m src.server"
echo "3. Test with MCP client or integrate with Claude Desktop"
echo ""
echo "📚 Documentation:"
echo "- Phase 1 tools available: capture_conversation_insight, auto_create_note"
echo "- Vault path: $(grep INMPARA_VAULT_PATH .env || echo '/workspace/vibes/repos/inmpara')"
echo "- Database: ./data/inmpara_vault.db"
echo "- Vector DB: localhost:6334"
