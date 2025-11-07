"""
LLM Service - Language Model Integration

This service handles all interactions with language models via Hugging Face Inference API.
It's responsible for generating natural language answers based on retrieved context from
the vector database (RAG pattern).

Key Features:
- Integrates with Hugging Face Inference API
- Uses Mistral-7B-Instruct model (optimized for instruction following)
- Implements RAG-optimized prompt templates
- Handles errors gracefully with fallback mechanisms
- Configurable parameters (temperature, tokens, etc.)

Model: mistralai/Mistral-7B-Instruct-v0.2
- Excellent for RAG applications
- Good instruction following
- Handles context well
- Free tier friendly

The service formats prompts specifically for RAG, instructing the model to:
- Answer based ONLY on provided context
- Cite sources when possible
- Say "I don't know" if context is insufficient
"""

import json
from typing import Dict, Optional, List
import requests
from ..config import settings
from ..utils.logger import logger


class LLMService:
    """Service for interacting with language models via Hugging Face Inference API."""
    
    def __init__(self):
        """Initialize the LLM service."""
        self.api_key = settings.huggingface_api_key
        self.model_name = settings.huggingface_model_name or "mistralai/Mistral-7B-Instruct-v0.2"
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model_name}"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        if not self.api_key:
            logger.warning("Hugging Face API key not set. LLM service will not work.")
        else:
            logger.info(f"LLM Service initialized with model: {self.model_name}")
    
    def generate_answer(
        self,
        query: str,
        context: str,
        max_new_tokens: int = 512,
        temperature: float = 0.3,
        top_p: float = 0.9,
        repetition_penalty: float = 1.1
    ) -> str:
        """
        Generate an answer using the LLM with provided context.
        
        Args:
            query: User's question
            context: Retrieved context from vector database
            max_new_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (lower = more focused)
            top_p: Nucleus sampling parameter
            repetition_penalty: Penalty for repetition
            
        Returns:
            str: Generated answer
        """
        if not self.api_key:
            raise ValueError("Hugging Face API key not configured. Please set HUGGINGFACE_API_KEY in .env file.")
        
        # Build prompt for Mistral-7B-Instruct format
        prompt = self._build_rag_prompt(query, context)
        
        # Prepare payload for Hugging Face Inference API
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_new_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "repetition_penalty": repetition_penalty,
                "return_full_text": False,  # Don't return the prompt, only the generated text
                "do_sample": True
            }
        }
        
        try:
            logger.debug(f"Sending request to Hugging Face API for model: {self.model_name}")
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30  # 30 second timeout
            )
            
            # Check for errors
            if response.status_code != 200:
                error_msg = f"API request failed with status {response.status_code}: {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            # Parse response
            result = response.json()
            
            # Handle different response formats
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get("generated_text", "")
            elif isinstance(result, dict):
                generated_text = result.get("generated_text", "")
            else:
                generated_text = str(result)
            
            # Clean up the response (remove any prompt artifacts)
            answer = self._clean_response(generated_text, query)
            
            logger.info(f"Successfully generated answer (length: {len(answer)} chars)")
            return answer
            
        except requests.exceptions.Timeout:
            logger.error("Request to Hugging Face API timed out")
            raise Exception("The model is taking too long to respond. Please try again.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Hugging Face API: {e}")
            raise Exception(f"Failed to generate answer: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in LLM generation: {e}")
            raise
    
    def _build_rag_prompt(self, query: str, context: str) -> str:
        """
        Build a RAG prompt in the format expected by Mistral-7B-Instruct.
        
        Args:
            query: User's question
            context: Retrieved context
            
        Returns:
            str: Formatted prompt
        """
        # Mistral-7B-Instruct uses a specific format
        prompt = f"""<s>[INST] You are a helpful assistant for Kennesaw State University IT Department students. 
Answer the question based ONLY on the provided context. Be concise, accurate, and helpful. 
If the context doesn't contain enough information to answer the question, say so clearly.

Context:
{context}

Question: {query}

Answer based on the context above: [/INST]"""
        
        return prompt
    
    def _clean_response(self, response: str, query: str) -> str:
        """
        Clean up the LLM response to remove any artifacts.
        
        Args:
            response: Raw response from LLM
            query: Original query (to detect if it was repeated)
            
        Returns:
            str: Cleaned response
        """
        # Remove the query if it was repeated at the start
        if response.startswith(query):
            response = response[len(query):].strip()
        
        # Remove any trailing prompt artifacts
        response = response.split("[/INST]")[-1].strip()
        response = response.split("[INST]")[0].strip()
        
        # Remove leading/trailing whitespace
        response = response.strip()
        
        return response
    
    def is_available(self) -> bool:
        """
        Check if the LLM service is available and configured.
        
        Returns:
            bool: True if service is available
        """
        return bool(self.api_key and self.model_name)


# Global LLM service instance
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """
    Get or create the global LLM service instance.
    
    Returns:
        LLMService: Singleton LLM service instance
    """
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service

