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
    
    # Vector Database Configuration (Pinecone - Cloud-based)
    pinecone_api_key: str = os.getenv("PINECONE_API_KEY", "")
    pinecone_environment: str = os.getenv("PINECONE_ENVIRONMENT", "")
    pinecone_index_name: str = os.getenv("PINECONE_INDEX_NAME", "ksu-it-rag-chatbot")
    # Embedding model configuration
    embedding_model_name: str = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
    embedding_dimension: int = int(os.getenv("EMBEDDING_DIMENSION", "384"))  # Default for all-MiniLM-L6-v2
    
    # LLM Configuration
    llm_provider: str = os.getenv("LLM_PROVIDER", "huggingface")  # "huggingface" or "openai"
    llm_model_name: str = os.getenv("LLM_MODEL_NAME", "")
    # OpenAI configuration (if using OpenAI)
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    # Hugging Face configuration (if using Hugging Face)
    huggingface_api_key: str = os.getenv("HUGGINGFACE_API_KEY", "")
    huggingface_model_name: str = os.getenv("HUGGINGFACE_MODEL_NAME", "mistralai/Mistral-7B-Instruct-v0.2")


# Global settings instance
settings = Settings()

