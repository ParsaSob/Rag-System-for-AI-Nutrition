from langchain.text_splitter import RecursiveCharacterTextSplitter
from src.config import CHUNK_SIZE, CHUNK_OVERLAP, DATA_DIR, DOCUMENTS
from src.llm import LLMService
from src.supabase_service import SupabaseService
import numpy as np
from typing import List, Tuple, Dict
import logging
import pandas as pd
import asyncio
from src.utils import count_tokens

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Handles document processing and chunking."""
    
    def __init__(self):
        """Initialize the document processor."""
        self.chunks = []
        self.chunk_embeddings = []
        self.current_document = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        self.llm_service = LLMService()
        self.supabase_service = SupabaseService()

    def load_pdf(self, document_name: str):
        """Load and extract text from PDF file."""
        try:
            try:
                import pymupdf as fitz  # Lazy import to avoid startup failure when not needed
            except Exception:
                raise Exception("PDF support is unavailable. Please install PyMuPDF to load PDFs.")
            if document_name not in DOCUMENTS:
                raise ValueError(f"Document {document_name} not found")
            
            pdf_path = DATA_DIR / DOCUMENTS[document_name]
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            logger.error(f"Error loading PDF: {str(e)}")
            raise Exception(f"Error loading PDF: {str(e)}")

    def load_excel(self, document_name: str):
        """Load and extract tables from all sheets in an Excel file as text chunks."""
        try:
            if document_name not in DOCUMENTS:
                raise ValueError(f"Document {document_name} not found")
            excel_path = DATA_DIR / DOCUMENTS[document_name]
            xls = pd.ExcelFile(excel_path)
            text_chunks = []
            for sheet_name in xls.sheet_names:
                df_dict = pd.read_excel(xls, sheet_name=sheet_name, header=None)
                # If the sheet is empty, skip
                if df_dict.empty:
                    continue
                # Try to split into tables by blank rows
                tables = []
                current_table = []
                for _, row in df_dict.iterrows():
                    if row.isnull().all():
                        if current_table:
                            tables.append(current_table)
                            current_table = []
                    else:
                        current_table.append(row.tolist())
                if current_table:
                    tables.append(current_table)
                # Convert each table to string
                for table in tables:
                    if not table:
                        continue
                    table_df = pd.DataFrame(table)
                    chunk_text = f"Sheet: {sheet_name}\n" + table_df.to_string(index=False, header=False)
                    text_chunks.append(chunk_text)
            return text_chunks
        except Exception as e:
            logger.error(f"Error loading Excel: {str(e)}")
            raise Exception(f"Error loading Excel: {str(e)}")

    def load_csv(self, document_name: str):
        """Load and chunk a CSV file into manageable text chunks with robust encoding detection."""
        try:
            if document_name not in DOCUMENTS:
                raise ValueError(f"Document {document_name} not found")
            csv_path = DATA_DIR / DOCUMENTS[document_name]
            
            # Try multiple encodings and separators
            encodings = ['utf-8', 'utf-8-sig', 'cp1256', 'cp1252', 'latin-1']
            separators = [None, ',', ';', '\t']  # None uses pandas auto-detection
            
            df = None
            for encoding in encodings:
                for sep in separators:
                    try:
                        if sep is None:
                            # Use pandas auto-detection with python engine
                            df = pd.read_csv(csv_path, encoding=encoding, sep=None, engine='python')
                        else:
                            df = pd.read_csv(csv_path, encoding=encoding, sep=sep)
                        
                        if not df.empty and len(df.columns) > 1:
                            logger.info(f"Successfully loaded CSV with encoding={encoding}, sep={sep}")
                            break
                    except Exception:
                        continue
                if df is not None and not df.empty:
                    break
            
            if df is None or df.empty:
                logger.warning(f"Could not load CSV file {document_name} with any encoding/separator combination")
                return []
            
            # Chunk rows into approximately CHUNK_SIZE-character chunks
            text_chunks = []
            start = 0
            total_rows = len(df)
            # Start with a heuristic of rows per chunk and adjust by length
            rows_per_chunk = max(10, min(100, CHUNK_SIZE // 50))
            while start < total_rows:
                end = min(total_rows, start + rows_per_chunk)
                part_df = df.iloc[start:end]
                chunk_text = (
                    f"CSV: {document_name} | Rows {start + 1}-{end}\n" +
                    part_df.to_string(index=False)
                )
                text_chunks.append(chunk_text)
                start = end
            return text_chunks
        except Exception as e:
            logger.error(f"Error loading CSV: {str(e)}")
            raise Exception(f"Error loading CSV: {str(e)}")

    def process_document(self, document_name: str):
        """Process the document (PDF or Excel) and create text chunks with embeddings."""
        if self.current_document != document_name:
            try:
                from src.config import DOCUMENTS
                file_ext = DOCUMENTS[document_name].split('.')[-1].lower()
                
                # Load document chunks
                if file_ext == 'pdf':
                    text = self.load_pdf(document_name)
                    self.chunks = self.text_splitter.split_text(text)
                elif file_ext == 'xlsx':
                    self.chunks = self.load_excel(document_name)
                elif file_ext == 'csv':
                    self.chunks = self.load_csv(document_name)
                else:
                    raise ValueError(f"Unsupported file type: {file_ext}")
                
                # Try to get cached embeddings first
                cached_data = None
                logger.info(f"Checking Supabase cache for document: {document_name}")
                logger.info(f"Supabase available: {self.supabase_service.is_available()}")
                
                if self.supabase_service.is_available():
                    try:
                        # Test connection first
                        connection_ok = self.supabase_service.test_connection()
                        logger.info(f"Supabase connection test: {connection_ok}")
                        
                        if connection_ok:
                            cached_data = asyncio.run(
                                self.supabase_service.get_cached_embeddings(document_name, self.chunks)
                            )
                        else:
                            logger.warning("Supabase connection failed, skipping cache retrieval")
                    except Exception as e:
                        logger.warning(f"Failed to retrieve cached embeddings: {str(e)}")
                
                if cached_data:
                    # Use cached embeddings
                    self.chunks = cached_data['chunks']
                    self.chunk_embeddings = cached_data['embeddings']
                    logger.info(f"Using cached embeddings for document {document_name} with {len(self.chunks)} chunks")
                else:
                    # Generate new embeddings
                    logger.info(f"Generating new embeddings for document {document_name}...")
                    embeddings = self.llm_service.get_embeddings()
                    self.chunk_embeddings = embeddings.embed_documents(self.chunks)
                    
                    # Cache the new embeddings
                    logger.info(f"Attempting to cache embeddings for document: {document_name}")
                    if self.supabase_service.is_available():
                        try:
                            # Test connection before caching
                            connection_ok = self.supabase_service.test_connection()
                            logger.info(f"Supabase connection test before caching: {connection_ok}")
                            
                            if connection_ok:
                                logger.info(f"Caching {len(self.chunks)} chunks with {len(self.chunk_embeddings)} embeddings")
                                success = asyncio.run(
                                    self.supabase_service.cache_embeddings(
                                        document_name, self.chunks, self.chunk_embeddings
                                    )
                                )
                                if success:
                                    logger.info(f"✅ Successfully cached embeddings for document {document_name}")
                                else:
                                    logger.warning(f"❌ Failed to cache embeddings for document {document_name}")
                            else:
                                logger.warning("Supabase connection failed, skipping cache storage")
                        except Exception as e:
                            logger.warning(f"Error caching embeddings: {str(e)}")
                    else:
                        logger.warning("Supabase service not available for caching")
                
                self.current_document = document_name
                logger.info(f"Successfully processed document {document_name} with {len(self.chunks)} chunks")
            except Exception as e:
                logger.error(f"Error processing document: {str(e)}")
                raise Exception(f"Error processing document: {str(e)}")
        return self.chunks

    def get_chunks(self, document_name: str):
        """Get the processed text chunks."""
        if self.current_document != document_name:
            self.process_document(document_name)
        return self.chunks

    def get_most_relevant_chunks(self, query: str, document_name: str, top_k: int = 3) -> List[Dict[str, any]]:
        """Get the most relevant chunks for a query using cosine similarity. Limit to top_k (default 3). Each chunk is truncated to 500 tokens if needed."""
        if self.current_document != document_name or self.chunks is None or self.chunk_embeddings is None:
            self.process_document(document_name)

        try:
            # Get query embedding
            embeddings = self.llm_service.get_embeddings()
            query_embedding = embeddings.embed_query(query)

            # Calculate cosine similarities
            similarities = []
            for chunk_embedding in self.chunk_embeddings:
                similarity = self._cosine_similarity(query_embedding, chunk_embedding)
                similarities.append(similarity)

            # Get top k chunks with their similarity scores
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            results = []
            for idx in top_indices:
                chunk_text = self.chunks[idx]
                # Truncate chunk to 500 tokens if needed
                if count_tokens(chunk_text) > 500:
                    # Approximate truncation by words (for safety)
                    words = chunk_text.split()
                    chunk_text = ' '.join(words[:500])
                results.append({
                    "chunk": chunk_text,
                    "similarity": similarities[idx]
                })
            return results[:top_k]
        except Exception as e:
            logger.error(f"Error in semantic search: {str(e)}")
            raise Exception(f"Error in semantic search: {str(e)}")

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        try:
            vec1 = np.array(vec1)
            vec2 = np.array(vec2)
            return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))
        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {str(e)}")
            return 0.0 