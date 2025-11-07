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
from .conversation_manager import get_conversation_manager
from ..utils.logger import logger


class RAGService:
    """Service for Retrieval-Augmented Generation."""
    
    def __init__(self):
        """Initialize the RAG service."""
        self.embedding_service = get_embedding_service()
        self.pinecone_service = get_pinecone_service()
        self.conversation_manager = get_conversation_manager()
        try:
            self.llm_service = get_llm_service()
            logger.info("RAG Service initialized with LLM support and conversation management")
        except Exception as e:
            logger.warning(f"LLM service not available: {e}. RAG will use placeholder responses.")
            self.llm_service = None
    
    def retrieve_context(self, query: str, top_k: int = 5, min_score: float = 0.3) -> List[Dict]:
        """
        Retrieve relevant context for a query using semantic search.
        
        Filters out low-relevance results based on similarity score to ensure
        only truly relevant sources are included.
        
        Args:
            query: User query text
            top_k: Number of relevant chunks to retrieve (will fetch more, then filter)
            min_score: Minimum similarity score threshold (0.0-1.0, cosine similarity)
                      Results below this score are filtered out as irrelevant
                      Default 0.3 ensures reasonable relevance (cosine similarity, lower is more lenient)
        
        Returns:
            List[Dict]: List of relevant chunks with metadata and scores (filtered by relevance)
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_service.embed_query(query)
            
            # Fetch more results than needed to account for filtering
            fetch_k = max(top_k * 2, 10)  # Fetch 2x or at least 10 results
            
            # Search in Pinecone
            results = self.pinecone_service.query(
                query_vector=query_embedding,
                top_k=fetch_k,
                include_metadata=True
            )
            
            # Format and filter results by relevance score
            context_chunks = []
            for result in results:
                score = result.get("score", 0.0)
                
                # Filter out low-relevance results
                if score < min_score:
                    logger.debug(f"Filtered out low-relevance result (score: {score:.3f} < {min_score}): {result.get('metadata', {}).get('url', 'unknown')[:50]}")
                    continue
                
                # Get full text from metadata
                text = result["metadata"].get("text", "")
                if not text or len(text.strip()) < 20:  # Skip very short chunks
                    continue
                
                context_chunks.append({
                    "text": text,
                    "url": result["metadata"].get("url", ""),
                    "score": score,
                    "metadata": result["metadata"]
                })
                
                # Stop once we have enough high-quality results
                if len(context_chunks) >= top_k:
                    break
            
            logger.info(f"Retrieved {len(context_chunks)} relevant context chunks (filtered from {len(results)} results, min_score={min_score})")
            
            # Log scores for debugging
            if context_chunks:
                scores = [chunk["score"] for chunk in context_chunks]
                logger.debug(f"Similarity scores: min={min(scores):.3f}, max={max(scores):.3f}, avg={sum(scores)/len(scores):.3f}")
            
            return context_chunks
            
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            raise
    
    def generate_answer(
        self,
        query: str,
        context_chunks: List[Dict],
        max_context_length: int = 2000,
        conversation_id: Optional[str] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Generate an answer using retrieved context and optional conversation history.
        
        TRANSPARENCY: This method ONLY uses the LLM to generate answers.
        There is NO fallback mechanism. If the LLM fails or is unavailable,
        a RuntimeError is raised, which the API route catches and returns
        a clear "unavailable" message to the user. This ensures transparency
        - users always know when they're getting AI-generated content vs.
        when the service is down.
        
        Args:
            query: User query
            context_chunks: Retrieved context chunks
            max_context_length: Maximum length of context to use
            conversation_id: Optional conversation ID for maintaining context
            conversation_history: Optional conversation history (if None, will fetch from manager)
            
        Returns:
            Dict: Answer with text and sources
            
        Raises:
            RuntimeError: If LLM service is unavailable or fails to generate answer
        """
        # Generate answer using LLM with retrieved context
        
        # Build context from chunks
        context_text = self._build_context(context_chunks, max_context_length)
        
        # Extract unique sources (filtered by relevance)
        # Use same min_score threshold as retrieval for consistency
        min_score = 0.3  # Minimum relevance score threshold (cosine similarity)
        sources = self._extract_sources(context_chunks, min_score=min_score)
        
        # Generate answer using LLM ONLY - no fallback for transparency
        # If LLM fails, we raise an exception so the API can return a clear
        # "unavailable" message instead of misleading fallback content
        if not self.llm_service or not self.llm_service.is_available():
            logger.error("LLM service is not available")
            raise RuntimeError("LLM service is currently unavailable. Please try again later.")
        
        try:
            # Get conversation history if conversation_id is provided
            if conversation_history is None and conversation_id:
                conversation_history = self.conversation_manager.get_recent_history(conversation_id)
            
            answer = self.llm_service.generate_answer(
                query=query,
                context=context_text,
                max_new_tokens=512,
                temperature=0.3,  # Lower temperature for more focused, accurate answers
                top_p=0.9,
                repetition_penalty=1.1,
                conversation_history=conversation_history
            )
            logger.info("Answer generated successfully using LLM")
            
            # Store messages in conversation history
            if conversation_id:
                self.conversation_manager.add_message(conversation_id, "user", query)
                self.conversation_manager.add_message(conversation_id, "assistant", answer)
        except Exception as e:
            logger.error(f"Error generating answer with LLM: {e}")
            # Raise exception instead of using fallback - transparency is key
            raise RuntimeError("LLM service failed to generate an answer. Please try again later.") from e
        
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
    
    def _extract_sources(self, chunks: List[Dict], min_score: float = 0.3) -> List[Dict]:
        """
        Extract unique sources from context chunks, prioritizing high-relevance sources.
        
        Only includes sources that meet the minimum relevance threshold to ensure
        users only see sources that are actually relevant to their query.
        Filters out announcement/news pages that may have high similarity but aren't
        directly relevant to the query.
        
        Args:
            chunks: List of context chunks with scores
            min_score: Minimum similarity score to include a source (default: 0.3)
            
        Returns:
            List[Dict]: List of unique, relevant sources sorted by relevance score
        """
        sources_map = {}
        
        # URLs to exclude (announcements, news posts that aren't directly relevant)
        excluded_url_patterns = [
            "/about/news/posts/",  # News/announcement posts
            "/transition",  # Transition announcements
        ]
        
        # Sort chunks by score (highest first) to prioritize most relevant sources
        sorted_chunks = sorted(chunks, key=lambda x: x.get("score", 0.0), reverse=True)
        
        for chunk in sorted_chunks:
            score = chunk.get("score", 0.0)
            url = chunk.get("url", "")
            
            # Only include sources that meet relevance threshold
            if score < min_score:
                continue
            
            # Filter out announcement/news pages unless they have very high relevance
            if url:
                is_excluded = any(pattern in url.lower() for pattern in excluded_url_patterns)
                # Only include excluded patterns if score is very high (0.7+)
                if is_excluded and score < 0.7:
                    logger.debug(f"Filtered out announcement/news page (score: {score:.3f}): {url[:60]}")
                    continue
            
            if url and url not in sources_map:
                # Get a better snippet - try to find a relevant portion of the text
                text = chunk.get("text", "")
                snippet = text[:200] if len(text) <= 200 else text[:197] + "..."
                
                sources_map[url] = {
                    "url": url,
                    "title": chunk.get("metadata", {}).get("title", ""),
                    "snippet": snippet,
                    "score": score  # Include score for reference (can be used for sorting)
                }
        
        # Return sources sorted by relevance (highest score first)
        sources = list(sources_map.values())
        sources.sort(key=lambda x: x.get("score", 0.0), reverse=True)
        
        logger.debug(f"Extracted {len(sources)} unique relevant sources (min_score={min_score})")
        return sources
    
    # Removed _generate_fallback_answer method - system now requires LLM to work
    # If LLM is unavailable, an exception is raised instead
    
    def query(self, query: str, top_k: int = 5, conversation_id: Optional[str] = None, min_score: float = 0.3) -> Dict:
        """
        Complete RAG pipeline: retrieve context and generate answer.
        
        This method supports conversation history. If conversation_id is provided,
        recent conversation history will be included in the LLM prompt to maintain
        context across multiple messages.
        
        Args:
            query: User query
            top_k: Number of context chunks to retrieve
            conversation_id: Optional conversation ID for maintaining context across messages
            min_score: Minimum similarity score threshold (0.0-1.0) for filtering relevant results
                      Default 0.3 filters out clearly irrelevant sources while keeping relevant ones
            
        Returns:
            Dict: Complete response with answer and sources
        """
        # Retrieve context with relevance filtering
        context_chunks = self.retrieve_context(query, top_k, min_score=min_score)
        
        if not context_chunks:
            return {
                "answer": "I couldn't find relevant information to answer your question. Please try rephrasing your query.",
                "sources": [],
                "context_chunks": 0
            }
        
        # Generate answer with conversation history
        response = self.generate_answer(query, context_chunks, conversation_id=conversation_id)
        
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

