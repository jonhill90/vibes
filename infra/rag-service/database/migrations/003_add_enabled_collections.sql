-- Migration 003: Add enabled_collections and update status enum for multi-collection architecture
--
-- Purpose: Enable per-source collection selection (documents, code, media)
-- Impact: Allows sources to opt into specific embedding collections for optimal embeddings
-- PRP Reference: prps/multi_collection_architecture.md (Task 1, Lines 364-392)
--
-- Changes:
-- 1. Add enabled_collections TEXT[] column with validation constraints
-- 2. Set default value ARRAY['documents']::TEXT[] for new sources
-- 3. Add CHECK constraint to validate collection values
-- 4. Add CHECK constraint to ensure array length > 0
-- 5. Create GIN index for efficient array queries
-- 6. Update existing rows with default collection
-- 7. Update status enum: remove "pending" and "completed", add "active" and "archived"
--
-- Rollback: See bottom of file for rollback statements
-- Applied: [DATE WILL BE SET ON EXECUTION]

-- =============================================================================
-- SCHEMA CHANGES: Add enabled_collections column
-- =============================================================================

-- Add enabled_collections column with default and constraints
-- Note: Using DO block for idempotency (safe to run multiple times)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'sources'
        AND column_name = 'enabled_collections'
    ) THEN
        -- Add column with default value
        ALTER TABLE sources
        ADD COLUMN enabled_collections TEXT[] DEFAULT ARRAY['documents']::TEXT[];

        RAISE NOTICE 'Added enabled_collections column to sources';
    ELSE
        RAISE NOTICE 'enabled_collections column already exists, skipping';
    END IF;
END $$;

-- =============================================================================
-- CONSTRAINT CREATION: Validate collection values
-- =============================================================================

-- Add CHECK constraint to ensure only valid collection types
-- Valid values: 'documents', 'code', 'media'
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'sources_enabled_collections_valid'
    ) THEN
        ALTER TABLE sources
        ADD CONSTRAINT sources_enabled_collections_valid
        CHECK (enabled_collections <@ ARRAY['documents', 'code', 'media']::TEXT[]);

        RAISE NOTICE 'Added CHECK constraint for valid collection types';
    ELSE
        RAISE NOTICE 'Valid collection types constraint already exists';
    END IF;
END $$;

-- Add CHECK constraint to ensure at least one collection enabled
-- Array must not be empty or null
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'sources_enabled_collections_not_empty'
    ) THEN
        ALTER TABLE sources
        ADD CONSTRAINT sources_enabled_collections_not_empty
        CHECK (
            enabled_collections IS NOT NULL
            AND array_length(enabled_collections, 1) > 0
        );

        RAISE NOTICE 'Added CHECK constraint for non-empty array';
    ELSE
        RAISE NOTICE 'Non-empty array constraint already exists';
    END IF;
END $$;

-- =============================================================================
-- INDEX CREATION: GIN index for array queries
-- =============================================================================

-- Create GIN index for efficient array containment queries
-- Supports queries like: WHERE 'code' = ANY(enabled_collections)
-- Also supports: WHERE enabled_collections @> ARRAY['code']::TEXT[]
CREATE INDEX IF NOT EXISTS idx_sources_enabled_collections
ON sources USING GIN(enabled_collections);

-- Log index creation
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE indexname = 'idx_sources_enabled_collections'
    ) THEN
        RAISE NOTICE '✓ GIN index created on enabled_collections';
    ELSE
        RAISE WARNING '✗ Failed to create GIN index';
    END IF;
END $$;

-- =============================================================================
-- DATA MIGRATION: Backfill enabled_collections for existing rows
-- =============================================================================

-- Update existing sources to have default collection
-- Only update NULL values (safe for re-runs)
UPDATE sources
SET enabled_collections = ARRAY['documents']::TEXT[]
WHERE enabled_collections IS NULL;

-- Log data migration
DO $$
DECLARE
    row_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO row_count
    FROM sources
    WHERE enabled_collections IS NOT NULL;

    RAISE NOTICE 'Backfilled % existing sources with default collection', row_count;
END $$;

-- =============================================================================
-- STATUS ENUM UPDATE: Remove "pending" and "completed", add "active" and "archived"
-- =============================================================================

-- Drop existing status constraint
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'sources_status_check'
    ) THEN
        ALTER TABLE sources DROP CONSTRAINT sources_status_check;
        RAISE NOTICE 'Dropped old status constraint';
    ELSE
        RAISE NOTICE 'Old status constraint does not exist, skipping drop';
    END IF;
END $$;

-- Add new status constraint with updated values
-- Old: 'pending', 'processing', 'completed', 'failed'
-- New: 'active', 'processing', 'failed', 'archived'
ALTER TABLE sources
ADD CONSTRAINT sources_status_check
CHECK (status IN ('active', 'processing', 'failed', 'archived'));

-- Migrate existing status values
-- "pending" -> "active" (source ready to use)
-- "completed" -> "active" (source ready to use)
UPDATE sources
SET status = 'active'
WHERE status IN ('pending', 'completed');

