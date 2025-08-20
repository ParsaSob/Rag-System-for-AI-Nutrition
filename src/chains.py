from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from src.config import QA_TEMPLATE
from src.llm import LLMService

class ChainService:
    def __init__(self):
        self.llm_service = LLMService()
        self.memory = None
        self.qa_chain = None

    def _initialize_chains(self):
        """Initialize conversation memory and QA chain lazily."""
        try:
            if self.memory is None:
                self.memory = ConversationBufferMemory(
                    memory_key="chat_history",
                    return_messages=True
                )
            if self.qa_chain is None:
                qa_prompt = PromptTemplate(
                    template=QA_TEMPLATE,
                    input_variables=["context", "question"]
                )
                self.qa_chain = LLMChain(
                    llm=self.llm_service.get_chat_model(),
                    prompt=qa_prompt
                )
        except Exception as e:
            # Bubble up so UI can show a readable error (e.g., missing API key)
            raise Exception(f"Error initializing chains: {str(e)}")

    def get_memory(self):
        """Get the conversation memory."""
        if self.memory is None:
            try:
                self._initialize_chains()
            except Exception:
                # Return a fresh memory even if QA chain failed (e.g., no API key)
                self.memory = ConversationBufferMemory(
                    memory_key="chat_history",
                    return_messages=True
                )
        return self.memory

    def get_qa_chain(self):
        """Get the QA chain."""
        if self.qa_chain is None:
            self._initialize_chains()
        return self.qa_chain 