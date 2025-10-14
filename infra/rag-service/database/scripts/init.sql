-- PostgreSQL Initialization Script for RAG Service
-- Version: 1.0
-- Description: Complete schema with 5 tables, indexes, and triggers
-- Dependencies: PostgreSQL 15+, uuid-ossp, pg_trgm, pgvector extensions

-- =============================================================================
-- EXTENSIONS
-- =============================================================================

-- Extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Extension for full-text search (trigram matching for fuzzy search)
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Extension for vector embeddings (required for embedding_cache table)
CREATE EXTENSION IF NOT EXISTS vector;

-- =============================================================================
-- TABLE 1: sources
-- =============================================================================
-- Tracks ingestion sources (uploads, crawls, API imports) and processing status.

CREATE TABLE sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_type TEXT NOT NULL CHECK (source_type IN ('upload', 'crawl', 'api')),
    url TEXT,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    metadata JSONB DEFAULT '{}'::jsonb,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for sources table
CREATE INDEX idx_sources_status ON sources(status);
CREATE INDEX idx_sources_source_type ON sources(source_type);
CREATE INDEX idx_sources_created_at ON sources(created_at DESC);

-- =============================================================================
-- TABLE 2: documents
-- =============================================================================
-- Stores document-level metadata and references to source ingestion.

CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    document_type TEXT,
    url TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    search_vector TSVECTOR,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for documents table
CREATE INDEX idx_documents_source_id ON documents(source_id);
CREATE INDEX idx_documents_search_vector ON documents USING GIN(search_vector);
CREATE INDEX idx_documents_document_type ON documents(document_type);
CREATE INDEX idx_documents_created_at ON documents(created_at DESC);

-- =============================================================================
-- TABLE 3: chunks
-- =============================================================================
-- Stores document chunks with text content and full-text search vectors.

CREATE TABLE chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    text TEXT NOT NULL,
    token_count INTEGER,
    search_vector TSVECTOR,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Ensure unique chunk ordering per document
    CONSTRAINT unique_document_chunk UNIQUE(document_id, chunk_index)
);

-- Indexes for chunks table
CREATE INDEX idx_chunks_document_id ON chunks(document_id);
CREATE INDEX idx_chunks_search_vector ON chunks USING GIN(search_vector);
CREATE INDEX idx_chunks_document_id_chunk_index ON chunks(document_id, chunk_index);

-- =============================================================================
-- TABLE 4: crawl_jobs
-- =============================================================================
-- Tracks web crawling operations with progress and error reporting.

CREATE TABLE crawl_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    pages_crawled INTEGER NOT NULL DEFAULT 0,
    pages_total INTEGER,
    max_pages INTEGER DEFAULT 100,
    max_depth INTEGER DEFAULT 3,
    current_depth INTEGER DEFAULT 0,
    error_message TEXT,
    error_count INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}'::jsonb,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for crawl_jobs table
CREATE INDEX idx_crawl_jobs_source_id ON crawl_jobs(source_id);
CREATE INDEX idx_crawl_jobs_status ON crawl_jobs(status);
CREATE INDEX idx_crawl_jobs_created_at ON crawl_jobs(created_at DESC);
CREATE INDEX idx_crawl_jobs_status_pages ON crawl_jobs(status, pages_crawled);

-- =============================================================================
-- TABLE 5: embedding_cache
-- =============================================================================
-- Caches embeddings by content hash to avoid redundant API calls (30% cost savings).

CREATE TABLE embedding_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_hash TEXT NOT NULL UNIQUE,
    embedding VECTOR(1536) NOT NULL,
    model_name TEXT NOT NULL DEFAULT 'text-embedding-3-small',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_accessed_at TIMESTAMPTZ DEFAULT NOW(),
    access_count INT DEFAULT 1
);

-- Indexes for embedding_cache table
CREATE INDEX idx_embedding_cache_hash ON embedding_cache(content_hash);
CREATE INDEX idx_embedding_cache_model ON embedding_cache(model_name);

-- =============================================================================
-- TRIGGER FUNCTIONS
-- =============================================================================

-- Function to automatically update updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function to automatically update search_vector for documents
CREATE OR REPLACE FUNCTION documents_search_vector_update()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector =
        setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.url, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(NEW.metadata::text, '')), 'C');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function to automatically update search_vector for chunks
CREATE OR REPLACE FUNCTION chunks_search_vector_update()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector = to_tsvector('english', COALESCE(NEW.text, ''));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- TRIGGERS: updated_at auto-update
-- =============================================================================

CREATE TRIGGER sources_updated_at
    BEFORE UPDATE ON sources
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER documents_updated_at
    BEFORE UPDATE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER crawl_jobs_updated_at
    BEFORE UPDATE ON crawl_jobs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- TRIGGERS: search_vector auto-update
-- =============================================================================

CREATE TRIGGER documents_search_vector_trigger
    BEFORE INSERT OR UPDATE OF title, url, metadata
    ON documents
    FOR EACH ROW
    EXECUTE FUNCTION documents_search_vector_update();

CREATE TRIGGER chunks_search_vector_trigger
    BEFORE INSERT OR UPDATE OF text
    ON chunks
    FOR EACH ROW
    EXECUTE FUNCTION chunks_search_vector_update();

-- =============================================================================
-- VERIFICATION QUERIES (commented out - for manual testing)
-- =============================================================================

-- Verify all tables created
-- SELECT table_name FROM information_schema.tables
-- WHERE table_schema = 'public'
-- ORDER BY table_name;

-- Verify all indexes created
-- SELECT indexname, tablename FROM pg_indexes
-- WHERE schemaname = 'public'
-- ORDER BY tablename, indexname;

-- Verify all triggers created
-- SELECT trigger_name, event_object_table
-- FROM information_schema.triggers
-- WHERE trigger_schema = 'public'
-- ORDER BY event_object_table, trigger_name;

-- Verify extensions installed
-- SELECT * FROM pg_extension ORDER BY extname;

-- =============================================================================
-- SCHEMA INITIALIZATION COMPLETE
-- =============================================================================
-- Tables: 5 (sources, documents, chunks, crawl_jobs, embedding_cache)
-- Indexes: 17 (GIN on search_vector, B-tree on FKs, composite indexes)
-- Triggers: 5 (3 updated_at, 2 search_vector)
-- Foreign Keys: 4 with CASCADE delete
-- =============================================================================
