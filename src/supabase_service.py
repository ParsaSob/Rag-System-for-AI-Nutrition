import hashlib
import json
import logging
from typing import List, Optional, Dict, Any
from src.config import SUPABASE_URL, SUPABASE_KEY

logger = logging.getLogger(__name__)

class SupabaseService:
    """Handles Supabase operations for caching embeddings."""
    
    def __init__(self):
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Supabase client if credentials are available."""
        if not SUPABASE_URL or not SUPABASE_KEY:
            logger.warning("Supabase credentials not configured. Embedding cache disabled.")
            return
        
        try:
            from supabase import create_client
            
            # Simple client creation without extra options
            self.client = create_client(SUPABASE_URL, SUPABASE_KEY)
            logger.info("Supabase client initialized successfully")
        except ImportError:
            logger.warning("Supabase package not installed. Embedding cache disabled.")
            self.client = None
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {str(e)}")
            # In production, disable Supabase if it fails rather than crashing
            logger.warning("Continuing without Supabase cache...")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if Supabase is available for use."""
        return self.client is not None
    
    def test_connection(self) -> bool:
        """Test the Supabase connection by trying to query the table."""
        if not self.is_available():
            return False
        
        try:
            # Try a simple query to test connection
            response = self.client.table('document_embeddings').select('count', count='exact').execute()
            logger.info(f"Supabase connection test successful. Table has {response.count} records.")
            return True
        except Exception as e:
            logger.error(f"Supabase connection test failed: {str(e)}")
            return False
    
    def _generate_document_hash(self, document_name: str, chunks: List[str]) -> str:
        """Generate a hash for the document based on name and content."""
        # Create a hash based on document name and chunk content
        content = f"{document_name}:{':'.join(chunks)}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    async def get_cached_embeddings(self, document_name: str, chunks: List[str]) -> Optional[Dict[str, Any]]:
        """Retrieve cached embeddings for a document if they exist and are current."""
        if not self.is_available():
            return None
        
        try:
            document_hash = self._generate_document_hash(document_name, chunks)
            
            # Add retry mechanism for SSL issues
            import time
            for attempt in range(3):
                try:
                    response = self.client.table('document_embeddings').select('*').eq('document_name', document_name).eq('content_hash', document_hash).execute()
                    
                    if response.data and len(response.data) > 0:
                        cached_data = response.data[0]
                        logger.info(f"Found cached embeddings for document: {document_name}")
                        return {
                            'chunks': json.loads(cached_data['chunks']),
                            'embeddings': json.loads(cached_data['embeddings'])
                        }
                    
                    logger.info(f"No cached embeddings found for document: {document_name}")
                    return None
                    
                except Exception as retry_error:
                    if attempt < 2:  # Try 3 times total
                        logger.warning(f"Attempt {attempt + 1} failed, retrying: {str(retry_error)}")
                        time.sleep(1)
                        continue
                    else:
                        raise retry_error
            
        except Exception as e:
            logger.error(f"Error retrieving cached embeddings after retries: {str(e)}")
            return None
    
    async def cache_embeddings(self, document_name: str, chunks: List[str], embeddings: List[List[float]]) -> bool:
        """Cache embeddings for a document in Supabase."""
        if not self.is_available():
            return False
        
        try:
            document_hash = self._generate_document_hash(document_name, chunks)
            
            # Add retry mechanism for SSL issues
            import time
            for attempt in range(3):
                try:
                    # Delete any existing cache for this document
                    self.client.table('document_embeddings').delete().eq('document_name', document_name).execute()
                    
                    # Insert new cache
                    cache_data = {
                        'document_name': document_name,
                        'content_hash': document_hash,
                        'chunks': json.dumps(chunks),
                        'embeddings': json.dumps(embeddings),
                        'chunk_count': len(chunks)
                    }
                    
                    response = self.client.table('document_embeddings').insert(cache_data).execute()
                    
                    if response.data:
                        logger.info(f"Successfully cached embeddings for document: {document_name}")
                        return True
                    else:
                        logger.error(f"Failed to cache embeddings for document: {document_name}")
                        return False
                        
                except Exception as retry_error:
                    if attempt < 2:  # Try 3 times total
                        logger.warning(f"Cache attempt {attempt + 1} failed, retrying: {str(retry_error)}")
                        time.sleep(1)
                        continue
                    else:
                        raise retry_error
                
        except Exception as e:
            logger.error(f"Error caching embeddings after retries: {str(e)}")
            return False
    
    def create_table_if_not_exists(self):
        """Create the document_embeddings table if it doesn't exist."""
        if not self.is_available():
            return False
        
        try:
            # Note: In practice, you should create this table via Supabase dashboard or migrations
            # This is just a reference for the expected schema
            logger.info("Please create the 'document_embeddings' table in Supabase with the following schema:")
            logger.info("""
            CREATE TABLE document_embeddings (
                id SERIAL PRIMARY KEY,
                document_name TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                chunks TEXT NOT NULL,
                embeddings TEXT NOT NULL,
                chunk_count INTEGER NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                UNIQUE(document_name, content_hash)
            );
            """)
            return True
        except Exception as e:
            logger.error(f"Error with table creation info: {str(e)}")
            return False
