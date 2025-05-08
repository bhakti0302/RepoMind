#!/usr/bin/env python3
"""
Test script for dependency graph construction and visualization.
"""

import os
import sys
import json
import argparse
from pathlib import Path

from codebase_analyser.graph import (
    build_and_store_dependency_graph,
    visualize_dependency_graph,
    generate_dot_file,
    generate_json_file
)
from codebase_analyser.database import open_db_connection, close_db_connection


def test_dependency_graph_construction(
    input_file,
    output_dir="samples",
    db_path=None,
    use_minimal_schema=True,
    visualize=True,
    store_in_db=False
):
    """Test dependency graph construction and visualization.

    Args:
        input_file: Path to the JSON file containing code chunks
        output_dir: Directory to save output files
        db_path: Path to the LanceDB database
        use_minimal_schema: Whether to use the minimal schema
        visualize: Whether to generate visualizations
        store_in_db: Whether to store dependencies in the database
    """
    print(f"Testing dependency graph construction with chunks from {input_file}...")

    # Load the chunks from the input file
    with open(input_file, 'r') as f:
        chunks = json.load(f)

    print(f"Loaded {len(chunks)} chunks from {input_file}")

    # Build the dependency graph
    graph = build_and_store_dependency_graph(
        chunks=chunks,
        db_path=db_path,
        use_minimal_schema=use_minimal_schema,
        store_in_db=store_in_db
    )

    print(f"Built dependency graph with {len(graph['nodes'])} nodes and {len(graph['edges'])} edges")

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Save the graph to a JSON file
    json_output = os.path.join(output_dir, "dependency_graph.json")
    with open(json_output, 'w') as f:
        json.dump(graph, f, indent=2)

    print(f"Saved dependency graph to {json_output}")

    # Generate visualizations if requested
    if visualize:
        # Generate a PNG visualization
        png_output = os.path.join(output_dir, "dependency_graph.png")
        visualize_dependency_graph(
            dependency_graph=graph,
            output_file=png_output,
            title="Sample Dependency Graph",
            layout="spring",
            node_size=1000,
            font_size=8
        )

        print(f"Saved PNG visualization to {png_output}")

        # Generate a DOT file
        dot_output = os.path.join(output_dir, "dependency_graph.dot")
        generate_dot_file(
            dependency_graph=graph,
            output_file=dot_output,
            title="Sample Dependency Graph"
        )

        print(f"Saved DOT file to {dot_output}")

    # Query dependencies from the database
    if db_path:
        print("\nQuerying dependencies from the database...")

        # Open a database connection
        db_manager = open_db_connection(
            db_path=db_path,
            use_minimal_schema=use_minimal_schema
        )

        try:
            # Get all dependencies
            dependencies = db_manager.get_dependencies()

            print(f"Found {len(dependencies)} dependencies in the database")

            # Print a sample of dependencies
            for i, dep in enumerate(dependencies[:5]):
                print(f"\nDependency {i+1}:")
                print(f"  Source: {dep['source_id']}")
                print(f"  Target: {dep['target_id']}")
                print(f"  Type: {dep['type']}")
                print(f"  Strength: {dep['strength']}")
                print(f"  Description: {dep['description']}")

            if len(dependencies) > 5:
                print(f"\n... and {len(dependencies) - 5} more dependencies")

        finally:
            # Close the database connection
            close_db_connection(db_manager)

    print("\nDependency graph test completed successfully!")


def main():
    parser = argparse.ArgumentParser(description="Test dependency graph construction and visualization")
    parser.add_argument("--input", default="samples/sample_chunks.json", help="Path to the JSON file containing code chunks")
    parser.add_argument("--output-dir", default="samples", help="Directory to save output files")
    parser.add_argument("--db-path", help="Path to the LanceDB database")
    parser.add_argument("--full-schema", action="store_true", help="Use the full schema")
    parser.add_argument("--no-visualize", action="store_true", help="Skip visualization generation")
    parser.add_argument("--store-in-db", action="store_true", help="Store dependencies in the database")

    args = parser.parse_args()

    test_dependency_graph_construction(
        input_file=args.input,
        output_dir=args.output_dir,
        db_path=args.db_path,
        use_minimal_schema=not args.full_schema,
        visualize=not args.no_visualize,
        store_in_db=args.store_in_db
    )


if __name__ == "__main__":
    main()
