"""
RAG (Retrieval-Augmented Generation) Service

This is the core service that implements the complete RAG pipeline for the chatbot.
RAG combines information retrieval with language generation to provide accurate,
source-cited answers to user questions.

Pipeline Flow:
1. Query Embedding: Convert user question to vector representation
2. Semantic Search: Find relevant chunks in Pinecone vector database
3. Context Retrieval: Extract top-k most relevant knowledge chunks
4. LLM Generation: Use retrieved context to generate accurate answer
5. Source Extraction: Extract and format source citations

Key Benefits:
- Prevents hallucinations by grounding answers in real data
- Provides source citations for transparency
- Uses semantic search for better relevance than keyword matching
- Handles queries about KSU IT department information

This service orchestrates the embedding service, Pinecone service, and LLM service
to provide a complete RAG solution.
"""

from typing import List, Dict, Optional
from .embedding_service import get_embedding_service
from .pinecone_service import get_pinecone_service
from .llm_service import get_llm_service
from ..utils.logger import logger


class RAGService:
    """Service for Retrieval-Augmented Generation."""
    
    def __init__(self):
        """Initialize the RAG service."""
        self.embedding_service = get_embedding_service()
        self.pinecone_service = get_pinecone_service()
        try:
            self.llm_service = get_llm_service()
            logger.info("RAG Service initialized with LLM support")
        except Exception as e:
            logger.warning(f"LLM service not available: {e}. RAG will use placeholder responses.")
            self.llm_service = None
    
    def retrieve_context(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Retrieve relevant context for a query using semantic search.
        
        Args:
            query: User query text
            top_k: Number of relevant chunks to retrieve
            
        Returns:
            List[Dict]: List of relevant chunks with metadata and scores
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_service.embed_query(query)
            
            # Search in Pinecone
            results = self.pinecone_service.query(
                query_vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            # Format results
            context_chunks = []
            for result in results:
                # Get full text from metadata
                text = result["metadata"].get("text", "")
                context_chunks.append({
                    "text": text,
                    "url": result["metadata"].get("url", ""),
                    "score": result["score"],
                    "metadata": result["metadata"]
                })
            
            logger.info(f"Retrieved {len(context_chunks)} context chunks for query")
            return context_chunks
            
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            raise
    
    def generate_answer(
        self,
        query: str,
        context_chunks: List[Dict],
        max_context_length: int = 2000
    ) -> Dict:
        """
        Generate an answer using retrieved context.
        
        Args:
            query: User query
            context_chunks: Retrieved context chunks
            max_context_length: Maximum length of context to use
            
        Returns:
            Dict: Answer with text and sources
        """
        # Generate answer using LLM with retrieved context
        
        # Build context from chunks
        context_text = self._build_context(context_chunks, max_context_length)
        
        # Extract unique sources
        sources = self._extract_sources(context_chunks)
        
        # Generate answer using LLM if available
        if self.llm_service and self.llm_service.is_available():
            try:
                answer = self.llm_service.generate_answer(
                    query=query,
                    context=context_text,
                    max_new_tokens=512,
                    temperature=0.3,  # Lower temperature for more focused, accurate answers
                    top_p=0.9,
                    repetition_penalty=1.1
                )
                logger.info("Answer generated successfully using LLM")
            except Exception as e:
                logger.error(f"Error generating answer with LLM: {e}")
                # Fallback to simple response
                answer = self._generate_fallback_answer(query, context_text)
        else:
            # Fallback if LLM is not available
            logger.warning("LLM service not available, using fallback response")
            answer = self._generate_fallback_answer(query, context_text)
        
        return {
            "answer": answer,
            "sources": sources,
            "context_chunks": len(context_chunks)
        }
    
    def _build_context(self, chunks: List[Dict], max_length: int) -> str:
        """Build context string from chunks."""
        context_parts = []
        current_length = 0
        
        for chunk in chunks:
            text = chunk.get("text", "")
            if current_length + len(text) <= max_length:
                context_parts.append(text)
                current_length += len(text)
            else:
                # Add partial chunk if there's space
                remaining = max_length - current_length
                if remaining > 100:  # Only add if meaningful
                    context_parts.append(text[:remaining])
                break
        
        return "\n\n".join(context_parts)
    
    def _extract_sources(self, chunks: List[Dict]) -> List[Dict]:
        """Extract unique sources from context chunks."""
        sources_map = {}
        
        for chunk in chunks:
            url = chunk.get("url", "")
            if url and url not in sources_map:
                sources_map[url] = {
                    "url": url,
                    "title": chunk.get("metadata", {}).get("title", ""),
                    "snippet": chunk.get("text", "")[:200]  # First 200 chars
                }
        
        return list(sources_map.values())
    
    def _generate_fallback_answer(self, query: str, context: str) -> str:
        """
        Generate a fallback answer when LLM is not available.
        
        Args:
            query: User's question
            context: Retrieved context
            
        Returns:
            str: Fallback answer
        """
        if not context or len(context.strip()) < 50:
            return "I couldn't find enough relevant information to answer your question. Please try rephrasing or asking about a different topic."
        
        # Simple extraction: return first few sentences of context
        sentences = context.split('. ')
        relevant_sentences = sentences[:3]  # First 3 sentences
        answer = '. '.join(relevant_sentences)
        
        if not answer.endswith('.'):
            answer += '.'
        
        return f"Based on the available information: {answer}"
    
    def query(self, query: str, top_k: int = 5) -> Dict:
        """
        Complete RAG pipeline: retrieve context and generate answer.
        
        Args:
            query: User query
            top_k: Number of context chunks to retrieve
            
        Returns:
            Dict: Complete response with answer and sources
        """
        # Retrieve context
        context_chunks = self.retrieve_context(query, top_k)
        
        if not context_chunks:
            return {
                "answer": "I couldn't find relevant information to answer your question. Please try rephrasing your query.",
                "sources": [],
                "context_chunks": 0
            }
        
        # Generate answer
        response = self.generate_answer(query, context_chunks)
        
        return response


# Global RAG service instance
_rag_service: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    """
    Get or create the global RAG service instance.
    
    Returns:
        RAGService: Singleton RAG service instance
    """
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service

