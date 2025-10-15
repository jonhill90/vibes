-- Migration 002: Add text_preview and access tracking to embedding_cache
--
-- Purpose: Fix schema mismatch where EmbeddingService expects text_preview column
-- Impact: Enables cache hit rate monitoring and debugging capabilities
-- PRP Reference: prps/rag_service_completion.md (Task 7, Gotcha #7)
--
-- Changes:
-- 1. Add text_preview column for debugging cached embeddings
-- 2. Add/enhance access tracking (access_count, last_accessed_at already exist)
-- 3. Add index on created_at for cache aging analysis
-- 4. Add composite unique constraint on (content_hash, model_name) for robustness
--
-- Rollback: See bottom of file for rollback statements
-- Applied: [DATE WILL BE SET ON EXECUTION]

-- =============================================================================
-- SCHEMA CHANGES
-- =============================================================================

-- Add text_preview column if it doesn't exist
-- Stores first 500 chars of text for debugging and cache analysis
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'embedding_cache'
        AND column_name = 'text_preview'
    ) THEN
        ALTER TABLE embedding_cache
        ADD COLUMN text_preview TEXT;

        RAISE NOTICE 'Added text_preview column to embedding_cache';
    ELSE
        RAISE NOTICE 'text_preview column already exists, skipping';
    END IF;
END $$;

-- Verify access_count exists (should already exist from init.sql line 130)
-- If missing, add it for backwards compatibility
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'embedding_cache'
        AND column_name = 'access_count'
    ) THEN
        ALTER TABLE embedding_cache
        ADD COLUMN access_count INTEGER DEFAULT 1;

        RAISE NOTICE 'Added access_count column to embedding_cache';
    ELSE
        RAISE NOTICE 'access_count column already exists';
    END IF;
END $$;

-- Verify last_accessed_at exists (should already exist from init.sql line 129)
-- Rename last_accessed to last_accessed_at if needed
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'embedding_cache'
        AND column_name = 'last_accessed_at'
    ) THEN
        -- Check if old column name exists
        IF EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'embedding_cache'
            AND column_name = 'last_accessed'
        ) THEN
            ALTER TABLE embedding_cache
            RENAME COLUMN last_accessed TO last_accessed_at;
            RAISE NOTICE 'Renamed last_accessed to last_accessed_at';
        ELSE
            ALTER TABLE embedding_cache
            ADD COLUMN last_accessed_at TIMESTAMP DEFAULT NOW();
            RAISE NOTICE 'Added last_accessed_at column';
        END IF;
    ELSE
        RAISE NOTICE 'last_accessed_at column already exists';
    END IF;
END $$;

-- =============================================================================
-- INDEX CREATION
-- =============================================================================

-- Index on created_at DESC for cache aging queries
-- Supports queries like: "Show oldest cached embeddings"
CREATE INDEX IF NOT EXISTS idx_embedding_cache_created
ON embedding_cache(created_at DESC);

-- Index on access_count for popularity analysis
-- Supports queries like: "Most frequently accessed embeddings"
CREATE INDEX IF NOT EXISTS idx_embedding_cache_access_count
ON embedding_cache(access_count DESC);

-- Index on last_accessed_at for LRU eviction
-- Supports queries like: "Least recently used embeddings"
CREATE INDEX IF NOT EXISTS idx_embedding_cache_last_accessed
ON embedding_cache(last_accessed_at DESC);

-- =============================================================================
-- CONSTRAINT UPDATES
-- =============================================================================

-- Ensure composite unique constraint exists on (content_hash, model_name)
-- This allows same text to have different embeddings across models
DO $$
BEGIN
    -- Drop old unique constraint on content_hash only (if exists)
    IF EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'embedding_cache_content_hash_key'
    ) THEN
        ALTER TABLE embedding_cache
        DROP CONSTRAINT embedding_cache_content_hash_key;
        RAISE NOTICE 'Dropped old unique constraint on content_hash';
    END IF;

    -- Add composite unique constraint
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'unique_content_hash_model'
    ) THEN
        ALTER TABLE embedding_cache
        ADD CONSTRAINT unique_content_hash_model
        UNIQUE (content_hash, model_name);
        RAISE NOTICE 'Added composite unique constraint (content_hash, model_name)';
    ELSE
        RAISE NOTICE 'Composite unique constraint already exists';
    END IF;
END $$;

-- =============================================================================
-- DATA MIGRATION (Backfill text_preview for existing rows)
-- =============================================================================

-- For existing cache entries without text_preview, set to placeholder
-- In production, these will be replaced as cache entries are accessed
UPDATE embedding_cache
SET text_preview = '[No preview - created before migration 002]'
WHERE text_preview IS NULL;

-- Update statistics
ANALYZE embedding_cache;

-- =============================================================================
-- VERIFICATION
-- =============================================================================

-- Verify columns exist
DO $$
DECLARE
    col_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO col_count
    FROM information_schema.columns
    WHERE table_name = 'embedding_cache'
    AND column_name IN ('text_preview', 'access_count', 'last_accessed_at');

    IF col_count = 3 THEN
        RAISE NOTICE '✓ All required columns exist';
    ELSE
        RAISE WARNING '✗ Missing columns (expected 3, found %)', col_count;
    END IF;
END $$;

-- Verify indexes exist
DO $$
DECLARE
    idx_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO idx_count
    FROM pg_indexes
    WHERE tablename = 'embedding_cache'
    AND indexname IN (
        'idx_embedding_cache_created',
        'idx_embedding_cache_access_count',
        'idx_embedding_cache_last_accessed'
    );

    IF idx_count = 3 THEN
        RAISE NOTICE '✓ All cache performance indexes exist';
    ELSE
        RAISE WARNING '✗ Missing indexes (expected 3, found %)', idx_count;
    END IF;
END $$;

-- Show table structure for verification
\d embedding_cache

-- Show cache statistics
SELECT
    COUNT(*) as total_entries,
    COUNT(CASE WHEN text_preview IS NOT NULL THEN 1 END) as with_preview,
    AVG(access_count) as avg_access_count,
    MAX(access_count) as max_access_count,
    MIN(created_at) as oldest_entry,
    MAX(created_at) as newest_entry
FROM embedding_cache;

-- =============================================================================
-- MIGRATION COMPLETE
-- =============================================================================

-- Log migration completion
DO $$
BEGIN
    RAISE NOTICE '=================================================';
    RAISE NOTICE 'Migration 002 completed successfully';
    RAISE NOTICE 'Schema: embedding_cache table updated';
    RAISE NOTICE 'Added: text_preview column';
    RAISE NOTICE 'Added: 3 performance indexes';
    RAISE NOTICE 'Updated: composite unique constraint';
    RAISE NOTICE '=================================================';
END $$;

-- =============================================================================
-- ROLLBACK INSTRUCTIONS (for emergency use)
-- =============================================================================

-- CAUTION: Only run these if migration needs to be reverted
--
-- DROP INDEX IF EXISTS idx_embedding_cache_created;
-- DROP INDEX IF EXISTS idx_embedding_cache_access_count;
-- DROP INDEX IF EXISTS idx_embedding_cache_last_accessed;
--
-- ALTER TABLE embedding_cache DROP CONSTRAINT IF EXISTS unique_content_hash_model;
-- ALTER TABLE embedding_cache ADD CONSTRAINT embedding_cache_content_hash_key UNIQUE (content_hash);
--
-- ALTER TABLE embedding_cache DROP COLUMN IF EXISTS text_preview;
--
-- Note: access_count and last_accessed_at existed in original schema (init.sql)
-- so they should NOT be dropped during rollback.
