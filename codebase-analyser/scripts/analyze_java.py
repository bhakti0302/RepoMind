#!/usr/bin/env python3
"""
Script to analyze Java files using the Java parser adapter.
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from codebase_analyser.parsing.java_parser_adapter import JavaParserAdapter

from codebase_analyser.parsing.java_parser_adapter import JavaParserAdapter
from codebase_analyser.chunking.code_chunk import CodeChunk
from codebase_analyser.database.unified_storage import UnifiedStorage
from codebase_analyser.embeddings.embedding_generator import EmbeddingGenerator
from codebase_analyser.visualization.visualizer import ChunkVisualizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Analyze Java files")
    parser.add_argument("repo_path", help="Path to the repository or directory to analyze")
    parser.add_argument("--db-path", help="Path to the LanceDB database", default=".lancedb")
    parser.add_argument("--data-dir", help="Path to the data directory", default="../data")
    parser.add_argument("--clear-db", action="store_true", help="Clear the database before adding new chunks")
    parser.add_argument("--mock-embeddings", action="store_true", help="Use mock embeddings instead of generating real ones")
    parser.add_argument("--visualize", action="store_true", help="Generate visualization of the dependency graph")
    parser.add_argument("--output-dir", help="Directory to save visualization files", default="samples")
    parser.add_argument("--graph-format", help="Format for the graph visualization", default="png", choices=["png", "svg", "pdf"])
    parser.add_argument("--project-id", help="Project ID for the chunks")
    parser.add_argument("--max-files", type=int, help="Maximum number of files to process", default=100)
    parser.add_argument("--skip-large-files", action="store_true", help="Skip files larger than 1MB")
    parser.add_argument("--embedding-model", help="Model to use for embeddings", default="BAAI/bge-small-en-v1.5")
    parser.add_argument("--embedding-cache-dir", help="Directory to cache embedding models", default=".cache")
    parser.add_argument("--embedding-batch-size", type=int, help="Batch size for embedding generation", default=8)
    parser.add_argument("--minimal-schema", action="store_true", help="Use minimal schema for the database")
    return parser.parse_args()


def analyze_java_files(args):
    """Analyze Java files in the repository."""
    import time
    start_time = time.time()

    repo_path = Path(args.repo_path)
    if not repo_path.exists():
        logger.error(f"Repository path does not exist: {repo_path}")
        return False

    logger.info(f"Starting analysis of repository: {repo_path}")

    # Step 1: Parse Java files and generate chunks
    logger.info("Step 1: Parsing Java files and generating chunks")

    file_count = 0
    skipped_count = 0
    max_files = args.max_files

    all_chunks = []

    # Find all Java files
    java_files = list(repo_path.glob('**/*.java'))
    logger.info(f"Found {len(java_files)} Java files")

    for file_path in java_files:
        if file_count >= max_files:
            break

        # Skip hidden files and directories
        if file_path.name.startswith('.') or any(part.startswith('.') for part in file_path.parts):
            continue

        # Skip large files if requested
        if args.skip_large_files and os.path.getsize(file_path) > 1024 * 1024:  # 1MB
            logger.warning(f"Skipping large file: {file_path}")
            skipped_count += 1
            continue

        try:
            logger.info(f"Parsing file: {file_path}")
            result = JavaParserAdapter.parse_file(file_path)
            if result:
                logger.info(f"Generated {len(result['chunks'])} chunks for {file_path}")

                # Convert chunks to CodeChunk objects
                chunks = []
                chunk_map = {}

                # First pass: create all chunks
                for chunk_data in result['chunks']:
                    # Create the chunk
                    chunk = CodeChunk(
                        node_id=chunk_data['node_id'],
                        chunk_type=chunk_data['chunk_type'],
                        content=chunk_data['content'],
                        file_path=chunk_data['file_path'],
                        start_line=chunk_data['start_line'],
                        end_line=chunk_data['end_line'],
                        language=chunk_data['language'],
                        name=chunk_data.get('name'),
                        qualified_name=chunk_data.get('qualified_name')
                    )

                    # Add metadata and context
                    if 'metadata' in chunk_data:
                        chunk.metadata = chunk_data['metadata']
                    if 'context' in chunk_data:
                        chunk.context = chunk_data['context']

                    # Store in map and list
                    chunk_map[chunk.node_id] = chunk
                    chunks.append(chunk)

                # Second pass: establish parent-child relationships
                for chunk_data in result['chunks']:
                    if 'parent_id' in chunk_data and chunk_data['parent_id']:
                        child = chunk_map.get(chunk_data['node_id'])
                        parent = chunk_map.get(chunk_data['parent_id'])
                        if child and parent:
                            parent.add_child(child)

                # Convert chunks to dictionaries
                for chunk in chunks:
                    chunk_dict = chunk.to_dict()

                    # Add project_id if provided
                    if args.project_id:
                        chunk_dict["project_id"] = args.project_id

                    all_chunks.append(chunk_dict)

                file_count += 1
            else:
                logger.warning(f"Failed to parse {file_path}")
                skipped_count += 1
        except Exception as e:
            logger.error(f"Error parsing file {file_path}: {e}")
            skipped_count += 1

    logger.info(f"Parsed {file_count} files, skipped {skipped_count} files")
    logger.info(f"Generated {len(all_chunks)} chunks in total")

    if not all_chunks:
        logger.error("No chunks generated. Aborting.")
        return False

    # Step 2: Generate embeddings
    logger.info("Step 2: Generating embeddings")

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

    # Step 3: Store in database
    logger.info("Step 3: Storing in database")
    storage_manager = UnifiedStorage(
        db_path=args.db_path,
        data_dir=args.data_dir,
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

        # Step 4: Generate visualization if requested
        if args.visualize:
            logger.info("Step 4: Generating dependency graph visualization")

            try:
                # Try to import matplotlib
                import matplotlib.pyplot as plt
                matplotlib_available = True
            except ImportError:
                logger.warning("Matplotlib is not available. Visualization will be skipped.")
                matplotlib_available = False

            if matplotlib_available:
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

                # Determine project ID
                project_id = args.project_id or os.path.basename(os.path.abspath(args.repo_path))

                # Generate visualization
                output_file = os.path.join(args.output_dir, f"dependency_graph.{args.graph_format}")
                project_vis_file = f"{project_id}_dependency_graph.{args.graph_format}"
                visualizer = ChunkVisualizer(output_dir=args.output_dir)

                # Convert graph nodes to CodeChunk objects
                chunks = []
                for node_id, node_attrs in nx_graph.nodes(data=True):
                    chunk = CodeChunk(
                        node_id=node_id,
                        chunk_type=node_attrs.get('type', 'unknown'),
                        content="",
                        file_path="",
                        start_line=0,
                        end_line=0,
                        language="java",
                        name=node_attrs.get('name', node_id)
                    )
                    chunks.append(chunk)

                # Add references based on graph edges
                for source, target in nx_graph.edges():
                    source_chunk = next((c for c in chunks if c.node_id == source), None)
                    target_chunk = next((c for c in chunks if c.node_id == target), None)
                    if source_chunk and target_chunk:
                        source_chunk.references.append(target_chunk)

                # Use matplotlib-based visualization instead of plotly
                try:
                    # Generate visualization in the samples directory
                    visualizer.visualize_hierarchy_matplotlib(
                        chunks=chunks,
                        output_file=output_file,
                        show=False,
                        figsize=(16, 12)
                    )
                    logger.info(f"Saved visualization to {output_file}")

                    # Also save to project-specific directory
                    import io
                    from PIL import Image

                    # Read the generated image
                    img = Image.open(output_file)
                    img_bytes = io.BytesIO()
                    img.save(img_bytes, format=args.graph_format.upper())
                    img_bytes.seek(0)

                    # Save to project-specific directory
                    project_vis_path = storage_manager.save_project_visualization(
                        project_id=project_id,
                        file_name=project_vis_file,
                        content=img_bytes.read()
                    )
                    logger.info(f"Saved project-specific visualization to {project_vis_path}")

                except Exception as e:
                    logger.error(f"Error generating visualization: {e}")
            else:
                logger.info("Skipping visualization due to missing matplotlib dependency")
    finally:
        # Close storage connection
        storage_manager.close()

    elapsed_time = time.time() - start_time
    logger.info(f"Analysis completed in {elapsed_time:.2f} seconds")
    return True


def main():
    """Main entry point."""
    args = parse_args()
    success = analyze_java_files(args)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
