"""
Dependency graph visualization module.

This module provides functionality to visualize dependency graphs in various formats.
"""

import os
import logging
import json
from typing import Dict, List, Set, Optional, Any, Tuple
from pathlib import Path
import networkx as nx

# Try to import matplotlib, but don't fail if it's not available
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_networkx_graph(dependency_graph: Dict[str, Any]) -> nx.DiGraph:
    """Create a NetworkX graph from a dependency graph.

    Args:
        dependency_graph: Dependency graph as a dictionary

    Returns:
        NetworkX directed graph
    """
    G = nx.DiGraph()

    # Add nodes
    for node in dependency_graph['nodes']:
        G.add_node(
            node['id'],
            type=node['type'],
            name=node['name'],
            qualified_name=node.get('qualified_name', node['name'])
        )

    # Add edges
    for edge in dependency_graph['edges']:
        G.add_edge(
            edge['source_id'],
            edge['target_id'],
            type=edge['type'],
            strength=edge['strength'],
            is_direct=edge['is_direct'],
            is_required=edge['is_required'],
            description=edge['description']
        )

    return G


def visualize_dependency_graph(
    dependency_graph: Dict[str, Any],
    output_file: Optional[str] = None,
    title: str = "Dependency Graph",
    layout: str = "spring",
    node_size: int = 1000,
    node_color: str = "skyblue",
    edge_color: str = "gray",
    font_size: int = 8,
    with_labels: bool = True,
    figsize: Tuple[int, int] = (12, 8)
) -> None:
    """Visualize a dependency graph using NetworkX and Matplotlib.

    Args:
        dependency_graph: Dependency graph as a dictionary
        output_file: Path to save the visualization (optional)
        title: Title of the visualization
        layout: Layout algorithm to use (spring, circular, shell, spectral, random)
        node_size: Size of the nodes
        node_color: Color of the nodes
        edge_color: Color of the edges
        font_size: Size of the node labels
        with_labels: Whether to show node labels
        figsize: Figure size (width, height) in inches
    """
    if not MATPLOTLIB_AVAILABLE:
        logger.warning("Matplotlib is not available. Visualization will be skipped.")
        return

    logger.info(f"Visualizing dependency graph with {len(dependency_graph['nodes'])} nodes and {len(dependency_graph['edges'])} edges...")

    # Create a NetworkX graph
    G = create_networkx_graph(dependency_graph)

    # Create a figure
    plt.figure(figsize=figsize)
    plt.title(title)

    # Choose the layout
    if layout == "spring":
        pos = nx.spring_layout(G, seed=42)
    elif layout == "circular":
        pos = nx.circular_layout(G)
    elif layout == "shell":
        pos = nx.shell_layout(G)
    elif layout == "spectral":
        pos = nx.spectral_layout(G)
    elif layout == "random":
        pos = nx.random_layout(G)
    else:
        pos = nx.spring_layout(G, seed=42)

    # Draw the graph
    nx.draw(
        G,
        pos,
        with_labels=with_labels,
        node_size=node_size,
        node_color=node_color,
        edge_color=edge_color,
        font_size=font_size,
        arrows=True
    )

    # Save the figure if an output file is provided
    if output_file:
        # Create the output directory if it doesn't exist
        output_dir = os.path.dirname(output_file)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        plt.savefig(output_file, bbox_inches="tight")
        logger.info(f"Saved visualization to {output_file}")

    # Show the figure
    plt.show()


def generate_dot_file(
    dependency_graph: Dict[str, Any],
    output_file: Optional[str] = None,
    title: str = "Dependency Graph"
) -> str:
    """Generate a DOT file for the dependency graph.

    Args:
        dependency_graph: Dependency graph as a dictionary
        output_file: Path to save the DOT file (optional)
        title: Title of the graph

    Returns:
        DOT file content as a string
    """
    logger.info(f"Generating DOT file for dependency graph with {len(dependency_graph['nodes'])} nodes and {len(dependency_graph['edges'])} edges...")

    # Create a NetworkX graph
    G = create_networkx_graph(dependency_graph)

    # Generate DOT file content
    dot_content = f"digraph {title.replace(' ', '_')} {{\n"
    dot_content += f"  label=\"{title}\";\n"
    dot_content += "  node [shape=box, style=filled, fillcolor=skyblue];\n"

    # Add nodes
    for node_id, node_attrs in G.nodes(data=True):
        node_name = node_attrs.get('name', node_id)
        node_type = node_attrs.get('type', 'unknown')
        dot_content += f"  \"{node_id}\" [label=\"{node_name}\\n({node_type})\"];\n"

    # Add edges
    for source, target, edge_attrs in G.edges(data=True):
        edge_type = edge_attrs.get('type', 'unknown')
        edge_strength = edge_attrs.get('strength', 0.0)
        edge_color = "black"
        edge_style = "solid"

        # Customize edge appearance based on type and strength
        if edge_type == "CONTAINS":
            edge_color = "blue"
            edge_style = "solid"
        elif edge_type == "IMPORTS":
            edge_color = "green"
            edge_style = "dashed"
        elif edge_type == "EXTENDS":
            edge_color = "red"
            edge_style = "bold"
        elif edge_type == "IMPLEMENTS":
            edge_color = "purple"
            edge_style = "dotted"
        elif edge_type == "CALLS":
            edge_color = "orange"
            edge_style = "solid"

        dot_content += f"  \"{source}\" -> \"{target}\" [label=\"{edge_type}\", color={edge_color}, style={edge_style}, penwidth={1 + edge_strength * 2}];\n"

    dot_content += "}\n"

    # Save the DOT file if an output file is provided
    if output_file:
        # Create the output directory if it doesn't exist
        output_dir = os.path.dirname(output_file)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        with open(output_file, 'w') as f:
            f.write(dot_content)

        logger.info(f"Saved DOT file to {output_file}")

    return dot_content


def generate_json_file(
    dependency_graph: Dict[str, Any],
    output_file: Optional[str] = None,
    pretty: bool = True
) -> str:
    """Generate a JSON file for the dependency graph.

    Args:
        dependency_graph: Dependency graph as a dictionary
        output_file: Path to save the JSON file (optional)
        pretty: Whether to format the JSON with indentation

    Returns:
        JSON content as a string
    """
    logger.info(f"Generating JSON file for dependency graph with {len(dependency_graph['nodes'])} nodes and {len(dependency_graph['edges'])} edges...")

    # Generate JSON content
    if pretty:
        json_content = json.dumps(dependency_graph, indent=2)
    else:
        json_content = json.dumps(dependency_graph)

    # Save the JSON file if an output file is provided
    if output_file:
        # Create the output directory if it doesn't exist
        output_dir = os.path.dirname(output_file)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        with open(output_file, 'w') as f:
            f.write(json_content)

        logger.info(f"Saved JSON file to {output_file}")

    return json_content
