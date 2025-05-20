#!/usr/bin/env python3
"""
Generate Generic UML-Style Diagrams

This script generates generic UML-style diagrams for a project without any specific highlighting.
It creates a comprehensive class diagram showing all classes and their relationships.
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def generate_generic_diagrams(project_id, output_dir, db_path=".lancedb"):
    """Generate generic UML-style diagrams for a project."""
    logger.info(f"Generating generic UML-style diagrams for project: {project_id}")

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Connect to the database
    from codebase_analyser.database.unified_storage import UnifiedStorage
    storage = UnifiedStorage(
        db_path=db_path,
        create_if_not_exists=False,
        read_only=True
    )

    try:
        # Get dependency graph from the database
        dependency_graph = storage.get_dependency_graph(project_id)

        if not dependency_graph or not dependency_graph.nodes:
            logger.error(f"No dependency graph found for project: {project_id}")
            return False

        logger.info(f"Found dependency graph with {len(dependency_graph.nodes)} nodes and {len(dependency_graph.edges)} edges")

        # Convert to NetworkX graph for visualization
        G = nx.DiGraph()

        # Add nodes
        for node_id, node_attrs in dependency_graph.nodes.items():
            G.add_node(
                node_id,
                name=node_attrs.get('name', ''),
                type=node_attrs.get('type', 'unknown'),
                qualified_name=node_attrs.get('qualified_name', '')
            )

        # Add edges
        for u, v, edge_attrs in dependency_graph.edges(data=True):
            G.add_edge(
                u,
                v,
                type=edge_attrs.get('type', 'REFERENCES'),
                description=edge_attrs.get('description', '')
            )

        # Generate Generic Class Diagram
        class_diagram_path = os.path.join(output_dir, "generic_class_diagram.png")
        generate_class_diagram(G, class_diagram_path, project_id)

        logger.info(f"Generic UML-style diagrams generated successfully")
        return True

    finally:
        # Close the database connection
        storage.close()

def generate_class_diagram(G, output_path, project_id):
    """Generate a generic UML-style class diagram without any highlighting."""
    logger.info("Generating Generic Class Diagram")

    # Create a subgraph with only class and interface nodes
    class_nodes = []
    for node, attrs in G.nodes(data=True):
        if attrs.get('type') in ['class_declaration', 'interface_declaration']:
            class_nodes.append(node)

    if not class_nodes:
        logger.warning("No class or interface nodes found in the graph")
        return

    # Create the subgraph
    subgraph = G.subgraph(class_nodes)

    # Create the figure
    plt.figure(figsize=(16, 12))

    # Use a hierarchical layout
    try:
        pos = nx.nx_agraph.graphviz_layout(subgraph, prog='dot')
    except:
        # Fall back to spring layout if graphviz fails
        pos = nx.spring_layout(subgraph, k=0.3, iterations=50, seed=42)

    # Draw nodes with different colors based on type
    node_colors = []
    for node in subgraph.nodes():
        node_type = subgraph.nodes[node].get('type', '')
        if node_type == 'class_declaration':
            node_colors.append('#FFC107')  # Amber for classes
        elif node_type == 'interface_declaration':
            node_colors.append('#3F51B5')  # Indigo for interfaces
        else:
            node_colors.append('#9E9E9E')  # Gray for other nodes

    nx.draw_networkx_nodes(subgraph, pos, node_color=node_colors, node_size=2500, alpha=0.8)

    # Draw edges with different styles based on relationship type
    for u, v, data in subgraph.edges(data=True):
        edge_color = 'black'
        edge_style = 'solid'

        if data.get('type') == 'EXTENDS':
            edge_color = 'blue'
            edge_style = 'solid'
        elif data.get('type') == 'IMPLEMENTS':
            edge_color = 'green'
            edge_style = 'dashed'
        elif data.get('type') == 'USES':
            edge_color = 'red'
            edge_style = 'solid'

        nx.draw_networkx_edges(
            subgraph, pos,
            edgelist=[(u, v)],
            width=1.5,
            alpha=0.7,
            edge_color=edge_color,
            style=edge_style,
            arrowsize=15
        )

    # Draw labels with class/interface name and type
    labels = {}
    for node, attrs in subgraph.nodes(data=True):
        node_type = attrs.get('type', 'unknown').replace('_declaration', '')
        node_name = attrs.get('name', node)
        labels[node] = f"{node_type.capitalize()}: {node_name}"

    nx.draw_networkx_labels(subgraph, pos, labels=labels, font_size=10, font_weight='bold')

    # Add a legend
    legend_elements = [
        mpatches.Patch(color='#FFC107', label='Class'),
        mpatches.Patch(color='#3F51B5', label='Interface'),
        plt.Line2D([0], [0], color='blue', lw=2, label='Extends'),
        plt.Line2D([0], [0], color='green', linestyle='dashed', lw=2, label='Implements'),
        plt.Line2D([0], [0], color='red', lw=2, label='Uses')
    ]

    plt.legend(handles=legend_elements, loc='upper right')

    # Set title
    plt.title(f'Class Diagram - {project_id} (UML-Style)', fontsize=16)

    # Remove axes
    plt.axis('off')

    # Save the figure
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    logger.info(f"Generic Class Diagram saved to {output_path}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate generic UML-style diagrams")
    parser.add_argument("--project-id", required=True, help="Project ID")
    parser.add_argument("--output-dir", required=True, help="Output directory for diagrams")
    parser.add_argument("--db-path", default=".lancedb", help="Path to the LanceDB database")

    args = parser.parse_args()

    success = generate_generic_diagrams(args.project_id, args.output_dir, args.db_path)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
