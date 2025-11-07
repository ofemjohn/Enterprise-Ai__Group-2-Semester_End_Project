"""
Data Processing Script

This script processes the crawled JSONL data:
1. Loads data from JSONL file
2. Chunks the text
3. Generates embeddings
4. Uploads to Pinecone vector database

Run with:
    python scripts/process_data.py
"""

import json
import sys
import hashlib
from pathlib import Path
from typing import List, Dict
from tqdm import tqdm

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.app.services.embedding_service import get_embedding_service
from backend.app.services.pinecone_service import get_pinecone_service
from backend.app.services.text_chunker import get_default_chunker
from backend.app.utils.logger import logger


def load_jsonl_data(file_path: Path) -> List[Dict]:
    """
    Load data from JSONL file.
    
    Args:
        file_path: Path to JSONL file
        
    Returns:
        List[Dict]: List of documents with url, depth, and text
    """
    logger.info(f"Loading data from {file_path}")
    documents = []
    
    with open(file_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            try:
                doc = json.loads(line.strip())
                if doc.get("text") and doc.get("text").strip():
                    documents.append(doc)
            except json.JSONDecodeError as e:
                logger.warning(f"Skipping invalid JSON on line {line_num}: {e}")
                continue
    
    logger.info(f"Loaded {len(documents)} documents from {file_path}")
    return documents


def process_and_upload(
    documents: List[Dict],
    embedding_service,
    pinecone_service,
    chunker,
    batch_size: int = 100
):
    """
    Process documents and upload to Pinecone.
    
    Args:
        documents: List of documents to process
        embedding_service: Embedding service instance
        pinecone_service: Pinecone service instance
        chunker: Text chunker instance
        batch_size: Batch size for processing
    """
    logger.info(f"Processing {len(documents)} documents...")
    
    all_vectors = []
    total_chunks = 0
    
    # Process documents
    for doc in tqdm(documents, desc="Processing documents"):
        url = doc.get("url", "")
        text = doc.get("text", "")
        depth = doc.get("depth", 0)
        
        # Chunk the text
        chunks = chunker.chunk_text(
            text,
            metadata={
                "url": url,
                "depth": depth,
                "source": url
            }
        )
        
        # Generate embeddings for chunks
        chunk_texts = [chunk["text"] for chunk in chunks]
        embeddings = embedding_service.embed_texts(chunk_texts, show_progress=False)
        
        # Prepare vectors for Pinecone
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            # Generate unique vector ID
            text_hash = hashlib.md5(chunk['text'].encode()).hexdigest()[:8]
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            vector_id = f"{url_hash}_{i}_{text_hash}"
            
            # Prepare metadata (store full text - chunks are limited to 500 chars so within Pinecone limits)
            metadata = {
                "url": url,
                "depth": str(depth),  # Pinecone metadata values must be strings, numbers, or booleans
                "chunk_index": str(i),
                "text": chunk["text"]  # Store full chunk text for RAG
            }
            
            vector = {
                "id": vector_id,
                "values": embedding,
                "metadata": metadata
            }
            all_vectors.append(vector)
            total_chunks += 1
        
        # Upload in batches
        if len(all_vectors) >= batch_size:
            pinecone_service.upsert_vectors(all_vectors)
            all_vectors = []
    
    # Upload remaining vectors
    if all_vectors:
        pinecone_service.upsert_vectors(all_vectors)
    
    logger.info(f"Successfully processed and uploaded {total_chunks} chunks from {len(documents)} documents")
    
    # Print index stats
    stats = pinecone_service.get_index_stats()
    logger.info(f"Pinecone index stats: {stats}")


def main():
    """Main function to process data and upload to Pinecone."""
    # Paths
    data_file = project_root / "data" / "raw" / "kennesaw_uits.jsonl"
    
    if not data_file.exists():
        logger.error(f"Data file not found: {data_file}")
        sys.exit(1)
    
    try:
        # Initialize services
        logger.info("Initializing services...")
        embedding_service = get_embedding_service()
        pinecone_service = get_pinecone_service()
        chunker = get_default_chunker()
        
        # Load data
        documents = load_jsonl_data(data_file)
        
        if not documents:
            logger.error("No documents found in data file")
            sys.exit(1)
        
        # Process and upload
        process_and_upload(documents, embedding_service, pinecone_service, chunker)
        
        logger.info("Data processing complete!")
        
    except Exception as e:
        logger.error(f"Error processing data: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

