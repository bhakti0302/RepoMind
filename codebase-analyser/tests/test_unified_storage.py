#!/usr/bin/env python3
"""
Test script for the unified storage system.

This script demonstrates how to use the unified storage system to store and retrieve
code chunks with graph metadata.
"""

import os
import json
import argparse
import logging
from pathlib import Path
import numpy as np

from codebase_analyser.database import open_unified_storage, close_unified_storage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_sample_chunks(file_path: str) -> list:
    """Load sample chunks from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        List of code chunk dictionaries
    """
    logger.info(f"Loading sample chunks from {file_path}")
    with open(file_path, 'r') as f:
        chunks = json.load(f)
    logger.info(f"Loaded {len(chunks)} chunks")
    return chunks


def load_sample_dependencies(file_path: str) -> list:
    """Load sample dependencies from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        List of dependency dictionaries
    """
    logger.info(f"Loading sample dependencies from {file_path}")
    with open(file_path, 'r') as f:
        dependencies = json.load(f)
    logger.info(f"Loaded {len(dependencies)} dependencies")
    return dependencies


def generate_random_embeddings(chunks: list, embedding_dim: int = 768) -> list:
    """Generate random embeddings for chunks.
    
    Args:
        chunks: List of code chunk dictionaries
        embedding_dim: Dimension of the embedding vectors
        
    Returns:
        List of code chunk dictionaries with embeddings
    """
    logger.info(f"Generating random embeddings for {len(chunks)} chunks")
    for chunk in chunks:
        # Generate a random embedding
        embedding = np.random.randn(embedding_dim).astype(np.float32)
        # Normalize the embedding
        embedding = embedding / np.linalg.norm(embedding)
        # Add the embedding to the chunk
        chunk["embedding"] = embedding.tolist()
    return chunks


def main():
    """Main function."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Test the unified storage system")
    parser.add_argument("--db-path", type=str, default="codebase-analyser/.lancedb",
                        help="Path to the LanceDB database")
    parser.add_argument("--clear-db", action="store_true",
                        help="Clear the database before testing")
    parser.add_argument("--full-schema", action="store_true",
                        help="Use the full schema instead of the minimal schema")
    args = parser.parse_args()

    # Load sample chunks and dependencies
    chunks = load_sample_chunks("samples/sample_chunks.json")
    dependencies = load_sample_dependencies("samples/sample_dependencies.json")

    # Generate random embeddings for the chunks
    chunks = generate_random_embeddings(chunks)

    # Prepare chunks for database storage
    print("Preparing chunks for database storage...")
    for chunk in chunks:
        # Make sure metadata is a dictionary
        if "metadata" not in chunk:
            chunk["metadata"] = {}

    # Open a unified storage connection
    print("Opening unified storage connection...")
    storage_manager = open_unified_storage(
        db_path=args.db_path,
        use_minimal_schema=not args.full_schema,
        create_if_not_exists=True,
        read_only=False
    )

    try:
        # Clear the database if requested
        if args.clear_db:
            print("Clearing database...")
            storage_manager.db_manager.clear_tables()

        # Add chunks with graph metadata to the database
        print("Adding chunks with graph metadata to the database...")
        storage_manager.add_code_chunks_with_graph_metadata(
            chunks=chunks,
            dependencies=dependencies
        )

        # Search for chunks with vector similarity
        print("Searching for chunks with vector similarity...")
        query_embedding = np.random.randn(storage_manager.embedding_dim).astype(np.float32)
        query_embedding = query_embedding / np.linalg.norm(query_embedding)
        results = storage_manager.db_manager.search_code_chunks(
            query_embedding=query_embedding.tolist(),
            limit=5
        )
        print(f"Found {len(results)} chunks")
        for i, result in enumerate(results):
            print(f"Result {i+1}: {result.get('name', 'Unknown')} ({result.get('node_id', 'Unknown')})")

        # Search for chunks with dependency filters
        print("Searching for chunks with dependency filters...")
        results = storage_manager.search_with_dependencies(
            query_embedding=query_embedding.tolist(),
            dependency_filter={"has_imports": True},
            limit=5
        )
        print(f"Found {len(results)} chunks with imports")
        for i, result in enumerate(results):
            print(f"Result {i+1}: {result.get('name', 'Unknown')} ({result.get('node_id', 'Unknown')})")

        # Get a chunk with its dependencies
        if results:
            print("Getting a chunk with its dependencies...")
            chunk_id = results[0]["node_id"]
            chunk = storage_manager.get_chunk_with_dependencies(chunk_id)
            print(f"Got chunk {chunk.get('name', 'Unknown')} ({chunk.get('node_id', 'Unknown')})")
            
            # Parse metadata
            metadata = json.loads(chunk["metadata"]) if isinstance(chunk["metadata"], str) else chunk["metadata"]
            if "dependencies" in metadata:
                print(f"Incoming dependencies: {len(metadata['dependencies']['incoming'])}")
                print(f"Outgoing dependencies: {len(metadata['dependencies']['outgoing'])}")

    finally:
        # Close the unified storage connection
        print("Closing unified storage connection...")
        close_unified_storage(storage_manager)


if __name__ == "__main__":
    main()
