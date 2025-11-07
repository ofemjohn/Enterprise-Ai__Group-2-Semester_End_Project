"""
Pinecone Vector Database Service

This service manages all interactions with Pinecone cloud vector database.
Pinecone stores the embedded knowledge chunks (vectors) and enables fast
semantic search to find relevant information for user queries.

Key Features:
- Cloud-based vector storage (accessible to team members)
- Automatic index creation if it doesn't exist
- Semantic search using cosine similarity
- Batch operations for efficient data upload
- Health checks and statistics

Current Configuration:
- Index: ksu-it-rag-chatbot
- Dimension: 384 (matches embedding model)
- Metric: cosine (for semantic similarity)
- Vectors: 8,592 knowledge chunks from 1,423 pages

Why Pinecone:
- Cloud-based for team collaboration
- Fast semantic search
- Scalable for future growth
- Free tier sufficient for this project
"""

from typing import List, Dict, Optional

try:
    from pinecone import Pinecone, ServerlessSpec
except ImportError:
    Pinecone = None
    ServerlessSpec = None

from ..config import settings
from ..utils.logger import logger


class PineconeService:
    """Service for interacting with Pinecone vector database."""
    
    def __init__(self):
        """Initialize the Pinecone service."""
        if not settings.pinecone_api_key:
            raise ValueError("PINECONE_API_KEY not set in environment variables")
        
        if Pinecone is None:
            raise ImportError("pinecone-client not installed. Run: pip install pinecone-client")
        
        self.api_key = settings.pinecone_api_key
        self.index_name = settings.pinecone_index_name
        self.pc = None
        self.index = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Pinecone client and connect to index."""
        try:
            logger.info("Initializing Pinecone client...")
            self.pc = Pinecone(api_key=self.api_key)
            
            # Check if index exists, create if not
            try:
                existing_indexes = self.pc.list_indexes()
                index_names = [idx.name for idx in existing_indexes] if hasattr(existing_indexes, '__iter__') else []
                
                if self.index_name not in index_names:
                    logger.info(f"Creating Pinecone index: {self.index_name}")
                    self._create_index()
                else:
                    logger.info(f"Connecting to existing Pinecone index: {self.index_name}")
            except Exception as e:
                # If list_indexes fails, try to create index anyway
                logger.warning(f"Could not list indexes, attempting to create: {e}")
                try:
                    self._create_index()
                except Exception as create_error:
                    # Index might already exist, try to connect
                    logger.info(f"Index creation failed (may already exist), connecting: {create_error}")
            
            self.index = self.pc.Index(self.index_name)
            logger.info("Pinecone service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {e}")
            raise
    
    def _create_index(self):
        """Create a new Pinecone index if it doesn't exist."""
        try:
            dimension = settings.embedding_dimension
            metric = "cosine"  # Cosine similarity for semantic search
            
            # Extract region from environment (e.g., "us-east-1-aws" -> "us-east-1")
            region = "us-east-1"  # Default
            if settings.pinecone_environment:
                parts = settings.pinecone_environment.split("-")
                if len(parts) >= 3:
                    region = f"{parts[0]}-{parts[1]}-{parts[2]}"
            
            self.pc.create_index(
                name=self.index_name,
                dimension=dimension,
                metric=metric,
                spec=ServerlessSpec(
                    cloud="aws",
                    region=region
                )
            )
            logger.info(f"Created Pinecone index: {self.index_name} with dimension {dimension} in region {region}")
        except Exception as e:
            logger.error(f"Failed to create Pinecone index: {e}")
            raise
    
    def upsert_vectors(self, vectors: List[Dict], namespace: str = "") -> None:
        """
        Insert or update vectors in Pinecone.
        
        Args:
            vectors: List of dictionaries with 'id', 'values', and 'metadata' keys
            namespace: Optional namespace for the vectors
        """
        if self.index is None:
            raise RuntimeError("Pinecone index not initialized")
        
        try:
            # Pinecone expects format: [{"id": "...", "values": [...], "metadata": {...}}, ...]
            self.index.upsert(vectors=vectors, namespace=namespace)
            logger.info(f"Upserted {len(vectors)} vectors to Pinecone")
        except Exception as e:
            logger.error(f"Error upserting vectors to Pinecone: {e}")
            raise
    
    def query(
        self,
        query_vector: List[float],
        top_k: int = 5,
        namespace: str = "",
        include_metadata: bool = True
    ) -> List[Dict]:
        """
        Query Pinecone for similar vectors.
        
        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            namespace: Optional namespace to search
            include_metadata: Whether to include metadata in results
            
        Returns:
            List[Dict]: List of matches with 'id', 'score', and optionally 'metadata'
        """
        if self.index is None:
            raise RuntimeError("Pinecone index not initialized")
        
        try:
            results = self.index.query(
                vector=query_vector,
                top_k=top_k,
                namespace=namespace,
                include_metadata=include_metadata
            )
            
            # Format results
            matches = []
            for match in results.matches:
                matches.append({
                    "id": match.id,
                    "score": match.score,
                    "metadata": match.metadata if include_metadata else {}
                })
            
            return matches
        except Exception as e:
            logger.error(f"Error querying Pinecone: {e}")
            raise
    
    def delete_vectors(self, ids: List[str], namespace: str = "") -> None:
        """
        Delete vectors by IDs.
        
        Args:
            ids: List of vector IDs to delete
            namespace: Optional namespace
        """
        if self.index is None:
            raise RuntimeError("Pinecone index not initialized")
        
        try:
            self.index.delete(ids=ids, namespace=namespace)
            logger.info(f"Deleted {len(ids)} vectors from Pinecone")
        except Exception as e:
            logger.error(f"Error deleting vectors from Pinecone: {e}")
            raise
    
    def get_index_stats(self) -> Dict:
        """
        Get statistics about the Pinecone index.
        
        Returns:
            Dict: Index statistics
        """
        if self.index is None:
            raise RuntimeError("Pinecone index not initialized")
        
        try:
            stats = self.index.describe_index_stats()
            return {
                "total_vector_count": stats.total_vector_count,
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness,
                "namespaces": dict(stats.namespaces) if hasattr(stats, 'namespaces') else {}
            }
        except Exception as e:
            logger.error(f"Error getting index stats: {e}")
            raise
    
    def health_check(self) -> bool:
        """
        Check if Pinecone service is healthy and accessible.
        
        Returns:
            bool: True if healthy, False otherwise
        """
        try:
            if self.index is None:
                return False
            # Try to get stats as a health check
            self.get_index_stats()
            return True
        except Exception as e:
            logger.error(f"Pinecone health check failed: {e}")
            return False


# Global Pinecone service instance
_pinecone_service: Optional[PineconeService] = None


def get_pinecone_service() -> PineconeService:
    """
    Get or create the global Pinecone service instance.
    
    Returns:
        PineconeService: Singleton Pinecone service instance
    """
    global _pinecone_service
    if _pinecone_service is None:
        _pinecone_service = PineconeService()
    return _pinecone_service

