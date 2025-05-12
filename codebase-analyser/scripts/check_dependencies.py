#!/usr/bin/env python3
"""
Check dependencies in the LanceDB database.
"""

import lancedb
import json
import networkx as nx
from codebase_analyser.database.unified_storage import UnifiedStorage

def main():
    """Main entry point."""
    # Connect to the database
    print("Connecting to the database...")
    storage = UnifiedStorage(
        db_path="./.lancedb",
        data_dir="../data",
        read_only=True
    )

    try:
        # Build the graph from the dependencies
        print("Building graph from dependencies...")
        graph = storage._build_graph_from_dependencies()

        # Print graph statistics
        print(f"Graph has {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges")

        # Count edge types
        edge_types = {}
        for _, _, attrs in graph.edges(data=True):
            edge_type = attrs.get('type', 'UNKNOWN')
            if edge_type not in edge_types:
                edge_types[edge_type] = 0
            edge_types[edge_type] += 1

        print("Edge types:")
        for edge_type, count in edge_types.items():
            print(f"  - {edge_type}: {count}")

        # Count node types
        node_types = {}
        for _, attrs in graph.nodes(data=True):
            node_type = attrs.get('type', 'UNKNOWN')
            if node_type not in node_types:
                node_types[node_type] = 0
            node_types[node_type] += 1

        print("Node types:")
        for node_type, count in node_types.items():
            print(f"  - {node_type}: {count}")

        # Check for project-specific nodes
        project_nodes = {}
        for node, attrs in graph.nodes(data=True):
            if 'project_id' in attrs:
                project_id = attrs['project_id']
                if project_id not in project_nodes:
                    project_nodes[project_id] = 0
                project_nodes[project_id] += 1

        print("Project-specific nodes:")
        for project_id, count in project_nodes.items():
            print(f"  - {project_id}: {count}")

        # Check for testshreya-specific nodes
        testshreya_nodes = [node for node, attrs in graph.nodes(data=True)
                           if attrs.get('project_id') == 'testshreya']

        print(f"Found {len(testshreya_nodes)} nodes for project 'testshreya'")

        # Check for testshreya-specific edges
        testshreya_edges = []
        for u, v, attrs in graph.edges(data=True):
            if u in testshreya_nodes and v in testshreya_nodes:
                testshreya_edges.append((u, v, attrs))

        print(f"Found {len(testshreya_edges)} edges for project 'testshreya'")

        # Count testshreya edge types
        testshreya_edge_types = {}
        for _, _, attrs in testshreya_edges:
            edge_type = attrs.get('type', 'UNKNOWN')
            if edge_type not in testshreya_edge_types:
                testshreya_edge_types[edge_type] = 0
            testshreya_edge_types[edge_type] += 1

        print("Testshreya edge types:")
        for edge_type, count in testshreya_edge_types.items():
            print(f"  - {edge_type}: {count}")

        # Check for inheritance relationships
        inheritance_edges = [edge for edge in testshreya_edges
                            if edge[2].get('type') in ['EXTENDS', 'IMPLEMENTS']]

        print(f"Found {len(inheritance_edges)} inheritance relationships for project 'testshreya'")
        for u, v, attrs in inheritance_edges:
            u_attrs = graph.nodes[u]
            v_attrs = graph.nodes[v]
            print(f"  - {u_attrs.get('name', u)} {attrs.get('type')} {v_attrs.get('name', v)}")

        # Check for field type relationships
        field_type_edges = [edge for edge in testshreya_edges
                           if edge[2].get('type') in ['USES', 'HAS_FIELD']]

        print(f"Found {len(field_type_edges)} field type relationships for project 'testshreya'")
        for u, v, attrs in field_type_edges[:5]:  # Show only the first 5
            u_attrs = graph.nodes[u]
            v_attrs = graph.nodes[v]
            print(f"  - {u_attrs.get('name', u)} {attrs.get('type')} {v_attrs.get('name', v)}")

        # Check for method call relationships
        method_call_edges = [edge for edge in testshreya_edges
                            if edge[2].get('type') in ['CALLS']]

        print(f"Found {len(method_call_edges)} method call relationships for project 'testshreya'")
        for u, v, attrs in method_call_edges[:5]:  # Show only the first 5
            u_attrs = graph.nodes[u]
            v_attrs = graph.nodes[v]
            print(f"  - {u_attrs.get('name', u)} {attrs.get('type')} {v_attrs.get('name', v)}")

    finally:
        # Close the database connection
        storage.close()

if __name__ == "__main__":
    main()
