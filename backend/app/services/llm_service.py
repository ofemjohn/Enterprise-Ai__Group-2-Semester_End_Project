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

# Try to use Hugging Face InferenceClient (handles endpoint changes automatically)
try:
    from huggingface_hub import InferenceClient
    INFERENCE_CLIENT_AVAILABLE = True
except ImportError:
    InferenceClient = None
    INFERENCE_CLIENT_AVAILABLE = False


class LLMService:
    """Service for interacting with language models via Hugging Face Inference API."""
    
    def __init__(self):
        """Initialize the LLM service."""
        self.api_key = settings.huggingface_api_key
        self.model_name = settings.huggingface_model_name or "mistralai/Mistral-7B-Instruct-v0.2"
        
        if not self.api_key:
            logger.warning("Hugging Face API key not set. LLM service will not work.")
            self.client = None
            self.api_url = None
            self.headers = None
        else:
            # Use InferenceClient if available (handles endpoint changes automatically)
            if INFERENCE_CLIENT_AVAILABLE:
                try:
                    self.client = InferenceClient(
                        model=self.model_name,
                        token=self.api_key
                    )
                    self.api_url = None  # Not needed when using InferenceClient
                    self.headers = None
                    logger.info(f"LLM Service initialized with InferenceClient, model: {self.model_name}")
                except Exception as e:
                    logger.warning(f"Failed to initialize InferenceClient: {e}. Falling back to direct API calls.")
                    self.client = None
                    self._setup_direct_api()
            else:
                self.client = None
                self._setup_direct_api()
    
    def _setup_direct_api(self):
        """Setup direct API calls (fallback method)."""
        # Try new router endpoint first
        self.api_url = f"https://router.huggingface.co/hf-inference/models/{self.model_name}"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        logger.info(f"LLM Service initialized with direct API, model: {self.model_name}")
    
    def generate_answer(
        self,
        query: str,
        context: str,
        max_new_tokens: int = 512,
        temperature: float = 0.3,
        top_p: float = 0.9,
        repetition_penalty: float = 1.1,
        conversation_history: Optional[List[Dict]] = None
    ) -> str:
        """
        Generate an answer using the LLM with provided context and optional conversation history.
        
        Args:
            query: User's question
            context: Retrieved context from vector database
            max_new_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (lower = more focused)
            top_p: Nucleus sampling parameter
            repetition_penalty: Penalty for repetition
            conversation_history: Optional list of previous messages in format [{"role": "user/assistant", "content": "..."}]
            
        Returns:
            str: Generated answer
        """
        if not self.api_key:
            raise ValueError("Hugging Face API key not configured. Please set HUGGINGFACE_API_KEY in .env file.")
        
        # Build prompt for Mistral-7B-Instruct format
        prompt = self._build_rag_prompt(query, context)
        
        try:
            # Use InferenceClient if available (preferred method)
            if self.client:
                logger.debug(f"Using InferenceClient for model: {self.model_name}")
                try:
                    # Try text generation first
                    generated_text = self.client.text_generation(
                        prompt,
                        max_new_tokens=max_new_tokens,
                        temperature=temperature,
                        top_p=top_p,
                        repetition_penalty=repetition_penalty,
                        return_full_text=False
                    )
                    # InferenceClient returns the generated text directly
                    answer = self._clean_response(generated_text, query)
                    logger.info(f"Successfully generated answer using InferenceClient (length: {len(answer)} chars)")
                    return answer
                except ValueError as e:
                    # If text_generation fails, try conversational API
                    if "conversational" in str(e).lower():
                        logger.debug("Model requires conversational API, using chat completion")
                        # Use chat completion format for Mistral models
                        # Enhanced system message for better structured responses
                        system_message = """You are a helpful assistant for Kennesaw State University IT Department students. 
Answer questions based ONLY on the provided context.

IMPORTANT FORMATTING GUIDELINES:
- Structure your response clearly and logically
- Use bullet points or numbered lists when listing multiple items
- Group related information together
- Avoid repetition - if you mention something once, don't repeat it
- Be concise but comprehensive
- Use clear, professional language
- If the context doesn't contain enough information, say so clearly
- If there's conversation history, use it to understand context and provide relevant follow-up answers"""
                        
                        # Build messages list with conversation history if available
                        messages = [{"role": "system", "content": system_message}]
                        
                        # Add conversation history (excluding the current query)
                        if conversation_history:
                            # Filter to only include assistant messages and previous user messages
                            for hist_msg in conversation_history:
                                if hist_msg.get("role") in ["user", "assistant"]:
                                    messages.append({
                                        "role": hist_msg["role"],
                                        "content": hist_msg["content"]
                                    })
                        
                        # Add current context and query
                        messages.append({
                            "role": "user",
                            "content": f"Context:\n{context}\n\nQuestion: {query}\n\nProvide a well-structured, organized answer based on the context above:"
                        })
                        response = self.client.chat_completion(
                            messages=messages,
                            max_tokens=max_new_tokens,
                            temperature=temperature,
                            top_p=top_p
                        )
                        # Extract answer from chat completion response
                        # ChatCompletionOutput has a choices attribute with message content
                        if hasattr(response, "choices") and len(response.choices) > 0:
                            generated_text = response.choices[0].message.content
                        elif isinstance(response, dict) and "choices" in response:
                            generated_text = response["choices"][0].get("message", {}).get("content", "")
                        else:
                            generated_text = str(response)
                        answer = self._clean_response(generated_text, query)
                        logger.info(f"Successfully generated answer using conversational API (length: {len(answer)} chars)")
                        return answer
                    else:
                        raise
            
            # Fallback to direct API calls
            logger.debug(f"Using direct API for model: {self.model_name}")
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": max_new_tokens,
                    "temperature": temperature,
                    "top_p": top_p,
                    "repetition_penalty": repetition_penalty,
                    "return_full_text": False,
                    "do_sample": True
                }
            }
            
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=60  # Increased timeout for model loading
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
        
        The prompt is designed to generate well-structured, organized responses
        that are easy to read and understand.
        
        Args:
            query: User's question
            context: Retrieved context
            
        Returns:
            str: Formatted prompt
        """
        # Mistral-7B-Instruct uses a specific format
        # Enhanced prompt for better structured responses
        prompt = f"""<s>[INST] You are a helpful assistant for Kennesaw State University IT Department students. 
