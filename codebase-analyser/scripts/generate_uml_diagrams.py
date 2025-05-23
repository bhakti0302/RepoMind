#!/usr/bin/env python3
"""
Generate UML-Style Diagrams

This script generates UML-style diagrams for a project, including:
1. Customer Java Highlight - Shows the Customer class with its relationships
2. Project Graph with Customer Highlight - Shows the entire project with Customer highlighted

These diagrams use a hierarchical layout similar to UML class diagrams.
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

def generate_uml_diagrams(project_id, output_dir, db_path=".lancedb"):
    """Generate UML-style diagrams for a project."""
    logger.info(f"Generating UML-style diagrams for project: {project_id}")

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

        # Generate Customer Java Highlight diagram
        customer_highlight_path = os.path.join(output_dir, "customer_java_highlight.png")
        generate_customer_highlight(G, customer_highlight_path)

        # Generate Project Graph with Customer Highlight diagram
        project_graph_path = os.path.join(output_dir, "project_graph_customer_highlight.png")
        generate_project_graph(G, project_graph_path)

        logger.info(f"UML-style diagrams generated successfully")
        return True

    finally:
        # Close the database connection
        storage.close()

def generate_customer_highlight(G, output_path):
    """Generate a UML-style diagram highlighting the Customer class."""
    logger.info("Generating Customer Java Highlight diagram")

    # Create a subgraph with Customer and its direct relationships
    customer_nodes = []

    # Find Customer node
    for node, attrs in G.nodes(data=True):
        if attrs.get('name') == 'Customer':
            customer_nodes.append(node)

    if not customer_nodes:
        logger.warning("No Customer node found in the graph")
        return

    # Create a subgraph with Customer and its neighbors
    subgraph_nodes = set()
    for customer_node in customer_nodes:
        subgraph_nodes.add(customer_node)
        # Add predecessors (parents)
        subgraph_nodes.update(G.predecessors(customer_node))
        # Add successors (children)
        subgraph_nodes.update(G.successors(customer_node))

    # Create the subgraph
    subgraph = G.subgraph(subgraph_nodes)

    # Create the figure
    plt.figure(figsize=(12, 8))

    # Use a hierarchical layout
    pos = nx.nx_agraph.graphviz_layout(subgraph, prog='dot')

    # Draw nodes
    node_colors = []
    for node in subgraph.nodes():
        if node in customer_nodes:
            node_colors.append('lightblue')  # Highlight Customer nodes
        else:
            node_colors.append('lightgray')

    nx.draw_networkx_nodes(subgraph, pos, node_color=node_colors, node_size=3000, alpha=0.8)

    # Draw edges with different styles based on relationship type
    edge_colors = []
    edge_styles = []

    for u, v, data in subgraph.edges(data=True):
        if data.get('type') == 'EXTENDS':
            edge_colors.append('blue')
            edge_styles.append('solid')
        elif data.get('type') == 'IMPLEMENTS':
            edge_colors.append('green')
            edge_styles.append('dashed')
        elif data.get('type') == 'USES':
            edge_colors.append('red')
            edge_styles.append('solid')
        else:
            edge_colors.append('black')
            edge_styles.append('dotted')

    # Draw edges
    for i, (u, v, data) in enumerate(subgraph.edges(data=True)):
        nx.draw_networkx_edges(
            subgraph, pos,
            edgelist=[(u, v)],
            width=2,
            alpha=0.7,
            edge_color=edge_colors[i],
            style=edge_styles[i],
            arrowsize=20
        )

    # Draw labels with class/interface name and type
    labels = {}
    for node, attrs in subgraph.nodes(data=True):
        node_type = attrs.get('type', 'unknown').replace('_declaration', '')
        node_name = attrs.get('name', node)
        labels[node] = f"{node_type.capitalize()}: {node_name}"

    nx.draw_networkx_labels(subgraph, pos, labels=labels, font_size=12, font_weight='bold')

    # Add a legend
    legend_elements = [
        mpatches.Patch(color='lightblue', label='Customer'),
        mpatches.Patch(color='lightgray', label='Related Class/Interface'),
        plt.Line2D([0], [0], color='blue', lw=2, label='Extends'),
        plt.Line2D([0], [0], color='green', linestyle='dashed', lw=2, label='Implements'),
        plt.Line2D([0], [0], color='red', lw=2, label='Uses')
    ]

    plt.legend(handles=legend_elements, loc='upper right')

    # Set title
    plt.title('Customer Class Relationships (UML-Style)', fontsize=16)

    # Remove axes
    plt.axis('off')

    # Save the figure
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    logger.info(f"Customer Java Highlight diagram saved to {output_path}")

def generate_project_graph(G, output_path):
    """Generate a UML-style diagram of the entire project with Customer highlighted."""
    logger.info("Generating Project Graph with Customer Highlight diagram")

    # Find Customer nodes
    customer_nodes = []
    for node, attrs in G.nodes(data=True):
        if attrs.get('name') == 'Customer':
            customer_nodes.append(node)

    # Create the figure
    plt.figure(figsize=(16, 12))

    # Use a hierarchical layout
    try:
        pos = nx.nx_agraph.graphviz_layout(G, prog='dot')
    except:
        # Fall back to spring layout if graphviz fails
        pos = nx.spring_layout(G, k=0.3, iterations=50, seed=42)

    # Draw nodes
    node_colors = []
    node_sizes = []
    for node in G.nodes():
        if node in customer_nodes:
            node_colors.append('lightblue')  # Highlight Customer nodes
            node_sizes.append(3000)
        else:
            node_colors.append('lightgray')
            node_sizes.append(2000)

    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes, alpha=0.8)

    # Draw edges with different styles based on relationship type
    for u, v, data in G.edges(data=True):
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
            G, pos,
            edgelist=[(u, v)],
            width=1.5,
            alpha=0.6,
            edge_color=edge_color,
            style=edge_style,
            arrowsize=15
        )

    # Draw labels with class/interface name
    labels = {}
    for node, attrs in G.nodes(data=True):
        if node in customer_nodes:
            # Highlight Customer nodes with more details
            node_type = attrs.get('type', 'unknown').replace('_declaration', '')
            node_name = attrs.get('name', node)
            labels[node] = f"{node_type.capitalize()}: {node_name}"
        else:
            # Just show name for other nodes
            labels[node] = attrs.get('name', node)

    nx.draw_networkx_labels(G, pos, labels=labels, font_size=10)

    # Add a legend
    legend_elements = [
        mpatches.Patch(color='lightblue', label='Customer'),
        mpatches.Patch(color='lightgray', label='Other Class/Interface'),
        plt.Line2D([0], [0], color='blue', lw=2, label='Extends'),
        plt.Line2D([0], [0], color='green', linestyle='dashed', lw=2, label='Implements'),
        plt.Line2D([0], [0], color='red', lw=2, label='Uses')
    ]

    plt.legend(handles=legend_elements, loc='upper right')

    # Set title
    plt.title('Project Class Diagram with Customer Highlight (UML-Style)', fontsize=16)

    # Remove axes
    plt.axis('off')

    # Save the figure
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    logger.info(f"Project Graph with Customer Highlight diagram saved to {output_path}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate UML-style diagrams")
    parser.add_argument("--project-id", required=True, help="Project ID")
    parser.add_argument("--output-dir", required=True, help="Output directory for diagrams")
    parser.add_argument("--db-path", default=".lancedb", help="Path to the LanceDB database")

    args = parser.parse_args()

    success = generate_uml_diagrams(args.project_id, args.output_dir, args.db_path)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
