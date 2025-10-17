-- Migration 004: Add collection_names JSONB column for per-domain collections
--
-- Purpose: Enable per-source collection name tracking for domain-isolated vector storage
-- Impact: Each source can now track its own Qdrant collection names (e.g., "AI_Knowledge_documents")
-- PRP Reference: prps/per_domain_collections.md (Task 1, Lines 136-162, 458-477)
--
-- Changes:
-- 1. Add collection_names JSONB column with default empty object
-- 2. Create GIN index for efficient JSON queries
-- 3. Populate collection_names for existing sources (sanitize title + collection type)
-- 4. Validate data integrity
--
-- Rollback: See bottom of file for rollback statements
-- Applied: [DATE WILL BE SET ON EXECUTION]

-- =============================================================================
-- SCHEMA CHANGES: Add collection_names column
-- =============================================================================

-- Add collection_names JSONB column with default empty object
-- This stores mapping of collection_type → Qdrant collection name
-- Example: {"documents": "AI_Knowledge_documents", "code": "AI_Knowledge_code"}
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'sources'
        AND column_name = 'collection_names'
    ) THEN
        -- Add column with default value
        ALTER TABLE sources
        ADD COLUMN collection_names JSONB DEFAULT '{}'::JSONB;

        RAISE NOTICE 'Added collection_names column to sources';
    ELSE
        RAISE NOTICE 'collection_names column already exists, skipping';
    END IF;
END $$;

-- =============================================================================
-- INDEX CREATION: GIN index for JSON queries
-- =============================================================================

-- Create GIN index for efficient JSON queries
-- Supports queries like: WHERE collection_names ? 'documents'
-- Also supports: WHERE collection_names @> '{"documents": "AI_Knowledge_documents"}'::jsonb
CREATE INDEX IF NOT EXISTS idx_sources_collection_names
ON sources USING GIN(collection_names);

-- Log index creation
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE indexname = 'idx_sources_collection_names'
    ) THEN
        RAISE NOTICE '✓ GIN index created on collection_names';
    ELSE
        RAISE WARNING '✗ Failed to create GIN index';
    END IF;
END $$;

-- =============================================================================
-- DATA MIGRATION: Populate collection_names for existing sources
-- =============================================================================

-- Populate collection_names for existing sources using sanitization logic
-- Sanitization rules (from PRP lines 119-130):
-- 1. Replace non-alphanumeric chars with underscores
-- 2. Collapse multiple underscores into one
-- 3. Strip leading/trailing underscores
-- 4. Limit length to 64 chars (leave room for collection type suffix)
-- 5. Append collection type (documents, code, media)
UPDATE sources
SET collection_names = (
    SELECT jsonb_object_agg(
        collection_type,
        -- Generate sanitized collection name from source title
        SUBSTRING(
            regexp_replace(
                regexp_replace(
                    regexp_replace(
                        COALESCE(metadata->>'title', 'Source_' || id::text),
                        '[^a-zA-Z0-9_]', '_', 'g'  -- Replace special chars with underscores
                    ),
                    '_+', '_', 'g'  -- Collapse multiple underscores
                ),
                '^_+|_+$', '', 'g'  -- Strip leading/trailing underscores
            ) || '_' || collection_type
            FROM 1 FOR 64  -- Limit to 64 chars total (Qdrant supports 255, but keep shorter)
        )
    )
    FROM unnest(enabled_collections) AS collection_type
)
WHERE collection_names = '{}'::JSONB  -- Only update empty collection_names (safe for re-runs)
   OR collection_names IS NULL;

-- Log data migration
DO $$
DECLARE
    migrated_count INTEGER;
    total_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO migrated_count
    FROM sources
    WHERE collection_names IS NOT NULL AND collection_names != '{}'::JSONB;

    SELECT COUNT(*) INTO total_count
    FROM sources;

    RAISE NOTICE 'Populated collection_names for % of % sources', migrated_count, total_count;
END $$;

-- =============================================================================
-- DATA VALIDATION
-- =============================================================================

-- Verify all sources have valid collection_names
DO $$
DECLARE
    invalid_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO invalid_count
    FROM sources
    WHERE collection_names IS NULL
       OR collection_names = '{}'::JSONB;

    IF invalid_count > 0 THEN
        RAISE WARNING '⚠ Found % sources with empty collection_names - this is expected if no enabled_collections', invalid_count;
    ELSE
        RAISE NOTICE '✓ All sources have valid collection_names';
    END IF;
END $$;

-- Verify collection_names structure matches enabled_collections
DO $$
DECLARE
    mismatch_count INTEGER;
