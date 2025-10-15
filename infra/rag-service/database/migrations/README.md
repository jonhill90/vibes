# RAG Service Database Migrations

This directory contains SQL migration files for the RAG Service PostgreSQL database.

## Migration Files

- **001_init.sql**: Initial schema creation (auto-applied via docker-entrypoint-initdb.d)
- **002_add_text_preview.sql**: Add text_preview and cache tracking to embedding_cache table

## How to Run Migrations

### Method 1: Using Docker Exec (Recommended)

```bash
# From the infra/rag-service directory
docker exec -i rag-postgres psql -U postgres -d rag_service < migrations/002_add_text_preview.sql
```

### Method 2: Using psql Directly (if database exposed on port 5434)

```bash
# From the infra/rag-service directory
psql postgresql://postgres:postgres@localhost:5434/rag_service -f migrations/002_add_text_preview.sql
```

### Method 3: Copy File into Container and Execute

```bash
# Copy migration file into container
docker cp migrations/002_add_text_preview.sql rag-postgres:/tmp/

# Execute migration
docker exec -i rag-postgres psql -U postgres -d rag_service -f /tmp/002_add_text_preview.sql
```

## Verifying Migration Success

After running migration 002, verify the changes:

```bash
# Check table structure
docker exec -i rag-postgres psql -U postgres -d rag_service -c "\d embedding_cache"

# Check for text_preview column
docker exec -i rag-postgres psql -U postgres -d rag_service -c "
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'embedding_cache'
ORDER BY ordinal_position;
"

# Check cache statistics
docker exec -i rag-postgres psql -U postgres -d rag_service -c "
SELECT
    COUNT(*) as total_entries,
    COUNT(CASE WHEN text_preview IS NOT NULL THEN 1 END) as with_preview,
    AVG(access_count) as avg_access_count,
    MAX(access_count) as max_access_count
FROM embedding_cache;
"
```

## Expected Output After Migration 002

You should see:
- ✅ `text_preview` column exists (type: TEXT)
- ✅ `access_count` column exists (type: INTEGER, default: 1)
- ✅ `last_accessed_at` column exists (type: TIMESTAMPTZ)
- ✅ 3 new indexes created (idx_embedding_cache_created, idx_embedding_cache_access_count, idx_embedding_cache_last_accessed)
- ✅ Composite unique constraint (content_hash, model_name)

## Migration Status Tracking

Track which migrations have been applied:

```bash
# Check if migration 002 has been applied
docker exec -i rag-postgres psql -U postgres -d rag_service -c "
SELECT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'embedding_cache'
    AND column_name = 'text_preview'
) as migration_002_applied;
"
```

## Troubleshooting

### Error: "column text_preview does not exist"

**Cause**: Migration 002 not applied, but EmbeddingService expects the column.

**Solution**: Run migration 002 using one of the methods above.

### Error: "role postgres does not exist"

**Cause**: Wrong database user specified.

**Solution**: Check docker-compose.yml for correct POSTGRES_USER (default: postgres).

### Warning: "Cache hit rate unusually low"

**Cause**: Cache not warming up properly, or unique content being embedded.

**Solution**:
1. Verify migration 002 applied successfully
2. Check that text_preview is being populated: `SELECT text_preview FROM embedding_cache LIMIT 5;`
3. Ensure ON CONFLICT clause updates access_count
4. Monitor logs for "[Cache Performance]" messages every 100 requests

## Rollback

To rollback migration 002 (emergency use only):

```bash
docker exec -i rag-postgres psql -U postgres -d rag_service -c "
DROP INDEX IF EXISTS idx_embedding_cache_created;
DROP INDEX IF EXISTS idx_embedding_cache_access_count;
DROP INDEX IF EXISTS idx_embedding_cache_last_accessed;
ALTER TABLE embedding_cache DROP CONSTRAINT IF EXISTS unique_content_hash_model;
ALTER TABLE embedding_cache ADD CONSTRAINT embedding_cache_content_hash_key UNIQUE (content_hash);
ALTER TABLE embedding_cache DROP COLUMN IF EXISTS text_preview;
"
```

**Note**: Do NOT drop `access_count` or `last_accessed_at` during rollback - they existed in the original schema.

## Testing Cache Performance

After applying migration 002 and restarting services:

```bash
# 1. Restart backend to initialize new cache tracking
docker-compose restart backend

# 2. Watch logs for cache hit rate
docker-compose logs -f backend | grep "Cache Performance"

# 3. Generate some embeddings (repeat same query multiple times)
curl -X POST http://localhost:8001/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "test query", "limit": 10}'

# 4. Check cache statistics in database
docker exec -i rag-postgres psql -U postgres -d rag_service -c "
SELECT
    COUNT(*) as total_cached,
    AVG(access_count) as avg_accesses,
    MAX(access_count) as max_accesses,
    COUNT(CASE WHEN access_count > 1 THEN 1 END) as reused_entries,
    COUNT(CASE WHEN access_count > 1 THEN 1 END)::FLOAT / COUNT(*) * 100 as reuse_rate
FROM embedding_cache;
"
```

Expected behavior:
- After 100 requests, you should see log: `[Cache Performance] Total requests: 100, Hits: X, Misses: Y, Hit rate: Z%`
- Target hit rate: 20-40% after warming up (500+ requests)
- If hit rate < 10% after 500 requests, warning logged automatically

## Migration Development Guidelines

When creating new migrations:

1. **File naming**: `NNN_descriptive_name.sql` (e.g., 003_add_vector_indexes.sql)
2. **Idempotency**: Use `IF NOT EXISTS`, `DO $$` blocks for safety
3. **Verification**: Include verification queries at end
4. **Rollback**: Document rollback commands in comments
5. **Testing**: Test on local database before production
6. **Documentation**: Update this README with new migration details

## References

- **PRP**: prps/rag_service_completion.md (Task 7: Embedding Cache Schema Fix)
- **Gotcha #7**: Embedding cache schema mismatch (lines 710-732)
- **EmbeddingService**: backend/src/services/embeddings/embedding_service.py
- **Init Schema**: database/scripts/init.sql
