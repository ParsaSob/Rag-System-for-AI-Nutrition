import streamlit as st
from src.config import APP_TITLE, APP_DESCRIPTION, DOCUMENTS, OPENAI_API_KEY, SUPABASE_URL, SUPABASE_KEY
from src.document_processor import DocumentProcessor
from src.chains import ChainService
from src.utils import count_tokens, estimate_cost, format_token_info
import plotly.graph_objects as go
import numpy as np

class UI:
    def __init__(self):
        self.document_processor = DocumentProcessor()
        self.chain_service = ChainService()
        self._initialize_session_state()

    def _initialize_session_state(self):
        """Initialize session state variables."""
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "context" not in st.session_state:
            st.session_state.context = ""
        if "last_search_results" not in st.session_state:
            st.session_state.last_search_results = None
        if "total_input_tokens" not in st.session_state:
            st.session_state.total_input_tokens = 0
        if "total_output_tokens" not in st.session_state:
            st.session_state.total_output_tokens = 0
        if "total_cost" not in st.session_state:
            st.session_state.total_cost = 0.0
        if "selected_documents" not in st.session_state:
            st.session_state.selected_documents = list(DOCUMENTS.keys())

    def setup_page(self):
        """Setup the Streamlit page configuration."""
        st.title(APP_TITLE)
        st.write(APP_DESCRIPTION)
        
        # Show configuration status
        col1, col2 = st.columns(2)
        with col1:
            if not OPENAI_API_KEY:
                st.warning("⚠️ OPENAI_API_KEY تنظیم نشده است. برای پاسخ‌دهی مدل، کلید را در محیط یا Streamlit secrets قرار دهید.")
            else:
                st.success("✅ OpenAI API configured")
        
        with col2:
            if not SUPABASE_URL or not SUPABASE_KEY:
                st.info("💡 Supabase غیرفعال است. embedding ها کش نمی‌شوند و هر بار دوباره محاسبه می‌شوند.")
            else:
                st.success("✅ Supabase cache enabled")
        
        # Create a container for document selection
        with st.container():
            st.write("#### Select documents to analyze:")
            # Add "Select All" checkbox
            select_all = st.checkbox("Select All", value=True, key="select_all")
            
            # Create individual checkboxes for each document
            selected_docs = []
            for doc in DOCUMENTS.keys():
                if select_all:
                    is_selected = st.checkbox(doc, value=True, key=f"doc_{doc}")
                else:
                    is_selected = st.checkbox(doc, value=False, key=f"doc_{doc}")
                if is_selected:
                    selected_docs.append(doc)
            
            st.session_state.selected_documents = selected_docs
            
            if not st.session_state.selected_documents:
                st.warning("Please select at least one document to continue.")
        
        # Display total usage statistics in the sidebar
        st.sidebar.markdown("### Usage Statistics")
        if st.session_state.total_input_tokens > 0:
            costs = estimate_cost(
                st.session_state.total_input_tokens,
                st.session_state.total_output_tokens
            )
            st.sidebar.markdown(format_token_info(
                st.session_state.total_input_tokens,
                st.session_state.total_output_tokens,
                costs
            ))
        else:
            st.sidebar.markdown("No usage statistics yet.")

    def display_chat_history(self):
        """Display the chat history."""
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if "token_info" in message:
                    st.markdown("---")
                    st.markdown("**Token Usage & Cost:**")
                    st.markdown(f'<div style="font-size: 0.8em">{message["token_info"]}</div>', unsafe_allow_html=True)

    def display_search_results(self, search_results):
        """Display the semantic search results with similarity scores."""
        if not search_results:
            return

        # Create a bar chart of similarity scores
        similarities = [result["similarity"] for result in search_results]
        chunks = [f"{result['document']} - Chunk {i+1}" for i, result in enumerate(search_results)]
        
        fig = go.Figure(data=[
            go.Bar(
                x=chunks,
                y=similarities,
                text=[f"{score:.3f}" for score in similarities],
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title="Semantic Search Results - Similarity Scores",
            xaxis_title="Document Chunks",
            yaxis_title="Cosine Similarity",
            yaxis_range=[0, 1],
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)

        # Display the chunks with their similarity scores
        st.subheader("Relevant Document Chunks")
        for i, result in enumerate(search_results, 1):
            with st.expander(f"{result['document']} - Chunk {i} (Similarity: {result['similarity']:.3f})"):
                st.markdown(result["chunk"])

    def handle_user_input(self, user_question):
        """Handle user input and generate response."""
        try:
            if not st.session_state.selected_documents:
                raise ValueError("Please select at least one document to analyze.")

            # Get relevant context using semantic search from all selected documents
            all_search_results = []
            for doc in st.session_state.selected_documents:
                results = self.document_processor.get_most_relevant_chunks(
                    user_question,
                    doc
                )
                # Add document name to each result
                for result in results:
                    result["document"] = doc
                all_search_results.extend(results)

            # Sort by similarity and take top results
            all_search_results.sort(key=lambda x: x["similarity"], reverse=True)
            # Limit the number of chunks by total token count and dynamically set chunk count
            MAX_CONTEXT_TOKENS = 5000  # Updated for your requirement
            MAX_CHUNKS = len(st.session_state.selected_documents) * 3  # 3 is top_k in processor
            context_chunks = []
            total_tokens = 0
            for result in all_search_results:
                if len(context_chunks) >= MAX_CHUNKS:
                    break
                chunk_tokens = count_tokens(result["chunk"])
                if total_tokens + chunk_tokens > MAX_CONTEXT_TOKENS:
                    break
                context_chunks.append(f"From {result['document']}:\n{result['chunk']}")
                total_tokens += chunk_tokens
            # Debug print for context size and token count
            print(f"DEBUG: Context length (chars): {len(''.join(context_chunks))}")
            print(f"DEBUG: Context token estimate: {count_tokens(''.join(context_chunks))}")
            print(f"DEBUG: Chunks sent: {len(context_chunks)}")
            st.session_state.last_search_results = all_search_results[:len(context_chunks)]
            # Extract just the chunks for the context
            context = "\n\n".join(context_chunks)
            st.session_state.context = context

            # HARD CAP: Truncate context if token count exceeds limit
            ACTUAL_TOKEN_COUNT = count_tokens(context)
            print(f"DEBUG: Final context token count before LLM: {ACTUAL_TOKEN_COUNT}")
            print(f"DEBUG: Final context length (chars): {len(context)}")
            if ACTUAL_TOKEN_COUNT > MAX_CONTEXT_TOKENS:
                # Truncate context to fit within token limit (approximate by chars)
                avg_token_len = max(1, len(context) // ACTUAL_TOKEN_COUNT)
                max_chars = MAX_CONTEXT_TOKENS * avg_token_len
                context = context[:max_chars]
                print(f"DEBUG: Context truncated to {len(context)} chars to fit token limit.")
            # Absolute hard character cap
            if len(context) > 10000:
                context = context[:10000]
                print(f"DEBUG: Context truncated to 10000 chars as absolute hard cap.")

            # Get QA chain and memory
            qa_chain = self.chain_service.get_qa_chain()
            memory = self.chain_service.get_memory()

            # Generate response
            response = qa_chain.run(
                context=context,
                question=user_question
            )

            # Update memory
            memory.save_context({"input": user_question}, {"output": response})

            # Calculate token usage and costs
            input_tokens = count_tokens(context + "\n" + user_question)
            output_tokens = count_tokens(response)
            costs = estimate_cost(input_tokens, output_tokens)
            
            # Update total usage
            st.session_state.total_input_tokens += input_tokens
            st.session_state.total_output_tokens += output_tokens
            st.session_state.total_cost += costs["total_cost"]

            return response, format_token_info(input_tokens, output_tokens, costs)
        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
            return None, None

    def run(self):
        """Run the Streamlit UI."""
        self.setup_page()
        self.display_chat_history()

        # Chat input
        if not st.session_state.selected_documents:
            st.info("Please select at least one document above to start chatting.")
            return

        doc_names = ", ".join(st.session_state.selected_documents)
        if prompt := st.chat_input(f"Ask a question about: {doc_names}"):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Generate and display assistant response
            with st.chat_message("assistant"):
                response, token_info = self.handle_user_input(prompt)
                if response:
                    st.markdown(response)
                    st.markdown("---")
                    st.markdown("**Token Usage & Cost:**")
                    st.markdown(f'<div style="font-size: 0.8em">{token_info}</div>', unsafe_allow_html=True)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response,
                        "token_info": token_info
                    })
                    
                    # Display search results after the response
                    if st.session_state.last_search_results:
                        st.divider()
                        self.display_search_results(st.session_state.last_search_results)

if __name__ == "__main__":
    ui = UI()
    ui.run()