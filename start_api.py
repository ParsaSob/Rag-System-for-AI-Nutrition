"""
Startup script for Smart Nutrition API
"""
import uvicorn
import sys
import os
from pathlib import Path

def check_requirements():
    """Check if all required files and configurations are present."""
    print("🔍 Checking requirements...")
    
    # Check data directory
    data_dir = Path("data")
    if not data_dir.exists():
        print("❌ Error: 'data' directory not found. Please create it and add your CSV/Excel files.")
        return False
    
    # Check for data files
    data_files = list(data_dir.glob("*.csv")) + list(data_dir.glob("*.xlsx"))
    if not data_files:
        print("❌ Error: No CSV or Excel files found in 'data' directory.")
        print("   Please add your food database files.")
        return False
    
    print(f"✅ Found {len(data_files)} data files:")
    for file in data_files:
        print(f"   - {file.name}")
    
    # Check environment variables
    required_env = ["OPENAI_API_KEY"]
    missing_env = []
    
    for env_var in required_env:
        if not os.getenv(env_var):
            missing_env.append(env_var)
    
    if missing_env:
        print(f"⚠️ Warning: Missing environment variables: {', '.join(missing_env)}")
        print("   The API will work but AI features may be limited.")
    else:
        print("✅ All required environment variables found.")
    
    # Check optional Supabase
    supabase_vars = ["SUPABASE_URL", "SUPABASE_ANON_KEY"]
    supabase_configured = all(os.getenv(var) for var in supabase_vars)
    
    if supabase_configured:
        print("✅ Supabase configured - embedding cache enabled.")
    else:
        print("💡 Supabase not configured - embeddings will be recalculated each time.")
    
    return True

def start_api(host="0.0.0.0", port=8000, reload=True):
    """Start the FastAPI server."""
    
    if not check_requirements():
        print("\\n❌ Requirements check failed. Please fix the issues above.")
        sys.exit(1)
    
    print(f"\\n🚀 Starting Smart Nutrition API...")
    print(f"📍 Server: http://{host}:{port}")
    print(f"📚 Documentation: http://{host}:{port}/docs")
    print(f"🔍 Alternative docs: http://{host}:{port}/redoc")
    print(f"\\n🔑 Demo API Keys:")
    print(f"   - demo-key-12345")
    print(f"   - nutrition-api-67890")
    print(f"\\n📖 Usage examples available in 'api_examples.py'")
    print(f"\\n🛑 Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        uvicorn.run(
            "api_server:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\\n\\n🛑 Server stopped by user.")
    except Exception as e:
        print(f"\\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Start Smart Nutrition API")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to (default: 8000)")
    parser.add_argument("--no-reload", action="store_true", help="Disable auto-reload")
    
    args = parser.parse_args()
    
    start_api(
        host=args.host,
        port=args.port,
        reload=not args.no_reload
    )

