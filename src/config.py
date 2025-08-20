import os
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st

# Load environment variables from .env file (for local development)
load_dotenv()

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"

def get_available_documents():
    """Automatically detect and load PDF and Excel documents from the data directory."""
    documents = {}
    # Add PDFs
    for pdf_file in DATA_DIR.glob("*.pdf"):
        if pdf_file.name.startswith((".", "_")):
            continue
        display_name = pdf_file.stem
        documents[display_name] = pdf_file.name
    # Add Excels
    for excel_file in DATA_DIR.glob("*.xlsx"):
        if excel_file.name.startswith((".", "_", "~$")):
            continue
        display_name = excel_file.stem
        documents[display_name] = excel_file.name
    # Add CSVs
    for csv_file in DATA_DIR.glob("*.csv"):
        if csv_file.name.startswith((".", "_")):
            continue
        display_name = csv_file.stem
        documents[display_name] = csv_file.name
    return documents

# Available documents - automatically loaded from data directory
DOCUMENTS = get_available_documents()

# OpenAI Configuration (do not hard-fail; allow UI to load without key)
# Try to get API key from environment variable first
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# If not in environment variables, try to get from Streamlit secrets
if not OPENAI_API_KEY:
    try:
        OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", None)
    except Exception:
        OPENAI_API_KEY = None

OPENAI_MODEL = "gpt-4-turbo-preview"
OPENAI_TEMPERATURE = 0.7

# Supabase Configuration for embedding cache
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
if not SUPABASE_URL:
    try:
        SUPABASE_URL = st.secrets.get("SUPABASE_URL", None)
    except Exception:
        SUPABASE_URL = None
if not SUPABASE_KEY:
    try:
        SUPABASE_KEY = st.secrets.get("SUPABASE_ANON_KEY", None)
    except Exception:
        SUPABASE_KEY = None

# Document Processing
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Chain Configuration
QA_TEMPLATE = """You are a helpful AI assistant that can both answer questions about food and nutrition data AND provide meal recommendations. Use the following pieces of context to answer the question at the end.

**For General Questions:**
1. Always cite specific data sources when referencing nutritional information
2. If you don't know the answer, say so clearly
3. Use exact values from the provided context

**For Meal Recommendations:**
If the question asks for meal suggestions or recommendations, follow this format:
1. Analyze user requirements (age, gender, activity, diet goals, restrictions)
2. Use ONLY ingredients found in the provided context
3. Calculate precise nutritional values
4. Return recommendations in JSON format with exact ingredient amounts

**Context (Food Database):**
{context}

**Question:** {question}

**Answer:**"""

# UI Configuration
APP_TITLE = "🍽️ Smart Nutrition & Meal Planning Assistant"
APP_DESCRIPTION = """
Your AI-powered nutrition consultant! Upload your food database (CSV, Excel, or PDF) and get:
• **Nutritional Information**: Ask about calories, macros, and ingredients
• **Meal Recommendations**: Get personalized meal suggestions based on your profile
• **Diet Planning**: Tailored advice for your health goals and dietary restrictions

Select your food database documents and start asking questions or requesting meal plans!
""" 