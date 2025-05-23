#!/usr/bin/env python3
"""
Visualize code relationships from the database.

This script reads the code chunks from the database and visualizes the relationships.
"""

import os
import sys
import json
import logging
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path
import math

from codebase_analyser.database.unified_storage import UnifiedStorage

def hierarchical_layout(G, root=None, width=1.0, height=1.0, iterations=50):
    """Create a hierarchical layout for a directed graph.

    Args:
        G: NetworkX graph
        root: Root node (if None, will be determined automatically)
        width: Width of the layout
        height: Height of the layout
        iterations: Number of iterations for the layout algorithm

    Returns:
        Dictionary mapping nodes to positions
    """
    # If the graph is empty, return an empty layout
    if len(G) == 0:
        return {}

    # Convert to directed graph if it's not already
    if not isinstance(G, nx.DiGraph):
        G = nx.DiGraph(G)

    # Find root nodes (nodes with no incoming edges or with only self-loops)
    if root is None:
        roots = [n for n in G.nodes() if G.in_degree(n) == 0 or
                 (G.in_degree(n) == 1 and n in G.predecessors(n))]

        # If no root nodes found, use nodes with the lowest in-degree
        if not roots:
            min_in_degree = min(G.in_degree(n) for n in G.nodes())
            roots = [n for n in G.nodes() if G.in_degree(n) == min_in_degree]

        # If still no roots, just use the first node
        if not roots:
            roots = [list(G.nodes())[0]]
    else:
        roots = [root]

    # Create a tree from the graph
    tree = nx.bfs_tree(G.to_undirected(), roots[0])

    # Get the depth of each node
    depths = nx.single_source_shortest_path_length(tree, roots[0])

    # Group nodes by depth
    nodes_by_depth = {}
    for node, depth in depths.items():
        if depth not in nodes_by_depth:
            nodes_by_depth[depth] = []
        nodes_by_depth[depth].append(node)

    # Calculate positions
    max_depth = max(depths.values())
    pos = {}

    for depth, nodes in nodes_by_depth.items():
        # Calculate y-coordinate based on depth
        y = height * (1 - depth / (max_depth + 1))

        # Calculate x-coordinates to spread nodes evenly
        n_nodes = len(nodes)
        for i, node in enumerate(nodes):
            if n_nodes == 1:
                x = width / 2
            else:
                x = width * i / (n_nodes - 1) if n_nodes > 1 else width / 2
            pos[node] = (x, y)

    # Add any remaining nodes not reached by BFS
    remaining_nodes = set(G.nodes()) - set(pos.keys())
    if remaining_nodes:
        # Place them at the bottom
        y = 0
        n_nodes = len(remaining_nodes)
        for i, node in enumerate(remaining_nodes):
            x = width * i / (n_nodes - 1) if n_nodes > 1 else width / 2
            pos[node] = (x, y)

    # Refine the layout with iterations of spring layout
    if iterations > 0:
        # Use the calculated positions as initial positions for spring layout
        pos = nx.spring_layout(G, pos=pos, fixed=roots, iterations=iterations, k=0.2)

    return pos

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Define colors for different relationship types
RELATIONSHIP_COLORS = {
    "IMPORTS": "#4CAF50",     # Green
    "EXTENDS": "#F44336",     # Red
    "IMPLEMENTS": "#9C27B0",  # Purple
    "CALLS": "#FF9800",       # Orange
    "USES": "#2196F3",        # Blue
    "CONTAINS": "#607D8B",    # Gray
    "HAS_FIELD": "#00BCD4",   # Cyan
    "DEFAULT": "#9E9E9E"      # Light Gray
}

# Define node colors based on type
NODE_COLORS = {
    "class_declaration": "#FFC107",      # Amber
    "interface_declaration": "#3F51B5",  # Indigo
    "method_declaration": "#8BC34A",     # Light Green
    "field_declaration": "#00BCD4",      # Cyan
    "import_declaration": "#9E9E9E",     # Gray
    "file": "#795548",                   # Brown
    "DEFAULT": "#9E9E9E"                 # Light Gray
}

