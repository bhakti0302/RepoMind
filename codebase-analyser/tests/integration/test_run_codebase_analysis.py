#!/usr/bin/env python3
"""
Test script for the run_codebase_analysis.py service.

This script tests the codebase analysis service by loading sample data
and running the complete analysis pipeline sequentially.
"""

import os
import json
import logging
import argparse
from pathlib import Path
import numpy as np

from codebase_analyser.database import open_unified_storage, close_unified_storage
from codebase_analyser.graph.visualizer import visualize_dependency_graph

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Test the codebase analysis service")

    parser.add_argument("--db-path", default=".lancedb", help="Path to the LanceDB database")
    parser.add_argument("--clear-db", action="store_true", help="Clear the database before processing")
    parser.add_argument("--minimal-schema", action="store_true", help="Use minimal schema for reduced storage")
    parser.add_argument("--output-dir", default="samples", help="Directory to save visualization outputs")
    parser.add_argument("--graph-format", default="png", choices=["png", "dot"], help="Format for graph visualization")

    return parser.parse_args()


def load_sample_data():
    """Load sample chunks and dependencies from the samples directory."""
    # Load sample chunks
    chunks_path = os.path.join("samples", "sample_chunks.json")
    with open(chunks_path, "r") as f:
        chunks = json.load(f)

    # Load sample dependencies
    dependencies_path = os.path.join("samples", "sample_dependencies.json")
    with open(dependencies_path, "r") as f:
        dependencies = json.load(f)

    logger.info(f"Loaded {len(chunks)} chunks and {len(dependencies)} dependencies from samples")
    return chunks, dependencies


def add_mock_embeddings(chunks):
    """Add mock embeddings to chunks."""
    embedding_dim = 768
    for chunk in chunks:
        # Generate a random embedding
        embedding = np.random.randn(embedding_dim).astype(np.float32)
        # Normalize the embedding
        embedding = embedding / np.linalg.norm(embedding)
        # Add the embedding to the chunk
        chunk["embedding"] = embedding.tolist()

    logger.info(f"Added mock embeddings to {len(chunks)} chunks")
    return chunks


def convert_graph_to_visualization_format(graph):
    """Convert a NetworkX graph to the format expected by the visualization function."""
    dependency_graph = {
        'nodes': [],
        'edges': []
    }

    # Add nodes
    for node_id, node_attrs in graph.nodes(data=True):
        node = {
            'id': node_id,
            'type': node_attrs.get('type', 'unknown'),
            'name': node_attrs.get('name', node_id),
            'qualified_name': node_attrs.get('qualified_name', node_id)
        }
        dependency_graph['nodes'].append(node)

    # Add edges
    for source, target, edge_attrs in graph.edges(data=True):
        edge = {
            'source_id': source,
            'target_id': target,
            'type': edge_attrs.get('type', 'UNKNOWN'),
            'strength': edge_attrs.get('strength', 1.0),
            'is_direct': edge_attrs.get('is_direct', True),
            'is_required': edge_attrs.get('is_required', False),
            'description': edge_attrs.get('description', '')
        }
        dependency_graph['edges'].append(edge)

    return dependency_graph


def main():
    """Main entry point."""
    args = parse_args()

    # Test both methods:
    # 1. Using the sample data
    test_with_sample_data(args)

    # 2. Using the complex Java project
    test_with_complex_java_project(args)

    logger.info("All tests completed successfully!")


def test_with_sample_data(args):
    """Test using the sample data."""
    logger.info("=== TESTING WITH SAMPLE DATA ===")

    # Step 1: Load sample data
    logger.info("Step 1: Loading sample data")
    chunks, dependencies = load_sample_data()

    # Step 2: Add mock embeddings
    logger.info("Step 2: Adding mock embeddings")
    chunks = add_mock_embeddings(chunks)

    # Step 3: Store in database
    logger.info("Step 3: Storing in database")
    storage_manager = open_unified_storage(
        db_path=args.db_path,
        use_minimal_schema=args.minimal_schema,
        create_if_not_exists=True,
        read_only=False
    )

    try:
        # Clear database if requested
        if args.clear_db:
            logger.info("Clearing database")
            storage_manager.db_manager.clear_tables()

        # Add chunks with graph metadata
        logger.info("Adding chunks with graph metadata")
        storage_manager.add_code_chunks_with_graph_metadata(chunks=chunks)

        # Step 4: Generate visualization
        logger.info("Step 4: Generating dependency graph visualization")

        # Build the graph
        nx_graph = storage_manager._build_graph_from_dependencies()

        # Convert NetworkX graph to the expected format
        dependency_graph = convert_graph_to_visualization_format(nx_graph)

        # Create output directory if it doesn't exist
        os.makedirs(args.output_dir, exist_ok=True)

        # Generate visualization
        output_file = os.path.join(args.output_dir, f"test_sample_data_graph.{args.graph_format}")
        visualize_dependency_graph(
            dependency_graph=dependency_graph,
            output_file=output_file,
            title="Sample Data Test Graph",
            layout="spring"
        )
        logger.info(f"Saved visualization to {output_file}")
    finally:
        # Close storage connection
        close_unified_storage(storage_manager)

    logger.info("Sample data test completed successfully!")


def test_with_complex_java_project(args):
    """Test using the complex Java project."""
    logger.info("=== TESTING WITH COMPLEX JAVA PROJECT ===")

    # Import the run_codebase_analysis module
    import sys
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    from run_codebase_analysis import analyze_codebase

    # Create a mock args object for analyze_codebase
    class MockArgs:
        repo_path = os.path.join(os.path.dirname(__file__), "samples", "complex_java_project")
        db_path = args.db_path
        clear_db = args.clear_db
        minimal_schema = args.minimal_schema
        embedding_model = "microsoft/codebert-base"
        embedding_batch_size = 8
        embedding_cache_dir = ".cache"
        mock_embeddings = True
        visualize = True
        output_dir = args.output_dir
        graph_format = args.graph_format
        project_id = "complex-java-project"
        max_files = None
        skip_large_files = False

    mock_args = MockArgs()

    # Run the analysis
    logger.info(f"Starting analysis of complex Java project at {mock_args.repo_path}")
    success = analyze_codebase(mock_args)

    if success:
        logger.info("Complex Java project test completed successfully!")
    else:
        logger.error("Complex Java project test failed!")
        raise RuntimeError("Analysis of complex Java project failed")


if __name__ == "__main__":
    main()
