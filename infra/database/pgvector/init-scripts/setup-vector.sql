-- Initialize PGVector extension and create sample schema
-- This runs automatically when the container starts

-- Enable the vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create a sample documents table with vector embeddings
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    embedding VECTOR(1536),  -- OpenAI embedding dimension
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for efficient vector search
-- HNSW index for approximate nearest neighbor search
CREATE INDEX IF NOT EXISTS documents_embedding_hnsw_idx 
ON documents USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- IVFFlat index (alternative, good for exact search)
-- CREATE INDEX IF NOT EXISTS documents_embedding_ivfflat_idx 
-- ON documents USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Create a function for hybrid search (text + vector)
CREATE OR REPLACE FUNCTION hybrid_search(
    query_text TEXT,
    query_embedding VECTOR(1536),
    text_weight FLOAT DEFAULT 0.5,
    vector_weight FLOAT DEFAULT 0.5,
    limit_count INTEGER DEFAULT 10
)
RETURNS TABLE (
    id INTEGER,
    content TEXT,
    metadata JSONB,
    combined_score FLOAT,
    text_score FLOAT,
    vector_similarity FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        d.id,
        d.content,
        d.metadata,
        (text_weight * ts_rank(to_tsvector('english', d.content), plainto_tsquery('english', query_text)) + 
         vector_weight * (1 - (d.embedding <=> query_embedding))) AS combined_score,
        ts_rank(to_tsvector('english', d.content), plainto_tsquery('english', query_text)) AS text_score,
        (1 - (d.embedding <=> query_embedding)) AS vector_similarity
    FROM documents d
    WHERE to_tsvector('english', d.content) @@ plainto_tsquery('english', query_text)
       OR d.embedding <=> query_embedding < 0.8  -- Similarity threshold
    ORDER BY combined_score DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- Create a simple vector similarity search function
CREATE OR REPLACE FUNCTION vector_search(
    query_embedding VECTOR(1536),
    similarity_threshold FLOAT DEFAULT 0.8,
    limit_count INTEGER DEFAULT 10
)
RETURNS TABLE (
    id INTEGER,
    content TEXT,
    metadata JSONB,
    similarity FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        d.id,
        d.content,
        d.metadata,
        (1 - (d.embedding <=> query_embedding)) AS similarity
    FROM documents d
    WHERE d.embedding <=> query_embedding < (1 - similarity_threshold)
    ORDER BY d.embedding <=> query_embedding
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- Insert some sample data for testing
INSERT INTO documents (content, embedding) VALUES 
(
    'PostgreSQL is a powerful, open source object-relational database system with over 30 years of active development.',
    array_fill(random(), ARRAY[1536])::vector  -- Random vector for demo
),
(
    'Vector databases are specialized databases designed to store and query high-dimensional vectors efficiently.',
    array_fill(random(), ARRAY[1536])::vector  -- Random vector for demo
),
(
    'Machine learning models often use embeddings to represent text, images, and other data as vectors.',
    array_fill(random(), ARRAY[1536])::vector  -- Random vector for demo
)
ON CONFLICT DO NOTHING;

-- Create a view for easy querying
CREATE OR REPLACE VIEW document_stats AS
SELECT 
    COUNT(*) as total_documents,
    AVG(array_length(embedding::real[], 1)) as avg_embedding_dimension,
    MAX(created_at) as last_document_added
FROM documents;

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON documents TO postgres;
GRANT USAGE, SELECT ON SEQUENCE documents_id_seq TO postgres;
GRANT SELECT ON document_stats TO postgres;

-- Log setup completion
DO $$
BEGIN
    RAISE NOTICE 'PGVector setup completed successfully!';
    RAISE NOTICE 'Sample data inserted. Use: SELECT * FROM document_stats;';
END $$;
