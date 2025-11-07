"""
Chat Routes - RAG Chatbot API Endpoints

This module implements the main chat endpoint for the RAG (Retrieval-Augmented Generation) chatbot.
It handles user queries, processes them through the RAG pipeline, and returns answers with source citations.

Key Features:
- Accepts natural language queries from users
- Retrieves relevant context from vector database
- Generates answers using LLM with retrieved context
- Returns answers with source URLs for transparency
"""

from fastapi import APIRouter, HTTPException
from typing import Dict

from ...models.schemas import ChatMessage, ChatResponse, Source, ErrorResponse
from ...services.rag_service import get_rag_service
from ...utils.logger import logger

# Create router for chat endpoints
# All routes in this module will be prefixed with /api/v1/chat
router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(message: ChatMessage) -> ChatResponse:
    """
    Main chat endpoint for RAG queries.
    
    This is the primary endpoint that students will use to ask questions about KSU IT.
    The endpoint:
    1. Takes a user's question
    2. Retrieves relevant context from Pinecone vector database
    3. Generates an answer using the LLM (Mistral-7B-Instruct)
    4. Returns the answer with source citations
    
    Example request:
        POST /api/v1/chat
        {
            "message": "How do I reset my KSU password?"
        }
    
    Example response:
        {
            "answer": "To reset your KSU password...",
            "sources": [
                {
                    "url": "https://kennesaw.edu/...",
                    "snippet": "..."
                }
            ]
        }
    
    Args:
        message: ChatMessage object containing the user's query
        
    Returns:
        ChatResponse: Contains the generated answer and list of source citations
        
    Raises:
        HTTPException: If there's an error processing the query
    """
    try:
        # Get RAG service
        rag_service = get_rag_service()
        
        # Process query through RAG pipeline
        result = rag_service.query(message.message, top_k=5)
        
        # Format sources
        sources = [
            Source(
                url=source.get("url", ""),
                title=source.get("title"),
                snippet=source.get("snippet")
            )
            for source in result.get("sources", [])
        ]
        
        # Build response
        response = ChatResponse(
            answer=result.get("answer", ""),
            sources=sources,
            conversation_id=message.conversation_id
        )
        
        logger.info(f"Processed chat query: {message.message[:50]}...")
        return response
        
    except Exception as e:
        logger.error(f"Error processing chat query: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )

