"""
FastAPI Application Entry Point

This module contains the main FastAPI application setup, middleware configuration,
and root-level endpoints for the KSU IT RAG Chatbot API.

The application structure follows best practices:
- Centralized configuration via config.py
- Modular route organization
- CORS middleware for cross-origin requests
- Health check endpoints for monitoring
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings

# Initialize FastAPI application with metadata
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    docs_url="/docs",  # Swagger UI documentation
    redoc_url="/redoc",  # ReDoc documentation
    openapi_url="/openapi.json",  # OpenAPI schema
)

# CORS Middleware Configuration
# Allows cross-origin requests from frontend applications
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)


# Include API route modules
from .api.routes import health as health_routes

# Register routers
app.include_router(health_routes.router)

# TODO: Add more routes as they are implemented
# from .api.routes import chat, documents
# app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
# app.include_router(documents.router, prefix="/api/v1", tags=["documents"])


@app.get("/", response_model=dict, tags=["root"])
async def root() -> dict:
    """
    Root endpoint providing API information.
    
    Returns:
        dict: API metadata including name, version, and status
    """
    return {
        "message": settings.api_title,
        "version": settings.api_version,
        "status": "running",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", response_model=dict, tags=["health"])
async def health_check() -> dict:
    """
    Health check endpoint for monitoring and load balancers.
    
    This endpoint can be used by:
    - Kubernetes liveness/readiness probes
    - Load balancers for health checks
    - Monitoring systems
    
    Returns:
        dict: Health status of the API
    """
    # TODO: Add database connection check
    # TODO: Add vector database connection check
    # TODO: Add LLM service health check
    
    return {
        "status": "healthy",
        "version": settings.api_version,
        "service": "KSU IT RAG Chatbot API",
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception) -> JSONResponse:
    """
    Global exception handler for unhandled exceptions.
    
    This provides a consistent error response format and prevents
    sensitive error information from being exposed to clients.
    
    Args:
        request: The request that caused the exception
        exc: The exception that was raised
        
    Returns:
        JSONResponse: Standardized error response
    """
    # Log the error (TODO: implement proper logging)
    print(f"Unhandled exception: {exc}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
            "type": type(exc).__name__,
        },
    )


if __name__ == "__main__":
    """
    Direct execution entry point.
    
    Run the application directly with:
        python -m backend.app.main
    """
    import uvicorn
    
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
    )