-- Log status migration
DO $$
DECLARE
    active_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO active_count
    FROM sources
    WHERE status = 'active';

    RAISE NOTICE 'Migrated status values: % sources now "active"', active_count;
END $$;

-- =============================================================================
-- UPDATE STATISTICS
-- =============================================================================

-- Update table statistics for query planner
ANALYZE sources;

-- =============================================================================
-- VERIFICATION
-- =============================================================================

-- Verify enabled_collections column exists with correct type
DO $$
DECLARE
    col_type TEXT;
BEGIN
    SELECT data_type INTO col_type
    FROM information_schema.columns
    WHERE table_name = 'sources'
    AND column_name = 'enabled_collections';

    IF col_type = 'ARRAY' THEN
        RAISE NOTICE '✓ enabled_collections column exists with ARRAY type';
    ELSE
        RAISE WARNING '✗ enabled_collections column has incorrect type: %', col_type;
    END IF;
END $$;

-- Verify constraints exist
DO $$
DECLARE
    constraint_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO constraint_count
    FROM pg_constraint
    WHERE conname IN (
        'sources_enabled_collections_valid',
        'sources_enabled_collections_not_empty',
        'sources_status_check'
    );

    IF constraint_count = 3 THEN
        RAISE NOTICE '✓ All constraints created (3/3)';
    ELSE
        RAISE WARNING '✗ Missing constraints (expected 3, found %)', constraint_count;
    END IF;
END $$;

-- Verify GIN index exists
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE tablename = 'sources'
        AND indexname = 'idx_sources_enabled_collections'
    ) THEN
        RAISE NOTICE '✓ GIN index exists on enabled_collections';
    ELSE
        RAISE WARNING '✗ GIN index missing';
    END IF;
END $$;

-- Verify all existing sources have valid enabled_collections
DO $$
DECLARE
    invalid_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO invalid_count
    FROM sources
    WHERE enabled_collections IS NULL
    OR array_length(enabled_collections, 1) IS NULL;

    IF invalid_count = 0 THEN
        RAISE NOTICE '✓ All sources have valid enabled_collections';
    ELSE
        RAISE WARNING '✗ Found % sources with invalid enabled_collections', invalid_count;
    END IF;
END $$;

-- Verify status values migrated correctly
DO $$
DECLARE
    old_status_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO old_status_count
    FROM sources
    WHERE status IN ('pending', 'completed');

    IF old_status_count = 0 THEN
        RAISE NOTICE '✓ All old status values migrated';
    ELSE
        RAISE WARNING '✗ Found % sources with old status values', old_status_count;
    END IF;
END $$;

-- Show table structure for verification
\d sources

-- Show migration statistics
SELECT
    COUNT(*) as total_sources,
    COUNT(CASE WHEN enabled_collections IS NOT NULL THEN 1 END) as with_collections,
    COUNT(CASE WHEN 'documents' = ANY(enabled_collections) THEN 1 END) as documents_enabled,
    COUNT(CASE WHEN 'code' = ANY(enabled_collections) THEN 1 END) as code_enabled,
    COUNT(CASE WHEN 'media' = ANY(enabled_collections) THEN 1 END) as media_enabled,
    COUNT(CASE WHEN status = 'active' THEN 1 END) as active_sources,
    COUNT(CASE WHEN status = 'processing' THEN 1 END) as processing_sources,
    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_sources
FROM sources;

-- =============================================================================
-- MIGRATION COMPLETE
-- =============================================================================

-- Log migration completion
DO $$
BEGIN
    RAISE NOTICE '=================================================';
    RAISE NOTICE 'Migration 003 completed successfully';
    RAISE NOTICE 'Schema: sources table updated';
    RAISE NOTICE 'Added: enabled_collections TEXT[] column';
    RAISE NOTICE 'Added: 2 CHECK constraints (valid values, non-empty)';
    RAISE NOTICE 'Added: 1 GIN index for array queries';
    RAISE NOTICE 'Updated: status enum (active, processing, failed, archived)';
    RAISE NOTICE 'Migrated: All existing sources to default collection';
    RAISE NOTICE '=================================================';
END $$;

-- =============================================================================
-- ROLLBACK INSTRUCTIONS (for emergency use)
-- =============================================================================

-- CAUTION: Only run these if migration needs to be reverted
--
-- -- Restore old status constraint
-- ALTER TABLE sources DROP CONSTRAINT sources_status_check;
-- ALTER TABLE sources ADD CONSTRAINT sources_status_check
-- CHECK (status IN ('pending', 'processing', 'completed', 'failed'));
--
-- -- Restore old status values
-- UPDATE sources SET status = 'pending' WHERE status = 'active';
--
-- -- Drop GIN index
-- DROP INDEX IF EXISTS idx_sources_enabled_collections;
--
-- -- Drop CHECK constraints
-- ALTER TABLE sources DROP CONSTRAINT IF EXISTS sources_enabled_collections_valid;
-- ALTER TABLE sources DROP CONSTRAINT IF EXISTS sources_enabled_collections_not_empty;
--
-- -- Drop enabled_collections column
-- ALTER TABLE sources DROP COLUMN IF EXISTS enabled_collections;
--
-- -- Update statistics
-- ANALYZE sources;
