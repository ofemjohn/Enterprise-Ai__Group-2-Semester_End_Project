"""
Health Check Routes

This module contains detailed health check endpoints for monitoring component status.
Provides both simple and detailed health check capabilities.
"""

from fastapi import APIRouter
from typing import Dict

from ...config import settings
from ...services.pinecone_service import get_pinecone_service
from ...services.llm_service import get_llm_service

# Create router for health check endpoints
router = APIRouter(prefix="/api/v1/health", tags=["health"])


@router.get("/detailed", response_model=Dict)
async def detailed_health() -> Dict:
    """
    Detailed health check with component status.
    
    This endpoint checks the health of:
    - API server
    - Vector database connection (Pinecone)
    - LLM service availability
    
    Returns:
        dict: Detailed health status of all components
    """
    components = {
        "api": "healthy",
        "vector_db": "unknown",
        "llm_service": "unknown",
    }
    
    # Check Pinecone connection
    try:
        pinecone_service = get_pinecone_service()
        if pinecone_service.health_check():
            stats = pinecone_service.get_index_stats()
            components["vector_db"] = "healthy"
            components["vector_db_stats"] = {
                "total_vectors": stats.get("total_vector_count", 0),
                "dimension": stats.get("dimension", 0)
            }
        else:
            components["vector_db"] = "unhealthy"
    except Exception as e:
        components["vector_db"] = f"error: {str(e)}"
    
    # Check LLM service
    try:
        llm_service = get_llm_service()
        if llm_service.is_available():
            components["llm_service"] = "healthy"
            components["llm_model"] = llm_service.model_name
        else:
            components["llm_service"] = "not_configured"
    except Exception as e:
        components["llm_service"] = f"error: {str(e)}"
    
    # Determine overall status
    overall_status = "healthy"
    if components["vector_db"] not in ["healthy", "unknown"]:
        overall_status = "degraded"
    
    return {
        "status": overall_status,
        "version": settings.api_version,
        "service": "KSU IT RAG Chatbot API",
        "components": components,
    }

