-- Migration: Create embedding_cache table
-- Date: 2025-10-17
-- Purpose: Add missing embedding_cache table for caching OpenAI embeddings
--
-- Rationale:
-- - Caches embeddings by content hash to avoid redundant API calls (30% cost savings)
-- - Table was defined in init.sql but not created in production database
-- - Fixes "relation embedding_cache does not exist" errors in logs

-- Install pgvector extension (required for VECTOR data type)
CREATE EXTENSION IF NOT EXISTS vector;

-- Create embedding_cache table
CREATE TABLE IF NOT EXISTS embedding_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_hash TEXT NOT NULL,
    text_preview TEXT,
    embedding VECTOR(1536) NOT NULL,
    model_name TEXT NOT NULL DEFAULT 'text-embedding-3-small',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_accessed_at TIMESTAMPTZ DEFAULT NOW(),
    access_count INT DEFAULT 1,

    -- Ensure unique hash per model (same text may have different embeddings per model)
    CONSTRAINT unique_content_hash_model UNIQUE(content_hash, model_name)
);

-- Indexes for embedding_cache table
CREATE INDEX IF NOT EXISTS idx_embedding_cache_hash ON embedding_cache(content_hash);
CREATE INDEX IF NOT EXISTS idx_embedding_cache_model ON embedding_cache(model_name);

-- Verification query (uncomment to test):
-- SELECT column_name, data_type, is_nullable
-- FROM information_schema.columns
-- WHERE table_name = 'embedding_cache'
-- ORDER BY ordinal_position;
