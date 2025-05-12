#!/usr/bin/env python3
"""
Analyze relationships in the testshreya project.

This script analyzes the testshreya project and outputs detailed information about the relationships.
"""

import sys
import json
from pathlib import Path

# Add the parent directory to the path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from codebase_analyser import CodebaseAnalyser
from codebase_analyser.parsing.dependency_types import DependencyType

def main():
    """Main entry point for the script."""
    # Parse the repository
    print("Parsing repository...")
    repo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'testshreya')
    analyser = CodebaseAnalyser(repo_path=repo_path)
    chunks = analyser.parse()

    print(f"Found {len(chunks)} chunks in the repository")

    # Print information about the chunks
    class_chunks = [c for c in chunks if c.chunk_type == 'class_declaration']
    interface_chunks = [c for c in chunks if c.chunk_type == 'interface_declaration']
    method_chunks = [c for c in chunks if c.chunk_type == 'method_declaration']

    print(f"Found {len(class_chunks)} classes, {len(interface_chunks)} interfaces, {len(method_chunks)} methods")

    # Print information about the classes
    print("\nClasses:")
    for chunk in class_chunks:
        print(f"  - {chunk.name} ({chunk.node_id})")

        # Print parent class if available
        if 'extends' in chunk.context:
            print(f"    Extends: {chunk.context['extends']}")

        # Print implemented interfaces if available
        if 'implements' in chunk.context:
            print(f"    Implements: {', '.join(chunk.context['implements'])}")

        # Print fields if available
        if 'fields' in chunk.context:
            print(f"    Fields:")
            for field in chunk.context['fields']:
                print(f"      - {field.get('name', 'unknown')} ({field.get('type', 'unknown')})")

    # Print information about the interfaces
    print("\nInterfaces:")
    for chunk in interface_chunks:
        print(f"  - {chunk.name} ({chunk.node_id})")

    # Analyze dependencies
    print("\nAnalyzing dependencies...")
    from codebase_analyser.parsing.dependency_analyzer import DependencyAnalyzer

    dependency_analyzer = DependencyAnalyzer()
    dependency_graph = dependency_analyzer.analyze_dependencies(chunks)

    # Print information about the dependencies
    print("\nDependencies:")
    edges = dependency_graph.edges

    # Group edges by type
    edge_types = {}
    for edge in edges:
        edge_type = edge.type.name
        if edge_type not in edge_types:
            edge_types[edge_type] = []
        edge_types[edge_type].append(edge)

    # Print edges by type
    for edge_type, edges in edge_types.items():
        print(f"\n  {edge_type} ({len(edges)}):")
        for edge in edges:
            source_id = edge.source_id
            target_id = edge.target_id

            # Find the source and target chunks
            source_chunk = next((c for c in chunks if c.node_id == source_id), None)
            target_chunk = next((c for c in chunks if c.node_id == target_id), None)

            source_name = source_chunk.name if source_chunk else source_id
            target_name = target_chunk.name if target_chunk else target_id

            print(f"    - {source_name} -> {target_name} ({edge.description})")

    # Convert to dictionary and save
    graph_dict = dependency_graph.to_dict()
    with open('samples/testshreya_dependency_graph.json', 'w') as f:
        json.dump(graph_dict, f, indent=2)

    print(f"\nGenerated dependency graph with {len(graph_dict['nodes'])} nodes and {len(graph_dict['edges'])} edges")
    print(f"Saved to samples/testshreya_dependency_graph.json")

if __name__ == "__main__":
    main()
