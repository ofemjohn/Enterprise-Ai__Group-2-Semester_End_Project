"""
Application Configuration

Centralized configuration for the FastAPI application.
Environment variables can be loaded from .env file using python-dotenv.
"""

import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()


class Settings:
    """Application settings loaded from environment variables or defaults."""
    
    # API Configuration
    api_title: str = os.getenv("API_TITLE", "KSU IT RAG Chatbot API")
    api_description: str = os.getenv(
        "API_DESCRIPTION",
        "Retrieval-Augmented Generation API for KSU IT Department"
    )
    api_version: str = os.getenv("API_VERSION", "0.1.0")
    
    # Server Configuration
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    reload: bool = os.getenv("RELOAD", "False").lower() == "true"
    
    # CORS Configuration
    # In production, set CORS_ORIGINS environment variable with comma-separated origins
    cors_origins: List[str] = os.getenv("CORS_ORIGINS", "*").split(",")
    cors_allow_credentials: bool = os.getenv("CORS_ALLOW_CREDENTIALS", "True").lower() == "true"
    cors_allow_methods: List[str] = os.getenv("CORS_ALLOW_METHODS", "*").split(",")
    cors_allow_headers: List[str] = os.getenv("CORS_ALLOW_HEADERS", "*").split(",")
    
    # Vector Database Configuration (to be added)
    # vector_db_url: str = os.getenv("VECTOR_DB_URL", "")
    # vector_db_api_key: str = os.getenv("VECTOR_DB_API_KEY", "")
    
    # LLM Configuration (to be added)
    # llm_model_name: str = os.getenv("LLM_MODEL_NAME", "")
    # llm_api_key: str = os.getenv("LLM_API_KEY", "")


# Global settings instance
settings = Settings()

