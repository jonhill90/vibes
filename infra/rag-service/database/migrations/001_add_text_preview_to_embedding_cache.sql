-- Migration: Add text_preview column to embedding_cache
-- Date: 2025-10-14
-- Purpose: Fix schema mismatch where embedding_service.py tries to insert text_preview
--          but the column doesn't exist in the table.
--
-- Rationale:
-- - text_preview stores first 500 chars of text for debugging/auditing
-- - Non-critical field (nullable) - won't break existing embeddings
-- - Improves troubleshooting by allowing inspection of cached content

-- Add text_preview column (nullable to avoid breaking existing rows)
ALTER TABLE embedding_cache
ADD COLUMN IF NOT EXISTS text_preview TEXT;

-- No index needed - text_preview is for debugging only, not queried

-- Verification query (uncomment to test):
-- SELECT column_name, data_type, is_nullable
-- FROM information_schema.columns
-- WHERE table_name = 'embedding_cache'
-- ORDER BY ordinal_position;
