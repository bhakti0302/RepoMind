#!/usr/bin/env python3
"""
Create UML-Style Diagrams

This script creates UML-style diagrams for a project.
"""

import os
import sys
import argparse
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx

def create_customer_highlight(output_path):
    """Create a UML-style diagram highlighting the Customer class."""
    print(f"Creating Customer Java Highlight diagram at {output_path}")

    # Create a directed graph
    G = nx.DiGraph()

    # Add nodes
    G.add_node("Customer", type="class", name="Customer")
    G.add_node("AbstractEntity", type="class", name="AbstractEntity")
    G.add_node("Address", type="class", name="Address")
    G.add_node("Order", type="class", name="Order")

    # Add edges
    G.add_edge("Customer", "AbstractEntity", type="EXTENDS")
    G.add_edge("Customer", "Address", type="USES")
    G.add_edge("Order", "Customer", type="USES")

    # Create the figure
    plt.figure(figsize=(12, 8))

    # Use a hierarchical layout
    # Create a manual hierarchical layout
    pos = {
        "Customer": (0.5, 0.5),
        "AbstractEntity": (0.5, 0.8),
        "Address": (0.8, 0.5),
        "Order": (0.2, 0.5)
    }

    # Draw nodes
    node_colors = {
        "Customer": "lightblue",
        "AbstractEntity": "lightgray",
        "Address": "lightgray",
        "Order": "lightgray"
    }

    for node in G.nodes():
        nx.draw_networkx_nodes(
            G, pos,
            nodelist=[node],
            node_color=node_colors[node],
            node_size=3000,
            alpha=0.8
        )

    # Draw edges with different styles based on relationship type
    for u, v, data in G.edges(data=True):
        edge_color = "black"
        edge_style = "solid"

        if data.get("type") == "EXTENDS":
            edge_color = "blue"
            edge_style = "solid"
        elif data.get("type") == "IMPLEMENTS":
            edge_color = "green"
            edge_style = "dashed"
        elif data.get("type") == "USES":
            edge_color = "red"
            edge_style = "solid"

        nx.draw_networkx_edges(
            G, pos,
            edgelist=[(u, v)],
            width=2,
            alpha=0.7,
            edge_color=edge_color,
            style=edge_style,
            arrowsize=20
        )

    # Draw labels with class/interface name and type
    labels = {}
    for node in G.nodes():
        node_type = G.nodes[node].get("type", "unknown")
        node_name = G.nodes[node].get("name", node)
        labels[node] = f"{node_type.capitalize()}: {node_name}"

    nx.draw_networkx_labels(G, pos, labels=labels, font_size=12, font_weight="bold")

    # Add a legend
    legend_elements = [
        mpatches.Patch(color="lightblue", label="Customer"),
        mpatches.Patch(color="lightgray", label="Related Class/Interface"),
        plt.Line2D([0], [0], color="blue", lw=2, label="Extends"),
        plt.Line2D([0], [0], color="green", linestyle="dashed", lw=2, label="Implements"),
        plt.Line2D([0], [0], color="red", lw=2, label="Uses")
    ]

    plt.legend(handles=legend_elements, loc="upper right")

    # Set title
    plt.title("Customer Class Relationships (UML-Style)", fontsize=16)

    # Remove axes
    plt.axis("off")

    # Save the figure
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Customer Java Highlight diagram saved to {output_path}")