Answer the question based ONLY on the provided context. 

IMPORTANT FORMATTING GUIDELINES:
- Structure your response clearly and logically
- Use bullet points or numbered lists when listing multiple items
- Group related information together
- Avoid repetition - if you mention something once, don't repeat it
- Be concise but comprehensive
- Use clear, professional language
- If the context doesn't contain enough information, say so clearly

Context:
{context}

Question: {query}

Provide a well-structured, organized answer based on the context above: [/INST]"""
        
        return prompt
    
    def _clean_response(self, response: str, query: str) -> str:
        """
        Clean up the LLM response to remove any artifacts and ensure proper formatting.
        
        Args:
            response: Raw response from LLM
            query: Original query (to detect if it was repeated)
            
        Returns:
            str: Cleaned and formatted response
        """
        import re
        
        # Remove the query if it was repeated at the start
        if response.startswith(query):
            response = response[len(query):].strip()
        
        # Remove any trailing prompt artifacts
        response = response.split("[/INST]")[-1].strip()
        response = response.split("[INST]")[0].strip()
        
        # Clean up multiple consecutive newlines (keep max 2 for proper spacing)
        response = re.sub(r'\n{3,}', '\n\n', response)
        
        # Remove leading/trailing whitespace
        response = response.strip()
        
        # Ensure response ends with proper punctuation if it's a complete sentence
        if response and not response[-1] in '.!?':
            # Only add period if it looks like a complete sentence (not ending with colon or list item)
            if len(response) > 50 and not response.endswith(':'):
                response += '.'
        
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

