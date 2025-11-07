"""
Conversation Manager - Manages conversation history and context window

This module handles conversation history storage and retrieval for maintaining
context across multiple chat messages. It implements a sliding window approach
to keep recent conversation history within token limits.

Key Features:
- Stores conversation history in memory (can be extended to use database)
- Maintains a sliding window of recent messages
- Limits context to prevent token overflow
- Supports multiple concurrent conversations via conversation_id
"""

from typing import List, Dict, Optional
from datetime import datetime
from collections import defaultdict
from ..utils.logger import logger


class ConversationMessage:
    """Represents a single message in a conversation."""
    
    def __init__(self, role: str, content: str, timestamp: Optional[datetime] = None):
        """
        Initialize a conversation message.
        
        Args:
            role: 'user' or 'assistant'
            content: Message content
            timestamp: Optional timestamp (defaults to now)
        """
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert message to dictionary format."""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }


class ConversationManager:
    """
    Manages conversation history with a sliding window approach.
    
    Maintains recent conversation history for each conversation_id,
    automatically trimming old messages to stay within context limits.
    """
    
    def __init__(self, max_history_messages: int = 10, max_history_tokens: int = 2000):
        """
        Initialize the conversation manager.
        
        Args:
            max_history_messages: Maximum number of messages to keep in history
            max_history_tokens: Maximum approximate tokens to keep (rough estimate: 1 token ≈ 4 chars)
        """
        self.max_history_messages = max_history_messages
        self.max_history_tokens = max_history_tokens
        # Store conversations by conversation_id
        self.conversations: Dict[str, List[ConversationMessage]] = defaultdict(list)
        logger.info(f"ConversationManager initialized: max_messages={max_history_messages}, max_tokens={max_history_tokens}")
    
    def add_message(self, conversation_id: str, role: str, content: str) -> None:
        """
        Add a message to the conversation history.
        
        Args:
            conversation_id: Unique identifier for the conversation
            role: 'user' or 'assistant'
            content: Message content
        """
        message = ConversationMessage(role=role, content=content)
        self.conversations[conversation_id].append(message)
        
        # Trim history if needed
        self._trim_history(conversation_id)
        
        logger.debug(f"Added {role} message to conversation {conversation_id[:8]}... (total: {len(self.conversations[conversation_id])} messages)")
    
    def get_conversation_history(self, conversation_id: str) -> List[Dict]:
        """
        Get conversation history for a given conversation_id.
        
        Args:
            conversation_id: Unique identifier for the conversation
            
        Returns:
            List of message dictionaries in format [{"role": "user/assistant", "content": "..."}]
        """
        if conversation_id not in self.conversations:
            return []
        
        # Return messages in format expected by LLM
        return [
            {"role": msg.role, "content": msg.content}
            for msg in self.conversations[conversation_id]
        ]
    
    def get_recent_history(self, conversation_id: str, num_messages: Optional[int] = None) -> List[Dict]:
        """
        Get recent conversation history (last N messages).
        
        Args:
            conversation_id: Unique identifier for the conversation
            num_messages: Number of recent messages to return (defaults to all)
            
        Returns:
            List of recent message dictionaries
        """
        history = self.get_conversation_history(conversation_id)
        if num_messages is None:
            return history
        return history[-num_messages:] if history else []
    
    def _trim_history(self, conversation_id: str) -> None:
        """
        Trim conversation history to stay within limits.
        
        Removes oldest messages if history exceeds max_history_messages or max_history_tokens.
        """
        if conversation_id not in self.conversations:
            return
        
        messages = self.conversations[conversation_id]
        
        # Trim by message count
        if len(messages) > self.max_history_messages:
            # Keep the most recent messages
            self.conversations[conversation_id] = messages[-self.max_history_messages:]
            messages = self.conversations[conversation_id]
            logger.debug(f"Trimmed conversation {conversation_id[:8]}... to {len(messages)} messages (by count)")
        
        # Trim by token count (rough estimate: 1 token ≈ 4 characters)
        total_chars = sum(len(msg.content) for msg in messages)
        estimated_tokens = total_chars // 4
        
        while estimated_tokens > self.max_history_tokens and len(messages) > 2:
            # Keep at least 2 messages (last user + assistant pair)
            messages.pop(0)
            total_chars = sum(len(msg.content) for msg in messages)
            estimated_tokens = total_chars // 4
        
        if estimated_tokens > self.max_history_tokens:
            logger.warning(f"Conversation {conversation_id[:8]}... still exceeds token limit after trimming")
    
    def clear_conversation(self, conversation_id: str) -> None:
        """
        Clear all history for a conversation.
        
        Args:
            conversation_id: Unique identifier for the conversation
        """
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            logger.info(f"Cleared conversation history for {conversation_id[:8]}...")
    
    def get_conversation_summary(self, conversation_id: str) -> Dict:
        """
        Get summary statistics for a conversation.
        
        Args:
            conversation_id: Unique identifier for the conversation
            
        Returns:
            Dictionary with conversation statistics
        """
        if conversation_id not in self.conversations:
            return {"message_count": 0, "estimated_tokens": 0}
        
        messages = self.conversations[conversation_id]
        total_chars = sum(len(msg.content) for msg in messages)
        estimated_tokens = total_chars // 4
        
        return {
            "message_count": len(messages),
            "estimated_tokens": estimated_tokens,
            "user_messages": sum(1 for msg in messages if msg.role == "user"),
            "assistant_messages": sum(1 for msg in messages if msg.role == "assistant")
        }


# Global conversation manager instance
_conversation_manager: Optional[ConversationManager] = None


def get_conversation_manager() -> ConversationManager:
    """
    Get or create the global conversation manager instance.
    
    Returns:
        ConversationManager: Singleton conversation manager instance
    """
    global _conversation_manager
    if _conversation_manager is None:
        _conversation_manager = ConversationManager()
    return _conversation_manager

