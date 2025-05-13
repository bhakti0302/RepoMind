#!/usr/bin/env python3
"""
Codebase Analysis Service

This script runs the entire Epic 2 pipeline:
1. Parse codebase and generate chunks
2. Analyze dependencies between chunks
3. Generate embeddings
4. Store everything in the database
5. Optionally visualize the dependency graph

Usage:
    python run_codebase_analysis.py --repo-path /path/to/repo [options]
"""

import os
import sys
import argparse
import logging
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

from codebase_analyser import CodebaseAnalyser
from codebase_analyser.database import open_unified_storage, close_unified_storage
from codebase_analyser.embeddings import EmbeddingGenerator
from codebase_analyser.graph.visualizer import visualize_dependency_graph
from codebase_analyser.parsing.dependency_analyzer import DependencyAnalyzer
from codebase_analyser.chunking.code_chunk import CodeChunk

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run the complete codebase analysis pipeline")

    # Required arguments
    parser.add_argument("--repo-path", required=True, help="Path to the repository to analyze")

    # Database options
    parser.add_argument("--db-path", default="codebase-analyser/.lancedb", help="Path to the LanceDB database")
    parser.add_argument("--clear-db", action="store_true", help="Clear the database before processing")
    parser.add_argument("--minimal-schema", action="store_true", help="Use minimal schema for reduced storage")

    # Embedding options
    parser.add_argument("--embedding-model", default="microsoft/codebert-base", help="Model to use for embeddings")
    parser.add_argument("--embedding-batch-size", type=int, default=8, help="Batch size for embedding generation")
    parser.add_argument("--embedding-cache-dir", default=".cache", help="Cache directory for embeddings")
    parser.add_argument("--mock-embeddings", action="store_true", help="Use mock embeddings instead of a real model")

    # Visualization options
    parser.add_argument("--visualize", action="store_true", help="Generate dependency graph visualization")
    parser.add_argument("--output-dir", default="samples", help="Directory to save visualization outputs")
    parser.add_argument("--graph-format", default="png", choices=["png", "dot"], help="Format for graph visualization")

    # Project options
    parser.add_argument("--project-id", help="Project ID for multi-project support")

    # Performance options
    parser.add_argument("--max-files", type=int, help="Maximum number of files to process (for testing)")
    parser.add_argument("--skip-large-files", action="store_true", help="Skip files larger than 1MB")

    return parser.parse_args()


