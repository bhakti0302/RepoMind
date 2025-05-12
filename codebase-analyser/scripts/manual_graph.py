#!/usr/bin/env python3
"""
Manual graph creation for testshreya.

This script manually creates a graph of the relationships in the testshreya project
and visualizes it.
"""

import os
import sys
import json
import logging
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path

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
    "class": "#FFC107",      # Amber
    "interface": "#3F51B5",  # Indigo
    "method": "#8BC34A",     # Light Green
    "field": "#00BCD4",      # Cyan
    "DEFAULT": "#9E9E9E"     # Light Gray
}

def create_manual_graph():
    """Create a manual graph of the testshreya project."""
    # Create a NetworkX graph
    G = nx.DiGraph()
    
    # Add nodes for classes and interfaces
    G.add_node("Entity", type="interface", name="Entity")
    G.add_node("AbstractEntity", type="class", name="AbstractEntity")
    G.add_node("User", type="class", name="User")
    G.add_node("Order", type="class", name="Order")
    G.add_node("Address", type="class", name="Address")
    
    # Add inheritance relationships
    G.add_edge("AbstractEntity", "Entity", type="IMPLEMENTS", description="AbstractEntity implements Entity")
    G.add_edge("User", "AbstractEntity", type="EXTENDS", description="User extends AbstractEntity")
    G.add_edge("Order", "AbstractEntity", type="EXTENDS", description="Order extends AbstractEntity")
    
    # Add field type relationships
    G.add_edge("User", "Address", type="FIELD_TYPE", description="User has field of type Address")
    G.add_edge("User", "Order", type="FIELD_TYPE", description="User has field of type Order")
    G.add_edge("Order", "User", type="FIELD_TYPE", description="Order has field of type User")
    
    # Add method call relationships
    G.add_edge("Order", "User", type="CALLS", description="Order constructor calls User.addOrder()")
    
    return G

def visualize_graph(G, output_file):
    """Visualize the graph with better relationship highlighting."""
    logger.info(f"Visualizing graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    
    # Create figure
    plt.figure(figsize=(16, 12))
    plt.title("Manual Code Relationships - testshreya", fontsize=16)
    
    # Use a more sophisticated layout
    try:
        pos = nx.kamada_kawai_layout(G)
    except:
        # Fall back to spring layout if kamada_kawai fails
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
        if node_type == 'class':
            labels[node] = f"Class: {node_name}"
        elif node_type == 'interface':
            labels[node] = f"Interface: {node_name}"
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
                mpatches.Patch(color=color, alpha=0.8, label=f"{node_type.capitalize()}")
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

def main():
    """Main entry point for the script."""
    # Create the graph
    G = create_manual_graph()
    
    # Visualize the graph
    visualize_graph(G, 'samples/testshreya_manual_graph.png')
    
    logger.info("Manual graph creation completed successfully")

if __name__ == "__main__":
    main()
