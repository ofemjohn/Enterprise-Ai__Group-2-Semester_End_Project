"""
FastAPI Application Entry Point - KSU IT RAG Chatbot API

This is the main FastAPI application that serves the RAG chatbot API.
It provides endpoints for students to query the chatbot and get answers
about KSU IT department information.

Application Features:
- RESTful API with automatic OpenAPI documentation
- CORS middleware for frontend integration
- Global exception handling
- Health check endpoints
- Modular route organization

API Endpoints:
- GET / - API information
- GET /health - Simple health check
- GET /api/v1/health/detailed - Detailed component status
- POST /api/v1/chat - Main chat endpoint (RAG queries)

Documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI Schema: http://localhost:8000/openapi.json

The application follows best practices:
- Centralized configuration via config.py
- Separation of concerns (routes, services, models)
- Comprehensive error handling
- Request/response logging
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .utils.logger import logger

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
# Allows cross-origin requests from frontend applications (React dev server on port 3000)
# Combine default React dev server origins with configured origins
cors_origins = [
    "http://localhost:3000",  # React development server
    "http://127.0.0.1:3000",
]
# Add configured origins (filter out "*" if present)
cors_origins.extend([origin for origin in settings.cors_origins if origin != "*"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins if cors_origins else ["*"],  # Fallback to all if empty
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)


# Include API route modules
from .api.routes import health as health_routes
from .api.routes import chat as chat_routes

# Register routers
app.include_router(health_routes.router)
app.include_router(chat_routes.router)

# Additional routes can be added here as needed
# Example: documents, admin, etc.


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


# Health check endpoint is now handled by /api/v1/health/detailed
# Keeping root /health for backward compatibility and simple checks
@app.get("/health", response_model=dict, tags=["health"])
async def health_check() -> dict:
    """
    Simple health check endpoint for quick status verification.
    
    For detailed health checks including component status, use /api/v1/health/detailed
    
    Returns:
        dict: Basic health status of the API
    """
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
    # Log the error using the configured logger
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
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