def create_project_graph(output_path):
    """Create a UML-style diagram of the entire project with Customer highlighted."""
    print(f"Creating Project Graph with Customer Highlight diagram at {output_path}")

    # Create a directed graph
    G = nx.DiGraph()

    # Add nodes
    G.add_node("Customer", type="class", name="Customer")
    G.add_node("AbstractEntity", type="class", name="AbstractEntity")
    G.add_node("Address", type="class", name="Address")
    G.add_node("Order", type="class", name="Order")
    G.add_node("Product", type="class", name="Product")
    G.add_node("User", type="class", name="User")
    G.add_node("Entity", type="interface", name="Entity")

    # Add edges
    G.add_edge("Customer", "AbstractEntity", type="EXTENDS")
    G.add_edge("Product", "AbstractEntity", type="EXTENDS")
    G.add_edge("User", "AbstractEntity", type="EXTENDS")
    G.add_edge("AbstractEntity", "Entity", type="IMPLEMENTS")
    G.add_edge("Customer", "Address", type="USES")
    G.add_edge("Order", "Customer", type="USES")
    G.add_edge("Order", "Product", type="USES")

    # Create the figure
    plt.figure(figsize=(16, 12))

    # Use a hierarchical layout
    # Create a manual hierarchical layout
    pos = {
        "Entity": (0.5, 0.9),
        "AbstractEntity": (0.5, 0.7),
        "Customer": (0.3, 0.5),
        "Product": (0.5, 0.5),
        "User": (0.7, 0.5),
        "Address": (0.3, 0.3),
        "Order": (0.5, 0.3)
    }

    # Draw nodes
    node_colors = {
        "Customer": "lightblue",  # Highlight Customer
        "AbstractEntity": "lightgray",
        "Address": "lightgray",
        "Order": "lightgray",
        "Product": "lightgray",
        "User": "lightgray",
        "Entity": "lightgreen"  # Interface
    }

    node_sizes = {
        "Customer": 3000,  # Larger for Customer
        "AbstractEntity": 2000,
        "Address": 2000,
        "Order": 2000,
        "Product": 2000,
        "User": 2000,
        "Entity": 2000
    }

    for node in G.nodes():
        nx.draw_networkx_nodes(
            G, pos,
            nodelist=[node],
            node_color=node_colors[node],
            node_size=node_sizes[node],
            alpha=0.8
        )

    # Draw edges with different styles based on relationship type
    for u, v, data in G.edges(data=True):
        edge_color = "black"
        edge_style = "solid"

        if data.get("type") == "EXTENDS":
            edge_color = "blue"
            edge_style = "solid"
        elif data.get("type") == "IMPLEMENTS":
            edge_color = "green"
            edge_style = "dashed"
        elif data.get("type") == "USES":
            edge_color = "red"
            edge_style = "solid"

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
    for node in G.nodes():
        if node == "Customer":
            # Highlight Customer with more details
            node_type = G.nodes[node].get("type", "unknown")
            node_name = G.nodes[node].get("name", node)
            labels[node] = f"{node_type.capitalize()}: {node_name}"
        else:
            # Just show name for other nodes
            labels[node] = G.nodes[node].get("name", node)

    nx.draw_networkx_labels(G, pos, labels=labels, font_size=10)

    # Add a legend
    legend_elements = [
        mpatches.Patch(color="lightblue", label="Customer"),
        mpatches.Patch(color="lightgray", label="Class"),
        mpatches.Patch(color="lightgreen", label="Interface"),
        plt.Line2D([0], [0], color="blue", lw=2, label="Extends"),
        plt.Line2D([0], [0], color="green", linestyle="dashed", lw=2, label="Implements"),
        plt.Line2D([0], [0], color="red", lw=2, label="Uses")
    ]

    plt.legend(handles=legend_elements, loc="upper right")

    # Set title
    plt.title("Project Class Diagram with Customer Highlight (UML-Style)", fontsize=16)

    # Remove axes
    plt.axis("off")

    # Save the figure
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Project Graph with Customer Highlight diagram saved to {output_path}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Create UML-style diagrams")
    parser.add_argument("--output-dir", required=True, help="Output directory for diagrams")

    args = parser.parse_args()

    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)

    # Create Customer Java Highlight diagram
    customer_highlight_path = os.path.join(args.output_dir, "customer_java_highlight.png")
    create_customer_highlight(customer_highlight_path)

    # Create Project Graph with Customer Highlight diagram
    project_graph_path = os.path.join(args.output_dir, "project_graph_customer_highlight.png")
    create_project_graph(project_graph_path)

    print("UML-style diagrams created successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
