-- Migration: Support variable embedding dimensions in cache
-- Date: 2025-10-18
-- Purpose: Allow embedding_cache to store both 1536d and 3072d embeddings
--
-- Rationale:
-- - Multi-collection architecture uses different models:
--   * text-embedding-3-small (1536d) for documents
--   * text-embedding-3-large (3072d) for code
-- - Current VECTOR(1536) constraint causes errors when caching 3072d embeddings
-- - PostgreSQL pgvector supports variable dimensions with VECTOR (no size)
--
-- Impact:
-- - Allows caching embeddings from both models
-- - Prevents "expected 1536 dimensions, not 3072" errors
-- - No data loss - existing 1536d embeddings remain valid

-- Change embedding column from fixed VECTOR(1536) to variable VECTOR
ALTER TABLE embedding_cache
  ALTER COLUMN embedding TYPE VECTOR USING embedding::VECTOR;

-- Verification query (uncomment to test):
-- SELECT column_name, data_type, character_maximum_length
-- FROM information_schema.columns
-- WHERE table_name = 'embedding_cache' AND column_name = 'embedding';
