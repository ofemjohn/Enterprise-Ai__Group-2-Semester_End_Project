"""
Embedding Service - Text to Vector Conversion

This service converts text into vector embeddings using Sentence Transformers.
Embeddings are numerical representations of text that capture semantic meaning,
enabling semantic search in the vector database.

Key Features:
- Uses Sentence Transformers model: all-MiniLM-L6-v2
- Generates 384-dimensional vectors
- Batch processing for efficiency
- Singleton pattern for model reuse

Model: sentence-transformers/all-MiniLM-L6-v2
- Fast and efficient
- 384 dimensions (good balance of quality and speed)
- Good for semantic similarity search
- Pre-trained on large text corpus

Usage:
- Converts text chunks to vectors for storage in Pinecone
- Converts user queries to vectors for semantic search
- Enables finding semantically similar content (not just keyword matches)
"""

from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer

from ..config import settings
from ..utils.logger import logger


class EmbeddingService:
    """Service for generating text embeddings using Sentence Transformers."""
    
    def __init__(self, model_name: str = None):
        """
        Initialize the embedding service.
        
        Args:
            model_name: Name of the Sentence Transformer model to use.
                       Defaults to settings.embedding_model_name
        """
        self.model_name = model_name or settings.embedding_model_name
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the Sentence Transformer model."""
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Embedding model loaded successfully. Dimension: {self.get_embedding_dimension()}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings produced by the model.
        
        Returns:
            int: Embedding dimension
        """
        if self.model is None:
            return settings.embedding_dimension
        # Get dimension from model or use config default
        return self.model.get_sentence_embedding_dimension() or settings.embedding_dimension
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text string.
        
        Args:
            text: Text to embed
            
        Returns:
            List[float]: Embedding vector
        """
        if self.model is None:
            raise RuntimeError("Embedding model not loaded")
        
        try:
            embedding = self.model.encode(text, convert_to_numpy=True, show_progress_bar=False)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def embed_texts(self, texts: List[str], batch_size: int = 32, show_progress: bool = True) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (batch processing).
        
        Args:
            texts: List of texts to embed
            batch_size: Batch size for processing
            show_progress: Whether to show progress bar
            
        Returns:
            List[List[float]]: List of embedding vectors
        """
        if self.model is None:
            raise RuntimeError("Embedding model not loaded")
        
        try:
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=show_progress,
                convert_to_numpy=True
            )
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    
    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a search query.
        This is an alias for embed_text but can be customized for query-specific processing.
        
        Args:
            query: Search query text
            
        Returns:
            List[float]: Embedding vector
        """
        return self.embed_text(query)


# Global embedding service instance
_embedding_service: EmbeddingService = None


def get_embedding_service() -> EmbeddingService:
    """
    Get or create the global embedding service instance.
    
    Returns:
        EmbeddingService: Singleton embedding service instance
    """
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service

