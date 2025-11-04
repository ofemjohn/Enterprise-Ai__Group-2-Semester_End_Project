"""
Pydantic Schemas for API Request/Response Models

This module defines all data models used for API request and response validation.
Using Pydantic ensures type safety and automatic validation of incoming data.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Chat message model for user queries."""
    
    message: str = Field(
        ...,
        description="The user's question or message",
        min_length=1,
        max_length=2000,
        example="How do I reset my KSU password?",
    )
    conversation_id: Optional[str] = Field(
        None,
        description="Optional conversation ID for multi-turn conversations",
        example="conv_123456",
    )


class Source(BaseModel):
    """Source citation model for RAG responses."""
    
    url: str = Field(..., description="URL of the source document")
    title: Optional[str] = Field(None, description="Title of the source document")
    snippet: Optional[str] = Field(None, description="Relevant snippet from the source")


class ChatResponse(BaseModel):
    """Response model for chat API endpoint."""
    
    answer: str = Field(
        ...,
        description="The AI-generated answer to the user's question",
        example="To reset your KSU password, visit the password reset page...",
    )
    sources: List[Source] = Field(
        default_factory=list,
        description="List of source documents used to generate the answer",
    )
    conversation_id: Optional[str] = Field(
        None,
        description="Conversation ID for this interaction",
    )


class ErrorResponse(BaseModel):
    """Standard error response model."""
    
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict] = Field(None, description="Additional error details")


class HealthResponse(BaseModel):
    """Health check response model."""
    
    status: str = Field(..., description="Health status", example="healthy")
    version: str = Field(..., description="API version", example="0.1.0")
    service: str = Field(..., description="Service name", example="KSU IT RAG Chatbot API")

