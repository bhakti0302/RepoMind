"""
Command-line interface for dependency graph operations.
"""

import os
import sys
import argparse
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

from ..database import open_db_connection, close_db_connection
from .dependency_graph_builder import DependencyGraphBuilder, build_and_store_dependency_graph
from .visualizer import visualize_dependency_graph, generate_dot_file, generate_json_file

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def build_graph_command(args):
    """Build a dependency graph from code chunks.

    Args:
        args: Command-line arguments
    """
    # Load the chunks from the input file
    logger.info(f"Loading chunks from {args.input_file}...")
    with open(args.input_file, 'r') as f:
        chunks = json.load(f)

    logger.info(f"Loaded {len(chunks)} chunks from {args.input_file}")

    # Build the dependency graph
    graph = build_and_store_dependency_graph(
        chunks=chunks,
        db_path=args.db_path,
        use_minimal_schema=not args.full_schema,
        store_in_db=args.store_in_db
    )

    logger.info(f"Built dependency graph with {len(graph['nodes'])} nodes and {len(graph['edges'])} edges")

    # Save the graph to a file if requested
    if args.output_file:
        # Create the output directory if it doesn't exist
        output_dir = os.path.dirname(args.output_file)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        with open(args.output_file, 'w') as f:
            json.dump(graph, f, indent=2)

        logger.info(f"Saved dependency graph to {args.output_file}")


def visualize_graph_command(args):
    """Visualize a dependency graph.

    Args:
        args: Command-line arguments
    """
    # Load the graph from the input file
    logger.info(f"Loading graph from {args.input_file}...")
    with open(args.input_file, 'r') as f:
        graph = json.load(f)

    logger.info(f"Loaded dependency graph with {len(graph['nodes'])} nodes and {len(graph['edges'])} edges")

    # Visualize the graph
    if args.format == "png":
        visualize_dependency_graph(
            dependency_graph=graph,
            output_file=args.output_file,
            title=args.title,
            layout=args.layout,
            node_size=args.node_size,
            font_size=args.font_size
        )
    elif args.format == "dot":
        generate_dot_file(
            dependency_graph=graph,
            output_file=args.output_file,
            title=args.title
        )
    elif args.format == "json":
        generate_json_file(
            dependency_graph=graph,
            output_file=args.output_file,
            pretty=True
        )
    else:
        logger.error(f"Unsupported format: {args.format}")


def query_dependencies_command(args):
    """Query dependencies from the database.

    Args:
        args: Command-line arguments
    """
    # Open a database connection
    db_manager = open_db_connection(
        db_path=args.db_path,
        use_minimal_schema=not args.full_schema
    )

    try:
        # Query dependencies
        if args.source_id and args.target_id:
            # Query dependencies between source and target
            dependencies = db_manager.get_dependencies(
                source_id=args.source_id,
                target_id=args.target_id,
                dep_type=args.type
            )
            logger.info(f"Found {len(dependencies)} dependencies between {args.source_id} and {args.target_id}")
        elif args.source_id:
            # Query outgoing dependencies
            dependencies = db_manager.get_dependencies(
                source_id=args.source_id,
                dep_type=args.type
            )
            logger.info(f"Found {len(dependencies)} outgoing dependencies from {args.source_id}")
        elif args.target_id:
            # Query incoming dependencies
            dependencies = db_manager.get_dependencies(
                target_id=args.target_id,
                dep_type=args.type
            )
            logger.info(f"Found {len(dependencies)} incoming dependencies to {args.target_id}")
        else:
            # Query all dependencies
            dependencies = db_manager.get_dependencies(
                dep_type=args.type
            )
            logger.info(f"Found {len(dependencies)} dependencies")

        # Print the dependencies
        for i, dep in enumerate(dependencies):
            print(f"\nDependency {i+1}:")
            print(f"  Source: {dep['source_id']}")
            print(f"  Target: {dep['target_id']}")
            print(f"  Type: {dep['type']}")
            print(f"  Strength: {dep['strength']}")
            print(f"  Direct: {dep['is_direct']}")
            print(f"  Required: {dep['is_required']}")
            print(f"  Description: {dep['description']}")

        # Save the dependencies to a file if requested
        if args.output_file:
            # Create the output directory if it doesn't exist
            output_dir = os.path.dirname(args.output_file)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)

            with open(args.output_file, 'w') as f:
                json.dump(dependencies, f, indent=2)

            logger.info(f"Saved {len(dependencies)} dependencies to {args.output_file}")

    finally:
        # Close the database connection
        close_db_connection(db_manager)


def main():
    """Command-line interface for dependency graph operations."""
    parser = argparse.ArgumentParser(description="Dependency graph operations")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Build graph command
    build_parser = subparsers.add_parser("build", help="Build a dependency graph from code chunks")
    build_parser.add_argument("input_file", help="Path to the JSON file containing code chunks")
    build_parser.add_argument("--output-file", help="Path to save the dependency graph")
    build_parser.add_argument("--db-path", help="Path to the LanceDB database")
    build_parser.add_argument("--full-schema", action="store_true", help="Use the full schema")
    build_parser.add_argument("--store-in-db", action="store_true", help="Store dependencies in the database")

    # Visualize graph command
    visualize_parser = subparsers.add_parser("visualize", help="Visualize a dependency graph")
    visualize_parser.add_argument("input_file", help="Path to the JSON file containing the dependency graph")
    visualize_parser.add_argument("--output-file", help="Path to save the visualization")
    visualize_parser.add_argument("--format", choices=["png", "dot", "json"], default="png", help="Output format")
    visualize_parser.add_argument("--title", default="Dependency Graph", help="Title of the visualization")
    visualize_parser.add_argument("--layout", choices=["spring", "circular", "shell", "spectral", "random"], default="spring", help="Layout algorithm")
    visualize_parser.add_argument("--node-size", type=int, default=1000, help="Size of the nodes")
    visualize_parser.add_argument("--font-size", type=int, default=8, help="Size of the node labels")

    # Query dependencies command
    query_parser = subparsers.add_parser("query", help="Query dependencies from the database")
    query_parser.add_argument("--source-id", help="Source node ID to filter by")
    query_parser.add_argument("--target-id", help="Target node ID to filter by")
    query_parser.add_argument("--type", help="Dependency type to filter by")
    query_parser.add_argument("--output-file", help="Path to save the query results")
    query_parser.add_argument("--db-path", help="Path to the LanceDB database")
    query_parser.add_argument("--full-schema", action="store_true", help="Use the full schema")

    args = parser.parse_args()

    if args.command == "build":
        build_graph_command(args)
    elif args.command == "visualize":
        visualize_graph_command(args)
    elif args.command == "query":
        query_dependencies_command(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
