#!/usr/bin/env python3
"""
Enhanced Graph Visualization Script

This script enhances the visualization of code relationships, focusing on:
1. Import relationships
2. Inheritance relationships
3. Field type relationships

Usage:
    python enhance_graph_visualization.py --input-file <path_to_dependency_graph.json> --output-file <path_to_output.png>
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba

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
    "FIELD_TYPE": "#00BCD4",  # Cyan
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

def load_dependency_graph(file_path: str) -> Dict[str, Any]:
    """Load a dependency graph from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Dependency graph as a dictionary
    """
    logger.info(f"Loading dependency graph from {file_path}")
    
    try:
        with open(file_path, 'r') as f:
            graph_data = json.load(f)
            
        logger.info(f"Loaded dependency graph with {len(graph_data.get('nodes', []))} nodes and {len(graph_data.get('edges', []))} edges")
        return graph_data
    except Exception as e:
        logger.error(f"Failed to load dependency graph: {e}")
        raise

def create_networkx_graph(dependency_graph: Dict[str, Any]) -> nx.DiGraph:
    """Create a NetworkX graph from a dependency graph.
    
    Args:
        dependency_graph: Dependency graph as a dictionary
        
    Returns:
        NetworkX directed graph
    """
    G = nx.DiGraph()
    
    # Add nodes
    for node in dependency_graph.get('nodes', []):
        node_id = node.get('id', '')
        node_type = node.get('type', 'DEFAULT')
        node_name = node.get('name', node_id)
        
        G.add_node(
            node_id,
            type=node_type,
            name=node_name,
            qualified_name=node.get('qualified_name', node_name),
            color=NODE_COLORS.get(node_type, NODE_COLORS['DEFAULT'])
        )
    
    # Add edges
    for edge in dependency_graph.get('edges', []):
        source_id = edge.get('source_id', '')
        target_id = edge.get('target_id', '')
        edge_type = edge.get('type', 'DEFAULT')
        
        # Skip if source or target doesn't exist
        if source_id not in G.nodes or target_id not in G.nodes:
            continue
        
        G.add_edge(
            source_id,
            target_id,
            type=edge_type,
            strength=edge.get('strength', 0.5),
            is_direct=edge.get('is_direct', True),
            is_required=edge.get('is_required', False),
            description=edge.get('description', ''),
            color=RELATIONSHIP_COLORS.get(edge_type, RELATIONSHIP_COLORS['DEFAULT'])
        )
    
    return G

def visualize_enhanced_graph(
    G: nx.DiGraph,
    output_file: str,
    title: str = "Enhanced Code Relationships",
    figsize: Tuple[int, int] = (16, 12),
    show: bool = False
) -> None:
    """Visualize the enhanced graph with better relationship highlighting.
    
    Args:
        G: NetworkX directed graph
        output_file: Path to save the visualization
        title: Title of the visualization
        figsize: Figure size (width, height) in inches
        show: Whether to show the visualization
    """
    logger.info(f"Visualizing enhanced graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    
    # Create figure
    plt.figure(figsize=figsize)
    plt.title(title, fontsize=16)
    
    # Use a more sophisticated layout
    try:
        pos = nx.kamada_kawai_layout(G)
    except:
        # Fall back to spring layout if kamada_kawai fails
        pos = nx.spring_layout(G, k=0.3, iterations=50, seed=42)
    
    # Draw nodes with different colors based on type
    node_colors = [G.nodes[n].get('color', NODE_COLORS['DEFAULT']) for n in G.nodes]
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
        else:
            labels[node] = node_name
    
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=10, font_weight='bold')
    
    # Add legend for relationship types
    legend_elements = []
    import matplotlib.patches as mpatches
    import matplotlib.lines as mlines
    
    # Node type legend
    for node_type, color in NODE_COLORS.items():
        if node_type != 'DEFAULT':
            legend_elements.append(
                mpatches.Patch(color=color, alpha=0.8, label=f"{node_type.replace('_declaration', '').capitalize()}")
            )
    
    # Edge type legend
    for edge_type, color in RELATIONSHIP_COLORS.items():
        if edge_type != 'DEFAULT':
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
    
    # Show if requested
    if show:
        plt.show()
    else:
        plt.close()

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Enhanced Graph Visualization")
    parser.add_argument("--input-file", required=True, help="Path to the dependency graph JSON file")
    parser.add_argument("--output-file", required=True, help="Path to save the visualization")
    parser.add_argument("--title", default="Enhanced Code Relationships", help="Title of the visualization")
    parser.add_argument("--show", action="store_true", help="Show the visualization")
    
    args = parser.parse_args()
    
    # Load the dependency graph
    dependency_graph = load_dependency_graph(args.input_file)
    
    # Create a NetworkX graph
    G = create_networkx_graph(dependency_graph)
    
    # Visualize the enhanced graph
    visualize_enhanced_graph(
        G,
        args.output_file,
        title=args.title,
        show=args.show
    )
    
    logger.info("Enhanced graph visualization completed successfully")

if __name__ == "__main__":
    main()
