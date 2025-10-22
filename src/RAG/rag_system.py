"""
RAG (Retrieval-Augmented Generation) System for Anime Script Processing

This module implements a basic RAG system that:
1. Processes PDF anime scripts and creates embeddings
2. Stores embeddings in a vector database (FAISS)
3. Retrieves relevant context for video generation prompts
"""

import os
import numpy as np
import faiss
import pickle
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from sentence_transformers import SentenceTransformer
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnimeScriptRAG:
    """
    RAG system specifically designed for anime script processing and video generation.
    """
    
    def __init__(self, 
                 embedding_model: str = "all-MiniLM-L6-v2",
                 chunk_size: int = 512,
                 chunk_overlap: int = 50,
                 vector_db_path: str = "rag_vector_db"):
        """
        Initialize the RAG system.
        
        Args:
            embedding_model: Name of the sentence transformer model
            chunk_size: Size of text chunks for processing
            chunk_overlap: Overlap between consecutive chunks
            vector_db_path: Path to store vector database files
        """
        self.embedding_model_name = embedding_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.vector_db_path = Path(vector_db_path)
        self.vector_db_path.mkdir(exist_ok=True)
        
        # Initialize embedding model
        logger.info(f"Loading embedding model: {embedding_model}")
        self.embedding_model = SentenceTransformer(embedding_model)
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
        
        # Initialize FAISS index
        self.index = None
        self.chunks = []
        self.metadata = []
        
        # Try to load existing index
        self._load_existing_index()
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from PDF file or text file.
        
        Args:
            pdf_path: Path to the PDF or text file
            
        Returns:
            Extracted text content
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"File not found: {pdf_path}")
        
        file_path = Path(pdf_path)
        
        # Handle text files
        if file_path.suffix.lower() in ['.txt', '.md']:
            try:
                with open(pdf_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                logger.info(f"Successfully extracted text from {file_path.name}")
                return text
            except Exception as e:
                logger.error(f"Error reading text file: {e}")
                raise
        
        # Handle PDF files
        try:
            import fitz
            doc = fitz.open(pdf_path)
            full_text = ""
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                full_text += f"\n--- PAGE {page_num + 1} ---\n{text}"
            
            doc.close()
            logger.info(f"Successfully extracted text from {file_path.name}")
            return full_text
            
        except ImportError:
            logger.error("PyMuPDF not available. Please install it with: pip install PyMuPDF")
            raise ImportError("PyMuPDF is required for PDF processing. Install with: pip install PyMuPDF")
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise
    
    def chunk_text(self, text: str, source_info: Dict) -> List[Dict]:
        """
        Split text into overlapping chunks with metadata.
        
        Args:
            text: Input text to chunk
            source_info: Metadata about the source document
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        # Simple word-based chunking
        words = text.split()
        chunks = []
        
        start_idx = 0
        chunk_id = 0
        
        while start_idx < len(words):
            end_idx = min(start_idx + self.chunk_size, len(words))
            chunk_words = words[start_idx:end_idx]
            chunk_text = " ".join(chunk_words)
            
            chunk_metadata = {
                "chunk_id": chunk_id,
                "start_word": start_idx,
                "end_word": end_idx,
                "source": source_info,
                "timestamp": datetime.now().isoformat(),
                "chunk_size": len(chunk_words)
            }
            
            chunks.append({
                "text": chunk_text,
                "metadata": chunk_metadata
            })
            
            chunk_id += 1
            start_idx += self.chunk_size - self.chunk_overlap
        
        logger.info(f"Created {len(chunks)} chunks from text")
        return chunks
    
    def generate_embeddings(self, chunks: List[Dict]) -> np.ndarray:
        """
        Generate embeddings for text chunks.
        
        Args:
            chunks: List of chunk dictionaries
            
        Returns:
            Numpy array of embeddings
        """
        texts = [chunk["text"] for chunk in chunks]
        logger.info(f"Generating embeddings for {len(texts)} chunks")
        
        embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
        return embeddings
    
    def create_vector_index(self, embeddings: np.ndarray, chunks: List[Dict]):
        """
        Create FAISS vector index from embeddings.
        
        Args:
            embeddings: Numpy array of embeddings
            chunks: List of chunk dictionaries
        """
        # Create FAISS index
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        
        # Add embeddings to index
        self.index.add(embeddings.astype('float32'))
        
        # Store chunks and metadata
        self.chunks = chunks
        self.metadata = [chunk["metadata"] for chunk in chunks]
        
        logger.info(f"Created FAISS index with {self.index.ntotal} vectors")
    
    def save_vector_db(self):
        """Save the vector database to disk."""
        if self.index is None:
            logger.warning("No index to save")
            return
        
        # Save FAISS index
        index_path = self.vector_db_path / "faiss_index.bin"
        faiss.write_index(self.index, str(index_path))
        
        # Save chunks and metadata
        chunks_path = self.vector_db_path / "chunks.pkl"
        with open(chunks_path, 'wb') as f:
            pickle.dump(self.chunks, f)
        
        metadata_path = self.vector_db_path / "metadata.pkl"
        with open(metadata_path, 'wb') as f:
            pickle.dump(self.metadata, f)
        
        # Save configuration
        config = {
            "embedding_model": self.embedding_model_name,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "embedding_dim": self.embedding_dim,
            "num_vectors": self.index.ntotal,
            "created_at": datetime.now().isoformat()
        }
        
        config_path = self.vector_db_path / "config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Vector database saved to {self.vector_db_path}")
    
    def _load_existing_index(self):
        """Load existing vector database if available."""
        index_path = self.vector_db_path / "faiss_index.bin"
        chunks_path = self.vector_db_path / "chunks.pkl"
        metadata_path = self.vector_db_path / "metadata.pkl"
        config_path = self.vector_db_path / "config.json"
        
        if all(path.exists() for path in [index_path, chunks_path, metadata_path, config_path]):
            try:
                # Load FAISS index
                self.index = faiss.read_index(str(index_path))
                
                # Load chunks and metadata
                with open(chunks_path, 'rb') as f:
                    self.chunks = pickle.load(f)
                
                with open(metadata_path, 'rb') as f:
                    self.metadata = pickle.load(f)
                
                # Load config
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                logger.info(f"Loaded existing vector database with {self.index.ntotal} vectors")
                
            except Exception as e:
                logger.error(f"Error loading existing index: {e}")
                self.index = None
                self.chunks = []
                self.metadata = []
    
    def add_pdf_to_rag(self, pdf_path: str, source_name: Optional[str] = None) -> bool:
        """
        Add a PDF script to the RAG system.
        
        Args:
            pdf_path: Path to the PDF file
            source_name: Optional name for the source (defaults to PDF filename)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if source_name is None:
                source_name = Path(pdf_path).stem
            
            # Extract text
            text = self.extract_text_from_pdf(pdf_path)
            
            # Create source info
            source_info = {
                "name": source_name,
                "path": pdf_path,
                "type": "anime_script",
                "added_at": datetime.now().isoformat()
            }
            
            # Chunk text
            new_chunks = self.chunk_text(text, source_info)
            
            # Generate embeddings
            new_embeddings = self.generate_embeddings(new_chunks)
            
            # Add to existing index or create new one
            if self.index is None:
                self.create_vector_index(new_embeddings, new_chunks)
            else:
                # Add to existing index
                self.index.add(new_embeddings.astype('float32'))
                self.chunks.extend(new_chunks)
                self.metadata.extend([chunk["metadata"] for chunk in new_chunks])
                logger.info(f"Added {len(new_chunks)} new chunks to existing index")
            
            # Save updated database
            self.save_vector_db()
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding PDF to RAG: {e}")
            return False
    
    def retrieve_relevant_context(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Retrieve relevant context for a given query.
        
        Args:
            query: Search query
            top_k: Number of top results to return
            
        Returns:
            List of relevant chunks with metadata
        """
        if self.index is None:
            logger.warning("No vector database loaded")
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])
            
            # Search for similar vectors
            distances, indices = self.index.search(query_embedding.astype('float32'), top_k)
            
            # Retrieve relevant chunks
            relevant_chunks = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < len(self.chunks):
                    chunk_info = {
                        "rank": i + 1,
                        "similarity_score": float(1 / (1 + distance)),  # Convert distance to similarity
                        "text": self.chunks[idx]["text"],
                        "metadata": self.chunks[idx]["metadata"]
                    }
                    relevant_chunks.append(chunk_info)
            
            logger.info(f"Retrieved {len(relevant_chunks)} relevant chunks for query")
            return relevant_chunks
            
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return []
    
    def get_rag_context_for_prompt(self, prompt: str, max_context_length: int = 2000) -> str:
        """
        Get formatted RAG context for video generation prompts.
        
        Args:
            prompt: The video generation prompt
            max_context_length: Maximum length of context to include
            
        Returns:
            Formatted context string
        """
        relevant_chunks = self.retrieve_relevant_context(prompt, top_k=5)
        
        if not relevant_chunks:
            return "No relevant context found in the script database."
        
        context_parts = ["=== RELEVANT SCRIPT CONTEXT ==="]
        current_length = len(context_parts[0])
        
        for chunk in relevant_chunks:
            chunk_text = f"\n--- Context {chunk['rank']} (Similarity: {chunk['similarity_score']:.3f}) ---\n"
            chunk_text += f"Source: {chunk['metadata']['source']['name']}\n"
            chunk_text += f"Content: {chunk['text']}\n"
            
            if current_length + len(chunk_text) > max_context_length:
                break
            
            context_parts.append(chunk_text)
            current_length += len(chunk_text)
        
        context_parts.append("\n=== END CONTEXT ===\n")
        
        return "\n".join(context_parts)
    
    def get_database_info(self) -> Dict:
        """Get information about the current vector database."""
        if self.index is None:
            return {"status": "No database loaded"}
        
        return {
            "status": "Database loaded",
            "num_vectors": self.index.ntotal,
            "embedding_dim": self.embedding_dim,
            "embedding_model": self.embedding_model_name,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "sources": list(set(chunk["metadata"]["source"]["name"] for chunk in self.chunks))
        }