def analyze_codebase(args):
    """Run the complete codebase analysis pipeline."""
    start_time = time.time()
    repo_path = args.repo_path

    # Validate repository path
    if not os.path.isdir(repo_path):
        logger.error(f"Repository path does not exist: {repo_path}")
        return False

    logger.info(f"Starting analysis of repository: {repo_path}")

    # Step 1: Parse codebase and generate chunks
    logger.info("Step 1: Parsing codebase and generating chunks")
    analyzer = CodebaseAnalyser(repo_path)

    # Process files
    file_count = 0
    skipped_count = 0
    max_files = args.max_files if args.max_files else float('inf')

    all_chunks = []

    for root, _, files in os.walk(repo_path):
        for file in files:
            if file_count >= max_files:
                break

            file_path = Path(os.path.join(root, file))

            # Skip hidden files and directories
            if file.startswith('.') or any(part.startswith('.') for part in file_path.parts):
                continue

            # Skip large files if requested
            if args.skip_large_files and os.path.getsize(file_path) > 1024 * 1024:  # 1MB
                logger.warning(f"Skipping large file: {file_path}")
                skipped_count += 1
                continue

            try:
                logger.info(f"Parsing file: {file_path}")
                result = analyzer.parse_file(file_path)
                if result:
                    chunks = analyzer.get_chunks(result)
                    logger.info(f"Generated {len(chunks)} chunks for {file_path}")

                    # Convert chunks to dictionaries
                    for chunk in chunks:
                        if isinstance(chunk, dict):
                            chunk_dict = chunk
                        else:
                            chunk_dict = chunk.to_dict()

                        # Add project_id if provided
                        if args.project_id:
                            chunk_dict["project_id"] = args.project_id

                        all_chunks.append(chunk_dict)

                    # Extract dependencies if available
                    if 'dependencies' in result and result['dependencies']:
                        logger.info(f"Found {len(result['dependencies'])} dependencies for {file_path}")

                        # Add dependencies to the chunks for better graph building
                        for chunk in all_chunks:
                            if 'dependencies' not in chunk:
                                chunk['dependencies'] = []
                            if 'reference_ids' not in chunk:
                                chunk['reference_ids'] = []
                            if 'metadata' not in chunk:
                                chunk['metadata'] = {}
                            if 'reference_types' not in chunk['metadata']:
                                chunk['metadata']['reference_types'] = {}

                        # Add the dependencies to the appropriate chunks
                        for dep in result['dependencies']:
                            source_id = dep['source_id']
                            target_id = dep['target_id']
                            dep_type = dep.get('type', 'REFERENCES')

                            # Find the source chunk
                            for chunk in all_chunks:
                                if chunk.get('node_id') == source_id:
                                    # Add dependency to the chunk
                                    chunk['dependencies'].append(dep)

                                    # Add reference_id for the database
                                    if target_id not in chunk['reference_ids']:
                                        chunk['reference_ids'].append(target_id)

                                    # Add reference type for the database
                                    chunk['metadata']['reference_types'][target_id] = dep_type

                    file_count += 1
            except Exception as e:
                logger.error(f"Error parsing file {file_path}: {e}")
                skipped_count += 1

    logger.info(f"Parsed {file_count} files, skipped {skipped_count} files")
    logger.info(f"Generated {len(all_chunks)} chunks in total")

    if not all_chunks:
        logger.error("No chunks generated. Aborting.")
        return False

    # Step 2: Analyze dependencies
    logger.info("Step 2: Analyzing dependencies")

    # Convert dictionary chunks to CodeChunk objects for dependency analysis
    code_chunks = []
    chunk_map = {}  # Map of node_id to CodeChunk objects

    # First pass: create all chunks
    for chunk_dict in all_chunks:
        # Create the chunk
        chunk = CodeChunk(
            node_id=chunk_dict.get('node_id', ''),
            chunk_type=chunk_dict.get('chunk_type', 'unknown'),
            content=chunk_dict.get('content', ''),
            file_path=chunk_dict.get('file_path', ''),
            start_line=chunk_dict.get('start_line', 0),
            end_line=chunk_dict.get('end_line', 0),
            language=chunk_dict.get('language', 'unknown'),
            name=chunk_dict.get('name', ''),
            qualified_name=chunk_dict.get('qualified_name', '')
        )

        # Add metadata and context
        if 'metadata' in chunk_dict:
            chunk.metadata = chunk_dict['metadata']
        if 'context' in chunk_dict:
            chunk.context = chunk_dict['context']

        # Store in map and list
        chunk_map[chunk.node_id] = chunk
        code_chunks.append(chunk)

    # Second pass: set parent-child relationships
    for chunk_dict in all_chunks:
        if 'parent_id' in chunk_dict and chunk_dict['parent_id'] is not None:
            child = chunk_map.get(chunk_dict['node_id'])
            parent = chunk_map.get(chunk_dict['parent_id'])
            if child and parent:
                parent.add_child(child)

    # Run dependency analysis
    dependency_analyzer = DependencyAnalyzer()
    dependency_graph = dependency_analyzer.analyze_dependencies(code_chunks)

    # Add dependencies to chunks
    for edge in dependency_graph.edges:
        source_id = edge.source_id
        target_id = edge.target_id

        # Find the source chunk in all_chunks
        for chunk in all_chunks:
            if chunk.get('node_id') == source_id:
                # Add reference_id if not already present
                if 'reference_ids' not in chunk:
                    chunk['reference_ids'] = []
                if target_id not in chunk['reference_ids']:
                    chunk['reference_ids'].append(target_id)

                # Add reference type
                if 'metadata' not in chunk:
                    chunk['metadata'] = {}
                if 'reference_types' not in chunk['metadata']:
                    chunk['metadata']['reference_types'] = {}
                chunk['metadata']['reference_types'][target_id] = edge.type.name

    logger.info(f"Found {len(dependency_graph.edges)} dependencies between chunks")

    # Step 3: Generate embeddings
    logger.info("Step 3: Generating embeddings")

    if args.mock_embeddings:
        logger.info("Using mock embeddings")
        import numpy as np

        # Generate mock embeddings (768-dimensional random vectors)
        embedding_dim = 768
        for chunk in all_chunks:
            # Generate a random embedding
            embedding = np.random.randn(embedding_dim).astype(np.float32)
            # Normalize the embedding
            embedding = embedding / np.linalg.norm(embedding)
            # Add the embedding to the chunk
            chunk["embedding"] = embedding.tolist()

        logger.info(f"Generated mock embeddings for {len(all_chunks)} chunks")
    else:
        logger.info("Using real embeddings with model: " + args.embedding_model)
        embedding_generator = EmbeddingGenerator(
            model_name=args.embedding_model,
            cache_dir=args.embedding_cache_dir,
            batch_size=args.embedding_batch_size
        )

        try:
            # Process chunks in batches
            batch_size = args.embedding_batch_size
            for i in range(0, len(all_chunks), batch_size):
                batch = all_chunks[i:i+batch_size]

                # Extract content and language for each chunk
                contents = [chunk["content"] for chunk in batch]
                languages = [chunk["language"] for chunk in batch]

                # Generate embeddings
                embeddings = embedding_generator.generate_embeddings_batch(contents, languages)

                # Add embeddings to chunks
                for j, embedding in enumerate(embeddings):
                    batch[j]["embedding"] = embedding.tolist()

                logger.info(f"Generated embeddings for batch {i//batch_size + 1}/{(len(all_chunks) + batch_size - 1)//batch_size}")
        finally:
            embedding_generator.close()

    # Step 4: Store in database
    logger.info("Step 4: Storing in database")
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
        storage_manager.add_code_chunks_with_graph_metadata(chunks=all_chunks)

        # Create dependencies table
        logger.info("Creating dependencies table")
        try:
            from scripts.create_dependencies_table import create_dependencies_table
            create_dependencies_table(args.project_id, args.db_path)
            logger.info("Dependencies table created successfully")
        except Exception as e:
            logger.error(f"Error creating dependencies table: {e}")

        # Generate UML-style diagrams
        logger.info("Generating UML-style diagrams")
        try:
            from scripts.generate_uml_diagrams import generate_uml_diagrams

            # Path to the central visualizations directory
            visualizations_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                             'data', 'visualizations', args.project_id)

            # Create the directory if it doesn't exist
            os.makedirs(visualizations_dir, exist_ok=True)

            # Generate the diagrams
            generate_uml_diagrams(args.project_id, visualizations_dir, args.db_path)
            logger.info("UML-style diagrams generated successfully")
        except Exception as e:
            logger.error(f"Error generating UML-style diagrams: {e}")

        # Generate colored relationship diagrams
        logger.info("Generating colored relationship diagrams")
        try:
            from scripts.generate_colored_diagrams import generate_multi_file_relationships, generate_relationship_types
            from datetime import datetime

            # Generate timestamp for filenames
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

            # Generate the diagrams
            multi_file_path = os.path.join(visualizations_dir, f"{args.project_id}_multi_file_relationships_{timestamp}.png")
            relationship_types_path = os.path.join(visualizations_dir, f"{args.project_id}_relationship_types_{timestamp}.png")

            generate_multi_file_relationships(multi_file_path)
            generate_relationship_types(relationship_types_path)

            logger.info("Colored relationship diagrams generated successfully")
        except Exception as e:
            logger.error(f"Error generating colored relationship diagrams: {e}")

        # Step 5: Generate visualization if requested
        if args.visualize:
            logger.info("Step 5: Generating dependency graph visualization")

            # Build the graph
            nx_graph = storage_manager._build_graph_from_dependencies()

            # Convert NetworkX graph to the expected format
            dependency_graph = {
                'nodes': [],
                'edges': []
            }

            # Add nodes
            for node_id, node_attrs in nx_graph.nodes(data=True):
                node = {
                    'id': node_id,
                    'type': node_attrs.get('type', 'unknown'),
                    'name': node_attrs.get('name', node_id),
                    'qualified_name': node_attrs.get('qualified_name', node_id)
                }
                dependency_graph['nodes'].append(node)

            # Add edges
            for source, target, edge_attrs in nx_graph.edges(data=True):
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

            # Create output directory if it doesn't exist
            os.makedirs(args.output_dir, exist_ok=True)

            # Generate visualization
            output_file = os.path.join(args.output_dir, f"dependency_graph.{args.graph_format}")
            visualize_dependency_graph(
                dependency_graph=dependency_graph,
                output_file=output_file,
                title="Dependency Graph",
                layout="spring"
            )
            logger.info(f"Saved visualization to {output_file}")
    finally:
        # Close storage connection
        close_unified_storage(storage_manager)

    elapsed_time = time.time() - start_time
    logger.info(f"Analysis completed in {elapsed_time:.2f} seconds")
    return True


def main():
    """Main entry point."""
    args = parse_args()
    success = analyze_codebase(args)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
