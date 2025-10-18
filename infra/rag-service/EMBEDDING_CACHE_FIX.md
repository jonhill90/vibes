# Embedding Cache Dimension Fix (Task 7)

## Problem

PostgreSQL error logs showing:
```
ERROR: expected 1536 dimensions, not 3072
STATEMENT: INSERT INTO embedding_cache (content_hash, text_preview, embedding, model_name) VALUES (...)
```

## Root Cause

The `embedding_cache` table was created with a fixed dimension constraint:
```sql
embedding VECTOR(1536) NOT NULL
```

However, the multi-collection architecture uses **two different embedding models**:
- **Documents**: text-embedding-3-small (1536 dimensions)
- **Code**: text-embedding-3-large (3072 dimensions)

When the system tried to cache 3072-dimensional code embeddings, PostgreSQL rejected them because the column only accepted 1536-dimensional vectors.

## Solution

Changed the embedding column to support variable dimensions:

```sql
-- Migration: 006_support_variable_embedding_dimensions.sql
ALTER TABLE embedding_cache
  ALTER COLUMN embedding TYPE VECTOR USING embedding::VECTOR;
```

This removes the dimension constraint while keeping the vector type, allowing the cache to store embeddings of any dimension.

## Verification

Before migration:
```sql
\d embedding_cache
-- embedding | vector(1536) | not null
```

After migration:
```sql
\d embedding_cache
-- embedding | vector | not null
```

## Impact

✅ **Fixes**: "expected 1536 dimensions, not 3072" errors in PostgreSQL logs
✅ **Enables**: Proper caching for both document (1536d) and code (3072d) embeddings
✅ **Preserves**: Existing 1536d cached embeddings remain valid
✅ **Improves**: Cost reduction through caching for code embeddings (previously uncacheable)

## Cache Key Structure

The embedding cache uses a composite key to differentiate embeddings from different models:

```python
# Cache key: (content_hash, model_name)
CONSTRAINT unique_content_hash_model UNIQUE(content_hash, model_name)
```

This ensures:
- Same text with different models → separate cache entries
- Same text with same model → cache hit
- No collision between 1536d and 3072d embeddings

## Files Changed

- `database/migrations/006_support_variable_embedding_dimensions.sql` - Migration script
- `TODO.md` - Task 7 marked complete

## References

- Migration: `database/migrations/006_support_variable_embedding_dimensions.sql`
- Embedding service: `backend/src/services/embeddings/embedding_service.py`
- Multi-collection architecture: `LANGUAGE_FIELD_WORKFLOW.md`
- Original cache creation: `database/migrations/005_create_embedding_cache.sql`