def visualize_graph(G, output_file, title):
    """Visualize the graph with better relationship highlighting."""
    logger.info(f"Visualizing graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")

    # Create figure
    plt.figure(figsize=(16, 12))
    plt.title(title, fontsize=16)

    # Use a hierarchical layout for better visualization
    try:
        # Try to use graphviz for a hierarchical layout
        try:
            import pygraphviz
            pos = nx.nx_agraph.graphviz_layout(G, prog='dot')
        except ImportError:
            # If pygraphviz is not available, try using pydot
            try:
                import pydot
                pos = nx.nx_pydot.graphviz_layout(G, prog='dot')
            except ImportError:
                # If both fail, use a custom hierarchical layout
                pos = hierarchical_layout(G)
    except Exception as e:
        logger.warning(f"Failed to use hierarchical layout: {e}")
        # Fall back to spring layout if hierarchical layout fails
        pos = nx.spring_layout(G, k=0.3, iterations=50, seed=42)

    # Draw nodes with different colors based on type
    node_colors = [NODE_COLORS.get(G.nodes[n].get('type', 'DEFAULT'), NODE_COLORS['DEFAULT']) for n in G.nodes]
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, alpha=0.8, node_size=700)

    # Draw edges with different colors based on type
    edge_types = set(nx.get_edge_attributes(G, 'type').values())

    for edge_type in edge_types:
        edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('type') == edge_type]
        if edges:
            edge_color = RELATIONSHIP_COLORS.get(edge_type, RELATIONSHIP_COLORS['DEFAULT'])
            edge_width = 2.0 if edge_type in ['EXTENDS', 'IMPLEMENTS', 'IMPORTS'] else 1.5
            edge_style = '-' if edge_type != 'IMPLEMENTS' else '--'

            nx.draw_networkx_edges(
                G, pos,
                edgelist=edges,
                edge_color=edge_color,
                width=edge_width,
                alpha=0.7,
                arrows=True,
                arrowstyle='-|>',
                connectionstyle='arc3,rad=0.1',
                style=edge_style
            )

    # Draw labels with better formatting
    labels = {}
    for node in G.nodes:
        node_type = G.nodes[node].get('type', '')
        node_name = G.nodes[node].get('name', node)

        # Format label based on node type
        if node_type == 'class_declaration':
            labels[node] = f"Class: {node_name}"
        elif node_type == 'interface_declaration':
            labels[node] = f"Interface: {node_name}"
        elif node_type == 'method_declaration':
            labels[node] = f"Method: {node_name}"
        elif node_type == 'field_declaration':
            labels[node] = f"Field: {node_name}"
        elif node_type == 'file':
            labels[node] = f"File: {node_name}"
        else:
            labels[node] = node_name

    nx.draw_networkx_labels(G, pos, labels=labels, font_size=10, font_weight='bold')

    # Add legend for relationship types
    legend_elements = []
    import matplotlib.patches as mpatches
    import matplotlib.lines as mlines

    # Node type legend
    for node_type, color in NODE_COLORS.items():
        if node_type != 'DEFAULT' and any(G.nodes[n].get('type') == node_type for n in G.nodes):
            legend_elements.append(
                mpatches.Patch(color=color, alpha=0.8, label=f"{node_type.replace('_declaration', '').capitalize()}")
            )

    # Edge type legend
    for edge_type, color in RELATIONSHIP_COLORS.items():
        if edge_type != 'DEFAULT' and edge_type in edge_types:
            style = '--' if edge_type == 'IMPLEMENTS' else '-'
            legend_elements.append(
                mlines.Line2D([0], [0], color=color, lw=2, label=edge_type.capitalize(), linestyle=style)
            )

    plt.legend(handles=legend_elements, loc='upper right', title="Legend")

    # Remove axis
    plt.axis('off')

    # Save the figure
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    logger.info(f"Saved visualization to {output_file}")

    # Return the path to the visualization
    return output_file

def main():
    """Main entry point for the script."""
    # Parse command-line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Visualize code relationships from the database")
    parser.add_argument("--project-id", default="testshreya", help="Project ID")
    default_output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'testshreya', 'visualizations')
    parser.add_argument("--output-dir", default=default_output_dir, help="Output directory")
    parser.add_argument("--db-path", default="./.lancedb", help="Path to the LanceDB database")
    parser.add_argument("--data-dir", default="../data", help="Path to the data directory")
    parser.add_argument("--timestamp", default=None, help="Timestamp to include in the filename")
    args = parser.parse_args()

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    # Connect to the database
    storage = UnifiedStorage(
        db_path=args.db_path,
        data_dir=args.data_dir,
        read_only=True
    )

    try:
        # Build the graph from the database
        graph = storage._build_graph_from_dependencies()

        # Get all chunks from the database
        table = storage.db_manager.get_code_chunks_table()
        chunks_df = table.to_pandas()
        project_chunks = chunks_df[chunks_df['project_id'] == args.project_id]

        # Get node IDs from the project chunks
        project_nodes = project_chunks['node_id'].tolist()

        # Add nodes that might be missing from the graph
        for _, chunk in project_chunks.iterrows():
            if chunk['node_id'] not in graph:
                graph.add_node(
                    chunk['node_id'],
                    type=chunk['chunk_type'],
                    name=chunk['name'],
                    qualified_name=chunk['qualified_name'],
                    project_id=chunk['project_id']
                )

        # Create a subgraph with only the project nodes
        project_graph = graph.subgraph(project_nodes)

        # Create filenames with timestamp if provided
        if args.timestamp:
            multi_file_filename = f"{args.project_id}_multi_file_relationships_{args.timestamp}.png"
            relationship_types_filename = f"{args.project_id}_relationship_types_{args.timestamp}.png"
        else:
            multi_file_filename = f"{args.project_id}_multi_file_relationships.png"
            relationship_types_filename = f"{args.project_id}_relationship_types.png"

        # Visualize the graph
        multi_file_path = visualize_graph(
            project_graph,
            os.path.join(args.output_dir, multi_file_filename),
            f"Multi-File Relationships - {args.project_id}"
        )

        # Create a relationship types graph
        relationship_types_graph = nx.DiGraph()

        # Add nodes and edges from the project graph
        for node, attrs in project_graph.nodes(data=True):
            # Skip file nodes
            if attrs.get('type') != 'file':
                relationship_types_graph.add_node(node, **attrs)

        # Add edges
        for u, v, attrs in project_graph.edges(data=True):
            # Skip edges involving file nodes
            if (project_graph.nodes[u].get('type') != 'file' and
                project_graph.nodes[v].get('type') != 'file'):
                relationship_types_graph.add_edge(u, v, **attrs)

        # Visualize the relationship types graph
        relationship_types_path = visualize_graph(
            relationship_types_graph,
            os.path.join(args.output_dir, relationship_types_filename),
            f"Different Types of Relationships - {args.project_id}"
        )

        logger.info("Visualization completed successfully")

        # Print the paths to the visualizations
        print(json.dumps({
            "multi_file_relationships": multi_file_path,
            "relationship_types": relationship_types_path
        }))

    finally:
        # Close the database connection
        storage.close()

if __name__ == "__main__":
    main()
