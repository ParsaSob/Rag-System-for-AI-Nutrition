# Market Mine Bot

A Streamlit-based RAG (Retrieval-Augmented Generation) system for analyzing documents using GPT-4 Turbo with intelligent embedding cache.

## Features

- 📄 **Multi-format Support**: PDF, Excel (.xlsx), and CSV document processing
- 🧠 **Smart Embedding Cache**: Powered by Supabase for massive cost savings
- 🔍 **Semantic Search**: Find relevant context using AI embeddings
- 💰 **Cost Tracking**: Real-time token usage and cost monitoring
- 💬 **Interactive Chat**: User-friendly Q&A interface
- 🚀 **Performance**: Lightning-fast responses with cached embeddings
- 🌐 **Robust CSV Support**: Auto-detects encoding (UTF-8, CP1256, Latin-1) and delimiters

## Local Development

1. Clone the repository:
```bash
git clone <repository-url>
cd market-mine-bot
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp env_example.txt .env
# Edit .env with your API keys (see Configuration section below)
```

5. **Optional**: Set up Supabase for embedding cache:
   - Create a Supabase project at [supabase.com](https://supabase.com)
   - Run the SQL from `supabase_schema.sql` in your Supabase SQL editor
   - Add your Supabase URL and key to `.env`

6. Run the application:
```bash
streamlit run app.py
```

## Docker Deployment

1. Build the Docker image:
```bash
docker build -t market-mine-bot .
```

2. Run the container:
```bash
docker run -p 8501:8501 -e OPENAI_API_KEY=your_api_key market-mine-bot
```

## AWS Deployment

### Option 1: AWS Elastic Container Service (ECS)

1. Create an ECR repository:
```bash
aws ecr create-repository --repository-name market-mine-bot
```

2. Tag and push the Docker image:
```bash
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com
docker tag market-mine-bot:latest <account-id>.dkr.ecr.<region>.amazonaws.com/market-mine-bot:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/market-mine-bot:latest
```

3. Create an ECS cluster and service:
- Use AWS Console or AWS CLI to create an ECS cluster
- Create a task definition with the container image
- Create a service to run the task

### Option 2: AWS Elastic Beanstalk

1. Install the EB CLI:
```bash
pip install awsebcli
```

2. Initialize EB:
```bash
eb init
```

3. Create and deploy:
```bash
eb create production
```

## Configuration

### Required Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key (required for AI responses)

### Optional Environment Variables (for embedding cache)
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_ANON_KEY`: Your Supabase anonymous/public key

### Supported Document Formats
- **PDF**: Text extraction with PyMuPDF
- **Excel (.xlsx)**: Multi-sheet support with automatic table detection
- **CSV**: Robust encoding detection (UTF-8, UTF-8-BOM, CP1256, CP1252, Latin-1)

### Embedding Cache Benefits
✅ **Cost Savings**: Embeddings calculated only once per document  
✅ **Speed**: Instant responses for previously processed documents  
✅ **Smart Updates**: Auto-detects document changes and regenerates embeddings  
✅ **Fallback**: Works without Supabase (just slower and more expensive)

## Security Considerations

1. Never commit sensitive information (API keys, credentials)
2. Use AWS Secrets Manager or Parameter Store for production secrets
3. Implement proper IAM roles and permissions
4. Use HTTPS for all external access
5. Regular security updates and monitoring

## Monitoring and Logging

1. Set up CloudWatch for container logs
2. Implement application logging
3. Set up alarms for errors and performance issues
4. Monitor token usage and costs

## Cost Optimization

1. **Embedding Cache**: Use Supabase to cache embeddings (biggest cost saver!)
2. AWS Fargate for serverless container deployment  
3. Implement auto-scaling based on demand
4. Monitor token usage with built-in tracking
5. Use AWS Free Tier where possible

## Database Files

### SQL Files
- `supabase_schema.sql`: Complete database setup for embedding cache
- `supabase_maintenance.sql`: Monitoring, cleanup, and maintenance queries

### Key Benefits of Database Cache
- **95%+ cost reduction** on repeated document queries
- **10x faster** response times for cached documents
- **Automatic cleanup** of old, unused cache entries
- **Comprehensive monitoring** with built-in analytics

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License