BEGIN
    -- Validate that collection_names keys match enabled_collections array
    SELECT COUNT(*) INTO mismatch_count
    FROM sources
    WHERE array_length(enabled_collections, 1) > 0
      AND (
          SELECT array_agg(key ORDER BY key)
          FROM jsonb_object_keys(collection_names) AS key
      ) IS DISTINCT FROM (
          SELECT array_agg(elem ORDER BY elem)
          FROM unnest(enabled_collections) AS elem
      );

    IF mismatch_count = 0 THEN
        RAISE NOTICE '✓ All collection_names match enabled_collections';
    ELSE
        RAISE WARNING '✗ Found % sources with mismatched collection_names', mismatch_count;
    END IF;
END $$;

-- =============================================================================
-- UPDATE STATISTICS
-- =============================================================================

-- Update table statistics for query planner
ANALYZE sources;

-- =============================================================================
-- VERIFICATION
-- =============================================================================

-- Verify collection_names column exists with correct type
DO $$
DECLARE
    col_type TEXT;
BEGIN
    SELECT data_type INTO col_type
    FROM information_schema.columns
    WHERE table_name = 'sources'
    AND column_name = 'collection_names';

    IF col_type = 'jsonb' THEN
        RAISE NOTICE '✓ collection_names column exists with JSONB type';
    ELSE
        RAISE WARNING '✗ collection_names column has incorrect type: %', col_type;
    END IF;
END $$;

-- Verify GIN index exists
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE tablename = 'sources'
        AND indexname = 'idx_sources_collection_names'
    ) THEN
        RAISE NOTICE '✓ GIN index exists on collection_names';
    ELSE
        RAISE WARNING '✗ GIN index missing';
    END IF;
END $$;

-- Show example collection names (for verification)
DO $$
DECLARE
    example_record RECORD;
    example_count INTEGER := 0;
BEGIN
    RAISE NOTICE '=================================================';
    RAISE NOTICE 'Sample collection_names (first 3 sources):';
    RAISE NOTICE '=================================================';

    FOR example_record IN
        SELECT
            id,
            metadata->>'title' as title,
            enabled_collections,
            collection_names
        FROM sources
        WHERE collection_names IS NOT NULL
          AND collection_names != '{}'::JSONB
        ORDER BY created_at DESC
        LIMIT 3
    LOOP
        example_count := example_count + 1;
        RAISE NOTICE 'Source: % (ID: %)', example_record.title, example_record.id;
        RAISE NOTICE 'Enabled: %', example_record.enabled_collections;
        RAISE NOTICE 'Collections: %', example_record.collection_names;
        RAISE NOTICE '-------------------------------------------------';
    END LOOP;

    IF example_count = 0 THEN
        RAISE NOTICE 'No sources with collection_names found';
    END IF;

    RAISE NOTICE '=================================================';
END $$;

-- Show migration statistics
SELECT
    COUNT(*) as total_sources,
    COUNT(CASE WHEN collection_names IS NOT NULL AND collection_names != '{}'::JSONB THEN 1 END) as with_collection_names,
    COUNT(CASE WHEN collection_names ? 'documents' THEN 1 END) as documents_collections,
    COUNT(CASE WHEN collection_names ? 'code' THEN 1 END) as code_collections,
    COUNT(CASE WHEN collection_names ? 'media' THEN 1 END) as media_collections
FROM sources;

-- =============================================================================
-- MIGRATION COMPLETE
-- =============================================================================

-- Log migration completion
DO $$
BEGIN
    RAISE NOTICE '=================================================';
    RAISE NOTICE 'Migration 004 completed successfully';
    RAISE NOTICE 'Schema: sources table updated';
    RAISE NOTICE 'Added: collection_names JSONB column';
    RAISE NOTICE 'Added: GIN index for JSON queries';
    RAISE NOTICE 'Migrated: All existing sources to domain-specific collection names';
    RAISE NOTICE 'Pattern: {sanitized_title}_{collection_type}';
    RAISE NOTICE 'Example: "AI Knowledge" + "documents" → "AI_Knowledge_documents"';
    RAISE NOTICE '=================================================';
END $$;

-- =============================================================================
-- ROLLBACK INSTRUCTIONS (for emergency use)
-- =============================================================================

-- CAUTION: Only run these if migration needs to be reverted
--
-- -- Drop GIN index
-- DROP INDEX IF EXISTS idx_sources_collection_names;
--
-- -- Drop collection_names column
-- ALTER TABLE sources DROP COLUMN IF EXISTS collection_names;
--
-- -- Update statistics
-- ANALYZE sources;
--
-- -- Verify rollback
-- SELECT column_name FROM information_schema.columns
-- WHERE table_name = 'sources' AND column_name = 'collection_names';
-- -- Should return no rows after rollback
