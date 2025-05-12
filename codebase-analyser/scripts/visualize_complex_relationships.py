#!/usr/bin/env python3
"""
Visualize complex relationships in the testshreya project.

This script creates visualizations for:
1. Circular relationships
2. Multi-file relationships
3. Different types of relationships with distinct colors and styles
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
    "file": "#795548",       # Brown
    "DEFAULT": "#9E9E9E"     # Light Gray
}

# Removed circular relationship graph function

def create_multi_file_relationship_graph():
    """Create a graph with multi-file relationships."""
    # Create a NetworkX graph
    G = nx.DiGraph()

    # Add nodes for files
    G.add_node("Entity.java", type="file", name="Entity.java")
    G.add_node("AbstractEntity.java", type="file", name="AbstractEntity.java")
    G.add_node("User.java", type="file", name="User.java")
    G.add_node("Order.java", type="file", name="Order.java")
    G.add_node("Address.java", type="file", name="Address.java")

    # Add nodes for classes
    G.add_node("Entity", type="interface", name="Entity", file="Entity.java")
    G.add_node("AbstractEntity", type="class", name="AbstractEntity", file="AbstractEntity.java")
    G.add_node("User", type="class", name="User", file="User.java")
    G.add_node("Order", type="class", name="Order", file="Order.java")
    G.add_node("Address", type="class", name="Address", file="Address.java")

    # Add file contains class relationships
    G.add_edge("Entity.java", "Entity", type="CONTAINS", description="File contains interface")
    G.add_edge("AbstractEntity.java", "AbstractEntity", type="CONTAINS", description="File contains class")
    G.add_edge("User.java", "User", type="CONTAINS", description="File contains class")
    G.add_edge("Order.java", "Order", type="CONTAINS", description="File contains class")
    G.add_edge("Address.java", "Address", type="CONTAINS", description="File contains class")

    # Add cross-file relationships
    G.add_edge("AbstractEntity", "Entity", type="IMPLEMENTS", description="AbstractEntity implements Entity")
    G.add_edge("User", "AbstractEntity", type="EXTENDS", description="User extends AbstractEntity")
    G.add_edge("Order", "AbstractEntity", type="EXTENDS", description="Order extends AbstractEntity")
    G.add_edge("User", "Address", type="FIELD_TYPE", description="User has field of type Address")
    G.add_edge("User", "Order", type="FIELD_TYPE", description="User has field of type Order")
    G.add_edge("Order", "User", type="FIELD_TYPE", description="Order has field of type User")

    # Add import relationships
    G.add_edge("AbstractEntity.java", "Entity.java", type="IMPORTS", description="AbstractEntity.java imports Entity.java")
    G.add_edge("User.java", "AbstractEntity.java", type="IMPORTS", description="User.java imports AbstractEntity.java")
    G.add_edge("User.java", "Address.java", type="IMPORTS", description="User.java imports Address.java")
    G.add_edge("User.java", "Order.java", type="IMPORTS", description="User.java imports Order.java")
    G.add_edge("Order.java", "AbstractEntity.java", type="IMPORTS", description="Order.java imports AbstractEntity.java")
    G.add_edge("Order.java", "User.java", type="IMPORTS", description="Order.java imports User.java")

    return G

def create_relationship_types_graph():
    """Create a graph with different types of relationships."""
    # Create a NetworkX graph
    G = nx.DiGraph()

    # Add nodes for classes and interfaces
    G.add_node("Entity", type="interface", name="Entity")
    G.add_node("AbstractEntity", type="class", name="AbstractEntity")
    G.add_node("User", type="class", name="User")
    G.add_node("Order", type="class", name="Order")
    G.add_node("Address", type="class", name="Address")
    G.add_node("Payment", type="class", name="Payment")

    # Add methods
    G.add_node("User.addOrder", type="method", name="addOrder")
    G.add_node("Order.getUser", type="method", name="getUser")
    G.add_node("User.getAddress", type="method", name="getAddress")

    # Add fields
    G.add_node("User.address", type="field", name="address")
    G.add_node("User.orders", type="field", name="orders")
    G.add_node("Order.user", type="field", name="user")

    # Add different types of relationships

    # Inheritance relationships
    G.add_edge("AbstractEntity", "Entity", type="IMPLEMENTS", description="AbstractEntity implements Entity")
    G.add_edge("User", "AbstractEntity", type="EXTENDS", description="User extends AbstractEntity")
    G.add_edge("Order", "AbstractEntity", type="EXTENDS", description="Order extends AbstractEntity")
    G.add_edge("Payment", "AbstractEntity", type="EXTENDS", description="Payment extends AbstractEntity")

    # Field type relationships
    G.add_edge("User", "Address", type="FIELD_TYPE", description="User has field of type Address")
    G.add_edge("User", "Order", type="FIELD_TYPE", description="User has field of type Order")
    G.add_edge("Order", "User", type="FIELD_TYPE", description="Order has field of type User")
    G.add_edge("Order", "Payment", type="FIELD_TYPE", description="Order has field of type Payment")

    # Method call relationships
    G.add_edge("Order.getUser", "User", type="CALLS", description="Order.getUser returns User")
    G.add_edge("User.getAddress", "Address", type="CALLS", description="User.getAddress returns Address")
    G.add_edge("User.addOrder", "Order", type="CALLS", description="User.addOrder uses Order")

    # Container relationships
    G.add_edge("User", "User.addOrder", type="CONTAINS", description="User contains addOrder method")
    G.add_edge("User", "User.getAddress", type="CONTAINS", description="User contains getAddress method")
    G.add_edge("User", "User.address", type="CONTAINS", description="User contains address field")
    G.add_edge("User", "User.orders", type="CONTAINS", description="User contains orders field")
    G.add_edge("Order", "Order.getUser", type="CONTAINS", description="Order contains getUser method")
    G.add_edge("Order", "Order.user", type="CONTAINS", description="Order contains user field")

    return G

def visualize_graph(G, output_file, title):
    """Visualize the graph with better relationship highlighting."""
    logger.info(f"Visualizing graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")

    # Create figure
    plt.figure(figsize=(16, 12))
    plt.title(title, fontsize=16)

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
        elif node_type == 'method':
            labels[node] = f"Method: {node_name}"
        elif node_type == 'field':
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
    # Create output directory if it doesn't exist
    os.makedirs('samples', exist_ok=True)

    # Create and visualize multi-file relationship graph
    G_multi_file = create_multi_file_relationship_graph()
    visualize_graph(G_multi_file, 'samples/multi_file_relationships.png', 'Multi-File Relationships')

    # Create and visualize relationship types graph
    G_relationship_types = create_relationship_types_graph()
    visualize_graph(G_relationship_types, 'samples/relationship_types.png', 'Different Types of Relationships')

    logger.info("Complex relationship visualization completed successfully")

if __name__ == "__main__":
    main()
