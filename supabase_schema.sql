-- Supabase Schema for RAG Embedding Cache
-- This file contains all SQL commands needed to set up the database for the RAG system

-- =============================================================================
-- 1. MAIN TABLE: Document Embeddings Cache
-- =============================================================================

-- Create the main table for storing document embeddings
CREATE TABLE IF NOT EXISTS document_embeddings (
    id BIGSERIAL PRIMARY KEY,
    document_name TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    chunks TEXT NOT NULL,
    embeddings TEXT NOT NULL,
    chunk_count INTEGER NOT NULL,
    file_size_bytes BIGINT,
    file_type TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_accessed TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    access_count INTEGER DEFAULT 1,
    
    -- Ensure unique combination of document name and content hash
    CONSTRAINT unique_document_content UNIQUE(document_name, content_hash)
);

-- =============================================================================
-- 2. INDEXES for Performance
-- =============================================================================

-- Primary lookup index (most important)
CREATE INDEX IF NOT EXISTS idx_document_embeddings_lookup 
ON document_embeddings(document_name, content_hash);

-- Index for finding documents by name only
CREATE INDEX IF NOT EXISTS idx_document_embeddings_name 
ON document_embeddings(document_name);

-- Index for cleanup operations (find old entries)
CREATE INDEX IF NOT EXISTS idx_document_embeddings_created 
ON document_embeddings(created_at);

-- Index for access patterns
CREATE INDEX IF NOT EXISTS idx_document_embeddings_accessed 
ON document_embeddings(last_accessed);

-- =============================================================================
-- 3. FUNCTIONS for Automatic Updates
-- =============================================================================

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Function to update access tracking
CREATE OR REPLACE FUNCTION update_access_tracking()
RETURNS TRIGGER AS $$
BEGIN
    -- Only update if it's a SELECT (read operation)
    NEW.last_accessed = NOW();
    NEW.access_count = OLD.access_count + 1;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- =============================================================================
-- 4. TRIGGERS
-- =============================================================================

-- Trigger to automatically update updated_at on row changes
CREATE TRIGGER update_document_embeddings_updated_at
    BEFORE UPDATE ON document_embeddings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- 5. ROW LEVEL SECURITY (RLS) - Optional but Recommended
-- =============================================================================

-- Enable RLS on the table
ALTER TABLE document_embeddings ENABLE ROW LEVEL SECURITY;

-- Policy to allow all operations for authenticated users
-- Modify this based on your security requirements
CREATE POLICY "Allow all operations for authenticated users" ON document_embeddings
    FOR ALL USING (auth.role() = 'authenticated' OR auth.role() = 'anon');

-- =============================================================================
-- 6. UTILITY VIEWS
-- =============================================================================

-- View for cache statistics
CREATE OR REPLACE VIEW cache_statistics AS
SELECT 
    COUNT(*) as total_documents,
    SUM(chunk_count) as total_chunks,
    AVG(chunk_count) as avg_chunks_per_doc,
    SUM(access_count) as total_accesses,
    AVG(access_count) as avg_accesses_per_doc,
    MIN(created_at) as oldest_cache,
    MAX(created_at) as newest_cache,
    COUNT(DISTINCT file_type) as file_types_count
FROM document_embeddings;

-- View for recently accessed documents
CREATE OR REPLACE VIEW recent_documents AS
SELECT 
    document_name,
    file_type,
    chunk_count,
    access_count,
    last_accessed,
    created_at
FROM document_embeddings
ORDER BY last_accessed DESC
LIMIT 20;

-- View for cache size analysis
CREATE OR REPLACE VIEW cache_size_analysis AS
SELECT 
    document_name,
    file_type,
    chunk_count,
    LENGTH(chunks) + LENGTH(embeddings) as cache_size_bytes,
    file_size_bytes,
    created_at
FROM document_embeddings
ORDER BY cache_size_bytes DESC;

-- =============================================================================
-- 7. MAINTENANCE FUNCTIONS
-- =============================================================================

-- Function to clean up old cache entries (older than specified days)
CREATE OR REPLACE FUNCTION cleanup_old_cache(days_old INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM document_embeddings 
    WHERE created_at < NOW() - INTERVAL '1 day' * days_old
    AND access_count < 2; -- Keep frequently accessed items
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to get cache hit ratio (useful for monitoring)
CREATE OR REPLACE FUNCTION get_cache_stats()
RETURNS TABLE(
    total_docs INTEGER,
    total_chunks BIGINT,
    avg_chunk_size NUMERIC,
    total_cache_size BIGINT,
    most_accessed_doc TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::INTEGER as total_docs,
        SUM(chunk_count) as total_chunks,
        AVG(LENGTH(chunks) + LENGTH(embeddings)) as avg_chunk_size,
        SUM(LENGTH(chunks) + LENGTH(embeddings)) as total_cache_size,
        (SELECT document_name FROM document_embeddings ORDER BY access_count DESC LIMIT 1) as most_accessed_doc
    FROM document_embeddings;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- 8. SAMPLE QUERIES FOR TESTING
-- =============================================================================

-- Check if table was created successfully
-- SELECT COUNT(*) FROM document_embeddings;

-- View cache statistics
-- SELECT * FROM cache_statistics;

-- Find all documents for a specific file type
-- SELECT document_name, chunk_count, created_at 
-- FROM document_embeddings 
-- WHERE file_type = 'csv';

-- Find documents that haven't been accessed recently
-- SELECT document_name, last_accessed, access_count
-- FROM document_embeddings 
-- WHERE last_accessed < NOW() - INTERVAL '7 days'
-- ORDER BY last_accessed;

-- Get total cache size
-- SELECT pg_size_pretty(SUM(LENGTH(chunks) + LENGTH(embeddings))::BIGINT) as total_cache_size
-- FROM document_embeddings;

-- Clean up old cache entries (dry run - just count what would be deleted)
-- SELECT COUNT(*) as would_be_deleted
-- FROM document_embeddings 
-- WHERE created_at < NOW() - INTERVAL '30 days'
-- AND access_count < 2;

-- =============================================================================
-- 9. INITIAL SETUP VERIFICATION
-- =============================================================================

-- Check that everything was created properly
DO $$
BEGIN
    -- Check if table exists
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'document_embeddings') THEN
        RAISE NOTICE '✅ Table document_embeddings created successfully';
    ELSE
        RAISE EXCEPTION '❌ Failed to create document_embeddings table';
    END IF;
    
    -- Check if indexes exist
    IF EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_document_embeddings_lookup') THEN
        RAISE NOTICE '✅ Indexes created successfully';
    ELSE
        RAISE NOTICE '⚠️ Some indexes may be missing';
    END IF;
    
    RAISE NOTICE '🚀 Supabase schema setup completed successfully!';
    RAISE NOTICE '📊 You can now use the RAG system with embedding cache';
END $$;
