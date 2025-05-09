#!/usr/bin/env python3
"""
Test script for custom relevance scoring.

This script demonstrates how to use the custom relevance scoring that combines
semantic similarity and graph proximity.
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

    # Add some additional dependencies for testing
    logger.info("Adding additional dependencies for testing")
    additional_deps = [
        {
            "source_id": "file:samples/SimpleClass.java",
            "target_id": "file:sample1.java",
            "type": "IMPORTS",
            "is_direct": True,
            "is_required": True,
            "strength": 1.0,
            "description": "Test dependency"
        },
        {
            "source_id": "file:sample1.java",
            "target_id": "class:HelloWorld",
            "type": "CONTAINS",
            "is_direct": True,
            "is_required": True,
            "strength": 1.0,
            "description": "Test dependency"
        },
        {
            "source_id": "class:HelloWorld",
            "target_id": "method:HelloWorld.main",
            "type": "CONTAINS",
            "is_direct": True,
            "is_required": True,
            "strength": 1.0,
            "description": "Test dependency"
        },
        {
            "source_id": "file:samples/SimpleClass.java",
            "target_id": "file:sample2.py",
            "type": "IMPORTS",
            "is_direct": True,
            "is_required": True,
            "strength": 0.5,
            "description": "Test dependency"
        },
        {
            "source_id": "file:sample2.py",
            "target_id": "function:hello_world",
            "type": "CONTAINS",
            "is_direct": True,
            "is_required": True,
            "strength": 1.0,
            "description": "Test dependency"
        },
        {
            "source_id": "file:samples/SimpleClass.java",
            "target_id": "file:sample3.js",
            "type": "IMPORTS",
            "is_direct": True,
            "is_required": True,
            "strength": 0.3,
            "description": "Test dependency"
        },
        {
            "source_id": "file:sample3.js",
            "target_id": "function:helloWorld",
            "type": "CONTAINS",
            "is_direct": True,
            "is_required": True,
            "strength": 1.0,
            "description": "Test dependency"
        }
    ]
    dependencies.extend(additional_deps)
    logger.info(f"Added {len(additional_deps)} additional dependencies")

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
    parser = argparse.ArgumentParser(description="Test custom relevance scoring")
    parser.add_argument("--db-path", type=str, default="codebase-analyser/.lancedb",
                        help="Path to the LanceDB database")
    parser.add_argument("--clear-db", action="store_true",
                        help="Clear the database before testing")
    parser.add_argument("--alpha", type=float, default=0.7,
                        help="Weight for semantic similarity (0.0 to 1.0)")
    parser.add_argument("--beta", type=float, default=0.3,
                        help="Weight for graph proximity (0.0 to 1.0)")
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
        # Add vector field for compatibility with different LanceDB versions
        if "embedding" in chunk and "vector" not in chunk:
            chunk["vector"] = chunk["embedding"]

    # Open a unified storage connection
    print("Opening unified storage connection...")
    storage_manager = open_unified_storage(
        db_path=args.db_path,
        use_minimal_schema=True,
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

        # Use a node ID that exists in the graph
        query_node_id = "file:samples/SimpleClass.java"
        print(f"Using query node: {query_node_id}")

        # Generate a query embedding
        query_embedding = np.random.randn(storage_manager.embedding_dim).astype(np.float32)
        query_embedding = query_embedding / np.linalg.norm(query_embedding)

        # Try the combined scoring method directly
        print("\nTesting combined scoring directly...")
        try:
            combined_results = storage_manager.search_with_combined_scoring(
                query_embedding=query_embedding.tolist(),
                query_node_id=query_node_id,
                alpha=args.alpha,
                beta=args.beta,
                limit=10
            )
            
            if combined_results:
                print(f"\nFound {len(combined_results)} results with combined scoring")
                for i, result in enumerate(combined_results[:5]):
                    print(f"Result {i+1}: {result.get('name', 'Unknown')} ({result.get('node_id', 'Unknown')})")
                    print(f"  Semantic Score: {result.get('semantic_score', 0.0):.4f}")
                    print(f"  Graph Proximity: {result.get('graph_proximity', 0.0):.4f}")
                    print(f"  Combined Score: {result.get('combined_score', 0.0):.4f}")
            else:
                print("No results found with combined scoring. Falling back to manual calculation.")
                # Fall back to manual calculation
                manual_test_combined_scoring(storage_manager, chunks, query_node_id, query_embedding, args.alpha, args.beta)
        except Exception as e:
            print(f"Combined scoring search failed: {e}")
            print("Falling back to manual calculation.")
            # Fall back to manual calculation
            manual_test_combined_scoring(storage_manager, chunks, query_node_id, query_embedding, args.alpha, args.beta)

    finally:
        # Close the unified storage connection
        print("Closing unified storage connection...")
        close_unified_storage(storage_manager)


def manual_test_combined_scoring(storage_manager, all_chunks, query_node_id, query_embedding, alpha, beta):
    """Test combined scoring manually when the built-in method fails."""
    print("\nTesting combined scoring manually...")

    # Use the chunks we already have
    print(f"Using {len(all_chunks)} chunks for testing")

    # Build the graph
    G = storage_manager._build_graph_from_dependencies()
    print(f"Built graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")

    # Print the nodes in the graph
    print("\nNodes in the graph:")
    for node in G.nodes():
        print(f"  {node}")

    # Calculate semantic similarity scores (simulated)
    print("\nCalculating semantic similarity scores...")
    for chunk in all_chunks:
        # Calculate actual cosine similarity
        if "embedding" in chunk:
            chunk_embedding = np.array(chunk["embedding"])
            query_embedding_np = np.array(query_embedding)
            # Normalize embeddings
            chunk_embedding = chunk_embedding / np.linalg.norm(chunk_embedding)
            query_embedding_np = query_embedding_np / np.linalg.norm(query_embedding_np)
            # Calculate cosine similarity
            chunk["semantic_score"] = np.dot(chunk_embedding, query_embedding_np)
        else:
            # Generate a random similarity score for demonstration
            chunk["semantic_score"] = np.random.random()
        
        print(f"Chunk {chunk['node_id']}: Semantic Score = {chunk['semantic_score']:.4f}")

    # Calculate graph proximity scores
    print("\nCalculating graph proximity scores...")
    for chunk in all_chunks:
        # Calculate graph distance
        try:
            graph_distance = storage_manager._calculate_graph_distance(G, query_node_id, chunk["node_id"])
            # Convert to proximity score
            chunk["graph_proximity"] = 1.0 / (1.0 + graph_distance) if graph_distance < float('inf') else 0.0
        except Exception as e:
            print(f"Error calculating graph distance for {chunk['node_id']}: {e}")
            chunk["graph_proximity"] = 0.0
        
        print(f"Chunk {chunk['node_id']}: Graph Distance = {graph_distance if 'graph_distance' in locals() else 'N/A'}, Proximity = {chunk['graph_proximity']:.4f}")

    # Calculate combined scores
    print(f"\nCalculating combined scores (alpha={alpha}, beta={beta})...")
    for chunk in all_chunks:
        chunk["combined_score"] = alpha * chunk["semantic_score"] + beta * chunk["graph_proximity"]
        print(f"Chunk {chunk['node_id']}: Combined Score = {chunk['combined_score']:.4f}")

    # Sort by combined score
    all_chunks.sort(key=lambda x: x["combined_score"], reverse=True)

    # Print top results
    print("\nTop results by combined score:")
    for i, chunk in enumerate(all_chunks[:5]):
        print(f"Result {i+1}: {chunk.get('name', 'Unknown')} ({chunk.get('node_id', 'Unknown')})")
        print(f"  Semantic Score: {chunk.get('semantic_score', 0.0):.4f}")
        print(f"  Graph Proximity: {chunk.get('graph_proximity', 0.0):.4f}")
        print(f"  Combined Score: {chunk.get('combined_score', 0.0):.4f}")

    # Sort by semantic score only
    semantic_sorted = sorted(all_chunks, key=lambda x: x["semantic_score"], reverse=True)

    # Print top results by semantic score
    print("\nTop results by semantic score only:")
    for i, chunk in enumerate(semantic_sorted[:5]):
        print(f"Result {i+1}: {chunk.get('name', 'Unknown')} ({chunk.get('node_id', 'Unknown')})")
        print(f"  Semantic Score: {chunk.get('semantic_score', 0.0):.4f}")

    # Compare the results
    print("\nComparing results:")
    combined_ids = [chunk["node_id"] for chunk in all_chunks[:5]]
    semantic_ids = [chunk["node_id"] for chunk in semantic_sorted[:5]]

    # Find differences
    semantic_only = [node_id for node_id in semantic_ids if node_id not in combined_ids]
    combined_only = [node_id for node_id in combined_ids if node_id not in semantic_ids]

    if semantic_only:
        print(f"Results only in semantic search: {semantic_only}")
    if combined_only:
        print(f"Results only in combined search: {combined_only}")

    if not semantic_only and not combined_only:
        print("Both searches returned the same results, but possibly in different order.")


if __name__ == "__main__":
    main()
