#!/bin/bash
set -e

echo "🚀 Starting LiteLLM with Supabase PostgreSQL (separate database)..."

# Check if Supabase is running
if ! docker ps | grep -q supabase-db; then
    echo "⚠️  Supabase is not running. Starting Supabase first..."
    cd ../supabase
    docker compose up -d
    echo "⏳ Waiting for Supabase database to be ready..."
    sleep 10
fi

# Create LiteLLM database if it doesn't exist
echo "📦 Creating LiteLLM database in Supabase PostgreSQL cluster..."
docker exec supabase-db psql -U postgres -d postgres -c "SELECT 1 FROM pg_database WHERE datname = 'litellm'" | grep -q 1 || \
docker exec supabase-db psql -U postgres -d postgres -f /dev/stdin < init-litellm-database.sql

echo "✅ LiteLLM database ready"

# Start LiteLLM
cd "$(dirname "$0")"
docker compose up -d

echo ""
echo "✅ LiteLLM started!"
echo ""
echo "📊 Architecture (SQL Server style):"
echo "   PostgreSQL Cluster: supabase-db"
echo "   ├── postgres database (Supabase)"
echo "   └── litellm database (LiteLLM)  ⭐"
echo ""
echo "📡 Access Points:"
echo "   - LiteLLM API: http://localhost:4001"
echo "   - LiteLLM UI:  http://localhost:4001"
echo ""
echo "💾 Database Management:"
echo "   - Backup LiteLLM:  docker exec supabase-db pg_dump -U postgres litellm > litellm_backup.sql"
echo "   - Backup Supabase: docker exec supabase-db pg_dump -U postgres postgres > supabase_backup.sql"
echo "   - List databases:  docker exec supabase-db psql -U postgres -l"
echo ""
echo "🔍 Check status: docker compose ps"
echo "📜 View logs:    docker compose logs -f"
