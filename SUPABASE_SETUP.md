# Supabase Setup for Embedding Cache

## 1. Create Supabase Project
1. Go to [supabase.com](https://supabase.com) and create a new project
2. Get your project URL and anon key from Settings > API

## 2. Create Database Table
Run this SQL in your Supabase SQL editor:

```sql
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

-- Create an index for faster lookups
CREATE INDEX idx_document_embeddings_lookup ON document_embeddings(document_name, content_hash);
```

## 3. Configure Environment Variables
Add these to your environment or `.streamlit/secrets.toml`:

```toml
SUPABASE_URL = "your-project-url"
SUPABASE_ANON_KEY = "your-anon-key"
OPENAI_API_KEY = "your-openai-key"
```

## 4. Benefits
- ✅ Embeddings are calculated only once per document
- ✅ Massive cost savings on OpenAI API calls
- ✅ Much faster response times for repeated queries
- ✅ Automatic cache invalidation when document content changes

## 5. Fallback Behavior
If Supabase is not configured, the system will:
- Generate embeddings fresh each time
- Show a warning in the UI
- Continue to work normally (just slower and more expensive)
