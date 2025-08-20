from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from src.config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE

class LLMService:
    def __init__(self):
        self.chat_model = None
        self.embeddings = None

    def _initialize_services(self):
        """Initialize OpenAI chat model and embeddings lazily when API key is available."""
        if not OPENAI_API_KEY:
            raise Exception("OPENAI_API_KEY is not set. Please configure it in environment variables or Streamlit secrets.")
        try:
            if self.chat_model is None:
                self.chat_model = ChatOpenAI(
                    model=OPENAI_MODEL,
                    temperature=OPENAI_TEMPERATURE,
                    api_key=OPENAI_API_KEY
                )
            if self.embeddings is None:
                self.embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
        except Exception as e:
            raise Exception(f"Error initializing LLM services: {str(e)}")

    def get_chat_model(self):
        """Get the initialized chat model."""
        if self.chat_model is None:
            self._initialize_services()
        return self.chat_model

    def get_embeddings(self):
        """Get the initialized embeddings model."""
        if self.embeddings is None:
            self._initialize_services()
        return self.embeddings 