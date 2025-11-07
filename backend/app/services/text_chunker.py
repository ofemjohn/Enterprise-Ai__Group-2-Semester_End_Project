"""
Text Chunking Service

This service handles text chunking for RAG systems.
Splits long documents into smaller, overlapping chunks for better retrieval.
"""

from typing import List
import re


class TextChunker:
    """Service for chunking text into smaller pieces for embedding."""
    
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        separators: List[str] = None
    ):
        """
        Initialize the text chunker.
        
        Args:
            chunk_size: Maximum number of characters per chunk
            chunk_overlap: Number of characters to overlap between chunks
            separators: List of separators to use for splitting (in order of preference)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", ". ", " ", ""]
    
    def chunk_text(self, text: str, metadata: dict = None) -> List[dict]:
        """
        Split text into chunks with overlap.
        
        Args:
            text: Text to chunk
            metadata: Optional metadata to attach to each chunk
            
        Returns:
            List[dict]: List of chunks with 'text' and 'metadata' keys
        """
        if not text or not text.strip():
            return []
        
        # Clean and normalize text
        text = text.strip()
        
        # Try to split by separators first
        chunks = self._split_by_separators(text)
        
        # If chunks are still too large, split by character
        final_chunks = []
        for chunk in chunks:
            if len(chunk) <= self.chunk_size:
                final_chunks.append(chunk)
            else:
                # Split large chunks by character
                final_chunks.extend(self._split_by_size(chunk))
        
        # Add overlap between chunks
        overlapped_chunks = self._add_overlap(final_chunks)
        
        # Format chunks with metadata
        result = []
        for i, chunk_text in enumerate(overlapped_chunks):
            chunk_metadata = {
                "chunk_index": i,
                "total_chunks": len(overlapped_chunks),
                **(metadata or {})
            }
            result.append({
                "text": chunk_text,
                "metadata": chunk_metadata
            })
        
        return result
    
    def _split_by_separators(self, text: str) -> List[str]:
        """Split text by separators, trying each separator in order."""
        chunks = [text]
        
        for separator in self.separators:
            if not separator:
                # Last resort: split by character
                break
            
            new_chunks = []
            for chunk in chunks:
                if len(chunk) <= self.chunk_size:
                    new_chunks.append(chunk)
                else:
                    # Split by this separator
                    parts = chunk.split(separator)
                    current_chunk = ""
                    
                    for part in parts:
                        if len(current_chunk) + len(separator) + len(part) <= self.chunk_size:
                            current_chunk += (separator if current_chunk else "") + part
                        else:
                            if current_chunk:
                                new_chunks.append(current_chunk)
                            current_chunk = part
                    
                    if current_chunk:
                        new_chunks.append(current_chunk)
            
            # If all chunks are small enough, we're done
            if all(len(chunk) <= self.chunk_size for chunk in new_chunks):
                chunks = new_chunks
                break
            
            chunks = new_chunks
        
        return chunks
    
    def _split_by_size(self, text: str) -> List[str]:
        """Split text into chunks of specified size."""
        chunks = []
        for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
            chunk = text[i:i + self.chunk_size]
            if chunk.strip():
                chunks.append(chunk)
        return chunks
    
    def _add_overlap(self, chunks: List[str]) -> List[str]:
        """Add overlap between chunks for better context preservation."""
        if len(chunks) <= 1 or self.chunk_overlap == 0:
            return chunks
        
        overlapped = []
        for i, chunk in enumerate(chunks):
            if i == 0:
                # First chunk: add overlap from next chunk
                if len(chunks) > 1:
                    next_preview = chunks[1][:self.chunk_overlap]
                    overlapped.append(chunk + " " + next_preview)
                else:
                    overlapped.append(chunk)
            elif i == len(chunks) - 1:
                # Last chunk: add overlap from previous chunk
                prev_preview = chunks[i-1][-self.chunk_overlap:]
                overlapped.append(prev_preview + " " + chunk)
            else:
                # Middle chunks: add overlap from both sides
                prev_preview = chunks[i-1][-self.chunk_overlap:]
                next_preview = chunks[i+1][:self.chunk_overlap]
                overlapped.append(prev_preview + " " + chunk + " " + next_preview)
        
        return overlapped


def get_default_chunker() -> TextChunker:
    """
    Get a default text chunker instance.
    
    Returns:
        TextChunker: Default chunker with standard settings
    """
    return TextChunker(
        chunk_size=500,  # ~100-150 words
        chunk_overlap=50  # ~10-15 words overlap
    )

