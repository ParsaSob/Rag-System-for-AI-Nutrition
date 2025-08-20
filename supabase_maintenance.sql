-- Supabase Maintenance and Management Queries
-- Collection of useful queries for managing the embedding cache

-- =============================================================================
-- MONITORING QUERIES
-- =============================================================================

-- 1. Cache Overview
SELECT 
    'Cache Overview' as metric,
    COUNT(*) as total_documents,
    SUM(chunk_count) as total_chunks,
    pg_size_pretty(SUM(LENGTH(chunks) + LENGTH(embeddings))::BIGINT) as total_cache_size,
    AVG(access_count) as avg_access_count
FROM document_embeddings;

-- 2. Storage by File Type
SELECT 
    COALESCE(file_type, 'unknown') as file_type,
    COUNT(*) as document_count,
    SUM(chunk_count) as total_chunks,
    pg_size_pretty(SUM(LENGTH(chunks) + LENGTH(embeddings))::BIGINT) as storage_used,
    AVG(access_count) as avg_accesses
FROM document_embeddings
GROUP BY file_type
ORDER BY COUNT(*) DESC;

-- 3. Most and Least Accessed Documents
(SELECT 'Most Accessed' as category, document_name, access_count, last_accessed
 FROM document_embeddings 
 ORDER BY access_count DESC 
 LIMIT 5)
UNION ALL
(SELECT 'Least Accessed' as category, document_name, access_count, last_accessed
 FROM document_embeddings 
 ORDER BY access_count ASC 
 LIMIT 5)
ORDER BY category, access_count DESC;

-- 4. Cache Age Analysis
SELECT 
    CASE 
        WHEN created_at > NOW() - INTERVAL '1 day' THEN 'Last 24 hours'
        WHEN created_at > NOW() - INTERVAL '1 week' THEN 'Last week'
        WHEN created_at > NOW() - INTERVAL '1 month' THEN 'Last month'
        ELSE 'Older than 1 month'
    END as age_group,
    COUNT(*) as document_count,
    SUM(chunk_count) as total_chunks,
    AVG(access_count) as avg_accesses
FROM document_embeddings
GROUP BY age_group
ORDER BY MIN(created_at) DESC;

-- =============================================================================
-- PERFORMANCE ANALYSIS
-- =============================================================================

-- 5. Largest Cache Entries (potential cleanup candidates)
SELECT 
    document_name,
    chunk_count,
    LENGTH(chunks) + LENGTH(embeddings) as cache_size_bytes,
    pg_size_pretty(LENGTH(chunks) + LENGTH(embeddings)) as cache_size_pretty,
    access_count,
    created_at,
    last_accessed
FROM document_embeddings
ORDER BY cache_size_bytes DESC
LIMIT 10;

-- 6. Unused Cache Entries (not accessed in last 30 days)
SELECT 
    document_name,
    chunk_count,
    access_count,
    created_at,
    last_accessed,
    NOW() - last_accessed as unused_duration
FROM document_embeddings
WHERE last_accessed < NOW() - INTERVAL '30 days'
ORDER BY last_accessed;

-- =============================================================================
-- CLEANUP OPERATIONS
-- =============================================================================

-- 7. Safe Cleanup - Remove very old, rarely accessed entries
-- (Run this as a transaction to be safe)
BEGIN;

-- Preview what will be deleted
SELECT 
    'PREVIEW - Would delete' as action,
    COUNT(*) as affected_documents,
    SUM(chunk_count) as affected_chunks,
    pg_size_pretty(SUM(LENGTH(chunks) + LENGTH(embeddings))::BIGINT) as space_to_free
FROM document_embeddings
WHERE created_at < NOW() - INTERVAL '60 days'
AND access_count <= 1;

-- Uncomment the line below to actually perform the deletion
-- DELETE FROM document_embeddings WHERE created_at < NOW() - INTERVAL '60 days' AND access_count <= 1;

ROLLBACK; -- Change to COMMIT if you want to execute the deletion

-- 8. Remove Specific Document Cache
-- DELETE FROM document_embeddings WHERE document_name = 'specific_document_name';

-- 9. Reset Access Counters (if needed)
-- UPDATE document_embeddings SET access_count = 1, last_accessed = NOW();

-- =============================================================================
-- BACKUP AND RESTORE
-- =============================================================================

-- 10. Export Cache Metadata (for backup)
SELECT 
    document_name,
    content_hash,
    chunk_count,
    file_type,
    file_size_bytes,
    created_at,
    access_count
FROM document_embeddings
ORDER BY document_name;

-- 11. Health Check Query
SELECT 
    CASE 
        WHEN COUNT(*) = 0 THEN '❌ No cached documents found'
        WHEN COUNT(*) < 5 THEN '⚠️ Very few cached documents'
        ELSE '✅ Cache is active with ' || COUNT(*) || ' documents'
    END as health_status,
    COUNT(*) as total_docs,
    MAX(created_at) as last_cache_time,
    SUM(CASE WHEN last_accessed > NOW() - INTERVAL '7 days' THEN 1 ELSE 0 END) as recently_used
FROM document_embeddings;

-- =============================================================================
-- INDEX MAINTENANCE
-- =============================================================================

-- 12. Check Index Usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan as times_used,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes 
WHERE tablename = 'document_embeddings'
ORDER BY idx_scan DESC;

-- 13. Reindex if needed (run only if performance issues)
-- REINDEX TABLE document_embeddings;

-- =============================================================================
-- OPTIMIZATION QUERIES
-- =============================================================================

-- 14. Find Duplicate Content Hashes (shouldn't happen, but good to check)
SELECT 
    content_hash,
    COUNT(*) as duplicate_count,
    STRING_AGG(document_name, ', ') as document_names
FROM document_embeddings
GROUP BY content_hash
HAVING COUNT(*) > 1;

-- 15. Cache Hit Ratio Simulation
-- This helps understand if cache is being used effectively
WITH cache_stats AS (
    SELECT 
        COUNT(*) as total_cached,
        SUM(access_count) as total_accesses,
        SUM(CASE WHEN access_count > 1 THEN 1 ELSE 0 END) as reused_caches
    FROM document_embeddings
)
SELECT 
    total_cached,
    total_accesses,
    reused_caches,
    ROUND((reused_caches::NUMERIC / NULLIF(total_cached, 0)) * 100, 2) as cache_hit_ratio_percent,
    CASE 
        WHEN reused_caches::NUMERIC / NULLIF(total_cached, 0) > 0.5 THEN '✅ Good cache utilization'
        WHEN reused_caches::NUMERIC / NULLIF(total_cached, 0) > 0.2 THEN '⚠️ Moderate cache utilization'
        ELSE '❌ Poor cache utilization - consider cleanup'
    END as recommendation
FROM cache_stats;

-- =============================================================================
-- USAGE EXAMPLES
-- =============================================================================

/*
-- Example 1: Clean up old, unused entries
SELECT cleanup_old_cache(45); -- Remove entries older than 45 days with low access

-- Example 2: Check cache statistics  
SELECT * FROM cache_statistics;

-- Example 3: Find specific document cache
SELECT * FROM document_embeddings WHERE document_name LIKE '%data_base%';

-- Example 4: Monitor cache growth over time
SELECT 
    DATE(created_at) as cache_date,
    COUNT(*) as documents_cached,
    SUM(chunk_count) as chunks_added
FROM document_embeddings
WHERE created_at > NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY cache_date;

*/
